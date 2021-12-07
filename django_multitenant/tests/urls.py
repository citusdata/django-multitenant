# -*- coding: utf-8 -*-
import django
from django.conf.urls import include

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
