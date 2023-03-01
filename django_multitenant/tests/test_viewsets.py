

from .views import AccountViewSet

from .base import BaseTestCase

from django.contrib.auth.models import User
from rest_framework.test import APIClient
from .models import Account
from .serializers import AccountSerializer 

class ViewSetTestCases(BaseTestCase):
    def setUp(self):
        
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpass'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_list(self):
        # create some test objects

        # simulate a GET request to the list endpoint
        mymodel1 = self.account_us
        mymodel2 = self.account_in
        response = self.client.get('/account/')
        expected_data = AccountSerializer([mymodel1, mymodel2], many=True).data
        print(expected_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, expected_data)