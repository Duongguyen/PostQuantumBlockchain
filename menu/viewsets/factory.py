from rest_framework.pagination import PageNumberPagination


class TransactionPagination(PageNumberPagination):
    page_size = 8
    page_size_query_param = 'page_size'

