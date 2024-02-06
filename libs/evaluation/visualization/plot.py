"""
Scripts for plotting utils and template settings
Created in 2023
@author: Forschungszentrum Jülich GmbH, Nico Röttcher
"""

import inspect
import sys
import warnings
import weakref  # keep track of instances of a class
from pathlib import Path

import matplotlib as mpl
import matplotlib.lines
import matplotlib.lines as mlines  # custom legend entries
import matplotlib.patches as mpatches  # custom legend entries
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sqlalchemy as sql  # Handling python - sql communication
from IPython.display import Javascript
from ipywidgets import *
from matplotlib.collections import LineCollection
from matplotlib.colors import ListedColormap  # for custom colormaps
from matplotlib.legend_handler import HandlerLineCollection
from scipy.odr import ODR, RealData, Model
from scipy.optimize import curve_fit
from scipy.stats import norm

from evaluation.processing import integration
from evaluation.utils import db
from evaluation.utils import user_input  # import user_input

# from importlib import reload
# reload(integration)

display(
    Javascript(
        """
                let b = document.createElement('pre');
                """
    )
)

custom_cmaps = {
    "pub_blues": [
        [179 / 256, 205 / 256, 224 / 256, 1],
        [1 / 256, 31 / 256, 75 / 256, 1],
    ],
    "pub_reds": np.array([[250, 137, 161, 256], [78, 0, 20, 256]]) / 256,
}  # rgba format: red, green, blue, alpha


def get_style(
    style="singleColumn",
    fig_size=None,
    fig_margins=None,
    fig_margins_between_subplots=None,
    add_margins=None,
    add_margins_and_figsize=None,
    add_margins_between_subplots=None,
    increase_fig_height=1,
    add_params=None,
    print_info=False,
    interactive=False,
):
    """
    Set style parameter for matplotlib plot. For size and margins use predefined style and adjust with
    absolute values (fig_size, fig_margins, fig_margins_between_subplots)
    or add relative values (add_margins, add_margins_and_figsize, add_margins_between_subplots)
    jupyters non-interactive backend might not display the extra white space
    you will have to check the exported file specifically
    Apply the style template like this:

    import matplotlib.pyplot as plt
    with plt.rc_context(plot.get_style(style='singleColumn',
                                       #fig_size={'width':6, 'height':4},
                                       #add_margins_and_figsize= {'left': 0.1,  },
                                       #interactive =True,
                                       )):
        # place your matplotlib figure here

    :param style: str or dict
            # 'singleColumn': single column figure in publications
            # 'doubleColumn': double column figure in publications
            # 'singleColumn_thesis': adds empty space to left and right so that the figure is centered in Latex
                # and the legend is still displayed
    :param fig_size: dict or None
        set absolute size of the matplotlib figure in cm
        default for 'singleColumn': {'width': 8, 'height': 5}
        default for 'doubleColumn': {'width': 16.8, 'height': 5}
    :param fig_margins: dict or None
        set absolute size of figure margins
        default: {'left': 1, 'right': 0.2, 'bottom': 0.8, 'top': 0.2}
    :param fig_margins_between_subplots:
        absolute margin between subplots in cm
        default: {'wspace': 0.2, 'hspace': 0.2}
    :param add_margins: dict or None
        adding margins to the figure by reducing axis size, values in cm
        this can change aspect ratio of axes
        default absolute margins are: {'left': 1, 'right': 0.2, 'bottom': 0.8, 'top': 0.2}
    :param add_margins_and_figsize: dict or None
        adding margins to the figureby increasing axis size, values in cm
        this will keep aspect ratio of axes
        default absolute margins are: {'left': 1, 'right': 0.2, 'bottom': 0.8, 'top': 0.2}
    :param add_margins_between_subplots:
        add margins between subplots, value is added, value in cm
        default absolute margins between subplots are: {'wspace': 0.2, 'hspace': 0.2}
    :param increase_fig_height: 1
        figure height is increased by factor x
    :param add_params={}, dict
        change manually specific style parameter.
        A list of all possible parameters can be fouund here:
        https://matplotlib.org/stable/users/explain/customizing.html
    :param print_info=False
        set to true to get extra info of the figure
    :param interactive: bool
        use an interactive backend or not
    :return: params
        params: style params of figure
    """

    # :param externalWindow: use a mpl backend open a plot in external window or inline
    # if externalWindow:
    #    mpl.use('TkAgg')

    if add_params is None:
        add_params = {}
    if add_margins_between_subplots is None:
        add_margins_between_subplots = {}
    if add_margins_and_figsize is None:
        add_margins_and_figsize = {}
    if add_margins is None:
        add_margins = {}
    if fig_margins_between_subplots is None:
        fig_margins_between_subplots = {}
    if fig_margins is None:
        fig_margins = {}
    if fig_size is None:
        fig_size = {}

    if interactive:
        matplotlib.use("module://ipympl.backend_nbagg")
    else:
        matplotlib.use("module://matplotlib_inline.backend_inline")
    # mpl.use('module://ipykernel.pylab.backend_inline')
    scaling = 0.4384  # scaling factor from cm to inch

    # Set default sizes and margins
    if style == "singleColumn":
        default_fig_size = {"width": 8, "height": 5}  # cm
        default_fig_margins = {"left": 1, "right": 0.2, "bottom": 0.8, "top": 0.2}  # cm
        default_fig_margins_between_subplots = {"wspace": 0.2, "hspace": 0.2}  # cm

    elif style == "doubleColumn":
        default_fig_size = {"width": 16.8, "height": 5}  # cm
        default_fig_margins = {"left": 1, "right": 0.2, "bottom": 0.8, "top": 0.2}  # cm
        default_fig_margins_between_subplots = {"wspace": 0.2, "hspace": 0.2}  # cm

    elif style == "singleColumn_thesis":
        default_fig_size = {
            "width": 16.8
            * 0.82,  # reduced due to larger page margins in latex document
            "height": 5,
        }
        # original 0.855#inches
        # --always as large as page to avoid cutting of legend
        # -- original figsize via distance_to_plot
        default_fig_margins = {
            "left": 1 + 2.488,
            "right": 0.2 + 2.488 + 0.8,
            "bottom": 0.8,
            "top": 0.2,
        }  # cm
        default_fig_margins_between_subplots = {"wspace": 0.2, "hspace": 0.2}  # cm
    else:
        print("Style ", style, ' not known! Try "singleColumn".')
        sys.exit(1)

    # adjust sizes and margins by absolute values
    def adjust_sizes(default, manual_set):
        return_set = {}
        for key_default in default.keys():
            return_set[key_default] = (
                manual_set[key_default] if key_default in manual_set.keys() else default[key_default]
            )
        return return_set

    figure_size = adjust_sizes(default_fig_size, fig_size)
    figure_margins = adjust_sizes(default_fig_margins, fig_margins)
    between_subplots = adjust_sizes(
        default_fig_margins_between_subplots, fig_margins_between_subplots
    )

    # adjust margins by relative values
    # add_margins
    for key, value in add_margins.items():
        figure_margins[key] = figure_margins[key] + value

    # add_margins_and_figsize
    for key, value in add_margins_and_figsize.items():
        width_height = "width" if key in ["right", "left"] else "height"
        figure_size[width_height] = figure_size[width_height] + value
        figure_margins[key] = figure_margins[key] + value

    # add_margins_between_subplots
    for key, value in add_margins_between_subplots.items():
        # width_height = 'width' if key in ['right', 'left'] else 'height'
        # figure_size[width_height] = figure_size[width_height]-value
        between_subplots[key] = between_subplots[key] + value

    # increase_fig_height
    figure_size["height"] = figure_size["height"] * increase_fig_height
    if print_info:
        print("figure size: ", figure_size)
        print("figure margins:", figure_margins)
        print("between subplots:", between_subplots)

    params = {
        # A list of all parameters: https://matplotlib.org/stable/tutorials/introductory/customizing.html
        # Figure
        "figure.figsize": (
            figure_size["width"] * scaling,
            figure_size["height"] * scaling,
        ),
        # 8:5 aspect ratio for whole figure
        # The figure subplot parameters.  All dimensions are a fraction of the figure width and height.
        "figure.dpi": 300,  # figure dots per inch
        "figure.subplot.left": figure_margins["left"] / figure_size["width"],
        # 0.125  # the left side of the subplots of the figure
        "figure.subplot.right": 1 - (figure_margins["right"] / figure_size["width"]),
        # 0.9    # the right side of the subplots of the figure
        "figure.subplot.bottom": figure_margins["bottom"] / figure_size["height"],
        # 0.11   # the bottom of the subplots of the figure
        "figure.subplot.top": 1 - (figure_margins["top"] / figure_size["height"]),
        # 0.88   # the top of the subplots of the figure
        # Space between subplots should be handled by gridspec
        "figure.subplot.wspace": between_subplots["wspace"] / figure_size["width"],
        # the amount of width reserved for space between subplots,
        # expressed as a fraction of the average axis width
        "figure.subplot.hspace": between_subplots["hspace"] / figure_size["height"],
        # the amount of height reserved for space between subplots,
        # expressed as a fraction of the average axis height
        # Font
        "font.sans-serif": "Arial"
        if db.MYSQL
        else "DejaVu Sans",  # Arial not available ein mybinder
        "font.family": "sans-serif",  # 'serif',#
        "font.size": 20 * scaling,  # Set font size to 20pt Arial
        "axes.labelsize": 18 * scaling,  # -> axis labels
        "legend.fontsize": 16 * scaling,  # legend font size
        # linewidth
        "lines.linewidth": 1.5 * scaling,  # line thickness
        "lines.markeredgewidth": 1.5 * scaling,
        # the line width around the marker symbol, also width of errorbar.cap
        "axes.linewidth": 1.5 * scaling,
        "patch.linewidth": 1.5 * scaling,  # edge width in points.
        "hatch.linewidth": 1.5
        * scaling,  # edge width in points. Hatch = shape/lines/.. inside a 2D area
        # Grid
        "axes.grid": False,  # display grid or not
        "grid.linewidth": 1.5 * scaling,  # grid line width
        "grid.linestyle": "--",  # solid
        "grid.alpha": 0.8,  # solid
        # Ticks
        "xtick.major.size": 5.8 * scaling,  # 3.5     # major tick size in points
        "xtick.minor.size": 3 * scaling,  # minor tick size in points
        "xtick.labelsize": 18 * scaling,  # x tick labels
        "xtick.top": True,  # draw ticks on the top side
        "xtick.bottom": True,  # draw ticks on the bottom side
        "xtick.major.width": 1.5 * scaling,  # x tick width
        "xtick.minor.width": 1.5 * scaling,  # x tick width
        "xtick.minor.visible": True,  # visibility of minor ticks on x-axis
        "xtick.direction": "in",  # direction: {in, out, inout}
        "ytick.major.size": 5.8 * scaling,  # major tick size in points
        "ytick.minor.size": 3 * scaling,  # minor tick size in points
        "ytick.left": True,  # draw ticks on the left side
        "ytick.right": True,  # draw ticks on the right side
        "ytick.labelsize": 18 * scaling,  # y tick labels
        "ytick.major.width": 1.5 * scaling,  # y tick width
        "ytick.minor.width": 1.5 * scaling,  # y tick width
        "ytick.minor.visible": True,  # visibility of minor ticks on x-axis
        "ytick.direction": "in",  # direction: {in, out, inout}
        "lines.markersize": 9 * scaling,  # marker size
        "errorbar.capsize": 2,  # length of end cap on error bars in pixels
        # ticklabel scientific notation
        # (https://matplotlib.org/3.4.3/api/_as_gen/matplotlib.axes.Axes.ticklabel_format.html#matplotlib.axes.Axes.ticklabel_format)
        # 'axes.formatter.limits': [-5, 6], # From which power on to use scientific notation Default [-5, 6]
        # 'axes.formatter.useoffset': True, # Whether top use offset or not
        #                                   # for example: 1.1000052, 1.1000053 --> transform to (2,3)*e-6 + 1.1
        "axes.formatter.use_mathtext": True,  # Use mathtext format 10^-2 instead of e-5, Default False
        # Legend
        "legend.frameon": True,  # if True, draw the legend on a background patch
        "legend.framealpha": 0.8,  # legend patch transparency
        "legend.edgecolor": "w",  # background patch boundary color
        # Savefig
        # 'savefig.bbox':      'standard',    # {tight, standard}
        # tight: changes the totalfigsizes and does not cut away legend
        # 'tight' is incompatible with pipe-based animation
        # backends (e.g. 'ffmpeg') but will work with those
        # based on temporary files (e.g. 'ffmpeg_file')
        # 'savefig.pad_inches':   0.1,      # Padding to be used when bbox is set to 'tight'
        "savefig.dpi": 2000,
        # Backend settings
        # 'mathtext.fontset': 'dejavuserif',
        "text.usetex": False,
        "pgf.texsystem": "pdflatex",
        # 'pgf.preamble': ''
    }

    # user adjustments to rc parameters
    for key, value in add_params.items():
        params[key] = value

    return params


def colname_add_subscript(colname, subscript):
    """
    add subscript to column name. So that: column_subscript__unit --> column_subscript_anothersubscript__unit
    :param colname: str
        name of the column
    :param subscript: str
        subscript to be added
    :return: str
        column name with subscript before the unit separator '__'
    """
    return (
        colname.split("__")[0]
        + "_"
        + subscript
        + "__"
        + "__".join(colname.split("__")[1:])
    )


