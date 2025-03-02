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

from traceback import format_exc
from typing import (
    Callable,
    Dict,
    List,
    Optional,
    Tuple,
)
from numpy import (
    array,
    complex128,
    inf,
    ndarray,
)
import pyimpspec
from pyimpspec import (
    Circuit,
    ComplexImpedance,
    Connection,
    Container,
    Element,
    Frequencies,
)
from pyimpspec.analysis.utility import _interpolate
import dearpygui.dearpygui as dpg
from deareis.signals import Signal
import deareis.signals as signals
import deareis.themes as themes
from deareis.utility import (
    align_numbers,
    calculate_window_position_dimensions,
    find_parent_containers,
    format_number,
    pad_tab_labels,
    process_cdc,
)
from deareis.tooltips import (
    attach_tooltip,
    update_tooltip,
)
import deareis.tooltips as tooltips
from deareis.gui.plots import (
    Bode,
    Impedance,
    Nyquist,
    Plot,
)
from deareis.enums import (
    Context,
    FitSimOutput,
    label_to_fit_sim_output,
)
from deareis.gui.circuit_editor import (
    CircuitPreview,
    CircuitEditor,
)
from deareis.data import (
    DataSet,
    SimulationResult,
    SimulationSettings,
)
from deareis.gui.widgets.combo import Combo
from deareis.typing.helpers import Tag
from deareis.enums import Action
from deareis.keybindings import (
    Keybinding,
    TemporaryKeybindingHandler,
)


STATE = None
_DEFAULT_NOISE: float = 0.0


class NoiseAdditionWindow:
    def __init__(
        self,
        **kwargs,
    ):
        x: int
        y: int
        w: int
        h: int
        x, y, w, h = calculate_window_position_dimensions(
            width=250,
            height=60,
        )

        self.window: Tag = dpg.generate_uuid()
        with dpg.window(
            label="Added noise",
            modal=True,
            pos=(
                x,
                y,
            ),
            width=w,
            height=h,
            no_resize=True,
            no_move=True,
            on_close=self.close,
            tag=self.window,
        ):
            with dpg.group(horizontal=True):
                dpg.add_text("Noise SD")
                attach_tooltip(tooltips.simulation.noise_pct)
                
                self.noise_input: Tag = dpg.generate_uuid()
                dpg.add_input_float(
                    label="% x |Z|",
                    default_value=_DEFAULT_NOISE,
                    min_value=0.0,
                    max_value=100.0,
                    min_clamped=True,
                    max_clamped=True,
                    on_enter=True,
                    format="%.3g",
                    step=0.0,
                    width=-56,
                    tag=self.noise_input,
                )

            dpg.add_spacer(height=16)

            self.accept_button: Tag = dpg.generate_uuid()
            dpg.add_button(
                label="Proceed",
                width=-1,
                callback=lambda s, a, u: self.accept(),
                user_data=kwargs,
                tag=self.accept_button,
            )

        self.register_keybindings()
        dpg.focus_item(self.noise_input)

    def register_keybindings(self):
        callbacks: Dict[Keybinding, Callable] = {}

        # Cancel
        kb: Keybinding = Keybinding(
            key=dpg.mvKey_Escape,
            mod_alt=False,
            mod_ctrl=False,
            mod_shift=False,
            action=Action.CANCEL,
        )
        callbacks[kb] = self.close

        # Accept
        for kb in STATE.config.keybindings:
            if kb.action is Action.PERFORM_ACTION:
                break
        else:
            kb = Keybinding(
                key=dpg.mvKey_Return,
                mod_alt=True,
                mod_ctrl=False,
                mod_shift=False,
                action=Action.PERFORM_ACTION,
            )
        callbacks[kb] = self.accept


        # Create the handler
        self.keybinding_handler: TemporaryKeybindingHandler = (
            TemporaryKeybindingHandler(callbacks=callbacks)
        )

    def close(self):
        dpg.hide_item(self.window)
        dpg.delete_item(self.window)
        self.keybinding_handler.delete()
        signals.emit(Signal.UNBLOCK_KEYBINDINGS)

    def accept(self):
        global _DEFAULT_NOISE

        noise_pct: float = dpg.get_value(self.noise_input)
        _DEFAULT_NOISE = max((0.0, noise_pct))

        kwargs = dpg.get_item_user_data(self.accept_button)
        if kwargs is None:
            return

        kwargs["noise_pct"] = noise_pct
        self.close()
        signals.emit(
            Signal.LOAD_SIMULATION_AS_DATA_SET,
            **kwargs,
        )

