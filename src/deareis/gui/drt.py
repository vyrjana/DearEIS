# DearEIS is licensed under the GPLv3 or later (https://www.gnu.org/licenses/gpl-3.0.html).
# Copyright 2022 DearEIS developers
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
    log10 as log,
    ndarray,
)
from pyimpspec.analysis.fitting import _calculate_residuals
import dearpygui.dearpygui as dpg
from deareis.utility import (
    align_numbers,
    format_number,
    is_filtered_item_visible,
    render_math,
)
from deareis.data.drt import (
    DRTSettings,
    DRTResult,
)
from deareis.enums import (
    DRTMethod,
    DRTMode,
    DRTOutput,
    derivative_order_to_label,
    drt_method_to_label,
    drt_mode_to_label,
    label_to_derivative_order,
    label_to_drt_method,
    label_to_drt_mode,
    label_to_drt_output,
    label_to_rbf_shape,
    label_to_rbf_type,
    rbf_shape_to_label,
    rbf_type_to_label,
)
from deareis.gui.plots import (
    Impedance,
    DRT,
    Residuals,
)
from deareis.enums import (
    Context,
)
import deareis.tooltips as tooltips
from deareis.tooltips import (
    attach_tooltip,
    update_tooltip,
)
from deareis.signals import Signal
import deareis.signals as signals
import deareis.themes as themes
from deareis.data import (
    DataSet,
)


MATH_DRT_WIDTH: int = 350
MATH_DRT_HEIGHT: int = 40
MATH_RBF_WIDTH: int = 380
MATH_RBF_HEIGHT: int = 40

MATH_DRT_WITHOUT_INDUCTANCE: int = render_math(
    r"$Z_{\rm DRT} = R_{\infty} + \int_{-\infty}^{\infty}\ \frac{\gamma \ln{\tau}}{1 + i 2 \pi f \tau}d\ln{\tau}$",
    MATH_DRT_WIDTH,
    MATH_DRT_HEIGHT,
)
MATH_DRT_WITH_INDUCTANCE: int = render_math(
    r"$Z_{\rm DRT} = R_{\infty} + i 2 \pi f L + \int_{-\infty}^{\infty}\ \frac{\gamma \ln{\tau}}{1 + i 2 \pi f \tau}d\ln{\tau}$",
    MATH_DRT_WIDTH,
    MATH_DRT_HEIGHT,
)

MATH_PIECEWISE_1: int = render_math(
    r"$\Phi_m(\tau) = 1-\frac{\ln{\tau} - \ln{\tau_m}}{\ln{\tau_{m-1} - \ln{\tau}}},\ \tau_{m-1} < \tau \leq \tau_m$",
    MATH_RBF_WIDTH,
    MATH_RBF_HEIGHT,
)
MATH_PIECEWISE_2: int = render_math(
    r"$\Phi_m(\tau) = 1-\frac{\ln{\tau} - \ln{\tau_m}}{\ln{\tau_{m+1} - \ln{\tau_m}}},\ \tau_m < \tau \leq \tau_{m+1}$",
    MATH_RBF_WIDTH,
    MATH_RBF_HEIGHT,
)
MATH_PIECEWISE_3: int = render_math(
    r"$\Phi_m(\tau) = 0,\ \tau_{m-1} < \tau\ {\rm or}\ \tau_{m+1} > \tau$",
    MATH_RBF_WIDTH,
    MATH_RBF_HEIGHT,
)
MATH_C0_MATERN: int = render_math(
    r"$\Phi_\mu(x) = \exp(-|\mu x|)$",
    MATH_RBF_WIDTH,
    MATH_RBF_HEIGHT,
)
MATH_C2_MATERN: int = render_math(
    r"$\Phi_\mu(x) = \exp(-|\mu x|)(1+|\mu x|)$",
    MATH_RBF_WIDTH,
    MATH_RBF_HEIGHT,
)
MATH_C4_MATERN: int = render_math(
    r"$\Phi_\mu(x) = \exp(-|\mu x|)(1+|\mu x|+\frac{1}{3}|\mu x|^2)$",
    MATH_RBF_WIDTH,
    MATH_RBF_HEIGHT,
)
MATH_C6_MATERN: int = render_math(
    r"$\Phi_\mu(x) = \exp(-|\mu x|)(1+|\mu x|+\frac{2}{5}|\mu x|^2+\frac{1}{15}|\mu x|^3)$",
    MATH_RBF_WIDTH,
    MATH_RBF_HEIGHT,
)
MATH_CAUCHY: int = render_math(
    r"$\Phi_\mu(x) = 1/(1+|\mu x|)$",
    MATH_RBF_WIDTH,
    MATH_RBF_HEIGHT,
)
MATH_GAUSSIAN: int = render_math(
    r"$\Phi_\mu(x) = \exp(-(\mu x)^2)$",
    MATH_RBF_WIDTH,
    MATH_RBF_HEIGHT,
)
MATH_INVERSE_QUADRATIC: int = render_math(
    r"$\Phi_\mu(x) = 1/(1+(\mu x)^2)$",
    MATH_RBF_WIDTH,
    MATH_RBF_HEIGHT,
)
MATH_INVERSE_QUADRIC: int = render_math(
    r"$\Phi_\mu(x) = 1/\sqrt{1+(\mu x)^2}$",
    MATH_RBF_WIDTH,
    MATH_RBF_HEIGHT,
)
MATH_GAMMA_LN_TAU: int = render_math(r"$\gamma(\ln{\tau})$", 44, 20, fontsize=10)
MATH_X: int = render_math(r"$x = |\ln{\tau} - \ln{\tau_m}|$", 96, 20, fontsize=10)
MATH_TAU_M: int = render_math(r"$\tau_m$", 18, 20, fontsize=10)
MATH_FWHM: int = render_math(r"$\mu = \frac{\Delta \ln{\tau}}{k}$", 200, 40)
MATH_SHAPE: int = render_math(r"$\mu = k$", 200, 40)


