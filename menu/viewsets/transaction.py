from rest_framework import viewsets, filters
from menu.models import Transaction, TitlePage, New
from menu.viewsets.factory import TransactionPagination
from menu.serializers.transaction import TransactionSerializer
from menu.serializers.blockchain import TitlePageSerializer, NewSerializer
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend


class TransactionViewset(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    pagination_class = TransactionPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['from_send', 'destination']
    search_fields = ['from_send']
    ordering_fields = ['create_at']


