"""
Scripts for the insertion of ICP-MS data from Agilent Mass Hunter or Perkin Elmer software
Created in 2023
@author: Forschungszentrum Jülich GmbH, Nico Röttcher
"""

import pandas as pd
import numpy as np

from pathlib import Path  # file paths
import sqlalchemy as sql

# install package mysqlclient!


import warnings
import datetime as dt
import glob, os, sys, socket

# git-synced modules
from evaluation.utils import db
from evaluation.utils.user_input import manually_add, user_input, init_new_entry
from evaluation.processing import icpms_calibration

from pathlib import Path
import pandas as pd
import os, glob, sys, warnings
from bs4 import BeautifulSoup


def to_str_or_none(beautifulsoupelement):
    return (
        str(beautifulsoupelement.string) if beautifulsoupelement is not None else None
    )


def auto_insert_AgilentBatch(
    path_to_data=Path(r"D:\Agilent\ICPMH\1\DATA"),
    name_setup_icpms="hte_1",
    id_calibration_set_from_same_user_only=True,  # default
):
    """
    Routine to guide user for automatic insertion of icpms experiments
    :param path_to_data: path to data storage of Agilent ICPMS Software
    :param name_setup_icpms: name of the ICPMS setup
    :param id_calibration_set_from_same_user_only: bool
        restrict selection of calibration set to the same user only
    :return: None
    """

    def get_csv_set(path):
        existing_files = set()
        # for path, subdir, files in os.walk(path):
        for file in [
            file
            for path, subdir, files in os.walk(path)
            for file in glob.glob(os.path.join(path, "*.csv"))
        ]:
            fullpath = os.path.join(path, file)
            is_2nd_order_subdir = (
                len(file.split("\\")) - len(str(path).split("\\")) > 2
            )  # Data is stored at least two subdirs below path: path_username/../batchname/dataname/data.csv
            is_ignored_batch = (Path(file).parent.parent / ".insertignore").is_file()
            if (
                os.path.isfile(fullpath)
                and is_2nd_order_subdir
                and not is_ignored_batch
                and check_Agilent_data_csv(file)
            ):
                # print(Path(file).parent.parent)
                existing_files.add(file)

        return existing_files

    engine = db.connect("hte_inserter_icpms")

    with engine.begin() as conn:
        exp_icpms_init = pd.DataFrame({})
        exp_icpms_init.loc[0, "dummy"] = "dummy"
        exp_icpms_init, manual_info_exp_icpms = manually_add(
            parameters=[
                {"name": "name_user", "fk_table_name": "users", "dtype": "fk"},
            ],
            preset={},
            write_to=exp_icpms_init,
            conn=conn,
            engine=engine,
        )
        name_user = exp_icpms_init.loc[0, "name_user"]
        ignored_files = set(
            row[0]
            for row in set(
                conn.execute(
                    """SELECT file_path_rawdata FROM exp_icpms WHERE name_user = '"""
                    + name_user
                    + """';"""
                ).fetchall()
            )
        )

    # existing_files = get_csv_set(path)
    do_file_search = True
    while do_file_search:
        now_existing_files = get_csv_set(path_to_data / name_user)
        new_files = now_existing_files - ignored_files
        # print('jo', new_files)

        set_of_new_batches = list(
            set([Path(new_batch).parent.parent for new_batch in new_files])
        )  # set removes duplicates
        set_of_new_batches.sort()
        rescan_text = "rescan for new files"
        quit_text = "quit the app"
        choices = set_of_new_batches.copy() + [rescan_text] + [quit_text]

        answer = user_input(
            text="\n\n Found new data in following batches. Choose which one to be inserted: \n"
            if len(set_of_new_batches) > 0
            else "\n\n Nothing new found. Choose:\n",
            dtype="int",
            optional=False,
            options=pd.DataFrame(
                {
                    "values": {no: str(val) for no, val in enumerate(choices)},
                    "dropdown": {
                        no: str(batch).replace(str(path_to_data), "")
                        for no, batch in enumerate(choices)
                    },
                }
            ),
        )

        if answer == rescan_text:
            continue
        elif answer == quit_text:
            do_file_search = False
        else:
            batch = Path(answer)
            # print(batch)
            # sys.exit()

            try:
                print("\x1b[32m", "\n\nInserting", batch.name, "\x1b[0m")
                insert_AgilentBatch(
                    path_to_files=batch,
                    name_user=name_user,
                    name_setup_icpms=name_setup_icpms,
                    id_calibration_set_from_same_user_only=id_calibration_set_from_same_user_only,
                    # default
                )
            except Exception as err:
                if str(err) in ["No data to be inserted"]:
                    print("\x1b[31m", err, "\x1b[0m")
                else:
                    raise Exception

            # add all csv files in batch to ignored files,
            # either inserted or already existent in database (will thrwo error)
            # print([file for file in new_files if str(batch) in str(file)])
            [ignored_files.add(file) for file in new_files if str(batch) in str(file)]


