"""
Scripts for database-related functions
Created in 2023
@author: Nico Röttcher
"""

import os.path

import sqlalchemy as sql
import pandas as pd
import sys
import numpy as np
from ipywidgets import *
import warnings
import datetime
from IPython.display import SVG

from evaluation.utils import db_config, tools
from evaluation.processing import tools_ec
from evaluation.visualization import plot

MYSQL = db_config.MYSQL


def connect(*args, **kwargs):
    """
    method to connect to database either Mysql or Sqlite as defined in evaluation.utils.db_config
    """
    return db_config.connect(*args, **kwargs)


def query_sql(query, params=None, con=None, method="pandas", debug=False, **kwargs):
    """
    Standard command to run a SQL query. If run with MySQL: The SQL query will be verified to be compatible
    with sqlite syntax (thereby, some common syntax differences are considered in evaluation.utils.mysql_to_sqlite.py)
    The compatibility is required to be able to run the code with sqlite in mybinder when publishing the code.
    Therefore, the direct use of sqlalchemy.connection.execute() or pandas.read_sql() is highly discouraged.
    :param query: str
        requested SQL query. If method='pandas' the table name is accepted to query the select complete table data.
    :param params: list of Any (any supported types)
        list of the parameters marked in query with '%s'
    :param con: sql.Connection or None, optional, default None
        database connection object, if None a new will be initialized
    :param method: one of ['pandas', 'sqlalchemy']
        choose with which module to run the query: sqlalchemy.connection.execute() or pandas.read_sql()
    :param debug: bool, optional, Default False
        print additional debug info
    :param kwargs:
        kwargs of sqlalchemy.connection.execute() or pandas.read_sql()
    :return: return of sqlalchemy.connection.execute() or pandas.read_sql()
    """
    query = db_config.verify_sql(query, params=params, method=method, debug=debug)

    if con is None:
        with connect().begin() as con:
            return query_sql(query, params=params, con=con, method=method, debug=debug, **kwargs)
    else:
        return query_sql_execute_method(query, params=params, con=con, method=method, debug=debug, **kwargs)


def query_sql_execute_method(
    query, params=None, con=None, method="pandas", debug=False, **kwargs
):
    """
    function called in evaluation.utils.db.query_sql() and evaluation.utils.db_config.verify_sql()
    Not intended for different use. Rather use evaluation.utils.db.query_sql()
    :param query: str
        requested SQL query. If method='pandas' the table name is accepted to query the select complete table data.
    :param params: list of Any (any supported types)
        list of the parameters marked in query with '%s'
    :param con: sql.Connection or None, optional, default None
        database connection object, if None a new will be initialized
    :param method: one of ['pandas', 'sqlalchemy']
        choose with which module to run the query: sqlalchemy.connection.execute() or pandas.read_sql()
    :param debug: bool, optional, Default False
        print additional debug info
    :param kwargs:
        kwargs of sqlalchemy.connection.execute() or pandas.read_sql()
    :return: return of sqlalchemy.connection.execute() or pandas.read_sql()
    """
    print(query, params, con) if debug else ""
    if method == "pandas":
        return pd.read_sql(query, params=params, con=con, **kwargs)
    elif method == "sqlalchemy":
        if params is None:
            return con.execute(query)
        else:
            return con.execute(query, params)
    else:
        raise NotImplementedError("Method not implemented")


def insert_into(conn, tb_name, df=None):
    """
    Run an 'INSERT INTO' query for data from df into database table with Auto Increment index column. Returns the
    auto increment index in the column inserted_primary_key
    :param conn: db connection
    :param tb_name: name of the table as string
    :param df: pd.DataFrame or None, optional, Default None
        values to be inserted as dataframe
        if None, current auto increment value is returned
    :return:
        if df is None, current auto increment value of the table is returned
        else: df is returned with the auto increment index added in the column inserted_primary_key
    """
    if df is None:
        stmt = sql.Table(tb_name, sql.MetaData(), autoload_with=conn).insert().values()
        return conn.execute(stmt).inserted_primary_key
    else:
        for index, row in df.iterrows():
            stmt = (
                sql.Table(tb_name, sql.MetaData(), autoload_with=conn)
                .insert()
                .values(**row.to_dict())
            )
            df.loc[index, "inserted_primary_key"] = conn.execute(
                stmt
            ).inserted_primary_key
        return df


def call_procedure(engine, name, params=None):
    """
    A function to run stored procedure, this will work for mysql-connector-python but may vary with other DBAPIs!
    :param engine: sqlalchemy engine
    :param name: name of the stored procedure
    :param params: parameter or the stored procedure as list
    :return: list of all result sets as pd.DataFrame
    """
    return db_config.call_procedure(engine, name, params=params)


def db_constraints_update():
    """
    restrictions for updates
    :return: dict
        keys: table name
        value: None (updates to the whole table allowed)
                list of str (names of column to which an update is allowed)
    """
    return {
        "exp_icpms_sfc": None,
        "gases": None,
        "exp_icpms_integration": None,
        "exp_ec_integration": None,
        "ana_integrations": None,
        "exp_sfc": ["t_end__timestamp"],
        "exp_icpms_sfc_batch": ["id_exp_ec_dataset", "name_analysis"],
    }


