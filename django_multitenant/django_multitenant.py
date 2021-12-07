import logging
from django.apps import apps
from django.db import models

try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local

from collections import OrderedDict

# file kept for compatibility with old version of the library

from .fields import TenantForeignKey, TenantOneToOneField
from .models import TenantManager, TenantModel
from .utils import get_model_by_db_table, get_current_tenant, set_current_tenant
