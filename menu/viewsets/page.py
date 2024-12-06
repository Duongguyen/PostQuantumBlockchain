from rest_framework import viewsets, filters
from menu.models import TitlePage, New
from menu.viewsets.factory import TransactionPagination
from menu.serializers.blockchain import TitlePageSerializer, NewSerializer
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend


class TitlePageViewset(viewsets.ModelViewSet):
    queryset = TitlePage.objects.all()
    serializer_class = TitlePageSerializer
    pagination_class = TransactionPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['title']
    search_fields = ['title']


class NewViewset(viewsets.ModelViewSet):
    queryset = New.objects.all()
    serializer_class = NewSerializer
    pagination_class = TransactionPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['summary']
    search_fields = ['summary']