def sql_update(df_update, table_name, engine=None, con=None, add_cond=None):
    """
    Update database by values given in DataFrame df_update. If error occurs, transaction is rolled back.
    :param df_update: pd.DataFrame
        DataFrame with rows and columns which should be updated in the database.
        Reduce columns to columns which actually should be updated.
    :param table_name: str
        Name of the table in database
    :param engine: sql.engine, optional
        Sqlalchemy engine to perform the update
    :param con: sql.connection, optional
        Sqlalchemy connection to perform the update, instead of engine
    :param add_cond: str
        additional condition to subselect rows in the table meant to be updated
    :return: None
    """
    return db_config.sql_update(
        df_update, table_name, engine=engine, con=con, add_cond=add_cond
    )


def get_exp(
    by,
    name_table=None,
    con=None,
    index_col=None,
    groupby_col=None,
    join_col=None,
    debug=False,
    dropna_index=False,
    **kwargs_read_sql
):
    """
    Standard routine to get list of experiments either by setting by=SQLquery or by=DataFrame with experimental
    index column.
    From the SQL query the name_base_table is automatically derived, from this the index_col is automatically set.
    If executed within a publication folder the requested experiments are linked to the publication.
    :param by: str or pd.DataFrame
        str: SQLquery to request experiment from database
        pd.DataFrame: having a column of the index column  of the experiment.
    :param name_table: str or None, optional Default None,
        name of the table from which to request data, required  or th
        if by is SQLquery: required only if auto detection of the table name from SQLquery fails
        if by is pd.DataFrame: required
    :param con: sqlalchemy.connection
        database connection object
    :param index_col: str or list of str or None
        name of the index columns
        if None: will be automatically set as the primary key of the given table
    :param groupby_col: str or list of str or None, optional, Default None
        only relevant if by is pd.Dataframe
        if None: set as index_col
        else: columns by which the given DataFrame should be grouped to derive the experiments
        necessary to redirect request to evaluation.utils.db.get_data()
    :param join_col:  list or None, optional, Default None
        common columns of given experimental and requested data table, if None index column(s) of caller is/are taken
        required for experiment overlaying
    :param debug: bool, Default False
        print additional debug info
    :param dropna_index:
        whether to drop NaN indices
    :param kwargs_read_sql:
        keyword arguments of pandas.read_sql
    :return: experimental DataFrame
    """
    if type(by) == str and name_table is None:
        name_table = derive_name_table(by, debug)
    name_base_table = derive_name_base_table(name_table, debug)
    if index_col is None:
        index_col = (
            get_primarykeys(name_base_table) if name_base_table is not None else []
        )

    if type(by) == str:  # by is a sql statement
        sql_exp = by
        if con is None:
            con = connect()
        df_exp = query_sql(
            sql_exp,
            con=con,
            index_col=index_col if len(index_col) > 0 else None,
            method="pandas",
            **kwargs_read_sql
        )
    elif (
        type(by) == pd.core.frame.DataFrame
    ):  # by is data DataFrame from which the experiments should be derived
        if groupby_col is None:
            groupby_col = index_col

        # short way via restructuring data table and hand it over to get_data
        df_exp = get_data(
            by.reset_index().groupby(groupby_col, dropna=dropna_index).min(),
            name_table,
            auto_add_id=False,
            join_cols=join_col,
            index_cols=index_col,
            **kwargs_read_sql
        )
    else:
        raise Exception(
            '"by" must be either SQL statement or a DataFrame from which to derive data from'
        )

    if db_config.MYSQL:
        from evaluation.publication import publication_export

        publication_export.add_publication_exp(df_exp, name_base_table)

    return df_exp


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
    return db_config.get_data_raw(name_table, col_names, col_values, add_cond)


