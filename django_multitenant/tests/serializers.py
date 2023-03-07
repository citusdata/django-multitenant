from rest_framework import serializers
from .models import Store


class StoreSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Store
        fields = ["name", "address", "email"]
