#Describe Schema

#Import the library
from stores import middleware

#Set the current tenant
s=Store.objects.all()[0];
middleware.set_current_tenant(s);


#Commands

#Get me all the products belonging to the current store.
Product.objects.all()
#Hop to the logs and show the query being generated.

#Get me all the purchases of iphone-7s
Purchase.objects.filter(product__name='iphone-7s');

#Total number of the iphone-7ss purchased
Purchase.objects.filter(product__name='iphone-7s').aggregate(Sum('quantity'));

#Now set the tenant to None and run the above query
middleware.set_current_tenant(None);
Purchase.objects.filter(product__name='iphone-7s').aggregate(Sum('quantity'));


#Create a new product
p=Product(id=13,name='ps4',description='product',store_id=1);
p.save() #Fails
#Show logs

#Reset the tenant
middleware.set_current_tenant(s);
p.save() #Passes
#Show logs


#Subqueries Example
#Get me all the purchases of the iphone-7s
p=Product.objects.filter(name='iphone-7s');
Purchase.objects.filter(product__in=p);
#Show logs

