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
    Callable,
    List,
    Optional,
)
from numpy import (
    array,
    ceil,
    floor,
    log10 as log,
    ndarray,
)
import dearpygui.dearpygui as dpg
import deareis.themes as themes
from deareis.gui.plots.base import Plot


class DRT(Plot):
    def __init__(self, width: int = -1, height: int = -1, *args, **kwargs):
        assert type(width) is int, width
        assert type(height) is int, height
        super().__init__()
        with dpg.plot(
            anti_aliased=True,
            crosshairs=True,
            width=width,
            height=height,
            tag=self._plot,
        ):
            dpg.add_plot_legend(
                horizontal=kwargs.get("legend_horizontal", True),
                location=kwargs.get("legend_location", dpg.mvPlot_Location_North),
                outside=kwargs.get("legend_outside", True),
            )
            self._x_axis: int = dpg.add_plot_axis(
                dpg.mvXAxis,
                label="tau (s)",
                log_scale=True,
                no_gridlines=True,
            )
            self._y_axis: int = dpg.add_plot_axis(
                dpg.mvYAxis,
                label="gamma (ohm)",
                no_gridlines=True,
            )
        dpg.bind_item_theme(self._plot, themes.plot)
        dpg.bind_item_handler_registry(self._plot, self._item_handler)

    @classmethod
    def duplicate(Class, original: Plot, *args, **kwargs) -> Plot:
        copy: Plot = Class(*args, **kwargs)
        for kwargs in original.get_series():
            copy.plot(**kwargs)
        return copy

    def is_blank(self) -> bool:
        return len(dpg.get_item_children(self._y_axis, slot=1)) == 0

    def clear(self, *args, **kwargs):
        delete: bool = kwargs.get("delete", True)
        if delete:
            dpg.delete_item(self._y_axis, children_only=True)
            self._series.clear()
        else:
            i: int
            series: int
            for i, series in enumerate(dpg.get_item_children(self._y_axis, slot=1)):
                self._series[i]["tau"] = array([])
                self._series[i]["gamma"] = array([])
                dpg.set_value(series, [[], []])

    def delete_series(self, *args, **kwargs):
        index: int = kwargs.get("index", -1)
        from_index: int = kwargs.get("from_index", -1)
        i: int
        series: int
        if index >= 0:
            for i, series in enumerate(dpg.get_item_children(self._y_axis, slot=1)):
                if i != index:
                    continue
                dpg.delete_item(series)
                self._series.pop(i)
        elif from_index >= 0:
            for i, series in enumerate(dpg.get_item_children(self._y_axis, slot=1)):
                if i < from_index:
                    continue
                dpg.delete_item(series)
                self._series[i] = None
            while None in self._series:
                self._series.remove(None)
        else:
            raise Exception("Unsupported case!")

    def update(self, index: int, *args, **kwargs):
        assert type(index) is int and index >= 0, index
        assert len(self._series) > index, (
            index,
            len(self._series),
        )
        assert len(args) == 0, args
        tau: ndarray = kwargs["tau"]
        gamma: ndarray = kwargs["gamma"]
        assert type(tau) is ndarray, tau
        assert type(gamma) is ndarray, gamma
        assert tau.shape == gamma.shape, (
            tau.shape,
            gamma.shape,
        )
        i: int
        series: int
        for i, series in enumerate(dpg.get_item_children(self._y_axis, slot=1)):
            if i != index:
                continue
            dpg.set_value(series, [list(tau), list(gamma)])
            if "label" in kwargs:
                label: Optional[str] = kwargs.get("label")
                assert type(label) is str or label is None, label
                dpg.set_item_label(series, label)
            self._series[index].update(kwargs)
            break

    def plot(self, *args, **kwargs) -> int:
        assert len(args) == 0, args
        tau: ndarray = kwargs["tau"]
        gamma: Optional[ndarray] = kwargs.get(
            "gamma",
            kwargs.get(
                "imaginary",
                kwargs.get("mean"),
            ),
        )
        lower: Optional[ndarray] = kwargs.get("lower")
        upper: Optional[ndarray] = kwargs.get("upper")
        label: str = kwargs.get("label", "")
        line: bool = kwargs.get("line", False)
        theme: Optional[int] = kwargs.get("theme")
        show_label: bool = kwargs.get("show_label", True)
        assert type(tau) is ndarray, tau
        assert type(gamma) is ndarray or gamma is None, gamma
        assert type(lower) is ndarray or lower is None, lower
        assert type(upper) is ndarray or upper is None, upper
        assert type(label) is str, label
        assert type(line) is bool, line
        assert type(theme) is int or theme is None, theme
        assert type(show_label) is bool, show_label
        tag: int
        if gamma is not None:
            tag = dpg.add_line_series(
                x=list(tau),
                y=list(gamma),
                label=label if show_label else None,
                parent=self._y_axis,
            )
        elif lower is not None and upper is not None:
            tag = dpg.add_shade_series(
                x=list(tau),
                y1=list(lower),  # Lower bounds
                y2=list(upper),  # Upper bounds
                label=label if show_label else None,
                parent=self._y_axis,
            )
        else:
            raise Exception("No data to plot!")
        self._series.append(kwargs)
        if theme is not None:
            dpg.bind_item_theme(tag, theme)
        return tag

    def adjust_limits(self):
        if not self.is_visible():
            self.queue_limits_adjustment()
            return
        elif self.are_limits_adjusted():
            return
        else:
            self.limits_adjusted()
        x_min: Optional[float] = None
        x_max: Optional[float] = None
        y_min: Optional[float] = None
        y_max: Optional[float] = None
        for kwargs in self._series:
            tau: ndarray = kwargs["tau"]
            if tau.size > 0:
                if x_min is None or min(tau) < x_min:
                    x_min = min(tau)
                if x_max is None or max(tau) > x_max:
                    x_max = max(tau)
            gamma: Optional[ndarray] = kwargs.get(
                "gamma",
                kwargs.get(
                    "imaginary",
                    kwargs.get("mean"),
                ),
            )
            if gamma is not None:
                if gamma.size > 0:
                    if y_min is None or min(gamma) < y_min:
                        y_min = min(gamma)
                    if y_max is None or max(gamma) > y_max:
                        y_max = max(gamma)
            else:
                lower: ndarray = kwargs["lower"]
                upper: ndarray = kwargs["upper"]
                if lower.size > 0 and upper.size > 0:
                    if y_min is None or min(lower) < y_min:
                        y_min = min(lower)
                    if y_max is None or max(upper) > y_max:
                        y_max = max(upper)
        if x_min is None:
            x_min = 0.5
            x_max = 1.0
            y_min = 0.0
            y_max = 1.0
        else:
            dx: float = 0.1
            x_min = 10 ** (floor(log(x_min) / dx) * dx - dx)
            x_max = 10 ** (ceil(log(x_max) / dx) * dx + dx)
            dy: float = abs(y_max - y_min) * 0.05
            y_min = y_min - dy
            y_max = y_max + dy
        dpg.split_frame()
        dpg.set_axis_limits(self._x_axis, ymin=x_min, ymax=x_max)
        dpg.set_axis_limits(self._y_axis, ymin=y_min, ymax=y_max)
        dpg.split_frame()
        dpg.set_axis_limits_auto(self._x_axis)
        dpg.set_axis_limits_auto(self._y_axis)

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
