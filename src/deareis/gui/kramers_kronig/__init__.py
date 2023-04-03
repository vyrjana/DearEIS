# DearEIS is licensed under the GPLv3 or later (https://www.gnu.org/licenses/gpl-3.0.html).
# Copyright 2023 DearEIS developers
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# The licenses of DearEIS' dependencies and/or sources of portions of code are included in
# the LICENSES folder.

from typing import (
    Callable,
    Dict,
    List,
    Optional,
)
from numpy import (
    allclose,
    array,
    isnan,
    log10 as log,
    ndarray,
)
from pyimpspec.analysis.utility import _calculate_residuals
from pyimpspec import ComplexResiduals
import dearpygui.dearpygui as dpg
from deareis.signals import Signal
import deareis.signals as signals
from deareis.enums import (
    CNLSMethod,
    Context,
    Test,
    TestMode,
    cnls_method_to_label,
    label_to_cnls_method,
    label_to_test,
    label_to_test_mode,
    test_mode_to_label,
    test_to_label,
)
from deareis.utility import (
    format_number,
    pad_tab_labels,
)
from deareis.data import (
    DataSet,
    TestResult,
    TestSettings,
)
from deareis.gui.plots import (
    Bode,
    Impedance,
    Nyquist,
    Plot,
    Residuals,
)
import deareis.tooltips as tooltips
from deareis.tooltips import (
    attach_tooltip,
    update_tooltip,
)
import deareis.themes as themes
from deareis.gui.shared import (
    DataSetsCombo,
    ResultsCombo,
)


