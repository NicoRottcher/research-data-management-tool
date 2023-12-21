"""
Scripts for processing and analyzing electrochemical data
Created in 2023
@author: Nico Röttcher
"""

import datetime as dt
import sys
import warnings
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sqlalchemy as sql
from IPython.display import clear_output
from ipywidgets import *
from matplotlib import gridspec

import evaluation.utils.db_config as db_config
from evaluation.utils import db
from evaluation.utils import user_input  # import user_input, round_digits, truncate
from evaluation.visualization import plot

# def _all_j_geo_cols(data, j_geo_col):
#    return [col for col in data.columns if col[:12] == 'j__mA_cm2geo'] if j_geo_col is None else [j_geo_col]


geo_columns = pd.DataFrame.from_dict(
    {
        "A_geo": {
            0: "spots_spot_size__mm2",
            1: "fc_top_name_flow_cell_A_opening_ideal__mm2",
            2: "fc_top_name_flow_cell_A_opening_real__mm2",
            3: "fc_top_id_sealing_A_opening__mm2",
            4: "fc_top_id_PTL_A_PTL__mm2",
            5: "fc_bottom_name_flow_cell_A_opening_ideal__mm2",
            6: "fc_bottom_name_flow_cell_A_opening_real__mm2",
            7: "fc_bottom_id_sealing_A_opening__mm2",
            8: "fc_bottom_id_PTL_A_PTL__mm2",
        },
        "j_geo": {
            0: "j__mA_cm2geo_spot_size",
            1: "j__mA_cm2geo_fc_top_cell_Aideal",
            2: "j__mA_cm2geo_fc_top_cell_Areal",
            3: "j__mA_cm2geo_fc_top_sealing",
            4: "j__mA_cm2geo_fc_top_PTL",
            5: "j__mA_cm2geo_fc_bottom_cell_Aideal",
            6: "j__mA_cm2geo_fc_bottom_cell_Areal",
            7: "j__mA_cm2geo_fc_bottom_sealing",
            8: "j__mA_cm2geo_fc_bottom_PTL",
        },
        "dm_dt_S": {
            0: "dm_dt_S__ng_s_cm2geo_spot_size",
            1: "dm_dt_S__ng_s_cm2geo_fc_top_cell_Aideal",
            2: "dm_dt_S__ng_s_cm2geo_fc_top_cell_Areal",
            3: "dm_dt_S__ng_s_cm2geo_fc_top_sealing",
            4: "dm_dt_S__ng_s_cm2geo_fc_top_PTL",
            5: "dm_dt_S__ng_s_cm2geo_fc_bottom_cell_Aideal",
            6: "dm_dt_S__ng_s_cm2geo_fc_bottom_cell_Areal",
            7: "dm_dt_S__ng_s_cm2geo_fc_bottom_sealing",
            8: "dm_dt_S__ng_s_cm2geo_fc_bottom_PTL",
        },
    }
)


def add_j_geo(
    exp_ec,
    data,
    I__A_col="I__A",
    suffix="",
    A_geo_col=None,
):
    """
    add j_geo to data_ec or data_eis, usually calculated by database view,
    however necessary if user-specific transformations are requested
    :param exp_ec: exp_ec with list of experiments
    :param data: data_ec or data_eis
    :param I__A_col: 'I__A' for data_ec and  data_eis 'I_dc__A' for data_eis or any other user-specific current column
    :param suffix: suffix for the resulting j_geo_column(s)
    :param A_geo_col: list or None, optional, Default None
        list of A_geo_col in exp_ec to derive j_geo
        None: will calculate j_geo for all A_geo columns defined in tools_ec.geo_columns.A_geo
    :return: data_ec
        including columns for j_geo
    """
    # get requested j_geo_cols
    if A_geo_col is None:
        A_geo_cols = geo_columns.A_geo.tolist()
    else:
        A_geo_cols = A_geo_col if type(A_geo_col) == list else [A_geo_col]
        for A_geo_col in A_geo_cols:
            if A_geo_col not in geo_columns.j_geo.tolist():
                print(
                    A_geo_col
                    + " is not a current density column check geo_columns.j_geo"
                )

    for A_geo_col in A_geo_cols:
        if A_geo_col in exp_ec.columns.tolist():
            j_geo_col = geo_columns.set_index("A_geo").loc[A_geo_col, "j_geo"]

            # check whteher j_geo_col exists in data_ec
            if j_geo_col in data.columns:
                print(
                    j_geo_col
                    + " already contained in given data. This column is skipped."
                )
                continue
            # print('add', j_geo_col)
            data.loc[:, j_geo_col + suffix] = (
                data.loc[:, I__A_col] * 1000 / (exp_ec.loc[:, A_geo_col] / 100)
            )

    return data


