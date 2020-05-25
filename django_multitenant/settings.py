from django.conf import settings

APP_NAMESPACE = "DJANGO_MULTITENANT"

TENANT_COOKIE_NAME = getattr(settings, 'TENANT_COOKIE_NAME', 'tenant_id')
TENANT_MODEL_NAME = getattr(settings, 'TENANT_MODEL_NAME', None)
CITUS_EXTENSION_INSTALLED = getattr(settings, 'CITUS_EXTENSION_INSTALLED', False)
