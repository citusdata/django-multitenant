import uuid

from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver


from django_multitenant.models import TenantModel
from django_multitenant.fields import TenantForeignKey


class Country(models.Model):
    name = models.CharField(max_length=255)

class Account(TenantModel):
    name = models.CharField(max_length=255)
    domain = models.CharField(max_length=255)
    subdomain = models.CharField(max_length=255)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)

    # TODO change to Meta
    tenant_id = 'id'


class Manager(TenantModel):
    name = models.CharField(max_length=255)
    account = models.ForeignKey(Account, on_delete=models.CASCADE,
                                related_name='managers')

    tenant_id = 'account_id'


class Project(TenantModel):
    name = models.CharField(max_length=255)
    account = models.ForeignKey(Account, related_name='projects',
                                on_delete=models.CASCADE)
    managers = models.ManyToManyField(Manager, through='ProjectManager')
    tenant_id = 'account_id'


class ProjectManager(TenantModel):
    project = TenantForeignKey(Project, on_delete=models.CASCADE)
    manager = TenantForeignKey(Manager, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)

    tenant_id = 'account_id'



class Task(TenantModel):
    name = models.CharField(max_length=255)
    project = TenantForeignKey(Project, on_delete=models.CASCADE,
                               related_name='tasks')
    account = models.ForeignKey(Account, on_delete=models.CASCADE)

    tenant_id = 'account_id'


class SubTask(TenantModel):
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    task = TenantForeignKey(Task, on_delete=models.CASCADE)
    project = TenantForeignKey(Project, on_delete=models.CASCADE, null=True)

    tenant_id = 'account_id'

class UnscopedModel(models.Model):
    name = models.CharField(max_length=255)


class AliasedTask(TenantModel):
    project_alias = TenantForeignKey(Project, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)

    tenant_id = 'account_id'


# Models for UUID tests
class Organization(TenantModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    tenant_id = 'id'


class Record(TenantModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    organization = TenantForeignKey(Organization, on_delete=models.CASCADE)

    tenant_id = 'organization_id'



class TenantNotIdModel(TenantModel):
    tenant_column = models.IntegerField(primary_key=True, editable=False)
    name = models.CharField(max_length=255)

    tenant_id = 'tenant_column'



class SomeRelatedModel(TenantModel):
    related_tenant = models.ForeignKey(TenantNotIdModel, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    tenant_id = 'related_tenant_id'
