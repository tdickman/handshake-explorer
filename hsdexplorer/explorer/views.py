from django.db.models import Max
from django.shortcuts import redirect, render
import math
import re

from . import hsd, math as hsdmath, models, utils

BLOCKS_PAGE_SIZE = 50
TXS_PAGE_SIZE = 20
EVENTS_PAGE_SIZE = 50


def index(request):
    info = hsd.get_info()
    events = models.Event.objects.filter().order_by('-block', '-block_index', '-output_index').prefetch_related('name')[:5]
    return render(request, 'explorer/index.html', context={
        'tip': info['chain']['tip'],
        'height': info['chain']['height'],
        'blocks': hsd.get_blocks(count=5),
        'events': events
    })


def events(request, page=1):
    offset = (page - 1) * EVENTS_PAGE_SIZE
    pages = [p for p in range(page - 5, page + 5) if p >= 1]
    events = models.Event.objects.all().order_by('-block', '-block_index', '-output_index').prefetch_related('name')[offset:offset + EVENTS_PAGE_SIZE]

    return render(request, 'explorer/events.html', context={
        'events': events,
        'current_page': page,
        'pages': pages
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
    txs = hsd.get_address_txs(address)
    pagified = utils.pagify(txs, page, TXS_PAGE_SIZE)
    received = hsdmath.total_received(txs, address)
    sent = hsdmath.total_sent(txs, address)
    return render(request, 'explorer/address.html', context={
        'address': address,
        'total_received': received,
        'total_sent': sent,
        'total_balance': received - sent,
        'tx_count': pagified['count'],
        'txs': pagified['data'],
        'current_page': pagified['current_page'],
        'max_page': pagified['max_page'],
        'pages': pagified['pages']
    })


def name(request, name):
    events = models.Event.objects.filter(name__name=name).order_by('-block', '-block_index', '-output_index')
    if not len(events):
        raise Exception('Invalid name (no events found)')
    # Find closest OPEN event
    open_block = next(e for e in events if e.action == models.Event.EventAction.OPEN.value).block_id
    auction_status = hsd.get_auction_status(open_block)
    auction_state = hsd.get_auction_state(open_block)
    time_remaining = hsd.get_time_remaining(open_block)
    return render(request, 'explorer/name.html', context={
        'name': name,
        'events': events,
        'auction_state': auction_state,
        'auction_status': auction_status,
        'time_remaining_minutes': int(time_remaining / 60)
    })


def names(request, page=1):
    names = models.Event.objects.filter(action='OPEN').values('name__name').annotate(Max('block')).order_by('-block__max')
    pagified = utils.pagify(names, page)
    for name in pagified['data']:
        name['state'] = hsd.get_auction_state(name['block__max'])


    return render(request, 'explorer/names.html', context={
        'names': pagified['data'],
        'current_page': pagified['current_page'],
        'max_page': pagified['max_page'],
        'pages': pagified['pages']
    })


def search(request):
    value = request.GET['value']
    if hsd.is_address(value):
        return redirect('address', address=value)
    if hsd.is_block(value):
        return redirect('block', block_hash=value)
    if hsd.is_transaction(value):
        return redirect('transaction', tx_hash=value)
    if hsd.is_name(value):
        return redirect('name', name=value)


def about(request):
    return render(request, 'explorer/about.html')