def find_subsequent_ec_technique(exp_ec, row, name_column):
    """
    find value in given column (name_column) of subsequent ec technique in the same EC batch (id_ML) given in exp_ec
    by id_ML_technique
    :param exp_ec: EC experimental DataFrame
    :param row: row of the experiment from whcih to find the subsequent experiment
    :param name_column: name of the column from which the value should be returned
    :return: value of name_column for the subsequent ec technique
    """
    # row = exp_ec.iloc[1]
    df_all_subsequent_techniques = exp_ec.loc[
        (
            (exp_ec.id_ML == row.id_ML)
            & (exp_ec.name_user == row.name_user)
            & (exp_ec.name_setup_sfc == row.name_setup_sfc)
            & (
                pd.to_datetime(exp_ec.t_start__timestamp).dt.date
                == pd.to_datetime(row.t_start__timestamp).date()
            )
            & (exp_ec.id_ML == row.id_ML)
            & (exp_ec.id_ML_technique > row.id_ML_technique)
        ),
        :,
    ]  # .min()
    # print(row.name_user, row.name_setup_sfc, pd.to_datetime(row.t_start__timestamp).date(),
    # row.id_ML, row.id_ML_technique)
    if len(df_all_subsequent_techniques.index) == 0:
        return np.nan
    return df_all_subsequent_techniques.loc[
        df_all_subsequent_techniques.id_ML_technique.idxmin(), name_column
    ]


def update_exp_sfc_t_end__timestamp():
    """
    Calculates timestamp of the end of an ec technique and upload it to exp_sfc.t_end__timestamp. This was necessary
    as the end timestamp was not uploaded to database in ECat <V4.5. Not required for new data.
    :return: None
    """
    con = db.connect("hte_write")
    name_user = db.current_user()

    # update_exp_sfc_t_end__timestamp for dc techniques using stored procedure
    db.call_procedure(con, "update_exp_sfc_t_end__timestamp", params=[name_user])
    # willl only update t_end__timestamp of experiments belonging to the current user

    # update_exp_sfc_t_end__timestamp for ac techniques using start time of subsequent experiment
    exp_ec = db.query_sql(
        """SELECT  *
                            FROM hte_data.exp_ec_expanded 
                            WHERE name_user= %s
                                AND ec_name_technique IN ('exp_ec_peis', 'exp_ec_geis')
                                AND t_end__timestamp IS NULL
                         ;""",
        params=[name_user],
        con=con,
        method="pandas",
        index_col="id_exp_sfc",
    )
    # data_eis = exp_ec.dataset.get_data(con, 'data_eis_analysis',

    # only consider eis experiments inserted directly by Jonas Software, because otherwise start timestamp is unknown
    # start time for ac techniques via python insert are build by id_ML and id_ML_technique
    exp_ec_selected = exp_ec.loc[
        [
            row.t_start__timestamp[-6:]
            != "000"[len(str(row["id_ML"])):]
            + str(row["id_ML"])
            + "000"[len(str(row["id_ML_technique"])):]
            + str(row["id_ML_technique"])
            for index, row in exp_ec.iterrows()
        ],
        :,
    ].copy()

    # if no eis techniques to update selected quit
    if len(exp_ec_selected.index) == 0:
        return True

    exp_ec_selected.loc[:, "Date"] = pd.to_datetime(
        exp_ec_selected.t_start__timestamp
    ).dt.date

    # select all techniques within id_MLs with ac techniques (necessary to find subsequent experiment)
    sql_query = "SELECT * FROM exp_ec_expanded WHERE "
    params = []
    for counter, (index, row) in enumerate(
        exp_ec_selected.loc[:, ["name_user", "name_setup_sfc", "Date"]]
        .drop_duplicates()
        .iterrows()
    ):
        id_MLs = (
            exp_ec_selected.loc[
                (
                    (exp_ec_selected.name_user == row.name_user)
                    & (exp_ec_selected.name_setup_sfc == row.name_setup_sfc)
                    & (
                        pd.to_datetime(exp_ec_selected.t_start__timestamp).dt.date
                        == row.Date
                    )
                ),
                "id_ML",
            ]
            .unique()
            .tolist()
        )
        id_MLs_str = ("%s, " * len(id_MLs))[:-2]
        # print(id_MLs_str)
        sql_query += " OR " if counter > 0 else ""
        sql_query += (
            """( name_user = %s
                        AND name_setup_sfc = %s 
                        AND DATE(t_start__timestamp) = %s 
                        AND id_ML IN ("""
            + id_MLs_str
            + """)
                   )"""
        )
        params += row.tolist() + id_MLs
    # print(' '.join([sql+str(params) for sql_query, params in zip(sql_query.split('%s'), params+[''])]))
    exp_ec_all = db.query_sql(
        sql_query, params=params, con=con, method="pandas", index_col="id_exp_sfc"
    )

    # derive t_end__timestamp
    exp_ec_selected.loc[:, "t_end__timestamp"] = exp_ec_selected.apply(
        lambda x: find_subsequent_ec_technique(exp_ec_all, x, "t_start__timestamp"),
        axis=1,
    ).tolist()  # tools_data_ec.find_subsequent_ec_technique(x, 't_start__timestamp', exp_ec)

    # update
    df_update = exp_ec_selected.loc[
        :,
        [
            "t_end__timestamp",
        ],
    ].dropna()
    if len(df_update.index) > 0:
        display(df_update)
        if user_input.user_input(
            text="Update the following experiments?\n",
            dtype="bool",
        ):
            db.sql_update(df_update, table_name="exp_sfc")
        else:
            print("Not updated")


