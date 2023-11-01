from django.shortcuts import render
from django.shortcuts import render, redirect

from ...form.transaction.form import TransactionForm
from ...models import User, Transaction
from ..blockchain.create import create_blockchain_use_case


def render_templates(request):
    return render(request, 'index.html')


def sell_crypto(request):
    return render(request, 'sell_crypto.html')


def create_transaction_use_case(request):
    print("e")
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = TransactionForm(request.POST)
            a = form['from_send'].value()
            get_user = User.objects.get(username=a)
            if form.is_valid() and float(form['amount'].value()) <= float(get_user.balance):
                form.save()
                handle = create_blockchain_use_case(from_send=form['from_send'].value(),
                                                    destination=form['destination'].value(),
                                                    amount=form['amount'].value())
                return render(request, 'index.html')
            else:
                return render(request, '401.html')
        else:
            return render(request, '500.html')




