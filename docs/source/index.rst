.. Django Multi-tenant documentation master file, created by
   sphinx-quickstart on Mon Feb 13 13:32:28 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Django Multi-tenant's documentation!
=================================================

|Latest Documentation Status| |Build Status| |Coverage Status| |PyPI Version|

.. |Latest Documentation Status| image:: https://readthedocs.org/projects/django-multitenant/badge/?version=latest
    :target: https://django-multitenant.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. |Build Status| image:: https://github.com/citusdata/django-multitenant/actions/workflows/django-multitenant-tests.yml/badge.svg
   :target: https://github.com/citusdata/django-multitenant/actions/workflows/django-multitenant-tests.yml
   :alt: Build Status

.. |Coverage Status| image:: https://codecov.io/gh/citusdata/django-multitenant/branch/main/graph/badge.svg?token=taRgoSgHUw 
   :target: https://codecov.io/gh/citusdata/django-multitenant
   :alt: Coverage Status

.. |PyPI Version| image:: https://badge.fury.io/py/django-multitenant.svg
   :target: https://badge.fury.io/py/django-multitenant


Python/Django support for distributed multi-tenant databases like
Postgres+Citus

Enables easy scale-out by adding the tenant context to your queries,
enabling the database (e.g. Citus) to efficiently route queries to the
right database node.

There are architecures for building multi-tenant databases viz. **Create
one database per tenant**, **Create one schema per tenant** and **Have
all tenants share the same table(s)**. This library is based on the 3rd
design i.e **Have all tenants share the same table(s)**, it assumes that
all the tenant relates models/tables have a tenant_id column for
representing a tenant.

The following link talks more about the trade-offs on when and how to
choose the right architecture for your multi-tenat database:

https://www.citusdata.com/blog/2016/10/03/designing-your-saas-database-for-high-scalability/

.. toctree::
   :maxdepth: 2
   :caption: Table Of Contents

   general
   usage
   migration_mt_django
   django_rest_integration
   license
