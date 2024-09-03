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

from math import isclose
from traceback import format_exc
from typing import (
    Callable,
    Dict,
    List,
    Optional,
    Tuple,
)
from numpy import (
    allclose,
    array,
    complex128,
    inf,
    isnan,
    log10 as log,
    ndarray,
)
from pyimpspec import (
    Circuit,
    ComplexImpedance,
    ComplexResiduals,
    Connection,
    Container,
    Element,
    FittedParameter,
    Frequencies,
)
import pyimpspec
from pyimpspec.analysis.utility import _calculate_residuals, _interpolate
import dearpygui.dearpygui as dpg
from deareis.signals import Signal
import deareis.signals as signals
from deareis.enums import (
    Context,
    CNLSMethod,
    FitSimOutput,
    Weight,
    label_to_cnls_method,
    label_to_weight,
    label_to_fit_sim_output,
    cnls_method_to_label,
    weight_to_label,
)
from deareis.data import (
    DataSet,
    FitResult,
    FitSettings,
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
from deareis.utility import (
    align_numbers,
    calculate_window_position_dimensions,
    find_parent_containers,
    format_number,
    pad_tab_labels,
    process_cdc,
    render_math,
)
import deareis.themes as themes
from deareis.gui.circuit_editor import (
    CircuitPreview,
    CircuitEditor,
)
from deareis.gui.shared import (
    DataSetsCombo,
    ResultsCombo,
)
from deareis.gui.widgets.combo import Combo
from deareis.typing.helpers import Tag


MATH_WEIGHT_WIDTH: int = 300
MATH_WEIGHT_HEIGHT: int = 40
MATH_WEIGHT_MODULUS: int = -1
MATH_WEIGHT_PROPORTIONAL: int = -1
MATH_WEIGHT_UNITY: int = -1
MATH_WEIGHT_BOUKAMP: int = -1
MATH_Z_FIT: int = -1
MATH_Z_EXP: int = -1


def process_math():
    global MATH_WEIGHT_MODULUS
    global MATH_WEIGHT_PROPORTIONAL
    global MATH_WEIGHT_UNITY
    global MATH_WEIGHT_BOUKAMP
    global MATH_Z_FIT
    global MATH_Z_EXP
    MATH_WEIGHT_MODULUS = render_math(
        r"$w_i = [|Z_{\rm re}(f_i)|, |Z_{\rm im}(f_i)|]^{-1}$",
        width=MATH_WEIGHT_WIDTH,
        height=MATH_WEIGHT_HEIGHT,
    )
    MATH_WEIGHT_PROPORTIONAL = render_math(
        r"$w_i = [Z_{\rm re}(f_i)^2, Z_{\rm im}(f_i)^2]^{-1}$",
        width=MATH_WEIGHT_WIDTH,
        height=MATH_WEIGHT_HEIGHT,
    )
    MATH_WEIGHT_UNITY = render_math(
        r"$w_i = [1]$",
        width=MATH_WEIGHT_WIDTH,
        height=MATH_WEIGHT_HEIGHT,
    )
    MATH_WEIGHT_BOUKAMP = render_math(
        r"$w_i = [(Z_{{\rm re},i})^2 + (Z_{{\rm im},i})^2]^{-1}$",
        width=MATH_WEIGHT_WIDTH,
        height=MATH_WEIGHT_HEIGHT,
    )
    MATH_Z_FIT = render_math(
        r"$Z_{\rm re/im}(f_i)$",
        width=54,
        height=20,
        fontsize=10,
    )
    MATH_Z_EXP = render_math(
        r"$Z_{{\rm re/im},i}$",
        width=44,
        height=20,
        fontsize=10,
    )


signals.register(Signal.RENDER_MATH, process_math)


class SettingsMenu:
    def __init__(
        self,
        default_settings: FitSettings,
        label_pad: int,
        circuit_editor: Optional[CircuitEditor] = None,
        editor_callback: Optional[Callable] = None,
    ):
        self.circuit_editor: Optional[CircuitEditor] = circuit_editor
        with dpg.group(horizontal=True):
            dpg.add_text("Circuit".rjust(label_pad))
            attach_tooltip(tooltips.fitting.cdc)

            self.cdc_input: Tag = dpg.generate_uuid()
            dpg.add_input_text(
                width=-50 if circuit_editor is not None else -1,
                tag=self.cdc_input,
                on_enter=True,
                callback=lambda s, a, u: self.parse_cdc(a, s),
            )

            self.cdc_tooltip: Tag = dpg.generate_uuid()
            attach_tooltip("", tag=self.cdc_tooltip, parent=self.cdc_input)
            dpg.hide_item(dpg.get_item_parent(self.cdc_tooltip))

            if circuit_editor is not None:
                self.editor_button: Tag = dpg.generate_uuid()
                dpg.add_button(
                    label="Edit",
                    callback=editor_callback,
                    width=-1,
                    tag=self.editor_button,
                    user_data={},
                )
                attach_tooltip(tooltips.general.open_circuit_editor)

        with dpg.group(horizontal=True):
            dpg.add_text("Method".rjust(label_pad))
            attach_tooltip(tooltips.fitting.method)

            self.method_combo: Combo = Combo(
                items=list(label_to_cnls_method.keys()),
                default_value="Auto",
                user_data=label_to_cnls_method,
                width=-1,
            )

        with dpg.group(horizontal=True):
            dpg.add_text("Weight".rjust(label_pad))
            with dpg.tooltip(dpg.last_item()):
                dpg.add_text(
                    "The weight function used when calculating residuals during fitting."
                )
                with dpg.table(
                    borders_outerV=True,
                    borders_outerH=True,
                    borders_innerV=True,
                    borders_innerH=True,
                    scrollY=True,
                    freeze_rows=1,
                    height=18 + 4 * (MATH_WEIGHT_HEIGHT + 4),
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
                        dpg.add_text("Modulus")
                        dpg.add_image(MATH_WEIGHT_MODULUS)

                    with dpg.table_row():
                        dpg.add_text("Proportional")
                        dpg.add_image(MATH_WEIGHT_PROPORTIONAL)

                    with dpg.table_row():
                        dpg.add_text("Unity")
                        dpg.add_image(MATH_WEIGHT_UNITY)

                    with dpg.table_row():
                        dpg.add_text("Boukamp (eq. 13)")
                        dpg.add_image(MATH_WEIGHT_BOUKAMP)

                with dpg.group(horizontal=True):
                    dpg.add_image(MATH_Z_FIT)
                    dpg.add_text(
                        "is the real/imaginary part of the ith modeled impedance."
                    )

                with dpg.group(horizontal=True):
                    dpg.add_image(MATH_Z_EXP)
                    dpg.add_text(
                        "is the real/imaginary part of the ith experimental impedance."
                    )

                dpg.add_text(tooltips.fitting.weight, wrap=500)

            self.weight_combo: Combo = Combo(
                items=list(label_to_weight.keys()),
                default_value="Auto",
                user_data=label_to_weight,
                width=-1,
            )

        with dpg.group(horizontal=True):
            dpg.add_text("Max. num. of func. eval.".rjust(label_pad))
            attach_tooltip(tooltips.fitting.nfev)

            self.max_nfev_input: Tag = dpg.generate_uuid()
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
            dpg.add_text("Timeout".rjust(label_pad))
            attach_tooltip(tooltips.fitting.timeout)

            self.timeout_input: Tag = dpg.generate_uuid()
            dpg.add_input_int(
                default_value=0,
                min_value=0,
                min_clamped=True,
                step=0,
                on_enter=True,
                tag=self.timeout_input,
                width=-1,
            )

        self.set_settings(default_settings)

    def get_settings(self) -> FitSettings:
        cdc: str = dpg.get_value(self.cdc_input) or ""
        circuit: Optional[Circuit] = dpg.get_item_user_data(self.cdc_input)
        if circuit is None or cdc != circuit.to_string():
            circuit = self.parse_cdc(cdc, self.cdc_input)

        return FitSettings(
            cdc=circuit.serialize() if circuit is not None else "",
            method=self.method_combo.get_value(),
            weight=self.weight_combo.get_value(),
            max_nfev=dpg.get_value(self.max_nfev_input),
            timeout=dpg.get_value(self.timeout_input),
        )

    def set_settings(self, settings: FitSettings):
        assert type(settings) is FitSettings, settings
        self.parse_cdc(settings.cdc)
        self.method_combo.set_value(settings.method)
        self.weight_combo.set_value(settings.weight)
        dpg.set_value(self.max_nfev_input, settings.max_nfev)
        dpg.set_value(self.timeout_input, settings.timeout)

    def parse_cdc(self, cdc: str, sender: int = -1) -> Optional[Circuit]:
        assert type(cdc) is str, cdc
        assert type(sender) is int, sender
        circuit: Optional[Circuit]
        msg: str
        try:
            circuit, msg = process_cdc(cdc)
        except Exception:
            signals.emit(
                Signal.SHOW_ERROR_MESSAGE,
                traceback=format_exc(),
            )
            return None

        if circuit is None:
            dpg.bind_item_theme(self.cdc_input, themes.cdc.invalid)
            update_tooltip(self.cdc_tooltip, msg)
            dpg.show_item(dpg.get_item_parent(self.cdc_tooltip))
            dpg.set_item_user_data(self.cdc_input, None)
            return None

        dpg.bind_item_theme(self.cdc_input, themes.cdc.valid)
        dpg.hide_item(dpg.get_item_parent(self.cdc_tooltip))
        dpg.set_item_user_data(self.cdc_input, circuit)
        if sender != self.cdc_input:
            dpg.set_value(self.cdc_input, circuit.to_string())

        return circuit

    def has_active_input(self) -> bool:
        return dpg.is_item_active(self.cdc_input) or dpg.is_item_active(
            self.max_nfev_input
        )


class ParametersTable:
    def __init__(self, fitted_values_callback: Callable):
        self._header: Tag = dpg.generate_uuid()
        with dpg.collapsing_header(
            label=" Parameters",
            leaf=True,
            tag=self._header,
        ):
            self._table: Tag = dpg.generate_uuid()
            with dpg.table(
                borders_outerV=True,
                borders_outerH=True,
                borders_innerV=True,
                borders_innerH=True,
                scrollY=True,
                freeze_rows=1,
                height=18 + 23,
                tag=self._table,
            ):
                dpg.add_table_column(
                    label="Element",
                    width_fixed=True,
                )
                attach_tooltip(tooltips.fitting.element)

                dpg.add_table_column(
                    label="Parameter",
                    width_fixed=True,
                )
                attach_tooltip(tooltips.fitting.parameter)

                dpg.add_table_column(
                    label="Value",
                    width_fixed=True,
                )
                attach_tooltip(tooltips.fitting.parameter_value)

                dpg.add_table_column(
                    label="Error (%)",
                )
                attach_tooltip(tooltips.fitting.error)

            dpg.add_spacer(height=8)

            self._copy_fitted_values_button: Tag = dpg.generate_uuid()
            dpg.add_button(
                label="Apply fitted values as initial values",
                callback=fitted_values_callback,
                tag=self._copy_fitted_values_button,
                width=-1,
            )
            attach_tooltip(tooltips.fitting.apply_fitted_as_initial)

            dpg.add_spacer(height=8)

    def clear(self, hide: bool):
        if hide:
            dpg.hide_item(self._header)

        dpg.delete_item(self._table, children_only=True, slot=1)

    def limited_parameter(
        self,
        key: str,
        value: float,
        element: Element,
    ) -> Tuple[str, int]:
        lower_limit: float = element.get_lower_limit(key)
        upper_limit: float = element.get_upper_limit(key)
        if isclose(value, lower_limit):
            return (
                "\n\nRestricted by lower limit!",
                themes.fitting.limited_parameter,
            )
        elif isclose(value, upper_limit):
            return (
                "\n\nRestricted by upper limit!",
                themes.fitting.limited_parameter,
            )
        else:
            return (
                "",
                -1,
            )

    def populate(self, fit: FitResult):
        dpg.show_item(self._header)
        column_pads: List[int] = [
            10,
            11,
            10,
            10,
        ]
        if fit is None:
            with dpg.table_row(parent=self._table):
                dpg.add_text("".ljust(column_pads[0]))
                dpg.add_text("".ljust(column_pads[1]))
                dpg.add_text("".ljust(column_pads[2]))
                dpg.add_text("".ljust(column_pads[3]))
            return

        element_names: List[str] = []
        element_tooltips: List[str] = []

        parameter_labels: List[str] = []
        parameter_tooltips: List[str] = []

        values: List[str] = []
        value_tooltips: List[str] = []
        value_themes: List[int] = []

        error_values: List[str] = []
        error_tooltips: List[str] = []
        error_themes: List[int] = []

        internal_identifiers: Dict[int, Element] = {
            v: k
            for k, v in fit.circuit.generate_element_identifiers(running=True).items()
        }
        external_identifiers: Dict[Element, int] = (
            fit.circuit.generate_element_identifiers(running=False)
        )

        parent_containers: Dict[Element, Container] = find_parent_containers(
            fit.circuit
        )

        element_name: str
        element_tooltip: str
        parameter_label: str
        parameter_tooltip: str
        value: str
        value_tooltip: str
        error_value: str
        error_tooltip: str
        parameters: Dict[str, FittedParameter]
        element: Element
        for _, element in sorted(internal_identifiers.items(), key=lambda _: _[0]):
            element_name = fit.circuit.get_element_name(
                element,
                identifiers=external_identifiers,
            )
            lines: List[str] = []
            line: str
            for line in element.get_extended_description().split("\n"):
                if line.strip().startswith(":math:"):
                    break
                lines.append(line)

            element_tooltip = "\n".join(lines).strip()
            parameters = fit.parameters[element_name]

            if element in parent_containers:
                parent_name: str = fit.circuit.get_element_name(
                    parent_containers[element],
                    identifiers=external_identifiers,
                )
                subcircuit_name: str
                subcircuit: Optional[Connection]

                for subcircuit_name, subcircuit in (
                    parent_containers[element].get_subcircuits().items()
                ):
                    if subcircuit is None:
                        continue

                    if element in subcircuit:
                        break

                element_name = f"*{element_name}"
                element_tooltip = f"*Nested inside {parent_name}'s {subcircuit_name} subcircuit\n\n{element_tooltip}"

            parameter: FittedParameter
            for parameter_label in sorted(parameters):
                parameter = parameters[parameter_label]
                element_names.append(element_name)
                element_tooltips.append(element_tooltip)
                parameter_labels.append(
                    parameter_label + (" (f)" if parameter.fixed else "")
                )
                unit: str = element.get_unit(parameter_label)
                parameter_tooltips.append(
                    (
                        f"{element.get_value_description(parameter_label)}\n\n"
                        f"Unit: {unit}\n"
                        + ("Fixed parameter" if parameter.fixed else "")
                    ).strip()
                )

                values.append(
                    f"{format_number(parameter.value, width=9, significants=3)}"
                )
                value_tooltips.append(
                    f"{format_number(parameter.value, decimals=6).strip()} {unit}".strip()
                )
                value_tooltip_appendix: str
                value_theme: int = -1
                if not parameter.fixed:
                    value_tooltip_appendix, value_theme = self.limited_parameter(
                        parameter_label,
                        parameter.value,
                        element,
                    )
                    value_tooltips[-1] += value_tooltip_appendix

                value_themes.append(value_theme)
                error_theme: int = -1
                if not isnan(parameter.stderr):
                    # TODO: Add settings for thresholds?
                    error: float = parameter.get_relative_error() * 100
                    if error > 100.0:
                        error_value = ">100"
                        error_theme = themes.fitting.huge_error
                    elif error < 0.01:
                        error_value = "<0.01"
                    else:
                        error_value = (
                            f"{format_number(error, exponent=False, significants=3)}"
                        )
                        if error >= 5.0:
                            error_theme = themes.fitting.large_error

                    error_tooltip = f"±{format_number(parameter.stderr, decimals=6).strip()} {parameter.unit}".strip()

                else:
                    error_value = "-"
                    if not parameter.fixed:
                        error_tooltip = "Unable to estimate error."
                    else:
                        error_tooltip = "Fixed parameter."

                error_values.append(error_value)
                error_tooltips.append(error_tooltip)
                error_themes.append(error_theme)

        values = align_numbers(values)
        error_values = align_numbers(error_values)
        num_rows: int = 0

        for (
            element_name,
            element_tooltip,
            parameter_label,
            parameter_tooltip,
            value,
            value_tooltip,
            value_theme,
            error_value,
            error_tooltip,
            error_theme,
        ) in zip(
            element_names,
            element_tooltips,
            parameter_labels,
            parameter_tooltips,
            values,
            value_tooltips,
            value_themes,
            error_values,
            error_tooltips,
            error_themes,
        ):
            with dpg.table_row(parent=self._table):
                dpg.add_text(element_name.ljust(column_pads[0]))
                attach_tooltip(element_tooltip)

                dpg.add_text(parameter_label.ljust(column_pads[1]))
                attach_tooltip(parameter_tooltip)

                value_widget: Tag = dpg.add_text(value.ljust(column_pads[2]))
                attach_tooltip(value_tooltip)
                if value_theme > 0:
                    dpg.bind_item_theme(value_widget, value_theme)

                error_widget: Tag = dpg.add_text(error_value.ljust(column_pads[3]))
                if error_tooltip != "":
                    attach_tooltip(error_tooltip)

                if error_theme > 0:
                    dpg.bind_item_theme(error_widget, error_theme)

                num_rows += 1

        dpg.set_item_height(self._table, 18 + 23 * max(1, num_rows))


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
                    width_fixed=True,
                )
                attach_tooltip(tooltips.fitting.statistics)

                label: str
                tooltip: str
                for label, tooltip in [
                    (
                        "log X² (pseudo)",
                        tooltips.fitting.pseudo_chisqr,
                    ),
                    (
                        "log X²",
                        tooltips.fitting.chisqr,
                    ),
                    (
                        "log X² (reduced)",
                        tooltips.fitting.red_chisqr,
                    ),
                    (
                        "Akaike inf. crit.",
                        tooltips.fitting.aic,
                    ),
                    (
                        "Bayesian inf. crit.",
                        tooltips.fitting.bic,
                    ),
                    (
                        "Degrees of freedom",
                        tooltips.fitting.nfree,
                    ),
                    (
                        "Number of data points",
                        tooltips.fitting.ndata,
                    ),
                    (
                        "Number of func. eval.",
                        tooltips.fitting.nfev,
                    ),
                    (
                        "Method",
                        tooltips.fitting.method,
                    ),
                    (
                        "Weight",
                        tooltips.fitting.weight,
                    ),
                ]:
                    with dpg.table_row():
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

    def populate(self, fit: FitResult):
        dpg.show_item(self._header)
        cells: List[int] = []

        row: int
        for row in dpg.get_item_children(self._table, slot=1):
            cells.append(dpg.get_item_children(row, slot=1)[2])

        assert len(cells) == 10, cells

        tag: int
        value: str
        theme: int
        for tag, value, theme in [
            (
                cells[0],
                f"{log(fit.pseudo_chisqr):.3f}",
                -1,
            ),
            (
                cells[1],
                f"{log(fit.chisqr):.3f}",
                -1,
            ),
            (
                cells[2],
                f"{log(fit.red_chisqr):.3f}",
                -1,
            ),
            (
                cells[3],
                format_number(fit.aic, decimals=3),
                -1,
            ),
            (
                cells[4],
                format_number(fit.bic, decimals=3),
                -1,
            ),
            (
                cells[5],
                f"{fit.nfree}",
                -1,
            ),
            (
                cells[6],
                f"{fit.ndata}",
                -1,
            ),
            (
                cells[7],
                f"{fit.nfev}",
                (
                    themes.fitting.highlighted_statistc
                    if fit.settings.max_nfev > 0 and fit.nfev >= fit.settings.max_nfev
                    else -1
                ),
            ),
            (
                cells[8],
                cnls_method_to_label.get(fit.method, ""),
                -1,
            ),
            (
                cells[9],
                weight_to_label.get(fit.weight, ""),
                -1,
            ),
        ]:
            dpg.set_value(tag, value)
            update_tooltip(dpg.get_item_user_data(tag), value)
            dpg.show_item(dpg.get_item_parent(dpg.get_item_user_data(tag)))
            dpg.bind_item_theme(
                tag,
                theme if theme > 0 else themes.fitting.default_statistic,
            )

        dpg.set_item_height(self._table, 18 + 23 * len(cells))


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
                height=18 + 23,
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
                    "Circuit",
                    "Method",
                    "Weight",
                    "Max. num. func. eval.",
                    "Timeout",
                ]:
                    with dpg.table_row():
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
                        Signal.APPLY_FIT_SETTINGS,
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

    def populate(self, fit: FitResult, data: DataSet):
        dpg.show_item(self._header)
        rows: List[int] = []
        cells: List[Tuple[int, int]] = []

        row: int
        for row in dpg.get_item_children(self._table, slot=1):
            rows.append(row)
            cells.append(dpg.get_item_children(row, slot=1))

        assert len(rows) == len(cells) == 5, (
            rows,
            cells,
        )

        circuit: Circuit = pyimpspec.parse_cdc(fit.settings.cdc)

        tag: int
        value: str
        for row, tag, value in [
            (
                rows[0],
                cells[0][1],
                f"{circuit}\n\n{circuit.to_string(3)}",
            ),
            (
                rows[1],
                cells[1][1],
                cnls_method_to_label.get(fit.settings.method, ""),
            ),
            (
                rows[2],
                cells[2][1],
                weight_to_label.get(fit.settings.weight, ""),
            ),
            (
                rows[3],
                cells[3][1],
                f"{fit.settings.max_nfev}",
            ),
            (
                rows[4],
                cells[4][1],
                f"{fit.settings.timeout}",
            ),
        ]:
            dpg.set_value(tag, value.split("\n")[0])
            update_tooltip(dpg.get_item_user_data(tag), value)
            dpg.show_item(dpg.get_item_parent(dpg.get_item_user_data(tag)))

        dpg.set_item_height(self._table, 18 + 23 * len(rows))
        dpg.set_item_user_data(
            self._apply_settings_button,
            {"settings": fit.settings},
        )
        dpg.set_item_user_data(
            self._apply_mask_button,
            {
                "data": data,
                "mask": fit.mask,
                "fit": fit,
            },
        )


