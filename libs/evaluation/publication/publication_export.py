"""
Scripts for preparing export of data and files for publication
Created in 2023
@author: Nico Röttcher
"""

import os
import warnings
from pathlib import Path
import shutil  # copy files

import pandas as pd
import numpy as np
import sqlalchemy as sql  # Handling python - sql communication


import evaluation
from evaluation.utils import mysql_to_sqlite  # , db
import evaluation.utils.db as db
from evaluation.publication import db_config_binder
from evaluation.utils import user_input  # import user_input

REL_DIR_UPLOAD = Path("upload/")  # in publication folder
# REL_DIR_SQLITE = Path('database/sqlite.db')  # defined in db_config
REL_DIR_LIBS = Path("libs/")
REL_DIR_EVALUATION = Path("libs/evaluation")
DIR_EVALUATION_MODULE = Path(evaluation.__file__).parent
DIR_EMPTY_SQLITE_NO_VIEWS = DIR_EVALUATION_MODULE / Path("publication/database/sqlite_no_views.db")
DIR_EMPTY_SQLITE = DIR_EVALUATION_MODULE / Path("publication/database/sqlite.db")


class Publication:
    """
    class storing all information of the publication
    """

    def __init__(self, debug=False):
        """
        Initializes Publication object, checks whether any publication is already created within
        the current working directory
        :param debug: print extra info for all publication functions
        """
        self.debug = debug
        self.engine_mysql = self.connect_mysql()
        self.cwd = Path(os.getcwd())  # current working directory

        with self.engine_mysql.begin() as con_mysql:
            df_publications = pd.read_sql("publications", con=con_mysql)
        publication_paths = [
            Path(path) for path in df_publications.path_to_jupyter_folder.tolist()
        ]
        # print(publication_paths)

        # Match publication by folder
        # cwd is wd or any subfolder of a publication
        df_publications_requested = df_publications.loc[
            [
                publication_path == self.cwd or publication_path in self.cwd.parents
                for publication_path in publication_paths
            ]
        ]
        # print(df_publications_requested)

        if len(df_publications_requested.index) == 0:
            self.created = False
            # print('No publication initiated in this or parent folder. Create publication first.')
        elif len(df_publications_requested.index) == 1:
            self.created = True
            self.id_publication = df_publications_requested.iloc[0].id_publication
            self.title = df_publications_requested.iloc[0].title
            self.name_journal = df_publications_requested.iloc[0].name_journal
            self.name_user = df_publications_requested.iloc[0].name_user
            self.path_to_jupyter_folder = Path(
                df_publications_requested.iloc[0].path_to_jupyter_folder
            )
            self.path_to_publication_upload = (
                self.path_to_jupyter_folder / REL_DIR_UPLOAD
            )
            self.path_to_publication_sqlite = (
                self.path_to_publication_upload / db_config_binder.REL_DIR_SQLITE
            )
            self.engine_sqlite = self.connect_sqlite()

            # database structure
            (
                self.foreign_keys_grouped,
                self.recursive_keys_grouped,
            ) = db.get_foreignkey_links()
            self.primary_keys_grouped = db.get_primarykeys()
            self.view_tables_sorted = db.get_views_sorted()

            # dictionary of dataframes holding copy of all entries in database tables to copy to sqlite
            self.DATABASE_DF = {}

            # experiment table
            self.df_publication_exp = self.publication_exp()

            print(
                "Publication ", self.id_publication, " initiated"
            ) if self.debug else None
        else:
            raise Exception(
                "Incorrect database state. Multiple publications initiated for this and parent folders:"
                + ", ".join(df_publications_requested.id_publication.tolist())
            )

    def connect_mysql(
        self,
    ):
        """
        Connect to Mysql database
        :return: mysql sqlalchemy engine
        """
        return db.connect(user="hte_processor")

    def connect_sqlite(
        self,
    ):
        """
        Connect to Sqlite database
        :return: sqlite sqlalchemy engine
        """
        if not os.path.isfile(self.path_to_publication_sqlite):
            # print('Unable to find sqlite file.')
            return None
        return db_config_binder.connect(path_to_sqlite=self.path_to_publication_sqlite)

    def create(self, id_publication=None, title=None, name_journal=None):
        """
        Create a publication for the given folder. Optionally add information for the publication
        :param id_publication: str or None, optional, Default None
            identifier for the publication
        :param title: str or None, optional, Default None
            (working) title of the publication
        :param name_journal: str or None, optional, Default None
            journal for the publication
        :return: self
        """
        if self.created:
            print("Already created!")
            if self.id_publication != id_publication:
                warnings.warn(
                    "Updating id_publication not yet developed. "
                    "Still id_publication = " + str(self.id_publication)
                )
            if self.title != title:
                warnings.warn(
                    "Updating title not yet developed. "
                    "Still title = " + str(self.title)
                )
            if self.name_journal != name_journal:
                warnings.warn(
                    "Updating name_journal not yet developed. "
                    "Still name_journal = " + str(self.name_journal)
                )
        else:
            self.id_publication = (
                user_input.user_input(
                    text="Input your id_publication title:", dtype="str", optional=True
                )
                if title is None
                else id_publication
            )
            self.title = (
                user_input.user_input(
                    text="Input your publications title:", dtype="str", optional=True
                )
                if title is None
                else title
            )
            self.name_journal = (
                user_input.user_input(
                    text="Input the journal name for your publication:",
                    dtype="str",
                    optional=True,
                )
                if name_journal is None
                else name_journal
            )
            self.name_user = (
                db.current_user()
            )  # this have to be outsourced to another table publication_authors to allow for collaboration
            self.path_to_jupyter_folder = self.cwd

            with self.engine_mysql.begin() as con_mysql:
                con_mysql.execute(
                    """INSERT INTO `hte_data`.`publications` 
                                    (`id_publication`, `title`, `name_journal`, `path_to_jupyter_folder`, `name_user`) 
                                    VALUES (%s, %s, %s, %s, %s);""",
                    [
                        self.id_publication,
                        self.title,
                        self.name_journal,
                        str(self.path_to_jupyter_folder),
                        self.name_user,
                    ],
                )
                print("Inserted entry %s into database." % self.id_publication)
        return self

    def publication_exp(self):
        """
        Get DataFrame of all experiments linked to the publication
        :return: DataFrame of all experiments linked to the publication
        """
        with self.engine_mysql.begin() as con_mysql:
            df_publication_exp = pd.read_sql(
                "SELECT name_table, count_exp, name_index_col, value_index_col "
                "FROM publication_exps "
                "WHERE id_publication=%s;",
                params=[self.id_publication],
                con=con_mysql,
            )
        return df_publication_exp

    def remove_experiment_links(self):
        """
        Removes all experiment links, after user confirmation
        :return: None
        """
        if self.name_user != db.current_user():
            print(
                "Deleting is only allowed for owner of publication: %s" % self.name_user
            )
            return False

        with self.engine_mysql.begin() as con_mysql:
            df_exp = pd.read_sql(
                "SELECT * FROM publication_exps WHERE id_publication = %s",
                params=[self.id_publication],
                con=con_mysql,
            )

            print(
                "Remove %s experiments linked to %s"
                % (
                    len(
                        df_exp.loc[:, ["name_table", "count_exp"]]
                        .drop_duplicates()
                        .index
                    ),
                    self.id_publication,
                )
            )
            display(df_exp)

            if not user_input.user_input(
                text="Do you want to delete the links? "
                "(You will need to rerun all data grabbing routines to establish the experimental link again) \n",
                dtype="bool",
            ):
                print("Cancelled")
                return False

            con_mysql.execute(
                "DELETE FROM publication_exps WHERE id_publication = %s",
                [self.id_publication],
            )
            self.DATABASE_DF = {}
            print("\x1b[32m", "Successfully deleted experiment links!", "\x1b[0m")

    def export_to_upload(
        self,
        debug=False,
        tables_transfer_all_values=None,
        path_to_sqlite_empty_tables=None,
        link_children_table=None,
    ):
        """
        Initialize database export
        :param debug: print extra info if True
        :param tables_transfer_all_values: list of name of tables from which all data should be appended
            - but no links to these tables will be considered
        :param path_to_sqlite_empty_tables: str or None, optional, Default None
            for specific cases in which not the current database schema is used
            file path to the sqlite template file with empty database structure
            (on-the-fly creation not yet developed)
        :param link_children_table: list of str or None
            list of name of tables from which to link corresponding children tables
            (a children table references (foreign key) on to a parent table index)
        """
        # if exclude_views is None:
        #    exclude_views = ['data_icpms_sfc_analysis_old']
        if tables_transfer_all_values is None:
            tables_transfer_all_values = ["dummy_data_icpms_sfc_batch_analysis",
                                          "documentation_columns",
                                          "documentation_tables"]
        self.debug = debug

        if self.path_to_jupyter_folder.name == "upload":
            raise Exception("Do not run export_to_upload script in upload folder")

        # initialize upload folder
        self.create_upload_folder()
        # copy files to upload folder
        print(
            "\x1b[34m",
            "Copy all required files to upload folder ... (This may take a while)",
            "\x1b[0m",
        )
        self.copy_upload_files(path_to_sqlite_empty_tables)

        # transfer selected experiments for the publication to DATABASE_DF

        # check mysql connection
        try:
            self.engine_mysql.connect()
        except sql.exc.OperationalError as e:
            print("reconnect to mysql...")
            self.engine_mysql = self.connect_mysql()

        # reinitialize DATABASE_DF
        self.DATABASE_DF = {}
        # refresh df_publication_exp
        self.df_publication_exp = self.publication_exp()

        # transfer mysql --> self.DATABASE_DF
        for name_table in self.df_publication_exp.name_table.tolist():
            unstacked = (
                self.df_publication_exp.loc[
                    self.df_publication_exp.name_table == name_table
                ]
                .set_index(["name_table", "count_exp", "name_index_col"])
                .unstack()
            )
            unstacked.columns = unstacked.columns.get_level_values(
                level="name_index_col"
            )
            print("Transfer experiments from", name_table, " to DATABASE_DF")
            self._transfer_tables_mysql2df(
                table_name=name_table,
                index_name=unstacked.columns.tolist(),
                index_values=unstacked.values,
                link_children_table=link_children_table,
            )

        # add complete data of specified tables
        index_cols = {'documentation_tables': ['name_table'],
                      'documentation_columns': ['name_table', 'name_column'],
                      }
        for name_table in tables_transfer_all_values:
            self._transfer_tables_specified_mysql2df(
                name_table=name_table,
                index_col=index_cols[name_table] if name_table in index_cols.keys() else None
            )

        # add publication data
        for name_table in ['publications', 'publication_exps']:
            self._transfer_tables_specified_mysql2df(name_table=name_table,
                                                     add_cond='id_publication = %s',
                                                     add_cond_params=[self.id_publication])

        # Fill sqlite database
        self.engine_sqlite = self.connect_sqlite()
        print("\x1b[34m", "Transfer experiments from DATABASE_DF to sqlite", "\x1b[0m")
        self.transfer_tables_df2sqlite()
        # print("\x1b[34m", 'Transfer views from mysql to sqlite', "\x1b[0m")
        # self.transfer_views_mysql2sqlite(exclude_views)
        print("\x1b[32m", "Successfully exported publication for upload!", "\x1b[0m")

        # dispose database connections
        self.engine_mysql.dispose()  # doesn't have to be disposed
        self.engine_sqlite.dispose()

    def display_linked_experiments(self):
        """
        Displays ids of all experiments linked to the publication
        :return: None
        """
        df_publication_exp = self.publication_exp()
        for name_table in df_publication_exp.name_table.unique().tolist():
            unstacked = (
                df_publication_exp.loc[df_publication_exp.name_table == name_table]
                .set_index(["name_table", "count_exp", "name_index_col"])
                .unstack()
            )
            unstacked.columns = unstacked.columns.get_level_values(
                level="name_index_col"
            )
            print(name_table)
            print(unstacked.values)

    def create_upload_folder(self):
        """
        Creates (or deletes and creates) the upload folder for the publication
        :return: None
        """
        if os.path.isdir(self.path_to_publication_upload):
            if not user_input.user_input(
                text="Upload folder already exists. Delete and continue data export?\n",
                dtype="bool",
            ):
                print("\x1b[31m", "Cancelled, no export has been performed!", "\x1b[0m")
                raise Exception('Program was cancelled by user.')

            shutil.rmtree(self.path_to_publication_upload)
            print("Deleted old upload folder")
        os.mkdir(self.path_to_publication_upload)
        print("Created upload folder ", str(self.path_to_publication_upload))

    def copy_upload_files(self, path_to_sqlite_empty_tables):
        """
        Copies to the upload folder:
            - all modules in evaluation, and also
                renaming db_config to db_config_mysql
                and copy db_config_binder as new db_config
            - all files in evaluation/publication/repo_files
            - all files in evaluation/publication/database
            - all files in publication folder
        Creates upload/reports/
        :param path_to_sqlite_empty_tables:
        :return: None
        """
        # all modules in folder
        shutil.copytree(
            src=DIR_EVALUATION_MODULE,
            dst=self.path_to_publication_upload / REL_DIR_EVALUATION,
            dirs_exist_ok=True,
            ignore=shutil.ignore_patterns(
                ".git", "__pycache__", "db_config_binder.py", "db_config.py"
            ),
        )

        # __init__.py for scripts folder
        shutil.copy2(
            src=Path(evaluation.__file__),
            dst=self.path_to_publication_upload / REL_DIR_LIBS / "__init__.py",
        )

        # db_config_binder.py --> db_config.py
        shutil.copy(
            src=DIR_EVALUATION_MODULE / Path("publication/db_config_binder.py"),
            dst=self.path_to_publication_upload
            / REL_DIR_EVALUATION
            / Path("utils/db_config.py"),
        )

        # db_config.py --> db_config_mysql.py
        copy_and_replace(
            src=DIR_EVALUATION_MODULE / Path("utils/db_config.py"),
            dst=self.path_to_publication_upload / REL_DIR_EVALUATION / Path("utils/db_config_mysql.py"),
            function=remove_part_between,
            str_find_remove='# %%% remove',
            str_prepend_file='# If you like to use connection to MySQL database as default, '
                             'replace the db_config.py file with this one.\n'
        )

        # repo-files including environment.yml
        shutil.copytree(
            src=DIR_EVALUATION_MODULE / Path("publication/repo_files"),
            dst=self.path_to_publication_upload,
            dirs_exist_ok=True,
        )

        # database/sqlite.db
        shutil.copytree(
            src=DIR_EVALUATION_MODULE / Path("publication/database"),
            dst=self.path_to_publication_sqlite.parent,  # same: self.path_to_publication_upload / Path("database"),
            dirs_exist_ok=True,
            ignore=shutil.ignore_patterns("sqlite_no_veiws.db")
        )
        if not os.path.isfile(self.path_to_publication_sqlite):
            raise Exception('Copied database folder, but still could not find database file: %s'
                            % self.path_to_publication_sqlite)

        # all files in publication folder
        shutil.copytree(
            src=self.path_to_jupyter_folder,
            dst=self.path_to_publication_upload,
            dirs_exist_ok=True,
            ignore=shutil.ignore_patterns("upload"),
        )
        if not os.path.isdir(
            self.path_to_publication_upload / db_config_binder.REL_DIR_REPORTS
        ):
            # print("\x1b[33m", 'reports folder created', "\x1b[0m")
            os.mkdir(self.path_to_publication_upload / db_config_binder.REL_DIR_REPORTS)

    def _remove_existing_index(
        self,
        table_name,
        index_name,
        index_name_str,
        index_values,
        index_values_str,
        index_values_params,
    ):
        """
        Unused?
        """
        # global df_sqlite_tables
        index_values_existing = (
            self.DATABASE_DF[table_name].reset_index().loc[:, index_name].values
            if table_name in self.DATABASE_DF.keys()
            else []
        )
        index_values_new = [
            value for value in index_values if value not in index_values_existing
        ]  # removes existing values

        index_values_new_str, index_values_new_params = values2sqlstring(
            index_values_new
        )
        return index_values_new, index_values_new_str, index_values_new_params

    def _transfer_tables_mysql2df(
        self,
        table_name,
        index_name,
        index_values,
        caller_table_name="",
        recursive_level="",
        link_children_table=None,
    ):
        """
        Core function to transfer all linked data of linked experiments of a publication from the corresponding
         MySQL table (table_name) to Publication.DATABASE_DF
        From the given table (name_table) all rows defined by (index_name, index_values) are added.
        If the given table has a foreign key to another (parent) table all required data is added recursively
        If another (children) table has a foreign key on the given table all required data is added if the given table
            is in link_children_table.

        :param table_name: str
            name of the given table
        :param index_name: list of str
            list of name of the index columns
        :param index_values: nested list or nested np.array()
            values for the index columns which should be selected from the database table
            either [1,2,3] for single index or [['a', 1, 2], ['b', 2,2]] for multiindex
        :param caller_table_name: str, optional, Default ''
            name of the caller table (parent or child of the given table), required to avoid circular dependencies
        :param recursive_level: str, optional, Default ''
            level of recursiveness, to reconstruct how the experiments
        :param link_children_table: list of str
            list of name_table for which also the children tables (tables having a foreign key on the given table)
            should be added. Restriction to only certain tables required to avoid circular dependencies.
        :return: None
        """
        if link_children_table is None:
            link_children_table = [
                "exp_ec",  # data_ec, exp_ec_cv,peis,... , gamry tables, ...
                "exp_sfc",  # flow_cell_assemblies
                "flow_cell_assemblies",
                "spots",
                # for spots_composition (and possibly other experiments pointing to that spot)
                # "samples",
                # for samples_composition (and possibly other experiments pointing to that sample)
                "exp_icpms",  # for exp_icpms_analyte_internalstandard, ...
                "exp_icpms_analyte_internalstandard",
                # for data_icpms, exp_icpms_calibration_params, exp_icpms_integration
                "exp_icpms_calibration_set",  # for calibration experiments
                "ana_icpms_sfc_fitting",  # for ana_icpms_sfc_fitting_peaks
            ]
        print(recursive_level, table_name) if self.debug else ""

        index_name_str = ", ".join(index_name)
        index_values_str, index_values_params = values2sqlstring(
            index_values
        )  # str(list(index_values))[1:-1]#', '.join(index_values)#
        # print(index_values)
        # print(index_values_str, index_values_params)# == '', len(index_values_str) > 0)
        """
        if len(index_values_str) > 0 and not all([val == 'None' for val in index_values_params]):
            index_values, index_values_str, index_values_params = self._remove_existing_index(table_name, index_name,
                                                                                              index_name_str,
                                                                                              index_values,
                                                                                              index_values_str,
                                                                                              index_values_params)
        """
        # print(index_values_str, index_values_params)
        with self.engine_mysql.begin() as con_mysql:
            table_data = pd.read_sql(
                """SELECT * 
                                        FROM %s 
                                        WHERE (%s) IN """
                % (table_name, index_name_str)
                + "("
                + index_values_str
                + ")"
                + ";"
                if True
                else """;""",
                params=index_values_params,
                con=con_mysql,
                index_col=index_name,
            )

        # global df_sqlite_tables
        if len(table_data.index) > 0:
            table_data_primary_key = table_data.reset_index().set_index(
                self.primary_keys_grouped.loc[table_name]
            )
            if table_name not in self.DATABASE_DF.keys():
                new_data_added = True
                self.DATABASE_DF[table_name] = table_data_primary_key
            else:
                new_data_added = not table_data_primary_key.index.isin(
                    self.DATABASE_DF[table_name].index
                ).all()
                if new_data_added:
                    display(self.DATABASE_DF[table_name]) if self.debug else ""
                    display(table_data) if self.debug else ""
                    self.DATABASE_DF[table_name] = (
                        pd.concat(
                            [self.DATABASE_DF[table_name], table_data_primary_key]
                        )
                        .reset_index()
                        .drop_duplicates()
                        .set_index(self.primary_keys_grouped.loc[table_name])
                    )
                else:
                    print("Nothing new for %s" % table_name) if self.debug else None
        else:
            new_data_added = False

        if (
            new_data_added
        ):  # len(index_values_params) > 0 and not all([val == 'None' for val in index_values_params]):
            # if recursive:
            if (
                table_name in self.foreign_keys_grouped.TABLE_NAME.tolist()
            ):  # index.get_level_values(level='TABLE_NAME')
                for index, row in self.foreign_keys_grouped.loc[
                    (
                        (self.foreign_keys_grouped.TABLE_NAME == table_name)
                        & (
                            self.foreign_keys_grouped.REFERENCED_TABLE_NAME
                            != caller_table_name
                        )
                    ),
                    :,
                ].iterrows():
                    # if row.COLUMN_NAME == index_name:
                    #    print('index', index_name, table_name, row.REFERENCED_COLUMN_NAME, row.REFERENCED_TABLE_NAME)
                    #    continue
                    # print(index_name, row.TABLE_NAME, row.COLUMN_NAME, ' child of ',
                    #       row.REFERENCED_TABLE_NAME, row.REFERENCED_COLUMN_NAME)

                    # display(table_data)
                    referenced_index_value = (
                        table_data.reset_index()
                        .loc[:, row.COLUMN_NAME]
                        .drop_duplicates()
                        .values
                    )
                    # referenced_index_value_str =
                    # print(referenced_index_value)
                    self._transfer_tables_mysql2df(
                        table_name=row.REFERENCED_TABLE_NAME,
                        index_name=row.REFERENCED_COLUMN_NAME,
                        index_values=referenced_index_value,
                        caller_table_name=table_name,
                        recursive_level="---" + recursive_level,
                        link_children_table=link_children_table,
                    )

            for index, row in self.foreign_keys_grouped.loc[
                (
                    (self.foreign_keys_grouped.REFERENCED_TABLE_NAME == table_name)
                    # & (self.foreign_keys_grouped.TABLE_NAME != caller_table_name)
                    # must not be set: would avoid
                    # exp_sfc <<< spots --- exp_sfc (addition of experiments previously performed at that spot)
                    # exp_icpms <<< exp_icpms_calibration_set --- exp_icpms (addition of calibration exps)
                    & (
                        self.foreign_keys_grouped.REFERENCED_TABLE_NAME.isin(
                            link_children_table
                        )
                    )
                ),
                :,
            ].iterrows():

                # if row.COLUMN_NAME == index_name:
                #    print('index', index_name, table_name, row.REFERENCED_COLUMN_NAME, row.REFERENCED_TABLE_NAME)
                #    continue
                # print(index_name,  row.REFERENCED_TABLE_NAME, row.REFERENCED_COLUMN_NAME,
                #       ' parent of ', row.TABLE_NAME, row.COLUMN_NAME)
                parent_index_value = (
                    table_data.reset_index()
                    .loc[:, row.COLUMN_NAME]
                    .drop_duplicates()
                    .values
                )
                if row.TABLE_NAME == caller_table_name and self.debug:
                    # TODO: Check whether also not selected spots from the same sample are selected
                    print(
                        caller_table_name,
                        "references back and forth",
                        row.TABLE_NAME,
                        "; This might lead to an endless loop",
                    )
                    print(
                        dict(
                            table_name=row.TABLE_NAME,
                            index_name=row.COLUMN_NAME,
                            index_values=parent_index_value,  # referenced_index_value,
                            caller_table_name=table_name,
                            recursive_level="<<<" + recursive_level,
                            link_children_table=link_children_table,
                        )
                    ) if self.debug else ""
                self._transfer_tables_mysql2df(
                    table_name=row.TABLE_NAME,
                    index_name=row.COLUMN_NAME,
                    index_values=parent_index_value,  # referenced_index_value,
                    caller_table_name=table_name,
                    recursive_level="<<<" + recursive_level,
                    link_children_table=link_children_table,
                )
            # else:
            #    print('No recursive search for ', table_name)

    def _transfer_tables_specified_mysql2df(self,
                                            name_table,
                                            index_col=None,
                                            add_cond=None,
                                            add_cond_params=None):
        """
        Transfers data from MySQL to Publication.DATABASE_DF for the given table, for entries fulfilling add_cond.
        Partially added tables are not supported.
        :param name_table: str
            table names from which entries fulfilling add_cond should be transferred to DATABASE_DF
        :param index_col: str or list of str or None
            index columns in the table. Does not have to provided if table has a primary key.
        :param add_cond: str
            additional SQL condition
        :param add_cond_params: str
            parameter for the additional SQL condition
        :return: None
        """
        if index_col is None:
            index_col = []
        if add_cond_params is None:
            add_cond_params = []

        with self.engine_mysql.begin() as con_mysql:
            print(name_table) if self.debug else ""
            if add_cond is not None:
                table_data = db.query_sql(
                    """SELECT * 
                       FROM """+name_table+""" 
                       WHERE """+add_cond+"""; """,
                    params=add_cond_params,
                    con=con_mysql,
                )
            else:
                table_data = db.query_sql(
                    """SELECT * 
                       FROM %s ; """
                    % name_table,
                    con=con_mysql,
                )
            if index_col:
                table_data = table_data.set_index(index_col)
            elif name_table in self.primary_keys_grouped.index:
                table_data = table_data.set_index(
                    self.primary_keys_grouped.loc[name_table]
                )
            else:
                warnings.warn('No index column provided. '
                              'This might lead to an error during insertion into sqlite database')

            if name_table not in self.DATABASE_DF.keys():
                self.DATABASE_DF[name_table] = table_data
            else:
                raise Exception(
                    "Table already partially added. Adding of all values for these tables not "
                    + "supported "
                )

    def transfer_tables_df2sqlite(self):
        """
        Transfers all data from Publication.DATABASE_DF to SQLITE database.
        :return:
        """
        # print()
        with self.engine_sqlite.begin() as con_sqlite:
            # loop through tables alphabetically
            for table_name in sorted(list(self.DATABASE_DF.keys())):
                table_data = self.DATABASE_DF[table_name]
                print(
                    "Add",
                    len(table_data.index),
                    "entries to table",
                    table_name,
                )
                # display(table)
                table_data.to_sql(table_name, con=con_sqlite, if_exists="append")
            if self.debug:
                display(
                    pd.read_sql(
                        """ SELECT *
                                    FROM sqlite_master
                                   WHERE type='table'
                                   ;""",  # , 'VIEW'
                        con=con_sqlite,
                    )
                )


