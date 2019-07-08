import logging
from django.conf import settings
from django.db import connections
from django.db.backends.postgresql.base import (
    DatabaseWrapper as PostgresqlDatabaseWrapper,
    DatabaseSchemaEditor as PostgresqlDatabaseSchemaEditor,
    DatabaseCreation as PostgresqlDatabaseCreation,
)
from django_multitenant.fields import (
    TenantForeignKey,
    TenantPrimaryKey,
    TenantOneToOneField,
)
from django_multitenant.mixins import TenantModelMixin
from django_multitenant.utils import (
    get_model_by_db_table,
    get_tenant_column,
    get_tenant_field,
)

logger = logging.getLogger(__name__)


class DatabaseSchemaEditor(PostgresqlDatabaseSchemaEditor):
    # Override
    def __enter__(self, *args, **kwargs):
        self.table_distribution_sql = []
        self.composite_constraints_sql = []
        ret = super(DatabaseSchemaEditor, self).__enter__()
        return ret

    # Override
    def _create_fk_sql(self, model, field, suffix):
        if isinstance(field, TenantForeignKey):
            try:
                # test if both models exists
                # This case happens when we are running from scratch migrations and one model was removed from code
                # In the previous migrations we would still be creating the foreign key
                from_model = get_model_by_db_table(model._meta.db_table)
                to_model = get_model_by_db_table(
                    field.target_field.model._meta.db_table
                )
            except ValueError:
                return None

            from_columns = field.column, get_tenant_column(from_model)
            to_columns = field.target_field.column, get_tenant_column(to_model)
            suffix = suffix % {
                "to_table": field.target_field.model._meta.db_table,
                "to_column": "_".join(to_columns),
            }

            return self.sql_create_fk % {
                "table": self.quote_name(model._meta.db_table),
                "name": self.quote_name(
                    self._create_index_name(model, from_columns, suffix=suffix)
                ),
                "column": ", ".join(
                    [self.quote_name(from_col) for from_col in from_columns]
                ),
                "to_table": self.quote_name(field.target_field.model._meta.db_table),
                "to_column": ", ".join(
                    [self.quote_name(to_col) for to_col in to_columns]
                ),
                "deferrable": self.connection.ops.deferrable_sql(),
            }
        return super(DatabaseSchemaEditor, self)._create_fk_sql(model, field, suffix)

    # Override
    def execute(self, sql, params=()):
        # Hack: Citus will throw the following error if these statements are
        # not executed separately: "ERROR: cannot execute multiple utility events"
        if sql and not params:
            for statement in str(sql).split(";"):
                if statement and not statement.isspace():
                    super(DatabaseSchemaEditor, self).execute(statement)
        elif sql:
            super(DatabaseSchemaEditor, self).execute(sql, params)

    def _create_index_name(self, model, column_names, suffix=""):
        # compat with django 2.X and django 1.X
        import django

        if not isinstance(model, str) and django.VERSION[0] > 1:
            model = model._meta.db_table

        return super(DatabaseSchemaEditor, self)._create_index_name(
            model, column_names, suffix=suffix
        )

    # Override
    def column_sql(self, model, field, include_default=False):
        if isinstance(field, TenantPrimaryKey):
            # We can't create a primary key over one column in our sharded setup,
            # but Django needs to believe we have a primary key, so only remove it now that we're actually writing SQL,
            # and add the correct constraint in create_model below.
            field.primary_key = False
        elif isinstance(field, TenantOneToOneField):
            # OneToOneFields write a UNIQUE column, but this isn't possible with our sharding, so remove it
            # and add the correct constraint in create_model below.
            field._unique = False
            # OneToOneFields write a Foreign Key constraint, which would require the field we point to to be unique.
            # Obviously it can't be, due to sharding, so opt out of this constraint.
            field.db_constraint = False
        sql, params = super().column_sql(model, field, include_default)
        return sql, params

    # Override
    def create_model(self, model):
        super().create_model(model)
        table_name = model._meta.db_table
        quoted_table_name = self.quote_name(table_name)

        for field in model._meta.local_fields:
            if isinstance(field, TenantPrimaryKey):
                quoted_tenant_column = self.quote_name(field.tenant_id)
                constraint_name = self.quote_name(f"{table_name}_pkey")
                self.composite_constraints_sql.extend(
                    [
                        f"""
                    ---
                    --- Add composite primary key to {table_name}
                    ---
                    ALTER TABLE {quoted_table_name}
                    ADD CONSTRAINT {constraint_name}
                    PRIMARY KEY ({quoted_tenant_column}, id)
                    """
                    ]
                )
            elif isinstance(field, TenantOneToOneField):
                tenant_column = field.tenant_id
                quoted_tenant_column = self.quote_name(tenant_column)
                one_to_one_column = field.column
                quoted_one_to_one_column = self.quote_name(one_to_one_column)
                constraint_name = self.quote_name(
                    self._create_index_name(
                        table_name, (tenant_column, one_to_one_column), "_uniq"
                    )
                )
                self.composite_constraints_sql.extend(
                    [
                        f"""
                    ---
                    --- Add composite constraint for onetoonefield to {table_name}
                    ---
                    ALTER TABLE {quoted_table_name}
                    ADD CONSTRAINT {constraint_name}
                    UNIQUE ({quoted_tenant_column}, {quoted_one_to_one_column})
                    """
                    ]
                )

        if issubclass(model, TenantModelMixin):
            if table_name == "core_brand":
                # Brand is distributed, but has no TenantPrimaryKey, as it is the model the other tenants are based on.
                distribution_column_name = "id"
            else:
                distribution_column_name = get_tenant_field(model)
            self.table_distribution_sql.extend(
                [
                    f"""
                ---
                --- Register {table_name} as a distributed (sharded) table
                ---
                SELECT CREATE_DISTRIBUTED_TABLE('{table_name}', '{distribution_column_name}');
                """
                ]
            )

    def __exit__(self, exc_type, exc_value, traceback):
        # We need to ensure our tables are distributed correctly before we try to apply constraints,
        # as otherwise we'd end up trying to apply constraints between distributed and local tables, which is invalid.
        if exc_type is None:
            for sql in self.table_distribution_sql:
                self.execute(sql)
            for sql in self.composite_constraints_sql:
                self.execute(sql)
        return super().__exit__(exc_type, exc_value, traceback)


