from django.urls import path, include
from rest_framework import routers
from .views import AccountViewSet

router = routers.DefaultRouter()
router.register(r'account', AccountViewSet, basename='Account')

urlpatterns = [
    path('', include(router.urls)),
]