class SettingsMenu:
    def __init__(self, default_settings: DRTSettings, label_pad: int):
        with dpg.group(horizontal=True):
            dpg.add_text("Method".rjust(label_pad))
            attach_tooltip(tooltips.drt.method)
            self.method_combo: int = dpg.generate_uuid()
            dpg.add_combo(
                default_value=drt_method_to_label[default_settings.method],
                items=list(label_to_drt_method.keys()),
                width=-1,
                callback=lambda s, a, u: self.update_settings(),
                tag=self.method_combo,
            )
        with dpg.group(horizontal=True):
            dpg.add_text("Mode".rjust(label_pad))
            attach_tooltip(tooltips.drt.mode)
            self.mode_combo: int = dpg.generate_uuid()
            dpg.add_combo(
                default_value=drt_mode_to_label[default_settings.mode],
                items=list(label_to_drt_mode.keys()),
                width=-1,
                callback=lambda s, a, u: self.update_settings(),
                tag=self.mode_combo,
            )
        with dpg.group(horizontal=True):
            dpg.add_text("Lambda".rjust(label_pad))
            attach_tooltip(tooltips.drt.lambda_value)
            self.lambda_checkbox: int = dpg.generate_uuid()
            dpg.add_checkbox(
                default_value=default_settings.lambda_value <= 0.0,
                callback=lambda s, a, u: self.update_settings(),
                tag=self.lambda_checkbox,
            )
            self.lambda_input: int = dpg.generate_uuid()
            dpg.add_input_float(
                default_value=default_settings.lambda_value,
                width=-1,
                min_value=1e-16,
                min_clamped=True,
                step=0.0,
                format="%.3g",
                on_enter=True,
                tag=self.lambda_input,
            )
        with dpg.group(horizontal=True):
            dpg.add_text("Derivative order".rjust(label_pad))
            with dpg.tooltip(dpg.last_item()):
                with dpg.group(horizontal=True):
                    dpg.add_text("The derivative order of")
                    dpg.add_image(MATH_GAMMA_LN_TAU)
                    dpg.add_text("to use as the penalty in the Tikhonov regularization.")
                dpg.add_text("\nThis is only used when the method setting is set to BHT or TR-RBF.")
            self.derivative_order_combo: int = dpg.generate_uuid()
            dpg.add_combo(
                default_value=derivative_order_to_label[
                    default_settings.derivative_order
                ],
                items=list(label_to_derivative_order.keys()),
                width=-1,
                tag=self.derivative_order_combo,
            )
        with dpg.group(horizontal=True):
            dpg.add_text("RBF type".rjust(label_pad))
            with dpg.tooltip(dpg.last_item()):
                dpg.add_text(
                    "The type of radial basis function to use with the BHT and TR-RBF methods."
                )
                with dpg.table(
                    borders_outerV=True,
                    borders_outerH=True,
                    borders_innerV=True,
                    borders_innerH=True,
                    scrollY=True,
                    freeze_rows=1,
                    height=18 + 8 * (MATH_RBF_HEIGHT + 4),
                ):
                    dpg.add_table_column(
                        label="Label",
                        width_fixed=True,
                    )
                    dpg.add_table_column(
                        label="Equation",
                        width_fixed=False,
                    )
                    with dpg.table_row():
                        dpg.add_text("C^0 Matérn")
                        dpg.add_image(MATH_C0_MATERN)
                    with dpg.table_row():
                        dpg.add_text("C^2 Matérn")
                        dpg.add_image(MATH_C2_MATERN)
                    with dpg.table_row():
                        dpg.add_text("C^4 Matérn")
                        dpg.add_image(MATH_C4_MATERN)
                    with dpg.table_row():
                        dpg.add_text("C^6 Matérn")
                        dpg.add_image(MATH_C6_MATERN)
                    with dpg.table_row():
                        dpg.add_text("Cauchy")
                        dpg.add_image(MATH_CAUCHY)
                    with dpg.table_row():
                        dpg.add_text("Gaussian")
                        dpg.add_image(MATH_GAUSSIAN)
                    with dpg.table_row():
                        dpg.add_text("Inverse quadratic")
                        dpg.add_image(MATH_INVERSE_QUADRATIC)
                    with dpg.table_row():
                        dpg.add_text("Inverse quadric")
                        dpg.add_image(MATH_INVERSE_QUADRIC)
                with dpg.group(horizontal=True):
                    dpg.add_text("µ is the shape coefficient and")
                    dpg.add_image(MATH_X)
                    dpg.add_text("where")
                    dpg.add_image(MATH_TAU_M)
                    dpg.add_text("is the mth collocation point.")
                dpg.add_text(
                    "Alternatively, piecewise linear discretization can also be used:"
                )
                dpg.add_image(MATH_PIECEWISE_1)
                dpg.add_image(MATH_PIECEWISE_2)
                dpg.add_image(MATH_PIECEWISE_3)
            self.rbf_type_combo: int = dpg.generate_uuid()
            dpg.add_combo(
                default_value=rbf_type_to_label[default_settings.rbf_type],
                items=list(label_to_rbf_type.keys()),
                width=-1,
                tag=self.rbf_type_combo,
            )
        with dpg.group(horizontal=True):
            dpg.add_text("Shape type".rjust(label_pad))
            with dpg.tooltip(dpg.last_item()):
                dpg.add_text(
                    "This is only used when the method setting is set to BHT or TR-RBF."
                )
                with dpg.table(
                    borders_outerV=True,
                    borders_outerH=True,
                    borders_innerV=True,
                    borders_innerH=True,
                    scrollY=True,
                    freeze_rows=1,
                    height=18 + 2 * (40 + 4),
                ):
                    dpg.add_table_column(
                        label="Label",
                        width_fixed=True,
                    )
                    dpg.add_table_column(
                        label="Equation",
                        width_fixed=False,
                    )
                    with dpg.table_row():
                        dpg.add_text("FWHM")
                        dpg.add_image(MATH_FWHM)
                    with dpg.table_row():
                        dpg.add_text("Factor")
                        dpg.add_image(MATH_SHAPE)
                dpg.add_text(
                    "µ is used in the setting above, k is the input value, and FWHM stands for full width half maximum."
                )
            self.rbf_shape_combo: int = dpg.generate_uuid()
            dpg.add_combo(
                default_value=rbf_shape_to_label[default_settings.rbf_shape],
                items=list(label_to_rbf_shape.keys()),
                width=-1,
                tag=self.rbf_shape_combo,
            )
        with dpg.group(horizontal=True):
            dpg.add_text("Shape coefficient".rjust(label_pad))
            attach_tooltip(tooltips.drt.shape_coeff)
            self.shape_coeff_input: int = dpg.generate_uuid()
            dpg.add_input_float(
                default_value=default_settings.shape_coeff,
                width=-1,
                min_value=1e-12,
                min_clamped=True,
                step=0.0,
                format="%.3g",
                on_enter=True,
                tag=self.shape_coeff_input,
            )
        with dpg.group(horizontal=True):
            dpg.add_text("Include inductance".rjust(label_pad))
            with dpg.tooltip(dpg.last_item()):
                dpg.add_text(
                    "Whether or not to include an inductive term in the calculations."
                )
                with dpg.table(
                    borders_outerV=True,
                    borders_outerH=True,
                    borders_innerV=True,
                    borders_innerH=True,
                    scrollY=True,
                    freeze_rows=1,
                    height=18 + 2 * (MATH_DRT_HEIGHT + 4),
                ):
                    dpg.add_table_column(
                        label="State",
                        width_fixed=True,
                    )
                    dpg.add_table_column(
                        label="Equation",
                        width_fixed=False,
                    )
                    with dpg.table_row():
                        dpg.add_text("True")
                        dpg.add_image(MATH_DRT_WITH_INDUCTANCE)
                    with dpg.table_row():
                        dpg.add_text("False")
                        dpg.add_image(MATH_DRT_WITHOUT_INDUCTANCE)
                dpg.add_text(
                    "This is only used when the method setting is set to TR-RBF."
                )
            self.inductance_checkbox: int = dpg.generate_uuid()
            dpg.add_checkbox(
                default_value=default_settings.inductance,
                tag=self.inductance_checkbox,
            )
        with dpg.group(horizontal=True):
            dpg.add_text("Credible intervals".rjust(label_pad))
            attach_tooltip(tooltips.drt.credible_intervals)
            self.credible_intervals_checkbox: int = dpg.generate_uuid()
            dpg.add_checkbox(
                default_value=default_settings.credible_intervals,
                callback=lambda s, a, u: self.update_settings(),
                tag=self.credible_intervals_checkbox,
            )
        with dpg.group(horizontal=True):
            dpg.add_text("Number of samples".rjust(label_pad))
            attach_tooltip(tooltips.drt.num_samples)
            self.num_samples_input: int = dpg.generate_uuid()
            dpg.add_input_int(
                default_value=default_settings.num_samples,
                width=-1,
                min_value=1000,
                min_clamped=True,
                step=0,
                on_enter=True,
                tag=self.num_samples_input,
            )
        with dpg.group(horizontal=True):
            dpg.add_text("Number of attempts".rjust(label_pad))
            attach_tooltip(tooltips.drt.num_attempts)
            self.num_attempts_input: int = dpg.generate_uuid()
            dpg.add_input_int(
                default_value=default_settings.num_attempts,
                width=-1,
                min_value=0,
                min_clamped=True,
                step=0,
                on_enter=True,
                tag=self.num_attempts_input,
            )
        with dpg.group(horizontal=True):
            dpg.add_text("Maximum symmetry".rjust(label_pad))
            attach_tooltip(tooltips.drt.maximum_symmetry)
            self.maximum_symmetry_input: int = dpg.generate_uuid()
            dpg.add_input_float(
                default_value=default_settings.maximum_symmetry,
                width=-1,
                min_value=0.0,
                max_value=1.0,
                step=0.0,
                format="%.3g",
                on_enter=True,
                tag=self.maximum_symmetry_input,
            )
        self.update_settings()

    def get_settings(self) -> DRTSettings:
        return DRTSettings(
            method=label_to_drt_method[dpg.get_value(self.method_combo)],
            mode=label_to_drt_mode[dpg.get_value(self.mode_combo)],
            lambda_value=dpg.get_value(self.lambda_input)
            if not dpg.get_value(self.lambda_checkbox)
            else -1.0,
            rbf_type=label_to_rbf_type[dpg.get_value(self.rbf_type_combo)],
            derivative_order=label_to_derivative_order[
                dpg.get_value(self.derivative_order_combo)
            ],
            rbf_shape=label_to_rbf_shape[dpg.get_value(self.rbf_shape_combo)],
            shape_coeff=dpg.get_value(self.shape_coeff_input),
            inductance=dpg.get_value(self.inductance_checkbox),
            credible_intervals=dpg.get_value(self.credible_intervals_checkbox),
            num_samples=dpg.get_value(self.num_samples_input),
            num_attempts=dpg.get_value(self.num_attempts_input),
            maximum_symmetry=dpg.get_value(self.maximum_symmetry_input),
        )

    def set_settings(self, settings: DRTSettings):
        dpg.set_value(self.method_combo, drt_method_to_label[settings.method])
        self.update_settings()
        dpg.set_value(self.mode_combo, drt_mode_to_label[settings.mode])
        dpg.set_value(self.lambda_checkbox, settings.lambda_value <= 0.0)
        if settings.lambda_value > 0.0:
            dpg.set_value(self.lambda_input, settings.lambda_value)
        dpg.set_value(self.rbf_type_combo, rbf_type_to_label[settings.rbf_type])
        dpg.set_value(
            self.derivative_order_combo,
            derivative_order_to_label[settings.derivative_order],
        )
        dpg.set_value(self.rbf_shape_combo, rbf_shape_to_label[settings.rbf_shape])
        dpg.set_value(self.shape_coeff_input, settings.shape_coeff)
        dpg.set_value(self.inductance_checkbox, settings.inductance)
        dpg.set_value(self.credible_intervals_checkbox, settings.credible_intervals)
        dpg.set_value(self.num_samples_input, settings.num_samples)
        dpg.set_value(self.num_attempts_input, settings.num_attempts)
        dpg.set_value(self.maximum_symmetry_input, settings.maximum_symmetry)
        self.update_settings(settings)

    def update_settings(self, settings: Optional[DRTSettings] = None):
        if settings is None:
            settings = self.get_settings()
        if settings.method == DRTMethod.TR_NNLS:
            dpg.configure_item(
                self.mode_combo,
                default_value=drt_mode_to_label[
                    DRTMode.REAL if settings.mode == DRTMode.COMPLEX else settings.mode
                ],
                items=[
                    v
                    for k, v in drt_mode_to_label.items()
                    if k == DRTMode.REAL or k == DRTMode.IMAGINARY
                ],
            )
            dpg.enable_item(self.mode_combo)
        elif settings.method == DRTMethod.TR_RBF:
            dpg.configure_item(
                self.mode_combo,
                default_value=drt_mode_to_label[DRTMode.COMPLEX],
                items=list(label_to_drt_mode.keys()),
            )
            dpg.enable_item(self.mode_combo)
        elif settings.method == DRTMethod.BHT:
            dpg.disable_item(self.mode_combo)
        if settings.method == DRTMethod.BHT:
            dpg.disable_item(self.lambda_checkbox)
            dpg.disable_item(self.lambda_input)
        else:
            dpg.enable_item(self.lambda_checkbox)
            if dpg.get_value(self.lambda_checkbox):
                dpg.disable_item(self.lambda_input)
            else:
                dpg.enable_item(self.lambda_input)
        if settings.method == DRTMethod.TR_NNLS:
            dpg.disable_item(self.rbf_type_combo)
            dpg.disable_item(self.derivative_order_combo)
            dpg.disable_item(self.rbf_shape_combo)
            dpg.disable_item(self.shape_coeff_input)
        else:
            dpg.enable_item(self.rbf_type_combo)
            dpg.enable_item(self.derivative_order_combo)
            dpg.enable_item(self.rbf_shape_combo)
            dpg.enable_item(self.shape_coeff_input)
        if settings.method == DRTMethod.TR_RBF:
            dpg.enable_item(self.inductance_checkbox)
        else:
            dpg.disable_item(self.inductance_checkbox)
        if settings.method == DRTMethod.TR_RBF:
            dpg.enable_item(self.credible_intervals_checkbox)
        else:
            dpg.disable_item(self.credible_intervals_checkbox)
        if settings.method == DRTMethod.BHT or (
            settings.method == DRTMethod.TR_RBF and settings.credible_intervals is True
        ):
            dpg.enable_item(self.num_samples_input)
        else:
            dpg.disable_item(self.num_samples_input)
        if settings.method == DRTMethod.BHT:
            dpg.enable_item(self.num_attempts_input)
        else:
            dpg.disable_item(self.num_attempts_input)
        if settings.method == DRTMethod.TR_NNLS:
            dpg.disable_item(self.maximum_symmetry_input)
        else:
            dpg.enable_item(self.maximum_symmetry_input)

    def has_active_input(self) -> bool:
        inputs: List[int] = [
            self.lambda_input,
            self.shape_coeff_input,
            self.num_samples_input,
            self.num_attempts_input,
            self.maximum_symmetry_input,
        ]
        tag: int
        for tag in inputs:
            if dpg.is_item_active(tag):
                return True
        return False


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
                height=18 + 23 * 9,
                tag=self._table,
            ):
                dpg.add_table_column(
                    label="Label".rjust(label_pad),
                    width_fixed=True,
                )
                dpg.add_table_column(
                    label="Value",
                    width_fixed=False,
                )
                for label, tooltip, filter_key in [
                    (
                        "log X²",
                        tooltips.fitting.chisqr,
                        ",".join(drt_method_to_label.values()),
                    ),
                    (
                        "Lambda",
                        tooltips.drt.lambda_value,
                        ",".join(
                            map(
                                lambda _: drt_method_to_label[_],
                                [
                                    DRTMethod.TR_NNLS,
                                    DRTMethod.TR_RBF,
                                ],
                            )
                        ),
                    ),
                ]:
                    with dpg.table_row(filter_key=filter_key):
                        dpg.add_text(label.rjust(label_pad))
                        attach_tooltip(tooltip)
                        dpg.add_text("")
            dpg.add_spacer(height=8)

    def clear(self, hide: bool):
        if hide:
            dpg.hide_item(self._header)
        row: int
        for row in dpg.get_item_children(self._table, slot=1):
            cell: int = dpg.get_item_children(row, slot=1)[1]
            dpg.set_value(cell, "")

    def populate(self, drt: DRTResult):
        dpg.show_item(self._header)
        filter_key: str = drt_method_to_label[drt.settings.method]
        dpg.set_value(self._table, filter_key)
        statistics: List[str] = [
            f"{log(drt.chisqr):.3g}",
            f"{drt.lambda_value:.3e}",
        ]
        visible_items: List[bool] = []
        i: int
        row: int
        for i, row in enumerate(dpg.get_item_children(self._table, slot=1)):
            cell: int = dpg.get_item_children(row, slot=1)[2]
            dpg.set_value(cell, statistics[i])
            visible_items.append(is_filtered_item_visible(row, filter_key))
        dpg.set_item_height(
            self._table,
            18 + 23 * len(list(filter(lambda _: _ is True, visible_items))),
        )


