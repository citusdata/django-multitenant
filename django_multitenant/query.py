from django.db.models.sql.subqueries import DeleteQuery
from django.db.models import Q

from .utils import get_current_tenant, get_tenant_column, get_tenant_filters


def wrap_get_compiler(base_get_compiler):

    def get_compiler(obj, *args, **kwargs):
        current_tenant = get_current_tenant()

        if current_tenant:
            try:
                filters = get_tenant_filters(obj.model)
                obj.add_q(Q(
                    **filters
                ))
            except ValueError:
                pass

        return base_get_compiler(obj, *args, **kwargs)

    get_compiler._sign = "get_compiler django-multitenant"
    return get_compiler
