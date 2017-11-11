# Shell Plus Model Imports
from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from django.contrib.sessions.models import Session
from stores.models import Product, Purchase, Store
# Shell Plus Django Imports
from django.core.cache import cache
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Avg, Case, Count, F, Max, Min, Prefetch, Q, Sum, When
from django.utils import timezone
from django.urls import reverse

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