def get_axis_label(col_name):
    """
    Translate database column name to plot axis label using matploltib latex syntax.
    Translation done on basis of
        manual_col_names,
        algorithm for gravimetric current density columns
        algorithm for geometric columns (current density, area, mass flow rate) as defined y plot.get_geo_column_label
        algorithm for synchronized times
        defined in database in VIEW documentation_columns
    :param col_name: str
        column name in database name syntax
    :return: str
        column name in matplotlib latex axis label syntax
    """
    # print(col_name)
    manual_col_names = {
        "count_ratio": "Counts$_{\mathrm{analayte}}$ / Counts$_{\mathrm{ISTD}}$ ",
        "a_is__countratio": "Counts$_{\mathrm{analayte}}$ / Counts$_{\mathrm{ISTD}}$ ",
    }

    # manual colnames
    if col_name in manual_col_names.keys():
        return manual_col_names[col_name]

    # special colnames
    if "j__mA_mg" == col_name[:8]:
        col_name_splitted = col_name.split("_")
        material = "_".join(col_name_splitted[4: col_name_splitted.index("geo")])
        geo = "_".join(col_name_splitted[col_name_splitted.index("geo"):])
        geo_label = get_axis_label("j__mA_cm2" + geo)
        if "$j_\mathrm{geo" in geo_label:
            geo_label = geo_label.split("{")[-2].split("}")[0].replace("geo", "")
            return str(
                "$j_\mathrm{mass}$ / mA mg$_\mathrm{"
                + material
                + "\ "
                + geo_label
                + "}^{-1}$"
            )
        else:
            return col_name
    if "synchronized__s" == col_name[-15:]:
        return "$t_\mathrm{synced}$ / s"

    if col_name in geo_columns.values:
        return get_geo_column_label(col_name)

    # colnames stored in database
    con = db.connect()
    col_names = [col_name]

    if col_name[-7:] == "_fitted":
        col_names += [col_name[-7:]]
    axislabel = db.query_sql(
        """SELECT DISTINCT  name_axislabel__latex 
                                FROM hte_data.documentation_columns 
                                WHERE name_column IN ("""
        + ", ".join(["%s"] * len(col_names))
        + """);""",
        params=col_names,
        con=con,
        method="sqlalchemy",
    ).fetchall()
    axislabel_filtered = list(
        set([i for i in axislabel if i[0] is not None])
    )  # removes duplicates and None
    # print(axislabel, axislabel_filtered, len(axislabel_filtered))
    if len(axislabel_filtered) == 0:
        if len(axislabel) > 0:
            warnings.warn("Axislabel entry missing in database for " + col_name)
        # else:
        #    warnings.warn('No corresponding axislabel found in database for ' + col_name)
        return str(col_name)
    elif len(axislabel_filtered) == 1:
        return str(axislabel_filtered[0][0])
    elif len(axislabel_filtered) > 1:
        warnings.warn(
            "Multiple axis labels available for "
            + col_name
            + ": "
            + str([el[0] for el in axislabel_filtered])
            + "\n Chose: "
            + str(axislabel_filtered[0])
        )
        return str(axislabel_filtered[0][0])


def get_geo_column(name, type_in, type_out):
    if name is None:
        return geo_columns.loc[:, type_out]

    name = [name] if type(name) == str else name
    if geo_columns.loc[:, type_in].isin(name).any():
        return geo_columns.loc[
            geo_columns.loc[:, type_in].isin(name), type_out
        ].to_list()
    else:
        return None


def get_geo_column_label(col_name):
    """
    Translate database column name to plot axis label using matploltib latex syntax for geometric columns
    :param col_name:
    :param col_name: str
        column name in database name syntax
    :return: str
        column name in matplotlib latex axis label syntax
    """
    idx_find = geo_columns.unstack().loc[geo_columns.unstack() == col_name].index[0]
    if idx_find[0] == "A_geo":
        return (
            "$A_\mathrm{geo}$ / cm$_{(\mathrm{"
            + geo_columns.loc[idx_find[1], "geo_label"]
            + "})}^{2}$"
        )
    if idx_find[0] == "dm_dt_S":
        return (
            "d$m$ d$t^{-1}$ $S^{-1}$ / ng s$^{-1}$ cm$_{(\mathrm{"
            + geo_columns.loc[idx_find[1], "geo_label"]
            + "})}^{-2}$"
        )
    if idx_find[0] == "j_geo":
        return (
            "$j_\mathrm{geo}$ / mA cm$_{(\mathrm{"
            + geo_columns.loc[idx_find[1], "geo_label"]
            + "})}^{-2}$"
        )


geo_columns = pd.DataFrame(
    [
        [
            "spots_spot_size__mm2",
            "spot\ size",
            "dm_dt_S__ng_s_cm2geo_spot_size",
            "j__mA_cm2geo_spot_size",
        ],
        [
            "fc_top_name_flow_cell_A_opening_ideal__mm2",
            "cell",
            "dm_dt_S__ng_s_cm2geo_fc_top_cell_Aideal",
            "j__mA_cm2geo_fc_top_cell_Aideal",
        ],
        [
            "fc_top_name_flow_cell_A_opening_real__mm2",
            "cell\ real",
            "dm_dt_S__ng_s_cm2geo_fc_top_cell_Areal",
            "j__mA_cm2geo_fc_top_cell_Areal",
        ],
        [
            "fc_top_id_sealing_A_opening__mm2",
            "sealing",
            "dm_dt_S__ng_s_cm2geo_fc_top_sealing",
            "j__mA_cm2geo_fc_top_sealing",
        ],
        [
            "fc_top_id_PTL_A_PTL__mm2",
            "PTL",
            "dm_dt_S__ng_s_cm2geo_fc_top_PTL",
            "j__mA_cm2geo_fc_top_PTL",
        ],
        [
            "fc_bottom_name_flow_cell_A_opening_ideal__mm2",
            "bottom\ cell",
            "dm_dt_S__ng_s_cm2geo_fc_bottom_cell_Aideal",
            "j__mA_cm2geo_fc_bottom_cell_Aideal",
        ],
        [
            "fc_bottom_name_flow_cell_A_opening_real__mm2",
            "bottom\ cell\ real",
            "dm_dt_S__ng_s_cm2geo_fc_bottom_cell_Areal",
            "j__mA_cm2geo_fc_bottom_cell_Areal",
        ],
        [
            "fc_bottom_id_sealing_A_opening__mm2",
            "bottom\ sealing",
            "dm_dt_S__ng_s_cm2geo_fc_bottom_sealing",
            "j__mA_cm2geo_fc_bottom_sealing",
        ],
        [
            "fc_bottom_id_PTL_A_PTL__mm2",
            "bottom\ PTL",
            "dm_dt_S__ng_s_cm2geo_fc_bottom_PTL",
            "j__mA_cm2geo_fc_bottom_PTL",
        ],
    ],
    columns=["A_geo", "geo_label", "dm_dt_S", "j_geo"],
)


# Plot manipulations
def align_yaxis(ax1, v1, ax2, v2):
    """
    adjust ax2 ylimit so that v2 in ax2 is aligned to v1 in ax1
    This is useful if the 0 point of ax1 and ax2 (twin of ax1) should be aligned to th esame height
    :param ax1: first axes object
    :param v1: value on first y axis which should be aligned
    :param ax2: second axes object to be aligned
    :param v2: value on second y axis which should be aligned
    :return: None
    """
    ax1.set_ylim(ax1.get_ylim())  # aligning fails if ylim not set beforehand - whyever?
    ax2.set_ylim(ax2.get_ylim())
    _, y1 = ax1.transData.transform((0, v1))
    _, y2 = ax2.transData.transform((0, v2))
    adjust_yaxis(ax1, (y2 - y1) / 2, v1)
    adjust_yaxis(ax2, (y1 - y2) / 2, v2)


def adjust_yaxis(ax, ydif, v):
    """
    shift axis ax by ydif, maintaining point v at the same location
    :param ax: matplotlib.Axes
        axes on which the axis should be adjusted
    :param ydif: int or float
        size of the y-axis
    :param v: int or float
        value on y-axis which should keep the same position
    :return: None
    """

    inv = ax.transData.inverted()
    _, dy = inv.transform((0, 0)) - inv.transform((0, ydif))
    miny, maxy = ax.get_ylim()

    nminy = miny - v + dy - abs(dy)
    nmaxy = maxy - v + dy + abs(dy)
    ax.set_ylim(nminy + v, nmaxy + v)


def autoscale_y(ax, margin=0.05, lines=None):
    """
    This function rescales the y-axis based on the data that is visible given the current xlim of the axis.
    :param ax: a matplotlib axes object
    :param margin: float, optonal, default=0.05
        percentage of margin between plot and frame considered during autoscale, default 5%
    :param lines: list of matplotlib.lines or None, optional, default None
        list of lines which should be scaled,
        if None scale all lines in axis
    :return: None
    """

    def get_bottom_top(line_obj):
        """
        get minimum and maximum y-value of a line in the given x limits
        :param line_obj: Matplotlib artist
        :return: ymin,ymax as minimum and maximum y-value
        """
        xd = line_obj.get_xdata()
        yd = line_obj.get_ydata()
        lo, hi = ax.get_xlim()
        y_displayed = yd[((xd > lo) & (xd < hi))]
        h = np.max(y_displayed) - np.min(y_displayed)
        ymin = np.min(y_displayed) - margin * h
        ymax = np.max(y_displayed) + margin * h
        return ymin, ymax

    if lines is None:
        lines = ax.get_lines()
    elif type(lines) == matplotlib.lines.Line2D:
        lines = [lines]
    elif type(lines) == list:
        lines = lines
    else:
        raise ValueError(
            "Lines must be None, matplotlib.lines.Line2D or list of matplotlib.lines.Line2D"
        )

    bot, top = np.inf, -np.inf

    for line in lines:
        new_bot, new_top = get_bottom_top(line)
        if new_bot < bot:
            bot = new_bot
        if new_top > top:
            top = new_top

    ax.set_ylim(bot, top)


def autoscale_axis(ax, which="y", margin=0.05, lines=None):
    """
    This function rescales the given axis based on the data that is visible given the current xlim of the axis.
    :param ax: matplotlib.Axes
        Axes object which should be autoscaled
    :param which: str one of ['y, 'x']
        which axis to scale
    :param margin: float, optonal, default=0.05
        percentage of margin between plot and frame considered during autoscale, default 5%
    :param lines: list of matplotlib.lines or None, optional, default None
        list of lines which should be scaled,
        if None scale all lines in axis
    :return: None
    """

    def get_axis_scale_min_max(line_obj):
        """
        get minimum and maximum y-value of a line in the given x limits or vice versa
        :param line_obj:
        :return:
        """
        data_axis_other = line_obj.get_xdata() if which == "y" else line_obj.get_ydata()
        data_axis_scale = line_obj.get_ydata() if which == "y" else line_obj.get_xdata()
        lo, hi = ax.get_xlim() if which == "y" else ax.get_ylim()
        # print(lo,hi)  # before scaling an axis, the other must be on a large window
        # print(type(data_axis_other), isinstance(data_axis_other, pd.core.series.Series))  # numpy
        if isinstance(data_axis_other, np.ndarray):
            if isinstance(data_axis_other[0], np.datetime64):
                lo, hi = np.datetime64(mpl.dates.num2date(lo)), np.datetime64(
                    mpl.dates.num2date(hi)
                )
        if isinstance(data_axis_other, pd.Series):  # pandas.Series
            if isinstance(data_axis_other.iloc[0], np.datetime64) or isinstance(
                data_axis_other.iloc[0], pd.Timestamp  # pd._libs.tslibs.timestamps.Timestamp
            ):
                lo, hi = np.datetime64(mpl.dates.num2date(lo)), np.datetime64(
                    mpl.dates.num2date(hi)
                )
        axis_scale__displayed = data_axis_scale[
            ((data_axis_other > lo) & (data_axis_other < hi))
        ]
        # print(axis_scale__displayed)
        if len(axis_scale__displayed) == 0:  # do not consider lines out of display
            return np.inf, -np.inf

        h = np.max(axis_scale__displayed) - np.min(axis_scale__displayed)
        ax_scale_min = np.min(axis_scale__displayed) - margin * h
        ax_scale_max = np.max(axis_scale__displayed) + margin * h
        return ax_scale_min, ax_scale_max

    if lines is None:
        lines = ax.get_lines()
    elif type(lines) == matplotlib.lines.Line2D:
        lines = [lines]
    elif type(lines) == list:
        lines = lines
    else:
        raise ValueError(
            "Lines must be None, matplotlib.lines.Line2D or list of matplotlib.lines.Line2D"
        )

    axis_scale_min, axis_scale_max = np.inf, -np.inf

    for line in lines:
        new_axis_scale_min, new_axis_scale_max = get_axis_scale_min_max(line)
        if new_axis_scale_min < axis_scale_min:
            axis_scale_min = new_axis_scale_min
        if new_axis_scale_max > axis_scale_max:
            axis_scale_max = new_axis_scale_max

    if np.isinf(axis_scale_min):
        print("No minimum limit found")
    if np.isinf(-axis_scale_max):
        print("No maximum limit found")

    # print(which, axis_scale_min,axis_scale_max)
    if which == "y":
        ax.set_ylim(axis_scale_min, axis_scale_max)
    elif which == "x":
        ax.set_xlim(axis_scale_min, axis_scale_max)


def has_twin(ax):
    """
    check whether the axes has a twin or not
    :param ax:
    :return:
    """
    for other_ax in ax.figure.axes:
        if other_ax is ax:
            continue
        if other_ax.bbox.bounds == ax.bbox.bounds:
            return True
    return False


def first_twin(ax):
    """
    get the first twin of an axes
    :param ax:
    :return:
    """
    # print(ax.figure.axes)
    for other_ax in ax.figure.axes:
        if other_ax is ax:
            continue
        if other_ax.bbox.bounds == ax.bbox.bounds:
            return other_ax
    return None


# Other functions
def synchronize_timestamps(
    data_ec,
    data_icpms,
    timestamp_col_ec="Timestamp",
    timestamp_col_icpms="t_delaycorrected__timestamp_sfc_pc",
    overlay_index_cols=None,
    time_unit="s",
    consider_extended_time_window=True,
):
    """
    convert timestamp to given time unit (default seconds) for ec and icpms data in a synchronized way
    :param data_ec: pandas.DataFrame
        DataFrame for EC data as given by .get_data() method
    :param data_icpms: pandas.DataFrame
        DataFrame for ICPMS data as given by .get_data() method
    :param timestamp_col_ec: str, optional, default 'Timestamp',
        name of the timestamp column consiedered for the synchronization for the EC data
    :param timestamp_col_icpms: str, optional, default 't_delaycorrected__timestamp_sfc_pc',
        name of the timestamp column consiedered for the synchronization for the ICPMS data
    :param overlay_index_cols: list of str or None, optional, default None
        list of column names, use this to overlay data in time dimension
        every unique value of the given columns in the EC data table will start the time counting from 0.
    :param time_unit: str, optional, default 's',
        the time unit of the returned time columns.
         Abbreviations as defined by numpy.timedelta64 (https://numpy.org/doc/stable/reference/arrays.datetime.html)
    :param consider_extended_time_window: bool, optional, default True,
        if True the time axis will be shifted by the same value as previously given in .get_data(extend_time_window=xx)
        depracated
    :return: data_ec, data_icpms
        with the time synchronized column derived by: timestamp_col_ec+ '_synchronized__' + time_unit
    """
    list_data = [data_ec, data_icpms]
    list_timestamp_cols = [timestamp_col_ec, timestamp_col_icpms]

    return synchronize_timestamps_multiple(
        list_data,
        list_timestamp_cols,
        list_index_data_ec=0,
        overlay_index_cols=overlay_index_cols,
        time_unit=time_unit,
    )


