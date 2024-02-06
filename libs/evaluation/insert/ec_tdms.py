"""
Scripts for the insertion of electrochemical data from LabView software eCat
Created in 2023
@author: Forschungszentrum Jülich GmbH, Nico Röttcher
"""

from nptdms import TdmsFile  # to read out tdms files
import arrow
import pandas as pd
import numpy as np

from pathlib import Path, WindowsPath  # file paths
import sqlalchemy as sql

import warnings
import sys
import datetime
import copy

# git-synced modules
from evaluation.utils import user_input
from evaluation.utils import db

# constraints
constraints = {
    "EC_techniques": np.array(
        [
            {
                "name_HTE_db": "exp_ec_cv",
                "id_control_mode": 1,
                "name_jonas": "CV",
                "cols": [
                    {"name_HTE_db": "E_initial__VvsRE", "name_jonas": "Initial"},
                    {"name_HTE_db": "E_apex1__VvsRE", "name_jonas": "Initial"},
                    {"name_HTE_db": "E_apex2__VvsRE", "name_jonas": "Final"},
                    {"name_HTE_db": "E_final__VvsRE", "name_jonas": "Initial"},
                    {"name_HTE_db": "scanrate__mV_s", "name_jonas": "Scan Rate"},
                    {"name_HTE_db": "scanrate__mV_s", "name_jonas": "ScanRate"},
                    {"name_HTE_db": "stepsize__mV", "name_jonas": "Stepsize"},
                    {"name_HTE_db": "stepsize__mV", "name_jonas": "StepSize"},
                    {"name_HTE_db": "cycles", "name_jonas": "Cycles"},
                ],
            },
            {
                "name_HTE_db": "exp_ec_cv",
                "id_control_mode": 1,
                "name_jonas": "CV advanced",
                "cols": [
                    {"name_HTE_db": "E_initial__VvsRE", "name_jonas": "Initial"},
                    {"name_HTE_db": "E_apex1__VvsRE", "name_jonas": "Apex1"},
                    {"name_HTE_db": "E_apex2__VvsRE", "name_jonas": "Apex2"},
                    {"name_HTE_db": "E_final__VvsRE", "name_jonas": "Final"},
                    {"name_HTE_db": "scanrate__mV_s", "name_jonas": "Scan Rate"},
                    {"name_HTE_db": "scanrate__mV_s", "name_jonas": "ScanRate"},
                    {"name_HTE_db": "stepsize__mV", "name_jonas": "Stepsize"},
                    {"name_HTE_db": "stepsize__mV", "name_jonas": "StepSize"},
                    {"name_HTE_db": "cycles", "name_jonas": "Cycles"},
                ],
            },
            {
                "name_HTE_db": "exp_ec_ramp",
                "id_control_mode": 1,
                "name_jonas": "Ramp",
                "cols": [
                    {"name_HTE_db": "E_initial__VvsRE", "name_jonas": "Initial"},
                    {"name_HTE_db": "E_final__VvsRE", "name_jonas": "Final"},
                    {"name_HTE_db": "scanrate__mV_s", "name_jonas": "Scan Rate"},
                    {"name_HTE_db": "scanrate__mV_s", "name_jonas": "ScanRate"},
                    {"name_HTE_db": "stepsize__mV", "name_jonas": "Stepsize"},
                    {"name_HTE_db": "stepsize__mV", "name_jonas": "StepSize"},
                    {"name_HTE_db": "cycles", "name_jonas": "Cycles"},
                ],
            },
            {
                "name_HTE_db": "exp_ec_ghold",
                "id_control_mode": 0,
                "name_jonas": "Hold",
                "cols": [
                    {"name_HTE_db": "I_hold__A", "name_jonas": "Hold"},
                    {"name_HTE_db": "t_hold__s", "name_jonas": "Time"},
                    {"name_HTE_db": "t_samplerate__s", "name_jonas": "Sample Rate"},
                    {"name_HTE_db": "t_samplerate__s", "name_jonas": "SampleRate"},
                ],
            },
            {
                "name_HTE_db": "exp_ec_phold",
                "id_control_mode": 1,
                "name_jonas": "Hold",
                "cols": [
                    {"name_HTE_db": "E_hold__VvsRE", "name_jonas": "Hold"},
                    {"name_HTE_db": "t_hold__s", "name_jonas": "Time"},
                    {"name_HTE_db": "t_samplerate__s", "name_jonas": "Sample Rate"},
                    {"name_HTE_db": "t_samplerate__s", "name_jonas": "SampleRate"},
                ],
            },
            {
                "name_HTE_db": "exp_ec_geis",
                "id_control_mode": 0,
                "name_jonas": "EIS",
                "cols": [
                    {"name_HTE_db": "f_initial__Hz", "name_jonas": "Initial"},
                    {"name_HTE_db": "f_final__Hz", "name_jonas": "Final"},
                    {"name_HTE_db": "I_dc__A", "name_jonas": "DC Offset"},
                    {"name_HTE_db": "I_amplitude__A", "name_jonas": "Amplitude"},
                    {
                        "name_HTE_db": "R_initialguess__ohm",
                        "name_jonas": "Initial Guess",
                    },
                    {
                        "name_HTE_db": "points_per_decade",
                        "name_jonas": "Pt. per Decade",
                    },
                ],
            },
            {
                "name_HTE_db": "exp_ec_peis",
                "id_control_mode": 1,
                "name_jonas": "EIS",
                "cols": [
                    {"name_HTE_db": "f_initial__Hz", "name_jonas": "Initial"},
                    {"name_HTE_db": "f_final__Hz", "name_jonas": "Final"},
                    {"name_HTE_db": "E_dc__VvsRE", "name_jonas": "DC Offset"},
                    {"name_HTE_db": "E_amplitude__VvsRE", "name_jonas": "Amplitude"},
                    {
                        "name_HTE_db": "R_initialguess__ohm",
                        "name_jonas": "Initial Guess",
                    },
                    {
                        "name_HTE_db": "points_per_decade",
                        "name_jonas": "Pt. per Decade",
                    },
                ],
            },
            {
                "name_HTE_db": "exp_ec_gpulse",
                "id_control_mode": 0,
                "name_jonas": "Pulse",
                "cols": [
                    {"name_HTE_db": "I_hold1__A", "name_jonas": "Hold1"},
                    {"name_HTE_db": "I_hold2__A", "name_jonas": "Hold2"},
                    {"name_HTE_db": "t_hold1__s", "name_jonas": "Time1"},
                    {"name_HTE_db": "t_hold2__s", "name_jonas": "Time2"},
                    {"name_HTE_db": "t_samplerate__s", "name_jonas": "SampleRate"},
                    {"name_HTE_db": "cycles", "name_jonas": "Cycles"},
                ],
            },
            {
                "name_HTE_db": "exp_ec_ppulse",
                "id_control_mode": 1,
                "name_jonas": "Pulse",
                "cols": [
                    {"name_HTE_db": "E_hold1__VvsRE", "name_jonas": "Hold1"},
                    {"name_HTE_db": "E_hold2__VvsRE", "name_jonas": "Hold2"},
                    {"name_HTE_db": "t_hold1__s", "name_jonas": "Time1"},
                    {"name_HTE_db": "t_hold2__s", "name_jonas": "Time2"},
                    {"name_HTE_db": "t_samplerate__s", "name_jonas": "SampleRate"},
                    {"name_HTE_db": "cycles", "name_jonas": "Cycles"},
                ],
            },
        ]
    ),
    "experiments_ec": [
        {"name_HTE_db": "name_device", "name_jonas": "Device"},
        {"name_HTE_db": "id_control_mode", "name_jonas": "Control Mode"},
        {"name_HTE_db": "id_ie_range", "name_jonas": "I/E Range"},
        {"name_HTE_db": "id_vch_range", "name_jonas": "Vch Range"},
        {"name_HTE_db": "id_ich_range", "name_jonas": "Ich Range"},
        {"name_HTE_db": "id_vch_filter", "name_jonas": "Vch Filter"},
        {"name_HTE_db": "id_ich_filter", "name_jonas": "Ich Filter"},
        {"name_HTE_db": "id_ca_speed", "name_jonas": "CA Speed"},
        {"name_HTE_db": "id_ie_stability", "name_jonas": "I/E Stability"},
        {"name_HTE_db": "id_sampling_mode", "name_jonas": "SamplingMode"},
        {"name_HTE_db": "ie_range_auto", "name_jonas": "IERangeAuto"},
        {"name_HTE_db": "vch_range_auto", "name_jonas": "VchRangeAuto"},
        {"name_HTE_db": "ich_range_auto", "name_jonas": "IchRangeAuto"},
        {"name_HTE_db": "ich_range_auto", "name_jonas": "IchRangeAuto"},
        {"name_HTE_db": "ich_range_auto", "name_jonas": "IchRangeAuto"},
        {"name_HTE_db": "ich_range_auto", "name_jonas": "IchRangeAuto"},
    ],
}


