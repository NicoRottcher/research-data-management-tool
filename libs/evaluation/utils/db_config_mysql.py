"""
Scripts for MySQL database connection
Created in 2023
@author: Forschungszentrum Jülich GmbH, Nico Röttcher
"""

from pathlib import Path
import sqlalchemy as sql
import pandas as pd
from mysql.connector import Error
import numpy as np
from ipywidgets import *
import warnings
import datetime

# from evaluation.utils import db
import evaluation.utils.db as db
import evaluation.publication.publication_export as publication_export
import evaluation.publication.db_config_binder as db_config_binder

MYSQL = True


def DIR_REPORTS():
    """
    Get directory to store reports,
    if called from a publication folder the processing reports folder of th epublication will be used
    else the standard location on jupyter hub server
    :return: directory to store reports
    """
    pub = publication_export.Publication()
    if pub.created:
        return pub.path_to_jupyter_folder / db_config_binder.REL_DIR_REPORTS
    else:
        return Path(r"/home/hte_admin/sciebo/jupyter/shared/03_processing_reports")


def connect(user="hte_read", echo=False, database=None, host=None):
    """
    method to connect to MySQL database reading database credential from file located up in the system
    :param user: str, optional default 'hte_read'
        name of the MySQL user to connect with to MySQL database
    :param echo: bool, optional default 'False
        whether to use echo parameter in sqlalchemy engine.
        This will print out detailed information on any interaction with the database
    :param database: str or None, default None
        name of the database, forces connection to a different database while keeping other credentials the same
        if None, database name from config file will be used
    :param host: str or None, default None
        host IP-Adress or localhost, forces connection to a different host while keeping other credentials the same
        if None, host from config file will be used
    :return: sqlalchemy.engine
    """
    # style of config file:
    # header line
    # credentials tabulator-separated
    """
    user    password    host    database  
    your_username   your_password    localhost_or_IPaddress   your_database_name
    """

    if os.name == "nt":  # for windows development computer
        config_file_path = ""
    else:  # for linux server
        config_file_path = ""
    db_config = pd.read_csv(config_file_path, sep="\t", header=0)
    config = db_config.loc[db_config.loc[:, "user"] == user, :].transpose().iloc[:, 0]
    config["database"] = database if database is not None else config["database"]
    config["host"] = host if host is not None else config["host"]

    return sql.create_engine(
        "mysql+mysqlconnector://%s:%s@%s/%s"
        % (config["user"], config["password"], config["host"], config["database"]),
        echo=echo,
    )


def verify_sql(query, params=None, method="pandas", debug=False):
    """
    Verify suitability of given SQL query with sqlite syntax. Some common syntax differences in syntax are translated in
    evaluation.utils.mysql_to_sqlite. If the query still fails to run an error is thrown. In this case, execution of the
    SQL query in SQLite database won't be possible, which should be avoided when intended to upload the code with a
    publication.
    :param query: str
        query in mysql syntax
    :param params: list of Any (any supported types) or None
        list of the parameters marked in query with '%s'
    :param method: one of ['pandas', 'sqlalchemy']
        choose with which module to run the query: sqlalchemy.connection.execute() or pandas.read_sql()
    :param debug: bool, optional, Default False
        print additional debug info
    :return: str
        query in mysql syntax
    """
    # Check compatibility with sqlite by using the empty sqlite database
    sql_query_sqlite = db_config_binder.verify_sql(query, debug=debug)
    try:
        with db_config_binder.connect(
            path_to_sqlite=publication_export.DIR_EMPTY_SQLITE
        ).begin() as con_sqlite:
            savepoint = con_sqlite.begin_nested()
            db.query_sql_execute_method(
                sql_query_sqlite, params=params, con=con_sqlite, method=method
            )
            savepoint.rollback()

    except Exception as error:
        print(
            "\x1b[31m"
            + "Translating query to SQlite fails (only problematic when exporting as publication). "
            "Please report to admin." + "\x1b[0m"
        )
        print(sql_query_sqlite, "\n", error)
    return query


def user_is_owner(index_col, index_value):
    """
    Check whether user is owner of a database entry specified index column name and value. Used to verify whether
    data processing is allowed.
    :param index_col: str
        name of the index column
    :param index_value: int
        value of the index
    :return: bool
    """
    name_table = {"id_exp_sfc": "exp_sfc", "id_exp_icpms": "exp_icpms"}[index_col]
    con = connect()
    is_owner = (
        con.execute(
            """ SELECT name_user 
                                FROM """
            + name_table
            + """ 
                                WHERE """
            + index_col
            + """ = %s""",
            [index_value],
        ).fetchall()[0][0]
        == current_user()
    )
    # print('is owner? ', is_owner)
    con.dispose()
    return is_owner


