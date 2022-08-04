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

from typing import Callable, List
from numpy import array, ndarray
import dearpygui.dearpygui as dpg
from deareis.gui.plots import Nyquist
import deareis.themes as themes
from deareis.utility import calculate_window_position_dimensions
from deareis.signals import Signal
import deareis.signals as signals
from deareis.data import DataSet
from deareis.tooltips import attach_tooltip
import deareis.tooltips as tooltips
from deareis.keybindings import (
    is_alt_down,
    is_control_down,
)


class CopyMask:
    def __init__(self, data: DataSet, data_sets: List[DataSet], callback: Callable):
        assert type(data) is DataSet, data
        assert type(data_sets) is list and all(
            map(lambda _: type(_) is DataSet, data_sets)
        ), data_sets
        self.data: DataSet = data
        self.preview_data: DataSet = DataSet.from_dict(data.to_dict())
        self.data_sets: List[DataSet] = [
            _ for _ in sorted(data_sets, key=lambda _: _.get_label()) if _ != data
        ]
        self.labels: List[str] = list(map(lambda _: _.get_label(), self.data_sets))
        self.callback: Callable = callback
        x: int
        y: int
        w: int
        h: int
        x, y, w, h = calculate_window_position_dimensions()
        self.window: int = dpg.generate_uuid()
        with dpg.window(
            label="Copy mask",
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
            with dpg.group(horizontal=True):
                dpg.add_text("Source")
                attach_tooltip(tooltips.data_sets.copy_mask_source)
                self.combo: int = dpg.generate_uuid()
                dpg.add_combo(
                    items=self.labels,
                    default_value=self.labels[0],
                    width=-1,
                    tag=self.combo,
                    callback=lambda s, a, u: self.select_source(a),
                )
            self.nyquist_plot: Nyquist = Nyquist(width=-1, height=-24)
            self.nyquist_plot.plot(
                real=array([]),
                imaginary=array([]),
                label="Excluded",
                theme=themes.nyquist.data,
            )
            self.nyquist_plot.plot(
                real=array([]),
                imaginary=array([]),
                label="Included",
                theme=themes.bode.phase_data,
                show_label=False,
            )
            self.nyquist_plot.plot(
                real=array([]),
                imaginary=array([]),
                label="Included",
                line=True,
                theme=themes.bode.phase_data,
            )
            dpg.add_button(label="Accept", callback=self.accept)
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
            dpg.add_key_release_handler(
                key=dpg.mvKey_Prior,
                callback=lambda: self.cycle_source(-1),
            )
            dpg.add_key_release_handler(
                key=dpg.mvKey_Next,
                callback=lambda: self.cycle_source(1),
            )
        self.select_source(self.labels[0])
        self.nyquist_plot.queue_limits_adjustment()

    def cycle_source(self, step: int):
        assert type(step) is int, step
        index: int = self.labels.index(dpg.get_value(self.combo)) + step
        label: str = self.labels[index % len(self.labels)]
        dpg.set_value(self.combo, label)
        self.select_source(label)

    def select_source(self, label: str):
        assert type(label) is str, label
        self.preview_data.set_mask(self.data.get_mask())
        self.preview_data.set_mask(self.data_sets[self.labels.index(label)].get_mask())
        self.update_preview()

    def update_preview(self):
        real: ndarray
        imag: ndarray
        real, imag = self.preview_data.get_nyquist_data(masked=True)
        self.nyquist_plot.update(
            index=0,
            real=real,
            imaginary=imag,
        )
        real, imag = self.preview_data.get_nyquist_data(masked=False)
        self.nyquist_plot.update(
            index=1,
            real=real,
            imaginary=imag,
        )
        self.nyquist_plot.update(
            index=2,
            real=real,
            imaginary=imag,
        )

    def close(self):
        dpg.hide_item(self.window)
        dpg.delete_item(self.window)
        dpg.delete_item(self.key_handler)
        signals.emit(Signal.UNBLOCK_KEYBINDINGS)

    def accept(self, keybinding: bool = False):
        if keybinding is True and not (
            is_control_down()
            if dpg.get_platform() == dpg.mvPlatform_Windows
            else is_alt_down()
        ):
            return
        self.callback(
            self.data_sets[self.labels.index(dpg.get_value(self.combo))].get_mask(),
        )
        self.close()
