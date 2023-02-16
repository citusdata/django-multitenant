import logging
import django
from django.db.backends.postgresql.base import (
    DatabaseFeatures as PostgresqlDatabaseFeatures,
    DatabaseWrapper as PostgresqlDatabaseWrapper,
    DatabaseSchemaEditor as PostgresqlDatabaseSchemaEditor,
)

from django_multitenant.backends import mixins

logger = logging.getLogger(__name__)


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
