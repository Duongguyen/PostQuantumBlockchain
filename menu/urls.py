from django.urls import path, include

from .utils.common.time_system import naive_now
from .views.transaction.views import base, sell_crypto,\
    create_transaction_use_case, mine_crypto, mining_crypto, register, login_base, log_out, process_register, render_templates, verify_email, news_detail

urlpatterns = [
    path('', base, name='base'),
    path('start/', render_templates, name='start'),
    path('sell_crypto/', sell_crypto, name='sell_crypto'),
    path('mine/', mine_crypto, name='mine_crypto'),
    path('POST/transaction/', create_transaction_use_case, name='transaction'),
    path('POST/mining/', mining_crypto, name='mining'),
    path('login/', login_base, name="login"),
    path('register/', register, name="register"),
    path('process_register/', process_register, name="process_register"),
    path('logout/', log_out, name="logout"),
    path('verify-email/<str:uidb64>/<str:token>/', verify_email, name='verify_email'),
    path('news/<int:news_id>/', news_detail, name='news_detail'),
]
