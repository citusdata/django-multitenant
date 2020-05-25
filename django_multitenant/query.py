from django.db import connections, transaction
from django.db.models import Q
from django.db.models.sql.constants import (
    GET_ITERATOR_CHUNK_SIZE, NO_RESULTS,
)
from django.conf import settings


from .utils import (get_current_tenant, get_tenant_column,
                    get_tenant_filters, is_distributed_model)


def add_tenant_filters_on_query(obj):
    current_tenant = get_current_tenant()

    if current_tenant:
        try:
            filters = get_tenant_filters(obj.model)
            obj.add_q(Q(
                **filters
            ))
        except ValueError:
            pass


def wrap_get_compiler(base_get_compiler):
    def get_compiler(obj, *args, **kwargs):
        add_tenant_filters_on_query(obj)
        return base_get_compiler(obj, *args, **kwargs)

    get_compiler._sign = "get_compiler django-multitenant"
    return get_compiler


def wrap_update_batch(base_update_batch):
    def update_batch(obj, pk_list, values, using):
        obj.add_update_values(values)
        for offset in range(0, len(pk_list), GET_ITERATOR_CHUNK_SIZE):
            obj.where = obj.where_class()
            obj.add_q(Q(pk__in=pk_list[offset: offset + GET_ITERATOR_CHUNK_SIZE]))
            add_tenant_filters_on_query(obj)
            obj.get_compiler(using).execute_sql(NO_RESULTS)

    update_batch._sign = "update_batch django-multitenant"
    return update_batch



def wrap_delete(base_delete):
    def delete(obj):
        obj_are_distributed = [is_distributed_model(instance) for instance in obj.data.keys()]

        # If all elements are from distributed tables, then we can do a simple atomic transaction.
        # If there are mixes of distributed and reference tables, it would raise the following error :

        # django.db.utils.InternalError: cannot execute DML on reference relation
        # "table" because there was a parallel DML access to distributed relation
        # "table2" in the same transaction

        if (len(set(obj_are_distributed)) > 1
            and getattr(settings, 'CITUS_EXTENSION_INSTALLED', False)):
            # all elements are not the same, some False, some True
            with transaction.atomic(using=obj.using, savepoint=False):
                connections[obj.using].cursor().execute("SET LOCAL citus.multi_shard_modify_mode TO 'sequential';")
                result = base_delete(obj)
                connections[obj.using].cursor().execute("SET LOCAL citus.multi_shard_modify_mode TO 'parallel';")
                return result

        return base_delete(obj)

    return delete