def get_data(
    df_exp,
    name_table,
    join_cols=None,
    join_overlay_cols=None,
    index_cols=None,
    auto_add_id=True,
    add_cond=None,
    extend_time_window=0,
    t_start_shift__s=0,
    t_end_shift__s=0,
    add_data_without_corresponding_ec=True,
):
    """
    Convenient way to get data tables from database, without formulating sql queries.
    Matches id_exp_sfc to data_icpms if name_table == data_icpms_sfc_analysis
    :param df_exp: pandas.DataFrame
        DataFrame of experimental set
    :param name_table: str, name of the table to get the data from
    :param join_cols: optional, list,
        common columns of given experimental and requested data table, if None index column(s) of df_exp is/are taken
    :param join_overlay_cols: optional, list,
        columns additional to join_cols used to join df_exp on the data table in case in index_col columns are given
        which are not supplied by database (required for overlay example)
    :param index_cols: optional, list,
        column(s) of requested columns which should be the index in the returned dataframe,
        if None the index of the df_exp plus the data id column is taken (if auto_add_id == True)
    :param auto_add_id: bool default True,
        if True searches for another index column in the requested data dataframe and add this to index column
    :param add_cond: str,
        additional condition for requesting the data dataframe.
        For example, use this to select only a specific cycle in a CV experiment
    :param extend_time_window: depracated
    :param t_start_shift__s: float
        substitutes expand_time_window will match n seconds before or after the start timestamp
        of the icpms experiment to th ec experiment
    :param t_end_shift__s: float
        substitutes expand_time_window will match icpms n seconds before or after the end timestamp
        of the icpms experiment to th ec experiment
    :param add_data_without_corresponding_ec: optional, default True,
            only applies for data_table_name == 'data_icpms_sfc_analysis'
            and when the df_exp is match_exp_sfc_exp_icpms,
            True will select also data which has no corresponding ec experiment
            False ignores that data, lower performance
    :return: experimental data DataFrame
    """
    if join_overlay_cols is None:
        join_overlay_cols = []
    print('Read data from "' + name_table + '" ...')
    t_start = datetime.datetime.now()

    if (
        name_table in ["exp_ec_expanded", "data_icpms_sfc_analysis"]
        and df_exp.reset_index()
        .columns.isin(
            ["id_exp_sfc", "id_exp_icpms", "t_start__timestamp", "t_end__timestamp"]
        )
        .sum()
        < 4
        and df_exp.reset_index().columns.str.contains("id_data").any()
    ):
        text = "This version of data grabbing will be depracated soon. " \
               "Please consider adjusting your data grabbing method. " \
               "Refer to shared/02_templates/03_Plotting/ICPMS_plot_templates.ipynb !"
        print("\x1b[31m", text, "\x1b[0m")
        warnings.warn(text)
        name_table += "_old"

    if name_table in ["data_icpms_sfc_analysis_no_ISTD_fitting"]:
        print(
            "\x1b[31m",
            "You requested ICPMS data with point-by-point count ratio, which is not recommended. "
            "Please use the ISTD fitting tool before using the data.",
            "\x1b[0m",
        )
    if extend_time_window > 0:
        warnings.warn(
            "extend_time_window parameter is depracated and will be ignored. "
            "Use t_start_shift__s and t_end_shift__s instead"
        )

    # Derive the columns from which the respective data should be requested
    # if using_cols not specified use index cols of the dataframe
    # else use the specified once
    col_names = df_exp.index.names if join_cols is None else join_cols
    col_values = (
        df_exp.index.to_list()
        if join_cols is None
        else df_exp.reset_index().groupby(join_cols).min().index.to_list()
    )

    if len(col_values) == 0:
        print(
            "\x1b[31m",
            "You requested data for an empty experimental dataset! I return an empty dataframe",
            "\x1b[0m",
        )
        return pd.DataFrame({}, index=col_names + ["id_data"])
        # sys.exit('No rows found to get data from')

    data = get_data_raw(
        name_table=name_table,
        col_names=col_names,
        col_values=col_values,
        add_cond=add_cond,
    )

    if len(data.index) == 0:
        print(
            "\x1b[31m",
            "There is no data found for the requested experiments. I return an empty dataframe",
            "\x1b[0m",
        )
        return pd.DataFrame({}, index=col_names + ["id_data"])
        # sys.exit('No data found in database, for the requested query.')

    # transform VARCHAR(45) timestamp columns to datetime64[ns]
    # (necessary as LabView is unable to insert into Datetime columns)
    for timestamp_col in [
        col
        for col in data.columns
        if "timestamp" in col.lower() and data[col].dtypes == "O"
    ]:
        data.loc[:, timestamp_col] = data.loc[:, timestamp_col].astype("datetime64[ns]")

    # special timestamp matching for data_icpms_sfc_analysis and when df_exp is match_exp_sfc_exp_icpms
    if df_exp.reset_index().columns.isin(
        ["id_exp_sfc", "id_exp_icpms"]
    ).sum() == 2 and name_table in [
        "data_icpms_sfc_analysis",
        "data_icpms_sfc_analysis_no_ISTD_fitting",
    ]:
        t_3 = datetime.datetime.now()
        data = data.set_index(["id_exp_icpms", "id_data_icpms"]).sort_index()
        start_shift = pd.Timedelta(seconds=t_start_shift__s)
        end_shift = pd.Timedelta(seconds=t_end_shift__s)
        for index, row in df_exp.reset_index().iterrows():
            # old (=slower) versions for time matching
            # v1 - not correct exp_icpms and exp_ec matching
            # data_icpms.loc[(row.id_exp_icpms,
            #                slice((data_icpms.t_delaycorrected__timestamp_sfc_pc
            #                - (pd.to_datetime(row.t_start__timestamp)-pd.Timedelta(seconds=0))).abs().idxmin()[1],
            #                    (data_icpms.t_delaycorrected__timestamp_sfc_pc
            #                    - (pd.to_datetime(row.t_end__timestamp)+pd.Timedelta(seconds=0))).abs().idxmin()[1]
            #                 )), 'id_exp_sfc'] = row.id_exp_sfc

            # v2  - not correct exp_icpms and exp_ec matching, problems when two icpms measurements simultaneously
            # data_icpms2.loc[(data_icpms2.t_delaycorrected__timestamp_sfc_pc
            #                   - (pd.to_datetime(row.t_start__timestamp)-pd.Timedelta(seconds=0))).abs().idxmin():\
            #                    (data_icpms2.t_delaycorrected__timestamp_sfc_pc
            #                    - (pd.to_datetime(row.t_end__timestamp)+pd.Timedelta(seconds=0))).abs().idxmin()
            #                 , 'id_exp_sfc'] = row.id_exp_sfc

            # v3 select all icpms experiments belonging to the looped exp_ec from these compare timestamps
            # - faster and correct matching
            # data_icpms.loc[(row.id_exp_icpms, (data_icpms.loc[row.id_exp_icpms].t_delaycorrected__timestamp_sfc_pc
            #               - (pd.to_datetime(row.t_start__timestamp)-pd.Timedelta(seconds=0))).abs().idxmin()):\
            #       (row.id_exp_icpms, (data_icpms.loc[row.id_exp_icpms].t_delaycorrected__timestamp_sfc_pc
            #           - (pd.to_datetime(row.t_end__timestamp)+pd.Timedelta(seconds=0))).abs().idxmin())
            #       , 'id_exp_sfc'] = row.id_exp_sfc

            # v3.2 with grab lines with matching id_exp_icpms only once
            # and calculate timedelta for start and end_shift before for loop - even a bit faster
            a = data.loc[row.id_exp_icpms]
            data.loc[
                (
                    row.id_exp_icpms,
                    (
                        a.t_delaycorrected__timestamp_sfc_pc
                        - (pd.to_datetime(row.t_start__timestamp) + start_shift)
                    )
                    .abs()
                    .idxmin(),
                ): (
                    row.id_exp_icpms,
                    (
                        a.t_delaycorrected__timestamp_sfc_pc
                        - (pd.to_datetime(row.t_end__timestamp) + end_shift)
                    )
                    .abs()
                    .idxmin(),
                ),
                "id_exp_sfc",
            ] = row.id_exp_sfc

            # v3.3 placing correction of start and end time before for loop --> slower
            # df_match.loc[:,'t_start__timestamp'] = pd.to_datetime(df_match.t_start__timestamp)
            #                                       - pd.Timedelta(seconds=500)
            # df_match.loc[:,'t_end__timestamp'] = pd.to_datetime(df_match.t_start__timestamp)
            #                                       + pd.Timedelta(seconds=500)

            # v4.1 with grouping index, reduce redudndat time columns appear with multiple measured analyte elements,
            # but slower
            # data_icpms.loc[(row.id_exp_icpms, (data_icpms.loc[row.id_exp_icpms].groupby(level=0)
            # .t_delaycorrected__timestamp_sfc_pc.first() - (pd.to_datetime(row.t_start__timestamp)
            # -pd.Timedelta(seconds=0))).abs().idxmin()):\
            #               (row.id_exp_icpms, (data_icpms.loc[row.id_exp_icpms].groupby(level=0)
            #               .t_delaycorrected__timestamp_sfc_pc.first() - (pd.to_datetime(row.t_end__timestamp)
            #               +pd.Timedelta(seconds=0))).abs().idxmin())
            #               , 'id_exp_sfc'] = row.id_exp_sfc

            # v4.2 similar but with .index.duplicated instead
            # a=data_icpms.loc[row.id_exp_icpms]
            # data_icpms.loc[(row.id_exp_icpms,
            #               (a.loc[~a.index.duplicated(keep='first')].t_delaycorrected__timestamp_sfc_pc
            #               - (pd.to_datetime(row.t_start__timestamp)-pd.Timedelta(seconds=0))).abs().idxmin()):\
            #               (row.id_exp_icpms,
            #               (a.loc[~a.index.duplicated(keep='first')].t_delaycorrected__timestamp_sfc_pc
            #               - (pd.to_datetime(row.t_end__timestamp)+pd.Timedelta(seconds=0))).abs().idxmin())
            #               , 'id_exp_sfc'] = row.id_exp_sfc

        # remove unmmatched data if requested by add_data_without_corresponding_ec
        if not add_data_without_corresponding_ec:
            data = data.loc[~data.id_exp_sfc.isna(), :]

        # add A_geo_cols
        A_geo_cols = df_exp.columns[df_exp.columns.isin(plot.geo_columns.A_geo)]
        # if join columns not overlapping --> check that all dataframes not series
        # data=data.reset_index().set_index(index_cols).sort_index() # index will be set later

        data_joined = data.join(
            df_exp.set_index("id_exp_sfc").sort_index().loc[:, A_geo_cols],
            on="id_exp_sfc",
        )  # .loc[:, A_geo_cols]
        # (data_joined.loc[:, A_geo_cols] / 100).div(data_joined.loc[:, ['dm_dt__ng_s', ]].values)#loc[:, A_geo_cols]

        for A_geo_col in A_geo_cols:
            data.loc[
                :, plot.get_geo_column(A_geo_col, "A_geo", "dm_dt_S")
            ] = data_joined.dm_dt__ng_s / (
                data_joined.loc[:, A_geo_col] / 100
            )  # loc[:, A_geo_cols]

        # might improve performance, but jupyter crashes when executing
        # data = data.join((data.join(match_ec_icpms.set_index('id_exp_sfc').sort_index().loc[:, A_geo_cols]
        # .rename(columns=plot.geo_columns.set_index('A_geo').to_dict()['dm_dt_S']), on='id_exp_sfc')
        # .loc[:, plot.get_geo_column(A_geo_cols, 'A_geo', 'dm_dt_S')]/ 100).rdiv(data.loc[:, ['dm_dt__ng_s', ]]
        # .values))

        data = data.reset_index()

        t_4 = datetime.datetime.now()
        print("Timestamp matching in ", t_4 - t_3)

    # for data tables an additional primary key column is added to index
    # for exp tables (when using get_exp()) this is not the case --> get_data is called with auto_add_id = False
    if index_cols is None:
        add_id_col = []
        if auto_add_id:
            id_cols = [
                colname
                for colname in data.columns
                if "id_" in colname and colname not in list(df_exp.index.names)
            ]
            if len(id_cols) > 0:
                add_id_col = [id_cols[0]]
        index_cols = list(df_exp.index.names) + add_id_col
    else:
        # eventually add requested index cols from df_Exp
        if any(
            [index_col not in data.reset_index().columns for index_col in index_cols]
        ):  # Any requested index cols not in data?
            index_col_from_self_obj = []
            for index_col in index_cols:
                if index_col in data.reset_index().columns:
                    continue
                elif index_col in df_exp.reset_index().columns:  # get it from self._obj
                    index_col_from_self_obj = index_col_from_self_obj + [index_col]
                else:
                    warnings.warn(
                        "Index column: "
                        + index_col
                        + " not in requested dataframe nor in given dataframe"
                    )
            data = data.join(
                df_exp.reset_index()
                .set_index(join_cols + join_overlay_cols)
                .loc[:, index_col_from_self_obj],
                on=join_cols + join_overlay_cols,
            )

    data_indexed = data.set_index(index_cols).sort_index()
    t_end = datetime.datetime.now()
    print("Done in ", t_end - t_start)
    return data_indexed