def insert_AgilentBatch(
    path_to_files,
    name_setup_icpms="hte_1",
    id_calibration_set_from_same_user_only=True,  # default
    name_user=None,
):
    """
    Insert an ICP-MS Batch measured with Agilents MassHunter Software using the parameters already given in the software.
    :param path_to_files: path to data folder of the ICP-MS. In there a folder named as the user must be contained!
    :param name_setup_icpms:
    :param id_calibration_set_from_same_user_only: bool
        restrict selection of calibration set to the same user only
    :param name_user: str
        name of the user
    :return:
    """
    engine = db.connect("hte_inserter_icpms")
    with engine.begin() as conn:
        exp_icpms_init = pd.DataFrame({})

        exp_icpms_init.loc[
            0, "name_computer_inserted_data"
        ] = socket.gethostname()  # os.environ['COMPUTERNAME'] not working under linux
        exp_icpms_init.loc[0, "t_inserted_data__timestamp"] = str(dt.datetime.now())
        exp_icpms_init.loc[0, "name_setup_icpms"] = name_setup_icpms
        if name_user is None:
            exp_icpms_init, manual_info_exp_icpms = manually_add(
                parameters=[
                    {"name": "name_user", "fk_table_name": "users", "dtype": "fk"},
                ],
                preset={},
                write_to=exp_icpms_init,
                conn=conn,
                engine=engine,
            )
        else:
            exp_icpms_init.loc[0, "name_user"] = name_user
        # read Batch from Agilent csv and xml files in given folder
        try:
            (
                exp_icpms,
                exp_icpms_analyte_internalstandard,
                data_icpms,
            ) = read_AgilentBatch(path_to_files, exp_icpms_init, conn)
        except Exception as err:
            raise Exception(err)
        # display(exp_icpms)

    with engine.begin() as conn:
        # connection restart otherwise program crashes after calling conn.execute in read_AgilentBatch function
        if "calibration" in exp_icpms.type_experiment.unique():
            print("Calibration specific information")
            is_complete_calib_set = user_input(
                text="Is the calibration set complete or would you like to add a datapoint later?\n",
                dtype="int",
                optional=False,
                options=pd.DataFrame(
                    {
                        "values": {
                            0: True,
                            1: False,
                        },
                        "dropdown": {
                            0: "It is complete. Please run the calibration.",
                            1: "I want to add other datapoints later",
                        },
                    }
                ),
            )

            is_new_calib_set = user_input(
                text="Does the calibration belong to a new or previously recorded calibration set?\n",
                dtype="int",
                optional=False,
                options=pd.DataFrame(
                    {
                        "values": {
                            0: True,
                            1: False,
                        },
                        "dropdown": {
                            0: "New calibration set",
                            1: "An additional datapoint for a previous calibration",
                        },
                    }
                ),
            )
        else:
            is_new_calib_set = False
            is_complete_calib_set = False

        if not is_new_calib_set:
            exp_icpms, manual_info_exp_icpms = manually_add(
                parameters=[
                    {
                        "name": "id_exp_icpms_calibration_set",
                        "fk_table_name": "exp_icpms_calibration_set",
                        "dtype": "fk",
                        "fk_table_filter": """SELECT id_exp_icpms_calibration_set, 
                                                      CONCAT('id_exp_icpms_calibration_set: ',
                                                            id_exp_icpms_calibration_set, 
                                                            ', ',CAST(CHAR(9) AS CHAR),
                                                            'name_user: ',MIN(name_user), 
                                                            ', ',CAST(CHAR(9) AS CHAR),
                                                            '    at: ',MIN(t_start__timestamp_icpms_pc),
                                                            CAST(CHAR(9) AS CHAR),
                                                            '    with icpms: ',MIN(name_setup_icpms),
                                                            CAST(CHAR(9) AS CHAR)
                                                            ) AS dropdown 
                                                FROM hte_data.exp_icpms
                                                """
                        + (
                            '''WHERE name_user = "'''
                            + exp_icpms.name_user.iloc[0]
                            + '''"'''
                            if id_calibration_set_from_same_user_only
                            else ""
                        )
                        + """GROUP BY id_exp_icpms_calibration_set;""",
                    },
                ],  # exp_icpms_sfc_expanded '    with sfc: ',MIN(name_setup_sfc),CAST(CHAR(9) AS CHAR)
                preset={},
                write_to=exp_icpms,
                conn=conn,
                engine=engine,
            )
        else:
            exp_icpms.loc[:, "id_exp_icpms_calibration_set"] = init_new_entry(
                "exp_icpms_calibration_set", conn, engine
            )

        exp_icpms_sfc = pd.DataFrame({})
        if "sfc-icpms" in exp_icpms.type_experiment.unique():
            print("\x1b[36m", "\nSFC-icpms specific information\n", "\x1b[0m")
            for index, row in (
                exp_icpms.loc[exp_icpms.type_experiment == "sfc-icpms", :]
                .reset_index()
                .iterrows()
            ):
                exp_icpms_sfc.loc[index, "id_sample_in_batch"] = row.id_sample_in_batch

                exp_icpms_sfc, manual_info_exp_icpms_sfc_file = manually_add(
                    parameters=[
                        {
                            "name": "name_setup_sfc",
                            "dtype": "fk",
                            "fk_table_name": "setups_sfc",
                            "optional": False,
                        },
                        {
                            "name": "t_start__timestamp_sfc_pc",
                            "dtype": "timestamp",
                            "optional": False,
                            "print_info_before": "ICP-MS starting time: "
                            + row.t_start__timestamp_icpms_pc,
                        },
                        {
                            "name": "t_delay__s",
                            "dtype": "float",
                            "optional": True,
                            "default": 0,
                        },
                        {
                            "name": "flow_rate_real__mul_min",
                            "dtype": "float",
                            "optional": True,
                        },
                    ],
                    preset={},
                    write_to=exp_icpms_sfc,
                    conn=conn,
                    engine=engine,
                    row_selector=index,
                )

        exp_icpms_sfc_batch = pd.DataFrame({})
        if "sfc-batch" in exp_icpms.type_experiment.unique():
            print("\x1b[36m", "\nSFC-batch specific information\n", "\x1b[0m")
            fill_batch_specific_values_later = user_input(
                text="Fill batch specific later via Workbench?\n",
                dtype="bool",
            )
            if fill_batch_specific_values_later:
                for index, row in (
                    exp_icpms.loc[exp_icpms.type_experiment == "sfc-batch", :]
                    .reset_index()
                    .iterrows()
                ):
                    exp_icpms_sfc_batch.loc[
                        index, "id_sample_in_batch"
                    ] = row.id_sample_in_batch
                (
                    exp_icpms_sfc_batch,
                    manual_info_exp_icpms_sfc_batch_file,
                ) = manually_add(
                    parameters=[
                        {
                            "name": "name_setup_sfc",
                            "dtype": "fk",
                            "fk_table_name": "setups_sfc",
                            "optional": False,
                        },
                        {
                            "name": "location",
                            "dtype": "enum",
                            "enum_table": "exp_icpms_sfc_batch",
                            "optional": False,
                        },
                        {"name": "t_delay__s", "dtype": "float", "optional": True},
                    ],
                    preset={},
                    write_to=exp_icpms_sfc_batch,
                    conn=conn,
                    engine=engine,
                )
            else:
                for index, row in (
                    exp_icpms.loc[exp_icpms.type_experiment == "sfc-batch", :]
                    .reset_index()
                    .iterrows()
                ):
                    exp_icpms_sfc_batch.loc[
                        index, "id_sample_in_batch"
                    ] = row.id_sample_in_batch
                    (
                        exp_icpms_sfc_batch,
                        manual_info_exp_icpms_sfc_batch_file,
                    ) = manually_add(
                        parameters=[
                            {
                                "name": "name_setup_sfc",
                                "dtype": "fk",
                                "fk_table_name": "setups_sfc",
                                "optional": False,
                            },
                            {
                                "name": "location",
                                "dtype": "enum",
                                "enum_table": "exp_icpms_sfc_batch",
                                "optional": False,
                            },
                            {
                                "name": "t_start__timestamp_sfc_pc",
                                "dtype": "timestamp",
                                "optional": True,
                            },
                            {
                                "name": "t_end__timestamp_sfc_pc",
                                "dtype": "timestamp",
                                "optional": True,
                            },
                            {"name": "t_delay__s", "dtype": "float", "optional": True},
                            {"name": "m_start__g", "dtype": "float", "optional": True},
                            {"name": "m_end__g", "dtype": "float", "optional": True},
                        ],
                        preset={},
                        write_to=exp_icpms_sfc_batch,
                        conn=conn,
                        engine=engine,
                        row_selector=index,
                    )
            # display(exp_icpms_sfc_batch)

    with engine.begin() as conn:  # connection restart

        # write into db
        db.call_procedure(engine, "Reset_Autoincrement", ["exp_icpms", "id_exp_icpms"])

        # exp_icpms
        try:
            display(exp_icpms)
            # print([type(val) for val in exp_icpms.iloc[0].to_numpy()])
            exp_icpms = db.insert_into(conn, "exp_icpms", exp_icpms).rename(
                columns={"inserted_primary_key": "id_exp_icpms"}
            )  # [0]
            print("\x1b[32m", "Successfully inserted to exp_icpms", "\x1b[0m")
        except sql.exc.IntegrityError as error:
            print(str(error.orig), type(error.orig))
            if "Duplicate entry" in str(error.orig) and "UNIQUE" in str(error.orig):
                warnings.warn(
                    "\n One of the files is already added to db and will be skipped. "
                    "\nIf this is not intended check uniqueness of couple: "
                    "\n name_setup_icpms, t_start__timestamp_icpms_pc, file_name_rawdata"
                )
            # return manual_info, id_exp_icpms_calibration_sets
            else:
                warnings.warn(error.orig)
                sys.exit("Duplicate entry")

        # exp_icpms_analyte_internalstandard
        exp_icpms_analyte_internalstandard.join(
            exp_icpms.loc[:, ["id_exp_icpms", "id_exp_icpms_calibration_set"]],
            on="id_sample_in_batch",
        ).set_index(
            ["id_exp_icpms", "name_isotope_analyte", "name_isotope_internalstandard"]
        ).drop(
            columns="id_sample_in_batch"
        ).to_sql(
            "exp_icpms_analyte_internalstandard", con=conn, if_exists="append"
        )
        print(
            "\x1b[32m",
            "Successfully inserted to exp_icpms_analyte_internalstandard",
            "\x1b[0m",
        )

        # exp_icpms_sfc
        if "sfc-icpms" in exp_icpms.type_experiment.unique():
            exp_icpms_sfc.join(
                exp_icpms.loc[:, ["id_exp_icpms"]], on="id_sample_in_batch"
            ).set_index(["id_exp_icpms"]).drop(columns="id_sample_in_batch").to_sql(
                "exp_icpms_sfc", con=conn, if_exists="append"
            )
            print("\x1b[32m", "Successfully inserted to exp_icpms_sfc", "\x1b[0m")

        # exp_icpms_sfc_batch
        if "sfc-batch" in exp_icpms.type_experiment.unique():
            exp_icpms_sfc_batch.join(
                exp_icpms.loc[:, ["id_exp_icpms"]], on="id_sample_in_batch"
            ).set_index(["id_exp_icpms"]).drop(columns="id_sample_in_batch").to_sql(
                "exp_icpms_sfc_batch", con=conn, if_exists="append"
            )
            print("\x1b[32m", "Successfully inserted to exp_icpms_sfc_batch", "\x1b[0m")

        # data_icpms
        print(
            "Start inserting time-resolved data. This can take some time please wait."
        )
        data_icpms.reset_index().join(
            exp_icpms.loc[:, ["id_exp_icpms"]], on="id_sample_in_batch"
        ).set_index(
            ["id_exp_icpms", "name_isotope_analyte", "name_isotope_internalstandard"]
        ).drop(
            columns="id_sample_in_batch"
        ).to_sql(
            "data_icpms", con=conn, if_exists="append", chunksize=1000
        )
        print("\x1b[32m", "Successfully inserted to data_icpms", "\x1b[0m")

    if is_complete_calib_set:
        print(
            "Auto start calibration of id_exp_icpms_calibration_set",
            exp_icpms.id_exp_icpms_calibration_set.iloc[0],
        )
        if os.name == "nt":  # for windows development computer
            icpms_calibration.calibrate(
                export_folder=path_to_files,
                id_exp_icpms_calibration_set=int(
                    exp_icpms.id_exp_icpms_calibration_set.iloc[0]
                ),
            )
        else:
            # if run on server directly copy+paste it to standard folder defined in calibrate method
            icpms_calibration.calibrate(
                id_exp_icpms_calibration_set=int(
                    exp_icpms.id_exp_icpms_calibration_set.iloc[0]
                )
            )