class SettingsMenu:
    def __init__(
        self,
        default_settings: TestSettings,
        label_pad: int,
        limited: bool = False,
        **kwargs,
    ):
        with dpg.group(horizontal=True):
            dpg.add_text("Test".rjust(label_pad))
            attach_tooltip(tooltips.kramers_kronig.test)
            self.test_combo: int = dpg.generate_uuid()
            dpg.add_combo(
                default_value=test_to_label[default_settings.test],
                items=list(label_to_test.keys()),
                callback=lambda s, a, u: self.update_settings(),
                width=-1,
                tag=self.test_combo,
            )
        with dpg.group(horizontal=True):
            dpg.add_text("Mode".rjust(label_pad))
            attach_tooltip(tooltips.kramers_kronig.mode)
            self.mode_combo: int = dpg.generate_uuid()
            dpg.add_combo(
                default_value=test_mode_to_label[default_settings.mode],
                items=list(label_to_test_mode.keys()),
                callback=lambda s, a, u: self.update_settings(),
                width=-1,
                tag=self.mode_combo,
            )
        with dpg.group(horizontal=True, show=not limited):
            self.num_RC_label: int = dpg.generate_uuid()
            num_RC_labels: List[str] = [
                "Max. num. RC elements".rjust(label_pad),
                "Number of RC elements".rjust(label_pad),
            ]
            dpg.add_text(
                num_RC_labels[0],
                user_data=num_RC_labels,
                tag=self.num_RC_label,
            )
            attach_tooltip(tooltips.kramers_kronig.max_num_RC)
            self.num_RC_slider: int = dpg.generate_uuid()
            dpg.add_slider_int(
                clamped=True,
                width=-1,
                tag=self.num_RC_slider,
            )
        with dpg.group(horizontal=True):
            dpg.add_text("Add capacitor in series".rjust(label_pad))
            attach_tooltip(tooltips.kramers_kronig.add_capacitance)
            self.add_cap_checkbox: int = dpg.generate_uuid()
            dpg.add_checkbox(
                default_value=default_settings.add_capacitance,
                tag=self.add_cap_checkbox,
            )
        with dpg.group(horizontal=True):
            dpg.add_text("Add inductor in series".rjust(label_pad))
            attach_tooltip(tooltips.kramers_kronig.add_inductance)
            self.add_ind_checkbox: int = dpg.generate_uuid()
            dpg.add_checkbox(
                default_value=default_settings.add_inductance,
                tag=self.add_ind_checkbox,
            )
        with dpg.group(horizontal=True):
            dpg.add_text("µ-criterion".rjust(label_pad))
            attach_tooltip(tooltips.kramers_kronig.mu_criterion)
            self.mu_crit_slider: int = dpg.generate_uuid()
            dpg.add_slider_float(
                default_value=default_settings.mu_criterion,
                min_value=0.01,
                max_value=0.99,
                clamped=True,
                format="%.2f",
                width=-1,
                tag=self.mu_crit_slider,
            )
        with dpg.group(horizontal=True):
            dpg.add_text("Fitting method".rjust(label_pad))
            attach_tooltip(tooltips.kramers_kronig.method)
            self.method_combo: int = dpg.generate_uuid()
            fitting_methods: List[str] = list(label_to_cnls_method.keys())
            fitting_methods.remove("Auto")
            dpg.add_combo(
                default_value=cnls_method_to_label.get(
                    default_settings.method,
                    fitting_methods[0],
                ),
                items=fitting_methods,
                width=-1,
                tag=self.method_combo,
            )
        with dpg.group(horizontal=True):
            dpg.add_text("Max. num. of func. eval.".rjust(label_pad))
            attach_tooltip(tooltips.kramers_kronig.nfev)
            self.max_nfev_input: int = dpg.generate_uuid()
            dpg.add_input_int(
                default_value=default_settings.max_nfev,
                min_value=0,
                min_clamped=True,
                step=0,
                on_enter=True,
                width=-1,
                tag=self.max_nfev_input,
            )
        self.update_settings()

    def get_settings(self) -> TestSettings:
        return TestSettings(
            test=label_to_test.get(dpg.get_value(self.test_combo), Test.COMPLEX),
            mode=label_to_test_mode.get(
                dpg.get_value(self.mode_combo), TestMode.EXPLORATORY
            ),
            num_RC=dpg.get_value(self.num_RC_slider),
            mu_criterion=dpg.get_value(self.mu_crit_slider),
            add_capacitance=dpg.get_value(self.add_cap_checkbox),
            add_inductance=dpg.get_value(self.add_ind_checkbox),
            method=label_to_cnls_method.get(
                dpg.get_value(self.method_combo), CNLSMethod.LEASTSQ
            ),
            max_nfev=dpg.get_value(self.max_nfev_input),
        )

    def set_settings(self, settings: TestSettings):
        assert type(settings) is TestSettings, settings
        dpg.set_value(self.test_combo, test_to_label.get(settings.test))
        dpg.set_value(self.mode_combo, test_mode_to_label.get(settings.mode))
        num_RC: int = settings.num_RC
        item_configuration: dict = dpg.get_item_configuration(self.num_RC_slider)
        if num_RC >= 2:
            if num_RC > item_configuration["max_value"]:
                num_RC = item_configuration["max_value"]
            dpg.set_value(self.num_RC_slider, num_RC)
        dpg.set_value(self.add_cap_checkbox, settings.add_capacitance)
        dpg.set_value(self.add_ind_checkbox, settings.add_inductance)
        dpg.set_value(self.mu_crit_slider, settings.mu_criterion)
        dpg.set_value(self.method_combo, cnls_method_to_label.get(settings.method))
        dpg.set_value(self.max_nfev_input, settings.max_nfev)
        self.update_settings()

    def update_settings(self, settings: Optional[TestSettings] = None):
        if settings is None:
            settings = self.get_settings()
        if settings.test == Test.CNLS:
            dpg.enable_item(self.add_ind_checkbox)
            dpg.enable_item(self.method_combo)
            dpg.enable_item(self.max_nfev_input)
        else:
            dpg.disable_item(self.add_ind_checkbox)
            dpg.set_value(self.add_ind_checkbox, True)
            dpg.disable_item(self.method_combo)
            dpg.disable_item(self.max_nfev_input)
        if settings.mode == TestMode.MANUAL:
            dpg.disable_item(self.mu_crit_slider)
            dpg.set_value(
                self.num_RC_label, dpg.get_item_user_data(self.num_RC_label)[1]
            )
        else:
            dpg.enable_item(self.mu_crit_slider)
            dpg.set_value(
                self.num_RC_label, dpg.get_item_user_data(self.num_RC_label)[0]
            )

    def update_num_RC_slider(self, data: Optional[DataSet]):
        min_num_RC: int = 0 if data is None else 2
        max_num_RC: int = 9999 if data is None else data.get_num_points()
        num_RC: int = dpg.get_value(self.num_RC_slider)
        if num_RC > max_num_RC:
            num_RC = max_num_RC
        elif num_RC < min_num_RC:
            num_RC = max_num_RC
        dpg.configure_item(
            self.num_RC_slider,
            default_value=num_RC,
            min_value=min_num_RC,
            max_value=max_num_RC,
        )

    def get_num_RC_labels(self) -> List[str]:
        return dpg.get_item_user_data(self.num_RC_label)

    def has_active_input(self) -> bool:
        return dpg.is_item_active(self.max_nfev_input)