def create_empty_sqlite(path_to_sqlite_empty_tables=None):
    """
    With each change in the database schema, the empty sqlite file has to be updated. With this function the terminal
    commands for empty sqlite file creation are generated.
    Creation via mysql2sqlite has to be performed in a pip environment. (mysql2sqlite is not available in conda)
    Afterwards run transfer_views_mysql2sqlite to transfer also view definitions.
    :return: None
    """
    print(
        "\x1b[33m",
        "On-the-fly creation of sqlite database structure from mysql not yet developed. Make sure sqlite "
        "template file is created from current database state"
        "\x1b[0m",
    )
    if path_to_sqlite_empty_tables is None:
        path_to_sqlite_empty_tables = DIR_EMPTY_SQLITE_NO_VIEWS

    if os.path.isfile(path_to_sqlite_empty_tables):
        if user_input.user_input(
            text="Delete previous empty database file? "
            + str(path_to_sqlite_empty_tables)
            + "\n",
            dtype="bool",
        ):
            os.remove(path_to_sqlite_empty_tables)
            print("\x1b[33m", "Successfully removed file!", "\x1b[0m")

    views_sorted = db.get_views_sorted()
    # Check that the base table for each view is defined in hte_data_documentation.view_information
    [db.derive_name_base_table(view) for view in views_sorted]

    print("\x1b[33m", "locally run to create sqlite.db without views:", "\x1b[0m")
    # -p to prompt for password instead of --mysql-password included in the file
    print(
        "mysql2sqlite -f %s -d %s -u %s -p -W -e %s -h %s"
        % (
            path_to_sqlite_empty_tables,
            "hte_data",
            "hte_read",
            " ".join(views_sorted),
            "%%mysql-host%%",
        )
    )
    # entries of documentation tables will be added later via _transfer_tables_specified_mysql2df
    '''
    print()
    print("\x1b[33m", "Also run:", "\x1b[0m")
    print(
        """mysql2sqlite -f %s -d %s -u %s -p -t documentation_tables documentation_columns -h %s"""
        % (path_to_sqlite_empty_tables,
           "hte_data",
           "hte_read",
           "%%mysql-host%%",)
    )
    '''
    # does not work as command is executed in path of jupyter notebook
    # os.system(command)

    # if os.path.isfile(self.path_to_publication_sqlite):
    #    os.remove(self.path_to_publication_sqlite)
    #    print('Deleted sqlite: ', self.path_to_publication_sqlite)


