import logging

from django.db import models
from django.db.models.sql import DeleteQuery
from django.db.models.deletion import Collector

from .deletion import related_objects
from .query import wrap_get_compiler
from .utils import (
    set_current_tenant,
    get_current_tenant,
    get_model_by_db_table,
    get_tenant_column
)


logger = logging.getLogger(__name__)



class TenantQuerySetMixin(object):
    def add_tenant_filters_with_joins(self):
        #This is adding tenant filters for all the models in the join.

        current_tenant = get_current_tenant()

        if current_tenant:
            current_tenant_id = current_tenant.tenant_value

            extra_sql = []
            extra_params = []
            current_table_name = self.model._meta.db_table
            alias_refcount = self.query.alias_refcount
            alias_map = self.query.alias_map

            for k,v in alias_refcount.items():
                if(v>0 and k!=current_table_name):
                    current_model=get_model_by_db_table(alias_map[k].table_name)

                    if issubclass(current_model, TenantModel):
                        tenant_column = get_tenant_column(current_model)
                        extra_sql.append(k + '."' + tenant_column + '" = %s')

                        extra_params.append(current_tenant_id)

            self.query.add_extra([],[],extra_sql,extra_params,[],[])

    def create(self, *args, **kwargs):
        #Below are APIs which generate SQL, this is where the tenant_id filters are injected for joins.
        current_tenant = get_current_tenant()
        if current_tenant:
            tenant_column = get_tenant_column(self.model)

            kwargs[tenant_column] = current_tenant.tenant_value

        return super(TenantQuerySetMixin, self).create(*args, **kwargs)

    def _as_sql(self, connection):
        #This API is called when there is a subquery. Injected tenant_ids for the subqueries.
        self.add_tenant_filters_with_joins()
        return super(TenantQuerySetMixin,self)._as_sql(connection)


class TenantQuerySet(TenantQuerySetMixin, models.QuerySet):
    #Modified QuerySet to add suitable filters on joins.
    pass


class TenantManagerMixin(object):
    #Below is the manager related to the above class.

    def get_queryset(self):
        #Injecting tenant_id filters in the get_queryset.
        #Injects tenant_id filter on the current model for all the non-join/join queries. 

        queryset = TenantQuerySet(self.model)
        current_tenant = get_current_tenant()
        if current_tenant:
            kwargs = { self.model.tenant_id: current_tenant.tenant_value}

            return queryset.filter(**kwargs)
        return queryset


class TenantModelMixin(object):
    #Abstract model which all the models related to tenant inherit.
    tenant_id = ''

    def __init__(self, *args, **kwargs):
        if not hasattr(DeleteQuery.get_compiler, "_sign"):
            DeleteQuery.get_compiler = wrap_get_compiler(DeleteQuery.get_compiler)
            Collector.related_objects = related_objects

        super(TenantModelMixin, self).__init__(*args, **kwargs)

    def _do_update(self, base_qs, using, pk_val, values, update_fields, forced_update):
        #adding tenant filters for save
        #Citus requires tenant_id filters for update, hence doing this below change.

        current_tenant = get_current_tenant()

        if current_tenant:
            kwargs = { self.__class__.tenant_id: current_tenant.tenant_value}
            base_qs = base_qs.filter(**kwargs)
        else:
            logger.warning('Attempting to update %s instance "%s" without a current tenant '
                           'set. This may cause issues in a partitioned environment. '
                           'Recommend calling set_current_tenant() before performing this '
                           'operation.',
                           self._meta.model.__name__, self)

        return super(TenantModelMixin,self)._do_update(base_qs, using,
                                                       pk_val, values,
                                                       update_fields,
                                                       forced_update)

    @property
    def tenant_field(self):
        return self.tenant_id

    @property
    def tenant_value(self):
        return getattr(self, self.tenant_field, None)
