import json
import math
import re
from enum import Enum

from . import hsd, models
from hsdexplorer import settings


def is_address(value):
    return re.compile('[a-z0-9]{42}').match(value) and value[:2] == 'ts'


def is_block(value):
    if re.compile('[a-f0-9]{64}').match(value):
        try:
            hsd.get_block(value)
            return True
        except json.decoder.JSONDecodeError:
            pass
    return False


def is_transaction(value):
    if re.compile('[a-f0-9]{64}').match(value):
        try:
            hsd.get_transaction(value)
            return True
        except json.decoder.JSONDecodeError:
            pass
    return False


def is_name(value):
    return len(models.Name.objects.filter(name=value)) > 0


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
