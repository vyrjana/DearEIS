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

from typing import List, Optional
import dearpygui.dearpygui as dpg
from deareis.typing.helpers import Tag


class Plot:
    def __init__(self):
        self._plot: Tag = dpg.generate_uuid()
        self._series: List[dict] = []
        self._item_handler: Tag = dpg.generate_uuid()
        with dpg.item_handler_registry(tag=self._item_handler):
            dpg.add_item_visible_handler(callback=self._visibility_handler)
        self._is_limits_adjustment_queued: bool = False

    def _visibility_handler(self, sender, app):
        if not self._is_limits_adjustment_queued:
            return
        elif not dpg.does_item_exist(self._plot):
            return
        dpg.split_frame()
        self.adjust_limits()
        self._is_limits_adjustment_queued = False

    @classmethod
    def duplicate(Class, original: "Plot", *args, **kwargs) -> "Plot":
        raise Exception("Method has not been implemented!")

    def copy_limits(self, other: "Plot"):
        raise Exception("Method has not been implemented!")

    def show(self):
        dpg.show_item(self._plot)

    def hide(self):
        dpg.hide_item(self._plot)

    def show_series(self, index: int):
        i: int
        if hasattr(self, "_y_axis"):
            series: int
            for i, series in enumerate(dpg.get_item_children(self._y_axis, slot=1)):
                if i == index:
                    dpg.show_item(series)
                    break
        elif hasattr(self, "_y_axis_1") and hasattr(self, "_y_axis_2"):
            series_1: int
            series_2: int
            for i, (series_1, series_2) in enumerate(
                zip(
                    dpg.get_item_children(self._y_axis_1, slot=1),
                    dpg.get_item_children(self._y_axis_2, slot=1),
                )
            ):
                if i == index:
                    dpg.show_item(series_1)
                    dpg.show_item(series_2)
                    break

    def hide_series(self, index: int):
        i: int
        if hasattr(self, "_y_axis"):
            series: int
            for i, series in enumerate(dpg.get_item_children(self._y_axis, slot=1)):
                if i == index:
                    dpg.hide_item(series)
                    break
        elif hasattr(self, "_y_axis_1") and hasattr(self, "_y_axis_2"):
            series_1: int
            series_2: int
            for i, (series_1, series_2) in enumerate(
                zip(
                    dpg.get_item_children(self._y_axis_1, slot=1),
                    dpg.get_item_children(self._y_axis_2, slot=1),
                )
            ):
                if i == index:
                    dpg.hide_item(series_1)
                    dpg.hide_item(series_2)
                    break

    def delete(self):
        dpg.delete_item(self._item_handler)
        dpg.delete_item(self._plot)

    def set_title(self, title: Optional[str]):
        dpg.set_item_label(self._plot, title)

    def are_limits_adjusted(self) -> bool:
        return not self._is_limits_adjustment_queued

    def queue_limits_adjustment(self):
        self._is_limits_adjustment_queued = True

    def limits_adjusted(self):
        self._is_limits_adjustment_queued = False

    def resize(self, width: int = -1, height: int = -1):
        assert type(width) is int, width
        assert type(height) is int, height
        dpg.configure_item(self._plot, width=width, height=height)

    def get_series(self) -> List[dict]:
        return self._series.copy()

    def is_visible(self) -> bool:
        return dpg.is_item_visible(self._plot)

    def clear(self, *args, **kwargs):
        raise Exception("'clear' method has not been implemented!")

    def plot(self, *args, **kwargs):
        raise Exception("'plot' method has not been implemented!")

    def adjust_limits(self, *args, **kwargs):
        raise Exception("'adjust_limits' method has not been implemented!")
