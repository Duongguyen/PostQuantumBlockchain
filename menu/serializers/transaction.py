from rest_framework import serializers

from menu.models import Transaction, BlockchainUser


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlockchainUser
        fields = '__all__'