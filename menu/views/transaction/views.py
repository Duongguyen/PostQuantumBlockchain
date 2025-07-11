import json
import time
import hashlib
from datetime import datetime, timedelta

import requests

from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.utils.timezone import now

from ...form.transaction.form import TransactionForm, CreateUserForm, AccountForm
from ...models import Account, New, TitlePage, Blockchains, Transaction
from ..blockchain.create import create_blockchain_use_case
from ...sphincs_python.package.sphincs import Sphincs
from ...utils.common.security import mine, check_valid_mine, hash_mine, check_valid_mine_sph
from .utils import email_verification_token, select_key
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, logout, login
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from ...utils.common.security import encrypt_aes_256, decrypt_aes_256
from .utils import sign_transactions
from django.core.cache import cache

from pqcrypto.pqcrypto.sign.sphincs_sha256_128s_simple import generate_keypair, sign, verify
from pqcrypto.pqcrypto.config import PDD_SEA, SK_SEA, NONCE

from .transactions import generate_otp


def render_templates(request):
    if request.user.is_authenticated and request.user.username != 'admin':
        return render(request, 'index.html')


def sell_crypto(request):
    if request.user.is_authenticated and request.user.username != 'admin':
        return render(request, 'sell_coin.html')


def mine_crypto(request):
    if request.user.is_authenticated and request.user.username != 'admin':
        return render(request, 'mine.html')


def information(request):
    return render(request, 'information.html')

def guide(request):
    return render(request, 'guide.html')

def solutions_view(request):
    return render(request, 'solutions.html')

def base(request):
    user_not_login = "show"
    user_login = "hidden"
    public_key_hex = ""
    decrypt_key_hex = ""

    if request.user.is_authenticated and request.user.username != 'admin':
        user_not_login = "hidden"
        user_login = "show"
        decrypt_key_hex, public_key_hex = select_key(request.user.id)

    return render(request, 'index.html', {
        'user_not_login': user_not_login,
        'user_login': user_login,
        'public_key': public_key_hex,
        'private_key': decrypt_key_hex
    })

def login_base(request):
    # Lấy dữ liệu dùng chung cho cả đã đăng nhập và chưa đăng nhập
    news_list = New.objects.all().order_by('-id')[:5]
    title_list = TitlePage.objects.all()
    for title in title_list:
        title.split_title = title.title.split(' ', 1)

    # Nếu người dùng đã đăng nhập và không phải admin
    if request.user.is_authenticated and request.user.username != 'admin':
        user_account = Account.objects.get(user_id=request.user.id)
        decrypt_key_hex, public_key_hex = select_key(request.user.id)

        return render(request, 'index.html', {
            'news_list': news_list,
            'title_list': title_list,
            'username': request.user.username,
            'user_account': user_account,
            'public_key': public_key_hex,
            'private_key': decrypt_key_hex,
            'is_authenticated': True
        })

    # Nếu là phương thức POST, xử lý đăng nhập
    if request.method == "POST":
        recaptcha_response = request.POST.get('g-recaptcha-response')
        data = {
            'secret': '6LdCS4QqAAAAAP54R6_B7rZ8Z00PTqUwehFqHlgu',
            'response': recaptcha_response
        }
        recaptcha_verify_url = "https://www.google.com/recaptcha/api/siteverify"
        result = requests.post(recaptcha_verify_url, data=data).json()

        if not result.get('success'):
            messages.error(request, 'Invalid reCAPTCHA. Please try again.')
            return render(request, 'login.html')

        username_check = request.POST.get('username')
        password_check = request.POST.get('password')
        user = authenticate(request, username=username_check, password=password_check)

        if user:
            login(request, user)
            return redirect('homepage')
        else:
            messages.info(request, 'User or password is not correct!')

    # Nếu chưa đăng nhập và không phải POST, hiển thị index.html dạng khách
    return render(request, 'index.html', {
        'news_list': news_list,
        'title_list': title_list,
        'is_authenticated': False
    })


def news_detail(request, news_id):
    news = get_object_or_404(New, id=news_id)
    user = get_object_or_404(User, id=news.user_id)
    return render(request, 'news_detail.html', {'news_item': news, 'username': user.username})


@login_required
@csrf_exempt
def toggle_like(request, news_id):
    if request.method == "POST":
        news = get_object_or_404(New, id=news_id)
        user_id = request.user.id

        if user_id in news.liked_users:
            news.liked_users.remove(user_id)
            news.like -= 1
        else:
            news.liked_users.append(user_id)
            news.like += 1

        news.save()

        return JsonResponse({'success': True, 'like_count': news.like})

    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=400)

def register(request):
    return render(request, 'sign_up.html')

def login_session(request):
    return render(request, 'login.html')

def log_out(request):
    logout(request)
    return redirect('homepage')

