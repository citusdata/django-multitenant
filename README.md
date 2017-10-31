# django-multitenant
Python/Django support for distributed multi-tenant databases like Postgres+Citus

Enables easy scale-out by adding the tenant context to your queries, enabling the database (e.g. Citus) to efficiently route queries to the right database node.

There are architecures for building multi-tenant databases viz. **Create one database per tenant**, **Create one schema per tenant** and **Have all tenants share the same table(s)**. This library is based on the 3rd design i.e **Have all tenants share the same table(s)**, it assumes that all the tenant relates models/tables have a tenant_id column for representing a tenant.

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
### Changes in Models:
1. In whichever files you want to use the library import it by just saying `from django_multitenant import *`
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
### Where to Set the Tenant?
1. Write authentication logic using a middleware which also sets/unsets a tenant for each session/request. This way developers need not worry about setting a tenant on a per view basis. Just set it while authentication and the library would ensure the rest (adding tenant_id filters to the queries). A sample implementation of the above is as follows:
   ```python
    class SetCurrentTenantFromUser(object):
    	def process_request(self, request):
     	        if not hasattr(self, 'authenticator'):
            		from rest_framework_jwt.authentication import JSONWebTokenAuthentication
            		self.authenticator = JSONWebTokenAuthentication()
                try:
            		user, _ = self.authenticator.authenticate(request)
                except:
            		# TODO: handle failure
            		return
                try:
            		#Assuming your app has a function to get the tenant associated for a user
            		current_tenant = get_tenant_for_user(user)
                except:
            		# TODO: handle failure
            		return
                set_current_tenant(current_tenant)
        def process_response(self, request, response):
                set_current_tenant(None)
                return response
   ```
   ```python
      MIDDLEWARE_CLASSES = (
    	'our_app.utils.multitenancy.SetCurrentTenantFromUser',
      )
   ```
1. Set the tenant using set_current_tenant(t) api in all the views which you want to be scoped based on tenant. This would scope all the django API calls automatically(without specifying explicit filters) to a single tenant. If the current_tenant is not set, then the default/native API  without tenant scoping is used.
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
	```python
    s=Store.objects.all()[0]
	set_current_tenant(s)
	
	#All the below API calls would add suitable tenant filters.
	#Simple get_queryset()
	Product.objects.get_queryset()
	
	#Simple join
	Purchase.objects.filter(id=1).filter(store__name='sai').filter(product__description='')
	
	#Update
	Purchase.objects.filter(id=1).update(id=1)
	
	#Save
	p=Product(8,1,'sai','hello')
	p.save()

	#Simple aggregates
	Product.objects.count()
	Product.objects.filter(store__name='sai').count()
	Product.objects.filter(name='sai').aggregate(Avg('store_id'))
	
	#Subqueries
	Product.objects.filter(name='sai');
	Purchase.objects.filter(product__in=p);
   ```

## Credits

This library uses similar logic of setting/getting tenant object as in [django-simple-multitenant](https://github.com/pombredanne/django-simple-multitenant). We thank the authors for their efforts.
