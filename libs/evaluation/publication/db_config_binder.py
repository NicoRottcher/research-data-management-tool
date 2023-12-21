"""
Scripts for SQLite database connection as used in mybinder
Created in 2023
@author: Nico Röttcher
"""

import math
import os
import sqlite3
from pathlib import Path

import pandas as pd
import sqlalchemy as sql

from evaluation.utils import db
from evaluation.utils import mysql_to_sqlite

MYSQL = False
REL_DIR_SQLITE = Path("database/sqlite.db")
REL_DIR_REPORTS = Path("processing_reports/")


def DIR_REPORTS():
    """
    Derive directory from jupyterhub environment variable (available in mybinder) to store reports
    :return: directory to store reports
    """
    DIR_REPORTS_ = Path("")
    if "REPO_DIR" in os.environ.keys():
        JPY_HOME_DIR = Path(os.environ["REPO_DIR"])
        DIR_REPORTS_ = JPY_HOME_DIR / REL_DIR_REPORTS
    return DIR_REPORTS_


def DATABASE_DIR():
    """
    Derive directory of sqlite database file
    :return: directory of sqlite database file
    """
    DATABASE_DIR_ = Path("")
    if "REPO_DIR" in os.environ.keys():
        JPY_HOME_DIR = Path(os.environ["REPO_DIR"])
        DATABASE_DIR_ = JPY_HOME_DIR / REL_DIR_SQLITE
    return DATABASE_DIR_


class StdevFunc:
    """
    Class to extend sqlite module with an aggregation function to derive standard deviation
    """

    def __init__(self):
        self.M = 0.0
        self.S = 0.0
        self.k = 1

    def step(self, value):
        if value is None:
            return
        tM = self.M
        self.M += (value - tM) / self.k
        self.S += (value - tM) * (value - self.M)
        self.k += 1

    def finalize(self):
        if self.k < 3:
            return None
        return math.sqrt(self.S / (self.k - 2))


def connect(
        user="hte_read",
        path_to_sqlite=DATABASE_DIR(),
        echo=False,
        database=None,
        host=None
):
    """
    method to connect to sqlite database. Appends user-defined functions not available in sqlite.
    :param user: dummy, required for compatibility with mysql connect
    :param path_to_sqlite: str, optional, Default DATABASE_DIR()
        path to sqlite database file
    :param echo: dummy, required for compatibility with mysql connect
    :param database: dummy, required for compatibility with mysql connect
    :param host: dummy, required for compatibility with mysql connect
    :return: sqlalchemy engine
    """

    def sqlite_engine_creator():
        con_sqlite_raw = sqlite3.connect(path_to_sqlite)
        con_sqlite_raw.create_aggregate(
            "stdv", 1, StdevFunc
        )  # add customized stdev function to sqlite
        con_sqlite_raw.create_function(
            "pow", 2, math.pow
        )  # add customized power function
        return con_sqlite_raw

    return sql.create_engine("sqlite+pysqlite://", creator=sqlite_engine_creator)


def translate_mysql2sqlite(query, debug=False):
    """
    translates syntax from mysql to sqlite
    :param query: query in mysql syntax
    :param debug: whether to print debug information
    :return: query in sqlite syntax
    """
    query = mysql_to_sqlite.time_intervals(query, debug)
    query = mysql_to_sqlite.timestampdiff(query, debug)
    query = mysql_to_sqlite.functions(query)
    query = mysql_to_sqlite.query_params(query)
    query = mysql_to_sqlite.database_name(query, debug)
    query = mysql_to_sqlite.comments(query, debug)
    print("sqlite query: ", query) if debug else ""
    return query


def verify_sql(query, params=None, method="pandas", debug=False):
    """
    dummy for compatibility when executed with mysql database. Translates syntax from mysql to sqlite
    :param query: query in mysql syntax
    :param params: dummy, required for compatibility with mysql
    :param method: dummy, required for compatibility with mysql
    :param debug: whether to print debug information
    :return: query in sqlite syntax
    """
    return translate_mysql2sqlite(query, debug=debug)


def user_is_owner(index_col, index_value):
    """
    dummy, required for compatibility with mysql. Sqlite doesn't have the concept of user roles.
    For compatibility: user is always owner, all changes to database are allowed.
    :param index_col: dummy, required for compatibility with mysql
    :param index_value: dummy, required for compatibility with mysql
    :return: True
    """
    print(
        "\x1b[33m",
        "You changed data in you personal binder session, this will not be stored permanently, "
        "and be reverted upon reload.",
        "\x1b[0m",
    )
    return True


def current_user():
    """
    dummy, required for compatibility with mysql. Username is set to 'mybinder_user'.
    :return: name_user, str
    """
    name_user = "mybinder_user"
    print(
        "\x1b[33m",
        "Your username "
        + name_user
        + ". Changing data in your mybinder session is possible but changes will not be stored permanently.",
        "\x1b[0m",
    )
    return name_user


