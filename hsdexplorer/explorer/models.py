from django.contrib.postgres.fields import JSONField
from django.core.validators import RegexValidator
from django.db import models
from explorer.utils import ChoiceEnum


# Create your models here.
class Name(models.Model):
    hash = models.CharField(primary_key=True, validators=[RegexValidator('^[a-f0-9]{64}$', 'Must be a 64 character hex string')], max_length=64)
    name = models.CharField(max_length=500, unique=True)


class Block(models.Model):
    height = models.PositiveIntegerField(primary_key=True)
    hash = models.CharField(validators=[RegexValidator(regex='^.[a-f0-9]{64}$', message='Must be a 64 character hex string', code='nomatch')], max_length=64)


class Event(models.Model):
    class EventAction(ChoiceEnum):
        NONE = 0
        CLAIM = 1
        OPEN = 2
        BID = 3
        REVEAL = 4
        REDEEM = 5
        REGISTER = 6
        UPDATE = 7
        RENEW = 8
        TRANSFER = 9
        FINALIZE = 10
        REVOKE = 11

    tx_hash = models.CharField(validators=[RegexValidator(regex='^.[a-f0-9]{64}$', message='Must be a 64 character hex string', code='nomatch')], max_length=64)
    output_index = models.PositiveIntegerField()
    class Meta:
        unique_together = (('tx_hash', 'output_index'),)
    action = models.PositiveIntegerField(choices=EventAction.choices())
    block = models.ForeignKey(Block, on_delete=models.CASCADE, related_name='block')
    data = JSONField(blank=True, null=True)
    name = models.ForeignKey(Name, on_delete=models.CASCADE)
    start_block = models.ForeignKey(Block, on_delete=models.CASCADE, related_name='start_height', blank=True, null=True)
    value = models.BigIntegerField(blank=True, null=True)
