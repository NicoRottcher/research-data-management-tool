"""
Scripts for processing and analysis of ICP-MS experiments
Created in 2023
@author: Forschungszentrum Jülich GmbH, Nico Röttcher
"""

from pathlib import Path
from matplotlib import gridspec
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import datetime, os, sys
from ipywidgets import *
from IPython.display import clear_output

# import matplotlib.ticker as mticker
from matplotlib.dates import DateFormatter, num2date, AutoDateLocator  # SecondLocator

# own modules
# from evaluation.utils import db, db_config
import evaluation.utils.db as db
import evaluation.utils.db_config as db_config
from evaluation.utils import user_input
import datetime

from evaluation.visualization import plot
from evaluation.visualization import extra_widgets
from evaluation.processing import tools_ec, Fit_SFC_ICP_MS_Dissolution

# from importlib import reload
# reload(plot)


def update_t_delay__s(
    id_exp_icpms,
    figure_dpi=280,
    export_plotdata=True,
    export_path=db_config.DIR_REPORTS() / Path("03_ICPMS_update_t_delay__s/"),
):
    """
    Update the delay time between applied electrochemical protocol and observed icpms counts.
    This will change depending on the cell design, SFC to ICPMS tube length and diameter.
    To evaluate the delay time, usually an EC experiment is performed which spontaneously lead to increase in the
    observed element (e.g.: Potential step, CV with fast scan rate, Contact peak).
    To adjust the delay time, zoom into and move the graph to the time point of the EC experiment. Use the buttons to
    autoscale the y-axis'. Use the Integer Field to adjust the delay time until the start of rising ICPMS signal is
    synchronized with the applied electrochemical protocol. For clearer aligning use th ebalck dotted lines.
    Updating database, inserts set delay time into exp_icpms_sfc.t_delay__s and stores plot in current zoom status
    to given export path.
    :param id_exp_icpms: id of the icpms experiment
    :param figure_dpi: dpi of the figure (this will scale figure size, use 150 on small screens)
    :param export_plotdata: whether to export plot to file and data to database
    :param export_path: optional, str
        path where the plot should be stored. Default path depends on whether run on institute jupyterhub or in mybinder
        as defined in evaluation.utils.db_config
    :return:
    """
    if type(id_exp_icpms) != int:
        raise Exception("id_exp_icpms must be a single integer")

    # Data
    con = db.connect()
    exp_icpms = db.get_exp(
        """SELECT * 
                             FROM exp_icpms_sfc_expanded 
                             WHERE id_exp_icpms = %s;""",
        params=[int(id_exp_icpms)],
    )
    # con=con,
    # index_col=['id_exp_icpms', 'name_isotope_analyte', 'name_isotope_internalstandard'])  # .iloc[:4]

    if exp_icpms.name_user.iloc[0] != db.current_user():
        print(
            "\x1b[33m",
            "View-only: This is data from ",
            exp_icpms.name_user.iloc[0],
            ". Updates are restricted!",
            "\x1b[0m",
        )

    if exp_icpms.loc[:, "t_delay__s"].isna().any():
        exp_icpms.loc[:, "t_delay__s"] = 0  # Make it 0 if nan
    data_icpms = exp_icpms.dataset.get_data(
        con,
        "data_icpms",
    )
    data_icpms.loc[:, "t_delaycorrected__timestamp_sfc_pc"] = (
        pd.to_datetime(exp_icpms.t_start__timestamp_sfc_pc)
        - pd.to_timedelta(exp_icpms.t_delay__s, unit="s")
        + pd.to_timedelta(data_icpms.t__s, unit="s")
    )  # _delaycorrected
    data_icpms.loc[:, "count_ratio"] = (
        data_icpms.loc[:, "counts_analyte"]
        / data_icpms.loc[:, "counts_internalstandard"]
    )

    match_ec_icpms = exp_icpms.dataset.match_exp_sfc_exp_icpms(
        con, A_geo_cols="fc_top_name_flow_cell_A_opening_ideal__mm2"
    )
    exp_ec = match_ec_icpms.dataset.get_exp(
        con, "exp_ec_expanded", index_cols=["id_exp_sfc"]
    )

    # remove eis experiments
    exp_ec = exp_ec.loc[~exp_ec.ec_name_technique.isin(["exp_ec_peis", "exp_ec_geis"])]

    data_ec = exp_ec.dataset.get_data(con, "data_ec_analysis")
    data_ec.loc[:, "Timestamp"] = data_ec.loc[:, "Timestamp"]

    # Plot
    with plt.rc_context(
        plot.get_style(
            style="singleColumn",
            increase_fig_height=1,
            add_margins_and_figsize={"left": 0.3, "right": 2.5, "bottom": 0.5},
            # add_margins={'left':0.3, 'right':3},
            add_params={"figure.dpi": figure_dpi},
            interactive=True,
        )
    ):
        plot_storage = plot.PlotDataStorage(
            "Update_t_delay__s__id_exp_icpms_" + str(id_exp_icpms),
            overwrite_existing=True,
        )
        exp_ec.export_name = "exp_ec"
        exp_icpms.export_name = "exp_icpms"

        fig = plt.figure()
        # gs = gridspec.GridSpec(2, 1)
        ax1 = fig.add_subplot(111)
        ax1.export_name = "left_yaxis"
        ax1r = ax1.twinx()
        ax1r.export_name = "right_1st_yaxis"
        ax1r2 = ax1.twinx()
        ax1r2.export_name = "right_2nd_yaxis"
        ax1r2.spines.right.set_position(("axes", 1.2))

        # ax1.grid(axis='x', color='black')

        colors = {"icpms": "tab:green", "I": "tab:blue", "E": "grey"}
        ax1.tick_params(axis="y", which="both", colors=colors["icpms"])
        ax1r2.spines["left"].set_color(colors["icpms"])
        ax1.yaxis.label.set_color(colors["icpms"])
        ax1r.tick_params(axis="y", which="both", colors=colors["E"])
        ax1r.spines["right"].set_color(colors["E"])
        ax1r.yaxis.label.set_color(colors["E"])
        ax1r2.tick_params(axis="y", which="both", colors=colors["I"])
        ax1r2.spines["right"].set_color(colors["I"])
        ax1r2.yaxis.label.set_color(colors["I"])

        # yaxis ticklabel if in scientific notation useMathtext
        ax1.ticklabel_format(useMathText=True)
        ax1r.ticklabel_format(useMathText=True)
        ax1r2.ticklabel_format(useMathText=True)
        ax1r2.get_yaxis().get_offset_text().set_position((1.32, 0))

        # Adjust xticks to date format
        ax1.xaxis.set_major_locator(AutoDateLocator())
        # ax1.set_xticklabels(ax1.get_xticks(), rotation = 30, ha='right') # will throw use locator warning
        for label in ax1.get_xticklabels(which="major"):
            label.set(rotation=30, horizontalalignment="right")
        # #horizontalalignment or ha [ 'center' | 'right' | 'left' ]
        ax1.xaxis.set_major_formatter(DateFormatter("%H:%M:%S"))

        exp_icpms = exp_icpms.dataset.plot(
            x_col="t_delaycorrected__timestamp_sfc_pc",
            y_col="counts_analyte",
            ax=ax1,
            data=data_icpms,
            color=colors["icpms"],
            timestamp_cols_to_seconds=False,
        ).return_dataset()

        # .add_column('label', values=exp_ec.loc[:, 'ec_name_technique'])\
        # .add_column('color', values='blue')\
        exp_ec = (
            exp_ec.dataset.plot(
                x_col="Timestamp",  # 'Timestamp_synchronized__s',
                y_col="E_WE_uncompensated__VvsRHE",
                ax=ax1r,
                data=data_ec,
                color=colors["E"],
                alpha=0.5,
                timestamp_cols_to_seconds=False,
            )
            .plot(
                x_col="Timestamp",  # 'Timestamp_synchronized__s',
                y_col="I__A",
                ax=ax1r2,
                data=data_ec,
                color=colors["I"],
                alpha=0.5,
                timestamp_cols_to_seconds=False,
            )
            .return_dataset()
        )

        # ax1.vlines(0.5, 0,1,linestyle='--', color='black', transform=ax1.transAxes)
        for x in [0.25, 0.5, 0.75]:
            ax1.plot(
                [x, x], [0, 1], linestyle="--", color="black", transform=ax1.transAxes
            )

        # Sliders
        intText_t_delay__s = widgets.IntText(
            value=int(exp_icpms.loc[:, "t_delay__s"].iloc[0]),
            description="Adjust delay time",
            continuous_update=False,
            disabled=False,
            style={"description_width": "initial"},
        )

        def update_on_intText(changed_value):
            # print((exp_icpms.t_start__timestamp_sfc_pc + pd.to_timedelta(data_icpms.t__s, unit='s')).iloc[0])
            data_icpms.loc[:, "t_delaycorrected__timestamp_sfc_pc"] = (
                pd.to_datetime(exp_icpms.t_start__timestamp_sfc_pc)
                - pd.to_timedelta(changed_value.new, unit="s")
                + pd.to_timedelta(data_icpms.t__s, unit="s")
            )
            # print(data_icpms.loc[:, 't_delaycorrected__timestamp_sfc_pc'].iloc[0])

            for index, row in exp_icpms.iterrows():
                # print(index, row.ax_plot_objects[-1][0])
                # display(data_icpms.loc[index, 'counts_analyte'])
                row.ax_plot_objects[-1][0].set_xdata(
                    data_icpms.loc[index, "t_delaycorrected__timestamp_sfc_pc"]
                )
                row.ax_plot_objects[-1][0].set_ydata(
                    data_icpms.loc[index, "counts_analyte"]
                )

            fig.canvas.draw()  # does the update of axis

        intText_t_delay__s.observe(update_on_intText, "value")

        # Upload Button
        upload_output = widgets.Output()

        def on_upload_button_clicked(changed_value):
            with upload_output:
                clear_output()
                if not db.user_is_owner(
                    "id_exp_icpms", index_value=int(exp_icpms.index[0][0])
                ):
                    print(
                        "\x1b[31m",
                        "You better not change data of other users",
                        "\x1b[0m",
                    )
                    return
                plot_file_type = "svg"
                exp_icpms.loc[:, "t_delay__s"] = intText_t_delay__s.value
                df_update = (
                    exp_icpms.droplevel(level=[1, 2])
                    .loc[
                        :,
                        [
                            "t_delay__s",
                        ],
                    ]
                    .assign(
                        t_updated_t_delay__timestamp=datetime.datetime.now(),
                        file_path_plot_update_t_delay=str(
                            export_path / (plot_storage.name + "." + plot_file_type)
                        ),
                    )
                )
                # display(df_update)
                engine = db.connect("hte_processor")
                with engine.begin() as con_update:
                    db.sql_update(
                        df_update,
                        table_name="exp_icpms_sfc",
                        con=con_update,
                    )

                print(
                    "\x1b[32m",
                    "Successfully updated to t_delay__s in exp_icpms_sfc",
                    "\x1b[0m",
                )
                if export_plotdata:
                    plot_storage.export(
                        fig, export_data=True, auto_overwrite=True, path=export_path
                    )

        button_upload_update = "Update t_delay__s in database"
        # button_upload_insert = 'Insert t_delay__s to database'
        upload_button = widgets.Button(
            description=button_upload_update,
            button_style="info",
            disabled=False,
            tooltip="Click me",
            icon="check",
            layout=Layout(
                width="300px",
            ),
        )
        upload_button.on_click(on_upload_button_clicked)

        autoscale_E_WE__VvsRHE = extra_widgets.button_autoscale(
            description="Autoscale E_WE__VvsRHE",
            ax=ax1r,
            which="y",
            margin=0.05,
            lines=[line_list[0][0] for line_list in exp_ec.ax_plot_objects.to_numpy()],
            layout=Layout(
                width="200px",
            ),
        )
        autoscale_I__A = extra_widgets.button_autoscale(
            description="Autoscale I__A",
            ax=ax1r2,
            which="y",
            margin=0.05,
            lines=[line_list[1][0] for line_list in exp_ec.ax_plot_objects.to_numpy()],
            layout=Layout(
                width="200px",
            ),
        )
        autoscale_counts_analyte = extra_widgets.button_autoscale(
            description="Autoscale counts analyte",
            ax=ax1,
            which="y",
            margin=0.05,
            lines=[
                line_list[0][0] for line_list in exp_icpms.ax_plot_objects.to_numpy()
            ],
            layout=Layout(
                width="200px",
            ),
        )

        fig.tight_layout()
        display(
            widgets.VBox(
                [
                    intText_t_delay__s,
                    upload_button,
                    upload_output,
                    widgets.HBox(
                        [
                            autoscale_counts_analyte,
                            autoscale_E_WE__VvsRHE,
                            autoscale_I__A,
                        ]
                    ),
                ]
            )
        )
        plt.show()
    return plot_storage


