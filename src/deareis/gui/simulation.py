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
from numpy import array, ndarray
import pyimpspec
from pyimpspec import (
    Circuit,
    Element,
    FittedParameter,
)
import dearpygui.dearpygui as dpg
from deareis.signals import Signal
import deareis.signals as signals
import deareis.themes as themes
from deareis.utility import (
    align_numbers,
    calculate_window_position_dimensions,
    format_number,
)
from deareis.tooltips import attach_tooltip, update_tooltip
import deareis.tooltips as tooltips
from deareis.gui.plots import Bode, Nyquist
from deareis.enums import (
    Context,
    FitSimOutput,
    label_to_fit_sim_output,
)
from deareis.gui.circuit_editor import CircuitPreview, CircuitEditor
from deareis.data import (
    DataSet,
    SimulationResult,
    SimulationSettings,
)


class SettingsMenu:
    def __init__(
        self,
        default_settings: SimulationSettings,
        label_pad: int,
        circuit_editor: Optional[CircuitEditor] = None,
    ):
        self.circuit_editor: Optional[CircuitEditor] = circuit_editor
        with dpg.group(horizontal=True):
            dpg.add_text("Circuit".rjust(label_pad))
            attach_tooltip(tooltips.simulation.cdc)
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
            dpg.add_text("Maximum frequency".rjust(label_pad))
            attach_tooltip(tooltips.simulation.max_freq)
            self.max_freq_input: int = dpg.generate_uuid()
            dpg.add_input_float(
                label="Hz",
                default_value=1e5,
                min_value=1e-20,
                max_value=1e20,
                min_clamped=True,
                max_clamped=True,
                on_enter=True,
                format="%.3g",
                step=0.0,
                width=-18,
                tag=self.max_freq_input,
            )
        with dpg.group(horizontal=True):
            dpg.add_text("Minimum frequency".rjust(label_pad))
            attach_tooltip(tooltips.simulation.min_freq)
            self.min_freq_input: int = dpg.generate_uuid()
            dpg.add_input_float(
                label="Hz",
                default_value=1e-2,
                min_value=1e-20,
                max_value=1e20,
                min_clamped=True,
                max_clamped=True,
                on_enter=True,
                format="%.3g",
                step=0.0,
                width=-18,
                tag=self.min_freq_input,
            )
        with dpg.group(horizontal=True):
            dpg.add_text("Num. points per decade".rjust(label_pad))
            attach_tooltip(tooltips.simulation.per_decade)
            self.per_decade_input: int = dpg.generate_uuid()
            dpg.add_input_int(
                default_value=10,
                min_value=1,
                min_clamped=True,
                step=0,
                on_enter=True,
                tag=self.per_decade_input,
                width=-1,
            )
        self.set_settings(default_settings)

    def get_settings(self) -> SimulationSettings:
        cdc: str = dpg.get_value(self.cdc_input) or ""
        circuit: Optional[Circuit] = dpg.get_item_user_data(self.cdc_input)
        if circuit is None or cdc != circuit.to_string():
            circuit = self.parse_cdc(cdc, self.cdc_input)
        min_f: float = dpg.get_value(self.min_freq_input)
        max_f: float = dpg.get_value(self.max_freq_input)
        if min_f > max_f:
            max_f = min_f
            min_f = dpg.get_value(self.max_freq_input)
            dpg.set_value(self.min_freq_input, min_f)
            dpg.set_value(self.max_freq_input, max_f)
        return SimulationSettings(
            cdc=circuit.to_string(12) if circuit is not None else "",
            min_frequency=min_f,
            max_frequency=max_f,
            num_per_decade=dpg.get_value(self.per_decade_input),
        )

    def set_settings(self, settings: SimulationSettings):
        assert type(settings) is SimulationSettings, settings
        self.parse_cdc(settings.cdc)
        dpg.set_value(self.min_freq_input, settings.min_frequency)
        dpg.set_value(self.max_freq_input, settings.max_frequency)
        dpg.set_value(self.per_decade_input, settings.num_per_decade)

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
        return (
            dpg.is_item_active(self.cdc_input)
            or dpg.is_item_active(self.max_freq_input)
            or dpg.is_item_active(self.min_freq_input)
            or dpg.is_item_active(self.per_decade_input)
        )