def call_procedure(engine, name, params=None):
    """
    dummy, required for compatibility with mysql.
    Procedures are not transferred from mysql to sqlite and thus cannot be run.
    :param engine: dummy, required for compatibility with mysql
    :param name: name of the procedure
    :param params: dummy, required for compatibility with mysql
    :return: True
    """
    # raise Exception('call_procedure not developed for sqlite. '+name+' could not be called')
    print("call_procedure not developed for sqlite. " + name + " could not be called")
    return True


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
            engine = connect()
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
        sql_query = "UPDATE  `" + table_name + "` SET "
        vals = []
        for iteration, (col, val) in enumerate(row.to_dict().items()):
            if db_constraints[table_name] is not None:
                if col not in db_constraints[table_name]:
                    raise ConnectionRefusedError(
                        "Update column " + col + " is not allowed."
                    )
            if (
                type(val) == pd.Timestamp
            ):  # sqlite cannot handle pd.timestamp type values
                val = str(val)
            sql_query += (
                "`" + col + "` = ?" + (" " if iteration == len(row.index) - 1 else ", ")
            )
            vals += [val]
        if type(index) == tuple:
            # multiindex
            sql_query += (
                " WHERE (("
                + ", ".join(df_update.index.names)
                + ") = ("
                + ("?, " * len(index))[:-2]
                + "))"
            )
            vals += list(index)
        else:
            sql_query += " WHERE (" + df_update.index.name + " = ?)"
            vals += [index]
        sql_query += ";" if add_cond is None else "AND " + add_cond + ";"

        # print(sql_query, vals)
        print(
            " ".join(
                [query + str(vals) for query, vals in zip(sql_query.split("%s"), vals + [""])]
            )
        )
        con.execute(sql_query, vals)
    if con_init is None:  # cursor is None
        connection.commit()


def get_data_raw(name_table, col_names, col_values, add_cond=None):
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
    if len(col_names) == 1:
        # print('Multiindex get_data_raw for sqlite not yet developed. This probably won\'t work...')

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
        col_values_params = []
    else:
        #  multindex

        col_values_params = list(sum(col_values, ()))
        sql_query = (
            "SELECT data.*"
            + "\n\t FROM "
            + name_table
            + " AS data"
            + "\n\t INNER JOIN ("
            + " UNION ALL ".join(
                ["SELECT " + ", ".join(["? AS " + name for name in col_names])]
                * int(len(col_values))
            )  # / len(index_name)
            + ") AS multiindex"
            + "\n\t ON "
            + " AND ".join(
                ["multiindex." + name + " = " + "data." + name for name in col_names]
            )
            + ";"
        )

    print(sql_query)
    with connect().begin() as con:
        data = pd.read_sql(sql_query, params=col_values_params, con=con)
    # display(data)
    return data


def get_primarykeys(name_table=None, table_schema="hte_data"):
    """
    Get primary keys of all tables (name_table is None) or of specific table (name_table = str) in the database.
    :param name_table: str or None, optional, Default None
        get primary keys of all (None) or specific table
    :param table_schema: dummy, required for compatibility with mysql
    :return: primary_keys_grouped
    """

    with connect().begin() as con:
        name_tables = pd.read_sql(
            'SELECT name FROM sqlite_schema WHERE type="table"', con=con
        ).name.tolist()

        if name_table is not None:
            if name_table in name_tables:
                name_tables = [name_table]
                # tables_column_info = pd.read_sql('PRAGMA table_info(%s)' %name_table, con=con_sqlite)
            else:
                raise Exception("Unknown table")

        primary_keys = {}
        for name_table_for in name_tables:
            tables_column_info = pd.read_sql(
                "PRAGMA table_info(%s)" % name_table_for, con=con
            )
            primary_keys[name_table_for] = (
                tables_column_info.loc[tables_column_info.pk > 0]
                .sort_values(by="pk")
                .name.tolist()
            )
            # print(name_table_for, primary_keys)

    if name_table is not None:
        # print(primary_keys[name_table])
        return primary_keys[name_table]
    else:
        return_Series = pd.Series(primary_keys)
        return_Series.name = "COLUMN_NAME"
        return_Series.index.name = "TABLE_NAME"
        # print(return_Series)
        return return_Series


def get_foreignkey_links(
    table_schema="hte_data",
    referenced_table_schema="hte_data",
):
    """
    Get Foreign keys in sqlite database.
    :param table_schema: dummy, required for compatibility with mysql
    :param referenced_table_schema: dummy, required for compatibility with mysql
    :return: None
    """
    raise Exception("get foreign keys not yet developed for sqlite")


def get_views(table_schema="hte_data",
              debug=False):
    """
    Get a list of all views in sqlite database
    :param table_schema: dummy, required for compatibility with mysql
    :param debug: dummy, required for compatibility with mysql
    :return: list of all views in database
    """
    # print('Get database views.')
    with connect().begin() as con:
        return pd.read_sql(
            'SELECT name FROM sqlite_schema WHERE type="view"', con=con
        ).name.tolist()


def get_create_view(name_view, debug=False):
    """
    get Create View statement from database
    :param name_view: name of the view
    :param debug: print extra info if True
    :return: create view statement
    """
    sql_query = (
        'SELECT * FROM sqlite_schema WHERE type="view" AND name = "%s";' % name_view
    )
    print(sql_query) if debug else ""
    with connect().begin() as con:
        return pd.read_sql(sql_query, con=con).sql.loc[0]
