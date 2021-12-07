# -*- coding: utf-8 -*-
import os
import django


BASE_PATH = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)
)

if django.VERSION >= (4, 0):
    test_db = {"NAME": "postgres"}
else:
    test_db = {"NAME": "postgres", "SERIALIZE": False}

DATABASES = {
    "default": {
        "ENGINE": "django_multitenant.backends.postgresql",
        "NAME": "postgres",
        "USER": "postgres",
        "PASSWORD": "",
        "HOST": "localhost",
        "PORT": 5600,
        "TEST": test_db,
    }
}

SITE_ID = 1
DEBUG = True

MIDDLEWARE = (
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
    "django.contrib.messages",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django_multitenant",
    "django_multitenant.tests",
]

SECRET_KEY = "blabla"

ROOT_URLCONF = "django_multitenant.tests.urls"


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.i18n",
            ],
        },
    },
]

USE_CITUS = True
CITUS_EXTENSION_INSTALLED = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
USE_TZ = True
