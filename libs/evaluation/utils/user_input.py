"""
Scripts to simplify user input
Created in 2023
@author: Forschungszentrum Jülich GmbH, Nico Röttcher
"""

import sys
import warnings
from datetime import datetime

import numpy as np
import pandas as pd
import sqlalchemy as sql

# git-synced modules
from evaluation.utils import db


def user_input(
    text,
    dtype,
    optional=False,
    options=None,
    int_min=0,
    format_timestamp="%Y-%m-%d %H:%M:%S.%f",
    default=" 12:00:00.000000",
):
    """
    user input function, asking user for an input checking for correct datatype and reask if unallowed input is given.
    :param text: str
        text for the input question
    :param dtype: str one of ['bool', 'timestamp', 'str', 'int', 'float']
        expected datatype of the input which will be checked after input is given
    :param optional: bool
        whether the input is optional, if True will accept any of ['', 'Null', 'None', 'No'] as None
    :param options: pd.DataFrame
        options from which ethe user can select
        pd.DataFrame with columns 'dropdown' (which should be displayed on screen) and 'values' (which will be returned)
    :param int_min: int
        minimum value for integer, only applies if dtype='int'
    :param format_timestamp: str
        format of timestamp, only applies if dtype='timestamp'
    :param default: str
        default time,  to fill given timestamp
    :return: formatted input
    """

    nulls = ["", "Null", "None", "No"]

    if dtype == "bool":
        return user_input(
            text=text,
            dtype="int",
            optional=optional,
            options=pd.DataFrame(
                {"values": {0: False, 1: True}, "dropdown": {0: "False", 1: "True"}}
            ),
        )

    if dtype == "timestamp":
        len_timestamp_format = {"Y": 4, "m": 2, "d": 2, "H": 2, "M": 2, "S": 2, "f": 6}
        format_replaced = format_timestamp
        for key, val in len_timestamp_format.items():
            format_replaced = format_replaced.replace("%" + key, str(key) * val)
        text = text + " using format " + format_replaced

    while True:
        input_string = input(
            text
            + (
                "".join(
                    [
                        "\t" + str(index) + ": " + str(row["dropdown"]) + "\n"
                        for index, row in options.iterrows()
                    ]
                )
                + "Your choice"
                if options is not None
                else ""
            )
            + (" or type one of " + ", ".join(nulls) + ":" if optional else ": ")
        )

        if input_string.casefold() in [
            null.casefold() for null in nulls
        ]:  # is null entered? case-insensitive
            if optional:
                return None
            else:
                print(
                    "Null not allowed! This is not an optional parameter. Please retry."
                )

        elif dtype == "str":
            try:
                input_string = str(input_string)
                if options is None:  # or input_string in options.loc[:, 'values']:
                    return input_string
                else:
                    print("Options for strings not developed")  # ('Not in options')
            except ValueError:
                print("Not a string!")
        elif dtype == "float":
            try:
                input_string = float(input_string)
                if options is None:  # or input_string in options.loc[:, 'values']:
                    return input_string
                else:
                    print("Options for floats not developed")  # ('Not in options')
            except ValueError:
                print("Not a float!")
        elif dtype == "int":
            try:
                input_string = int(input_string)
                if input_string < int_min:
                    print("Value too low, at least", int_min)
                    continue
                if options is None:
                    return input_string
                elif input_string in options.loc[:, "values"]:
                    return options.loc[input_string, "values"]
                else:
                    print("Not in options")
            except ValueError:
                print("Not an int!")
        elif dtype == "timestamp":
            # additional check for sufficient length of given timestamp, as defined by length of default
            if (
                len(format_replaced)
                > len(input_string)
                >= len(format_replaced) - len(default)
            ):
                # fill up timestamp with default value
                input_string = (
                    input_string
                    + default[
                        len(input_string) - (len(format_replaced) - len(default)):
                    ]
                )
                print("formatted with default to:", input_string)
            elif len(input_string) < len(format_replaced) - len(default):
                # precision is not high enough, default value too short to fill up
                print(
                    "\x1b[31m",
                    "'" + str(input_string) + "' is too short. Please be more precise.",
                    "\x1b[0m",
                    "\n\n",
                )
                continue

            try:
                return datetime.strptime(input_string, format_timestamp)
            except ValueError:
                print("Not a timestamp")
        else:
            warnings.warn(dtype + " not implemented as manual dtype")
            sys.exit()


def init_new_entry(tbname, conn, engine):
    """
    Insert a new entry in the database table with name tbname and returns the auto_increment id
    :param tbname: str
        name of the table
    :param conn: sqlalchemy.connection
        database connection to execute the insert
    :param engine: sqlalchemy.engine
        database engine to call Reset_Autoincrement procedure
    :return: None
    """
    if tbname == "exp_icpms_calibration_set":
        db.call_procedure(
            engine,
            "Reset_Autoincrement",
            ["exp_icpms_calibration_set", "id_exp_icpms_calibration_set"],
        )
        return conn.execute(
            sql.text("INSERT INTO hte_data.exp_icpms_calibration_set() VALUES();")
        ).lastrowid
    else:
        warnings.warn("Init new entry for table " + tbname + " not developed yet")


