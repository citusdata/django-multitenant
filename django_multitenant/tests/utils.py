def undistribute_table(connection, table_name):
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


def is_table_distributed(connection, table_name, column_name):
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

    return distributed
