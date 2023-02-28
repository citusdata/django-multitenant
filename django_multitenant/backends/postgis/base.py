from django.contrib.gis.db.backends.postgis.base import (
    DatabaseWrapper as PostGISDatabaseWrapper,
)
from django.contrib.gis.db.backends.postgis.features import (
    DatabaseFeatures as PostGISDatabaseFeatures,
)
from django.contrib.gis.db.backends.postgis.schema import (
    PostGISSchemaEditor as BasePostGISSchemaEditor,
)

from django_multitenant import mixins


class DatabaseSchemaEditor(mixins.DatabaseSchemaEditorMixin, BasePostGISSchemaEditor):
    pass


# noqa
class TenantDatabaseFeatures(mixins.DatabaseFeaturesMixin, PostGISDatabaseFeatures):
    pass


class DatabaseWrapper(PostGISDatabaseWrapper):
    # Override
    SchemaEditorClass = DatabaseSchemaEditor
    features_class = TenantDatabaseFeatures

    # Override
    # The PostGIS DatabaseWrapper overrides the init function and sets the database features explicitly
    # Which will override the usage of `features_class`.
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.features = self.features_class(self)