class SettingsMenu:
    def __init__(
        self,
        default_settings: SimulationSettings,
        label_pad: int,
        circuit_editor: Optional[CircuitEditor] = None,
        editor_callback: Optional[Callable] = None,
    ):
        self.circuit_editor: Optional[CircuitEditor] = circuit_editor
        with dpg.group(horizontal=True):
            dpg.add_text("Circuit".rjust(label_pad))
            attach_tooltip(tooltips.simulation.cdc)

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
            dpg.add_text("Maximum frequency".rjust(label_pad))
            attach_tooltip(tooltips.simulation.max_freq)
            
            self.max_freq_input: Tag = dpg.generate_uuid()
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
            
            self.min_freq_input: Tag = dpg.generate_uuid()
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
            
            self.per_decade_input: Tag = dpg.generate_uuid()
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
            cdc=circuit.serialize() if circuit is not None else "",
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
        return (
            dpg.is_item_active(self.cdc_input)
            or dpg.is_item_active(self.max_freq_input)
            or dpg.is_item_active(self.min_freq_input)
            or dpg.is_item_active(self.per_decade_input)
        )


class ParametersTable:
    def __init__(self):
        self._header: Tag = dpg.generate_uuid()
        with dpg.collapsing_header(label=" Parameters", leaf=True, tag=self._header):
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

        element_names: List[str] = []
        element_tooltips: List[str] = []

        parameter_labels: List[str] = []
        parameter_tooltips: List[str] = []

        values: List[str] = []
        value_tooltips: List[str] = []

        internal_identifiers: Dict[int, Element] = {
            v: k
            for k, v in simulation.circuit.generate_element_identifiers(
                running=True
            ).items()
        }
        external_identifiers: Dict[Element, int] = (
            simulation.circuit.generate_element_identifiers(running=False)
        )
        parent_containers: Dict[Element, Container] = find_parent_containers(
            simulation.circuit
        )

        element_name: str
        element_tooltip: str
        parameter_label: str
        parameter_tooltip: str
        value: str
        value_tooltip: str
        for _, element in sorted(internal_identifiers.items(), key=lambda _: _[0]):
            element_name = simulation.circuit.get_element_name(
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
            if element in parent_containers:
                parent_name: str = simulation.circuit.get_element_name(
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

            float_value: float
            for parameter_label, float_value in element.get_values().items():
                element_names.append(element_name)
                element_tooltips.append(element_tooltip)
                parameter_labels.append(parameter_label)
                unit: str = element.get_unit(parameter_label)
                parameter_tooltips.append(
                    (
                        f"{element.get_value_description(parameter_label)}\n\n"
                        f"Unit: {unit}\n"
                    ).strip()
                )
                values.append(f"{format_number(float_value, width=9, significants=3)}")
                value_tooltips.append(
                    f"{format_number(float_value, decimals=6).strip()} {unit}".strip()
                )

        values = align_numbers(values)
        num_rows: int = 0
        for (
            element_name,
            element_tooltip,
            parameter_label,
            parameter_tooltip,
            value,
            value_tooltip,
        ) in zip(
            element_names,
            element_tooltips,
            parameter_labels,
            parameter_tooltips,
            values,
            value_tooltips,
        ):
            with dpg.table_row(parent=self._table):
                dpg.add_text(element_name.ljust(column_pads[0]))
                attach_tooltip(element_tooltip)
                dpg.add_text(parameter_label.ljust(column_pads[1]))
                attach_tooltip(parameter_tooltip)
                dpg.add_text(value.ljust(column_pads[2]))
                attach_tooltip(value_tooltip)
                num_rows += 1

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
                        tooltip_tag: Tag = dpg.generate_uuid()
                        dpg.add_text("", user_data=tooltip_tag)
                        attach_tooltip("", tag=tooltip_tag)

            dpg.add_spacer(height=8)

            with dpg.group(horizontal=True):
                self._apply_button: Tag = dpg.generate_uuid()
                dpg.add_button(
                    label="Apply settings",
                    callback=lambda s, a, u: signals.emit(
                        Signal.APPLY_SIMULATION_SETTINGS,
                        **u,
                    ),
                    tag=self._apply_button,
                    width=154,
                )
                attach_tooltip(tooltips.general.apply_settings)

                self._load_as_data_button: Tag = dpg.generate_uuid()
                dpg.add_button(
                    label="Load as data set",
                    callback=lambda s, a, u: self.show_noise_addition_window(**u),
                    tag=self._load_as_data_button,
                    width=-1,
                )
                attach_tooltip(tooltips.simulation.load_as_data_set)

    def show_noise_addition_window(self, **kwargs):
        window: NoiseAdditionWindow = NoiseAdditionWindow(**kwargs)
        signals.emit(
            Signal.BLOCK_KEYBINDINGS,
            window=window.window,
            window_object=window,
        )

    def clear(self, hide: bool):
        if hide:
            dpg.hide_item(self._header)

        row: int
        for row in dpg.get_item_children(self._table, slot=1):
            tag: Tag = dpg.get_item_children(row, slot=1)[1]
            dpg.set_value(tag, "")
            dpg.hide_item(dpg.get_item_parent(dpg.get_item_user_data(tag)))

    def populate(self, simulation: SimulationResult):
        settings: SimulationSettings = simulation.settings
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
        for row, tag, value in [
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
        dpg.set_item_user_data(
            self._load_as_data_button,
            {"simulation": simulation},
        )


class DataSetsCombo:
    def __init__(self, label: str, width: int, callback: Callable):
        self.labels: List[str] = []
        dpg.add_text(label)
        self.tag: Tag = dpg.generate_uuid()
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
        self.tag: Tag = dpg.generate_uuid()
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
            cdc: str
            timestamp: str
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
        dpg.set_value(self.tag, label)

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
        index: int = labels.index(self.labels[dpg.get_value(self.tag)]) + 1

        return lookup[labels[index % len(labels)]]

    def get_previous(self) -> Optional[SimulationResult]:
        lookup: Dict[str, SimulationResult] = dpg.get_item_user_data(self.tag)
        if not lookup:
            return None

        labels: List[str] = list(lookup.keys())
        index: int = labels.index(self.labels[dpg.get_value(self.tag)]) - 1

        return lookup[labels[index % len(labels)]]


class SimulationTab:
    def __init__(self, state):
        global STATE

        STATE = state

        self.state = state
        self.queued_update: Optional[Callable] = None
        self.create_tab(state)
        self.set_settings(self.state.config.default_simulation_settings)

    def create_tab(self, state):
        self.tab: Tag = dpg.generate_uuid()
        with dpg.tab(label="Simulation", tag=self.tab):
            self.sidebar_width: int = 350
            settings_height: int = 128
            label_pad: int = 24
            with dpg.group(horizontal=True):
                self.create_sidebar(state, label_pad, settings_height)
                self.create_plots()

    def create_sidebar(self, state, label_pad: int, settings_height: int):
        self.sidebar_window: Tag = dpg.generate_uuid()
        with dpg.child_window(
            border=False,
            width=self.sidebar_width,
            tag=self.sidebar_window,
        ):
            self.create_settings_menu(state, label_pad, settings_height)
            self.create_results_menu()
            self.create_results_tables()

    def create_settings_menu(self, state, label_pad: int, settings_height: int):
        with dpg.child_window(border=True, width=-1, height=settings_height):
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
                state.config.default_simulation_settings,
                label_pad,
                circuit_editor=self.circuit_editor,
                editor_callback=self.show_circuit_editor,
            )

            with dpg.group(horizontal=True):
                self.visibility_item: Tag = dpg.generate_uuid()
                dpg.add_text("".rjust(label_pad), tag=self.visibility_item)

                self.perform_sim_button: Tag = dpg.generate_uuid()
                dpg.add_button(
                    label="Perform",
                    callback=lambda s, a, u: signals.emit(
                        Signal.PERFORM_SIMULATION,
                        data=u,
                        settings=self.get_settings(),
                    ),
                    user_data=None,
                    width=-1,
                    tag=self.perform_sim_button,
                )

    def create_results_menu(self):
        with dpg.child_window(width=-1, height=82):
            label_pad = 8
            with dpg.group(horizontal=True):
                self.data_sets_combo: DataSetsCombo = DataSetsCombo(
                    label="Data set".rjust(label_pad),
                    width=-60,
                    callback=lambda s, a, u: signals.emit(
                        Signal.SELECT_SIMULATION_RESULT,
                        simulation=dpg.get_item_user_data(self.delete_button),
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

                self.delete_button: Tag = dpg.generate_uuid()
                dpg.add_button(
                    label="Delete",
                    callback=lambda s, a, u: signals.emit(
                        Signal.DELETE_SIMULATION_RESULT,
                        simulation=u,
                    ),
                    width=-1,
                    tag=self.delete_button,
                )
                attach_tooltip(tooltips.simulation.remove)

            with dpg.group(horizontal=True):
                dpg.add_text("Output".rjust(label_pad))
                output_items: List[str] = [
                    _ for _ in label_to_fit_sim_output.keys() if "statistics" not in _
                ]
                self.output_combo: Combo = Combo(
                    items=output_items,
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
                self.parameters_table: ParametersTable = ParametersTable()
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
                dpg.add_text("Simulated circuit")
                self.circuit_preview: CircuitPreview = CircuitPreview()

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
                label="Sim.",
                line=False,
                simulation=True,
                theme=themes.nyquist.simulation,
            )
            self.nyquist_plot.plot(
                impedances=array([], dtype=complex128),
                label="Sim.",
                line=True,
                simulation=True,
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
                        context=Context.SIMULATION_TAB,
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
                    "Mod(sim.)",
                    "Phase(sim.)",
                ),
                line=False,
                simulation=True,
                themes=(
                    themes.bode.magnitude_simulation,
                    themes.bode.phase_simulation,
                ),
            )
            self.bode_plot.plot(
                frequencies=array([]),
                impedances=array([], dtype=complex128),
                labels=(
                    "Mod(sim.)",
                    "Phase(sim.)",
                ),
                line=True,
                simulation=True,
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
                        context=Context.SIMULATION_TAB,
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
                    "Re(sim.)",
                    "Im(sim.)",
                ),
                line=False,
                simulation=True,
                themes=(
                    themes.impedance.real_simulation,
                    themes.impedance.imaginary_simulation,
                ),
            )
            self.impedance_plot.plot(
                frequencies=array([]),
                impedances=array([], dtype=complex128),
                labels=(
                    "Re(sim.)",
                    "Im(sim.)",
                ),
                line=True,
                simulation=True,
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
                        context=Context.SIMULATION_TAB,
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

    def get_settings(self) -> SimulationSettings:
        return self.settings_menu.get_settings()

    def set_settings(self, settings: SimulationSettings):
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
        self.settings_table.clear(hide=hide)
        self.circuit_preview.clear()
        self.nyquist_plot.clear(delete=False)
        self.bode_plot.clear(delete=False)
        self.impedance_plot.clear(delete=False)

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

    def select_simulation_result(
        self,
        simulation: Optional[SimulationResult],
        data: Optional[DataSet],
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

            if dpg.get_value(self.adjust_bode_limits_checkbox):
                self.bode_plot.queue_limits_adjustment()

            if dpg.get_value(self.adjust_impedance_limits_checkbox):
                self.impedance_plot.queue_limits_adjustment()

            return

        self.results_combo.set(simulation.get_label())
        self.parameters_table.populate(simulation)
        self.settings_table.populate(simulation)
        self.circuit_preview.update(pyimpspec.parse_cdc(simulation.settings.cdc))

        freq_markers: ndarray = simulation.get_frequencies()
        freq_line: ndarray = simulation.get_frequencies(
            num_per_decade=self.state.config.num_per_decade_in_simulated_lines
        )
        Z_markers: ndarray = simulation.get_impedances()
        Z_line: ndarray = simulation.get_impedances(
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

        if dpg.get_value(self.adjust_nyquist_limits_checkbox):
            self.nyquist_plot.queue_limits_adjustment()

        if dpg.get_value(self.adjust_bode_limits_checkbox):
            self.bode_plot.queue_limits_adjustment()

        if dpg.get_value(self.adjust_impedance_limits_checkbox):
            self.impedance_plot.queue_limits_adjustment()

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

        settings: SimulationSettings = self.settings_menu.get_settings()
        circuit: Optional[Circuit] = self.settings_menu.parse_cdc(
            settings.cdc,
            sender=self.settings_menu.cdc_input,
        )

        editor_kwargs: dict = dpg.get_item_user_data(self.settings_menu.editor_button)
        if editor_kwargs["data"] is None:
            editor_kwargs = editor_kwargs.copy()
            f: Frequencies = _interpolate(
                [settings.max_frequency, settings.min_frequency],
                num_per_decade=settings.num_per_decade,
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
        if circuit is None:
            return

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

    def accept_parameters(self, circuit: Circuit):
        self.settings_menu.parse_cdc(circuit.serialize())

    def get_active_output(self) -> Optional[FitSimOutput]:
        return self.output_combo.get_value()

    def has_active_input(self) -> bool:
        return self.settings_menu.has_active_input()

    def show_admittance_plots(self) -> bool:
        return dpg.get_value(self.nyquist_admittance_checkbox)