def read_AgilentBatch(path_to_files, exp_icpms_init=pd.DataFrame({}), conn=None):
    # Problem BatchLog.csv and BatchLog.xml just written after execution...
    # df_BatchLogcsv = read_BatchLogcsv(path_to_files)
    # df_sample_list, df_icpms_elements = read_AcqMethod( path_to_files)
    # exp_icpms = join_BatchLogcsv_AcqMethod(df_BatchLogcsv, df_sample_list)

    # Alternative via SampleInfo
    df_sample_list, df_icpms_elements = read_AcqMethod(path_to_files)
    exp_icpms = add_sampleInfo(path_to_files, df_sample_list)
    # exp_icpms.loc[:, 'type_experiment'] = exp_icpms.loc[:, 'type_experiment'].replace({'CalStd': 'calibration',
    #                                                                                    'Sample': 'sfc-icpms'})
    # Transform type_experiment to database format (calibration, sfc-ipcms, sfc-batch)
    for index, row in exp_icpms.iterrows():
        if row.type_experiment == "CalStd":
            exp_icpms.loc[index, "type_experiment"] = "calibration"
        elif row.type_experiment == "Sample":
            if row.comment in ["batch", "sfc-batch"]:
                exp_icpms.loc[index, "type_experiment"] = row.comment
            else:
                exp_icpms.loc[index, "type_experiment"] = "sfc-icpms"
            if row.comment != "batch" and row.level is not None:
                print(
                    "\x1b[31m",
                    "For",
                    row.name_sample,
                    " a Analyte Concentration level is given. "
                    "This conflicts with CHECK_exp_icpms_c_analyte__mug_L_optional_for_calibration.",
                    "\x1b[0m",
                )
                if user_input(
                    text="Do you want to ignore the given analyte concentration level?\n",
                    dtype="bool",
                ):
                    exp_icpms.loc[index, "level"] = None
                else:
                    print(
                        "\x1b[31m", "This will probably fail, let's see...", "\x1b[0m"
                    )
                    # raise Exception('Other units are not supported yet.')
        else:
            print(
                "\x1b[31m",
                "Unknown sample type database only capable of sample type = CalStd and Sample",
                "\x1b[0m",
            )

    # add init values to exp_icpms
    # print(exp_icpms_init not None)
    # if exp_icpms_init not None:
    exp_icpms.loc[:, exp_icpms_init.columns] = exp_icpms_init.values[0]

    # sort exp_icpms
    exp_icpms = exp_icpms.sort_values(by="t_start__timestamp_icpms_pc")
    # display(exp_icpms)

    # Check and remove already inserted experiments
    for index, row in exp_icpms.iterrows():
        # print(row.name_setup_icpms, str(row.t_start__timestamp_icpms_pc))
        if (
            conn.execute(
                """SELECT COUNT(*) FROM exp_icpms WHERE name_setup_icpms='"""
                + row.name_setup_icpms
                + """' AND t_start__timestamp_icpms_pc = '"""
                + str(row.t_start__timestamp_icpms_pc)
                + """';"""
            ).first()[0]
            == 1
        ):
            exp_icpms = exp_icpms.drop(labels=index, axis="index")
            print(
                "\x1b[33m",
                row.name_sample,
                " is already inserted into database and will be skipped. Overwriting is not possible."
                "\x1b[0m",
            )

    # Check if csv exists and read in
    exp_icpms, data_icpms_all_csv = read_datacsv(path_to_files, exp_icpms)

    # Return False if empty
    if exp_icpms.empty:
        raise Exception("No data to be inserted")
    # display(exp_icpms)

    exp_icpms_analyte_internalstandard = exp_icpms.loc[
        :, ["id_sample_in_batch", "type_experiment", "level", "ISTD_level"]
    ]
    # display(exp_icpms_analyte_internalstandard)

    # read DA method
    df_calib_Level_conc, df_calib_icpms_elements = read_DAMethod(path_to_files)

    df_calib_icpms_elements = df_calib_icpms_elements.join(
        df_icpms_elements.set_index("name_isotope"), on=["name_isotope"]
    )
    # display(df_calib_icpms_elements)

    # Check that ISTD flagging is properly done (there are redundant values)
    if any(
        df_calib_icpms_elements.ISTDFlag != df_calib_icpms_elements.is_internalstandard
    ):
        print(
            "\x1b[31m",
            "Not matching redundant columns! "
            "Columns ISTDFlag (DAMethod.batch.xml) and is_internalstandard (AcqMethod.xml) do not match.\n",
            " Further processes will consider ISTDFlag column, "
            "if this information is wrong, please abort the insertion.",
            "\n Please inform Nico!",
            "\x1b[0m",
        )
        display(df_calib_icpms_elements)

    df_calib_Level_conc = df_calib_Level_conc.join(
        df_calib_icpms_elements.set_index("CompoundID"), on=["CompoundID"]
    )

    # Separate df_calib_Level_conc in analyte and ISTD levels.
    # Selecting only levels which are actually used in Sample List
    df_calib_Level_conc_analyte = (
        df_calib_Level_conc.loc[
            (df_calib_Level_conc.loc[:, "ISTDFlag"] == "false")
            & (
                df_calib_Level_conc.loc[:, "LevelName"].isin(
                    exp_icpms_analyte_internalstandard.loc[:, "level"].unique()
                )
            ),
            [
                "LevelName",
                "name_isotope",
                "t_integration__s",
                "LevelConcentration",
                "ISTDMZ",
            ],
        ]
        .set_index("LevelName")
        .rename(
            columns={
                "name_isotope": "name_isotope_analyte",
                # 'LevelName': ,
                "t_integration__s": "t_integration_analyte__s",
                "LevelConcentration": "c_analyte__mug_L",
            }
        )
    )

    # create dummy line with level None, for batch or sfc-icpms measurements where no level is given,
    # this is necessary because only over calib_level the analyte elements can be matched th internal standard ones.
    df_calib_Level_conc_analyte_noLevel = df_calib_icpms_elements.loc[
        df_calib_icpms_elements.ISTDFlag == "false",
        ["name_isotope", "t_integration__s", "ISTDMZ"],
    ].rename(
        columns={
            "name_isotope": "name_isotope_analyte",
            "t_integration__s": "t_integration_analyte__s",
        }
    )
    # print(df_calib_Level_conc_analyte_noLevel)
    df_calib_Level_conc_analyte_noLevel.loc[:, "c_analyte__mug_L"] = None
    df_calib_Level_conc_analyte_noLevel.loc[:, "LevelName"] = None
    df_calib_Level_conc_analyte_noLevel = (
        df_calib_Level_conc_analyte_noLevel.reset_index(drop=True).set_index(
            "LevelName"
        )
    )
    df_calib_Level_conc_analyte = pd.concat(
        [df_calib_Level_conc_analyte_noLevel, df_calib_Level_conc_analyte]
    )
    # print(df_calib_Level_conc_analyte)

    df_calib_Level_conc_internalstandard = (
        df_calib_Level_conc.loc[
            (df_calib_Level_conc.loc[:, "ISTDFlag"] == "true")
            & (
                df_calib_Level_conc.loc[:, "LevelName"].isin(
                    exp_icpms_analyte_internalstandard.loc[:, "ISTD_level"].unique()
                )
            ),
            [
                "LevelName",
                "isotope_mz",
                "name_isotope",
                "t_integration__s",
                "LevelConcentration",
            ],
        ]
        .set_index(["isotope_mz", "LevelName"])
        .rename(
            columns={
                "name_isotope": "name_isotope_internalstandard",
                # 'LevelName': ,
                "t_integration__s": "t_integration_internalstandard__s",
                "LevelConcentration": "c_internalstandard__mug_L",
            }
        )
    )

    # Check if there is any level information missing
    # 0. Remove analytes without ISTD
    if any(
        (
            (df_calib_Level_conc_analyte.ISTDMZ.isna())
            | (df_calib_Level_conc_analyte.ISTDMZ == "None")
        )
    ):
        print(
            "\x1b[31m",
            "The following elements has been measured without ISTD and will be discarded:\n "
            + ",\n".join(
                df_calib_Level_conc_analyte.loc[
                    (
                        (df_calib_Level_conc_analyte.ISTDMZ.isna())
                        | (df_calib_Level_conc_analyte.ISTDMZ == "None")
                    ),
                    :,
                ].name_isotope_analyte.tolist()
            ),
            "Please stop insertion if this wa snot intended and inform Nico",
            "\x1b[0m",
        )
        df_calib_Level_conc_analyte = df_calib_Level_conc_analyte.loc[
            ~(
                (df_calib_Level_conc_analyte.ISTDMZ.isna())
                | (df_calib_Level_conc_analyte.ISTDMZ == "None")
            ),
            :,
        ]
    # 1. check that for all found levels all elements are measured
    #   a) for analyte
    if (
        len(
            df_calib_Level_conc_analyte.groupby(level=0, dropna=False)[
                "name_isotope_analyte"
            ]
            .nunique()
            .unique()
        )
        > 1
    ):
        print(
            "\x1b[31m",
            "Analyte levels are not filled for every element to be analyzed:",
            "\n Please inform Nico!",
            "\x1b[0m",
        )
        display(df_calib_Level_conc_analyte)
    #   b) for internal standard
    if (
        len(
            df_calib_Level_conc_internalstandard.groupby(level=1, dropna=False)[
                "name_isotope_internalstandard"
            ]
            .nunique()
            .unique()
        )
        > 1
    ):
        print(
            "\x1b[31m",
            "Internalstandard levels are not filled for every element to be analyzed:",
            "\n Please inform Nico!",
            "\x1b[0m",
        )
        display(df_calib_Level_conc_internalstandard)
    # 2. Check that all levels requested in BatchLog are found in DAMethod.xml
    if not (
        exp_icpms_analyte_internalstandard.loc[:, "ISTD_level"]
        .isin(df_calib_Level_conc_internalstandard.index.get_level_values(1))
        .all()
        and exp_icpms_analyte_internalstandard.loc[:, "level"]
        .isin(df_calib_Level_conc_analyte.index.get_level_values(0))
        .all()
    ):
        print(
            "\x1b[31m",
            "Missing level information for \n",
            "\n ".join(
                [
                    "  analyte level "
                    + row.level
                    + " as used in id_sample_in_batch = "
                    + row.id_sample_in_batch
                    for index, row in exp_icpms_analyte_internalstandard.loc[
                        exp_icpms_analyte_internalstandard.loc[:, "level"].isin(
                            df_calib_Level_conc_analyte.index.get_level_values(0)
                        )
                        == False,
                        :,
                    ].iterrows()
                ]
            ),
            "\n ".join(
                [
                    "  ISTD level "
                    + row.ISTD_level
                    + " as used in id_sample_in_batch = "
                    + row.id_sample_in_batch
                    for index, row in exp_icpms_analyte_internalstandard.loc[
                        exp_icpms_analyte_internalstandard.loc[:, "ISTD_level"].isin(
                            df_calib_Level_conc_internalstandard.index.get_level_values(
                                1
                            )
                        )
                        == False,
                        :,
                    ].iterrows()
                ]
            ),
            "\n Please inform Nico",
            "\x1b[0m",
        )

    # Check that there is only one ISTD concentration used
    ISTDS_multiple_conc = (
        df_calib_Level_conc_internalstandard.groupby("name_isotope_internalstandard")[
            "c_internalstandard__mug_L"
        ].nunique()
        > 1
    )
    if (ISTDS_multiple_conc).any():
        print(
            "\x1b[33m",
            "Multiple concentrations given for ISTD elements: \n   ",
            ", ".join(ISTDS_multiple_conc.loc[ISTDS_multiple_conc].index),
            "\n Be sure that this was intended!",
            "\x1b[0m",
        )
        print("Check all ISTD levels found in../Method/DAMethod.batch.xml:")
        display(df_calib_Level_conc_internalstandard)
        if user_input(
            text="Do you want to quit insertion?\n",
            dtype="bool",
            optional=False,
        ):
            sys.exit("User exit due to wrong concentrations set for ISTD elements")

    # exp_icpms_analyte_internalstandard.loc[
    #   exp_icpms_analyte_internalstandard.loc[:, 'ISTD_level'].isna(), 'ISTD_level'
    #   ] = '1'
    # todo restrict this only if only one level exists
    # display(exp_icpms_analyte_internalstandard)

    exp_icpms_analyte_internalstandard = (
        exp_icpms_analyte_internalstandard.join(df_calib_Level_conc_analyte, on="level")
        .join(df_calib_Level_conc_internalstandard, on=["ISTDMZ", "ISTD_level"])
        .loc[
            :,
            [
                "id_sample_in_batch",
                "name_isotope_analyte",
                "name_isotope_internalstandard",
                "type_experiment",
                "c_analyte__mug_L",
                "c_internalstandard__mug_L",
                "t_integration_analyte__s",
                "t_integration_internalstandard__s",
            ],
        ]
    )

    data_icpms = restructure_dataicpms(
        data_icpms_all_csv, exp_icpms_analyte_internalstandard
    )
    exp_icpms = exp_icpms.set_index("id_sample_in_batch").loc[
        :,
        [
            "name_sample",
            # 'name_user',
            # 'name_setup_icpms',
            "t_start__timestamp_icpms_pc",
            "t_duration__s",
            "t_duration_planned__s",
            "num_of_scans",
            "type_experiment",
            # 'id_exp_icpms_calibration_set',
            "plasma_mode",
            "tune_mode",
            "gas_dilution_factor",
            "name_gas_collision",
            "flow_rate_collision__mL_min",
            # 'name_gas_reaction',
            # 'flow_rate_reaction__mL_min',
            "comment",
            # 'name_computer_inserted_data',
            "file_path_rawdata",
            # 't_inserted_data__timestamp',
            "file_name_rawdata",
            #'acquisition_result',
            #'error_message',
        ]
        + exp_icpms_init.columns.to_list(),
    ]
    exp_icpms.loc[:, "batch_name"] = (
        exp_icpms.loc[:, "file_path_rawdata"].str.split("\\", expand=True).iloc[:, -3]
    )
    if not (
        exp_icpms.batch_name.str.slice(
            -2,
        )
        == ".b"
    ).all():
        print(
            "\x1b[33m",
            "Maybe reading batch name from folder failed. Name of batch folder should end with .b but it doesn't.",
            "\x1b[0m",
        )
        display(
            exp_icpms.loc[
                exp_icpms.batch_name.str.slice(
                    -2,
                )
                != ".b",
                ["batch_name", "file_path_rawdata"],
            ]
        )
    # print(exp_icpms)
    return exp_icpms, exp_icpms_analyte_internalstandard, data_icpms


