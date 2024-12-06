from rest_framework import routers
from ...viewsets.transaction import TransactionViewset
from ...viewsets.page import TitlePageViewset, NewViewset

router = routers.DefaultRouter()

router.register('transactions', TransactionViewset)
router.register('titles', TitlePageViewset)
router.register('news', NewViewset)
