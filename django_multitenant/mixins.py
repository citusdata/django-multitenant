import logging

from django.db.models.sql import DeleteQuery, UpdateQuery
from django.db.models.deletion import Collector
from django.db.utils import NotSupportedError
from django.conf import settings


from .deletion import related_objects
from .exceptions import EmptyTenant
from .query import wrap_get_compiler, wrap_update_batch, wrap_delete
from .utils import (
    set_current_tenant,
    get_current_tenant,
    get_current_tenant_value,
    get_tenant_field,
    get_tenant_filters,
    get_object_tenant,
    set_object_tenant,
)


logger = logging.getLogger(__name__)


class TenantManagerMixin(object):
    # Below is the manager related to the above class.
    def get_queryset(self):
        # Injecting tenant_id filters in the get_queryset.
        # Injects tenant_id filter on the current model for all the non-join/join queries.
        queryset = self._queryset_class(self.model)
        current_tenant = get_current_tenant()
        if current_tenant:
            kwargs = get_tenant_filters(self.model)
            return queryset.filter(**kwargs)
        return queryset

    def bulk_create(self, objs, **kwargs):
        if get_current_tenant():
            tenant_value = get_current_tenant_value()
            for obj in objs:
                set_object_tenant(obj, tenant_value)

        return super(TenantManagerMixin, self).bulk_create(objs, **kwargs)


class TenantModelMixin(object):
    # Abstract model which all the models related to tenant inherit.
    tenant_id = ""

    def __init__(self, *args, **kwargs):
        if not hasattr(DeleteQuery.get_compiler, "_sign"):
            DeleteQuery.get_compiler = wrap_get_compiler(DeleteQuery.get_compiler)
            Collector.related_objects = related_objects
            Collector.delete = wrap_delete(Collector.delete)

        if not hasattr(UpdateQuery.get_compiler, "_sign"):
            UpdateQuery.update_batch = wrap_update_batch(UpdateQuery.update_batch)

        super(TenantModelMixin, self).__init__(*args, **kwargs)

    def __setattr__(self, attrname, val):

        if (
            attrname in (self.tenant_field, get_tenant_field(self).name)
            and not self._state.adding
            and val
            and self.tenant_value
            and val != self.tenant_value
            and val != self.tenant_object
        ):
            self._try_update_tenant = True

        return super(TenantModelMixin, self).__setattr__(attrname, val)

    def _do_update(self, base_qs, using, pk_val, values, update_fields, forced_update):
        # adding tenant filters for save
        # Citus requires tenant_id filters for update, hence doing this below change.

        current_tenant = get_current_tenant()

        if current_tenant:
            kwargs = get_tenant_filters(self.__class__)
            base_qs = base_qs.filter(**kwargs)
        else:
            empty_tenant_message = (
                f"Attempting to update {self._meta.model.__name__} instance {self} "
                "without a current tenant set. "
                "This may cause issues in a partitioned environment. "
                "Recommend calling set_current_tenant() before performing this "
                "operation.",
            )
            if getattr(settings, "TENANT_STRICT_MODE", False):
                raise EmptyTenant(empty_tenant_message)
            else:
                logger.warning(empty_tenant_message)

        return super(TenantModelMixin, self)._do_update(
            base_qs, using, pk_val, values, update_fields, forced_update
        )

    def save(self, *args, **kwargs):
        if hasattr(self, "_try_update_tenant"):
            raise NotSupportedError("Tenant column of a row cannot be updated.")

        current_tenant = get_current_tenant()
        tenant_value = get_current_tenant_value()

        set_object_tenant(self, tenant_value)

        if self.tenant_value and tenant_value != self.tenant_value:
            self_tenant = get_object_tenant(self)
            set_current_tenant(self_tenant)

        try:
            obj = super(TenantModelMixin, self).save(*args, **kwargs)
        finally:
            set_current_tenant(current_tenant)

        return obj

    @property
    def tenant_field(self):
        return self.tenant_id

    @property
    def tenant_value(self):
        return getattr(self, self.tenant_field, None)

    @property
    def tenant_object(self):
        return get_object_tenant(self)