class ScoresTable:
    def __init__(self):
        label_pad: int = 23
        self._header: int = dpg.generate_uuid()
        with dpg.collapsing_header(label=" Scores", leaf=True, tag=self._header):
            self._table: int = dpg.generate_uuid()
            with dpg.table(
                borders_outerV=True,
                borders_outerH=True,
                borders_innerV=True,
                borders_innerH=True,
                scrollY=True,
                freeze_rows=1,
                height=18 + 23 * 9,
                tag=self._table,
            ):
                dpg.add_table_column(
                    label="Score".rjust(label_pad),
                    width_fixed=True,
                )
                dpg.add_table_column(
                    label="Real (%)",
                    width_fixed=False,
                )
                dpg.add_table_column(
                    label="Imag. (%)",
                    width_fixed=False,
                )
                label: str
                tooltip: str
                for (label, tooltip) in [
                    (
                        "Mean",
                        tooltips.drt.score_mean,
                    ),
                    (
                        "Residuals, 1 sigma",
                        tooltips.drt.score_residuals,
                    ),
                    (
                        "Residuals, 2 sigma",
                        tooltips.drt.score_residuals,
                    ),
                    (
                        "Residuals, 3 sigma",
                        tooltips.drt.score_residuals,
                    ),
                    (
                        "Hellinger distance",
                        tooltips.drt.score_hd,
                    ),
                    (
                        "Jensen-Shannon distance",
                        tooltips.drt.score_jsd,
                    ),
                ]:
                    with dpg.table_row():
                        dpg.add_text(label.rjust(label_pad))
                        attach_tooltip(tooltip)
                        dpg.add_text("")  # Real
                        dpg.add_text("")  # Imag.
            dpg.add_spacer(height=8)

    def clear(self, hide: bool):
        if hide:
            dpg.hide_item(self._header)
        row: int
        for row in dpg.get_item_children(self._table, slot=1):
            cell: int
            for cell in dpg.get_item_children(row, slot=1)[2:]:
                dpg.set_value(cell, "")

    def populate(self, drt: DRTResult):
        scores: Dict[str, complex] = drt.get_scores()
        if len(scores) > 0:
            dpg.show_item(self._header)
        else:
            dpg.hide_item(self._header)
            return
        keys: List[str] = [
            "mean",
            "residuals_1sigma",
            "residuals_2sigma",
            "residuals_3sigma",
            "hellinger_distance",
            "jensen_shannon_distance",
        ]
        real_values: List[str] = []
        imaginary_values: List[str] = []
        number_format: dict = {
            "significants": 3,
            "exponent": False,
        }
        for key in keys:
            real_values.append(format_number(scores[key].real * 100, **number_format))
            imaginary_values.append(
                format_number(scores[key].imag * 100, **number_format)
            )
        real_values = align_numbers(real_values)
        imaginary_values = align_numbers(imaginary_values)
        i: int
        row: int
        for i, row in enumerate(dpg.get_item_children(self._table, slot=1)):
            tags: List[int] = dpg.get_item_children(row, slot=1)[2:]
            dpg.set_value(tags[0], real_values[i])
            dpg.set_value(tags[1], imaginary_values[i])
        dpg.set_item_height(self._table, 18 + 23 * len(keys))


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
                height=18 + 23 * 12,
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
                for (label, filter_key) in [
                    (
                        "Method",
                        ",".join(drt_method_to_label.values()),
                    ),
                    (
                        "Mode",
                        ",".join(
                            map(
                                lambda _: drt_method_to_label[_],
                                [
                                    DRTMethod.TR_NNLS,
                                    DRTMethod.TR_RBF,
                                ],
                            )
                        ),
                    ),
                    (
                        "Lambda",
                        ",".join(
                            map(
                                lambda _: drt_method_to_label[_],
                                [
                                    DRTMethod.TR_NNLS,
                                    DRTMethod.TR_RBF,
                                ],
                            )
                        ),
                    ),
                    (
                        "RBF type",
                        ",".join(
                            map(
                                lambda _: drt_method_to_label[_],
                                [
                                    DRTMethod.BHT,
                                    DRTMethod.TR_RBF,
                                ],
                            )
                        ),
                    ),
                    (
                        "Deriv. order",
                        ",".join(
                            map(
                                lambda _: drt_method_to_label[_],
                                [
                                    DRTMethod.BHT,
                                    DRTMethod.TR_RBF,
                                ],
                            )
                        ),
                    ),
                    (
                        "RBF shape",
                        ",".join(
                            map(
                                lambda _: drt_method_to_label[_],
                                [
                                    DRTMethod.BHT,
                                    DRTMethod.TR_RBF,
                                ],
                            )
                        ),
                    ),
                    (
                        "Shape coeff.",
                        ",".join(
                            map(
                                lambda _: drt_method_to_label[_],
                                [
                                    DRTMethod.BHT,
                                    DRTMethod.TR_RBF,
                                ],
                            )
                        ),
                    ),
                    (
                        "Include inductance",
                        drt_method_to_label[DRTMethod.TR_RBF],
                    ),
                    (
                        "Credible intervals",
                        drt_method_to_label[DRTMethod.TR_RBF],
                    ),
                    (
                        "Number of samples",
                        ",".join(
                            map(
                                lambda _: drt_method_to_label[_],
                                [
                                    DRTMethod.BHT,
                                    DRTMethod.TR_RBF,
                                ],
                            )
                        ),
                    ),
                    (
                        "Number of attempts",
                        drt_method_to_label[DRTMethod.BHT],
                    ),
                    (
                        "Maximum symmetry",
                        ",".join(
                            map(
                                lambda _: drt_method_to_label[_],
                                [
                                    DRTMethod.BHT,
                                    DRTMethod.TR_RBF,
                                ],
                            )
                        ),
                    ),
                ]:
                    with dpg.table_row(filter_key=filter_key):
                        dpg.add_text(label.rjust(label_pad))
                        tooltip_tag: int = dpg.generate_uuid()
                        dpg.add_text("", user_data=tooltip_tag)
                        attach_tooltip("", tag=tooltip_tag)
            with dpg.group(horizontal=True):
                self._apply_settings_button: int = dpg.generate_uuid()
                dpg.add_button(
                    label="Apply settings",
                    callback=lambda s, a, u: signals.emit(
                        Signal.APPLY_DRT_SETTINGS,
                        **u,
                    ),
                    tag=self._apply_settings_button,
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

    def populate(self, drt: DRTResult, data: DataSet):
        dpg.show_item(self._header)
        filter_key: str = drt_method_to_label[drt.settings.method]
        dpg.set_value(self._table, filter_key)
        values: List[str] = [
            drt_method_to_label[drt.settings.method],
            drt_mode_to_label[drt.settings.mode],
            f"{drt.settings.lambda_value:.3e}" if drt.settings.lambda_value > 0.0 else "Automatic",
            rbf_type_to_label[drt.settings.rbf_type],
            derivative_order_to_label[drt.settings.derivative_order],
            rbf_shape_to_label[drt.settings.rbf_shape],
            f"{drt.settings.shape_coeff:.3g}",
            "True" if drt.settings.inductance else "False",
            "True" if drt.settings.credible_intervals else "False",
            str(drt.settings.num_samples),
            str(drt.settings.num_attempts),
            f"{drt.settings.maximum_symmetry:.3g}",
        ]
        visible_items: List[bool] = []
        i: int
        row: int
        for i, row in enumerate(dpg.get_item_children(self._table, slot=1)):
            if not is_filtered_item_visible(row, filter_key):
                visible_items.append(False)
                continue
            tag: List[int] = dpg.get_item_children(row, slot=1)[1]
            value: str = values[i]
            dpg.set_value(tag, value)
            update_tooltip(dpg.get_item_user_data(tag), value)
            dpg.show_item(dpg.get_item_parent(dpg.get_item_user_data(tag)))
            visible_items.append(True)
        dpg.set_item_height(
            self._table,
            18 + 23 * len(list(filter(lambda _: _ is True, visible_items))),
        )
        dpg.set_item_user_data(
            self._apply_settings_button,
            {"settings": drt.settings},
        )
        dpg.set_item_user_data(
            self._apply_mask_button,
            {
                "data": data,
                "mask": drt.mask,
                "drt": drt,
            },
        )


class DataSetsCombo:
    def __init__(self, label: str, width: int):
        self.labels: List[str] = []
        dpg.add_text(label)
        self.tag: int = dpg.generate_uuid()
        dpg.add_combo(
            callback=lambda s, a, u: signals.emit(
                Signal.SELECT_DATA_SET,
                data=u.get(a),
            ),
            user_data={},
            width=width,
            tag=self.tag,
        )

    def populate(self, labels: List[str], lookup: Dict[str, DataSet]):
        self.labels.clear()
        self.labels.extend(labels)
        label: str = dpg.get_value(self.tag) or ""
        if labels and label not in labels:
            label = labels[0]
        dpg.configure_item(
            self.tag,
            default_value=label,
            items=labels,
            user_data=lookup,
        )

    def get(self) -> Optional[DataSet]:
        return dpg.get_item_user_data(self.tag).get(dpg.get_value(self.tag))

    def set(self, label: str):
        assert type(label) is str, label
        assert label in self.labels, (
            label,
            self.labels,
        )
        dpg.set_value(self.tag, label)

    def clear(self):
        dpg.configure_item(
            self.tag,
            default_value="",
        )


class ResultsCombo:
    def __init__(self, label: str, width: int):
        self.labels: Dict[str, str] = {}
        dpg.add_text(label)
        self.tag: int = dpg.generate_uuid()
        dpg.add_combo(
            callback=lambda s, a, u: signals.emit(
                Signal.SELECT_DRT_RESULT,
                drt=u[0].get(a),
                data=u[1],
            ),
            user_data=(
                {},
                None,
            ),
            width=width,
            tag=self.tag,
        )

    def populate(self, lookup: Dict[str, DRTResult], data: Optional[DataSet]):
        self.labels.clear()
        labels: List[str] = list(lookup.keys())
        longest_cdc: int = max(list(map(lambda _: len(_[: _.find(" ")]), labels)) + [1])
        old_key: str
        for old_key in labels:
            drt: DRTResult = lookup[old_key]
            del lookup[old_key]
            cdc, timestamp = (
                old_key[: old_key.find(" ")],
                old_key[old_key.find(" ") + 1 :],
            )
            new_key: str = f"{cdc.ljust(longest_cdc)} {timestamp}"
            self.labels[old_key] = new_key
            lookup[new_key] = drt
        labels = list(lookup.keys())
        dpg.configure_item(
            self.tag,
            default_value=labels[0] if labels else "",
            items=labels,
            user_data=(
                lookup,
                data,
            ),
        )

    def get(self) -> Optional[DRTResult]:
        return dpg.get_item_user_data(self.tag)[0].get(dpg.get_value(self.tag))

    def set(self, label: str):
        assert type(label) is str, label
        assert label in self.labels, (
            label,
            list(self.labels.keys()),
        )
        dpg.set_value(self.tag, self.labels[label])

    def clear(self):
        dpg.configure_item(
            self.tag,
            default_value="",
        )

    def get_next_result(self) -> Optional[DRTResult]:
        lookup: Dict[str, DRTResult] = dpg.get_item_user_data(self.tag)[0]
        if not lookup:
            return None
        labels: List[str] = list(lookup.keys())
        index: int = labels.index(dpg.get_value(self.tag)) + 1
        return lookup[labels[index % len(labels)]]

    def get_previous_result(self) -> Optional[DRTResult]:
        lookup: Dict[str, DRTResult] = dpg.get_item_user_data(self.tag)[0]
        if not lookup:
            return None
        labels: List[str] = list(lookup.keys())
        index: int = labels.index(dpg.get_value(self.tag)) - 1
        return lookup[labels[index % len(labels)]]


class DRTTab:
    def __init__(self, state):
        self.state = state
        self.queued_update: Optional[Callable] = None
        label_pad: int = 24
        self.tab: int = dpg.generate_uuid()
        with dpg.tab(label="DRT analysis", tag=self.tab):
            with dpg.group(horizontal=True):
                self.sidebar_width: int = 350
                self.sidebar_window: int = dpg.generate_uuid()
                with dpg.child_window(
                    border=False,
                    width=self.sidebar_width,
                    tag=self.sidebar_window,
                ):
                    # Settings
                    with dpg.child_window(
                        border=True,
                        width=-1,
                        height=312,
                    ):
                        self.settings_menu: SettingsMenu = SettingsMenu(
                            state.config.default_drt_settings, label_pad
                        )
                        with dpg.group(horizontal=True):
                            self.visibility_item: int = dpg.generate_uuid()
                            dpg.add_text("?".rjust(label_pad), tag=self.visibility_item)
                            attach_tooltip(tooltips.drt.perform)
                            self.perform_drt_button: int = dpg.generate_uuid()
                            dpg.add_button(
                                label="Perform analysis",
                                callback=lambda s, a, u: signals.emit(
                                    Signal.PERFORM_DRT,
                                    data=u,
                                    settings=self.get_settings(),
                                ),
                                user_data=None,
                                width=-1,
                                tag=self.perform_drt_button,
                            )
                    # Results
                    with dpg.child_window(width=-1, height=82):
                        label_pad = 8
                        with dpg.group(horizontal=True):
                            self.data_sets_combo: DataSetsCombo = DataSetsCombo(
                                label="Data set".rjust(label_pad),
                                width=-60,
                            )
                        with dpg.group(horizontal=True):
                            self.results_combo: ResultsCombo = ResultsCombo(
                                label="Result".rjust(label_pad),
                                width=-60,
                            )
                            self.delete_button: int = dpg.generate_uuid()
                            dpg.add_button(
                                label="Delete",
                                callback=lambda s, a, u: signals.emit(
                                    Signal.DELETE_DRT_RESULT,
                                    **u,
                                ),
                                user_data={},
                                width=-1,
                                tag=self.delete_button,
                            )
                            attach_tooltip(tooltips.drt.delete)
                        with dpg.group(horizontal=True):
                            dpg.add_text("Output".rjust(label_pad))
                            # TODO: Split into combo class?
                            self.output_combo: int = dpg.generate_uuid()
                            dpg.add_combo(
                                default_value=list(label_to_drt_output.keys())[0],
                                items=list(label_to_drt_output.keys()),
                                tag=self.output_combo,
                                width=-60,
                            )
                            self.copy_output_button: int = dpg.generate_uuid()
                            dpg.add_button(
                                label="Copy",
                                callback=lambda s, a, u: signals.emit(
                                    Signal.COPY_OUTPUT,
                                    output=self.get_active_output(),
                                    **u,
                                ),
                                user_data={},
                                width=-1,
                                tag=self.copy_output_button,
                            )
                            attach_tooltip(tooltips.general.copy_output)
                    # Results/settings tables
                    with dpg.child_window(width=-1, height=-1):
                        self.result_group: int = dpg.generate_uuid()
                        with dpg.group(tag=self.result_group):
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
                            self.scores_table: ScoresTable = ScoresTable()
                            self.settings_table: SettingsTable = SettingsTable()
                # Plots window
                self.plot_window: int = dpg.generate_uuid()
                with dpg.child_window(
                    border=False,
                    width=-1,
                    height=-1,
                    tag=self.plot_window,
                ):
                    self.minimum_plot_side: int = 400
                    # Gamma (or real gamma if BHT)
                    self.drt_plot: DRT = DRT(
                        width=-1,
                        height=self.minimum_plot_side,
                    )
                    self.drt_plot.plot(
                        tau=array([]),
                        gamma=array([]),
                        label="gamma",
                        theme=themes.drt.real_gamma,
                    )
                    with dpg.group(horizontal=True):
                        self.enlarge_drt_button: int = dpg.generate_uuid()
                        self.adjust_drt_limits_checkbox: int = dpg.generate_uuid()
                        dpg.add_button(
                            label="Enlarge DRT",
                            callback=self.show_enlarged_drt,
                            tag=self.enlarge_drt_button,
                        )
                        dpg.add_checkbox(
                            default_value=True,
                            tag=self.adjust_drt_limits_checkbox,
                        )
                        attach_tooltip(tooltips.general.adjust_drt_limits)
                        dpg.add_button(
                            label="Copy as CSV",
                            callback=lambda s, a, u: signals.emit(
                                Signal.COPY_PLOT_DATA,
                                plot=self.drt_plot,
                                context=Context.DRT_TAB,
                            ),
                        )
                        attach_tooltip(tooltips.general.copy_plot_data_as_csv)
                    # Impedance plot
                    self.impedance_plot: Impedance = Impedance(
                        width=-1,
                        height=self.minimum_plot_side,
                    )
                    self.impedance_plot.plot(
                        frequency=array([]),
                        real=array([]),
                        imaginary=array([]),
                        labels=(
                            "Z' (d)",
                            'Z" (d)',
                        ),
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
                            "Z' (f)",
                            'Z" (f)',
                        ),
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
                            "Z' (f)",
                            'Z" (f)',
                        ),
                        fit=True,
                        line=True,
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
                            label="Enlarge impedance",
                            callback=self.show_enlarged_impedance,
                            tag=self.enlarge_impedance_button,
                        )
                        dpg.add_checkbox(
                            default_value=True,
                            tag=self.adjust_impedance_limits_checkbox,
                        )
                        attach_tooltip(tooltips.general.adjust_impedance_limits)
                        dpg.add_button(
                            label="Copy as CSV",
                            callback=lambda s, a, u: signals.emit(
                                Signal.COPY_PLOT_DATA,
                                plot=self.impedance_plot,
                                context=Context.DRT_TAB,
                            ),
                        )
                        attach_tooltip(tooltips.general.copy_plot_data_as_csv)
                    # Residuals
                    self.residuals_plot: Residuals = Residuals(
                        width=-1,
                        height=300,
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
                            label="Enlarge residuals",
                            callback=self.show_enlarged_residuals,
                            tag=self.enlarge_residuals_button,
                        )
                        dpg.add_checkbox(
                            default_value=True,
                            tag=self.adjust_residuals_limits_checkbox,
                        )
                        attach_tooltip(tooltips.general.adjust_residuals_limits)
                        dpg.add_button(
                            label="Copy as CSV",
                            callback=lambda s, a, u: signals.emit(
                                Signal.COPY_PLOT_DATA,
                                plot=self.residuals_plot,
                                context=Context.DRT_TAB,
                            ),
                        )
                        attach_tooltip(tooltips.general.copy_plot_data_as_csv)

    def is_visible(self) -> bool:
        return dpg.is_item_visible(self.visibility_item)

    def has_active_input(self) -> bool:
        return self.settings_menu.has_active_input()

    def get_settings(self) -> DRTSettings:
        return self.settings_menu.get_settings()

    def set_settings(self, settings: DRTSettings):
        self.settings_menu.set_settings(settings)

    def resize(self, width: int, height: int):
        assert type(width) is int and width > 0
        assert type(height) is int and height > 0
        if not self.is_visible():
            return
        width, height = dpg.get_item_rect_size(self.plot_window)
        height = round(height / 2) - 24 * 2
        self.drt_plot.resize(-1, height)
        self.impedance_plot.resize(-1, height)

    def clear(self, hide: bool = True):
        self.data_sets_combo.clear()
        self.results_combo.clear()
        self.statistics_table.clear(hide=True)
        self.scores_table.clear(hide=True)
        self.settings_table.clear(hide=True)
        self.drt_plot.update(
            index=0,
            tau=array([]),
            gamma=array([]),
            label="gamma",
        )
        self.drt_plot.delete_series(from_index=1)
        self.impedance_plot.clear(delete=False)
        self.residuals_plot.clear(delete=False)

    def show_enlarged_drt(self):
        signals.emit(
            Signal.SHOW_ENLARGED_PLOT,
            plot=self.drt_plot,
            adjust_limits=dpg.get_value(self.adjust_drt_limits_checkbox),
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

    def populate_data_sets(self, labels: List[str], lookup: Dict[str, DataSet]):
        assert type(labels) is list, labels
        assert type(lookup) is dict, lookup
        self.data_sets_combo.populate(labels, lookup)

    def populate_drts(self, lookup: Dict[str, DRTResult], data: Optional[DataSet]):
        assert type(lookup) is dict, lookup
        assert type(data) is DataSet or data is None, data
        self.results_combo.populate(lookup, data)
        dpg.hide_item(dpg.get_item_parent(self.validity_text))
        if data is not None and self.results_combo.labels:
            signals.emit(
                Signal.SELECT_DRT_RESULT,
                drt=self.results_combo.get(),
                data=data,
            )
        else:
            self.statistics_table.clear(hide=True)
            self.scores_table.clear(hide=True)
            self.settings_table.clear(hide=True)
            self.select_data_set(data)
            dpg.set_item_user_data(
                self.delete_button,
                {},
            )

    def get_next_data_set(self) -> Optional[DataSet]:
        lookup: Dict[str, DataSet] = dpg.get_item_user_data(self.data_sets_combo.tag)
        if not lookup:
            return None
        labels: List[str] = list(lookup.keys())
        index: int = labels.index(dpg.get_value(self.data_sets_combo.tag)) + 1
        return lookup[labels[index % len(labels)]]

    def get_previous_data_set(self) -> Optional[DataSet]:
        lookup: Dict[str, DataSet] = dpg.get_item_user_data(self.data_sets_combo.tag)
        if not lookup:
            return None
        labels: List[str] = list(lookup.keys())
        index: int = labels.index(dpg.get_value(self.data_sets_combo.tag)) - 1
        return lookup[labels[index % len(labels)]]

    def get_next_result(self) -> Optional[DRTResult]:
        return self.results_combo.get_next_result()

    def get_previous_result(self) -> Optional[DRTResult]:
        return self.results_combo.get_previous_result()

    def select_data_set(self, data: Optional[DataSet]):
        assert type(data) is DataSet or data is None, data
        self.clear(hide=data is None)
        dpg.set_item_user_data(self.perform_drt_button, data)
        if data is None:
            return
        self.data_sets_combo.set(data.get_label())
        f: ndarray = data.get_frequency()
        Z: ndarray = data.get_impedance()
        self.impedance_plot.update(
            index=0,
            frequency=f,
            real=Z.real,
            imaginary=-Z.imag,
        )

    def assert_drt_up_to_date(self, drt: DRTResult, data: DataSet):
        # Check if the number of unmasked points is the same
        Z_exp: ndarray = data.get_impedance()
        Z_drt: ndarray = drt.get_impedance()
        assert Z_exp.shape == Z_drt.shape, "The number of data points differ!"
        # Check if the masks are the same
        mask_exp: Dict[int, bool] = data.get_mask()
        mask_drt: Dict[int, bool] = {
            k: drt.mask.get(k, mask_exp.get(k, False)) for k in drt.mask
        }
        num_masked_exp: int = list(data.get_mask().values()).count(True)
        num_masked_drt: int = list(drt.mask.values()).count(True)
        assert num_masked_exp == num_masked_drt, "The masks are different sizes!"
        i: int
        for i in mask_drt.keys():
            assert (
                i in mask_exp
            ), f"The data set does not have a point at index {i + 1}!"
            assert (
                mask_exp[i] == mask_drt[i]
            ), f"The data set's mask differs at index {i + 1}!"
        # Check if the frequencies and impedances are the same
        assert allclose(
            drt.get_frequency(), data.get_frequency()
        ), "The frequencies differ!"
        real_residual: ndarray
        imaginary_residual: ndarray
        real_residual, imaginary_residual = _calculate_residuals(Z_exp, Z_drt)
        assert allclose(drt.real_residual, real_residual) and allclose(
            drt.imaginary_residual, imaginary_residual
        ), "The data set's impedances differ from what they were when the DRT analysis was performed!"

    def select_drt_result(self, drt: Optional[DRTResult], data: Optional[DataSet]):
        assert type(drt) is DRTResult or drt is None, drt
        assert type(data) is DataSet or data is None, data
        dpg.set_item_user_data(
            self.delete_button,
            {
                "drt": drt,
                "data": data,
            },
        )
        dpg.set_item_user_data(
            self.copy_output_button,
            {
                "drt": drt,
                "data": data,
            },
        )
        if not self.is_visible():
            self.queued_update = lambda: self.select_drt_result(drt, data)
            return
        self.queued_update = None
        self.select_data_set(data)
        if drt is None or data is None:
            if dpg.get_value(self.adjust_drt_limits_checkbox):
                self.drt_plot.queue_limits_adjustment()
            if dpg.get_value(self.adjust_residuals_limits_checkbox):
                self.residuals_plot.queue_limits_adjustment()
            if dpg.get_value(self.adjust_impedance_limits_checkbox):
                self.impedance_plot.queue_limits_adjustment()
            return
        self.results_combo.set(drt.get_label())
        message: str
        try:
            self.assert_drt_up_to_date(drt, data)
            dpg.hide_item(dpg.get_item_parent(self.validity_text))
        except AssertionError as message:
            dpg.set_value(
                self.validity_text,
                f"DRT analysis result is not valid for the current state of the data set!\n\n{message}",
            )
            dpg.show_item(dpg.get_item_parent(self.validity_text))
        self.statistics_table.populate(drt)
        self.scores_table.populate(drt)
        self.settings_table.populate(drt, data)
        tau: ndarray
        gamma: ndarray
        tau, gamma = drt.get_drt_data()
        self.drt_plot.update(
            index=0,
            tau=tau,
            gamma=gamma,
            label="real" if drt.settings.method == DRTMethod.BHT else "gamma",
        )
        if (
            drt.settings.method == DRTMethod.TR_RBF
            and drt.settings.credible_intervals is True
        ):
            mean: ndarray
            lower: ndarray
            upper: ndarray
            tau, gamma, lower, upper = drt.get_drt_credible_intervals()
            self.drt_plot.plot(
                tau=tau,
                mean=gamma,
                label="mean",
                theme=themes.drt.mean_gamma,
            )
            self.drt_plot.plot(
                tau=tau,
                lower=lower,
                upper=upper,
                label="3-sigma CI",
                theme=themes.drt.credible_intervals,
            )
        if drt.settings.method == DRTMethod.BHT:
            tau, gamma = drt.get_drt_data(imaginary=True)
            self.drt_plot.plot(
                tau=tau,
                imaginary=gamma,
                label="imag.",
                theme=themes.drt.imaginary_gamma,
            )
        f: ndarray = drt.get_frequency()
        Z: ndarray = drt.get_impedance()
        self.impedance_plot.update(
            index=1,
            frequency=f,
            real=Z.real,
            imaginary=-Z.imag,
        )
        self.impedance_plot.update(
            index=2,
            frequency=f,
            real=Z.real,
            imaginary=-Z.imag,
        )
        real: ndarray
        imaginary: ndarray
        f, real, imaginary = drt.get_residual_data()
        self.residuals_plot.update(
            index=0,
            frequency=f,
            real=real,
            imaginary=imaginary,
        )
        if dpg.get_value(self.adjust_drt_limits_checkbox):
            self.drt_plot.queue_limits_adjustment()
        if dpg.get_value(self.adjust_impedance_limits_checkbox):
            self.impedance_plot.queue_limits_adjustment()
        if dpg.get_value(self.adjust_residuals_limits_checkbox):
            self.residuals_plot.queue_limits_adjustment()

    def get_active_output(self) -> Optional[DRTOutput]:
        return label_to_drt_output.get(dpg.get_value(self.output_combo))
