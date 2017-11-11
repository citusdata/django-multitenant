import uuid
from django.utils import timezone
from django.db import models
from djmoney.models.fields import MoneyField
from collections import OrderedDict
#import stores.middleware
#from stores.middleware import *
import django_multitenant
from django_multitenant import *
import pdb


def autoTimestamp():
    # TODO: force a real database column default like "NOW"
    return models.DateTimeField(editable=False, default=timezone.now)

class Store(models.Model):
    name = models.CharField(max_length=255)
    tenant_id='id'

class Product(TenantModel):
    store = models.ForeignKey(Store)
    tenant_id='store_id'

    def get_tenant():
        return self.store

    name = models.CharField(max_length=255)
    description = models.TextField()
    class Meta(object):
        unique_together = ["id", "store"]

class Purchase(TenantModel):
    store = models.ForeignKey(Store)
    tenant_id='store_id'
    product = models.ForeignKey(Product,
        db_constraint=False,
        db_index=False,
    )
    quantity = models.IntegerField(default=0)
    class Meta(object):
        unique_together = ["id", "store"]

# TODO: add a Customer model
