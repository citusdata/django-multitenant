# Generated by Django 2.2.9 on 2020-01-29 04:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("tests", "0019_auto_20200129_0357"),
    ]

    atomic = False

    operations = [
        migrations.AddField(
            model_name="project",
            name="employee",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="projects",
                to="tests.Employee",
            ),
        ),
    ]