def transfer_views_mysql2sqlite(exclude_views=None, debug=False):
    """
    Transfer definition of views from mysql to sqlite database
    :param exclude_views: list or None, optional, Default None
        list of views to be excluded for the transfer
    :param debug: print debug info if True
    :return:
    """
    if exclude_views is None:
        exclude_views = ["data_icpms_sfc_analysis_old"]
    if os.path.isfile(DIR_EMPTY_SQLITE):
        os.remove(DIR_EMPTY_SQLITE)
        print("Deleted previous file: ", DIR_EMPTY_SQLITE)
    shutil.copy2(src=DIR_EMPTY_SQLITE_NO_VIEWS, dst=DIR_EMPTY_SQLITE)
    for view in db.get_views_sorted():
        if view in exclude_views:
            print("Excluded view: ", view)
            continue
        print("CONVERT VIEW", view)

        with db.connect(user="hte_processor").begin() as con_mysql:
            create_view_statement = (
                pd.read_sql(
                    """SHOW CREATE VIEW %s;""" % view, con=con_mysql  # , 'VIEW'
                )
                .loc[:, "Create View"]
                .loc[0]
            )

        create_view_statement = mysql_to_sqlite.view_header(create_view_statement)
        create_view_statement = mysql_to_sqlite.time_intervals(
            create_view_statement, debug
        )
        create_view_statement = mysql_to_sqlite.timestampdiff(
            create_view_statement, debug
        )
        create_view_statement = mysql_to_sqlite.functions(create_view_statement)
        create_view_statement = mysql_to_sqlite.redundant_brackets(
            create_view_statement, debug
        )

        # print(create_view_statement)
        engine_sqlite = db_config_binder.connect(path_to_sqlite=DIR_EMPTY_SQLITE)
        with engine_sqlite.begin() as con_sqlite:
            con_sqlite.execute("""DROP VIEW IF EXISTS %s""" % view)
            con_sqlite.execute(create_view_statement)
            display(
                pd.read_sql(""" SELECT * FROM %s;""" % view, con=con_sqlite)
            ) if debug else ""
        engine_sqlite.dispose()


