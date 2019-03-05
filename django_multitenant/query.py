from django.db.models.sql.subqueries import DeleteQuery
from django.db.models import Q

from .utils import get_current_tenant, get_tenant_column


def wrap_get_compiler(base_get_compiler):

    def get_compiler(obj, *args, **kwargs):
        current_tenant = get_current_tenant()

        if current_tenant:
            try:
                tenant_column = get_tenant_column(obj.model)
                tenant_value = getattr(current_tenant, current_tenant.tenant_id, None)
                obj.add_q(Q(
                    **{tenant_column: tenant_value}
                ))
            except ValueError:
                pass

        return base_get_compiler(obj, *args, **kwargs)

    get_compiler._sign = "get_compiler django-multitenant"
    return get_compiler
