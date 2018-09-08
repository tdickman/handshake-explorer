from django.conf import settings
import codecs
import datetime
import json
import pytz
import requests
import subprocess

from . import models
from .utils import cache_function


@cache_function
def get_info():
    return _request('/')


def get_auction_status(open_block):
    info = get_info()
    blocks_since_open = info['chain']['height'] - open_block

    return {
        'open_completed': max(min(blocks_since_open, settings.OPEN_PERIOD), 0),
        'open_total': settings.OPEN_PERIOD,
        'bidding_completed': max(min(
            blocks_since_open - settings.OPEN_PERIOD,
            settings.BIDDING_PERIOD), 0),
        'bidding_total': settings.BIDDING_PERIOD,
        'reveal_completed': max(min(
            blocks_since_open - settings.OPEN_PERIOD - settings.BIDDING_PERIOD,
            settings.REVEAL_PERIOD), 0),
        'reveal_total': settings.REVEAL_PERIOD
    }


def get_auction_state(open_block):
    info = get_info()
    blocks_since_open = info['chain']['height'] - open_block

    if blocks_since_open < settings.OPEN_PERIOD:
        return 'Open'

    if blocks_since_open < settings.BIDDING_PERIOD:
        return 'Bidding'

    if blocks_since_open < settings.REVEAL_PERIOD:
        return 'Reveal'

    return 'Live'


def get_time_remaining(open_block):
    auction_status = get_auction_status(open_block)
    current_state = get_auction_state(open_block).lower()
    blocks_completed = auction_status['{}_completed'.format(current_state)]
    blocks_total = auction_status['{}_total'.format(current_state)]
    return (blocks_total - blocks_completed) * settings.BLOCK_TIME_SECONDS


def get_blocks(offset=0, count=20):
    """
    Retrieve the `count` previous blocks, starting at `start`.
    If `start` is set to None, this will start at the current
    block.
    """
    info = get_info()
    current_block = info['chain']['height'] - offset
    blocks = []
    for block_number in range(current_block, max(current_block - count, 0), -1):
        block_details = get_block(block_number)
        blocks.append(block_details)

    return blocks


def get_block(block_hash_or_height, decode_resource=False):
    return _format_block(_request('/block/{}'.format(block_hash_or_height)), decode_resource=decode_resource)


def get_transaction(tx_hash):
    return _format_tx(_request('/tx/{}'.format(tx_hash)))


def get_address_txs(address):
    txs = [_format_tx(tx, address=address) for tx in _request('/tx/address/{}'.format(address))]
    return sorted(txs, key=lambda tx: tx['time'], reverse=True)


def _format_block(block, decode_resource=False):
    # Time parameter isn't present on txs if they we are returned as part of a
    # block, but they are included with a raw transaction
    for tx in block['txs']:
        tx['time'] = block['time']
    block['time'] = datetime.datetime.fromtimestamp(block['time'], tz=pytz.UTC)
    block['txs'] = [_format_tx(tx, decode_resource=decode_resource) for tx in block['txs']]
    return block


def _format_tx(tx, address=None, decode_resource=False):
    """
    Format a transaction. If `address` is provided, include the transaction
    direction relative to that address.
    """
    tx['time'] = datetime.datetime.fromtimestamp(tx['time'], tz=pytz.UTC)
    tx['inputs'] = [_format_input(i) for i in tx['inputs']]
    tx['outputs'] = [_format_output(o, decode_resource=decode_resource) for o in tx['outputs']]
    if address:
        tx['direction'] = None
        if len([o for o in tx['outputs'] if o.get('address') == address]):
            tx['direction'] = 'incoming' 
        if len([i for i in tx['inputs'] if i.get('address') == address]):
            tx['direction'] = 'outgoing' 
    return tx


def _format_input(input_data):
    # Mining
    if input_data['prevout']['hash'] == '0' * 64:
        return {
            'action': 'mine'
        }
    action = input_data['coin']['covenant']['action']
    return {
        'action': action,
        'value': input_data['coin']['value'],
        'address': input_data['coin']['address'],
        'source_tx': input_data['prevout']['hash']
    }
    return input_data


def _format_output(output, decode_resource=False):
    items = output['covenant']['items']
    action = output['covenant']['action']
    resp = {
        'action': action,
        'address': output['address']
    }

    if action == 'NONE':
        resp['address'] = output['address']
        resp['value'] = output['value']
        return resp

    # Process all other actions
    resp['name_hash'] = items[0]
    if action == 'OPEN':
        # items[1] == 00000000
        resp['name'] = _decode_name(items[2])
    elif action == 'BID':
        resp['start_height'] = _decode_u32(items[1])
        resp['name'] = _decode_name(items[2])
        resp['value'] = output['value']
        # items[3] == blind
    elif action == 'REVEAL':
        resp['start_height'] = _decode_u32(items[1])
        resp['nonce'] = items[2]
        resp['value'] = output['value']
    elif action == 'REGISTER':
        resp['start_height'] = _decode_u32(items[1])
        resp['data'] = _decode_resource(items[2])
    elif action == 'REDEEM':
        resp['start_height'] = _decode_u32(items[1])
        resp['value'] = output['value']
    elif action == 'UPDATE':
        resp['start_height'] = _decode_u32(items[1])
        resp['data'] = _decode_resource(items[2])
    elif action == 'RENEW':
        resp['start_height'] = _decode_u32(items[1])
        resp['renewal_block_hash'] = _decode_u32(items[2])

    # Lookup the name if it isn't included in the transaction. This will fail
    # for new domains that we encounter when processing with celery, in which
    # case we can skip it.
    if 'name' not in resp:
        try:
            resp['name'] = models.Name.objects.get(hash=resp['name_hash']).name
        except models.Name.DoesNotExist:
            pass

    return resp


def _decode_u32(hex_val):
    """Decode the specified little endian hex value into a u32."""
    return int(codecs.encode(codecs.decode(hex_val, 'hex')[::-1], 'hex').decode(), 16)


def _decode_resource(data):
    return json.loads(subprocess.check_output(['node', 'hsdbin/decode.js', data]).decode())


def _decode_name(hex_val):
    return bytes.fromhex(hex_val).decode('utf-8')


def _request(path):
    resp = requests.get('{}{}'.format(settings.HSD_URI, path), timeout=5)
    return resp.json()


def is_address(value):
    return re.compile('[a-z0-9]{42}').match(value) and value[:2] == 'ts'


def is_block(value):
    if re.compile('[a-f0-9]{64}').match(value):
        try:
            hsd.get_block(value)
            return True
        except json.decoder.JSONDecodeError:
            pass
    return False


def is_transaction(value):
    if re.compile('[a-f0-9]{64}').match(value):
        try:
            hsd.get_transaction(value)
            return True
        except json.decoder.JSONDecodeError:
            pass
    return False


def is_name(value):
    return len(models.Name.objects.filter(name=value)) > 0


