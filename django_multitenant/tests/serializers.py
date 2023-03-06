from rest_framework import serializers
from .models import Account,Store

class AccountSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Account
        fields = [ 'name', 'domain', 'subdomain']


class StoreSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Store
        fields = [ 'name', 'address', 'email']