import sys

if sys.version_info >= (3,0):
    from django_multitenant.django_multitenant import *
else:
    from .django_multitenant import *
