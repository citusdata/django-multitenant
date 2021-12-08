# -*- coding: utf-8 -*-
import django
from django.conf.urls import include

# django.conf.urls.url is deprecated since Django 3.1, re_path is the
# replacement:
# https://docs.djangoproject.com/en/3.1/ref/urls/#url
if django.VERSION >= (3, 1):
    from django.urls import re_path as url
else:
    from django.conf.urls import url

from django.contrib import admin


# TODO
# Add view to verify objects in context


urlpatterns = [
    url(r"^admin/", admin.site.urls),
]