def synchronize_timestamps_multiple(
    list_data,
    list_timestamp_cols,
    list_index_data_ec,
    overlay_index_cols=None,
    time_unit="s",
):
    """
    convert timestamp to given time unit (default seconds) for mutliple data DataFrames in a synchronized way
    :param list_data: list of DataFrames
    :param list_timestamp_cols: list of timestamp_columns
        corresponding name of the timestamp column considered for the synchronization
    :param list_index_data_ec: int
        index of data_ec in list_data. Data_ec must be identified to determine offset_timestamp
    :param overlay_index_cols: list of str or None, optional, default None
        list of column names, use this to overlay data in time dimension
        every unique value of the given columns in the EC data table will start the time counting from 0.
    :param time_unit: str, optional, default 's',
        the time unit of the returned time columns.
         Abbreviations as defined by numpy.timedelta64 (https://numpy.org/doc/stable/reference/arrays.datetime.html)
    :return: data_ec, data_icpms
        with the time synchronized column derived by: timestamp_col_ec+ '_synchronized__' + time_unit
    """
    list_data_offset_determination = [data for data in list_data]

    if overlay_index_cols is not None:
        # Check that overlay_index_cols are given in all given dataframes
        if any(
            [
                any(
                    [
                        overlay_index_col not in data.reset_index().columns
                        for overlay_index_col in overlay_index_cols
                    ]
                )
                for data in list_data_offset_determination
            ]
        ):
            sys.exit(
                "overlay_index_cols must be contained in all dataframes listed in list_data!"
            )
        offset_timestamp = (
            list_data[list_index_data_ec]
            .reset_index()
            .groupby(by=overlay_index_cols)
            .min()
            .loc[:, "Timestamp"]
        )
    else:
        # print(list_data_offset_determination, list_timestamp_cols, np.array([data.loc[:, timestamp_col].iloc[0]
        # for data, timestamp_col in zip(list_data_offset_determination, list_timestamp_cols)]))
        offset_timestamp = np.array(
            [
                data.loc[:, timestamp_col].iloc[0]
                for data, timestamp_col in zip(
                    list_data_offset_determination, list_timestamp_cols
                )
            ]
        ).min()
        # offset_timestamp_aray = np.array(
        #    [data.loc[:, timestamp_col].iloc[0]
        #    for data, timestamp_col in zip(list_data_offset_determination, list_timestamp_cols)])
        # print((offset_timestamp_aray[1]-offset_timestamp_aray[0])/ np.timedelta64(1, time_unit))
    # print(offset_timestamp)

    return_data = []
    # Loop through given data with corresponding timestamp_col
    for data, timestamp_col in zip(list_data, list_timestamp_cols):
        data.loc[:, timestamp_col + "_synchronized__" + time_unit] = (
            data.loc[:, timestamp_col] - offset_timestamp
        ) / np.timedelta64(1, time_unit)
        print(
            "Added snychronized timestamp column: ",
            timestamp_col + "_synchronized__" + time_unit,
        )
        return_data = return_data + [data]
    return return_data


def get_j__mA_mg(
    exp_ec,
    data_ec,
    j_geo_col=None,
):
    """
    Add loading and composition columns to exp_ec_expanded and mass normalized current to data_ec.
    Using loading column in spots/sample table and compositon given in samples_composition/spots_composition
    :param exp_ec: exp_ec
    :param data_ec: data_ec
    :param j_geo_col: str of list of str or None
        Selected a specific column for geometric area which will be used to normalize by mass.
        Optional, if None procedure is done for all geometric columns.
    :return: exp_ec, data_ec
    """
    con = db.connect()

    # total loading from spots (preferred) or samples table
    for index, row in exp_ec.iterrows():
        exp_ec.loc[index, "total_loading__mg_cm2"] = (
            row.spots_total_loading__mg_cm2
            if row.spots_total_loading__mg_cm2 is not None
            else row.samples_total_loading__mg_cm2
        )
    # exp_ec.loc[:, ['total_loading__mg_cm2', 'spots_total_loading__mg_cm2','samples_total_loading__mg_cm2']]

    # get compositions
    sample_spot_composition = pd.read_sql(
        """ SELECT id_sample, NULL as id_spot, material, wt_percent 
                            FROM samples_composition 
                                WHERE id_sample IN ("""
        + str(list(exp_ec.id_sample.to_list()))[1:-1]
        + """)
                                UNION
                                SELECT id_sample, id_spot, material, wt_percent  
                                FROM spots_composition 
                                WHERE (id_sample, id_spot) IN ("""
        + str(
            [tuple([row.id_sample, row.id_spot]) for index, row in exp_ec.iterrows()]
        )[1:-1]
        + """)
                               ;""",
        con=con,
        index_col=["id_sample", "id_spot"],
    )
    # display(sample_spot_composition)

    # for each material given, get values and write composition and loading into exp_ec
    materials = sample_spot_composition.material.unique()
    material_composition_cols = "wt_percent_" + materials
    material_loading_cols = "loading__mg_" + materials + "_cm2"
    for material, material_colname in zip(materials, material_composition_cols):
        # exp_ec.loc[:, material_colname] = None #default #Not necessary?

        # composition of materials for each experiment for each spot
        exp_ec_spots_composition = exp_ec.loc[:, ["id_sample", "id_spot"]].join(
            sample_spot_composition.loc[
                (sample_spot_composition.loc[:, "material"] == material)
                & (sample_spot_composition.index.get_level_values("id_spot").notna()),
                :,
            ]
            .reset_index()
            .set_index(["id_sample", "id_spot"])
            .loc[
                :,
                [
                    "wt_percent",
                ],
            ]
            .rename(columns={"wt_percent": material_colname}),
            on=["id_sample", "id_spot"],
        )
        # display(exp_ec_spots_composition)

        # composition of materials for each experiment for each sample
        exp_ec_samples_composition = exp_ec.loc[:, ["id_sample", "id_spot"]].join(
            sample_spot_composition.loc[
                (sample_spot_composition.loc[:, "material"] == material)
                & (sample_spot_composition.index.get_level_values("id_spot").isna()),
                :,
            ]
            .reset_index()
            .set_index(["id_sample"])
            .loc[
                :,
                [
                    "wt_percent",
                ],
            ]
            .rename(columns={"wt_percent": material_colname}),
            on=["id_sample"],
        )
        # display(exp_ec_samples_composition)

        # combine spots and sample-specific composition, thereby spots-specific is preferred over sample-specfic
        # display(exp_ec_spots_composition.combine_first(exp_ec_samples_composition))
        exp_ec = exp_ec.join(
            exp_ec_spots_composition.combine_first(exp_ec_samples_composition).drop(
                columns=["id_sample", "id_spot"]
            ),
            on=exp_ec.index.names,
        )  # ['id_exp_sfc'])
        exp_ec.loc[:, material_loading_cols] = (
            exp_ec.loc[:, "total_loading__mg_cm2"]
            * exp_ec.loc[:, material_colname]
            / 100
        )

    # get all j_geo columns available in given exp_ec and j_geo_col not given
    j_geo_cols = (
        [col for col in data_ec.columns if col[:12] == "j__mA_cm2geo"]
        if j_geo_col is None
        else [j_geo_col]
    )
    # print(j_geo_cols)

    # calculate mass normalized current
    data_ec = data_ec.join(
        exp_ec.loc[:, ["total_loading__mg_cm2"] + list(material_loading_cols)],
        on=exp_ec.index.name,
    )
    # display(data_ec.total_loading__mg_cm2)
    for j_geo_col in j_geo_cols:
        # print(j_geo_col, '_geo' + j_geo_col[12:])

        data_ec.loc[:, "j__mA_mg_total" + "_geo" + j_geo_col[12:]] = (
            data_ec.loc[:, j_geo_col] / data_ec.total_loading__mg_cm2
        )
        for material, material_loading_colname in zip(materials, material_loading_cols):
            data_ec.loc[:, "j__mA_mg_" + material + "_geo" + j_geo_col[12:]] = (
                data_ec.loc[:, j_geo_col] / data_ec.loc[:, material_loading_colname]
            )
    data_ec = data_ec.drop(columns=["total_loading__mg_cm2"])
    return exp_ec, data_ec


def average(
    exp,
    data,
    on=None,
    overlay_index_cols=None,
    name_id_data_overlay_col=None,
    average_cols_by_dtypes=None,
    average_cols=None,
):
    """
    Average repetitions of experiments.
    To average multiple experiment, data of the single experiments must be aligned on their x-Axis. This is critical
    if the different experiments have different x values for each experiment (e.g. different acquisition frequencies.)
    For example, the 100th datapoint of the first experiment might not be at the same x-value as the 100th datapoint
    of the second experiment. Interpolation of the x-values might be necessary to align the values. This is not covered
    in this function. You can align your data defining a new index which states which point belong to the same x
    externally and give here the name of this column as name_id_data_overlay_col.
    If your experiments are sufficiently aligned in x, you can set name_id_data_overlay_col to the columns which were
    used to overlay the different experiments. Then name_id_data_overlay_col will be created by assuming perfect
    alignment of the x datapoints.
    :param exp: pandas.DataFrame
        experimental dataframe, with a list of experiments, which should be averaged
    :param data: pandas.DataFrame
        corresponding data DataFrame
    :param on: str or list of str or None, optional default None
        on which columns the grouping should be performed
        if None empty list --> all experiments will be averaged to one experiment
    :param overlay_index_cols: list of str or None, optional, default None
        list of column names which were used to overlay data
        Create column id_data_overlay, assuming synchronization of timestamps of to be averaged experiments
        all 1st (all 2nd, 3rd, ...) datapoints within a overlay group will be averaged
    :param name_id_data_overlay_col:
        Instead of overlay_index_cols, name_id_data_overlay_col can be set, to define which datapoints of the overlay
        groups belong to each other. This can be achieved by comparing timestamps (for example if different acquisition
        frequencies across frequencies)
    :param average_cols_by_dtypes: list of type, optional default [np.float64]
        Select which of the data columns should be averaged by the data type of the column
    :param average_cols: list of str, optional default None
        instead of average_cols_by_dtypes columns which should be averaged can be set manually
    :return: exp_avg, data_avg
    """
    if on is None:
        on = []
    if average_cols_by_dtypes is None:
        average_cols_by_dtypes = [np.float64]
    if not on:  # on == []
        exp = exp.assign(group="all")
        data = data.assign(group="all")
        on = ["group"]

    # Average of experimental dataframe
    # primitive approach selecting only the first experiment in each group,
    # information of different experimental metadata is lost
    # exp_avg = exp.groupby(on).first()
    # more advanced: if there are different values across experiments them group them into a list
    exp_avg = exp.groupby(on).apply(
        lambda overlay_group: overlay_group.apply(
            lambda col:
            # for each column check whether non-unique values
            # if different values, return a list of those
            # if all the same values just return this value
            pd.Series({col.index[0]: list(col.tolist())})
            if col.nunique() > 1
            else col.iloc[0]
        )
    )

    # print((exp.groupby(on).nunique() > 1).transpose().any(axis=1))
    cols_with_discrepancies = (
        exp.reset_index()
        .set_index(on)
        .loc[
            :,
            (exp.reset_index().set_index(on).groupby(on).nunique() > 1)
            .transpose()
            .any(axis=1),
        ]
        .columns
    )
    if len(cols_with_discrepancies) > 0:
        print(
            "\x1b[33m"
            + "Discrepancies in experimental parameters of averaged experiments "
              "in at least one group in following columns:\n   "
            + ", ".join(cols_with_discrepancies)
            + "\n   "
            + "Different values are aggregated as list in the returned experimental dataframe, check for details!"
            + "\x1b[0m"
        )

    # Determine data_on (which datapoints should be averaged?)
    if overlay_index_cols is not None:
        # Create column id_data_overlay, assuming synchronization of timestamps of to be averaged experiments
        # all 1st (all 2nd, 3rd, ..) datapoints within a overlay group will be averaged
        overlay_index = overlay_index_cols + on
        index = data.index.names
        unused_index_cols = [col for col in index if col not in overlay_index]
        name_id_data_overlay_col = "id_data_overlay"

        data = data.assign(
            id_data_overlay=data.groupby(overlay_index)
            .apply(
                lambda x: pd.Series(
                    pd.RangeIndex(0, len(x.index)),
                    index=x.reset_index().set_index(unused_index_cols).index,
                    name=name_id_data_overlay_col,
                )
            )
            .reset_index()
            .set_index(index)
            .loc[:, name_id_data_overlay_col]
            # if on=[], group column is in output, leading to error in assign
        )  # .groupby('t_delaycorrected__timestamp_sfc_pc_synchronized__s').count()
    elif name_id_data_overlay_col is None:
        # Instead of overlay_index_cols, name_id_data_overlay_col can be set,
        # this column should define which datapoints of the overlay groups belong to each other
        # This can be achieved for example by interpolating different timestamps
        # (for example if different acquisition frequencies across frequencies)
        raise Exception(
            "If create_id_data_overlay=False, name_id_data_overlay_col can't be None "
            + "- a custom column need to define which datapoints of each overlay group should be averaged."
        )

    if average_cols is None:
        # Auto determine the columns selected for averaging, by default these are all float-columns
        average_cols = data.select_dtypes(
            include=average_cols_by_dtypes
        ).columns  # .columns[data.dtypes == 'float64']

    if type(name_id_data_overlay_col) == str:
        # allow name_id_data_overlay_col to be single column (string) or multiple columns (list)
        name_id_data_overlay_col = [name_id_data_overlay_col]

    # column to group data dataframe on
    data_on = on + name_id_data_overlay_col

    # Average of data dataframe
    data_avg = (
        data.groupby(data_on)[average_cols]
        .mean(numeric_only=False)
        .join(
            data.groupby(data_on)[average_cols].std(ddof=1),  # numeric_only=False),
            rsuffix="_std",
        )
        .join(
            data.groupby(data_on)[average_cols].min(),  # numeric_only=False),
            rsuffix="_min",
        )
        .join(
            data.groupby(data_on)[average_cols].max(),  # numeric_only=False),
            rsuffix="_max",
        )
        .join(
            data.groupby(data_on).count().max(axis=1).rename("avg_counts"),
            rsuffix="_count",
        )
    )
    if len(data_avg.avg_counts.unique()) > 1:
        print(
            "\x1b[33m"
            + "Different number of datapoints averaged, check avg_counts column in data dataframe.\n"
            + "   Number of experiments averaged: "
            + str(data_avg.avg_counts.unique())
            + "\x1b[0m"
        )
    # Calculate mean+- stdandard deviation for all avergaed columns
    for avg_col in average_cols:
        data_avg.loc[:, avg_col + "_std_lolim"] = (
            data_avg.loc[:, avg_col] - data_avg.loc[:, avg_col + "_std"]
        )
        data_avg.loc[:, avg_col + "_std_uplim"] = (
            data_avg.loc[:, avg_col] + data_avg.loc[:, avg_col + "_std"]
        )

    return exp_avg, data_avg