class FitResultsCombo(ResultsCombo):
    def selection_callback(self, sender: int, app_data: str, user_data: tuple):
        signals.emit(
            Signal.SELECT_FIT_RESULT,
            fit=user_data[0].get(app_data),
            data=user_data[1],
        )

    def adjust_label(self, old: str, longest: int) -> str:
        i: int = old.rfind(" (")
        cdc: str
        timestamp: str
        cdc, timestamp = (old[:i], old[i + 1 :])
        return f"{cdc.ljust(longest)} {timestamp}"


class FittingTab:
    def __init__(self, state):
        self.state = state
        self.queued_update: Optional[Callable] = None
        self.create_tab(state)

    def create_tab(self, state):
        label_pad: int = 24
        self.tab: Tag = dpg.generate_uuid()
        with dpg.tab(label="Fitting", tag=self.tab):
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
            height=150,
        ):
            self.circuit_editor: CircuitEditor = CircuitEditor(
                window=dpg.add_window(
                    label="Circuit editor",
                    show=False,
                    modal=True,
                    on_close=lambda s, a, u: self.accept_circuit(None),
                ),
                callback=self.accept_circuit,
                keybindings=state.config.keybindings,
            )

            self.settings_menu: SettingsMenu = SettingsMenu(
                state.config.default_fit_settings,
                label_pad,
                circuit_editor=self.circuit_editor,
                editor_callback=self.show_circuit_editor,
            )

            with dpg.group(horizontal=True):
                self.visibility_item: Tag = dpg.generate_uuid()
                dpg.add_text(
                    "?".rjust(label_pad),
                    tag=self.visibility_item,
                )
                attach_tooltip(tooltips.fitting.perform)

                self.perform_fit_button: Tag = dpg.generate_uuid()
                dpg.add_button(
                    label="Perform",
                    callback=lambda s, a, u: signals.emit(
                        Signal.PERFORM_FIT,
                        data=u,
                        settings=self.get_settings(),
                    ),
                    user_data=None,
                    width=-70,
                    tag=self.perform_fit_button,
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
                self.results_combo: FitResultsCombo = FitResultsCombo(
                    label="Result".rjust(label_pad),
                    width=-60,
                )

                self.delete_button: Tag = dpg.generate_uuid()
                dpg.add_button(
                    label="Delete",
                    callback=lambda s, a, u: signals.emit(
                        Signal.DELETE_FIT_RESULT,
                        **u,
                    ),
                    user_data={},
                    width=-1,
                    tag=self.delete_button,
                )
                attach_tooltip(tooltips.fitting.delete)

            with dpg.group(horizontal=True):
                dpg.add_text("Output".rjust(label_pad))
                self.output_combo: Combo = Combo(
                    items=list(label_to_fit_sim_output.keys()),
                    user_data=label_to_fit_sim_output,
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

                self.parameters_table: ParametersTable = ParametersTable(
                    fitted_values_callback=self.apply_fitted_values_as_initial_values,
                )

                dpg.add_spacer(height=8)

                self.statistics_table: StatisticsTable = StatisticsTable()

                dpg.add_spacer(height=8)

                self.settings_table: SettingsTable = SettingsTable()

    def create_plots(self):
        self.plot_window: Tag = dpg.generate_uuid()
        with dpg.child_window(
            border=False,
            width=-1,
            height=-1,
            tag=self.plot_window,
        ):
            self.circuit_preview_height: int = 250
            with dpg.child_window(
                border=False,
                width=-1,
                height=self.circuit_preview_height,
            ):
                dpg.add_text("Fitted circuit")
                self.circuit_preview: CircuitPreview = CircuitPreview()

            self.plot_tab_bar: Tag = dpg.generate_uuid()
            with dpg.tab_bar(tag=self.plot_tab_bar):
                self.create_nyquist_plot()
                self.create_bode_plot()
                self.create_impedance_plot()
                self.create_residuals_plot()

            pad_tab_labels(self.plot_tab_bar)

            self.plots: List[Plot] = [
                self.nyquist_plot,
                self.bode_plot,
                self.impedance_plot,
                self.residuals_plot,
            ]

    def create_nyquist_plot(self):
        with dpg.tab(label="Nyquist"):
            self.nyquist_plot: Nyquist = Nyquist(width=-1, height=-24)
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
                        context=Context.FITTING_TAB,
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
            self.bode_plot: Bode = Bode(width=-1, height=-24)
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
                        context=Context.FITTING_TAB,
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
            self.impedance_plot: Impedance = Impedance(width=-1, height=-24)
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
                        context=Context.FITTING_TAB,
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

    def create_residuals_plot(self):
        with dpg.tab(label="Residuals"):
            self.residuals_plot: Residuals = Residuals(width=-1, height=-24)
            self.residuals_plot.plot(
                frequencies=array([]),
                real=array([]),
                imaginary=array([]),
            )

            with dpg.group(horizontal=True):
                self.enlarge_residuals_button: Tag = dpg.generate_uuid()
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
                        context=Context.FITTING_TAB,
                    ),
                )
                attach_tooltip(tooltips.general.copy_plot_data_as_csv)

                self.adjust_residuals_limits_checkbox: Tag = dpg.generate_uuid()
                dpg.add_checkbox(
                    label="Adjust limits",
                    default_value=True,
                    tag=self.adjust_residuals_limits_checkbox,
                )
                attach_tooltip(tooltips.general.adjust_residuals_limits)

    def is_visible(self) -> bool:
        return dpg.is_item_visible(self.visibility_item)

    def get_settings(self) -> FitSettings:
        return self.settings_menu.get_settings()

    def set_settings(self, settings: FitSettings):
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
        editor_kwargs: dict = dpg.get_item_user_data(self.settings_menu.editor_button)
        editor_kwargs["admittance"] = admittance

    def resize(self, width: int, height: int):
        if not self.is_visible():
            return

        width, height = dpg.get_item_rect_size(self.plot_window)
        height -= self.circuit_preview_height + 24 * 3 - 21
        for plot in self.plots:
            plot.resize(-1, height)

    def next_plot_tab(self):
        tabs: List[Tag] = dpg.get_item_children(self.plot_tab_bar, slot=1)
        index: int = tabs.index(dpg.get_value(self.plot_tab_bar)) + 1
        dpg.set_value(self.plot_tab_bar, tabs[index % len(tabs)])

    def previous_plot_tab(self):
        tabs: List[Tag] = dpg.get_item_children(self.plot_tab_bar, slot=1)
        index: int = tabs.index(dpg.get_value(self.plot_tab_bar)) - 1
        dpg.set_value(self.plot_tab_bar, tabs[index % len(tabs)])

    def clear(self, hide: bool = True):
        self.data_sets_combo.clear()
        self.results_combo.clear()
        self.parameters_table.clear(hide=hide)
        self.statistics_table.clear(hide=hide)
        self.settings_table.clear(hide=hide)
        self.circuit_preview.clear()
        self.nyquist_plot.clear(delete=False)
        self.bode_plot.clear(delete=False)
        self.impedance_plot.clear(delete=False)
        self.residuals_plot.clear(delete=False)

    def populate_data_sets(self, labels: List[str], lookup: Dict[str, DataSet]):
        assert type(labels) is list, labels
        assert type(lookup) is dict, lookup
        self.data_sets_combo.populate(labels, lookup)

    def populate_fits(self, lookup: Dict[str, FitResult], data: Optional[DataSet]):
        assert type(lookup) is dict, lookup
        assert type(data) is DataSet or data is None, data
        self.results_combo.populate(lookup, data)
        dpg.hide_item(dpg.get_item_parent(self.validity_text))
        if data is not None and self.results_combo.labels:
            signals.emit(
                Signal.SELECT_FIT_RESULT,
                fit=self.results_combo.get(),
                data=data,
            )
        else:
            self.parameters_table.clear(hide=True)
            self.statistics_table.clear(hide=True)
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

    def get_next_result(self) -> Optional[FitResult]:
        return self.results_combo.get_next()

    def get_previous_result(self) -> Optional[FitResult]:
        return self.results_combo.get_previous()

    def select_data_set(self, data: Optional[DataSet]):
        assert type(data) is DataSet or data is None, data
        self.clear(hide=data is None)
        dpg.set_item_user_data(self.perform_fit_button, data)
        editor_kwargs: dict = dpg.get_item_user_data(self.settings_menu.editor_button)
        editor_kwargs["data"] = data
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

    def assert_fit_up_to_date(self, fit: FitResult, data: DataSet):
        # Check if the number of unmasked points is the same
        Z_exp: ndarray = data.get_impedances()
        Z_fit: ndarray = fit.get_impedances()
        assert Z_exp.shape == Z_fit.shape, "The number of data points differ!"

        # Check if the masks are the same
        mask_exp: Dict[int, bool] = data.get_mask()
        mask_fit: Dict[int, bool] = {
            k: fit.mask.get(k, mask_exp.get(k, False)) for k in fit.mask
        }
        num_masked_exp: int = list(data.get_mask().values()).count(True)
        num_masked_fit: int = list(fit.mask.values()).count(True)
        assert num_masked_exp == num_masked_fit, "The masks are different sizes!"

        i: int
        for i in mask_fit.keys():
            assert (
                i in mask_exp
            ), f"The data set does not have a point at index {i + 1}!"
            assert (
                mask_exp[i] == mask_fit[i]
            ), f"The data set's mask differs at index {i + 1}!"

        # Check if the frequencies and impedances are the same
        assert allclose(
            fit.get_frequencies(),
            data.get_frequencies(),
        ), "The frequencies differ!"

        residuals: ComplexResiduals = _calculate_residuals(Z_exp, Z_fit)
        assert allclose(fit.residuals.real, residuals.real) and allclose(
            fit.residuals.imag, residuals.imag
        ), "Either the data set's impedances differ from what they were when the fit was performed or some aspect of the circuit's implementation has changed!"

    def select_fit_result(self, fit: Optional[FitResult], data: Optional[DataSet]):
        assert type(fit) is FitResult or fit is None, fit
        assert type(data) is DataSet or data is None, data
        dpg.set_item_user_data(
            self.delete_button,
            {
                "fit": fit,
                "data": data,
            },
        )
        dpg.set_item_user_data(
            self.copy_output_button,
            {
                "fit_or_sim": fit,
                "data": data,
            },
        )

        if not self.is_visible():
            self.queued_update = lambda: self.select_fit_result(fit, data)
            return

        self.queued_update = None
        self.select_data_set(data)
        if fit is None or data is None:
            if dpg.get_value(self.adjust_nyquist_limits_checkbox):
                self.nyquist_plot.queue_limits_adjustment()

            if dpg.get_value(self.adjust_bode_limits_checkbox):
                self.bode_plot.queue_limits_adjustment()

            if dpg.get_value(self.adjust_impedance_limits_checkbox):
                self.impedance_plot.queue_limits_adjustment()

            if dpg.get_value(self.adjust_residuals_limits_checkbox):
                self.residuals_plot.queue_limits_adjustment()

            return

        self.results_combo.set(fit.get_label())

        try:
            self.assert_fit_up_to_date(fit, data)
            dpg.hide_item(dpg.get_item_parent(self.validity_text))
        except AssertionError as err:
            dpg.set_value(
                self.validity_text,
                f"Fit result is not valid for the current state of the data set!\n\n{str(err)}",
            )
            dpg.show_item(dpg.get_item_parent(self.validity_text))

        self.parameters_table.populate(fit)
        self.statistics_table.populate(fit)
        self.settings_table.populate(fit, data)
        self.circuit_preview.update(pyimpspec.parse_cdc(fit.settings.cdc))

        freq_markers: ndarray = fit.get_frequencies()
        freq_line: ndarray = fit.get_frequencies(
            num_per_decade=self.state.config.num_per_decade_in_simulated_lines
        )
        Z_markers: ndarray = fit.get_impedances()
        Z_line: ndarray = fit.get_impedances(
            num_per_decade=self.state.config.num_per_decade_in_simulated_lines
        )
        self.nyquist_plot.update(
            index=1,
            impedances=Z_markers,
        )
        self.bode_plot.update(
            index=1,
            frequencies=freq_markers,
            impedances=Z_markers,
        )
        self.impedance_plot.update(
            index=1,
            frequencies=freq_markers,
            impedances=Z_markers,
        )

        self.nyquist_plot.update(
            index=2,
            impedances=Z_line,
        )
        self.bode_plot.update(
            index=2,
            frequencies=freq_line,
            impedances=Z_line,
        )
        self.impedance_plot.update(
            index=2,
            frequencies=freq_line,
            impedances=Z_line,
        )

        freq: ndarray
        real: ndarray
        imag: ndarray
        freq, real, imag = fit.get_residuals_data()
        self.residuals_plot.update(
            index=0,
            frequencies=freq,
            real=real,
            imaginary=imag,
        )

        if dpg.get_value(self.adjust_nyquist_limits_checkbox):
            self.nyquist_plot.queue_limits_adjustment()

        if dpg.get_value(self.adjust_bode_limits_checkbox):
            self.bode_plot.queue_limits_adjustment()

        if dpg.get_value(self.adjust_impedance_limits_checkbox):
            self.impedance_plot.queue_limits_adjustment()

        if dpg.get_value(self.adjust_residuals_limits_checkbox):
            self.residuals_plot.queue_limits_adjustment()

    def show_circuit_editor(self):
        if self.settings_menu.circuit_editor is None:
            return

        x: int
        y: int
        w: int
        h: int
        x, y, w, h = calculate_window_position_dimensions()
        dpg.configure_item(
            self.settings_menu.circuit_editor.window,
            pos=(x, y),
            width=w,
            height=h,
        )

        circuit: Optional[Circuit] = self.settings_menu.parse_cdc(
            self.settings_menu.get_settings().cdc,
            sender=self.settings_menu.cdc_input,
        )
        editor_kwargs: dict = dpg.get_item_user_data(self.settings_menu.editor_button)
        if editor_kwargs["data"] is None:
            editor_kwargs = editor_kwargs.copy()
            f: Frequencies = _interpolate(
                [1e6, 1e-3],
                num_per_decade=10,
            )
            editor_kwargs["data"] = DataSet(
                frequencies=f,
                impedances=array([complex(inf, inf)] * len(f), dtype=ComplexImpedance),
            )

        signals.emit(
            Signal.BLOCK_KEYBINDINGS,
            window=self.settings_menu.circuit_editor.window,
            window_object=self.settings_menu.circuit_editor,
        )
        self.settings_menu.circuit_editor.show(
            circuit=circuit,
            num_per_decade=self.state.config.num_per_decade_in_simulated_lines,
            **editor_kwargs,
        )

    def accept_circuit(self, circuit: Optional[Circuit]):
        signals.emit(Signal.UNBLOCK_KEYBINDINGS)
        self.circuit_editor.hide()
        if circuit is not None:
            self.settings_menu.parse_cdc(circuit.serialize())

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

    def accept_parameters(self, circuit: Circuit):
        self.settings_menu.parse_cdc(circuit.serialize())

    def get_active_output(self) -> Optional[FitSimOutput]:
        return self.output_combo.get_value()

    def has_active_input(self) -> bool:
        return self.settings_menu.has_active_input()

    def apply_fitted_values_as_initial_values(self):
        user_data = dpg.get_item_user_data(self.delete_button)
        if (user_data is None) or (isinstance(user_data, dict) is False):
            return

        fit: Optional[FitResult] = user_data.get("fit", None)
        if fit is None:
            return

        circuit: Optional[Circuit]
        err: str
        circuit, err = process_cdc(fit.settings.cdc)
        if circuit is None:
            signals.emit(Signal.SHOW_ERROR_MESSAGE, err)
            return

        identifiers: Dict[Element, int] = circuit.generate_element_identifiers(
            running=True
        )
        fitted_element_lookup: Dict[int, Element] = {
            v: k
            for k, v in fit.circuit.generate_element_identifiers(running=True).items()
        }

        initial_element: Element
        ident: int
        for initial_element, ident in identifiers.items():
            initial_element.set_values(**fitted_element_lookup[ident].get_values())

        settings: FitSettings = self.get_settings()
        signals.emit(
            Signal.APPLY_FIT_SETTINGS,
            settings=FitSettings(
                cdc=circuit.serialize(),
                method=settings.method,
                weight=settings.weight,
                max_nfev=settings.max_nfev,
                timeout=settings.timeout,
            ),
        )

    def show_admittance_plots(self) -> bool:
        return dpg.get_value(self.nyquist_admittance_checkbox)
