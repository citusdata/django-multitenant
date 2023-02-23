import inspect
import importlib

from django.apps import apps
from django.db.models.signals import post_save

try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local


_thread_locals = local()


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
    Utils to get the tenant that hass been set in the current thread using `set_current_tenant`.
    Can be used by doing:
    ```
        my_class_object = get_current_tenant()
    ```
    Will return None if the tenant is not set
    """
    return getattr(_thread_locals, "tenant", None)


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
        register_post_save_signal()


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
    Utils to set a tenant in the current thread.
    Often used in a middleware once a user is logged in to make sure all db
    calls are sharded to the current tenant.
    Can be used by doing:
    ```
        get_current_tenant(my_class_object)
    ```
    """
    setattr(_thread_locals, "tenant", tenant)
    register_post_save_signal()


def unset_current_tenant():
    setattr(_thread_locals, "tenant", None)


def is_distributed_model(model):
    """
    If model has tenant_field, it is distributed model and returns True
    """
    try:
        get_tenant_field(model)
        return True
    except ValueError:
        return False

def wrap_many_related_manager_add(many_related_manager_add):

    """
    Wraps the add method of many to many field to set tenant_id in through_defaults
    parameter of the add method.
    """

    def add(obj, *objs, through_defaults=None):

        if get_current_tenant():
            through_defaults[get_tenant_column(obj)] = get_current_tenant_value()
        return many_related_manager_add(obj, *objs, through_defaults=through_defaults)

    # pylint: disable=protected-access
    add._sign = "add django-multitenant"

    return add

def post_save_signal( **kwargs):

    """
    Gets all many to many fields for the object being saved
    and wraps the add method to set tenant_id for the related objects
    """

    instance = kwargs["instance"]
    many_to_many_fields = [
        field
        for field in instance._meta.get_fields()
        if field.many_to_many and not field.auto_created
    ]

    for field in many_to_many_fields:
        field_value = getattr(instance, field.name)
        if not hasattr(field_value.add, "_sign"):
            field_value.add = wrap_many_related_manager_add(field_value.add)

def register_post_save_signal():
    app_configs = apps.get_app_configs()

    models = apps.get_models()
    for model in models:
        if is_subclass(model, "django_multitenant.models.TenantModel")  :
            post_save.connect(post_save_signal, sender=model)


def is_subclass(subclass, superclass_name):
    """
    Gets the model class and superclass name and returns True if the model class is subclass of the superclass
    Normally issubclass method is used to check if a class is subclass of another class.However, when using
    issubclass method, the class should be imported. In our case, we don't want to import the class because
    importing TenantModel creates a circular dependency with the models.py file. So, we are using this method
    """
    
    try:
        module_name, class_name = superclass_name.rsplit('.', 1)
        module = importlib.import_module(module_name)
        superclass = getattr(module, class_name)
        return isinstance(subclass, type) and isinstance(superclass, type) and issubclass(subclass, superclass)
    except (ImportError, AttributeError):
        return False