def match_exp_sfc_exp_icpms(
    df_exp, overlay_cols=None, add_cond=None, A_geo_cols=None, add_cols=None
):
    """
    Get a DataFrame which matches sfc and icpms experiments. Matching on experiment level is required to
    optimize the matching on datapoint level later (match an sfc experiment to each icpms datapoint), is performed in+
    evaluation.utils.db.get_data()
    :param df_exp: pd.DataFrame
        either exp_icpms or exp_ec, depending on whether sfc-icpms experiments are selected by icpms or ec experiments
    :param overlay_cols: str or list of str or None
        name of index columns used to overlay multiple experiments
    :param add_cond: str
        additional condition to subselect specific experiments
    :param A_geo_cols:
        geometric columns (information on electrode size) which should be handed over to icpms experiments
        (to calculate geometric corrected icpms mass transfer rates)
    :param add_cols:
        additonal columns which shoul dbe handed over from icpms or ec to the other
    :return: pd.DataFrame matching sfc and icpms experiment
    """
    if overlay_cols is None:
        overlay_cols = []
    A_geo_cols = plot.get_geo_column(
        A_geo_cols, "A_geo", "A_geo"
    )  # check that geoi col exist
    index_names = df_exp.reset_index().columns
    index_names = index_names[index_names.isin(["id_exp_sfc", "id_exp_icpms"])]
    if len(index_names) > 1:  # len(index_names) >1:
        print(index_names)
        warnings.warn(
            "id_exp_sfc and id_exp_icpms found in df_exp. Did you already match? Just returned df_exp dataframe"
        )
        return df_exp
    elif len(index_names) == 0:
        sys.exit(
            "id_exp_sfc and id_exp_icpms not found in columns of dfexp. "
            "Please use propper experiment dataframe as df_exp"
        )
    # print(index_names)
    index_names = index_names[0]
    index_values = df_exp.reset_index().loc[:, str(index_names)].unique()  # .to_list()

    # engine = db.connect('hte_write')
    # db.call_procedure(engine, 'update_exp_sfc_t_end__timestamp')
    tools_ec.update_exp_sfc_t_end__timestamp()

    sql_query = (
        """SELECT id_exp_sfc, t_start__timestamp,t_end__timestamp, id_exp_icpms"""
        + ((", " + ", ".join(A_geo_cols)) if A_geo_cols is not None else "")
        + ((", " + ", ".join(add_cols)) if add_cols is not None else "")
        + """  FROM match_exp_sfc_exp_icpms m   
           WHERE ("""
        + str(index_names).replace("'", "`")
        + """)   IN ("""
        + str(list(index_values))[1:-1]
        + ")"
        + (" AND " + str(add_cond) if add_cond is not None else "")
        + ";"
    )
    print(sql_query)
    with connect().begin() as con:
        df = pd.read_sql(
            sql_query,
            con=con,
        )

    if len(overlay_cols) > 0:
        df = df.join(
            df_exp.reset_index().set_index(index_names).loc[:, overlay_cols],
            on=index_names,
        )
    return df


