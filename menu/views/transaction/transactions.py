import random
import string
import requests
from datetime import timedelta

from django.contrib.auth import get_user
from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.utils import timezone

from ...form.transaction.form import TransactionForm
from ...models import Account, Transaction
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from ..blockchain.create import create_blockchain_use_case
from django.core.cache import cache
from django.contrib import messages
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required


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
            a = form['from_send'].value()
            try:
                get_user = User.objects.get(username=a)
                get_detail_user = Account.objects.get(user_id=get_user.id)
            except User.DoesNotExist:
                return render(request, '401.html', {'error': 'User does not exist.'})

            if (form.is_valid() and
                    float(form['amount'].value()) <= float(get_detail_user.balance) - 0.1 and
                    get_user.check_password(form['pass_check'].value()) and
                    form['amount'].value()):

                # Generate OTP and expiration time
                otp = generate_otp()
                expiration_time = now() + timedelta(minutes=5)  # OTP valid for 5 minutes

                # Save OTP and expiration time to cache
                cache.set(f"otp_{request.user.id}", otp, timeout=300)
                cache.set(f"otp_{request.user.id}_expiration", expiration_time, timeout=300)

                # Send OTP to user's email
                send_mail(
                    subject="Your OTP for Transaction",
                    message=f"Your OTP is: {otp}. It will expire in 5 minutes.",
                    from_email="admin@example.com",
                    recipient_list=[get_user.email],
                )

                # Save transaction details temporarily in the session
                request.session['pending_transaction'] = form.cleaned_data

                # Redirect to OTP verification page
                return redirect('otp_verification_page')

            else:
                return render(request, '401.html', {'error': 'Invalid transaction details.'})
        else:
            return render(request, '500.html')
    return redirect('login')


def otp_verification_view(request):
    if request.method == 'POST':
        otp_input = request.POST.get('otp_code')
        cached_otp = cache.get(f"otp_{request.user.id}")
        expiration_time = cache.get(f"otp_{request.user.id}_expiration")
        time_remaining = (expiration_time - now()).total_seconds() if expiration_time else 0

        if cached_otp and otp_input == cached_otp:
            # OTP is valid
            transaction_data = request.session.get('pending_transaction')
            if transaction_data:
                # Save transaction to database
                form = TransactionForm(transaction_data)
                if form.is_valid():
                    # Lấy from_key dựa trên user
                    from_send_username = form.cleaned_data['from_send']
                    get_user_id = User.objects.get(username=from_send_username)
                    get_detail_user = Account.objects.get(user_id=get_user_id.id)
                    from_key_value = get_detail_user.address_wallet

                    transaction = form.save(commit=False)
                    transaction.from_key = from_key_value
                    transaction.save()

                    del request.session['pending_transaction']
                    cache.delete(f"otp_{request.user.id}")
                    cache.delete(f"otp_{request.user.id}_expiration")
                    messages.success(request, "Transaction completed successfully.")
                    return redirect('pending_transactions')

            messages.error(request, "Error processing the transaction.")
            return redirect('transaction_page')

        elif time_remaining > 0:
            # OTP is invalid, but still active
            error_message = f"Invalid OTP. Time remaining: {int(time_remaining)} seconds."
        else:
            # OTP has expired
            error_message = "OTP has expired. Please request a new transaction."
            cache.delete(f"otp_{request.user.id}")
            cache.delete(f"otp_{request.user.id}_expiration")
            return redirect('transaction_page')

        # Render the page with error message
        return render(request, 'otp_verification.html', {'error_message': error_message})

    return render(request, 'otp_verification.html')

@login_required
def pending_transactions_view(request):
    username = request.user.username
    pending_transactions = Transaction.objects.filter(status_sell=False).exclude(from_send=username).order_by('-created_at')
    return render(request, 'pending_transactions.html', {'pending_transactions': pending_transactions})


