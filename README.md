# django-multitenant
Python/Django support for distributed multi-tenant databases like Postgres+Citus


##Installation:
1. pip install django_multitenant

## Usage:
1. In all the files add from django_multitenant import *
1. All models should inherit the TenantModel class.
Ex: class Product(TenantModel):
1. Define a static variable named tenant_id and specify the tenant column using this variable.
Ex: tenant_id='store_id'
1. In an application function set the tenant using set_current_tenant(t) api. This would scope all the django API calls automatically(without specifying explicit filters) to a single tenant.
Ex: def application_function:
      t = current_tenant (Can come from login session etc)
      #set the tenant
      set_current_tenant(t);
      #Django ORM API calls
       Command 1
       Command 2
       Command 3
       Command 4
       Command 5