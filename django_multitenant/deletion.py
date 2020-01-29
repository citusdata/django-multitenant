from django.db.models.deletion import Collector
from django.db import connections, transaction

from .utils import (get_current_tenant, get_tenant_filters,
                    is_distributed_model)


def related_objects(obj, related, objs):
    filters = {
        "%s__in" % related.field.name: objs
    }
    current_tenant = get_current_tenant()

    if current_tenant:
        try:
            filters = get_tenant_filters(related.related_model, filters)
        except ValueError:
            pass

    return related.related_model._base_manager.using(obj.using).filter(**filters)


def wrap_delete(base_delete):
    def delete(obj):
        obj_are_distributed = [is_distributed_model(instance) for instance in obj.data.keys()]

        # If all elements are from distributed tables, then we can do a simple atomic transaction.
        # If there are mixes of distributed and reference tables, it would raise the following error :

        # django.db.utils.InternalError: cannot execute DML on reference relation
        # "table" because there was a parallel DML access to distributed relation
        # "table2" in the same transaction

        if len(set(obj_are_distributed)) > 1:
            # all elements are not the same, some False, some True
            with transaction.atomic(using=obj.using, savepoint=False):
                connections[obj.using].cursor().execute("SET LOCAL citus.multi_shard_modify_mode TO 'sequential';")
                result = base_delete(obj)
                connections[obj.using].cursor().execute("SET LOCAL citus.multi_shard_modify_mode TO 'parallel';")
                return result

        return base_delete(obj)

    return delete
