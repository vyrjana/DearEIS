# DearEIS is licensed under the GPLv3 or later (https://www.gnu.org/licenses/gpl-3.0.html).
# Copyright 2024 DearEIS developers
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
    Tuple,
    Optional,
)
from numpy import (
    allclose,
    array,
    complex128,
    isnan,
    log10 as log,
    ndarray,
)
from pyimpspec.analysis.utility import _calculate_residuals
from pyimpspec import ComplexResiduals
from pandas import DataFrame
import dearpygui.dearpygui as dpg
from deareis.signals import Signal
import deareis.signals as signals
from deareis.enums import (
    CNLSMethod,
    Context,
    KramersKronigTest,
    KramersKronigMode,
    KramersKronigRepresentation,
    cnls_method_to_label,
    label_to_cnls_method,
    label_to_test,
    label_to_test_mode,
    label_to_test_representation,
    test_mode_to_label,
    test_representation_to_label,
    test_to_label,
)
from deareis.utility import (
    format_number,
    pad_tab_labels,
)
from deareis.data import (
    DataSet,
    KramersKronigResult,
    KramersKronigSettings,
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
from deareis.gui.widgets.combo import Combo
from deareis.typing.helpers import Tag


class SettingsMenu:
    def __init__(
        self,
        default_settings: KramersKronigSettings,
        label_pad: int,
        limited: bool,
        state,
        **kwargs,
    ):
        self.state = state

        with dpg.group(horizontal=True):
            dpg.add_text("Test".rjust(label_pad))
            attach_tooltip(tooltips.kramers_kronig.test)

            self.test_combo: Combo = Combo(
                default_value=test_to_label[default_settings.test],
                items=list(label_to_test.keys()),
                callback=lambda s, a, u: self.update_settings(),
                user_data=label_to_test,
                width=-1,
            )

        with dpg.group(horizontal=True):
            dpg.add_text("Mode".rjust(label_pad))
            attach_tooltip(tooltips.kramers_kronig.mode)

            self.mode_combo: Combo = Combo(
                default_value=test_mode_to_label[default_settings.mode],
                items=list(label_to_test_mode.keys()),
                callback=lambda s, a, u: self.update_settings(),
                user_data=label_to_test_mode,
                width=-1,
            )

        with dpg.group(horizontal=True):
            dpg.add_text("Representation".rjust(label_pad))
            attach_tooltip(tooltips.kramers_kronig.representation_setting)

            self.representation_combo: Combo = Combo(
                default_value=test_representation_to_label[
                    default_settings.representation
                ],
                items=list(label_to_test_representation.keys()),
                callback=lambda s, a, u: self.update_settings(),
                user_data=label_to_test_representation,
                width=-1,
            )

        with dpg.group(horizontal=True):
            dpg.add_text("Add parallel/series".rjust(label_pad))
            self.add_cap_checkbox: Tag = dpg.generate_uuid()
            dpg.add_checkbox(
                default_value=default_settings.add_capacitance,
                label="Cap.   ",
                tag=self.add_cap_checkbox,
            )
            attach_tooltip(tooltips.kramers_kronig.add_capacitance)

            self.add_ind_checkbox: Tag = dpg.generate_uuid()
            dpg.add_checkbox(
                default_value=default_settings.add_inductance,
                label="Ind.   ",
                tag=self.add_ind_checkbox,
            )
            attach_tooltip(tooltips.kramers_kronig.add_inductance)

        with dpg.group(horizontal=True, show=not limited):
            self.num_RC_label: Tag = dpg.generate_uuid()
            dpg.add_text(
                "Number of RC elements".rjust(label_pad),
                tag=self.num_RC_label,
            )
            attach_tooltip(tooltips.kramers_kronig.num_RC)

            self.num_RC_input: Tag = dpg.generate_uuid()
            dpg.add_input_int(
                default_value=1,
                min_value=1,
                min_clamped=True,
                max_value=9999,
                max_clamped=True,
                step=0,
                on_enter=True,
                width=-1,
                tag=self.num_RC_input,
            )

        with dpg.group(horizontal=True):
            dpg.add_text("Log Fext".rjust(label_pad))
            attach_tooltip(tooltips.kramers_kronig.log_F_ext)

            self.log_F_ext_input: Tag = dpg.generate_uuid()
            dpg.add_input_float(
                default_value=default_settings.log_F_ext,
                step=0.0,
                on_enter=True,
                width=-1,
                tag=self.log_F_ext_input,
            )

        with dpg.group(horizontal=True):
            dpg.add_text("Minimum log Fext".rjust(label_pad))
            attach_tooltip(tooltips.kramers_kronig.min_log_F_ext)

            self.min_log_F_ext_input: Tag = dpg.generate_uuid()
            dpg.add_input_float(
                default_value=default_settings.min_log_F_ext,
                max_value=0.0,
                max_clamped=True,
                step=0.0,
                on_enter=True,
                width=-1,
                tag=self.min_log_F_ext_input,
            )

        with dpg.group(horizontal=True):
            dpg.add_text("Maximum log Fext".rjust(label_pad))
            attach_tooltip(tooltips.kramers_kronig.max_log_F_ext)

            self.max_log_F_ext_input: Tag = dpg.generate_uuid()
            dpg.add_input_float(
                default_value=default_settings.max_log_F_ext,
                min_value=0.0,
                min_clamped=True,
                step=0.0,
                on_enter=True,
                width=-1,
                tag=self.max_log_F_ext_input,
            )

        with dpg.group(horizontal=True):
            dpg.add_text("Number of Fext eval.".rjust(label_pad))
            attach_tooltip(tooltips.kramers_kronig.num_F_ext_evaluations)

            self.num_F_ext_evaluations_input: Tag = dpg.generate_uuid()
            dpg.add_input_int(
                default_value=default_settings.num_F_ext_evaluations,
                step=0,
                on_enter=True,
                width=-1,
                callback=lambda s, a, u: self.update_settings(),
                tag=self.num_F_ext_evaluations_input,
            )

        with dpg.group(horizontal=True):
            self.rapid_F_ext_evaluations_checkbox: Tag = dpg.generate_uuid()
            dpg.add_text("Rapid Fext eval.".rjust(label_pad))
            attach_tooltip(tooltips.kramers_kronig.rapid_F_ext_evaluations)

            dpg.add_checkbox(
                default_value=default_settings.rapid_F_ext_evaluations,
                tag=self.rapid_F_ext_evaluations_checkbox,
            )

        with dpg.group(horizontal=True):
            dpg.add_text("CNLS method".rjust(label_pad))
            attach_tooltip(tooltips.kramers_kronig.cnls_method)

            fitting_methods: List[str] = list(label_to_cnls_method.keys())
            fitting_methods.remove("Auto")
            self.cnls_method_combo: Combo = Combo(
                default_value=cnls_method_to_label.get(
                    default_settings.cnls_method,
                    fitting_methods[0],
                ),
                items=fitting_methods,
                user_data=label_to_cnls_method,
                width=-1,
            )

        with dpg.group(horizontal=True):
            dpg.add_text("Max. num. of func. eval.".rjust(label_pad))
            attach_tooltip(tooltips.kramers_kronig.nfev)

            self.max_nfev_input: Tag = dpg.generate_uuid()
            dpg.add_input_int(
                default_value=default_settings.max_nfev,
                min_value=0,
                min_clamped=True,
                step=0,
                on_enter=True,
                width=-1,
                tag=self.max_nfev_input,
            )

        with dpg.group(horizontal=True):
            dpg.add_text("Timeout".rjust(label_pad))
            attach_tooltip(tooltips.kramers_kronig.timeout)

            self.timeout_input: Tag = dpg.generate_uuid()
            dpg.add_input_int(
                default_value=default_settings.timeout,
                min_value=1,
                min_clamped=True,
                step=0,
                on_enter=True,
                width=-1,
                tag=self.timeout_input,
            )

        self.update_settings()

    def get_settings(self) -> KramersKronigSettings:
        return KramersKronigSettings(
            test=self.test_combo.get_value(),
            mode=self.mode_combo.get_value(),
            representation=self.representation_combo.get_value(),
            add_capacitance=dpg.get_value(self.add_cap_checkbox),
            add_inductance=dpg.get_value(self.add_ind_checkbox),
            num_RC=dpg.get_value(self.num_RC_input),
            min_log_F_ext=dpg.get_value(self.min_log_F_ext_input),
            max_log_F_ext=dpg.get_value(self.max_log_F_ext_input),
            log_F_ext=dpg.get_value(self.log_F_ext_input),
            num_F_ext_evaluations=dpg.get_value(self.num_F_ext_evaluations_input),
            rapid_F_ext_evaluations=dpg.get_value(
                self.rapid_F_ext_evaluations_checkbox
            ),
            cnls_method=self.cnls_method_combo.get_value(),
            max_nfev=dpg.get_value(self.max_nfev_input),
            timeout=dpg.get_value(self.timeout_input),
            suggestion_settings=self.state.kramers_kronig_suggestion_settings,
        )

    def set_settings(self, settings: KramersKronigSettings):
        assert type(settings) is KramersKronigSettings, settings

        self.test_combo.set_value(settings.test)
        self.mode_combo.set_value(settings.mode)
        self.representation_combo.set_value(settings.representation)
        dpg.set_value(
            self.add_cap_checkbox,
            settings.add_capacitance,
        )
        dpg.set_value(
            self.add_ind_checkbox,
            settings.add_inductance,
        )

        num_RC: int = settings.num_RC
        item_configuration: dict = dpg.get_item_configuration(self.num_RC_input)
        if num_RC >= 1:
            if num_RC > item_configuration["max_value"]:
                num_RC = item_configuration["max_value"]
            dpg.set_value(self.num_RC_input, num_RC)

        dpg.set_value(
            self.min_log_F_ext_input,
            settings.min_log_F_ext,
        )
        dpg.set_value(
            self.max_log_F_ext_input,
            settings.max_log_F_ext,
        )
        dpg.set_value(
            self.log_F_ext_input,
            settings.log_F_ext,
        )
        dpg.set_value(
            self.num_F_ext_evaluations_input,
            settings.num_F_ext_evaluations,
        )
        dpg.set_value(
            self.rapid_F_ext_evaluations_checkbox,
            settings.rapid_F_ext_evaluations,
        )

        self.cnls_method_combo.set_value(settings.cnls_method)
        dpg.set_value(
            self.max_nfev_input,
            settings.max_nfev,
        )
        dpg.set_value(
            self.timeout_input,
            settings.timeout,
        )

        self.update_settings()

    def update_settings(self, settings: Optional[KramersKronigSettings] = None):
        if settings is None:
            settings = self.get_settings()

        if settings.test in (KramersKronigTest.COMPLEX, KramersKronigTest.REAL, KramersKronigTest.IMAGINARY):
            dpg.disable_item(self.add_ind_checkbox)
            dpg.set_value(self.add_ind_checkbox, True)
        else:
            dpg.enable_item(self.add_ind_checkbox)

        if settings.mode == KramersKronigMode.MANUAL:
            dpg.enable_item(self.num_RC_input)
            dpg.set_value(self.num_F_ext_evaluations_input, 0)
            settings = self.get_settings()
        else:
            dpg.disable_item(self.num_RC_input)

        if settings.test == KramersKronigTest.CNLS:
            self.cnls_method_combo.enable()
            dpg.enable_item(self.max_nfev_input)
            dpg.enable_item(self.timeout_input)
        else:
            self.cnls_method_combo.disable()
            dpg.disable_item(self.max_nfev_input)
            dpg.disable_item(self.timeout_input)

        if settings.num_F_ext_evaluations != 0:
            dpg.enable_item(self.min_log_F_ext_input)
            dpg.enable_item(self.max_log_F_ext_input)
            dpg.disable_item(self.log_F_ext_input)
            dpg.enable_item(self.rapid_F_ext_evaluations_checkbox)
        else:
            dpg.disable_item(self.min_log_F_ext_input)
            dpg.disable_item(self.max_log_F_ext_input)
            dpg.enable_item(self.log_F_ext_input)
            dpg.disable_item(self.rapid_F_ext_evaluations_checkbox)

        dpg.set_value(
            self.num_F_ext_evaluations_input,
            settings.num_F_ext_evaluations,
        )

    def update_num_RC_input(self, data: Optional[DataSet]):
        min_num_RC: int = 1
        max_num_RC: int = 999999 if data is None else data.get_num_points()

        num_RC: int = dpg.get_value(self.num_RC_input)
        if num_RC > max_num_RC:
            num_RC = max_num_RC
        elif num_RC < min_num_RC:
            num_RC = max_num_RC

        dpg.configure_item(
            self.num_RC_input,
            default_value=num_RC,
            min_value=min_num_RC,
            max_value=max_num_RC,
        )

    def has_active_input(self) -> bool:
        for tag in (
            self.log_F_ext_input,
            self.max_log_F_ext_input,
            self.max_nfev_input,
            self.min_log_F_ext_input,
            self.num_F_ext_evaluations_input,
            self.num_RC_input,
            self.timeout_input,
        ):
            if dpg.is_item_active(tag):
                return True

        return False


# TODO: AbstractStatisticsTable
class StatisticsTable:
    def __init__(self):
        label_pad: int = 26
        self._header: Tag = dpg.generate_uuid()
        with dpg.collapsing_header(label=" Statistics", leaf=True, tag=self._header):
            self._table: Tag = dpg.generate_uuid()
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
                for label, tooltip in [
                    (
                        "Immittance representation",
                        tooltips.kramers_kronig.representation,
                    ),
                    (
                        "log X² (pseudo)",
                        tooltips.kramers_kronig.pseudo_chisqr,
                    ),
                    (
                        "log Fext",
                        tooltips.kramers_kronig.log_F_ext,
                    ),
                    (
                        "Number of RC elements",
                        tooltips.kramers_kronig.num_RC,
                    ),
                    (
                        "Series resistance",
                        tooltips.kramers_kronig.series_resistance,
                    ),
                    (
                        "Series capacitance",
                        tooltips.kramers_kronig.series_capacitance,
                    ),
                    (
                        "Series inductance",
                        tooltips.kramers_kronig.series_inductance,
                    ),
                    (
                        "Parallel resistance",
                        tooltips.kramers_kronig.parallel_resistance,
                    ),
                    (
                        "Parallel capacitance",
                        tooltips.kramers_kronig.parallel_capacitance,
                    ),
                    (
                        "Parallel inductance",
                        tooltips.kramers_kronig.parallel_inductance,
                    ),
                    (
                        "Estimated noise SD",
                        tooltips.kramers_kronig.estimated_noise_sd,
                    ),
                    (
                        "Kolmogorov-Smirnov (real)",
                        tooltips.kramers_kronig.kolmogorov_smirnov,
                    ),
                    (
                        "Kolmogorov-Smirnov (imag.)",
                        tooltips.kramers_kronig.kolmogorov_smirnov,
                    ),
                    (
                        "Shapiro-Wilk (real)",
                        tooltips.kramers_kronig.shapiro_wilk,
                    ),
                    (
                        "Shapiro-Wilk (imag.)",
                        tooltips.kramers_kronig.shapiro_wilk,
                    ),
                    (
                        "Lilliefors (real)",
                        tooltips.kramers_kronig.lilliefors,
                    ),
                    (
                        "Lilliefors (imag.)",
                        tooltips.kramers_kronig.lilliefors,
                    ),
                    (
                        "Mean of resid. (real)",
                        tooltips.kramers_kronig.residuals_means,
                    ),
                    (
                        "Mean of resid. (imag.)",
                        tooltips.kramers_kronig.residuals_means,
                    ),
                    (
                        "SD of resid. (real)",
                        tooltips.kramers_kronig.residuals_sd,
                    ),
                    (
                        "SD of resid. (imag.)",
                        tooltips.kramers_kronig.residuals_sd,
                    ),
                    (
                        "Resid. within 1 SD (real)",
                        tooltips.kramers_kronig.residuals_within_n_sd,
                    ),
                    (
                        "Resid. within 1 SD (imag.)",
                        tooltips.kramers_kronig.residuals_within_n_sd,
                    ),
                    (
                        "Resid. within 2 SD (real)",
                        tooltips.kramers_kronig.residuals_within_n_sd,
                    ),
                    (
                        "Resid. within 2 SD (imag.)",
                        tooltips.kramers_kronig.residuals_within_n_sd,
                    ),
                    (
                        "Resid. within 3 SD (real)",
                        tooltips.kramers_kronig.residuals_within_n_sd,
                    ),
                    (
                        "Resid. within 3 SD (imag.)",
                        tooltips.kramers_kronig.residuals_within_n_sd,
                    ),
                ]:
                    with dpg.table_row(parent=self._table):
                        dpg.add_text(label.rjust(label_pad))
                        attach_tooltip(tooltip)

                        tooltip_tag: Tag = dpg.generate_uuid()
                        dpg.add_text("", user_data=tooltip_tag)
                        attach_tooltip("", tag=tooltip_tag)

    def clear(self, hide: bool):
        if hide:
            dpg.hide_item(self._header)
        row: int
        for row in dpg.get_item_children(self._table, slot=1):
            tag: Tag = dpg.get_item_children(row, slot=1)[2]
            dpg.set_value(tag, "")
            dpg.hide_item(dpg.get_item_parent(dpg.get_item_user_data(tag)))

    def assign_theme_to_p_value(
        self,
        p: float,
        alpha_1: float = 0.05,
        alpha_2: float = 0.01,
    ) -> int:
        if p < alpha_2:
            return themes.fitting.huge_error
        elif p < alpha_1:
            return themes.fitting.large_error
        else:
            return themes.fitting.default_statistic

    def populate(self, test: KramersKronigResult):
        dpg.show_item(self._header)
        rows: List[Tag] = dpg.get_item_children(self._table, slot=1)
        cells: List[Tag] = []
        row: Tag
        for row in rows:
            cells.append(dpg.get_item_children(row, slot=1)[2])

        assert len(cells) == 27, cells

        series_R: float = test.get_series_resistance()
        series_C: float = test.get_series_capacitance()
        series_L: float = test.get_series_inductance()

        parallel_R: float = test.get_parallel_resistance()
        parallel_C: float = test.get_parallel_capacitance()
        parallel_L: float = test.get_parallel_inductance()

        # TODO: Make the alpha_1 and alpha_2 thresholds configurable?
        alpha_1: float = 0.05
        alpha_2: float = 0.01
        values: List[Tuple[str, int]] = [
            (
                "Admittance" if test.admittance else "Impedance",
                -1,
            ),
            (
                f"{log(test.pseudo_chisqr):.3f}",
                -1,
            ),
            (
                f"{test.get_log_F_ext():.3f}",
                -1,
            ),
            (
                f"{test.num_RC}",
                -1,
            ),
            (
                (
                    format_number(series_R, significants=3).strip()
                    if not isnan(series_R)
                    else ""
                ),
                -1,
            ),
            (
                (
                    format_number(series_C, significants=3).strip()
                    if not isnan(series_C)
                    else ""
                ),
                -1,
            ),
            (
                (
                    format_number(series_L, significants=3).strip()
                    if not isnan(series_L)
                    else ""
                ),
                -1,
            ),
            (
                (
                    format_number(parallel_R, significants=3).strip()
                    if not isnan(parallel_R)
                    else ""
                ),
                -1,
            ),
            (
                (
                    format_number(parallel_C, significants=3).strip()
                    if not isnan(parallel_C)
                    else ""
                ),
                -1,
            ),
            (
                (
                    format_number(parallel_L, significants=3).strip()
                    if not isnan(parallel_L)
                    else ""
                ),
                -1,
            ),
            (
                f"{test.get_estimated_percent_noise():.2g}",
                -1,
            ),
            (
                f"{test.kolmogorov_smirnov[0]:.3f}",
                self.assign_theme_to_p_value(test.kolmogorov_smirnov[0]),
            ),
            (
                f"{test.kolmogorov_smirnov[1]:.3f}",
                self.assign_theme_to_p_value(test.kolmogorov_smirnov[1]),
            ),
            (
                f"{test.shapiro_wilk[0]:.3f}",
                self.assign_theme_to_p_value(test.shapiro_wilk[0]),
            ),
            (
                f"{test.shapiro_wilk[1]:.3f}",
                self.assign_theme_to_p_value(test.shapiro_wilk[1]),
            ),
            (
                f"{test.lilliefors[0]:.3f}",
                self.assign_theme_to_p_value(test.lilliefors[0]),
            ),
            (
                f"{test.lilliefors[1]:.3f}",
                self.assign_theme_to_p_value(test.lilliefors[1]),
            ),
            (
                f"{test.residuals_means[0]:.3g}",
                -1,
            ),
            (
                f"{test.residuals_means[1]:.3g}",
                -1,
            ),
            (
                f"{test.residuals_sd[0]:.3g}",
                -1,
            ),
            (
                f"{test.residuals_sd[1]:.3g}",
                -1,
            ),
            (
                f"{test.residuals_within_1sd[0]:.3g}",
                -1,
            ),
            (
                f"{test.residuals_within_1sd[1]:.3g}",
                -1,
            ),
            (
                f"{test.residuals_within_2sd[0]:.3g}",
                -1,
            ),
            (
                f"{test.residuals_within_2sd[1]:.3g}",
                -1,
            ),
            (
                f"{test.residuals_within_3sd[0]:.3g}",
                -1,
            ),
            (
                f"{test.residuals_within_3sd[1]:.3g}",
                -1,
            ),
        ]

        num_rows: int = 0
        cell: int
        value: str
        for row, cell, (value, theme) in zip(rows, cells, values):
            if value == "":
                dpg.hide_item(row)
                continue
            else:
                dpg.show_item(row)
                num_rows += 1
            dpg.set_value(cell, value)
            update_tooltip(dpg.get_item_user_data(cell), value)
            dpg.show_item(dpg.get_item_parent(dpg.get_item_user_data(cell)))
            if theme > 0:
                dpg.bind_item_theme(cell, theme)

        dpg.set_item_height(self._table, 18 + 23 * max(1, num_rows))


class SettingsTable:
    def __init__(self):
        label_pad: int = 23
        self._header: Tag = dpg.generate_uuid()
        with dpg.collapsing_header(label=" Settings", leaf=True, tag=self._header):
            self._table: Tag = dpg.generate_uuid()
            with dpg.table(
                borders_outerV=True,
                borders_outerH=True,
                borders_innerV=True,
                borders_innerH=True,
                scrollY=True,
                freeze_rows=1,
                height=18 + 23 * 16,
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
                    "Representation",
                    "Add capacitor in series",
                    "Add inductor in series",
                    "Number of RC elements",
                    "Fitting method",
                    "Max. num. func. eval.",
                    "Timeout",
                    "Lower num. RC limit",
                    "Upper num. RC limit",
                    "Num. RC limit delta",
                    "Method(s) for num. RC",
                    "Method combination",
                    "µ-criterion",
                    "Beta",
                ]:
                    with dpg.table_row(parent=self._table):
                        dpg.add_text(label.rjust(label_pad))
                        tooltip_tag: Tag = dpg.generate_uuid()
                        dpg.add_text("", user_data=tooltip_tag)
                        attach_tooltip("", tag=tooltip_tag)

            dpg.add_spacer(height=8)
            with dpg.group(horizontal=True):
                self._apply_settings_button: Tag = dpg.generate_uuid()
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

                self._apply_mask_button: Tag = dpg.generate_uuid()
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
            tag: Tag = dpg.get_item_children(row, slot=1)[1]
            dpg.set_value(tag, "")
            dpg.hide_item(dpg.get_item_parent(dpg.get_item_user_data(tag)))

    def populate(self, test: KramersKronigResult, data: DataSet):
        dpg.show_item(self._header)
        rows: List[int] = []
        cells: List[List[int]] = []

        row: int
        for row in dpg.get_item_children(self._table, slot=1):
            rows.append(row)
            cells.append(dpg.get_item_children(row, slot=1))

        assert len(rows) == len(cells) == 16, (
            rows,
            cells,
        )

        num_rows: int = 0

        tag: int
        value: str
        visible: bool
        for i, (value, visible) in enumerate(
            [
                (
                    test_to_label.get(test.settings.test, ""),
                    True,
                ),
                (
                    test_mode_to_label.get(test.settings.mode, ""),
                    True,
                ),
                (
                    test_representation_to_label[test.settings.representation],
                    True,
                ),
                (
                    str(test.settings.add_capacitance),
                    test.settings.add_capacitance,
                ),
                (
                    str(test.settings.add_inductance),
                    test.settings.add_inductance,
                ),
                (
                    f"{test.settings.num_RC}",
                    test.settings.mode == KramersKronigMode.MANUAL,
                ),
                (
                    cnls_method_to_label.get(test.settings.cnls_method, ""),
                    test.settings.test == KramersKronigTest.CNLS,
                ),
                (
                    f"{test.settings.max_nfev}",
                    test.settings.test == KramersKronigTest.CNLS,
                ),
                (
                    f"{test.settings.timeout}",
                    test.settings.test == KramersKronigTest.CNLS,
                ),
                (
                    (
                        f"{test.settings.suggestion_settings.lower_limit}"
                        if test.settings.suggestion_settings.lower_limit > 0
                        else "Auto"
                    ),
                    True,
                ),
                (
                    (
                        f"{test.settings.suggestion_settings.upper_limit}"
                        if test.settings.suggestion_settings.upper_limit != 0
                        else "Auto"
                    ),
                    True,
                ),
                (
                    f"{test.settings.suggestion_settings.limit_delta}",
                    test.settings.suggestion_settings.limit_delta > 0,
                ),
                (
                    (
                        ", ".join(map(str, test.settings.suggestion_settings.methods))
                        if len(test.settings.suggestion_settings.methods) > 0
                        else "Default combination"
                    ),
                    True,
                ),
                (
                    ""
                    + ("Mean" if test.settings.suggestion_settings.use_mean else "")
                    + ("Ranking" if test.settings.suggestion_settings.use_ranking else "")
                    + ("Sum" if test.settings.suggestion_settings.use_sum else ""),
                    len(test.settings.suggestion_settings.methods) > 1 and any(
                        (
                            test.settings.suggestion_settings.use_mean,
                            test.settings.suggestion_settings.use_ranking,
                            test.settings.suggestion_settings.use_sum,
                        )
                    ),
                ),
                (
                    f"{test.settings.suggestion_settings.m1_mu_criterion:.2f}",
                    True if 1 in test.settings.suggestion_settings.methods else False,
                ),
                (
                    f"{test.settings.suggestion_settings.m1_beta:.2f}",
                    True if 1 in test.settings.suggestion_settings.methods else False,
                ),
            ]
        ):
            row = rows[i]
            tag = cells[i][1]
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
        self.set_settings(self.state.config.default_kramers_kronig_settings)

    def create_tab(self, state):
        self.tab: Tag = dpg.generate_uuid()
        label_pad: int = 24
        with dpg.tab(label="Kramers-Kronig", tag=self.tab):
            with dpg.child_window(border=False):
                with dpg.group(horizontal=True):
                    self.create_sidebar(state, label_pad)
                    self.create_plots()

    def create_sidebar(self, state, label_pad: int):
        self.sidebar_window: Tag = dpg.generate_uuid()
        self.sidebar_width: int = 350
        with dpg.child_window(
            border=False,
            width=self.sidebar_width,
            tag=self.sidebar_window,
        ):
            # TODO: Split into a separate class?
            with dpg.child_window(width=-1, height=334):
                self.settings_menu: SettingsMenu = SettingsMenu(
                    default_settings=state.config.default_kramers_kronig_settings,
                    label_pad=label_pad,
                    limited=False,
                    state=state,
                )
                with dpg.group(horizontal=True):
                    self.visibility_item: Tag = dpg.generate_uuid()
                    dpg.add_text(
                        "?".rjust(label_pad),
                        tag=self.visibility_item,
                    )
                    attach_tooltip(tooltips.kramers_kronig.perform)

                    self.perform_test_button: Tag = dpg.generate_uuid()
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
                    self.delete_button: Tag = dpg.generate_uuid()
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
                    self.validity_text: Tag = dpg.generate_uuid()
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
        self.plot_window: Tag = dpg.generate_uuid()
        with dpg.child_window(border=False, tag=self.plot_window):
            self.create_residuals_plot()
            dpg.add_spacer(height=4)
            dpg.add_separator()
            dpg.add_spacer(height=4)

            self.plot_tab_bar: Tag = dpg.generate_uuid()
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
            limit=0.5,
        )
        self.residuals_plot.plot(
            frequencies=array([]),
            real=array([]),
            imaginary=array([]),
        )

        with dpg.group(horizontal=True):
            self.enlarge_residuals_button: Tag = dpg.generate_uuid()
            self.adjust_residuals_limits_checkbox: Tag = dpg.generate_uuid()
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
                impedances=array([], dtype=complex128),
                label="Data",
                line=False,
                theme=themes.nyquist.data,
            )
            self.nyquist_plot.plot(
                impedances=array([], dtype=complex128),
                label="Fit",
                line=False,
                fit=True,
                theme=themes.nyquist.simulation,
            )
            self.nyquist_plot.plot(
                impedances=array([], dtype=complex128),
                label="Fit",
                line=True,
                fit=True,
                theme=themes.nyquist.simulation,
                show_label=False,
            )

            with dpg.group(horizontal=True):
                self.enlarge_nyquist_button: Tag = dpg.generate_uuid()
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

                self.adjust_nyquist_limits_checkbox: Tag = dpg.generate_uuid()
                dpg.add_checkbox(
                    label="Adjust limits",
                    default_value=True,
                    tag=self.adjust_nyquist_limits_checkbox,
                )
                attach_tooltip(tooltips.general.adjust_nyquist_limits)

                self.nyquist_admittance_checkbox: Tag = dpg.generate_uuid()
                dpg.add_checkbox(
                    label="Y",
                    callback=lambda s, a, u: self.toggle_plot_admittance(a),
                    tag=self.nyquist_admittance_checkbox,
                )
                attach_tooltip(tooltips.general.plot_admittance)

    def create_bode_plot(self):
        with dpg.tab(label="Bode"):
            self.bode_plot: Bode = Bode(
                width=-1,
                height=-24,
            )
            self.bode_plot.plot(
                frequencies=array([]),
                impedances=array([], dtype=complex128),
                labels=(
                    "Mod(data)",
                    "Phase(data)",
                ),
                line=False,
                themes=(
                    themes.bode.magnitude_data,
                    themes.bode.phase_data,
                ),
            )
            self.bode_plot.plot(
                frequencies=array([]),
                impedances=array([], dtype=complex128),
                labels=(
                    "Mod(fit)",
                    "Phase(fit)",
                ),
                line=False,
                fit=True,
                themes=(
                    themes.bode.magnitude_simulation,
                    themes.bode.phase_simulation,
                ),
            )
            self.bode_plot.plot(
                frequencies=array([]),
                impedances=array([], dtype=complex128),
                labels=(
                    "Mod(fit)",
                    "Phase(fit)",
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
                self.enlarge_bode_button: Tag = dpg.generate_uuid()
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

                self.adjust_bode_limits_checkbox: Tag = dpg.generate_uuid()
                dpg.add_checkbox(
                    label="Adjust limits",
                    default_value=True,
                    tag=self.adjust_bode_limits_checkbox,
                )
                attach_tooltip(tooltips.general.adjust_bode_limits)

                self.bode_admittance_checkbox: Tag = dpg.generate_uuid()
                dpg.add_checkbox(
                    label="Y",
                    callback=lambda s, a, u: self.toggle_plot_admittance(a),
                    tag=self.bode_admittance_checkbox,
                )
                attach_tooltip(tooltips.general.plot_admittance)

    def create_impedance_plot(self):
        with dpg.tab(label="Real & imag."):
            self.impedance_plot: Impedance = Impedance(
                width=-1,
                height=-24,
            )
            self.impedance_plot.plot(
                frequencies=array([]),
                impedances=array([], dtype=complex128),
                labels=(
                    "Re(data)",
                    "Im(data)",
                ),
                line=False,
                themes=(
                    themes.impedance.real_data,
                    themes.impedance.imaginary_data,
                ),
            )
            self.impedance_plot.plot(
                frequencies=array([]),
                impedances=array([], dtype=complex128),
                labels=(
                    "Re(fit)",
                    "Im(fit)",
                ),
                line=False,
                fit=True,
                themes=(
                    themes.impedance.real_simulation,
                    themes.impedance.imaginary_simulation,
                ),
            )
            self.impedance_plot.plot(
                frequencies=array([]),
                impedances=array([], dtype=complex128),
                labels=(
                    "Re(fit)",
                    "Im(fit)",
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
                self.enlarge_impedance_button: Tag = dpg.generate_uuid()
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

                self.adjust_impedance_limits_checkbox: Tag = dpg.generate_uuid()
                dpg.add_checkbox(
                    label="Adjust limits",
                    default_value=True,
                    tag=self.adjust_impedance_limits_checkbox,
                )
                attach_tooltip(tooltips.general.adjust_impedance_limits)

                self.impedance_admittance_checkbox: Tag = dpg.generate_uuid()
                dpg.add_checkbox(
                    label="Y",
                    callback=lambda s, a, u: self.toggle_plot_admittance(a),
                    tag=self.impedance_admittance_checkbox,
                )
                attach_tooltip(tooltips.general.plot_admittance)

    def is_visible(self) -> bool:
        return dpg.is_item_visible(self.visibility_item)

    def toggle_plot_admittance(self, admittance: bool):
        tag: int
        for tag in (
            self.nyquist_admittance_checkbox,
            self.bode_admittance_checkbox,
            self.impedance_admittance_checkbox,
        ):
            dpg.set_value(tag, admittance)

        self.nyquist_plot.set_admittance(admittance)
        self.bode_plot.set_admittance(admittance)
        self.impedance_plot.set_admittance(admittance)

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

    def get_settings(self) -> KramersKronigSettings:
        return self.settings_menu.get_settings()

    def set_settings(self, settings: KramersKronigSettings):
        self.settings_menu.set_settings(settings)

    def populate_data_sets(self, labels: List[str], lookup: Dict[str, DataSet]):
        assert type(labels) is list, labels
        assert type(lookup) is dict, lookup
        self.data_sets_combo.populate(labels, lookup)

    def populate_tests(self, lookup: Dict[str, KramersKronigResult], data: Optional[DataSet]):
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

    def get_next_result(self) -> Optional[KramersKronigResult]:
        return self.results_combo.get_next()

    def get_previous_result(self) -> Optional[KramersKronigResult]:
        return self.results_combo.get_previous()

    def select_data_set(self, data: Optional[DataSet]):
        assert type(data) is DataSet or data is None, data
        self.clear(hide=data is None)
        dpg.set_item_user_data(self.perform_test_button, data)
        self.settings_menu.update_num_RC_input(data)
        if data is None:
            return

        self.data_sets_combo.set(data.get_label())

        Z: ndarray = data.get_impedances()
        self.nyquist_plot.update(
            index=0,
            impedances=Z,
        )

        freq: ndarray = data.get_frequencies()
        self.bode_plot.update(
            index=0,
            frequencies=freq,
            impedances=Z,
        )
        self.impedance_plot.update(
            index=0,
            frequencies=freq,
            impedances=Z,
        )

    def assert_test_up_to_date(self, test: KramersKronigResult, data: DataSet):
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

    def select_test_result(self, test: Optional[KramersKronigResult], data: Optional[DataSet]):
        assert type(test) is KramersKronigResult or test is None, test
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
        )

        freq: ndarray
        real: ndarray
        imag: ndarray
        freq, real, imag = test.get_residuals_data()
        self.residuals_plot.update(
            index=0,
            frequencies=freq,
            real=real,
            imaginary=imag,
        )

        Z_exp: ndarray = test.get_impedances()
        Z_fit: ndarray = test.get_impedances(
            num_per_decade=self.state.config.num_per_decade_in_simulated_lines
        )
        self.nyquist_plot.update(
            index=1,
            impedances=Z_exp,
        )
        self.nyquist_plot.update(
            index=2,
            impedances=Z_fit,
        )

        freq_exp: ndarray = test.get_frequencies()
        freq_fit: ndarray = test.get_frequencies(
            num_per_decade=self.state.config.num_per_decade_in_simulated_lines
        )
        self.bode_plot.update(
            index=1,
            frequencies=freq_exp,
            impedances=Z_exp,
        )
        self.bode_plot.update(
            index=2,
            frequencies=freq_fit,
            impedances=Z_fit,
        )

        self.impedance_plot.update(
            index=1,
            frequencies=freq_exp,
            impedances=Z_exp,
        )
        self.impedance_plot.update(
            index=2,
            frequencies=freq_fit,
            impedances=Z_fit,
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
        tabs: List[Tag] = dpg.get_item_children(self.plot_tab_bar, slot=1)
        index: int = tabs.index(dpg.get_value(self.plot_tab_bar)) + 1
        dpg.set_value(self.plot_tab_bar, tabs[index % len(tabs)])

    def previous_plot_tab(self):
        tabs: List[Tag] = dpg.get_item_children(self.plot_tab_bar, slot=1)
        index: int = tabs.index(dpg.get_value(self.plot_tab_bar)) - 1
        dpg.set_value(self.plot_tab_bar, tabs[index % len(tabs)])

    def show_enlarged_nyquist(self):
        signals.emit(
            Signal.SHOW_ENLARGED_PLOT,
            plot=self.nyquist_plot,
            adjust_limits=dpg.get_value(self.adjust_nyquist_limits_checkbox),
            admittance=dpg.get_value(self.nyquist_admittance_checkbox),
        )

    def show_enlarged_bode(self):
        signals.emit(
            Signal.SHOW_ENLARGED_PLOT,
            plot=self.bode_plot,
            adjust_limits=dpg.get_value(self.adjust_bode_limits_checkbox),
            admittance=dpg.get_value(self.bode_admittance_checkbox),
        )

    def show_enlarged_impedance(self):
        signals.emit(
            Signal.SHOW_ENLARGED_PLOT,
            plot=self.impedance_plot,
            adjust_limits=dpg.get_value(self.adjust_impedance_limits_checkbox),
            admittance=dpg.get_value(self.impedance_admittance_checkbox),
        )

    def show_enlarged_residuals(self):
        signals.emit(
            Signal.SHOW_ENLARGED_PLOT,
            plot=self.residuals_plot,
            adjust_limits=dpg.get_value(self.adjust_residuals_limits_checkbox),
        )

    def has_active_input(self) -> bool:
        return self.settings_menu.has_active_input()

    def show_admittance_plots(self) -> bool:
        return dpg.get_value(self.nyquist_admittance_checkbox)
