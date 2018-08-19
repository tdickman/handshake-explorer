from django.shortcuts import render
import math

from . import hsd, history as history_lib

BLOCKS_PAGE_SIZE = 50
TXS_PAGE_SIZE = 10


def index(request):
    info = hsd.get_info()
    return render(request, 'explorer/index.html', context={
        'tip': info['chain']['tip'],
        'height': info['chain']['height'],
        'blocks': hsd.get_blocks(count=5)
    })


def blocks(request, page=1):
    info = hsd.get_info()
    max_page = math.ceil(info['chain']['height'] / BLOCKS_PAGE_SIZE)
    offset = (page - 1) * BLOCKS_PAGE_SIZE
    pages = [p for p in range(page - 5, page + 5) if p >= 1 and p <= max_page]
    return render(request, 'explorer/blocks.html', context={
        'blocks': hsd.get_blocks(offset=offset, count=BLOCKS_PAGE_SIZE),
        'current_page': page,
        'max_page': max_page,
        'pages': pages
    })


def block(request, block_hash):
    return render(request, 'explorer/block.html', context={
        'hsdblock': hsd.get_block(block_hash)
    })


def transaction(request, tx_hash):
    return render(request, 'explorer/transaction.html', context={
        'tx': hsd.get_transaction(tx_hash)
    })


def address(request, address, page=1):
    page = int(page)
    txs = hsd.get_address_txs(address)
    max_page = math.ceil(len(txs) / TXS_PAGE_SIZE)
    offset = (page - 1) * TXS_PAGE_SIZE
    pages = [p for p in range(page - 5, page + 5) if p >= 1 and p <= max_page]
    return render(request, 'explorer/address.html', context={
        'address': address,
        'txs': txs[offset:offset + TXS_PAGE_SIZE],
        'current_page': page,
        'max_page': max_page,
        'pages': pages
    })


def name(request, name):
    events = history_lib.get_events(name)
    if not len(events):
        raise Exception('Invalid name (no events found)')
    return render(request, 'explorer/name.html', context={
        'name': name,
        'events': events
    })


def names(request):
    names = history_lib.get_names()
    return render(request, 'explorer/names.html', context={
        'names': names
    })
