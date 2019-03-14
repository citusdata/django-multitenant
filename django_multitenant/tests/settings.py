# -*- coding: utf-8 -*-
import os
import django

BASE_PATH = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)
)

DATABASES = {
    "default": {
        'ENGINE': 'django_multitenant.backends.postgresql',
        "NAME": "postgres",
        "USER": "postgres",
        "PASSWORD": "",
        "HOST": "localhost",
        "PORT": 5600,
        "TEST": {
            "NAME": "postgres",
            "SERIALIZE": False
        }
    }
}


# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.postgresql_psycopg2",
#         "NAME": "citus",
#         "USER": "citus",
#         "PASSWORD": "GB7TYh-6ITjhmpOu2uClOQ",
#         "HOST": "c.fpt7dawylvzhhdmd2uitsoaoqpq.db.citusdata.com",
#         "PORT": 5432,
#         'OPTIONS': {
#             'sslmode': 'require',
#         },
#         "TEST": {
#             "NAME": "citus",
#             "SERIALIZE": False
#         }
#     }
# }

SITE_ID = 1
DEBUG = True

MIDDLEWARE_CLASSES = (
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
)

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django_multitenant",
    "django_multitenant.tests",
]

SECRET_KEY = "blabla"

ROOT_URLCONF = "django_multitenant.tests.urls"