class ParametersTable:
    def __init__(self):
        self._header: int = dpg.generate_uuid()
        with dpg.collapsing_header(label=" Parameters", leaf=True, tag=self._header):
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
                attach_tooltip(tooltips.simulation.element)
                dpg.add_table_column(
                    label="Parameter",
                    width_fixed=True,
                )
                attach_tooltip(tooltips.simulation.parameter)
                dpg.add_table_column(
                    label="Value",
                    width_fixed=True,
                )
                attach_tooltip(tooltips.simulation.parameter_value)

    def clear(self, hide: bool):
        if hide:
            dpg.hide_item(self._header)
        dpg.delete_item(self._table, children_only=True, slot=1)

    def populate(self, simulation: SimulationResult):
        dpg.show_item(self._header)
        column_pads: List[int] = [
            10,
            11,
            10,
        ]
        if simulation is None:
            with dpg.table_row(parent=self._table):
                dpg.add_text("".ljust(column_pads[0]))
                dpg.add_text("".ljust(column_pads[1]))
                dpg.add_text("".ljust(column_pads[2]))
            return
        element_labels: List[str] = []
        element_tooltips: List[str] = []
        parameter_labels: List[str] = []
        values: List[str] = []
        value_tooltips: List[str] = []
        element_label: str
        element_tooltip: str
        parameter_label: str
        value: str
        value_tooltip: str
        parameters: Dict[str, FittedParameter]
        for element in simulation.circuit.get_elements():
            float_value: float
            for parameter_label, float_value in element.get_parameters().items():
                element_labels.append(element.get_label())
                element_tooltips.append(element.get_extended_description())
                parameter_labels.append(parameter_label)
                values.append(f"{format_number(float_value, width=9, significants=3)}")
                value_tooltips.append(
                    f"{format_number(float_value, decimals=6).strip()}"
                )
        values = align_numbers(values)
        num_rows: int = 0
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
            with dpg.table_row(parent=self._table):
                dpg.add_text(element_label.ljust(column_pads[0]))
                if element_tooltip != "":
                    attach_tooltip(element_tooltip)
                dpg.add_text(parameter_label.ljust(column_pads[1]))
                dpg.add_text(value.ljust(column_pads[2]))
                attach_tooltip(value_tooltip)
                num_rows += 1
        dpg.set_item_height(self._table, 18 + 23 * max(1, num_rows))


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
                    "Maximum frequency",
                    "Minimum frequency",
                    "Points per decade",
                ]:
                    with dpg.table_row():
                        dpg.add_text(label.rjust(label_pad))
                        tooltip_tag: int = dpg.generate_uuid()
                        dpg.add_text("", user_data=tooltip_tag)
                        attach_tooltip("", tag=tooltip_tag)
            self._apply_button: int = dpg.generate_uuid()
            dpg.add_button(
                label="Apply settings",
                callback=lambda s, a, u: signals.emit(
                    Signal.APPLY_SIMULATION_SETTINGS,
                    **u,
                ),
                tag=self._apply_button,
            )
            attach_tooltip(tooltips.general.apply_settings)

    def clear(self, hide: bool):
        if hide:
            dpg.hide_item(self._header)
        row: int
        for row in dpg.get_item_children(self._table, slot=1):
            tag: int = dpg.get_item_children(row, slot=1)[1]
            dpg.set_value(tag, "")
            dpg.hide_item(dpg.get_item_parent(dpg.get_item_user_data(tag)))

    def populate(self, settings: SimulationSettings):
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
        circuit: Circuit = pyimpspec.parse_cdc(settings.cdc)
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
                format_number(settings.max_frequency, 3, 12),
            ),
            (
                rows[2],
                cells[2][1],
                format_number(settings.min_frequency, 3, 12),
            ),
            (
                rows[3],
                cells[3][1],
                f"{settings.num_per_decade}",
            ),
        ]:
            dpg.set_value(tag, value.split("\n")[0])
            update_tooltip(dpg.get_item_user_data(tag), value)
            dpg.show_item(dpg.get_item_parent(dpg.get_item_user_data(tag)))
        dpg.set_item_height(self._table, 18 + 23 * 4)
        dpg.set_item_user_data(
            self._apply_button,
            {"settings": settings},
        )