def get_exp_ec_dataset(exp_ec, con=None):
    """
    Shorthand function to get datasets from a list of ec experiments
    :param exp_ec: pd.DataFrame
        list of ec experiments
    :param con: sqlalchemy.connection or None
        database connection
        if None a new will be initialized
    :return: exp_ec_dataset_definer
    """
    if con is None:
        con = connect()
    ids_exp_sfc = exp_ec.reset_index().id_exp_sfc.tolist()
    ids_exp_sfc_str = ", ".join(["%s"] * len(ids_exp_sfc))

    exp_ec_datasets_definer = query_sql(
        """SELECT *
           FROM exp_ec_datasets_definer
           WHERE  id_exp_ec_dataset IN (SELECT id_exp_ec_dataset FROM exp_ec_datasets_definer
                                        GROUP BY id_exp_ec_dataset
                                        HAVING COUNT(*)= %s)
                                        # Exclude datasets with more or less id_exp_sfc than selected                
               AND  id_exp_ec_dataset NOT IN (SELECT id_exp_ec_dataset FROM exp_ec_datasets_definer
                                              WHERE id_exp_sfc NOT IN (""" + ids_exp_sfc_str + """))
                                        # Exclude datasets with other id_exp_sfc than selected
        ; """,
        params=[len(ids_exp_sfc)] + ids_exp_sfc,
        method="pandas",
        con=con,
    )
    return exp_ec_datasets_definer


