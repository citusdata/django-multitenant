from .settings import *

DATABASES["default"]["ENGINE"] = "django_multitenant.backends.postgis"
DATABASES["default"]["PORT"] = 5605

INSTALLED_APPS.append(
    "django.contrib.gis",
)

USE_GIS = True

USE_CITUS = False
CITUS_EXTENSION_INSTALLED = False