def read_tdms(file_path):
    """
    :param file_path: path of file including file extension (.tdms) which should be read data_ec, using pathlib
    :type file_path: str | pathlib.WindowsPath
    :return: data from tdms file, merged in one DataFrame
    :rtype: pd.DataFrame
    """
    if type(file_path) != WindowsPath:  # @Deniz would it be LinuxPath under linux?!
        file_path = Path(file_path)
    # handle tdms file
    t_0_file = datetime.datetime.now()
    print("\x1b[32m", "Opening ", file_path, "\x1b[0m")
    with TdmsFile.open(file_path) as tdms_file:
        data_ec = pd.DataFrame()  # initialize data_ec
        data_eis = pd.DataFrame()  # initialize data_ec
        tdms_init = tdms_file.properties

        for group in tdms_file.groups():
            df = group.as_dataframe()  # transform tdms datasheet to pandas DataFrame
            if (
                len(df.index) == 0
            ):  #  stopping execution before first datapoint is measured will create empty table
                continue  # skip empty tables
            df.loc[:, "data_ec_tablename"] = group.name  # attach column for measurement name
            # (necessary if all data should be returned in one DataFrame)

            df = df.reset_index().set_index(["data_ec_tablename", "index"])  # adjust index accordingly

            # apply Berlin timezone to timestammp columns (tdms just stores utc timestamps (London))
            for col in [
                index for index, value in df.dtypes.items() if value == "datetime64[ns]"
            ]:
                df.loc[:, col] = df.loc[:, col].apply(
                    lambda x: arrow.get(x).to("local").datetime
                )  # df.loc[:, col].dt.tz_localize(tz='Europe/London').dt.tz_convert(tz='Europe/Berlin')

            # rename columns
            df = df.rename(
                columns={
                    "Time (s)": "t__s",
                    "Current (A)": "I__A",
                    "Potential WE (V)": "E_WE_raw__VvsRE",
                    "Potential WE uncomp (V)": "Delta_E_WE_uncomp__V",
                    "Potential Signal (V)": "E_Signal__VvsRE",
                    "Frequency (Hz)": "f__Hz",
                    "Z real": "Z_real__ohm",
                    "-Z img": "minusZ_img__ohm",
                    "Vdc": "E_dc__VvsRE",
                    "Idc": "I_dc__A",
                    #'Timestamp': 'Timestamp',
                }
            )

            # Considering line skip for corrupted tdms files. here primitive cutting of first n lines as given by user
            if "EIS" not in group.name:
                if df.loc[:, "t__s"].iloc[0] > 10:
                    print(
                        "\x1b[31m",
                        "Tdms file technique "
                        + group.name
                        + " might be corrupted. As time of first data point > 10 s. "
                          "Check out the file and tell me how many lines to skip."
                        "\x1b[0m",
                        "\n\n",
                    )
                    display(df.t__s.iloc[:20])
                    df = df.iloc[
                        user_input.user_input(
                            text="How many lines to skip?",
                            dtype="int",
                        ):
                    ]
            # merge all into one pd DataFrame for EIS and for EC
            if "EIS" in group.name:
                data_eis = pd.concat([data_eis, df])
            else:
                data_ec = pd.concat([data_ec, df])

        t_1_file = datetime.datetime.now()
        print("tdms reading time: ", t_1_file - t_0_file, " s")
        print()
        return tdms_init, data_ec, data_eis


