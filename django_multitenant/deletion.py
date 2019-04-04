from .utils import (get_current_tenant, get_tenant_filters)


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
