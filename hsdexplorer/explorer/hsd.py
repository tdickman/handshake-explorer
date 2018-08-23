from django.conf import settings
import codecs
import datetime
import json
import pytz
import requests
import subprocess

import explorer.history.read


def get_info():
    return _request('/')


def get_auction_state(open_block):
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


def get_blocks(offset=0, count=20):
    """
    Retrieve the `count` previous blocks, starting at `start`.
    If `start` is set to None, this will start at the current
    block.
    """
    info = get_info()
    current_block = info['chain']['height'] - offset

    remaining_blocks = count
    blocks = []
    while remaining_blocks > 0 and current_block >= 0:
        block_details = get_block(current_block)
        blocks.append(block_details)
        current_block -= 1
        remaining_blocks -= 1

    return blocks


def get_block(block_hash_or_height, decode_resource=False):
    try:
        return _format_block(_request('/block/{}'.format(block_hash_or_height), decode_resource=decode_resource))
    except json.decoder.JSONDecodeError:
        return


def get_transaction(tx_hash):
    return _format_tx(_request('/tx/{}'.format(tx_hash)))


def get_address_txs(address):
    return [_format_tx(tx, address=address) for tx in _request('/tx/address/{}'.format(address))]


def _format_block(block, decode_resource=False):
    block['time'] = datetime.datetime.fromtimestamp(block['time'], tz=pytz.UTC)
    block['txs'] = [_format_tx(tx, decode_resource=decode_resource) for tx in block['txs']]
    return block


def _format_tx(tx, address=None, decode_resource=False):
    """
    Format a transaction. If `address` is provided, include the transaction
    direction relative to that address.
    """
    tx['time'] = datetime.datetime.fromtimestamp(tx['mtime'])
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

    if 'value' in output:
        resp['value'] = output['value']

    if action == 'NONE':
        resp['address'] = output['address']
        return resp

    # Process all other actions
    resp['name_hash'] = items[0]
    if action == 'OPEN':
        # items[1] == 00000000
        resp['name'] = _decode_name(items[2])
    elif action == 'BID':
        resp['start_height'] = _decode_u32(items[1])
        resp['name'] = _decode_name(items[2])
        # items[3] == blind
    elif action == 'REVEAL':
        resp['start_height'] = _decode_u32(items[1])
        resp['nonce'] = items[2]
    elif action == 'REGISTER':
        resp['start_height'] = _decode_u32(items[1])
        resp['data'] = _decode_resource(items[2])
    elif action == 'REDEEM':
        resp['start_height'] = _decode_u32(items[1])
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
            resp['name'] = explorer.history.read.lookup_name(resp['name_hash'])
        except IndexError:
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
