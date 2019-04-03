import logging
from django.db.models.sql.subqueries import DeleteQuery

from .utils import get_tenant_column, get_current_tenant

logger = logging.getLogger(__name__)


def wrap_get_compiler(original_get_compiler):

    def get_compiler(obj, *args, **kwargs):
        from .models import TenantModel
        if issubclass(obj.model, TenantModel):
            current_tenant = get_current_tenant()
            if current_tenant:
                tenant_column = get_tenant_column(obj.model)
                db_table = obj.model._meta.db_table

                # Bad SQL injection
                extra_sql = ['{table}."{column}" = %s'.format(
                    table=db_table, column=tenant_column)]

                extra_params = [current_tenant.tenant_value]
                obj.add_extra([],[],extra_sql,extra_params,[],[])
        return original_get_compiler(obj, *args, **kwargs)

    get_compiler._sign = "monkey patch by django-multitenant"
    return get_compiler


def patch_delete_queries_to_include_tenant_ids():
    '''
    Patches the `get_compiler` method of DeleteQuery to include an additional
    filter on tenant_id for any deletions that occur while a tenant is set.

    See https://github.com/citusdata/django-multitenant/issues/15 for a more
    detailed description.
    '''
    if not hasattr(DeleteQuery.get_compiler, "_sign"):
        logger.debug("Patching DeleteQuery.get_compiler()")
        DeleteQuery.get_compiler = wrap_get_compiler(DeleteQuery.get_compiler)