def read_SampleInfo(path_to_data):
    """
    Read sample info from file .../AcqMethod/sample_info.xml
    :param path_to_data:
    :return: dictionary of values found in file or None if no corresponding csv file exists
    """
    print("read ../", path_to_data.name, "/AcqData/sample_info.xml")
    SampleInfo = read_xml(path_to_data / r"AcqData/sample_info.xml", header_offset=0)

    dict_sampleInfo = {}
    keys = ["AcqTime", "Comment", "Data File"]
    column_rename_dict = {
        y: x
        for x, y in {
            "folder_path_rawdata": "Data File",
            "comment": "Comment",
            "t_start__timestamp_icpms_pc": "AcqTime",
            "type_experiment": "Sample Type",
            "name_sample": "Sample Name",
            "level": "Level Name",
            "ISTD_level": "Custom ISTD Conc Level",
        }.items()
    }
    # print(SampleInfo)
    for field in SampleInfo.SampleInfo.find_all("Field"):
        # print(field.Name.string)
        if (
            field.Name.string in column_rename_dict.keys()
        ):  # .find('LevelConcentration') is not None:
            dict_sampleInfo[column_rename_dict[str(field.Name.string)]] = (
                to_str_or_none(field.Value)
                if to_str_or_none(field.Value) not in ["", "\n", " "]
                else None
            )
    # print(dict_sampleInfo)
    dict_sampleInfo["t_start__timestamp_icpms_pc"] = (
        pd.to_datetime(dict_sampleInfo["t_start__timestamp_icpms_pc"], utc=True)
        .tz_localize(None)
        .tz_localize(tz="UTC")
        .tz_convert(tz="Europe/Berlin")
        .tz_localize(None)
        .strftime("%Y-%m-%d %X")
    )
    # Asia/Tokyo

    # Search csv file in given folder
    # print('joo', Path(row.file_path_rawdata).name)
    csv_files = sorted(
        glob.glob(str(Path(dict_sampleInfo["folder_path_rawdata"]) / "*.csv"))
    )  # for insertion from measurment computer # not including subdirectories
    csv_files = sorted(
        glob.glob(str(path_to_data / "*.csv"))
    )  # not including subdirectories

    # print(csv_files)
    for file_path in csv_files:
        if not check_Agilent_data_csv(file_path):
            csv_files.remove(file_path)
    if len(csv_files) == 0:
        print(
            "\x1b[33m",
            "No .csv data file found for",
            dict_sampleInfo["name_sample"],
            "in",
            str(path_to_data),
            "\n  Probably it is not measured yet. "
            "Please rerun after measurement or export data manually using Agilents MassHunter Offline Analysis."  
            # . For future change settings to auto-export in MassHunter Measurement Software'
            "\x1b[0m",
        )
        # exp_icpms = exp_icpms.drop(labels=index, axis='index')
        return None
        # sys.exit()
    elif len(csv_files) > 1:
        print(
            "\x1b[31m",
            "Multiple .csv data file found for",
            dict_sampleInfo["name_sample"],
            "in",
            dict_sampleInfo["folder_path_rawdata"],
            "\n   Please remove all but the one csv file you would like to insert"
            "\x1b[0m",
        )
        sys.exit()
    # else:
    file_path = Path(csv_files[0])
    dict_sampleInfo["file_name_rawdata"] = str(file_path.name)
    dict_sampleInfo["file_path_rawdata"] = str(file_path)

    # print(df_calibLevelConcCoumpound)

    print("read ../", path_to_data.name, "/AcqData/MSTS.xml")
    AcqDataMSTS = read_xml(path_to_data / r"AcqData/MSTS.xml")
    dict_sampleInfo["num_of_scans"] = to_str_or_none(
        AcqDataMSTS.TimeSegments.NumOfScans
    )

    return dict_sampleInfo


def add_sampleInfo(path_to_files, df_sample_list):
    for index, row in df_sample_list.iterrows():
        # print(path_to_files/row.folder_name_rawdata)
        if Path(path_to_files / row.DataFileName).is_dir():
            # dict_sampleInfo = read_SampleInfo(path_to_files/row.DataFileName)
            dict_sampleInfo = read_SampleInfo(path_to_files / row.DataFileName)
            if dict_sampleInfo is None:
                df_sample_list = df_sample_list.drop(labels=index, axis="index")
                continue
            for key, value in dict_sampleInfo.items():
                if key in row.index:
                    if value != row[key]:
                        print(
                            "\x1b[31m",
                            "Incoherent sampleInfo.xml and AcqMethod.xml regarding ",
                            key,
                            ":",
                            value,
                            "!=",
                            row[key],
                            "\x1b[0m",
                        )
                        sys.exit()
                    # else:
                    #    print('Match')
                df_sample_list.loc[index, key] = value
        else:
            print(
                "\x1b[33m",
                "Folder ",
                row.DataFileName,
                " not found. I assume it is not measured. Batchlist entry will be skipped."  
                # . For future change settings to auto-export in MassHunter Measurement Software'
                "\x1b[0m",
            )
            df_sample_list = df_sample_list.drop(labels=index, axis="index")
    df_sample_list.drop(columns="DataFileName", inplace=True)
    df_sample_list.loc[:, "comment"] = df_sample_list.loc[:, "comment"].replace(
        {np.nan: None}
    )  # weirdly None comments turned inot np.nan
    return df_sample_list


def read_xml(file_path, header_offset=1):
    with open(file_path, "r") as f:
        # print(f.readlines()[:])
        # print(''.join(f.readlines()[1:]))
        # print(f.read())
        # Do no use f before this command!
        file = BeautifulSoup("".join(f.readlines()[header_offset:]), "xml")
        # print(BeautifulSoup(f.read(), "xml"))
    # print(file.prettify())
    # print(len(file.prettify()))
    if len(file.prettify()) < 50:
        print(
            "\x1b[33m",
            "Warning: Short xml file detected. You might need to change the header_offset. Please inform Nico!",
            "\x1b[0m",
        )
    return file