class TestDBCursor(object):
    def __init__(self, connection, test_db_name):
        self.connection = connection
        self.cursor = None
        self.current_db_name = settings.DATABASES[self.connection.alias]["NAME"]

        self.test_database_name = test_db_name

    def __enter__(self):
        self.connection.close()
        settings.DATABASES[self.connection.alias]["NAME"] = self.test_database_name
        self.connection.settings_dict["NAME"] = self.test_database_name
        self.cursor = connections[self.connection.alias].cursor()
        return self.cursor

    def __exit__(self, *args):
        self.connection.close()
        self.cursor = None


class DatabaseCreation(PostgresqlDatabaseCreation):
    def _execute_create_test_db(self, cursor, *args, **kwargs):
        super()._execute_create_test_db(cursor, *args, **kwargs)
        cursor.execute(
            f"SELECT success FROM RUN_COMMAND_ON_WORKERS('CREATE DATABASE {self._get_test_db_name()}')"
        )
        success = cursor.fetchone()[0]
        if not success:
            raise ValueError("DB already exists on worker")

    def _create_test_db(self, verbosity, autoclobber, keepdb=False):
        """
        Internal implementation - create the test db tables.
        """
        test_database_name = self._get_test_db_name()
        test_db_params = {
            "dbname": self.connection.ops.quote_name(test_database_name),
            "suffix": self.sql_table_creation_suffix(),
        }
        worker_details = []

        # Create the test database and connect to it.
        with self._nodb_connection.cursor() as cursor:
            try:
                self._execute_create_test_db(cursor, test_db_params, keepdb)
            except Exception as e:
                # if we want to keep the db, then no need to do any of the below,
                # just return and skip it all.
                if keepdb:
                    return test_database_name

                self.log("Got an error creating the test database: %s" % e)
                if not autoclobber:
                    confirm = input(
                        "Type 'yes' if you would like to try deleting the test "
                        "database '%s', or 'no' to cancel: " % test_database_name
                    )
                if autoclobber or confirm == "yes":
                    try:
                        if verbosity >= 1:
                            self.log(
                                "Destroying old test database for alias %s..."
                                % (
                                    self._get_database_display_str(
                                        verbosity, test_database_name
                                    ),
                                )
                            )
                        db_name = test_db_params["dbname"]
                        cursor.execute(
                            f"SELECT * FROM run_command_on_workers('DROP DATABASE IF EXISTS {db_name}')"
                        )
                        cursor.execute(f"DROP DATABASE IF EXISTS {db_name}")
                        self._execute_create_test_db(cursor, test_db_params, keepdb)
                    except Exception as e:
                        self.log("Got an error recreating the test database: %s" % e)
                        sys.exit(2)
                else:
                    self.log("Tests cancelled.")
                    sys.exit(1)

            # Fetch worker details from the existing database on master, so we can set the up on the new database
            cursor.execute("SELECT MASTER_GET_ACTIVE_WORKER_NODES()")
            worker_strings = cursor.fetchall()
            # MASTER_ADD_NODES returns a list of one-tuples of strings of the form '(citus_worker_1, 5432)'
            worker_details = [
                worker_row[0].strip("(").strip(")").split(",")
                for worker_row in worker_strings
            ]

        with TestDBCursor(self.connection, test_database_name) as cursor:
            # Install citus on the test db master
            cursor.execute("CREATE EXTENSION IF NOT EXISTS citus;")
            # Connect worker with master db
            for worker_name, worker_port in worker_details:
                # Make the test database on master aware of the worker
                cursor.execute(
                    f"SELECT * FROM MASTER_ADD_NODE('{worker_name}', {worker_port});"
                )
            cursor.execute(
                f"SELECT RUN_COMMAND_ON_WORKERS($cmd$ CREATE EXTENSION IF NOT EXISTS citus; $cmd$)"
            )

        return test_database_name

    def _destroy_test_db(self, test_database_name, verbosity):
        test_db_name = self.connection.ops.quote_name(test_database_name)
        with self.connection._nodb_connection.cursor() as cursor:
            cursor.execute(f"DROP DATABASE {test_db_name}")
            cursor.execute(
                f"SELECT RUN_COMMAND_ON_WORKERS('DROP DATABASE {test_db_name}')"
            )


class DatabaseWrapper(PostgresqlDatabaseWrapper):
    # Override
    SchemaEditorClass = DatabaseSchemaEditor
    creation_class = DatabaseCreation
