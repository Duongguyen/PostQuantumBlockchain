from rest_framework import routers
from ...viewsets.transaction import TransactionViewset

router = routers.DefaultRouter()
router.register('API', TransactionViewset)
