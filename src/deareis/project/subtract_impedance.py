# Copyright 2022 DearEIS developers
# DearEIS is licensed under the GPLv3 or later (https://www.gnu.org/licenses/gpl-3.0.html).
# The licenses of DearEIS' dependencies and/or sources of portions of code are included in
# the LICENSES folder.

from pyimpspec import DataSet, Circuit
from typing import Callable, Dict, List, Optional
from numpy import array, ndarray
import pyimpspec
import dearpygui.dearpygui as dpg
from deareis.plot import NyquistPlot
import deareis.themes as themes
from deareis.utility import window_pos_dims, number_formatter
from deareis.project.circuit_editor import CircuitEditor

# TODO: Argument type assertions

# TODO: Add resize handler to check when the viewport is resized


class SubtractImpedance:
    def __init__(self, data: DataSet, datasets: List[DataSet], callback: Callable):
        assert type(data) is DataSet
        assert type(datasets) is list and all(
            map(lambda _: type(_) is DataSet, datasets)
        )
        assert callback is not None
        self.data: DataSet = data
        self.datasets: List[DataSet] = [
            _ for _ in sorted(datasets, key=lambda _: _.get_label()) if _ != data
        ]
        self.labels: List[str] = list(map(lambda _: _.get_label(), self.datasets))
        self.preview_data: DataSet = DataSet.from_dict(data.to_dict())
        self.callback: Callable = callback
        self.options: List[str] = ["Constant:", " Circuit:"]
        if len(datasets) > 0:
            self.options.append("Spectrum:")
        self.window: int = dpg.generate_uuid()
        self.preview_window: int = dpg.generate_uuid()
        self.circuit_editor_window: int = dpg.generate_uuid()
        self.circuit_editor: CircuitEditor = None
        self.radio_buttons: int = dpg.generate_uuid()
        self.constant_group: int = dpg.generate_uuid()
        self.constant_real: int = dpg.generate_uuid()
        self.constant_imag: int = dpg.generate_uuid()
        self.circuit_group: int = dpg.generate_uuid()
        self.circuit_cdc: int = dpg.generate_uuid()
        self.spectrum_group: int = dpg.generate_uuid()
        self.spectrum_combo: int = dpg.generate_uuid()
        self.nyquist_plot: NyquistPlot = None
        self.key_handler: int = dpg.generate_uuid()
        self._assemble()
        self._setup_keybindings()
        self.select_option(self.radio_buttons, self.options[0])

    def _setup_keybindings(self):
        with dpg.handler_registry(tag=self.key_handler):
            dpg.add_key_release_handler(
                key=dpg.mvKey_Escape,
                callback=self.close,
            )
            dpg.add_key_release_handler(
                key=dpg.mvKey_Return,
                callback=self.accept,
            )

    def _assemble(self):
        x: int
        y: int
        w: int
        h: int
        x, y, w, h = window_pos_dims()
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
            with dpg.child_window(border=False, tag=self.preview_window):
                with dpg.child_window(
                    width=-1, height=82 if len(self.datasets) > 0 else 80
                ):
                    with dpg.group(horizontal=True):
                        dpg.add_radio_button(
                            items=self.options,
                            default_value=self.options[0],
                            callback=self.select_option,
                            tag=self.radio_buttons,
                        )
                        with dpg.group():
                            with dpg.group(horizontal=True, tag=self.constant_group):
                                dpg.add_text("Z' = ")
                                dpg.add_input_float(
                                    label="ohm,",
                                    default_value=0.0,
                                    step=0.0,
                                    on_enter=True,
                                    width=100,
                                    tag=self.constant_real,
                                    callback=self.update_preview,
                                )
                                dpg.add_text('-Z" = ')
                                dpg.add_input_float(
                                    label="ohm",
                                    default_value=0.0,
                                    step=0.0,
                                    on_enter=True,
                                    width=100,
                                    tag=self.constant_imag,
                                    callback=self.update_preview,
                                )
                            with dpg.group(horizontal=True, tag=self.circuit_group):
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
                            if len(self.datasets) > 0:
                                with dpg.group(
                                    horizontal=True, tag=self.spectrum_group
                                ):
                                    dpg.add_combo(
                                        items=self.labels,
                                        default_value=self.labels[0],
                                        width=358,
                                        tag=self.spectrum_combo,
                                        callback=self.update_preview,
                                    )
                self.nyquist_plot = NyquistPlot(
                    dpg.add_plot(
                        equal_aspects=True,
                        width=-1,
                        height=-24,
                        anti_aliased=True,
                    )
                )
                dpg.add_button(
                    label="Accept",
                    callback=self.accept,
                )
            with dpg.child_window(
                border=False, show=False, tag=self.circuit_editor_window
            ):
                self.circuit_editor = CircuitEditor(
                    self.circuit_editor_window,
                    self.update_cdc,
                )

    def close(self):
        dpg.hide_item(self.window)
        dpg.delete_item(self.key_handler)

    def accept(self):
        if dpg.is_item_shown(self.circuit_editor_window):
            return
        dictionary: dict = self.preview_data.to_dict()
        assert "uuid" in dictionary
        del dictionary["uuid"]
        self.callback(self.data, DataSet.from_dict(dictionary))
        self.close()

    def select_option(self, sender: int, value: str):
        def disable_group(group: int):
            for item in dpg.get_item_children(group, slot=1):
                if dpg.get_item_type(item).endswith("mvText"):
                    continue
                dpg.disable_item(item)

        def enable_group(group: int):
            for item in dpg.get_item_children(group, slot=1):
                if dpg.get_item_type(item).endswith("mvText"):
                    continue
                dpg.enable_item(item)

        index: int = self.options.index(value)
        if index == 0:
            enable_group(self.constant_group)
            disable_group(self.circuit_group)
            disable_group(self.spectrum_group)
        elif index == 1:
            disable_group(self.constant_group)
            enable_group(self.circuit_group)
            disable_group(self.spectrum_group)
        elif index == 2:
            disable_group(self.constant_group)
            disable_group(self.circuit_group)
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
                dpg.get_value(self.constant_real), -dpg.get_value(self.constant_imag)
            )
            Z = Z - Z_const
        elif index == 1:
            try:
                circuit: Circuit = pyimpspec.string_to_circuit(
                    dpg.get_value(self.circuit_cdc)
                )
            except Exception as e:
                print(e)
                return
            Z = Z - circuit.impedances(f)
        elif index == 2:
            spectrum: DataSet
            spectrum = self.datasets[
                self.labels.index(dpg.get_value(self.spectrum_combo))
            ]
            Z = Z - spectrum.get_impedance(masked=None)
        else:
            raise Exception(f"Unsupported option!")
        self.preview_data._impedance = Z
        self.update_plot()

    def update_plot(self):
        self.nyquist_plot.clear_plot()
        self.nyquist_plot._plot(
            *self.data.get_nyquist_data(masked=None),
            "Before",
            False,
            True,
            themes.nyquist_data,
            -1,
            self.nyquist_plot.x_axis,
            self.nyquist_plot.y_axis,
        )
        self.nyquist_plot._plot(
            *self.preview_data.get_nyquist_data(masked=None),
            "After",
            False,
            True,
            themes.bode_phase_data,
            -1,
            self.nyquist_plot.x_axis,
            self.nyquist_plot.y_axis,
        )
        self.nyquist_plot.adjust_limits()

    def edit_circuit(self):
        dpg.hide_item(self.preview_window)
        dpg.show_item(self.circuit_editor_window)

    def update_cdc(self, circuit: Optional[Circuit]):
        if circuit is not None:
            for element in circuit.get_elements():
                element.set_label("")
                for param in element.get_parameters():
                    element.set_fixed(param, True)
        dpg.set_value(
            self.circuit_cdc, circuit.to_string(6) if circuit is not None else ""
        )
        dpg.show_item(self.preview_window)
        self.update_preview()
