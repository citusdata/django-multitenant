from django_multitenant.utils import set_current_tenant

from django_multitenant.views import get_tenant


class MultitenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user and not request.user.is_anonymous:
            tenant = get_tenant(request)
            set_current_tenant(tenant)
        return self.get_response(request)
