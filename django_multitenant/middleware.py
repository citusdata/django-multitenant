from django.conf import settings
from django.apps import apps


from .settings import (TENANT_COOKIE_NAME,
                       TENANT_MODEL_NAME)


class TenantMiddleware(object):
    def __call__(self, request):
        try:
            tenant_id = request.COOKIES.get(TENANT_COOKIE_NAME) or request.session.tenant_id
        except:  # add exception
            raise ImproperlyConfigured('message')

        if not tenant_id:
            return

        # find the settings TENANT_MODEL_NAME
        request.session.tenant_id = tenant_id
        tenant_model = apps.get_model(*TENANT_MODEL_NAME.split('.'))
        request.session.tenant = tenant_model.objects.get(**{tenant_model.tenant_id: tenant_id})

    def process_request(self, request):
        self.__call__(request)  # compat django 1.9
