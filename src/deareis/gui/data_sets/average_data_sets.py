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

from typing import Callable, List, Optional
from numpy import ndarray
import dearpygui.dearpygui as dpg
from deareis.gui.plots import Nyquist
from deareis.tooltips import attach_tooltip
from deareis.themes import PLOT_MARKERS, VIBRANT_COLORS, create_plot_series_theme
import deareis.themes as themes
from deareis.utility import calculate_window_position_dimensions
from deareis.signals import Signal
import deareis.signals as signals
from deareis.data import DataSet
from deareis.keybindings import (
    is_alt_down,
    is_control_down,
)


class AverageDataSets:
    def __init__(self, data_sets: List[DataSet], callback: Callable):
        assert type(data_sets) is list and all(
            map(lambda _: type(_) is DataSet, data_sets)
        )
        self.data_sets: List[DataSet] = data_sets
        self.callback: Callable = callback
        self.plot_themes: List[int] = list(
            map(
                self.get_plot_theme,
                range(0, 12),
            )
        )
        self.final_data: Optional[DataSet] = None
        x: int
        y: int
        w: int
        h: int
        x, y, w, h = calculate_window_position_dimensions()
        self.window: int = dpg.generate_uuid()
        with dpg.window(
            label="Average of multiple data sets",
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
                with dpg.group():
                    with dpg.child_window(border=False, width=300, height=-24):
                        with dpg.group(horizontal=True):
                            dpg.add_text("Label")
                            self.label_input: int = dpg.generate_uuid()
                            self.final_data_series: int = -1
                            dpg.add_input_text(
                                hint="REQUIRED",
                                default_value="Average",
                                width=-1,
                                tag=self.label_input,
                                callback=lambda s, a, u: self.update_label(a),
                            )
                        self.dataset_table: int = dpg.generate_uuid()
                        with dpg.table(
                            borders_outerV=True,
                            borders_outerH=True,
                            borders_innerV=True,
                            borders_innerH=True,
                            scrollY=True,
                            freeze_rows=1,
                            width=-1,
                            height=-1,
                            tag=self.dataset_table,
                        ):
                            dpg.add_table_column(label="", width_fixed=True)
                            dpg.add_table_column(label="Label", width_fixed=True)
                            data: DataSet
                            for data in self.data_sets:
                                with dpg.table_row():
                                    dpg.add_checkbox(
                                        callback=lambda: self.update_preview([])
                                    )
                                    label: str = data.get_label()
                                    dpg.add_text(label)
                                    attach_tooltip(label)
                    dpg.add_button(label="Accept", callback=self.accept)
                self.nyquist_plot: Nyquist = Nyquist(
                    width=-1,
                    height=-12,
                    legend_horizontal=False,
                    legend_outside=False,
                    legend_location=dpg.mvPlot_Location_NorthEast,
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
        self.update_preview([])

    def close(self):
        dpg.hide_item(self.window)
        dpg.delete_item(self.window)
        dpg.delete_item(self.key_handler)
        signals.emit(Signal.UNBLOCK_KEYBINDINGS)

    def accept(self, keybinding: bool = False):
        if self.final_data is None:
            return
        if keybinding is True and not (
            is_control_down()
            if dpg.get_platform() == dpg.mvPlatform_Windows
            else is_alt_down()
        ):
            return
        label: str = dpg.get_value(self.label_input).strip()
        if label == "":
            return
        self.final_data.set_label(label)
        self.callback(self.final_data)
        self.close()

    def get_selection(self) -> List[DataSet]:
        data_sets: List[DataSet] = []
        i: int
        row: int
        for i, row in enumerate(dpg.get_item_children(self.dataset_table, slot=1)):
            column: int
            for column in dpg.get_item_children(row, slot=1):
                assert dpg.get_item_type(column).endswith("Checkbox")
                if dpg.get_value(column) is True:
                    data_sets.append(self.data_sets[i])
                break
        return data_sets

    def get_plot_theme(self, index: int) -> int:
        assert type(index) is int, index
        return create_plot_series_theme(
            VIBRANT_COLORS[index % len(VIBRANT_COLORS)],
            list(PLOT_MARKERS.values())[index % len(PLOT_MARKERS)],
        )

    def update_preview(self, data_sets: List[DataSet]):
        assert type(data_sets) is list and all(
            map(lambda _: type(_) is DataSet, data_sets)
        ), data_sets
        from_empty: bool = False
        if len(self.nyquist_plot.get_series()) == 0:
            from_empty = True
        self.nyquist_plot.clear()
        selection: List[DataSet] = self.get_selection()
        i: int
        data: DataSet
        real: ndarray
        imag: ndarray
        for i, data in enumerate(selection):
            real, imag = data.get_nyquist_data(masked=None)
            self.nyquist_plot.plot(
                real=real,
                imaginary=imag,
                label=data.get_label(),
                line=False,
                theme=self.plot_themes[i % 12],
            )
        self.final_data_series = -1
        if len(selection) > 1:
            try:
                self.final_data = DataSet.average(
                    selection,
                    label=dpg.get_value(self.label_input),
                )
                assert self.final_data is not None
                real, imag = self.final_data.get_nyquist_data(masked=None)
                self.final_data_series = self.nyquist_plot.plot(
                    real=real,
                    imaginary=imag,
                    label=self.final_data.get_label(),
                    line=True,
                    theme=themes.nyquist.data,
                )
            except AssertionError:
                self.final_data = None
        if from_empty:
            self.nyquist_plot.queue_limits_adjustment()

    def update_label(self, label: str):
        assert type(label) is str, label
        if self.final_data_series < 0 or not dpg.does_item_exist(
            self.final_data_series
        ):
            return
        # TODO: Apply a theme that attracts attention when no label is provided
        if label == "":
            pass
        else:
            pass
        dpg.set_item_label(self.final_data_series, label)
