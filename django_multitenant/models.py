import logging

from django.db import models

from django.contrib.gis.db import models as gis_models

from .mixins import TenantManagerMixin, TenantModelMixin


logger = logging.getLogger(__name__)


class TenantManager(TenantManagerMixin, models.Manager):
    # Below is the manager related to the above class.
    pass


class TenantModel(TenantModelMixin, models.Model):
    # Abstract model which all the models related to tenant inherit.

    objects = TenantManager()

    class Meta:
        abstract = True


class GisTenantManager(TenantManagerMixin, gis_models.Manager):
    # Below is the manager related to the above class.
    pass


class GisTenantModel(TenantModelMixin, gis_models.Model):
    # Abstract model which all the models related to tenant inherit.

    objects = GisTenantManager()

    class Meta:
        abstract = True