class DataSetsCombo:
    def __init__(self, label: str, width: int, callback: Callable):
        self.labels: List[str] = []
        dpg.add_text(label)
        self.tag: int = dpg.generate_uuid()
        dpg.add_combo(
            callback=callback,
            user_data={},
            width=width,
            tag=self.tag,
        )

    def populate(self, labels: List[str], lookup: Dict[str, DataSet]):
        self.labels.clear()
        self.labels.append("")
        self.labels.extend(labels)
        label: str = dpg.get_value(self.tag) or ""
        if labels and label not in labels:
            label = ""
        dpg.configure_item(
            self.tag,
            default_value=label,
            items=[""] + labels,
            user_data=lookup,
        )

    def get(self) -> Optional[DataSet]:
        return dpg.get_item_user_data(self.tag).get(dpg.get_value(self.tag))

    def set(self, label: str):
        assert type(label) is str, label
        assert label in self.labels
        dpg.set_value(self.tag, label)

    def clear(self):
        dpg.configure_item(
            self.tag,
            default_value="",
        )

    def get_next(self) -> Optional[DataSet]:
        lookup: Dict[str, DataSet] = dpg.get_item_user_data(self.tag)
        if not lookup:
            return None
        labels: List[str] = list(lookup.keys())
        current_label: str = dpg.get_value(self.tag)
        if current_label not in labels:
            return lookup[labels[0]]
        index: int = labels.index(current_label) + 1
        if index == len(labels):
            return None
        return lookup[labels[index % len(labels)]]

    def get_previous(self) -> Optional[DataSet]:
        lookup: Dict[str, DataSet] = dpg.get_item_user_data(self.tag)
        if not lookup:
            return None
        labels: List[str] = list(lookup.keys())
        current_label: str = dpg.get_value(self.tag)
        if current_label not in labels:
            return lookup[labels[-1]]
        index: int = labels.index(current_label) - 1
        if index == -1:
            return None
        return lookup[labels[index % len(labels)]]


class ResultsCombo:
    def __init__(self, label: str, width: int, callback: Callable):
        self.labels: Dict[str, str] = {}
        dpg.add_text(label)
        self.tag: int = dpg.generate_uuid()
        dpg.add_combo(
            callback=callback,
            user_data={},
            width=width,
            tag=self.tag,
        )

    def populate(self, lookup: Dict[str, SimulationResult]):
        self.labels.clear()
        labels: List[str] = list(lookup.keys())
        longest_cdc: int = max(list(map(lambda _: len(_[: _.find(" ")]), labels)) + [1])
        old_key: str
        for old_key in labels:
            simulation: SimulationResult = lookup[old_key]
            del lookup[old_key]
            cdc, timestamp = (
                old_key[: old_key.find(" ")],
                old_key[old_key.find(" ") + 1 :],
            )
            new_key: str = f"{cdc.ljust(longest_cdc)} {timestamp}"
            self.labels[old_key] = new_key
            lookup[new_key] = simulation
        labels = list(lookup.keys())
        dpg.configure_item(
            self.tag,
            default_value=labels[0] if labels else "",
            items=labels,
            user_data=lookup,
        )

    def get(self) -> Optional[SimulationResult]:
        return dpg.get_item_user_data(self.tag).get(dpg.get_value(self.tag))

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

    def get_next(self) -> Optional[SimulationResult]:
        lookup: Dict[str, SimulationResult] = dpg.get_item_user_data(self.tag)
        if not lookup:
            return None
        labels: List[str] = list(lookup.keys())
        index: int = labels.index(dpg.get_value(self.tag)) + 1
        return lookup[labels[index % len(labels)]]

    def get_previous(self) -> Optional[SimulationResult]:
        lookup: Dict[str, SimulationResult] = dpg.get_item_user_data(self.tag)
        if not lookup:
            return None
        labels: List[str] = list(lookup.keys())
        index: int = labels.index(dpg.get_value(self.tag)) - 1
        return lookup[labels[index % len(labels)]]


