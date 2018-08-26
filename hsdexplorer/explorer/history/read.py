from django.conf import settings
import hashlib
import os
import sys
from functools import lru_cache
if sys.version_info < (3, 6):
    import sha3

from explorer import models


def get_events(name=None, limit=50, offset=0):
    """Retrieve event history for a given name."""
    if name:
        events = models.Event.objects.filter(name__name=name)
    else:
        events = models.Event.objects.all()
    return events.order_by('-block_id', '-output_index')[offset:offset + limit]


def get_names():
    return models.Name.objects.all()


@lru_cache(maxsize=2048)
def lookup_name(name_hash):
    return models.Name.objects.get(hash=name_hash).name


def _get_name_hash(name):
    m = hashlib.sha3_256()
    m.update(name.encode('ascii'))
    return m.hexdigest()


def get_name(name):
    return models.Name.objects.get(name=name)
