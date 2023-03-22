Using Django ORM Migrations with Django Multitenant
====================================================

Django Multitenant employs transient fields to define the tenant field for the model. 
In Django `documents <https://docs.djangoproject.com/en/4.1/ref/migration-operations/#runpython>`_, the 'apps' parameter of the method being executed by 'RunPython' is recommended to obtain the models. 
However, using this parameter creates 'fake' models that lack transient fields, rendering the apps parameter ineffective. 
In such situations, it is recommended to utilize the apps module from django.apps or directly import the model using the import clause. 
Two sample usages have been provided for this purpose. 
The first involves using the apps module to obtain the desired model, whereas the second entails importing the model class directly.

Sample Usages 

1. Use apps module from  to get the model you want to use instead of the 'apps' in the method being executed in RunPython
``` python
from django.apps import apps  
MigrationUseInMigrationsModel = apps.get_model("tests", "MigrationUseInMigrationsModel")
MigrationUseInMigrationsModel.objects.create(name="test")
```
2. Use directly the model class import 
``` python
from .models import  MigrationUseInMigrationsModel 

MigrationUseInMigrationsModel.objects.create(name="test")
```