def data_eis_avg_to_data_ec(exp_ec, data_ec, data_eis):
    """
    add weighted average value for dc current and potential during EIS measurement to data_ec.
    Useful for integration of current during eis experiments
    Per eis experiment two datapoints are added. One with the start time of the experiment.
    Another one with the start time of the next experiment as end time is not recorded (yet)
    :param exp_ec: pd.DataFrame
        EC experimental dataframe
    :param data_ec: pd.DataFrame
        EC data dataframe
    :param data_eis: pd.DataFrame
        EIS data dataframe
    :return: concatted data_ec and data_eis values transformed
    """
    if not data_eis.Timestamp.isna().all():
        print(
            "\x1b[33m",
            "At least some of the EIS data has a Timestamp (measured with eCat >4.9).",
            "This is not developed yet.",
            "\x1b[0m",
        )

    # data_eis.f__Hz / data_eis.f__Hz.groupby(level=0).sum()
    data_eis_ec_begin = pd.DataFrame({})
    data_eis_ec_begin.loc[:, "Timestamp"] = pd.to_datetime(
        exp_ec.loc[
            exp_ec.ec_name_technique.isin(["exp_ec_geis", "exp_ec_peis"]),
            "t_start__timestamp",
        ]
    )
    data_eis_ec_begin.loc[:, "id_data_ec"] = 0
    # data_eis_ec_begin.set_index('id_data_ec', append=True, inplace=True)
    data_eis_ec_end = pd.DataFrame({})
    data_eis_ec_end.loc[:, "Timestamp"] = pd.to_datetime(
        exp_ec.loc[
            exp_ec.ec_name_technique.isin(["exp_ec_geis", "exp_ec_peis"]),
            "t_end__timestamp",
        ]
    )
    # exp_ec.loc[exp_ec.ec_name_technique.isin(['exp_ec_geis', 'exp_ec_peis']), :]\
    #    .apply(lambda row: find_subsequent_ec_technique(exp_ec,
    #                                                    row,
    #                                                    't_start__timestamp'),
    #            axis=1)
    data_eis_ec_end.loc[:, "id_data_ec"] = 1
    # data_eis_ec_end.set_index('id_data_ec', append=True, inplace=True)
    data_eis_ec = pd.concat([data_eis_ec_begin, data_eis_ec_end])

    level = list(
        range(len(data_eis.index[0]) - 1)
    )  # usually just id_exp_sfc (level=0) but necessary for overlap with multiple indexes

    data_eis_ec.loc[:, "E_WE_raw__VvsRE"] = (
        (
            1
            / data_eis.f__Hz
            / (1 / data_eis.f__Hz).groupby(level=level).sum()
            * data_eis.E_dc__VvsRE
        )
        .groupby(level=level)
        .sum()
    )
    data_eis_ec.loc[:, "E_WE_uncompensated__VvsRHE"] = (
        (
            1
            / data_eis.f__Hz
            / (1 / data_eis.f__Hz).groupby(level=level).sum()
            * data_eis.E_dc__VvsRE
        )
        .groupby(level=level)
        .sum()
    )
    data_eis_ec.loc[:, "I__A"] = (
        (
            1
            / data_eis.f__Hz
            / (1 / data_eis.f__Hz).groupby(level=level).sum()
            * data_eis.I_dc__A
        )
        .groupby(level=level)
        .sum()
    )
    data_eis_ec.set_index("id_data_ec", append=True, inplace=True)
    data_eis_ec.loc[:, "t__s"] = pd.to_timedelta(
        data_eis_ec.loc[:, "Timestamp"] - data_eis_ec_begin.loc[:, "Timestamp"]
    ).dt.total_seconds()

    data_eis_ec = add_j_geo(
        exp_ec,
        data_eis_ec,
    )
    data_eis_ec.sort_index()  # .dataset.display()

    return pd.concat([data_ec, data_eis_ec]).sort_index()


