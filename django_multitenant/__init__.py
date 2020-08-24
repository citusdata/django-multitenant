# -*- coding: utf-8 -*-
version = (2, 3, 0)

__version__ = ".".join(map(str, version))

default_app_config = "django_multitenant.apps.MultitenantConfig"

__all__ = ["default_app_config", "version"]