def read_infotxt(file_path):
    """
    :param file_path: path of file including file extension (.txt) which should be read out, using pathlib
    :type file_path: str | pathlib.WindowsPath
    :return: data from info file, structured for experiments_ec table and merged into a pd.DataFrame
    :rtype: pd.DataFrame
    """

    if not Path(file_path).is_file():
        warnings.warn("Info File not found")
        sys.exit(1)

    print("\x1b[32m", "Opening ", file_path, "\x1b[0m")
    with open(file_path, "r", encoding="ISO-8859-1") as info_file:
        header_lines = {}
        exp_ec_list = pd.DataFrame()  # np.array([])
        for id_line, line in enumerate(info_file.readlines()):
            # print(id_line, line[0])
            # Header lines
            if line[0] == "#" and ":" in line:
                sep_index = int(line.find(":"))
                header_name = line[1:sep_index]
                header_value = line[sep_index + 1 :].strip(" \t\n")
                header_lines[header_name] = header_value

                if header_name in ["Gamry iR compensation", "iR compensation"]:
                    header_lines["R_u__ohm"] = float(
                        header_value.split("\t")[0].strip(" Ohm")
                    )
                    header_lines["iR_corr_in_situ__percent"] = float(
                        header_value.split("\t")[2].strip(" %")
                    )
                    # print('Found iR-compensation values: ', header_lines['R_u__ohm'], ' ohms,  ',
                    # header_lines['iR_corr_in_situ__percent'], '%')

                    if (
                        header_lines["R_u__ohm"] == 0
                        or header_lines["iR_corr_in_situ__percent"] == 0
                    ):
                        header_lines["R_u__ohm"] = None
                        header_lines["iR_corr_in_situ__percent"] = None

            # Technique lines
            elif line[0] == "\t":
                cols = ["id_ML_technique"] + line.strip(" \t\n").split("\t")
                # col renaming
                # print(cols)
            elif line[0].isdigit():
                technique_dict = dict(zip(cols, line.strip(" \t\n").split("\t")))
                if technique_dict["Technique"] == "Settings":
                    settings = technique_dict.copy()
                    settings.pop("Technique")
                    settings.pop(
                        "id_ML_technique"
                    )  # in principle not necessary --> see comment when merge dicts
                    for key, val in settings.items():
                        if val == "FALSE":
                            settings[key] = "0"
                        elif val == "TRUE":
                            settings[key] = "1"
                    print(settings)
                # elif technique_dict['Technique'] == 'Gases': # and other handlers
                elif technique_dict["Technique"] in [
                    table["name_jonas"] for table in constraints["EC_techniques"]
                ]:
                    warnings.warn(
                        "Device of settings and technique are not the same"
                    ) if technique_dict["Device"] != settings["Device"] else ""

                    # insert into exp_ec
                    # ## rename columns from settings and write to new dict
                    exp_ec_dict = {
                        [
                            item["name_HTE_db"]
                            for item in constraints["experiments_ec"]
                            if item["name_jonas"] == entry[0]
                        ][0]: entry[1]
                        for entry in settings.items()
                    }
                    #   add additional exp_ec parameter

                    if (
                        file_path.name.lower()
                        != header_lines["Path to save file"].split("\\")[-1].lower()
                    ):
                        warnings.warn(
                            "File_name has been changed! "
                            "Please check the filename in the infofile and see that it does not correspond: "
                            + file_path.name
                            + ", "
                            + header_lines["Path to save file"].split("\\")[-1]
                        )
                        # sys.exit(1)
                    exp_ec_dict["id_ML"] = int(
                        str(file_path)[-7:-4]
                    )  # int(header_lines['Path to save file'][-7:-4])
                    exp_ec_dict["id_ML_technique"] = int(
                        technique_dict["id_ML_technique"]
                    )  # before it is str --> will ruine sorting by this column
                    exp_ec_dict["name_technique"] = [
                        table["name_HTE_db"]
                        for table in constraints["EC_techniques"]
                        if table["name_jonas"] == technique_dict["Technique"]
                        and table["id_control_mode"]
                        == int(exp_ec_dict["id_control_mode"])
                    ][0]
                    exp_ec_dict["rawdata_path"] = header_lines["Path to save file"]
                    exp_ec_dict["R_u__ohm"] = header_lines["R_u__ohm"]
                    exp_ec_dict["iR_corr_in_situ__percent"] = header_lines[
                        "iR_corr_in_situ__percent"
                    ]
                    exp_ec_dict["labview_sfc_version"] = (
                        header_lines["Version"].split(",")[0].split(" ")[-1]
                    )

                    # rename columns of ec_technique columns
                    # and place them as as dict into exp_ec with the technique name as key
                    colnames = pd.DataFrame(
                        [
                            table["cols"]
                            for table in constraints["EC_techniques"]
                            if table["name_HTE_db"] == exp_ec_dict["name_technique"]
                            and table["id_control_mode"]
                            == int(exp_ec_dict["id_control_mode"])
                        ][0]
                    )
                    print(technique_dict)
                    exp_ec_dict["exp_ec_technique_table"] = [
                        {
                            row.name_HTE_db: technique_dict[row.name_jonas]
                            for key, row in colnames.iterrows()
                            if row.name_jonas in technique_dict
                        }
                    ]
                    # sys.exit(1)
                    # construct  name of corresponding data table
                    exp_ec_dict["data_ec_tablename"] = (
                        technique_dict["Device"]
                        + "_"
                        + technique_dict["Technique"]
                        + "_ "
                        + technique_dict["id_ML_technique"]
                    )

                    exp_ec_list = pd.concat([exp_ec_list, pd.DataFrame(exp_ec_dict)])
                    # print(exp_ec_list)

                else:
                    warnings.warn(
                        'Found technique: "'
                        + technique_dict["Technique"]
                        + '", which is not implemented yet. '
                    )

                # print(pd.DataFrame.from_dict(techniques))

    print()
    return exp_ec_list.reset_index(drop=True)


