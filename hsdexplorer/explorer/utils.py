import json
import re
from enum import Enum

from . import hsd, models


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
