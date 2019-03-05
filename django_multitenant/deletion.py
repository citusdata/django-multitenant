from .utils import get_current_tenant, get_tenant_column



def related_objects(obj, related, objs):
    filters = {
        "%s__in" % related.field.name: objs
    }
    current_tenant = get_current_tenant()

    if current_tenant:
        try:
            tenant_column = get_tenant_column(related.related_model)
            tenant_value = getattr(current_tenant, current_tenant.tenant_id, None)
            filters[tenant_column] = tenant_value
        except ValueError:
            pass

    return related.related_model._base_manager.using(obj.using).filter(**filters)
