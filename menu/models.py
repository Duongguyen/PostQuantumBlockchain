from django.db import models

from menu.utils.common.time_system import naive_now
from menu.utils.common import get_uuid4
from django.utils import timezone
from django.contrib.auth.models import User


class Transaction(models.Model):
    header = models.IntegerField(null=True, default=0)
    from_send = models.CharField(max_length=200, null=False)
    destination = models.CharField(max_length=200, null=True)
    pass_check = models.CharField(max_length=200, null=True)
    amount = models.FloatField(null=True)
    from_key = models.CharField(max_length=200, null=True)
    destination_key = models.CharField(max_length=200, null=True)
    created_at = models.DateTimeField(default=timezone.now(), null=True)
    status_sell = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.created_at:  # Nếu from_key trống, gán giá trị mặc định
            self.created_at = timezone.now()

        super().save(*args, **kwargs)

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


class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    birthday = models.DateField()
    phone = models.IntegerField(null=False, unique=True)
    gender = models.CharField(
        max_length=6
    )
    balance = models.FloatField(null=False, default=0)
    address_wallet = models.CharField(max_length=200, null=False, default=get_uuid4())
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


class New(models.Model):
    user_id = models.IntegerField(null=False, unique=True)
    title = models.CharField(max_length=300)
    content = models.TextField(max_length=2000)
    like = models.IntegerField(default=0)
    share = models.IntegerField(default=0)
    tag = models.CharField(max_length=50)
    summary = models.CharField(max_length=50)
    liked_users = models.JSONField(default=list)

    def __str__(self):
        return self.title


class TitlePage(models.Model):
    title = models.CharField(max_length=100)
    link = models.CharField(max_length=100)

    def __str__(self):
        return self.title


class BlockchainUser(models.Model):
    username = models.CharField(max_length=50, null=False, unique=True)
    password1 = models.CharField(max_length=200, null=True)
    password2 = models.CharField(max_length=200, null=True)
    email = models.EmailField(max_length=255, null=True, unique=True)
    name = models.TextField(max_length=50, null=False)
    address_wallet = models.CharField(max_length=200, null=False)
    balance = models.FloatField(null=False, default=0)
    phone = models.IntegerField(null=False, unique=True)
    is_verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(default=naive_now(), null=True)
    updated_at = models.DateTimeField(default=naive_now(), null=True)
    deleted_at = models.DateTimeField(default=naive_now(), null=True)
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.username
