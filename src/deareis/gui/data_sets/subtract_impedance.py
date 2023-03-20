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

from pyimpspec import Circuit
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
from deareis.data import (
    DataSet,
    FitResult,
)
from deareis.state import STATE
from deareis.enums import Action
from deareis.keybindings import (
    Keybinding,
    TemporaryKeybindingHandler,
)


def format_fit_labels(fits: List[FitResult]) -> List[str]:
    old_labels: List[str] = list(map(lambda _: _.get_label(), fits))
    longest_cdc: int = max(list(map(lambda _: len(_[: _.find(" ")]), old_labels)) + [1])
    new_labels: List[str] = []
    old_key: str
    for old_key in old_labels:
        cdc, timestamp = (
            old_key[: old_key.find(" ")],
            old_key[old_key.find(" ") + 1 :],
        )
        new_labels.append(f"{cdc.ljust(longest_cdc)} {timestamp}")
    return new_labels


class SubtractImpedance:
    def __init__(
        self,
        data: DataSet,
        data_sets: List[DataSet],
        fits: List[FitResult],
        callback: Callable,
    ):
        assert type(data) is DataSet, data
        assert type(data_sets) is list and all(
            map(lambda _: type(_) is DataSet, data_sets)
        ), data_sets
        self.data: DataSet = data
        self.data_sets: List[DataSet] = [
            _
            for _ in sorted(data_sets, key=lambda _: _.get_label())
            if _ != data
            and data.get_num_points(masked=None) == _.get_num_points(masked=None)
            and allclose(
                data.get_frequencies(masked=None), _.get_frequencies(masked=None)
            )
        ]
        self.data_labels: List[str] = list(map(lambda _: _.get_label(), self.data_sets))
        self.fits: List[FitResult] = fits
        self.fit_labels: List[str] = format_fit_labels(fits)
        self.preview_data: DataSet = DataSet.from_dict(data.to_dict())
        self.callback: Callable = callback
        self.create_window()
        self.register_keybindings()
        self.editing_circuit: bool = False
        self.select_option(self.radio_buttons, self.options[0])

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
        # Previous fit/data set
        for kb in STATE.config.keybindings:
            if kb.action is Action.PREVIOUS_SECONDARY_RESULT:
                break
        else:
            kb = Keybinding(
                key=dpg.mvKey_Prior,
                mod_alt=True,
                mod_ctrl=False,
                mod_shift=False,
                action=Action.PREVIOUS_SECONDARY_RESULT,
            )
        callbacks[kb] = lambda: self.cycle_results(step=-1)
        # Next fit/data set
        for kb in STATE.config.keybindings:
            if kb.action is Action.NEXT_SECONDARY_RESULT:
                break
        else:
            kb = Keybinding(
                key=dpg.mvKey_Next,
                mod_alt=True,
                mod_ctrl=False,
                mod_shift=False,
                action=Action.NEXT_SECONDARY_RESULT,
            )
        callbacks[kb] = lambda: self.cycle_results(step=1)
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

    def create_window(self):
        self.options: List[str] = [
            "Constant:",
            " Circuit:",
            "     Fit:",
            "Data set:",
        ]
        self.circuit_editor_window: int = -1
        x: int
        y: int
        w: int
        h: int
        x, y, w, h = calculate_window_position_dimensions()
        self.window: int = dpg.generate_uuid()
        with dpg.window(
            label="Subtract impedance",
            modal=True,
            pos=(
                x,
                y,
            ),
            width=w,
            height=h,
            tag=self.window,
            on_close=self.close,
        ):
            self.preview_window: int = dpg.generate_uuid()
            with dpg.child_window(border=False, tag=self.preview_window):
                self.create_preview_window()
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

    def create_preview_window(self):
        with dpg.child_window(
            width=-1,
            height=104,
        ):
            self.radio_buttons: int = dpg.generate_uuid()
            with dpg.group(horizontal=True):
                dpg.add_radio_button(
                    items=self.options,
                    default_value=self.options[0],
                    callback=self.select_option,
                    tag=self.radio_buttons,
                )
                with dpg.group():
                    self.constant_group: int = dpg.generate_uuid()
                    with dpg.group(horizontal=True, tag=self.constant_group):
                        dpg.add_text("Re(Z) = ")
                        self.constant_real: int = dpg.generate_uuid()
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
                        self.constant_imag: int = dpg.generate_uuid()
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
                    self.circuit_group: int = dpg.generate_uuid()
                    with dpg.group(horizontal=True, tag=self.circuit_group):
                        self.circuit_cdc: int = dpg.generate_uuid()
                        dpg.add_input_text(
                            hint="Input CDC",
                            on_enter=True,
                            width=361,
                            tag=self.circuit_cdc,
                            callback=self.update_preview,
                        )
                        self.circuit_editor_button: int = dpg.generate_uuid()
                        dpg.add_button(
                            label="Edit",
                            callback=self.edit_circuit,
                            tag=self.circuit_editor_button,
                        )
                        attach_tooltip(tooltips.general.open_circuit_editor)
                    self.fit_group: int = dpg.generate_uuid()
                    with dpg.group(horizontal=True, tag=self.fit_group):
                        self.fit_combo: int = dpg.generate_uuid()
                        dpg.add_combo(
                            items=self.fit_labels,
                            default_value=self.fit_labels[0] if self.fit_labels else "",
                            width=405,
                            tag=self.fit_combo,
                            callback=self.update_preview,
                        )
                    self.spectrum_group: int = dpg.generate_uuid()
                    with dpg.group(horizontal=True, tag=self.spectrum_group):
                        self.spectrum_combo: int = dpg.generate_uuid()
                        dpg.add_combo(
                            items=self.data_labels,
                            default_value=self.data_labels[0]
                            if self.data_labels
                            else "",
                            width=405,
                            tag=self.spectrum_combo,
                            callback=self.update_preview,
                        )
        self.create_plots()
        dpg.add_button(
            label="Accept".ljust(12),
            callback=self.accept,
        )

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
        self.plot_tab_bar: int = dpg.generate_uuid()
        with dpg.tab_bar(tag=self.plot_tab_bar):
            self.create_nyquist_plot(settings)
            self.create_magnitude_plot(settings)
            self.create_phase_plot(settings)
        pad_tab_labels(self.plot_tab_bar)

    def create_nyquist_plot(self, settings: List[dict]):
        with dpg.tab(label="Nyquist"):
            self.nyquist_plot: Nyquist = Nyquist(width=-1, height=-24)
            for kwargs in settings:
                self.nyquist_plot.plot(
                    real=array([]),
                    imaginary=array([]),
                    **kwargs,
                )

    def create_magnitude_plot(self, settings: List[dict]):
        with dpg.tab(label="Bode - magnitude"):
            self.magnitude_plot: BodeMagnitude = BodeMagnitude(width=-1, height=-24)
            for kwargs in settings:
                self.magnitude_plot.plot(
                    frequency=array([]),
                    magnitude=array([]),
                    **kwargs,
                )

    def create_phase_plot(self, settings: List[dict]):
        with dpg.tab(label="Bode - phase"):
            self.phase_plot: BodePhase = BodePhase(width=-1, height=-24)
            for kwargs in settings:
                self.phase_plot.plot(
                    frequency=array([]),
                    phase=array([]),
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
        self.circuit_editor.keybinding_handler.delete()
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
        data.set_label(f"{self.preview_data.get_label()} - subtracted")
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
        if index == 0:
            enable_group(self.constant_group)
            disable_group(self.circuit_group)
            disable_group(self.fit_group)
            disable_group(self.spectrum_group)
        elif index == 1:
            disable_group(self.constant_group)
            enable_group(self.circuit_group)
            disable_group(self.fit_group)
            disable_group(self.spectrum_group)
        elif index == 2:
            disable_group(self.constant_group)
            disable_group(self.circuit_group)
            enable_group(self.fit_group)
            disable_group(self.spectrum_group)
        elif index == 3:
            disable_group(self.constant_group)
            disable_group(self.circuit_group)
            disable_group(self.fit_group)
            enable_group(self.spectrum_group)
        else:
            raise Exception(f"Unsupported option: {value}")
        self.update_preview()

    def update_preview(self):
        index: int = self.options.index(dpg.get_value(self.radio_buttons))
        f: ndarray = self.data.get_frequencies(masked=None)
        Z: ndarray = self.data.get_impedances(masked=None)
        if index == 0:
            Z_const: complex = complex(
                dpg.get_value(self.constant_real),
                -dpg.get_value(self.constant_imag),
            )
            Z = Z - Z_const
        elif index == 1:
            cdc: str = dpg.get_value(self.circuit_cdc)
            circuit: Optional[Circuit] = dpg.get_item_user_data(self.circuit_cdc)
            if circuit is None or circuit.to_string() != cdc:
                try:
                    circuit, _ = process_cdc(cdc)
                except Exception:
                    return
            if circuit is None:
                return
            Z = Z - circuit.get_impedances(f)
        elif index == 2:
            if len(self.fits) > 0:
                fit: FitResult
                fit = self.fits[self.fit_labels.index(dpg.get_value(self.fit_combo))]
                Z = Z - fit.circuit.get_impedances(f)
        elif index == 3:
            if len(self.data_sets) > 0:
                spectrum: DataSet
                spectrum = self.data_sets[
                    self.data_labels.index(dpg.get_value(self.spectrum_combo))
                ]
                Z = Z - spectrum.get_impedances(masked=None)
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
            original.get_nyquist_data(masked=None),
            original.get_nyquist_data(masked=None),
            preview.get_nyquist_data(masked=None),
            preview.get_nyquist_data(masked=None),
        ]
        i: int
        real: ndarray
        imag: ndarray
        for i, (real, imag) in enumerate(data):
            self.nyquist_plot.update(
                index=i,
                real=real,
                imaginary=imag,
            )
        self.nyquist_plot.queue_limits_adjustment()

    def update_magnitude_plot(self, original: DataSet, preview: DataSet):
        data: List[Tuple[ndarray, ndarray, ndarray]] = [
            original.get_bode_data(masked=None),
            original.get_bode_data(masked=None),
            preview.get_bode_data(masked=None),
            preview.get_bode_data(masked=None),
        ]
        i: int
        freq: ndarray
        mag: ndarray
        for i, (freq, mag, _) in enumerate(data):
            self.magnitude_plot.update(
                index=i,
                frequency=freq,
                magnitude=mag,
            )
        self.magnitude_plot.queue_limits_adjustment()

    def update_phase_plot(self, original: DataSet, preview: DataSet):
        data: List[Tuple[ndarray, ndarray, ndarray]] = [
            original.get_bode_data(masked=None),
            original.get_bode_data(masked=None),
            preview.get_bode_data(masked=None),
            preview.get_bode_data(masked=None),
        ]
        i: int
        freq: ndarray
        phase: ndarray
        for i, (freq, _, phase) in enumerate(data):
            self.phase_plot.update(
                index=i,
                frequency=freq,
                phase=phase,
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
        self.circuit_editor.show(circuit)

    def accept_circuit(self, circuit: Optional[Circuit]):
        self.circuit_editor.hide()
        dpg.show_item(self.preview_window)
        self.update_cdc(circuit)
        self.keybinding_handler.unblock()

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

    def cycle_results(self, step: int):
        index: int
        if dpg.is_item_enabled(self.fit_combo):
            index = self.fit_labels.index(dpg.get_value(self.fit_combo)) + step
            dpg.set_value(self.fit_combo, self.fit_labels[index % len(self.fit_labels)])
            self.update_preview()
        elif dpg.is_item_enabled(self.spectrum_combo):
            index = self.data_labels.index(dpg.get_value(self.spectrum_combo)) + step
            dpg.set_value(
                self.spectrum_combo, self.data_labels[index % len(self.data_labels)]
            )
            self.update_preview()
        else:
            return

    def cycle_plot_tab(self, step: int):
        tabs: List[int] = dpg.get_item_children(self.plot_tab_bar, slot=1)
        index: int = tabs.index(dpg.get_value(self.plot_tab_bar)) + step
        dpg.set_value(self.plot_tab_bar, tabs[index % len(tabs)])

    def has_active_input(self) -> bool:
        return (
            dpg.is_item_active(self.constant_real)
            or dpg.is_item_active(self.constant_imag)
            or dpg.is_item_active(self.circuit_cdc)
        )