def add_publication_exp(df_exp, name_base_table):
    """
    Adds experiment to a publication in the database table publication_exp.
    Is performed when evaluation.utils.db.get_exp() is called within a previously initialized publication folder
    :param df_exp: pd.DataFrame
        DataFrame of the experiments to be added
    :param name_base_table: str
        name of the base table to which the experiment is referenced to
    :return:
    """
    publication = Publication()
    if publication.created:
        print("Link selected experiments to publication: ", publication.id_publication)
    else:
        print("No publication created to link experiments")
        return False

    primary_keys = db.get_primarykeys()

    # TODO: add user restriction, only add experiment when own data

    with db.connect(user="hte_processor").begin() as con_write:
        counter_existed = 0
        counter_inserted = 0
        for index, row in df_exp.reset_index().iterrows():
            # check whether experiment already added
            sql_check_existing = (
                """SELECT count_exp
                                    FROM publication_exps 
                                    WHERE id_publication=%s 
                                        AND name_table =%s
                                    """
                + " AND ("
                + " OR ".join(
                    ["(name_index_col = %s AND value_index_col = %s )\n"]
                    * len(primary_keys.loc[name_base_table])
                )
                + """) 
                    GROUP BY count_exp
                    HAVING COUNT(*) = %s;"""
            )
            # print(sql)
            params = (
                [publication.id_publication, name_base_table]
                + sum(
                    [
                        [name_index_col, row.loc[name_index_col]]
                        for name_index_col in primary_keys.loc[name_base_table]
                    ],
                    [],
                )
                + [len(primary_keys.loc[name_base_table])]
            )
            # print(params)
            count_exp_exist = pd.read_sql(
                sql_check_existing, params=params, con=con_write
            )  # .count_exp.max()
            if len(count_exp_exist) > 0:
                # print('Already added', params)
                counter_existed += 1
                continue

            # check for highest count_exp and add correspondingly
            counter_in_db = pd.read_sql(
                "SELECT MAX(count_exp)+1 AS counter FROM publication_exps WHERE id_publication=%s AND name_table =%s",
                params=[publication.id_publication, name_base_table],
                con=con_write,
            ).loc[0, "counter"]
            counter_in_db = 1 if counter_in_db is None else int(counter_in_db)

            # add experiment to publication_exp
            for name_index_col in primary_keys.loc[name_base_table]:
                # print('Insert experiment: ', name_base_table, counter_in_db, name_index_col, row.loc[index_col])
                con_write.execute(
                    """INSERT INTO publication_exps (`id_publication`, 
                                                     `name_table`, 
                                                     `count_exp`, 
                                                     `name_index_col`, 
                                                     `value_index_col`)
                       VALUES (%s, %s, %s, %s, %s)
                    """,
                    [
                        publication.id_publication,
                        name_base_table,
                        counter_in_db,
                        name_index_col,
                        row.loc[name_index_col],
                    ],
                )
            counter_inserted += 1
    print(
        "\x1b[32m",
        "For table",
        name_base_table,
        ": inserted new experiments =",
        counter_inserted,
        ", skipped existing experiments =",
        counter_existed,
        "\x1b[0m",
    )


