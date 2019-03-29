import logging
from django.apps import apps
from django.db.backends.postgresql.base import (
    DatabaseWrapper as PostgresqlDatabaseWrapper,
    DatabaseSchemaEditor as PostgresqlDatabaseSchemaEditor,
    DatabaseCreation,
    DatabaseFeatures,
    DatabaseOperations,
    DatabaseClient,
    DatabaseIntrospection
)
from django_multitenant.fields import TenantForeignKey

logger = logging.getLogger(__name__)


class DatabaseSchemaEditor(PostgresqlDatabaseSchemaEditor):
    # Override
    def __enter__(self):
        ret = super(DatabaseSchemaEditor, self).__enter__()
        return ret

    # Override
    def _alter_field(self, model, old_field, new_field, old_type, new_type,
                     old_db_params, new_db_params, strict=False):

        super(DatabaseSchemaEditor, self)._alter_field(model, old_field,
                                                       new_field, old_type,
                                                       new_type, old_db_params,
                                                       new_db_params, strict)

        # If the pkey was dropped in the previous distribute migration,
        # foreign key constraints didn't previously exists so django does not
        # recreated them.
        # Here we test if we are in this case
        if isinstance(new_field, TenantForeignKey) and new_field.db_constraint:
            fk_names = self._constraint_names(model, [new_field.column], foreign_key=True)
            if not fk_names:
                self.execute(self._create_fk_sql(model, new_field,
                                                 "_fk_%(to_table)s_%(to_column)s"))

    # Override
    def _create_fk_sql(self, model, field, suffix):
        if isinstance(field, TenantForeignKey):
            from_table = model._meta.db_table
            from_columns = field.column, self.get_tenant_column(model)
            to_table = field.target_field.model._meta.db_table
            to_columns = field.target_field.column, self.get_tenant_column(field.target_field.model)
            suffix = suffix % {
                "to_table": to_table,
                "to_column": '_'.join(to_columns),
            }

            return self.sql_create_fk % {
                "table": self.quote_name(from_table),
                "name": self.quote_name(self._create_index_name(model, from_columns, suffix=suffix)),
                "column": ', '.join([self.quote_name(from_col) for from_col in from_columns]),
                "to_table": self.quote_name(field.target_field.model._meta.db_table),
                "to_column": ', '.join([self.quote_name(to_col) for to_col in to_columns]),
                "deferrable": self.connection.ops.deferrable_sql(),
            }
        return super(DatabaseSchemaEditor, self)._create_fk_sql(model, field, suffix)

    # Override
    def execute(self, sql, params=()):
        # Hack: Citus will throw the following error if these statements are
        # not executed separately: "ERROR: cannot execute multiple utility events"
        if not params:
            for statement in str(sql).split(';'):
                if statement and not statement.isspace():
                    super(DatabaseSchemaEditor, self).execute(statement)
        else:
            super(DatabaseSchemaEditor, self).execute(sql, params)

    @staticmethod
    def get_tenant_column(model):
        app_label = model._meta.app_label
        model_name = model._meta.model_name
        for candidate_model in apps.get_models():
            if (candidate_model._meta.app_label == app_label
                and candidate_model._meta.model_name == model_name):
                return candidate_model.tenant_id
        else:
            # here you can do fallback logic if no model with db_table found
            raise ValueError('Model {}.{} not found!'.format(app_label, model_name))


    def _create_index_name(self, model, column_names, suffix=""):
        # compat with django 2.X and django 1.X
        import django

        if not isinstance(model, str) and django.VERSION[0] > 1:
            model = model._meta.db_table

        return super(DatabaseSchemaEditor, self)._create_index_name(model,
                                                                    column_names,
                                                                    suffix=suffix)


class DatabaseWrapper(PostgresqlDatabaseWrapper):
    # Override
    SchemaEditorClass = DatabaseSchemaEditor
