from django.db import models

from menu.utils.common.time_system import naive_now
from menu.utils.common import get_uuid4
from django.utils import timezone


class Transaction(models.Model):
    header = models.IntegerField(null=True, default=0)
    from_send = models.CharField(max_length=200, null=False)
    destination = models.CharField(max_length=200, null=True)
    amount = models.FloatField(null=True)
    from_key = models.CharField(max_length=200, null=False, default=get_uuid4())
    destination_key = models.CharField(max_length=200, null=False, default=get_uuid4())
    created_at = models.DateTimeField(default=timezone.now(), null=True)

    def __str__(self):
        return self.from_send


class Blockchains(models.Model):
    version = models.FloatField(null=False, default=4.0)
    header = models.IntegerField(null=True, default=0)
    previous_hash = models.CharField(max_length=200, null=True)
    hash_blockchain = models.CharField(max_length=200, null=False)
    created_at = models.DateTimeField(default=timezone.now(), null=True)

    def __str__(self):
        return self.hash_blockchain


class BlockchainUser(models.Model):
    username = models.CharField(max_length=200, null=False, unique=True)
    password = models.CharField(max_length=200, null=False)
    name = models.TextField(max_length=2000, null=False)
    address_wallet = models.CharField(max_length=200, null=False, unique=True, default=get_uuid4())

    balance = models.FloatField(null=False, default=0)
    phone = models.IntegerField(null=False)

    created_at = models.DateTimeField(default=naive_now(), null=True)
    updated_at = models.DateTimeField(default=naive_now(), null=True)
    deleted_at = models.DateTimeField(default=naive_now(), null=True)
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.username

