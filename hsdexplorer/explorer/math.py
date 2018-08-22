def total_received(txs, address):
    received = 0
    for tx in txs:
        for it in tx['outputs']:
            if it.get('address') == address:
                received += it.get('value', 0)
    return received


def total_sent(txs, address):
    sent = 0
    for tx in txs:
        for ot in tx['inputs']:
            if ot.get('address') == address:
                sent += ot.get('value', 0)
    return sent
