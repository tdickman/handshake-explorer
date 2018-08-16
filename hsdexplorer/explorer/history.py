from django.conf import settings
from google.cloud import datastore
import hashlib
import sys
from functools import lru_cache
if sys.version_info < (3, 6):
    import sha3


datastore_client = datastore.Client(namespace=settings.DATASTORE_NAMESPACE)


def get_events(name):
    """Retrieve event history for a given name."""
    name_hash = _get_name_hash(name)
    query = datastore_client.query(kind='HSEvent')
    query.add_filter('name_hash', '=', name_hash)
    query.order = ['-block', '-tx_index']
    return list(query.fetch())


def get_names():
    query = datastore_client.query(kind='HSName')
    return list(query.fetch())


@lru_cache()
def decode_name(name_hash):
    query = datastore_client.query(kind='HSName')
    query.add_filter('name_hash', '=', name_hash)
    return list(query.fetch())[0]['name']


def _get_name_hash(name):
    m = hashlib.sha3_256()
    m.update(name.encode('ascii'))
    return m.hexdigest()
