from django.conf import settings
import datetime
import requests


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
    while remaining_blocks > 0:
        block_details = get_block(current_block)
        blocks.append(block_details)
        current_block = block_details['prevBlock']
        remaining_blocks -= 1

    return blocks


def get_block(block_hash_or_height):
    return _format_block(_request('/block/{}'.format(block_hash_or_height)))


def get_transaction(tx_hash):
    return _request('/tx/{}'.format(tx_hash))


def get_address(address):
    return _request('/coin/address/{}'.format(address))


def _format_block(block):
    block['time'] = datetime.datetime.fromtimestamp(block['time'])
    block['txs'] = [_format_tx(tx) for tx in block['txs']]
    return block


def _format_tx(tx):
    tx['mtime'] = datetime.datetime.fromtimestamp(tx['mtime'])
    return tx


def _request(path):
    resp = requests.get('{}{}'.format(settings.HSD_URI, path), timeout=5)
    return resp.json()
