from django.contrib.postgres.fields import JSONField
from django.core.validators import RegexValidator
from django.db import models
from explorer.utils import ChoiceEnum


# Create your models here.
class Name(models.Model):
    hash = models.CharField(primary_key=True, validators=[RegexValidator('^[a-f0-9]{64}$', 'Must be a 64 character hex string')], max_length=64)
    name = models.CharField(max_length=500, unique=True, db_index=True)


class Block(models.Model):
    height = models.PositiveIntegerField(primary_key=True)
    hash = models.CharField(validators=[RegexValidator(regex='^.[a-f0-9]{64}$', message='Must be a 64 character hex string', code='nomatch')], max_length=64, db_index=True)


class Event(models.Model):
    class EventAction(ChoiceEnum):
        NONE = 'NONE'
        CLAIM = 'CLAIM'
        OPEN = 'OPEN'
        BID = 'BID'
        REVEAL = 'REVEAL'
        REDEEM = 'REDEEM'
        REGISTER = 'REGISTER'
        UPDATE = 'UPDATE'
        RENEW = 'RENEW'
        TRANSFER = 'TRANSFER'
        FINALIZE = 'FINALIZE'
        REVOKE = 'REVOKE'

    tx_hash = models.CharField(validators=[RegexValidator(regex='^.[a-f0-9]{64}$', message='Must be a 64 character hex string', code='nomatch')], max_length=64)
    output_index = models.PositiveIntegerField()
    block_index = models.PositiveIntegerField()  # Index within block
    action = models.CharField(choices=EventAction.choices(), max_length=10)
    block = models.ForeignKey(Block, on_delete=models.CASCADE, related_name='block')
    data = JSONField(blank=True, null=True)
    name = models.ForeignKey(Name, on_delete=models.CASCADE)
    start_block = models.ForeignKey(Block, on_delete=models.CASCADE, related_name='start_height', blank=True, null=True)
    value = models.BigIntegerField(blank=True, null=True)

    class Meta:
        unique_together = (('tx_hash', 'output_index'),)
        indexes = [
            models.Index(fields=['-block', '-block_index', '-output_index'])
        ]
