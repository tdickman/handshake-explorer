from django.conf import settings
import datetime
import requests

from . import history


def get_info():
    return _request('/')


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


def get_block(block_hash_or_height):
    return _format_block(_request('/block/{}'.format(block_hash_or_height)))


def get_transaction(tx_hash):
    return _format_tx(_request('/tx/{}'.format(tx_hash)))


def get_address_txs(address):
    return [_format_tx(tx) for tx in _request('/tx/address/{}'.format(address))]


def _format_block(block):
    block['time'] = datetime.datetime.fromtimestamp(block['time'])
    block['txs'] = [_format_tx(tx) for tx in block['txs']]
    return block


def _format_tx(tx):
    tx['mtime'] = datetime.datetime.fromtimestamp(tx['mtime'])
    tx['inputs'] = [_format_input(i) for i in tx['inputs']]
    tx['outputs'] = [_format_output(o) for o in tx['outputs']]
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


def _format_output(output_data):
    action = output_data['covenant']['action']
    if action == 'OPEN':
        return {
            'action': 'open',
            'name': bytes.fromhex(output_data['covenant']['items'][-1]).decode('utf-8')
        }
    elif action == 'REVEAL':
        return {
            'action': 'reveal',
            'value': output_data['value'],
            'address': output_data['address'],
            'name': history.decode_name(output_data['covenant']['items'][0])
        }
    elif action == 'BID':
        return {
            'value': output_data['value'],
            'action': 'bid',
            'name': bytes.fromhex(output_data['covenant']['items'][-2]).decode('utf-8')
        }
    elif action == 'NONE':
        return {
            'value': output_data['value'],
            'action': 'transfer',
            'address': output_data['address']
        }
    elif action == 'REGISTER':
        return {
            'action': 'register',
            'name': history.decode_name(output_data['covenant']['items'][0])
        }
    elif action == 'UPDATE':
        return {
            'action': 'update',
            'name': history.decode_name(output_data['covenant']['items'][0])
        }
    elif action == 'REDEEM':
        return {
            'action': 'redeem',
            'name': history.decode_name(output_data['covenant']['items'][0])
        }
    raise Exception('Unknown action encountered {}'.format(action))


def _request(path):
    resp = requests.get('{}{}'.format(settings.HSD_URI, path), timeout=5)
    return resp.json()
