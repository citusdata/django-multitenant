from django_multitenant.utils import set_current_tenant

from tutorial.quickstart.base_view import get_tenant
    
class MultitenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user and not request.user.is_anonymous:
            account = get_tenant(request)
            set_current_tenant(account)
        return self.get_response(request)