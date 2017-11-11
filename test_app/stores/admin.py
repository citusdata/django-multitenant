from django.contrib import admin

from .models import Store, Product, Purchase

for m in [Store, Product, Purchase]:
    admin.site.register(m)
