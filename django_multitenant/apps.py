# -*- coding: utf-8 -*-
from django.apps import AppConfig


class MultitenantConfig(AppConfig):
    name = "django_multitenant"
    verbose_name = "Multitenant"

    def ready(self):
        super(MultitenantConfig, self).ready()
