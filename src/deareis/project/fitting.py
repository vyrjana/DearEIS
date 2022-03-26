# Copyright 2022 DearEIS developers
# DearEIS is licensed under the GPLv3 or later (https://www.gnu.org/licenses/gpl-3.0.html).
# The licenses of DearEIS' dependencies and/or sources of portions of code are included in
# the LICENSES folder.

from pyimpspec import DataSet
import pyimpspec
from typing import Dict, List, Optional, Tuple, Union
import dearpygui.dearpygui as dpg
from numpy import floor, log10 as log
import deareis.tooltips as tooltips
from deareis.plot import (
    BodePlot,
    NyquistPlot,
    ResidualsPlot,
)
from deareis.utility import (
    attach_tooltip,
    number_formatter,
    align_numbers,
)
from deareis.project.circuit_editor import CircuitEditor, CircuitPreview
from deareis.data.fitting import (
    FitResult,
    FitSettings,
    Method,
    Weight,
    label_to_method,
    label_to_weight,
    method_to_label,
    method_to_value,
    weight_to_label,
    weight_to_value,
)
from deareis.data.shared import (
    Output,
    label_to_output,
    output_to_label,
)

# TODO: Argument type assertions

class FittingTab:
    def __init__(self):
        self.tab: int = dpg.generate_uuid()
        self.resize_group: int = dpg.generate_uuid()
        self.sidebar_window: int = dpg.generate_uuid()
        # Settings
        self.cdc_input: int = dpg.generate_uuid()
        self.editor_button: int = dpg.generate_uuid()
        self.method_combo: int = dpg.generate_uuid()
        self.weight_combo: int = dpg.generate_uuid()
        self.max_nfev_input: int = dpg.generate_uuid()
        self.perform_fit_button: int = dpg.generate_uuid()
        # Statistics and used settings
        self.dataset_combo: int = dpg.generate_uuid()
        self.result_combo: int = dpg.generate_uuid()
        self.results_window: int = dpg.generate_uuid()
        self.result_info_text: int = dpg.generate_uuid()
        self.delete_result_button: int = dpg.generate_uuid()
        self.statistics_table: int = dpg.generate_uuid()
        self.settings_table: int = dpg.generate_uuid()
        self.apply_settings_button: int = dpg.generate_uuid()
        # Plots window
        self.plots_window: int = dpg.generate_uuid()
        self.parameters_table: int = dpg.generate_uuid()
        self.output_combo: int = dpg.generate_uuid()
        self.copy_output_button: int = dpg.generate_uuid()
        self.circuit_preview: int = dpg.generate_uuid()
        self.residuals_plot: ResidualsPlot = None
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
        self.circuit_preview_height: int = 250
        #
        self._assemble()
        self._assign_handlers()

    def to_dict(self) -> dict:
        return {
            "cdc": dpg.get_value(self.cdc_input),
            "method": dpg.get_value(self.method_combo),
            "weight": dpg.get_value(self.weight_combo),
            "max_nfev": dpg.get_value(self.max_nfev_input),
            "output": dpg.get_value(self.output_combo),
        }

    def restore_state(self, state: dict):
        dpg.set_value(self.cdc_input, state["cdc"]),
        dpg.get_item_callback(self.cdc_input)(self.cdc_input, state["cdc"])
        dpg.set_value(self.method_combo, state["method"]),
        dpg.set_value(self.weight_combo, state["weight"]),
        dpg.set_value(self.max_nfev_input, state["max_nfev"]),
        dpg.set_value(self.output_combo, state["output"]),

    def _assemble(self):
        sidebar_width: int = 350
        settings_height: int = 128
        label_pad: int = 22
        with dpg.tab(label="Fitting", tag=self.tab):
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
                            attach_tooltip(tooltips.fitting_cdc)
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
                        with dpg.group(horizontal=True):
                            dpg.add_text("Method".rjust(label_pad))
                            attach_tooltip(tooltips.fitting_method)
                            dpg.add_combo(
                                items=["Auto"] + list(label_to_method.keys()),
                                default_value="Auto",
                                width=-1,
                                tag=self.method_combo,
                            )
                        with dpg.group(horizontal=True):
                            dpg.add_text("Weight function".rjust(label_pad))
                            attach_tooltip(tooltips.fitting_weight)
                            dpg.add_combo(
                                items=["Auto"] + list(label_to_weight.keys()),
                                default_value="Auto",
                                width=-1,
                                tag=self.weight_combo,
                            )
                        with dpg.group(horizontal=True):
                            dpg.add_text("Max. num. func. eval.".rjust(label_pad))
                            attach_tooltip(tooltips.fitting_nfev)
                            dpg.add_input_int(
                                default_value=1000,
                                min_value=0,
                                min_clamped=True,
                                step=0,
                                on_enter=True,
                                tag=self.max_nfev_input,
                                width=-1,
                            )
                        with dpg.group(horizontal=True):
                            dpg.add_text("?".rjust(label_pad))
                            attach_tooltip(tooltips.fitting_perform)
                            dpg.add_button(
                                label="Perform fit",
                                width=-1,
                                tag=self.perform_fit_button,
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
                    with dpg.child_window(width=-1, height=-1):
                        with dpg.group(show=False):
                            dpg.add_text("", tag=self.result_info_text)
                            dpg.add_spacer(height=8)
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
                        with dpg.collapsing_header(label=" Statistics", leaf=True):
                            dpg.add_table(
                                borders_outerV=True,
                                borders_outerH=True,
                                borders_innerV=True,
                                borders_innerH=True,
                                scrollY=True,
                                freeze_rows=1,
                                height=87,
                                tag=self.statistics_table,
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
                with dpg.child_window(
                    border=False,
                    width=-1,
                    height=-1,
                    tag=self.plots_window,
                ):
                    with dpg.child_window(
                        border=False,
                        width=-1,
                        height=self.circuit_preview_height,
                    ):
                        dpg.add_node_editor(tag=self.circuit_preview)
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
                    with dpg.group(tag=self.vertical_bode_group):
                        self.bode_plot_vertical = BodePlot(
                            dpg.add_plot(
                                width=400,
                                height=400,
                                anti_aliased=True,
                            )
                        )
                        with dpg.group(horizontal=True):
                            dpg.add_button(
                                label="Enlarge Nyquist",
                                user_data=self.bode_plot_vertical,
                                tag=self.enlarge_bode_vertical_button,
                            )
                            dpg.add_button(
                                label="Copy as CSV",
                                callback=self.bode_plot_vertical.copy_data,
                            )
                    self.residuals_plot = ResidualsPlot(
                        dpg.add_plot(
                            width=400,
                            height=400,
                            anti_aliased=True,
                        )
                    )
                    with dpg.group(horizontal=True):
                        dpg.add_button(
                            label="Enlarge residuals",
                            user_data=self.residuals_plot,
                            tag=self.enlarge_residuals_button,
                        )
                        dpg.add_button(
                            label="Copy as CSV",
                            callback=self.residuals_plot.copy_data,
                        )

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
        sidebar_height -= 5 + 16
        plot_width: int = int(total_width - sidebar_width - 29)
        plot_height: int = int(self.circuit_preview_height)
        if aspect_ratio > 1.5 and total_width - sidebar_width > 250:
            if dpg.is_item_shown(self.vertical_bode_group):
                dpg.hide_item(self.vertical_bode_group)
                dpg.show_item(self.horizontal_bode_group)
            self.residuals_plot.resize(plot_width, plot_height)
            plot_height = int(sidebar_height - self.circuit_preview_height - 34)
            plot_width = int(round((plot_width - 7) / 2))
            self.nyquist_plot.resize(plot_width, plot_height)
            self.bode_plot_horizontal.resize(plot_width, plot_height)
            self.bode_plot_horizontal.adjust_limits()
        else:
            if dpg.is_item_shown(self.horizontal_bode_group):
                dpg.hide_item(self.horizontal_bode_group)
                dpg.show_item(self.vertical_bode_group)
            plot_width = -1
            if total_height > 4 * self.circuit_preview_height:
                plot_height = int(
                    floor((total_height - self.circuit_preview_height) / 3) - 3 * 10
                )
            self.residuals_plot.resize(plot_width, plot_height)
            self.nyquist_plot.resize(plot_width, plot_height)
            self.bode_plot_vertical.resize(plot_width, plot_height)
            self.bode_plot_vertical.adjust_limits()
        self.residuals_plot.adjust_limits()
        self.nyquist_plot.adjust_limits()

    def is_visible(self) -> bool:
        return dpg.is_item_visible(self.cdc_input)

    def is_input_active(self) -> bool:
        return dpg.is_item_active(self.cdc_input)

    def populate_combo(self, labels: List[str], default: str = ""):
        assert type(labels) is list and all(list(map(lambda _: type(_) is str, labels)))
        assert type(default) is str
        if default == "" and len(labels) > 0:
            default = labels[0]
        dpg.configure_item(self.dataset_combo, items=labels, default_value=default)

    def select_dataset(
        self,
        data: Optional[DataSet],
        results: List[FitResult],
        update_table_plots: bool,
    ):
        assert type(data) is DataSet or data is None
        assert type(results) is list and (
            len(results) == 0 or all(map(lambda _: type(_) is FitResult, results))
        )
        assert type(update_table_plots) is bool
        labels: List[str] = list(map(lambda _: _.get_label(), results))
        dpg.configure_item(
            self.result_combo,
            items=labels,
            default_value=labels[0] if len(labels) > 0 else "",
        )
        dpg.set_value(self.dataset_combo, data.get_label() if data is not None else "")
        self.select_result(data, results[0] if len(results) > 0 else None)

    def select_result(self, data: Optional[DataSet], result: Optional[FitResult]):
        assert type(data) is DataSet or data is None
        assert type(result) is FitResult or result is None
        if result is None:
            dpg.hide_item(dpg.get_item_parent(self.result_info_text))
        else:
            dpg.set_value(self.result_info_text, result.get_info(data))
            if dpg.get_value(self.result_info_text) != "":
                dpg.show_item(dpg.get_item_parent(self.result_info_text))
            else:
                dpg.hide_item(dpg.get_item_parent(self.result_info_text))
        dpg.set_item_user_data(self.result_combo, result)
        dpg.set_item_user_data(self.delete_result_button, result)
        dpg.set_item_user_data(self.apply_settings_button, result)
        dpg.set_item_user_data(self.copy_output_button, result)
        dpg.set_value(
            self.result_combo, result.get_label() if result is not None else ""
        )
        self.populate_tables(result)
        self.preview_circuit(result)
        self.plot(data, result)

    def get_result(self) -> Optional[FitResult]:
        if not dpg.does_item_exist(self.result_combo):
            return None
        return dpg.get_item_user_data(self.result_combo)

    def preview_circuit(self, result: Optional[FitResult]):
        dpg.delete_item(self.circuit_preview, children_only=True)
        if result is None:
            return
        editor: CircuitEditor = CircuitEditor(dpg.add_window(show=False))
        preview: CircuitPreview = CircuitPreview(self.circuit_preview)
        editor.parse_cdc(result.settings.cdc)
        preview.update(editor.nodes_to_dict())

    def populate_tables(self, result: Optional[FitResult]):
        header_height: int = 18
        row_height: int = 23
        label_pad: int = 23
        dpg.delete_item(self.statistics_table, children_only=True)
        dpg.add_table_column(
            parent=self.statistics_table,
            label="Label".rjust(label_pad),
            width_fixed=True,
        )
        dpg.add_table_column(
            parent=self.statistics_table, label="Value", width_fixed=True
        )
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
        dpg.add_table_column(
            parent=self.parameters_table,
            label="Parameter",
            width_fixed=True,
        )
        dpg.add_table_column(
            parent=self.parameters_table,
            label="Value",
            width_fixed=True,
        )
        dpg.add_table_column(
            parent=self.parameters_table,
            label="Error (%)",
        )
        statistics: List[Tuple[str, str, str]] = [
            (
                "log X²",
                f"{log(result.chisqr):.3f}" if result is not None else "",
                tooltips.fitting_chisqr,
            ),
            (
                "log X² (reduced)",
                f"{log(result.red_chisqr):.3f}" if result is not None else "",
                tooltips.fitting_red_chisqr,
            ),
            (
                "Akaike inf. crit.",
                f"{result.aic:.3E}" if result is not None else "",
                tooltips.fitting_aic,
            ),
            (
                "Bayesian inf. crit.",
                f"{result.bic:.3E}" if result is not None else "",
                tooltips.fitting_bic,
            ),
            (
                "Degrees of freedom",
                str(result.nfree) if result is not None else "",
                tooltips.fitting_nfree,
            ),
            (
                "Number of data points",
                str(result.ndata) if result is not None else "",
                tooltips.fitting_ndata,
            ),
            (
                "Number of func. eval.",
                str(result.nfev) if result is not None else "",
                tooltips.fitting_nfev,
            ),
            (
                "Method",
                method_to_label.get(result.method) if result is not None else "",
                tooltips.fitting_method,
            ),
            (
                "Weight",
                weight_to_label.get(result.weight) if result is not None else "",
                tooltips.fitting_weight,
            ),
        ]
        cdc: str = result.settings.cdc if result is not None else ""
        while "{" in cdc:
            i: int = cdc.find("{")
            j: int = cdc.find("}")
            cdc = cdc.replace(cdc[i : j + 1], "")
        settings: List[Tuple[str, str, str]] = [
            (
                "Circuit",
                cdc,
                tooltips.fitting_cdc,
            ),
            (
                "Method",
                method_to_label.get(result.settings.method)
                if result is not None
                else "",
                tooltips.fitting_method,
            ),
            (
                "Weight",
                weight_to_label.get(result.settings.weight)
                if result is not None
                else "",
                tooltips.fitting_weight,
            ),
            (
                "Max. num. func. eval.",
                str(result.settings.max_nfev) if result is not None else "",
                tooltips.fitting_nfev,
            ),
        ]
        max_label_len: int = max(map(lambda _: len(_[0]), statistics + settings))
        assert max_label_len <= label_pad, (
            max_label_len,
            label_pad,
        )
        label: str
        value: str
        tooltip: str
        for (label, value, tooltip) in statistics:
            with dpg.table_row(parent=self.statistics_table):
                dpg.add_text(label.rjust(label_pad))
                attach_tooltip(tooltip)
                dpg.add_text(value)
                attach_tooltip(value)
        dpg.set_item_height(
            self.statistics_table, header_height + len(statistics) * row_height
        )
        for (label, value, tooltip) in settings:
            with dpg.table_row(parent=self.settings_table):
                dpg.add_text(label.rjust(label_pad))
                attach_tooltip(tooltip)
                dpg.add_text(value)
                attach_tooltip(value)
        dpg.set_item_height(
            self.settings_table, header_height + len(settings) * row_height
        )
        element_classes: Dict[str, Type[Element]] = pyimpspec.get_elements()
        element_labels: List[str] = []
        element_tooltips: List[str] = []
        parameter_labels: List[str] = []
        values: List[str] = []
        value_tooltips: List[str] = []
        error_values: List[str] = []
        error_tooltips: List[str] = []
        if result is not None:
            element_label: str
            element_tooltip: str
            parameter_label: str
            value: str
            value_tooltip: str
            error_value: str
            error_tooltip: str
            parameters: Dict[str, FittedParameter]
            for element_label, parameters in result.parameters.items():
                Class: Type[Element] = element_classes[
                    element_label[: element_label.find("_")]
                ]
                element_tooltip = Class.get_extended_description()
                parameter: FittedParameter
                for parameter_label, parameter in parameters.items():
                    element_labels.append(element_label)
                    element_tooltips.append(element_tooltip)
                    parameter_labels.append(
                        parameter_label + (" (fixed)" if parameter.fixed else "")
                    )
                    values.append(
                        f"{number_formatter(parameter.value, width=9, significants=3)}"
                    )
                    value_tooltips.append(
                        f"{number_formatter(parameter.value, decimals=6).strip()}"
                    )
                    if parameter.stderr is not None:
                        error: float = parameter.stderr / parameter.value * 100
                        if error > 100.0:
                            error_value = ">100"
                        elif error < 0.01:
                            error_value = "<0.01"
                        else:
                            error_value = f"{number_formatter(error, exponent=False, significants=3)}"
                        error_tooltip = (
                            f"{number_formatter(parameter.value, decimals=6).strip()} "
                            + f"± {number_formatter(parameter.stderr, decimals=6).strip()}"
                        )
                    else:
                        error_value = "-"
                        if not parameter.fixed:
                            error_tooltip = "Unable to estimate error."
                        else:
                            error_tooltip = "Fixed parameter."
                    error_values.append(error_value)
                    error_tooltips.append(error_tooltip)
            values = align_numbers(values)
            error_values = align_numbers(error_values)
            for (
                element_label,
                element_tooltip,
                parameter_label,
                value,
                value_tooltip,
                error_value,
                error_tooltip,
            ) in zip(
                element_labels,
                element_tooltips,
                parameter_labels,
                values,
                value_tooltips,
                error_values,
                error_tooltips,
            ):
                with dpg.table_row(parent=self.parameters_table):
                    dpg.add_text(element_label.ljust(10))
                    if element_tooltip != "":
                        attach_tooltip(element_tooltip)
                    dpg.add_text(parameter_label.ljust(11))
                    dpg.add_text(value.ljust(10))
                    attach_tooltip(value_tooltip)
                    dpg.add_text(error_value.ljust(10))
                    if error_tooltip != "":
                        attach_tooltip(error_tooltip)
        else:
            with dpg.table_row(parent=self.parameters_table):
                dpg.add_text("".ljust(10))
                dpg.add_text("".ljust(11))
                dpg.add_text("".ljust(10))
                dpg.add_text("".ljust(10))
        dpg.set_item_height(
            self.parameters_table, header_height + max(len(values), 1) * row_height
        )

    def plot(self, data: Optional[DataSet], result: Optional[FitResult]):
        self.residuals_plot.clear_plot()
        self.nyquist_plot.clear_plot()
        self.bode_plot_horizontal.clear_plot()
        self.bode_plot_vertical.clear_plot()
        if data is None:
            return
        if result is not None:
            self.residuals_plot.plot_data(*result.get_residual_data())
        before: Union[int, Tuple[int, int]] = -1
        if result is not None:
            before = self.nyquist_plot.plot_smooth(
                *result.get_nyquist_data(num_per_decade=100),
                False,
            )
            before = self.nyquist_plot.plot_sim(
                *result.get_nyquist_data(),
                False,
                before,
            )
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
                *result.get_bode_data(num_per_decade=100),
                False,
            )
            before = self.bode_plot_horizontal.plot_sim(
                *result.get_bode_data(),
                False,
                before,
            )
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
                *result.get_bode_data(num_per_decade=100),
                False,
            )
            before = self.bode_plot_vertical.plot_sim(
                *result.get_bode_data(),
                False,
                before,
            )
        self.bode_plot_vertical.plot_data(
            *data.get_bode_data(),
            before,
            True,
        )
        self.residuals_plot.adjust_limits()
        self.nyquist_plot.adjust_limits()
        self.bode_plot_horizontal.adjust_limits()
        self.bode_plot_vertical.adjust_limits()

    def get_cdc_input(self) -> str:
        return dpg.get_value(self.cdc_input).strip()

    def update_cdc_input(self, string: str, theme: int):
        dpg.bind_item_theme(self.cdc_input, theme)
        dpg.set_value(self.cdc_input, string)

    def get_output_type(self) -> Output:
        return label_to_output.get(dpg.get_value(self.output_combo))

    def get_method(self) -> Method:
        return label_to_method.get(dpg.get_value(self.method_combo), Method.AUTO)

    def get_weight(self) -> Weight:
        return label_to_weight.get(dpg.get_value(self.weight_combo), Weight.AUTO)

    def get_max_nfev(self) -> int:
        return dpg.get_value(self.max_nfev_input)


if __name__ == "__main__":
    dpg.create_context()
    dpg.create_viewport(title="Fitting tab")
    dpg.setup_dearpygui()
    dpg.show_viewport()
    window: int
    with dpg.window() as window:
        with dpg.tab_bar():
            FittingTab()
    dpg.set_primary_window(window, True)
    dpg.start_dearpygui()
    dpg.destroy_context()
