import re
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from ...models import Transaction, BlockchainUser, Account

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['from_send'].required = False
        self.fields['pass_check'].required = False
        self.fields['created_at'].required = False
        self.fields['amount'].required = False
        self.fields['header'].required = False
        self.fields['status_sell'].required = False
        self.fields['hash_session'].required = False


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']


class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['phone', 'birthday', 'gender']

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields['address_wallet'].required = False  # Làm cho không bắt buộc
    #     self.fields['is_verified'].required = False  # Làm cho không bắt buộc