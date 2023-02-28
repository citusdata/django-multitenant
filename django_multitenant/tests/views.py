from django_multitenant.views import TenantModelViewSet
from .models import Account
from .serializers import AccountSerializer
from rest_framework import permissions

class AccountViewSet(TenantModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """

    model_class = Account
    serializer_class = AccountSerializer
    permission_classes = [permissions.IsAuthenticated]