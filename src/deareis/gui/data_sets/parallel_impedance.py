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

from warnings import (
    catch_warnings,
    filterwarnings,
)
from pyimpspec import Circuit
from threading import Timer
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
    ndarray,
)
import dearpygui.dearpygui as dpg
from deareis.gui.plots import (
    BodeMagnitude,
    BodePhase,
    Nyquist,
)
import deareis.themes as themes
from deareis.utility import (
    calculate_window_position_dimensions,
    pad_tab_labels,
    process_cdc,
)
from deareis.tooltips import attach_tooltip
import deareis.tooltips as tooltips
from deareis.gui.circuit_editor import CircuitEditor
from deareis.signals import Signal
import deareis.signals as signals
from deareis.data import DataSet
from deareis.state import STATE
from deareis.enums import Action
from deareis.keybindings import (
    Keybinding,
    TemporaryKeybindingHandler,
)
from deareis.typing.helpers import Tag


class ParallelImpedance:
    def __init__(
        self,
        data: DataSet,
        callback: Callable,
        admittance: bool,
    ):
        assert type(data) is DataSet, data
        self.data: DataSet = data
        self.preview_data: DataSet = DataSet.from_dict(data.to_dict())
        self.callback: Callable = callback
        self.create_window(admittance=admittance)
        self.register_keybindings()
        # This bool is used to prevent the Escape key from closing the window
        # when the intention is to only hide/close the circuit editor.
        self.editing_circuit: bool = False
        self.select_option(self.radio_buttons, self.options[0])
        self.toggle_plot_admittance(admittance)

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

        # Previous option
        for kb in STATE.config.keybindings:
            if kb.action is Action.PREVIOUS_PRIMARY_RESULT:
                break
        else:
            kb = Keybinding(
                key=dpg.mvKey_Prior,
                mod_alt=False,
                mod_ctrl=False,
                mod_shift=False,
                action=Action.PREVIOUS_PRIMARY_RESULT,
            )
        callbacks[kb] = lambda: self.cycle_options(step=-1)

        # Next option
        for kb in STATE.config.keybindings:
            if kb.action is Action.NEXT_PRIMARY_RESULT:
                break
        else:
            kb = Keybinding(
                key=dpg.mvKey_Next,
                mod_alt=False,
                mod_ctrl=False,
                mod_shift=False,
                action=Action.NEXT_PRIMARY_RESULT,
            )
        callbacks[kb] = lambda: self.cycle_options(step=1)

        # Previous plot tab
        for kb in STATE.config.keybindings:
            if kb.action is Action.PREVIOUS_PLOT_TAB:
                break
        else:
            kb = Keybinding(
                key=dpg.mvKey_Prior,
                mod_alt=True,
                mod_ctrl=False,
                mod_shift=True,
                action=Action.PREVIOUS_PLOT_TAB,
            )
        callbacks[kb] = lambda: self.cycle_plot_tab(step=-1)

        # Next plot tab
        for kb in STATE.config.keybindings:
            if kb.action is Action.NEXT_PLOT_TAB:
                break
        else:
            kb = Keybinding(
                key=dpg.mvKey_Next,
                mod_alt=True,
                mod_ctrl=False,
                mod_shift=True,
                action=Action.NEXT_PLOT_TAB,
            )
        callbacks[kb] = lambda: self.cycle_plot_tab(step=1)

        # Open circuit editor
        for kb in STATE.config.keybindings:
            if kb.action is Action.SHOW_CIRCUIT_EDITOR:
                break
        else:
            kb = Keybinding(
                key=dpg.mvKey_E,
                mod_alt=True,
                mod_ctrl=False,
                mod_shift=False,
                action=Action.SHOW_CIRCUIT_EDITOR,
            )
        callbacks[kb] = self.edit_circuit

        # Create the handler
        self.keybinding_handler: TemporaryKeybindingHandler = (
            TemporaryKeybindingHandler(callbacks=callbacks)
        )

    def create_window(self, admittance: bool):
        self.options: List[str] = [
            "Constant:",
            "Circuit:",
        ]
        label_pad: int = max(map(len, self.options))
        self.options = list(map(lambda _: _.rjust(label_pad), self.options))
        self.circuit_editor_window: int = -1

        x: int
        y: int
        w: int
        h: int
        x, y, w, h = calculate_window_position_dimensions()

        self.window: Tag = dpg.generate_uuid()
        with dpg.window(
            label="Add parallel impedance",
            modal=True,
            pos=(x, y),
            width=w,
            height=h,
            tag=self.window,
            on_close=self.close,
        ):
            self.preview_window: Tag = dpg.generate_uuid()
            with dpg.child_window(border=False, tag=self.preview_window):
                self.create_preview_window(admittance=admittance)

            self.circuit_editor_window = dpg.generate_uuid()

            with dpg.child_window(
                border=False,
                show=False,
                tag=self.circuit_editor_window,
            ):
                self.circuit_editor: CircuitEditor = CircuitEditor(
                    window=self.circuit_editor_window,
                    callback=self.accept_circuit,
                    keybindings=STATE.config.keybindings,
                )

    def create_preview_window(self, admittance: bool):
        with dpg.child_window(
            width=-1,
            height=58,
        ):
            self.radio_buttons: Tag = dpg.generate_uuid()
            with dpg.group(horizontal=True):
                dpg.add_radio_button(
                    items=self.options,
                    default_value=self.options[0],
                    callback=self.select_option,
                    tag=self.radio_buttons,
                )
                with dpg.group():
                    self.constant_group: Tag = dpg.generate_uuid()
                    with dpg.group(horizontal=True, tag=self.constant_group):
                        dpg.add_text("Re(Z) = ")

                        self.constant_real: Tag = dpg.generate_uuid()
                        dpg.add_input_float(
                            label="ohm,",
                            default_value=0.0,
                            step=0.0,
                            format="%.3g",
                            on_enter=True,
                            width=100,
                            tag=self.constant_real,
                            callback=self.update_preview,
                        )

                        dpg.add_text("-Im(Z) = ")

                        self.constant_imag: Tag = dpg.generate_uuid()
                        dpg.add_input_float(
                            label="ohm",
                            default_value=0.0,
                            step=0.0,
                            format="%.3g",
                            on_enter=True,
                            width=100,
                            tag=self.constant_imag,
                            callback=self.update_preview,
                        )

                    self.circuit_group: Tag = dpg.generate_uuid()
                    with dpg.group(horizontal=True, tag=self.circuit_group):
                        self.circuit_cdc: Tag = dpg.generate_uuid()
                        dpg.add_input_text(
                            hint="Input CDC",
                            on_enter=True,
                            width=361,
                            tag=self.circuit_cdc,
                            callback=self.update_preview,
                        )

                        self.circuit_editor_button: Tag = dpg.generate_uuid()
                        dpg.add_button(
                            label="Edit",
                            callback=self.edit_circuit,
                            tag=self.circuit_editor_button,
                        )
                        attach_tooltip(tooltips.general.open_circuit_editor)

                    self.groups: List[int] = [
                        self.constant_group,
                        self.circuit_group,
                    ]

        self.create_plots()

        with dpg.group(horizontal=True):
            dpg.add_button(
                label="Accept".ljust(12),
                callback=self.accept,
            )

            self.admittance_checkbox: Tag = dpg.generate_uuid()
            dpg.add_checkbox(
                label="Y",
                default_value=admittance,
                callback=lambda s, a, u: self.toggle_plot_admittance(a),
                tag=self.admittance_checkbox,
            )
            attach_tooltip(tooltips.general.plot_admittance)

    def toggle_plot_admittance(self, admittance: bool):
        self.nyquist_plot.set_admittance(admittance)
        self.magnitude_plot.set_admittance(admittance)
        self.phase_plot.set_admittance(admittance)

    def create_plots(self):
        settings: List[dict] = [
            {
                "label": "Before",
                "theme": themes.nyquist.data,
                "show_label": False,
            },
            {
                "label": "Before",
                "line": True,
                "theme": themes.nyquist.data,
            },
            {
                "label": "After",
                "theme": themes.bode.phase_data,
                "show_label": False,
            },
            {
                "label": "After",
                "line": True,
                "theme": themes.bode.phase_data,
            },
        ]
        with dpg.child_window(height=-24, border=False):
            self.plot_tab_bar: Tag = dpg.generate_uuid()
            with dpg.tab_bar(tag=self.plot_tab_bar):
                self.create_nyquist_plot(settings)
                self.create_magnitude_plot(settings)
                self.create_phase_plot(settings)

            pad_tab_labels(self.plot_tab_bar)

    def create_nyquist_plot(self, settings: List[dict]):
        with dpg.tab(label="Nyquist"):
            self.nyquist_plot: Nyquist = Nyquist(width=-1, height=-1)
            for kwargs in settings:
                self.nyquist_plot.plot(
                    impedances=array([], dtype=complex128),
                    **kwargs,
                )

    def create_magnitude_plot(self, settings: List[dict]):
        with dpg.tab(label="Bode - magnitude"):
            self.magnitude_plot: BodeMagnitude = BodeMagnitude(width=-1, height=-1)
            for kwargs in settings:
                self.magnitude_plot.plot(
                    frequencies=array([]),
                    impedances=array([], dtype=complex128),
                    **kwargs,
                )

    def create_phase_plot(self, settings: List[dict]):
        with dpg.tab(label="Bode - phase"):
            self.phase_plot: BodePhase = BodePhase(width=-1, height=-1)
            for kwargs in settings:
                self.phase_plot.plot(
                    frequencies=array([]),
                    impedances=array([], dtype=complex128),
                    **kwargs,
                )

    def close(self):
        if not dpg.is_item_visible(self.constant_real):
            return
        elif self.circuit_editor.is_shown():
            return
        elif self.editing_circuit is True:
            self.editing_circuit = False
            return

        self.circuit_editor.delete()
        dpg.hide_item(self.window)
        dpg.delete_item(self.window)
        self.keybinding_handler.delete()
        signals.emit(Signal.UNBLOCK_KEYBINDINGS)

    def accept(self):
        if not dpg.is_item_visible(self.constant_real):
            return
        elif self.circuit_editor.is_shown():
            return
        elif self.editing_circuit is True:
            self.editing_circuit = False
            return
        self.close()
        dictionary: dict = self.preview_data.to_dict()
        del dictionary["uuid"]
        data: DataSet = DataSet.from_dict(dictionary)
        data.set_mask({})
        data.set_label(f"{self.preview_data.get_label()} - added parallel impedance")
        self.callback(data)

    def select_option(self, sender: int, value: str):
        def disable_group(group: int):
            for item in dpg.get_item_children(group, slot=1):
                item_type: str = dpg.get_item_type(item)
                if item_type.endswith("mvText") or item_type.endswith("mvTooltip"):
                    continue
                dpg.disable_item(item)

        def enable_group(group: int):
            for item in dpg.get_item_children(group, slot=1):
                item_type: str = dpg.get_item_type(item)
                if item_type.endswith("mvText") or item_type.endswith("mvTooltip"):
                    continue
                dpg.enable_item(item)

        index: int = self.options.index(value)
        assert 0 <= index < len(self.groups), "Unsupported option!"
        i: int
        group: int
        for i, group in enumerate(self.groups):
            if i == index:
                enable_group(group)
            else:
                disable_group(group)
        self.update_preview()

    def update_preview(self):
        index: int = self.options.index(dpg.get_value(self.radio_buttons))
        f: ndarray = self.data.get_frequencies(masked=None)
        Z: ndarray = self.data.get_impedances(masked=None)
        if index == 0:  # Constant
            Z_const: complex = complex(
                dpg.get_value(self.constant_real),
                -dpg.get_value(self.constant_imag),
            )
            try:
                Z = 1 / (1 / Z + 1 / Z_const)
            except ZeroDivisionError:
                pass
        elif index == 1:  # Circuit
            cdc: str = dpg.get_value(self.circuit_cdc)
            circuit: Optional[Circuit] = dpg.get_item_user_data(self.circuit_cdc)
            if circuit is None or circuit.to_string() != cdc:
                try:
                    circuit, _ = process_cdc(cdc)
                except Exception:
                    return
            if circuit is None:
                return
            with catch_warnings():
                filterwarnings("error", message="divide by zero encountered in divide")
                try:
                    Z = 1 / (1 / Z + 1 / circuit.get_impedances(f))
                except RuntimeWarning:
                    pass
        else:
            raise Exception("Unsupported option!")
        dictionary: dict = self.preview_data.to_dict()
        dictionary.update(
            {
                "real_impedances": list(Z.real),
                "imaginary_impedances": list(Z.imag),
            }
        )
        self.preview_data = DataSet.from_dict(dictionary)
        self.update_plots()

    def update_plots(self):
        self.update_nyquist_plot(self.data, self.preview_data)
        self.update_magnitude_plot(self.data, self.preview_data)
        self.update_phase_plot(self.data, self.preview_data)

    def update_nyquist_plot(self, original: DataSet, preview: DataSet):
        data: List[Tuple[ndarray, ndarray]] = [
            original.get_impedances(masked=None),
            original.get_impedances(masked=None),
            preview.get_impedances(masked=None),
            preview.get_impedances(masked=None),
        ]

        i: int
        Z: ndarray
        for i, Z in enumerate(data):
            self.nyquist_plot.update(
                index=i,
                impedances=Z,
            )

        self.nyquist_plot.queue_limits_adjustment()

    def update_magnitude_plot(self, original: DataSet, preview: DataSet):
        data: List[Tuple[ndarray, ndarray]] = [
            (
                original.get_frequencies(masked=None),
                original.get_impedances(masked=None),
            ),
            (
                original.get_frequencies(masked=None),
                original.get_impedances(masked=None),
            ),
            (
                preview.get_frequencies(masked=None),
                preview.get_impedances(masked=None),
            ),
            (
                preview.get_frequencies(masked=None),
                preview.get_impedances(masked=None),
            ),
        ]

        i: int
        freq: ndarray
        Z: ndarray
        for i, (freq, Z) in enumerate(data):
            self.magnitude_plot.update(
                index=i,
                frequencies=freq,
                impedances=Z,
            )

        self.magnitude_plot.queue_limits_adjustment()

    def update_phase_plot(self, original: DataSet, preview: DataSet):
        data: List[Tuple[ndarray, ndarray]] = [
            (
                original.get_frequencies(masked=None),
                original.get_impedances(masked=None),
            ),
            (
                original.get_frequencies(masked=None),
                original.get_impedances(masked=None),
            ),
            (
                preview.get_frequencies(masked=None),
                preview.get_impedances(masked=None),
            ),
            (
                preview.get_frequencies(masked=None),
                preview.get_impedances(masked=None),
            ),
        ]

        i: int
        freq: ndarray
        Z: ndarray
        for i, (freq, Z) in enumerate(data):
            self.phase_plot.update(
                index=i,
                frequencies=freq,
                impedances=Z,
            )

        self.phase_plot.queue_limits_adjustment()

    def edit_circuit(self):
        if not dpg.is_item_enabled(self.circuit_editor_button):
            return

        self.editing_circuit = True
        self.keybinding_handler.block()
        dpg.hide_item(self.preview_window)

        circuit: Optional[Circuit]
        circuit, _ = process_cdc(dpg.get_value(self.circuit_cdc) or "[]")
        self.circuit_editor.show(circuit, data=self.data)

    def accept_circuit(self, circuit: Optional[Circuit]):
        self.circuit_editor.hide()

        dpg.show_item(self.preview_window)
        self.update_cdc(circuit)
        self.keybinding_handler.unblock()

        t: Timer = Timer(0.5, self.disable_keybinding_override)
        t.start()

    def disable_keybinding_override(self):
        self.editing_circuit = False

    def update_cdc(self, circuit: Optional[Circuit]):
        if circuit is not None:
            for element in circuit.get_elements():
                element.set_label("")
                for param in element.get_values():
                    element.set_fixed(param, True)

        assert dpg.does_item_exist(self.circuit_cdc)
        dpg.configure_item(
            self.circuit_cdc,
            default_value=circuit.to_string() if circuit is not None else "",
            user_data=circuit,
        )
        dpg.show_item(self.preview_window)

        dpg.split_frame(delay=33)
        self.update_preview()

    def cycle_options(self, step: int):
        if self.has_active_input():
            return

        index: int = self.options.index(dpg.get_value(self.radio_buttons)) + step
        dpg.set_value(self.radio_buttons, self.options[index % len(self.options)])
        self.select_option(self.radio_buttons, self.options[index % len(self.options)])

    def cycle_plot_tab(self, step: int):
        tabs: List[Tag] = dpg.get_item_children(self.plot_tab_bar, slot=1)
        index: int = tabs.index(dpg.get_value(self.plot_tab_bar)) + step
        dpg.set_value(self.plot_tab_bar, tabs[index % len(tabs)])

    def has_active_input(self) -> bool:
        return (
            dpg.is_item_active(self.constant_real)
            or dpg.is_item_active(self.constant_imag)
            or dpg.is_item_active(self.circuit_cdc)
        )
