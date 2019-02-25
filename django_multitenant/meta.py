# -*- coding: utf-8 -*-
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.db.models.fields import NOT_PROVIDED
from django.forms.forms import pretty_name
from django.utils import six



def validate_meta(meta):
    """
    Validates Mulitenannt Meta attribute.
    """
    if not isinstance(meta, (dict,)):
        raise TypeError('Model Meta "multitenant" must be a dict')

    # Type can be 'distributed' or 'reference'
    distributed_type = getattr(meta, 'type', 'distributed')

    required_keys = []
    if distributed_type == 'distributed':
        required_keys = ['tenant_id',]

    for key in required_keys:
        if key not in meta:
            raise KeyError('Model Meta "multitenant" dict requires %s to be defined', key)

    if not isinstance(meta['tenant_id'], str):
        raise ImproperlyConfigured(
            'Mulitenant Meta\'s field tenant_id must be a column name'
        )


class TenantMeta(models.base.ModelBase):
    def __new__(cls, name, bases, attrs):
        from .mixins import TenantModelMixin

        meta = None

        if "Meta" not in attrs or not hasattr(attrs["Meta"], "multitenant"):
            return super(TenantMeta, cls).__new__(cls, name, bases, attrs)

        validate_meta(attrs['Meta'].multitenant)
        meta = attrs['Meta'].multitenant
        delattr(attrs['Meta'], 'multitenant')

        #
        # Auto-add Mixins
        #

        bases = (TenantModelMixin,) + bases

        #
        # Let's create class
        #

        new_class = super(TenantMeta, cls).__new__(cls, name, bases, attrs)

        #
        # Multitenant Meta
        #

        new_class._meta.multitenant = meta

        return new_class
