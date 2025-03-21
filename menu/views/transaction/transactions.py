import random
import string
import requests
from datetime import timedelta, datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.utils import timezone

from ...form.transaction.form import TransactionForm
from ...models import Account, Transaction
from django.contrib.auth.models import User
from ..blockchain.create import create_blockchain_use_case
from django.core.cache import cache
from django.contrib import messages
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required
from ...utils.common.security import SHA256
from .utils import sign_transactions
from pqcrypto.pqcrypto.config import PDD_SEA, SK_SEA
from ...utils.common.security import encrypt_aes_256, decrypt_aes_256


def generate_otp():
    """Generate a random 6-digit OTP."""
    return ''.join(random.choices(string.digits, k=6))


def create_transaction_use_case(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            recaptcha_response = request.POST.get('g-recaptcha-response')
            data = {
                'secret': '6LdCS4QqAAAAAP54R6_B7rZ8Z00PTqUwehFqHlgu',  # Thay YOUR_SECRET_KEY bằng Secret Key từ Google
                'response': recaptcha_response
            }
            recaptcha_verify_url = "https://www.google.com/recaptcha/api/siteverify"
            result = requests.post(recaptcha_verify_url, data=data).json()

            if not result.get('success'):
                messages.error(request, 'Invalid reCAPTCHA. Please try again.')
                return redirect('transaction')

            form = TransactionForm(request.POST)
            name = request.user.username
            try:
                get_user = User.objects.get(username=name)
                get_detail_user = Account.objects.get(user_id=get_user.id)
                get_destination = Account.objects.get(address_wallet=form['destination'].value())
            except User.DoesNotExist:
                return render(request, '401.html', {'error': 'User does not exist.'})
            print(get_destination.address_wallet)
            print(get_detail_user.address_wallet)

            if (form.is_valid() and
                    float(form['amount'].value()) <= float(get_detail_user.balance) - 0.1 and
                    get_user.check_password(form['pass_check'].value()) and
                    form['amount'].value() and get_destination.address_wallet != get_detail_user.address_wallet):

                otp = generate_otp()
                expiration_time = now() + timedelta(minutes=5)

                cache.set(f"otp_{request.user.id}", otp, timeout=300)
                cache.set(f"otp_{request.user.id}_expiration", expiration_time, timeout=300)

                dt = datetime.fromisoformat(str(now()))
                result = dt.strftime("%Y-%m-%d %H:%M:%S")

                send_mail(
                    subject="Your OTP for Transaction",
                    message=f"Your OTP is: {otp}. It will expire in 5 minutes."
                            f"receiver: {form['destination'].value()}, "
                            f"amount: {form['amount'].value()}, created_at: {result}, "
                            f"hash_session: {SHA256(form['destination'].value() + str(float(form['amount'].value())) + result)}",
                    from_email="bitcoinvietnam1811@gmail.com",
                    recipient_list=[get_user.email],
                )

                request.session['pending_transaction'] = form.cleaned_data

                return redirect('otp_verification_page', result=result)
            else:
                return render(request, '401.html', {'error': 'Invalid transaction details.'})
        else:
            return render(request, '500.html')
    return redirect('login')


def otp_verification_view(request, result):
    if request.user.is_authenticated:
        if request.method == 'POST':
            otp_input = request.POST.get('otp_code')
            cached_otp = cache.get(f"otp_{request.user.id}")
            expiration_time = cache.get(f"otp_{request.user.id}_expiration")
            time_remaining = (expiration_time - now()).total_seconds() if expiration_time else 0

            if cached_otp and otp_input == cached_otp:
                transaction_data = request.session.get('pending_transaction')
                if transaction_data:
                    form = TransactionForm(transaction_data)
                    if form.is_valid():
                        # from_send_username = request.user.username
                        get_user_send = User.objects.get(username=request.user.username)
                        # get_destination_receiver = User.objects.get(username=form['destination'].value())
                        get_detail_user = Account.objects.get(user_id=get_user_send.id)
                        # from_key_value = get_detail_user.address_wallet

                        transaction = form.save(commit=False)

                        hash_session_transaction = SHA256(get_detail_user.address_wallet + str(transaction.amount) + result)
                        transaction.from_send = get_detail_user.address_wallet
                        transaction.destination = form['destination'].value()
                        transaction.hash_session = hash_session_transaction
                        transaction.created_at = result
                        transaction.save()

                        data = get_detail_user.address_wallet + str(transaction.amount) + result
                        data_bytes = data.encode('utf-8')

                        sk_sea_bytes_hex = bytes.fromhex(SK_SEA)
                        pdd_sea_bytes_hex = bytes.fromhex(PDD_SEA)
                        encrypt_data = encrypt_aes_256(data_bytes, sk_sea_bytes_hex, pdd_sea_bytes_hex)

                        signature_hex, data_sign = sign_transactions(encrypt_data, get_user_send.id)

                        data_block = transaction.from_send + ',' + transaction.destination + ',' + str(transaction.amount) + ',' + result
                        data_bytes_block = data_block.encode('utf-8')
                        encrypt_data_block = encrypt_aes_256(data_bytes_block, sk_sea_bytes_hex, pdd_sea_bytes_hex)

                        handle = create_blockchain_use_case(encrypt_data_block=encrypt_data_block,
                                                            hash_mine="",
                                                            user_id=get_user_send.id,
                                                            signature_hex=signature_hex,
                                                            data=data_sign)
                        if handle:
                            cache.delete(f"otp_{request.user.id}")
                            cache.delete(f"otp_{request.user.id}_expiration")
                            alert = "Transaction completed, Let's start the next transaction"
                            messages.success(request, "Transaction completed, Let's start the next transaction")
                            return render(request, 'sell_coin.html', {"messages": alert})

                        alert = "Transaction failed, please try again"
                        messages.success(request, "Transaction failed, please try again")
                        return render(request, 'sell_coin.html', {"messages": alert})

                messages.error(request, "Error processing the transaction.")
                return redirect('transaction_page', {"result": result})

            elif time_remaining > 0:
                error_message = f"Invalid OTP. Time remaining: {int(time_remaining)} seconds."
            else:
                error_message = "OTP has expired. Please request a new transaction."
                cache.delete(f"otp_{request.user.id}")
                cache.delete(f"otp_{request.user.id}_expiration")
                return redirect('transaction_page', {"result": result})

            # Render the page with error message
            return render(request, 'otp_verification.html', {'error_message': error_message})

        return render(request, 'otp_verification.html', {"result": result})

@login_required
def pending_transactions_view(request):
    username = request.user.username
    pending_transactions = Transaction.objects.filter(status_sell=False)\
                                              .exclude(from_send=username)\
                                              .order_by('-created_at')
    return render(request, 'pending_transactions.html', {'pending_transactions': pending_transactions})


@login_required
def transaction_detail(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id)

    if request.method == 'POST':
        recaptcha_response = request.POST.get('g-recaptcha-response')
        data = {
            'secret': '6LdCS4QqAAAAAP54R6_B7rZ8Z00PTqUwehFqHlgu',
            'response': recaptcha_response
        }
        recaptcha_verify_url = "https://www.google.com/recaptcha/api/siteverify"
        result = requests.post(recaptcha_verify_url, data=data).json()

        if not result.get('success'):
            messages.error(request, 'Invalid reCAPTCHA. Please try again.')
            return render(request, 'process_sell.html', {'transaction': transaction})

        if 'password' in request.POST:
            password = request.POST.get('password')

            if request.user.check_password(password):
                otp = generate_otp()
                send_mail(
                    'Your OTP Code',
                    f'Your OTP code is {otp}. It is valid for 5 minutes.',
                    'bitcoinvietnam1811@gmail.com',
                    [request.user.email],
                    fail_silently=False,
                )

                cache.set(f"otp_{request.user.id}", otp, timeout=300)  # OTP có hiệu lực trong 5 phút
                cache.set(f"otp_{request.user.id}_expiration", timezone.now() + timedelta(minutes=5), timeout=300)

                return render(request, 'verification_sell_otp.html', {'transaction': transaction})

            else:
                messages.error(request, 'Invalid password. Please try again.')

    print(transaction_id)

    return render(request, 'process_sell.html', {'transaction': transaction})

@login_required
def process_sell(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id)
    return render(request, 'process_sell.html', {'transaction': transaction})


def my_transactions(request):
    transactions = Transaction.objects.filter(status_sell=True)
    return render(request, 'my_transactions.html', {'transactions': transactions})

# def mark_as_sold(request, transaction_id):
#     transaction = get_object_or_404(Transaction, id=transaction_id, status_sell=False)
#     transaction.status_sell = True
#     username = request.user.username
#     get_user_id = User.objects.get(username=username)
#     get_detail_user = Account.objects.get(user_id=get_user_id.id)
#     address_wallet = get_detail_user.address_wallet
#     transaction.destination_key = address_wallet
#     transaction.destination = username
#     transaction.save()
#
#     created_at_str = format(transaction.created_at, 'Y-m-d H:i:s')
#
#     handle = create_blockchain_use_case(from_send=username,
#                                         destination=transaction.destination,
#                                         amount=transaction.amount,
#                                         create_at=created_at_str,
#                                         hash_mine="",
#                                         user_id=get_user_id.id)
#     return redirect('pending_transactions')


# def otp_verification_sell(request, transaction_id):
#     if request.user.is_authenticated:
#         if request.method == 'POST':
#             otp_input = request.POST.get('otp_code')
#             cached_otp = cache.get(f"otp_{request.user.id}")
#             expiration_time = cache.get(f"otp_{request.user.id}_expiration")
#             time_remaining = (expiration_time - now()).total_seconds() if expiration_time else 0
#
#             if cached_otp and otp_input == cached_otp:
#                 try:
#                     transaction = get_object_or_404(Transaction, id=transaction_id, status_sell=False)
#                     transaction.status_sell = True
#                     username = request.user.username
#                     get_user_id = User.objects.get(username=username)
#                     get_detail_user = Account.objects.get(user_id=get_user_id.id)
#                     address_wallet = get_detail_user.address_wallet
#                     transaction.destination_key = address_wallet
#                     transaction.destination = username
#                     transaction.save()
#
#                     created_at_str = format(transaction.created_at, 'Y-m-d H:i:s')
#
#                     handle = create_blockchain_use_case(from_send=username,
#                                                         destination=transaction.destination,
#                                                         amount=transaction.amount,
#                                                         create_at=created_at_str,
#                                                         hash_mine="",
#                                                         user_id=get_user_id.id)
#                     messages.success(request, "Transaction completed, please continue to proceed with the transaction")
#                     return redirect('pending_transactions')
#                 except Exception as e:
#                     messages.error(request, f"Error saving transaction: {e}")
#                     return redirect('pending-transactions')
#
#             elif time_remaining > 0:
#                 # OTP không hợp lệ, nhưng vẫn còn thời gian hiệu lực
#                 error_message = f"Invalid OTP. Time remaining: {int(time_remaining)} seconds."
#             else:
#                 # OTP đã hết hạn
#                 error_message = "OTP has expired. Please request a new transaction."
#                 cache.delete(f"otp_{request.user.id}")
#                 cache.delete(f"otp_{request.user.id}_expiration")
#                 return redirect('pending_transactions')
#
#             # Render trang nhập OTP với thông báo lỗi
#             return render(request, 'otp_verification.html', {'error_message': error_message})
#
#         return render(request, 'otp_verification.html')



# def create_transaction_use_case(request):
#     if request.user.is_authenticated:
#         if request.method == 'POST':
#             recaptcha_response = request.POST.get('g-recaptcha-response')
#             data = {
#                 'secret': '6LdCS4QqAAAAAP54R6_B7rZ8Z00PTqUwehFqHlgu',  # Thay YOUR_SECRET_KEY bằng Secret Key từ Google
#                 'response': recaptcha_response
#             }
#             recaptcha_verify_url = "https://www.google.com/recaptcha/api/siteverify"
#             result = requests.post(recaptcha_verify_url, data=data).json()
#
#             if not result.get('success'):
#                 messages.error(request, 'Invalid reCAPTCHA. Please try again.')
#                 return redirect('transaction')
#
#             form = TransactionForm(request.POST)
#             a = form['from_send'].value()
#             try:
#                 get_user = User.objects.get(username=a)
#                 get_detail_user = Account.objects.get(user_id=get_user.id)
#             except User.DoesNotExist:
#                 return render(request, '401.html', {'error': 'User does not exist.'})
#
#             if (form.is_valid() and
#                     float(form['amount'].value()) <= float(get_detail_user.balance) - 0.1 and
#                     get_user.check_password(form['pass_check'].value()) and
#                     form['amount'].value()):
#
#                 # Generate OTP and expiration time
#                 otp = generate_otp()
#                 expiration_time = now() + timedelta(minutes=5)  # OTP valid for 5 minutes
#
#                 # Save OTP and expiration time to cache
#                 cache.set(f"otp_{request.user.id}", otp, timeout=300)
#                 cache.set(f"otp_{request.user.id}_expiration", expiration_time, timeout=300)
#
#                 dt = datetime.fromisoformat(str(now()))
#                 result = dt.strftime("%Y-%m-%d %H:%M:%S")
#
#                 send_mail(
#                     subject="Your OTP for Transaction",
#                     message=f"Your OTP is: {otp}. It will expire in 5 minutes. from_send: {form['from_send'].value()}, "
#                             f"amount: {form['amount'].value()}, created_at: {result}, "
#                             f"hash_session: {SHA256(form['from_send'].value() + str(float(form['amount'].value())) + result)}",
#                     from_email="bitcoinvietnam1811@gmail.com",
#                     recipient_list=[get_user.email],
#                 )
#
#                 # Save transaction details temporarily in the session
#                 request.session['pending_transaction'] = form.cleaned_data
#
#                 # Redirect to OTP verification page
#                 return redirect('otp_verification_page', result=result)
#             else:
#                 return render(request, '401.html', {'error': 'Invalid transaction details.'})
#         else:
#             return render(request, '500.html')
#     return redirect('login')