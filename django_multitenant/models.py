# flake8: noqa
import logging

from django.db import models

from collections import OrderedDict
import pdb

from .patch import patch_delete_queries_to_include_tenant_ids
from .utils import (
    set_current_tenant,
    get_current_tenant,
    get_model_by_db_table,
    get_tenant_column,
)

logger = logging.getLogger(__name__)


#Modified QuerySet to add suitable filters on joins.
class TenantQuerySet(models.QuerySet):

    #This is adding tenant filters for all the models in the join.
    def add_tenant_filters_with_joins(self):
        current_tenant=get_current_tenant()
        if current_tenant:
            extra_sql=[]
            extra_params=[]
            current_table_name=self.model._meta.db_table
            alias_refcount = self.query.alias_refcount
            alias_map = self.query.alias_map
            for k,v in alias_refcount.items():
                if(v>0 and k!=current_table_name):
                    current_model=get_model_by_db_table(alias_map[k].table_name)
                    if issubclass(current_model, TenantModel):
                        tenant_column = get_tenant_column(current_model)
                        extra_sql.append(k+'."'+tenant_column+'" = %s')
                        extra_params.append(current_tenant.id)
            self.query.add_extra([],[],extra_sql,extra_params,[],[])

    def add_tenant_filters_without_joins(self):
        current_tenant=get_current_tenant()
        if current_tenant:
            extra_sql=[]
            extra_params = []
            table_name=self.model._meta.db_table
            tenant_column = get_tenant_column(self.model)
            extra_sql.append(table_name+'."'+tenant_column+'" = %s')
            extra_params.append(current_tenant.id)
            self.query.add_extra([],[],extra_sql,extra_params,[],[])

    #Below are APIs which generate SQL, this is where the tenant_id filters are injected for joins.

    def __iter__(self):
        # self.add_tenant_filters_with_joins()
        return super(TenantQuerySet,self).__iter__()

    def aggregate(self, *args, **kwargs):
        # self.add_tenant_filters_with_joins()
        return super(TenantQuerySet,self).aggregate(*args, **kwargs)

    def count(self):
        # self.add_tenant_filters_with_joins()
        return super(TenantQuerySet,self).count()

    def get(self, *args, **kwargs):
        return super(TenantQuerySet,self).get(*args,**kwargs)

    def create(self, *args, **kwargs):
        if get_current_tenant():
            tenant_column = get_tenant_column(self.model)
            kwargs[tenant_column] = get_current_tenant().id
        return super(TenantQuerySet, self).create(*args, **kwargs)

    # def delete(self, *args, **kwargs):
    #     import pdb; pdb.set_trace()
    #     self.add_tenant_filters_without_joins()
    #     return super(TenantQuerySet, self).delete(*args, **kwargs)

    # def get_or_create(self, defaults=None, **kwargs):
    #     self.add_tenant_filters()
    #     return super(TenantQuerySet,self).get_or_create(defaults,**kwargs)

    # def update(self, **kwargs):
    #     self.add_tenant_filters_without_joins()
    #     #print(self.query.alias_refcount)
    #     return super(TenantQuerySet,self).update(**kwargs)

    # def _update(self, values):
    #     self.add_tenant_filters_without_joins()
    #     #print(self.query.alias_refcount)
    #     return super(TenantQuerySet,self)._update(values)

    #This API is called when there is a subquery. Injected tenant_ids for the subqueries.
    def _as_sql(self, connection):
        self.add_tenant_filters_with_joins()
        return super(TenantQuerySet,self)._as_sql(connection)

#Below is the manager related to the above class. 
class TenantManager(TenantQuerySet.as_manager().__class__):
    #Injecting tenant_id filters in the get_queryset.
    #Injects tenant_id filter on the current model for all the non-join/join queries. 
    def get_queryset(self):
        current_tenant=get_current_tenant()
        if current_tenant:
            kwargs = { self.model.tenant_id: current_tenant.id}
            return super(TenantManager, self).get_queryset().filter(**kwargs)
        return super(TenantManager, self).get_queryset()

#Abstract model which all the models related to tenant inherit.
class TenantModel(models.Model):
    def __init__(self, *args, **kwargs):
        patch_delete_queries_to_include_tenant_ids()
        super(TenantModel, self).__init__(*args, **kwargs)

    #New manager from middleware
    objects = TenantManager()
    tenant_id=''

    #adding tenant filters for save
    #Citus requires tenant_id filters for update, hence doing this below change.
    def _do_update(self, base_qs, using, pk_val, values, update_fields, forced_update):
        current_tenant=get_current_tenant()
        if current_tenant:
            kwargs = { self.__class__.tenant_id: current_tenant.id}
            base_qs = base_qs.filter(**kwargs)
        else:
            logger.warn('Attempting to update %s instance "%s" without a current tenant '
                        'set. This may cause issues in a partitioned environment. '
                        'Recommend calling set_current_tenant() before performing this '
                        'operation.',
                        self._meta.model.__name__, self)
        return super(TenantModel,self)._do_update(base_qs, using, pk_val, values, update_fields, forced_update)

    class Meta:
        abstract = True


class ThreadLocals(object):
    """Middleware that gets various objects from the
    request object and saves them in thread local storage."""
    def process_request(self, request):
        _thread_locals.user = getattr(request, 'user', None)

        # Attempt to set tenant
        if _thread_locals.user and not _thread_locals.user.is_anonymous():
            try:
                profile = _thread_locals.user.get_profile()
                if profile:
                    _thread_locals.tenant = getattr(profile, 'tenant', None)
            except:
                raise ValueError(
                    """A User was created with no profile.  For security reasons, 
                    we cannot allow the request to be processed any further.
                    Try deleting this User and creating it again to ensure a 
                    UserProfile gets attached, or link a UserProfile 
                    to this User.""")
