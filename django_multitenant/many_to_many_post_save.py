from django.apps.registry import apps
from django.db.models.signals import post_save

def wrap_many_related_manager_add(many_related_manager_add):

    """
    Wraps the add method of many to many field to set tenant_id in through_defaults
    parameter of the add method.
    """

    def add(obj, *objs, through_defaults=None):
        from django_multitenant.utils import (
            get_current_tenant_value,
            get_tenant_column,
            get_current_tenant,
        )

        if get_current_tenant():
            through_defaults[get_tenant_column(obj)] = get_current_tenant_value()
        return many_related_manager_add(obj, *objs, through_defaults=through_defaults)

    # pylint: disable=protected-access
    add._sign = "add django-multitenant"

    return add

def post_save_signal(sender, **kwargs):

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
        # pylint: disable=protected-access
        if not hasattr(field_value.add, "_sign"):
            field_value.add = wrap_many_related_manager_add(field_value.add)

def register_post_save_signal():

    from django_multitenant.models import TenantModel

    app_configs = apps.get_app_configs()

    models = apps.get_models()
    for model in models:
        if issubclass(model, TenantModel):
            post_save.connect(post_save_signal, sender=model)