def values2sqlstring(values):
    """
    used in _transfer_tables_mysql2df, transform list of values to sql '%s' string and correspodning params list
    :param values: list of index values, either [1,2,3] for single index or [['a', 1, 2], ['b', 2,2]] for multiindex
    :return: sqlstring, params
    """
    # singlevalues_types = [str, int, float, ]
    multivalues_types = [list, np.ndarray]

    if len(values) == 0:
        sqlstring = ""
        params = []
    elif type(values) not in multivalues_types:
        sqlstring = "%s"
        params = [values]
    else:  # if type(values) in multivalues_types:
        # print(values)
        if (
            type(values[0]) in multivalues_types and len(values[0]) == 1
        ):  # singleindex in brakets reduce dimension
            values = [val[0] for val in values]
        # print(values,type(values[0]) not in multivalues_types)
        if type(values[0]) not in multivalues_types:  # singleindex
            # values.remove(None)
            sqlstring = ", ".join(["%s"] * len(values))
            params = [str(val) for val in values]
        else:  # multiindex
            sqlstring = ", ".join(
                ["(" + ", ".join(["%s"] * len(row)) + ")" for row in values]
            )
            params = []
            [[params.append(str(val)) for val in row] for row in values]

    # print(sqlstring, params)
    return sqlstring, params


