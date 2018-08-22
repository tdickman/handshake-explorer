import json
import re

from . import hsd
import explorer.history.read


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
    return explorer.history.read.get_name(value)
