# django-multitenant
Python/Django support for distributed multi-tenant databases like Postgres+Citus

Enables easy scale-out by adding the tenant context to your queries, enabling the database (e.g. Citus) to efficiently route queries to the right database node.

There are architecures for building multi-tenant databases viz. **Create one database per tenant**, **Create one schema per tenant** and **Have all tenants share the same table(s)**. This library is based on the 3rd design i.e **Have all tenants share the same table(s)**, it assumes that all the tenant relates models/tables have a tenant_id column for represnting a tenant.

The following link talks more about the trade-offs on when and how to choose the right architecture for your multi-tenat database:

https://www.citusdata.com/blog/2016/10/03/designing-your-saas-database-for-high-scalability/

**Other useful links on multi-tenancy**:
1. https://www.citusdata.com/blog/2017/03/09/multi-tenant-sharding-tutorial/
1. https://www.citusdata.com/blog/2017/06/02/scaling-complex-sql-transactions/


## Installation:
1. pip install django_multitenant

## Supported Django versions/Pre-requisites.
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
    	name = models.CharField(max_length=255)
    	description = models.TextField()
    	class Meta(object):
    		unique_together = ["id", "store"]
 	```

1. In an application function set the tenant using set_current_tenant(t) api. This would scope all the django API calls automatically(without specifying explicit filters) to a single tenant. If the current_tenant is not set, then the default/native API  without tenant scoping is used.
   ```python
    def application_function:
    	# current_tenant can be stored as a SESSION variable when a user logs in.
    	# This should be done by the app
    	t = current_tenant
    	#set the tenant
    	set_current_tenant(t);
    	#Django ORM API calls;
    	#Command 1;
    	#Command 2;
   		#Command 3;
    	#Command 4;
   		#Command 5;
   ```
## Supported APIs:
1. Most of the APIs under Model.objects.* except `select_related()`.
1. Model.save() injects tenant_id for tenant inherited models.

## Credits

This library uses similar logic of setting/getting tenant object as in [django-simple-multitenant](https://github.com/pombredanne/django-simple-multitenant). We thank the authors for their efforts.

## License

Licensed under the MIT license<br>
Copyright (c) 2016, Citus Data Inc.

