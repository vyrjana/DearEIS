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
    Tuple,
)
import dearpygui.dearpygui as dpg
from numpy import (
    array,
    ceil,
    floor,
    log10 as log,
    ndarray,
)
import deareis.themes as themes
from deareis.gui.plots.base import Plot


class Bode(Plot):
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
                horizontal=True,
                location=dpg.mvPlot_Location_North,
                outside=kwargs.get("legend_outside", True),
            )
            self._x_axis: int = dpg.add_plot_axis(
                dpg.mvXAxis,
                label="f (Hz)",
                log_scale=True,
                no_gridlines=True,
            )
            self._y_axis_1: int = dpg.add_plot_axis(
                dpg.mvYAxis,
                label="|Z| (ohm)",
                log_scale=True,
                no_gridlines=True,
            )
            self._y_axis_2: int = dpg.add_plot_axis(
                dpg.mvYAxis,
                label="-phi (°)",
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
        return (
            len(dpg.get_item_children(self._y_axis_1, slot=1)) == 0
            and len(dpg.get_item_children(self._y_axis_2, slot=1)) == 0
        )

    def clear(self, *args, **kwargs):
        delete: bool = kwargs.get("delete", True)
        if delete:
            dpg.delete_item(self._y_axis_1, children_only=True)
            dpg.delete_item(self._y_axis_2, children_only=True)
            self._series.clear()
        else:
            i: int
            series_1: int
            series_2: int
            for i, (series_1, series_2) in enumerate(
                zip(
                    dpg.get_item_children(self._y_axis_1, slot=1),
                    dpg.get_item_children(self._y_axis_2, slot=1),
                )
            ):
                self._series[i]["frequency"] = array([])
                self._series[i]["magnitude"] = array([])
                self._series[i]["phase"] = array([])
                dpg.set_value(series_1, [[], []])
                dpg.set_value(series_2, [[], []])

    def update(self, index: int, *args, **kwargs):
        assert type(index) is int and index >= 0, index
        assert len(self._series) > index, (
            index,
            len(self._series),
        )
        assert len(args) == 0, args
        freq: ndarray = kwargs["frequency"]
        mag: ndarray = kwargs["magnitude"]
        phase: ndarray = kwargs["phase"]
        assert type(freq) is ndarray, freq
        assert type(mag) is ndarray, mag
        assert type(phase) is ndarray, phase
        i: int
        series_1: int
        series_2: int
        for i, (series_1, series_2) in enumerate(
            zip(
                dpg.get_item_children(self._y_axis_1, slot=1),
                dpg.get_item_children(self._y_axis_2, slot=1),
            )
        ):
            if i != index:
                continue
            self._series[index].update(kwargs)
            dpg.set_value(series_1, [list(freq), list(mag)])
            dpg.set_value(series_2, [list(freq), list(phase)])
            break

    def plot(self, *args, **kwargs) -> Tuple[int, int]:
        assert len(args) == 0, args
        freq: ndarray = kwargs["frequency"]
        mag: ndarray = kwargs["magnitude"]
        phase: ndarray = kwargs["phase"]
        labels: Tuple[str, str] = kwargs["labels"]
        sim: bool = kwargs.get("simulation", False)
        fit: bool = kwargs.get("fit", False)
        line: bool = kwargs.get("line", False)
        show_labels: bool = kwargs.get("show_labels", True)
        themes: Optional[Tuple[int, int]] = kwargs.get("themes")
        assert type(freq) is ndarray, freq
        assert type(mag) is ndarray, mag
        assert type(phase) is ndarray, phase
        assert type(labels) is tuple and len(labels) == 2, labels
        assert type(sim) is bool, sim
        assert type(fit) is bool, fit
        assert type(line) is bool, line
        assert (type(themes) is tuple and len(themes) == 2) or themes is None, themes
        assert type(show_labels) is bool, show_labels
        self._series.append(kwargs)
        func: Callable = dpg.add_scatter_series if not line else dpg.add_line_series
        x: list = list(freq)
        tag_mag: int = func(
            x=x,
            y=list(mag),
            label=labels[0] if show_labels else None,
            parent=self._y_axis_1,
        )
        tag_phase: int = func(
            x=x,
            y=list(phase),
            label=labels[1] if show_labels else None,
            parent=self._y_axis_2,
        )
        if themes is not None:
            dpg.bind_item_theme(tag_mag, themes[0])
            dpg.bind_item_theme(tag_phase, themes[1])
        return (
            tag_mag,
            tag_phase,
        )

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
        y1_min: Optional[float] = None
        y1_max: Optional[float] = None
        y2_min: Optional[float] = None
        y2_max: Optional[float] = None
        for kwargs in self._series:
            freq: ndarray = kwargs["frequency"]
            mag: ndarray = kwargs["magnitude"]
            phase: ndarray = kwargs["phase"]
            if freq.size > 0:
                if x_min is None or min(freq) < x_min:
                    x_min = min(freq)
                if x_max is None or max(freq) > x_max:
                    x_max = max(freq)
            if mag.size > 0:
                if y1_min is None or min(mag) < y1_min:
                    y1_min = min(mag)
                if y1_max is None or max(mag) > y1_max:
                    y1_max = max(mag)
            if phase.size > 0:
                if y2_min is None or min(phase) < y2_min:
                    y2_min = min(phase)
                if y2_max is None or max(phase) > y2_max:
                    y2_max = max(phase)
        if x_min is None:
            x_min = 0.0
            x_max = 1.0
            y1_min = 0.0
            y1_max = 1.0
            y2_min = 0.0
            y2_max = 1.0
        else:
            dx: float = 0.1
            x_min = 10 ** (floor(log(x_min) / dx) * dx - dx)
            x_max = 10 ** (ceil(log(x_max) / dx) * dx + dx)
            dy: float = 0.1
            y1_min = 10 ** (floor(log(y1_min) / dy) * dy - dy)
            y1_max = 10 ** (ceil(log(y1_max) / dy) * dy + dy)
            if log(y1_max) - log(y1_min) < 1.0:
                y1_min = 10 ** floor(log(y1_min))
                y1_max = 10 ** ceil(log(y1_max))
            n: int = 5
            y2_min = floor(y2_min / n) * n - n
            y2_max = ceil(y2_max / n) * n + n
        dpg.split_frame()
        dpg.set_axis_limits(self._x_axis, ymin=x_min, ymax=x_max)
        dpg.set_axis_limits(self._y_axis_1, ymin=y1_min, ymax=y1_max)
        dpg.set_axis_limits(self._y_axis_2, ymin=y2_min, ymax=y2_max)
        dpg.split_frame()
        dpg.set_axis_limits_auto(self._x_axis)
        dpg.set_axis_limits_auto(self._y_axis_1)
        dpg.set_axis_limits_auto(self._y_axis_2)

    def copy_limits(self, other: Plot):
        src: int
        dst: int
        for src, dst in zip(
            [
                other._x_axis,
                other._y_axis_1,
                other._y_axis_2,
            ],
            [
                self._x_axis,
                self._y_axis_1,
                self._y_axis_2,
            ],
        ):
            limits: List[float] = dpg.get_axis_limits(src)
            dpg.set_axis_limits(dst, *limits)
        dpg.split_frame()
        dpg.set_axis_limits_auto(self._x_axis)
        dpg.set_axis_limits_auto(self._y_axis_1)
        dpg.set_axis_limits_auto(self._y_axis_2)


class BodeMagnitude(Plot):
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
                label="f (Hz)",
                log_scale=True,
                no_gridlines=True,
            )
            self._y_axis: int = dpg.add_plot_axis(
                dpg.mvYAxis,
                label="|Z| (ohm)",
                log_scale=True,
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
        dpg.delete_item(self._y_axis, children_only=True)
        self._series.clear()

    def plot(self, *args, **kwargs) -> int:
        assert len(args) == 0, args
        freq: ndarray = kwargs["frequency"]
        mag: ndarray = kwargs["magnitude"]
        label: str = kwargs["label"]
        sim: bool = kwargs.get("simulation", False)
        fit: bool = kwargs.get("fit", False)
        line: bool = kwargs.get("line", False)
        theme: Optional[int] = kwargs.get("theme")
        show_label: bool = kwargs.get("show_label", True)
        assert type(freq) is ndarray, freq
        assert type(mag) is ndarray, mag
        assert type(label) is str, label
        assert type(sim) is bool, sim
        assert type(fit) is bool, fit
        assert type(line) is bool, line
        assert type(theme) is int or theme is None, theme
        assert type(show_label) is bool, show_label
        self._series.append(kwargs)
        func: Callable = dpg.add_scatter_series if not line else dpg.add_line_series
        tag: int = func(
            x=list(freq),
            y=list(mag),
            label=label if show_label else None,
            parent=self._y_axis,
        )
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
            freq: ndarray = kwargs["frequency"]
            mag: ndarray = kwargs["magnitude"]
            if freq.size > 0:
                if x_min is None or min(freq) < x_min:
                    x_min = min(freq)
                if x_max is None or max(freq) > x_max:
                    x_max = max(freq)
            if mag.size > 0:
                if y_min is None or min(mag) < y_min:
                    y_min = min(mag)
                if y_max is None or max(mag) > y_max:
                    y_max = max(mag)
        if x_min is None:
            x_min = 0.0
            x_max = 1.0
            y_min = 0.0
            y_max = 1.0
        else:
            dx: float = 0.1
            x_min = 10 ** (floor(log(x_min) / dx) * dx - dx)
            x_max = 10 ** (ceil(log(x_max) / dx) * dx + dx)
            dy: float = 0.1
            y_min = 10 ** (floor(log(y_min) / dy) * dy - dy)
            y_max = 10 ** (ceil(log(y_max) / dy) * dy + dy)
            if log(y_max) - log(y_min) < 1.0:
                y_min = 10 ** floor(log(y_min))
                y_max = 10 ** ceil(log(y_max))
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


class BodePhase(Plot):
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
                label="f (Hz)",
                log_scale=True,
                no_gridlines=True,
            )
            self._y_axis: int = dpg.add_plot_axis(
                dpg.mvYAxis,
                label="-phi (°)",
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
        dpg.delete_item(self._y_axis, children_only=True)
        self._series.clear()

    def plot(self, *args, **kwargs) -> int:
        assert len(args) == 0, args
        freq: ndarray = kwargs["frequency"]
        phase: ndarray = kwargs["phase"]
        label: str = kwargs["label"]
        sim: bool = kwargs.get("simulation", False)
        fit: bool = kwargs.get("fit", False)
        line: bool = kwargs.get("line", False)
        theme: Optional[int] = kwargs.get("theme")
        show_label: bool = kwargs.get("show_label", True)
        assert type(freq) is ndarray, freq
        assert type(phase) is ndarray, phase
        assert type(label) is str, label
        assert type(sim) is bool, sim
        assert type(fit) is bool, fit
        assert type(line) is bool, line
        assert type(theme) is int or theme is None, theme
        assert type(show_label) is bool, show_label
        self._series.append(kwargs)
        func: Callable = dpg.add_scatter_series if not line else dpg.add_line_series
        tag: int = func(
            x=list(freq),
            y=list(phase),
            label=label if show_label else None,
            parent=self._y_axis,
        )
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
            freq: ndarray = kwargs["frequency"]
            phase: ndarray = kwargs["phase"]
            if freq.size > 0:
                if x_min is None or min(freq) < x_min:
                    x_min = min(freq)
                if x_max is None or max(freq) > x_max:
                    x_max = max(freq)
            if phase.size > 0:
                if y_min is None or min(phase) < y_min:
                    y_min = min(phase)
                if y_max is None or max(phase) > y_max:
                    y_max = max(phase)
        if x_min is None:
            x_min = 0.0
            x_max = 1.0
            y_min = 0.0
            y_max = 1.0
        else:
            dx: float = 0.1
            x_min = 10 ** (floor(log(x_min) / dx) * dx - dx)
            x_max = 10 ** (ceil(log(x_max) / dx) * dx + dx)
            n: int = 5
            y_min = floor(y_min / n) * n - n
            y_max = ceil(y_max / n) * n + n
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
