from django.conf import settings
from google.cloud import datastore
import os


if not os.environ.get('COLLECTSTATIC'):
    datastore_client = datastore.Client(namespace=settings.DATASTORE_NAMESPACE)


def get_max_block():
    query = datastore_client.query(kind='HSBlock')
    query.order = ['-height']
    try:
        return list(query.fetch())[0]['height']
    except TypeError:
        return 0


def get_processed_block_hash(height):
    if height < 0:
        return '0000000000000000000000000000000000000000000000000000000000000000'
    key = datastore_client.key('HSBlock', height)
    return datastore_client.get(key)['hash']


def unprocess_block(height):
    """Delete all entries from the specified block from our datastore."""
    keys = [datastore_client.key('HSBlock', height)]

    # Events
    query = datastore_client.query(kind='HSEvent')
    query.add_filter('block', '=', height)
    keys += list(query.fetch())
    datastore_client.delete_multi(keys)


def insert(event):
    # Event
    kind = 'HSEvent'
    key = datastore_client.key(kind, '{}:{}'.format(event['tx_hash'], event['tx_index']))
    hs_event = datastore.Entity(key=key, exclude_from_indexes=['data', 'value'])
    hs_event['action'] = event['action']
    hs_event['name_hash'] = event['name_hash']
    hs_event['tx_hash'] = event['tx_hash']
    hs_event['tx_index'] = event['tx_index']
    hs_event['block'] = event['block']
    if 'start_height' in event:
        hs_event['start_height'] = event['start_height']
    if 'data' in event:
        hs_event['data'] = json.dumps(event['data'])
    if 'value' in event:
        hs_event['value'] = event['value']

    # Domain
    if 'name' in event:
        kind = 'HSName'
        key = datastore_client.key(kind, event['name'])
        hs_domain = datastore.Entity(key=key, exclude_from_indexes=['data'])
        hs_domain['name_hash'] = event['name_hash']
        hs_domain['name'] = event['name']
        # Persist any changes to the associated domain
        if event['action'] == 'UPDATE':
            hs_domain['data'] = event['data']
        datastore_client.put(hs_domain)

    datastore_client.put(hs_event)


def mark_block(height, hash_val):
    # Since datastore doesn't allow an index of 0
    key = datastore_client.key('HSBlock', height)
    entity = datastore.Entity(key=key)
    entity['height'] = height
    entity['hash'] = hash_val
    datastore_client.put(entity)