def read_BatchLogcsv(path_to_files):
    print("read ../BatchLog.csv")
    fileName = path_to_files / r"BatchLog.csv"

    BatchLog = pd.read_csv(
        fileName
    )  # , skiprows=3, skipfooter=1).rename(columns={'Time [Sec]': 't__s'})
    # display(BatchLog)

    if "<Auto tune>" in BatchLog.loc[:, "Sample Type"].to_numpy():
        print("\x1b[33m", "Auto tune in BatchLog is skipped", "\x1b[0m")
        BatchLog = (
            BatchLog.loc[BatchLog.loc[:, "Sample Type"] != "<Auto tune>", :]
            .reset_index(drop=True)
            .drop(labels="#", axis="columns")
            .reset_index(names="#")
        )
        BatchLog.loc[:, "#"] = (BatchLog.loc[:, "#"].astype(int) + 1).astype(str)
    # ,  'User Def. 1', 'User Def. 2', 'User Def. 3', ]]\
    df_BatchLogcsv = BatchLog.loc[
        :,
        [
            "#",
            "Sample Name",
            "Sample Type",
            "File Name",
            "Acq. Date-Time",
            "Total Acq Time",
            "Comment",
            "Acquisition Result",
            "Error Message",
            "Level",
            "ISTD Conc",
        ],
    ].rename(
        columns={
            "#": "id_sample_in_batch",
            "Sample Name": "name_sample",
            "Sample Type": "type_experiment",
            "File Name": "file_path_rawdata",
            "Acq. Date-Time": "t_start__timestamp_icpms_pc",
            "Total Acq Time": "t_duration_planned__s",
            "Comment": "comment",
            "Acquisition Result": "acquisition_result",
            "Error Message": "error_message",
            "Level": "level",
            "ISTD Conc": "ISTD_level",
            # 'User Def. 1',
            # 'User Def. 2',
            # 'User Def. 3',
        }
    )
    df_BatchLogcsv.loc[:, "id_sample_in_batch"] = (
        df_BatchLogcsv.loc[:, "id_sample_in_batch"].astype(int) - 1
    ).astype(str)
    df_BatchLogcsv.loc[:, "level"] = df_BatchLogcsv.loc[:, "level"].str.replace(
        "Level ", ""
    )
    df_BatchLogcsv.loc[:, "ISTD_level"] = df_BatchLogcsv.loc[
        :, "ISTD_level"
    ].str.replace("Level ", "")
    df_BatchLogcsv = df_BatchLogcsv.replace("-", None)  # replace '-' values with None

    # if any() df_BatchLogcsv.'Acquisition Result' != 'Pass':
    #    what is the result? Stopped?

    # df_BatchLogcsv#.loc[:, 'File Name'].iloc[0]

    for index, row in df_BatchLogcsv.iterrows():
        # print(Path(row.file_name_rawdata).name)

        if row.file_path_rawdata is None:
            print("\x1b[31m", "File path of rawdata not found", "\x1b[0m")
            display(row)
        AcqDataMSTS = read_xml(
            path_to_files / Path(row.file_path_rawdata).name / r"AcqData/MSTS.xml"
        )
        df_BatchLogcsv.loc[index, "num_of_scans"] = to_str_or_none(
            AcqDataMSTS.TimeSegments.NumOfScans
        )
    return df_BatchLogcsv


def read_AcqMethod(path_to_files):
    print("read ../Method/AcqMethod.xml")
    AcqMethod = read_xml(path_to_files / r"Method/AcqMethod.xml")

    # CalibrationLevel
    # Another place fo rth ecalibration level --> this is probably changed when batch method is adjusted afterwards.
    # In contrast to BatchLog.csv
    # AcqMethod.find_all('SampleParameter')[1].CalibrationLevel.string
    samples_parameters = {}
    for sample in AcqMethod.find_all("SampleParameter"):
        column_rename_dict = {
            "id_sample_in_batch": "SampleID",
            "name_sample": "SampleName",
            "DataFileName": "DataFileName",
            "type_experiment": "SampleType",
            "level": "CalibrationLevel",
            "ISTD_level": "ISTDConcLevel",
            "t_duration_planned__s": "CompositeAcquisitionTime",
        }
        sample_parameters = {}
        for key, value in column_rename_dict.items():
            if sample.find(value) is not None:
                sample_parameters[key] = to_str_or_none(sample.find(value))
            elif value == "CalibrationLevel" and sample.SampleType.string == "Sample":
                sample_parameters[
                    key
                ] = None  # for sample measurements, concentration of analyte is unknown
            else:
                sample_parameters[key] = None
                print(
                    "\x1b[31m",
                    "For",
                    str(to_str_or_none(sample.SampleName)),
                    value,
                    "not found in SampleParameters of AcqMethod. Unfortunately you cannot update.\n",
                    "Use the old insertion routine and "
                    "use a correct Batch template next timew ith a complete SampleList.",
                    "\x1b[0m",
                )
                # sys.exit()
        samples_parameters[int(sample.SampleID.string)] = sample_parameters

    # print(pd.DataFrame(samples_parameters).transpose())
    df_sample_list = pd.DataFrame(samples_parameters).transpose()

    # Tuning parameters

    # Check whether in first or second IcpmsOptimize
    icpms_optimize = AcqMethod.find_all("IcpmsOptimize")[
        1
    ]  # AcqMethod.find_all('IcpmsOptimize')[0]

    # print('Collision gas: ', icpms_optimize.Opt_Cell_UseGas.string)
    if str(to_str_or_none(icpms_optimize.Opt_Cell_UseGas)) == "true":
        print(
            "He ",
            str(to_str_or_none(icpms_optimize.Opt_Cell_HeFlow)),
            ", H2 ",
            str(to_str_or_none(icpms_optimize.Opt_Cell_H2Flow)),
        )
        if (
            icpms_optimize.Opt_Cell_HeFlow.string != "0"
            and icpms_optimize.Opt_Cell_H2Flow.string != "0"
        ):
            warnings.warn("Database only ready for one collision gas")
        elif str(to_str_or_none(icpms_optimize.Opt_Cell_HeFlow)) != "0":
            df_sample_list.loc[:, "name_gas_collision"] = "He"
            df_sample_list.loc[:, "flow_rate_collision__mL_min"] = to_str_or_none(
                icpms_optimize.Opt_Cell_HeFlow
            )
        elif str(to_str_or_none(icpms_optimize.Opt_Cell_H2Flow)) != "0":
            df_sample_list.loc[:, "name_gas_collision"] = "H2"
            df_sample_list.loc[:, "flow_rate_collision__mL_min"] = to_str_or_none(
                icpms_optimize.Opt_Cell_H2Flow
            )
        else:
            warnings.warn("Use gas activated but no gas flowrate > 0")
    else:
        df_sample_list.loc[:, "name_gas_collision"] = None
        df_sample_list.loc[:, "flow_rate_collision__mL_min"] = None

    # print('PlasmaMode: ', icpms_optimize.OptimizationPlasmaMode.string)
    df_sample_list.loc[:, "plasma_mode"] = to_str_or_none(
        icpms_optimize.OptimizationPlasmaMode
    )

    # if icpms_optimize.OptimizationPlasmaMode.string == 'HMI':
    df_sample_list.loc[:, "gas_dilution_factor"] = to_str_or_none(
        icpms_optimize.Opt_Plasma_MakeupDilutionGas
    )
    # else:
    #    df_sample_list.loc[:, 'gas_dilution_factor'] = 0

    # print('TuneMode: ', AcqMethod.find_all('TuneStep')[1].TuneModeName.string)
    df_sample_list.loc[:, "tune_mode"] = to_str_or_none(
        AcqMethod.find_all("TuneStep")[1].TuneModeName
    )

    icpms_elements = []
    for IcpmsElement in AcqMethod.find_all("IcpmsElement"):
        # print(IcpmsElement.ElementName.string + IcpmsElement.MZ.string, IcpmsElement.ISTDFlag.string,
        #      IcpmsElement.IntegrationTime.string)
        icpms_elements.append(
            [
                to_str_or_none(IcpmsElement.ElementName)
                + to_str_or_none(IcpmsElement.MZ),
                to_str_or_none(IcpmsElement.ElementName),
                to_str_or_none(IcpmsElement.MZ),
                to_str_or_none(IcpmsElement.ISTDFlag),
                to_str_or_none(IcpmsElement.IntegrationTime),
            ]
        )
    df_icpms_elements = pd.DataFrame(
        icpms_elements,
        columns=[
            "name_isotope",
            "name_element",
            "isotope_mz",
            "is_internalstandard",
            "t_integration__s",
        ],
    )
    # display(df_icpms_elements)

    return df_sample_list, df_icpms_elements


def join_BatchLogcsv_AcqMethod(df_BatchLogcsv, df_sample_list):
    # display(df_BatchLogcsv)
    # display(df_sample_list)
    # Check for differences
    try:
        df_differences = (
            df_BatchLogcsv.loc[
                :,
                [
                    "id_sample_in_batch",
                    "name_sample",
                    "type_experiment",
                    "level",
                    "ISTD_level",
                ],
            ]
            .sort_values(by="id_sample_in_batch")
            .set_index("id_sample_in_batch")
            .compare(
                df_sample_list.loc[
                    :,
                    [
                        "id_sample_in_batch",
                        "name_sample",
                        "type_experiment",
                        "level",
                        "ISTD_level",
                    ],
                ]
                .sort_values(by="id_sample_in_batch")
                .set_index("id_sample_in_batch"),
                result_names=("BatchLog.csv", "AcqMethod.xml"),
            )
        )
    except ValueError as error:
        display(df_BatchLogcsv)
        display(df_sample_list)
        sys.exit(
            "BatchLog.csv and AcqMethod.xml do not match. Did you added/deleted lines in the Sample List? Please don't!"
        )

    if not df_differences.empty:
        display(df_differences)
        for index, changed_sample in df_differences.iterrows():
            for index, changed_col in changed_sample.unstack(level=1).iterrows():
                # display(changed_col)
                if changed_col.notna().values.any():
                    print(
                        "\x1b[33m",
                        # 'For', sample.SampleName.string,
                        index,
                        "updated during measurement.",  # BatchLog.csv != AcqMethod.xml values:
                        changed_col["AcqMethod.xml"],
                        "-->",
                        changed_col["BatchLog.csv"],
                        ". \n   The updated value",
                        changed_col["BatchLog.csv"],
                        " (from AcqMethod.xml) will be inserted into database."
                        "\x1b[0m",
                    )
    df_sample_list.drop(columns="DataFileName", inplace=True)
    df_BatchLogcsv = df_BatchLogcsv.join(
        df_sample_list.set_index("id_sample_in_batch"),
        on="id_sample_in_batch",
        rsuffix="_AcqMethod",
    ).rename(columns={"type_experiment": "type_experiment_Batchlog"})
    # rename type_experiment according to database
    df_BatchLogcsv.loc[:, "type_experiment"] = df_BatchLogcsv.loc[
        :, "type_experiment_AcqMethod"
    ].replace({"CalStd": "calibration", "Sample": "sfc-icpms"})
    # Check restrictions for c_analyte__mug_L with type_experiment
    for index, row in df_BatchLogcsv.loc[
        (df_BatchLogcsv.loc[:, "type_experiment"] != "calibration")
        & (df_BatchLogcsv.loc[:, "level"].notna()),
        :,
    ].iterrows():
        print(
            "\x1b[31m",
            "For the sample",
            row.name_sample,
            "a calibration Level is given but it is not set as a CalStd experiment. \n ",
            " Use the old insertion routine and use a correct Batch template next time.\n"
            "Therefore, adjust either: Level --> None (for sample experiments)  "
            "or SampleType --> CalStd (for calibration experiments) in Sample List."
            "\x1b[0m",
        )
    # display(df_BatchLogcsv)
    return df_BatchLogcsv