def send_verification_email(user, request):
    current_site = get_current_site(request)
    mail_subject = 'Activate your account'
    token = email_verification_token.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))

    # In ra để kiểm tra
    print(f"UID: {uid}, Token: {token}")

    verification_url = f'https://{current_site.domain}/verify-email/{uid}/{token}/'
    email_content = render_to_string('email_verification.html', {
        'user': user,
        'verification_url': verification_url,
    })

    send_mail(
        mail_subject,
        '',
        'bitcoinvietnam1811@gmail.com',
        [user.email],
        html_message=email_content,
        fail_silently=False,
    )

def process_register(request):
    if request.user.is_authenticated and request.user.username != 'admin':
        return render(request, 'index.html')
    if request.method == "POST":
        recaptcha_response = request.POST.get('g-recaptcha-response')
        data = {
            'secret': '6LdCS4QqAAAAAP54R6_B7rZ8Z00PTqUwehFqHlgu',  # Thay YOUR_SECRET_KEY bằng Secret Key từ Google
            'response': recaptcha_response
        }
        recaptcha_verify_url = "https://www.google.com/recaptcha/api/siteverify"
        result = requests.post(recaptcha_verify_url, data=data).json()

        if not result.get('success'):
            messages.error(request, 'Invalid reCAPTCHA. Please try again.')
            return render(request, 'login.html')

        user_form = CreateUserForm(request.POST)
        account_form = AccountForm(request.POST)
        if user_form.is_valid():
            if account_form.is_valid():
                username = user_form.cleaned_data['username']
                firstname = user_form.cleaned_data['first_name']
                lastname = user_form.cleaned_data['last_name']
                email = user_form.cleaned_data['email']
                password1 = user_form.cleaned_data['password1']
                password2 = user_form.cleaned_data['password2']
                phone = account_form.cleaned_data['phone']
                birthday = account_form.cleaned_data['birthday']
                gender = account_form.cleaned_data['gender']

                if password1 != password2:
                    messages.error(request, "Passwords do not match!")
                    return render(request, 'sign_up.html', {'form': user_form})

                if User.objects.filter(username=username).exists():
                    messages.error(request, "Username already exists!")
                    return render(request, 'sign_up.html', {'form': user_form})

                if User.objects.filter(email=email).exists():
                    messages.error(request, "Email already exists!")
                    return render(request, 'sign_up.html', {'form': user_form})
                user = User(
                    username=username,
                    first_name=firstname,
                    last_name=lastname,
                    email=email,
                    is_active=False,
                )
                user.set_password(password1)
                user.save()
                public_key, secret_key = generate_keypair()

                public_key_hex = public_key.hex()
                secret_key_hex = secret_key.hex()

                secret_key_bytes = bytes.fromhex(secret_key_hex)

                sk_sea_bytes_hex = bytes.fromhex(SK_SEA)
                pdd_sea_bytes_hex = bytes.fromhex(PDD_SEA)

                encrypt_key = encrypt_aes_256(secret_key_bytes, sk_sea_bytes_hex, pdd_sea_bytes_hex)
                encrypt_key_hex = encrypt_key.hex()
                user_account = User.objects.get(username=username)
                account = Account(
                    user=user,
                    address_wallet=public_key_hex,
                    birthday=birthday,
                    gender=gender,
                    phone=phone,
                    is_verified=False,
                    private_key=encrypt_key_hex,
                    user_id=user_account.id,
                    balance=5,
                )
                print("3")
                account.save()
                send_verification_email(user, request)

                messages.success(request, "Vui lòng kiểm tra email của bạn để xác thực tài khoản!")
                return redirect('homepage')

        else:
            messages.error(request, "Đăng ký không thành công! Vui lòng kiểm tra lại.")
            return render(request, 'sign_up.html', {'form': user_form})

    form = CreateUserForm()
    return render(request, 'sign_up.html', {'form': form})


def authenticity_mine(request):
    start_time = time.time()
    if request.user.is_authenticated and request.user.username != 'admin':
        if request.method == 'POST':
            form = TransactionForm(request.POST)
            if form.is_valid():
                otp = generate_otp()
                expiration_time = now() + timedelta(minutes=5)

                cache.set(f"otp_{request.user.id}", otp, timeout=300)
                cache.set(f"otp_{request.user.id}_expiration", expiration_time, timeout=300)

                dt = datetime.fromisoformat(str(now()))
                result = dt.strftime("%Y-%m-%d %H:%M:%S")

                print(form['from_send'].value())

                get_user_account = Account.objects.get(address_wallet=form['from_send'].value())
                get_user = User.objects.get(id=get_user_account.user_id)

                send_mail(
                    subject="Your OTP for Mine Authentication",
                    message=f"Your OTP is: {otp}. It will expire in 5 minutes."
                            f"Nonce number: {form['header'].value()}, "
                            f"Address to receive rewards: {form['from_send'].value()}, "
                            f"hash_session: {form['hash_session'].value()}",
                    from_email="bitcoinvietnam1811@gmail.com",
                    recipient_list=[get_user.email],
                )

                request.session['pending_transaction'] = form.cleaned_data

                return redirect('otp_verification_mine')
            else:
                return render(request, '401.html', {'error': 'Invalid transaction details.'})
        else:
            return render(request, '500.html')
    return redirect('login')


