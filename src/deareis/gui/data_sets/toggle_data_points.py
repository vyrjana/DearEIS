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

from typing import Callable, Dict, List
from numpy import array, ndarray
import dearpygui.dearpygui as dpg
from deareis.gui.plots import Nyquist
import deareis.themes as themes
from deareis.data import DataSet
from deareis.utility import (
    align_numbers,
    calculate_window_position_dimensions,
    format_number,
)
from deareis.signals import Signal
import deareis.signals as signals
from deareis.tooltips import attach_tooltip
from deareis.keybindings import (
    is_alt_down,
    is_control_down,
)


class ToggleDataPoints:
    def __init__(self, data: DataSet, callback: Callable):
        assert type(data) is DataSet
        self.data: DataSet = data
        self.callback: Callable = callback
        self.preview_data: DataSet = DataSet.from_dict(data.to_dict())
        self.original_mask: Dict[int, bool] = data.get_mask()
        self.final_mask: Dict[int, bool] = {
            i: state for i, state in self.original_mask.items()
        }
        self.labels: List[str] = []
        indices: List[str] = align_numbers(
            list(map(str, range(1, data.get_num_points(masked=None) + 1)))
        )
        freq: List[str] = list(
            map(
                lambda _: _.ljust(9),
                align_numbers(
                    list(
                        map(
                            lambda _: format_number(_, 1, 9),
                            data.get_frequency(masked=None),
                        )
                    )
                ),
            )
        )
        Z: ndarray = data.get_impedance(masked=None)
        real: List[str] = list(
            map(
                lambda _: _.ljust(10),
                align_numbers(list(map(lambda _: format_number(_, 1, 10), Z.real))),
            )
        )
        imag: List[str] = list(
            map(
                lambda _: _.ljust(10),
                align_numbers(list(map(lambda _: format_number(_, 1, 10), -Z.imag))),
            )
        )
        i: str
        f: str
        re: str
        im: str
        for (i, f, re, im) in zip(
            indices,
            freq,
            real,
            imag,
        ):
            self.labels.append(
                f"{i}: " + f"f = {f} | " + f"Z'= {re} | " + f'-Z" = {im}'
            )

        x: int
        y: int
        w: int
        h: int
        x, y, w, h = calculate_window_position_dimensions()
        self.window: int = dpg.generate_uuid()
        with dpg.window(
            label="Toggle points",
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
                dpg.add_text("From")
                self.from_combo: int = dpg.generate_uuid()
                dpg.add_combo(
                    default_value=self.labels[0],
                    width=-1,
                    callback=self.update_items,
                    tag=self.from_combo,
                )
            with dpg.group(horizontal=True):
                dpg.add_text("  To")
                self.to_combo: int = dpg.generate_uuid()
                dpg.add_combo(
                    default_value=self.labels[-1],
                    width=-1,
                    callback=self.update_items,
                    tag=self.to_combo,
                )
            with dpg.group(horizontal=True):
                dpg.add_text("  ?")
                attach_tooltip(
                    """Points can also be chosen by drawing rectangle while holding down the middle-mouse button.""".strip()
                )
                dpg.add_button(
                    label="Exclude all",
                    callback=self.exclude,
                )
                dpg.add_button(
                    label="Include all",
                    callback=self.include,
                )
            self.nyquist_plot: Nyquist = Nyquist(width=-1, height=-24)
            self.nyquist_plot.plot(
                real=array([]),
                imaginary=array([]),
                label="Excluded",
                theme=themes.nyquist.data,
            )
            real, imag = self.preview_data.get_nyquist_data(masked=False)
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
            dpg.configure_item(self.nyquist_plot._plot, query=True)
            dpg.add_button(
                label="Accept",
                callback=self.accept,
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
        self.update_items(self.from_combo, self.labels[0])
        self.update_items(self.to_combo, self.labels[-1])
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
        self.nyquist_plot.queue_limits_adjustment()

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
        if dpg.is_plot_queried(self.nyquist_plot._plot):
            sx, ex, sy, ey = dpg.get_plot_query_area(self.nyquist_plot._plot)
            for i, Z in enumerate(self.data.get_impedance(masked=None)):
                if Z.real >= sx and Z.real <= ex and -Z.imag >= sy and -Z.imag <= ey:
                    self.final_mask[i] = not self.final_mask[i]
        self.callback(self.final_mask)
        self.close()

    def exclude(self):
        self.final_mask = {i: True for i in self.original_mask}
        self.preview_data.set_mask(self.final_mask)
        self.update_preview()

    def include(self):
        self.final_mask = {i: False for i in self.original_mask}
        self.preview_data.set_mask(self.final_mask)
        self.update_preview()

    def update_items(self, sender: int, label: str):
        index: int = self.labels.index(label)
        receiver: int
        items: List[str]
        if sender == self.from_combo:
            receiver = self.to_combo
            items = self.labels[index + 1 :]
        elif sender == self.to_combo:
            receiver = self.from_combo
            items = self.labels[:index]
        dpg.configure_item(receiver, items=items)
        start: int = self.labels.index(dpg.get_value(self.from_combo))
        end: int = self.labels.index(dpg.get_value(self.to_combo))
        assert end > start
        self.final_mask = {}
        for i, state in self.original_mask.items():
            if i >= start and i <= end:
                self.final_mask[i] = not state
            else:
                self.final_mask[i] = state
        self.preview_data.set_mask(self.final_mask)
        self.update_preview()
