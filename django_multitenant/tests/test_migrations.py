from django.db import connection
from django.db.migrations.migration import Migration
from django.db.migrations.recorder import MigrationRecorder
from django.db.migrations.state import ModelState, ProjectState
from django.conf import settings
from django.test import TransactionTestCase

from django_multitenant.db import migrations


if settings.USE_CITUS:

    class MigrationTest(TransactionTestCase):
        def undistribute_table(self, table_name):
            queries = [
                "CREATE TABLE %(table_name)s_bis (LIKE %(table_name)s INCLUDING ALL);"
                "CREATE TEMP TABLE %(table_name)s_temp AS SELECT * FROM %(table_name)s;"
                "INSERT INTO %(table_name)s_bis SELECT * FROM %(table_name)s_temp;"
                "DROP TABLE %(table_name)s CASCADE;"
                "ALTER TABLE %(table_name)s_bis RENAME TO %(table_name)s;"
            ]

            with connection.cursor() as cursor:
                for query in queries:
                    cursor.execute(query % {"table_name": table_name})

        def assertTableIsDistributed(self, table_name, column_name, value=True):
            query = """
            SELECT logicalrelid, pg_attribute.attname
            FROM pg_dist_partition
            INNER JOIN pg_attribute ON (logicalrelid=attrelid)
            WHERE logicalrelid::varchar(255) = '{}'
            AND partmethod='h'
            AND attnum=substring(partkey from '%:varattno #"[0-9]+#"%' for '#')::int;
            """
            distributed = False
            with connection.cursor() as cursor:
                cursor.execute(query.format(table_name))
                row = cursor.fetchone()

                if row and row[1] == column_name:
                    distributed = True

                self.assertEqual(distributed, value)

        def assertTableIsNotDistributed(self, table_name, column_name, value=True):
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

                distributed = True if row else False

            self.assertEqual(distributed, value)

        def assertTableIsNotReference(self, table_name, value=False):
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
            self.undistribute_table("tests_migrationtestmodel")

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
            self.undistribute_table("tests_migrationtestreferencemodel")

        def test_reference_different_app_table(self):
            project_state = ProjectState(real_apps={"auth"})
            operation = migrations.Distribute("auth.User", reference=True)

            self.assertEqual(
                operation.describe(),
                "Run create_(distributed/reference)_table statement",
            )
            self.assertTableIsNotReference("auth_user")
            new_state = project_state.clone()

            with connection.schema_editor() as editor:
                operation.database_forwards("tests", editor, project_state, new_state)

            self.assertTableIsReference("auth_user")
            self.undistribute_table("auth_user")