def otp_verification_mine(request):
    if request.user.is_authenticated and request.user.username != 'admin':
        print("000")
        if request.method == 'POST':
            print("111")
            otp_input = request.POST.get('otp_code')
            cached_otp = cache.get(f"otp_{request.user.id}")
            expiration_time = cache.get(f"otp_{request.user.id}_expiration")
            time_remaining = (expiration_time - now()).total_seconds() if expiration_time else 0

            if cached_otp and otp_input == cached_otp:
                print("222")
                transaction_data = request.session.get('pending_transaction')
                if transaction_data:
                    form = TransactionForm(transaction_data)
                    if form.is_valid():
                        data_session = Transaction.objects.get(hash_session=form['hash_session'].value())
                        created_at_str = str(data_session.created_at)

                        created_at_dt = datetime.fromisoformat(created_at_str.split('+')[0])

                        formatted_time = created_at_dt.strftime('%Y-%m-%d %H:%M:%S')
                        data = {
                            "from_send": form['from_send'].value(),
                            "amount": data_session.amount,
                            "timestamp": formatted_time
                        }
                        print(data)
                        handle = check_valid_mine_sph(str(data), int(form['header'].value()))
                        account_info = Account.objects.get(user_id=request.user.id)

                        if handle and form['header'].value():
                            print("333")
                            dt = datetime.fromisoformat(str(now()))
                            result = dt.strftime("%Y-%m-%d %H:%M:%S")

                            data_block = account_info.address_wallet + "," + "none" + "," + "1" + "," + result + "," + str(form['header'].value())
                            data_bytes = data_block.encode('utf-8')

                            sk_sea_bytes_hex = bytes.fromhex(SK_SEA)
                            pdd_sea_bytes_hex = bytes.fromhex(PDD_SEA)
                            encrypt_data = encrypt_aes_256(data_bytes, sk_sea_bytes_hex, pdd_sea_bytes_hex)

                            signature_hex, data_sign = sign_transactions(encrypt_data, request.user.id)

                            # data_bytes_block = data_block.encode('utf-8')
                            encrypt_data_block = encrypt_aes_256(data_bytes, sk_sea_bytes_hex, pdd_sea_bytes_hex)
                            handle_mine_blockchain = create_blockchain_use_case(encrypt_data_block=encrypt_data_block,
                                                                hash_mine=handle,
                                                                user_id=request.user.id,
                                                                signature_hex=signature_hex,
                                                                data=data_sign)

                            end_time = time.time()
                            # print(f"Thời gian chạy: {end_time - start_time} giây")
                            return render(request, 'mine_success.html')
                        else:
                            return render(request, '401.html')
                    else:
                        return render(request, '401.html')
                else:
                    return render(request, '500.html')

            elif time_remaining > 0:
                # OTP sai nhưng vẫn còn thời gian
                error_message = "OTP is incorrect, please try again."
                return render(request, 'otp_verification_mine.html', {'error_message': error_message})

            else:
                # Hết thời gian
                cache.delete(f"otp_{request.user.id}")
                cache.delete(f"otp_{request.user.id}_expiration")
                messages.error(request, "OTP đã hết hạn. Vui lòng yêu cầu giao dịch mới.")
                #sua lai toan bo redirect
                return redirect('transaction_page')

        return render(request, 'otp_verification_mine.html')
    return render(request, 'login.html')

def mining_page(request):
    if request.user.is_authenticated and request.user.username != 'admin':
        return render(request, 'mining.html')


def verify_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and email_verification_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Xác thực tài khoản thành công!")
        return render(request, 'login.html')
    else:
        messages.error(request, "Liên kết xác thực không hợp lệ hoặc đã hết hạn!")
        return render(request, 'sign_up.html')

@csrf_exempt
def mining_crypto_sph(request):
    if request.method == "POST":
        try:
            # NONCE = '00000'
            nonce_base = 0
            data = json.loads(request.body)
            transactions = data['transactions']
            block = json.dumps(transactions) + str(nonce_base)
            new_hash = hash_mine(block)
            print(str(NONCE))
            while not new_hash.startswith(str(NONCE)):
                nonce_base += 1
                block = json.dumps(transactions) + str(nonce_base)
                new_hash = hash_mine(block)
            #     print(nonce_base)
            #     print(new_hash)
            #     print(block)
            #
            # print(new_hash)
            return JsonResponse({"success": True, "nonce": nonce_base})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    return JsonResponse({"success": False, "error": "Invalid request"})

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def account_details(request):
    public_key, secret_key = generate_keypair()

    public_key_hex = public_key.hex()  # Chuyển đổi sang dạng hex để hiển thị
    secret_key_hex = secret_key.hex()

    return render(request, 'base.html', {
        'public_key': public_key_hex,
        'private_key': secret_key_hex
    })