def update_counts_internalstandard_fitted(
    id_exp_icpms,
    t_start_shift__s=0,  # -100,  # 0#
    t_end_shift__s=0,  # 200,  # 300#0#
    confidence_interval=1,
    figure_dpi=150,
    export_plotdata=True,
    export_path=db_config.DIR_REPORTS() / Path("04_ICPMS_ISTD_fitting/"),
    display_exp_icpms_sfc_batch=False,
    display_calibration_limits=True,
    ignore_id_exp_sfc=None,
):
    """
    Fitting internal standard counts during ec experiments. This is required as the concentration of species is derived
    by ratio of counts from analyte and internalstandard. Instrument depending noise and unphysical spikes in
    internalstandard counts will propagate to calculated concentration. Linear fitting removes the propagation of this
    error, while accounting for a linear shift in internalstandard counts which are frequently observed.
    The linear fitting is performed per EC experiment batch, depending on t_start_shift__s and t_end_shift__s multiple
    EC batches might be considered as one, which will be printed during the routine. By this splitting of fit, icpms
    signal in between EC experiments is not of interest in further analysis and are frequently prone to large
    fluctuations due to bubbles.
    If the linear fit is insufficient, there are two parameters to adjust the fitting procedure: confidence_interval
    (perform a 2nd fitting including only datapoints within th egiven confidence ionterval) and
    t_start_shift__s/t_end_shift__s (select more or less icpms points at edge of EC experiment)
    Fitted internalstandard counts are uploaded to database:
        data_icpms_internalstandard_fitting.counts_internalstandard_fitted.
    :param id_exp_icpms: Index of the icpms experiment to be analyzed.
    :param t_start_shift__s: start time shift of matching icpms data to ec experiment,
        useful if no dissolution free ec protocol was used before the protocol of interest.
        However, consider in regard of good scientific practice that potential is unknown in that timeframe.
    :param confidence_interval: int > 0 and <= 1. Default 1. For <1: A 2nd fitting routine is performed which only
        includes datapoints within the given confidence interval. By this, unintended spikes (bubbles in ICPMS flow)
        are filtered out. The amount of removed counts is printed in %. Use with care!
    :param t_end_shift__s: end time shift of matching icpms data to ec data, useful if tailing of icpms signal appears,
        Enter a sufficient large value to include tailed signal into integration analysis
        However, consider in regard of good scientific practice that potential is unknown in that timeframe.
    :param figure_dpi: dpi of the figure (this will scale figure size, use 150 on small screens)
    :param export_plotdata: optional, default True. Whether to export the plot and corresponding data in the given path
    :param export_path: optional, str
        path where the plot should be stored. Default path depends on whether run on institute jupyterhub or in mybinder
        as defined in evaluation.utils.db_config
    :param display_exp_icpms_sfc_batch: optional, default False; searches for batch measurement
        with id_exp_icpms = id_exp_icpms_sfc_online and displays it
    :param display_calibration_limits: optional, default True
        - setting this to true, displays two additional things in the ICPMS plot
            - 1. the countratio of the measured calibration solutions marked with x at the left edge of the plot
            - 2. the area above the maximum countratio and below its minimum is marked in red
        --> with this you can quickly see whether the analyte concentrations in your calibration solutions
        are chosen carefully
        A good plot should display:
        - the markers for the different calibration solutions on the left side (if you cannot see them,
            they will be much higher --> the analyte concentrations for your calibration are chosen too high)
        - all dissolution data should be in between the red marked areas. If your data is in the red area the
            analyte concentrations are chosen too low.
    :param ignore_id_exp_sfc: optional, default [], list of id_exp_sfcs which should be ignored
    :return: PlotDataStorage object
    """
    if ignore_id_exp_sfc is None:
        ignore_id_exp_sfc = []
    con = db.connect()
    exp_icpms = db.get_exp(
        """SELECT * 
           FROM exp_icpms_sfc_expanded 
           WHERE id_exp_icpms = %s;""",
        params=[int(id_exp_icpms)],
    )
    # , con=con, index_col=['id_exp_icpms', 'name_isotope_analyte', 'name_isotope_internalstandard'])  # .iloc[:4]
    if exp_icpms.t_delay__s.iloc[0] == 0:
        print(
            "\x1b[31m",
            "The delay time is set to 0 s. Adjust the delay time before performing integration analysis!",
            "\x1b[0m",
        )
    if exp_icpms.name_user.iloc[0] != db.current_user():
        print(
            "\x1b[33m",
            "View-only: This is data from ",
            exp_icpms.name_user.iloc[0],
            ". Updates are restricted!",
            "\x1b[0m",
        )

    match_ec_icpms = exp_icpms.dataset.match_exp_sfc_exp_icpms(
        con, A_geo_cols="fc_top_name_flow_cell_A_opening_ideal__mm2"
    )  # , 'fc_top_name_flow_cell_A_opening_real__mm2' ])
    exp_ec = match_ec_icpms.dataset.get_exp(
        con, "exp_ec_expanded", index_cols=["id_exp_sfc"]
    )
    exp_ec = exp_ec.loc[~exp_ec.index.isin(ignore_id_exp_sfc), :]

    data_ec = exp_ec.dataset.get_data(con, "data_ec_analysis")
    data_icpms = match_ec_icpms.dataset.get_data(
        con,
        "data_icpms_sfc_analysis",
        join_cols=["id_exp_icpms"],
        index_cols=[
            "id_exp_icpms",
            "name_isotope_analyte",
            "name_isotope_internalstandard",
            "id_data_icpms",
        ],
        t_start_shift__s=0,
        t_end_shift__s=0,
    )
    data_icpms.loc[:, "count_ratio"] = (
        data_icpms.loc[:, "counts_analyte"]
        / data_icpms.loc[:, "counts_internalstandard"]
    )
    data_icpms = data_icpms.drop(
        columns=["counts_internalstandard_fitted"]
    )  # remove stored results in database --> could be used in future implementation to plot previous analysis

    if display_exp_icpms_sfc_batch:
        exp_icpms_batch = db.get_exp(
            """SELECT * 
                                         FROM exp_icpms_sfc_batch_expanded 
                                         WHERE id_exp_icpms_sfc_online= %s
                                         ;""",
            params=[int(id_exp_icpms)],
        )
        # con=con, index_col=['id_exp_icpms', 'name_isotope_analyte', 'name_isotope_internalstandard'])  # .iloc[:4]
        data_icpms_batch = exp_icpms_batch.dataset.get_data(
            con, "data_icpms_sfc_batch_analysis"
        )
        data_ec, data_icpms, data_icpms_batch = plot.synchronize_timestamps_multiple(
            list_data=[data_ec, data_icpms, data_icpms_batch],
            list_timestamp_cols=[
                "Timestamp",
                "t_delaycorrected__timestamp_sfc_pc",
                "t_delaycorrected__timestamp_sfc_pc",
            ],
            list_index_data_ec=0,
        )
    else:
        data_ec, data_icpms = plot.synchronize_timestamps(
            data_ec=data_ec,
            data_icpms=data_icpms,
            timestamp_col_ec="Timestamp",
            timestamp_col_icpms="t_delaycorrected__timestamp_sfc_pc",
        )

    # plot.
    exp_ec.loc[:, "Date"] = pd.to_datetime(exp_ec.t_start__timestamp).dt.date
    exp_ec_ML = exp_ec.reset_index().groupby(["Date", "id_ML"]).first().sort_index()
    exp_ec_ML["t_end__timestamp"] = exp_ec.groupby(["Date", "id_ML"])[
        "t_end__timestamp"
    ].last()
    exp_ec_ML = exp_ec_ML.reset_index()
    exp_ec_ML.index.name = "id_ML_datesafe"

    exp_ec_ML.loc[:, "t_start__timestamp_shifted"] = exp_ec_ML.loc[
        :, "t_start__timestamp"
    ] + pd.Timedelta(seconds=t_start_shift__s)
    exp_ec_ML.loc[:, "t_end__timestamp_shifted"] = exp_ec_ML.loc[
        :, "t_end__timestamp"
    ] + pd.Timedelta(seconds=t_end_shift__s)
    exp_ec_ML.loc[
        :, "t_start__timestamp_shifted_next"
    ] = exp_ec_ML.t_start__timestamp_shifted.shift(-1)
    exp_ec_ML.loc[
        :, "t_end__timestamp_shifted_next"
    ] = exp_ec_ML.t_end__timestamp_shifted.shift(-1)
    exp_ec_ML.loc[:, "id_ML_next"] = exp_ec_ML.id_ML.shift(-1)
    exp_ec_ML.loc[:, "index_next"] = exp_ec_ML.index + 1  # .shift(-1)
    exp_ec_ML.loc[:, "index_prev"] = [
        index - 1 if index > 0 else np.nan for index in exp_ec_ML.index
    ]  # .shift(-1)

    index_exp_ec_ML_overlapping = (
        exp_ec_ML.t_end__timestamp_shifted > exp_ec_ML.t_start__timestamp_shifted_next
    )  # , :]
    # print(index_exp_ec_ML_overlapping)
    if index_exp_ec_ML_overlapping.any():
        print(
            "\x1b[33m"
            + "Some id_ML overlapped: "
            + "".join(
                [
                    str(int(row.id_ML))
                    + (
                        ("/" + str(int(row.id_ML_next)) + ", ")
                        if int(row.id_ML_next)
                        not in exp_ec_ML.loc[
                            index_exp_ec_ML_overlapping, "id_ML"
                        ].tolist()
                        else "/"
                    )
                    for index, row in exp_ec_ML.loc[
                        index_exp_ec_ML_overlapping
                    ].iterrows()
                ]
            )[:-2]
            + ". The id_MLs will be treated as one experiment and their ISTD fits will be combined."
            + "\x1b[0m"
        )
        for index, row in (
            exp_ec_ML.loc[index_exp_ec_ML_overlapping].iloc[::-1].iterrows()
        ):
            # print(index)
            # print(exp_ec_ML.loc[index, 'index_prev'])
            exp_ec_ML.loc[index, "t_end__timestamp_shifted"] = exp_ec_ML.loc[
                index, "t_end__timestamp_shifted_next"
            ]
            if not np.isnan(exp_ec_ML.loc[index, "index_prev"]):
                exp_ec_ML.loc[
                    exp_ec_ML.loc[index, "index_prev"], "t_end__timestamp_shifted_next"
                ] = exp_ec_ML.loc[index, "t_end__timestamp_shifted_next"]

            # print('Removed id_ML', exp_ec_ML.loc[index,'id_ML_next'])
            # print(row.)
            # instead of dropping overlapped id_ML, groupby t_end_timestamp
            # exp_ec_ML.drop(index=exp_ec_ML.loc[index,'index_next'], inplace=True)

    exp_ec_ML_grouped = (
        exp_ec_ML.groupby("t_end__timestamp_shifted").first().reset_index()
    )
    exp_ec_ML_grouped.index.name = "id_ML_datesafe_overlapsafe"

    # calculate relation of id_exp_sfc and id_ML_datesafe_overlapsafe
    exp_ec = exp_ec.join(
        exp_ec_ML.join(
            exp_ec_ML_grouped.reset_index()
            .set_index("t_end__timestamp_shifted")
            .id_ML_datesafe_overlapsafe,
            on="t_end__timestamp_shifted",
        )
        .reset_index()
        .set_index(["Date", "id_ML"])
        .id_ML_datesafe_overlapsafe,
        on=["Date", "id_ML"],
        # lsuffix='g'
    )

    exp_ec_ML = exp_ec_ML_grouped.reset_index(drop=True)
    exp_ec_ML.index.name = "id_ML_datesafe_overlapsafe"

    # add NaN row at end of each id_exp_sfc to ensure no connecting lines between experiments
    for index, value in (
        data_ec.reset_index().groupby("id_exp_sfc")["id_data_ec"].last().items()
    ):  # last()
        # print(index, value)
        data_ec.loc[(index, value + 1), "t__s"] = np.nan
    data_ec = data_ec.sort_index()

    data_ec_ML = data_ec.join(
        exp_ec.id_ML_datesafe_overlapsafe, on="id_exp_sfc"
    ).sort_index()  #
    data_ec_ML["id_data_ec_ML"] = data_ec_ML.groupby(
        "id_ML_datesafe_overlapsafe"
    ).cumcount()  # .dataset.display()
    # data_ec_ML.iloc[-2600:].dataset.display()
    data_ec_ML = data_ec_ML.reset_index().set_index(
        ["id_ML_datesafe_overlapsafe", "id_data_ec_ML"]
    )  # , inplace=True)#.loc[data_ec_ML.id_ML==5]
    # data_ec_ML

    # only possible for one id_exp_icpms selected
    # --> otherwise it need to be checked which id_exp_icpms belongs to which exp_ec
    if len(exp_icpms.index.get_level_values(level=0).unique()) > 1:
        sys.exit("Multiple exp_icpms not implemented")

    exp_icpms_ML = (
        exp_icpms.reset_index()
        .merge(
            exp_ec_ML.reset_index().loc[
                :,
                [
                    "id_ML_datesafe_overlapsafe",
                    "t_start__timestamp_shifted",
                    "t_end__timestamp_shifted",
                ],
            ],
            how="cross",
        )
        .set_index(
            [
                "id_exp_icpms",
                "name_isotope_analyte",
                "name_isotope_internalstandard",
                "id_ML_datesafe_overlapsafe",
            ]
        )
    )

    data_icpms_ML = data_icpms.copy()
    for index, row in exp_icpms_ML.reset_index().iterrows():
        a = data_icpms.loc[
            (
                row.id_exp_icpms,
                row.name_isotope_analyte,
                row.name_isotope_internalstandard,
                slice(None),
            )
        ]

        index_data_icpms_ML = slice(
            (
                row.id_exp_icpms,
                row.name_isotope_analyte,
                row.name_isotope_internalstandard,
                (
                    a.t_delaycorrected__timestamp_sfc_pc
                    - (pd.to_datetime(row.t_start__timestamp_shifted))
                )
                .abs()
                .idxmin(),
            ),
            (
                row.id_exp_icpms,
                row.name_isotope_analyte,
                row.name_isotope_internalstandard,
                (
                    a.t_delaycorrected__timestamp_sfc_pc
                    - (pd.to_datetime(row.t_end__timestamp_shifted))
                )
                .abs()
                .idxmin(),
            ),
        )
        # print(index_data_icpms_ML)
        data_icpms_ML.loc[
            index_data_icpms_ML, "id_ML_datesafe_overlapsafe"
        ] = row.id_ML_datesafe_overlapsafe

    data_icpms_ML = data_icpms_ML.loc[
        ~data_icpms_ML.id_ML_datesafe_overlapsafe.isna()
    ].sort_index()
    data_icpms_ML = data_icpms_ML.reset_index().set_index(
        [
            "id_exp_icpms",
            "name_isotope_analyte",
            "name_isotope_internalstandard",
            "id_ML_datesafe_overlapsafe",
            "id_data_icpms",
        ]
    )  # .sort_index()

    # Handling very short EC experiments which just match with one ICPMS datapoint --> remove these experiments
    exp_too_short = exp_icpms_ML.loc[
        data_icpms_ML.reset_index()
        .groupby(
            [
                "id_exp_icpms",
                "name_isotope_analyte",
                "name_isotope_internalstandard",
                "id_ML_datesafe_overlapsafe",
            ]
        )
        .count()
        .id_data_icpms
        <= 1,
        :,
    ]

    for index, row in (
        exp_too_short.groupby(["id_exp_icpms", "id_ML_datesafe_overlapsafe"])
        .first()
        .iterrows()
    ):
        print(
            "\x1b[31m",
            "For these Macrolists only a single ICPMS datapoint is found "
            "(the ML is too short or was interrupted pretty fast).\n    ",
            exp_ec_ML.loc[index[1], ["Date", "id_ML"]].astype(str).to_json() + "\n",
            "Linear fitting of a single point is impossible, "
            "thus these MLs are neglected for the following analysis. Please inform admin if this is not intended.",
            "\x1b[0m",
        )
    exp_icpms_ML = exp_icpms_ML.loc[~(exp_icpms_ML.index.isin(exp_too_short.index)), :]
    exp_ec_ML = exp_ec_ML.loc[
        ~(exp_ec_ML.index.isin(exp_too_short.reset_index().id_ML_datesafe_overlapsafe)),
        :,
    ]

    if display_calibration_limits:
        id_exp_icpms_calibrations = db.query_sql(
            """SELECT id_exp_icpms
               FROM exp_icpms 
               WHERE exp_icpms.id_exp_icpms_calibration_set = %s 
                    AND exp_icpms.type_experiment='calibration'
               ;""",
            params=[int(exp_icpms_ML.iloc[0].id_exp_icpms_calibration_set)],
            con=con,
            method="sqlalchemy",
        ).fetchall()
        data_calibration = db.query_sql(
            """SELECT * 
               FROM data_icpms 
               WHERE id_exp_icpms IN ("""
            + ", ".join(["%s"] * len(id_exp_icpms_calibrations))
            + """);""",
            params=[idx[0] for idx in id_exp_icpms_calibrations],
            con=con,
            method="pandas",
            index_col=[
                "id_exp_icpms",
                "name_isotope_analyte",
                "name_isotope_internalstandard",
                "id_data_icpms",
            ],
        )
        data_calibration_grouped = (
            data_calibration.groupby(
                [
                    "id_exp_icpms",
                    "name_isotope_analyte",
                    "name_isotope_internalstandard",
                ]
            )
            .mean()
            .reset_index()
            .set_index(["name_isotope_analyte", "name_isotope_internalstandard"])
        )
        data_calibration_grouped = data_calibration_grouped.assign(
            a_is__countratio=data_calibration_grouped.counts_analyte
            / data_calibration_grouped.counts_internalstandard
        )

        exp_calibration = data_calibration_grouped.groupby(
            ["name_isotope_analyte", "name_isotope_internalstandard"]
        ).mean()

    a_is_pairs = (
        exp_icpms_ML.index.to_frame()
        .reset_index(drop=True)
        .groupby(
            ["id_exp_icpms", "name_isotope_analyte", "name_isotope_internalstandard"]
        )
        .first()
        .index
    )
    no_axes_white = 1
    no_axes_per_ec_plot = 2
    no_axes_per_icpms_plot = 4
    no_axes_per_a_is_pair = 2 * no_axes_per_icpms_plot + no_axes_white

    with plt.rc_context(
        plot.get_style(
            style="singleColumn",
            increase_fig_height=0.75
            + len(
                a_is_pairs
            ),  # 1+len(a_is_pairs)*no_axes_per_a_is_pair/(2*no_axes_per_ec_plot),
            add_margins={"left": 0.8},
            add_margins_and_figsize={"right": 4},
            fig_margins_between_subplots={"hspace": 0},
            interactive=True,
            add_params={"figure.dpi": figure_dpi},
        )
    ):
        # plot.
        plot_storage = plot.PlotDataStorage(
            "ISTD_fit__id_exp_icpms_" + str(id_exp_icpms), overwrite_existing=True
        )
        exp_ec_ML.export_name = "exp_ec_ML"
        exp_icpms_ML.export_name = "exp_icpms_ML"

        fig = plt.figure()
        gs = gridspec.GridSpec(
            2 * no_axes_per_ec_plot + len(a_is_pairs) * no_axes_per_a_is_pair, 1
        )
        ax1 = fig.add_subplot(gs[0:no_axes_per_ec_plot, 0])
        ax1.export_name = "EC_E_WE__VvsRHE"
        ax2 = fig.add_subplot(
            gs[no_axes_per_ec_plot: 2 * no_axes_per_ec_plot, 0], sharex=ax1
        )
        ax2.export_name = "EC_I__A"
        axs_icpms = []

        for i, a_is_pair in enumerate(a_is_pairs):
            # print(2+i*4, 4+i*4)
            ax_ratio = fig.add_subplot(
                gs[
                    2 * no_axes_per_ec_plot
                    + no_axes_white
                    + i * no_axes_per_a_is_pair : 2 * no_axes_per_ec_plot
                    + no_axes_white
                    + no_axes_per_icpms_plot
                    + i * no_axes_per_a_is_pair,
                    0,
                ],
                sharex=ax1,
            )
            ax_ratio.export_name = "_".join(a_is_pair[1:]) + "_counts_ratio"
            exp_icpms_ML.loc[a_is_pair, "ax_ratio"] = ax_ratio
            if display_exp_icpms_sfc_batch:
                exp_icpms_batch.loc[
                    exp_icpms_batch.reset_index()
                    .set_index(
                        [
                            "id_exp_icpms_sfc_online",
                            "name_isotope_analyte",
                            "name_isotope_internalstandard",
                        ]
                    )
                    .index.isin([a_is_pair]),
                    "ax_ratio",
                ] = ax_ratio
            ax_ratio.text(
                1.02,
                0.95,
                "/".join(a_is_pair[1:]),
                horizontalalignment="left",
                verticalalignment="top",
                # fontsize='x-small',
                transform=ax_ratio.transAxes,
            )
            # ax_ratio.set_title(label='/'.join(a_is_pair[1:]), )
            axs_icpms += [ax_ratio]
            ax_raw = fig.add_subplot(
                gs[
                    2 * no_axes_per_ec_plot
                    + no_axes_white
                    + no_axes_per_icpms_plot
                    + i * no_axes_per_a_is_pair: 2 * no_axes_per_ec_plot
                    + no_axes_white
                    + no_axes_per_icpms_plot * 2
                    + i * no_axes_per_a_is_pair,
                    0,
                ],
                sharex=ax1,
            )
            ax_raw.export_name = "_".join(a_is_pair[1:]) + "_counts_raw"
            exp_icpms_ML.loc[a_is_pair, "ax_raw"] = ax_raw
            axs_icpms += [ax_raw]

        # Hide xaxis label on ax1
        plt.setp(ax1.get_xticklabels(), visible=False)

        cmap = "tab10"
        color_behind_cmap = "black"
        color_ISTD_fit_complete_data = "orangered"
        # .add_column('label', values=exp_ec.loc[:, 'ec_name_technique'])\
        #
        exp_ec_ML.dataset.add_column("color", values=cmap).plot(
            x_col="Timestamp_synchronized__s",
            y_col="E_WE_uncompensated__VvsRHE",
            ax=ax1,
            data=data_ec_ML,
            export_name="EC_E_WE__VvsRHE",
        ).plot(
            x_col="Timestamp_synchronized__s",
            y_col="I__A",
            ax=ax2,
            data=data_ec_ML,
            export_name="EC_I__A",
        )
        ax1.set_ylim([0, 1.5])
        # ax1.legend()

        ax1.text(
            1.02,
            0.95,
            ax1.get_ylabel(),
            horizontalalignment="left",
            verticalalignment="top",
            # fontsize='x-small',
            transform=ax1.transAxes,
        )
        ax1.set_ylabel("")
        ax2.text(
            1.02,
            0.95,
            ax2.get_ylabel(),
            horizontalalignment="left",
            verticalalignment="top",
            # fontsize='x-small',
            transform=ax2.transAxes,
        )
        ax2.set_ylabel("")

        ax1.autoscale(axis="y")
        ax2.autoscale(axis="y")

        exp_icpms_ML = (
            exp_icpms_ML.dataset.add_column("color", values=cmap)
            .plot(
                x_col="t_delaycorrected__timestamp_sfc_pc_synchronized__s",
                y_col="count_ratio",
                ax="ax_ratio",
                data=data_icpms_ML,
                color=color_behind_cmap,
                alpha=0.7,
            )
            .plot(
                x_col="t_delaycorrected__timestamp_sfc_pc_synchronized__s",
                y_col="counts_analyte",
                ax="ax_raw",
                data=data_icpms_ML,
                alpha=0.5,
                axlabel_auto=False,
            )
            .plot(
                x_col="t_delaycorrected__timestamp_sfc_pc_synchronized__s",
                y_col="counts_internalstandard",
                ax="ax_raw",
                data=data_icpms_ML,
                color=color_behind_cmap,
                axlabel_auto=False,
            )
            .fit(
                x_col="t_delaycorrected__timestamp_sfc_pc_synchronized__s",
                y_col="counts_internalstandard",
                y_col_fitted="counts_internalstandard_fitted",
                ax="ax_raw",
                data=data_icpms_ML,
                **{"color": color_ISTD_fit_complete_data}
                if confidence_interval < 1
                else {},  # color='black',
                model=plot.linear_func,  # plot.
                beta0=[0, 0],
                # ifixb=[1, 1],
                confidence_interval=1,
                method="scipy.optimize.curve_fit",  # 'scipy.odr',#
                # label='dummy',
                # label_fit_style=fit_label(description=False, params=False),
                display_fit=True,
            )
            .return_dataset()
        )

        if confidence_interval < 1:
            exp_icpms_ML = (
                exp_icpms_ML.dataset.add_column("color", values=cmap)
                .fit(
                    x_col="t_delaycorrected__timestamp_sfc_pc_synchronized__s",
                    y_col="counts_internalstandard",  # 'dm_dt__ng_s',#'dm_dt_S__ng_s_cm2geo_fc_top_cell_Aideal',
                    y_col_fitted="counts_internalstandard_fitted",
                    ax="ax_raw",
                    data=data_icpms_ML,
                    # color='black',
                    model=plot.linear_func,  # plot.
                    beta0=[0, 0],
                    # ifixb=[1, 1],
                    confidence_interval=confidence_interval,
                    method="scipy.optimize.curve_fit",  # 'scipy.odr',#
                    # label='dummy',
                    # label_fit_style=fit_label(description=False, params=False),
                    display_fit=True,
                )
                .return_dataset()
            )

        if "linear_fit_m" in data_icpms_ML.columns:
            data_icpms_ML.drop(columns=["linear_fit_m", "linear_fit_b"], inplace=True)
        data_icpms_ML = data_icpms_ML.join(
            exp_icpms_ML.loc[:, ["linear_fit_m", "linear_fit_b"]],
            on=[
                "id_exp_icpms",
                "name_isotope_analyte",
                "name_isotope_internalstandard",
                "id_ML_datesafe_overlapsafe",
            ],
        )
        data_icpms_ML = plot_storage.DataSets[-1].data
        data_icpms_ML.loc[:, "a_is_fitted__countratio"] = (
            data_icpms_ML.counts_analyte / data_icpms_ML.counts_internalstandard_fitted
        )

        exp_icpms_ML.dataset.plot(
            x_col="t_delaycorrected__timestamp_sfc_pc_synchronized__s",
            y_col="a_is_fitted__countratio",  # 'dm_dt__ng_s',#'dm_dt_S__ng_s_cm2geo_fc_top_cell_Aideal',
            ax="ax_ratio",
            data=data_icpms_ML,
            # color='black',
            alpha=0.7,
            axlabel_auto=False,
        )

        legendpos = [(1.0, 0.85), "upper left"]
        for ax in [ax for ax in axs_icpms if "counts_ratio" in ax.export_name]:
            handles, labels = [], []
            handler_map_dict = {}
            handles, labels, handler_map_dict = plot.add_legend_handle_label(
                handles,
                labels,
                handler_map_dict,
                handle=plot.legend_handle_line(color=color_behind_cmap),
                label="Count ratio point-by-point",
            )
            handles, labels, handler_map_dict = plot.add_legend_handle_label(
                handles,
                labels,
                handler_map_dict,
                handle=plot.legend_handle_colormap(cmap=cmap),
                label="Count ratio ISTD fit",
                handler_map=plot.HandlerColorLineCollection(numpoints=6),
            )

            if display_calibration_limits:
                handles, labels, handler_map_dict = plot.add_legend_handle_label(
                    handles,
                    labels,
                    handler_map_dict,
                    handle=plot.legend_handle_patch(color="red", alpha=0.5),
                    label="out of calibration range",
                )

            ax.legend(
                handles,
                labels,
                handler_map=handler_map_dict,
                bbox_to_anchor=legendpos[0],
                loc=legendpos[1],
            )
        for ax in [ax for ax in axs_icpms if "counts_raw" in ax.export_name]:
            handles, labels = [], []  # ax4.get_legend_handles_labels()
            handler_map_dict = {}
            handles, labels, handler_map_dict = plot.add_legend_handle_label(
                handles,
                labels,
                handler_map_dict,
                handle=plot.legend_handle_colormap(cmap=cmap),
                label="ISTD fit"
                if not confidence_interval < 1
                else "ISTD fit ("
                + str(confidence_interval * 100)
                + "% conf. interval)",
                handler_map=plot.HandlerColorLineCollection(numpoints=6),
            )
            if confidence_interval < 1:
                handles, labels, handler_map_dict = plot.add_legend_handle_label(
                    handles,
                    labels,
                    handler_map_dict,
                    handle=plot.legend_handle_line(
                        color=color_ISTD_fit_complete_data
                    ),
                    label="ISTD fit of complete data",
                )
            handles, labels, handler_map_dict = plot.add_legend_handle_label(
                handles,
                labels,
                handler_map_dict,
                handle=plot.legend_handle_line(color=color_behind_cmap),
                label="ISTD raw signal",
            )

            # handler_map = {}
            # lc =
            # handles = [lc]
            # handler_map[lc] = HandlerColorLineCollection(numpoints=6)
            # labels = ['IS fit']

            ax.legend(
                handles,
                labels,
                handler_map=handler_map_dict,
                bbox_to_anchor=legendpos[0],
                loc=legendpos[1],
            )
            ax.set_ylabel("Counts")

        if display_exp_icpms_sfc_batch:
            exp_icpms_batch.dataset.add_column("color", values=cmap).set_name(
                "exp_icpms_batch"
            ).plot(
                x_col="t_delaycorrected__timestamp_sfc_pc_synchronized__s",
                y_col="a_is__countratio",
                # 'dm_dt_S__ng_s_cm2geo_fc_top_cell_Aideal',#'dm_dt__ng_s',#'dm_dt_S__ng_s_cm2geo_fc_top_cell_Aideal',
                ax="ax_ratio",
                data=data_icpms_batch,
                axlabel_auto=False,
                marker="|",
            )
        if display_calibration_limits:
            for i, a_is_pair in enumerate(a_is_pairs):
                ax_for_calibration = exp_icpms_ML.loc[a_is_pair, "ax_ratio"].iloc[0]
                ylims = ax_for_calibration.get_ylim()
                xlims = ax_for_calibration.get_xlim()
                calibration_countratio = data_calibration_grouped.loc[
                    a_is_pair[1:], "a_is__countratio"
                ]

                ax_for_calibration.plot(
                    [xlims[0]] * len(calibration_countratio.index),
                    calibration_countratio,
                    marker="x",
                    color="red",
                    linestyle="",
                )
                ax_for_calibration.fill_between(
                    x=xlims,
                    y1=[calibration_countratio.max()] * 2,
                    y2=[
                        ylims[1]
                        if ylims[1] > calibration_countratio.max()
                        else calibration_countratio.max() + 1
                    ]
                    * 2,
                    color="red",
                    alpha=0.5,
                    label="out of calibration",
                )
                ax_for_calibration.fill_between(
                    x=xlims,
                    y1=[
                        ylims[0]
                        if ylims[0] < calibration_countratio.min()
                        else calibration_countratio.min() - 1
                    ]
                    * 2,
                    y2=[calibration_countratio.min()] * 2,
                    color="red",
                    alpha=0.5,
                )
                ax_for_calibration.set_ylim(ylims)
                ax_for_calibration.set_xlim(xlims)

        fig.align_ylabels([ax1, ax2] + axs_icpms)

        # print(plot_storage.name)

        existing_datapoints = db.query_sql(
            """SELECT COUNT(*) 
               FROM data_icpms_internalstandard_fitting 
               WHERE id_exp_icpms=%s
            ;""",
            params=[str(id_exp_icpms)],
            method="sqlalchemy",
        ).fetchall()[0][0]
        button_upload_update = "Update ISTD fit data in database"
        button_upload_insert = "Insert ISTD fit data in database"
        button_upload = widgets.Button(
            description=button_upload_update
            if existing_datapoints > 0
            else button_upload_insert,
            button_style="info" if existing_datapoints > 0 else "success",
            # 'success', 'info', 'warning', 'danger' or ''
            tooltip="Click me",
            icon="check",
            disabled=False,  # self.link_name_analysis,
            layout=Layout(
                width="250px",
            ),
        )
        output_upload = widgets.Output()

        def on_button_upload_clicked(changed_value):
            with output_upload:
                clear_output()
                if not db.user_is_owner(
                    "id_exp_icpms", index_value=id_exp_icpms
                ):  # exp_icpms.name_user.iloc[0] != db.current_user():
                    print(
                        "\x1b[31m",
                        "You better not change data of other users",
                        "\x1b[0m",
                    )
                    return
                print("Update. This can take some seconds...")
                engine = db.connect("hte_processor")
                with engine.begin() as con_update:
                    plot_file_type = "svg"
                    db.sql_update(
                        pd.DataFrame(
                            [
                                [
                                    id_exp_icpms,
                                    t_start_shift__s,
                                    t_end_shift__s,
                                    confidence_interval,
                                    datetime.datetime.now(),
                                    str(
                                        export_path
                                        / (plot_storage.name + "." + plot_file_type)
                                    ),
                                ]
                            ],
                            columns=[
                                "id_exp_icpms",
                                "t_start_shift__s",
                                "t_end_shift__s",
                                "ISTD_fit_confidence_interval",
                                "t_updated_ISTD_fit__timestamp",
                                "file_path_plot_update_ISTD_fit",
                            ],
                        ).set_index("id_exp_icpms"),
                        table_name="exp_icpms_sfc",
                        con=con_update,
                    )

                    if existing_datapoints > 0:
                        db.query_sql(
                            """DELETE FROM data_icpms_internalstandard_fitting 
                                        WHERE id_exp_icpms=%s
                                        ;""",
                            con=con_update,
                            params=[str(id_exp_icpms)],
                            method="sqlalchemy",
                        )
                        print("")
                        print(
                            "\x1b[32m"
                            + "Successfully deleted "
                            + str(existing_datapoints)
                            + " datapoints"
                            + "\x1b[0m"
                        )
                    data_icpms_ML.reset_index().set_index(
                        [
                            "id_exp_icpms",
                            "name_isotope_analyte",
                            "name_isotope_internalstandard",
                            "id_data_icpms",
                        ]
                    ).loc[
                        :,
                        [
                            "counts_internalstandard_fitted",
                        ],
                    ].to_sql(
                        "data_icpms_internalstandard_fitting",
                        con=con_update,
                        if_exists="append",
                    )
                    print(
                        "\x1b[32m"
                        + "Successfully inserted "
                        + str(len(data_icpms_ML.index))
                        + " datapoints"
                        + "\x1b[0m"
                    )
                engine.dispose()
                button_upload.disabled = True
                if export_plotdata:
                    plot_storage.export(
                        fig,
                        export_data=True,
                        plot_format=plot_file_type,
                        auto_overwrite=True,
                        path=export_path,
                    )

        button_upload.on_click(on_button_upload_clicked)
        display(widgets.VBox([button_upload, output_upload]))
        # fig.tight_layout()
        plt.show()
    return plot_storage