def derive_HFR(
    exp_eis,
    data_eis,
    on="id_exp_sfc",
    method="minimumorintercept",
    show_control_plot=True,
    suffix="",
    append_cols=None,
):
    """
    Derive a guess for high frequency resistance for a set of experiments
    :param exp_eis: list of eis experiments to be analyzed
    :param data_eis: corresponding data of eis experiments
    :param on: index to match experiments to data
    :param method: method to derive the HFR , choose from: 'minimum', 'intercept', 'minimumorintercept'
    :param show_control_plot: creates a figure to visually control the quality of the HFR extraction
    :param suffix: str, optional default ''
        suffix to append to the name of columns being appended to exp_eis (for example if applied mutliple times)
    :param append_cols: list of columns to be appended to exp_eis, default only essential columns
    :return: exp_eis with derived HFR the experimental set with
    """

    def derive_HFR_single_exp(group):
        """
        Derive a guess for high frequency resistance for a signle experiment
        """
        # display( group.sort_values(by=['id_exp_sfc',  'f__Hz'],
        # ascending=[True, False]).shift(-1).sort_values(by=['id_exp_sfc',  'id_data_eis']).minusZ_img__ohm)

        # determine possible x-axis intercept points by comparing
        # with neighbouring values with lower and higher frequency
        group.loc[:, "next_lf_minusZ_img__ohm"] = (
            group.sort_values(by=["id_exp_sfc", "f__Hz"], ascending=[True, False])
            .shift(-1)
            .sort_values(by=["id_exp_sfc", "id_data_eis"])
            .minusZ_img__ohm
        )
        group.loc[:, "next_hf_minusZ_img__ohm"] = (
            group.sort_values(by=["id_exp_sfc", "f__Hz"], ascending=[True, False])
            .shift(1)
            .sort_values(by=["id_exp_sfc", "id_data_eis"])
            .minusZ_img__ohm
        )
        possible_intercept_points = (
            (group.minusZ_img__ohm < 0) & (group.next_lf_minusZ_img__ohm > 0)
        ) | ((group.minusZ_img__ohm > 0) & (group.next_hf_minusZ_img__ohm < 0))

        if method == "minimumorintercept":
            method_local = (
                "intercept"
                if group.minusZ_img__ohm.min() < 0 and possible_intercept_points.any()
                else "minimum"
            )
        else:
            method_local = method

        if method_local == "intercept":
            # intercept if negative values and x-axis intercept values
            id_data_eis_chosen_Ru = (
                group.loc[possible_intercept_points, "minusZ_img__ohm"]
                .abs()
                .idxmin()[-1]
            )
            # R_u_derived_by = 'intercept'
        elif method_local == "minimum":
            # minimum value if all values positive (or negative --> this should not be the case)
            id_data_eis_chosen_Ru = group.minusZ_img__ohm.idxmin()[-1]
            # R_u_derived_by = 'minimum'
        else:
            raise Exception(
                'method must be one of ["minimumorintercept", "minimum", "intercept"'
            )

        return pd.concat(
            [
                pd.Series(
                    {
                        "id_data_eis_chosen_Ru": id_data_eis_chosen_Ru,
                        "R_u_derived_by": method_local,  # R_u_derived_by,
                        "R_u__ohm": group.loc[
                            (group.index[0][0], id_data_eis_chosen_Ru), "Z_real__ohm"
                        ],
                    }
                ),
                None
                if append_cols is None
                else group.loc[
                    group.index.get_level_values(level=-1) == id_data_eis_chosen_Ru,
                    append_cols,
                ].iloc[0],
            ]
        )

    # Apply derife_HFR_single on each experiment in the list
    exp_eis = exp_eis.join(
        data_eis.groupby(level=0).apply(derive_HFR_single_exp), on=on, rsuffix=suffix
    )  # 'id_exp_sfc_geis')

    if show_control_plot:
        print("\x1b[33m", "Control quality of HFR extraction:", "\x1b[0m")
        with plt.rc_context(
            plot.get_style(
                style="singleColumn",
                add_params={
                    "figure.dpi": 150,
                },
            )
        ):
            fig = plt.figure()
            ax1 = fig.add_subplot(111)
            exp_eis = (
                exp_eis.dataset.add_column("color", values="tab10")
                .plot(
                    x_col="Z_real__ohm",
                    y_col="minusZ_img__ohm",
                    data=data_eis,
                    ax=ax1,
                    marker="s",
                    markersize=2,
                    alpha=0.3,
                    label="",
                )
                .add_column(
                    "label",
                    values="R$_\mathrm{u}$: "
                    + exp_eis.assign(dummy_index=exp_eis.index).dummy_index.astype(str),
                )
                .plot(
                    x_col="R_u__ohm",
                    y_col=0,
                    axlabel_auto=False,
                    marker="|",
                    markersize=15,
                    linestyle="",
                )
                .return_dataset()
            )
            ax1.legend(fontsize=5)
            plt.show()

    return exp_eis


