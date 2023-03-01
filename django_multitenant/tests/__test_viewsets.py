

from .views import AccountViewSet

from .base import BaseTestCase

from django.contrib.auth.models import User
from rest_framework.test import APIClient

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
        request = self.client.get('/account/')
        view = AccountViewSet.as_view({'get': 'list'})
        response = view(request)

        # check that the response contains the correct data
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['name'], 'Object 1')
        self.assertEqual(response.data[1]['name'], 'Object 2')