def sfc_icpms_integration_analysis(
    id_exp_icpms=None,
    date=None,
    name_user=None,
    id_ML=None,
    t_start_shift__s=-100,
    t_end_shift__s=200,
    figure_dpi=150,
    ec_set_baseline="fixed",
    ec_set_integrationlims="manual",
    icpms_set_baseline=None,
    icpms_set_integrationlims=None,
    add_data_without_corresponding_ec=True,
    data_eis_avg_to_data_ec=False,
    export_plotdata=True,
    export_path=db_config.DIR_REPORTS() / Path("05_ICPMS_integration/"),
    # r'/home/hte_admin/sciebo/jupyter/shared/03_processing_reports/05_ICPMS_integration',
    display_exp_icpms_sfc_batch=False,
):
    """
    Combined EC and ICPMS Integration of SFC-ICPMS experiments.
    Interactive creation of EC datasets (refer in database to exp_ec_dataset and exp_ec_dataset_definer).
    The integration is always combined of an EC dataset and an ICPMS experiment of one analyte-internalstandard pair.
    Results are stored in corresponding database tables (exp_ec_integration, exp_icpms_integration)
    :param id_exp_icpms: index of the icpms experiment to be analyzed
    :param date: date at which the experiment was performed selects icpms by DATE(t_start__timestamp_sfc_pc).
                Enter either date of id_exp_icpms.
    :param name_user: specify if you want to view data of other users
    :param id_ML: subselect ec experiments by id_ML
    :param t_start_shift__s: start time shift of matching icpms data to ec data
                However, consider in regard of good scientific parctice that potential is unknown in that timeframe.
    :param t_end_shift__s: end time shift of matching icpms data to ec data, useful if tailing of icpms signal appears,
                Enter a sufficient large value to include tailed signal into integration analysis
                However, consider in regard of good scientific parctice that potential is unknown in that timeframe.
    :param figure_dpi: reduce to 150 if the figure does not fit your screen
    :param ec_set_baseline: list of possible values
            'fixed': baseline is set as 0
            'auto': baseline based on update_baseline_auto algorithm
            'manual': baseline points set by user manually
    :param ec_set_integrationlims: list of possible values
            'nolims': fixed integration across the compelete window
            'auto': integration limits based on update_baseline_auto algorithm
            'manual': integration limits set by user manually
    :param icpms_set_baseline: list of possible values
            'fixed': baseline is set as 0
            'auto': baseline based on update_baseline_auto algorithm
            'manual': baseline points set by user manually
    :param icpms_set_integrationlims: list of possible values
            'nolims': fixed integration across the compelete window
            'auto': integration limits based on update_baseline_auto algorithm
            'manual': integration limits set by user manually
    :param add_data_without_corresponding_ec: should icpms data which is not matched with ec data be displayed?
    :param data_eis_avg_to_data_ec: using processing.tools_ec.data_eis_avg_to_data_ec to get ec_data for eis experiments
    :param export_plotdata: optional, default True.
        Whether to export the plot and corresponding data in the given path
    :param export_path: optional, str
        path where the plot should be stored. Default path depends on whether run on institute jupyterhub or in mybinder
        as defined in evaluation.utils.db_config
    :param display_exp_icpms_sfc_batch: bool, optional, Default False
        Will search for sfc-icpms batch experiments in exp_icpms_sfc_batch performed simultaneously and
        displays averaged concentration.
    :return: PlotStorage Object
    """

    if icpms_set_integrationlims is None:
        icpms_set_integrationlims = ["auto", "manual"]
    if icpms_set_baseline is None:
        icpms_set_baseline = ["auto", "manual"]
    if type(id_exp_icpms) != int and id_exp_icpms is not None:
        raise ValueError("id_exp_icpms must be a single integer")
    if isinstance(date, str):
        date = str(datetime.datetime.strptime(date, "%Y-%m-%d").date())
    elif date is not None:
        raise ValueError("date must be a date string or None")
    if id_exp_icpms is None and date is None:
        raise Exception("You must suppply either id_exp_icpms or date")
    # if name_user is None:
    #    name_user = db.current_user()
    if not isinstance(name_user, str) and name_user is not None:
        raise ValueError("name_user must be a string or None")
    if isinstance(id_ML, int):
        id_ML = [id_ML]
    if not (isinstance(id_ML, list) or id_ML is None):
        raise ValueError("id_ML must be a single integer, list of integer or None")

    # Data
    engine = db.connect()
    icpms_where = []
    icpms_where_params = []  # {}
    if id_exp_icpms is not None:
        icpms_where += ["id_exp_icpms = %s"]  # ['id_exp_icpms = %(id_exp_icpms)s']
        icpms_where_params += [
            id_exp_icpms
        ]  # icpms_where_params['id_exp_icpms'] = id_exp_icpms
    if date is not None:
        icpms_where += ["DATE(t_start__timestamp_sfc_pc) = %s"]
        icpms_where_params += [date]  # ['date']
    if name_user is not None:
        icpms_where += ["name_user = %s"]
        icpms_where_params += [name_user]  # ['name_user']
    icpms_where = "WHERE " + " AND ".join(icpms_where)
    # print(icpms_where, icpms_where_params)
    # sql_query = '''SELECT * FROM exp_icpms_sfc_expanded ''' + icpms_where+';'
    # for key, value in icpms_where_params.items():
    #    sql_query = sql_query.replace('%('+key+')s', '"'+str(value)+'"')
    query_sep = ("""SELECT * FROM exp_icpms_sfc_expanded """ + icpms_where + ";").split(
        "%s"
    )
    query_print = ""
    for param_no, param in enumerate(icpms_where_params):
        query_print += query_sep[param_no] + str(param)
    query_print += query_sep[-1]
    print(query_print)
    exp_icpms = db.get_exp(
        """SELECT * 
                              FROM exp_icpms_sfc_expanded """
        + icpms_where
        + ";",
        params=icpms_where_params,
    )
    # con=engine,
    # index_col=['id_exp_icpms', 'name_isotope_analyte', 'name_isotope_internalstandard'])  # .iloc[:4]

    if len(exp_icpms.index) == 0:
        raise Exception("No icpms experiments found")
    if exp_icpms.flow_rate_real__mul_min.isna().all():
        raise Exception(
            "There is no flow_rate given for the sfc-icpms experiment selected."
            + "This is necessary to calculate ion concentration."
        )
    if exp_icpms.t_delay__s.iloc[0] == 0:
        print(
            "\x1b[31m",
            "The delay time is set to 0 s. Adjust the delay time before performing integration analysis!",
            "\x1b[0m",
        )
    if exp_icpms.name_user.iloc[0] != db.current_user():
        print(
            "\x1b[33m",
            "View-only: This is data from ",
            exp_icpms.name_user.iloc[0],
            ". Updates are restricted!",
            "\x1b[0m",
        )
    ec_where = []
    if id_ML is not None:
        ec_where += ["id_ML IN (" + ", ".join([str(item) for item in id_ML]) + ")"]
    ec_where = " AND ".join(ec_where) if len(ec_where) > 0 else None
    # print(ec_where)

    match_ec_icpms = exp_icpms.dataset.match_exp_sfc_exp_icpms(
        engine,
        A_geo_cols="fc_top_name_flow_cell_A_opening_ideal__mm2",
        add_cond=ec_where,
    )  # , 'fc_top_name_flow_cell_A_opening_real__mm2' ])
    exp_ec = match_ec_icpms.dataset.get_exp(
        engine, "exp_ec_expanded", index_cols=["id_exp_sfc"]
    )

    data_ec = exp_ec.dataset.get_data(engine, "data_ec_analysis")
    data_icpms = match_ec_icpms.dataset.get_data(
        engine,
        "data_icpms_sfc_analysis",
        join_cols=["id_exp_icpms"],
        index_cols=[
            "id_exp_icpms",
            "name_isotope_analyte",
            "name_isotope_internalstandard",
            "id_data_icpms",
        ],
        t_start_shift__s=t_start_shift__s,
        t_end_shift__s=t_end_shift__s,
        add_data_without_corresponding_ec=add_data_without_corresponding_ec,
        # False makes more sense if subselect an id_ML but lead to errors
    )  #
    if exp_ec.ec_name_technique.isin(["exp_ec_peis", "exp_ec_geis"]).any():
        if data_eis_avg_to_data_ec:
            data_eis = exp_ec.dataset.get_data(engine, "data_eis_analysis")
            data_ec = tools_ec.data_eis_avg_to_data_ec(exp_ec, data_ec, data_eis)
        else:
            print(
                "\x1b[33m",
                "EIS data is not considered by default as data is not time-resolved.\n",
                'Averaged current, potential values can be derived if param "data_eis_avg_to_data_ec" is set to True',
                "\x1b[0m",
            )

    if display_exp_icpms_sfc_batch:
        exp_icpms_batch = db.get_exp(
            """SELECT * 
                             FROM exp_icpms_sfc_batch_expanded 
                             WHERE id_exp_icpms_sfc_online= %s
                             ;""",
            params=[int(id_exp_icpms)],
        )
        # con=engine, index_col=['id_exp_icpms', 'name_isotope_analyte',
        #                    'name_isotope_internalstandard'])  # .iloc[:4]
        data_icpms_batch = exp_icpms_batch.dataset.get_data(
            engine, "data_icpms_sfc_batch_analysis"
        )
        data_ec, data_icpms, data_icpms_batch = plot.synchronize_timestamps_multiple(
            list_data=[data_ec, data_icpms, data_icpms_batch],
            list_timestamp_cols=[
                "Timestamp",
                "t_delaycorrected__timestamp_sfc_pc",
                "t_delaycorrected__timestamp_sfc_pc",
            ],
            list_index_data_ec=0,
        )
    else:
        data_ec, data_icpms = plot.synchronize_timestamps(
            data_ec=data_ec,
            data_icpms=data_icpms,
            timestamp_col_ec="Timestamp",
            timestamp_col_icpms="t_delaycorrected__timestamp_sfc_pc",
        )

    # data_ec, data_icpms, data_icpms_batch = synchronize_timestamps_multiple(
    #    list_data=[data_ec, data_icpms, data_icpms_batch],
    #    list_timestamp_cols=['Timestamp', 't_delaycorrected__timestamp_sfc_pc', 't_delaycorrected__timestamp_sfc_pc'])

    # display(data_icpms)
    with plt.rc_context(
        plot.get_style(
            style="singleColumn",
            increase_fig_height=1.5,
            add_margins_and_figsize={"left": 0.3, "right": 1.2},  # 1.8},
            interactive=True,
            add_params={"figure.dpi": figure_dpi},
        )
    ):
        plot_storage = plot.PlotDataStorage(
            "sfc_icpms_integration", overwrite_existing=True
        )
        # name will be completed within IntegrateContainer
        exp_ec.export_name = "exp_ec"
        exp_icpms.export_name = "exp_icpms"

        fig = plt.figure()
        gs = gridspec.GridSpec(2, 1)
        ax1 = fig.add_subplot(gs[0, 0])
        ax1.export_name = "top_leftAxis"
        ax1r = ax1.twinx()
        ax1r.export_name = "top_rightAxis"
        ax2 = fig.add_subplot(gs[1, 0], sharex=ax1)
        ax2.export_name = "bottom_leftAxis"
        ax2.ticklabel_format(useMathText=True)

        cmap = "tab10"
        exp_ec = (
            exp_ec.dataset.add_column("color", values=cmap)
            .plot(
                x_col="Timestamp_synchronized__s",
                y_col="E_WE_uncompensated__VvsRHE",
                ax=ax1,
                data=data_ec,
                color="grey",
                alpha=0.3,
                export_object=plot_storage,
                export_name="E_WE_uncompensated__VvsRHE",
            )
            .integrate(
                x_col="Timestamp_synchronized__s",
                y_col="I__A",  # 'dm_dt_S__ng_s_cm2geo_fc_top_cell_Aideal',
                y2_col=0,  # 'test_baseline',#0,
                ax=ax1r,
                data=data_ec,
                export_object=plot_storage,
                export_name="EC",
                set_baseline=ec_set_baseline,
                set_integrationlims=ec_set_integrationlims,
                export_plotdata=export_plotdata,
                export_path=export_path,
            )
            .return_dataset()
        )

        exp_icpms = (
            exp_icpms.dataset.add_column(
                "label",
                values=(
                    exp_icpms.index.get_level_values(level=1)
                    + "_"
                    + exp_icpms.index.get_level_values(level=2)
                ).tolist(),
            )
            .add_column("color", values=cmap)
            .integrate(
                x_col="t_delaycorrected__timestamp_sfc_pc_synchronized__s",
                y_col="dm_dt__ng_s",
                y2_col=0,
                ax=ax2,
                data=data_icpms,
                export_object=plot_storage,
                export_name="ICPMS",
                set_baseline=icpms_set_baseline,
                set_integrationlims=icpms_set_integrationlims,
                link_name_analysis=True,
                x_start_shift=t_start_shift__s,
                x_end_shift=t_end_shift__s,
            )
            .return_dataset()
        )

        # exp_icpms_sfc implementation
        # .add_column('color', values=cmap) \
        if display_exp_icpms_sfc_batch:
            exp_icpms_batch = (
                exp_icpms_batch.join(
                    exp_icpms.color,
                    on=[
                        "id_exp_icpms_sfc_online",
                        "name_isotope_analyte",
                        "name_isotope_internalstandard",
                    ],
                )
                .dataset.set_name("exp_icpms_batch")
                .plot(
                    x_col="t_delaycorrected__timestamp_sfc_pc_synchronized__s",
                    y_col="dm_dt__ng_s",
                    # 'dm_dt_S__ng_s_cm2geo_fc_top_cell_Aideal',#'dm_dt__ng_s',#'dm_dt_S__ng_s_cm2geo_fc_top_cell_Aideal',
                    ax=ax2,
                    data=data_icpms_batch,
                    axlabel_auto=False,
                    marker="|",
                )
                .return_dataset()
            )

            engine = db.connect("hte_processor")
            exp_icpms_batch.loc[:, "dropdown_label"] = [
                "_".join([str(value) for value in tup])
                for tup in exp_icpms_batch.index.tolist()
            ]

            dropdown_select_icpmssfcbatch_all = "all"
            dropdown_select_icpmssfcbatch = widgets.Dropdown(
                description="Select ICPMS SCF batch: ",
                options=[dropdown_select_icpmssfcbatch_all]
                + exp_icpms_batch.dropdown_label.tolist(),
                style={"description_width": "initial"},
            )

            def on_dropdown_select_icpmssfcbatch(changed_value):
                if changed_value.old == dropdown_select_icpmssfcbatch_all:
                    print(changed_value.old)
                    [
                        row.ax_plot_objects[0][0].set_alpha(0.3)
                        for index, row in exp_icpms_batch.iterrows()
                    ]
                else:
                    exp_icpms_batch.loc[
                        exp_icpms_batch.dropdown_label == changed_value.old
                    ].ax_plot_objects.iloc[0][0][0].set_alpha(0.3)

                if changed_value.new == dropdown_select_icpmssfcbatch_all:
                    with output_icpmssfcbatch:
                        clear_output()
                    print(changed_value.new)
                    [
                        row.ax_plot_objects[0][0].set_alpha(1)
                        for index, row in exp_icpms_batch.iterrows()
                    ]
                else:
                    row = exp_icpms_batch.loc[
                        exp_icpms_batch.dropdown_label == changed_value.new
                    ]
                    row.ax_plot_objects.iloc[0][0][0].set_alpha(1)
                    with output_icpmssfcbatch:
                        with engine.begin() as con:
                            read_exp_icpms_sfc_batch(
                                con,
                                id_exp_icpms_batch=int(
                                    row.reset_index().iloc[0].id_exp_icpms
                                ),
                            )
                fig.canvas.draw()

            dropdown_select_icpmssfcbatch.observe(
                on_dropdown_select_icpmssfcbatch, "value"
            )

            button_update_icpmssfcbatch = widgets.Button(
                description="Update ICPMS-SFC Batch",
                layout=Layout(
                    width="200px",
                ),
            )

            def read_exp_icpms_sfc_batch(con, id_exp_icpms_batch):
                clear_output()
                # display(row.reset_index().iloc[0].id_exp_icpms)
                display(
                    db.query_sql(
                        """SELECT id_exp_icpms, id_exp_ec_dataset, name_analysis, comment 
                                        FROM exp_icpms_sfc_batch 
                                        WHERE id_exp_icpms = %s ;""",
                        params=[id_exp_icpms_batch],
                        con=con,
                        method="pandas",
                        index_col="id_exp_icpms",
                    )
                )

            def write_exp_icpms_sfc_batch(
                con, id_exp_icpms_batch, id_exp_ec_dataset, name_analysis
            ):
                df_update = pd.DataFrame.from_dict(
                    {
                        "id_exp_icpms": [id_exp_icpms_batch],
                        "id_exp_ec_dataset": [id_exp_ec_dataset],
                        "name_analysis": [name_analysis],
                    }
                ).set_index("id_exp_icpms")
                db.sql_update(df_update, table_name="exp_icpms_sfc_batch", con=con)

            def on_button_update_icpmssfcbatch(changed_value):
                print("clicked")
                with output_icpmssfcbatch:
                    with engine.begin() as con:
                        row = exp_icpms_batch.loc[
                            exp_icpms_batch.dropdown_label
                            == dropdown_select_icpmssfcbatch.value
                        ]
                        EC_IntegrationDataSet = [
                            IntegrationDataSet
                            for IntegrationDataSet in [
                                DataSet
                                for DataSet in plot_storage.DataSets
                                if DataSet.data_type == "IntegrationData"
                            ]
                            if IntegrationDataSet.IntegrateContainer.to_database_table
                            == "exp_ec_integration"
                        ][0]
                        id_exp_icpms_batch = int(row.reset_index().iloc[0].id_exp_icpms)
                        write_exp_icpms_sfc_batch(
                            con,
                            id_exp_icpms_batch=id_exp_icpms_batch,
                            id_exp_ec_dataset=int(
                                EC_IntegrationDataSet.IntegrateContainer.active().exp_row.id_exp_ec_dataset
                            ),
                            name_analysis=EC_IntegrationDataSet.IntegrateContainer.name_analysis_text.value,
                        )
                        read_exp_icpms_sfc_batch(con, id_exp_icpms_batch)
                        print(
                            "\x1b[32m",
                            "Successfully updated exp_icpms_sfc_batch",
                            "\x1b[0m",
                        )

            button_update_icpmssfcbatch.on_click(on_button_update_icpmssfcbatch)

            output_icpmssfcbatch = widgets.Output()

            display(
                widgets.VBox(
                    [
                        widgets.HBox(
                            [dropdown_select_icpmssfcbatch, button_update_icpmssfcbatch]
                        ),
                        output_icpmssfcbatch,
                    ]
                )
            )

        plt.setp(ax1.get_xticklabels(), visible=False)
        ax1.set_xlabel("")

        fig.tight_layout()

        # print(exp_ec.ax_plot_objects.to_numpy(), [line_list[0][0] for line_list in exp_ec.ax_plot_objects.to_numpy()])
        autoscale_E_WE = extra_widgets.button_autoscale(
            description="Autoscale Potential",
            ax=ax1,
            which="y",
            margin=0.05,
            lines=[line_list[0][0] for line_list in exp_ec.ax_plot_objects.to_numpy()],
        )
        display(autoscale_E_WE)
        plt.show()

        return plot_storage


