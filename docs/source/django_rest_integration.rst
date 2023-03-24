Using with Django Rest Framwork
=================================

1. Add ``'django_multitenant.middleware.MultitenantMiddleware'`` to the ``MIDDLEWARE`` list in your ``settings.py`` file:

    .. code-block:: python

        MIDDLEWARE = [
            # other middleware
            'django_multitenant.middleware.MultitenantMiddleware',
        ]

2. Monkey patch ``django_multitenant.views.get_tenant`` function with your own function which returns tenant object:

    .. code-block:: python

        # views.py

        def tenant_func(request):
            return Store.objects.filter(user=request.user).first()

        # Monkey patching get_tenant function
        from django_multitenant import views
        views.get_tenant = tenant_func
3. Add your viewset derived from TenantModelViewSet:

    .. code-block:: python

        # views.py

        class StoreViewSet(TenantModelViewSet):
            """
            API endpoint that allows groups to be viewed or edited.
            """
            model_class = Store
            serializer_class = StoreSerializer
            permission_classes = [permissions.IsAuthenticated]

    In the above example, we're defining a StoreViewSet that is derived from TenantModelViewSet. This means that any views in StoreViewSet will automatically be scoped to the current tenant based on the tenant attribute of the request object.

    You can then define the queryset and serializer_class attributes as usual. Note that you do not need to filter the queryset by the current tenant, as this is automatically handled by django-multitenant.

    That's it! With these steps, you should be able to use django-multitenant with Django Rest Framework to build multi-tenant applications.