def update_R_u__ohm(
    exp_ec,
    match_eis_id_ML=None,
    match_eis_timedelta__h=3,
    user_control=True,
    **kwargs_derive_HFR
):
    """
    Loops through all exp_ec and searches for matching EIS data.
    For found EIS experiments the HFR will be derived and updated in exp_ec
    :param exp_ec: experimental dataframe received from exp_ec_expanded
    :param match_eis_id_ML: int or None, optional, default None
        match eis from given id_ML given as single int or list of ints with length of exp_ec
    :param match_eis_timedelta__h: search for matched eis n hours before and after start timestamp of ec experiment
    :param user_control: bool, optional, Default True
        whether user has to control the selection of EIS experiment and derivation of uncompensated resistance
    :param kwargs_derive_HFR: keyword arguments for the derive_HFR method
    :return: exp_ec with updated columns ec_R_u__ohm, ec_R_u_determining_exp_ec
    """

    if (
        exp_ec.index.name != "id_exp_sfc"
        or "ec_R_u__ohm" not in exp_ec.columns
        or "ec_R_u_determining_exp_ec" not in exp_ec.columns
    ):
        raise Exception("Only works with exp_ec derived from exp_ec_expanded!")

    exp_ec.loc[:, "match_eis_id_ML"] = match_eis_id_ML
    for index, row in exp_ec.iterrows():
        # if row.name_user != db.current_user():
        #    print("\x1b[33m", 'View-only: This is data from ',
        #          row.name_user,
        #          '. Updates are restricted!',
        #          "\x1b[0m")

        if (
            row.ec_R_u__ohm != 0
            and row.ec_R_u__ohm is not None
            or row.ec_R_u_determining_exp_ec is not None
        ):
            # Either R_u_ohm already given when performed experiment
            # or updated by using this routine (ec_R_u_determining_exp_ec)
            print(
                "\x1b[33m",
                "Already updated exp_ec with index:",
                index,
                "with R_u__ohm=",
                row.ec_R_u__ohm,
                " from id_exp_sfc=",
                row.ec_R_u_determining_exp_ec,
                "\x1b[0m",
            )
            continue
        # print(index, ', '.join(exp_ec.index.names))
        sql_query = (
            '''
                    SELECT  *
                    FROM exp_ec_expanded 
                    WHERE name_user= "'''
            + row.name_user
            + '''"
                        AND name_setup_sfc = "'''
            + row.name_setup_sfc
            + """"
                        AND id_sample = """
            + str(row.id_sample)
            + """
                        AND id_spot = """
            + str(row.id_spot)
            + (
                ''' AND t_start__timestamp < "'''
                + str(
                    pd.to_datetime(exp_ec.iloc[0].t_start__timestamp)
                    + pd.Timedelta(hours=match_eis_timedelta__h)
                )
                + '''"
                         AND t_start__timestamp > "'''
                + str(
                    pd.to_datetime(exp_ec.iloc[0].t_start__timestamp)
                    - pd.Timedelta(hours=match_eis_timedelta__h)
                )
                + '"'
                if match_eis_id_ML is None
                else """ AND id_ML=""" + str(row.match_eis_id_ML)
            )
            + """ AND ec_name_technique IN ("exp_ec_peis", "exp_ec_geis")
                        ;
                     """
        )

        exp_eis = db.get_exp(sql_query)

        if len(exp_eis.index) == 0:
            print(
                "\x1b[33m",
                "No EIS experiments matched to given ec experiment with "
                + ", ".join(exp_ec.index.names)
                + ": "
                + str(index),
                "\x1b[0m",
            )
            print(sql_query)
            continue

        data_eis = db.get_data(exp_eis, "data_eis_analysis")
        exp_eis = derive_HFR(exp_eis, data_eis, **kwargs_derive_HFR)

        exp_eis.loc[:, "time_diff_to_ec__min"] = (
            pd.to_datetime(exp_eis.t_start__timestamp)
            - pd.to_datetime(row.t_start__timestamp)
        ).dt.total_seconds() / 60
        exp_eis.loc[:, "time_diff_to_ec_abs__min"] = exp_eis.time_diff_to_ec__min.abs()

        if len(exp_eis.index) == 1:
            print(
                "Matched experiment performed ",
                exp_eis.iloc[0].time_diff_to_ec__min,
                "min ",
                "earlier" if exp_eis.iloc[0].time_diff_to_ec__min > 0 else "later",
            )
            if user_control:
                if not user_input.user_input(
                    text="Transfer extracted R_u to given exp_ec with index: "
                    + str(index)
                    + "?\n",
                    dtype="bool",
                ):
                    continue
            index_selected_eis = exp_eis.index[0]
        else:
            print("\x1b[33m", "Multiple EIS experiments matched. Choose:", "\x1b[0m")
            exp_eis = exp_eis.sort_values(by="time_diff_to_ec_abs__min")
            # print((pd.to_datetime(exp_eis.t_start__timestamp)
            #        - pd.to_datetime(row.t_start__timestamp)).abs().idxmin())
            iloc_index_selected_eis = user_input.user_input(
                text="Select: \n",
                dtype="int",
                optional=False,
                options=pd.DataFrame(
                    {
                        "values": {
                            no: str(val)
                            for no, val in enumerate(exp_eis.reset_index().index)
                        },
                        "dropdown": {
                            no: ", ".join(
                                row_eis[exp_eis.index.names].values.astype(str)
                            )
                            + ", "
                            + row_eis.ec_name_technique
                            + ", "
                            + "id_ML="
                            + str(row_eis.id_ML)
                            + ", "
                            + "R_u="
                            + str(user_input.round_digits(row_eis.R_u__ohm, digits=3))
                            + " \u03A9, "
                            + "time difference to ec="
                            + str(
                                user_input.truncate(
                                    row_eis.time_diff_to_ec__min, decimals=2
                                )
                            )
                            + " min"
                            for no, (index_eis, row_eis) in enumerate(
                                exp_eis.reset_index().iterrows()
                            )
                        },
                    }
                ),
            )
            index_selected_eis = exp_eis.index[int(iloc_index_selected_eis)]
        # print(exp_eis.iloc[int(index_selected_eis)])
        print(
            "Updated exp_ec with index:",
            index,
            "with ec_R_u_postdetermined__ohm=",
            exp_eis.loc[index_selected_eis, "R_u__ohm"],
            " from id_exp_sfc=",
            index_selected_eis,
        )  # exp_eis.loc[index_selected_eis, :].index.get_level_values(level='id_exp_sfc'))
        # to link experiment to publication
        db.get_exp(
            by="SELECT * FROM exp_ec_expanded WHERE id_exp_sfc=%s",
            params=[int(index_selected_eis)],
        )
        exp_ec.loc[
            index, ["ec_R_u_postdetermined__ohm", "ec_R_u_determining_exp_ec"]
        ] = [
            exp_eis.loc[index_selected_eis, "R_u__ohm"],
            index_selected_eis,
        ]

    return exp_ec


