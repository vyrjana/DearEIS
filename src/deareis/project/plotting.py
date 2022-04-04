# Copyright 2022 DearEIS developers
# DearEIS is licensed under the GPLv3 or later (https://www.gnu.org/licenses/gpl-3.0.html).
# The licenses of DearEIS' dependencies and/or sources of portions of code are included in
# the LICENSES folder.

from typing import Callable, Dict, List, Optional, Union
from pyimpspec import DataSet
from numpy import ndarray, ceil
import dearpygui.dearpygui as dpg
import deareis.themes as themes
import deareis.tooltips as tooltips
from deareis.utility import attach_tooltip
from deareis.data.kramers_kronig import TestResult
from deareis.data.fitting import FitResult
from deareis.data.simulation import SimulationResult
from deareis.data.plotting import (
    PlotSettings,
    PlotType,
    label_to_plot_type,
    plot_type_to_label,
)
from deareis.plot.shared import line, scatter
from deareis.config import CONFIG


"""
Left-hand side
- Sidebar
    - Combo for choosing a plot (also via keyboard shortcuts)
    - Text input for setting the label of the plot
    - Button for deleting a plot
    - Collapsing headers for each data set
        - Collapsing headers for test and fit results
        - Each data set, test, and fit would have
            - Checkbox for visibility
            - Color edit
            - Combo for picking a marker (also "no marker" as an option)
            - Checkbox for also plotting a line

Implement automatic theme creation and binding
Implement modifying of appearance settings
Implement copying of appearance settings


Update
- When data sets are added, removed, or modified
    - Mask is modified
    - Impedances are subtracted
    - Data sets are averaged
    - Label is changed
- When tests are performed or removed
- When fits are performed or removed
- When simulations are performed or removed
- When editing or copying appearance settings

Keybindings
- Select plot (PgUp/PgDn)
- Select plot type (Alt+PgUp/PgDn)
"""


