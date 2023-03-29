from django.db import connection

from django.db.migrations.state import ProjectState
from django.conf import settings
from django.test import TransactionTestCase

from django_multitenant.db import migrations
from .utils import undistribute_table, is_table_distributed


if settings.USE_CITUS:

    class MigrationTest(TransactionTestCase):
        def assertTableIsDistributed(self, table_name, column_name, value=True):
            distributed = is_table_distributed(connection, table_name, column_name)

            self.assertEqual(distributed, value)

        def assertTableIsNotDistributed(self, table_name, column_name):
            return self.assertTableIsDistributed(table_name, column_name, value=False)

        def assertTableIsReference(self, table_name, value=False):
            query = """
            SELECT 1
            FROM pg_dist_partition
            WHERE logicalrelid::varchar(255) = %s
            AND partmethod='m';
            """
            distributed = False

            with connection.cursor() as cursor:
                cursor.execute(query, [table_name])
                row = cursor.fetchone()

                distributed = bool(row)

            self.assertEqual(distributed, value)

        def assertTableIsNotReference(self, table_name):
            return self.assertTableIsReference(table_name, value=False)

        def test_distribute_table(self):
            project_state = ProjectState(real_apps={"tests"})
            operation = migrations.Distribute("MigrationTestModel")

            self.assertEqual(
                operation.describe(),
                "Run create_(distributed/reference)_table statement",
            )

            self.assertTableIsNotDistributed("tests_migrationtestmodel", "id")
            new_state = project_state.clone()

            with connection.schema_editor() as editor:
                operation.database_forwards("tests", editor, project_state, new_state)

            self.assertTableIsDistributed("tests_migrationtestmodel", "id")
            undistribute_table(connection, "tests_migrationtestmodel")

        def test_reference_table(self):
            project_state = ProjectState(real_apps={"tests"})
            operation = migrations.Distribute(
                "MigrationTestReferenceModel", reference=True
            )

            self.assertEqual(
                operation.describe(),
                "Run create_(distributed/reference)_table statement",
            )
            self.assertTableIsNotReference("tests_migrationtestreferencemodel")
            new_state = project_state.clone()

            with connection.schema_editor() as editor:
                operation.database_forwards("tests", editor, project_state, new_state)

            self.assertTableIsReference("tests_migrationtestreferencemodel")
            undistribute_table(connection, "tests_migrationtestreferencemodel")

        def test_reference_different_app_table(self):
            project_state = ProjectState(real_apps={"auth"})
            operation = migrations.Distribute("auth.Group", reference=True)

            self.assertEqual(
                operation.describe(),
                "Run create_(distributed/reference)_table statement",
            )
            self.assertTableIsNotReference("auth_group")
            new_state = project_state.clone()

            with connection.schema_editor() as editor:
                operation.database_forwards("tests", editor, project_state, new_state)

            self.assertTableIsReference("auth_group")
            undistribute_table(connection, "auth_group")
