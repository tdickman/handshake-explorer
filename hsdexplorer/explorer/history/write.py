from django.conf import settings
import os
import json

from explorer import models


def get_max_block():
    max_block = models.Block.objects.order_by('-height').first()
    return max_block.height if max_block else -1


def get_processed_block_hash(height):
    if height < 0:
        return '0000000000000000000000000000000000000000000000000000000000000000'
    return models.Block.objects.get(height=height).hash


def unprocess_block(height):
    """Delete all entries from the specified block from our datastore."""
    # Delete block -> should automatically cascade and cause events to be deleted
    models.Block.objects.get(height=height).delete()


def insert(event):
    if 'name' in event:
        models.Name.objects.update_or_create(
            hash=event['name_hash'],
            name=event['name']
        )
    models.Event(
        tx_hash=event['tx_hash'],
        output_index=event['output_index'],
        action=models.Event.EventAction[event['action']].value,
        block_id=event['block'],
        data=event.get('data'),
        name_id=event['name_hash'],
        start_block_id=event.get('start_height'),
        value=event.get('value')
    ).save()


def mark_block(height, hash_val):
    models.Block(
        height=height,
        hash=hash_val
    ).save()