def read_DAMethod(path_to_files):
    print("read ../Method/DAMethod.batch.xml")
    CalibrationInfo = read_xml(path_to_files / r"Method/DAMethod.batch.xml")

    calibLevelConc = []
    for CalibLevel in CalibrationInfo.find_all("Calibration"):
        if CalibLevel.find("LevelConcentration") is not None:
            calibLevelConc.append(
                [
                    to_str_or_none(CalibLevel.LevelID),
                    to_str_or_none(CalibLevel.LevelName),
                    to_str_or_none(CalibLevel.LevelConcentration),
                    to_str_or_none(CalibLevel.CompoundID),
                ]
            )
            # print(CalibLevel.LevelID.string, CalibLevel.LevelName.string,
            #       CalibLevel.LevelConcentration.string, CalibLevel.CompoundID.string)
    df_calib_Level_conc = pd.DataFrame(
        calibLevelConc,
        columns=["LevelID", "LevelName", "LevelConcentration", "CompoundID"],
    )
    # print(df_calibLevelConcCoumpound)

    compounds = {}
    for TargetCompound in CalibrationInfo.find_all("TargetCompound"):
        column_rename_dict = {
            "CompoundID": "CompoundID",
            "CompoundName": "CompoundName",
            "MZ": "MZ",
            "ISTDFlag": "ISTDFlag",
            "CompoundType": "CompoundType",
            # 'SQResultUnit':'SQResultUnit',
            "ISTDMZ": "ISTDMZ",
            "ConcentrationUnits": "ConcentrationUnits",
        }

        compound_parameters = {}
        for key, value in column_rename_dict.items():
            if TargetCompound.find(value) is not None:
                compound_parameters[key] = to_str_or_none(TargetCompound.find(value))
            else:
                print(
                    "\x1b[31m",
                    "For",
                    str(to_str_or_none(TargetCompound.CompoundName)),
                    value,
                    "not found in TargetCompounds in DAMethod.batch.xml.",
                    "\x1b[0m",
                )
                if key == "ConcentrationUnits":
                    if user_input(
                        text="Did you use UgL?\n",
                        dtype="bool",
                    ):
                        compound_parameters[key] = "UgL"
                    else:
                        raise Exception("Other units are not supported yet.")
                else:
                    compound_parameters[key] = None
                    print(
                        "\x1b[31m",
                        "Use the old insertion routine and use a correct Batch template next time. ",
                        "(With a complete calibration table)",
                        "\x1b[0m",
                    )
                # sys.exit()
        # print(compound_parameters, TargetCompound.find('ConcentrationUnits'), TargetCompound )
        compounds[int(TargetCompound.CompoundID.string)] = compound_parameters
    # print(pd.DataFrame(samples_parameters).transpose())
    df_calib_icpms_elements = pd.DataFrame(compounds).transpose()
    df_calib_icpms_elements.loc[:, "name_isotope"] = df_calib_icpms_elements.loc[
        :, "CompoundName"
    ] + df_calib_icpms_elements.loc[:, "MZ"].astype(str)

    for index, row in df_calib_icpms_elements.loc[
        (df_calib_icpms_elements.ConcentrationUnits != "UgL"), :
    ].iterrows():
        if row.ISTDFlag == "true":
            update_table = "internal Standard table at bottom of calibration pane"
        else:
            update_table = "sample calibration table at top of calibration pane"
        print(
            "\x1b[31m",
            "For",
            row.CompoundName + str(row.MZ),
            "Concentration Unit is not set as UgL. It is assumed that values are given in UgL. \n",
            "If not use the old insertion routine with recalculated values.\n",
            "For next time, adjust concentrations in ",
            update_table,
            "\x1b[0m",
        )

    # display(df_calib_icpms_elements)
    # display(df_calib_Level_conc)
    return df_calib_Level_conc, df_calib_icpms_elements


def read_datacsv(path_to_files, exp_icpms):
    data_icpms_all_csv = pd.DataFrame()
    # print(exp_icpms)
    for index, row in exp_icpms.iterrows():
        file_path = Path(row.file_path_rawdata)
        # Check timestamps
        with open(file_path, "r") as f:
            file_lines = f.readlines()
            timestamp_csv = (
                file_lines[2].replace("Acquired      : ", "").split("using")[0].strip()
            )
        if row.t_start__timestamp_icpms_pc != timestamp_csv:
            exp_icpms.loc[index, "t_start__timestamp_icpms_pc"] = timestamp_csv
            display(exp_icpms)
            print(
                "\x1b[31m",
                "Timestamps for the start of the sample stored in different files do not match! ",
                "\n   from csv: ",
                timestamp_csv,
                "\n   from AcqData/sample_info.xml",
                row.t_start__timestamp_icpms_pc,
                "\n Timestamp from from csv will be used for further process. Please inform Nico!",
                "\x1b[0m",
            )

        print("read ../" + str(file_path.parent.name) + "/" + str(file_path.name))
        data_icpms_single_csv = (
            pd.read_csv(file_path, skiprows=3, skipfooter=1, engine="python")
            .dropna()
            .reset_index()
            .rename(columns={"index": "id_data_icpms", "Time [Sec]": "t__s"})
        )
        # .rename(columns={'Time [Sec]': 't__s'})\
        # .reset_index(names='id_data_icpms')
        data_icpms_single_csv.loc[:, "id_sample_in_batch"] = row.id_sample_in_batch
        data_icpms_single_csv = data_icpms_single_csv.set_index("id_sample_in_batch")
        data_icpms_all_csv = pd.concat([data_icpms_all_csv, data_icpms_single_csv])
        # print(len(data_icpms_single_csv.index))

        exp_icpms.loc[index, "t_duration__s"] = data_icpms_single_csv.loc[
            :, "t__s"
        ].max()
        # print(data_icpms_single_csv)
    # print(exp_icpms)
    return exp_icpms, data_icpms_all_csv


def restructure_dataicpms(data_icpms_all_csv, exp_icpms_analyte_internalstandard):
    # restructure to data_icpms with counts analyte and internalstandard sorted as in exp_icpms_analyte_internalstandard
    data_icpms = pd.DataFrame()
    for index, row in exp_icpms_analyte_internalstandard.iterrows():
        # if pd.isna(row.name_isotope_analyte) or pd.isna(row.name_isotope_internalstandard):
        #    print('Fail')
        #    continue
        # else:
        #    print(row.id_sample_in_batch, row.name_isotope_analyte, row.name_isotope_internalstandard)
        # if row.name_isotope_analyte
        data_icpms_single = data_icpms_all_csv.loc[
            row.id_sample_in_batch,
            [
                "id_data_icpms",
                "t__s",
                row["name_isotope_analyte"],
                row["name_isotope_internalstandard"],
            ],
        ].copy()
        # data_icpms_to_sql.loc[:, 'id_exp_icpms'] = id_exp_icpms
        data_icpms_single.loc[:, "name_isotope_analyte"] = row["name_isotope_analyte"]
        data_icpms_single.loc[:, "name_isotope_internalstandard"] = row[
            "name_isotope_internalstandard"
        ]
        data_icpms_single = (
            data_icpms_single.reset_index()
            .rename(
                columns={
                    row["name_isotope_analyte"]: "counts_analyte",
                    row["name_isotope_internalstandard"]: "counts_internalstandard",
                }
            )
            .set_index(
                [
                    "id_sample_in_batch",
                    "name_isotope_analyte",
                    "name_isotope_internalstandard",
                    "id_data_icpms",
                ]
            )
            .loc[:, ["t__s", "counts_analyte", "counts_internalstandard"]]
        )
        # display(data_icpms_single)
        data_icpms = pd.concat([data_icpms, data_icpms_single])

    return data_icpms


def check_Agilent_data_csv(file_path):
    with open(file_path, "r") as f:
        file_lines = f.readlines()

    # Check that csv file is data file
    if not (
        file_lines[2].split(" ")[0] == "Acquired"
        and r"D:\Agilent\ICPMH\1\DATA" in file_lines[0]
    ):
        print(
            "\x1b[31m",
            "I assume "
            + Path(file_path).name
            + " is not an ICP-MS data file but another .csv file. File will be skipped.",
            "\x1b[0m",
            "\n\n",
        )
        return False
    # Check correct export unit (Counts not CPS)
    if file_lines[1].split(",")[1].strip("\n") == "CPS":
        sys.exit(
            "HTE-Database stores only Counts not Counts per second (CPS) as given in the file, "
            "please adjust settings in Agilent MassHunter and reexport csv."
        )
    return True


