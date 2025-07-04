# Generated by Django 4.2.7 on 2025-03-05 17:29

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Blockchains',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('version', models.FloatField(default=4.0)),
                ('header', models.IntegerField(default=0, null=True)),
                ('previous_hash', models.CharField(max_length=200, null=True)),
                ('hash_blockchain', models.CharField(max_length=200)),
                ('created_at', models.DateTimeField(default=datetime.datetime(2025, 3, 5, 17, 29, 20, 466326, tzinfo=datetime.timezone.utc), null=True)),
            ],
        ),
        migrations.CreateModel(
            name='BlockchainUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=50, unique=True)),
                ('password1', models.CharField(max_length=200, null=True)),
                ('password2', models.CharField(max_length=200, null=True)),
                ('email', models.EmailField(max_length=255, null=True, unique=True)),
                ('name', models.TextField(max_length=50)),
                ('address_wallet', models.CharField(max_length=200)),
                ('balance', models.FloatField(default=0)),
                ('phone', models.IntegerField(unique=True)),
                ('is_verified', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(default=datetime.datetime(2025, 3, 5, 17, 29, 20, 467890), null=True)),
                ('updated_at', models.DateTimeField(default=datetime.datetime(2025, 3, 5, 17, 29, 20, 467929), null=True)),
                ('deleted_at', models.DateTimeField(default=datetime.datetime(2025, 3, 5, 17, 29, 20, 467956), null=True)),
                ('deleted', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='New',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField()),
                ('title', models.CharField(max_length=300)),
                ('content', models.TextField(max_length=2000)),
                ('like', models.IntegerField(default=0)),
                ('share', models.IntegerField(default=0)),
                ('tag', models.CharField(max_length=50)),
                ('summary', models.CharField(max_length=50)),
                ('liked_users', models.JSONField(default=list)),
            ],
        ),
        migrations.CreateModel(
            name='TitlePage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('link', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('header', models.IntegerField(max_length=10, null=True)),
                ('from_send', models.CharField(max_length=200)),
                ('destination', models.CharField(max_length=200, null=True)),
                ('pass_check', models.CharField(max_length=200, null=True)),
                ('amount', models.FloatField(null=True)),
                ('from_key', models.CharField(max_length=200, null=True)),
                ('destination_key', models.CharField(max_length=200, null=True)),
                ('created_at', models.DateTimeField(default=datetime.datetime(2025, 3, 5, 17, 29, 20, 465577, tzinfo=datetime.timezone.utc), null=True)),
                ('status_sell', models.BooleanField(default=False)),
                ('hash_session', models.CharField(max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('birthday', models.DateField()),
                ('phone', models.IntegerField(unique=True)),
                ('gender', models.CharField(max_length=6)),
                ('balance', models.FloatField(default=0)),
                ('address_wallet', models.CharField(max_length=1000, null=True)),
                ('is_verified', models.BooleanField(default=False)),
                ('private_key', models.CharField(max_length=1000, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
