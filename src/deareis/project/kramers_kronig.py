# Copyright 2022 DearEIS developers
# DearEIS is licensed under the GPLv3 or later (https://www.gnu.org/licenses/gpl-3.0.html).
# The licenses of DearEIS' dependencies and/or sources of portions of code are included in
# the LICENSES folder.

from pyimpspec import DataSet
from typing import List, Optional, Tuple, Union
from numpy import floor, log10 as log
import dearpygui.dearpygui as dpg
import deareis.tooltips as tooltips
from deareis.plot import (
    ResidualsPlot,
    NyquistPlot,
    BodePlot,
)
from deareis.utility import attach_tooltip
from deareis.data.kramers_kronig import (
    Method,
    Mode,
    Test,
    TestResult,
    label_to_method,
    label_to_mode,
    label_to_test,
    method_to_label,
    mode_to_label,
    test_to_label,
)
from deareis.config import CONFIG


# TODO: Argument type assertions


class KramersKronigTab:
    def __init__(self):
        self.tab: int = dpg.generate_uuid()
        self.resize_group: int = dpg.generate_uuid()
        # Settings
        self.test_combo: int = dpg.generate_uuid()
        self.mode_combo: int = dpg.generate_uuid()
        self.num_RC_label: int = dpg.generate_uuid()
        self.num_RC_slider: int = dpg.generate_uuid()
        self.add_cap_checkbox: int = dpg.generate_uuid()
        self.add_ind_checkbox: int = dpg.generate_uuid()
        self.mu_crit_slider: int = dpg.generate_uuid()
        self.method_combo: int = dpg.generate_uuid()
        self.max_nfev_input: int = dpg.generate_uuid()
        self.perform_test_button: int = dpg.generate_uuid()
        # Statistics and used settings
        self.sidebar_window: int = dpg.generate_uuid()
        self.dataset_combo: int = dpg.generate_uuid()
        self.result_combo: int = dpg.generate_uuid()
        self.result_info_text: int = dpg.generate_uuid()
        self.delete_result_button: int = dpg.generate_uuid()
        self.statistics_table: int = dpg.generate_uuid()
        self.settings_table: int = dpg.generate_uuid()
        self.apply_settings_button: int = dpg.generate_uuid()
        # Plots window
        self.plots_window: int = dpg.generate_uuid()
        self.residuals_plot: ResidualsPlot = None
        self.nyquist_plot: NyquistPlot = None
        self.horizontal_bode_group: int = dpg.generate_uuid()
        self.vertical_bode_group: int = dpg.generate_uuid()
        self.bode_plot_horizontal: BodePlot = None
        self.bode_plot_vertical: BodePlot = None
        self.enlarge_nyquist_button: int = dpg.generate_uuid()
        self.enlarge_bode_horizontal_button: int = dpg.generate_uuid()
        self.enlarge_bode_vertical_button: int = dpg.generate_uuid()
        self.enlarge_residuals_button: int = dpg.generate_uuid()
        #
        self._assemble()
        self._assign_handlers()
        self.populate_tables(None)

    def to_dict(self) -> dict:
        return {
            "test": dpg.get_value(self.test_combo),
            "mode": dpg.get_value(self.mode_combo),
            "num_RC": dpg.get_value(self.num_RC_slider),
            "add_cap": dpg.get_value(self.add_cap_checkbox),
            "add_ind": dpg.get_value(self.add_ind_checkbox),
            "mu_crit": dpg.get_value(self.mu_crit_slider),
            "method": dpg.get_value(self.method_combo),
            "max_nfev": dpg.get_value(self.max_nfev_input),
        }

    def restore_state(self, state: dict):
        dpg.set_value(self.test_combo, state["test"])
        dpg.set_value(self.mode_combo, state["mode"])
        dpg.set_value(self.num_RC_slider, state["num_RC"])
        dpg.set_value(self.add_cap_checkbox, state["add_cap"])
        dpg.set_value(self.add_ind_checkbox, state["add_ind"])
        dpg.set_value(self.mu_crit_slider, state["mu_crit"])
        dpg.set_value(self.method_combo, state["method"])
        dpg.set_value(self.max_nfev_input, state["max_nfev"])

    def _assemble(self):
        sidebar_width: int = 350
        settings_height: int = 220
        label_pad: int = 23
        with dpg.tab(label="Kramers-Kronig", tag=self.tab):
            with dpg.child_window(border=False):
                with dpg.group(horizontal=True, tag=self.resize_group):
                    with dpg.child_window(
                        border=False,
                        width=sidebar_width,
                        tag=self.sidebar_window,
                    ):
                        with dpg.child_window(width=-1, height=settings_height):
                            with dpg.group(horizontal=True):
                                dpg.add_text("Test".rjust(label_pad))
                                attach_tooltip(tooltips.kramers_kronig_test)
                                dpg.add_combo(
                                    items=list(label_to_test.keys()),
                                    default_value=list(label_to_test.keys())[1],
                                    tag=self.test_combo,
                                    width=-1,
                                )
                            with dpg.group(horizontal=True):
                                dpg.add_text("Mode".rjust(label_pad))
                                attach_tooltip(tooltips.kramers_kronig_mode)
                                dpg.add_combo(
                                    items=list(label_to_mode.keys()),
                                    default_value=list(label_to_mode.keys())[1],
                                    tag=self.mode_combo,
                                    width=-1,
                                )
                            with dpg.group(horizontal=True):
                                dpg.add_text(
                                    "Number of RC circuits".rjust(label_pad),
                                    tag=self.num_RC_label,
                                )
                                attach_tooltip(tooltips.kramers_kronig_num_RC)
                                dpg.add_slider_int(
                                    tag=self.num_RC_slider,
                                    width=-1,
                                    clamped=True,
                                )
                            with dpg.group(horizontal=True):
                                dpg.add_text("Add capacitor in series".rjust(label_pad))
                                attach_tooltip(tooltips.kramers_kronig_add_cap)
                                dpg.add_checkbox(
                                    default_value=True,
                                    tag=self.add_cap_checkbox,
                                )
                            with dpg.group(horizontal=True):
                                dpg.add_text("Add inductor in series".rjust(label_pad))
                                attach_tooltip(tooltips.kramers_kronig_add_ind)
                                dpg.add_checkbox(
                                    default_value=True,
                                    tag=self.add_ind_checkbox,
                                )
                            with dpg.group(horizontal=True):
                                dpg.add_text("µ-criterion".rjust(label_pad))
                                attach_tooltip(tooltips.kramers_kronig_mu_crit)
                                dpg.add_slider_float(
                                    default_value=0.85,
                                    min_value=0.01,
                                    max_value=0.99,
                                    clamped=True,
                                    format="%.2f",
                                    tag=self.mu_crit_slider,
                                    width=-1,
                                )
                            with dpg.group(horizontal=True):
                                dpg.add_text("Fitting method".rjust(label_pad))
                                attach_tooltip(tooltips.kramers_kronig_method)
                                dpg.add_combo(
                                    items=list(label_to_method.keys()),
                                    default_value=list(label_to_method.keys())[0],
                                    tag=self.method_combo,
                                    width=-1,
                                )
                            with dpg.group(horizontal=True):
                                dpg.add_text("Max. num. func. eval.".rjust(label_pad))
                                attach_tooltip(tooltips.kramers_kronig_nfev)
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
                                attach_tooltip(tooltips.kramers_kronig_perform)
                                dpg.add_button(
                                    label="Perform test",
                                    tag=self.perform_test_button,
                                    width=-1,
                                )
                        with dpg.child_window(width=-1, height=58):
                            label_pad = 8
                            with dpg.group(horizontal=True):
                                dpg.add_text("Data set".rjust(label_pad))
                                dpg.add_combo(
                                    tag=self.dataset_combo,
                                    width=-60,
                                )
                            with dpg.group(horizontal=True):
                                dpg.add_text("Result".rjust(label_pad))
                                dpg.add_combo(
                                    tag=self.result_combo,
                                    width=-60,
                                )
                                dpg.add_button(
                                    label="Delete",
                                    width=-1,
                                    tag=self.delete_result_button,
                                )
                                attach_tooltip(tooltips.kramers_kronig_remove)
                        with dpg.child_window(width=-1, height=-1):
                            with dpg.group(show=False):
                                dpg.add_text("", tag=self.result_info_text)
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
                                attach_tooltip(tooltips.apply_settings)
                    with dpg.child_window(border=False, tag=self.plots_window):
                        with dpg.group():
                            # Residuals
                            self.residuals_plot = ResidualsPlot(
                                dpg.add_plot(
                                    width=-1,
                                    height=-12,
                                    anti_aliased=True,
                                )
                            )
                            with dpg.group(horizontal=True):
                                dpg.add_button(
                                    label="Enlarge residuals",
                                    user_data=self.residuals_plot,
                                    tag=self.enlarge_residuals_button,
                                )
                                dpg.set_item_callback(
                                    dpg.add_button(label="Copy as CSV"),
                                    self.residuals_plot.copy_data,
                                )
                                attach_tooltip(tooltips.copy_plot_data_as_csv)
                            # Nyquist and Bode
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
                                        dpg.set_item_callback(
                                            dpg.add_button(label="Copy as CSV"),
                                            self.nyquist_plot.copy_data,
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
                                        dpg.set_item_callback(
                                            dpg.add_button(label="Copy as CSV"),
                                            self.bode_plot_horizontal.copy_data,
                                        )
                                        attach_tooltip(tooltips.copy_plot_data_as_csv)
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
                                        label="Enlarge Bode",
                                        user_data=self.bode_plot_vertical,
                                        tag=self.enlarge_bode_vertical_button,
                                    )
                                    dpg.set_item_callback(
                                        dpg.add_button(label="Copy as CSV"),
                                        self.bode_plot_vertical.copy_data,
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
        sidebar_height -= 5 + 16
        minimum_plot_height: int = 250
        plot_width: int = int(total_width - sidebar_width - 8)
        plot_height: int = int(minimum_plot_height)
        if aspect_ratio > 1.5 and total_width - sidebar_width > 25:
            if dpg.is_item_shown(self.vertical_bode_group):
                dpg.hide_item(self.vertical_bode_group)
                dpg.show_item(self.horizontal_bode_group)
            self.residuals_plot.resize(plot_width, plot_height)
            plot_height = int(sidebar_height - minimum_plot_height - 34)
            plot_width = int(round((plot_width - 7) / 2))
            self.nyquist_plot.resize(plot_width, plot_height)
            self.bode_plot_horizontal.resize(plot_width, plot_height)
            self.bode_plot_horizontal.adjust_limits()
        else:
            if dpg.is_item_shown(self.horizontal_bode_group):
                dpg.hide_item(self.horizontal_bode_group)
                dpg.show_item(self.vertical_bode_group)
            plot_width = -1
            if total_height > 3 * minimum_plot_height:
                plot_height = int(floor(total_height / 3) - 3 * 9)
            self.residuals_plot.resize(plot_width, plot_height)
            self.nyquist_plot.resize(plot_width, plot_height)
            self.bode_plot_vertical.resize(plot_width, plot_height)
            self.bode_plot_vertical.adjust_limits()
        self.residuals_plot.adjust_limits()
        self.nyquist_plot.adjust_limits()

    def is_visible(self) -> bool:
        return dpg.is_item_visible(self.test_combo)

    def populate_tables(self, result: Optional[TestResult]):
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
        statistics: List[Tuple[str, str, str]] = [
            (
                "log X² (pseudo)",
                f"{log(result.pseudo_chisqr):.3f}" if result is not None else "",
                tooltips.kramers_kronig_pseudo_chisqr,
            ),
            (
                "µ",
                f"{result.mu:.3f}" if result is not None else "",
                tooltips.kramers_kronig_mu_crit,
            ),
            (
                "Number of RC circuits",
                str(result.num_RC) if result is not None else "",
                tooltips.kramers_kronig_num_RC,
            ),
        ]
        settings: List[Tuple[str, str, str]] = [
            (
                "Test",
                test_to_label.get(result.settings.test, "")
                if result is not None
                else "",
                tooltips.kramers_kronig_test,
            ),
            (
                "Mode",
                mode_to_label.get(result.settings.mode, "")
                if result is not None
                else "",
                tooltips.kramers_kronig_mode,
            ),
            (
                "Number of RC circuits",
                str(result.settings.num_RC) if result is not None else "",
                tooltips.kramers_kronig_num_RC,
            ),
            (
                "Add capacitor in series",
                ("True" if result.settings.add_capacitance else "False")
                if result is not None
                else "",
                tooltips.kramers_kronig_add_cap,
            ),
            (
                "Add inductor in series",
                ("True" if result.settings.add_inductance else "False")
                if result is not None
                else "",
                tooltips.kramers_kronig_add_ind,
            ),
        ]
        if result is None or result.settings.mode != Mode.MANUAL:
            settings.append(
                (
                    "µ-criterion",
                    f"{result.settings.mu_criterion:.2f}" if result is not None else "",
                    tooltips.kramers_kronig_mu_crit,
                ),
            )
        if result is None or result.settings.test == Test.CNLS:
            settings.extend(
                [
                    (
                        "Method",
                        method_to_label.get(result.settings.method, "")
                        if result is not None
                        else "",
                        tooltips.kramers_kronig_method,
                    ),
                    (
                        "Max. num. func. eval.",
                        (
                            str(result.settings.max_nfev)
                            if result.settings.max_nfev > 0
                            else "-"
                        )
                        if result is not None
                        else "",
                        tooltips.kramers_kronig_nfev,
                    ),
                ]
            )
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

    def populate_combo(self, labels: List[str], default: str = ""):
        assert type(labels) is list and all(list(map(lambda _: type(_) is str, labels)))
        assert type(default) is str
        if default == "" and len(labels) > 0:
            default = labels[0]
        dpg.configure_item(self.dataset_combo, items=labels, default_value=default)

    def select_dataset(
        self,
        data: Optional[DataSet],
        results: List[TestResult],
        update_table_plots: bool,
    ):
        assert type(data) is DataSet or data is None
        assert type(results) is list and (
            len(results) == 0 or all(map(lambda _: type(_) is TestResult, results))
        )
        assert type(update_table_plots) is bool
        dpg.set_item_user_data(self.dataset_combo, data)
        labels: List[str] = list(map(lambda _: _.get_label(), results))
        dpg.configure_item(
            self.result_combo,
            items=labels,
            default_value=labels[0] if len(labels) > 0 else "",
        )
        dpg.set_value(self.dataset_combo, data.get_label() if data is not None else "")
        min_value: int = 2 if data is not None else 0
        max_value: int = data.get_num_points() if data is not None else 1
        default_value: int = dpg.get_value(self.num_RC_slider)
        default_value = (
            default_value if min_value < default_value <= max_value else max_value
        )
        dpg.configure_item(
            self.num_RC_slider,
            min_value=min_value,
            max_value=max_value,
            default_value=default_value,
        )
        self.select_result(data, results[0] if len(results) > 0 else None)

    def plot(self, data: Optional[DataSet], result: Optional[TestResult]):
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
                *result.get_nyquist_data(
                    num_per_decade=CONFIG.num_per_decade_in_simulated_lines
                ),
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
                *result.get_bode_data(
                    num_per_decade=CONFIG.num_per_decade_in_simulated_lines
                ),
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
                *result.get_bode_data(
                    num_per_decade=CONFIG.num_per_decade_in_simulated_lines
                ),
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

    def select_result(self, data: Optional[DataSet], result: Optional[TestResult]):
        assert type(data) is DataSet or data is None
        assert type(result) is TestResult or result is None
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
        dpg.set_value(
            self.result_combo, result.get_label() if result is not None else ""
        )
        self.populate_tables(result)
        self.plot(data, result)

    def get_result(self) -> Optional[TestResult]:
        if not dpg.does_item_exist(self.result_combo):
            return None
        return dpg.get_item_user_data(self.result_combo)

    def get_method(self) -> Method:
        return label_to_method.get(dpg.get_value(self.method_combo), Method.LEASTSQ)

    def get_max_nfev(self) -> int:
        return dpg.get_value(self.max_nfev_input)

    def get_mu_criterion(self) -> float:
        return dpg.get_value(self.mu_crit_slider)

    def get_add_inductor(self) -> bool:
        return dpg.get_value(self.add_ind_checkbox)

    def get_add_capacitor(self) -> bool:
        return dpg.get_value(self.add_cap_checkbox)

    def get_num_RC(self) -> int:
        return dpg.get_value(self.num_RC_slider)


if __name__ == "__main__":
    dpg.create_context()
    dpg.create_viewport(title="Kramers-Kronig tab")
    dpg.setup_dearpygui()
    dpg.show_viewport()
    window: int
    with dpg.window() as window:
        with dpg.tab_bar():
            KramersKronigTab()
    dpg.set_primary_window(window, True)
    dpg.start_dearpygui()
    dpg.destroy_context()