# TODO: AbstractStatisticsTable
class StatisticsTable:
    def __init__(self):
        label_pad: int = 23
        self._header: int = dpg.generate_uuid()
        with dpg.collapsing_header(label=" Statistics", leaf=True, tag=self._header):
            self._table: int = dpg.generate_uuid()
            with dpg.table(
                borders_outerV=True,
                borders_outerH=True,
                borders_innerV=True,
                borders_innerH=True,
                scrollY=True,
                freeze_rows=1,
                height=18 + 23 * 3,
                tag=self._table,
            ):
                dpg.add_table_column(
                    label="Label".rjust(label_pad),
                    width_fixed=True,
                )
                dpg.add_table_column(
                    label="Value",
                    width_fixed=True,
                )
                label: str
                tooltip: str
                for (label, tooltip) in [
                    ("log X² (pseudo)", tooltips.kramers_kronig.pseudo_chisqr),
                    ("µ", tooltips.kramers_kronig.mu),
                    ("Number of RC elements", tooltips.kramers_kronig.num_RC),
                    ("Series resistance", tooltips.kramers_kronig.series_resistance),
                    ("Series capacitance", tooltips.kramers_kronig.series_capacitance),
                    ("Series inductance", tooltips.kramers_kronig.series_inductance),
                ]:
                    with dpg.table_row(parent=self._table):
                        dpg.add_text(label.rjust(label_pad))
                        attach_tooltip(tooltip)
                        tooltip_tag: int = dpg.generate_uuid()
                        dpg.add_text("", user_data=tooltip_tag)
                        attach_tooltip("", tag=tooltip_tag)

    def clear(self, hide: bool):
        if hide:
            dpg.hide_item(self._header)
        row: int
        for row in dpg.get_item_children(self._table, slot=1):
            tag: int = dpg.get_item_children(row, slot=1)[2]
            dpg.set_value(tag, "")
            dpg.hide_item(dpg.get_item_parent(dpg.get_item_user_data(tag)))

    def populate(self, test: TestResult):
        dpg.show_item(self._header)
        rows: List[int] = dpg.get_item_children(self._table, slot=1)
        cells: List[int] = []
        row: int
        for row in rows:
            cells.append(dpg.get_item_children(row, slot=1)[2])
        assert len(cells) == 6, cells
        R: float = test.get_series_resistance()
        C: float = test.get_series_capacitance()
        L: float = test.get_series_inductance()
        values: List[str] = [
            f"{log(test.pseudo_chisqr):.3f}",
            f"{test.mu:.3f}",
            f"{test.num_RC}",
            format_number(R, significants=3).strip() if not isnan(R) else "",
            format_number(C, significants=3).strip() if not isnan(C) else "",
            format_number(L, significants=3).strip() if not isnan(L) else "",
        ]
        num_rows: int = 0
        cell: int
        value: str
        for row, cell, value in zip(rows, cells, values):
            if value == "":
                dpg.hide_item(row)
                continue
            else:
                dpg.show_item(row)
                num_rows += 1
            dpg.set_value(cell, value)
            update_tooltip(dpg.get_item_user_data(cell), value)
            dpg.show_item(dpg.get_item_parent(dpg.get_item_user_data(cell)))
        dpg.set_item_height(self._table, 18 + 23 * max(1, num_rows))