def compensate_R_u(exp_ec, data_ec):
    """
    Derive compensated potential based on given potential, current, and uncompensated resistance by columns
    ec_R_u__ohm or ec_R_u_postdetermined__ohm and ec_iR_corr_in_situ__percent in exp_ec.
    Also referencing potential to RHE by column ec_E_RE__VvsRHE on exp_ec
    :param exp_ec: experimental dataframe as received by exp_ec_expanded
    :param data_ec: experimental dataframe as received by data_ec
    :return: data_ec with new columns for compensated potential E_WE__VvsRHE
    """
    if "ec_R_u_postdetermined__ohm" in exp_ec.columns:
        # R_u as determined by tools_ec.update_Ru__ohm where exists
        # else R_u as given by user and stored in db as R_u__ohm (or ec_R_u__ohm)
        exp_ec.loc[
            ~exp_ec.ec_R_u_postdetermined__ohm.isna(), "ec_R_u__ohm"
        ] = exp_ec.loc[
            ~exp_ec.ec_R_u_postdetermined__ohm.isna(), "ec_R_u_postdetermined__ohm"
        ]

    ec_R_u__ohm = data_ec.join(exp_ec.ec_R_u__ohm, on="id_exp_sfc").ec_R_u__ohm
    ec_iR_corr_in_situ__percent = data_ec.join(
        exp_ec.ec_iR_corr_in_situ__percent, on="id_exp_sfc"
    ).ec_iR_corr_in_situ__percent
    ec_E_RE__VvsRHE = data_ec.join(
        exp_ec.ec_E_RE__VvsRHE, on="id_exp_sfc"
    ).ec_E_RE__VvsRHE

    data_ec = data_ec.assign(
        E_WE__VvsRHE=(data_ec.E_WE_raw__VvsRE + ec_E_RE__VvsRHE)
        - ((data_ec.I__A * ec_R_u__ohm) * (1 - (ec_iR_corr_in_situ__percent / 100))),
        E_WE_uncompensated__VvsRHE=(data_ec.E_WE_raw__VvsRE + ec_E_RE__VvsRHE)
        + data_ec.Delta_E_WE_uncomp__V,
        E_WE_raw__VvsRHE=(data_ec.E_WE_raw__VvsRE + ec_E_RE__VvsRHE),
    )
    # ((data_ec.E_WE__VvsRHE_test - data_ec.E_WE__VvsRHE) > 1e-7).any()
    # deviations from SQL result only due to FLOAT nature of value
    return data_ec


def geometric_current(
    exp_ec, data_ec, geo_cols=None, j_geo_col_subscript="", I_col__A="I__A"
):
    """
    Derive geometric current density based on metadata sample area, column name(s) specified by geo_cols
    :param exp_ec: experimental dataframe as received by exp_ec_expanded
    :param data_ec: experimental dataframe as received by data_ec
    :param geo_cols: optional, str or list of column names in exp_ec to derive geometric current density,
                    only values in plot.geo_columns allowed, default all values in plot.geo_column
    :param j_geo_col_subscript: add a subscript to create j_geo columns
    :param I_col__A: name of the colum from whic to derive the geometric current
    :return: data_ec with new columns for geometric current density
    """
    if geo_cols is None:
        geo_cols = plot.geo_columns.loc[:, "A_geo"]
    elif type(geo_cols) == str:
        geo_cols = [geo_cols]
    for geo_col in geo_cols:
        j_geo_col = plot.geo_columns.set_index("A_geo").loc[geo_col, "j_geo"]
        if j_geo_col_subscript != "":
            j_geo_col = j_geo_col.replace("j__", "j_" + j_geo_col_subscript + "__")
        geo_value__mm2 = data_ec.join(exp_ec.loc[:, geo_col], on="id_exp_sfc").loc[
            :, geo_col
        ]
        data_ec.loc[:, j_geo_col] = (
            data_ec.loc[:, I_col__A] * 1000 / (geo_value__mm2 / 100)
        )

    return data_ec


def gravimetric_current(exp_ec, data_ec, j_geo_col=None):
    """
    Add loading and composition columns to exp_ec_expanded and mass normalized current to data_ec.
    Using loading column in spots/sample table and composition given in samples_composition/spots_composition
    :param exp_ec: experimental dataframe as received by exp_ec_expanded
    :param data_ec: experimental dataframe as received by data_ec
    :param j_geo_col: Selected a specific column for geometric area which will be used to normalize by mass.
    Optional, if None procedure is done for all geometric columns.
    :return: exp_ec, data_ec
        with appended columns for loading and gravimetric current density
    """
    return plot.get_j__mA_mg(
        exp_ec,
        data_ec,
        j_geo_col,
    )


