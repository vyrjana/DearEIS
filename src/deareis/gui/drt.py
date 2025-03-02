# DearEIS is licensed under the GPLv3 or later (https://www.gnu.org/licenses/gpl-3.0.html).
# Copyright 2025 DearEIS developers
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
    Union,
)
from numpy import (
    allclose,
    array,
    complex128,
    log10 as log,
    ndarray,
)
from pyimpspec.exceptions import DRTError
from pyimpspec import (
    ComplexImpedances,
    ComplexResiduals,
    Frequencies,
)
from pyimpspec.analysis.drt.mrq_fit import _validate_circuit
from pyimpspec.analysis.utility import _calculate_residuals
import dearpygui.dearpygui as dpg
from deareis.utility import (
    align_numbers,
    format_number,
    is_filtered_item_visible,
    pad_tab_labels,
    render_math,
)
from deareis.data.drt import (
    DRTSettings,
    DRTResult,
)
from deareis.data.fitting import FitResult
from deareis.enums import (
    CrossValidationMethod,
    DRTMethod,
    DRTMode,
    DRTOutput,
    TRNNLSLambdaMethod,
    cross_validation_method_to_label,
    derivative_order_to_label,
    drt_method_to_label,
    drt_mode_to_label,
    label_to_cross_validation_method,
    label_to_derivative_order,
    label_to_drt_method,
    label_to_drt_mode,
    label_to_drt_output,
    label_to_rbf_shape,
    label_to_rbf_type,
    label_to_tr_nnls_lambda_method,
    rbf_shape_to_label,
    rbf_type_to_label,
    tr_nnls_lambda_method_to_label,
)
from deareis.gui.plots import (
    Bode,
    DRT,
    Impedance,
    Nyquist,
    Plot,
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
from deareis.gui.shared import (
    DataSetsCombo,
    ResultsCombo,
)
from deareis.gui.widgets.combo import Combo
from deareis.typing.helpers import Tag


MATH_DRT_WIDTH: int = 350
MATH_DRT_HEIGHT: int = 40
MATH_RBF_WIDTH: int = 380
MATH_RBF_HEIGHT: int = 40
MATH_DRT_WITHOUT_INDUCTANCE: int = -1
MATH_DRT_WITH_INDUCTANCE: int = -1
MATH_PIECEWISE_1: int = -1
MATH_PIECEWISE_2: int = -1
MATH_PIECEWISE_3: int = -1
MATH_C0_MATERN: int = -1
MATH_C2_MATERN: int = -1
MATH_C4_MATERN: int = -1
MATH_C6_MATERN: int = -1
MATH_CAUCHY: int = -1
MATH_GAUSSIAN: int = -1
MATH_INVERSE_QUADRATIC: int = -1
MATH_INVERSE_QUADRIC: int = -1
MATH_GAMMA_LN_TAU: int = -1
MATH_X: int = -1
MATH_TAU_M: int = -1
MATH_FWHM: int = -1
MATH_SHAPE: int = -1


def process_math():
    global MATH_DRT_WITHOUT_INDUCTANCE
    global MATH_DRT_WITH_INDUCTANCE
    global MATH_PIECEWISE_1
    global MATH_PIECEWISE_2
    global MATH_PIECEWISE_3
    global MATH_C0_MATERN
    global MATH_C2_MATERN
    global MATH_C4_MATERN
    global MATH_C6_MATERN
    global MATH_CAUCHY
    global MATH_GAUSSIAN
    global MATH_INVERSE_QUADRATIC
    global MATH_INVERSE_QUADRIC
    global MATH_GAMMA_LN_TAU
    global MATH_X
    global MATH_TAU_M
    global MATH_FWHM
    global MATH_SHAPE
    MATH_DRT_WITHOUT_INDUCTANCE = render_math(
        r"$Z_{\rm DRT} = R_{\infty} + \int_{-\infty}^{\infty}\ \frac{\gamma \ln{\tau}}{1 + i 2 \pi f \tau}d\ln{\tau}$",
        MATH_DRT_WIDTH,
        MATH_DRT_HEIGHT,
    )
    MATH_DRT_WITH_INDUCTANCE = render_math(
        r"$Z_{\rm DRT} = R_{\infty} + i 2 \pi f L + \int_{-\infty}^{\infty}\ \frac{\gamma \ln{\tau}}{1 + i 2 \pi f \tau}d\ln{\tau}$",
        MATH_DRT_WIDTH,
        MATH_DRT_HEIGHT,
    )
    MATH_PIECEWISE_1 = render_math(
        r"$\Phi_m(\tau) = 1-\frac{\ln{\tau} - \ln{\tau_m}}{\ln{\tau_{m-1} - \ln{\tau}}},\ \tau_{m-1} < \tau \leq \tau_m$",
        MATH_RBF_WIDTH,
        MATH_RBF_HEIGHT,
    )
    MATH_PIECEWISE_2 = render_math(
        r"$\Phi_m(\tau) = 1-\frac{\ln{\tau} - \ln{\tau_m}}{\ln{\tau_{m+1} - \ln{\tau_m}}},\ \tau_m < \tau \leq \tau_{m+1}$",
        MATH_RBF_WIDTH,
        MATH_RBF_HEIGHT,
    )
    MATH_PIECEWISE_3 = render_math(
        r"$\Phi_m(\tau) = 0,\ \tau_{m-1} < \tau\ {\rm or}\ \tau_{m+1} > \tau$",
        MATH_RBF_WIDTH,
        MATH_RBF_HEIGHT,
    )
    MATH_C0_MATERN = render_math(
        r"$\Phi_\mu(x) = \exp(-|\mu x|)$",
        MATH_RBF_WIDTH,
        MATH_RBF_HEIGHT,
    )
    MATH_C2_MATERN = render_math(
        r"$\Phi_\mu(x) = \exp(-|\mu x|)(1+|\mu x|)$",
        MATH_RBF_WIDTH,
        MATH_RBF_HEIGHT,
    )
    MATH_C4_MATERN = render_math(
        r"$\Phi_\mu(x) = \exp(-|\mu x|)(1+|\mu x|+\frac{1}{3}|\mu x|^2)$",
        MATH_RBF_WIDTH,
        MATH_RBF_HEIGHT,
    )
    MATH_C6_MATERN = render_math(
        r"$\Phi_\mu(x) = \exp(-|\mu x|)(1+|\mu x|+\frac{2}{5}|\mu x|^2+\frac{1}{15}|\mu x|^3)$",
        MATH_RBF_WIDTH,
        MATH_RBF_HEIGHT,
    )
    MATH_CAUCHY = render_math(
        r"$\Phi_\mu(x) = 1/(1+|\mu x|)$",
        MATH_RBF_WIDTH,
        MATH_RBF_HEIGHT,
    )
    MATH_GAUSSIAN = render_math(
        r"$\Phi_\mu(x) = \exp(-(\mu x)^2)$",
        MATH_RBF_WIDTH,
        MATH_RBF_HEIGHT,
    )
    MATH_INVERSE_QUADRATIC = render_math(
        r"$\Phi_\mu(x) = 1/(1+(\mu x)^2)$",
        MATH_RBF_WIDTH,
        MATH_RBF_HEIGHT,
    )
    MATH_INVERSE_QUADRIC = render_math(
        r"$\Phi_\mu(x) = 1/\sqrt{1+(\mu x)^2}$",
        MATH_RBF_WIDTH,
        MATH_RBF_HEIGHT,
    )
    MATH_GAMMA_LN_TAU = render_math(r"$\gamma(\ln{\tau})$", 44, 20, fontsize=10)
    MATH_X = render_math(r"$x = |\ln{\tau} - \ln{\tau_m}|$", 96, 20, fontsize=10)
    MATH_TAU_M = render_math(r"$\tau_m$", 18, 20, fontsize=10)
    MATH_FWHM = render_math(r"$\mu = \frac{\Delta \ln{\tau}}{k}$", 200, 40)
    MATH_SHAPE = render_math(r"$\mu = k$", 200, 40)


signals.register(Signal.RENDER_MATH, process_math)


class SettingsMenu:
    def __init__(self, default_settings: DRTSettings, label_pad: int):
        self.main_group: Tag = dpg.generate_uuid()
        with dpg.child_window(border=False, height=250):
            with dpg.group(horizontal=True):
                dpg.add_text("Method".rjust(label_pad))
                attach_tooltip(tooltips.drt.method)

                self.method_combo: Combo = Combo(
                    default_value=drt_method_to_label[default_settings.method],
                    items=list(label_to_drt_method.keys()),
                    callback=lambda s, a, u: self.update_settings(),
                    user_data=label_to_drt_method,
                    width=-1,
                )

            with dpg.group(horizontal=True):
                dpg.add_text("Mode".rjust(label_pad))
                attach_tooltip(tooltips.drt.mode)

                self.mode_combo: Combo = Combo(
                    default_value=drt_mode_to_label[default_settings.mode],
                    items=list(label_to_drt_mode.keys()),
                    callback=lambda s, a, u: self.update_settings(),
                    user_data=label_to_drt_mode,
                    width=-1,
                )

            with dpg.group(horizontal=True):
                dpg.add_text("Lambda".rjust(label_pad))
                attach_tooltip(tooltips.drt.lambda_value)

                self.lambda_checkbox: Tag = dpg.generate_uuid()
                dpg.add_checkbox(
                    default_value=default_settings.lambda_value <= 0.0,
                    callback=lambda s, a, u: self.update_settings(),
                    tag=self.lambda_checkbox,
                )

                self.lambda_input: Tag = dpg.generate_uuid()
                dpg.add_input_float(
                    default_value=(
                        default_settings.lambda_value
                        if default_settings.lambda_value > 0.0
                        else 1e-3
                    ),
                    width=-1,
                    step=0.0,
                    format="%.3g",
                    on_enter=True,
                    tag=self.lambda_input,
                )

                self.lambda_combo: Combo = Combo(
                    items=[""],
                    user_data={"": CrossValidationMethod.NONE},
                    width=-1,
                )

            with dpg.group(horizontal=True):
                dpg.add_text("Derivative order".rjust(label_pad))
                with dpg.tooltip(dpg.last_item()):
                    with dpg.group(horizontal=True):
                        dpg.add_text("The derivative order of")
                        dpg.add_image(MATH_GAMMA_LN_TAU)
                        dpg.add_text(
                            "to use as the penalty in the Tikhonov regularization."
                        )
                    dpg.add_text(
                        "\nThis is only used when the method setting is set to BHT or TR-RBF."
                    )

                self.derivative_order_combo: Combo = Combo(
                    default_value=derivative_order_to_label[
                        default_settings.derivative_order
                    ],
                    items=list(label_to_derivative_order.keys()),
                    user_data=label_to_derivative_order,
                    width=-1,
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

                self.rbf_type_combo: Combo = Combo(
                    default_value=rbf_type_to_label[default_settings.rbf_type],
                    items=list(label_to_rbf_type.keys()),
                    user_data=label_to_rbf_type,
                    width=-1,
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

                self.rbf_shape_combo: Combo = Combo(
                    default_value=rbf_shape_to_label[default_settings.rbf_shape],
                    items=list(label_to_rbf_shape.keys()),
                    user_data=label_to_rbf_shape,
                    width=-1,
                )

            with dpg.group(horizontal=True):
                dpg.add_text("Shape coefficient".rjust(label_pad))
                attach_tooltip(tooltips.drt.shape_coeff)

                self.shape_coeff_input: Tag = dpg.generate_uuid()
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

                self.inductance_checkbox: Tag = dpg.generate_uuid()
                dpg.add_checkbox(
                    default_value=default_settings.inductance,
                    tag=self.inductance_checkbox,
                )

            with dpg.group(horizontal=True):
                dpg.add_text("Credible intervals".rjust(label_pad))
                attach_tooltip(tooltips.drt.credible_intervals)

                self.credible_intervals_checkbox: Tag = dpg.generate_uuid()
                dpg.add_checkbox(
                    default_value=default_settings.credible_intervals,
                    callback=lambda s, a, u: self.update_settings(),
                    tag=self.credible_intervals_checkbox,
                )

                dpg.add_text("Timeout")
                attach_tooltip(tooltips.drt.credible_intervals_timeout)

                self.timeout_input: Tag = dpg.generate_uuid()
                dpg.add_input_int(
                    default_value=default_settings.timeout,
                    min_value=1,
                    min_clamped=True,
                    step=0,
                    width=-1,
                    on_enter=True,
                    tag=self.timeout_input,
                )

            with dpg.group(horizontal=True):
                dpg.add_text("Number of samples".rjust(label_pad))
                attach_tooltip(tooltips.drt.num_samples)

                self.num_samples_input: Tag = dpg.generate_uuid()
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

                self.num_attempts_input: Tag = dpg.generate_uuid()
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

                self.maximum_symmetry_input: Tag = dpg.generate_uuid()
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

            with dpg.group(horizontal=True):
                dpg.add_text("Circuit".rjust(label_pad))
                attach_tooltip(tooltips.drt.circuit)

                self.circuit_combo: Tag = dpg.generate_uuid()
                dpg.add_combo(
                    default_value="",
                    items=[],
                    user_data={},
                    width=-1,
                    callback=lambda s, a, u: self.update_settings(),
                    tag=self.circuit_combo,
                )

            with dpg.group(horizontal=True):
                dpg.add_text("Gaussian width".rjust(label_pad))
                attach_tooltip(tooltips.drt.gaussian_width)

                self.gaussian_width_input: Tag = dpg.generate_uuid()
                dpg.add_input_float(
                    default_value=default_settings.gaussian_width,
                    width=-1,
                    min_value=0.0,
                    max_value=1.0,
                    step=0.0,
                    format="%.3g",
                    on_enter=True,
                    tag=self.gaussian_width_input,
                )

            with dpg.group(horizontal=True):
                dpg.add_text("Num. points per decade".rjust(label_pad))
                attach_tooltip(tooltips.drt.num_per_decade)

                self.num_per_decade_input: Tag = dpg.generate_uuid()
                dpg.add_input_int(
                    default_value=default_settings.num_per_decade,
                    width=-1,
                    min_value=1,
                    step=0,
                    on_enter=True,
                    tag=self.num_per_decade_input,
                )

        self.update_settings()

    def update_valid_circuits(self, fits: Dict[str, FitResult]):
        lookup: Dict[str, FitResult] = {}
        label: str
        fit: FitResult
        for label, fit in fits.items():
            try:
                _validate_circuit(fit.circuit)
            except DRTError:
                continue
            lookup[label] = fit
        if len(lookup) > 0:
            longest_cdc: int = max(
                map(
                    lambda _: len(_[: _.find(" (") + 1].strip()),
                    lookup.keys(),
                )
            )
            for label in list(lookup.keys()):
                new_label: str = (
                    f"{label[:label.find(' (') + 1].strip().ljust(longest_cdc + 1)}{label[label.find(' (') + 1:]}"
                )
                lookup[new_label] = lookup[label]
                if new_label != label:
                    del lookup[label]
        labels: List[str] = list(lookup.keys())
        dpg.configure_item(
            self.circuit_combo,
            default_value=labels[0] if len(labels) > 0 else "",
            items=labels,
            user_data=lookup,
        )
        self.update_settings()

    def get_lambda_value(self, method: DRTMethod) -> float:
        if not dpg.get_value(self.lambda_checkbox):
            return dpg.get_value(self.lambda_input)

        return -1.0

    def get_tr_nnls_lambda_method(self, method: DRTMethod) -> TRNNLSLambdaMethod:
        if method is not DRTMethod.TR_NNLS or not dpg.get_value(self.lambda_checkbox):
            return TRNNLSLambdaMethod.NONE

        tr_nnls_lambda_method: TRNNLSLambdaMethod = (
            self.lambda_combo.get_value()
        )
        if not isinstance(tr_nnls_lambda_method, TRNNLSLambdaMethod):
            return TRNNLSLambdaMethod.NONE

        return tr_nnls_lambda_method

    def get_cross_validation_method(self, method: DRTMethod) -> CrossValidationMethod:
        if method is not DRTMethod.TR_RBF or not dpg.get_value(self.lambda_checkbox):
            return CrossValidationMethod.NONE

        cross_validation_method: CrossValidationMethod = (
            self.lambda_combo.get_value()
        )
        if not isinstance(cross_validation_method, CrossValidationMethod):
            return CrossValidationMethod.NONE

        return cross_validation_method

    def get_settings(self) -> DRTSettings:
        fit: Optional[FitResult] = dpg.get_item_user_data(self.circuit_combo).get(
            dpg.get_value(self.circuit_combo),
        )
        method: DRTMethod = self.method_combo.get_value()
        lambda_value: float = self.get_lambda_value(method)
        cross_validation_method: CrossValidationMethod = (
            self.get_cross_validation_method(method)
        )
        tr_nnls_lambda_method: TRNNLSLambdaMethod = self.get_tr_nnls_lambda_method(method)

        return DRTSettings(
            method=method,
            mode=self.mode_combo.get_value(),
            lambda_value=lambda_value,
            rbf_type=self.rbf_type_combo.get_value(),
            derivative_order=self.derivative_order_combo.get_value(),
            rbf_shape=self.rbf_shape_combo.get_value(),
            shape_coeff=dpg.get_value(self.shape_coeff_input),
            inductance=dpg.get_value(self.inductance_checkbox),
            credible_intervals=dpg.get_value(self.credible_intervals_checkbox),
            timeout=dpg.get_value(self.timeout_input),
            num_samples=dpg.get_value(self.num_samples_input),
            num_attempts=dpg.get_value(self.num_attempts_input),
            maximum_symmetry=dpg.get_value(self.maximum_symmetry_input),
            fit=fit if method is DRTMethod.MRQ_FIT else None,
            gaussian_width=dpg.get_value(self.gaussian_width_input),
            num_per_decade=dpg.get_value(self.num_per_decade_input),
            cross_validation_method=cross_validation_method,
            tr_nnls_lambda_method=tr_nnls_lambda_method,
        )

    def set_settings(self, settings: DRTSettings):
        self.method_combo.set_value(settings.method)
        self.update_settings()
        self.mode_combo.set_value(settings.mode)

        if settings.method is DRTMethod.TR_NNLS:
            if settings.tr_nnls_lambda_method is TRNNLSLambdaMethod.NONE:
                dpg.set_value(self.lambda_input, settings.lambda_value)
                dpg.set_value(self.lambda_checkbox, False)
            else:
                dpg.set_value(self.lambda_checkbox, True)
                self.lambda_combo.set_value(settings.tr_nnls_lambda_method)

        elif settings.method is DRTMethod.TR_RBF:
            if settings.cross_validation_method is CrossValidationMethod.NONE:
                dpg.set_value(self.lambda_input, settings.lambda_value)
                dpg.set_value(self.lambda_checkbox, False)
            else:
                dpg.set_value(self.lambda_checkbox, True)
                self.lambda_combo.set_value(settings.cross_validation_method)

        self.rbf_type_combo.set_value(settings.rbf_type)
        self.derivative_order_combo.set_value(settings.derivative_order)
        self.rbf_shape_combo.set_value(settings.rbf_shape)
        dpg.set_value(self.shape_coeff_input, settings.shape_coeff)
        dpg.set_value(self.inductance_checkbox, settings.inductance)
        dpg.set_value(self.credible_intervals_checkbox, settings.credible_intervals)
        dpg.set_value(self.timeout_input, settings.timeout)
        dpg.set_value(self.num_samples_input, settings.num_samples)
        dpg.set_value(self.num_attempts_input, settings.num_attempts)
        dpg.set_value(self.maximum_symmetry_input, settings.maximum_symmetry)

        labels: List[str] = list(dpg.get_item_user_data(self.circuit_combo).keys())
        default_value: str = ""
        if settings.fit is not None:
            label: str
            fit: FitResult
            for label, fit in dpg.get_item_user_data(self.circuit_combo).items():
                if settings.fit.uuid == fit.uuid:
                    default_value = label
                    break

            if default_value == "" and len(labels) > 0:
                default_value = labels[0]

        dpg.configure_item(
            self.circuit_combo,
            default_value=default_value,
        )
        dpg.set_value(self.gaussian_width_input, settings.gaussian_width)
        dpg.set_value(self.num_per_decade_input, settings.num_per_decade)

        self.update_settings(settings)

    def show_setting(self, widget: int):
        assert type(widget) is int and widget > 0, widget
        dpg.enable_item(widget)
        dpg.show_item(dpg.get_item_parent(widget))

    def hide_setting(self, widget: int):
        assert type(widget) is int and widget > 0, widget
        dpg.disable_item(widget)
        dpg.hide_item(dpg.get_item_parent(widget))

    def update_settings(self, settings: Optional[DRTSettings] = None):
        if settings is None:
            settings = self.get_settings()

        if settings.method is DRTMethod.TR_NNLS:
            self.mode_combo.set_items(
                [
                    v
                    for k, v in drt_mode_to_label.items()
                    if k == DRTMode.REAL or k == DRTMode.IMAGINARY
                ]
            )
            self.mode_combo.set_label(
                drt_mode_to_label[
                    DRTMode.REAL if settings.mode == DRTMode.COMPLEX else settings.mode
                ]
            )
            self.show_setting(self.mode_combo.tag)

            tr_nnls_lambda_dict: Dict[str, TRNNLSLambdaMethod] = {
                k: v
                for k, v in label_to_tr_nnls_lambda_method.items()
                if v is not TRNNLSLambdaMethod.NONE
            }
            self.lambda_combo.set_items(list(tr_nnls_lambda_dict.keys()))
            self.lambda_combo.set_user_data(tr_nnls_lambda_dict)
            if settings.tr_nnls_lambda_method is TRNNLSLambdaMethod.NONE:
                self.lambda_combo.set_value(TRNNLSLambdaMethod.CUSTOM)
            else:
                self.lambda_combo.set_value(settings.tr_nnls_lambda_method)

        elif settings.method is DRTMethod.TR_RBF:
            self.mode_combo.set_items(list(label_to_drt_mode.keys()))
            self.mode_combo.set_value(settings.mode)
            self.show_setting(self.mode_combo.tag)

            tr_rbf_lambda_dict: Dict[str, CrossValidationMethod] = {
                k: v
                for k, v in label_to_cross_validation_method.items()
                if v is not CrossValidationMethod.NONE
            }
            self.lambda_combo.set_items(list(tr_rbf_lambda_dict.keys()))
            self.lambda_combo.set_user_data(tr_rbf_lambda_dict)
            if settings.cross_validation_method is CrossValidationMethod.NONE:
                self.lambda_combo.set_value(CrossValidationMethod.GCV)
            else:
                self.lambda_combo.set_value(settings.cross_validation_method)

        elif settings.method in (DRTMethod.BHT, DRTMethod.MRQ_FIT):
            self.hide_setting(self.mode_combo.tag)

        if settings.method in (DRTMethod.TR_RBF, DRTMethod.TR_NNLS):
            self.show_setting(self.lambda_checkbox)
            dpg.enable_item(self.lambda_input)
            if dpg.get_value(self.lambda_checkbox):
                dpg.hide_item(self.lambda_input)
                self.lambda_combo.show()
            else:
                dpg.show_item(self.lambda_input)
                self.lambda_combo.hide()

        else:
            self.hide_setting(self.lambda_checkbox)
            dpg.disable_item(self.lambda_input)

        if settings.method in (DRTMethod.TR_RBF, DRTMethod.BHT):
            self.show_setting(self.rbf_type_combo.tag)
            self.show_setting(self.derivative_order_combo.tag)
            self.show_setting(self.rbf_shape_combo.tag)
            self.show_setting(self.shape_coeff_input)
        else:
            self.hide_setting(self.rbf_type_combo.tag)
            self.hide_setting(self.derivative_order_combo.tag)
            self.hide_setting(self.rbf_shape_combo.tag)
            self.hide_setting(self.shape_coeff_input)

        if settings.method is DRTMethod.TR_RBF:
            self.show_setting(self.inductance_checkbox)
        else:
            self.hide_setting(self.inductance_checkbox)

        if settings.method is DRTMethod.TR_RBF:
            self.show_setting(self.credible_intervals_checkbox)
            self.show_setting(self.timeout_input)
        else:
            self.hide_setting(self.credible_intervals_checkbox)
            self.hide_setting(self.timeout_input)

        if settings.method is DRTMethod.BHT:
            self.show_setting(self.num_samples_input)
        elif settings.method is DRTMethod.TR_RBF:
            self.show_setting(self.num_samples_input)
            if settings.credible_intervals is False:
                dpg.disable_item(self.num_samples_input)
                dpg.disable_item(self.timeout_input)
        else:
            self.hide_setting(self.num_samples_input)

        if settings.method is DRTMethod.BHT:
            self.show_setting(self.num_attempts_input)
        else:
            self.hide_setting(self.num_attempts_input)

        if settings.method is DRTMethod.BHT:
            self.show_setting(self.maximum_symmetry_input)
        else:
            self.hide_setting(self.maximum_symmetry_input)

        if settings.method is DRTMethod.MRQ_FIT:
            self.show_setting(self.circuit_combo)
            self.show_setting(self.gaussian_width_input)
            self.show_setting(self.num_per_decade_input)
            dpg.enable_item(self.num_per_decade_input)
        else:
            self.hide_setting(self.circuit_combo)
            self.hide_setting(self.gaussian_width_input)
            self.hide_setting(self.num_per_decade_input)

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
                        "log X² (pseudo)",
                        tooltips.fitting.pseudo_chisqr,
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
                        cell: Tag = dpg.add_text("")
                        dpg.set_item_user_data(cell, attach_tooltip("", parent=cell))

            dpg.add_spacer(height=8)

    def clear(self, hide: bool):
        if hide:
            dpg.hide_item(self._header)

        row: int
        for row in dpg.get_item_children(self._table, slot=1):
            cell: Tag = dpg.get_item_children(row, slot=1)[1]
            dpg.set_value(cell, "")

    def populate(self, drt: DRTResult):
        dpg.show_item(self._header)
        filter_key: str = drt_method_to_label[drt.settings.method]
        dpg.set_value(self._table, filter_key)
        statistics: List[str] = [
            f"{log(drt.pseudo_chisqr):.3g}",
            f"{drt.lambda_value:.3e}",
        ]

        visible_items: List[bool] = []

        i: int
        row: int
        for i, row in enumerate(dpg.get_item_children(self._table, slot=1)):
            cell: Tag = dpg.get_item_children(row, slot=1)[2]
            dpg.set_value(cell, statistics[i])
            update_tooltip(tag=dpg.get_item_user_data(cell), msg=statistics[i])
            visible_items.append(is_filtered_item_visible(row, filter_key))

        dpg.set_item_height(
            self._table,
            18 + 23 * len(list(filter(lambda _: _ is True, visible_items))),
        )


class ScoresTable:
    def __init__(self):
        label_pad: int = 23
        self._header: Tag = dpg.generate_uuid()
        with dpg.collapsing_header(label=" Scores", leaf=True, tag=self._header):
            self._table: Tag = dpg.generate_uuid()
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
                for label, tooltip in [
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

        key: str
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
            tags: List[Tag] = dpg.get_item_children(row, slot=1)[2:]
            dpg.set_value(tags[0], real_values[i])
            dpg.set_value(tags[1], imaginary_values[i])

        dpg.set_item_height(self._table, 18 + 23 * len(keys))


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
                height=18 + 23 * 15,
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
                filter_key: str
                for label, filter_key in [
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
                    (
                        "Circuit",
                        drt_method_to_label[DRTMethod.MRQ_FIT],
                    ),
                    (
                        "Gaussian width",
                        drt_method_to_label[DRTMethod.MRQ_FIT],
                    ),
                    (
                        "Num. per decade",
                        drt_method_to_label[DRTMethod.MRQ_FIT],
                    ),
                ]:
                    with dpg.table_row(filter_key=filter_key):
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
                        Signal.APPLY_DRT_SETTINGS,
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

    def populate(self, drt: DRTResult, data: DataSet):
        dpg.show_item(self._header)
        filter_key: str = drt_method_to_label[drt.settings.method]
        dpg.set_value(self._table, filter_key)

        lambda_label: str = ""
        if drt.settings.lambda_value > 0.0:
            lambda_label = f"{drt.settings.lambda_value:.3e}"
        elif drt.settings.method is DRTMethod.TR_NNLS:
            if drt.settings.tr_nnls_lambda_method is TRNNLSLambdaMethod.NONE:
                lambda_label = f"{drt.settings.lambda_value:.3e}"
            else:
                lambda_label = tr_nnls_lambda_method_to_label[drt.settings.tr_nnls_lambda_method]
        elif drt.settings.method is DRTMethod.TR_RBF:
            if drt.settings.cross_validation_method is CrossValidationMethod.NONE:
                lambda_label = f"{drt.settings.lambda_value:.3e}"
            else:
                lambda_label = cross_validation_method_to_label[drt.settings.cross_validation_method]
        else:
            # TODO: Handle other cases
            pass

        values: List[str] = [
            drt_method_to_label[drt.settings.method],
            drt_mode_to_label[drt.settings.mode],
            lambda_label,
            rbf_type_to_label[drt.settings.rbf_type],
            derivative_order_to_label[drt.settings.derivative_order],
            rbf_shape_to_label[drt.settings.rbf_shape],
            f"{drt.settings.shape_coeff:.3g}",
            "True" if drt.settings.inductance else "False",
            "True" if drt.settings.credible_intervals else "False",
            str(drt.settings.num_samples),
            str(drt.settings.num_attempts),
            f"{drt.settings.maximum_symmetry:.3g}",
            str(drt.settings.fit.circuit) if drt.settings.fit is not None else "",
            f"{drt.settings.gaussian_width:.3g}",
            str(drt.settings.num_per_decade),
        ]
        visible_items: List[bool] = []

        i: int
        row: int
        for i, row in enumerate(dpg.get_item_children(self._table, slot=1)):
            if not is_filtered_item_visible(row, filter_key):
                visible_items.append(False)
                continue

            tag: List[Tag] = dpg.get_item_children(row, slot=1)[1]
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


class DRTResultsCombo(ResultsCombo):
    def selection_callback(self, sender: int, app_data: str, user_data: tuple):
        signals.emit(
            Signal.SELECT_DRT_RESULT,
            drt=user_data[0].get(app_data),
            data=user_data[1],
        )

    def adjust_label(self, old: str, longest: int) -> str:
        i: int = old.rfind(" (")
        label: str
        timestamp: str
        label, timestamp = (old[:i], old[i + 1 :])

        return f"{label.ljust(longest)} {timestamp}"


class DRTTab:
    def __init__(self, state):
        self.state = state
        self.queued_update: Optional[Callable] = None
        self.create_tab(state)

    def create_tab(self, state):
        label_pad: int = 24
        self.tab: Tag = dpg.generate_uuid()
        with dpg.tab(label="DRT analysis", tag=self.tab):
            with dpg.group(horizontal=True):
                self.create_sidebar(state, label_pad)
                self.create_plots()

    def create_sidebar(self, state, label_pad: int):
        self.sidebar_width: int = 350
        self.sidebar_window: Tag = dpg.generate_uuid()
        with dpg.child_window(
            border=False,
            width=self.sidebar_width,
            tag=self.sidebar_window,
        ):
            self.create_settings_menu(state, label_pad)
            self.create_results_menu()
            self.create_results_tables()

    def create_settings_menu(self, state, label_pad: int):
        with dpg.child_window(
            border=True,
            width=-1,
            height=290,
        ):
            self.settings_menu: SettingsMenu = SettingsMenu(
                state.config.default_drt_settings, label_pad
            )
            with dpg.group(horizontal=True):
                self.visibility_item: Tag = dpg.generate_uuid()
                dpg.add_text("?".rjust(label_pad), tag=self.visibility_item)
                attach_tooltip(tooltips.drt.perform)

                self.perform_drt_button: Tag = dpg.generate_uuid()
                dpg.add_button(
                    label="Perform",
                    callback=lambda s, a, u: signals.emit(
                        Signal.PERFORM_DRT,
                        data=u,
                        settings=self.get_settings(),
                    ),
                    user_data=None,
                    width=-70,
                    tag=self.perform_drt_button,
                )

                dpg.add_button(
                    label="Batch",
                    callback=lambda s, a, u: signals.emit(
                        Signal.BATCH_PERFORM_ANALYSIS,
                        settings=self.get_settings(),
                    ),
                    width=-1,
                )

    def create_results_menu(self):
        with dpg.child_window(width=-1, height=82):
            label_pad = 8
            with dpg.group(horizontal=True):
                self.data_sets_combo: DataSetsCombo = DataSetsCombo(
                    label="Data set".rjust(label_pad),
                    width=-60,
                )

            with dpg.group(horizontal=True):
                self.results_combo: DRTResultsCombo = DRTResultsCombo(
                    label="Result".rjust(label_pad),
                    width=-60,
                )

                self.delete_button: Tag = dpg.generate_uuid()
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
                self.output_combo: Combo = Combo(
                    items=list(label_to_drt_output.keys()),
                    user_data=label_to_drt_output,
                    width=-60,
                )

                self.copy_output_button: Tag = dpg.generate_uuid()
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

    def create_results_tables(self):
        with dpg.child_window(width=-1, height=-1):
            self.result_group: Tag = dpg.generate_uuid()
            with dpg.group(tag=self.result_group):
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
                self.scores_table: ScoresTable = ScoresTable()
                self.settings_table: SettingsTable = SettingsTable()

    def create_plots(self):
        self.plot_window: Tag = dpg.generate_uuid()
        with dpg.child_window(
            border=False,
            width=-1,
            height=-1,
            tag=self.plot_window,
        ):
            self.create_drt_plot()
            dpg.add_spacer(height=4)
            dpg.add_separator()
            dpg.add_spacer(height=4)
            self.plot_tab_bar: Tag = dpg.generate_uuid()
            self.minimum_plot_height: int = -24

            with dpg.tab_bar(tag=self.plot_tab_bar):
                self.create_nyquist_plot()
                self.create_bode_plot()
                impedance_tab: int = self.create_impedance_plot()
                self.create_residuals_plot()

            pad_tab_labels(self.plot_tab_bar)
            dpg.set_value(self.plot_tab_bar, impedance_tab)
            self.plots: List[Plot] = [
                self.nyquist_plot,
                self.bode_plot,
                self.impedance_plot,
            ]

    def create_drt_plot(self):
        self.drt_plot: DRT = DRT(width=-1, height=400)
        self.drt_plot.plot(
            tau=array([]),
            gamma=array([]),
            label="gamma",
            theme=themes.drt.real_gamma,
        )
        with dpg.group(horizontal=True):
            self.enlarge_drt_button: Tag = dpg.generate_uuid()
            dpg.add_button(
                label="Enlarge plot",
                callback=self.show_enlarged_drt,
                tag=self.enlarge_drt_button,
            )

            dpg.add_button(
                label="Copy as CSV",
                callback=lambda s, a, u: signals.emit(
                    Signal.COPY_PLOT_DATA,
                    plot=self.drt_plot,
                    context=Context.DRT_TAB,
                ),
            )
            attach_tooltip(tooltips.general.copy_plot_data_as_csv)

            self.adjust_drt_limits_checkbox: Tag = dpg.generate_uuid()
            dpg.add_checkbox(
                label="Adjust limits",
                default_value=True,
                tag=self.adjust_drt_limits_checkbox,
            )
            attach_tooltip(tooltips.general.adjust_drt_limits)

            self.toggle_drt_frequency_checkbox: Tag = dpg.generate_uuid()
            dpg.add_checkbox(
                label="Frequency",
                default_value=False,
                callback=lambda s, a, u: self.toggle_drt_frequency(a),
                tag=self.toggle_drt_frequency_checkbox,
            )
            attach_tooltip(tooltips.general.plot_drt_frequency)

    def toggle_drt_frequency(self, frequency: bool):
        self.drt_plot.set_frequency(frequency)

    def create_nyquist_plot(self):
        with dpg.tab(label="Nyquist"):
            self.nyquist_plot: Nyquist = Nyquist(
                width=-1,
                height=self.minimum_plot_height,
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
                        context=Context.DRT_TAB,
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
                height=self.minimum_plot_height,
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
                        context=Context.DRT_TAB,
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

    def create_impedance_plot(self) -> int:
        tab: int
        with dpg.tab(label="Real & imag.") as tab:
            self.impedance_plot: Impedance = Impedance(
                width=-1,
                height=self.minimum_plot_height,
            )
            self.impedance_plot.plot(
                frequencies=array([]),
                impedances=array([], dtype=complex128),
                labels=(
                    "Re(data)",
                    "Im(data)",
                ),
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
                fit=True,
                line=True,
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
                        context=Context.DRT_TAB,
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

        return tab

    def create_residuals_plot(self):
        with dpg.tab(label="Residuals"):
            self.residuals_plot: Residuals = Residuals(
                width=-1,
                height=self.minimum_plot_height,
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
                        context=Context.DRT_TAB,
                    ),
                )
                attach_tooltip(tooltips.general.copy_plot_data_as_csv)
                dpg.add_checkbox(
                    label="Adjust limits",
                    default_value=True,
                    tag=self.adjust_residuals_limits_checkbox,
                )
                attach_tooltip(tooltips.general.adjust_residuals_limits)

    def is_visible(self) -> bool:
        return dpg.is_item_visible(self.visibility_item)

    def has_active_input(self) -> bool:
        return self.settings_menu.has_active_input()

    def get_settings(self) -> DRTSettings:
        return self.settings_menu.get_settings()

    def set_settings(self, settings: DRTSettings):
        self.settings_menu.set_settings(settings)

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
        height = round(height / 2) - 24 * 2 + 1
        self.drt_plot.resize(-1, height)

        for plot in self.plots:
            plot.resize(-1, height)

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

        self.nyquist_plot.clear(delete=False)
        self.bode_plot.clear(delete=False)
        self.impedance_plot.clear(delete=False)
        self.residuals_plot.clear(delete=False)

    def next_plot_tab(self):
        tabs: List[Tag] = dpg.get_item_children(self.plot_tab_bar, slot=1)
        index: int = tabs.index(dpg.get_value(self.plot_tab_bar)) + 1
        dpg.set_value(self.plot_tab_bar, tabs[index % len(tabs)])

    def previous_plot_tab(self):
        tabs: List[Tag] = dpg.get_item_children(self.plot_tab_bar, slot=1)
        index: int = tabs.index(dpg.get_value(self.plot_tab_bar)) - 1
        dpg.set_value(self.plot_tab_bar, tabs[index % len(tabs)])

    def show_enlarged_drt(self):
        signals.emit(
            Signal.SHOW_ENLARGED_PLOT,
            plot=self.drt_plot,
            adjust_limits=dpg.get_value(self.adjust_drt_limits_checkbox),
            frequency=dpg.get_value(self.toggle_drt_frequency_checkbox),
        )

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
        return self.data_sets_combo.get_next()

    def get_previous_data_set(self) -> Optional[DataSet]:
        return self.data_sets_combo.get_previous()

    def get_next_result(self) -> Optional[DRTResult]:
        return self.results_combo.get_next()

    def get_previous_result(self) -> Optional[DRTResult]:
        return self.results_combo.get_previous()

    def populate_fits(self, fits: List[FitResult]):
        assert type(fits) is dict, fits
        self.settings_menu.update_valid_circuits(fits)

    def select_data_set(self, data: Optional[DataSet]):
        assert type(data) is DataSet or data is None, data
        self.clear(hide=data is None)
        dpg.set_item_user_data(self.perform_drt_button, data)
        if data is None:
            return
        self.data_sets_combo.set(data.get_label())
        freq: ndarray = data.get_frequencies()
        Z: ndarray = data.get_impedances()
        self.nyquist_plot.update(
            index=0,
            impedances=Z,
        )
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

    def assert_drt_up_to_date(self, drt: DRTResult, data: DataSet):
        # Check if the number of unmasked points is the same
        Z_exp: ndarray = data.get_impedances()
        Z_drt: ndarray = drt.get_impedances()
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
            drt.get_frequencies(), data.get_frequencies()
        ), "The frequencies differ!"

        residuals: ComplexResiduals = _calculate_residuals(Z_exp, Z_drt)
        assert allclose(drt.residuals.real, residuals.real) and allclose(
            drt.residuals.imag, residuals.imag
        ), "The data set's impedances differ from what they were when the DRT analysis was performed!"

    def select_drt_result(
        self,
        drt: Optional[DRTResult],
        data: Optional[DataSet],
    ):
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

            if dpg.get_value(self.adjust_nyquist_limits_checkbox):
                self.nyquist_plot.queue_limits_adjustment()

            if dpg.get_value(self.adjust_bode_limits_checkbox):
                self.bode_plot.queue_limits_adjustment()

            if dpg.get_value(self.adjust_impedance_limits_checkbox):
                self.impedance_plot.queue_limits_adjustment()

            if dpg.get_value(self.adjust_residuals_limits_checkbox):
                self.residuals_plot.queue_limits_adjustment()

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
        real_gamma: ndarray
        imaginary_gamma: ndarray
        tau, real_gamma, imaginary_gamma = drt.get_drt_data()
        self.drt_plot.update(
            index=0,
            tau=tau,
            gamma=real_gamma,
            label="real" if drt.settings.method == DRTMethod.BHT else "gamma",
        )

        if (
            drt.settings.method == DRTMethod.TR_RBF
            and drt.settings.credible_intervals is True
        ):
            mean: ndarray
            lower: ndarray
            upper: ndarray
            tau, mean, lower, upper = drt.get_drt_credible_intervals_data()
            self.drt_plot.plot(
                tau=tau,
                gamma=mean,
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
        elif drt.settings.method == DRTMethod.BHT:
            self.drt_plot.plot(
                tau=tau,
                gamma=imaginary_gamma,
                label="imag.",
                theme=themes.drt.imaginary_gamma,
            )

        Z: ComplexImpedances = drt.get_impedances()
        self.nyquist_plot.update(
            index=1,
            impedances=Z,
        )
        self.nyquist_plot.update(
            index=2,
            impedances=Z,
        )

        freq: Frequencies = drt.get_frequencies()
        self.bode_plot.update(
            index=1,
            frequencies=freq,
            impedances=Z,
        )
        self.bode_plot.update(
            index=2,
            frequencies=freq,
            impedances=Z,
        )

        self.impedance_plot.update(
            index=1,
            frequencies=freq,
            impedances=Z,
        )
        self.impedance_plot.update(
            index=2,
            frequencies=freq,
            impedances=Z,
        )

        freq, real, imaginary = drt.get_residuals_data()
        self.residuals_plot.update(
            index=0,
            frequencies=freq,
            real=real,
            imaginary=imaginary,
        )

        if dpg.get_value(self.adjust_nyquist_limits_checkbox):
            self.nyquist_plot.queue_limits_adjustment()

        if dpg.get_value(self.adjust_bode_limits_checkbox):
            self.bode_plot.queue_limits_adjustment()

        if dpg.get_value(self.adjust_drt_limits_checkbox):
            self.drt_plot.queue_limits_adjustment()

        if dpg.get_value(self.adjust_impedance_limits_checkbox):
            self.impedance_plot.queue_limits_adjustment()

        if dpg.get_value(self.adjust_residuals_limits_checkbox):
            self.residuals_plot.queue_limits_adjustment()

    def get_active_output(self) -> Optional[DRTOutput]:
        return self.output_combo.get_value()
