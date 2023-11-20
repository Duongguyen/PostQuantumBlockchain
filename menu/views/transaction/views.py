from django.shortcuts import render, redirect

from ...form.transaction.form import TransactionForm
from ...models import User, Transaction
from ..blockchain.create import create_blockchain_use_case
from ...utils.common.security import mine


def render_templates(request):
    return render(request, 'index.html')


def sell_crypto(request):
    return render(request, 'sell_crypto.html')


def mine_crypto(request):
    return render(request, 'mine.html')


def mining_crypto(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = TransactionForm(request.POST)
            if form.is_valid():
                data = {
                    "from_send": form['from_send'].value(),
                    "destination": form['destination'].value(),
                    "amount": form['amount'].value(),
                }
                handle = mine(data, 2, form['created_at'].value())
                if handle:
                    get_user = User.objects.get(username=form['from_send'].value())
                    get_user.balance -= float(form['amount'].value())
                    get_user.save()
                    return render(request, 'mine_success.html')
                else:
                    return render(request, '401.html')
            else:
                return render(request, '401.html')
        else:
            return render(request, '500.html')


def create_transaction_use_case(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            #Thay uuid() vào
            form = TransactionForm(request.POST)
            a = form['from_send'].value()
            get_user = User.objects.get(username=a)
            if form.is_valid() and float(form['amount'].value()) <= float(get_user.balance):
                form.save()
                handle = create_blockchain_use_case(from_send=form['from_send'].value(),
                                                    destination=form['destination'].value(),
                                                    amount=form['amount'].value(),
                                                    create_at=form['created_at'].value())
                return render(request, 'index.html')
            else:
                return render(request, '401.html')
        else:
            return render(request, '500.html')