def current_user():
    """
    get the current user name
    :return: str, current user name
    """

    # return 'HTE_team'
    if os.getcwd()[:31] != "/home/hte_admin/sciebo/jupyter/":
        raise ConnectionRefusedError(
            "Wrong current working directory. Please inform Admin."
        )
    username = os.getcwd().replace("/home/hte_admin/sciebo/jupyter/", "").split("/")[0]
    if username == "shared":
        raise ConnectionRefusedError(
            "Do not run this script in shared but in your personal folder."
        )
    if "JUPYTERHUB_USER" in [name for name, value in os.environ.items()]:
        if username != os.environ["JUPYTERHUB_USER"]:
            raise ConnectionRefusedError("Do not change your username.")
    return username


def call_procedure(engine, name, params=None):
    """
    A function to run stored procedure, this will work for mysql-connector-python but may vary with other DBAPIs!
    :param engine: sqlalchemy.engine
        database connection
    :param name: str
        name of the stored procedure
    :param params: list of Any (any supported types)
        list of the parameters marked in query with '%s'
    :return: list of all result sets as pd.DataFrame
    """

    # If this get stuck make sure, tables are unlocked and you have the privilege to execute the stored procedure
    if params is None:
        params = []
    if engine is None:
        raise Exception(
            "Call_procedure must be called with an engine from sqlalchemy and cannot run with out"
        )

    try:
        connection = engine.raw_connection()
        cursor = connection.cursor()
        cursor.callproc(name, params)
        results = []
        for (
            result
        ) in cursor.stored_results():  # multiple resultssets should be possible
            results = results + [
                pd.DataFrame(
                    result.fetchall(), columns=[i[0] for i in result.description]
                )
            ]
        return results

    except Error as e:
        sys.exit(e)
    finally:
        cursor.close()
        connection.commit()
        connection.close()
        #


def sql_update(df_update, table_name, engine=None, con=None, add_cond=None):
    """
    Update sqlite database by values given in DataFrame df_update. If error occurs, transaction is rolled back.
    :param df_update: pd.DataFrame
        DataFrame with rows and columns which should be updated in the database.
        Not required to give all columns of the database table just the one meant to be updated.
    :param table_name: str
        Name of the table in sqlite database
    :param engine: sql.engine, optional
        Sqlalchemy engine to perform the update
    :param con: sql.connection, optional
        Sqlalchemy connection to perform the update, instead of engine
    :param add_cond: str
        additional condition to subselect rows in the table meant to be updated
    :return: None
    """
    con_init = con
    if con is None:  # cursor is None and
        if engine is None:
            engine = connect("hte_write")
        connection = engine.raw_connection()
        con = connection.cursor()

    # name_user would need to be checked to ensure user_safe update
    # index_col = [df_update.index.name] if df_update.index.name is not None else df_update.index.names
    # print(db.current_user(), index_col)

    # tablename: [updatable colums]
    db_constraints = db.db_constraints_update()
    if (
        table_name not in db_constraints.keys()
    ):  # ['exp_icpms_sfc', 'exp_icpms_integration', 'exp_ec_integration', 'ana_integrations', 'exp_sfc']:
        raise Exception("Udating " + table_name + " not implemented yet")

    for index, row in df_update.iterrows():
        # print(len(row.index))
        sql_query = "UPDATE  hte_data.`" + table_name + "` SET "
        vals = []
        for iteration, (col, val) in enumerate(row.to_dict().items()):
            if db_constraints[table_name] is not None:
                if col not in db_constraints[table_name]:
                    raise ConnectionRefusedError(
                        "Update column " + col + " is not allowed."
                    )
            sql_query += (
                "`"
                + col
                + "` = %s"
                + (" " if iteration == len(row.index) - 1 else ", ")
            )
            vals += [val]
        if type(index) == tuple:
            sql_query += (
                " WHERE (("
                + ", ".join(df_update.index.names)
                + ") = ("
                + ("%s, " * len(index))[:-2]
                + "))"
            )
            vals += list(index)
        else:
            sql_query += " WHERE (" + df_update.index.name + " = %s)"
            vals += [index]
        sql_query += ";" if add_cond is None else "AND " + add_cond + ";"

        # print(sql, vals)
        print(
            " ".join(
                [query + str(vals) for query, vals in zip(sql_query.split("%s"), vals + [""])]
            )
        )
        con.execute(sql_query, vals)
    if con_init is None:  # cursor is None
        connection.commit()


def get_data_raw(name_table, col_names, col_values, add_cond):
    """
    Core part of the get_data defined in evaluation.utils.db in which the database query is built and executed.
    Here, query is built in sqlite syntax.
    :param name_table: name of the table from which data should be received
    :param col_names: name of the index columns
    :param col_values: values of the index columns
    :param add_cond: str, optional Default None
        additional condition to subselect only part of the data
    :return: data as pd.DataFrame
    """
    col_names_str = "(" + str(list(col_names))[1:-1].replace("'", "`") + ")"
    col_values_str = "(" + str(list(col_values))[1:-1] + ")"

    sql_query = (
        "SELECT * FROM "
        + name_table
        + " WHERE "
        + col_names_str  # str(tuple(self._obj.index.names)).replace('\'', '`')
        + " IN "
        + col_values_str
        + (" AND " + str(add_cond) if add_cond is not None else "")
        + ";"
    )
    print(sql_query)
    # data = pd.DataFrame(conn.execute(sql.text(sql_query)).fetchall())
    with connect().begin() as con:
        data = pd.read_sql(sql_query, con=con)  # similar performance
    return data


