# Generated by Django 2.2.9 on 2020-01-28 08:53

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings

from django_multitenant.db import migrations as tenant_migrations


def get_operations():
    operations = [
        migrations.CreateModel(
            name="Employee",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                (
                    "account",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="employees",
                        db_constraint=False,
                        to="tests.Account",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="users_created",
                        to="tests.Employee",
                    ),
                ),
            ],
        ),
    ]

    if settings.USE_CITUS:
        operations += [
            tenant_migrations.Distribute(
                "Employee", reference=True, reverse_ignore=True
            ),
        ]

    return operations


class Migration(migrations.Migration):

    dependencies = [
        ("tests", "0016_auto_20191025_0844"),
    ]

    operations = get_operations()
