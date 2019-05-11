import inspect

from django.apps import apps

try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local


_thread_locals = local()


def get_current_user():
    """
    Despite arguments to the contrary, it is sometimes necessary to find out who is the current
    logged in user, even if the request object is not in scope.  The best way to do this is
    by storing the user object in middleware while processing the request.
    """
    return getattr(_thread_locals, 'user', None)


def get_model_by_db_table(db_table):
    for model in apps.get_models():
        if model._meta.db_table == db_table:
            return model
    else:
        # here you can do fallback logic if no model with db_table found
        raise ValueError('No model found with db_table {}!'.format(db_table))
        # or return None


def get_current_tenant():
    """
    To get the Tenant instance for the currently logged in tenant.
    example:
        tenant = get_current_tenant()
    """
    # tenant may not be set yet, if request user is anonymous, or has no profile,
    return getattr(_thread_locals, 'tenant', None)


def get_tenant_column(model_class_or_instance):
    if inspect.isclass(model_class_or_instance):
        model_class_or_instance = model_class_or_instance()

    try:
        return model_class_or_instance.tenant_field
    except:
        raise ValueError('''%s is not an instance or a subclass of TenantModel
                         or does not inherit from TenantMixin'''
                         % model_class_or_instance.__class__.__name__)


def get_tenant_field(model_class_or_instance):
    tenant_column = get_tenant_column(model_class_or_instance)
    all_fields = model_class_or_instance._meta.fields
    try:
        return next(field for field in all_fields if field.column == tenant_column)
    except StopIteration:
        raise ValueError('No field found in {} with column name "{}"'.format(
                         model_class_or_instance, tenant_column))


def get_current_tenant_value():
    current_tenant = get_current_tenant()
    if not current_tenant:
        return None

    try:
        current_tenant = list(current_tenant)
    except TypeError:
        return current_tenant.tenant_value

    values = []
    for t in current_tenant:
        values.append(t.tenant_value)
    return values


def get_tenant_filters(table, filters=None):
    filters = filters or {}

    current_tenant_value = get_current_tenant_value()

    if not current_tenant_value:
        return filters

    if isinstance(current_tenant_value, list):
        filters['%s__in' % get_tenant_column(table)] = current_tenant_value
    else:
        filters[get_tenant_column(table)] = current_tenant_value

    return filters


def set_current_tenant(tenant):
    setattr(_thread_locals, 'tenant', tenant)


def unset_current_tenant():
    setattr(_thread_locals, 'tenant', None)
