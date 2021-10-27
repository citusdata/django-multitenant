from django.apps.registry import apps as global_apps
from django.db import connection
from django.db.migrations.operations.base import Operation
from django.db.migrations.state import _get_app_label_and_model_name

from django_multitenant.utils import get_tenant_column


class Distribute(Operation):
    def __init__(self, model_name, reference=False, reverse_ignore=False):
        self.reverse_ignore = reverse_ignore
        self.model_name = model_name
        self.reference = reference

    def get_query(self):
        if self.reference:
            return "SELECT create_reference_table(%s)"

        return "SELECT create_distributed_table(%s, %s)"

    def state_forwards(self, app_label, state):
        # Distribute objects have no state effect.
        pass

    def get_fake_model(self, app_label, from_state):
        # The following step is necessary because if we distribute a table from a different app
        # than the one in which the migrations/00XX_distribute.py is, we need to load the different
        # app to get the model
        new_app_label, self.model_name = _get_app_label_and_model_name(self.model_name)
        app_label = new_app_label or app_label

        # Using the current state of the migration, it retrieves a class '__fake__.ModelName'
        # As it's using the state, if the model has been deleted since, it will still find the model
        # This will fail if it's trying to find a model that never existed
        return from_state.apps.get_model(app_label, self.model_name)

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        if self.reverse_ignore:
            return
        fake_model = self.get_fake_model(app_label, from_state)

        self.args = [fake_model._meta.db_table]

        schema_editor.execute("SELECT undistribute_table(%s)", params=self.args)

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        fake_model = self.get_fake_model(app_label, from_state)

        # We now need the real model, the problem is that the __fake__ model doesn't have access
        # to anything else (functions / properties) than the Fields
        # So to access the model.tenant_id, we need this.
        app = global_apps.get_app_config(app_label)
        self.model = None

        for model in app.get_models():
            if model.__name__ == self.model_name:
                self.model = model

        if fake_model and not self.model:
            # The model has been deleted
            # We can't distribute that table as we don't have the initial model anymore
            # So no idea what the tenant column is
            # However, as there are create foreign key constraints that will fail in further migrations
            # We need to make it a reference table
            self.reference = True

        self.args = [fake_model._meta.db_table]
        if not self.reference:
            self.args.append(get_tenant_column(self.model))

        schema_editor.execute(self.get_query(), params=self.args)

    def describe(self):
        return "Run create_(distributed/reference)_table statement"