def get_colormap(cmap_name, count_rows, cmap_min=0, cmap_max=1):
    """
    Split a colormap into n (= count_rows) defined colors. Set cmap_min and cmap_max to cut edges from the colormap,
    to avoid white and black - insufficient contrast to background.
    :param cmap_name: str
        name of the colormap. Either defined in evaluation.visualization.plot.custom_cmaps or in
        matplotlib.pyplot.colormaps (https://matplotlib.org/stable/gallery/color/colormap_reference.html)
        or cmcrameri scientific colormaps (https://pypi.org/project/cmcrameri/)
    :param count_rows: int
        number of defined colors to split the colormap
    :param cmap_min: float, 0<cmap_min<cmap_max
        cut left side of colormap
    :param cmap_max: float, cmap_min<cmap_max<1
        cut right side of colormap
    :return: list
        list of defined colors
    """
    color_selector = np.linspace(cmap_min, cmap_max, count_rows)  # default
    if cmap_name in custom_cmaps.keys():
        color_data = ListedColormap(
            np.array(
                [
                    np.linspace(
                        custom_cmaps[cmap_name][0][i],
                        custom_cmaps[cmap_name][1][i],
                        count_rows,
                    )
                    for i in np.arange(0, 4)
                ]
            ).transpose()
        )
    elif cmap_name in plt.colormaps():
        color_data = plt.get_cmap(cmap_name)
        if hasattr(color_data, "N"):
            if (
                count_rows > color_data.N and color_data.N <= 20
            ):  # only for qualitative colormaps with up to 20 discrete colors
                color_selector = [x % color_data.N for x in range(count_rows)]
    else:
        raise NameError(
            "Colormap not available, check colormaps from matplotlib "
            "https://matplotlib.org/stable/gallery/color/colormap_reference.html "
            "and custom colormaps (definition of this function)"
        )

    return [color_data(i) for i in color_selector]


class HandlerColorLineCollection(HandlerLineCollection):
    def create_artists(
        self, legend, artist, xdescent, ydescent, width, height, fontsize, trans
    ):
        x = np.linspace(0, width, self.get_numpoints(legend) + 1)
        y = np.zeros(self.get_numpoints(legend) + 1) + height / 2.0 - ydescent
        points = np.array([x, y]).T.reshape(-1, 1, 2)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)
        lc = LineCollection(
            segments,
            cmap=artist.cmap,
            transform=trans,
        )
        lc.set_array(x)
        lc.set_linewidth(artist.get_linewidth())
        return [lc]


def legend_handle_colormap(cmap):
    """
    To set a colormap as legend handle.
    :param cmap: str
        name of the colormap.
    :return: empty LineCollection
    """
    lc = LineCollection(
        [[[0, 0], [0, 0]]],
        cmap=plt.get_cmap(cmap),
        norm=plt.Normalize(0, 10),
        # linewidth=3,
        alpha=0,
    )
    # ax.add_collection(lc)
    return lc


def legend_handle_line(**kwargs):
    """
    To set a line as legend handle.
    :param kwargs: keyword arguments of matplotlib.lines.Line2D
    :return: empty Line2D
    """
    return mlines.Line2D([], [], **kwargs)


def legend_handle_patch(**kwargs):
    """
    To set a patch as legend handle.
    :param kwargs: keyword arguments of matplotlib.patches.Patch
    :return: empty Patch
    """
    return mpatches.Patch(**kwargs)


def add_legend_handle_label(
    handles,
    labels,
    handler_map_dict,
    handle,
    label,
    handler_map=None,
):
    """
    add legend handle+label to existing handles and labels. To custom build your legend entries.
    :param handles: list or handles from matplotlib.axes.Axes.get_legend_handles_labels
    :param labels: list or labels from matplotlib.axes.Axes.get_legend_handles_labels
    :param handler_map_dict: dict or handler_map_dict
        required to have colormaps handles
    :param handle: matpltolib handle
        Use for example: legend_handle_line, legend_handle_patch, legend_handle_colormap
    :param label: str
        Label to be added
    :param handler_map: plot.HandlerColorLineCollection()
        for example with numpoints=6, to set number of colors displayed
    :return:
    """
    handles += [handle]
    labels += [label]
    if handler_map is not None:
        handler_map_dict[handle] = handler_map
    return handles, labels, handler_map_dict


# Fitting functions
def linear_func(B, x):
    """
    Linear function use for fitting data
    :param B: list or str
        list of parameters: [slope, y-axis intercept]
        str: 'label' to receive information for fitting label
            or 'curve_fit_model' to use with scipy.optimize.curve_fit use: model('curve_fit_model', 0)
    :param x: list, np.array, pd.Series
        x-data
    :return: y-data
    """
    if type(B) == str:
        if B == "label":
            return {
                "model": "linear_fit",  # used in legend and in result column name
                "formula": "mx+b",  # used in legend
                "beta0": ["m", "b"],
            }  # used in legend and in result column name
        elif (
            B == "curve_fit_model"
        ):  # use model('curve_fit_model', 0) when using scipy.optimize.curve_fit instead of scipy.odr
            return linear_func_curve_fit
    else:
        return B[0] * x + B[1]


def linear_func_curve_fit(x, *B):
    """
    Linear function to allow for compatibility of scipy.optimize.curve_fit and scipy.odr
    :param x: list, np.array, pd.Series
        x-data
    :param B: list
        list of parameters: [slope, y-axis intercept]
    :return: y-data
    """
    return linear_func(B, x)


def tafel_func(B, x):
    """
    Tafel function to use for fitting data
    :param B: list or str
        list of parameters: [slope, y-axis intercept]
        str: 'label' to receive information for fitting label
            or 'curve_fit_model' to use with scipy.optimize.curve_fit use: model('curve_fit_model', 0)
    :param x: list, np.array, pd.Series
        x-data
    :return: y-data
    """
    if type(B) == str:
        if B == "label":
            return {
                "model": "tafel_fit",  # used in legend and in result column name
                "formula": "m*log(x)+b",  # used in legend
                "beta0": ["m", "b"],
            }  # used in legend and in result column name
        elif (
            B == "curve_fit_model"
        ):  # use model('curve_fit_model', 0) when using scipy.optimize.curve_fit instead of scipy.odr
            return tafel_func_curve_fit
    else:
        return B[0] * np.log10(x) + B[1]


def tafel_func_curve_fit(x, *B):
    """
    Tafel function to allow for compatibility of scipy.optimize.curve_fit and scipy.odr
    :param x: list, np.array, pd.Series
        x-data
    :param B: list
        list of parameters: [slope, y-axis intercept]
    :return: y-data
    """
    return tafel_func(B, x)


class curve_fit_odr_style:
    """
    class to mimic output of scipy.optimize.curve_fit in a shape as given by scipy.odr
    """

    def __init__(self, f, xdata, ydata, **kwargs):
        popt, pcov = curve_fit(f("curve_fit_model", 0), xdata, ydata, **kwargs)
        perr = np.sqrt(
            np.diag(pcov)
        )
        # as described in manual
        # https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.curve_fit.html?highlight=curve_fit#scipy.optimize.curve_fit

        # Rsquare calculation according to
        # https://stackoverflow.com/questions/19189362/getting-the-r-squared-value-using-curve-fit
        residuals = ydata - f(popt, xdata)
        ss_res = np.sum(residuals**2)  # residual sum of squares
        ss_tot = np.sum((ydata - np.mean(ydata)) ** 2)  # total sum of squares
        r_squared = (1 - (ss_res / ss_tot)) if ss_tot != 0 else 1  # R_square

        # define attributes
        self.beta = popt
        self.sd_beta = perr
        self.rsquared = r_squared


def create_fit_label(
    description=True,
    params=True,
    rsquared=False,
    err_considered=False,
):
    return dict(
        description=description,
        params=params,
        rsquared=rsquared,
        err_considered=err_considered,
    )


