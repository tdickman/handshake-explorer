from django.shortcuts import render

from . import hsd


def index(request):
    info = hsd.get_info()
    return render(request, 'explorer/index.html', context={
        'tip': info['chain']['tip'],
        'height': info['chain']['height'],
        'blocks': hsd.get_blocks(count=5)
    })


def blocks(request, page=1):
    print(page)
    offset = page * 50 - 50
    return render(request, 'explorer/blocks.html', context={
        'blocks': hsd.get_blocks(offset=offset, count=50)
    })


def block(request, block_hash):
    return render(request, 'explorer/block.html', context={
        'hsdblock': hsd.get_block(block_hash)
    })


def transaction(request, tx_hash):
    return render(request, 'explorer/transaction.html', context={
        'tx': hsd.get_transaction(tx_hash)
    })


def address(request, address):
    return render(request, 'explorer/address.html', context={
        'address': address
    })
