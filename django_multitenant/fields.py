import logging
import django
from django.db import models
from django.db.models.expressions import Col
from django.db.models.sql.where import WhereNode
from django.conf import settings

from .exceptions import EmptyTenant
from .utils import get_current_tenant, get_tenant_column, get_tenant_filters

logger = logging.getLogger(__name__)


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
            return get_tenant_filters(self.related_model)
        else:
            empty_tenant_message = (
                f"TenantForeignKey field {self.model.__name__}.{self.name} "
                "accessed without a current tenant set. "
                "This may cause issues in a partitioned environment. "
                "Recommend calling set_current_tenant() before accessing "
                "this field."
            )

            if getattr(settings, "TENANT_STRICT_MODE", False):
                raise EmptyTenant(empty_tenant_message)

            logger.warning(empty_tenant_message)
            return super(TenantForeignKey, self).get_extra_descriptor_filter(instance)

    # Override
    # Django 4.0 removed the where_class argument from this method, so
    # depending on the version we define the function with a different
    # signature.
    if django.VERSION >= (4, 0):

        def get_extra_restriction(self, alias, related_alias):
            return self.get_extra_restriction_citus(alias, related_alias)

    else:

        def get_extra_restriction(self, where_class, alias, related_alias):
            return self.get_extra_restriction_citus(alias, related_alias)

    def get_extra_restriction_citus(self, alias, related_alias):
        """
        Return a pair condition used for joining and subquery pushdown. The
        condition is something that responds to as_sql(compiler, connection)
        method.

        Note that currently referring both the 'alias' and 'related_alias'
        will not work in some conditions, like subquery pushdown.

        A parallel method is get_extra_descriptor_filter() which is used in
        instance.fieldname related object fetching.
        """

        if not (related_alias and alias):
            return None

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
        condition = WhereNode()
        condition.add(lookup, "AND")
        return condition


class TenantOneToOneField(models.OneToOneField, TenantForeignKey):
    # Override
    def __init__(self, *args, **kwargs):
        kwargs["unique"] = False
        super(TenantOneToOneField, self).__init__(*args, **kwargs)