@pd.api.extensions.register_dataframe_accessor("dataset")
class datasetAccessor:
    """
    class to bundle functions and properties of sets of experiments to make them ready to plot
    """

    def __init__(self, pandas_obj):
        self._obj = pandas_obj
        if not hasattr(self._obj, "export_name"):
            self._obj.export_name = None

    def set_name(self, name, export_object=None):
        """
        Set the name of the dataframe as it will be used by the PlotDataStorage function
        :param name: str
            name of the dataset
        :param export_object: current_PlotDataStorage() object or None
            if None initialize a new current_PlotDataStorage object
        :return: self
        """
        if export_object is None:
            export_object = current_PlotDataStorage()

        if hasattr(self._obj, "export_name"):
            if self._obj.export_name is not None:
                warnings.warn(
                    'Dataset has already a name! "'
                    + str(self._obj.export_name)
                    + '" will be overwritten with '
                    + name
                )
        self._obj.export_name = name
        return self

    def return_dataset(self):
        """
        Return DataFrame
        :return: pandas.DataFrame
        """
        return self._obj

    def display(self, only_different_cols=False):
        """
        Method to display complete DataFrame in jupyter (large DataFrames will be cut in rows and cols)
        :param only_different_cols: bool
            if True only display columns which have non-unique values,
            used to quickly compare experiments whether they have matching metadata
        :return:
        """
        dataFrame = self._obj

        def unique_cols(df):
            cols = []
            for col in df.columns:
                if (df.loc[:, col].map(type) == list).any():
                    cols += [col]
                elif df.loc[:, col].unique().size > 1:
                    cols += [col]
            return cols

        if only_different_cols:
            # dataFrame = self._obj.loc[:, [col for col in self._obj.columns
            #                                   if self._obj.loc[:, col].unique().size > 1]]
            # fails for columns with list values
            dataFrame = self._obj.loc[:, unique_cols(self._obj)]

        with pd.option_context(
            "display.max_rows", None, "display.max_columns", None
        ):  # more options can be specified also
            try:
                display(dataFrame)  # works only in Jupyter Notebook/Lab environment
            except NameError:
                print(dataFrame)

    def _colormap(self, cmap_name, rowindexer=slice(None), cmap_min=0, cmap_max=1):
        """
        Internal function to define a colormap for DataSet
        :param cmap_name: str
            name of the colormap. Either defined in evaluation.visualization.plot.custom_cmaps or in
            matplotlib.pyplot.colormaps (https://matplotlib.org/stable/gallery/color/colormap_reference.html)
            or cmcrameri scientific colormaps (https://pypi.org/project/cmcrameri/)
        :param rowindexer: tuple | list of bools
            rowindexer: selector of rows which should get color use different formats:
            ('row5', slice(None)) --> tuple of indexs;
            or dataframe.loc[:, 'col1'] > 5  --> list of bools;
        :return: pd.Series with the color value for each row
        """
        count_rows = self._obj.loc[rowindexer, :].shape[0]
        return pd.Series(
            data=get_colormap(
                cmap_name, count_rows, cmap_min=cmap_min, cmap_max=cmap_max
            ),
            index=self._obj.loc[rowindexer, :].index,
            dtype="object",
        )

    def add_column(
        self,
        name,
        rowindexers=None,
        # conditions=None,
        values=None,
        rowindexer_first_of_group=None,
        **kwargs,
    ):
        """
        Function to add a column to dataset. Similar to pandas.DataFrame.assign().
        Mainly meant to add style parameters for plotting to experimental datasets depending on experimental parameters,
        like for example a material specific color code.
        For this the name should be a style parameter of matplotlib.pyplot.plot
        :param name: str
            name of column to add, for styles check signature of .plot
        :param rowindexers: tuple | list of bools or None
            one or a list of rowindexers as used in Pandas .loc(),
            if None, th evalue is applied to all rows
        :param values: list of Any or Any
            if list: must be of same length as rowindexers,
            if Any: all rows will have this value
        :param rowindexer_first_of_group: str or list of str or None
            name of the column or list of name of the columns from which only the first of each group should get
            the value. For example, this can be used to set a legend label only for the first of each material class.
        :param kwargs:
            cmap_min, cmap_max for removing edges of selected colormap
        :return:
        """
        if len(self._obj.index) == 0:
            return self

        if rowindexer_first_of_group is not None:
            if rowindexers is not None:
                warnings.warn(
                    "rowindexer_first_of_group can only be defined for rowindexers=None"
                )
            rowindexers = [
                self._obj.index.isin(
                    self._obj.reset_index()
                    .groupby(rowindexer_first_of_group)
                    .first()
                    .set_index(self._obj.index.names)
                    .index
                ),
                slice(None),
            ]
            values = [values, None]
        # print(rowindexers)
        # print(values)
        if values is None:
            values = [np.nan]
        if rowindexers is None:
            rowindexers = [slice(None)]

        values = (
            [values]
            if (
                type(values) != list
                or (
                    type(values) == list
                    and type(values[0]) != list
                    and len(rowindexers) == 1
                )
            )
            else values
        )
        rowindexers = [rowindexers] if type(rowindexers) != list else rowindexers
        # if type(rowindexers) != list or type(values) != list:
        #    raise ValueError('rowindexers and values must be type list')
        if len(rowindexers) != len(values):
            # or (len(rowindexers) == 1 and len(values) == )):
            raise ValueError(
                "rowindexers ("
                + str(len(rowindexers))
                + ") and values ("
                + str(len(values))
                + ") must be list of same length"
            )

        for (rowindexer, value) in zip(rowindexers[::-1], values[::-1]):
            # print(rowindexer, value)
            if name == "color" and type(value) == str:
                if (
                    value in custom_cmaps.keys() or value in plt.colormaps()
                ):  # exception for colormaps
                    value = self._colormap(value, rowindexer=rowindexer, **kwargs)
                    # self.add_colormaps(value, rowindexer)

            self._obj.loc[rowindexer, name] = value
        # self._obj.loc[:, name] = np.select(conditions, values) # older version using conditions
        return self

    def get_data(self, con, data_table_name, **kwargs):
        """
        Depracated. Please use: evaluations.utils.db.get_data()
        :param con: database connection
        :param data_table_name: name of the data table
        :param kwargs:
        :return: pandas.DataFrame
        """
        return db.get_data(self._obj, name_table=data_table_name, **kwargs)

    def get_exp(
        self,
        conn,
        name_table,
        index_cols=None,
        join_cols=None,
        groupby_cols=None,
        **kwargs,
    ):
        """
        Depracated. Please use: evaluations.utils.db.get_exp()
        :param conn: database connection
        :param name_table:
        :param index_cols:
        :param join_cols:
        :param groupby_cols:
        :param kwargs:
        :return: pandas.DataFrame
        """
        return db.get_exp(
            self._obj,
            name_table=name_table,
            index_col=index_cols,
            join_col=join_cols,
            groupby_col=groupby_cols,
            **kwargs,
        )

    def match_exp_sfc_exp_icpms(self, con, **kwargs):
        """
        Depracated. Please use: evaluations.utils.db.match_exp_sfc_exp_icpms()
        :param con: database connection
        :param kwargs: keyword arguments of evaluation.utils.db.match_exp_sfc_exp_icpms
        :return: pandas.DataFrame
        """
        return db.match_exp_sfc_exp_icpms(self._obj, **kwargs)

    @staticmethod
    def _extend_kwargs_from_dataframe(
        row, index, plt_kwargs, possible_kwarg_params_name
    ):
        """
        Translate columns from experimental dataset to keyword arguments for matplotlib plot styling
        :param row: pandas.Series
            row of the experimental dataset DataFrame
        :param index: pd.Index or pd.MultIndex or tuple
            index of the row of the experimental dataset DataFrame
        :param plt_kwargs: dict
            keyword arguments already defined for th eplot
        :param possible_kwarg_params_name: list
            possible keyword arguments for ths type of plot
        :return: dict
            keyword arguments dict extended by the values from experimental dataset
        """
        # old
        """
        for param in inspect.signature(matplotlib.lines.Line2D).parameters.values():
            if (param.kind == param.POSITIONAL_OR_KEYWORD   # only include parameter of kind POSITIONAL_OR_KEYWORD
                    and not param.default is param.empty    # only include parameter with default value
                    and param.name in row.keys()            # compare whether parameter is set in ovt
                    and not pd.isnull(row[param.name]) and row[param.name] != ''  # exclude if NaN or empty string
            ):
                print('Parameter set by ovt:', param.name)
                plt_kwargs[param.name] = row[param.name]
        """
        plt_kwargs_extended = (
            plt_kwargs.copy()
        )  # extend plt_kwargs by columns in dataset
        for param_name in row.keys():
            if (
                param_name
                in possible_kwarg_params_name  # if dataset col_name a kwarg_param of plot()
                and param_name not in plt_kwargs_extended.keys()
            ):
                # params given directly when function called are prioritized
                if (
                    not pd.isnull(row[param_name]) and row[param_name] != ""
                ):  # exclude if NaN or empty string
                    plt_kwargs_extended[param_name] = row[param_name]
                elif param_name in ["label", "hatch"]:
                    # allow NaN entries in label, to remove point from legend
                    # --> if data parameter in plot is used, label is automatically set as y_col,
                    # which avoids removing legend entries by setting to NaN
                    # --> with this, label is specifically set as NaN
                    # allow also removing of hatches
                    plt_kwargs_extended[param_name] = ""  # row[param_name]
                else:
                    warnings.warn(param_name + " not specified for " + str(index))

        return plt_kwargs_extended

    @staticmethod
    def _get_possible_kwargs(style_class):
        """
        Get possible keyword arguments for a class of plot
        :param style_class:
        :return: list of possible keyword arguments
        """
        # search in signature of Line2D for parameter which might have been set in experimental dataset
        return [
            param.name
            for param in inspect.signature(style_class).parameters.values()
            if param.kind == param.KEYWORD_ONLY
        ]  # only include parameter of kind POSITIONAL_OR_KEYWORD (for Line2D) KEYWORD_ONLY (for Line2D.set)
        # and param.default is not param.empty]      # only include parameter with default value

    def _plot_labels(self, x_col, y_col, ax):
        """
        set axis label by name of selected x and y columns.
        :param x_col: str
            name of the x column
        :param y_col: str
            name of the y column
        :param ax: matpltolib.Axes object
            axes on which to set the axis labels
        :return: None
        """
        if ax is None:
            ax = plt.gca()

        if type(x_col) == str:
            x_axislabel = get_axis_label(x_col)
            if ax.get_xlabel() not in ["", x_axislabel]:
                warnings.warn(
                    "x-axis label is overwritten from "
                    + str(ax.get_xlabel())
                    + " to "
                    + x_axislabel
                )
            ax.set_xlabel(x_axislabel)

        if type(y_col) == str:
            y_axislabel = get_axis_label(y_col)
            if ax.get_ylabel() not in ["", y_axislabel]:
                warnings.warn(
                    "y-axis label is overwritten from "
                    + str(ax.get_ylabel())
                    + " to "
                    + y_axislabel
                )
            ax.set_ylabel(y_axislabel)

    def _data_timestamp_to_seconds(self, data, col):
        """
        Translate values of timestamp to seconds relative to the first data point.
        Datapoints not in the experimental list will be ignored.
        :param data: pandas.DataFrame
            data used to plot.
        :param col: str
            name of the column in data with timestampt unit
        :return: pandas.Series
            seconds relative to the first data point.
        """
        data_selected = data.loc[
            (
                data.reset_index()
                .set_index(self._obj.index.names)
                .index.isin(self._obj.index)
            ),
            :,
        ]
        return (
            pd.to_datetime(data_selected.loc[:, col])
            - pd.to_datetime(data_selected.loc[:, col].iloc[0])
        ).dt.total_seconds()

    def plot(
        self,
        x_col,
        y_col,
        xerr_col=None,
        yerr_col=None,
        data=None,
        con=None,
        ax=None,
        print_info=False,
        axlabel_auto=True,
        timestamp_cols_to_seconds=True,
        export_object=None,
        export_name="plot_unspecified",
        plot_type="plot",
        # rowindexer=None, # idea to select experiments here and only loop over these
        **plt_kwargs,
    ):
        """
        Core function to display all experiments in an experimental dataset in one command. The index of the given data
        DataFrame should have one additional column to the index of the experiment. Different types of plot are
        available based on matplotlib plotting functions (Also refer to DataSet.fill_between, DataSet.scatter,
        DataSet.bar, DataSet.fit, Dataset.Integrate). Axis labels will be automatically set based on name of the
        selected data columns, this can be toggled off by axlabel_auto=False. Any plot style parameters which should be
        applied to all experiments can be set here. Experiment depending style parameter should be set beforehand in the
        experimental dataset. By specifying for example a column 'color' with the individual color for each experiment.
        :param x_col: str or int or float
            if data is not None: name of the x column in data DtaFrame
            if data is None: name of the x column in experimental dataset (caller)
                or integer/float (will create a new column in caller)
        :param y_col: str or int or float
            if data is not None: name of the y column in data DtaFrame
            if data is None: name of the y column in experimental dataset (caller)
                or integer/float (will create a new column in caller)
        :param xerr_col: str
            name of the x error column in data DtaFrame, to be displayed as horizontal errorbars
        :param yerr_col: str
            name of the y error column in data DtaFrame, to be displayed as vertical errorbars
        :param data: pd.DataFrame or str or None
            data for the experiments in the experimental dataset (caller)
            if str: name of the table form which to get data from
            if None: columns from caller will be searched for data
        :param con: sqlalchemy.engine.base.Engine | sqlalchemy.engine.base.Connection or None
            database connection
        :param ax: matplotlib.Axes object or str or None
            Axes where to put the plot.
            if str: name of the column in experimental dataset (caller)
            None: current axes is received from plt.gca()
        :param print_info: bool
            whether to print additional info to debug and get style paramters
        :param axlabel_auto: bool
            whether to toggle on or off autimatic placemt of axis labels
        :param timestamp_cols_to_seconds: bool
            íf True and x_col or y_col is of type timestamp a new column with relative seconds from first datapoint will
            be created and used for plot
        :param export_object: PlotDataStorage object or None
            append to PlotDataStorage object. If None new is created
        :param export_name: str, default 'plot_unspecified'
            name of the plot as stored in PlotDataStorage
        :param plot_type: str one of ['plot', 'fill_between', 'scatter', 'bar'], default 'plot'
            plot: either matplotlib.pyplot.plot or matploltib.pyplot.errorbar
            others as matplotlib function. Also refer to DataSet.fill_between, DataSet.scatter, DataSet.bar
        :param plt_kwargs:
        :return:
        """

        if len(self._obj.index) == 0:
            return self

        if type(ax) != str:
            if ax is None:
                ax = plt.gca()  # get current axis
            self._obj.loc[:, "ax"] = ax
            ax_col = "ax"
        else:
            ax_col = ax

        if export_object is None:
            export_object = current_PlotDataStorage()
        add_data_to_export_object = export_object is not None and data is not None
        # print(x_col, y_col)

        if not self._obj.index.is_unique:
            raise Exception(
                "Index of dataset dataframe is not unique! Only provide unique index, "
                "check index and add another column if necessary"
            )
        if type(data) == pd.DataFrame:
            # if (type(x_col) != str or type(y_col) != str): # support x=str and y=int but its too much effort
            #    x_col = x_col if type(x_col) == str else data.loc[:, x_col]
            #    y_col = y_col if type(y_col) == str else data.loc[:, y_col]
            if (
                x_col in data.columns
                or type(x_col) == int
                and y_col in data.columns
                or type(y_col) == int
            ):
                plot_data = data.sort_index()
            else:
                raise ValueError(
                    str(x_col)
                    + " or "
                    + str(y_col)
                    + " not found in data columns ("
                    + data.columns
                    + ")"
                )
        elif data in ["data_ec", "data_ec_analysis", "data_eis"] and con is not None:
            if type(con) in [sql.engine.base.Engine, sql.engine.base.Connection]:
                plot_data = pd.read_sql(
                    "SELECT * \
                                        FROM "
                    + data
                    + " \
                                        WHERE id_exp_ec IN ("
                    + ",".join(self._obj.index.to_numpy(dtype=str))
                    + ");",
                    con=con,
                    index_col=["id_exp_ec", "id_" + data.replace("_analysis", "")],
                )
                # print(plot_data)
            else:
                raise ValueError(
                    x_col
                    + " or "
                    + y_col
                    + " not found in data columns ("
                    + data.columns
                    + ")"
                )
        elif data is None:

            if type(x_col) == str or type(y_col) == str:
                if type(x_col) == str and x_col not in self._obj.columns:
                    raise ValueError(
                        str(x_col)
                        + " not found in caller's columns ("
                        + self._obj.columns
                        + ")"
                    )
                elif type(x_col) in (int, float):
                    x_col_name = "x_col__int"
                    if x_col_name in self._obj.columns:
                        warnings.warn(
                            "Column: "
                            + x_col_name
                            + " is already defined and will be overwritten"
                        )
                    self._obj.loc[:, x_col_name] = x_col
                    x_col = x_col_name
                if type(y_col) == str and y_col not in self._obj.columns:
                    raise ValueError(
                        str(y_col)
                        + " not found in caller's columns ("
                        + self._obj.columns
                        + ")"
                    )
                elif type(y_col) in (int, float):
                    y_col_name = "y_col__int"
                    if y_col_name in self._obj.columns:
                        warnings.warn(
                            "Column: "
                            + y_col_name
                            + " is already defined and will be overwritten"
                        )
                    self._obj.loc[:, y_col_name] = y_col
                    y_col = y_col_name
                plot_data = self._obj

            else:
                plot_data = None
                timestamp_cols_to_seconds = False
                axlabel_auto = False

                x_col = [x_col] if type(x_col) == int else x_col
                y_col = [y_col] if type(y_col) == int else y_col
                if len(x_col) != len(y_col):
                    if len(x_col) == 1 or len(y_col) == 1:
                        x_col = x_col * len(y_col) if len(x_col) == 1 else x_col
                        y_col = y_col * len(x_col) if len(y_col) == 1 else y_col
                    else:
                        raise ValueError(
                            "and y must have same first dimension, but have shapes x:"
                            + str(len(x_col))
                            + ", y:"
                            + str(len(y_col))
                        )
        else:
            raise ValueError(
                "Cannot handle given value for data. Either give pd.Dataframe or name of data table"
            )

        # Timestamp cols to seconds
        if timestamp_cols_to_seconds:
            for col in plot_data.columns[
                (plot_data.dtypes == "datetime64[ns]")
                & plot_data.columns.isin([x_col, y_col])
            ]:
                if col == x_col:
                    x_col = col + "__s"
                    plot_data.loc[:, x_col] = self._data_timestamp_to_seconds(data, col)
                    print("Adjusted x_col to ", x_col)
                elif col == y_col:
                    y_col = col + "__s"
                    plot_data.loc[:, y_col] = self._data_timestamp_to_seconds(data, col)
                    print("Adjusted y_col to ", y_col)
        # print(x_col, y_col)

        possible_kwarg_params_name = self._get_possible_kwargs(
            matplotlib.lines.Line2D.set
        )
        if plot_type == "scatter":
            possible_kwarg_params_name += [
                "c",
                "s",
                "cmap",
                "norm",
                "vmin",
                "vmax",
                "linewidths",
                "edgecolors",
                "plotnonfinite",
            ]
        if plot_type == "bar":
            possible_kwarg_params_name += ["hatch"]

        # add column ax_plot_objects and initialize as empty list (little workaround)
        if "ax_plot_objects" not in self._obj.columns:
            self._obj.loc[:, "ax_plot_objects"] = np.nan
            self._obj.loc[:, "ax_plot_objects"] = self._obj.loc[
                :, "ax_plot_objects"
            ].apply(
                lambda d: d if isinstance(d, list) else []
            )  # [[] for i in range(len(self._obj.index))]

        if add_data_to_export_object:
            # for ax in self._obj[ax_col].unique():
            export_Dataset_object = export_object.add_DataSet(
                ax_list=self._obj[ax_col].unique(),  # ax,
                export_name=export_name,
                data_type="PlotData",
                params=locals(),
                exp=self._obj,
                data=data,
            )
            # print(export_Dataset_object)
            # if not export_object.has_exp(ax.ax_name, export_name):
            #    export_object.exp.append({'ax_name': ax.ax_name,
            #                           'export_name': export_name,
            #                           'exp': pd.DataFrame()})

        # loop over all experiments and plot each experiment row
        for i, (index, row) in enumerate(self._obj.iterrows()):
            plt_kwargs_extended = self._extend_kwargs_from_dataframe(
                row, index, plt_kwargs, possible_kwarg_params_name
            )
            print(
                plt_kwargs_extended, (index,) not in plot_data.index
            ) if print_info else ""

            # get ax from caller DataFrame
            ax = row[ax_col]
            # Configure axis labels
            if axlabel_auto:
                self._plot_labels(x_col, y_col, ax)

            empty_plot = False
            if plot_data is not None and index not in plot_data.index:
                warnings.warn(
                    "index: "
                    + str(index)
                    + " does not exist in data table. Will be skipped and not plotted"
                    + (
                        plt_kwargs_extended["label"]
                        if "label" in plt_kwargs_extended.keys()
                        else " no label given"
                    )
                )
                empty_plot = True
                # self._obj.loc[index, 'ax_plot_objects'].append(ax.plot([], [], **plt_kwargs_extended))
                # continue
            # print('dimensions')
            # print(data.loc[index, :][x_col].shape, data.loc[index, :][y_col].shape)
            # print(data.loc[index, :])
            param_data = (
                plot_data.loc[index, :]
                if plot_data is not None and not empty_plot
                else None
            )
            if plot_type == "plot":
                if yerr_col is None and xerr_col is None:
                    if empty_plot:
                        (plot,) = ax.plot([], [], **plt_kwargs_extended)
                    else:
                        (plot,) = ax.plot(  # x = data.loc[index, x_col],
                            # y = data.loc[index, y_col],
                            x_col,
                            y_col,
                            data=param_data,
                            # data.loc[index, :] if type(data) != type(None) else row,
                            **plt_kwargs_extended,
                        )
                else:
                    if empty_plot:
                        plot = ax.errorbar([], [], **plt_kwargs_extended)
                    else:
                        plot = ax.errorbar(  # x = data.loc[index, x_col],
                            # y = data.loc[index, y_col],
                            x_col,
                            y_col,
                            yerr=yerr_col,
                            xerr=xerr_col,
                            data=param_data,
                            **plt_kwargs_extended,
                        )
            elif plot_type == "fill_between":
                # print('sss',param_data)
                if empty_plot:
                    plot = ax.fill_between([], [], **plt_kwargs_extended)
                else:
                    plot = ax.fill_between(
                        x_col,
                        y_col,
                        # y2_col,
                        data=param_data,  # ,plot_data.loc[index, :],
                        # data.loc[index, :] if type(data) != type(None) else row,
                        **plt_kwargs_extended,
                    )
            elif plot_type == "scatter":
                if empty_plot:
                    plot = ax.scatter([], [], **plt_kwargs_extended)
                else:
                    # print('sss',param_data)
                    plot = ax.scatter(
                        x_col,
                        y_col,
                        data=param_data,  # ,plot_data.loc[index, :],
                        # data.loc[index, :] if type(data) != type(None) else row,
                        **plt_kwargs_extended,
                    )

            elif plot_type == "bar":
                if empty_plot:
                    (plot,) = ax.scatter([], [], **plt_kwargs_extended)
                else:
                    (plot,) = [
                        ax.bar(
                            x=x_col,
                            height=y_col,
                            yerr=yerr_col,
                            data=param_data,
                            edgecolor=plt_kwargs_extended["edgecolor"]
                            if "edgecolor" in plt_kwargs_extended.keys()
                            else "black",
                            **plt_kwargs_extended,
                        )
                    ]
                    ax.set_xlabel("")

            # write plot object in ax_plot_x column
            if type(self._obj.loc[index, "ax_plot_objects"]) != list:
                print("error for ax_plot_objects  in", self._obj.loc[index, :])
            self._obj.loc[index, "ax_plot_objects"].append([plot])
            if add_data_to_export_object:
                export_object.add_DataItem(
                    ax=ax,
                    export_Dataset_object=export_Dataset_object,
                    export_name=export_name,
                    data_type="PlotData",
                    params=locals(),
                    exp_row_index=index,
                    item=plot,
                )
        return self

    def fit(
        self,
        model,
        x_col,
        y_col,
        data,
        y_col_fitted=None,
        xerr_col=None,
        yerr_col=None,
        beta0=None,
        ifixb=None,
        confidence_interval=1,
        ax=None,
        label=None,
        label_fit=True,
        label_fit_overwrite=False,
        label_fit_style=None,
        exp_col_label="",
        display_fit=True,
        method="scipy.optimize.curve_fit",
        debug=False,
        **plt_kwargs,
    ):
        """
        Perform a fit of any defined type for all experiments defined in the caller on a column in the data dataframe.
        Parameters are stored in experimental dataset (caller) and fit data in data. Fit result are plotted by default.
        :param model: Function
            for example plot.linear_func, plot.tafel_func, ask Admin to implement more or create your own.
        :param x_col: str
            column name in the caller for the x data in data DataFrame
        :param y_col: str
            column name in the caller for the y data in data DataFrame
        :param data: pandas.DataFrame
            DataFrame with all the data. The index in data DataFrame must be complementary to the experimental
            dataset (caller)
        :param y_col_fitted: str
            name of the column in data DataFrame, where the fitted data will be stored.
            If exist in data DataFrame, column will be overwritten.
        :param xerr_col: str
            column name in the caller for the xerr data in data DataFrame
        :param yerr_col: str
            column name in the caller for the yerr data in data DataFrame
        :param beta0: list of float
            initial guess of the fitting parameters of the requested model.
        :param ifixb: list of int
            select which parameter to optimize.
                =0: fix the parameter,
                >0: optimize the parameter.
            Only available for method='scipy.odr'
        :param confidence_interval: int 0<confidence_interval<1
            choose a confidence interval from which outliers of preliminary fit will be removed
            and a second fit will be performed.
            Default =1. Only first fit will be performed
        :param ax: Matplotlib.Axes object or str
            Axes object or
            if str: column name in the caller, which refers to an Axes Object for each dataset.
        :param label: str
            additional label for the fitted plot
        :param label_fit_overwrite: bool
            whether label of fit should be overwritten
        :param label_fit: bool
            add a fit specific label to the label?
        :param label_fit_style: create_fit_label()
            style of the added label Use corresponding function create_fit_label()
        :param exp_col_label: str
            prefix label for the columns added for the fit parameter to the experimental dataset (caller)
        :param display_fit: bool
            whether or not to plot the fit result
        :param method: str one of ['scipy.optimize.curve_fit', 'scipy.odr'], 'scipy.optimize.curve_fit'
            default  check corresponding documentation for details
        :param plt_kwargs: keyword arguments of pd.DataFrame.dataset.plot and matplotlib.pyplot.plot
        :return: self
        """

        if label_fit_style is None:
            label_fit_style = create_fit_label()

        if ax is None:
            ax = plt.gca()  # get current axis

        if y_col_fitted is None:
            y_col_fitted = y_col + "_fitted"
            i = 2
            if y_col_fitted in data.columns:
                y_col_fitted = y_col_fitted + str(i)
            while y_col_fitted in data.columns:
                i += 1
                y_col_fitted = y_col_fitted[: -len(str(i - 1))] + str(i)
        elif y_col_fitted in data.columns:
            warnings.warn("Column " + y_col_fitted + " will be overwritten")
            data.loc[:, y_col_fitted] = np.nan
        print("FitData is stored in column: ", y_col_fitted)

        # init column label_fit
        # if 'label_fit' in self._obj.columns:
        #    warnings.warn('Column label_fit will be overwritten')
        if label_fit:
            self._obj.loc[:, "label_fit"] = ""

        self.data = data.sort_index()  # adjust this as in .plot
        # possible_kwarg_params_name = self._get_possible_kwargs(matplotlib.lines.Line2D.set)

        # init exp_col_label
        exp_col_label = exp_col_label + "_" if exp_col_label != "" else ""

        for i, (index, row) in enumerate(self._obj.iterrows()):
            if data is not None and index not in data.index:
                warnings.warn(
                    "index: "
                    + str(index)
                    + " does not exist in data table. Will be skipped and not plotted"
                )
                continue

            if method == "scipy.optimize.curve_fit":
                warnings.warn(
                    "ifixb parameter will be ignored. "
                    "Using scipy.optimize.curve_fit all parameters of the requested model are optimized."
                ) if ifixb is not None else ""
                if yerr_col is not None and xerr_col is None:
                    [x, y, sigma] = [
                        self.data.loc[index, col].astype(float)
                        for col in [x_col, y_col, yerr_col]
                    ]
                # elif xerr_col is not None and yerr_col is None:
                # consideration of only xerr would require inversed function
                #    [x, y, sigma] = [self.data.loc[index, col].astype(float) for col in
                #                                              [y_col, x_col, xerr_col]]
                elif [xerr_col, yerr_col] == [None, None]:
                    [x, y, sigma] = [
                        self.data.loc[index, col].astype(float)
                        for col in [x_col, y_col]
                    ] + [None]
                else:
                    sys.exit(
                        "Fitting with "
                        + method
                        + " is only possible with an uncertainty given in one parameter, "
                          "but xerr_col and yerr_col both are given."
                    )

                fit_results = curve_fit_odr_style(
                    model, x, y, p0=beta0, sigma=sigma, absolute_sigma=True
                )
                if confidence_interval < 1:
                    y_fit = model(fit_results.beta, x).values
                    res = y_fit - y
                    sigmas = norm.ppf(np.sqrt(confidence_interval))  # 3
                    idx_selected = (res < sigmas * np.std(res)) & (
                        res > -sigmas * np.std(res)
                    )

                    warning_color = (
                        "31"
                        if 100 - len(res.loc[idx_selected]) / len(res) * 100 > 10
                        else "33"
                    )
                    print(
                        "\x1b[" + warning_color + "m",
                        "Removed ",
                        100 - len(res.loc[idx_selected]) / len(res) * 100,
                        "% of data for ",
                        index,
                        "\x1b[0m",
                    )
                    fit_results = curve_fit_odr_style(
                        model,
                        x.loc[idx_selected],
                        y.loc[idx_selected],
                        p0=beta0,
                        sigma=sigma.loc[idx_selected] if sigma is not None else None,
                        absolute_sigma=True,
                    )

            elif method == "scipy.odr":
                if confidence_interval != 1:
                    warnings.warn(
                        "confidence_interval not implemented yet for scipy.odr"
                    )
                fit_results = ODR(
                    RealData(
                        self.data.loc[index, x_col].astype(float),
                        self.data.loc[index, y_col].astype(float),
                        sx=self.data.loc[index, xerr_col]
                        if xerr_col is not None
                        else None,
                        sy=self.data.loc[index, yerr_col]
                        if yerr_col is not None
                        else None,
                    ),
                    Model(model),
                    beta0=beta0,
                    ifixb=ifixb,
                ).run()
                # print(fit_results.beta)
            else:
                sys.exit("Fitting method does not exist: " + method)
            fit_label = model("label", 0)

            res_var = fit_results.res_var if hasattr(fit_results, "res_var") else None
            rsquared = (
                fit_results.rsquared if hasattr(fit_results, "rsquared") else None
            )
            # Not available for scipy.odr:
            # read https://stackoverflow.com/questions/21395328/how-to-estimate-goodness-of-fit-using-scipy-odr

            for param_label, value, stdev in zip(
                fit_label["beta0"], fit_results.beta, fit_results.sd_beta
            ):
                self._obj.loc[
                    index, exp_col_label + fit_label["model"] + "_" + param_label
                ] = value
                self._obj.loc[
                    index,
                    exp_col_label + fit_label["model"] + "_" + param_label + "_sd",
                ] = stdev
                if debug:
                    print("value: ", value, "stdev:", stdev)
            # self._obj.loc[:, fit_label['model'] + '_Rsquare'] = fit_results.res_var
            self._obj.loc[
                index, exp_col_label + fit_label["model"] + "_ResVar"
            ] = res_var
            self._obj.loc[
                index, exp_col_label + fit_label["model"] + "_Rsquared"
            ] = rsquared
            self._obj.loc[index, exp_col_label + "fit_method"] = method  # 'scipy.odr'

            self.data.loc[index, y_col_fitted] = model(
                fit_results.beta, self.data.loc[index, x_col].astype(float)
            ).values

            if label_fit:
                if label_fit_style["description"]:
                    self._obj.loc[index, "label_fit"] += (
                        fit_label["model"]
                        + " ("
                        + fit_label["formula"]
                        + ") using "
                        + method
                        + "\n"
                    )
                if label_fit_style["params"]:
                    self._obj.loc[index, "label_fit"] += (
                        "    "
                        + "\n    ".join(
                            [
                                label + " = %.4f $\pm$ %.4f" % (value, stdev)
                                for label, value, stdev in zip(
                                    fit_label["beta0"],
                                    fit_results.beta,
                                    fit_results.sd_beta,
                                )
                            ]
                        )
                        + "\n"
                    )
                if label_fit_style["rsquared"]:
                    self._obj.loc[index, "label_fit"] += (
                        "    $R^2$ = %.6f" % rsquared
                        if rsquared is not None
                        else "    res var = %.6f" % res_var
                    ) + "\n"
                if label_fit_style["err_considered"]:
                    self._obj.loc[index, "label_fit"] += (
                        "    yerr considered"
                        if yerr_col is not None
                        else "    yerr not considered"
                    )
                self._obj.loc[index, "label_fit"] = self._obj.loc[
                    index, "label_fit"
                ].strip("\n")

        if display_fit:
            if (
                "label" not in self._obj.columns or label_fit_overwrite
            ):  # initialize or reset label
                self._obj.loc[:, "label"] = ""

            if label is not None:
                self._obj.loc[:, "label"] += label

            if label_fit:
                self._obj.loc[:, "label"] += self._obj.loc[:, "label_fit"]

            """
            if label_fit:
                if label is None:
                    if 'label' not in self._obj.columns or label_fit_overwrite:
                        self._obj.loc[:, 'label'] = ''
                    self._obj.loc[:, 'label'] = self._obj.loc[:, 'label'] + self._obj.loc[:, 'label_fit']
                else:
                    self._obj.loc[:, 'label'] = label + self._obj.loc[:, 'label_fit']
            """

            self.plot(
                x_col=x_col, y_col=y_col_fitted, data=self.data, ax=ax, **plt_kwargs
            )

        return self

    def integrate(self, y_col, **plt_kwargs):
        """
        Manual integration tool used for integration of SFC-ICPMS experiments. This might not work for other cases.
        :param y_col: str
            name of the y data column
        :param plt_kwargs: keyword arguments of IntegrateContainer
        :return: self
        """
        if y_col == "dm_dt__ng_s":
            integration.IntegrateContainerICPMS(
                objExp_df=self._obj,
                objExp_df_export_name=self._obj.export_name,
                y_col=y_col,
                **plt_kwargs,
            )
        elif y_col == "I__A":
            integration.IntegrateContainerEC(
                objExp_df=self._obj,
                objExp_df_export_name=self._obj.export_name,
                y_col=y_col,
                **plt_kwargs,
            )
        else:
            integration.IntegrateContainer(
                objExp_df=self._obj,
                objExp_df_export_name=self._obj.export_name,
                y_col=y_col,
                db_update=False,
                **plt_kwargs,
            )
        return self

    def fill_between(self, y2_col=0, **plt_kwargs):
        """
        Extension to .plot, to implement matplotlib.pyplot.fill_between.
        :param y2_col: str
            name of the second y-col. Area between y_col and y2_co will be filled.
        :param plt_kwargs: keyword arguments of evaluation.visualization.plot
        :return: self
        """
        self.plot(plot_type="fill_between", y2=y2_col, **plt_kwargs)
        return self

    def scatter(self, **plt_kwargs):
        """
        Extension to .plot, to implement matplotlib.pyplot.scatter.
        :param plt_kwargs: keyword arguments of evaluation.visualization.plot
        :return: self
        """
        self.plot(plot_type="scatter", **plt_kwargs)
        return self

    def bar(
        self,
        x_col=None,
        sort_groups_by=None,
        width_between_groups=0.5,
        width_between_bars=0,
        data=None,
        ax=None,
        **plt_kwargs,
    ):
        """
        Extension to .plot, to implement matplotlib.pyplot.bar. In addition, x position of the bars will be caluclated
        from the value in x_col. Bars with the same x-value will be grouped and will be displayed with no distance to
        each other by default which can be adjusted by width_between_bars. Distance between groups is 0.5 bar width
        by default and can be adjusted by width_between_groups.
        :param x_col: str
            name of the x column
        :param sort_groups_by: list
            list of x_col values in their order of how they should be displayed.
        :param width_between_groups: float
            width between groups of bars in units of width of the bar
        :param width_between_bars: float
            witdh between bars within a group in units of width of the bar
        :param data: None
            Multiple bars per experiment is not yet supported.
        :param ax: matplotlib.Axes object or None
            Axes on to which to plot the bars
            str: name of the column in experimental dataset not yet supported.
        :param plt_kwargs: keyword arguments of evaluation.visualization.plot
        :return: self
        """

        width_bars = 1
        if data is None:
            data = self._obj.copy()
        else:
            raise Exception("Multiple bars per experiment not yet supported.")

        df_groups = (
            data.groupby([x_col])[
                [
                    x_col,
                ]
            ]
            .count()
            .rename(columns={x_col: "size"})
        )  # .sort_index()
        if sort_groups_by is not None:
            # sort_by = ['before', 'after']  # [::-1] # or data.loc[:, x_col].unique()
            df_sort_by = (
                pd.DataFrame(sort_groups_by, columns=[x_col])
                .reset_index()
                .set_index(x_col)
                .rename(columns={"index": "sort_by"})
            )
            df_sort_by.loc[:, "sort_by"] = df_sort_by.loc[:, "sort_by"]
            df_groups = df_groups.join(df_sort_by).sort_values(by="sort_by")
        else:
            df_groups = (
                df_groups.reset_index()
                .reset_index()
                .set_index(x_col)
                .rename(columns={"index": "sort_by"})
            )

        width_group_max = df_groups.loc[:, "size"].max()
        width_group = (width_group_max + width_between_groups) * width_bars
        df_groups.loc[:, "x_ticks_pos"] = (
            df_groups.loc[:, "sort_by"] + 1 / 2
        ) * width_group
        # display(df_groups)

        data["x_pos"] = np.nan
        data_index = (
            data.index.names if data.index.names is not None else data.index.name
        )
        data = data.reset_index()  # in case the given indexs have not been unique
        for index, row in data.iterrows():
            # print(index)
            # position of bar in group
            current_size_of_group = data.loc[
                (data.loc[:, x_col] == row[x_col]) & (data.loc[:, "x_pos"].notna()),
                "x_pos",
            ].shape[0]
            # print(current_size_of_group)
            # position of bar on x-axis
            data.loc[index, "x_pos"] = (
                (width_group_max - df_groups.loc[row[x_col], "size"]) / 2
                + (width_between_groups + 1) / 2
                + current_size_of_group
            ) * width_bars + df_groups.loc[row[x_col], "sort_by"] * width_group

        data = data.set_index(data_index)

        if type(ax) == str:
            raise Exception("ax defined in caller column not yet supported for .bar()")
        if ax is None:
            ax = plt.gca()  # get current axis

        ax.set_xticks(df_groups["x_ticks_pos"].to_numpy(), df_groups.index.to_numpy())
        ax.tick_params(axis="x", which="minor", bottom=False, top=False)
        ax.tick_params(axis="x", which="major", top=False, bottom=True, direction="out")
        return self.plot(
            plot_type="bar",
            x_col="x_pos",
            width=width_bars - width_between_bars,
            data=data,
            ax=ax,
            **plt_kwargs,
        )

    def vlines(self, x_col, ymin=None, ymax=None, data=None, ax=None, **plt_kwargs):
        """
        Implementation of vertical lines for multiple experiments matplotlib.pyplot.vlines.
        :param x_col: str or int or float
            name of the x column in data
            or value where to set the vertical line
        :param ymin: int or float
            y-minimum of the line
        :param ymax: int or float
            y-maximum of the line
        :param data: pd.DataFrame  or None
            data for the experiments in the experimental dataset (caller)
            if None: columns from caller will be searched for data
        :param ax: matplotlib.Axes objector None
            Axes where to put the plot.
            None: current axes is received from plt.gca()
        :param plt_kwargs:
        :return: self
        """
        if ax is None:
            ax = plt.gca()
        # print(ax)

        ylim = ax.get_ylim()
        if isinstance(ymin, type(None)):
            ymin = ylim[0]
        if isinstance(ymax, type(None)):
            ymax = ylim[1]

        possible_kwarg_params_name = self._get_possible_kwargs(matplotlib.lines.Line2D)
        for i, (index, row) in enumerate(self._obj.iterrows()):
            plt_kwargs_extended = self._extend_kwargs_from_dataframe(
                row, index, plt_kwargs, possible_kwarg_params_name
            )
            ax.vlines(
                x_col,
                ymin,
                ymax,
                data=data.loc[index, :] if not isinstance(data, type(None)) else row,
                **plt_kwargs_extended,
            )
            print(row[x_col], ymin, ymax)
        return ax

    def hlines(self, y_col, xmin=None, xmax=None, data=None, ax=None, **plt_kwargs):
        """
        Implementation of horizontal lines for multiple experiments matplotlib.pyplot.hlines.
        :param y_col: str or int or float
            name of the x column in data
            or value where to set the vertical line
        :param xmin: int or float
            x-minimum of the line
        :param xmax: int or float
            x-maximum of the line
        :param data: pd.DataFrame  or None
            data for the experiments in the experimental dataset (caller)
            if None: columns from caller will be searched for data
        :param ax: matplotlib.Axes objector None
            Axes where to put the plot.
            None: current axes is received from plt.gca()
        :param plt_kwargs:
        :return: self
        """
        if ax is None:
            ax = plt.gca()
        # print(ax)

        xlim = ax.get_xlim()
        if isinstance(xmin, type(None)):
            xmin = xlim[0]
        if isinstance(xmax, type(None)):
            xmax = xlim[1]

        possible_kwarg_params_name = self._get_possible_kwargs(matplotlib.lines.Line2D)
        for i, (index, row) in enumerate(self._obj.iterrows()):
            plt_kwargs_extended = self._extend_kwargs_from_dataframe(
                row, index, plt_kwargs, possible_kwarg_params_name
            )
            ax.hlines(
                y_col,
                xmin,
                xmax,
                data=data.loc[index, :] if not isinstance(data, type(None)) else row,
                **plt_kwargs_extended,
            )
            print(row[y_col], xmin, xmax)
        return ax

    # TODO: add more plot types, see https://matplotlib.org/stable/api/axes_api.html#plotting

    def create_dataset(self, **plt_kwargs):
        """
        Interactive creation of a dataset. Used for SFC-ICPMS integration. Other usecases not tested.
        :param plt_kwargs: keywords of evaluation.processing.integration.CreateDataset()
        :return:
        """
        integration.CreateDataset(objExp=self, **plt_kwargs)
        return self