def derive_ECSA(
    exp_ec,
    data_ec,
    method="Pt_Hupd_horizontal",
    geo_cols=None,
    Q_spec__C_cm2=None,
    display_result_plot=True,
):
    """
    Derive the ECSA from experimental data by different methods.
    :param exp_ec: experimental dataframe as received by exp_ec_expanded
    :param data_ec: experimental dataframe as received by data_ec
    :param method: method of the derivation to be used
    :param geo_cols: geometric colum to be used to derive roughness factor
    :param Q_spec__C_cm2: specific charge to be used to evaluate the specific area.
        On Pt for Hupd default of 210e-6 is used. (e.g.: https://doi.org/10.20964/2016.06.71)
    :param display_result_plot: bool
        whether to display result plot
    :return: exp_ec, data_ec
        with appended columns for surface-specific charge, specific electrode area, ECSA,
        and surface specific current density
    """
    if geo_cols is None:
        geo_cols = plot.geo_columns.loc[:, "A_geo"]
    elif type(geo_cols) == str:
        geo_cols = [geo_cols]

    if len(exp_ec.index) > 1:
        # raise Exception('derivation of ECSA for multiple experiments not yet developed.')
        exp_ec_return = pd.DataFrame()
        data_ec_return = pd.DataFrame()
        for index, row in exp_ec.iterrows():
            exp_ec_single = exp_ec.loc[
                [
                    index,
                ]
            ]
            data_ec_single = data_ec.loc[
                [
                    index,
                ]
            ]
            exp_ec_single, data_ec_single = derive_ECSA(
                exp_ec_single,
                data_ec_single,
                method=method,
                geo_cols=geo_cols,
                Q_spec__C_cm2=Q_spec__C_cm2,
            )

            exp_ec_return = pd.concat([exp_ec_return, exp_ec_single])
            data_ec_return = pd.concat([data_ec_return, data_ec_single])
        return exp_ec_return, data_ec_return

    if len(data_ec.loc[(exp_ec.index, slice(None)), "cycle"].unique()) > 1:
        raise Exception("derivation of ECSA for multiple cycles not yet developed.")

    if method == "Pt_Hupd_horizontal":
        print(
            "\x1b[33m",
            "This is just a basic implementation of ECSA calculation for single CV cycle on "
            "Pt with constant capacitive current correction in acidic electrolyte.",
            "Be aware analysis procedure need to be adjusted for different electrode material, electrolyte, ...",
            "\x1b[0m",
        )
        data_ec.loc[:, "selection_derive_minimum"] = (
            data_ec.E_WE__VvsRHE.diff() > 0
        ) & (data_ec.E_WE__VvsRHE > 0.2)
        data_ec.loc[:, "selection_derive_intersection"] = (
            data_ec.E_WE__VvsRHE.diff() > 0
        ) & (data_ec.E_WE__VvsRHE < 0.2)
        index_minimum = data_ec.loc[
            data_ec.selection_derive_minimum, :
        ].I__A.idxmin()
        iloc_minimum = (
            data_ec.reset_index().loc[data_ec.index == index_minimum, :].index[0]
        )
        number_datapoints_avg_minimum = 11
        data_ec.loc[:, "selection_minimum"] = data_ec.index.isin(
            data_ec.iloc[
                iloc_minimum - int((number_datapoints_avg_minimum - 1) / 2):
                iloc_minimum + int((number_datapoints_avg_minimum - 1) / 2 + 1)
            ].index
        )
        I_capacitive__A = data_ec.loc[data_ec.selection_minimum, :].I__A.mean()

        index_intersect = data_ec.loc[
            (
                (data_ec.E_WE__VvsRHE.diff() > 0)
                & (data_ec.E_WE__VvsRHE < 0.2)
                & (data_ec.I__A > I_capacitive__A)
            ),
            :,
        ].index[0]
        # first datapoint above capacitive current
        data_ec.loc[:, "selection_derive_ecsa"] = data_ec.index.isin(
            data_ec.loc[index_intersect:index_minimum, :].index
        )
        data_ec.loc[
            data_ec.selection_derive_ecsa, "I_capacitive__A"
        ] = I_capacitive__A

        data_ec = geometric_current(
            exp_ec,
            data_ec,
            geo_cols=geo_cols,
            j_geo_col_subscript="capacitive",
            I_col__A="I_capacitive__A",
        )  # calculate geometric current density

        exp_ec.loc[:, "Q_ECSA__C"] = np.trapz(
            data_ec.loc[data_ec.selection_derive_ecsa, :].I__A,
            x=data_ec.loc[data_ec.selection_derive_ecsa, :].t__s,
        ) - np.trapz(
            data_ec.loc[data_ec.selection_derive_ecsa, :].I_capacitive__A,
            x=data_ec.loc[data_ec.selection_derive_ecsa, :].t__s,
        )
        Q_spec_Hupd__C_cm2 = 210 * 10**-6  # default value
        exp_ec.loc[:, "Q_spec__C_cm2"] = (
            Q_spec_Hupd__C_cm2 if Q_spec__C_cm2 is None else Q_spec__C_cm2
        )

        exp_ec.loc[:, "ECSA_method"] = method
        exp_ec.loc[:, "A_spec__m2"] = exp_ec.Q_ECSA__C / exp_ec.Q_spec__C_cm2 / 10**4
        exp_ec.loc[:, "A_spec__mm2"] = exp_ec.A_spec__m2 * 1e6
        data_ec.loc[:, "j__mA_cm2spec_Pt_hupd"] = (
            data_ec.loc[:, "I__A"] * 1000 / (exp_ec.A_spec__mm2.iloc[0] / 100)
        )

        # print('A_spec = ', A_spec__m2, ' m²')
        for geo_col in geo_cols:
            exp_ec.loc[:, "roughness_factor_" + geo_col] = (
                exp_ec.A_spec__m2 / exp_ec.loc[:, geo_col] * 1e6
            )

        if 'loading__mg_Pt_cm2' in exp_ec.columns:
            if ~exp_ec.loading__mg_Pt_cm2.isna().all():
                exp_ec.loc[:, "ECSA__m2_gPt"] = exp_ec.A_spec__m2 / (
                    exp_ec.loading__mg_Pt_cm2 / 1000 * exp_ec.spots_spot_size__mm2 / 100
                )
                # print('ECSA-Hupd = ', ECSA, ' m²/gPt')

        if display_result_plot:
            data_ec_selection_derive_minimum = (
                data_ec.loc[data_ec.selection_derive_minimum, :]
                .sort_values(by="E_WE__VvsRHE")
                .reset_index()
                .reset_index()
                .rename(columns={"index": "id_data_ec_sorted"})
                .set_index(["id_exp_sfc", "id_data_ec_sorted"])
                .copy()
            )
            data_ec_selection_minimum = (
                data_ec.loc[data_ec.selection_minimum, :]
                .sort_values(by="E_WE__VvsRHE")
                .reset_index()
                .reset_index()
                .rename(columns={"index": "id_data_ec_sorted"})
                .set_index(["id_exp_sfc", "id_data_ec_sorted"])
                .copy()
            )
            data_ec_selection_derive_ecsa = (
                data_ec.loc[data_ec.selection_derive_ecsa, :]
                .sort_values(by="E_WE__VvsRHE")
                .reset_index()
                .reset_index()
                .rename(columns={"index": "id_data_ec_sorted"})
                .set_index(["id_exp_sfc", "id_data_ec_sorted"])
                .copy()
            )

            with plt.rc_context(
                plot.get_style(
                    style="singleColumn",
                    fig_size={"width": 6, "height": 4},
                    add_margins_and_figsize={
                        "left": -0.3,
                        "bottom": -0.3,
                    },
                )
            ):
                fig = plt.figure()
                ax1 = fig.add_subplot(111)
                # ax1.yaxis.set_tick_params(which='both', labelleft=False)

                exp_ec.dataset.plot(
                    x_col="E_WE__VvsRHE",
                    y_col="I__A",
                    data=data_ec,
                    ax=ax1,
                    label="raw data",
                    color="tab:blue",
                ).plot(
                    x_col="E_WE__VvsRHE",
                    y_col="I__A",
                    data=data_ec_selection_derive_minimum,
                    ax=ax1,
                    label="datapoints to derive minimum",
                    color="tab:orange",
                ).plot(
                    x_col="E_WE__VvsRHE",
                    y_col="I__A",
                    data=data_ec_selection_minimum,
                    ax=ax1,
                    label="datapoints of minimum",
                    color="tab:red",
                ).plot(
                    x_col="E_WE__VvsRHE",
                    y_col="I__A",
                    data=data_ec_selection_derive_ecsa,
                    ax=ax1,
                    label="datapoints to derive ecsa",
                    color="tab:red",
                    linestyle="--",
                ).plot(
                    x_col="E_WE__VvsRHE",
                    y_col="I_capacitive__A",
                    data=data_ec_selection_derive_ecsa,
                    ax=ax1,
                    label="capacitive current",
                    color="tab:red",
                    linestyle="-.",
                    axlabel_auto=False,
                ).fill_between(
                    x_col="E_WE__VvsRHE",
                    y_col="I_capacitive__A",
                    y2_col="I__A",
                    data=data_ec_selection_derive_ecsa,
                    ax=ax1,
                    label="$Q_\mathrm{ECSA}\ =$ %.2E C"
                    % (exp_ec.loc[:, "Q_ECSA__C"].iloc[0]),
                    color="tab:blue",
                    alpha=0.6,
                    axlabel_auto=False,
                ).return_dataset()

                # ax1.set_ylabel("$j_\\mathrm{geo}$ / mA cm$^{-2}$")
                # ax1.set_xlabel("$E$ / V vs. RHE")

                legend = ax1.legend(loc="upper left", bbox_to_anchor=(0, -0.2))
                legend.get_frame().set_alpha(0)
                # plot_storage.export(fig)

                plt.show()

    else:
        raise Exception("Method: " + method + " not yet implemented")

    return exp_ec, data_ec


