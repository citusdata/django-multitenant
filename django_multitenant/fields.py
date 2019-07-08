import logging
from django.db import models

from .utils import get_current_tenant, get_tenant_column, get_tenant_filters

logger = logging.getLogger(__name__)


class TenantIDFieldMixin:
    """
    Since migrations shouldn't import the models they depend on,
    and we need Model.tenant_id to figure out how to create our composite constraints for sharding,
    store tenant_id on the field itself and add it to the migrations.
    """

    def __init__(self, *args, **kwargs):
        self.tenant_id = kwargs.pop("tenant_id", None)
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs["tenant_id"] = self.tenant_id
        return name, path, args, kwargs


class TenantForeignKey(models.ForeignKey):
    """
    Should be used in place of models.ForeignKey for all foreign key relationships to
    subclasses of TenantModel.

    Adds additional clause to JOINs over this relation to include tenant_id in the JOIN
    on the TenantModel.

    Adds clause to forward accesses through this field to include tenant_id in the
    TenantModel lookup.
    """

    # Override
    def get_extra_descriptor_filter(self, instance):
        """
        Return an extra filter condition for related object fetching when
        user does 'instance.fieldname', that is the extra filter is used in
        the descriptor of the field.

        The filter should be either a dict usable in .filter(**kwargs) call or
        a Q-object. The condition will be ANDed together with the relation's
        joining columns.

        A parallel method is get_extra_restriction() which is used in
        JOIN and subquery conditions.
        """

        current_tenant = get_current_tenant()
        if current_tenant:
            return get_tenant_filters(instance)
        else:
            logger.warn(
                "TenantForeignKey field %s.%s"
                "accessed without a current tenant set. "
                "This may cause issues in a partitioned environment. "
                "Recommend calling set_current_tenant() before accessing "
                "this field.",
                self.model.__name__,
                self.name,
            )
            return super(TenantForeignKey, self).get_extra_descriptor_filter(instance)

    # Override
    def get_extra_restriction(self, where_class, alias, related_alias):
        """
        Return a pair condition used for joining and subquery pushdown. The
        condition is something that responds to as_sql(compiler, connection)
        method.

        Note that currently referring both the 'alias' and 'related_alias'
        will not work in some conditions, like subquery pushdown.

        A parallel method is get_extra_descriptor_filter() which is used in
        instance.fieldname related object fetching.
        """

        # Fetch tenant column names for both sides of the relation
        lhs_model = self.model
        rhs_model = self.related_model
        lhs_tenant_id = get_tenant_column(lhs_model)
        rhs_tenant_id = get_tenant_column(rhs_model)

        # Fetch tenant fields for both sides of the relation
        lhs_tenant_field = lhs_model._meta.get_field(lhs_tenant_id)
        rhs_tenant_field = rhs_model._meta.get_field(rhs_tenant_id)

        # Get references to both tenant columns
        lookup_lhs = lhs_tenant_field.get_col(related_alias)
        lookup_rhs = rhs_tenant_field.get_col(alias)

        # Create "AND lhs.tenant_id = rhs.tenant_id" as a new condition
        lookup = lhs_tenant_field.get_lookup("exact")(lookup_lhs, lookup_rhs)
        condition = where_class()
        condition.add(lookup, "AND")
        return condition

    def _check_unique_target(self):
        # Disable "<field> must set unique=True because it is referenced by a foreign key." error (ID fields.E311),
        # as we can't enforce that with composite keys.
        return []


class TenantOneToOneField(models.OneToOneField, TenantIDFieldMixin, TenantForeignKey):
    # Override
    def __init__(self, *args, **kwargs):
        kwargs["unique"] = False
        super(TenantOneToOneField, self).__init__(*args, **kwargs)


class TenantPrimaryKey(TenantIDFieldMixin, models.AutoField):
    def __init__(self, *args, **kwargs):
        kwargs["primary_key"] = True
        super().__init__(*args, **kwargs)

    def _check_primary_key(self):
        # Disable "AutoFields must set primary_key=True" error (ID fields.E100),
        # as we can't enforce that with composite keys.
        return []
