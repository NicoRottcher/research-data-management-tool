"""
Scripts for calibration of ICP-MS experiments
Created in 2023
@author: Forschungszentrum Jülich GmbH, Nico Röttcher
"""

import pandas as pd
import numpy as np

from pathlib import Path, WindowsPath  # file paths
import sqlalchemy as sql

# install package mysqlclient!
import matplotlib.pyplot as plt
from matplotlib import gridspec

import warnings
import datetime as dt
import os, socket

import sys

# git-synced modules
from evaluation.utils import db
from evaluation.visualization import plot


def calibrate(
    export_folder=Path(
        r"/home/hte_admin/sciebo/jupyter/shared/03_processing_reports/01_icpms_calibration_reports"
    ),
    id_exp_icpms_calibration_set="missing",  # id as
    id_exp_icpms=None,
    export_sql_plot=True,
):
    """
    Run calibration of icpms experiments with defined analyte and internal standard concentration.
    :param export_folder: folder, where to export calibration report
    :param id_exp_icpms_calibration_set: id o the calibration set as defined in database
        or 'missing' will analyze all missing id_exp_icpms_calibration_set
    :param id_exp_icpms: optional instead of id_exp_icpms_calibration_set, index of the icpms experiment
        from which the calibration should be performed
    :param export_sql_plot: whetehr or not to upload results to sql and store a plot.
        False: To just display the calibration
    :return: None
    """

    if id_exp_icpms is not None:
        if not type(id_exp_icpms) == int:
            raise ValueError("id_exp_icpms must be of type int")
        id_exp_icpms_calibration_set = db.query_sql(
            """SELECT id_exp_icpms_calibration_set
                                                       FROM exp_icpms
                                                       WHERE id_exp_icpms = %s
                                                            ; """,
            params=[id_exp_icpms],
            method="pandas",
        ).id_exp_icpms_calibration_set.iloc[0]

    missing_id_exp_icpms_calibration_sets = db.query_sql(
        """SELECT id_exp_icpms_calibration_set
                                                            FROM exp_icpms_calibration_set
                                                            WHERE id_exp_icpms_calibration_set 
                                                                NOT IN (SELECT DISTINCT id_exp_icpms_calibration_set 
                                                                        FROM exp_icpms_calibration_params)
                                                            ; """,
        method="pandas",
    )
    # print(type(id_exp_icpms_calibration_set))
    if type(id_exp_icpms_calibration_set) == str:
        if id_exp_icpms_calibration_set == "missing":
            for index, row in missing_id_exp_icpms_calibration_sets.iterrows():
                calibrate(
                    id_exp_icpms_calibration_set=row["id_exp_icpms_calibration_set"]
                )
        else:
            sys.exit("Not defined " + id_exp_icpms_calibration_set + '. Try: "missing"')
    elif type(id_exp_icpms_calibration_set) == list:
        for missing_id_exp_icpms_calibration_set in id_exp_icpms_calibration_set:
            calibrate(id_exp_icpms_calibration_set=missing_id_exp_icpms_calibration_set)

    elif type(id_exp_icpms_calibration_set) in [int, np.int64]:
        if (
            id_exp_icpms_calibration_set
            not in missing_id_exp_icpms_calibration_sets.loc[
                :, "id_exp_icpms_calibration_set"
            ].tolist()
        ):
            print(
                "Calibration was already performed. Overwriting is not developed. "
                "First delete database entry to recalibrate."
            )
            if export_sql_plot:  # sys.exit(1)
                print(
                    "toggle export_sql_plot=False to view calibration without storing"
                )
                return ""

        print("Analyze calibration set with id ", id_exp_icpms_calibration_set)
        # select experiment parameters
        calibration_exp = (
            db.get_exp(
                """SELECT exp_a_is.*, exp.name_user, exp.name_setup_icpms, 
                                                 DATE(exp.t_start__timestamp_icpms_pc) AS date
                                          FROM exp_icpms_analyte_internalstandard AS exp_a_is
                                          LEFT JOIN exp_icpms AS exp USING(id_exp_icpms)
                                          WHERE exp_a_is.type_experiment = "calibration"
                                            AND exp_a_is.id_exp_icpms_calibration_set = %s; """,
                params=[int(id_exp_icpms_calibration_set)],
                name_table="exp_icpms_analyte_internalstandard",
            )
            .reset_index()
            .sort_values(
                by=[
                    "id_exp_icpms_calibration_set",
                    "name_isotope_analyte",
                    "name_isotope_internalstandard",
                    "c_analyte__mug_L",
                ]
            )
            .set_index(
                [
                    "name_isotope_analyte",
                    "name_isotope_internalstandard",
                    "id_exp_icpms",
                ]
            )
        )
        # select experiment icpms data
        calibration_rawdata = db.get_data(calibration_exp, "data_icpms")

        # transform data type
        calibration_exp.loc[:, "c_analyte__mug_L"] = calibration_exp.loc[
            :, "c_analyte__mug_L"
        ].astype(float)
        calibration_exp.loc[:, "id_exp_icpms_calibration_set"] = calibration_exp.loc[
            :, "id_exp_icpms_calibration_set"
        ].astype(str)

        # Reindex
        calibration_exp = calibration_exp.reset_index().set_index(
            [
                "id_exp_icpms_calibration_set",
                "name_isotope_analyte",
                "name_isotope_internalstandard",
                "id_exp_icpms",
            ]
        )
        calibration_rawdata = pd.concat(
            {str(id_exp_icpms_calibration_set): calibration_rawdata},
            names=["id_exp_icpms_calibration_set"],
        )

        # calculate count_ratio
        calibration_rawdata.loc[:, "count_ratio"] = (
            calibration_rawdata.loc[:, "counts_analyte"]
            / calibration_rawdata.loc[:, "counts_internalstandard"]
        )

        # calculate mean and standard deviation of rawdata counts
        calibration_data = calibration_exp.join(
            calibration_rawdata.loc[
                :, ["counts_analyte", "counts_internalstandard", "count_ratio"]
            ]
            .groupby(
                level=[
                    "id_exp_icpms_calibration_set",
                    "name_isotope_analyte",
                    "name_isotope_internalstandard",
                    "id_exp_icpms",
                ]
            )
            .mean()
        ).join(
            calibration_rawdata.loc[
                :, ["counts_analyte", "counts_internalstandard", "count_ratio"]
            ]
            .groupby(
                level=[
                    "id_exp_icpms_calibration_set",
                    "name_isotope_analyte",
                    "name_isotope_internalstandard",
                    "id_exp_icpms",
                ]
            )
            .std(),
            rsuffix="_std",
        )
        display(calibration_data)

        calibration_data_a_is_pairs = (
            calibration_exp.loc[:, "type_experiment"]
            .reset_index()
            .drop(columns=["id_exp_icpms"])
            .groupby(
                [
                    "id_exp_icpms_calibration_set",
                    "name_isotope_analyte",
                    "name_isotope_internalstandard",
                ]
            )
            .min()
        )

        for index, row in calibration_data_a_is_pairs.iterrows():
            # print(index)
            # display(calibration_data.loc[(index, ), :])
            calibration_a_is_pair = calibration_data_a_is_pairs.loc[
                [
                    index,
                ],
                :,
            ]
            calibration_data_a_is = calibration_data.loc[index + (slice(None),), :]
            if (len(calibration_data_a_is.index)) == 1:
                print(
                    "\x1b[31m",
                    "Cannot calibrate with only one data point. "
                    "Please check that id_exp_icpms_calibration_set is set correctly for each experiment.",
                    "\x1b[0m",
                    "\n\n",
                )
                continue
            with plt.rc_context(
                plot.get_style(
                    style="singleColumn",
                    increase_fig_height=2.8,
                    # add_margins_between_subplots={'hspace': 0.6},
                    add_params={"legend.fontsize": 6},
                )
            ):
                # init figure
                fig = plt.figure()
                gs = gridspec.GridSpec(14, 1)
                subgs = gs[1:4, 0].subgridspec(
                    2, len(calibration_data_a_is.index), hspace=0.3, wspace=1
                )

                # title

                ax_title = fig.add_subplot(gs[0, 0])
                ax_title.axis("off")

                ax_title.text(
                    x=0.98,
                    y=0.9,
                    s="$Calibration$ $set$ "
                    + str(id_exp_icpms_calibration_set)
                    + "\n$measured$ $by$ "
                    + "$and$ ".join(calibration_data.name_user.unique())
                    + "\n$recorded$ $with$ "
                    + "$and$ ".join(calibration_data.name_setup_icpms.unique())
                    + "\n$at$ "
                    + "$and$ ".join(
                        [
                            date_val.strftime("%d-%b-%Y")
                            for date_val in pd.to_datetime(calibration_data.date.unique())
                        ]
                    ),
                    fontsize=5,
                    horizontalalignment="right",
                )

                # show raw data
                for enum, (index_a_is, row_a_is) in enumerate(calibration_data_a_is.iterrows()):
                    # print(index_a_is, calibration_data_a_is.loc[[index_a_is, ], :])
                    ax_raw_is = fig.add_subplot(subgs[0, enum])
                    ax_raw_a = fig.add_subplot(subgs[1, enum])
                    calibration_data_a_is.loc[[index_a_is, ], :].dataset.add_column(
                        "label", values="Internal Standard"
                    ).plot(
                        x_col="t__s",
                        y_col="counts_internalstandard",
                        data=calibration_rawdata,
                        color="tab:orange",
                        ax=ax_raw_is,
                    ).add_column(
                        "label", values="Analyte"
                    ).plot(
                        x_col="t__s",
                        y_col="counts_analyte",
                        data=calibration_rawdata,
                        color="tab:blue",
                        ax=ax_raw_a,
                    )
                    # calibration_data_a_is.loc[:, 'c_analyte__mug_L'].astype(str) + ' µg L$^{-1}$')\

                    ax_raw_is.text(
                        1,  # x
                        1.3,  # y
                        (
                            "$c_{\mathrm{a}}$ / µg L$^{-1}$ = "
                            if index_a_is == calibration_data_a_is.index[0]
                            else ""
                        )
                        + str(
                            row_a_is["c_analyte__mug_L"]
                        ),  # + (' µg L$^{-1}$' if index_a_is == calibration_data_a_is.index[-1] else ''),  # label
                        transform=ax_raw_is.transAxes,
                        horizontalalignment="right",
                        verticalalignment="bottom",
                        fontsize=6,  # 15 * 0.4384
                    )

                    ax_raw_a.ticklabel_format(scilimits=(-5, 4))
                    ax_raw_a.yaxis.offsetText.set_fontsize(5)
                    ax_raw_is.ticklabel_format(scilimits=(-5, 4))
                    ax_raw_is.yaxis.offsetText.set_fontsize(5)
                    ax_raw_a.set_ylabel("")
                    ax_raw_is.set_ylabel("counts")
                    ax_raw_is.set_xlabel("")
                    ax_raw_is.set_xticklabels("")
                    ax_raw_is.set_ylim(
                        [
                            calibration_data_a_is.loc[
                                :, "counts_internalstandard"
                            ].min()
                            * 0.9,
                            calibration_data_a_is.loc[
                                :, "counts_internalstandard"
                            ].max()
                            * 1.1,
                        ]
                    )
                    # Make ticklabels smaller
                    ax_raw_a.tick_params(axis="both", which="major", labelsize=5)
                    ax_raw_is.tick_params(axis="both", which="major", labelsize=5)

                    if enum == 0:
                        ax_raw_is_0 = ax_raw_is
                        ax_raw_a_0 = ax_raw_a
                        handles_is, labels_is = ax_raw_is.get_legend_handles_labels()
                        handles_a, labels_a = ax_raw_a.get_legend_handles_labels()
                        ax_raw_is.legend(
                            handles_a + handles_is,
                            labels_a + labels_is,
                            bbox_to_anchor=(-0.8, 1.4),
                            loc="lower left",
                            framealpha=0,
                        )
                        # ylims = ax_raw.get_ylim()
                    else:
                        ax_raw_is.set_ylabel("")
                        # ax_raw.set_yticklabels([])
                        # ax_raw.set_ylim(ylims)

                # empty plot for common y label of _ and _is
                # ax_raw_a_is = fig.add_subplot(gs[0, 0])
                # ax_raw_a_is.set_ylabel('Counts')
                # for pos in ['right', 'top', 'bottom', 'left']:
                #    ax_raw_a_is.spines[pos].set_visible(False)
                # ax_raw_a_is.patch.set_facecolor('none')
                # ax_raw_a_is.tick_params(bottom=False, top=False, left=False,right=False)
                # ax_raw_a_is.set_xticklabels([])
                # ax_raw_a_is.set_yticklabels([])

                # calibration plot + fit
                ax_fit = fig.add_subplot(gs[5:9, :])
                calibration_a_is_pair = (
                    calibration_a_is_pair.dataset.add_column(
                        "label",
                        values="Calibration set: "
                        + calibration_a_is_pair.index.map(", ".join),
                    )
                    .plot(
                        x_col="c_analyte__mug_L",
                        y_col="count_ratio",
                        yerr_col="count_ratio_std",
                        data=calibration_data,
                        marker=".",
                        linestyle="",
                    )
                    .fit(
                        model=plot.linear_func,
                        x_col="c_analyte__mug_L",
                        y_col="count_ratio",
                        yerr_col="count_ratio_std",
                        beta0=[1, 0],
                        ifixb=[1, 1],
                        method="scipy.odr",  # or 'scipy.optimize.curve_fit',
                        data=calibration_data,
                        linestyle="-",
                        axlabel_auto=False,
                        label_fit_overwrite=True,
                        label_fit_style=plot.create_fit_label(
                            description=True,
                            params=True,
                            rsquared=True,
                            err_considered=True,
                        ),
                    )
                    .fit(
                        model=plot.linear_func,
                        x_col="c_analyte__mug_L",
                        y_col="count_ratio",
                        yerr_col="count_ratio_std",
                        beta0=[1, 0],
                        # ifixb=[1, 1],
                        method="scipy.optimize.curve_fit",  #'scipy.odr',  #
                        data=calibration_data,
                        linestyle="-",
                        axlabel_auto=False,
                        label_fit_overwrite=True,
                        label_fit_style=plot.create_fit_label(
                            description=True,
                            params=True,
                            rsquared=True,
                            err_considered=True,
                        ),
                    )
                    .fit(
                        model=plot.linear_func,
                        x_col="c_analyte__mug_L",
                        y_col="count_ratio",
                        # yerr_col='count_ratio_std',
                        beta0=[1, 0],
                        # ifixb=[1, 1],
                        method="scipy.optimize.curve_fit",  # 'scipy.odr',  #
                        data=calibration_data,
                        linestyle="-",
                        axlabel_auto=False,
                        label_fit_overwrite=True,
                        label_fit_style=plot.create_fit_label(
                            description=True,
                            params=True,
                            rsquared=True,
                            err_considered=True,
                        ),
                    )
                    .return_dataset()
                )

                # change fit to curve_fit weighted
                # https://scipython.com/book/chapter-8-scipy/examples/weighted-and-non-weighted-least-squares-fitting/
                # caluclate R_squar
                # https://stackoverflow.com/questions/19189362/getting-the-r-squared-value-using-curve-fit

                ax_fit.legend(
                    fontsize=5, bbox_to_anchor=(0.02, -0.24), loc="upper left"
                )
                fig.align_ylabels(
                    [ax_fit, ax_raw_is_0]
                )  # ax_raw_a_is])#ax_raw_is_0, ax_raw_a_0])

                export_file_path = str(
                    export_folder
                    / str(
                        [
                            f"{id_exp_icpms_calibration_set}_{name_isotope_analyte}_{name_isotope_internalstandard}.pdf"
                            for id_exp_icpms_calibration_set, name_isotope_analyte, name_isotope_internalstandard
                                in calibration_a_is_pair.index
                        ][0]
                    )
                )
                # plt.tight_layout() # doesn't work with legend below plot
                if export_sql_plot:
                    plt.savefig(export_file_path, bbox_inches="tight")
                    plt.savefig(export_file_path[:-4] + ".svg", bbox_inches="tight")
                    print(
                        "\x1b[32m",
                        "Successfully saved result plot in: ",
                        export_file_path,
                        "\x1b[0m",
                    )
                else:
                    print("\x1b[31m", "Plot not saved!", "\x1b[0m")
                plt.show()

            # Prepare SQL insertion
            rename_columns = {
                "linear_fit_m": "calibration_slope__countratio_mug_L",
                "linear_fit_m_sd": "delta_calibration_slope__countratio_mug_L",
                "linear_fit_b": "calibration_intercept__countratio",
                "linear_fit_b_sd": "delta_calibration_intercept__countratio",
                "linear_fit_Rsquared": "Rsquared",
                #'linear_fit_ResVar': 'Rsquared',  # not correct need to be adjusted!
                "fit_method": "calibration_method",
            }
            calibration_a_is_pair = calibration_a_is_pair.rename(
                columns=rename_columns
            ).loc[
                :, list(rename_columns.values())
            ]  # + ['file_path_calibration_plot']
            calibration_a_is_pair.loc[
                :, "file_path_calibration_plot"
            ] = export_file_path
            calibration_a_is_pair.loc[
                :, "name_computer_inserted_data"
            ] = socket.gethostname()  # os.environ['COMPUTERNAME']
            calibration_a_is_pair.loc[
                :, "t_inserted_data__timestamp"
            ] = dt.datetime.now()
            display(calibration_a_is_pair)

            if export_sql_plot:
                with db.connect("hte_icpms_calibrater").begin() as con:
                    # print('Not stored')

                    calibration_a_is_pair.to_sql(
                        "exp_icpms_calibration_params", con=con, if_exists="append"
                    )
                    print(
                        "\x1b[32m",
                        "Successfully inserted calibration data for id_calibration_set = "
                        + str(id_exp_icpms_calibration_set),
                        "\x1b[0m",
                        "\n\n",
                    )
            else:
                print("\x1b[31m", "Data not inserted into database", "\x1b[0m")


# Todo
# - view with data to plot calibrated data
# - save calibration plot on server and store path to figure in file_path_calibration_plot

if __name__ == "__main__":
    calibrate()
