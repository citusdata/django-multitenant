import logging

from django.db import models

from .mixins import TenantManagerMixin, TenantModelMixin

from .utils import (
    set_current_tenant,
    get_current_tenant,
    get_model_by_db_table,
    get_tenant_column,
)

logger = logging.getLogger(__name__)


class TenantManager(TenantManagerMixin, models.Manager):
    # Below is the manager related to the above class.
    pass


class TenantModel(TenantModelMixin, models.Model):
    # Abstract model which all the models related to tenant inherit.

    objects = TenantManager()

    class Meta:
        abstract = True
