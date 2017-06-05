# django-multitenant
Python/Django support for distributed multi-tenant databases like Postgres+Citus

Enables easy scale-out by adding the tenant context to your queries, enabling the database (e.g. Citus) to efficiently route queries to the right database node.

There are architecures for building multi-tenant databases viz. **Create one database per tenant**, **Create one schema per tenant** and **Have all tenants share the same table(s)**. This library is based on the 3rd design i.e **Have all tenants share the same table(s)**, it assumes that all the tenant relates models/tables have a tenant_id column for represnting a tenant.

The following link talks more about the trade-offs on when and how to choose the right architecture for your multi-tenat database:

https://www.citusdata.com/blog/2016/10/03/designing-your-saas-database-for-high-scalability/


## Installation:
1. pip install django_multitenant

## Supported Django versions
Tested with django 1.10 or higher.

## Usage:
1. In whichever files you want to use the library import it by just saying `import django_multitenant`
1. All models should inherit the TenantModel class.
   `Ex: class Product(TenantModel):`
1. Define a static variable named tenant_id and specify the tenant column using this variable.
   `Ex: tenant_id='store_id'`
1. A sample model implementing the above 2 steps:
   ```python
    class Product(TenantModel):
    	store = models.ForeignKey(Store)
    	tenant_id='store_id'

    	def get_tenant():
        	return self.store

    	name = models.CharField(max_length=255)
    	description = models.TextField()
    	class Meta(object):
        	unique_together = ["id", "store"]
 	```

1. In an application function set the tenant using set_current_tenant(t) api. This would scope all the django API calls automatically(without specifying explicit filters) to a single tenant.
   ```python
    def application_function:
   		t = current_tenant (Can come from login session etc)
    	#set the tenant
    	set_current_tenant(t);
    	#Django ORM API calls
    	#Command 1;
    	#Command 2;
   		#Command 3;
    	#Command 4;
   		#Command 5;
   ```
##Supported APIs:
1. Most of the APIs under Model.objects.* except `select_related()`.
1. Model.save() injects tenant_id for tenant inherited models.