def insert_icpms(
    path_to_files,
    manual_info={},
    auto_calibrate=True,
    device="PerkinElmer",
):
    """
    :param path_to_files: path of folder in which  icpms data files (*.xl ) are located
    :param manual_info: manual info which can be given as dict. user will be asked during procedure fo rmissing data
    :param auto_calibrate: True: calibration routine will be performed for each newly inserted calibration_set
    :param device: str on of ['PerkinElmer', 'Agilent']
        Will search for .xl or .csv files in the standard format of the corresponding device.
    :return:
    """
    print("You are using Version 20230204.")

    warnings.warn(
        "\nCurrently start time of the icpms measurement is not stored. \n\
        Instead the modification date of the file is used. \n\
        Be aware of not uploading the file again after manual modifying it. \n\
        Database constraints won't stop you from that"
    )

    # initialize calibration sets which should be calibrated after insertion
    id_exp_icpms_calibration_sets = []

    if device == "PerkinElmer":
        xl_files = sorted(
            glob.glob(str(path_to_files / "*.xl"))
        )  # not including subdirectories
        if len(xl_files) == 0:
            sys.exit("No files to be inserted found in the given path_to_files")
        print("Found", len(list(xl_files)), "files to be analysed")
        for file_path in xl_files:
            # if data_icpms.iloc[:, 1].max() < 5:  # condition to test that this column is actually a ratio
            #    warnings.warn('Values larger 5 found for the analyte to standard ratio.
            #    Be aware of that it should be <1')

            manual_info, id_exp_icpms_calibration_sets = _insert_single_datafile(
                file_path,
                manual_info,
                data_icpms=pd.read_csv(file_path, sep=",", header=1).rename(
                    columns={"Time in Seconds ": "t__s"}
                ),
                counts_analyte_as_ratio=True,
                id_exp_icpms_calibration_sets=id_exp_icpms_calibration_sets,
            )

    if device == "Agilent":
        csv_files = sorted(
            [
                file
                for path, subdir, files in os.walk(path_to_files)
                for file in glob.glob(os.path.join(path, "*.csv"))
            ]
        )  # including all subdirectories

        for file_path in csv_files:  # filter none Agilent data csv file
            if not check_Agilent_data_csv(file_path):
                csv_files.remove(file_path)

        if len(csv_files) == 0:
            sys.exit("No files to be inserted found in the given path_to_files")

        print("Found", len(list(csv_files)), "files to be analysed")
        for file_path in csv_files:
            manual_info, id_exp_icpms_calibration_sets = _insert_single_datafile(
                file_path,
                manual_info,
                data_icpms=pd.read_csv(file_path, skiprows=3, skipfooter=1)
                .dropna()
                .rename(columns={"Time [Sec]": "t__s"}),
                counts_analyte_as_ratio=False,
                id_exp_icpms_calibration_sets=id_exp_icpms_calibration_sets,
            )

    # Pretty print of manual_info
    print("Summary of manual set:")  # , str(manual_info).replace(',', ',\n'))
    count_tab = 0
    line_continuation = False
    for line in (
        str(manual_info)
        .replace(",", ",\n")
        .replace("{", "{\n")
        .replace("}", "\n}")
        .split("\n")
    ):
        if (line.count("'") % 2) == 1 or (line.count('"') % 2) == 1:
            line_continuation = not line_continuation
        if line_continuation:
            line = line + "\\"
        if "id_exp_icpms_calibration_set" in line:
            line = "#" + line
        print("     " * count_tab + line.strip())
        count_tab = count_tab + line.count("{") - line.count("}")
        # print(count_tab)

    # calibrate new 'id_exp_icpms_calibration_set'
    if auto_calibrate:
        icpms_calibration.calibrate(
            id_exp_icpms_calibration_set=id_exp_icpms_calibration_sets
        )
        return id_exp_icpms_calibration_sets


