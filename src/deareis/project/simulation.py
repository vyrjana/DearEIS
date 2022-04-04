# Copyright 2022 DearEIS developers
# DearEIS is licensed under the GPLv3 or later (https://www.gnu.org/licenses/gpl-3.0.html).
# The licenses of DearEIS' dependencies and/or sources of portions of code are included in
# the LICENSES folder.

from pyimpspec import DataSet
from typing import Dict, List, Optional, Tuple, Union
import dearpygui.dearpygui as dpg
from pyimpspec import FittedParameter, Element
from numpy import floor, logspace
from deareis.utility import attach_tooltip, number_formatter, align_numbers
import deareis.tooltips as tooltips
from deareis.project.circuit_editor import CircuitEditor, CircuitPreview
from deareis.plot import (
    BodePlot,
    NyquistPlot,
)
from deareis.data.simulation import (
    SimulationResult,
    SimulationSettings,
)
from deareis.data.shared import (
    Output,
    label_to_output,
    output_to_label,
)
from deareis.config import CONFIG

# TODO: Argument type assertions


class SimulationTab:
    def __init__(self):
        self.tab: int = dpg.generate_uuid()
        self.resize_group: int = dpg.generate_uuid()
        # Settings
        self.cdc_input: int = dpg.generate_uuid()
        self.editor_button: int = dpg.generate_uuid()
        self.min_freq_input: int = dpg.generate_uuid()
        self.max_freq_input: int = dpg.generate_uuid()
        self.per_decade_input: int = dpg.generate_uuid()
        self.perform_sim_button: int = dpg.generate_uuid()
        # Parameters and used settings
        self.sidebar_window: int = dpg.generate_uuid()
        self.dataset_combo: int = dpg.generate_uuid()
        self.result_combo: int = dpg.generate_uuid()
        self.delete_result_button: int = dpg.generate_uuid()
        self.results_window: int = dpg.generate_uuid()
        self.statistics_table: int = dpg.generate_uuid()
        self.settings_table: int = dpg.generate_uuid()
        self.apply_settings_button: int = dpg.generate_uuid()
        # Plots window
        self.plots_window: int = dpg.generate_uuid()
        self.cdc_text: int = dpg.generate_uuid()
        self.parameters_table: int = dpg.generate_uuid()
        self.output_combo: int = dpg.generate_uuid()
        self.copy_output_button: int = dpg.generate_uuid()
        self.circuit_preview_node_editor: int = dpg.generate_uuid()
        self.nyquist_plot: NyquistPlot = None
        self.bode_plot_horizontal: BodePlot = None
        self.bode_plot_vertical: BodePlot = None
        self.horizontal_bode_group: int = dpg.generate_uuid()
        self.vertical_bode_group: int = dpg.generate_uuid()
        self.enlarge_nyquist_button: int = dpg.generate_uuid()
        self.enlarge_bode_horizontal_button: int = dpg.generate_uuid()
        self.enlarge_bode_vertical_button: int = dpg.generate_uuid()
        self.enlarge_residuals_button: int = dpg.generate_uuid()
        #
        self._assemble()
        self._assign_handlers()

    def to_dict(self) -> dict:
        return {
            "cdc": dpg.get_value(self.cdc_input),
            "min_freq": dpg.get_value(self.min_freq_input),
            "max_freq": dpg.get_value(self.max_freq_input),
            "num_per_decade": dpg.get_value(self.per_decade_input),
            "output": dpg.get_value(self.output_combo),
        }

    def restore_state(self, state: dict):
        dpg.set_value(self.cdc_input, state["cdc"])
        dpg.get_item_callback(self.cdc_input)(self.cdc_input, state["cdc"])
        dpg.set_value(self.min_freq_input, state["min_freq"])
        dpg.set_value(self.max_freq_input, state["max_freq"])
        dpg.set_value(self.per_decade_input, state["num_per_decade"])
        dpg.set_value(self.output_combo, state["output"])

    def _assemble(self):
        sidebar_width: int = 350
        settings_height: int = 128
        label_pad: int = 22
        with dpg.tab(label="Simulation", tag=self.tab):
            with dpg.group(horizontal=True, tag=self.resize_group):
                with dpg.child_window(
                    border=False,
                    width=sidebar_width,
                    tag=self.sidebar_window,
                ):
                    # Settings
                    with dpg.child_window(
                        border=True, width=-1, height=settings_height
                    ):
                        with dpg.group(horizontal=True):
                            dpg.add_text("Circuit".rjust(label_pad))
                            attach_tooltip(tooltips.simulation_cdc)
                            dpg.add_input_text(
                                width=-50,
                                tag=self.cdc_input,
                                on_enter=True,
                            )
                            dpg.add_button(
                                label="Edit",
                                width=-1,
                                tag=self.editor_button,
                            )
                            attach_tooltip(tooltips.open_circuit_editor)
                        with dpg.group(horizontal=True):
                            dpg.add_text("Maximum frequency".rjust(label_pad))
                            attach_tooltip(tooltips.simulation_max_freq)
                            dpg.add_input_float(
                                label="Hz",
                                default_value=1e5,
                                min_value=1e-20,
                                max_value=1e20,
                                min_clamped=True,
                                max_clamped=True,
                                on_enter=True,
                                format="%.3E",
                                step=0.0,
                                width=-18,
                                tag=self.max_freq_input,
                            )
                        with dpg.group(horizontal=True):
                            dpg.add_text("Minimum frequency".rjust(label_pad))
                            attach_tooltip(tooltips.simulation_min_freq)
                            dpg.add_input_float(
                                label="Hz",
                                default_value=1e-2,
                                min_value=1e-20,
                                max_value=1e20,
                                min_clamped=True,
                                max_clamped=True,
                                on_enter=True,
                                format="%.3E",
                                step=0.0,
                                width=-18,
                                tag=self.min_freq_input,
                            )
                        with dpg.group(horizontal=True):
                            dpg.add_text("Num. points per decade".rjust(label_pad))
                            attach_tooltip(tooltips.simulation_per_decade)
                            dpg.add_input_int(
                                default_value=10,
                                min_value=1,
                                min_clamped=True,
                                step=0,
                                on_enter=True,
                                tag=self.per_decade_input,
                                width=-1,
                            )
                        with dpg.group(horizontal=True):
                            dpg.add_text("".rjust(label_pad))
                            dpg.add_button(
                                label="Perform simulation",
                                width=-1,
                                tag=self.perform_sim_button,
                            )
                    with dpg.child_window(width=-1, height=82):
                        label_pad = 8
                        with dpg.group(horizontal=True):
                            dpg.add_text("Data set".rjust(label_pad))
                            dpg.add_combo(
                                width=-60,
                                tag=self.dataset_combo,
                            )
                        with dpg.group(horizontal=True):
                            dpg.add_text("Result".rjust(label_pad))
                            dpg.add_combo(
                                width=-60,
                                tag=self.result_combo,
                            )
                            dpg.add_button(
                                label="Delete",
                                width=-1,
                                tag=self.delete_result_button,
                            )
                            attach_tooltip(tooltips.simulation_remove)
                        with dpg.group(horizontal=True):
                            dpg.add_text("Output".rjust(label_pad))
                            dpg.add_combo(
                                items=list(label_to_output.keys()),
                                default_value=list(label_to_output.keys())[0],
                                tag=self.output_combo,
                                width=-60,
                            )
                            dpg.add_button(
                                label="Copy",
                                width=-1,
                                tag=self.copy_output_button,
                            )
                            attach_tooltip(tooltips.copy_output)
                    with dpg.child_window(width=-1, height=-1):
                        with dpg.collapsing_header(label=" Parameters", leaf=True):
                            dpg.add_table(
                                borders_outerV=True,
                                borders_outerH=True,
                                borders_innerV=True,
                                borders_innerH=True,
                                scrollY=True,
                                freeze_rows=1,
                                height=18,
                                tag=self.parameters_table,
                            )
                        dpg.add_spacer(height=8)
                        with dpg.collapsing_header(label=" Settings", leaf=True):
                            dpg.add_table(
                                borders_outerV=True,
                                borders_outerH=True,
                                borders_innerV=True,
                                borders_innerH=True,
                                scrollY=True,
                                freeze_rows=1,
                                height=202,
                                tag=self.settings_table,
                            )
                            dpg.add_button(
                                label="Apply settings",
                                tag=self.apply_settings_button,
                            )
                            attach_tooltip(tooltips.apply_settings)
                with dpg.child_window(
                    border=False,
                    width=-1,
                    height=-1,
                    tag=self.plots_window,
                ):
                    with dpg.group(horizontal=True):
                        with dpg.child_window(border=False, width=-1, height=250):
                            dpg.add_node_editor(tag=self.circuit_preview_node_editor)
                    with dpg.group(horizontal=True):
                        with dpg.group():
                            self.nyquist_plot = NyquistPlot(
                                dpg.add_plot(
                                    width=400,
                                    height=400,
                                    equal_aspects=True,
                                    anti_aliased=True,
                                )
                            )
                            with dpg.group(horizontal=True):
                                dpg.add_button(
                                    label="Enlarge Nyquist",
                                    user_data=self.nyquist_plot,
                                    tag=self.enlarge_nyquist_button,
                                )
                                dpg.add_button(
                                    label="Copy as CSV",
                                    callback=self.nyquist_plot.copy_data,
                                )
                                attach_tooltip(tooltips.copy_plot_data_as_csv)
                        with dpg.group(tag=self.horizontal_bode_group):
                            self.bode_plot_horizontal = BodePlot(
                                dpg.add_plot(
                                    width=400,
                                    height=400,
                                    anti_aliased=True,
                                )
                            )
                            with dpg.group(horizontal=True):
                                dpg.add_button(
                                    label="Enlarge Bode",
                                    user_data=self.bode_plot_horizontal,
                                    tag=self.enlarge_bode_horizontal_button,
                                )
                                dpg.add_button(
                                    label="Copy as CSV",
                                    callback=self.bode_plot_horizontal.copy_data,
                                )
                                attach_tooltip(tooltips.copy_plot_data_as_csv)
                    with dpg.group(tag=self.vertical_bode_group, show=False):
                        self.bode_plot_vertical = BodePlot(
                            dpg.add_plot(
                                width=400,
                                height=400,
                                anti_aliased=True,
                            )
                        )
                        with dpg.group(horizontal=True):
                            dpg.add_button(
                                label="Enlarge Bode",
                                user_data=self.bode_plot_vertical,
                                tag=self.enlarge_bode_vertical_button,
                            )
                            dpg.add_button(
                                label="Copy as CSV",
                                callback=self.bode_plot_vertical.copy_data,
                            )
                            attach_tooltip(tooltips.copy_plot_data_as_csv)

    def _assign_handlers(self):
        group_handler: int
        with dpg.item_handler_registry() as group_handler:
            dpg.add_item_resize_handler(callback=self.resize)
        dpg.bind_item_handler_registry(self.resize_group, group_handler)

        tab_handler: int
        with dpg.item_handler_registry() as tab_handler:
            dpg.add_item_clicked_handler(callback=self.resize)
        dpg.bind_item_handler_registry(self.tab, tab_handler)

    def resize(self):
        dpg.split_frame(delay=100)
        viewport_width: int = dpg.get_viewport_width()
        viewport_height: int = dpg.get_viewport_height()
        aspect_ratio: float = (
            viewport_width / viewport_height if viewport_height > 0 else 1.0
        )
        total_width: int
        total_height: int
        total_width, total_height = dpg.get_item_rect_size(self.resize_group)
        sidebar_width: int
        sidebar_height: int
        sidebar_width, sidebar_height = dpg.get_item_rect_size(self.sidebar_window)
        editor_width: int
        editor_height: int
        editor_width, editor_height = dpg.get_item_rect_size(
            self.circuit_preview_node_editor
        )
        editor_width = int(floor(editor_width))
        editor_height = int(floor(editor_height))
        sidebar_height -= 5 + 16
        plot_width: int = editor_width
        plot_height: int = editor_height
        if aspect_ratio > 1.5 and total_width - sidebar_width > 250:
            if dpg.is_item_shown(self.vertical_bode_group):
                dpg.hide_item(self.vertical_bode_group)
                dpg.show_item(self.horizontal_bode_group)
            plot_width = int(round(((total_width - sidebar_width - 16)) / 2))
            plot_height = int(sidebar_height - editor_height - 8)
            self.nyquist_plot.resize(plot_width, plot_height)
            self.bode_plot_horizontal.resize(plot_width, plot_height)
            self.bode_plot_horizontal.adjust_limits()
        else:
            if dpg.is_item_shown(self.horizontal_bode_group):
                dpg.hide_item(self.horizontal_bode_group)
                dpg.show_item(self.vertical_bode_group)
            if total_height > 3 * editor_height:
                plot_height = int(floor((total_height - editor_height) / 2) - 2 * 15)
            self.nyquist_plot.resize(plot_width, plot_height)
            self.bode_plot_vertical.resize(plot_width, plot_height)
            self.bode_plot_vertical.adjust_limits()
        self.nyquist_plot.adjust_limits()

    def is_visible(self) -> bool:
        return dpg.is_item_visible(self.cdc_input)

    def is_input_active(self) -> bool:
        return dpg.is_item_active(self.cdc_input)

    def populate_dataset_combo(self, labels: List[str]):
        assert type(labels) is list and all(list(map(lambda _: type(_) is str, labels)))
        labels.insert(0, "None")
        dpg.configure_item(self.dataset_combo, items=labels)
        if dpg.get_value(self.dataset_combo) not in labels:
            dpg.set_value(self.dataset_combo, labels[0])

    def populate_result_combo(self, labels: List[str], default: str = ""):
        assert type(labels) is list and all(list(map(lambda _: type(_) is str, labels)))
        assert type(default) is str
        if default == "" and len(labels) > 0:
            default = labels[0]
        dpg.configure_item(self.result_combo, items=labels, default_value=default)

    def select_dataset(
        self, data: Optional[DataSet], result: Optional[SimulationResult]
    ):
        assert type(data) is DataSet or data is None
        assert type(result) is SimulationResult or result is None
        self.select_result(data, result)

    def get_dataset(self) -> Optional[DataSet]:
        if not dpg.does_item_exist(self.dataset_combo):
            return None
        return dpg.get_item_user_data(self.dataset_combo)

    def get_dataset_label(self) -> str:
        return dpg.get_value(self.dataset_combo)

    def get_result(self) -> Optional[SimulationResult]:
        if not dpg.does_item_exist(self.result_combo):
            return None
        return dpg.get_item_user_data(self.result_combo)

    def select_result(
        self, data: Optional[DataSet], result: Optional[SimulationResult]
    ):
        assert type(data) is DataSet or data is None
        assert type(result) is SimulationResult or result is None
        dpg.set_item_user_data(self.dataset_combo, data)
        dpg.set_item_user_data(self.result_combo, result)
        dpg.set_item_user_data(self.delete_result_button, result)
        dpg.set_item_user_data(self.apply_settings_button, result)
        dpg.set_item_user_data(self.copy_output_button, result)
        dpg.set_value(
            self.result_combo, result.get_label() if result is not None else ""
        )
        dpg.set_value(
            self.dataset_combo, data.get_label() if data is not None else "None"
        )
        self.populate_tables(result)
        self.preview_circuit(result)
        self.plot(data, result)

    def populate_tables(self, result: Optional[SimulationResult]):
        header_height: int = 18
        row_height: int = 23
        label_pad: int = 23
        dpg.delete_item(self.settings_table, children_only=True)
        dpg.add_table_column(
            parent=self.settings_table, label="Label".rjust(label_pad), width_fixed=True
        )
        dpg.add_table_column(
            parent=self.settings_table, label="Value", width_fixed=True
        )
        dpg.delete_item(self.parameters_table, children_only=True)
        dpg.add_table_column(
            parent=self.parameters_table,
            label="Element",
            width_fixed=True,
        )
        attach_tooltip(tooltips.simulation_element)
        dpg.add_table_column(
            parent=self.parameters_table,
            label="Parameter",
            width_fixed=True,
        )
        attach_tooltip(tooltips.simulation_parameter)
        dpg.add_table_column(
            parent=self.parameters_table,
            label="Value",
        )
        attach_tooltip(tooltips.simulation_parameter_value)
        cdc: str = result.settings.cdc if result is not None else ""
        while "{" in cdc:
            i: int = cdc.find("{")
            j: int = cdc.find("}")
            cdc = cdc.replace(cdc[i : j + 1], "")
        freqs: List[str] = align_numbers(
            [
                number_formatter(result.settings.max_frequency, decimals=3, width=9)
                if result is not None
                else "",
                number_formatter(result.settings.min_frequency, decimals=3, width=9)
                if result is not None
                else "",
            ]
        )
        settings: List[Tuple[str, str, str]] = [
            (
                "Circuit",
                cdc,
                tooltips.fitting_cdc,
            ),
            (
                "Maximum frequency",
                freqs[0] + (" Hz" if freqs[0].strip() != "" else ""),
                tooltips.simulation_max_freq,
            ),
            (
                "Minimum frequency",
                freqs[1] + (" Hz" if freqs[1].strip() != "" else ""),
                tooltips.simulation_min_freq,
            ),
            (
                "Num. points per decade",
                str(result.settings.num_freq_per_dec) if result is not None else "",
                tooltips.simulation_per_decade,
            ),
        ]
        max_label_len: int = max(map(lambda _: len(_[0]), settings))
        assert max_label_len <= label_pad, (
            max_label_len,
            label_pad,
        )
        label: str
        value: str
        tooltip: str
        for (label, value, tooltip) in settings:
            with dpg.table_row(parent=self.settings_table):
                dpg.add_text(label.rjust(label_pad))
                attach_tooltip(tooltip)
                dpg.add_text(value)
                attach_tooltip(value.strip())
        dpg.set_item_height(
            self.settings_table, header_height + len(settings) * row_height
        )
        element_labels: List[str] = []
        element_tooltips: List[str] = []
        parameter_labels: List[str] = []
        values: List[str] = []
        value_tooltips: List[str] = []
        if result is not None:
            element_label: str
            element_tooltip: str
            parameter_label: str
            value: Union[str, float]
            value_tooltip: str
            element: Element
            for element in result.circuit.get_elements():
                for parameter_label, value in element.get_parameters().items():
                    element_labels.append(element.get_label())
                    element_tooltips.append(element.get_extended_description())
                    parameter_labels.append(parameter_label)
                    values.append(f"{number_formatter(value, width=9, significants=3)}")
                    value_tooltips.append(
                        f"{number_formatter(value, decimals=6).strip()}"
                    )
            values = align_numbers(values)
            for (
                element_label,
                element_tooltip,
                parameter_label,
                value,
                value_tooltip,
            ) in zip(
                element_labels,
                element_tooltips,
                parameter_labels,
                values,
                value_tooltips,
            ):
                with dpg.table_row(parent=self.parameters_table):
                    dpg.add_text(element_label.ljust(10))
                    if element_tooltip != "":
                        attach_tooltip(element_tooltip)
                    dpg.add_text(parameter_label.ljust(11))
                    dpg.add_text(value.ljust(10))
                    attach_tooltip(value_tooltip)
        else:
            with dpg.table_row(parent=self.parameters_table):
                dpg.add_text("".ljust(10))
                dpg.add_text("".ljust(11))
                dpg.add_text("".ljust(10))
        dpg.set_item_height(
            self.parameters_table, header_height + max(len(values), 1) * row_height
        )

    def plot(self, data: Optional[DataSet], result: Optional[SimulationResult]):
        self.nyquist_plot.clear_plot()
        self.bode_plot_horizontal.clear_plot()
        self.bode_plot_vertical.clear_plot()
        before: Union[int, Tuple[int, int]] = -1
        if result is not None:
            before = self.nyquist_plot.plot_smooth(
                *result.get_nyquist_data(
                    num_per_decade=CONFIG.num_per_decade_in_simulated_lines
                ),
                True,
            )
            before = self.nyquist_plot.plot_sim(
                *result.get_nyquist_data(),
                True,
                before,
            )
        if data is not None:
            self.nyquist_plot.plot_data(
                *data.get_nyquist_data(),
                before,
                True,
            )
        before = (
            -1,
            -1,
        )
        if result is not None:
            before = self.bode_plot_horizontal.plot_smooth(
                *result.get_bode_data(
                    num_per_decade=CONFIG.num_per_decade_in_simulated_lines
                ),
                True,
            )
            before = self.bode_plot_horizontal.plot_sim(
                *result.get_bode_data(),
                True,
                before,
            )
        if data is not None:
            self.bode_plot_horizontal.plot_data(
                *data.get_bode_data(),
                before,
                True,
            )
        before = (
            -1,
            -1,
        )
        if result is not None:
            before = self.bode_plot_vertical.plot_smooth(
                *result.get_bode_data(
                    num_per_decade=CONFIG.num_per_decade_in_simulated_lines
                ),
                True,
            )
            before = self.bode_plot_vertical.plot_sim(
                *result.get_bode_data(),
                True,
                before,
            )
        if data is not None:
            self.bode_plot_vertical.plot_data(
                *data.get_bode_data(),
                before,
                True,
            )
        self.nyquist_plot.adjust_limits()
        self.bode_plot_horizontal.adjust_limits()
        self.bode_plot_vertical.adjust_limits()

    def preview_circuit(self, result: Optional[SimulationResult]):
        dpg.delete_item(self.circuit_preview_node_editor, children_only=True)
        if result is None:
            return
        editor: CircuitEditor = CircuitEditor(dpg.add_window(show=False))
        preview: CircuitPreview = CircuitPreview(self.circuit_preview_node_editor)
        editor.parse_cdc(result.settings.cdc)
        preview.update(editor.nodes_to_dict())

    def get_cdc_input(self) -> str:
        return dpg.get_value(self.cdc_input).strip()

    def update_cdc_input(self, string: str, theme: int):
        dpg.bind_item_theme(self.cdc_input, theme)
        dpg.set_value(self.cdc_input, string)

    def get_output_type(self) -> Output:
        return label_to_output.get(dpg.get_value(self.output_combo))

    def get_max_freq(self) -> float:
        return dpg.get_value(self.max_freq_input)

    def get_min_freq(self) -> float:
        return dpg.get_value(self.min_freq_input)

    def set_freq_range(self, minimum: float, maximum: float):
        dpg.set_value(self.min_freq_input, minimum)
        dpg.set_value(self.max_freq_input, maximum)

    def get_num_per_decade(self) -> int:
        return dpg.get_value(self.per_decade_input)


if __name__ == "__main__":
    dpg.create_context()
    dpg.create_viewport(title="Simulation tab")
    dpg.setup_dearpygui()
    dpg.show_viewport()
    window: int
    with dpg.window() as window:
        with dpg.tab_bar():
            SimulationTab()
    dpg.set_primary_window(window, True)
    dpg.start_dearpygui()
    dpg.destroy_context()