class PlottingTab:
    def __init__(self):
        self.tab: int = dpg.generate_uuid()
        self.resize_group: int = dpg.generate_uuid()
        #
        self.plot_combo: int = dpg.generate_uuid()
        self.label_input: int = dpg.generate_uuid()
        self.type_combo: int = dpg.generate_uuid()
        self.new_button: int = dpg.generate_uuid()
        self.remove_button: int = dpg.generate_uuid()
        #
        self.active_series_table: int = dpg.generate_uuid()
        #
        self.possible_series_group: int = dpg.generate_uuid()
        self.possible_datasets_header: int = dpg.generate_uuid()
        self.possible_tests_header: int = dpg.generate_uuid()
        self.possible_fits_header: int = dpg.generate_uuid()
        self.possible_simulations_header: int = dpg.generate_uuid()
        #
        self.select_all_button: int = dpg.generate_uuid()
        self.unselect_all_button: int = dpg.generate_uuid()
        self.copy_appearances_button: int = dpg.generate_uuid()
        #
        self.plots_group: int = dpg.generate_uuid()
        self.plot_types: Dict[PlotType, int] = {}
        self.plot_datas: Dict[PlotType, dict] = {}
        self.copy_csv_button: int = dpg.generate_uuid()
        #
        self._assemble()

    def _assemble(self):
        label_pad: int = 5
        sidebar_width: int = 400
        with dpg.tab(label="Plotting", tag=self.tab):
            with dpg.group(horizontal=True, tag=self.resize_group):
                with dpg.group():
                    with dpg.child_window(width=sidebar_width, height=82):
                        with dpg.group(horizontal=True):
                            dpg.add_text("Plot".rjust(label_pad))
                            dpg.add_combo(width=-64, tag=self.plot_combo)
                            dpg.add_button(label="New", width=-1, tag=self.new_button)
                            attach_tooltip(tooltips.plotting_create)
                        with dpg.group(horizontal=True):
                            dpg.add_text("Label".rjust(label_pad))
                            dpg.add_input_text(
                                width=-64, on_enter=True, tag=self.label_input
                            )
                            dpg.add_button(
                                label="Delete", width=-1, tag=self.remove_button
                            )
                            attach_tooltip(tooltips.plotting_remove)
                        with dpg.group(horizontal=True):
                            dpg.add_text("Type".rjust(label_pad))
                            dpg.add_combo(width=-64, tag=self.type_combo)
                    with dpg.child_window(width=sidebar_width, height=-40):
                        dpg.add_table(
                            borders_outerV=True,
                            borders_outerH=True,
                            borders_innerV=True,
                            borders_innerH=True,
                            scrollY=True,
                            freeze_rows=1,
                            width=-1,
                            height=41,
                            tag=self.active_series_table,
                        )
                        dpg.add_spacer(height=8)
                        with dpg.group(horizontal=True):
                            dpg.add_text("Filter")
                            attach_tooltip(tooltips.plotting_filter)
                            dpg.add_input_text(
                                width=-1,
                                callback=self.filter_possible_series,
                            )
                        with dpg.group(tag=self.possible_series_group):
                            dpg.add_collapsing_header(
                                label="Data sets",
                                tag=self.possible_datasets_header,
                            )
                            with dpg.collapsing_header(
                                label="Kramers-Kronig tests",
                                tag=self.possible_tests_header,
                            ):
                                with dpg.group(horizontal=True, indent=8):
                                    dpg.add_button(
                                        label="Expand all",
                                        callback=lambda s, a, u: self.expand_subheaders(
                                            u, True
                                        ),
                                        user_data=self.possible_tests_header,
                                    )
                                    dpg.add_button(
                                        label="Collapse all",
                                        callback=lambda s, a, u: self.expand_subheaders(
                                            u, False
                                        ),
                                        user_data=self.possible_tests_header,
                                    )
                            with dpg.collapsing_header(
                                label="Fitted equivalent circuits",
                                tag=self.possible_fits_header,
                            ):
                                with dpg.group(horizontal=True, indent=8):
                                    dpg.add_button(
                                        label="Expand all",
                                        callback=lambda s, a, u: self.expand_subheaders(
                                            u, True
                                        ),
                                        user_data=self.possible_fits_header,
                                    )
                                    dpg.add_button(
                                        label="Collapse all",
                                        callback=lambda s, a, u: self.expand_subheaders(
                                            u, False
                                        ),
                                        user_data=self.possible_fits_header,
                                    )
                            dpg.add_collapsing_header(
                                label="Simulated spectra",
                                tag=self.possible_simulations_header,
                            )
                    with dpg.child_window(width=sidebar_width, height=-1):
                        with dpg.group(horizontal=True):
                            dpg.add_button(
                                label="Select all",
                                user_data=True,
                                tag=self.select_all_button,
                            )
                            attach_tooltip(tooltips.plotting_select_all)
                            dpg.add_button(
                                label="Unselect all",
                                user_data=False,
                                tag=self.unselect_all_button,
                            )
                            attach_tooltip(tooltips.plotting_unselect_all)
                            dpg.add_button(
                                label="Copy appearance settings",
                                tag=self.copy_appearances_button,
                            )
                            attach_tooltip(tooltips.plotting_copy_appearance)
                with dpg.child_window(border=False, width=-1, height=-1):
                    with dpg.group(tag=self.plots_group):
                        # Nyquist
                        parent: int
                        with dpg.plot(
                            label=plot_type_to_label[PlotType.NYQUIST],
                            equal_aspects=True,
                            anti_aliased=True,
                            crosshairs=True,
                            width=-1,
                            height=-24,
                        ) as parent:
                            dpg.bind_item_theme(parent, themes.plot_theme)
                            self.plot_types[PlotType.NYQUIST] = parent
                            dpg.add_plot_legend(
                                location=dpg.mvPlot_Location_NorthEast,
                            )
                            dpg.add_plot_axis(dpg.mvXAxis, label="Z' (ohm)")
                            dpg.add_plot_axis(dpg.mvYAxis, label='-Z" (ohm)')
                        # Bode - magnitude
                        with dpg.plot(
                            label=plot_type_to_label[PlotType.BODE_MAGNITUDE],
                            anti_aliased=True,
                            crosshairs=True,
                            width=-1,
                            height=-24,
                        ) as parent:
                            dpg.bind_item_theme(parent, themes.plot_theme)
                            self.plot_types[PlotType.BODE_MAGNITUDE] = parent
                            dpg.add_plot_legend(
                                location=dpg.mvPlot_Location_NorthEast,
                            )
                            dpg.add_plot_axis(dpg.mvXAxis, label="log f")
                            dpg.add_plot_axis(dpg.mvYAxis, label="log |Z|")
                        # Bode - phase
                        with dpg.plot(
                            label=plot_type_to_label[PlotType.BODE_PHASE],
                            anti_aliased=True,
                            crosshairs=True,
                            width=-1,
                            height=-24,
                        ) as parent:
                            dpg.bind_item_theme(parent, themes.plot_theme)
                            self.plot_types[PlotType.BODE_PHASE] = parent
                            dpg.add_plot_legend(
                                location=dpg.mvPlot_Location_NorthEast,
                            )
                            dpg.add_plot_axis(dpg.mvXAxis, label="log f", parent=parent)
                            dpg.add_plot_axis(
                                dpg.mvYAxis, label="-phi (deg.)", parent=parent
                            )
                        #
                        dpg.show_item(list(self.plot_types.values())[0])
                        dpg.configure_item(
                            self.type_combo,
                            items=list(
                                sorted(
                                    map(
                                        lambda _: plot_type_to_label[_],
                                        self.plot_types.keys(),
                                    )
                                )
                            ),
                            default_value=plot_type_to_label[PlotType.NYQUIST],
                            user_data=PlotType.NYQUIST,
                        )
                        with dpg.group(horizontal=True):
                            dpg.add_button(
                                label="Copy as CSV", tag=self.copy_csv_button
                            )
                            attach_tooltip(tooltips.copy_plot_data_as_csv)

    def resize(self):
        # Other tabs have this method, which is called e.g. when navigating to a tab via
        # keybindings.
        return

    def expand_subheaders(self, header: int, state: bool):
        assert type(header) is int
        assert type(state) is bool
        for subheader in dpg.get_item_children(header, slot=1):
            if "::mvGroup" in dpg.get_item_type(subheader):
                continue
            dpg.set_value(subheader, state)

    def filter_possible_series(self, sender: int, string: str):
        string = string.lower()
        num_visible_items: int
        headers: List[int] = []
        subheaders: Dict[int, List[int]] = {}
        tables: Dict[int, List[int]] = {}
        rows: Dict[int, List[int]] = {}
        header: int
        for header in dpg.get_item_children(self.possible_series_group, slot=1):
            headers.append(header)
            group_or_subheader: int
            for group_or_subheader in dpg.get_item_children(header, slot=1):
                item_type: str = dpg.get_item_type(group_or_subheader)
                if "::mvGroup" in item_type:
                    table: int
                    for table in dpg.get_item_children(group_or_subheader, slot=1):
                        if "::mvTable" in dpg.get_item_type(table):
                            if header not in tables:
                                tables[header] = []
                            tables[header].append(table)
                            rows[table] = dpg.get_item_children(table, slot=1)
                elif "::mvCollapsingHeader" in item_type:
                    subheader: int
                    for group in dpg.get_item_children(group_or_subheader, slot=1):
                        if "::mvCollapsingHeader" in dpg.get_item_type(
                            group_or_subheader
                        ):
                            if header not in subheaders:
                                subheaders[header] = []
                            subheaders[header].append(group_or_subheader)
                            table_or_group: int
                            for table in dpg.get_item_children(group, slot=1):
                                item_type = dpg.get_item_type(table)
                                if "::mvTable" in item_type:
                                    if group_or_subheader not in tables:
                                        tables[group_or_subheader] = []
                                    tables[group_or_subheader].append(table)
                                    rows[table] = dpg.get_item_children(table, slot=1)
        if string.strip() == "":
            for header in headers:
                if header in subheaders:
                    num_visible_subheaders = 0
                    for subheader in subheaders[header]:
                        num_visible_items = 0
                        if subheader in tables:
                            for table in tables[subheader]:
                                dpg.set_value(table, string)
                                num_visible_items += len(rows[table])
                        if num_visible_items == 0:
                            dpg.hide_item(subheader)
                        else:
                            num_visible_subheaders += 1
                            dpg.show_item(subheader)
                    if num_visible_subheaders == 0:
                        dpg.hide_item(header)
                    else:
                        dpg.show_item(header)
                elif header in tables:
                    num_visible_items = 0
                    for table in tables[header]:
                        dpg.set_value(table, string)
                        num_visible_items += len(rows[table])
                    if num_visible_items == 0:
                        dpg.hide_item(header)
                    else:
                        dpg.show_item(header)
            return
        for header in headers:
            if header in subheaders:
                assert header not in tables
                num_visible_subheaders = 0
                for subheader in subheaders[header]:
                    assert subheader in tables and len(tables[subheader]) == 1
                    for table in tables[subheader]:
                        dpg.set_value(table, string)
                        num_visible_items = sum(
                            map(
                                lambda _: 1
                                if string in dpg.get_item_filter_key(_)
                                else 0,
                                rows[table],
                            )
                        )
                        if num_visible_items == 0:
                            dpg.hide_item(subheader)
                        else:
                            dpg.show_item(subheader)
                            num_visible_subheaders += 1
                if num_visible_subheaders == 0:
                    dpg.hide_item(header)
                else:
                    dpg.show_item(header)
            else:
                assert header in tables and len(tables[header]) == 1
                for table in tables[header]:
                    dpg.set_value(table, string)
                    num_visible_items = sum(
                        map(
                            lambda _: 1 if string in dpg.get_item_filter_key(_) else 0,
                            rows[table],
                        )
                    )
                    if num_visible_items == 0:
                        dpg.hide_item(header)
                    else:
                        dpg.show_item(header)

    def is_visible(self) -> bool:
        return dpg.is_item_visible(self.plot_combo)

    def populate_plot_combo(self, plots: List[PlotSettings]):
        assert (
            type(plots) is list
            and len(plots) > 0
            and all(map(lambda _: type(_) is PlotSettings, plots))
        )
        dpg.configure_item(
            self.plot_combo, items=list(map(lambda _: _.get_label(), plots))
        )

    def select_plot(
        self,
        plot: PlotSettings,
    ):
        assert type(plot) is PlotSettings
        dpg.set_item_user_data(self.plot_combo, plot)
        dpg.set_value(self.plot_combo, plot.get_label())

        def update_checkboxes(parent: int):
            if "::mvTableRow" not in dpg.get_item_type(parent):
                item: int
                for item in dpg.get_item_children(parent, slot=1):
                    update_checkboxes(item)
            else:
                cell: int
                for cell in dpg.get_item_children(parent, slot=1):
                    if "::mvCheckbox" not in dpg.get_item_type(cell):
                        continue
                    user_data = dpg.get_item_user_data(cell)
                    if hasattr(user_data, "uuid"):
                        dpg.set_value(cell, user_data.uuid in plot.series_order)
                        return

        dpg.set_value(self.label_input, plot.get_label())
        update_checkboxes(self.possible_series_group)
        self.select_plot_type(plot.plot_type)

    def get_plot(self) -> Optional[PlotSettings]:
        return dpg.get_item_user_data(self.plot_combo)

    def select_plot_type(self, plot_type: PlotType):
        assert type(plot_type) is PlotType
        dpg.set_item_user_data(self.type_combo, plot_type)
        dpg.set_value(self.type_combo, plot_type_to_label[plot_type])
        plot_tag: int
        for plot_tag in self.plot_types.values():
            dpg.hide_item(plot_tag)
        dpg.show_item(self.plot_types[plot_type])

    def get_plot_type(self) -> PlotType:
        return dpg.get_item_user_data(self.type_combo)

    def populate_active_series(
        self,
        plot: Optional[PlotSettings],
        datasets: List[DataSet],
        tests: Dict[str, List[TestResult]],
        fits: Dict[str, List[FitResult]],
        simulations: List[SimulationResult],
        label_callback: Optional[Callable],
        edit_callback: Optional[Callable],
        move_callback: Optional[Callable],
    ):
        dpg.delete_item(self.active_series_table, children_only=True)
        dpg.add_table_column(
            label="Type", width_fixed=True, parent=self.active_series_table
        )
        attach_tooltip("The type of data.")
        dpg.add_table_column(label="Label", parent=self.active_series_table)
        attach_tooltip(tooltips.plotting_label)
        dpg.add_table_column(
            label="Appearance", width_fixed=True, parent=self.active_series_table
        )
        attach_tooltip(tooltips.plotting_appearance)
        dpg.add_table_column(
            label="Position", width_fixed=True, parent=self.active_series_table
        )
        attach_tooltip(tooltips.plotting_position)
        if plot is None or len(plot.series_order) == 0:
            with dpg.table_row(parent=self.active_series_table):
                dpg.add_text()
                dpg.add_text()
                dpg.add_text()
                dpg.add_text()
            dpg.set_item_height(
                self.active_series_table,
                18 + 23 * 10,
            )
            return
        marker_lookup: Dict[int, str] = {v: k for k, v in themes.PLOT_MARKERS.items()}
        uuid: str
        for uuid in plot.series_order:
            typ: str = "?"
            typ_tooltip: str = "UNKNOWN"
            series: Optional[Union[DataSet, TestResult, FitResult, SimulationResult]]
            series = plot.find_series(uuid, datasets, tests, fits, simulations)
            if type(series) is DataSet:
                typ = "D"
                typ_tooltip = "Data set"
            elif type(series) is TestResult:
                typ = "KK"
                typ_tooltip = "Kramers-Kronig test"
            elif type(series) is FitResult:
                typ = "F"
                typ_tooltip = "Fit"
            elif type(series) is SimulationResult:
                typ = "S"
                typ_tooltip = "Simulation"
            else:
                continue
            with dpg.table_row(parent=self.active_series_table):
                dpg.add_text(typ.ljust(4))
                attach_tooltip(typ_tooltip)
                dpg.add_input_text(
                    hint=series.get_label(),
                    default_value=plot.get_series_label(uuid),
                    width=-1,
                    on_enter=True,
                    callback=label_callback,
                    user_data=uuid,
                )
                attach_tooltip(series.get_label())
                dpg.add_button(
                    label="Edit",
                    width=-1,
                    callback=edit_callback,
                    user_data=series,
                )
                with dpg.tooltip(parent=dpg.last_item()):
                    with dpg.group(horizontal=True):
                        dpg.add_text(" Color:")
                        dpg.add_color_edit(
                            default_value=plot.get_series_color(uuid),
                            enabled=False,
                            alpha_preview=dpg.mvColorEdit_AlphaPreviewHalf,
                            no_inputs=True,
                        )
                    dpg.add_text(
                        "Marker: "
                        + marker_lookup.get(plot.get_series_marker(uuid), "None")
                    )
                    dpg.add_text(
                        "  Line: " + ("Yes" if plot.get_series_line(uuid) else "No")
                    )
                with dpg.group(horizontal=True):
                    dpg.add_button(
                        label="U",
                        width=24,
                        callback=move_callback,
                        user_data=(
                            uuid,
                            -1,
                        ),
                    )
                    dpg.add_button(
                        label="D",
                        width=24,
                        callback=move_callback,
                        user_data=(
                            uuid,
                            1,
                        ),
                    )
        dpg.set_item_height(
            self.active_series_table,
            18
            + 23
            * ceil(
                len(dpg.get_item_children(self.active_series_table, slot=1)) / 10 + 0.1
            )
            * 10,
        )

    def update_plots(
        self,
        plot: PlotSettings,
        datasets: List[DataSet],
        tests: Dict[str, List[TestResult]],
        fits: Dict[str, List[FitResult]],
        simulations: List[SimulationResult],
        fit_to_data: Optional[bool] = None,
    ):
        assert type(fit_to_data) is bool or fit_to_data is None
        if fit_to_data is None:
            # If the plots were previously empty and now one or more series are being added,
            # then adjust the limits.
            fit_to_data = (
                len(
                    dpg.get_item_children(
                        dpg.get_item_children(
                            self.plot_types[PlotType.NYQUIST], slot=1
                        )[1],
                        slot=1,
                    )
                )
                == 0
            )
        # Clear the axes and previous data
        plot_type: PlotType
        for plot_type in self.plot_types:
            plot_tag: int = self.plot_types[plot_type]
            dpg.set_item_label(plot_tag, plot.get_label())
            axis: int
            for axis in dpg.get_item_children(plot_tag, slot=1):
                dpg.delete_item(axis, children_only=True)
            self.plot_datas[plot_type] = {}
        # Start plotting
        existing_series: List[
            Union[DataSet, TestResult, FitResult, SimulationResult]
        ] = []
        series: Optional[Union[DataSet, TestResult, FitResult, SimulationResult]]
        uuid: str
        for uuid in plot.series_order:
            series = plot.find_series(uuid, datasets, tests, fits, simulations)
            if series is None:
                plot.remove_series(uuid)
                continue
            existing_series.append(series)
        # Nyquist
        axes: List[int] = dpg.get_item_children(
            self.plot_types[PlotType.NYQUIST], slot=1
        )
        label: Optional[str]
        data_label: str
        show_line: bool
        x: ndarray
        y: ndarray
        for series in existing_series:
            uuid = series.uuid
            label = plot.get_series_label(uuid) or series.get_label()
            data_label = label
            if label.strip() == "":
                label = None
            show_line = plot.get_series_line(uuid)
            x, y = series.get_nyquist_data()
            if plot.get_series_marker(uuid) >= 0:
                scatter(
                    x,
                    y,
                    label if not show_line else None,
                    axes[1],
                    plot.themes[uuid],
                )
                self.plot_datas[PlotType.NYQUIST].update(
                    {
                        f"Zre (ohm) - {data_label} - scatter": x,
                        f"-Zim (ohm) - {data_label} - scatter": y,
                    }
                )
            if show_line:
                if type(series) is not DataSet:
                    x, y = series.get_nyquist_data(
                        num_per_decade=CONFIG.num_per_decade_in_simulated_lines
                    )
                line(
                    x,
                    y,
                    label,
                    axes[1],
                    plot.themes[uuid],
                )
                self.plot_datas[PlotType.NYQUIST].update(
                    {
                        f"Zre (ohm) - {data_label} - line": x,
                        f"-Zim (ohm) - {data_label} - line": y,
                    }
                )
        if fit_to_data:
            dpg.fit_axis_data(axes[0])
            dpg.fit_axis_data(axes[1])
        # Bode - magnitude
        axes = dpg.get_item_children(self.plot_types[PlotType.BODE_MAGNITUDE], slot=1)
        for series in existing_series:
            uuid = series.uuid
            label = plot.get_series_label(uuid) or series.get_label()
            data_label = label
            if label.strip() == "":
                label = None
            show_line = plot.get_series_line(uuid)
            x, y, _ = series.get_bode_data()
            if plot.get_series_marker(uuid) >= 0:
                scatter(
                    x,
                    y,
                    label if not show_line else None,
                    axes[1],
                    plot.themes[uuid],
                )
                self.plot_datas[PlotType.BODE_MAGNITUDE].update(
                    {
                        f"log f - {data_label} - scatter": x,
                        f"log |Z| - {data_label} - scatter": y,
                    }
                )
            if show_line:
                if type(series) is not DataSet:
                    x, y, _ = series.get_bode_data(
                        num_per_decade=CONFIG.num_per_decade_in_simulated_lines
                    )
                line(
                    x,
                    y,
                    label,
                    axes[1],
                    plot.themes[uuid],
                )
                self.plot_datas[PlotType.BODE_MAGNITUDE].update(
                    {
                        f"log f - {data_label} - line": x,
                        f"log |Z| - {data_label} - line": y,
                    }
                )
        if fit_to_data:
            dpg.fit_axis_data(axes[0])
            dpg.fit_axis_data(axes[1])
        # Bode - phase
        axes = dpg.get_item_children(self.plot_types[PlotType.BODE_PHASE], slot=1)
        for series in existing_series:
            uuid = series.uuid
            label = plot.get_series_label(uuid) or series.get_label()
            data_label = label
            if label.strip() == "":
                label = None
            show_line = plot.get_series_line(uuid)
            x, _, y = series.get_bode_data()
            if plot.get_series_marker(uuid) >= 0:
                scatter(
                    x,
                    y,
                    label if not show_line else None,
                    axes[1],
                    plot.themes[uuid],
                )
                self.plot_datas[PlotType.BODE_PHASE].update(
                    {
                        f"log f - {data_label} - scatter": x,
                        f"-phase (deg.) - {data_label} - scatter": y,
                    }
                )
            if show_line:
                if type(series) is not DataSet:
                    x, _, y = series.get_bode_data(
                        num_per_decade=CONFIG.num_per_decade_in_simulated_lines
                    )
                line(
                    x,
                    y,
                    label,
                    axes[1],
                    plot.themes[uuid],
                )
                self.plot_datas[PlotType.BODE_PHASE].update(
                    {
                        f"log f - {data_label} - line": x,
                        f"-phase (deg.) - {data_label} - line": y,
                    }
                )
        if fit_to_data:
            dpg.fit_axis_data(axes[0])
            dpg.fit_axis_data(axes[1])

    def populate_possible_series(
        self,
        plot: PlotSettings,
        datasets: List[DataSet],
        tests: Dict[str, List[TestResult]],
        fits: Dict[str, List[FitResult]],
        simulations: List[SimulationResult],
        toggle_callback: Callable,
        select_callback: Callable,
    ):
        assert type(datasets) is list
        assert type(tests) is dict
        assert type(fits) is dict
        assert type(simulations) is list
        self.populate_possible_datasets(
            plot, datasets, toggle_callback, select_callback
        )
        self.populate_possible_tests(
            plot, datasets, tests, toggle_callback, select_callback
        )
        self.populate_possible_fits(
            plot, datasets, fits, toggle_callback, select_callback
        )
        self.populate_possible_simulations(
            plot, simulations, toggle_callback, select_callback
        )

    def populate_possible_datasets(
        self,
        plot: PlotSettings,
        datasets: List[DataSet],
        toggle_callback: Callable,
        select_callback: Callable,
    ):
        dpg.delete_item(self.possible_datasets_header, children_only=True)
        with dpg.group(indent=8, parent=self.possible_datasets_header):
            with dpg.table(
                borders_outerV=True,
                borders_outerH=True,
                borders_innerV=True,
                borders_innerH=True,
                scrollY=True,
                freeze_rows=1,
                width=-1,
                height=18 + 23 * max(1, len(datasets)),
            ):
                dpg.add_table_column(label="", width_fixed=True)
                attach_tooltip(tooltips.plotting_dataset_checkbox)
                dpg.add_table_column(label="Label", width_fixed=True)
                attach_tooltip(tooltips.plotting_dataset_label)
                data: DataSet
                for data in datasets:
                    with dpg.table_row(filter_key=data.get_label().lower()):
                        dpg.add_checkbox(
                            default_value=data.uuid in plot.series_order,
                            callback=toggle_callback,
                            user_data=data,
                        )
                        dpg.add_text(data.get_label())
                        attach_tooltip(data.get_label())
            if len(datasets) > 0:
                with dpg.group(horizontal=True):
                    dpg.add_button(
                        label="Select all",
                        callback=lambda s, a, u: select_callback(u),
                        user_data=(True, datasets),
                    )
                    dpg.add_button(
                        label="Unselect all",
                        callback=lambda s, a, u: select_callback(u),
                        user_data=(False, datasets),
                    )
                dpg.add_spacer(height=8, parent=self.possible_datasets_header)
                dpg.show_item(self.possible_datasets_header)
            else:
                dpg.hide_item(self.possible_datasets_header)

    def populate_possible_tests(
        self,
        plot: PlotSettings,
        datasets: List[DataSet],
        tests: Dict[str, List[TestResult]],
        toggle_callback: Callable,
        select_callback: Callable,
    ):
        # Remove headers for data sets that no longer exist
        uuids: List[str] = list(map(lambda _: _.uuid, datasets))
        headers: Dict[str, int] = {}
        header: int
        for header in dpg.get_item_children(self.possible_tests_header, slot=1):
            if "::mvGroup" in dpg.get_item_type(header):
                continue
            uuid: Optional[str] = dpg.get_item_user_data(header)
            if uuid not in uuids:
                dpg.delete_item(header)
            else:
                headers[uuid] = header
        # Update or create headers for data sets that do exist
        num_visible_subheaders: int = 0
        data: DataSet
        for data in datasets:
            # TODO: Make sure that the subheaders are in alphabetical order even after adding or
            # renaming data sets.
            if data.uuid in headers:
                header = headers[data.uuid]
                dpg.set_item_label(header, data.get_label())
                dpg.delete_item(header, children_only=True)
            else:
                header = dpg.add_collapsing_header(
                    label=data.get_label(),
                    user_data=data.uuid,
                    indent=8,
                    parent=self.possible_tests_header,
                )
            with dpg.group(indent=8, parent=header):
                with dpg.table(
                    borders_outerV=True,
                    borders_outerH=True,
                    borders_innerV=True,
                    borders_innerH=True,
                    scrollY=True,
                    freeze_rows=1,
                    width=-1,
                    height=18 + 23 * max(1, len(tests.get(data.uuid, []))),
                ):
                    dpg.add_table_column(label="", width_fixed=True)
                    attach_tooltip(tooltips.plotting_test_checkbox)
                    dpg.add_table_column(label="Label", width_fixed=True)
                    test: TestResult
                    for test in tests.get(data.uuid, []):
                        with dpg.table_row(
                            filter_key=f"{data.get_label()} {test.get_label()}".lower()
                        ):
                            dpg.add_checkbox(
                                default_value=test.uuid in plot.series_order,
                                callback=toggle_callback,
                                user_data=test,
                            )
                            dpg.add_text(test.get_label())
                            attach_tooltip(test.get_label())
                if len(tests.get(data.uuid, [])) > 0:
                    with dpg.group(horizontal=True):
                        dpg.add_button(
                            label="Select all",
                            callback=lambda s, a, u: select_callback(u),
                            user_data=(True, tests.get(data.uuid, [])),
                        )
                        dpg.add_button(
                            label="Unselect all",
                            callback=lambda s, a, u: select_callback(u),
                            user_data=(False, tests.get(data.uuid, [])),
                        )
                    num_visible_subheaders += 1
                    dpg.show_item(header)
                else:
                    dpg.hide_item(header)
        if num_visible_subheaders > 0:
            dpg.add_spacer(height=8, parent=self.possible_tests_header)
            dpg.show_item(self.possible_tests_header)
        else:
            dpg.hide_item(self.possible_tests_header)

    def populate_possible_fits(
        self,
        plot: PlotSettings,
        datasets: List[DataSet],
        fits: Dict[str, List[FitResult]],
        toggle_callback: Callable,
        select_callback: Callable,
    ):
        # Remove headers for data sets that no longer exist
        uuids: List[str] = list(map(lambda _: _.uuid, datasets))
        headers: Dict[str, int] = {}
        header: int
        for header in dpg.get_item_children(self.possible_fits_header, slot=1):
            if "::mvGroup" in dpg.get_item_type(header):
                continue
            uuid: Optional[str] = dpg.get_item_user_data(header)
            if uuid not in uuids:
                dpg.delete_item(header)
            else:
                headers[uuid] = header
        # Update or create headers for data sets that do exist
        num_visible_subheaders: int = 0
        data: DataSet
        for data in datasets:
            if data.uuid in headers:
                header = headers[data.uuid]
                dpg.set_item_label(header, data.get_label())
                dpg.delete_item(header, children_only=True)
            else:
                header = dpg.add_collapsing_header(
                    label=data.get_label(),
                    user_data=data.uuid,
                    indent=8,
                    parent=self.possible_fits_header,
                )
            with dpg.group(indent=8, parent=header):
                with dpg.table(
                    borders_outerV=True,
                    borders_outerH=True,
                    borders_innerV=True,
                    borders_innerH=True,
                    scrollY=True,
                    freeze_rows=1,
                    width=-1,
                    height=18 + 23 * max(1, len(fits.get(data.uuid, []))),
                ):
                    dpg.add_table_column(label="", width_fixed=True)
                    attach_tooltip(tooltips.plotting_fit_checkbox)
                    dpg.add_table_column(label="Label", width_fixed=True)
                    fit: FitResult
                    for fit in fits.get(data.uuid, []):
                        with dpg.table_row(
                            filter_key=f"{data.get_label()} {fit.get_label()}".lower()
                        ):
                            dpg.add_checkbox(
                                default_value=fit.uuid in plot.series_order,
                                callback=toggle_callback,
                                user_data=fit,
                            )
                            dpg.add_text(fit.get_label())
                            attach_tooltip(fit.get_label())
                if len(fits.get(data.uuid, [])) > 0:
                    with dpg.group(horizontal=True):
                        dpg.add_button(
                            label="Select all",
                            callback=lambda s, a, u: select_callback(u),
                            user_data=(True, fits.get(data.uuid, [])),
                        )
                        dpg.add_button(
                            label="Unselect all",
                            callback=lambda s, a, u: select_callback(u),
                            user_data=(False, fits.get(data.uuid, [])),
                        )
                    num_visible_subheaders += 1
                    dpg.show_item(header)
                else:
                    dpg.hide_item(header)
        if num_visible_subheaders > 0:
            dpg.add_spacer(height=8, parent=self.possible_fits_header)
            dpg.show_item(self.possible_fits_header)
        else:
            dpg.hide_item(self.possible_fits_header)

    def populate_possible_simulations(
        self,
        plot: PlotSettings,
        simulations: List[SimulationResult],
        toggle_callback: Callable,
        select_callback: Callable,
    ):
        dpg.delete_item(self.possible_simulations_header, children_only=True)
        with dpg.group(indent=8, parent=self.possible_simulations_header):
            with dpg.table(
                borders_outerV=True,
                borders_outerH=True,
                borders_innerV=True,
                borders_innerH=True,
                scrollY=True,
                freeze_rows=1,
                width=-1,
                height=18 + 23 * max(1, len(simulations)),
            ):
                dpg.add_table_column(label="", width_fixed=True)
                attach_tooltip(tooltips.plotting_simulation_checkbox)
                dpg.add_table_column(label="Label", width_fixed=True)
                sim: SimulationResult
                for sim in simulations:
                    with dpg.table_row(filter_key=sim.get_label().lower()):
                        dpg.add_checkbox(
                            default_value=sim.uuid in plot.series_order,
                            callback=toggle_callback,
                            user_data=sim,
                        )
                        dpg.add_text(sim.get_label())
                        attach_tooltip(sim.get_label())
            if len(simulations) > 0:
                with dpg.group(horizontal=True):
                    dpg.add_button(
                        label="Select all",
                        callback=lambda s, a, u: select_callback(u),
                        user_data=(True, simulations),
                    )
                    dpg.add_button(
                        label="Unselect all",
                        callback=lambda s, a, u: select_callback(u),
                        user_data=(False, simulations),
                    )
                dpg.add_spacer(height=8, parent=self.possible_simulations_header)
                dpg.show_item(self.possible_simulations_header)
            else:
                dpg.hide_item(self.possible_simulations_header)

    def get_data(self) -> dict:
        return self.plot_datas[self.get_plot_type()]


if __name__ == "__main__":
    dpg.create_context()
    dpg.create_viewport(title="Plotting tab")
    dpg.setup_dearpygui()
    dpg.show_viewport()
    window: int
    with dpg.window() as window:
        with dpg.tab_bar():
            PlottingTab()
    dpg.set_primary_window(window, True)
    dpg.start_dearpygui()
    dpg.destroy_context()
