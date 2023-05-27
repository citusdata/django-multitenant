Usage
=================================

In order to use this library you can either use Mixins or have your
models inherit from our custom model class.

Changes in Models
-----------------

1. In whichever files you want to use the library import it:

   .. code:: python

      from django_multitenant.fields import *
      from django_multitenant.models import *

2. All models should inherit the TenantModel class.
   ``Ex: class Product(TenantModel):``

3. Define a static variable named tenant_id and specify the tenant
   column using this variable. ``Ex: tenant_id='store_id'``

4. All foreign keys to TenantModel subclasses should use
   TenantForeignKey in place of models.ForeignKey

5. A sample model implementing the above 2 steps:

   .. code:: python

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


Reserved tenant_id keyword
~~~~~~~~~~~~~~~~~~~~~~~~~~
tenant_id column name should not be 'tenant_id'. 'tenant_id' is a reserved keyword across the library.

Example model with correct tenant_id column name:

.. code:: python

   class Tenant
      tenant_id = 'id'

   class Business(TenantModel):
      ten = models.ForeignKey(Tenant, blank=True, null=True, on_delete=models.SET_NULL)
      tenant_id = 'tenant_id' # This is wrong
      tenant_id = 'ten_id' # This is correct


Changes in Models using mixins
-------------------------------

1. In whichever files you want to use the library import it by just
   saying

   .. code:: python

      from django_multitenant.mixins import *

2. All models should use the ``TenantModelMixin`` and the django
   ``models.Model`` or your customer Model class
   ``Ex: class Product(TenantModelMixin, models.Model):``

3. Define a static variable named tenant_id and specify the tenant
   column using this variable. ``Ex: tenant_id='store_id'``

4. All foreign keys to TenantModel subclasses should use
   TenantForeignKey in place of models.ForeignKey

5. Referenced table in TenenatForeignKey should include a unique key
   including tenant_id and primary key

   ::

      Ex:       
      class Meta(object):
           unique_together = ["id", "store"]

6. A sample model implementing the above 3 steps:

   .. code:: python


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

Changes in Migrations
---------------------

Typical Django ORM migrations use ``apps.get_model()`` in `RunPython
<https://docs.djangoproject.com/en/4.1/ref/migration-operations/#runpython>`_
to get a model from the app registry. For example:

.. code:: python

   # normal way -- does NOT work in Django Multitenant

   def forwards_func(apps, schema_editor):
      MigrationUseInMigrationsModel = apps.get_model("tests", "MigrationUseInMigrationsModel")
      MigrationUseInMigrationsModel.objects.create(name="test")

However the ``get_model`` method creates "fake" models that lack transient
fields, and Django Multitenant relies on the ``tenant_id`` transient field to
function properly.  When doing ORM database migrations with Django Multitenant,
you'll need to get the model differently.

Here are two alternatives.

1. Use the ``apps`` module rather than the ``apps`` parameter in RunPython
   methods (such as ``forwards_func``) to get the model you want to use:

   .. code:: python

      from django.apps import apps

      def forwards_func(ignored, schema_editor):
         MigrationUseInMigrationsModel = apps.get_model("tests", "MigrationUseInMigrationsModel")
         MigrationUseInMigrationsModel.objects.create(name="test")

2. Directly import the class from models:

   .. code:: python

      from .models import  MigrationUseInMigrationsModel

      def forwards_func(ignored, schema_editor):
         MigrationUseInMigrationsModel.objects.create(name="test")

Automating composite foreign keys at db layer
----------------------------------------------

1. Creating foreign keys between tenant related models using
   TenantForeignKey would automate adding tenant_id to reference queries
   (ex. product.purchases) and join queries (ex. product__name). If you
   want to ensure to create composite foreign keys (with tenant_id) at
   the db layer, you should change the database ENGINE in the
   settings.py to ``django_multitenant.backends.postgresql``.

   .. code:: python

      'default': {
            'ENGINE': 'django_multitenant.backends.postgresql',
            ......
            ......
            ......
      }

Where to Set the Tenant?
------------------------

1. Write authentication logic using a middleware which also sets/unsets
   a tenant for each session/request. This way developers need not worry
   about setting a tenant on a per view basis. Just set it while
   authentication and the library would ensure the rest (adding
   tenant_id filters to the queries). A sample implementation of the
   above is as follows:

   .. code:: python

    from django_multitenant.utils import set_current_tenant, unset_current_tenant
    from django.contrib.auth import logout


    class MultitenantMiddleware:
      def __init__(self, get_response):
         self.get_response = get_response

      def __call__(self, request):
         if request.user and not request.user.is_anonymous:
            if not request.user.account and not request.user.is_superuser:
               print(
                  "Logging out because user doesnt have account and not a superuser"
               )
               logout(request.user)

            set_current_tenant(request.user.account)

         response = self.get_response(request)

         """
         The following unsetting of the tenant is essential because of how webservers work
         Since the tenant is set as a thread local, the thread is not killed after the request is processed
         So after processing of the request, we need to ensure that the tenant is unset
         Especially required if you have public users accessing the site 
         
         This is also essential if you have admin users not related to a tenant (not possible in actual citus env)
         """
         unset_current_tenant()

         return response


   In your settings, you will need to update the ``MIDDLEWARE`` setting
   to include the one you created.

   .. code:: python

        MIDDLEWARE = [
            # ...
            # existing items
            # ...
            'appname.middleware.MultitenantMiddleware'
        ]

2. Set the tenant using set_current_tenant(t) api in all the views which
   you want to be scoped based on tenant. This would scope all the
   django API calls automatically(without specifying explicit filters)
   to a single tenant. If the current_tenant is not set, then the
   default/native API without tenant scoping is used.

   .. code:: python

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

Supported APIs
=================================

1. Most of the APIs under Model.objects.*.
2. Model.save() injects tenant_id for tenant inherited models.

.. code:: python

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

Credits
=================================

This library uses similar logic of setting/getting tenant object as in
`django-simple-multitenant <https://github.com/pombredanne/django-simple-multitenant>`__.
We thank the authors for their efforts.