def current_PlotDataStorage():
    """
    Helper to get current PlotDataStorage object
    :return:
    """
    if len(PlotDataStorage.instanceArr) == 0:
        # warnings.warn('PlotDataStorage not initiated. No plot data will be stored.')
        return None
    return PlotDataStorage.instanceArr[-1]


class PlotDataStorage:
    """
    class to store all PlotData into an objectc
    """

    instanceArr = []

    def __init__(self, name, overwrite_existing):
        """
        Initialize a PlotDataStorage object
        :param name:
        :param overwrite_existing:
        """
        try:
            if name in [ob.name for ob in self.__class__.instanceArr]:
                if overwrite_existing:
                    while name in [ob.name for ob in self.__class__.instanceArr]:
                        self.__class__.instanceArr.remove(
                            [
                                ob
                                for ob in self.__class__.instanceArr
                                if ob.name == name
                            ][0]
                        )
                else:
                    warnings.warn(
                        "PlotDataStorage "
                        + name
                        + " already exists but is not overwritten."
                        + " Please use a different name or overwrite_existing=True to avoid duplicates "
                        + "and consistent naming."
                    )
        except ReferenceError:
            warnings.warn(
                "weakly reference error, all PlotDataStorage objects are deleted."
            )
            # print(len(self.__class__.instanceArr))
            self.__class__.instanceArr = []
        self.__class__.instanceArr.append(weakref.proxy(self))
        self.name = name
        self.DataSets = []
        self.DataItems = []
        self.df_PlotDataSets = pd.DataFrame()
        self.df_PlotDataItems = pd.DataFrame()
        self.df_IntegrationDataSets = pd.DataFrame()
        self.dict_PlotDataSets = {}
        self.dict_PlotDataItems = {}
        self.dict_IntegrationDataSets = {}
        self.dict_exps = {}  # has structure df.export_name: df
        self.dict_datas = {}  # has structure df.export_name: df
        # self.IntegrationDataObjs = []

    def add_DataItem(
        self,
        ax,
        export_Dataset_object,
        export_name,
        data_type,  # ='PlotData',
        # exp_export_name,
        exp_row_index,
        params,
        item,
        # **item_kwargs
    ):
        """
        Add a data item to the DataStorage.
        :param ax: Matplotlib.Axes
            axes on which the data was plotted
        :param export_Dataset_object:
            export_Dataset_object
        :param export_name: str
            name of the DataItem (plot)
        :param data_type: str one of ['PlotData']
        :param exp_row_index: pandas.Index or pandas.MultiIndex
            index of the row to which the DataItem belongs
        :param params: dict
            parameter of the evaluation.visualization.plot parameter
        :param item: Matplotlib.pyplot artist
            artis added to the plot
        :return:
        """
        if data_type == "PlotData":
            self.DataItems.append(
                self.DataItem(
                    ax,
                    export_Dataset_object,
                    export_name,
                    data_type,  # ='PlotData',
                    # exp_export_name,
                    exp_row_index,
                    params,
                    item,
                )
            )
        else:
            sys.exit("Not implemented")

    def add_DataSet(self, ax_list, export_name, data_type, **kwargs):
        """
        Add a DataSet to DataStorage.
        :param ax_list:
        :param export_name:
        :param data_type: str, one of ['PlotData', 'IntegrationData']
        :param kwargs:
        :return: added DataSet
        """
        if data_type == "PlotData":
            DataSet = self.PlotDataSet(ax_list, export_name, data_type, **kwargs)
            self.DataSets.append(DataSet)

        elif data_type == "IntegrationData":
            self.DataSets.append(
                self.IntegrationDataSet(ax_list, export_name, data_type, **kwargs)
            )

        return self.DataSets[-1]

    def has_DataSet(self, ax_list, export_name, data_type):
        """
        Whether DataSet already exists in DataStorage
        :param ax_list: list of Matplotlib.Axes
        :param export_name:
        :param data_type:
        :return: bool
        """
        return [ax_list, export_name, data_type] in [
            [item.ax, item.export_name, item.data_type] for item in self.DataSets
        ]

    def structure_data(self):
        """
        Structure data in DataStorage according to DataSet subclass
        :return: None
        """
        self.dict_PlotDataSets = (
            {}
        )  # always reset when called, in case store method called multiply
        self.dict_PlotDataItems = {}
        self.dict_IntegrationDataSets = (
            {}
        )  # always reset when called, in case store method called multiply
        # self.df_PlotDataSets = pd.DataFrame()
        # self.df_PlotDataItems = pd.DataFrame()
        self.dict_exps = {}  # has structure df.export_name: df
        self.dict_datas = {}  # has structure df.export_name: df

        for i, DataSet in enumerate(self.DataSets):  #
            DataSet.structure(self, i)  # as defined in Dataset Subclass

            # print(self.dict_PlotDataSets[i])
        self.df_PlotDataSets = pd.DataFrame.from_dict(
            self.dict_PlotDataSets, orient="index"
        ).set_index("export_name")
        self.df_PlotDataItems = pd.DataFrame.from_dict(
            self.dict_PlotDataItems, orient="index"
        )  # .set_index('export_name')
        self.df_IntegrationDataSets = pd.DataFrame.from_dict(
            self.dict_IntegrationDataSets, orient="index"
        )  # .set_index('export_name')

    def export(
        self,
        fig,  # defined by plt.gcf() would only work before plt.show
        path="",
        plot_format="svg",
        # export_plot=True,
        export_data=False,
        auto_overwrite=False,
        print_obsidian_link=True,
        **kwargs,
    ):
        """
        Export plot as image/vector file (determined by plot_format) and corresponding data as csv (if export_data)
        :param fig: matplotlib.pyplot.Figure
            figure which to export,
            cannot be set by plt.gcf(), otherwise calling export function after plt.show() would not work
        :param path: pathlib.Path() or str
            Path where to export figure and data
        :param plot_format: str, default='svg'
            format of the plot
        :param export_data: bool
            whether to export data as csv
        :param auto_overwrite: bool
            whether to auto overwirte or ask for confirmation
        :param print_obsidian_link: bool
            whether to print a link which can be used within markdown editors such as obsidian
        :param kwargs: keyword arguments of pandas.to_csv and fig.savefig
        :return: None
        """
        # import inspect
        # print([param.name  for param in inspect.signature(pd.DataFrame.to_csv).parameters.values() ])
        # print([param.name  for param in inspect.signature(fig.savefig).parameters.values() ]) # doesn't work properly

        plot_kwargs = {
            key: value
            for key, value in kwargs.items()
            if key
            in [
                "dpi",
                "metadata",
                "bbox_inches",
                "pad_inches",
                "facecolor",
                "edgecolor",
                "backend",
                "orientation",
                "papertype",
                "transparent",
                "bbox_extra_artists",
            ]
        }
        data_kwargs = {
            key: value
            for key, value in kwargs.items()
            if key
            in [
                "sep",
                "na_rep",
                "float_format",
                "columns",
                "header",
                "index",
                "index_label",
                "mode",
                "encoding",
                "compression",
                "quoting",
                "quotechar",
                "lineterminator",
                "chunksize",
                "date_format",
                "doublequote",
                "escapechar",
                "decimal",
                "errors",
                "storage_options",
            ]
        }

        # print(fig==plt.gcf()) # should be equivalent

        # fig = plt.gcf()

        existing_files = []

        path = Path(path)
        if not path.is_dir():
            path.mkdir(parents=True, exist_ok=True)
            print("\x1b[32m", "Created missing folder in path: ", str(path), "\x1b[0m")
        plot_filename = path / Path(self.name + "." + plot_format)
        if plot_filename.is_file():
            print("\x1b[33m", "File ", str(plot_filename), " already exists", "\x1b[0m")
            existing_files.append([plot_filename])

        if export_data:
            data_pathname = path / Path(self.name)
            self.structure_data()
            if data_pathname.is_dir():
                print(
                    "\x1b[33m",
                    "Path ",
                    str(data_pathname),
                    " already exists",
                    "\x1b[0m",
                )
            else:
                os.mkdir(data_pathname)
                print(
                    "\x1b[32m",
                    "Successfully created folder ",
                    str(data_pathname),
                    "\x1b[0m",
                )

            self.data_files = {
                "PlotDataItems": self.df_PlotDataItems,
                "PlotDataSets": self.df_PlotDataSets,
                "IntegrationDataSets": self.df_IntegrationDataSets,
                **self.dict_exps,
                **self.dict_datas,
            }
            self.data_filenames = {}
            for data_filekey in self.data_files.keys():
                self.data_filenames[data_filekey] = data_pathname / (
                    data_filekey + ".csv"
                )
                if self.data_filenames[data_filekey].is_file():
                    print(
                        "\x1b[33m",
                        "File ",
                        str(self.data_filenames[data_filekey]),
                        " already exists",
                        "\x1b[0m",
                    )
            # self.df_PlotDataItems.to_csv()

        if len(existing_files) > 0 and not auto_overwrite:
            if not user_input.user_input(
                text="Overwrite?\n",
                dtype="bool",
                optional=False,
            ):
                print("\x1b[31m", "Nothing stored!", "\x1b[0m")
                return False

        fig.savefig(plot_filename, **plot_kwargs)
        print("\x1b[32m", "Plot ", str(plot_filename), " successfully saved", "\x1b[0m")

        if db.MYSQL:
            path_relative_to_root = ""
            if os.name != "nt":
                path_relative_to_root = str(
                    Path(os.getcwd()).relative_to(
                        Path(os.getcwd()).parents[
                            os.getcwd().split("/").index("jupyter") - 2
                        ]
                    )
                )
            # print("[link name]("+str(path_relative_to_root/str(plot_filename))+")")
            # display(Markdown("[link name]("+str(path_relative_to_root/str(plot_filename))+")"))
            if print_obsidian_link:
                print(
                    "![["
                    + str(path_relative_to_root + str(plot_filename))
                    + "]] <br> *jupyter notebook source:* ![["
                    + str(path_relative_to_root)
                    + "$$dummy_replaced_by_obsidian_jupyter$$]]"
                )
            # display(Javascript("""
            #          const b = document.createElement('pre');
            #          b.textContent="jupyter notebook source: ![[" + window.document.URL.split("/").slice(-1) + "]]";
            #          element.append(b);
            #          """)
            #        ) # nice idea but conversion within Obsidian looses information of window.document.URL

        if export_data:
            for data_filekey in self.data_files.keys():
                if not self.data_files[data_filekey].empty:
                    self.data_files[data_filekey].to_csv(
                        self.data_filenames[data_filekey], **data_kwargs
                    )
                    print(
                        "\x1b[32m",
                        "Datafile ",
                        str(self.data_filenames[data_filekey]),
                        " successfully saved",
                        "\x1b[0m",
                    )

    class DataItem:
        """
        class to store raw and processed data of plots
        """

        def __init__(
            self,
            ax,
            export_Dataset_object,
            export_name,
            data_type,  # ='PlotData',
            # exp_export_name,
            exp_row_index,
            params,
            item,
        ):
            """
            Add a data item to the DataStorage.
            :param ax: Matplotlib.Axes
                axes on which the data was plotted
            :param export_Dataset_object:
                export_Dataset_object
            :param export_name: str
                name of the DataItem (plot)
            :param data_type: str one of ['PlotData']
            :param exp_row_index: pandas.Index or pandas.MultiIndex
                index of the row to which the DataItem belongs
            :param params: dict
                parameter of the evaluation.visualization.plot parameter
            :param item: Matplotlib.pyplot artist
                artis added to the plot
            """
            self.ax = ax
            self.export_name = export_name
            self.data_type = data_type
            self.export_Dataset_object = export_Dataset_object
            # print(export_Dataset_object)
            # self.exp_export_name = export_Dataset_object.exp.export_name
            # self.data_export_name = export_Dataset_object.data.export_name
            self.exp_row_index = exp_row_index
            self.params = params
            self.item = item

    class DataSet:
        """
        class to store raw and processed data of plots
        """

        def __init__(self, ax_list, export_name, data_type):
            """

            :param ax_list:
            :param export_name:
            :param data_type:
            """
            self.ax_list = ax_list
            # if not hasattr(ax, 'export_name'):  # name
            #    ax.export_name = 'ax_export_name_unspecified'
            # warnings.warn(
            #    'Export_name of Axes is not specified.
            #    Specify by ax.export_name = "your_export_name" to make PlotDataStorage more comprehensive')
            # self.ax_name = ax.name
            self.export_name = export_name
            self.data_type = data_type

    class PlotDataSet(DataSet):
        """
        subclass to store rawdata of plot for purpose of reusing and exporting to csv
        """

        def __init__(self, ax, export_name, data_type, params, exp, data):
            """

            :param ax:
            :param export_name:
            :param data_type:
            :param params:
            :param exp:
            :param data:
            """
            self.params = params
            self.exp = exp
            # if not hasattr(self.exp, 'export_name'):
            # #not in self.dict_exps.keys(): # already defined in dataset.__init__
            #    self.exp.export_name = 'undefined'
            self.data = data
            if not hasattr(self.data, "export_name"):  # not in self.dict_exps.keys():
                self.data.export_name = str(self.exp.export_name) + "_data"
            super().__init__(ax, export_name, data_type)
            # super.__init__(super, ax_name, export_name, data_type)
            # DataSet.__init__(ax_name, export_name, data_type)

        def structure(self, PlotDataStorageObj, i):
            """

            :param PlotDataStorageObj:
            :param i:
            :return:
            """
            # self.dict_exps
            if self.exp.export_name not in PlotDataStorageObj.dict_exps.keys():
                PlotDataStorageObj.dict_exps[self.exp.export_name] = self.exp  # .copy()
            elif (
                self.exp.index.names
                == PlotDataStorageObj.dict_exps[self.exp.export_name].index.names
            ):
                idx_new_rows = ~self.exp.index.isin(
                    PlotDataStorageObj.dict_exps[self.exp.export_name].index
                )
                if idx_new_rows.any():
                    PlotDataStorageObj.dict_exps[self.exp.export_name] = pd.concat(
                        [
                            PlotDataStorageObj.dict_exps[self.exp.export_name],
                            self.exp.loc[idx_new_rows, :],
                        ]
                    )
                # else:
                #    print('No new experiment rows')
            else:
                raise ValueError(
                    "Name "
                    + str(self.exp.export_name)
                    + " already exists but with a different index. "
                    + "Each experiment dataset must have it's unique name"
                )

            # self.dict_datas
            if self.data.export_name not in PlotDataStorageObj.dict_datas.keys():
                PlotDataStorageObj.dict_datas[
                    self.data.export_name
                ] = (
                    self.data
                )  # .copy() # changes made later to data will be transferred -- link to object
            elif (
                self.data.index.names
                == PlotDataStorageObj.dict_datas[self.data.export_name].index.names
            ):
                idx_new_rows = ~self.data.index.isin(
                    PlotDataStorageObj.dict_datas[self.data.export_name].index
                )
                if idx_new_rows.any():
                    PlotDataStorageObj.dict_datas[self.data.export_name] = pd.concat(
                        [
                            PlotDataStorageObj.dict_datas[self.data.export_name],
                            self.data.loc[idx_new_rows, :],
                        ]
                    )

            # Name warnings
            if self.params["export_name"] == "plot_unspecified":
                self.params["export_name"] = self.params["y_col"]
                # warnings.warn(
                #    'Export name of '+ordinal(i+1)+' dataset plot is not specified.
                #    Specify by plot(export_name = "your export_name" to make PlotDataStorage more comprehensive')
            # No warning for same Dataset name - is handled before...
            # if DataSet.exp.export_name in [dict_DataSet['exp']
            # for key, dict_DataSet in self.dict_PlotDataSets.items()]:
            #    warnings.warn(
            #        'Dataset name "' + str(DataSet.exp.export_name) + '" already exists,
            #        consider using unique dataset names')

            #
            for j, DataItem in enumerate(
                [
                    DataItem
                    for DataItem in PlotDataStorageObj.DataItems
                    if DataItem.export_Dataset_object == self
                ]
            ):
                # print(DataItem.exp_export_name)
                if not hasattr(DataItem.ax, "export_name"):
                    warnings.warn(
                        'Export_name of Axes is not specified. Specify by ax.export_name = "your_export_name" to make '
                        "PlotDataStorage more comprehensive"
                    )
                    DataItem.ax.export_name = "ax_export_name_unspecified"
                PlotDataStorageObj.dict_PlotDataItems[(i, j)] = {
                    **dict(
                        ax_export_name=DataItem.ax.export_name,
                        Dataset_export_name=DataItem.params["export_name"],
                        # ax=DataItem.ax,
                        exp=DataItem.export_Dataset_object.exp.export_name,
                        data=DataItem.export_Dataset_object.data.export_name,
                        exp_row_index=DataItem.exp_row_index,
                        x_label=DataItem.ax.get_xlabel(),
                        y_label=DataItem.ax.get_ylabel(),
                    ),
                    **{
                        key: value
                        for key, value in DataItem.params.items()
                        if key
                        not in [
                            "self",
                            "data",
                            "con",
                            "plot_data",
                            "possible_kwarg_params_name",
                            "plt_kwargs",
                            "export_object",
                            "export_Dataset_object",
                            "export_name",
                        ]
                    },
                    **{
                        key: value
                        for key, value in DataItem.item.__dict__.items()
                        if key
                        not in [
                            "_xorig",
                            "_yorig",  # '_x', '_y',
                            "_xy",
                            "_path",
                            "_x_filled",
                            "export_object",
                        ]
                    },
                    # | dict()
                }

                # self.dict_PlotDataSets
                PlotDataStorageObj.dict_PlotDataSets[i] = {
                    **dict(  # ax_export_name=DataSet.params['ax'].export_name,
                        exp=self.exp.export_name,
                        data=self.data.export_name,
                        ax_list=self.ax_list,
                        ax_list_export_names=[ax.export_name for ax in self.ax_list],
                    ),
                    **{
                        key: value
                        for key, value in self.params.items()
                        if key
                        not in [
                            "self",
                            "data",
                            "con",
                            "plot_data",
                            "possible_kwarg_params_name",
                            "plt_kwargs",
                            "export_object",
                        ]
                    },
                    **dict(
                        x_label=self.params["ax"].get_xlabel(),
                        y_label=self.params["ax"].get_ylabel(),
                    ),
                }

    class IntegrationDataSet(DataSet):
        """
        class to store raw processed data of integration for purpose of reusing and exporting to database
        """

        def __init__(self, ax_list, export_name, data_type, IntegrateContainer):
            """

            :param ax_list:
            :param export_name:
            :param data_type:
            :param IntegrateContainer:
            """
            self.IntegrateContainer = IntegrateContainer
            super().__init__(ax_list, export_name, data_type)

        def structure(self, PlotDataStorageObj, i):
            """

            :param PlotDataStorageObj:
            :param i:
            :return:
            """
            PlotDataStorageObj.dict_IntegrationDataSets[i] = {
                **dict(
                    export_name=self.export_name,
                ),
                **{
                    key: value
                    for key, value in self.IntegrateContainer.__dict__.items()
                    if key
                    in [
                        "x_col",
                        "y_col",
                        "y_col_std",
                        "y_col_1stderiv",
                        "y_col_2ndderiv",
                        "y_col_baselineavg",
                        "y_col_endavg",
                        "y2_col_int",
                        "y2_col",
                    ]
                },
                **{
                    key: value
                    for key, value in self.IntegrateContainer.active().__dict__.items()
                    if key
                    in [
                        "area_integrated_simps",
                        "area_integrated_trapz",
                        "id_ana_integration",
                        "idx_baseline",
                        "idx_integrate_begin",
                        "idx_integrate_min",
                        "idx_integrate_end",
                        "idx_integrate_max",
                        "zoom_home_x",
                        "zoom_home_y",
                        "no_of_datapoints_avg",
                        "no_of_datapoints_rolling",
                        "endavg_offset",
                        "idx_baseline_datapoints",
                        "baselineavg",
                        "idx_integrate_end_datapoints",
                        "endavg",
                    ]
                },
                **{
                    key: widgetObj.value
                    for key, widgetObj in self.IntegrateContainer.__dict__.items()
                    if key
                    in [
                        "name_analysis_text",
                        "dropdown_select_exp",
                        "dropdown_ec_reaction",
                        "floattext_faradaic_efficiency",
                    ]
                },
            }

    """
    class PlotData:


        def __init__(self, ax_name, export_name, params, exp, data):
            self.ax_name = ax_name
            self.export_name = export_name
            self.params = params
            self.exp = exp
            self.data = data

    def add_PlotData(self, ax_name, export_name, params, exp, data):
        self.PlotDataObjs.append(self.PlotData(ax_name, export_name, params, exp, data))

    def has_PlotData(self, ax_name, export_name):
        return [ax_name, export_name] in [[entry.ax_name, entry.export_name] for entry in self.PlotDataObjs]
    """
    """
    def has_exp(self, ax_name, export_name):
        return [ax_name, export_name] in [[entry['ax_name'], entry['export_name']] for entry in self.exp]
    def get_exp(self, ax_name, export_name):
        if self.has_exp(self, ax_name, export_name):
            return self.exp
        else:
            raise ValueError('ax_name='+ax_name+', export_name='+export_name+'  not defined in self.exp')
    """


def retrieve_name_caller(var):
    callers_local_vars = inspect.currentframe().f_back.f_back.f_locals.items()
    return [var_name for var_name, var_val in callers_local_vars if var_val is var]
