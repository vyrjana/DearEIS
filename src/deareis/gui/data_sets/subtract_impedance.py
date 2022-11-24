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

from pyimpspec import (
    Circuit,
    ParsingError,
)
from typing import (
    Callable,
    List,
    Optional,
)
from numpy import (
    allclose,
    array,
    ndarray,
)
import pyimpspec
import dearpygui.dearpygui as dpg
from deareis.gui.plots import Nyquist
import deareis.themes as themes
from deareis.utility import calculate_window_position_dimensions
from deareis.tooltips import attach_tooltip
import deareis.tooltips as tooltips
from deareis.gui.circuit_editor import CircuitEditor
from deareis.signals import Signal
import deareis.signals as signals
from deareis.data import (
    DataSet,
    FitResult,
)
from deareis.keybindings import (
    is_alt_down,
    is_control_down,
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
            and allclose(data.get_frequency(masked=None), _.get_frequency(masked=None))
        ]
        self.data_labels: List[str] = list(map(lambda _: _.get_label(), self.data_sets))
        self.fits: List[FitResult] = fits
        self.fit_labels: List[str] = format_fit_labels(fits)
        self.preview_data: DataSet = DataSet.from_dict(data.to_dict())
        self.callback: Callable = callback
        self.options: List[str] = [
            "Constant:",
            " Circuit:",
            "     Fit:",
            "Spectrum:",
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
                                dpg.add_text("Z' = ")
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
                                dpg.add_text('-Z" = ')
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
                                    width=314,
                                    tag=self.circuit_cdc,
                                    callback=self.update_preview,
                                )
                                dpg.add_button(
                                    label="Edit",
                                    callback=self.edit_circuit,
                                )
                                attach_tooltip(tooltips.general.open_circuit_editor)
                            self.fit_group: int = dpg.generate_uuid()
                            with dpg.group(horizontal=True, tag=self.fit_group):
                                self.fit_combo: int = dpg.generate_uuid()
                                dpg.add_combo(
                                    items=self.fit_labels,
                                    default_value=self.fit_labels[0]
                                    if self.fit_labels
                                    else "",
                                    width=358,
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
                                    width=358,
                                    tag=self.spectrum_combo,
                                    callback=self.update_preview,
                                )
                self.nyquist_plot: Nyquist = Nyquist(width=-1, height=-24)
                self.nyquist_plot.plot(
                    real=array([]),
                    imaginary=array([]),
                    label="Before",
                    theme=themes.nyquist.data,
                    show_label=False,
                )
                self.nyquist_plot.plot(
                    real=array([]),
                    imaginary=array([]),
                    label="Before",
                    line=True,
                    theme=themes.nyquist.data,
                )
                self.nyquist_plot.plot(
                    real=array([]),
                    imaginary=array([]),
                    label="After",
                    theme=themes.bode.phase_data,
                    show_label=False,
                )
                self.nyquist_plot.plot(
                    real=array([]),
                    imaginary=array([]),
                    label="After",
                    line=True,
                    theme=themes.bode.phase_data,
                )
                dpg.add_button(
                    label="Accept",
                    callback=self.accept,
                )
            self.circuit_editor_window = dpg.generate_uuid()
            with dpg.child_window(
                border=False,
                show=False,
                tag=self.circuit_editor_window,
            ):
                self.circuit_editor: CircuitEditor = CircuitEditor(
                    window=self.circuit_editor_window,
                    callback=self.accept_circuit,
                )
        self.key_handler: int = dpg.generate_uuid()
        with dpg.handler_registry(tag=self.key_handler):
            dpg.add_key_release_handler(
                key=dpg.mvKey_Escape,
                callback=self.close,
            )
            dpg.add_key_release_handler(
                key=dpg.mvKey_Return,
                callback=lambda: self.accept(keybinding=True),
            )
        self.select_option(self.radio_buttons, self.options[0])

    def close(self):
        if not dpg.is_item_visible(self.constant_real):
            return
        self.circuit_editor.hide()
        dpg.hide_item(self.window)
        dpg.delete_item(self.window)
        dpg.delete_item(self.key_handler)
        signals.emit(Signal.UNBLOCK_KEYBINDINGS)

    def accept(self, keybinding: bool = False):
        if not dpg.is_item_visible(self.constant_real):
            return
        elif (
            self.circuit_editor_window > 0
            and dpg.does_item_exist(self.circuit_editor_window)
            and dpg.is_item_shown(self.circuit_editor_window)
        ):
            return
        elif keybinding is True and not (
            is_control_down()
            if dpg.get_platform() == dpg.mvPlatform_Windows
            else is_alt_down()
        ):
            return
        self.close()
        self.callback(DataSet.from_dict(self.preview_data.to_dict()))

    def select_option(self, sender: int, value: str):
        item_type: str

        def disable_group(group: int):
            for item in dpg.get_item_children(group, slot=1):
                item_type = dpg.get_item_type(item)
                if item_type.endswith("mvText") or item_type.endswith("mvTooltip"):
                    continue
                dpg.disable_item(item)

        def enable_group(group: int):
            for item in dpg.get_item_children(group, slot=1):
                item_type = dpg.get_item_type(item)
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
        f: ndarray = self.data.get_frequency(masked=None)
        Z: ndarray = self.data.get_impedance(masked=None)
        if index == 0:
            Z_const: complex = complex(
                dpg.get_value(self.constant_real),
                -dpg.get_value(self.constant_imag),
            )
            Z = Z - Z_const
        elif index == 1:
            try:
                circuit: Circuit = pyimpspec.parse_cdc(dpg.get_value(self.circuit_cdc))
            except Exception:
                return
            Z = Z - circuit.impedances(f)
        elif index == 2:
            if len(self.fits) > 0:
                fit: FitResult
                fit = self.fits[self.fit_labels.index(dpg.get_value(self.fit_combo))]
                Z = Z - fit.circuit.impedances(f)
        elif index == 3:
            if len(self.data_sets) > 0:
                spectrum: DataSet
                spectrum = self.data_sets[
                    self.data_labels.index(dpg.get_value(self.spectrum_combo))
                ]
                Z = Z - spectrum.get_impedance(masked=None)
        else:
            raise Exception("Unsupported option!")
        dictionary: dict = self.preview_data.to_dict()
        dictionary.update(
            {
                "real": list(Z.real),
                "imaginary": list(Z.imag),
            }
        )
        self.preview_data = DataSet.from_dict(dictionary)
        self.update_plot()

    def update_plot(self):
        real: ndarray
        imag: ndarray
        real, imag = self.data.get_nyquist_data(masked=None)
        self.nyquist_plot.update(
            index=0,
            real=real,
            imaginary=imag,
        )
        self.nyquist_plot.update(
            index=1,
            real=real,
            imaginary=imag,
        )
        real, imag = self.preview_data.get_nyquist_data(masked=None)
        self.nyquist_plot.update(
            index=2,
            real=real,
            imaginary=imag,
        )
        self.nyquist_plot.update(
            index=3,
            real=real,
            imaginary=imag,
        )
        self.nyquist_plot.queue_limits_adjustment()

    def edit_circuit(self):
        dpg.hide_item(self.preview_window)
        circuit: Optional[Circuit] = None
        try:
            circuit = pyimpspec.parse_cdc(dpg.get_value(self.circuit_cdc) or "[]")
        except ParsingError:
            pass
        self.circuit_editor.show(circuit)

    def accept_circuit(self, circuit: Optional[Circuit]):
        self.circuit_editor.hide()
        dpg.show_item(self.preview_window)
        self.update_cdc(circuit)

    def update_cdc(self, circuit: Optional[Circuit]):
        if circuit is not None:
            for element in circuit.get_elements():
                element.set_label("")
                for param in element.get_parameters():
                    element.set_fixed(param, True)
        assert dpg.does_item_exist(self.circuit_cdc)
        dpg.set_value(
            self.circuit_cdc,
            circuit.to_string(6) if circuit is not None else "",
        )
        dpg.show_item(self.preview_window)
        dpg.split_frame(delay=33)
        self.update_preview()