def sfc_icpms_peakfitting(
    sql_ec=None,
    id_exp_ec_dataset=None,
    background_correction=True,
    manual_peak_detect=True,
    datapoints_fit_single_peak=500,
    datapoints_peak_distance=50,
    prominence=0.04,
    maximum_peak_number=15,
    export_path=db_config.DIR_REPORTS() / Path("06_ICPMS_SFC_peakfitting/"),
):
    """
    Routine to perform empirical lognormal peak fitting on ICPMS dissolution curves as introduced in Fiedler et al.
    (see https://doi.org/10.1002/celc.202300373). There is no physical model in the back to explain the peak shape.
    SFC-ICPMS experiments are selected by querying EC experiments (sql_ec) or giving id_exp_ec_dataset
    :param sql_ec: optional, str
        SQL query to select EC experiments from database
    :param id_exp_ec_dataset: optional, str
        instead of sql_ec index of the ec dataset to be analyzed as defined by exp_ec_dataset
    :param manual_peak_detect: bool, Default True
        whether optionally peaks should be added by manually by give the time value of the peak.
    :param background_correction: optional, bool, Default True
        perform an additional lognormal fit on the residual from single peak fits. Usually this is required to receive
        good fit results
    :param datapoints_fit_single_peak:  Amount of datapoints in time matching to a peak tip in icpms_data.
        The default is 500.
    :param datapoints_peak_distance: Amount of datapoints as minimum distance between peaks in icpms_data.
        The default is 50.
    :param prominence: prominence of the peak to detect it automatically as peak.
        Parameter of scipy.signal._peak_finding. Default 0.04.
    :param maximum_peak_number: maximum number of peaks which should be searche for
    :param export_path: optional, str
        path where the plot should be stored. Default path depends on whether run on institute jupyterhub or in mybinder
        as defined in evaluation.utils.db_config
    :return: df_ana_icpms_sfc_fitting, df_ana_icpms_sfc_fitting_peaks
        fitting and peak parameters as uploaded to database
    """
    # Not yet developed
    id_exp_icpms = None
    name_isotope_analyte = None
    name_isotope_internalstandard = None
    exp_ec, data_ec, exp_icpms, data_icpms = db.get_exp_sfc_icpms(
        sql_ec=sql_ec,
        id_exp_ec_dataset=id_exp_ec_dataset,
        id_exp_icpms=id_exp_icpms,
        name_isotope_analyte=name_isotope_analyte,
        name_isotope_internalstandard=name_isotope_internalstandard,
        overlay_cols=["id_exp_ec_dataset"],
        multiple_exp_ec=True,
        multiple_exp_ec_datasets=False,
        multiple_exp_icpms=False,
        multiple_exp_icpms_isotopes=False,
        join_exp_ec_dataset_to_exp_ec=True,
    )

    for index, row in exp_icpms.iterrows():

        print(
            "Analyzing icpms experiment: ", ", ".join([str(val) for val in list(index)])
        )
        print(
            "\x1b[33m",
            "If no plot appears, please consider restarting your kernel. "
            "This can happen if you have run interactive plots beforehand",
            "\x1b[0m",
        )
        # reduce data_icpms to data of the experiment
        data_icpms_selected = data_icpms.loc[index, :]

        # exclude nan values and negative times
        data_icpms_selected = data_icpms_selected.loc[
            (
                (
                    ~data_icpms_selected.t_delaycorrected__timestamp_sfc_pc_synchronized__s.isna()
                )
                & (
                    data_icpms_selected.t_delaycorrected__timestamp_sfc_pc_synchronized__s
                    > 0
                )
                & (~data_icpms_selected.dm_dt_S__ng_s_cm2geo_fc_top_cell_Aideal.isna())
            ),
            :,
        ]
        Fit_SFC_ICP_MS_Dissolution.maximum_peak_number = maximum_peak_number
        Fit_SFC_ICP_MS_Dissolution.savename = "sfc icpms peakfitting"

        fit_output = Fit_SFC_ICP_MS_Dissolution.fit_data(
            data_icpms_selected.t_delaycorrected__timestamp_sfc_pc_synchronized__s,
            data_icpms_selected.dm_dt__ng_s,
            background_correction=background_correction,
            manual_peak_detect=manual_peak_detect,
            datapoints_fit_single_peak=datapoints_fit_single_peak,
            datapoints_peak_distance=datapoints_peak_distance,
            prominence=prominence,
            correlate_with_potential=True,
            time_potential=data_ec.Timestamp_synchronized__s,
            potential=data_ec.E_WE_uncompensated__VvsRHE,
            id_fit=0,
        )  # additional peaks @ 180 450 727

        (
            df_ana_icpms_sfc_fitting,
            df_ana_icpms_sfc_fitting_peaks,
            output_dct,
            plot_dct,
        ) = fit_output

        # adjust indices
        df_ana_icpms_sfc_fitting.index = pd.MultiIndex.from_product(
            [[item] for item in index] + [df_ana_icpms_sfc_fitting.index.values],
            names=exp_icpms.index.names + df_ana_icpms_sfc_fitting.index.names,
        )
        # different method for df_ana_icpms_sfc_fitting_peaks necessary
        df_ana_icpms_sfc_fitting_peaks.loc[:, exp_icpms.index.names] = index
        df_ana_icpms_sfc_fitting_peaks = (
            df_ana_icpms_sfc_fitting_peaks.reset_index().set_index(
                exp_icpms.index.names + df_ana_icpms_sfc_fitting_peaks.index.names
            )
        )

        # create figure
        with plt.rc_context(
            plot.get_style(style="singleColumn", increase_fig_height=1.5)
        ):
            plot_storage = plot.PlotDataStorage(
                "sfc_icpms_fit", overwrite_existing=True
            )
            fig = plt.figure()
            gs = gridspec.GridSpec(3, 1)
            ax_ec = fig.add_subplot(gs[0, 0])
            ax_ms = fig.add_subplot(gs[1:, 0], sharex=ax_ec)

            plt.setp(ax_ec.get_xticklabels(), visible=False)

            ax_ms.set_xlabel("$t$ / s")
            ax_ms.set_ylabel(
                "d$M$ d$t^{-1} s^{-1}_\\mathrm{geo}$ / ng s$^{-1}$ cm$^{-2}$"
            )

            # plot ec data
            if not data_ec.E_WE__VvsRHE.isna().all():
                Ecol = "E_WE__VvsRHE"
                ax_ec.set_ylabel("$E$ / V vs. RHE")
            else:
                Ecol = "E_WE_uncompensated__VvsRHE"
                ax_ec.set_ylabel("$E_{\mathrm{uncompensated}}$ /\nV vs. RHE")
            exp_ec.dataset.plot(
                "Timestamp_synchronized__s",
                Ecol,
                data=data_ec,
                ax=ax_ec,
                color="grey",
                axlabel_auto=False,
            )
            ax_ec.set_xlabel("")

            # plot ms data
            time = (
                data_icpms_selected.t_delaycorrected__timestamp_sfc_pc_synchronized__s
            )
            ax_ms.plot(time, data_icpms_selected.dm_dt__ng_s, ".", label="Data")

            # plot ms fit
            if df_ana_icpms_sfc_fitting.fit_successful.iloc[0]:
                # is not the case if fit failed
                ax_ms.plot(
                    time,
                    Fit_SFC_ICP_MS_Dissolution.multi_lognormal_fit(
                        time,
                        *df_ana_icpms_sfc_fitting_peaks.loc[
                            df_ana_icpms_sfc_fitting_peaks.index.get_level_values(
                                level="fit_type"
                            )
                            == "sum",
                            ["area__ng_cm2", "ln_std", "xc__s"],
                        ].values.flatten(),
                    ),
                    "-",
                    label=df_ana_icpms_sfc_fitting.fit_label.iloc[0],
                    linewidth=2,
                )

                # plot single lognormal functions optimized for the full fit (fit_type = sum or background)
                for index_peak, row_peak in (
                    df_ana_icpms_sfc_fitting_peaks.loc[
                        df_ana_icpms_sfc_fitting_peaks.index.get_level_values(
                            level="fit_type"
                        ).isin(["sum", "background"]),
                        :,
                    ]
                    .reset_index()
                    .iterrows()
                ):
                    yfit_single = Fit_SFC_ICP_MS_Dissolution.lognormal(
                        time, row_peak.area__ng_cm2, row_peak.ln_std, row_peak.xc__s
                    )
                    if row_peak.fit_type == "background":
                        ax_ms.plot(time, yfit_single, ":", label="Background")
                    else:
                        if np.isnan(row_peak.mode_potential_error__VvsRHE) or np.isnan(
                            row_peak.mode_potential__VvsRHE
                        ):
                            labeltxt = "Peak, no potential matched."
                        else:
                            sd = Fit_SFC_ICP_MS_Dissolution.get_significant_digit(
                                row_peak.mode_potential_error__VvsRHE
                            )
                            labeltxt = (
                                "Peak %s: " % row_peak.id_peak
                                + "%s$\\pm$%s V" % (Fit_SFC_ICP_MS_Dissolution.ensure_significant_digit(
                                                        round(row_peak.mode_potential__VvsRHE, sd), sd),
                                                    round(row_peak.mode_potential_error__VvsRHE, sd))
                                + "$_\\mathrm{RHE}$"
                            )
                        ax_ms.plot(time, yfit_single, "--", label=labeltxt)

            ax_ms.legend(fontsize=3, ncol=1, loc="upper left", bbox_to_anchor=(0, -0.1))

            # store plot
            # for end in ['png', 'pdf', 'svg']:
            #    f.savefig(f'{savename}_{material}.{end}', dpi=300)
            plt.tight_layout()
            fig.align_ylabels([ax_ec, ax_ms])

            # Uplpoad Button
            # upload_output = widgets.Output()

            def on_upload_button_clicked(changed_value):
                # with upload_output:
                # clear_output()
                # print('test')

                if not db.user_is_owner(
                    "id_exp_icpms",
                    index_value=int(
                        exp_icpms.index.get_level_values(level="id_exp_icpms")[0]
                    ),
                ):  # exp_icpms.name_user.iloc[0] != db.current_user():
                    print(
                        "\x1b[31m",
                        "You better not change data of other users",
                        "\x1b[0m",
                    )
                    return False

                # return
                engine = db.connect("hte_processor")
                with engine.begin() as con:
                    if np.isnan(
                        df_ana_icpms_sfc_fitting.index.get_level_values(
                            level="id_exp_ec_dataset"
                        )[0]
                    ):
                        if user_input.user_input(
                            text="For uploading fit results, at first a new exp_ec_dataset "
                                 "from selected ec experiments will be created. Continue? \n",
                            dtype="bool",
                            optional=False,
                        ):
                            name_exp_ec_dataset = user_input.user_input(
                                text="Name of the dataset?",
                                dtype="str",
                                optional=False,
                            )
                            pd.DataFrame(
                                exp_ec.index.get_level_values(level="id_exp_sfc")
                            )

                            db.call_procedure(
                                engine,
                                "Reset_Autoincrement",
                                ["exp_ec_datasets", "id_exp_ec_dataset"],
                            )
                            id_exp_ec_dataset_created = int(
                                db.insert_into(
                                    con,
                                    tb_name="exp_ec_datasets",
                                    df=pd.DataFrame.from_dict(
                                        {"name_exp_ec_dataset": [name_exp_ec_dataset]}
                                    ),
                                )["inserted_primary_key"][0]
                            )
                            print(id_exp_ec_dataset_created)
                            exp_ec.index.to_frame().assign(
                                id_exp_ec_dataset=id_exp_ec_dataset_created
                            ).set_index("id_exp_ec_dataset").to_sql(
                                "exp_ec_datasets_definer", con=con, if_exists="append"
                            )

                            # insert new id_exp_ec_dataset value into fitting dataframes
                            for df in [
                                df_ana_icpms_sfc_fitting,
                                df_ana_icpms_sfc_fitting_peaks,
                            ]:
                                index_name = df.index.names
                                df.reset_index(inplace=True)
                                df.id_exp_ec_dataset = id_exp_ec_dataset_created
                                df.set_index(index_name, inplace=True)
                            print(
                                "\x1b[32m",
                                "Successfully inserted new exp_ec_dataset with id: ",
                                id_exp_ec_dataset_created,
                                "\x1b[0m",
                            )
                        else:
                            print(
                                "\x1b[31m",
                                "Insertion canceled by user. "
                                "You need to create an exp_ec_dataset from selected ec experiments",
                                "\x1b[0m",
                            )
                            return False

                    #
                    df_exist = db.query_sql(
                        """SELECT COUNT(*) AS  'exist'
                                    FROM ana_icpms_sfc_fitting 
                                    WHERE id_exp_ec_dataset = %s
                                        AND id_exp_icpms = %s
                                        AND name_isotope_analyte = %s
                                        AND name_isotope_internalstandard = %s
                                        AND id_fit = %s
                                    ;
                                    """,
                        params=list(df_ana_icpms_sfc_fitting.index.values[0]),
                        con=con,
                    )

                    # Check whether there is already a fit in database
                    if df_exist.iloc[0].exist >= 1:
                        if user_input.user_input(
                            text="You already fitted ec dataset of this icpms experiment. "
                                 "Do you want to overwrite old fit? \n",
                            dtype="bool",
                            optional=False,
                        ):
                            print()
                            for name_table in [
                                "ana_icpms_sfc_fitting_peaks",
                                "ana_icpms_sfc_fitting",
                            ]:
                                # print(list(df_ana_icpms_sfc_fitting.index.values[0])[:5])
                                db.query_sql(
                                    """DELETE FROM """
                                    + name_table
                                    + """ WHERE id_exp_ec_dataset = %s
                                                    AND id_exp_icpms = %s
                                                    AND name_isotope_analyte = %s
                                                    AND name_isotope_internalstandard = %s
                                                    AND id_fit = %s
                                                ;""",
                                    params=list(
                                        df_ana_icpms_sfc_fitting.index.values[0]
                                    )[:5],
                                    method="sqlalchemy",
                                    con=con,
                                )
                            print(
                                "\x1b[32m",
                                "Successfully removed old fit",
                                "\x1b[0m",
                            )
                        else:
                            print(
                                "\x1b[31m",
                                "Insertion canceled by user, you have to overwrite old fit to store values",
                                "\x1b[0m",
                            )
                            return False

                    # process data to database compatible format
                    df_ana_icpms_sfc_fitting.manual_peaks = (
                        df_ana_icpms_sfc_fitting.manual_peaks.astype(str).str.strip(
                            "[]"
                        )
                    )
                    df_ana_icpms_sfc_fitting.loc[
                        :, "t_inserted__timestamp"
                    ] = datetime.datetime.now()

                    plot_format = "svg"
                    plot_storage.name = "sfc_icpms_fit_" + "_".join(
                        [str(val) for val in df_ana_icpms_sfc_fitting.index[0]]
                    )
                    df_ana_icpms_sfc_fitting.loc[
                        :, "file_path_plot_sfc_icpms_peakfit"
                    ] = str(export_path / (plot_storage.name + "." + plot_format))

                    # insert fit data
                    df_ana_icpms_sfc_fitting.drop(
                        columns=["fit_label", "fit_successful"]
                    ).to_sql(name="ana_icpms_sfc_fitting", con=con, if_exists="append")
                    df_ana_icpms_sfc_fitting_peaks.to_sql(
                        name="ana_icpms_sfc_fitting_peaks", con=con, if_exists="append"
                    )
                    print(
                        "\x1b[32m",
                        "Successfully inserted fit data",
                        "\x1b[0m",
                    )

                plot_file_type = "svg"

                plot_storage.export(
                    fig,
                    export_data=False,
                    auto_overwrite=True,
                    plot_format=plot_format,
                    path=export_path,
                )
                return True


            display(df_ana_icpms_sfc_fitting)
            display(df_ana_icpms_sfc_fitting_peaks)

            plt.show()
            plt.close("all")

            if user_input.user_input(
                text="Store fitted data in database? \n",
                dtype="bool",
                optional=False,
            ):
                on_upload_button_clicked(True)

    return df_ana_icpms_sfc_fitting, df_ana_icpms_sfc_fitting_peaks