def get_primarykeys(name_table=None, table_schema="hte_data"):
    """
    Get primary keys of all tables (name_table is None) or of specific table (name_table = str) in MysQL database.
    :param name_table: str or None, optional, Default None
        get primary keys of all (None) or specific table
    :param table_schema: str, default='hte_data'
        name of the database schema of the table
    :return: primary_keys_grouped
    """
    # print('Get primary keys of database tables.')
    with connect().begin() as con:
        # PRIMARY KEYS
        primary_keys = pd.read_sql(
            """SELECT * 
               FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
               WHERE TABLE_SCHEMA = %s
                    AND CONSTRAINT_NAME = 'PRIMARY'
            """
            + (" AND TABLE_NAME = %s" if name_table is not None else ""),
            params=[table_schema] + ([name_table] if name_table is not None else []),
            con=con,
        )

        if name_table is not None:
            if name_table not in primary_keys.TABLE_NAME.tolist():
                warnings.warn("No primary key found for table " + str(name_table))
                return None
            return primary_keys.COLUMN_NAME.tolist()
        else:
            primary_keys_grouped = (
                primary_keys.loc[
                    :,
                    [
                        "CONSTRAINT_NAME",
                        "TABLE_NAME",
                        "COLUMN_NAME",
                    ],
                ]
                .groupby(
                    [
                        "CONSTRAINT_NAME",
                        "TABLE_NAME",
                    ]
                )
                .apply(
                    lambda group: group.apply(
                        lambda col: pd.Series({col.index[0]: list(col.tolist())})
                    )
                )
                .loc[
                    :,
                    [
                        "COLUMN_NAME",
                    ],
                ]
                .reset_index()
                .set_index("TABLE_NAME")
                .loc[:, "COLUMN_NAME"]
            )
            # display(primary_keys_grouped)
            return primary_keys_grouped


def get_foreignkey_links(
    table_schema="hte_data",
    referenced_table_schema="hte_data",
):
    """
    Get Foreign keys in MySQL database.
    :param table_schema: str, default='hte_data'
        name of the database schema of the table
    :param referenced_table_schema: str, default='hte_data'
        name of the database schema of the referenced table
    :return: foreign_key table as pd.DataFrame
    """
    # print('Get links between database tables.')
    with connect().begin() as con:
        # FOREIGN KEYS
        foreign_keys = pd.read_sql(
            """SELECT * 
                FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                WHERE TABLE_SCHEMA = '%s'
                    AND REFERENCED_TABLE_SCHEMA = '%s'
            """
            % (table_schema, referenced_table_schema),
            con=con,
        )
        foreign_keys_grouped = (
            foreign_keys.loc[
                :,
                [
                    "CONSTRAINT_NAME",
                    "TABLE_NAME",
                    "REFERENCED_TABLE_NAME",
                    "COLUMN_NAME",
                    "REFERENCED_COLUMN_NAME",
                ],
            ]
            .groupby(["CONSTRAINT_NAME", "TABLE_NAME", "REFERENCED_TABLE_NAME"])
            .apply(
                lambda group: group.apply(
                    lambda col: pd.Series({col.index[0]: list(col.tolist())})
                )
            )
            .loc[:, ["COLUMN_NAME", "REFERENCED_COLUMN_NAME"]]
        )
        foreign_keys_grouped = foreign_keys_grouped.reset_index()
        recursive_keys_grouped = foreign_keys_grouped.loc[
            foreign_keys_grouped.TABLE_NAME
            == foreign_keys_grouped.REFERENCED_TABLE_NAME
        ]
        # display(foreign_keys_grouped)
        # display(recursive_keys_grouped)
        return foreign_keys_grouped, recursive_keys_grouped


def get_views(table_schema="hte_data", debug=False):
    """
    Get a list of all views in MySQL database
    :param table_schema: table_schema: str, default='hte_data'
        name of the database schema of the table
    :param debug: bool
        print additional debug info
    :return: list of all views in MySQL database
    """
    # print('Get database views.')
    with connect().begin() as con:
        # VIEWS
        view_tables = pd.read_sql(
            """ SELECT TABLE_NAME, TABLE_TYPE
                                    FROM information_schema.tables
                                    WHERE TABLE_SCHEMA = %s
                                     AND TABLE_TYPE IN (%s)
                                    ;""",  # , 'VIEW'
            params=[table_schema, "VIEW"],
            con=con,
        ).TABLE_NAME
        view_tables_list = view_tables.tolist()
    print(view_tables_list) if debug else ''
    return view_tables_list


def get_create_view(name_view, debug=False):
    """
    get Create View statement from MySQL database
    :param name_view: name of the view
    :param debug: bool
        print additional debug info
    :return: create view statement
    """
    sql_query = "SHOW CREATE VIEW %s;" % name_view
    print(sql_query) if debug else ""
    with connect(user="hte_processor").begin() as con:
        return pd.read_sql(sql_query, con=con).loc[:, "Create View"].loc[0]
