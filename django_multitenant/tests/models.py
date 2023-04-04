import uuid

from django.db import models

from django.contrib.auth import get_user_model

from django_multitenant.mixins import TenantModelMixin, TenantManagerMixin
from django_multitenant.models import TenantModel
from django_multitenant.fields import TenantForeignKey


class Country(models.Model):
    name = models.CharField(max_length=255)


class Account(TenantModel):
    name = models.CharField(max_length=255)
    domain = models.CharField(max_length=255)
    subdomain = models.CharField(max_length=255)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    employee = models.ForeignKey(
        "Employee",
        on_delete=models.CASCADE,
        related_name="accounts",
        null=True,
        blank=True,
    )

    # TODO change to Meta
    tenant_id = "id"


class Employee(models.Model):
    # Reference table
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="employees",
    )
    created_by = models.ForeignKey(
        "self",
        blank=True,
        null=True,
        related_name="users_created",
        on_delete=models.SET_NULL,
    )

    name = models.CharField(max_length=255)


class ModelConfig(TenantModel):
    name = models.CharField(max_length=255)
    account = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name="configs"
    )
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="configs",
        null=True,
        blank=True,
    )

    tenant_id = "account_id"


class Manager(TenantModel):
    name = models.CharField(max_length=255)
    account = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name="managers"
    )
    tenant_id = "account_id"


class Project(TenantModel):
    name = models.CharField(max_length=255)
    account = models.ForeignKey(
        Account, related_name="projects", on_delete=models.CASCADE
    )
    managers = models.ManyToManyField(Manager, through="ProjectManager")
    employee = models.ForeignKey(
        Employee,
        related_name="projects",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    tenant_id = "account_id"


class ProjectManager(TenantModel):
    project = TenantForeignKey(
        Project, on_delete=models.CASCADE, related_name="projectmanagers"
    )
    manager = TenantForeignKey(Manager, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)

    tenant_id = "account_id"


class TaskQueryset(models.QuerySet):
    def opened(self):
        return self.filter(opened=True)

    def closed(self):
        return self.filter(opened=False)


class TaskManager(TenantManagerMixin, models.Manager):
    _queryset_class = TaskQueryset

    def opened(self):
        return self.get_queryset().opened()

    def closed(self):
        return self.get_queryset().closed()


class Task(TenantModelMixin, models.Model):
    name = models.CharField(max_length=255)
    project = TenantForeignKey(Project, on_delete=models.CASCADE, related_name="tasks")
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    opened = models.BooleanField(default=True)

    parent = TenantForeignKey(
        "self", on_delete=models.CASCADE, db_index=False, blank=True, null=True
    )

    objects = TaskManager()

    tenant_id = "account_id"


class SubTask(TenantModel):
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    task = TenantForeignKey(Task, on_delete=models.CASCADE)
    project = TenantForeignKey(Project, on_delete=models.CASCADE, null=True)

    tenant_id = "account_id"


class UnscopedModel(models.Model):
    name = models.CharField(max_length=255)


class AliasedTask(TenantModel):
    project_alias = TenantForeignKey(Project, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)

    tenant_id = "account_id"


class Revenue(TenantModel):
    # To test for correct tenant_id push down in query
    acc = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="revenues")
    project = TenantForeignKey(
        Project, on_delete=models.CASCADE, related_name="revenues"
    )
    value = models.CharField(max_length=30)

    tenant_id = "acc_id"


# Models for UUID tests
class Organization(TenantModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)

    class TenantMeta:
        tenant_field_name = "id"


class Record(TenantModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    organization = TenantForeignKey(Organization, on_delete=models.CASCADE)

    class TenantMeta:
        tenant_id = "organization_id"


class TenantNotIdModel(TenantModel):
    tenant_column = models.IntegerField(primary_key=True, editable=False)
    name = models.CharField(max_length=255)

    tenant_id = "tenant_column"


class SomeRelatedModel(TenantModel):
    related_tenant = models.ForeignKey(TenantNotIdModel, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    tenant_id = "related_tenant_id"


class MigrationTestModel(TenantModel):
    name = models.CharField(max_length=255)
    tenant_id = "id"


class MigrationTestReferenceModel(models.Model):
    name = models.CharField(max_length=255)


class Tenant(TenantModel):
    tenant_id = "id"
    name = models.CharField("tenant name", max_length=100)


class Business(TenantModel):
    tenant = models.ForeignKey(Tenant, blank=True, null=True, on_delete=models.SET_NULL)
    bk_biz_id = models.IntegerField("business ID")
    bk_biz_name = models.CharField("business name", max_length=100)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["id", "tenant_id"], name="unique_business_tenant"
            )
        ]

    class TenantMeta:
        tenant_field_name = "tenant_id"


class Template(TenantModel):
    tenant = models.ForeignKey(Tenant, blank=True, null=True, on_delete=models.SET_NULL)
    business = TenantForeignKey(
        Business, blank=True, null=True, on_delete=models.SET_NULL
    )
    name = models.CharField("name", max_length=100)

    class TenantMeta:
        tenant_field_name = "tenant_id"


# Non-Tenant Model which should be Reference Table
# to be referenced by Store which is a Tenant Model
# in Citus 10.
class Staff(models.Model):
    name = models.CharField(max_length=50)


class Store(TenantModel):
    tenant_id = "id"
    name = models.CharField(max_length=50)
    address = models.CharField(max_length=255)
    email = models.CharField(max_length=50)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True)

    store_staffs = models.ManyToManyField(
        Staff, through="StoreStaff", through_fields=("store", "staff"), blank=True
    )


class StoreStaff(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)


class Product(TenantModel):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    tenant_id = "store_id"
    name = models.CharField(max_length=255)
    description = models.TextField()

    class Meta:
        unique_together = ["id", "store"]


class Purchase(TenantModel):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    tenant_id = "store_id"
    product_purchased = models.ManyToManyField(
        Product, through="Transaction", through_fields=("purchase", "product")
    )

    class Meta:
        unique_together = ["id", "store"]


class Transaction(TenantModel):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    tenant_id = "store_id"
    purchase = TenantForeignKey(
        Purchase, on_delete=models.CASCADE, blank=True, null=True
    )
    product = TenantForeignKey(Product, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)


class MigrationUseInMigrationsModel(TenantModel):
    name = models.CharField(max_length=255)

    class TenantMeta:
        tenant_field_name = "id"