def copy_and_replace(src, dst, function, str_prepend_file='', **kwargs):
    """
    Copy a file to another location while replacing lines according to separate function
    :param src: str or pathlib.Path
        path to the file which should be copied
    :param dst:  str or pathlib.Path
        path to where the file should be copied
    :param function: callable
        is called for each line and should return a formatted string as the line in th enew file
    :param str_prepend_file: str
        string which will be prepended to the copied file
    :param kwargs: keywaord arguments of fucntion
    :return:
    """
    with open(dst, 'w') as new_file:
        new_file.write(str_prepend_file+'\n')
        with open(src) as old_file:
            for line in old_file:
                new_file.write(function(line, **kwargs))


def remove_part_between(line, str_find_remove='# %%% remove'):
    """
    removes part of the given string as defined in a comment at the end of the line giving
    between start_string and end_string.
    :param line: str
        input line
    :param str_find_remove: str, default '# %%% remove'
        string which indicates a removal
    :return:
    """
    if str_find_remove in line:
        str_find_between = 'between'
        str_find_between_and = 'and'
        how_to_remove = line.split(str_find_remove)[1]
        if str_find_between in how_to_remove:
            str_start, str_end = [item.strip(' \n') for item in
                                  how_to_remove.split(str_find_between)[1].split(str_find_between_and)]
            # line_up_to_start, line_from_start_on
            line_removed_comment = line.split(str_find_remove)[0]
            idx_start = line_removed_comment.find(str_start) + len(str_start)
            newline = line_removed_comment[:idx_start]
            newline += line_removed_comment[idx_start:][line_removed_comment[idx_start:].find(str_end):]
            newline += '\n'
            print('Removed part of line, result: ', newline)
            return newline
        else:
            warnings.warn(
                'Found comment to remove line when uploading: ' + str_find_remove
                + '; But it is not developed how to remove.')
    else:
        return line