def manually_add(
    parameters,
    preset,
    write_to,
    conn,
    engine=None,
    row_selector=slice(None),
):
    """
    give a user questionary to complement all data given in parameters list
    :param parameters: list of dictionaries with following entry possibilities
        name = name of te created column
        dtype = differnet types available
            'fk': column is foreign key constrained, extra values:
                fk_table_name: name of the referenced table
                fk_table_cond: optional, add a constraint (only select entries where .. = ..)
                fk_table_filter: optional, use a self-built table
                init_new_entry: optional, bool, gives a new entry as an option to select
                auto_select_unique: optional, bool, autoi selects an entry if only one entry is selectable
            'enum': if the column is constrained as enum, asks database for options and displays them
            'float'
            'str'
            'timestamp'
        print_info_before = another string printed before the question, to give the user additional data
    :param preset: preset values, from which to choose rather than asking user
    :param write_to: dataframe to which columns should be added
    :param conn: db connnection
    :param engine: db engine (required for fk_table requests)
    :param row_selector: write only to specific rows in dataframe
    :return:
    """
    for parameter in parameters:
        parameter["optional"] = (
            False if "optional" not in parameter.keys() else parameter["optional"]
        )  # default not optional!

        if parameter["name"] not in write_to.columns:
            write_to.loc[row_selector, parameter["name"]] = np.nan

        # check whether selected row(s) and columns are empty, and need to be filled by user input
        # .loc[] can lead to series or specific value (.isna() does not work)
        # thats why get the index as row_selector_is_empty,
        #   if row_selector gives specific value write_to.loc[row_selector, :] gives Series --> index by .name
        #   if row_selector gives multiple rows value write_to.loc[row_selector, :] gives DataFrame --> index by .index
        row_selector_is_empty = (
            [
                write_to.loc[row_selector, :].name,
            ]
            if type(write_to.loc[row_selector, :]) == pd.core.series.Series
            else write_to.loc[row_selector, :].index
        )

        if write_to.loc[row_selector_is_empty, parameter["name"]].isna().all():
            if parameter["name"] not in preset.keys():
                print(
                    parameter["print_info_before"]
                ) if "print_info_before" in parameter.keys() else ""
                if parameter["dtype"] == "fk":
                    parameter["init_new_entry"] = (
                        parameter["init_new_entry_in"]
                        if "init_new_entry_in" in parameter.keys()
                        else False
                    )  # default no init of new entry
                    parameter["auto_select_unique"] = (
                        parameter["auto_select_unique"]
                        if "auto_select_unique" in parameter.keys()
                        else False
                    )  # default no init of new entry
                    parameter["fk_name"] = (
                        parameter["fk_name"]
                        if "fk_name" in parameter.keys()
                        else parameter["name"]
                    )

                    if "fk_table_filter" not in parameter.keys():
                        cond = (
                            parameter["fk_table_cond"]
                            if "fk_table_cond" in parameter.keys()
                            else ""
                        )
                        fk_table = pd.DataFrame(
                            db.call_procedure(
                                engine,
                                "get_dropdown",
                                [parameter["fk_table_name"], cond, "", 0],
                            )[0]
                        )
                    else:
                        # print(parameter['fk_table_filter'])
                        # print(conn.execute(sql.text(parameter['fk_table_filter'])).fetchall())
                        fk_table = pd.DataFrame(
                            conn.execute(sql.text(parameter["fk_table_filter"]))
                        )  # [0]
                        # print(fk_table)
                    if parameter["fk_name"] not in fk_table.columns:
                        warnings.warn(
                            "fk_name: "
                            + parameter["fk_name"]
                            + " not found in fk_table: "
                            + parameter["fk_table_name"]
                            + ";\n fk_name should be: "
                            + fk_table.columns[0]
                            + " only found: "
                            + ", ".join(fk_table.columns)
                        )
                        sys.exit()
                    else:
                        fk_table = (
                            fk_table.rename(columns={parameter["fk_name"]: "values"})
                            .sort_values(by=["values"])
                            .reset_index(drop=True)
                        )

                    if parameter["init_new_entry"]:
                        fk_table = pd.concat(
                            [
                                pd.DataFrame(
                                    {"values": "new", "dropdown": "new entry"},
                                    index=[0],
                                ),
                                fk_table,
                            ]
                        ).reset_index(drop=True)
                        # print(fk_table)
                    # print(len(fk_table.index), )

                    if len(fk_table.index) == 1 and parameter["auto_select_unique"]:
                        input_value = fk_table.loc[0, "values"]
                        print(
                            parameter["name"],
                            " = ",
                            input_value,
                            " was auto-selected as only one entry is defined in fk_table",
                        )
                    else:
                        input_value = user_input(
                            text="Choose "
                            + parameter["name"]
                            + " from entries in "
                            + parameter["fk_table_name"]
                            + ":\n ",
                            dtype="int",
                            optional=parameter["optional"],
                            options=fk_table,
                        )
                    if parameter["init_new_entry"] and input_value == "new":
                        input_value = init_new_entry(
                            parameter["init_new_entry_in"], conn, engine
                        )
                elif parameter["dtype"] == "enum":
                    options = pd.DataFrame(
                        {
                            "values": conn.execute(
                                sql.text(
                                    "SELECT SUBSTRING(COLUMN_TYPE,5)\
                                                        FROM information_schema.COLUMNS\
                                                        WHERE  TABLE_NAME='"
                                    + parameter["enum_table"]
                                    + "'\
                                                            AND COLUMN_NAME='"
                                    + parameter["name"]
                                    + "';",
                                )
                            )
                            .first()[0]
                            .strip("()' ")
                            .split("','")
                        }
                    )
                    options.loc[:, "dropdown"] = options.loc[:, "values"]
                    input_value = user_input(
                        text="Choose "
                        + parameter["name"]
                        + " from entries in enum: \n",
                        dtype="int",
                        optional=parameter["optional"],
                        options=options,
                    )
                elif parameter["dtype"] in ["float", "str"]:
                    input_value = user_input(
                        text="Set " + parameter["name"] + " to ",
                        dtype=parameter["dtype"],
                        optional=parameter["optional"],
                        options=None,
                    )
                elif parameter["dtype"] == "timestamp":
                    input_value = user_input(
                        text="Set " + parameter["name"] + " ",
                        dtype=parameter["dtype"],
                        optional=parameter["optional"],
                        options=None,
                        format_timestamp="%Y-%m-%d %H:%M:%S.%f",
                        default=".000000",  # at least second precision
                    )
                else:
                    warnings.warn(
                        parameter["dtype"] + " not implemented as manual dtype"
                    )
                    sys.exit()
                if input_value is None and "default" in parameter.keys():
                    input_value = parameter["default"]
                write_to.loc[row_selector, parameter["name"]] = input_value
                preset[parameter["name"]] = input_value
            else:
                write_to.loc[row_selector, parameter["name"]] = preset[
                    parameter["name"]
                ]
    return write_to, preset


