# django-multitenant [![Build Status](https://travis-ci.org/citusdata/django-multitenant.svg?branch=master)](https://travis-ci.org/citusdata/django-multitenant)
Python/Django support for distributed multi-tenant databases like Postgres+Citus

Enables easy scale-out by adding the tenant context to your queries, enabling the database (e.g. Citus) to efficiently route queries to the right database node.

There are architecures for building multi-tenant databases viz. **Create one database per tenant**, **Create one schema per tenant** and **Have all tenants share the same table(s)**. This library is based on the 3rd design i.e **Have all tenants share the same table(s)**, it assumes that all the tenant relates models/tables have a tenant_id column for representing a tenant.

The following link talks more about the trade-offs on when and how to choose the right architecture for your multi-tenat database:

https://www.citusdata.com/blog/2016/10/03/designing-your-saas-database-for-high-scalability/

**Other useful links on multi-tenancy**:
1. https://www.citusdata.com/blog/2017/03/09/multi-tenant-sharding-tutorial/
1. https://www.citusdata.com/blog/2017/06/02/scaling-complex-sql-transactions/


## Installation:
1. `pip install  --no-cache-dir django_multitenant`

## Supported Django versions/Pre-requisites.

| Python        | Django        |
| ------------- | -------------:|
| 3.X           | 2.2           |
| 3.X           | 3.2           |
| 3.X           | 4.0           |


## Usage:

In order to use this library you can either use Mixins or have your models inherit from our custom model class.


### Changes in Models:
1. In whichever files you want to use the library import it:
   ```python
   from django_multitenant.fields import *
   from django_multitenant.models import *
   ```
1. All models should inherit the TenantModel class.
   `Ex: class Product(TenantModel):`
1. Define a static variable named tenant_id and specify the tenant column using this variable.
   `Ex: tenant_id='store_id'`
1. All foreign keys to TenantModel subclasses should use TenantForeignKey in place of
   models.ForeignKey
1. A sample model implementing the above 2 steps:
  ```python
    class Store(TenantModel):
      tenant_id = 'id'
      name =  models.CharField(max_length=50)
      address = models.CharField(max_length=255)
      email = models.CharField(max_length=50)

    class Product(TenantModel):
      store = models.ForeignKey(Store)
      tenant_id='store_id'
      name = models.CharField(max_length=255)
      description = models.TextField()
      class Meta(object):
        unique_together = ["id", "store"]
    class Purchase(TenantModel):
      store = models.ForeignKey(Store)
      tenant_id='store_id'
      product_purchased = TenantForeignKey(Product)
  ```


### Changes in Models using mixins:
1. In whichever files you want to use the library import it by just saying 
   ```python
   from django_multitenant.mixins import *
   ```
1. All models should use the `TenantModelMixin` and the django `models.Model` or your customer Model class
   `Ex: class Product(TenantModelMixin, models.Model):`
1. Define a static variable named tenant_id and specify the tenant column using this variable.
   `Ex: tenant_id='store_id'`
1. All foreign keys to TenantModel subclasses should use TenantForeignKey in place of
   models.ForeignKey
1. A sample model implementing the above 2 steps:
  ```python

    class ProductManager(TenantManagerMixin, models.Manager):
      pass

    class Product(TenantModelMixin, models.Model):
      store = models.ForeignKey(Store)
      tenant_id='store_id'
      name = models.CharField(max_length=255)
      description = models.TextField()

      objects = ProductManager()

      class Meta(object):
        unique_together = ["id", "store"]

    class PurchaseManager(TenantManagerMixin, models.Manager):
      pass

    class Purchase(TenantModelMixin, models.Model):
      store = models.ForeignKey(Store)
      tenant_id='store_id'
      product_purchased = TenantForeignKey(Product)

      objects = PurchaseManager()
  ```



### Automating composite foreign keys at db layer:
1. Creating foreign keys between tenant related models using TenantForeignKey would automate adding tenant_id to reference queries (ex. product.purchases) and join queries (ex. product__name). If you want to ensure to create composite foreign keys (with tenant_id) at the db layer, you should change the database ENGINE in the settings.py to `django_multitenant.backends.postgresql`.
  ```python
    'default': {
        'ENGINE': 'django_multitenant.backends.postgresql',
        ......
        ......
        ......
  }
  ```
### Where to Set the Tenant?
1. Write authentication logic using a middleware which also sets/unsets a tenant for each session/request. This way developers need not worry about setting a tenant on a per view basis. Just set it while authentication and the library would ensure the rest (adding tenant_id filters to the queries). A sample implementation of the above is as follows:
   ```python
       from django_multitenant.utils import set_current_tenant
       
       class MultitenantMiddleware:
           def __init__(self, get_response):
               self.get_response = get_response

           def __call__(self, request):
               if request.user and not request.user.is_anonymous:
                   set_current_tenant(request.user.employee.company)
               return self.get_response(request)
   ```
   
   In your settings, you will need to update the `MIDDLEWARE` setting to include the one you created.
   ```python
      MIDDLEWARE = [
          # ...
          # existing items
          # ...
          'appname.middleware.MultitenantMiddleware'
      ]
   ```
2. Set the tenant using set_current_tenant(t) api in all the views which you want to be scoped based on tenant. This would scope all the django API calls automatically(without specifying explicit filters) to a single tenant. If the current_tenant is not set, then the default/native API  without tenant scoping is used.
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
1. Most of the APIs under Model.objects.*.
1. Model.save() injects tenant_id for tenant inherited models.
  ```python
   s=Store.objects.all()[0]
  set_current_tenant(s)

  #All the below API calls would add suitable tenant filters.
  #Simple get_queryset()
  Product.objects.get_queryset()

  #Simple join
  Purchase.objects.filter(id=1).filter(store__name='The Awesome Store').filter(product__description='All products are awesome')

  #Update
  Purchase.objects.filter(id=1).update(id=1)

  #Save
  p=Product(8,1,'Awesome Shoe','These shoes are awesome')
  p.save()

  #Simple aggregates
  Product.objects.count()
  Product.objects.filter(store__name='The Awesome Store').count()

  #Subqueries
  Product.objects.filter(name='Awesome Shoe');
  Purchase.objects.filter(product__in=p);

   ```

## Credits

This library uses similar logic of setting/getting tenant object as in [django-simple-multitenant](https://github.com/pombredanne/django-simple-multitenant). We thank the authors for their efforts.

## License

Copyright (C) 2018, Citus Data
Licensed under the MIT license, see LICENSE file for details.
