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
    List,
    Tuple,
)
import dearpygui.dearpygui as dpg
import deareis.themes as themes
from deareis.gui.plots.base import Plot


class Image(Plot):
    def __init__(self, width: int = -1, height: int = -1, *args, **kwargs):
        assert type(width) is int, width
        assert type(height) is int, height
        super().__init__()
        with dpg.plot(
            anti_aliased=True,
            crosshairs=True,
            equal_aspects=True,
            no_mouse_pos=True,
            no_menus=True,
            width=width,
            height=height,
            tag=self._plot,
        ):
            self._x_axis: int = dpg.add_plot_axis(
                dpg.mvXAxis,
                label="",
                no_tick_labels=True,
                no_tick_marks=True,
                no_gridlines=True,
            )
            self._y_axis: int = dpg.add_plot_axis(
                dpg.mvYAxis,
                label="",
                no_tick_labels=True,
                no_tick_marks=True,
                no_gridlines=True,
            )
        dpg.bind_item_theme(self._plot, themes.plot)
        dpg.bind_item_handler_registry(self._plot, self._item_handler)

    def is_blank(self) -> bool:
        return len(dpg.get_item_children(self._y_axis, slot=1)) == 0

    def clear(self, *args, **kwargs):
        dpg.delete_item(self._y_axis, children_only=True)
        self._series.clear()

    def plot(self, *args, **kwargs) -> int:
        assert len(args) == 0, args
        texture: int = kwargs["texture"]
        bounds_min: Tuple[int, int] = kwargs["bounds_min"]
        bounds_max: Tuple[int, int] = kwargs["bounds_max"]
        assert type(texture) is int and texture > 0, texture
        assert type(bounds_min) is tuple and all(
            map(lambda _: type(_) is int, bounds_min)
        ), bounds_min
        assert type(bounds_max) is tuple and all(
            map(lambda _: type(_) is int, bounds_max)
        ), bounds_max
        self._series.append(kwargs)
        tag: int = dpg.add_image_series(
            texture,
            bounds_min,
            bounds_max,
            parent=self._y_axis,
        )
        return tag

    def adjust_limits(self):
        if not self.is_visible():
            self.queue_limits_adjustment()
            return
        elif self.are_limits_adjusted():
            return
        else:
            self.limits_adjusted()
        dpg.split_frame()
        dpg.fit_axis_data(self._x_axis)
        dpg.fit_axis_data(self._y_axis)

    def copy_limits(self, other: Plot):
        src: int
        dst: int
        for src, dst in zip(
            [
                other._x_axis,
                other._y_axis,
            ],
            [
                self._x_axis,
                self._y_axis,
            ],
        ):
            limits: List[float] = dpg.get_axis_limits(src)
            dpg.set_axis_limits(dst, *limits)
        dpg.split_frame()
        dpg.set_axis_limits_auto(self._x_axis)
        dpg.set_axis_limits_auto(self._y_axis)
