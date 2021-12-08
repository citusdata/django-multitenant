# -*- coding: utf-8 -*-
import django

version = (2, 3, 2)

__version__ = ".".join(map(str, version))

# default_app_config is auto detected for versions 3.2 and higher:
# https://docs.djangoproject.com/en/3.2/ref/applications/#for-application-authors
if django.VERSION < (3, 2):
    default_app_config = "django_multitenant.apps.MultitenantConfig"

__all__ = ["default_app_config", "version"]