@login_required
def transaction_detail(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id)

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
            return redirect('transaction_detail')

        if 'password' in request.POST:
            password = request.POST.get('password')

            # Kiểm tra mật khẩu người dùng
            if request.user.check_password(password):
                # Tạo OTP và gửi email
                otp = generate_otp()
                send_mail(
                    'Your OTP Code',
                    f'Your OTP code is {otp}. It is valid for 5 minutes.',
                    'bitcoinvietnam1811@gmail.com',
                    [request.user.email],
                    fail_silently=False,
                )

                # Lưu OTP vào cache
                cache.set(f"otp_{request.user.id}", otp, timeout=300)  # OTP có hiệu lực trong 5 phút
                cache.set(f"otp_{request.user.id}_expiration", timezone.now() + timedelta(minutes=5), timeout=300)

                # Chuyển đến giao diện nhập OTP
                return render(request, 'verification_sell_otp.html', {'transaction': transaction})

            else:
                # Hiển thị thông báo lỗi
                messages.error(request, 'Invalid password. Please try again.')

    # Hiển thị giao diện nhập mật khẩu
    return render(request, 'transaction_detail.html', {'transaction': transaction})

@login_required
def process_sell(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id)
    return render(request, 'process_sell.html', {'transaction': transaction})

def otp_verification_sell(request, transaction_id):
    if request.method == 'POST':
        otp_input = request.POST.get('otp_code')
        cached_otp = cache.get(f"otp_{request.user.id}")
        expiration_time = cache.get(f"otp_{request.user.id}_expiration")
        time_remaining = (expiration_time - now()).total_seconds() if expiration_time else 0

        if cached_otp and otp_input == cached_otp:
            try:
                transaction = get_object_or_404(Transaction, id=transaction_id, status_sell=False)
                transaction.status_sell = True
                username = request.user.username
                get_user_id = User.objects.get(username=username)
                get_detail_user = Account.objects.get(user_id=get_user_id.id)
                address_wallet = get_detail_user.address_wallet
                transaction.destination_key = address_wallet
                transaction.destination = username
                transaction.save()

                created_at_str = format(transaction.created_at, 'Y-m-d H:i:s')

                handle = create_blockchain_use_case(from_send=username,
                                                    destination=transaction.destination,
                                                    amount=transaction.amount,
                                                    create_at=created_at_str,
                                                    hash_mine="",
                                                    user_id=get_user_id.id)
                messages.success(request, "Transaction completed successfully.")
                return redirect('pending_transactions')
            except Exception as e:
                messages.error(request, f"Error saving transaction: {e}")
                return redirect('pending-transactions')

        elif time_remaining > 0:
            # OTP không hợp lệ, nhưng vẫn còn thời gian hiệu lực
            error_message = f"Invalid OTP. Time remaining: {int(time_remaining)} seconds."
        else:
            # OTP đã hết hạn
            error_message = "OTP has expired. Please request a new transaction."
            cache.delete(f"otp_{request.user.id}")
            cache.delete(f"otp_{request.user.id}_expiration")
            return redirect('pending_transactions')

        # Render trang nhập OTP với thông báo lỗi
        return render(request, 'otp_verification.html', {'error_message': error_message})

    return render(request, 'otp_verification.html')


def mark_as_sold(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id, status_sell=False)
    transaction.status_sell = True
    username = request.user.username
    get_user_id = User.objects.get(username=username)
    get_detail_user = Account.objects.get(user_id=get_user_id.id)
    address_wallet = get_detail_user.address_wallet
    transaction.destination_key = address_wallet
    transaction.destination = username
    transaction.save()

    created_at_str = format(transaction.created_at, 'Y-m-d H:i:s')

    handle = create_blockchain_use_case(from_send=username,
                                        destination=transaction.destination,
                                        amount=transaction.amount,
                                        create_at=created_at_str,
                                        hash_mine="",
                                        user_id=get_user_id.id)
    return redirect('pending_transactions')