def ordinal(n: int):
    """
    Get the ordinal of a number
    :param n: int
    :return: str
        number with ordinal (1st, 2nd, ...)
    """
    if 11 <= (n % 100) <= 13:
        suffix = "th"
    else:
        suffix = ["th", "st", "nd", "rd", "th"][min(n % 10, 4)]
    return str(n) + suffix


def truncate(value, decimals=0):
    """
    cutoff decimal numbers from float value to return a value with n decimals. Always round to lower number.
    :param value: float
        decimal number
    :param decimals: int
        number of decimals
    :return: float
        decimal number with number of decimals defined by decimals
    """
    multiplier = 10**decimals
    return int(value * multiplier) / multiplier


def round_digits(value, digits=1, method="half_up", return_str_scientific=False):
    """
    round a float value to specified number of digits (sum before and after comma).
    You can specify method whether to round always up, down or half_up.
    Please verify as there are some errors in some cases.
    :param value: float
        value to be transformed
    :param digits: int
        number of digits to be returned
    :param method: str one of ['up', 'down', 'half_up']
        up: always round up
        down: always round down
        half_up: round up if first cut digit >=5 and down if <5
    :param return_str_scientific: bool
        whether to return as scientific notation string or as number (int or float depending on whether decimal or not)
    :return: str or int or float
    """
    if method not in ["up", "down", "half_up"]:
        raise Exception("method must be one of ['up', 'down', 'half_up']")

    value_no_comma_str = str(value).replace(".", "")
    digits_given = len(value_no_comma_str)
    digits_before_comma = len(str(int(value)))
    # digits_after_comma = digits_given - digits_before_comma

    # No need to cut if less digits given then requested
    if digits_given <= digits:
        if return_str_scientific:
            return_str = f"%.{digits_given - 1}E"
            return return_str % value
        else:
            return value

    # cut value to fulfill given digits
    value_no_comma_str_cut = value_no_comma_str[:digits]

    if method == "down":
        round_up = False
    elif method == "up":
        round_up = True
    elif method == "half_up":
        round_up = True if int(value_no_comma_str[digits]) >= 5 else False
    else:
        raise Exception("method must be one of ['up', 'down', 'half_up']")

    if round_up:
        value_no_comma_str_cut = str(int(value_no_comma_str_cut) + 1)

    if digits_before_comma < digits:
        # return float if decimal number
        value_return = float(
            value_no_comma_str_cut[:digits_before_comma]
            + "."
            + value_no_comma_str_cut[digits_before_comma:]
        )
    else:
        # return int if all decimal sare cut, add zeros if necessary
        value_return = int(value_no_comma_str_cut) * 10 ** (
            digits_before_comma - digits
        )

    # adjust return type
    if return_str_scientific:
        return_str = f"%.{digits - 1}E"
        return return_str % value_return
    else:
        return value_return
