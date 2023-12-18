### Django-Multitenant v4.1.1 (December 18, 2023) ###

* Fix utils to not require TENANT_USE_ASGIREF to be defined in the host django project (#206)

### Django-Multitenant v4.1.0 (December 14, 2023) ###

* Use asgiref when available instead of thread locals (#176) (#198) 

### Django-Multitenant v4.0.0 (September 26, 2023) ###

* Fixes citus 11.3 identity column bigint constraint (#181)

* Adds new python versions for dj3.2 (#188)

* Adds Citus 12  and Django 4.1 and 4.2 support (#197)

### Django-Multitenant v3.2.1 (April 10, 2023) ###

* Add m2m with no through_defaults fix (#170)

### Django-Multitenant v3.2.0 (March 29, 2023) ###

* Adds DjangoRestFramework support (#157)

* Adds guidelines to get model in migration (#167) 

### Django-Multitenant v3.1.1 (March 15, 2023) ###

* Fixes #164 ManyToMany Non tenant model save issue 

### Django-Multitenant v3.1.0(March 1, 2023) ###

* Adds support for Django 4.1

* Adds support for setting tenant automatically for ManyToMany related model

* Fixes invalid error message problem in case of invalid field name

* Adds support for getting models using apps.get_model  

* Removes reserved tenant_id limitation by introducing TenantMeta usage

* Introduces ReadTheDocs documentation

### Django-Multitenant v3.0.0(December 8, 2021) ###

* Adds support for Django 4.0

* Drops support for the following EOLed Django and Python versions:
    1. Python 2.7
    2. Django 1.11
    3. Django 3.1

### Django-Multitenant v2.4.0(November 11, 2021) ###

* Backwards migration for `Distribute` migration using `undistribute_table()`

* Adds tests for Django 3.2 and Python 3.9

* Fixes migrations on Django 3.0+

* Fixes aggregations using `annotate`

### Django-Multitenant v2.0.9 (May 18, 2019) ###

* Fixes the process of running old migrations when the model has been deleted from the code.

### Django-Multitenant v2.0.8 (May 18, 2019) ###

* Add tests to confirm the join condition in subqueries includes tenant column.

### Django-Multitenant v2.0.7 (May 18, 2019) ###

* Fixes create with current tenant

### Django-Multitenant v2.0.6 (May 18, 2019) ###

* Fix recursive loop in warning for fields when joining without current_tenant set

### Django-Multitenant v2.0.5 (May 18, 2019) ###

* Adds support for custom query_set in TenantManager

* Cleans the delete code to ensure deleting rows only related to current tenant

### Django-Multitenant v2.0.4 (May 18, 2019) ###

* Adds support for multiple tenant

### Django-Multitenant v1.1.0 (January 26, 2018) ###

* Add TenantForeignKey to emulate composite foreign keys between tenant related models.

* Split apart library into multiple files. Importing the utility function `get_current_tenant` would cause errors due to the import statement triggering evaluation of the TenantModel class. This would cause problems if TenantModel were evaluated before the database backend was initialized.

*  Added a simple TenantOneToOneField which does not try to enforce a uniqueness constraint on the ID column, but preserves all the relationship semantics of using a traditional OneToOneField in Django.

*  Overrode Django's DatabaseSchemaEditor to produce foreign key constraints on composite foreign keys consisting of both the ID and tenant ID columns for any foreign key between TenantModels

*  Monkey-patched Django's DeleteQuery implementation to include tenant_id in its SQL queries.

### Django-Multitenant v1.0.1 (November 7, 2017) ###

* Some bug fixes.
