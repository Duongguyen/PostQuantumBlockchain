import time
import hashlib
import requests
import random
import string

from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.core.mail import send_mail
from ...form.transaction.form import TransactionForm, CreateUserForm, AccountForm
from ...models import BlockchainUser, Transaction, Account, New
from ..blockchain.create import create_blockchain_use_case
from ...utils.common.security import mine, check_valid_mine
from .utils import email_verification_token
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.core.cache import cache

def render_templates(request):
    if request.user.is_authenticated:
        return render(request, 'index.html')


def sell_crypto(request):
    if request.user.is_authenticated:
        return render(request, 'sell_crypto.html')


def mine_crypto(request):
    if request.user.is_authenticated:
        return render(request, 'mine.html')


def base(request):
    if request.user.is_authenticated:
        user_not_login = "hidden"
        user_login = "show"
        context = {'user_not_login': user_not_login,
                   'user_login': user_login,
                   # 'evolutions': evolutions
                   }

        return render(request, 'index.html', context)
    else:
        user_not_login = "show"
        user_login = "hidden"
        # form = RecapchaForm()
        context = {'user_not_login': user_not_login,
                   'user_login': user_login,
                   # "form": form
                   }

        return render(request, 'login.html', context)

def login_base(request):
    if request.user.is_authenticated:
        # Lấy danh sách tin tức từ cơ sở dữ liệu
        news_list = New.objects.all().order_by('-id')[:5]  # Lấy 5 tin tức mới nhất
        return render(request, 'index.html', {'news_list': news_list})

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

        username_check = request.POST.get('username')
        password_check = request.POST.get('password')

        user = authenticate(request, username=username_check, password=password_check)
        if user:
            login(request, user)
            news_list = New.objects.all().order_by('-id')[:5]  # Lấy 5 tin tức mới nhất
            return render(request, 'index.html', {'news_list': news_list})
        else:
            messages.info(request, 'user or pass not correct!')

    return render(request, 'login.html')


def news_detail(request, news_id):
    # Lấy bài viết từ cơ sở dữ liệu, nếu không tìm thấy sẽ trả về 404
    news = get_object_or_404(New, id=news_id)
    user = get_object_or_404(User, id=news.user_id)
    return render(request, 'news_detail.html', {'news_item': news, 'username': user.username})


@login_required
@csrf_exempt
def toggle_like(request, news_id):
    print("x")
    if request.method == "POST":
        news = get_object_or_404(New, id=news_id)
        user_id = request.user.id

        # Kiểm tra xem user đã thích bài viết chưa
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

def log_out(request):
    logout(request)
    return render(request, 'login.html')

def send_verification_email(user, request):
    current_site = get_current_site(request)
    mail_subject = 'Activate your account'
    token = email_verification_token.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))

    # In ra để kiểm tra
    print(f"UID: {uid}, Token: {token}")

    verification_url = f'http://{current_site.domain}/blockchains/verify-email/{uid}/{token}/'
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
    if request.user.is_authenticated:
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
                account = Account(
                    user=user,
                    address_wallet=hashlib.sha256(username.encode()).hexdigest(),
                    birthday=birthday,
                    gender=gender,
                    phone=phone,
                    is_verified=False,
                )

                account.save()
                send_verification_email(user, request)

                messages.success(request, "Vui lòng kiểm tra email của bạn để xác thực tài khoản!")
                return redirect('homepage')

        else:
            messages.error(request, "Đăng ký không thành công! Vui lòng kiểm tra lại.")
            return render(request, 'sign_up.html', {'form': user_form})

    form = CreateUserForm()
    return render(request, 'sign_up.html', {'form': form})

def mining_crypto(request):
    start_time = time.time()
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = TransactionForm(request.POST)
            if form.is_valid():
                timestamp = timezone.now()
                text_timestamp = str(timestamp)
                data = {
                    "from_send": request.user.username,
                    # "timestamp": text_timestamp
                }
                handle = check_valid_mine(data, form['header'].value())
                if handle and form['header'].value():
                    handle_mine_blockchain = create_blockchain_use_case(from_send=form['from_send'].value(),
                                                                        amount=5,
                                                                        create_at=timestamp,
                                                                        destination="",
                                                                        hash_mine=handle,
                                                                        user_id=request.user.id)
                    end_time = time.time()
                    print(f"Thời gian chạy: {end_time - start_time} giây")
                    return render(request, 'mine_success.html')
                else:
                    return render(request, '401.html')
            else:
                return render(request, '401.html')
        else:
            return render(request, '500.html')


# def create_transaction_use_case(request):
#     if request.user.is_authenticated:
#         if request.method == 'POST':
#             form = TransactionForm(request.POST)
#             a = form['from_send'].value()
#             get_user = User.objects.get(username=a)
#             get_detail_user = Account.objects.get(user_id=get_user.id)
#             if (form.is_valid() and float(form['amount'].value()) <= float(get_detail_user.balance) - 0.1 and
#                     get_user.check_password(form['pass_check'].value()) and form['amount'].value()):
#
#                 form.save()
#                 handle = create_blockchain_use_case(from_send=form['from_send'].value(),
#                                                     destination=form['destination'].value(),
#                                                     amount=form['amount'].value(),
#                                                     create_at=form['created_at'].value(),
#                                                     hash_mine="",
#                                                     user_id=get_user.id)
#                 return render(request, 'index.html')
#             else:
#                 return render(request, '401.html')
#         else:
#             return render(request, '500.html')


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

# def select_balance():
#     get_balance = BlockchainUser.objects.get(username=form['from_send'].value())


# class RegisterView(generics.GenericAPIView):
#     serializer_class = RegisterSerializer
#
#     def post(self, request):
#         user = request.data
#         serializer = self.serializer_class(data=user)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         user_data = serializer.data
#
#         user = BlockchainUser.objects.get(email=user_data['email'])
#
#         token = RefreshToken.for_user(user)
#
#         return Response(user_data, status=status.HTTP_201_CREATED)