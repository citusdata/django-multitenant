from .views import AccountViewSet

from .base import BaseTestCase
import django_multitenant

from django.contrib.auth.models import User
from rest_framework.test import APIClient
from .models import Account, Store, Product, Purchase
from .serializers import AccountSerializer,StoreSerializer
from datetime import date

class ViewSetTestCases(BaseTestCase):
    def setUp(self):
        
        def tenant_func(request):
            return Store.objects.filter(user=request.user).first()


        django_multitenant.views.get_tenant = tenant_func

        self.user = User.objects.create_user(
            username="testuser", email="testuser@example.com", password="testpass"
        )
        
        self.user2 = User.objects.create_user(
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

        # product = Product.objects.create(name="product1", store=store)
        # product.save()

        # purchase = Purchase.objects.create(store=store)
        # purchase.save()
        # purchase.product_purchased.add(product, through_defaults={"date": date.today()})

        # simulate a GET request to the list endpoint
        
        mymodel1 = store
        mymodel2 = store2
        response = self.client.get("/store/")
        expected_data = StoreSerializer([mymodel1], many=True).data
        print(expected_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, expected_data)
