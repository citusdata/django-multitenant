import inspect

from django.apps import apps
from .settings import TENANT_USE_ASGIREF


if TENANT_USE_ASGIREF:
    # asgiref must be installed, its included with Django >= 3.0
    from asgiref.local import Local as local
else:
    try:
        from threading import local
    except ImportError:
        from django.utils._threading_local import local


_thread_locals = _context = local()


def get_model_by_db_table(db_table):
    """
    Gets django model using db_table name
    """
    for model in apps.get_models():
        if model._meta.db_table == db_table:
            return model

    # here you can do fallback logic if no model with db_table found
    raise ValueError(f"No model found with db_table {db_table}!")
    # or return None


def get_current_tenant():
    """
    Utils to get the tenant that hass been set in the current thread/context using `set_current_tenant`.
    Can be used by doing:
    ```
        my_class_object = get_current_tenant()
    ```
    Will return None if the tenant is not set
    """
    return getattr(_context, "tenant", None)


def get_tenant_column(model_class_or_instance):
    """
    Get the tenant field from the model object or class
    """
    if inspect.isclass(model_class_or_instance):
        model_class_or_instance = model_class_or_instance()

    try:
        return model_class_or_instance.tenant_field
    except Exception as not_a_tenant_model:
        raise ValueError(
            f"{model_class_or_instance.__class__.__name__} is not an instance or a subclass of TenantModel or does not inherit from TenantMixin"
        ) from not_a_tenant_model


def get_tenant_field(model_class_or_instance):
    """
    Gets the tenant field object from the model
    """
    tenant_column = get_tenant_column(model_class_or_instance)
    all_fields = model_class_or_instance._meta.fields
    try:
        return next(field for field in all_fields if field.column == tenant_column)
    except StopIteration as no_field_found:
        raise ValueError(
            f'No field found in {type(model_class_or_instance).name} with column name "{tenant_column}"'
        ) from no_field_found


def get_object_tenant(instance):
    """
    Gets the tenant value from the object. If the object itself is a tenant, it will return the same object
    """
    field = get_tenant_field(instance)

    if field.primary_key:
        return instance

    return getattr(instance, field.name, None)


def set_object_tenant(instance, value):
    if instance.tenant_value is None and value and not isinstance(value, list):
        setattr(instance, instance.tenant_field, value)


def get_current_tenant_value():
    """
    Returns current set tenant value if exists
    If tenant is a list, it will return a list of tenant values
    If there is no tenant set, it will return None
    """
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
    """
    Returns filter with tenant column added to it if exists.
    If there is more than one tenant column, it will return fiter with in statement.
    """
    filters = filters or {}

    current_tenant_value = get_current_tenant_value()

    if not current_tenant_value:
        return filters

    if isinstance(current_tenant_value, list):
        filters[f"{get_tenant_column(table)}__in"] = current_tenant_value
    else:
        filters[get_tenant_column(table)] = current_tenant_value

    return filters


def set_current_tenant(tenant):
    """
    Utils to set a tenant in the current thread/context.
    Often used in a middleware once a user is logged in to make sure all db
    calls are sharded to the current tenant.
    Can be used by doing:
    ```
        get_current_tenant(my_class_object)
    ```
    """
    setattr(_context, "tenant", tenant)


def unset_current_tenant():
    setattr(_context, "tenant", None)


def is_distributed_model(model):
    """
    If model has tenant_field, it is distributed model and returns True
    """
    try:
        get_tenant_field(model)
        return True
    except ValueError:
        return False
