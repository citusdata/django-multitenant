from django_multitenant import views
from .base import BaseTestCase


from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from .models import Store
from .serializers import StoreSerializer


class ViewSetTestCases(BaseTestCase):
    def setUp(self):
        def tenant_func(request):
            return Store.objects.filter(user=request.user).first()

        views.get_tenant = tenant_func

        self.user = get_user_model().objects.create_user(
            username="testuser", email="testuser@example.com", password="testpass"
        )

        self.user2 = get_user_model().objects.create_user(
            username="testuser2", email="testuser2@example.com", password="testpass2"
        )
        self.client = APIClient()
        self.client.login(username="testuser", password="testpass")

    def test_list(self):
        # create some test objects

        store = Store.objects.create(name="store1", user=self.user)
        store.save()

        store2 = Store.objects.create(name="store2", user=self.user2)
        store2.save()

        # make the request and check the response if it is matching the store object
        # related to the test_user which is the logged in user

        response = self.client.get("/store/")
        expected_data = StoreSerializer([store], many=True).data
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, expected_data)
