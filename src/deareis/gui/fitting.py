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
    Tuple,
    Type,
)
from numpy import (
    allclose,
    array,
    log10 as log,
    ndarray,
)
from pyimpspec import (
    Circuit,
    Element,
    FittedParameter,
)
import pyimpspec
from pyimpspec.analysis.fitting import _calculate_residuals
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
    Nyquist,
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
    format_number,
    render_math,
)
import deareis.themes as themes
from deareis.gui.circuit_editor import (
    CircuitPreview,
    CircuitEditor,
)


MATH_WEIGHT_WIDTH: int = 300
MATH_WEIGHT_HEIGHT: int = 40
MATH_WEIGHT_MODULUS: int = render_math(
    r"$w_i = [|Z_{\rm re}(f_i)|, |Z_{\rm im}(f_i)|]^{-1}$",
    width=MATH_WEIGHT_WIDTH,
    height=MATH_WEIGHT_HEIGHT,
)
MATH_WEIGHT_PROPORTIONAL: int = render_math(
    r"$w_i = [Z_{\rm re}(f_i)^2, Z_{\rm im}(f_i)^2]^{-1}$",
    width=MATH_WEIGHT_WIDTH,
    height=MATH_WEIGHT_HEIGHT,
)
MATH_WEIGHT_UNITY: int = render_math(
    r"$w_i = [1]$",
    width=MATH_WEIGHT_WIDTH,
    height=MATH_WEIGHT_HEIGHT,
)
MATH_WEIGHT_BOUKAMP: int = render_math(
    r"$w_i = [(Z_{{\rm re},i})^2 + (Z_{{\rm im},i})^2]^{-1}$",
    width=MATH_WEIGHT_WIDTH,
    height=MATH_WEIGHT_HEIGHT,
)
MATH_Z_FIT: int = render_math(
    r"$Z_{\rm re/im}(f_i)$",
    width=54,
    height=20,
    fontsize=10,
)
MATH_Z_EXP: int = render_math(
    r"$Z_{{\rm re/im},i}$",
    width=44,
    height=20,
    fontsize=10,
)


