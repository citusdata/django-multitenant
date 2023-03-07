

from django_multitenant.utils import set_current_tenant
from django_multitenant.models import TenantModel
from rest_framework import viewsets
from abc import abstractmethod


@abstractmethod
def get_tenant(request) -> TenantModel:
    pass


class TenantModelViewSet(viewsets.ModelViewSet):
    model_class = TenantModel

    def get_queryset(self):
        if self.request.user.is_anonymous:
            return self.model_class.objects.none()
        tenant = get_tenant(self.request)
        print("View Tenant", tenant)
        print("Model Class", self.model_class)
        set_current_tenant(tenant)
        list3 = self.model_class.objects.all()
        print("View List", list3)
        return list3
