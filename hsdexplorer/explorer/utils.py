from django.conf import settings
from django.core.cache import caches
import json
import math
import re
from enum import Enum


class ChoiceEnum(Enum):
    @classmethod
    def choices(cls):
        return tuple((x.name, x.value) for x in cls)


def pagify(data, page, page_size=settings.DEFAULT_PAGE_SIZE):
    """Given a list of data, return paginated data."""
    page = int(page)
    max_page = math.ceil(len(data) / page_size)
    offset = (page - 1) * page_size
    pages = [p for p in range(page - 5, page + 5) if p >= 1 and p <= max_page]
    return {
        'data': data[offset:offset + page_size],
        'count': len(data),
        'current_page': page,
        'max_page': max_page,
        'pages': pages
    }


def cache_function(func):
    def cached(*args, **kw):
        cache_name = 'func-cache-{}'.format(func.__name__)
        resp = caches['in_memory'].get(cache_name)
        if resp:
            return resp
        resp = func(*args, **kw)
        caches['in_memory'].set(cache_name, resp, 10)
        return resp
    return cached
