#!/usr/bin/env python
import os
import sys


SUPPORTED_ENVS = "tests"

SETTINGS_MODULES = {
    "test": "django_multitenant.tests.settings",
}

ENV = os.environ.get("ENV", "test")
ENV = ENV.lower()

if ENV not in SUPPORTED_ENVS:
    raise Exception("Unsupported environment: %s" % ENV)

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", SETTINGS_MODULES[ENV])
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
