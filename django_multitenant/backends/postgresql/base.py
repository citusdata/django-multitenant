from django.db.backends.postgresql.base import (
    DatabaseFeatures as PostgresqlDatabaseFeatures,
    DatabaseWrapper as PostgresqlDatabaseWrapper,
    DatabaseSchemaEditor as PostgresqlDatabaseSchemaEditor,
)

from django_multitenant import mixins


class DatabaseSchemaEditor(
    mixins.DatabaseSchemaEditorMixin, PostgresqlDatabaseSchemaEditor
):
    pass


# noqa
class TenantDatabaseFeatures(mixins.DatabaseFeaturesMixin, PostgresqlDatabaseFeatures):
    pass


class DatabaseWrapper(PostgresqlDatabaseWrapper):
    # Override
    SchemaEditorClass = DatabaseSchemaEditor
    features_class = TenantDatabaseFeatures
