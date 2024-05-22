import time
from django.shortcuts import render, redirect

from ...form.transaction.form import TransactionForm
from ...models import User, Transaction
from ..blockchain.create import create_blockchain_use_case
from ...utils.common.security import mine, check_valid_mine
from django.utils import timezone


def render_templates(request):
    return render(request, 'index.html')


def sell_crypto(request):
    return render(request, 'sell_crypto.html')


def mine_crypto(request):
    return render(request, 'mine.html')


def create_transaction_use_case(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            #Thay uuid() vào
            form = TransactionForm(request.POST)
            a = form['from_send'].value()
            get_user = User.objects.get(username=a)
            if (form.is_valid() and float(form['amount'].value()) <= float(get_user.balance) - 0.1 and
                    form['destination'].value() and form['amount'].value()):

                form.save()
                handle = create_blockchain_use_case(from_send=form['from_send'].value(),
                                                    destination=form['destination'].value(),
                                                    amount=form['amount'].value(),
                                                    create_at=form['created_at'].value(),
                                                    hash_mine="")
                return render(request, 'index.html')
            else:
                return render(request, '401.html')
        else:
            return render(request, '500.html')


def mining_crypto(request):
    start_time = time.time()
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = TransactionForm(request.POST)
            if form.is_valid():
                timestamp = timezone.now()
                text_timestamp = str(timestamp)
                data = {
                    "from_send": form['from_send'].value(),
                    # "timestamp": text_timestamp
                }
                handle = check_valid_mine(data, form['header'].value())
                if handle and form['header'].value():
                    get_user = User.objects.get(username=form['from_send'].value())
                    handle_mine_blockchain = create_blockchain_use_case(from_send=form['from_send'].value(),
                                                                        amount=5,
                                                                        create_at=timestamp,
                                                                        destination="",
                                                                        hash_mine=handle)
                    end_time = time.time()
                    print(f"Thời gian chạy: {end_time - start_time} giây")
                    return render(request, 'mine_success.html')

                else:
                    return render(request, '401.html')
            else:
                return render(request, '401.html')
        else:
            return render(request, '500.html')
