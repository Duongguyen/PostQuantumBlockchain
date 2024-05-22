from django import forms

from ...models import Transaction


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['from_key'].required = False
        self.fields['destination_key'].required = False
        self.fields['created_at'].required = False
        self.fields['header'].required = False
        self.fields['destination'].required = False
        self.fields['amount'].required = False
