"""
Scripts for interactive integration and uploading to database
Created in 2023
@author: Forschungszentrum Jülich GmbH, Nico Röttcher
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors
import warnings

from ipywidgets import *
from IPython.display import clear_output
import scipy.integrate

from evaluation.utils import db
from evaluation.visualization import plot
from evaluation.visualization import extra_widgets


class CreateDataset:
    """
    Class to create a dataset, default for EC dataset
    """

    def __init__(
        self,
        objExp_df,
        x_col,
        y_col,
        data=None,
        # con=None, --> write to database requires special user
        ax=None,
        print_info=False,
        axlabel_auto=True,
        timestamp_cols_to_seconds=True,
        export_object=None,
        export_name="plot_unspecified",
        func_new_dataset=None,
        func_deactivate_all=None,
        **plt_kwargs,
    ):
        self.objExp_df = objExp_df
        engine = db.connect(user="hte_processor")  # , echo=True)
        self.name_id_exp = (
            [self.objExp_df.index.name]
            if not type(self.objExp_df.index) == pd.MultiIndex
            else self.objExp_df.index.names
        )
        if "id_exp_sfc" in self.name_id_exp:
            self.name_id_exp = "id_exp_sfc"
            self.name_id_dataset = "id_exp_ec_dataset"
            self.name_id_data_dataset = "id_data_ec_dataset"
            self.name_table_dataset_definer = "exp_ec_datasets_definer"
            self.name_table_dataset = "exp_ec_datasets"

        else:
            raise ValueError(
                "Create dataset not implemented for index "
                + ", ".join(self.name_id_exp)
            )

        self.df_selected = pd.DataFrame()
        self.ids_selected = ""
        self.fig = ax.get_figure()

        self.objExp_df = self.objExp_df.dataset.plot(
            x_col,
            y_col,
            # xerr_col=None,
            # yerr_col=None,
            data=data,
            ax=ax,
            print_info=print_info,
            axlabel_auto=axlabel_auto,
            timestamp_cols_to_seconds=timestamp_cols_to_seconds,
            export_object=export_object,
            export_name=export_name,  # 'plot',
            alpha=0.3,
            **plt_kwargs,
        ).return_dataset()

        self.integration_label = widgets.HTML(
            value=f"<b style='font-size:2em''>{export_name} - Create Dataset</b>"
        )

        # print(objExp._obj)

        self.objExp_df.loc[:, "dropdown_select_exp_label"] = [
            "_".join(
                [str(item) for item in ([index] if type(index) == int else list(index))]
            )
            for index in self.objExp_df.index
        ]
        if "id_exp_sfc" in self.name_id_exp:
            self.objExp_df.loc[:, "dropdown_select_exp_label"] = (
                self.objExp_df.loc[:, "dropdown_select_exp_label"].astype(str)
                + ": "
                + self.objExp_df.loc[:, "id_ML"].astype(str)
                + ", "
                + self.objExp_df.loc[:, "id_ML_technique"].astype(str)
            )

        self.output_create_dataset = widgets.Output(
            layout=Layout(
                width="800px",
                display="flex",  # overflow="scroll"
            )
        )

        self.dropdown_select_id_ML_none = "none"
        if "id_exp_sfc" in self.name_id_exp:
            self.dropdown_select_id_ML = widgets.Select(
                options=[self.dropdown_select_id_ML_none]
                + self.objExp_df.id_ML.unique().tolist(),
                # value='macOS',
                # rows=10,
                description="Select id_ML:",
                disabled=False,
            )

            def on_dropdown_select_id_ML(changed_value):
                if changed_value.new == self.dropdown_select_id_ML_none:
                    self.dropdown_selectmultiple_exp.value = []
                else:
                    self.dropdown_selectmultiple_exp.value = self.objExp_df.loc[
                        self.objExp_df.id_ML == changed_value.new,
                        "dropdown_select_exp_label",
                    ].tolist()

            self.dropdown_select_id_ML.observe(on_dropdown_select_id_ML, names="value")
        self.dropdown_selectmultiple_exp = widgets.SelectMultiple(
            options=self.objExp_df.dropdown_select_exp_label.tolist(),
            # value=['Oranges'],
            # rows=10,
            description="Select experiments (hold Ctrl): ",
            disabled=False,
            layout=Layout(
                height="80px"
            ),  # , display='flex'),# if multiple_exp else 'none'),
            style={"description_width": "initial"},
        )

        def on_dropdown_select_multiple_exp(changed_value):
            # nothing selected
            if len(changed_value.new) == 0:
                self.button_create_dataset.disabled = True
                for index, row in self.objExp_df.iterrows():
                    row.ax_plot_objects[-1][0].set_alpha(0.3)
                    row.ax_plot_objects[-1][0].set_zorder(1)
                self.fig.canvas.draw()
                return ""

            with self.output_create_dataset:
                clear_output()
                df_unselected = self.objExp_df.loc[
                    self.objExp_df.dropdown_select_exp_label.isin(changed_value.old), :
                ].copy()
                self.df_selected = self.objExp_df.loc[
                    self.objExp_df.dropdown_select_exp_label.isin(changed_value.new), :
                ].copy()

                # display(self.df_selected)
                if len(self.df_selected.index) > 1:
                    print("Differences of selected experiments in dataset: ")
                    self.df_selected.loc[
                        :,
                        ~self.df_selected.columns.isin(
                            [
                                "t_start__timestamp",
                                "t_end__timestamp",
                                "id_ML_technique",
                                "ax_plot_objects",
                                "dropdown_select_exp_label",
                            ]
                        ),
                    ].dataset.display(only_different_cols=True)
                self.id_dataset_selected = None
                self.ids_selected = ",".join(
                    [
                        str(item)
                        for item in self.df_selected.reset_index()
                        .loc[:, self.name_id_exp]
                        .tolist()
                    ]
                )

                id_dataset_exists = db.query_sql(
                    """ SELECT * 
                                                        FROM (SELECT `"""
                    + self.name_id_dataset
                    + """`, GROUP_CONCAT(`"""
                    + self.name_id_exp
                    + """`) AS ids_exp
                                                                FROM hte_data.`"""
                    + self.name_table_dataset_definer
                    + """`
                                                                GROUP BY `"""
                    + self.name_id_dataset
                    + """`) a
                                                        WHERE ids_exp = %s;
                                                                        """,
                    params=[self.ids_selected],
                    con=engine,
                    method="sqlalchemy",
                ).fetchall()
                # print(id_dataset_exists)
                if len(id_dataset_exists) == 0:
                    self.button_create_dataset.disabled = False
                elif len(id_dataset_exists) > 0:
                    self.button_create_dataset.disabled = True
                    self.id_dataset_selected = id_dataset_exists[0][0]
                    if len(id_dataset_exists) > 1:
                        warnings.warn("Inconsistency in database. Please inform Admin")
                    print(
                        "\x1b[32m",
                        "Dataset already exists. ",
                        str(self.id_dataset_selected) + ": ",
                        id_dataset_exists[0][1],
                        "\x1b[0m",
                    )

                for index, row in df_unselected.iterrows():
                    row.ax_plot_objects[-1][0].set_alpha(0.3)
                    row.ax_plot_objects[-1][0].set_zorder(10)
                    # print(index)#row.ax_plot_objects[0][-1])

                for index, row in self.df_selected.iterrows():
                    row.ax_plot_objects[-1][0].set_alpha(1)
                    # print(row.ax_plot_objects[-1][-1])

            # avoid printing on_dropdown_select_exp(...)
            # deactivate plotted new datasets
            if func_deactivate_all is not None:
                func_deactivate_all()
                for index, row in self.objExp_df.iterrows():
                    row.ax_plot_objects[-1][0].set_zorder(10)

            self.fig.canvas.draw()

        self.dropdown_selectmultiple_exp.observe(
            on_dropdown_select_multiple_exp, names="value"
        )

        self.button_create_dataset = widgets.Button(
            description="Create dataset",
            button_style="",  # 'success', 'info', 'warning', 'danger' or ''
            # tooltip='Click me',
            icon="check",
            # disabled=link_name_analysis,
            # layout=Layout(display='block'),# if multiple_exp else 'none')
        )

        def on_button_create_dataset(changed_value):

            if self.id_dataset_selected is None:
                with self.output_create_dataset:
                    # display(self.df_selected.name_user.unique())

                    # if not all([item == db.current_user() for item in self.df_selected.name_user.unique()]):
                    if not all(
                        [
                            db.user_is_owner(
                                index_col=self.name_id_exp,
                                index_value=row[self.name_id_exp],
                            )
                            for index, row in self.df_selected.reset_index().iterrows()
                        ]
                    ):
                        print(
                            "\x1b[31m",
                            "You better not change data of user",
                            ", ".join(self.df_selected.name_user.unique()),
                            "\x1b[0m",
                        )
                        raise PermissionError(
                            "You better not change data of user"
                            + ", ".join(self.df_selected.name_user.unique())
                        )

                    db.call_procedure(
                        engine,
                        "Reset_Autoincrement",
                        [self.name_table_dataset, self.name_id_dataset],
                    )
                    self.id_dataset_selected = db.insert_into(
                        engine,
                        self.name_table_dataset,
                    )[0]

                    self.df_selected.loc[
                        :, self.name_id_dataset
                    ] = self.id_dataset_selected
                    df_dataset_definer = (
                        self.df_selected.reset_index()
                        .set_index(self.name_id_dataset)
                        .loc[
                            :,
                            [
                                self.name_id_exp,
                            ],
                        ]
                    )
                    df_dataset_definer.to_sql(
                        self.name_table_dataset_definer, con=engine, if_exists="append"
                    )

                    print(
                        "\x1b[32m",
                        "Successfully inserted",
                        str(self.id_dataset_selected) + ": ",
                        self.ids_selected,
                        "\x1b[0m",
                    )
                    self.dropdown_selectmultiple_exp.value = tuple()
                df_dataset = self.transform_df_exp(df_dataset_definer)
                df_data_dataset = self.transform_df_data(df_dataset_definer, data)
                if func_new_dataset is not None:
                    for index, row in self.objExp_df.iterrows():
                        row.ax_plot_objects[-1][0].set_zorder(1)
                    func_new_dataset(df_dataset, df_data_dataset)

        self.button_create_dataset.on_click(on_button_create_dataset)

        display(self.integration_label)
        if "id_exp_sfc" in self.name_id_exp:
            display(self.dropdown_select_id_ML)
        display(  # widgets.VBox([self.integration_label,
            widgets.HBox(
                [
                    self.dropdown_selectmultiple_exp,
                    widgets.VBox(
                        [self.button_create_dataset, self.output_create_dataset]
                    ),
                ]
            ),
            #             ]),
        )

    def transform_df_data(self, df_dataset_definer, data):
        df_data_dataset = df_dataset_definer.join(
            data.reset_index().set_index(self.name_id_exp), on=self.name_id_exp
        ).reset_index()
        df_data_dataset.loc[:, self.name_id_data_dataset] = df_data_dataset.groupby(
            self.name_id_dataset
        ).cumcount()
        df_data_dataset.set_index(
            [self.name_id_dataset, self.name_id_data_dataset], inplace=True
        )
        return df_data_dataset

    def transform_df_exp(self, df_dataset_definer):
        # display(list(df_dataset_definer.index.unique()))
        df_dataset = pd.DataFrame(
            {}, index=df_dataset_definer.index.unique()
        )  # self.id_dataset_selected])
        df_dataset.index.name = self.name_id_dataset
        if type(df_dataset.index) == pd.MultiIndex:
            print("Might not work ... ?")
            # [df_dataset_definer.loc[index].id_exp_sfc.tolist() for index in
            # list(df_dataset.index)])
            df_dataset.loc[:, "dropdown_select_exp_label"] = [
                ", ".join(list([str(val) for val in index]))
                + ": "
                + ",".join(
                    [
                        str(val)
                        for val in df_dataset_definer.loc[index].id_exp_sfc.tolist()
                    ]
                )
                for index in list(df_dataset.index)
            ]
            # str(df_dataset.loc[:,self.name_id_dataset]) + ': ' + self.ids_selected
        else:
            df_dataset.loc[:, "dropdown_select_exp_label"] = [
                ", ".join(
                    list(
                        [
                            str(val)
                            for val in [
                                index,
                            ]
                        ]
                    )
                )
                + ": "
                + ",".join(
                    [
                        str(val)
                        for val in df_dataset_definer.loc[
                            [
                                index,
                            ],
                            "id_exp_sfc",
                        ].tolist()
                    ]
                )
                for index in df_dataset.index
            ]
        return df_dataset


class IntegrateContainer:
    """
    General Class for an Integration Container, carrying required widgets
    """

    def __init__(
        self,
        objExp_df,
        x_col,
        y_col,
        y2_col=0,
        data=None,
        ax=None,
        print_info=False,
        axlabel_auto=True,
        timestamp_cols_to_seconds=True,
        export_object=None,
        export_name="plot_unspecified",
        export_plotdata=True,
        export_path="",
        objExp_df_export_name="undefined",
        set_baseline=None,  # #'auto', 'manual', 'fixed'
        # set_baseline_type='horizontal',# #'horizontal', 'tilted', 'from_data'
        set_integrationlims=None,  # #'auto', 'manual', 'nolims'
        link_name_analysis=True,
        x_start_shift=0,
        x_end_shift=0,
        # multiple_exp=False,
        **plt_kwargs,
    ):
        """
        Initialize integration container. Container for integration of multiple experiments within one plot.
        :param objExp_df: pandas.DataFrame
            experimental dataset DataFrame
        :param x_col: str
            name of Column for x-data in data
        :param y_col: str
            name of Column for y-data in data
        :param y2_col: str or int
            if str: name of Column for y-baseline-data in data
            if int: value of baseline
        :param data: pandas.DataFrame
            DataFrame carrying the data of the experiments
        :param ax: Matplotlib.Axes
            axes in which the plots will be displayed
        :param print_info: bool
            print debug information
        :param axlabel_auto: bool
            whether to print additional info to debug and get style paramters
        :param timestamp_cols_to_seconds:bool
            íf True and x_col or y_col is of type timestamp a new column with relative seconds from first datapoint will
             be created an used for plot
        :param export_object: PlotDataStorage object or None
            append to PlotDataStorage object. If None new is created
        :param export_name: str, default 'plot_unspecified'
            name of the plot as stored in PlotDataStorage
        :param export_plotdata: bool
            whether to export plot data
        :param export_path: pathlib.Path() or str
            Path where to export figure and data
        :param objExp_df_export_name: str
            name of the experimental dataset
        :param set_baseline: list of possible values:
            'fixed': no user modification possible, y2_col must be set as int or data column of the baseline data
            'auto': baseline based on update_baseline_auto algorithm
            'manual': baseline points set by user manually
        :param set_integrationlims: str or list of ['auto', 'manual', 'nolims'] or None
            'auto': integration limits are automatically set according to peak detection algorithm
            'manual': add sliders to adjust integraion limits manually
            'nolims': integrate the whole experiment
        :param link_name_analysis: bool
            whether to link the name analysis to a previous initialized Integration Container
        :param x_start_shift: int
            for linked name analysis, adjust window size (shift start of windowd) in which integration is possible
        :param x_end_shift: int
            for linked name analysis, adjust window size (shift end of windowd) in which integration is possible
        :param plt_kwargs: keyword arguments of evaluation.visualization.plot
        """
        if set_baseline is None:
            set_baseline = ["auto", "manual"]
        if set_integrationlims is None:
            set_integrationlims = ["auto", "manual"]
        self.print_info = print_info
        self.axlabel_auto = axlabel_auto
        self.timestamp_cols_to_seconds = timestamp_cols_to_seconds
        self.export_object = export_object
        self.export_name = export_name  # 'plot',
        self.plt_kwargs = plt_kwargs
        self.plt_rcParams = plt.rcParams.copy()

        self.ax = ax
        if self.export_object is None:
            self.export_object = plot.current_PlotDataStorage()
        # check if IntegrationContainer instance already exists in PlotDataStorage
        existing_IntegrationContainer = [
            item
            for item in self.export_object.DataSets
            if item.data_type == "IntegrationData"
        ]
        self.linked_integrations = []
        if self.export_object is not None:
            self.export_object.add_DataSet(
                ax_list=[self.ax],
                export_name=self.export_name,
                data_type="IntegrationData",
                IntegrateContainer=self,
            )

        self.df_exp = objExp_df  # objExp._obj
        self.df_exp.export_name = objExp_df_export_name + "_integration"  # objExp._obj
        self.data = data
        if not hasattr(self, "df_integrate_names_analysis"):
            self.df_integrate_names_analysis = pd.DataFrame(
                {}, columns=["name_analysis_init"]
            )

        self.set_baseline = (
            set_baseline if type(set_baseline) == list else [set_baseline]
        )  # ['auto', 'manual'] if set_baseline=='both' else [set_baseline]
        self.set_integrationlims = (
            set_integrationlims
            if type(set_integrationlims) == list
            else [set_integrationlims]
        )  # ['auto', 'manual'] if set_baseline=='both' else [set_baseline]
        self.export_plotdata = export_plotdata
        self.export_path = export_path
        self.export_object.name_init = self.export_object.name

        self.x_col = x_col
        self.y_col = y_col
        self.y_col_std = plot.colname_add_subscript(
            y_col, subscript="std"
        )  # y_col.split('__')[0]+'_std__'+'__'.join(y_col.split('__')[1:])
        self.y_col_1stderiv = plot.colname_add_subscript(y_col, subscript="1stderiv")
        self.y_col_2ndderiv = plot.colname_add_subscript(y_col, subscript="2ndderiv")
        self.y_col_baselineavg = plot.colname_add_subscript(
            y_col, subscript="baslineavg"
        )
        self.y_col_endavg = plot.colname_add_subscript(y_col, subscript="endavg")
        self.y2_col_int = None
        if type(y2_col) == str:
            warnings.warn("Defining a data column as baseline is not yet implemented.")
            self.y2_col = y2_col
        elif type(y2_col) == int:
            self.y2_col_int = y2_col
            self.y2_col = plot.colname_add_subscript(y_col, subscript="baseline")
            if len(self.data.index) > 0:
                self.data.loc[:, self.y2_col] = self.y2_col_int
        else:
            raise ValueError("y2_col must be either str or int and not " + type(y2_col))

        self.fig = ax.get_figure()  # plt.gcf()

        if "auto" in self.set_baseline:
            ax_first_twin = plot.first_twin(ax)
            if ax_first_twin is not None:
                # print(ax_first_twin.get_ylabel())
                self.axr = ax_first_twin.twinx()  # for std, 1stderiv, .. plots
                self.axr.spines.right.set_position(("axes", 1.2))
                self.axr.ticklabel_format(useMathText=True)
                self.axr.get_yaxis().get_offset_text().set_position((1.32, 0))
            else:
                self.axr = ax.twinx()

        self.df_result = pd.DataFrame()

        self.link_name_analysis = link_name_analysis
        if self.link_name_analysis:
            if len(existing_IntegrationContainer) > 0:
                if len(existing_IntegrationContainer) > 1:
                    print(
                        "\x1b[33m",
                        "Multiple IntegrationContainer initialized. Will link name_analysis to first one",
                        "\x1b[0m",
                    )
                    # warnings.warn('')
            else:
                self.link_name_analysis = False
                # warnings.warn('')
        self.x_start_shift = x_start_shift
        self.x_end_shift = x_end_shift

        self.name_analysis_dropdown_choose = "Choose..."
        self.name_analysis_dropdown_new = "New Entry"
        self.name_analysis_dropdown = widgets.Dropdown(
            options=[
                self.name_analysis_dropdown_choose,
                self.name_analysis_dropdown_new,
            ]
            + self.df_integrate_names_analysis.name_analysis_init.dropna()
            .unique()
            .tolist(),
            # + [self.name_analysis_dropdown_new],
            # value='2',
            description="  Choose name analysis:",
            style={"description_width": "initial"},
            disabled=self.link_name_analysis,
            # layout=Layout(display='flex' if not link_name_analysis else 'none'),
        )

        self.init_new_entry_name_analysis_dropdown = False

        def on_name_analysis_dropdown(changed_value):
            # with upload_output:
            #    clear_output()
            # print(changed_value.new)
            if self.init_new_entry_name_analysis_dropdown:
                self.init_new_entry_name_analysis_dropdown = False
                return True

            for integration in self.linked_integrations:
                integration["upload_button"].button_style = ""
                integration["name_analysis_dropdown"].value = changed_value.new

            self.upload_button.button_style = ""
            # self.upload_button.disabled = True
            if changed_value.new == self.name_analysis_dropdown_choose:
                self.name_analysis_text.disabled = True
                self.toggle_disabled_widgets(disabled=True)
                return None
            elif changed_value.new == self.name_analysis_dropdown_new:

                self.name_analysis_text.value = ""
                self.name_analysis_text.disabled = self.link_name_analysis  # False
                # df_integrate = init_new_name_analysis(df_integrate)
                # analysis_integration.read_data(changed_value.new)
                # analysis_integration.write_widgets()
                # print('new entry', changed_value.new)
                self.activate_analysis()
            else:
                self.name_analysis_text.disabled = self.link_name_analysis  # False
                self.name_analysis_text.value = changed_value.new

                self.activate_analysis()

        self.name_analysis_dropdown.observe(on_name_analysis_dropdown, names="value")

        self.name_analysis_text = widgets.Text(
            # value=df_integrate.name_analysis.iloc[0],
            placeholder="Enter a name for this integration analysis",
            description="  Analysis name:",
            style={"description_width": "initial"},
            disabled=True,  # link_name_analysis,
        )

        self.upload_button_insert = "Insert new entry to database"
        self.upload_button_update = "Updating entry in database"
        self.upload_button = widgets.Button(
            description=self.upload_button_update,
            button_style="",  # 'success', 'info', 'warning', 'danger' or ''
            tooltip="Click me",
            icon="check",
            disabled=True,  # self.link_name_analysis,
            layout=Layout(
                width="250px",
            ),
        )

        def on_upload_button_clicked(changed_value):
            self.upload_button.disabled = True
            self.upload_button.description = "Processing..."
            self.click_upload_button()
            self.upload_button.disabled = False

        self.upload_button.on_click(on_upload_button_clicked)

        if self.link_name_analysis:
            self.name_analysis_dropdown.value = existing_IntegrationContainer[
                0
            ].IntegrateContainer.name_analysis_dropdown.value
            # widgets.jslink((existing_IntegrationContainer[0].IntegrateContainer.name_analysis_dropdown, 'value'),
            #               (self.name_analysis_dropdown, 'value')) # dropdown value cannot be synced --> sync it via on_name_analysis_dropdown of parent
            widgets.jslink(
                (
                    existing_IntegrationContainer[
                        0
                    ].IntegrateContainer.name_analysis_text,
                    "value",
                ),
                (self.name_analysis_text, "value"),
            )

            self.upload_button.description = "Update via linked"
            # existing_IntegrationContainer[0].IntegrateContainer
            self.parent_integrate_container = existing_IntegrationContainer[
                0
            ].IntegrateContainer
            self.parent_integrate_container.linked_integrations.append(
                {
                    "upload_button": self.upload_button,
                    "name_analysis_dropdown": self.name_analysis_dropdown,
                    "database_constraints": self.database_constraints,
                    "self": self,
                }
            )

        self.integration_label = widgets.HTML(
            value=f"<b style='font-size:2em''>{export_name}</b>"
        )
        objSelf = self
        # self.objExp = objExp
        if "dropdown_select_exp_label" not in self.df_exp.columns:
            self.df_exp.loc[:, "dropdown_select_exp_label"] = [
                "_".join(
                    [
                        str(item)
                        for item in ([index] if type(index) == int else list(index))
                    ]
                )
                for index in self.df_exp.index
            ]

        self.dropdown_entry_all = "all"
        self.dropdown_entry_none = "none"
        self.dropdown_select_exp = widgets.Dropdown(
            options=[self.dropdown_entry_all, self.dropdown_entry_none]
            + self.df_exp.dropdown_select_exp_label.tolist(),
            value=self.dropdown_entry_all,  # self.df_exp.dropdown_select_exp_label.iloc[0],
            disabled=False,  # len(self.df_exp.index) == 1,
            description="Select experiment: ",
            style={"description_width": "initial"},
        )

        def on_dropdown_select_exp(changed_value):
            print("on_dropdown_select_exp", changed_value)
            # hide previous selected
            self.toggle_disabled_widgets(disabled=True)
            if changed_value.old == self.dropdown_entry_all:
                # self.toggle_disabled_widgets(disabled=False)
                [row.objIntegrate.deactivate() for index, row in self.df_exp.iterrows()]
            elif changed_value.old == self.dropdown_entry_none:
                # self.toggle_disabled_widgets(disabled=False)
                print("dropdown_select_exp was none")
            else:
                self.df_exp.loc[
                    self.df_exp.dropdown_select_exp_label == changed_value.old
                ].iloc[0].objIntegrate.deactivate()
            # show selected
            if changed_value.new == self.dropdown_entry_all:
                # self.toggle_disabled_widgets(disabled=True)
                [
                    row.objIntegrate.activate(overview=True)
                    for index, row in self.df_exp.iterrows()
                ]
                for integration in self.linked_integrations:
                    integration["self"].dropdown_select_exp.value = integration[
                        "self"
                    ].dropdown_entry_all
            elif changed_value.new == self.dropdown_entry_none:
                # self.toggle_disabled_widgets(disabled=True)
                [row.objIntegrate.deactivate() for index, row in self.df_exp.iterrows()]
            else:
                self.activate_analysis()
                # self.df_exp.loc[self.df_exp.dropdown_select_exp_label == changed_value.new].iloc[
                #    0].objIntegrate.activate()

            self.fig.canvas.draw()

        self.dropdown_select_exp.observe(on_dropdown_select_exp, names="value")

        self.intText_no_of_datapoints_rolling = widgets.IntText(
            # value=int(self.no_of_datapoints_rolling),
            description="Adjust number of datapoints used to smooth signal:",
            continuous_update=False,
            disabled=True,
            layout=Layout(
                width="500px", display="flex" if "auto" in self.set_baseline else "none"
            ),
            style={"description_width": "initial"},
        )

        def update_on_intText_no_of_datapoints_rolling(changed_value):
            if (
                objSelf.active().initialized
            ):  # avoid update when integration object is activated
                print("update_on_intText_no_of_datapoints_rolling", changed_value)
                objSelf.active().set_no_of_datapoints_rolling(
                    changed_value.new, objSelf.active().widget_fires_update
                )
                self.fig.canvas.draw()

        self.intText_no_of_datapoints_rolling.observe(
            update_on_intText_no_of_datapoints_rolling, "value"
        )

        self.intText_no_of_datapoints_avg = widgets.IntText(
            # value=int(analysis_integration.no_of_datapoints_avg),
            description="Adjust number of datapoints used to average baseline and end:",
            continuous_update=False,
            disabled=True,
            layout=Layout(
                width="500px",
                display="flex"
                if ("auto" in self.set_baseline or "manual" in self.set_baseline)
                else "none",
            ),
            style={"description_width": "initial"},
        )

        def update_on_intText_no_of_datapoints_avg(changed_value):
            if objSelf.active().initialized:
                print("update_on_intText_no_of_datapoints_avg", changed_value)
                objSelf.active().set_no_of_datapoints_avg(
                    changed_value.new, objSelf.active().widget_fires_update
                )
                self.fig.canvas.draw()

        self.intText_no_of_datapoints_avg.observe(
            update_on_intText_no_of_datapoints_avg, "value"
        )

        self.intSlider_baseline = widgets.IntSlider(
            step=1,
            description="Position baseline:",
            disabled=True,
            continuous_update=False,
            orientation="horizontal",
            readout=True,
            readout_format="d",
            layout=Layout(
                width="500px",
                display="flex" if "manual" in self.set_baseline else "none",
            ),
            style={"description_width": "initial"},
        )
        self.intText_baseline = widgets.IntText(
            disabled=True,
            layout=Layout(display="flex" if "manual" in self.set_baseline else "none"),
        )
        linked_baseline = widgets.jslink(
            (self.intSlider_baseline, "value"), (self.intText_baseline, "value")
        )

        def update_on_intSlider_baseline(changed_value):
            if objSelf.active().initialized:
                print(
                    "update_on_intSlider_baseline",
                    objSelf.active().idx_baseline,
                    changed_value,
                )
                objSelf.active().set_idx_baseline(
                    changed_value.new, objSelf.active().widget_fires_update
                )
                self.fig.canvas.draw()

        self.intSlider_baseline.observe(update_on_intSlider_baseline, "value")

        self.intSlider_integrate_begin = widgets.IntSlider(
            step=1,
            description="Begin integration:",
            disabled=True,
            continuous_update=False,
            orientation="horizontal",
            readout=True,
            readout_format="d",
            layout=Layout(
                width="500px",
                display="flex" if "manual" in self.set_integrationlims else "none",
            ),
            style={"description_width": "initial"},
        )
        self.intText_integrate_begin = widgets.IntText(
            disabled=True,
            layout=Layout(
                display="flex" if "manual" in self.set_integrationlims else "none"
            ),
        )
        linked_integrate_begin = widgets.jslink(
            (self.intSlider_integrate_begin, "value"),
            (self.intText_integrate_begin, "value"),
        )

        def update_on_intSlider_integrate_begin(changed_value):
            if objSelf.active().initialized:
                print(
                    "update_on_intSlider_begin",
                    objSelf.active().idx_integrate_begin,
                    changed_value,
                )
                objSelf.active().set_idx_integrate_begin(
                    changed_value.new, objSelf.active().widget_fires_update
                )
                # objSelf.active().initialized = False
                # objSelf.intSlider_integrate_end.min = changed_value.new
                # objSelf.active().initialized = True
                self.fig.canvas.draw()

        self.intSlider_integrate_begin.observe(
            update_on_intSlider_integrate_begin, "value"
        )

        self.intSlider_integrate_end = widgets.IntSlider(
            step=1,
            description="End integration:",
            disabled=True,
            continuous_update=False,
            orientation="horizontal",
            readout=True,
            readout_format="d",
            layout=Layout(
                width="500px",
                display="flex" if "manual" in self.set_integrationlims else "none",
            ),
            style={"description_width": "initial"},
        )
        self.intText_integrate_end = widgets.IntText(
            disabled=True,
            layout=Layout(
                display="flex" if "manual" in self.set_integrationlims else "none"
            ),
        )
        linked_integrate_end = widgets.jslink(
            (self.intSlider_integrate_end, "value"),
            (self.intText_integrate_end, "value"),
        )

        def update_on_intSlider_integrate_end(changed_value):
            if objSelf.active().initialized:
                print(
                    "update_on_intSlider_end",
                    objSelf.active().idx_integrate_end,
                    changed_value,
                )
                objSelf.active().set_idx_integrate_end(
                    changed_value.new, objSelf.active().widget_fires_update
                )
                # objSelf.active().idx_integrate_end = changed_value.new
                # objSelf.active().update_integration_data()
                # objSelf.active().update_integration_plot()
                self.fig.canvas.draw()

        self.intSlider_integrate_end.observe(update_on_intSlider_integrate_end, "value")

        self.output_integration = widgets.Output()
        self.output_integration_activate = widgets.Output()
        self.output_debug = widgets.Output()

        self.toggle_disabled_widgets_list = [
            self.intText_no_of_datapoints_rolling,
            self.intText_no_of_datapoints_avg,
            self.intSlider_baseline,
            self.intText_baseline,
            self.intSlider_integrate_begin,
            self.intText_integrate_begin,
            self.intSlider_integrate_end,
            self.intText_integrate_end,
        ]

        self.df_exp.loc[:, "objIntegrate"] = [
            Integrate(
                self,
                self.df_exp.loc[self.df_exp.index.isin([index]), :],
                # .reset_index(),#.iloc[0], #exp_row
                self.data.loc[
                    (index + (slice(None),))
                    if type(index) == tuple
                    else (index, slice(None)),
                    :,
                ].sort_index(),
                # self.data.loc[(*index,slice(None)), :].sort_index(),#.copy(), #data
            )
            for row_number, (index, row) in enumerate(self.df_exp.iterrows())
        ]

        # first analysis found in database set as starting point
        """
        init_integration = self.df_integrate_names_analysis.loc[
            ~self.df_integrate_names_analysis.name_analysis_init.isna()]
        display(init_integration)
        display(self.df_exp.loc[init_integration.index])
        if len(init_integration.index) == 1:
            self.dropdown_select_exp.value = 
        """

    def active(self):
        active_integrations = self.df_exp.objIntegrate[
            [objInt.active for objInt in self.df_exp.objIntegrate.tolist()]
        ]
        if len(active_integrations) == 1:
            return active_integrations.iloc[0]
        else:
            raise ValueError("Multiple integration objs are active")

    def activate_analysis_constraints(self):
        return True

    def activate_analysis(self):
        if (
            self.dropdown_select_exp.value
            not in [self.dropdown_entry_all, self.dropdown_entry_none]
            and self.name_analysis_dropdown.value != self.name_analysis_dropdown_choose
            and self.activate_analysis_constraints()
        ):
            self.df_exp.loc[
                self.df_exp.dropdown_select_exp_label == self.dropdown_select_exp.value
            ].iloc[0].objIntegrate.activate()
            [
                integration["self"].activate_analysis()
                for integration in self.linked_integrations
            ]
            self.toggle_disabled_widgets(disabled=False)
            if self.active().id_ana_integration is None:
                self.upload_button.description = self.upload_button_insert
                self.upload_button.button_style = "success"
                # self.upload_button.disabled = self.link_name_analysis
            else:
                self.upload_button.description = self.upload_button_update
                self.upload_button.button_style = "primary"
                # self.upload_button.disabled = self.link_name_analysis
            # display('hello test', self.active().id_ana_integration)

    def toggle_disabled_widgets(self, disabled):
        # self.intText_no_of_datapoints_rolling.layout.display = 'None' if disabled else 'flex'
        # self.intText_no_of_datapoints_rolling.disabled = disabled
        # self.intText_no_of_datapoints_rolling.layout.visibility = 'hidden' if disabled else 'visible'
        for widget_toggle in self.toggle_disabled_widgets_list:
            widget_toggle.disabled = disabled
        self.upload_button.disabled = self.link_name_analysis | disabled

    def database_constraints(self):
        if self.name_analysis_text.value == "":
            print("\x1b[31m", "You need to provide an analysis name", "\x1b[0m")
            return False

        if " " in self.name_analysis_text.value:
            self.name_analysis_text.value = self.name_analysis_text.value.replace(
                " ", "_"
            )
            print(
                "\x1b[33m",
                'spaces in analysis name is not allowed. They are substituted automatically with "_", please check und try uploading again.',
                "\x1b[0m",
            )
            return False

        if (
            self.name_analysis_text.value in self.name_analysis_dropdown.options
            and self.name_analysis_dropdown.value == self.name_analysis_dropdown_new
        ):
            print(
                "\x1b[31m",
                "Analysis name already exists. Please provide a unique name or choose name in dropdown menu to update analysis",
                "\x1b[0m",
            )
            return False
        if self.dropdown_select_exp.value == self.dropdown_entry_all:
            print("\x1b[31m", "You need to select one of the experiments", "\x1b[0m")
            return False

        return True

    def click_upload_button(self):
        def update(con):
            with self.output_integration:
                # clear_output()
                if not (
                    self.database_constraints()
                    and all(
                        [
                            integration_linked["database_constraints"]()
                            for integration_linked in self.linked_integrations
                        ]
                    )
                ):
                    return False
                # with self.con.begin():#self.connection = self.con.c
                # with self.con.connect() as self.connection:
                # if not objSelf.active().to_database(con):
                #    print("\x1b[31m", 'Update not successful', "\x1b[0m")
                #    return False
                self.active().to_database(con)

                # print("\x1b[32m", 'Successfully updated', self.name_analysis_text.value, "\x1b[0m")

                # name_analysis_dropdown.options = df_integrate.name_analysis.tolist() + ['new entry']
                # deactivate_analysis()
                # for integration in self.linked_integrations:
                #    integration['upload_button'].click()
                return True

        with self.output_integration:
            if hasattr(self, "parent_integrate_container"):
                # print('has parent: ', self.parent.name)
                returned = update(self.parent_integrate_container.connection)
                # print('child:', returned)
                return returned  # update linked name analysis with connection of parent (rollback all in case of error)

            # else:
            # print('has no parent')
            if not hasattr(self, "con"):  # should be already initialized by subclass
                self.con = db.connect("hte_processor")

            with self.con.begin() as self.connection:
                returned = update(self.connection)
                # print('parent:', returned)
                if not returned:
                    raise Exception("Error during database upload")

                for integration in self.linked_integrations:
                    # exception raising in children method is not sufficient this would return None and proceed
                    # but process of parent need to be stopped and rollbacked!
                    returned = integration["self"].click_upload_button()
                    # ('parent called child:', returned)
                    if not returned:
                        # return False
                        raise Exception(
                            "Error during database upload of linked analysis"
                        )

                if (
                    self.name_analysis_dropdown.value == self.name_analysis_dropdown_new
                ):  # add new entry to dropdown
                    self.name_analysis_dropdown.options += (
                        self.name_analysis_text.value,
                    )
                    for linked_integration in self.linked_integrations:
                        linked_integration["name_analysis_dropdown"].options += (
                            self.name_analysis_text.value,
                        )
                self.init_new_entry_name_analysis_dropdown = True
                self.name_analysis_dropdown.value = (
                    self.name_analysis_text.value
                )  # name_analysis_dropdown_choose
                # deactivate_analysis()
                print("\x1b[32m", "Successfully saved all data in database", "\x1b[0m")

            if self.export_plotdata:
                self.export_object.name = (
                    self.export_object.name_init
                    + "_"
                    + str(self.dropdown_select_exp.value).split(":")[0]
                    + "_"
                    + str(self.name_analysis_dropdown.value)
                    + "_"
                    + "_".join(
                        [
                            str(linked_integration["self"].dropdown_select_exp.value)
                            for linked_integration in self.linked_integrations
                        ]
                    )
                )
                self.export_object.export(
                    fig=self.fig,
                    export_data=True,
                    auto_overwrite=True,
                    path=self.export_path,
                )
            return True


class IntegrateContainerICPMS(IntegrateContainer):
    """
    extension of IntegrateContainer Class for ICPMS experiment integration
    """

    def __init__(self, objExp_df, **kwargs):
        self.to_database_table = "exp_icpms_integration"
        self.to_database_name_id_data = "id_data_icpms"
        self.to_database_name_timestamp = "t_delaycorrected__timestamp_sfc_pc"
        self.con = db.connect(user="hte_processor")

        idxs = [tuple(str(val) for val in index) for index, row in objExp_df.iterrows()]
        if len(idxs) > 0:
            self.df_integrate_names_analysis = db.query_sql(
                """SELECT id_exp_icpms, name_isotope_analyte, name_isotope_internalstandard,
                         name_analysis AS 'name_analysis_init',  
                         id_exp_ec_dataset,
                         integ.*
                    FROM exp_icpms_integration
                    LEFT JOIN hte_data.ana_integrations integ USING(id_ana_integration)
                    WHERE (id_exp_icpms, name_isotope_analyte, name_isotope_internalstandard) IN ("""
                + str(idxs).strip("[]")
                + """);""",
                con=self.con,
                method="pandas",
                index_col=[
                    "id_exp_icpms",
                    "name_isotope_analyte",
                    "name_isotope_internalstandard",
                ],
            )
            self.df_integrate_names_analysis = self.df_integrate_names_analysis.join(
                objExp_df, how="outer"
            )
            # display(self.df_integrate_names_analysis)

        super().__init__(objExp_df, **kwargs)
        display(
            widgets.VBox(
                [
                    self.integration_label,
                    widgets.HBox(
                        [
                            self.name_analysis_dropdown,
                            self.name_analysis_text,
                            self.upload_button,
                        ]
                    ),
                    self.dropdown_select_exp,
                    self.intText_no_of_datapoints_rolling,
                    self.intText_no_of_datapoints_avg,
                    widgets.HBox([self.intSlider_baseline, self.intText_baseline]),
                    widgets.HBox(
                        [self.intSlider_integrate_begin, self.intText_integrate_begin]
                    ),
                    widgets.HBox(
                        [self.intSlider_integrate_end, self.intText_integrate_end]
                    ),
                    self.output_integration_activate,
                    self.output_integration,
                    self.output_debug,
                ]
            )
        )

    def activate_analysis_constraints(self):
        id_exp_ec_dataset_selected = self.parent_integrate_container.df_exp.loc[
            self.parent_integrate_container.df_exp.dropdown_select_exp_label
            == self.parent_integrate_container.dropdown_select_exp.value
        ].index
        if len(id_exp_ec_dataset_selected) == 0:
            with self.output_integration:
                print("\x1b[31m", "Select corresponding ec experiment first", "\x1b[0m")
            return False

        return True

    def get_id_ana_integration(self):
        id_exp_ec_dataset_selected = self.parent_integrate_container.df_exp.loc[
            self.parent_integrate_container.df_exp.dropdown_select_exp_label
            == self.parent_integrate_container.dropdown_select_exp.value
        ].index
        id_ana_integration_return = None
        if len(id_exp_ec_dataset_selected) > 0:
            # print(id_exp_ec_dataset_selected)
            # print(self.df_exp.loc[self.df_exp.dropdown_select_exp_label == self.dropdown_select_exp.value].index)
            # print(self.name_analysis_dropdown)
            id_ana_integration_selected = self.df_integrate_names_analysis.loc[
                (
                    self.df_integrate_names_analysis.index.isin(
                        self.df_exp.loc[
                            self.df_exp.dropdown_select_exp_label
                            == self.dropdown_select_exp.value
                        ].index
                    )
                    & (
                        self.df_integrate_names_analysis.id_exp_ec_dataset
                        == id_exp_ec_dataset_selected[0]
                    )
                    & (
                        self.df_integrate_names_analysis.name_analysis_init
                        == self.name_analysis_dropdown.value
                    )
                ),
                "id_ana_integration",
            ]
            # display(id_ana_integration_selected)
            if len(id_ana_integration_selected.index) == 0:
                id_ana_integration_return = None
            elif len(id_ana_integration_selected.index) == 1:
                id_ana_integration_return = id_ana_integration_selected.iloc[0]
            else:
                display(id_exp_ec_dataset_selected)
                raise ValueError(
                    "Multiple integration analyses found. Please inform Admin!"
                )
        return id_ana_integration_return

    def database_constraint_username(self, index):
        users_db = db.query_sql(
            """ SELECT name_user FROM exp_icpms
                                         WHERE id_exp_icpms = %s;
                                    """,
            params=[str(index[0])],
            method="sqlalchemy",
            con=self.con,
        ).fetchall()[0]

        # if not all([item == db.current_user() for item in users_db]):
        if not db.user_is_owner("id_exp_icpms", index_value=int(index[0])):
            print(
                "\x1b[31m",
                "You better not change data of user",
                ", ".join(users_db),
                "\x1b[0m",
            )
            raise PermissionError(
                "You better not change data of user " + ", ".join(users_db)
            )

        return True


class IntegrateContainerEC(IntegrateContainer):
    """
    extension of IntegrateContainer Class for EC experiment integration
    """

    def __init__(
        self,
        objExp_df,
        x_col,  # =0,
        y_col,  # =0,
        data,
        ax=None,
        print_info=False,
        axlabel_auto=True,
        timestamp_cols_to_seconds=True,
        export_object=None,
        export_name="plot_unspecified",
        **kwargs,
    ):
        self.to_database_table = "exp_ec_integration"
        # self.to_database_name_id_data = 'id_data_ec'
        self.to_database_name_timestamp = "Timestamp"
        self.con = db.connect(user="hte_processor")
        # display(objExp_df.reset_index().id_exp_sfc.tolist())
        vals = [
            str(int(index)) for index in objExp_df.reset_index().id_exp_sfc.tolist()
        ] * 2
        vals_placeholder = ("%s, " * len(objExp_df.index))[:-2]
        df_dataset_definer = db.query_sql(
            """SELECT id_exp_ec_dataset, id_exp_sfc
                                            FROM hte_data.exp_ec_datasets_definer
                                            WHERE id_exp_ec_dataset IN (SELECT id_exp_ec_dataset 
                                                                        FROM hte_data.exp_ec_datasets_definer
                                                                        WHERE id_exp_sfc IN ("""
            + vals_placeholder
            + """))
                                                AND id_exp_ec_dataset NOT IN (SELECT id_exp_ec_dataset 
                                                                              FROM hte_data.exp_ec_datasets_definer
                                                                              WHERE id_exp_sfc NOT IN ("""
            + vals_placeholder
            + """))  
                                          ;""",
            params=vals,
            con=self.con,
            method="pandas",
            index_col="id_exp_ec_dataset",
        )

        # display(str(df_dataset_definer.index.tolist()).strip('[]'))
        idxs = (
            df_dataset_definer.index.tolist()
        )  # tuple(df_dataset_definer.index.tolist())
        idxs = (
            idxs if len(idxs) > 0 else [-1]
        )  # if len(idxs) > 0: # self.df_integrate_names_analysis need to be initialized also if no ec dataset exist
        self.df_integrate_names_analysis = db.query_sql(
            """SELECT id_exp_ec_dataset, 
                    name_analysis AS 'name_analysis_init', 
                    name_reaction,
                    faradaic_efficiency__percent,
                    integ.*
                FROM exp_ec_integration ec 
                LEFT JOIN hte_data.ana_integrations integ USING(id_ana_integration)
                WHERE id_exp_ec_dataset IN ("""
            + str(idxs).strip("[]")
            + """);""",
            con=self.con,
            method="pandas",
            index_col="id_exp_ec_dataset",
        )  # , 'name_analysis_init_index'
        # self.df_integrate_names_analysis = self.df_integrate_names_analysis.join(df_dataset_definer, how='outer')
        for index in df_dataset_definer.index:
            if index not in self.df_integrate_names_analysis.index:
                self.df_integrate_names_analysis.loc[index] = pd.Series(dtype=object)
        self.df_integrate_names_analysis.id_ana_integration.replace(
            np.nan, None, inplace=True
        )

        # display(self.df_integrate_names_analysis)
        # objExp._obj_copy = objExp._obj.copy()

        self.create_dataset = CreateDataset(
            objExp_df,
            x_col,  # =0,
            y_col,  # =0,
            data=data,
            ax=ax,
            print_info=print_info,
            axlabel_auto=axlabel_auto,
            timestamp_cols_to_seconds=timestamp_cols_to_seconds,
            export_object=export_object,
            export_name=export_name,
            func_new_dataset=self.add_exp,
            func_deactivate_all=self.deactivate_all,
        )

        # self.df_exp = pd.DataFrame()
        # self.data = pd.DataFrame()
        # else:
        #    self.df_exp = objExp._obj
        #    self.data = data
        df_datasets = self.create_dataset.transform_df_exp(df_dataset_definer)
        # display(df_datasets.index)
        df_data_dataset = self.create_dataset.transform_df_data(
            df_dataset_definer, data
        )
        self.to_database_name_id_data = self.create_dataset.name_id_data_dataset
        # display(df_names.join(df_datasets, how='outer'))
        super().__init__(
            df_datasets,  # objExp_df
            x_col,
            y_col,
            ax=ax,
            print_info=print_info,
            axlabel_auto=axlabel_auto,
            timestamp_cols_to_seconds=timestamp_cols_to_seconds,
            export_object=export_object,
            export_name=export_name,
            data=df_data_dataset,
            **kwargs,
        )

        self.read_ec_reactions()
        self.dropdown_ec_reaction = widgets.Dropdown(
            options=self.df_ec_reactions.dropdown_label.tolist(),
            # value=self.dropdown_entry_all,  # self.df_exp.dropdown_select_exp_label.iloc[0],
            disabled=True,  # len(self.df_exp.index) == 1,
            description="Select electrochemical reaction: ",
            style={"description_width": "initial"},
        )

        def on_dropdown_ec_reaction(changed_value):
            self.read_ec_reactions()
            self.dropdown_ec_reaction.options = (
                self.df_ec_reactions.dropdown_label.tolist()
            )
            self.dropdown_ec_reaction.value = changed_value.new
            # hide previous selected

        self.dropdown_ec_reaction.observe(on_dropdown_ec_reaction, names="value")

        self.floattext_faradaic_efficiency = widgets.BoundedFloatText(
            value=100,
            min=0,
            max=100,
            step=1,
            description="Faradaic effciency:",
            disabled=True,
            style={"description_width": "initial"},
        )

        display(
            widgets.VBox(
                [
                    self.integration_label,
                    widgets.HBox(
                        [
                            self.name_analysis_dropdown,
                            self.name_analysis_text,
                            self.upload_button,
                        ]
                    ),
                    self.dropdown_select_exp,
                    self.intText_no_of_datapoints_rolling,
                    self.intText_no_of_datapoints_avg,
                    widgets.HBox([self.intSlider_baseline, self.intText_baseline]),
                    widgets.HBox(
                        [self.intSlider_integrate_begin, self.intText_integrate_begin]
                    ),
                    widgets.HBox(
                        [self.intSlider_integrate_end, self.intText_integrate_end]
                    ),
                    widgets.HBox(
                        [self.dropdown_ec_reaction, self.floattext_faradaic_efficiency]
                    ),
                    # self.autoscale_E_WE,
                    self.output_integration_activate,
                    self.output_integration,
                    self.output_debug,
                ]
            )
        )
        self.toggle_disabled_widgets_list = [
            self.intText_no_of_datapoints_rolling,
            self.intText_no_of_datapoints_avg,
            self.intSlider_baseline,
            self.intText_baseline,
            self.intSlider_integrate_begin,
            self.intText_integrate_begin,
            self.intSlider_integrate_end,
            self.intText_integrate_end,
            self.dropdown_ec_reaction,
            # self.floattext_faradaic_efficiency # always disabled
        ]

    def deactivate_all(self):
        self.dropdown_select_exp.value = self.dropdown_entry_none

    def add_exp(self, exp, data):
        # print(exp, data)
        export_name = self.df_exp.export_name

        self.df_exp = pd.concat([self.df_exp, exp])
        self.data = pd.concat([self.data, data])
        self.df_exp.export_name = export_name
        # add baseline column
        if self.y2_col_int is not None:
            self.data.loc[:, self.y2_col] = self.y2_col_int

        # display(self.df_exp.loc[self.df_exp.objIntegrate.isna()])
        for index, row in self.df_exp.loc[self.df_exp.objIntegrate.isna()].iterrows():
            print(index)
            self.df_integrate_names_analysis.loc[index] = pd.Series(dtype=object)
        # display(self.df_integrate_names_analysis)

        self.df_exp.loc[self.df_exp.objIntegrate.isna(), "objIntegrate"] = [
            Integrate(
                self,
                self.df_exp.loc[self.df_exp.index.isin([index]), :],
                # .reset_index(),#.iloc[0], #exp_row
                self.data.loc[
                    (index + (slice(None),))
                    if type(index) == tuple
                    else (index, slice(None)),
                    :,
                ].sort_index(),  # .copy(), #data
            )
            for row_number, (index, row) in enumerate(
                self.df_exp.loc[self.df_exp.objIntegrate.isna()].iterrows()
            )
        ]

        # self.df_exp.loc[:, 'dropdown_select_exp_label'] =  # initiated by CreateDataset
        display(self.dropdown_select_exp.options)
        self.dropdown_select_exp.options += tuple(exp.dropdown_select_exp_label)

        display(self.dropdown_select_exp.options)

    def database_constraint_username(self, index):
        users_db = db.query_sql(
            """SELECT exp_ec_datasets_definer.id_exp_sfc, name_user 
                                   FROM exp_ec_datasets_definer
                                   LEFT JOIN (SELECT id_exp_sfc, name_user FROM exp_sfc) a USING (id_exp_sfc)
                                   WHERE id_exp_ec_dataset = %s
                                   GROUP BY exp_ec_datasets_definer.id_exp_sfc, name_user;
                                 """,
            params=[str(index[0])],
            method="pandas",
            con=self.con,
        )

        # display(users_db)
        # if not all([item == db.current_user() for item in users_db]):
        for index, row in users_db.iterrows():
            if not db.user_is_owner("id_exp_sfc", index_value=int(row.id_exp_sfc)):
                print(
                    "\x1b[31m",
                    "You better not change data of user ",
                    ", ".join(row.name_user),
                    "\x1b[0m",
                )
                raise PermissionError(
                    "You better not change data of user " + ", ".join(row.name_user)
                )
        return True

    def get_id_ana_integration(self):
        # print(self.df_exp.loc[self.df_exp.dropdown_select_exp_label == self.dropdown_select_exp.value].index)
        # display(self.df_integrate_names_analysis.index)
        analysis_selected = self.df_integrate_names_analysis.loc[
            (
                self.df_integrate_names_analysis.index.isin(
                    self.df_exp.loc[
                        self.df_exp.dropdown_select_exp_label
                        == self.dropdown_select_exp.value
                    ].index
                )
                & (
                    self.df_integrate_names_analysis.name_analysis_init
                    == self.name_analysis_dropdown.value
                )
            ),
            :,
        ]
        id_ana_integration_selected = analysis_selected.id_ana_integration
        # display(analysis_selected)
        if len(id_ana_integration_selected.index) == 0:
            id_ana_integration_return = None
        elif len(id_ana_integration_selected.index) == 1:
            id_ana_integration_return = id_ana_integration_selected.iloc[0]
            # display(self.df_ec_reactions)
            # display(analysis_selected)
            # read exp_ec_integration values from database
            with self.con.begin() as con:
                exp_ec_integration = db.query_sql(
                    """SELECT name_reaction, faradaic_efficiency__percent 
                       FROM hte_data.exp_ec_integration
                       WHERE id_exp_ec_dataset = %s
                       AND name_analysis = %s;
                    """,
                    params=[
                        int(analysis_selected.reset_index().id_exp_ec_dataset.iloc[0]),
                        analysis_selected.name_analysis_init.iloc[0],
                    ],
                    method="pandas",
                    con=con,
                )  # .iloc[0]
                if len(exp_ec_integration) == 0:
                    display(exp_ec_integration)
                    raise Exception(
                        "Cannot update name_reaction, faradaic_efficiency__percent, entry not find in database."
                    )
                exp_ec_integration_row = exp_ec_integration.iloc[0]
            self.dropdown_ec_reaction.value = self.df_ec_reactions.loc[
                self.df_ec_reactions.name_reaction
                == exp_ec_integration_row.name_reaction,
                "dropdown_label",
            ].iloc[
                0
            ]
            self.floattext_faradaic_efficiency.value = (
                exp_ec_integration_row.faradaic_efficiency__percent
            )

        else:
            raise ValueError(
                "Multiple integration analyses found. Please inform Admin!"
            )
        return id_ana_integration_return

    def read_ec_reactions(self):
        self.df_ec_reactions = db.query_sql(
            "ec_reactions",
            con=self.con,
            method="pandas",
            # index_col='id_exp_ec_dataset'
        )
        self.df_ec_reactions.loc[:, "dropdown_label"] = (
            self.df_ec_reactions.name_reaction
            + ": "
            + self.df_ec_reactions.number_electrons.astype(str)
            + " e-"
            + " per "
            + self.df_ec_reactions.name_product_of_interest
        )
        self.df_ec_reactions.loc[
            self.df_ec_reactions.dropdown_label.isna(), "dropdown_label"
        ] = self.df_ec_reactions.name_reaction


class Integrate:  # IntegrateContainer:
    """
    Class to perform the actual integration on the selected part of the data
    """

    def __init__(
        self,
        integrate_container,
        exp,
        data,
        # fig,
        # idx_baseline,
        # idx_integrate_begin,
        # idx_integrate_end,
    ):  # index):

        self.integrate_container = integrate_container
        self.exp = exp.copy()
        self.exp_index = (
            self.exp.index[0]
            if type(self.exp.index[0]) == tuple
            else tuple(self.exp.index)
        )  # difference between normal and multiindex

        try:
            self.exp.export_name = self.integrate_container.df_exp.export_name
        except AttributeError:
            warnings.warn("exp export_name undefined.")
            self.exp.export_name = str(self.exp_index)
        self.data = data  # all aw data
        self.data_zoom = data  # data which is within x window - for ICPMS limited by linked EC dataset selection
        # print(data)

        with plt.rc_context(self.integrate_container.plt_rcParams):
            self.exp.dataset.plot(
                self.integrate_container.x_col,
                self.integrate_container.y_col,
                # xerr_col=None,
                # yerr_col=None,
                data=self.data,
                ax=self.integrate_container.ax,
                print_info=self.integrate_container.print_info,
                axlabel_auto=self.integrate_container.axlabel_auto,
                timestamp_cols_to_seconds=self.integrate_container.timestamp_cols_to_seconds,
                export_object=self.integrate_container.export_object,
                export_name=self.integrate_container.export_name,  # 'plot',
                alpha=0.3,
                **self.integrate_container.plt_kwargs,
            ).add_column(
                "color",
                values=[
                    matplotlib.colors.to_hex(objPlot[-1][0].get_color())
                    for objPlot in self.exp.ax_plot_objects.tolist()
                ],
            ).plot(
                self.integrate_container.x_col,
                self.integrate_container.y_col,
                # xerr_col=None,
                # yerr_col=None,
                data=self.data_zoom,
                ax=self.integrate_container.ax,
                print_info=self.integrate_container.print_info,
                axlabel_auto=self.integrate_container.axlabel_auto,
                timestamp_cols_to_seconds=self.integrate_container.timestamp_cols_to_seconds,
                export_object=self.integrate_container.export_object,
                export_name=self.integrate_container.export_name,  # 'plot',
                **self.integrate_container.plt_kwargs,
            ).plot(
                x_col=self.integrate_container.x_col
                if type(self.integrate_container.x_col) == int
                or type(self.integrate_container.y2_col) == str
                else self.data.loc[:, self.integrate_container.x_col].to_numpy(),
                y_col=self.integrate_container.y2_col
                if type(self.integrate_container.y2_col) == int
                or type(self.integrate_container.x_col) == str
                else self.data.loc[:, self.integrate_container.y2_col].to_numpy(),
                ax=self.integrate_container.ax,
                data=self.data
                if type(self.integrate_container.x_col) == str
                and type(self.integrate_container.y2_col) == str
                else None,
                print_info=self.integrate_container.print_info,
                axlabel_auto=False,
                timestamp_cols_to_seconds=self.integrate_container.timestamp_cols_to_seconds,
                export_object=self.integrate_container.export_object,
                export_name=self.integrate_container.export_name + "_baseline",
                alpha=0.3,
                linestyle="--",
            ).fill_between(
                x_col=self.integrate_container.x_col,
                y_col=self.integrate_container.y_col,
                y2_col=self.integrate_container.y2_col,
                ax=self.integrate_container.ax,
                data=self.integrate_container.data,
                print_info=self.integrate_container.print_info,
                axlabel_auto=self.integrate_container.axlabel_auto,
                timestamp_cols_to_seconds=self.integrate_container.timestamp_cols_to_seconds,
                export_object=self.integrate_container.export_object,
                export_name=self.integrate_container.export_name + "_fill_between",
                alpha=0.3,
            )

            self.exp_row = self.exp.reset_index().iloc[0]

            self.zoom_home_x = self.integrate_container.ax.get_xlim()
            self.zoom_home_y = self.integrate_container.ax.get_ylim()

            self.id_ana_integration = None
            # self.from_database()

            self.idx_baseline = 0  # self.data.reset_index().index[20]# idx_baseline
            self.idx_integrate_begin = (
                0  # self.data.reset_index().index[0]#idx_integrate_begin
            )
            self.idx_integrate_min = 0
            self.idx_integrate_end = self.data_zoom.reset_index().index[
                -1
            ]  # idx_integrate_end
            self.idx_integrate_max = self.data_zoom.reset_index().index[-1]
            # print('jo', self.idx_integrate_begin, self.idx_integrate_end)
            # self.fig = fig
            self.plot_y1_all = self.exp_row.ax_plot_objects[-4][0]
            self.plot_y1 = self.exp_row.ax_plot_objects[-3][0]
            self.plot_y2 = self.exp_row.ax_plot_objects[-2][0]
            self.plot_fill_between = self.exp_row.ax_plot_objects[-1][0]
            if "auto" in self.integrate_container.set_baseline:
                (self.plot_y_col_std,) = self.integrate_container.axr.plot(
                    0, 0, color="tab:red", linestyle="-", alpha=0
                )  # 0.3
                (self.plot_y_col_1stderiv,) = self.integrate_container.axr.plot(
                    0, 0, color="tab:red", linestyle="--", alpha=0
                )  # 0.3
                (self.plot_y_col_2ndderiv,) = self.integrate_container.axr.plot(
                    0, 0, color="tab:red", linestyle="-.", alpha=0
                )  # 0.3
            (self.plot_baselinepoint,) = self.integrate_container.ax.plot(
                0, 0, color="tab:red", marker="x", alpha=0
            )  # self.exp_row.color
            (self.plot_beginpoint,) = self.integrate_container.ax.plot(
                0, 0, color="tab:red", marker="|", alpha=0
            )
            (self.plot_endpoint,) = self.integrate_container.ax.plot(
                0, 0, color="tab:red", marker="|", alpha=0
            )
            (self.plot_endpoint_offset,) = self.integrate_container.ax.plot(
                0, 0, color="tab:red", marker="x", alpha=0
            )
            (self.plot_baselineavg,) = self.integrate_container.ax.plot(
                0, 0, color="tab:red", alpha=0
            )
            (self.plot_endavg,) = self.integrate_container.ax.plot(
                0, 0, color="tab:red", alpha=0
            )

        self.active = True
        self.widget_fires_update = True

        self.no_of_datapoints_rolling = (
            200
            if len(self.data_zoom.index) / 4 > 200
            else int(len(self.data_zoom.index) / 4)
        )
        self.no_of_datapoints_avg = 20

        # dum y set left and right data to left and right edges
        self.data_left = self.data.reset_index().iloc[:self.no_of_datapoints_rolling]
        self.data_right = self.data.reset_index().iloc[-self.no_of_datapoints_rolling:]
        # print(self.data_left.index)

        self.auto_integration = False
        # calculating data_zoom is required if auto baseline detection fails,
        # begin/end would be determined not on the zoomed window --> throwing error
        self.get_data_zoom()
        if "auto" in self.integrate_container.set_baseline:
            self.auto_integration = True
            self.update_baseline()

        self.update_integration_data()  # intText_no_of_datapoints_avg.value)
        self.update_integration_plot()

        with self.integrate_container.output_integration:
            clear_output()
        self.deactivate()
        self.activate(overview=True)

    def get_data_zoom(
        self,
    ):
        if self.integrate_container.link_name_analysis:
            with self.integrate_container.output_integration_activate:
                clear_output()
                try:  # necessary due to construction of method .active()
                    # display(self.integrate_container.parent_integrate_container.active().data)
                    x_min = (
                        self.integrate_container.parent_integrate_container.active()
                        .data.loc[
                            :, self.integrate_container.parent_integrate_container.x_col
                        ]
                        .iloc[0]
                        + self.integrate_container.x_start_shift
                    )
                    x_max = (
                        self.integrate_container.parent_integrate_container.active()
                        .data.loc[
                            :, self.integrate_container.parent_integrate_container.x_col
                        ]
                        .iloc[-1]
                        + self.integrate_container.x_end_shift
                    )
                    # print('x-Axis data in range:', x_min, x_max)

                    idxs_zoom = (
                        (self.data[self.integrate_container.x_col] > x_min)
                        & (self.data[self.integrate_container.x_col] < x_max)
                        & (~self.data[self.integrate_container.y_col].isna())
                    )
                    self.data_zoom = self.data.loc[idxs_zoom, :].sort_index()
                    # display(self.data_zoom)
                    self.plot_y1.set_data(
                        self.data_zoom.loc[:, self.integrate_container.x_col],
                        self.data_zoom.loc[:, self.integrate_container.y_col],
                    )

                    self.integrate_container.ax.set_ylim(
                        [
                            self.data[self.integrate_container.y_col].min(),
                            self.data[self.integrate_container.y_col].max(),
                        ]
                    )
                    plot.autoscale_axis(
                        self.integrate_container.ax, which="x", lines=self.plot_y1
                    )

                    print("x-Axis zoom to:", self.integrate_container.ax.get_xlim())
                    plot.autoscale_axis(
                        self.integrate_container.ax, which="y", lines=self.plot_y1
                    )
                    plot.autoscale_axis(
                        self.integrate_container.parent_integrate_container.ax,
                        which="y",
                        lines=self.integrate_container.parent_integrate_container.active().plot_y1,
                    )
                except ValueError as error:
                    print(error)
                    print("No linked analysis selected, no zoom performed")
                    self.data_zoom = self.data.sort_index()

        else:
            self.data_zoom = self.data.sort_index()

    def activate(self, overview=False):

        self.active = True
        self.initialized = False
        self.plot_y1_all.set_alpha(0.3)
        self.plot_y1.set_alpha(1)
        self.plot_y2.set_alpha(1)
        self.plot_fill_between.set_alpha(0.3)

        if not overview:
            # clear old integration output
            with self.integrate_container.output_integration:
                clear_output()

            self.get_data_zoom()

            self.id_ana_integration = self.integrate_container.get_id_ana_integration()
            # print('hallo', self.id_ana_integration, int(self.id_ana_integration))
            if self.id_ana_integration is not None:
                with self.integrate_container.output_integration:
                    print("read from database...")
                    # display(ana_integration)
                    with self.integrate_container.con.begin() as con:
                        df_from_database = db.query_sql(
                            """ SELECT * 
                                        FROM hte_data.ana_integrations 
                                        WHERE id_ana_integration = %s;""",
                            params=[int(self.id_ana_integration)],
                            method="pandas",
                            con=con,
                        ).iloc[0]
                    # display(df_from_database)
                    # display(self.exp.index, (df_from_database.id_data_integration_baseline,))

                    self.idx_baseline = np.argwhere(
                        self.data.index
                        == self.exp_index
                        + (df_from_database.id_data_integration_baseline,)
                    )[0][0]
                    self.idx_integrate_begin = np.argwhere(
                        self.data.index
                        == self.exp_index
                        + (df_from_database.id_data_integration_begin,)
                    )[0][0]
                    self.idx_integrate_end = np.argwhere(
                        self.data.index
                        == self.exp_index + (df_from_database.id_data_integration_end,)
                    )[0][0]
                    self.no_of_datapoints_rolling = (
                        df_from_database.no_of_datapoints_rolling
                    )
                    self.no_of_datapoints_avg = df_from_database.no_of_datapoints_avg
                    self.auto_integration = df_from_database.auto_integration

                    # set exp_ec/icpms_integration table parameters in get_id_ana_integration
                    # if self.integrate_container.to_database_table == 'exp_ec_integration':
                    #    self.integrate_container.dropdown_ec_reaction.value =
                    #    self.integrate_container.df_ec_reactions.loc[
                    #        self.integrate_container.df_ec_reactions.name_reaction ==
                    #        df_from_database.name_reaction, 'dropdown_label'].iloc[0]
                    #    self.integrate_container.floattext_faradaic_efficiency.value =
                    #    df_from_database.faradaic_efficiency__percent

                    print(
                        "\x1b[32m"
                        + "Integration parameter successfully read from database.\n"
                        + "\x1b[0m"
                    )
            elif "auto" in self.integrate_container.set_baseline:
                self.update_baseline()
                # print("\x1b[32m", 'Integration parameter derived from auto-algorithm', "\x1b[0m")

            # first limits of intSlider_baseline need to be set than intText_no_of_datapoints_rolling van initiated
            # if 'manual' in self.integrate_container.set_baseline:

            self.idx_integrate_min = (
                self.data.reset_index()
                .loc[self.data.index.isin(self.data_zoom.index), :]
                .index.min()
            )
            self.idx_integrate_max = (
                self.data.reset_index()
                .loc[self.data.index.isin(self.data_zoom.index), :]
                .index.max()
            )
            # display(self.data_zoom)
            self.integrate_container.intSlider_baseline.min = 0  # avoid set max < min
            self.integrate_container.intSlider_integrate_begin.min = (
                0  # avoid set max < min
            )
            self.integrate_container.intSlider_integrate_end.min = (
                0  # avoid set max < min
            )
            self.integrate_container.intSlider_baseline.max = (
                self.idx_integrate_max
            )  # self.data_left.index.max()
            self.integrate_container.intSlider_baseline.min = (
                self.idx_integrate_min
            )  # self.data_left.index.min()
            self.integrate_container.intSlider_integrate_begin.max = (
                self.data.reset_index()
                .loc[self.data.index.isin(self.data_zoom.index), :]
                .index.max()
                - 1
            )  # self.data_left.index.max()
            self.integrate_container.intSlider_integrate_begin.min = max(
                self.idx_baseline, self.integrate_container.intSlider_baseline.min
            )  # self.data_left.index.min()
            self.integrate_container.intSlider_integrate_end.max = (
                self.data.reset_index()
                .loc[self.data.index.isin(self.data_zoom.index), :]
                .index.max()
            )  # self.data_right.index.max()
            self.integrate_container.intSlider_integrate_end.min = max(
                self.idx_integrate_begin,
                self.integrate_container.intSlider_integrate_begin.min + 1,
            )  # self.data_right.index.min()
            # if 'auto' not in self.integrate_container.set_baseline:
            self.integrate_container.intSlider_baseline.value = self.idx_baseline
            self.integrate_container.intSlider_integrate_begin.value = (
                self.idx_integrate_begin
            )
            self.integrate_container.intSlider_integrate_end.value = (
                self.idx_integrate_end
            )

            # if 'auto' in self.integrate_container.set_baseline:
            self.integrate_container.intText_no_of_datapoints_rolling.value = int(
                self.no_of_datapoints_rolling
            )
            self.integrate_container.intText_no_of_datapoints_avg.value = int(
                self.no_of_datapoints_avg
            )

            self.update_integration_data()  # intText_no_of_datapoints_avg.value)
            self.update_integration_plot()
            self.initialized = True
            # print(self.data_left.index)
        # else:
        #    self.update_integration_plot()

    def deactivate(self):
        self.active = False
        self.plot_y1_all.set_alpha(0.1)
        self.plot_y1.set_alpha(0.1)
        self.plot_y2.set_alpha(0)
        self.plot_fill_between.set_alpha(0)

        self.data_zoom = self.data.sort_index()
        self.plot_y1.set_data(
            self.data_zoom.loc[:, self.integrate_container.x_col],
            self.data_zoom.loc[:, self.integrate_container.y_col],
        )
        self.integrate_container.ax.set_xlim(self.zoom_home_x)
        self.integrate_container.ax.set_ylim(self.zoom_home_y)

        for plot_show in [
            self.plot_baselinepoint,
            self.plot_baselineavg,
            self.plot_beginpoint,
            self.plot_endpoint,
            self.plot_endpoint_offset,
            self.plot_endavg,
        ]:
            plot_show.set_alpha(0)

        if "auto" in self.integrate_container.set_baseline:
            for plot_show in [
                self.plot_y_col_std,
                self.plot_y_col_1stderiv,
                self.plot_y_col_2ndderiv,
            ]:
                plot_show.set_alpha(0)

    def to_database(self, con):
        if not self.integrate_container.database_constraint_username(self.exp_index):
            return False

        print("send to db", self.integrate_container.y_col)
        # con = db.connect(user='hte_integrater')

        df_ana_integration = pd.DataFrame(
            {
                "id_ana_integration": self.id_ana_integration,
                "id_data_integration_baseline": self.data.reset_index()
                .iloc[self.idx_baseline]
                .loc[self.integrate_container.to_database_name_id_data],
                "id_data_integration_begin": self.data.reset_index()
                .iloc[self.idx_integrate_begin]
                .loc[self.integrate_container.to_database_name_id_data],
                "id_data_integration_end": self.data.reset_index()
                .iloc[self.idx_integrate_end]
                .loc[self.integrate_container.to_database_name_id_data],
                "t_integration_baseline__timestamp": self.data.reset_index()
                .iloc[self.idx_baseline]
                .loc[self.integrate_container.to_database_name_timestamp],
                "t_integration_begin__timestamp": self.data.reset_index()
                .iloc[self.idx_integrate_begin]
                .loc[self.integrate_container.to_database_name_timestamp],
                "t_integration_end__timestamp": self.data.reset_index()
                .iloc[self.idx_integrate_end]
                .loc[self.integrate_container.to_database_name_timestamp],
                "area_integrated_simps": self.area_integrated_simps,  # _simps
                "area_integrated_trapz": self.area_integrated_trapz,
                "y_offset": self.endavg_offset,
                "no_of_datapoints_avg": self.no_of_datapoints_avg,
                "no_of_datapoints_rolling": self.no_of_datapoints_rolling,
                "auto_integration": self.auto_integration,
            },
            index=[0],
        ).set_index("id_ana_integration")
        # display(df_ana_integration)

        if df_ana_integration.drop(columns=["y_offset"]).iloc[0].isna().any():
            display(df_ana_integration)
            raise ValueError(
                "Not allowed NULL values found in df_ana_integration. Please report to Admin"
            )

        if self.integrate_container.to_database_table == "exp_ec_integration":
            df_exp_integration = pd.DataFrame(
                {
                    "id_exp_ec_dataset": int(self.exp_row.id_exp_ec_dataset),
                    "name_analysis": self.integrate_container.name_analysis_text.value,
                    "id_ana_integration": self.id_ana_integration,
                    "name_reaction": self.integrate_container.df_ec_reactions.loc[
                        self.integrate_container.df_ec_reactions.dropdown_label
                        == self.integrate_container.dropdown_ec_reaction.value,
                        "name_reaction",
                    ].iloc[0],
                    "faradaic_efficiency__percent": self.integrate_container.floattext_faradaic_efficiency.value,
                },
                index=[0],
            )
            index_insert = ["id_exp_ec_dataset", "name_analysis"]
            index_update = ["id_exp_ec_dataset", "id_ana_integration"]
        elif self.integrate_container.to_database_table == "exp_icpms_integration":
            df_exp_integration = pd.DataFrame(
                {
                    "id_exp_icpms": int(self.exp_row.id_exp_icpms),
                    "name_isotope_analyte": self.exp_row.name_isotope_analyte,
                    "name_isotope_internalstandard": self.exp_row.name_isotope_internalstandard,
                    "name_analysis": self.integrate_container.name_analysis_text.value,
                    "id_exp_ec_dataset": int(
                        self.integrate_container.parent_integrate_container.active().exp_row.id_exp_ec_dataset
                    ),
                    "id_ana_integration": self.id_ana_integration,
                },
                index=[0],
            )
            index_insert = [
                "id_exp_icpms",
                "name_isotope_analyte",
                "name_isotope_internalstandard",
                "name_analysis",
                "id_exp_ec_dataset",
            ]
            index_update = [
                "id_exp_icpms",
                "name_isotope_analyte",
                "name_isotope_internalstandard",
                "id_exp_ec_dataset",
                "id_ana_integration",
            ]

        else:
            raise ValueError(
                "integration of "
                + self.integrate_container.y_col
                + " not yet implemented"
            )

        if self.id_ana_integration is None:
            # insert
            print("Insert new integration analysis...")
            # insert without id_ana_integration
            df_exp_integration = df_exp_integration.set_index(index_insert)
            df_exp_integration.to_sql(
                self.integrate_container.to_database_table,
                con=con,  # cursor,#self.integrate_container.con,
                if_exists="append",
            )

            # display(df_ana_integration)
            df_ana_integration = (
                db.insert_into(
                    conn=con,  # cursor,#self.integrate_container.con,
                    tb_name="ana_integrations",
                    df=df_ana_integration,
                )
                .reset_index(drop=True)
                .rename(columns={"inserted_primary_key": "id_ana_integration"})
                .set_index("id_ana_integration")
            )
            self.id_ana_integration = df_ana_integration.index[0]
            # display(df_exp_integration)
            # update without id_ana_integratio
            df_exp_integration.id_ana_integration = self.id_ana_integration
            db.sql_update(
                df_update=df_exp_integration,
                table_name=self.integrate_container.to_database_table,
                # engine=self.integrate_container.con,
                # cursor=cursor,
                con=con,
            )
            # display(df_ana_integration)

            # display(self.exp.index)
            self.integrate_container.df_integrate_names_analysis = pd.concat(
                [
                    self.integrate_container.df_integrate_names_analysis,
                    pd.DataFrame(
                        [
                            list(self.exp_index)
                            + [
                                self.integrate_container.name_analysis_text.value,
                                self.id_ana_integration,
                            ]
                            + (
                                [
                                    int(
                                        self.integrate_container.parent_integrate_container.active()
                                            .exp_row.id_exp_ec_dataset
                                    )
                                ]
                                if self.integrate_container.to_database_table
                                == "exp_icpms_integration"
                                else []
                            )
                        ],
                        columns=self.exp.index.names
                        + ["name_analysis_init", "id_ana_integration"]
                        + (
                            ["id_exp_ec_dataset"]
                            if self.integrate_container.to_database_table
                            == "exp_icpms_integration"
                            else []
                        ),
                        index=[0],
                    ).set_index(self.exp.index.names),
                ]
            )

            # if self.integrate_container.to_database_table == 'exp_icpms_integration':
            #    self.integrate_container.df_integrate_names_analysis\
            #        .loc[((self.integrate_container.df_integrate_names_analysis.index.isin([tuple(self.exp_index)])),
            #              (self.integrate_container.df_integrate_names_analysis.isna()),
            #              (self.integrate_container.df_integrate_names_analysis.id_ana_integration
            #              == self.id_ana_integration)),
            #             'id_exp_ec_dataset'] = int(
            #                                       self.integrate_container.parent_integrate_container.active()
            #                                       .exp_row.id_exp_ec_dataset)
            # display(self.integrate_container.df_integrate_names_analysis)

            print(
                "\x1b[32m",
                "Successfully prepared data for insert into database of analysis",
                self.integrate_container.name_analysis_text.value,
                "\x1b[0m",
            )
        else:
            print("Update existing integration analysis...")
            df_exp_integration = df_exp_integration.set_index(index_update)

            # update name_analysis
            db.sql_update(
                df_update=df_exp_integration,
                table_name=self.integrate_container.to_database_table,
                # engine=self.integrate_container.con,
                # cursor=cursor,
                con=con,
                add_cond='name_analysis = "'
                + self.integrate_container.name_analysis_dropdown.value
                + '"',
            )
            # print(self.integrate_container.df_integrate_names_analysis, self.exp.index)
            self.integrate_container.df_integrate_names_analysis.loc[
                self.exp_index, "name_analysis_init"
            ] = self.integrate_container.name_analysis_text.value

            db.sql_update(
                df_update=df_ana_integration,
                table_name="ana_integrations",
                # engine=self.integrate_container.con,
                # cursor=cursor,
                con=con,
            )
            print(
                "\x1b[32m",
                "Successfully prepared data for update database entry of analysis",
                self.integrate_container.name_analysis_text.value,
                "\x1b[0m",
            )

        # print("\x1b[32m", 'Successfully updated', self.name_analysis_text.value, "\x1b[0m")
        return True

    def set_no_of_datapoints_rolling(self, value, update):
        self.no_of_datapoints_rolling = value

        with self.integrate_container.output_integration:
            clear_output()

        self.update_baseline()

        self.widget_fires_update = False
        self.integrate_container.intSlider_baseline.value = self.idx_baseline
        self.integrate_container.intSlider_integrate_begin.value = (
            self.idx_integrate_begin
        )
        self.integrate_container.intSlider_integrate_end.value = self.idx_integrate_end
        # self.integrate_container.intSlider_integrate_begin.min = self.idx_baseline
        # self.integrate_container.intSlider_integrate_end.min = self.idx_integrate_begin

        if update:
            self.auto_integration = True
            self.update_integration_data()
            self.update_integration_plot()
            self.widget_fires_update = True

    def set_no_of_datapoints_avg(self, value, update):
        self.no_of_datapoints_avg = value

        self.widget_fires_update = False

        if update:
            with self.integrate_container.output_integration:
                clear_output()
            # self.auto_integration = False  # do not change, keep auto_integration value
            self.update_integration_data()
            self.update_integration_plot()
            self.widget_fires_update = True

    def set_idx_baseline(self, value, update):
        self.idx_baseline = value

        self.widget_fires_update = False
        self.integrate_container.intSlider_integrate_begin.min = self.idx_baseline
        # self.integrate_container.intSlider_integrate_end.min = self.idx_integrate_begin+1

        if update:
            with self.integrate_container.output_integration:
                clear_output()
            self.auto_integration = False
            self.update_integration_data()  # intText_no_of_datapoints_avg.value)
            self.update_integration_plot()
            self.widget_fires_update = True

    def set_idx_integrate_begin(self, value, update):
        self.idx_integrate_begin = value

        self.widget_fires_update = False
        self.integrate_container.intSlider_integrate_end.min = (
            self.idx_integrate_begin + 1
        )
        if update:
            with self.integrate_container.output_integration:
                clear_output()
            self.auto_integration = False
            self.update_integration_data()  # intText_no_of_datapoints_avg.value)
            self.update_integration_plot()
            self.widget_fires_update = True

    def set_idx_integrate_end(self, value, update):
        self.idx_integrate_end = value

        if update:
            with self.integrate_container.output_integration:
                clear_output()
            self.auto_integration = False
            self.update_integration_data()  # intText_no_of_datapoints_avg.value)
            self.update_integration_plot()
            self.widget_fires_update = True

    def update_baseline(self):
        with self.integrate_container.output_integration:
            self.data.loc[:, self.integrate_container.y_col_std] = (
                self.data.loc[:, self.integrate_container.y_col]
                .rolling(self.no_of_datapoints_rolling, center=True)
                .std()
            )
            self.data.loc[:, self.integrate_container.y_col_1stderiv] = (
                self.data.loc[:, self.integrate_container.y_col]
                .rolling(self.no_of_datapoints_rolling, center=True)
                .mean()
                .diff()
                .rolling(self.no_of_datapoints_rolling, center=True)
                .mean()
                .abs()
            )
            self.data.loc[:, self.integrate_container.y_col_2ndderiv] = (
                self.data.loc[:, self.integrate_container.y_col]
                .rolling(self.no_of_datapoints_rolling, center=True)
                .mean()
                .diff()
                .rolling(self.no_of_datapoints_rolling, center=True)
                .mean()
                .diff()
                .rolling(self.no_of_datapoints_rolling, center=True)
                .mean()
                .abs()
            )

            cut_peakdata_factor_of_max = 0.1
            try:
                self.data_left = self.data.reset_index().loc[
                    (
                        (self.data.index.isin(self.data_zoom.index))
                        & (
                            self.data.index
                            < self.data_zoom.loc[
                                :, self.integrate_container.y_col
                            ].idxmax()
                        )
                    ),
                    :,
                ]
                if (
                    self.data_left.loc[:, self.integrate_container.y_col_std]
                    .isna()
                    .all()
                ):
                    raise ValueError(
                        "no_datapoints_rolling too large for that small selected window"
                    )
                self.idx_baseline = (
                    self.data_left.loc[
                        self.data_left.loc[:, self.integrate_container.y_col]
                        < self.data_left.loc[:, self.integrate_container.y_col].max()
                        * cut_peakdata_factor_of_max,
                        self.integrate_container.y_col_1stderiv,
                    ].fillna(0)
                    + self.data_left.loc[
                        self.data_left.loc[:, self.integrate_container.y_col]
                        < self.data_left.loc[:, self.integrate_container.y_col].max()
                        * cut_peakdata_factor_of_max,
                        self.integrate_container.y_col_2ndderiv,
                    ].fillna(0)
                    + self.data_left.loc[
                        self.data_left.loc[:, self.integrate_container.y_col]
                        < self.data_left.loc[:, self.integrate_container.y_col].max()
                        * cut_peakdata_factor_of_max,
                        self.integrate_container.y_col_std,
                    ].fillna(0)
                ).idxmin()
            except ValueError:
                # if np.isnan(self.idx_baseline):
                # warnings.warn('No baseline detected\n Please inform Admin!')
                self.idx_baseline = (
                    self.data_left.loc[
                        ~self.data_left.loc[:, self.integrate_container.y_col].isna(), :
                    ]
                    .iloc[0]
                    .name
                )
                print(
                    "\x1b[33m",
                    "No baseline detected. Please inform Admin!",
                    "Instead using:",
                    self.idx_baseline,
                    "\x1b[0m",
                )

            try:
                self.data_right = self.data.reset_index().loc[
                    (
                        (self.data.index.isin(self.data_zoom.index))
                        & (
                            self.data.index
                            > self.data_zoom.loc[
                                :, self.integrate_container.y_col
                            ].idxmax()
                        )
                    ),
                    :,
                ]
                if (
                    self.data_right.loc[:, self.integrate_container.y_col_std]
                    .isna()
                    .all()
                ):
                    raise ValueError(
                        "no_datapoints_rolling too large for that small selected window"
                    )
                self.idx_integrate_end = (
                    self.data_right.loc[
                        self.data_right.loc[:, self.integrate_container.y_col]
                        < self.data_right.loc[:, self.integrate_container.y_col].max()
                        * cut_peakdata_factor_of_max,
                        self.integrate_container.y_col_1stderiv,
                    ].fillna(0)
                    + self.data_right.loc[
                        self.data_right.loc[:, self.integrate_container.y_col]
                        < self.data_right.loc[:, self.integrate_container.y_col].max()
                        * cut_peakdata_factor_of_max,
                        self.integrate_container.y_col_2ndderiv,
                    ].fillna(0)
                    + self.data_right.loc[
                        self.data_right.loc[:, self.integrate_container.y_col]
                        < self.data_right.loc[:, self.integrate_container.y_col].max()
                        * cut_peakdata_factor_of_max,
                        self.integrate_container.y_col_std,
                    ].fillna(0)
                ).idxmin()
            except ValueError:
                # print('integrate_end', self.idx_integrate_end)
                # if np.isnan(self.idx_integrate_end):
                # warnings.warn('No end detected\n Please inform Admin!')
                self.idx_integrate_end = (
                    self.data_right.loc[
                        ~self.data_right.loc[:, self.integrate_container.y_col].isna(),
                        :,
                    ]
                    .iloc[-1]
                    .name
                )
                print(
                    "\x1b[33m",
                    "No end detected. Please inform Admin!",
                    "Instead using:",
                    self.idx_integrate_end,
                    "\x1b[0m",
                )

            # display(self.data_right)
            self.idx_integrate_begin = self.idx_baseline

    def update_integration_data(self):
        with self.integrate_container.output_integration:
            if self.auto_integration:
                print(
                    "\x1b[35m"
                    + "Integration parameter derived from auto-algorithm"
                    + "\x1b[0m"
                )
            else:
                print(
                    "\x1b[35m" + "Integration parameter manually adjusted" + "\x1b[0m"
                )
            #    clear_output()
            # print('ll', self.idx_integrate_begin, self.idx_integrate_end)
            self.idx_fitted = self.data.iloc[
                self.idx_integrate_begin : self.idx_integrate_end + 1
            ].index
            self.endavg_offset = None

            print(
                "integration limits: ",
                self.data.loc[:, self.integrate_container.x_col].iloc[
                    self.idx_integrate_begin
                ],
                self.integrate_container.x_col.split("__")[-1],
                self.data.loc[:, self.integrate_container.x_col].iloc[
                    self.idx_integrate_end
                ],
                self.integrate_container.x_col.split("__")[-1],
            )

            # baseline derivation, y_col_baselineavg
            if (
                "auto" in self.integrate_container.set_baseline
                or "manual" in self.integrate_container.set_baseline
            ):
                self.data.loc[:, self.integrate_container.y_col_baselineavg] = np.nan
                """
                if 'fixed' in self.integrate_container.set_baseline:
                    self.idx_baseline_datapoints = slice(self.idx_baseline, self.idx_baseline+1)
                    #print(self.data.iloc[self.idx_baseline_datapoints].index, self.data.columns)
                    self.data.loc[self.data.iloc[self.idx_baseline_datapoints].index,
                                  self.integrate_container.y_col_baselineavg] 
                                  = self.data.iloc[self.idx_baseline_datapoints].loc[:, self.integrate_container.y2_col]

                else:
                """
                self.idx_baseline_datapoints = slice(
                    int(self.idx_baseline - (self.no_of_datapoints_avg / 2))
                    if (
                        int(self.idx_baseline - (self.no_of_datapoints_avg / 2))
                        > self.idx_integrate_min
                    )
                    # if self.idx_baseline > (self.no_of_datapoints_avg / 2)
                    else self.idx_integrate_min,  # 0,
                    int(self.idx_baseline + (self.no_of_datapoints_avg / 2)),
                )
                # (self.idx_baseline_datapoints)
                self.data.loc[
                    self.data.iloc[self.idx_baseline_datapoints].index,
                    self.integrate_container.y_col_baselineavg,
                ] = self.data.iloc[self.idx_baseline_datapoints].loc[
                    :, self.integrate_container.y_col
                ]

                self.baselineavg = (
                    self.data.iloc[self.idx_baseline_datapoints]
                    .loc[:, self.integrate_container.y_col_baselineavg]
                    .mean()
                )
                if np.isnan(self.baselineavg):
                    print(
                        "\x1b[31m",
                        "Baseline y-value is nan, possibly an error in calculation. "
                        "Baseline is set to 0. Please inform Admin.",
                        "\x1b[0m",
                    )
                    self.baselineavg = 0

                # end derivation, integrate_container
                self.idx_integrate_end_datapoints = slice(
                    int(self.idx_integrate_end - (self.no_of_datapoints_avg / 2)),
                    int(self.idx_integrate_end + (self.no_of_datapoints_avg / 2)) + 1
                    if (
                        int(self.idx_integrate_end + (self.no_of_datapoints_avg / 2))
                        + 1
                        < self.idx_integrate_max + 1
                    )
                    else self.idx_integrate_max + 1,
                )
                self.data.loc[:, self.integrate_container.y_col_endavg] = np.nan
                self.data.loc[
                    self.data.iloc[self.idx_integrate_end_datapoints].index,
                    self.integrate_container.y_col_endavg,
                ] = self.data.iloc[self.idx_integrate_end_datapoints].loc[
                    :, self.integrate_container.y_col
                ]
                self.endavg = (
                    self.data.iloc[self.idx_integrate_end_datapoints]
                    .loc[:, self.integrate_container.y_col_endavg]
                    .mean()
                )
                if np.isnan(self.endavg):
                    print(
                        "\x1b[31m",
                        "End y-value is nan, possibly an error in calculation. "
                        "End y-value is set to 0. Please inform Admin.",
                        "\x1b[0m",
                    )
                    self.endavg = 0

                self.endavg_offset = self.endavg - self.baselineavg

                print(
                    "baseline:",
                    self.baselineavg,
                    self.integrate_container.y_col.split("__")[-1],
                )
                # print('end:', self.endavg, self.integrate_container.y_col.split('__')[-1])
                # self.beginavg_offset = self.endavg - self.baselineavg
                # print('offset begin:', self.endavg_offset, self.integrate_container.y_col.split('__')[-1])#, 'ng_s')
                print(
                    "offset end:",
                    self.endavg_offset,
                    self.integrate_container.y_col.split("__")[-1],
                )  # , 'ng_s')

                # baseline
                # self.idx_fitted = self.data.iloc[self.idx_integrate_begin:self.idx_integrate_end+1].index
                self.data.loc[:, self.integrate_container.y2_col] = np.nan
                self.data.loc[
                    self.idx_fitted, self.integrate_container.y2_col
                ] = self.baselineavg

            if (
                self.data.loc[self.idx_fitted, self.integrate_container.y_col]
                .isna()
                .any()
            ):
                print(
                    "\x1b[33m",
                    "There are nan values in your data. This is not possible to integrate.",
                    "\x1b[0m",
                )

            # integrate
            self.area_integrated_simps = scipy.integrate.simps(
                y=self.data.loc[self.idx_fitted, self.integrate_container.y_col]
                - self.data.loc[self.idx_fitted, self.integrate_container.y2_col],  #
                x=self.data.loc[self.idx_fitted, self.integrate_container.x_col],
            )
            self.area_integrated_trapz = np.trapz(
                y=self.data.loc[self.idx_fitted, self.integrate_container.y_col]
                - self.data.loc[self.idx_fitted, self.integrate_container.y2_col],  #
                x=self.data.loc[self.idx_fitted, self.integrate_container.x_col],
            )

            print("integrated area (simps):", self.area_integrated_simps)  # , 'ng')
            print("integrated area (trapz):", self.area_integrated_trapz)  # , 'ng')

            # quality indicator
            if (
                self.area_integrated_simps / self.area_integrated_trapz < 0.95
                or self.area_integrated_simps / self.area_integrated_trapz > 1.05
            ):
                print(
                    "\x1b[33m",
                    "Significant deviation between trapezoidal and integration following Simpson's rule.\n",
                    "Be aware of which result your are going to use for analysis. Both values stored in database.",
                    "\x1b[0m",
                )

    def update_integration_plot(self):
        self.plot_y2.set_data(
            self.data.loc[:, self.integrate_container.x_col],
            self.data.loc[:, self.integrate_container.y2_col],
        )
        self.plot_fill_between.set_paths(
            [
                np.array(
                    self.integrate_container.ax.fill_between(
                        x=self.integrate_container.x_col,
                        y1=self.integrate_container.y_col,
                        y2=self.integrate_container.y2_col,
                        data=self.data.loc[self.idx_fitted, :],
                        alpha=0,
                    )
                    .get_paths()[0]
                    .vertices
                )
            ]
        )
        if "auto" in self.integrate_container.set_baseline:
            for plot_show in [
                self.plot_y_col_std,
                self.plot_y_col_1stderiv,
                self.plot_y_col_2ndderiv,
            ]:
                plot_show.set_alpha(0.3)
            self.plot_y_col_std.set_data(
                self.data.loc[:, self.integrate_container.x_col],
                self.data.loc[:, self.integrate_container.y_col_std],
            )
            self.plot_y_col_1stderiv.set_data(
                self.data.loc[:, self.integrate_container.x_col],
                self.data.loc[:, self.integrate_container.y_col_1stderiv],
            )
            self.plot_y_col_2ndderiv.set_data(
                self.data.loc[:, self.integrate_container.x_col],
                self.data.loc[:, self.integrate_container.y_col_2ndderiv],
            )

            if (
                len(
                    self.data.loc[
                        self.data.index.isin(self.data_zoom.index),
                        self.integrate_container.y_col_std,
                    ]
                    .dropna()
                    .index
                )
                > 0
            ):
                # perform autoscale if in zoomed window auto baseline was derived and any value notna
                # all na would happen if number of datapoints in window < no_datapoints_rolling
                plot.autoscale_axis(self.integrate_container.axr, which="y")
        if (
            "auto" in self.integrate_container.set_baseline
            or "manual" in self.integrate_container.set_baseline
        ):
            # print('jojo', self.data.loc[:, self.integrate_container.x_col].iloc[self.idx_baseline],
            #                                 self.baselineavg)
            for plot_show in [
                self.plot_baselinepoint,
                self.plot_baselineavg,
                self.plot_beginpoint,
                self.plot_endpoint,
                self.plot_endpoint_offset,
                self.plot_endavg,
            ]:
                plot_show.set_alpha(1)
            self.plot_baselinepoint.set_data(
                self.data.loc[:, self.integrate_container.x_col].iloc[
                    self.idx_baseline
                ],
                self.baselineavg,
            )
            self.plot_baselineavg.set_data(
                self.data.loc[:, self.integrate_container.x_col].iloc[
                    self.idx_baseline_datapoints
                ],
                self.data.loc[:, self.integrate_container.y_col].iloc[
                    self.idx_baseline_datapoints
                ],
            )
            self.plot_beginpoint.set_data(
                self.data.loc[:, self.integrate_container.x_col].iloc[
                    self.idx_integrate_begin
                ],
                self.baselineavg,
            )
            # self.idx_integrate_end
            # --> self.idx_integrate_end - 1 slicing until self.idx_integrate_end will end 1 datapoint before
            self.plot_endpoint.set_data(
                self.data.loc[:, self.integrate_container.x_col].iloc[
                    self.idx_integrate_end
                ],
                self.baselineavg,
            )
            self.plot_endpoint_offset.set_data(
                self.data.loc[:, self.integrate_container.x_col].iloc[
                    self.idx_integrate_end
                ],
                self.endavg,
            )
            self.plot_endavg.set_data(
                self.data.loc[:, self.integrate_container.x_col].iloc[
                    self.idx_integrate_end_datapoints
                ],
                self.data.loc[:, self.integrate_container.y_col].iloc[
                    self.idx_integrate_end_datapoints
                ],
            )
        elif "fixed" in self.integrate_container.set_baseline:
            for plot_show in [
                self.plot_baselinepoint,
                self.plot_beginpoint,
                self.plot_endpoint,
            ]:
                plot_show.set_alpha(1)
            data_plot_beginpoint = self.plot_beginpoint.get_data()
            self.plot_beginpoint.set_data(
                self.data.loc[:, self.integrate_container.x_col].iloc[
                    self.idx_integrate_begin
                ],
                data_plot_beginpoint[1],
            )
            data_plot_endpoint = self.plot_endpoint.get_data()
            self.plot_endpoint.set_data(
                self.data.loc[:, self.integrate_container.x_col].iloc[
                    self.idx_integrate_end
                ],
                data_plot_endpoint[1],
            )
