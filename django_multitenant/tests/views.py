from django_multitenant.views import TenantModelViewSet
from .models import Store
from .serializers import StoreSerializer
from rest_framework import permissions


class StoreViewSet(TenantModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """

    model_class = Store
    serializer_class = StoreSerializer
    permission_classes = [permissions.IsAuthenticated]