def get_ana_icpms_sfc_fitting(exp_ec, exp_icpms, id_fit=0, show_result_svg=True):
    """
    Shorthand function to get sfc icpms peak fitting reuslts stored in ana_icpms_sfc_fitting
    from ec and icpms experiemnt list
    peak details can be retrieved by db.get_data(ana_icpms_sfc_fitting, name_table='ana_icpms_sfc_fitting_peaks')
    :param exp_ec: pd.DataFrame
        EC experiment list
    :param exp_icpms: pd.DataFrame
        EC experiment list
    :param id_fit: int, optional Default 0
        index of the fit, id_fit!=0 if multiple fits are performed on the same dataset
    :param show_result_svg: boll, optional, Default True
        whether to show the result plot of the fitting procedure
        as linked in ana_icpms_sfc_fitting.file_path_plot_sfc_icpms_peakfit
    :return: ana_icpms_sfc_fitting
    """
    exp_ec_dataset_definer = get_exp_ec_dataset(exp_ec)
    dataset_sfc_icpms = pd.DataFrame(
        index=tools.multiindex_from_product_indices(
            exp_ec_dataset_definer.set_index("id_exp_ec_dataset").index.unique(),
            exp_icpms.index,
        )
    )
    dataset_sfc_icpms.loc[:, "id_fit"] = id_fit
    ana_icpms_sfc_fitting = get_exp(
        dataset_sfc_icpms, name_table="ana_icpms_sfc_fitting"
    )
    if show_result_svg:
        for path in ana_icpms_sfc_fitting.file_path_plot_sfc_icpms_peakfit.tolist():
            if os.path.isfile(path):
                display(SVG(filename=path))

    return ana_icpms_sfc_fitting


