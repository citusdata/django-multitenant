# -*- coding: utf-8 -*-
from django.conf.urls import include, url
from django.contrib import admin


# TODO
# Add view to verify objects in context


urlpatterns = [
    url(r"^admin/", admin.site.urls),
]