# TODO: AbstractSettingsTable
class SettingsTable:
    def __init__(self):
        label_pad: int = 23
        self._header: int = dpg.generate_uuid()
        with dpg.collapsing_header(label=" Settings", leaf=True, tag=self._header):
            self._table: int = dpg.generate_uuid()
            with dpg.table(
                borders_outerV=True,
                borders_outerH=True,
                borders_innerV=True,
                borders_innerH=True,
                scrollY=True,
                freeze_rows=1,
                height=18 + 23 * 8,
                tag=self._table,
            ):
                dpg.add_table_column(
                    label="Label".rjust(label_pad),
                    width_fixed=True,
                )
                dpg.add_table_column(
                    label="Value",
                    width_fixed=True,
                )
                label: str
                for label in [
                    "Test",
                    "Mode",
                    "Number of RC elements",
                    "Add capacitor in series",
                    "Add inductor in series",
                    "µ-criterion",
                    "Fitting method",
                    "Max. num. func. eval.",
                ]:
                    with dpg.table_row(parent=self._table):
                        dpg.add_text(label.rjust(label_pad))
                        tooltip_tag: int = dpg.generate_uuid()
                        dpg.add_text("", user_data=tooltip_tag)
                        attach_tooltip("", tag=tooltip_tag)
            dpg.add_spacer(height=8)
            with dpg.group(horizontal=True):
                self._apply_settings_button: int = dpg.generate_uuid()
                dpg.add_button(
                    label="Apply settings",
                    callback=lambda s, a, u: signals.emit(
                        Signal.APPLY_TEST_SETTINGS,
                        **u,
                    ),
                    tag=self._apply_settings_button,
                    width=154,
                )
                attach_tooltip(tooltips.general.apply_settings)
                self._apply_mask_button: int = dpg.generate_uuid()
                dpg.add_button(
                    label="Apply mask",
                    callback=lambda s, a, u: signals.emit(
                        Signal.APPLY_DATA_SET_MASK,
                        **u,
                    ),
                    tag=self._apply_mask_button,
                    width=-1,
                )
                attach_tooltip(tooltips.general.apply_mask)

    def clear(self, hide: bool):
        if hide:
            dpg.hide_item(self._header)
        row: int
        for row in dpg.get_item_children(self._table, slot=1):
            tag: int = dpg.get_item_children(row, slot=1)[1]
            dpg.set_value(tag, "")
            dpg.hide_item(dpg.get_item_parent(dpg.get_item_user_data(tag)))

    def populate(self, test: TestResult, data: DataSet, num_RC_labels: List[str]):
        dpg.show_item(self._header)
        rows: List[int] = []
        cells: List[List[int]] = []
        row: int
        for row in dpg.get_item_children(self._table, slot=1):
            rows.append(row)
            cells.append(dpg.get_item_children(row, slot=1))
        assert len(rows) == len(cells) == 8, (
            rows,
            cells,
        )
        if test.settings.mode == TestMode.MANUAL:
            dpg.set_value(
                cells[1][0],
                num_RC_labels[1],
            )
        else:
            dpg.set_value(
                cells[1][0],
                num_RC_labels[0],
            )
        num_rows: int = 0
        tag: int
        value: str
        visible: bool
        for (row, tag, value, visible) in [
            (
                rows[0],
                cells[0][1],
                test_to_label.get(test.settings.test, ""),
                True,
            ),
            (
                rows[1],
                cells[1][1],
                test_mode_to_label.get(test.settings.mode, ""),
                True,
            ),
            (
                rows[2],
                cells[2][1],
                f"{test.settings.num_RC}",
                True,
            ),
            (
                rows[3],
                cells[3][1],
                "True" if test.settings.add_capacitance else "False",
                test.settings.add_capacitance,
            ),
            (
                rows[4],
                cells[4][1],
                "True" if test.settings.add_inductance else "False",
                test.settings.add_inductance,
            ),
            (
                rows[5],
                cells[5][1],
                f"{test.settings.mu_criterion:.2f}",
                test.settings.mode != TestMode.MANUAL,
            ),
            (
                rows[6],
                cells[6][1],
                cnls_method_to_label.get(test.settings.method, ""),
                test.settings.test == Test.CNLS,
            ),
            (
                rows[7],
                cells[7][1],
                f"{test.settings.max_nfev}",
                test.settings.test == Test.CNLS,
            ),
        ]:
            dpg.set_value(tag, value)
            update_tooltip(dpg.get_item_user_data(tag), value)
            dpg.show_item(dpg.get_item_parent(dpg.get_item_user_data(tag)))
            if visible:
                dpg.show_item(row)
                num_rows += 1
            else:
                dpg.hide_item(row)
        dpg.set_item_height(self._table, 18 + 23 * max(1, num_rows))
        dpg.set_item_user_data(
            self._apply_settings_button,
            {
                "settings": test.settings,
            },
        )
        dpg.set_item_user_data(
            self._apply_mask_button,
            {
                "data": data,
                "mask": test.mask,
                "test": test,
            },
        )


class TestResultsCombo(ResultsCombo):
    def selection_callback(self, sender: int, app_data: str, user_data: tuple):
        signals.emit(
            Signal.SELECT_TEST_RESULT,
            test=user_data[0].get(app_data),
            data=user_data[1],
        )

    def adjust_label(self, old: str, longest: int) -> str:
        i: int = old.rfind(" (")
        label: str
        timestamp: str
        label, timestamp = (old[:i], old[i + 1 :])
        return f"{label.ljust(longest)} {timestamp}"


