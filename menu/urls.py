from django.urls import path, include
from .views.transaction.views import render_templates, sell_crypto, create_transaction_use_case

urlpatterns = [
    path('', render_templates, name='base'),
    path('sell_crypto/', sell_crypto, name='sell_crypto'),
    path('POST/transaction/', create_transaction_use_case, name='transaction'),
]
