import uuid

from django.db import models
from django.conf import settings

from django_multitenant.models import TenantModel
from django_multitenant.fields import TenantForeignKey
from django_multitenant.tests.models import Organization

if settings.USE_GIS:
    from django.contrib.gis.db import models as gis_models

    class OrganizationLocation(TenantModel):
        # import gis_models inline to

        id = gis_models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
        organization = TenantForeignKey(
            Organization, on_delete=models.CASCADE, related_name="locations"
        )
        tenant_id = "organization_id"

        location = gis_models.PointField()
