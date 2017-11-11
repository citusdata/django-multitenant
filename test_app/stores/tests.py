from django.test import TestCase

# Create your tests here.
from stores import middleware
s=Store.objects.all()[0]
middleware.set_current_tenant(s)

#Random tests I tried.
#(Very rough)
#Will make it in a more readable format in the future.
Tests:

#This is how you set the tenant.
s=Store.objects.all()[0]
middleware.set_current_tenant(s)

Product.objects.get_queryset()

p=Purchase.objects.filter(id=1).filter(store__name='sai').filter(product__description='')

p=Purchase.objects.filter()

p=Purchase.objects.filter(id=1).update(id=1)

s=Store.objects.all()[0]
middleware.set_current_tenant(s)
p=Product(8,1,'sai','hello')
p.save()

p=Product.objects.count()

p=Product.objects.filter(store__name='sai').count()

p=Product.objects.filter(name='sai').aggregate(Avg('store_id'))


s=Store.objects.all()
p=Product.objects.filter(store__in=s)

p=Product.objects.filter(name='sai');
pur=Purchase.objects.filter(product__in=p);


p=Product.objects.filter(name='sai');
