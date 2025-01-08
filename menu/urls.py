from django.urls import path, include

from .views.transaction.views import (base, sell_crypto,\
    mine_crypto, mining_crypto, register, login_base, log_out, process_register,
                                      render_templates, verify_email, news_detail, toggle_like)
from .views.transaction.transactions import (create_transaction_use_case, otp_verification_view, pending_transactions_view,
                                             mark_as_sold, transaction_detail, otp_verification_sell, process_sell)

urlpatterns = [
    path('', base, name='base'),
    path('start/', render_templates, name='start'),
    path('sell_crypto/', sell_crypto, name='sell_crypto'),
    path('mine/', mine_crypto, name='mine_crypto'),
    path('POST/transaction/', create_transaction_use_case, name='transaction'),
    path('verification', otp_verification_view, name='otp_verification_page'),
    path('pending-transactions/', pending_transactions_view, name='pending_transactions'),
    path('verification_sell/<int:transaction_id>/', otp_verification_sell, name='otp_verification_sell'),
    path('transaction/<int:transaction_id>/', transaction_detail, name='transaction_detail'),
    path('process_sell/<int:transaction_id>/', process_sell, name='process_sell'),
    path('POST/mining/', mining_crypto, name='mining'),
    path('homepage/', login_base, name="homepage"),
    path('register/', register, name="register"),
    path('process_register/', process_register, name="process_register"),
    path('logout/', log_out, name="logout"),
    path('verify-email/<str:uidb64>/<str:token>/', verify_email, name='verify_email'),
    path('news/<int:news_id>/', news_detail, name='news_detail'),
    path('toggle-like/<int:news_id>/', toggle_like, name='toggle_like'),
]