class KramersKronigTab:
    def __init__(self, state):
        self.state = state
        self.queued_update: Optional[Callable] = None
        self.create_tab(state)
        self.set_settings(self.state.config.default_test_settings)

    def create_tab(self, state):
        self.tab: int = dpg.generate_uuid()
        label_pad: int = 24
        with dpg.tab(label="Kramers-Kronig", tag=self.tab):
            with dpg.child_window(border=False):
                with dpg.group(horizontal=True):
                    self.create_sidebar(state, label_pad)
                    self.create_plots()

    def create_sidebar(self, state, label_pad: int):
        self.sidebar_window: int = dpg.generate_uuid()
        self.sidebar_width: int = 350
        with dpg.child_window(
            border=False,
            width=self.sidebar_width,
            tag=self.sidebar_window,
        ):
            # TODO: Split into a separate class?
            with dpg.child_window(width=-1, height=220):
                self.settings_menu: SettingsMenu = SettingsMenu(
                    state.config.default_test_settings,
                    label_pad,
                )
                with dpg.group(horizontal=True):
                    self.visibility_item: int = dpg.generate_uuid()
                    dpg.add_text(
                        "?".rjust(label_pad),
                        tag=self.visibility_item,
                    )
                    attach_tooltip(tooltips.kramers_kronig.perform)
                    self.perform_test_button: int = dpg.generate_uuid()
                    dpg.add_button(
                        label="Perform",
                        callback=lambda s, a, u: signals.emit(
                            Signal.PERFORM_TEST,
                            data=u,
                            settings=self.get_settings(),
                        ),
                        user_data=None,
                        width=-70,
                        tag=self.perform_test_button,
                    )
                    dpg.add_button(
                        label="Batch",
                        callback=lambda s, a, u: signals.emit(
                            Signal.BATCH_PERFORM_ANALYSIS,
                            settings=self.get_settings(),
                        ),
                        width=-1,
                    )
            with dpg.child_window(width=-1, height=58):
                label_pad = 8
                with dpg.group(horizontal=True):
                    self.data_sets_combo: DataSetsCombo = DataSetsCombo(
                        label="Data set".rjust(label_pad),
                        width=-60,
                    )
                with dpg.group(horizontal=True):
                    self.results_combo: TestResultsCombo = TestResultsCombo(
                        label="Result".rjust(label_pad),
                        width=-60,
                    )
                    self.delete_button: int = dpg.generate_uuid()
                    dpg.add_button(
                        label="Delete",
                        callback=lambda s, a, u: signals.emit(
                            Signal.DELETE_TEST_RESULT,
                            **u,
                        ),
                        width=-1,
                        tag=self.delete_button,
                    )
                    attach_tooltip(tooltips.kramers_kronig.delete)
            with dpg.child_window(width=-1, height=-1):
                with dpg.group(show=False):
                    self.validity_text: int = dpg.generate_uuid()
                    dpg.bind_item_theme(
                        dpg.add_text(
                            "",
                            wrap=self.sidebar_width - 24,
                            tag=self.validity_text,
                        ),
                        themes.result.invalid,
                    )
                    dpg.add_spacer(height=8)
                self.statistics_table: StatisticsTable = StatisticsTable()
                dpg.add_spacer(height=8)
                self.settings_table: SettingsTable = SettingsTable()

    def create_plots(self):
        self.plot_window: int = dpg.generate_uuid()
        with dpg.child_window(border=False, tag=self.plot_window):
            self.create_residuals_plot()
            dpg.add_spacer(height=4)
            dpg.add_separator()
            dpg.add_spacer(height=4)
            self.plot_tab_bar: int = dpg.generate_uuid()
            with dpg.tab_bar(tag=self.plot_tab_bar):
                self.create_nyquist_plot()
                self.create_bode_plot()
                self.create_impedance_plot()
            pad_tab_labels(self.plot_tab_bar)
            self.plots: List[Plot] = [
                self.nyquist_plot,
                self.bode_plot,
                self.impedance_plot,
            ]

    def create_residuals_plot(self):
        self.residuals_plot_height: int = 300
        self.residuals_plot: Residuals = Residuals(
            width=-1,
            height=self.residuals_plot_height,
        )
        self.residuals_plot.plot(
            frequency=array([]),
            real=array([]),
            imaginary=array([]),
        )
        with dpg.group(horizontal=True):
            self.enlarge_residuals_button: int = dpg.generate_uuid()
            self.adjust_residuals_limits_checkbox: int = dpg.generate_uuid()
            dpg.add_button(
                label="Enlarge plot",
                callback=self.show_enlarged_residuals,
                tag=self.enlarge_residuals_button,
            )
            dpg.add_button(
                label="Copy as CSV",
                callback=lambda s, a, u: signals.emit(
                    Signal.COPY_PLOT_DATA,
                    plot=self.residuals_plot,
                    context=Context.KRAMERS_KRONIG_TAB,
                ),
            )
            attach_tooltip(tooltips.general.copy_plot_data_as_csv)
            dpg.add_checkbox(
                label="Adjust limits",
                default_value=True,
                tag=self.adjust_residuals_limits_checkbox,
            )
            attach_tooltip(tooltips.general.adjust_residuals_limits)

    def create_nyquist_plot(self):
        with dpg.tab(label="Nyquist"):
            self.nyquist_plot: Nyquist = Nyquist(
                width=-1,
                height=-24,
            )
            self.nyquist_plot.plot(
                real=array([]),
                imaginary=array([]),
                label="Data",
                line=False,
                theme=themes.nyquist.data,
            )
            self.nyquist_plot.plot(
                real=array([]),
                imaginary=array([]),
                label="Fit",
                line=False,
                fit=True,
                theme=themes.nyquist.simulation,
            )
            self.nyquist_plot.plot(
                real=array([]),
                imaginary=array([]),
                label="Fit",
                line=True,
                fit=True,
                theme=themes.nyquist.simulation,
                show_label=False,
            )
            with dpg.group(horizontal=True):
                self.enlarge_nyquist_button: int = dpg.generate_uuid()
                self.adjust_nyquist_limits_checkbox: int = dpg.generate_uuid()
                dpg.add_button(
                    label="Enlarge plot",
                    callback=self.show_enlarged_nyquist,
                    tag=self.enlarge_nyquist_button,
                )
                dpg.add_button(
                    label="Copy as CSV",
                    callback=lambda s, a, u: signals.emit(
                        Signal.COPY_PLOT_DATA,
                        plot=self.nyquist_plot,
                        context=Context.KRAMERS_KRONIG_TAB,
                    ),
                )
                attach_tooltip(tooltips.general.copy_plot_data_as_csv)
                dpg.add_checkbox(
                    label="Adjust limits",
                    default_value=True,
                    tag=self.adjust_nyquist_limits_checkbox,
                )
                attach_tooltip(tooltips.general.adjust_nyquist_limits)

    def create_bode_plot(self):
        with dpg.tab(label="Bode"):
            self.bode_plot: Bode = Bode(
                width=-1,
                height=-24,
            )
            self.bode_plot.plot(
                frequency=array([]),
                magnitude=array([]),
                phase=array([]),
                labels=(
                    "Mod(Z), d.",
                    "Phase(Z), d.",
                ),
                line=False,
                themes=(
                    themes.bode.magnitude_data,
                    themes.bode.phase_data,
                ),
            )
            self.bode_plot.plot(
                frequency=array([]),
                magnitude=array([]),
                phase=array([]),
                labels=(
                    "Mod(Z), f.",
                    "Phase(Z), f.",
                ),
                line=False,
                fit=True,
                themes=(
                    themes.bode.magnitude_simulation,
                    themes.bode.phase_simulation,
                ),
            )
            self.bode_plot.plot(
                frequency=array([]),
                magnitude=array([]),
                phase=array([]),
                labels=(
                    "Mod(Z), f.",
                    "Phase(Z), f.",
                ),
                line=True,
                fit=True,
                themes=(
                    themes.bode.magnitude_simulation,
                    themes.bode.phase_simulation,
                ),
                show_labels=False,
            )
            with dpg.group(horizontal=True):
                self.enlarge_bode_button: int = dpg.generate_uuid()
                self.adjust_bode_limits_checkbox: int = dpg.generate_uuid()
                dpg.add_button(
                    label="Enlarge plot",
                    callback=self.show_enlarged_bode,
                    tag=self.enlarge_bode_button,
                )
                dpg.add_button(
                    label="Copy as CSV",
                    callback=lambda s, a, u: signals.emit(
                        Signal.COPY_PLOT_DATA,
                        plot=self.bode_plot,
                        context=Context.KRAMERS_KRONIG_TAB,
                    ),
                )
                attach_tooltip(tooltips.general.copy_plot_data_as_csv)
                dpg.add_checkbox(
                    label="Adjust limits",
                    default_value=True,
                    tag=self.adjust_bode_limits_checkbox,
                )
                attach_tooltip(tooltips.general.adjust_bode_limits)

    def create_impedance_plot(self):
        with dpg.tab(label="Real & Imag."):
            self.impedance_plot: Impedance = Impedance(
                width=-1,
                height=-24,
            )
            self.impedance_plot.plot(
                frequency=array([]),
                real=array([]),
                imaginary=array([]),
                labels=(
                    "Re(Z), d.",
                    "Im(Z), d.",
                ),
                line=False,
                themes=(
                    themes.impedance.real_data,
                    themes.impedance.imaginary_data,
                ),
            )
            self.impedance_plot.plot(
                frequency=array([]),
                real=array([]),
                imaginary=array([]),
                labels=(
                    "Re(Z), f.",
                    "Im(Z), f.",
                ),
                line=False,
                fit=True,
                themes=(
                    themes.impedance.real_simulation,
                    themes.impedance.imaginary_simulation,
                ),
            )
            self.impedance_plot.plot(
                frequency=array([]),
                real=array([]),
                imaginary=array([]),
                labels=(
                    "Re(Z), f.",
                    "Im(Z), f.",
                ),
                line=True,
                fit=True,
                themes=(
                    themes.impedance.real_simulation,
                    themes.impedance.imaginary_simulation,
                ),
                show_labels=False,
            )
            with dpg.group(horizontal=True):
                self.enlarge_impedance_button: int = dpg.generate_uuid()
                self.adjust_impedance_limits_checkbox: int = dpg.generate_uuid()
                dpg.add_button(
                    label="Enlarge plot",
                    callback=self.show_enlarged_impedance,
                    tag=self.enlarge_impedance_button,
                )
                dpg.add_button(
                    label="Copy as CSV",
                    callback=lambda s, a, u: signals.emit(
                        Signal.COPY_PLOT_DATA,
                        plot=self.impedance_plot,
                        context=Context.KRAMERS_KRONIG_TAB,
                    ),
                )
                attach_tooltip(tooltips.general.copy_plot_data_as_csv)
                dpg.add_checkbox(
                    label="Adjust limits",
                    default_value=True,
                    tag=self.adjust_impedance_limits_checkbox,
                )
                attach_tooltip(tooltips.general.adjust_impedance_limits)

    def is_visible(self) -> bool:
        return dpg.is_item_visible(self.visibility_item)

    def resize(self, width: int, height: int):
        if not self.is_visible():
            return
        width, height = dpg.get_item_rect_size(self.plot_window)
        height -= self.residuals_plot_height + 24 * 4 - 1
        for plot in self.plots:
            plot.resize(-1, height)

    def clear(self, hide: bool = True):
        self.data_sets_combo.clear()
        self.results_combo.clear()
        self.statistics_table.clear(hide=hide)
        self.settings_table.clear(hide=hide)
        dpg.set_item_user_data(self.perform_test_button, None)
        self.residuals_plot.clear(delete=False)
        self.nyquist_plot.clear(delete=False)
        self.bode_plot.clear(delete=False)
        self.impedance_plot.clear(delete=False)

    def get_settings(self) -> TestSettings:
        return self.settings_menu.get_settings()

    def set_settings(self, settings: TestSettings):
        self.settings_menu.set_settings(settings)

    def populate_data_sets(self, labels: List[str], lookup: Dict[str, DataSet]):
        assert type(labels) is list, labels
        assert type(lookup) is dict, lookup
        self.data_sets_combo.populate(labels, lookup)

    def populate_tests(self, lookup: Dict[str, TestResult], data: Optional[DataSet]):
        assert type(lookup) is dict, lookup
        assert type(data) is DataSet or data is None, data
        self.results_combo.populate(lookup, data)
        dpg.hide_item(dpg.get_item_parent(self.validity_text))
        if data is not None and self.results_combo.labels:
            signals.emit(
                Signal.SELECT_TEST_RESULT,
                test=self.results_combo.get(),
                data=data,
            )
        else:
            self.statistics_table.clear(hide=True)
            self.settings_table.clear(hide=True)
            self.select_data_set(data)

    def get_next_data_set(self) -> Optional[DataSet]:
        return self.data_sets_combo.get_next()

    def get_previous_data_set(self) -> Optional[DataSet]:
        return self.data_sets_combo.get_previous()

    def get_next_result(self) -> Optional[TestResult]:
        return self.results_combo.get_next()

    def get_previous_result(self) -> Optional[TestResult]:
        return self.results_combo.get_previous()

    def select_data_set(self, data: Optional[DataSet]):
        assert type(data) is DataSet or data is None, data
        self.clear(hide=data is None)
        dpg.set_item_user_data(self.perform_test_button, data)
        self.settings_menu.update_num_RC_slider(data)
        if data is None:
            return
        self.data_sets_combo.set(data.get_label())
        real: ndarray
        imag: ndarray
        real, imag = data.get_nyquist_data()
        self.nyquist_plot.update(
            index=0,
            real=real,
            imaginary=imag,
        )
        freq: ndarray
        mag: ndarray
        phase: ndarray
        freq, mag, phase = data.get_bode_data()
        self.bode_plot.update(
            index=0,
            frequency=freq,
            magnitude=mag,
            phase=phase,
        )
        self.impedance_plot.update(
            index=0,
            frequency=freq,
            real=real,
            imaginary=imag,
        )

    def assert_test_up_to_date(self, test: TestResult, data: DataSet):
        # Check if the number of unmasked points is the same
        Z_exp: ndarray = data.get_impedances()
        Z_test: ndarray = test.get_impedances()
        assert Z_exp.shape == Z_test.shape, "The number of data points differ!"
        # Check if the masks are the same
        mask_exp: Dict[int, bool] = data.get_mask()
        mask_test: Dict[int, bool] = {
            k: test.mask.get(k, mask_exp.get(k, False)) for k in test.mask
        }
        num_masked_exp: int = list(data.get_mask().values()).count(True)
        num_masked_test: int = list(test.mask.values()).count(True)
        assert num_masked_exp == num_masked_test, "The masks are different sizes!"
        i: int
        for i in mask_test.keys():
            assert (
                i in mask_exp
            ), f"The data set does not have a point at index {i + 1}!"
            assert (
                mask_exp[i] == mask_test[i]
            ), f"The data set's mask differs at index {i + 1}!"
        # Check if the frequencies and impedances are the same
        assert allclose(
            test.get_frequencies(),
            data.get_frequencies(),
        ), "The frequencies differ!"
        residuals: ComplexResiduals = _calculate_residuals(Z_exp, Z_test)
        assert allclose(test.residuals.real, residuals.real) and allclose(
            test.residuals.imag, residuals.imag
        ), "The data set's impedances differ from what they were when the test was performed!"

    def select_test_result(self, test: Optional[TestResult], data: Optional[DataSet]):
        assert type(test) is TestResult or test is None, test
        assert type(data) is DataSet or data is None, data
        dpg.set_item_user_data(
            self.delete_button,
            {
                "test": test,
                "data": data,
            },
        )
        if not self.is_visible():
            self.queued_update = lambda: self.select_test_result(test, data)
            return
        self.queued_update = None
        self.select_data_set(data)
        if test is None or data is None:
            if dpg.get_value(self.adjust_residuals_limits_checkbox):
                self.residuals_plot.queue_limits_adjustment()
            if dpg.get_value(self.adjust_nyquist_limits_checkbox):
                self.nyquist_plot.queue_limits_adjustment()
            if dpg.get_value(self.adjust_bode_limits_checkbox):
                self.bode_plot.queue_limits_adjustment()
            if dpg.get_value(self.adjust_impedance_limits_checkbox):
                self.impedance_plot.queue_limits_adjustment()
            return
        self.results_combo.set(test.get_label())
        message: str
        try:
            self.assert_test_up_to_date(test, data)
            dpg.hide_item(dpg.get_item_parent(self.validity_text))
        except AssertionError as message:
            dpg.set_value(
                self.validity_text,
                f"Test result is not valid for the current state of the data set!\n\n{message}",
            )
            dpg.show_item(dpg.get_item_parent(self.validity_text))
        self.statistics_table.populate(test)
        self.settings_table.populate(
            test,
            data,
            self.settings_menu.get_num_RC_labels(),
        )
        freq: ndarray
        real: ndarray
        imag: ndarray
        freq, real, imag = test.get_residuals_data()
        self.residuals_plot.update(
            index=0,
            frequency=freq,
            real=real,
            imaginary=imag,
        )
        real, imag = test.get_nyquist_data()
        self.nyquist_plot.update(
            index=1,
            real=real,
            imaginary=imag,
        )
        real, imag = test.get_nyquist_data(
            num_per_decade=self.state.config.num_per_decade_in_simulated_lines
        )
        self.nyquist_plot.update(
            index=2,
            real=real,
            imaginary=imag,
        )
        mag: ndarray
        phase: ndarray
        freq, mag, phase = test.get_bode_data()
        self.bode_plot.update(
            index=1,
            frequency=freq,
            magnitude=mag,
            phase=phase,
        )
        freq, mag, phase = test.get_bode_data(
            num_per_decade=self.state.config.num_per_decade_in_simulated_lines
        )
        self.bode_plot.update(
            index=2,
            frequency=freq,
            magnitude=mag,
            phase=phase,
        )
        freq = test.get_frequencies()
        Z: ndarray = test.get_impedances()
        self.impedance_plot.update(
            index=1,
            frequency=freq,
            real=Z.real,
            imaginary=-Z.imag,
        )
        freq = test.get_frequencies(
            num_per_decade=self.state.config.num_per_decade_in_simulated_lines
        )
        Z: ndarray = test.get_impedances(
            num_per_decade=self.state.config.num_per_decade_in_simulated_lines
        )
        self.impedance_plot.update(
            index=2,
            frequency=freq,
            real=Z.real,
            imaginary=-Z.imag,
        )
        if dpg.get_value(self.adjust_residuals_limits_checkbox):
            self.residuals_plot.queue_limits_adjustment()
        if dpg.get_value(self.adjust_nyquist_limits_checkbox):
            self.nyquist_plot.queue_limits_adjustment()
        if dpg.get_value(self.adjust_bode_limits_checkbox):
            self.bode_plot.queue_limits_adjustment()
        if dpg.get_value(self.adjust_impedance_limits_checkbox):
            self.impedance_plot.queue_limits_adjustment()

    def next_plot_tab(self):
        tabs: List[int] = dpg.get_item_children(self.plot_tab_bar, slot=1)
        index: int = tabs.index(dpg.get_value(self.plot_tab_bar)) + 1
        dpg.set_value(self.plot_tab_bar, tabs[index % len(tabs)])

    def previous_plot_tab(self):
        tabs: List[int] = dpg.get_item_children(self.plot_tab_bar, slot=1)
        index: int = tabs.index(dpg.get_value(self.plot_tab_bar)) - 1
        dpg.set_value(self.plot_tab_bar, tabs[index % len(tabs)])

    def show_enlarged_nyquist(self):
        signals.emit(
            Signal.SHOW_ENLARGED_PLOT,
            plot=self.nyquist_plot,
            adjust_limits=dpg.get_value(self.adjust_nyquist_limits_checkbox),
        )

    def show_enlarged_bode(self):
        signals.emit(
            Signal.SHOW_ENLARGED_PLOT,
            plot=self.bode_plot,
            adjust_limits=dpg.get_value(self.adjust_bode_limits_checkbox),
        )

    def show_enlarged_impedance(self):
        signals.emit(
            Signal.SHOW_ENLARGED_PLOT,
            plot=self.impedance_plot,
            adjust_limits=dpg.get_value(self.adjust_impedance_limits_checkbox),
        )

    def show_enlarged_residuals(self):
        signals.emit(
            Signal.SHOW_ENLARGED_PLOT,
            plot=self.residuals_plot,
            adjust_limits=dpg.get_value(self.adjust_residuals_limits_checkbox),
        )

    def has_active_input(self) -> bool:
        return self.settings_menu.has_active_input()