def insert_ec_tdms(path_to_files, manual_info):
    """
    Inserts all tdms file in the given folder to MySQL database
    :param path_to_files: one tdms file or folder containing tdms files
    :type path_to_files: Pathlib.WindowsPath()
    :return:
    """
    print("You are using Version 20220124.")

    # Pretty print of manual_info
    def pretty_summary_print(manual_info):
        print("Summary of manual set:")
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
            print("     " * count_tab + line.strip())
            count_tab = count_tab + line.count("{") - line.count("}")

    t_0_read_folder = datetime.datetime.now()

    manual_info_initial = copy.copy(manual_info)

    tdms_files = (
        [path_to_files]
        if path_to_files.is_file() and path_to_files.suffix == ".tdms"
        else sorted(list(Path(path_to_files).glob("*.tdms")))
    )
    if len(tdms_files) == 0:
        sys.exit("No files to be inserted found in the given path_to_files")
    else:
        print("Found", len(tdms_files), "files to be analysed")

    for tdms_file in tdms_files:
        print()
        engine = db.connect(user="hte_inserter_ec", echo=False)
        if tdms_file.is_file():
            info_file = tdms_file.parent / (
                "Info_" + tdms_file.with_suffix(".txt").name
            )
            if not info_file.is_file():
                warnings.warn(
                    "\n No info file found for "
                    + tdms_file.name
                    + " \n File is skipped!"
                )
            else:

                # reading of info and corresponding tdms file
                exp_ec_list = read_infotxt(info_file)
                tdms_init, data_ec, data_eis = read_tdms(tdms_file)

                with engine.begin() as conn:  # connect to sql after file reading to avoid lost connection error
                    exp_ec_list.loc[:, "rawdata_computer"] = tdms_init[
                        "computer"
                    ]  # if 'computer' in tdms_init.keys() else 'unknown'

                    # exp_ec from data_ec (from eis there are no timestamps available yet)
                    if (
                        not data_ec.empty
                    ):  # only eis data --> data_ec is empty will throw error
                        t_start_timestamps = pd.Series(
                            data_ec.groupby(level=0).first().loc[:, "Timestamp"]
                            - pd.to_timedelta(
                                data_ec.groupby(level=0).first().loc[:, "t__s"],
                                unit="seconds",
                            ),
                            name="t_start__timestamp",
                        )
                        exp_ec_list = exp_ec_list.join(
                            t_start_timestamps, on="data_ec_tablename"
                        )
                        # display(data_ec.Timestamp)
                        # display(exp_ec_list.t_start__timestamp)

                    else:
                        exp_ec_list.loc[:, "t_start__timestamp"] = np.nan

                    # calculate dummy timestamp for eis
                    # won't disturb ICP-MS data matching, as t_end__timestamp is still undefined thus WHERE statement will remove geis/peis lines
                    date = info_file.name.split("_")[1]
                    timestamp = (
                        date[:4] + "-" + date[4:6] + "-" + date[6:] + " 00:00:00."
                    )
                    exp_ec_list.loc[
                        exp_ec_list.loc[:, "t_start__timestamp"].isna(),
                        "t_start__timestamp",
                    ] = [
                        timestamp
                        + "000"[len(str(row["id_ML"])) :]
                        + str(row["id_ML"])
                        + "000"[len(str(row["id_ML_technique"])) :]
                        + str(row["id_ML_technique"])
                        for index, row in exp_ec_list.loc[
                            exp_ec_list.loc[:, "t_start__timestamp"].isna(), :
                        ].iterrows()
                    ]

                    # Check if data is available for teh experiment otherwise assume the technique wasnt executed
                    executed_ec_techniques = (
                        data_ec.reset_index().loc[:, "data_ec_tablename"].unique()
                        if not data_ec.empty
                        else []
                    )
                    executed_eis_techniques = (
                        data_eis.reset_index().loc[:, "data_ec_tablename"].unique()
                        if not data_eis.empty
                        else []
                    )
                    exp_ec_list.loc[:, "executed"] = (
                        exp_ec_list.loc[:, "data_ec_tablename"]
                        .isin(
                            np.append(executed_ec_techniques, executed_eis_techniques)
                        )
                        .to_numpy()
                    )

                    # Remove unexecuted techniques
                    exp_ec_list = exp_ec_list.loc[
                        (exp_ec_list.loc[:, "executed"] == 1), :
                    ]
                    if exp_ec_list.empty:
                        warnings.warn(
                            "\nFile "
                            + tdms_file.name
                            + " does not contain any data. I suspect there are only unexecuted techniques in this ML."
                        )
                        continue

                    exp_ec_list, manual_info = user_input.manually_add(
                        parameters=[
                            {
                                "name": "name_user",
                                "fk_table_name": "users",
                                "dtype": "fk",
                            },
                            {
                                "name": "id_sample",
                                "fk_table_name": "samples",
                                "dtype": "fk",
                            },
                        ],
                        preset=manual_info,
                        write_to=exp_ec_list,
                        conn=conn,
                        engine=engine,
                    )

                    exp_ec_list, manual_info = user_input.manually_add(
                        parameters=[
                            {
                                "name": "id_spot",
                                "fk_table_name": "spots",
                                "dtype": "fk",
                                "fk_table_cond": "id_sample="
                                + str(manual_info["id_sample"]),
                            },
                            {
                                "name": "name_setup_sfc",
                                "fk_table_name": "setups_sfc",
                                "dtype": "fk",
                            },
                            {
                                "name": "name_RE",
                                "fk_table_name": "reference_electrodes",
                                "dtype": "fk",
                            },
                            {
                                "name": "name_CE",
                                "fk_table_name": "counter_electrodes",
                                "dtype": "fk",
                            },
                            {"name": "E_RE__VvsRHE", "dtype": "float"},
                            {"name": "force__N", "dtype": "float"},
                            {
                                "name": "T_stage__degC",
                                "dtype": "float",
                                "optional": True,
                            },
                            {"name": "comment", "dtype": "str", "optional": True},
                        ],
                        preset=manual_info,
                        write_to=exp_ec_list,
                        conn=conn,
                        engine=engine,
                    )

                    flow_cell_assemblies_list = pd.DataFrame()
                    enum_table = pd.Series(
                        conn.execute(
                            sql.text(
                                'SELECT SUBSTRING(COLUMN_TYPE,5) FROM information_schema.COLUMNS WHERE TABLE_NAME="'
                                + "flow_cell_assemblies"
                                + '" AND COLUMN_NAME="'
                                + "location"
                                + '";'
                            )
                        )
                        .first()[0]
                        .strip("()' ")
                        .split("','")
                    )
                    for index, value in enum_table.iteritems():  # 'top, bottom
                        key = "flow_cell" + "_" + value
                        if key not in manual_info.keys():
                            manual_info[key] = user_input.user_input(
                                text="Does setup include " + key + "? \n",
                                dtype="bool",
                                optional=False,
                            )
                            manual_info[key] = {} if manual_info[key] != 0 else False
                        if manual_info[key] != False:  # either True or dict
                            flow_cell_assemblies = exp_ec_list.drop(
                                columns=exp_ec_list.columns
                            )
                            flow_cell_assemblies.loc[:, "location"] = value
                            flow_cell_assemblies = (
                                flow_cell_assemblies.reset_index().set_index(
                                    ["index", "location"]
                                )
                            )
                            (
                                flow_cell_assemblies,
                                manual_info[key],
                            ) = user_input.manually_add(
                                parameters=[
                                    {
                                        "name": "name_flow_cell",
                                        "fk_table_name": "flow_cells",
                                        "dtype": "fk",
                                    },
                                    {
                                        "name": "id_sealing",
                                        "fk_table_name": "sealings",
                                        "dtype": "fk",
                                        "optional": True,
                                    },
                                    {
                                        "name": "id_PTL",
                                        "fk_table_name": "porous_transport_layers",
                                        "dtype": "fk",
                                        "optional": True,
                                    },
                                ],
                                preset=manual_info[key],
                                write_to=flow_cell_assemblies,
                                conn=conn,
                                engine=engine,
                            )
                            flow_cell_assemblies_list = pd.concat(
                                [flow_cell_assemblies_list, flow_cell_assemblies]
                            )
                            # print(manual_info[key])

                    electrolyte_flow_list = pd.DataFrame()
                    enum_table = pd.Series(
                        conn.execute(
                            sql.text(
                                'SELECT SUBSTRING(COLUMN_TYPE,5) FROM information_schema.COLUMNS WHERE TABLE_NAME="'
                                + "flow_electrolyte"
                                + '" AND COLUMN_NAME="'
                                + "location"
                                + '";'
                            )
                        )
                        .first()[0]
                        .strip("()' ")
                        .split("','")
                    )
                    for index, value in enum_table.iteritems():  #'top, bottom
                        key = "electrolyte" + "_" + value
                        if key not in manual_info.keys():
                            manual_info[key] = user_input.user_input(
                                text="Does setup include " + key + "? \n",
                                dtype="bool",
                                optional=False,
                            )
                            manual_info[key] = {} if manual_info[key] != 0 else False
                        if manual_info[key] != False:  # either True or dict
                            electrolyte_flow = exp_ec_list.drop(
                                columns=exp_ec_list.columns
                            )
                            electrolyte_flow.loc[:, "location"] = value
                            electrolyte_flow = electrolyte_flow.reset_index().set_index(
                                ["index", "location"]
                            )
                            (
                                electrolyte_flow,
                                manual_info[key],
                            ) = user_input.manually_add(
                                parameters=[
                                    {
                                        "name": "id_pump_in",
                                        "fk_name": "id_pump",
                                        "fk_table_name": "peristaltic_pumps",
                                        "dtype": "fk",
                                    },
                                    {
                                        "name": "id_tubing_in",
                                        "fk_name": "id_tubing",
                                        "fk_table_name": "peristaltic_tubings",
                                        "dtype": "fk",
                                    },
                                    {
                                        "name": "pump_rate_in__rpm",
                                        "dtype": "float",
                                        "optional": True,
                                    },
                                    {
                                        "name": "id_pump_out",
                                        "fk_name": "id_pump",
                                        "fk_table_name": "peristaltic_pumps",
                                        "dtype": "fk",
                                    },
                                    {
                                        "name": "id_tubing_out",
                                        "fk_name": "id_tubing",
                                        "fk_table_name": "peristaltic_tubings",
                                        "dtype": "fk",
                                    },
                                    {
                                        "name": "pump_rate_out__rpm",
                                        "dtype": "float",
                                        "optional": True,
                                    },
                                    {
                                        "name": "flow_rate_real__mul_min",
                                        "dtype": "float",
                                        "optional": True,
                                    },
                                    {
                                        "name": "name_electrolyte",
                                        "fk_table_name": "electrolytes",
                                        "dtype": "fk",
                                    },
                                    {"name": "c_electrolyte__mol_L", "dtype": "float"},
                                ],
                                preset=manual_info[key],
                                write_to=electrolyte_flow,
                                conn=conn,
                                engine=engine,
                            )
                            electrolyte_flow_list = pd.concat(
                                [electrolyte_flow_list, electrolyte_flow]
                            )
                            # print(manual_info[key])

                    gas_flow_list = pd.DataFrame()
                    enum_table_location = pd.Series(
                        conn.execute(
                            sql.text(
                                'SELECT SUBSTRING(COLUMN_TYPE,5) FROM information_schema.COLUMNS WHERE TABLE_NAME="'
                                + "flow_gas"
                                + '" AND COLUMN_NAME="'
                                + "location"
                                + '";'
                            )
                        )
                        .first()[0]
                        .strip("()' ")
                        .split("','"),
                        name="location",
                    )
                    enum_table_function = pd.Series(
                        conn.execute(
                            sql.text(
                                'SELECT SUBSTRING(COLUMN_TYPE,5) FROM information_schema.COLUMNS WHERE TABLE_NAME="'
                                + "flow_gas"
                                + '" AND COLUMN_NAME="'
                                + "function"
                                + '";'
                            )
                        )
                        .first()[0]
                        .strip("()' ")
                        .split("','"),
                        name="function",
                    )
                    enum_table = pd.merge(
                        enum_table_location, enum_table_function, how="cross"
                    )

                    for index, row in enum_table.iterrows():
                        key = "gas" + "_" + row["location"] + "_" + row["function"]
                        if key not in manual_info.keys():
                            manual_info[key] = user_input.user_input(
                                text="Does setup include " + key + "? \n",
                                dtype="bool",
                                optional=False,
                            )
                            manual_info[key] = {} if manual_info[key] != 0 else False
                        if manual_info[key] != False:  # either True or dict
                            gas_flow = exp_ec_list.drop(columns=exp_ec_list.columns)
                            gas_flow.loc[:, "location"] = row["location"]
                            gas_flow.loc[:, "function"] = row["function"]
                            gas_flow = gas_flow.reset_index().set_index(
                                ["index", "location", "function"]
                            )
                            gas_flow, manual_info[key] = user_input.manually_add(
                                parameters=[
                                    {
                                        "name": "name_gas",
                                        "fk_table_name": "gases",
                                        "dtype": "fk",
                                    },
                                    {
                                        "name": "flow_rate__ml_min",
                                        "dtype": "float",
                                        "optional": True,
                                    },
                                ],
                                preset=manual_info[key],
                                write_to=gas_flow,
                                conn=conn,
                                engine=engine,
                            )
                            gas_flow_list = pd.concat([gas_flow_list, gas_flow])
                    # print('Summary of manual set: \n', manual_info)

                    if "use_for_whole_dataset" not in manual_info.keys():
                        pretty_summary_print(manual_info)
                        manual_info["use_for_whole_dataset"] = user_input.user_input(
                            text="Use this infos for the whole dataset?\n",
                            dtype="bool",
                            optional=False,
                        )
                    if not manual_info["use_for_whole_dataset"]:
                        manual_info_initial["use_for_whole_dataset"] = manual_info[
                            "use_for_whole_dataset"
                        ]
                        manual_info = copy.copy(manual_info_initial)  # {}

                # print(manual_info)

                # write into db #.connect()
                with engine.begin() as conn:  # new connection once all files are read

                    # Reset exp_ec Auto increment
                    db.call_procedure(
                        engine, "Reset_Autoincrement", ["exp_sfc", "id_exp_sfc"]
                    )
                    # Lock Tables to avoid simultaneous insertions from multiple PC
                    # conn.execute(sql.text("LOCK TABLES exp_ec WRITE, exp_ec_cv WRITE, exp_ec_geis WRITE,
                    # exp_ec_ghold WRITE, exp_ec_peis WRITE, exp_ec_phold WRITE, exp_ec_ramp WRITE, data_ec WRITE,
                    # data_eis WRITE, flow_cell_assemblies WRITE, flow_electrolyte WRITE, flow_gas WRITE;"))
                    # Lock tables to avoid simultaneous insertion

                    if any(
                        exp_ec_list.loc[:, "id_ML_technique"]
                        != exp_ec_list.sort_values(by=["id_ML_technique"])
                        .reset_index()
                        .loc[:, "id_ML_technique"]
                    ):  # Check if order is still alright otherwise need to be implemented .sort_values(by=['id_ML_technique'])
                        warnings.warn(
                            "\n Error, exp_ec_list not sorted according id_ML_technique!"
                        )
                        sys.exit()

                    exp_sfc_list_to_sql = exp_ec_list.drop(
                        columns=[
                            "exp_ec_technique_table",
                            "data_ec_tablename",
                            "executed",
                        ]
                    ).rename(columns={"name_setup_ec": "name_setup_sfc"})
                    exp_sfc_list_to_sql.loc[
                        :, "id_exp_sfc"
                    ] = 0  # must be set to 0 to invoke auto_increment
                    exp_sfc_list_to_sql = exp_sfc_list_to_sql.set_index("id_exp_sfc")
                    exp_sfc_list_to_sql = exp_sfc_list_to_sql.loc[
                        :,
                        [
                            "name_user",
                            "name_setup_sfc",
                            "t_start__timestamp",
                            "rawdata_path",
                            "rawdata_computer",
                            "id_ML",
                            "id_ML_technique",
                            "id_sample",
                            "id_spot",
                            "force__N",
                            "T_stage__degC",
                            "labview_sfc_version",
                            "comment",
                        ],
                    ]

                    # print(exp_sfc_list_to_sql)

                    # print(exp_sfc_list_to_sql)#.loc[:, 't_start__timestamp'])
                    try:
                        exp_sfc_list_to_sql.to_sql(
                            "exp_sfc", con=conn, if_exists="append"
                        )
                    except sql.exc.IntegrityError as error:
                        print(str(error.orig), type(error.orig))
                        if "Duplicate entry" in str(error.orig) and "UNIQUE" in str(
                            error.orig
                        ):
                            warnings.warn(
                                "\nFile "
                                + tdms_file.name
                                + " is already added to db and will be skipped. \n"
                                  "If this is not intended check uniqueness of couples: \n "
                                  "1) rawdata_computer - rawdata_path - id_ML_technique \n "
                                  "2) timestamp - name_setup_ec"
                            )
                            conn.execute(sql.text("UNLOCK TABLES"))
                            continue
                        else:
                            warnings.warn(error.orig)
                            sys.exit("Duplicate entry")
                    # print(conn.execute(sql.text("SELECT * FROM exp_ec")).all())

                    # get id_exp_sfc according to unique columns
                    # rawdata_path, computer, user, 'id_ML', 'id_ML_technique'
                    join_columns = [
                        "name_user",
                        "rawdata_path",
                        "rawdata_computer",
                        "id_ML",
                        "id_ML_technique",
                    ]
                    # Jonas SFC Software instead: 't_start__timestamp', 'rawdata_computer', 'name_user'
                    # --> but for old IES timestamp not available (although this is already solved!)
                    updated_exp_ec = pd.DataFrame(
                        conn.execute(
                            sql.text(
                                "SELECT `id_exp_sfc`, "
                                + ",".join(join_columns)
                                + " FROM exp_sfc;"
                            )
                        ).all(),
                        columns=["id_exp_sfc"] + join_columns,
                    ).set_index(join_columns)
                    # print(updated_exp_ec)
                    # print(exp_ec_list.loc[:, join_columns])
                    exp_ec_list = exp_ec_list.join(
                        updated_exp_ec, on=join_columns, how="left"
                    )


                    # write exp_ec
                    exp_ec_list_to_sql = exp_ec_list.set_index("id_exp_sfc").loc[
                        :,
                        [
                            "name_technique",
                            "R_u__ohm",
                            "iR_corr_in_situ__percent",
                            "E_RE__VvsRHE",
                            "name_RE",
                            "name_CE",
                            "name_device",
                            "id_control_mode",
                            "id_ie_range",
                            "id_vch_range",
                            "id_ich_range",
                            "id_vch_filter",
                            "id_ich_filter",
                            "id_ca_speed",
                            "id_ie_stability",
                            "id_sampling_mode",
                            "ie_range_auto",
                            "vch_range_auto",
                            "ich_range_auto",
                        ],
                    ]
                    exp_ec_list_to_sql.to_sql("exp_ec", con=conn, if_exists="append")

                    # write exp_ec_technique_tables
                    for index, row in exp_ec_list.iterrows():
                        # print(row, row.loc['exp_ec_technique_table'])
                        exp_ec_technique_table_tosql = pd.DataFrame(
                            row.loc["exp_ec_technique_table"], index=[row["id_exp_sfc"]]
                        )
                        exp_ec_technique_table_tosql.index = (
                            exp_ec_technique_table_tosql.index.rename("id_exp_sfc")
                        )
                        # print(exp_ec_technique_table_tosql.index)
                        exp_ec_technique_table_tosql.to_sql(
                            row["name_technique"], con=conn, if_exists="append"
                        )
                        # print(exp_ec_technique_table_tosql, row['name_technique'])

                    # data_ec table
                    if not data_ec.empty:
                        data_ec_tosql = (
                            data_ec.join(
                                exp_ec_list.loc[
                                    :, ("id_exp_sfc", "data_ec_tablename")
                                ].set_index(["data_ec_tablename"]),
                                on=["data_ec_tablename"],
                            )
                            .reset_index()
                            .rename(columns={"index": "id_data_ec"})
                            .set_index(["id_exp_sfc", "id_data_ec"])
                            .drop(columns="data_ec_tablename")
                        )
                        data_ec_tosql.to_sql(
                            "data_ec", con=conn, if_exists="append", chunksize=1000
                        )

                    # data_eis table
                    if not data_eis.empty:
                        # print(data_eis, exp_ec_list.loc[:, ('id_exp_sfc', 'data_ec_tablename')])
                        data_eis_tosql = (
                            data_eis.join(
                                exp_ec_list.loc[
                                    :, ("id_exp_sfc", "data_ec_tablename")
                                ].set_index(["data_ec_tablename"]),
                                on=["data_ec_tablename"],
                            )
                            .reset_index()
                            .rename(columns={"index": "id_data_eis"})
                            .set_index(["id_exp_sfc", "id_data_eis"])
                            .drop(columns="data_ec_tablename")
                        )
                        data_eis_tosql.to_sql(
                            "data_eis", con=conn, if_exists="append", chunksize=1000
                        )

                    # flow_cell_assemblies
                    if not flow_cell_assemblies_list.empty:
                        flow_cell_assemblies_list_tosql = (
                            flow_cell_assemblies_list.reset_index()
                            .join(exp_ec_list.loc[:, ("id_exp_sfc")], on=["index"])
                            .drop(columns=["index"])
                            .set_index(["id_exp_sfc", "location"])
                        )
                        # print(flow_cell_assemblies_list_tosql)
                        flow_cell_assemblies_list_tosql.to_sql(
                            "flow_cell_assemblies", con=conn, if_exists="append"
                        )  # , method='multi')

                    # flow_electrolyte table
                    if not electrolyte_flow_list.empty:
                        electrolyte_flow_list_tosql = (
                            electrolyte_flow_list.reset_index()
                            .join(exp_ec_list.loc[:, ("id_exp_sfc")], on=["index"])
                            .drop(columns=["index"])
                            .set_index(["id_exp_sfc", "location"])
                        )
                        electrolyte_flow_list_tosql.to_sql(
                            "flow_electrolyte", con=conn, if_exists="append"
                        )

                    # flow_gas table
                    if not gas_flow_list.empty:
                        gas_flow_list_tosql = (
                            gas_flow_list.reset_index()
                            .join(exp_ec_list.loc[:, ("id_exp_sfc")], on=["index"])
                            .drop(columns=["index"])
                            .set_index(["id_exp_sfc", "location", "function"])
                        )
                        gas_flow_list_tosql.to_sql(
                            "flow_gas", con=conn, if_exists="append"
                        )

                    # Check constraints on exp_ec parent-child relationship
                    conn.execute(sql.text("CALL CheckConstraints_exp_ec_techniques;"))
                    conn.execute(sql.text("UNLOCK TABLES"))

                    print(
                        "\x1b[32m",
                        "Successfully inserted data belonging to ",
                        tdms_file.name,
                        "\x1b[0m",
                        "\n\n",
                    )

    """
    Throw warning for overload error != 8191 with translation --> build function for that
    """
    pretty_summary_print(manual_info)
    t_1_read_folder = datetime.datetime.now()
    print(
        "Time to read+insert all requested files: ",
        t_1_read_folder - t_0_read_folder,
        " s",
    )