def _insert_single_datafile(
    file_path,
    manual_info,
    data_icpms,
    counts_analyte_as_ratio,  # PerkinElmer True, Agilent: False
    id_exp_icpms_calibration_sets,
):
    """
    Inserts a single icpms data file
    :param file_path: path of the file to be inserted
    :param manual_info: experimental parameters belonging to the datafile
    :param data_icpms: data file given as dataframe, time column must be called 't__s', element columns as Element+MZ
    :param counts_analyte_as_ratio: are analyte counts given as ratio? Yes --> True, No --> False
    :return: manual_info, id_exp_icpms_calibration_sets
    """
    file = Path(file_path).name

    if not Path(file_path).is_file():
        sys.exit("File " + file_path.name + " not found")
    else:
        print("\x1b[32m", "Opening file: ", file, "\x1b[0m")

    engine = db.connect(user="hte_inserter_icpms", echo=False)
    with engine.begin() as conn:
        # initialize
        exp_icpms = pd.DataFrame()
        exp_icpms_analyte_internalstandard = pd.DataFrame()
        exp_icpms_sfc = pd.DataFrame()

        # os.path.getmtime(file_path) / os.path.getmtime(file_path)
        # --> creation and modification time see:
        # https://stackoverflow.com/questions/237079/how-do-i-get-file-creation-and-modification-date-times
        # getctime --> problem for cloud synced files
        # --> these will have the cloud creation time as creaton time, modification time stays the same
        exp_icpms.loc[0, "t_start__timestamp_icpms_pc"] = str(
            dt.datetime.fromtimestamp(os.path.getmtime(file_path)).replace(
                second=0, microsecond=0
            )
        )  # round down to minutes as this is not the experiment starting time but rather the file creation time!
        exp_icpms.loc[0, "t_duration__s"] = data_icpms.loc[:, "t__s"].max()
        exp_icpms.loc[
            0, "name_computer_inserted_data"
        ] = socket.gethostname()  # os.environ['COMPUTERNAME'] not working under linux
        exp_icpms.loc[0, "file_path_rawdata"] = str(os.path.abspath(file_path))
        exp_icpms.loc[0, "file_name_rawdata"] = str(file)
        exp_icpms.loc[0, "t_inserted_data__timestamp"] = dt.datetime.now()

        if "file_specific" not in manual_info.keys():
            manual_info["file_specific"] = {}

        exp_icpms, manual_info_file_specific = manually_add(
            parameters=[
                {"name": "type_experiment", "dtype": "enum", "enum_table": "exp_icpms"},
            ],
            preset=manual_info["file_specific"][file]
            if file in manual_info["file_specific"].keys()
            else {},
            write_to=exp_icpms,
            conn=conn,
            engine=engine,
        )
        manual_info["file_specific"][file] = manual_info_file_specific

        exp_icpms, manual_info_exp_icpms = manually_add(
            parameters=[
                {"name": "name_user", "fk_table_name": "users", "dtype": "fk"},
                {
                    "name": "name_setup_icpms",
                    "fk_table_name": "setups_icpms",
                    "dtype": "fk",
                },
                {"name": "gas_dilution_factor", "dtype": "float", "optional": True},
                {
                    "name": "name_gas_collision",
                    "fk_table_name": "gases",
                    "fk_name": "name_gas",
                    "dtype": "fk",
                    "optional": True,
                },
                {
                    "name": "flow_rate_collision__mL_min",
                    "dtype": "float",
                    "optional": True,
                },
                {
                    "name": "name_gas_reaction",
                    "fk_table_name": "gases",
                    "fk_name": "name_gas",
                    "dtype": "fk",
                    "optional": True,
                },
                {
                    "name": "flow_rate_reaction__mL_min",
                    "dtype": "float",
                    "optional": True,
                },
                {"name": "comment", "dtype": "str", "optional": True},
                # {'name': 'type_experiment', 'dtype': 'enum', 'enum_table': 'exp_icpms'},
                {
                    "name": "id_exp_icpms_calibration_set",
                    "fk_table_name": "exp_icpms_calibration_set",
                    "dtype": "fk",
                    "init_new_entry_in": "exp_icpms_calibration_set",
                    "auto_select_unique": True,
                },
            ],
            preset=manual_info["exp_icpms"]
            if "exp_icpms" in manual_info.keys()
            else {},
            write_to=exp_icpms,
            conn=conn,
            engine=engine,
        )
        manual_info["exp_icpms"] = manual_info_exp_icpms

        # print(exp_icpms )

        # analyte_internalstandard -

        manual_info["exp_icpms_analyte_internalstandard"] = (
            manual_info["exp_icpms_analyte_internalstandard"]
            if "exp_icpms_analyte_internalstandard" in manual_info.keys()
            else {}
        )

        manual_info["exp_icpms_analyte_internalstandard"]["no_a_is_pair"] = (
            user_input(
                text="How many analyte internal standard pairs has been measured?",
                dtype="int",
                int_min=1,
                optional=False,
                options=None,
            )
            if "no_a_is_pair" not in manual_info["exp_icpms_analyte_internalstandard"]
            else manual_info["exp_icpms_analyte_internalstandard"]["no_a_is_pair"]
        )
        no_a_is_pair = manual_info["exp_icpms_analyte_internalstandard"]["no_a_is_pair"]
        for id_a_is_pair in range(0, no_a_is_pair):
            print(
                "\n Information for analyte standard pair ",
                id_a_is_pair,
                ": ",
                manual_info["exp_icpms_analyte_internalstandard"][id_a_is_pair][
                    "name_isotope_analyte"
                ]
                + "(x µg/L) / "
                + manual_info["exp_icpms_analyte_internalstandard"][id_a_is_pair][
                    "name_isotope_internalstandard"
                ]
                + "("
                + str(
                    manual_info["exp_icpms_analyte_internalstandard"][id_a_is_pair][
                        "c_internalstandard__mug_L"
                    ]
                )
                + " µg/L)"
                if id_a_is_pair
                in manual_info["exp_icpms_analyte_internalstandard"].keys()
                else "",
            )
            # id_a_is_pair = 0  # only one pair can be inserted for now
            manual_info["exp_icpms_analyte_internalstandard"][id_a_is_pair] = (
                manual_info["exp_icpms_analyte_internalstandard"][id_a_is_pair]
                if id_a_is_pair
                in manual_info["exp_icpms_analyte_internalstandard"].keys()
                else {}
            )

            exp_icpms_analyte_internalstandard_single_row = pd.DataFrame()
            exp_icpms_analyte_internalstandard_single_row.loc[
                id_a_is_pair, "type_experiment"
            ] = exp_icpms.loc[
                0, "type_experiment"
            ]  # copy paste
            exp_icpms_analyte_internalstandard_single_row.loc[
                id_a_is_pair, "id_exp_icpms_calibration_set"
            ] = exp_icpms.loc[
                0, "id_exp_icpms_calibration_set"
            ]  # copy paste
            # if exp_icpms.loc[0, 'type_experiment'] != 'calibration':
            #    manual_info['exp_icpms_analyte_internalstandard'][id_a_is_pair]['c_analyte__mug_L'] = None
            #    #for none caibration experiments this concentration must be NULL
            # if exp_icpms.loc[0, 'type_experiment'] == 'calibration'
            # and 'c_analyte__mug_L' in manual_info['exp_icpms_analyte_internalstandard'][id_a_is_pair].keys():
            #    del manual_info['exp_icpms_analyte_internalstandard'][id_a_is_pair]['c_analyte__mug_L']
            #    #for calibration experiments the concentration must be given
            (
                exp_icpms_analyte_internalstandard_single_row,
                manual_info_exp_icpms_analyte_internalstandard,
            ) = manually_add(
                parameters=[
                    {
                        "name": "name_isotope_internalstandard",
                        "fk_table_name": "isotopes",
                        "fk_name": "name_isotope",
                        "dtype": "fk",
                    },
                    {
                        "name": "name_isotope_analyte",
                        "fk_table_name": "isotopes",
                        "fk_name": "name_isotope",
                        "dtype": "fk",
                    },
                    # {'name': 'c_analyte__mug_L', 'dtype': 'float', 'optional': False},
                    {"name": "c_internalstandard__mug_L", "dtype": "float"},
                ],
                preset=manual_info["exp_icpms_analyte_internalstandard"][
                    id_a_is_pair
                ],  # if 'exp_icpms_analyte_internalstandard' in manual_info.keys() else {},
                write_to=exp_icpms_analyte_internalstandard_single_row,
                conn=conn,
                engine=engine,
                row_selector=id_a_is_pair,
            )
            manual_info["exp_icpms_analyte_internalstandard"][
                id_a_is_pair
            ] = manual_info_exp_icpms_analyte_internalstandard

            if exp_icpms.loc[0, "type_experiment"] != "calibration":
                if file in manual_info_exp_icpms_analyte_internalstandard.keys():
                    if (
                        "c_analyte__mug_L"
                        in manual_info_exp_icpms_analyte_internalstandard[file].keys()
                    ):
                        if (
                            manual_info_exp_icpms_analyte_internalstandard[file][
                                "c_analyte__mug_L"
                            ]
                            is not None
                        ):
                            warnings.warn(
                                "None-calibration files cannot have a known analyte concentration "
                                "your manual_info is wrong. Value for c_analyte wille be replaced by None"
                            )
                manual_info["file_specific"][file][id_a_is_pair] = {
                    "c_analyte__mug_L": None
                }  # for none caibration experiments this concentration must be NULL

            (
                exp_icpms_analyte_internalstandard_single_row,
                manual_info_file_specific_analyte_internalstandard,
            ) = manually_add(
                parameters=[
                    {"name": "c_analyte__mug_L", "dtype": "float", "optional": False},
                ],
                preset=manual_info["file_specific"][file][id_a_is_pair]
                if id_a_is_pair in manual_info["file_specific"][file].keys()
                else {},
                write_to=exp_icpms_analyte_internalstandard_single_row,
                conn=conn,
                engine=engine,
                row_selector=id_a_is_pair,
            )
            manual_info["file_specific"][file][
                id_a_is_pair
            ] = manual_info_file_specific_analyte_internalstandard

            # print(exp_icpms_analyte_internalstandard.empty, pd.concat([exp_icpms_analyte_internalstandard,
            # exp_icpms_analyte_internalstandard_single_row]))
            exp_icpms_analyte_internalstandard = pd.concat(
                [
                    exp_icpms_analyte_internalstandard,
                    exp_icpms_analyte_internalstandard_single_row,
                ]
            )  # if not exp_icpms_analyte_internalstandard.empty else exp_icpms_analyte_internalstandard_single_row
            # print(exp_icpms_analyte_internalstandard)
            print("\tCompleted\n")

        if exp_icpms.loc[0, "type_experiment"] == "sfc-icpms":
            # manual_info_exp_icpms_sfc = manual_info['exp_icpms_sfc'] if 'exp_icpms_sfc' in manual_info.keys() else {}
            print("SFC-ICPMS specific information")
            exp_icpms_sfc, manual_info_exp_icpms_sfc_file = manually_add(
                parameters=[
                    {
                        "name": "t_start__timestamp_sfc_pc",
                        "dtype": "timestamp",
                        "optional": False,
                    },
                    {"name": "t_delay__s", "dtype": "float", "optional": True},
                    {
                        "name": "name_setup_sfc",
                        "dtype": "fk",
                        "fk_table_name": "setups_sfc",
                        "optional": False,
                    },
                    {
                        "name": "flow_rate_real__mul_min",
                        "dtype": "float",
                        "optional": True,
                    },
                ],
                preset=manual_info["file_specific"][
                    file
                ],  # if file in manual_info_exp_icpms_sfc.keys() else {},# is initialized before by type_experiment
                write_to=exp_icpms_sfc,
                conn=conn,
                engine=engine,
                row_selector=0,
            )

            manual_info["file_specific"][file] = manual_info_exp_icpms_sfc_file
            print("Completed\n")

        # write into db
        db.call_procedure(engine, "Reset_Autoincrement", ["exp_icpms", "id_exp_icpms"])

        # exp_icpms
        try:
            id_exp_icpms = db.insert_into(
                conn, "exp_icpms", exp_icpms
            ).inserted_primary_key[0]
        except sql.exc.IntegrityError as error:
            print(str(error.orig), type(error.orig))
            if "Duplicate entry" in str(error.orig) and "UNIQUE" in str(error.orig):
                warnings.warn(
                    "\nFile "
                    + file
                    + " is already added to db and will be skipped. "
                      "\nIf this is not intended check uniqueness of couple:"
                      " \n name_setup_icpms, t_start__timestamp_icpms_pc, file_name_rawdata"
                )
                return manual_info, id_exp_icpms_calibration_sets
            else:
                warnings.warn(error.orig)
                sys.exit("Duplicate entry")

        # exp_icpms_analyte_internalstandard
        exp_icpms_analyte_internalstandard.loc[:, "id_exp_icpms"] = id_exp_icpms
        exp_icpms_analyte_internalstandard.set_index(
            ["id_exp_icpms", "name_isotope_analyte", "name_isotope_internalstandard"]
        ).to_sql("exp_icpms_analyte_internalstandard", con=conn, if_exists="append")

        # exp_icpms_sfc
        if exp_icpms.loc[0, "type_experiment"] == "sfc-icpms":
            exp_icpms_sfc.loc[:, "id_exp_icpms"] = id_exp_icpms
            exp_icpms_sfc.set_index(["id_exp_icpms"]).to_sql(
                "exp_icpms_sfc", con=conn, if_exists="append"
            )

        # data_icpms
        for index, row in exp_icpms_analyte_internalstandard.iterrows():
            data_icpms_to_sql = data_icpms.loc[
                :,
                [
                    "t__s",
                    row["name_isotope_analyte"],
                    row["name_isotope_internalstandard"],
                ],
            ].copy()
            data_icpms_to_sql.loc[:, "id_exp_icpms"] = id_exp_icpms
            data_icpms_to_sql.loc[:, "name_isotope_analyte"] = row[
                "name_isotope_analyte"
            ]
            data_icpms_to_sql.loc[:, "name_isotope_internalstandard"] = row[
                "name_isotope_internalstandard"
            ]
            if counts_analyte_as_ratio:
                data_icpms_to_sql.loc[:, row["name_isotope_analyte"]] = (
                    data_icpms_to_sql.loc[:, row["name_isotope_analyte"]]
                    * data_icpms_to_sql.loc[:, row["name_isotope_internalstandard"]]
                )  # recalculate actual counts of analyte rather than ratio
            data_icpms_to_sql.reset_index().rename(
                columns={
                    "index": "id_data_icpms",
                    row["name_isotope_analyte"]: "counts_analyte",
                    row["name_isotope_internalstandard"]: "counts_internalstandard",
                }
            ).set_index(
                [
                    "id_exp_icpms",
                    "name_isotope_analyte",
                    "name_isotope_internalstandard",
                ]
            ).to_sql(
                "data_icpms", con=conn, if_exists="append", chunksize=1000
            )
        print(
            "\x1b[32m",
            "Successfully inserted data belonging to ",
            file,
            "\x1b[0m",
            "\n\n",
        )

    # add new 'id_exp_icpms_calibration_set' to id_exp_icpms_calibration_sets
    if (
        exp_icpms.loc[0, "id_exp_icpms_calibration_set"]
        not in id_exp_icpms_calibration_sets
    ):
        id_exp_icpms_calibration_sets = id_exp_icpms_calibration_sets + [
            int(exp_icpms.loc[0, "id_exp_icpms_calibration_set"])
        ]

    return (
        manual_info,
        id_exp_icpms_calibration_sets,
    )  # if thsi is change, change return statement when duplicate entry is detected (few lines above)
