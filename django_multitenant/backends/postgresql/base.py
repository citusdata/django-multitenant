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
        if isinstance(old_field, TenantForeignKey):
            if old_field.remote_field and old_field.db_constraint:
                fk_names = self._constraint_names(model, [old_field.column, self.get_tenant_column(model)], foreign_key=True)
                if strict and len(fk_names) != 1:
                    raise ValueError("Found wrong number (%s) of foreign key constraints for %s.%s" % (
                        len(fk_names),
                        model._meta.db_table,
                        old_field.column,
                    ))
                for fk_name in fk_names:
                    logger.info('Deleting foreign key constraint "%s"' % fk_name)
                    sql = self._delete_constraint_sql(self.sql_delete_fk, model, fk_name)
                    for statement in sql.split(';'):
                        self.execute(statement)

        return super(DatabaseSchemaEditor, self)._alter_field(model, old_field, new_field, old_type, new_type,
                     old_db_params, new_db_params, strict)

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
            for statement in sql.split(';'):
                if statement:
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


class DatabaseWrapper(PostgresqlDatabaseWrapper):
    # Override
    SchemaEditorClass = DatabaseSchemaEditor