def get_exp_sfc_icpms(
    sql_ec=None,
    sql_icpms=None,
    id_exp_sfc=None,
    id_exp_ec_dataset=None,
    id_exp_icpms=None,
    name_isotope_analyte=None,
    name_isotope_internalstandard=None,
    overlay_cols=None,
    multiple_exp_ec=True,
    multiple_exp_ec_datasets=True,
    multiple_exp_icpms=True,
    multiple_exp_icpms_isotopes=True,
    join_exp_ec_dataset_to_exp_ec=True,
    add_data_without_corresponding_ec=False,
):
    """
    Shorthand function to retrieve sfc icpms datasets by SQL query for ec experiments or icpms experiments
    or by specifiying one of the experiment indices.

    :param sql_ec: str or None, default None
        SQL query for ec experiments
    :param sql_icpms: str or None, default None
        SQL query for icpms experiments
    :param id_exp_sfc: int, or list of int or None
        indices of sfc experiments
    :param id_exp_ec_dataset: int, or list of int or None
        indices of ec experiment datasets
    :param id_exp_icpms: int, or list of int or None
        indices of icpms experiments
    :param name_isotope_analyte: str, or list of str or None
        indices of icpms analyte isotopes, not yet implemented
    :param name_isotope_internalstandard: str, or list of str or None
        indices of icpms internalstandard isotopes, not yet implemented
    :param overlay_cols: str, or list of str or None
        SFC experiment columns on which the experiments should be overlayed when time-synced
    :param multiple_exp_ec: bool, Default True
        restrict selection to maximum one ec experiment
    :param multiple_exp_ec_datasets: bool, Default True
        restrict selection to maximum one ec experiment dataset
    :param multiple_exp_icpms: bool, Default True
        restrict selection to maximum one icpms experiment
    :param multiple_exp_icpms_isotopes: bool, Default True
        restrict selection to maximum one icpms isotope pair
    :param join_exp_ec_dataset_to_exp_ec: bool, Default True
        whether to join id_exp_ec_dataset into exp_ec
    :param add_data_without_corresponding_ec: bool, Default False
        whether to add icpms data during which no ec experiment was performed
    :return: exp_ec, data_ec, exp_icpms, data_icpms
        each as pd.DataFrame
    """
    if overlay_cols is None:
        overlay_cols = []

    id_exp_sfc = tools.check_type(
        "id_exp_sfc",
        id_exp_sfc,
        allowed_types=[int, list, np.array],
        str_int_to_list=True,
        allowed_None=True,
    )
    id_exp_ec_dataset = tools.check_type(
        "id_exp_ec_dataset",
        id_exp_ec_dataset,
        allowed_types=[int, list, np.array],
        str_int_to_list=True,
        allowed_None=True,
    )
    id_exp_icpms = tools.check_type(
        "id_exp_icpms",
        id_exp_icpms,
        allowed_types=[int, list, np.array],
        str_int_to_list=True,
        allowed_None=True,
    )
    overlay_cols = tools.check_type(
        "overlay_cols",
        overlay_cols,
        allowed_types=[str, list, np.array],
        str_int_to_list=True,
        allowed_None=False,
    )

    if any([param is not None for param in [sql_ec, id_exp_ec_dataset, id_exp_sfc]]):
        # Init with None
        exp_ec_datasets_definer = None

        if sql_ec is not None:
            exp_ec = get_exp(sql_ec, index_col=["id_exp_sfc"])

        elif id_exp_ec_dataset is not None:
            exp_ec_datasets_definer = get_exp(
                pd.DataFrame(
                    id_exp_ec_dataset, columns=["id_exp_ec_dataset"]
                ).set_index("id_exp_ec_dataset"),
                name_table="exp_ec_datasets_definer",
                join_col=["id_exp_ec_dataset"],
                index_col=["id_exp_ec_dataset"],
            )
            exp_ec = get_exp(
                exp_ec_datasets_definer,
                name_table="exp_ec_expanded",
                join_col=["id_exp_sfc"],
                index_col=["id_exp_sfc"],
            )

        elif id_exp_sfc is not None:
            exp_ec = get_exp(
                pd.DataFrame(id_exp_sfc, columns=["id_exp_sfc"]).set_index(
                    "id_exp_sfc"
                ),
                name_table="exp_ec_expanded",
                join_col=["id_exp_sfc"],
                index_col=["id_exp_sfc"],
            )
        else:
            raise ValueError("Not enough parameters to get sfc icpms data!")

        if exp_ec_datasets_definer is None:
            exp_ec_datasets_definer = get_exp_ec_dataset(exp_ec)
        if join_exp_ec_dataset_to_exp_ec:
            exp_ec = pd.concat(
                [  # experiments with id_exp_ec_dataset already initiated
                    exp_ec_datasets_definer.reset_index()
                    .join(exp_ec, on="id_exp_sfc")
                    .set_index("id_exp_sfc"),
                    # experiments with id_exp_ec_dataset = NaN
                    exp_ec.loc[~exp_ec.index.isin(exp_ec_datasets_definer.id_exp_sfc)],
                ]
            )

        exp_ec = exp_ec.reset_index().set_index(overlay_cols + ["id_exp_sfc"])

        # Check multiple exp_ec and exp_ec_dataset
        if not multiple_exp_ec:
            if len(exp_ec.reset_index().id_exp_sfc.unique()) > 1:
                display(exp_ec)
                raise Exception("More than one ec experiment selected")
        if not multiple_exp_ec_datasets:
            if (
                len(exp_ec_datasets_definer.reset_index().id_exp_ec_dataset.unique())
                > 1
            ):
                display(exp_ec)
                raise Exception("More than one ec experiment dataset selected")

        # ec data
        data_ec = get_data(
            exp_ec,
            "data_ec_analysis",
            join_cols=["id_exp_sfc"],
            index_cols=overlay_cols + ["id_exp_sfc", "id_data_ec"],
        )

        # ICP-MS data
        match_ec_icpms = match_exp_sfc_exp_icpms(exp_ec, overlay_cols=overlay_cols)
        exp_icpms = get_exp(
            match_ec_icpms,
            "exp_icpms_sfc_expanded",
            groupby_col=overlay_cols + ["id_exp_icpms"],
            index_col=overlay_cols
            + ["id_exp_icpms", "name_isotope_analyte", "name_isotope_internalstandard"],
            join_col=["id_exp_icpms"],
        )

        if not multiple_exp_icpms:
            if len(exp_icpms.reset_index().id_exp_icpms.unique()) > 1:
                display(exp_icpms)
                raise Exception("More than one ec experiment dataset selected")
        if not multiple_exp_icpms_isotopes:
            if len(exp_icpms.reset_index().name_isotope_analyte.unique()) > 1:
                display(exp_icpms)
                raise Exception("More than one ec experiment dataset selected")
        if not multiple_exp_icpms_isotopes:
            if len(exp_icpms.reset_index().name_isotope_internalstandard.unique()) > 1:
                display(exp_icpms)
                raise Exception("More than one ec experiment dataset selected")

                # icpms data
        data_icpms = get_data(
            match_ec_icpms,
            "data_icpms_sfc_analysis",
            join_cols=["id_exp_icpms"],
            join_overlay_cols=["id_exp_sfc"],
            index_cols=overlay_cols
            + [
                "id_exp_icpms",
                "name_isotope_analyte",
                "name_isotope_internalstandard",
                "id_data_icpms",
            ],
            # t_start_shift__s=-100,
            # t_end_shift__s=200,
            add_data_without_corresponding_ec=add_data_without_corresponding_ec,
        )

    elif any(
        [
            param is not None
            for param in [
                sql_icpms,
                id_exp_icpms,
            ]
        ]
    ):
        raise Exception("Not developed yet!")
    else:
        raise Exception("Not enough parameters to get sfc icpms data!")

    # Time synchronization
    data_ec, data_icpms = plot.synchronize_timestamps(
        data_ec=data_ec,
        data_icpms=data_icpms,
        timestamp_col_ec="Timestamp",
        timestamp_col_icpms="t_delaycorrected__timestamp_sfc_pc",
        overlay_index_cols=overlay_cols,
    )

    if not (exp_ec.name_user == current_user()).all():
        print(
            "\x1b[33m",
            "This is data from ",
            ", ".join(exp_ec.name_user.tolist()),
            # '. Updates are restricted!',
            "\x1b[0m",
        )
    return exp_ec, data_ec, exp_icpms, data_icpms