def get_derived_ECSA(
    sql_ec,
    cycle=2,
    match_eis_id_ML=None,
    match_eis_timedelta__h=3,
    user_control_eis=True,
    geo_cols="fc_top_name_flow_cell_A_opening_ideal__mm2",
    method="Pt_Hupd_horizontal",
    Q_spec__C_cm2=None,
    display_result_plot=True,
):
    """
    Get ECSA for an exp_ec derived from an other ec experiment defined via sql_ec
    :param sql_ec: define experiment from which to derive ECSA from
    :param cycle: cycle of the experiment from whcih to derive ECSA from
    :param match_eis_id_ML: update_R_u__ohm parameter to derive compensated potentials
    :param match_eis_timedelta__h: update_R_u__ohm parameter to derive compensated potentials
    :param user_control_eis: update_R_u__ohm parameter to derive compensated potentials
    :param geo_cols: derive_ECSA parameter
    :param method: derive_ECSA parameter
    :param Q_spec__C_cm2: derive_ECSA parameter
    :param display_result_plot: derive_ECSA parameter
    :return: exp_ec, data_ec of the experiments from which ECSA is derived
    """
    exp_ec = db.get_exp(sql_ec)

    exp_ec = update_R_u__ohm(
        exp_ec,
        match_eis_id_ML=match_eis_id_ML,
        match_eis_timedelta__h=match_eis_timedelta__h,
        user_control=user_control_eis,
    )  # derive uncompensated resistance from EIS experiemtn performed in id_ML=61

    data_ec = db.get_data(exp_ec, "data_ec", add_cond="cycle IN (%s)" % (int(cycle)))
    data_ec = compensate_R_u(exp_ec, data_ec)  # calculate compensated potentials
    data_ec = geometric_current(
        exp_ec, data_ec, geo_cols=geo_cols
    )  # calculate geometric current density
    exp_ec, data_ec = plot.get_j__mA_mg(
        exp_ec,
        data_ec,
        # j_geo_col='j_geo__mA_cm2geo_spot_size',
    )

    exp_ec, data_ec = derive_ECSA(
        exp_ec,
        data_ec,
        method=method,
        geo_cols=geo_cols,
        Q_spec__C_cm2=Q_spec__C_cm2,
        display_result_plot=display_result_plot,
    )

    return exp_ec, data_ec