class SimulationTab:
    def __init__(self, state):
        self.state = state
        self.queued_update: Optional[Callable] = None
        self.tab: int = dpg.generate_uuid()
        with dpg.tab(label="Simulation", tag=self.tab):
            self.sidebar_width: int = 350
            settings_height: int = 128
            label_pad: int = 24
            with dpg.group(horizontal=True):
                self.sidebar_window: int = dpg.generate_uuid()
                with dpg.child_window(
                    border=False,
                    width=self.sidebar_width,
                    tag=self.sidebar_window,
                ):
                    # Settings
                    with dpg.child_window(
                        border=True, width=-1, height=settings_height
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
                            state.config.default_simulation_settings,
                            label_pad,
                            circuit_editor=self.circuit_editor,
                        )
                        with dpg.group(horizontal=True):
                            self.visibility_item: int = dpg.generate_uuid()
                            dpg.add_text("".rjust(label_pad), tag=self.visibility_item)
                            self.perform_sim_button: int = dpg.generate_uuid()
                            dpg.add_button(
                                label="Perform simulation",
                                callback=lambda s, a, u: signals.emit(
                                    Signal.PERFORM_SIMULATION,
                                    data=u,
                                    settings=self.get_settings(),
                                ),
                                user_data=None,
                                width=-1,
                                tag=self.perform_sim_button,
                            )
                    with dpg.child_window(width=-1, height=82):
                        label_pad = 8
                        with dpg.group(horizontal=True):
                            self.data_sets_combo: DataSetsCombo = DataSetsCombo(
                                label="Data set".rjust(label_pad),
                                width=-60,
                                callback=lambda s, a, u: signals.emit(
                                    Signal.SELECT_SIMULATION_RESULT,
                                    simulation=self.results_combo.get(),
                                    data=u.get(a),
                                ),
                            )
                        with dpg.group(horizontal=True):
                            self.results_combo: ResultsCombo = ResultsCombo(
                                label="Result".rjust(label_pad),
                                width=-60,
                                callback=lambda s, a, u: signals.emit(
                                    Signal.SELECT_SIMULATION_RESULT,
                                    data=self.data_sets_combo.get(),
                                    simulation=u.get(a),
                                ),
                            )
                            self.delete_button: int = dpg.generate_uuid()
                            dpg.add_button(
                                label="Delete",
                                callback=lambda s, a, u: signals.emit(
                                    Signal.DELETE_SIMULATION_RESULT, simulation=u
                                ),
                                width=-1,
                                tag=self.delete_button,
                            )
                            attach_tooltip(tooltips.simulation.remove)
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
                    with dpg.child_window(width=-1, height=-1):
                        self.result_group: int = dpg.generate_uuid()
                        with dpg.group(tag=self.result_group):
                            self.parameters_table: ParametersTable = ParametersTable()
                            dpg.add_spacer(height=8)
                            self.settings_table: SettingsTable = SettingsTable()
                self.plot_window: int = dpg.generate_uuid()
                with dpg.child_window(
                    border=False,
                    width=-1,
                    height=-1,
                    tag=self.plot_window,
                ):
                    self.minimum_plot_side: int = 400
                    with dpg.group(horizontal=True):
                        self.circuit_preview_height: int = 250
                        with dpg.child_window(
                            border=False,
                            width=-1,
                            height=self.circuit_preview_height,
                        ):
                            self.circuit_preview: CircuitPreview = CircuitPreview()
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
                                label="Sim.",
                                simulation=True,
                                theme=themes.nyquist.simulation,
                            )
                            self.nyquist_plot.plot(
                                real=array([]),
                                imaginary=array([]),
                                label="Sim.",
                                simulation=True,
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
                                    "|Z| (s)",
                                    "phi (s)",
                                ),
                                simulation=True,
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
                                    "|Z| (s)",
                                    "phi (s)",
                                ),
                                simulation=True,
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
                                    callback=lambda s, a, u: signals.emit(
                                        Signal.SHOW_ENLARGED_PLOT,
                                        plot=self.bode_plot_horizontal,
                                        adjust_limits=dpg.get_value(
                                            self.adjust_bode_limits_horizontal_checkbox
                                        ),
                                    ),
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
                    with dpg.group(tag=self.vertical_bode_group, show=False):
                        self.bode_plot_vertical: Bode = Bode(
                            width=self.minimum_plot_side, height=self.minimum_plot_side
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
                                "|Z| (s)",
                                "phi (s)",
                            ),
                            simulation=True,
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
                                "|Z| (s)",
                                "phi (s)",
                            ),
                            simulation=True,
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
        self.set_settings(self.state.config.default_simulation_settings)

    def is_visible(self) -> bool:
        return dpg.is_item_visible(self.visibility_item)

    def get_settings(self) -> SimulationSettings:
        return self.settings_menu.get_settings()

    def set_settings(self, settings: SimulationSettings):
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
                self.bode_plot_vertical.resize(-1, self.minimum_plot_side)
        else:
            if dpg.is_item_shown(self.vertical_bode_group):
                dpg.show_item(self.horizontal_bode_group)
                dpg.hide_item(self.vertical_bode_group)
            dpg.split_frame()
            width, height = dpg.get_item_rect_size(self.plot_window)
            width = round((width - 8) / 2)
            height = height - 228 - 24 * 2 - 2
            self.nyquist_plot.resize(width, height)
            self.bode_plot_horizontal.resize(width, height)

    def clear(self, hide: bool = True):
        self.data_sets_combo.clear()
        self.results_combo.clear()
        self.parameters_table.clear(hide=hide)
        self.settings_table.clear(hide=hide)
        self.circuit_preview.clear()
        self.nyquist_plot.clear(delete=False)
        self.bode_plot_horizontal.clear(delete=False)
        self.bode_plot_vertical.clear(delete=False)

    def populate_data_sets(self, labels: List[str], lookup: Dict[str, DataSet]):
        assert type(labels) is list, labels
        assert type(lookup) is dict, lookup
        self.data_sets_combo.populate(labels, lookup)

    def populate_simulations(self, lookup: Dict[str, SimulationResult]):
        assert type(lookup) is dict, lookup
        if not lookup:
            self.clear()
        self.results_combo.populate(lookup)
        data: Optional[DataSet] = dpg.get_item_user_data(self.perform_sim_button)
        if not self.results_combo.labels:
            self.select_simulation_result(None, data)
            return
        signals.emit(
            Signal.SELECT_SIMULATION_RESULT,
            simulation=self.results_combo.get(),
            data=data,
        )

    def get_next_data_set(self) -> Optional[DataSet]:
        return self.data_sets_combo.get_next()

    def get_previous_data_set(self) -> Optional[DataSet]:
        return self.data_sets_combo.get_previous()

    def get_next_result(self) -> Optional[SimulationResult]:
        return self.results_combo.get_next()

    def get_previous_result(self) -> Optional[SimulationResult]:
        return self.results_combo.get_previous()

    def select_data_set(self, data: Optional[DataSet]):
        assert type(data) is DataSet or data is None, data
        self.clear()
        dpg.set_item_user_data(self.perform_sim_button, data)
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

    def select_simulation_result(
        self, simulation: Optional[SimulationResult], data: Optional[DataSet]
    ):
        assert type(simulation) is SimulationResult or simulation is None, simulation
        assert type(data) is DataSet or data is None, data
        dpg.set_item_user_data(
            self.delete_button,
            simulation,
        )
        dpg.set_item_user_data(
            self.copy_output_button,
            {
                "fit_or_sim": simulation,
                "data": data,
            },
        )
        if not self.is_visible():
            self.queued_update = lambda: self.select_simulation_result(simulation, data)
            return
        self.queued_update = None
        self.select_data_set(data)
        if simulation is None:
            if dpg.get_value(self.adjust_nyquist_limits_checkbox):
                self.nyquist_plot.queue_limits_adjustment()
            if dpg.get_value(self.adjust_bode_limits_horizontal_checkbox):
                self.bode_plot_horizontal.queue_limits_adjustment()
                self.bode_plot_vertical.queue_limits_adjustment()
            return
        self.results_combo.set(simulation.get_label())
        self.parameters_table.populate(simulation)
        self.settings_table.populate(simulation.settings)
        self.circuit_preview.update(pyimpspec.parse_cdc(simulation.settings.cdc))
        real: ndarray
        imag: ndarray
        real, imag = simulation.get_nyquist_data()
        self.nyquist_plot.update(
            index=1,
            real=real,
            imaginary=imag,
        )
        real, imag = simulation.get_nyquist_data(
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
        freq, mag, phase = simulation.get_bode_data()
        self.bode_plot_horizontal.update(
            index=1,
            frequency=freq,
            magnitude=mag,
            phase=phase,
        )
        freq, mag, phase = simulation.get_bode_data(
            num_per_decade=self.state.config.num_per_decade_in_simulated_lines
        )
        self.bode_plot_horizontal.update(
            index=2,
            frequency=freq,
            magnitude=mag,
            phase=phase,
        )
        freq, mag, phase = simulation.get_bode_data()
        self.bode_plot_vertical.update(
            index=1,
            frequency=freq,
            magnitude=mag,
            phase=phase,
        )
        freq, mag, phase = simulation.get_bode_data(
            num_per_decade=self.state.config.num_per_decade_in_simulated_lines
        )
        self.bode_plot_vertical.update(
            index=2,
            frequency=freq,
            magnitude=mag,
            phase=phase,
        )
        if dpg.get_value(self.adjust_nyquist_limits_checkbox):
            self.nyquist_plot.queue_limits_adjustment()
        if dpg.get_value(self.adjust_bode_limits_horizontal_checkbox):
            self.bode_plot_horizontal.queue_limits_adjustment()
            self.bode_plot_vertical.queue_limits_adjustment()

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

    def get_active_output(self) -> Optional[FitSimOutput]:
        return label_to_fit_sim_output.get(dpg.get_value(self.output_combo))

    def has_active_input(self) -> bool:
        return self.settings_menu.has_active_input()