def derive_name_table(sql_exp, debug=False):
    """
    auto-derive the name of the table from which data is requested
    :param sql_exp: str
        sql query
    :param debug: bool
        print additional debug info
    :return: name of the table
    """
    name_table = (
        sql_exp.split("FROM")[1]
        .split("WHERE")[0]
        .strip(" \n\t")
        .replace("hte_data.", "")
    )
    if debug:
        print("Derived name_table:", name_table)
    return name_table


def derive_name_base_table(name_table, debug=False):
    """
    derive the name of the base table from documentation_tables,
    this table name will be stored when experiments are linked to apublication in publication_exp
    :param name_table: str
        name of a table or view
    :param debug: bool
        print additional debug info
    :return: name of the base table
    """
    primary_keys = get_primarykeys()
    if name_table not in primary_keys.index:
        with connect().begin() as con:
            df_view_information = pd.read_sql(
                """SELECT name_table, name_base_table
                             FROM documentation_tables
                             WHERE table_type = 'VIEW'
                            """,
                con=con,
                index_col="name_table",
            )
        if name_table not in df_view_information.index:
            raise Exception(
                name_table
                + " is neither name of a table or view. "
                  "Correct your sql statement or specify name_table as function parameter."
            )
        elif df_view_information.loc[name_table, "name_base_table"] is None:
            warnings.warn(
                "Base table of view " + name_table + " is not defined. "
                "Please refer to admin to add to hte_data_documentation.view_information"
            )
        name_base_table = df_view_information.loc[name_table, "name_base_table"]

        if debug:
            print("Derived name_base_table:", name_base_table)
    else:
        name_base_table = name_table

    return name_base_table


def get_primarykeys(name_table=None, table_schema="hte_data"):
    """
    Get primary keys of all tables (name_table is None) or of specific table (name_table = str) in the database.
    :param name_table: str or None, optional, Default None
        get primary keys of all (None) or specific table
    :param table_schema: str, default='hte_data'
        name of the database schema of the table
    :return: primary_keys_grouped
    """
    return db_config.get_primarykeys(name_table=name_table, table_schema=table_schema)


def get_foreignkey_links(
    table_schema="hte_data",
    referenced_table_schema="hte_data",
):
    """
    Get Foreign keys in sqlite database.
    :param table_schema: str, default='hte_data'
        name of the database schema of the table
    :param referenced_table_schema: str, default='hte_data'
        name of the database schema of the referenced table
    :return: foreign_key table as pd.DataFrame
    """
    return db_config.get_foreignkey_links(
        table_schema=table_schema,
        referenced_table_schema=referenced_table_schema,
    )


def get_views(table_schema="hte_data", debug=False):
    """
    Get a list of all views in database
    :param table_schema: table_schema: str, default='hte_data'
        name of the database schema of the table
    :param debug: bool
        print additional debug info
    :return: list of all views in database
    """
    return db_config.get_views(table_schema=table_schema, debug=debug)


def get_create_view(name_view, debug=False):
    """
    get Create View statement from database
    :param name_view: name of the view
    :param debug: print extra info if True
    :return: create view statement
    """
    return db_config.get_create_view(name_view=name_view, debug=debug)


def get_views_sorted(table_schema="hte_data", debug=False):
    """
    Read and sort views in the database
    :param table_schema: table_schema: str, default='hte_data'
        name of the database schema of the table
    :param debug: bool
        print additional debug info
    :return: list of all views in database
    """
    view_tables_list = get_views(table_schema=table_schema, debug=debug)

    view_references = {}
    for name_view in view_tables_list:
        # print(view)
        create_view_statement = get_create_view(name_view=name_view, debug=False)

        view_references[name_view] = np.array(view_tables_list)[
            [
                referenced_view in create_view_statement
                and referenced_view != name_view
                for referenced_view in view_tables_list
            ]
        ]
    # view_references

    view_tables_sorted = [
        key for key, val in view_references.items() if len(val) == 0
    ]  # views without any references

    while not all([view in view_tables_sorted for view in view_tables_list]):
        if debug:
            print(
                "Still missing views: ",
                np.array(view_tables_list)[
                    [view not in view_tables_sorted for view in view_tables_list]
                ],
            )
        for key, val in view_references.items():
            if key in view_tables_sorted:
                continue

            if all([referenced_view in view_tables_sorted for referenced_view in val]):
                view_tables_sorted.append(key)

    view_tables_sorted.remove("documentation_columns")
    view_tables_sorted.remove("documentation_tables")
    # print('All views sorted')
    # print(view_tables_sorted)
    return view_tables_sorted


def current_user():
    """
    get the current user name
    :return: current user name
    """
    return db_config.current_user()


def user_is_owner(index_col, index_value):
    """
    Check whether user is owner of a database entry specified index column name and value. Used to verify whether
    data processing is allowed.
    :param index_col: str
    :param index_value: int
    :return: bool
    """
    return db_config.user_is_owner(index_col, index_value)