class SettingsMenu:
    def __init__(
        self,
        default_settings: FitSettings,
        label_pad: int,
        circuit_editor: Optional[CircuitEditor] = None,
    ):
        self.circuit_editor: Optional[CircuitEditor] = circuit_editor
        with dpg.group(horizontal=True):
            dpg.add_text("Circuit".rjust(label_pad))
            attach_tooltip(tooltips.fitting.cdc)
            self.cdc_input: int = dpg.generate_uuid()
            dpg.add_input_text(
                width=-50 if circuit_editor is not None else -1,
                tag=self.cdc_input,
                on_enter=True,
                callback=lambda s, a, u: self.parse_cdc(a, s),
            )
            self.cdc_tooltip: int = dpg.generate_uuid()
            attach_tooltip("", tag=self.cdc_tooltip, parent=self.cdc_input)
            dpg.hide_item(dpg.get_item_parent(self.cdc_tooltip))
            if circuit_editor is not None:
                self.editor_button: int = dpg.generate_uuid()
                dpg.add_button(
                    label="Edit",
                    callback=self.show_circuit_editor,
                    width=-1,
                    tag=self.editor_button,
                )
                attach_tooltip(tooltips.general.open_circuit_editor)
        with dpg.group(horizontal=True):
            dpg.add_text("Method".rjust(label_pad))
            attach_tooltip(tooltips.fitting.method)
            self.method_combo: int = dpg.generate_uuid()
            dpg.add_combo(
                items=list(label_to_cnls_method.keys()),
                default_value="Auto",
                width=-1,
                tag=self.method_combo,
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
            self.weight_combo: int = dpg.generate_uuid()
            dpg.add_combo(
                items=list(label_to_weight.keys()),
                default_value="Auto",
                width=-1,
                tag=self.weight_combo,
            )
        with dpg.group(horizontal=True):
            dpg.add_text("Max. num. of func. eval.".rjust(label_pad))
            attach_tooltip(tooltips.fitting.nfev)
            self.max_nfev_input: int = dpg.generate_uuid()
            dpg.add_input_int(
                default_value=1000,
                min_value=0,
                min_clamped=True,
                step=0,
                on_enter=True,
                tag=self.max_nfev_input,
                width=-1,
            )
        self.set_settings(default_settings)

    def get_settings(self) -> FitSettings:
        cdc: str = dpg.get_value(self.cdc_input) or ""
        circuit: Optional[Circuit] = dpg.get_item_user_data(self.cdc_input)
        if circuit is None or cdc != circuit.to_string():
            circuit = self.parse_cdc(cdc, self.cdc_input)
        return FitSettings(
            cdc=circuit.to_string(12) if circuit is not None else "",
            method=label_to_cnls_method.get(
                dpg.get_value(self.method_combo), CNLSMethod.AUTO
            ),
            weight=label_to_weight.get(dpg.get_value(self.weight_combo), Weight.AUTO),
            max_nfev=dpg.get_value(self.max_nfev_input),
        )

    def set_settings(self, settings: FitSettings):
        assert type(settings) is FitSettings, settings
        self.parse_cdc(settings.cdc)
        dpg.set_value(self.method_combo, cnls_method_to_label.get(settings.method))
        dpg.set_value(self.weight_combo, weight_to_label.get(settings.weight))
        dpg.set_value(self.max_nfev_input, settings.max_nfev)

    def parse_cdc(self, cdc: str, sender: int = -1) -> Optional[Circuit]:
        assert type(cdc) is str, cdc
        assert type(sender) is int, sender
        try:
            circuit: Circuit = pyimpspec.parse_cdc(cdc)
        except (pyimpspec.ParsingError, pyimpspec.UnexpectedCharacter) as err:
            dpg.bind_item_theme(self.cdc_input, themes.cdc.invalid)
            update_tooltip(self.cdc_tooltip, str(err))
            dpg.show_item(dpg.get_item_parent(self.cdc_tooltip))
            dpg.set_item_user_data(self.cdc_input, None)
            return None
        dpg.bind_item_theme(self.cdc_input, themes.cdc.valid)
        dpg.hide_item(dpg.get_item_parent(self.cdc_tooltip))
        dpg.set_item_user_data(self.cdc_input, circuit)
        if sender != self.cdc_input:
            dpg.set_value(self.cdc_input, circuit.to_string())
        return circuit

    def show_circuit_editor(self):
        if self.circuit_editor is None:
            return
        x: int
        y: int
        w: int
        h: int
        x, y, w, h = calculate_window_position_dimensions()
        dpg.configure_item(
            self.circuit_editor.window,
            pos=(
                x,
                y,
            ),
            width=w,
            height=h,
        )
        circuit: Optional[Circuit] = None
        try:
            circuit = pyimpspec.parse_cdc(self.get_settings().cdc)
        except pyimpspec.ParsingError:
            pass
        signals.emit(
            Signal.BLOCK_KEYBINDINGS,
            window=self.circuit_editor.window,
            window_object=self.circuit_editor,
        )
        self.circuit_editor.show(circuit)

    def has_active_input(self) -> bool:
        return dpg.is_item_active(self.cdc_input) or dpg.is_item_active(
            self.max_nfev_input
        )


class ParametersTable:
    def __init__(self):
        self._header: int = dpg.generate_uuid()
        with dpg.collapsing_header(
            label=" Parameters",
            leaf=True,
            tag=self._header,
        ):
            self._table: int = dpg.generate_uuid()
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

    def clear(self, hide: bool):
        if hide:
            dpg.hide_item(self._header)
        dpg.delete_item(self._table, children_only=True, slot=1)

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
        element_labels: List[str] = []
        element_tooltips: List[str] = []
        parameter_labels: List[str] = []
        values: List[str] = []
        value_tooltips: List[str] = []
        error_values: List[str] = []
        error_tooltips: List[str] = []
        element_label: str
        element_tooltip: str
        parameter_label: str
        value: str
        value_tooltip: str
        error_value: str
        error_tooltip: str
        parameters: Dict[str, FittedParameter]
        for element in fit.circuit.get_elements():
            Class: Type[Element] = type(element)
            element_label = element.get_label()
            element_tooltip = Class.get_extended_description()
            parameters = fit.parameters[element_label]
            parameter: FittedParameter
            for parameter_label in sorted(parameters):
                parameter = parameters[parameter_label]
                element_labels.append(element_label)
                element_tooltips.append(element_tooltip)
                parameter_labels.append(
                    parameter_label + (" (fixed)" if parameter.fixed else "")
                )
                values.append(
                    f"{format_number(parameter.value, width=9, significants=3)}"
                )
                value_tooltips.append(
                    f"{format_number(parameter.value, decimals=6).strip()}"
                )
                if parameter.stderr is not None:
                    error: float = parameter.get_relative_error() * 100
                    if error > 100.0:
                        error_value = ">100"
                    elif error < 0.01:
                        error_value = "<0.01"
                    else:
                        error_value = (
                            f"{format_number(error, exponent=False, significants=3)}"
                        )
                    error_tooltip = (
                        f"±{format_number(parameter.stderr, decimals=6).strip()}"
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
        num_rows: int = 0
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
            with dpg.table_row(parent=self._table):
                dpg.add_text(element_label.ljust(column_pads[0]))
                if element_tooltip != "":
                    attach_tooltip(element_tooltip)
                dpg.add_text(parameter_label.ljust(column_pads[1]))
                dpg.add_text(value.ljust(column_pads[2]))
                attach_tooltip(value_tooltip)
                dpg.add_text(error_value.ljust(column_pads[3]))
                if error_tooltip != "":
                    attach_tooltip(error_tooltip)
                num_rows += 1
        dpg.set_item_height(self._table, 18 + 23 * max(1, num_rows))


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
                    width_fixed=True,
                )
                label: str
                tooltip: str
                for (label, tooltip) in [
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

    def populate(self, fit: FitResult):
        dpg.show_item(self._header)
        cells: List[int] = []
        row: int
        for row in dpg.get_item_children(self._table, slot=1):
            cells.append(dpg.get_item_children(row, slot=1)[2])
        assert len(cells) == 9, cells
        tag: int
        value: str
        for (tag, value) in [
            (
                cells[0],
                f"{log(fit.chisqr):.3f}",
            ),
            (
                cells[1],
                f"{log(fit.red_chisqr):.3f}",
            ),
            (
                cells[2],
                f"{fit.aic:.3E}",
            ),
            (
                cells[3],
                f"{fit.bic:.3E}",
            ),
            (
                cells[4],
                f"{fit.nfree}",
            ),
            (
                cells[5],
                f"{fit.ndata}",
            ),
            (
                cells[6],
                f"{fit.nfev}",
            ),
            (
                cells[7],
                cnls_method_to_label.get(fit.method, ""),
            ),
            (
                cells[8],
                weight_to_label.get(fit.weight, ""),
            ),
        ]:
            dpg.set_value(tag, value)
            update_tooltip(dpg.get_item_user_data(tag), value)
            dpg.show_item(dpg.get_item_parent(dpg.get_item_user_data(tag)))
        dpg.set_item_height(self._table, 18 + 23 * 9)


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
                ]:
                    with dpg.table_row():
                        dpg.add_text(label.rjust(label_pad))
                        tooltip_tag: int = dpg.generate_uuid()
                        dpg.add_text("", user_data=tooltip_tag)
                        attach_tooltip("", tag=tooltip_tag)
            with dpg.group(horizontal=True):
                self._apply_settings_button: int = dpg.generate_uuid()
                dpg.add_button(
                    label="Apply settings",
                    callback=lambda s, a, u: signals.emit(
                        Signal.APPLY_FIT_SETTINGS,
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

    def populate(self, fit: FitResult, data: DataSet):
        dpg.show_item(self._header)
        rows: List[int] = []
        cells: List[Tuple[int, int]] = []
        row: int
        for row in dpg.get_item_children(self._table, slot=1):
            rows.append(row)
            cells.append(dpg.get_item_children(row, slot=1))
        assert len(rows) == len(cells) == 4, (
            rows,
            cells,
        )
        circuit: Circuit = pyimpspec.parse_cdc(fit.settings.cdc)
        tag: int
        value: str
        for (row, tag, value) in [
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
        ]:
            dpg.set_value(tag, value.split("\n")[0])
            update_tooltip(dpg.get_item_user_data(tag), value)
            dpg.show_item(dpg.get_item_parent(dpg.get_item_user_data(tag)))
        dpg.set_item_height(self._table, 18 + 23 * 4)
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
                Signal.SELECT_FIT_RESULT,
                fit=u[0].get(a),
                data=u[1],
            ),
            user_data=(
                {},
                None,
            ),
            width=width,
            tag=self.tag,
        )

    def populate(self, lookup: Dict[str, FitResult], data: Optional[DataSet]):
        self.labels.clear()
        labels: List[str] = list(lookup.keys())
        longest_cdc: int = max(list(map(lambda _: len(_[: _.find(" ")]), labels)) + [1])
        old_key: str
        for old_key in labels:
            fit: FitResult = lookup[old_key]
            del lookup[old_key]
            cdc, timestamp = (
                old_key[: old_key.find(" ")],
                old_key[old_key.find(" ") + 1 :],
            )
            new_key: str = f"{cdc.ljust(longest_cdc)} {timestamp}"
            self.labels[old_key] = new_key
            lookup[new_key] = fit
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

    def get(self) -> Optional[FitResult]:
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

    def get_next_result(self) -> Optional[FitResult]:
        lookup: Dict[str, FitResult] = dpg.get_item_user_data(self.tag)[0]
        if not lookup:
            return None
        labels: List[str] = list(lookup.keys())
        index: int = labels.index(dpg.get_value(self.tag)) + 1
        return lookup[labels[index % len(labels)]]

    def get_previous_result(self) -> Optional[FitResult]:
        lookup: Dict[str, FitResult] = dpg.get_item_user_data(self.tag)[0]
        if not lookup:
            return None
        labels: List[str] = list(lookup.keys())
        index: int = labels.index(dpg.get_value(self.tag)) - 1
        return lookup[labels[index % len(labels)]]


class FittingTab:
    def __init__(self, state):
        self.state = state
        self.queued_update: Optional[Callable] = None
        label_pad: int = 24
        self.tab: int = dpg.generate_uuid()
        with dpg.tab(label="Fitting", tag=self.tab):
            with dpg.group(horizontal=True):
                self.sidebar_width: int = 350
                self.sidebar_window: int = dpg.generate_uuid()
                with dpg.child_window(
                    border=False,
                    width=self.sidebar_width,
                    tag=self.sidebar_window,
                ):
                    with dpg.child_window(
                        border=True,
                        width=-1,
                        height=128,
                    ):
                        self.circuit_editor: CircuitEditor = CircuitEditor(
                            window=dpg.add_window(
                                label="Circuit editor",
                                show=False,
                                modal=True,
                                on_close=lambda s, a, u: self.accept_circuit(None),
                            ),
                            callback=self.accept_circuit,
                        )
                        self.settings_menu: SettingsMenu = SettingsMenu(
                            state.config.default_fit_settings,
                            label_pad,
                            circuit_editor=self.circuit_editor,
                        )
                        with dpg.group(horizontal=True):
                            self.visibility_item: int = dpg.generate_uuid()
                            dpg.add_text(
                                "?".rjust(label_pad),
                                tag=self.visibility_item,
                            )
                            attach_tooltip(tooltips.fitting.perform)
                            self.perform_fit_button: int = dpg.generate_uuid()
                            dpg.add_button(
                                label="Perform fit",
                                callback=lambda s, a, u: signals.emit(
                                    Signal.PERFORM_FIT,
                                    data=u,
                                    settings=self.get_settings(),
                                ),
                                user_data=None,
                                width=-1,
                                tag=self.perform_fit_button,
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
                            # TODO: Split into combo class?
                            self.output_combo: int = dpg.generate_uuid()
                            dpg.add_combo(
                                items=list(label_to_fit_sim_output.keys()),
                                default_value=list(label_to_fit_sim_output.keys())[0],
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
                    #
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
                            self.parameters_table: ParametersTable = ParametersTable()
                            dpg.add_spacer(height=8)
                            self.statistics_table: StatisticsTable = StatisticsTable()
                            dpg.add_spacer(height=8)
                            self.settings_table: SettingsTable = SettingsTable()
                self.plot_window: int = dpg.generate_uuid()
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
                        self.circuit_preview: CircuitPreview = CircuitPreview()
                    self.minimum_plot_side: int = 400
                    with dpg.group(horizontal=True):
                        with dpg.group():
                            self.nyquist_plot: Nyquist = Nyquist(
                                width=self.minimum_plot_side,
                                height=self.minimum_plot_side,
                            )
                            self.nyquist_plot.plot(
                                real=array([]),
                                imaginary=array([]),
                                label="Data",
                                theme=themes.nyquist.data,
                            )
                            self.nyquist_plot.plot(
                                real=array([]),
                                imaginary=array([]),
                                label="Fit",
                                fit=True,
                                theme=themes.nyquist.simulation,
                            )
                            self.nyquist_plot.plot(
                                real=array([]),
                                imaginary=array([]),
                                label="Fit",
                                fit=True,
                                line=True,
                                theme=themes.nyquist.simulation,
                                show_label=False,
                            )
                            with dpg.group(horizontal=True):
                                self.enlarge_nyquist_button: int = dpg.generate_uuid()
                                self.adjust_nyquist_limits_checkbox: int = (
                                    dpg.generate_uuid()
                                )
                                dpg.add_button(
                                    label="Enlarge Nyquist",
                                    callback=self.show_enlarged_nyquist,
                                    tag=self.enlarge_nyquist_button,
                                )
                                dpg.add_checkbox(
                                    default_value=True,
                                    tag=self.adjust_nyquist_limits_checkbox,
                                )
                                attach_tooltip(tooltips.general.adjust_nyquist_limits)
                                dpg.add_button(
                                    label="Copy as CSV",
                                    callback=lambda s, a, u: signals.emit(
                                        Signal.COPY_PLOT_DATA,
                                        plot=self.nyquist_plot,
                                        context=Context.FITTING_TAB,
                                    ),
                                )
                                attach_tooltip(tooltips.general.copy_plot_data_as_csv)
                        self.horizontal_bode_group: int = dpg.generate_uuid()
                        with dpg.group(tag=self.horizontal_bode_group):
                            self.bode_plot_horizontal: Bode = Bode(
                                width=self.minimum_plot_side,
                                height=self.minimum_plot_side,
                            )
                            self.bode_plot_horizontal.plot(
                                frequency=array([]),
                                magnitude=array([]),
                                phase=array([]),
                                labels=(
                                    "|Z| (d)",
                                    "phi (d)",
                                ),
                                themes=(
                                    themes.bode.magnitude_data,
                                    themes.bode.phase_data,
                                ),
                            )
                            self.bode_plot_horizontal.plot(
                                frequency=array([]),
                                magnitude=array([]),
                                phase=array([]),
                                labels=(
                                    "|Z| (f)",
                                    "phi (f)",
                                ),
                                fit=True,
                                themes=(
                                    themes.bode.magnitude_simulation,
                                    themes.bode.phase_simulation,
                                ),
                            )
                            self.bode_plot_horizontal.plot(
                                frequency=array([]),
                                magnitude=array([]),
                                phase=array([]),
                                labels=(
                                    "|Z| (f)",
                                    "phi (f)",
                                ),
                                fit=True,
                                line=True,
                                themes=(
                                    themes.bode.magnitude_simulation,
                                    themes.bode.phase_simulation,
                                ),
                                show_labels=False,
                            )
                            with dpg.group(horizontal=True):
                                self.enlarge_bode_horizontal_button: int = (
                                    dpg.generate_uuid()
                                )
                                self.adjust_bode_limits_horizontal_checkbox: int = (
                                    dpg.generate_uuid()
                                )
                                dpg.add_button(
                                    label="Enlarge Bode",
                                    callback=self.show_enlarged_bode,
                                    tag=self.enlarge_bode_horizontal_button,
                                )
                                dpg.add_checkbox(
                                    default_value=True,
                                    tag=self.adjust_bode_limits_horizontal_checkbox,
                                )
                                attach_tooltip(tooltips.general.adjust_bode_limits)
                                dpg.add_button(
                                    label="Copy as CSV",
                                    callback=lambda s, a, u: signals.emit(
                                        Signal.COPY_PLOT_DATA,
                                        plot=self.bode_plot_horizontal,
                                        context=Context.FITTING_TAB,
                                    ),
                                )
                                attach_tooltip(tooltips.general.copy_plot_data_as_csv)
                    self.vertical_bode_group: int = dpg.generate_uuid()
                    with dpg.group(tag=self.vertical_bode_group):
                        self.bode_plot_vertical: Bode = Bode(
                            width=-1,
                            height=self.minimum_plot_side,
                        )
                        self.bode_plot_vertical.plot(
                            frequency=array([]),
                            magnitude=array([]),
                            phase=array([]),
                            labels=(
                                "|Z| (d)",
                                "phi (d)",
                            ),
                            themes=(
                                themes.bode.magnitude_data,
                                themes.bode.phase_data,
                            ),
                        )
                        self.bode_plot_vertical.plot(
                            frequency=array([]),
                            magnitude=array([]),
                            phase=array([]),
                            labels=(
                                "|Z| (f)",
                                "phi (f)",
                            ),
                            fit=True,
                            themes=(
                                themes.bode.magnitude_simulation,
                                themes.bode.phase_simulation,
                            ),
                        )
                        self.bode_plot_vertical.plot(
                            frequency=array([]),
                            magnitude=array([]),
                            phase=array([]),
                            labels=(
                                "|Z| (f)",
                                "phi (f)",
                            ),
                            fit=True,
                            line=True,
                            themes=(
                                themes.bode.magnitude_simulation,
                                themes.bode.phase_simulation,
                            ),
                            show_labels=False,
                        )
                        with dpg.group(horizontal=True):
                            self.enlarge_bode_vertical_button: int = dpg.generate_uuid()
                            self.adjust_bode_limits_vertical_checkbox: int = (
                                dpg.generate_uuid()
                            )
                            dpg.add_button(
                                label="Enlarge Bode",
                                callback=lambda s, a, u: signals.emit(
                                    Signal.SHOW_ENLARGED_PLOT,
                                    plot=self.bode_plot_vertical,
                                    adjust_limits=dpg.get_value(
                                        self.adjust_bode_limits_horizontal_checkbox
                                    ),
                                ),
                                tag=self.enlarge_bode_vertical_button,
                            )
                            dpg.add_checkbox(
                                default_value=True,
                                source=self.adjust_bode_limits_horizontal_checkbox,
                                tag=self.adjust_bode_limits_vertical_checkbox,
                            )
                            attach_tooltip(tooltips.general.adjust_bode_limits)
                            dpg.add_button(
                                label="Copy as CSV",
                                callback=lambda s, a, u: signals.emit(
                                    Signal.COPY_PLOT_DATA,
                                    plot=self.bode_plot_vertical,
                                    context=Context.FITTING_TAB,
                                ),
                            )
                            attach_tooltip(tooltips.general.copy_plot_data_as_csv)
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
                                context=Context.FITTING_TAB,
                            ),
                        )
                        attach_tooltip(tooltips.general.copy_plot_data_as_csv)

    def is_visible(self) -> bool:
        return dpg.is_item_visible(self.visibility_item)

    def get_settings(self) -> FitSettings:
        return self.settings_menu.get_settings()

    def set_settings(self, settings: FitSettings):
        self.settings_menu.set_settings(settings)

    def resize(self, width: int, height: int):
        assert type(width) is int and width > 0
        assert type(height) is int and height > 0
        if not self.is_visible():
            return
        if width < (self.sidebar_width + self.minimum_plot_side * 2):
            if dpg.is_item_shown(self.horizontal_bode_group):
                dpg.hide_item(self.horizontal_bode_group)
                dpg.show_item(self.vertical_bode_group)
                self.nyquist_plot.resize(-1, self.minimum_plot_side)
        else:
            if dpg.is_item_shown(self.vertical_bode_group):
                dpg.show_item(self.horizontal_bode_group)
                dpg.hide_item(self.vertical_bode_group)
            dpg.split_frame()
            width, height = dpg.get_item_rect_size(self.plot_window)
            width = round((width - 24) / 2)
            height = height - 300 - 24 * 2 - 2
            self.nyquist_plot.resize(width, height)
            self.bode_plot_horizontal.resize(width, height)

    def clear(self, hide: bool = True):
        self.data_sets_combo.clear()
        self.results_combo.clear()
        self.parameters_table.clear(hide=hide)
        self.statistics_table.clear(hide=hide)
        self.settings_table.clear(hide=hide)
        self.circuit_preview.clear()
        self.nyquist_plot.clear(delete=False)
        self.bode_plot_horizontal.clear(delete=False)
        self.bode_plot_vertical.clear(delete=False)
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

    def get_next_result(self) -> Optional[FitResult]:
        return self.results_combo.get_next_result()

    def get_previous_result(self) -> Optional[FitResult]:
        return self.results_combo.get_previous_result()

    def select_data_set(self, data: Optional[DataSet]):
        assert type(data) is DataSet or data is None, data
        self.clear(hide=data is None)
        dpg.set_item_user_data(self.perform_fit_button, data)
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
        self.bode_plot_horizontal.update(
            index=0,
            frequency=freq,
            magnitude=mag,
            phase=phase,
        )
        self.bode_plot_vertical.update(
            index=0,
            frequency=freq,
            magnitude=mag,
            phase=phase,
        )

    def assert_fit_up_to_date(self, fit: FitResult, data: DataSet):
        # Check if the number of unmasked points is the same
        Z_exp: ndarray = data.get_impedance()
        Z_fit: ndarray = fit.get_impedance()
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
            fit.get_frequency(), data.get_frequency()
        ), "The frequencies differ!"
        real_residual: ndarray
        imaginary_residual: ndarray
        real_residual, imaginary_residual = _calculate_residuals(Z_exp, Z_fit)
        assert allclose(fit.real_residual, real_residual) and allclose(
            fit.imaginary_residual, imaginary_residual
        ), "The data set's impedances differ from what they were when the fit was performed!"

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
            if dpg.get_value(self.adjust_bode_limits_horizontal_checkbox):
                self.bode_plot_horizontal.queue_limits_adjustment()
                self.bode_plot_vertical.queue_limits_adjustment()
            if dpg.get_value(self.adjust_residuals_limits_checkbox):
                self.residuals_plot.queue_limits_adjustment()
            return
        self.results_combo.set(fit.get_label())
        message: str
        try:
            self.assert_fit_up_to_date(fit, data)
            dpg.hide_item(dpg.get_item_parent(self.validity_text))
        except AssertionError as message:
            dpg.set_value(
                self.validity_text,
                f"Fit result is not valid for the current state of the data set!\n\n{message}",
            )
            dpg.show_item(dpg.get_item_parent(self.validity_text))
        self.parameters_table.populate(fit)
        self.statistics_table.populate(fit)
        self.settings_table.populate(fit, data)
        self.circuit_preview.update(pyimpspec.parse_cdc(fit.settings.cdc))
        real: ndarray
        imag: ndarray
        real, imag = fit.get_nyquist_data()
        self.nyquist_plot.update(
            index=1,
            real=real,
            imaginary=imag,
        )
        real, imag = fit.get_nyquist_data(
            num_per_decade=self.state.config.num_per_decade_in_simulated_lines
        )
        self.nyquist_plot.update(
            index=2,
            real=real,
            imaginary=imag,
        )
        freq: ndarray
        mag: ndarray
        phase: ndarray
        freq, mag, phase = fit.get_bode_data()
        self.bode_plot_horizontal.update(
            index=1,
            frequency=freq,
            magnitude=mag,
            phase=phase,
        )
        freq, mag, phase = fit.get_bode_data(
            num_per_decade=self.state.config.num_per_decade_in_simulated_lines
        )
        self.bode_plot_horizontal.update(
            index=2,
            frequency=freq,
            magnitude=mag,
            phase=phase,
        )
        freq, mag, phase = fit.get_bode_data()
        self.bode_plot_vertical.update(
            index=1,
            frequency=freq,
            magnitude=mag,
            phase=phase,
        )
        freq, mag, phase = fit.get_bode_data(
            num_per_decade=self.state.config.num_per_decade_in_simulated_lines
        )
        self.bode_plot_vertical.update(
            index=2,
            frequency=freq,
            magnitude=mag,
            phase=phase,
        )
        freq, real, imag = fit.get_residual_data()
        self.residuals_plot.update(
            index=0,
            frequency=freq,
            real=real,
            imaginary=imag,
        )
        if dpg.get_value(self.adjust_nyquist_limits_checkbox):
            self.nyquist_plot.queue_limits_adjustment()
        if dpg.get_value(self.adjust_bode_limits_horizontal_checkbox):
            self.bode_plot_horizontal.queue_limits_adjustment()
            self.bode_plot_vertical.queue_limits_adjustment()
        if dpg.get_value(self.adjust_residuals_limits_checkbox):
            self.residuals_plot.queue_limits_adjustment()

    def show_circuit_editor(self):
        self.settings_menu.show_circuit_editor()

    def accept_circuit(self, circuit: Optional[Circuit]):
        signals.emit(Signal.UNBLOCK_KEYBINDINGS)
        self.circuit_editor.hide()
        if circuit is None:
            return
        self.settings_menu.parse_cdc(circuit.to_string(12))

    def show_enlarged_nyquist(self):
        signals.emit(
            Signal.SHOW_ENLARGED_PLOT,
            plot=self.nyquist_plot,
            adjust_limits=dpg.get_value(self.adjust_nyquist_limits_checkbox),
        )

    def show_enlarged_bode(self):
        signals.emit(
            Signal.SHOW_ENLARGED_PLOT,
            plot=self.bode_plot_horizontal,
            adjust_limits=dpg.get_value(self.adjust_bode_limits_horizontal_checkbox),
        )

    def show_enlarged_residuals(self):
        signals.emit(
            Signal.SHOW_ENLARGED_PLOT,
            plot=self.residuals_plot,
            adjust_limits=dpg.get_value(self.adjust_residuals_limits_checkbox),
        )

    def get_active_output(self) -> Optional[FitSimOutput]:
        return label_to_fit_sim_output.get(dpg.get_value(self.output_combo))

    def has_active_input(self) -> bool:
        return self.settings_menu.has_active_input()
