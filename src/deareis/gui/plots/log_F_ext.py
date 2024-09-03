# DearEIS is licensed under the GPLv3 or later (https://www.gnu.org/licenses/gpl-3.0.html).
# Copyright 2024 DearEIS developers
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
    inf,
    isneginf,
    isposinf,
)
import deareis.themes as themes
from deareis.gui.plots.base import Plot
from deareis.typing.helpers import Tag


class LogFextStatistic(Plot):
    def __init__(self, width: int = -1, height: int = -1, *args, **kwargs):
        assert isinstance(width, int), width
        assert isinstance(height, int), height
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
            self._x_axis: Tag = dpg.add_plot_axis(
                dpg.mvXAxis,
                label="log Fext",
                log_scale=False,
                no_gridlines=True,
            )
            self._y_axis: Tag = dpg.add_plot_axis(
                dpg.mvYAxis,
                label="Minimized statistic",
                log_scale=False,
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
            series: Tag
            for i, series in enumerate(dpg.get_item_children(self._y_axis, slot=1)):
                self._series[i]["log_F_ext"] = array([])
                self._series[i]["statistic"] = array([])
                dpg.set_value(series, [[], []])

    def update(self, index: int, *args, **kwargs):
        assert isinstance(index, int) and index >= 0, index
        assert len(self._series) > index, (
            index,
            len(self._series),
        )
        assert len(args) == 0, args

        log_F_ext: List[float] = kwargs["log_F_ext"]
        statistic: List[float] = kwargs["statistic"]

        assert isinstance(log_F_ext, list), log_F_ext
        assert isinstance(statistic, list), statistic

        i: int
        series: Tag
        for i, series in enumerate(dpg.get_item_children(self._y_axis, slot=1)):
            if i != index:
                continue

            self._series[index].update(kwargs)
            dpg.set_value(
                series,
                [
                    log_F_ext,
                    statistic,
                ],
            )
            dpg.show_item(series)
            break

    def plot(self, *args, **kwargs) -> Tuple[int, int]:
        assert len(args) == 0, args

        log_F_ext: List[float] = kwargs["log_F_ext"]
        statistic: List[float] = kwargs["statistic"]
        label: str = kwargs["label"]
        line: bool = kwargs.get("line", False)
        theme: Optional[Tuple[int, int]] = kwargs.get("theme")

        assert isinstance(log_F_ext, list), log_F_ext
        assert isinstance(statistic, list), statistic
        assert isinstance(label, str), label
        assert isinstance(line, bool), line
        assert isinstance(theme, int) or theme is None, theme

        self._series.append(kwargs)
        func: Callable = dpg.add_scatter_series if not line else dpg.add_line_series

        x: list = list(log_F_ext)
        y: list = list(statistic)
        tag_statistic: int = func(
            x=x,
            y=y,
            label=label if label != "" else None,
            parent=self._y_axis,
        )
        if themes is not None:
            dpg.bind_item_theme(tag_statistic, theme)

        return tag_statistic

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
            log_F_ext: List[float] = kwargs["log_F_ext"]
            if len(log_F_ext) > 0:
                if x_min is None or min(log_F_ext) < x_min:
                    x_min = min(log_F_ext)
                if x_max is None or max(log_F_ext) > x_max:
                    x_max = max(log_F_ext)

            statistic: List[float] = kwargs["statistic"]
            if len(statistic) > 0:
                if y_min is None or min(statistic) < y_min:
                    y_min = min(statistic)
                if y_max is None or max(statistic) > y_max:
                    y_max = max(statistic)

        if x_min is None:
            x_min = -1.0
            x_max = 1.0
            y_min = 0.0
            y_max = 1.0
        else:
            dx: float = 0.1
            x_min -= dx
            x_max += dx

            dy: float = abs(y_max - y_min) / 10
            y_min -= dy
            y_max += dy

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


class PseudoChisqr(Plot):
    def __init__(self, width: int = -1, height: int = -1, *args, **kwargs):
        assert isinstance(width, int), width
        assert isinstance(height, int), height
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
            self._x_axis: Tag = dpg.add_plot_axis(
                dpg.mvXAxis,
                label="Number of RC elements",
                log_scale=False,
                no_gridlines=True,
            )
            self._y_axis: Tag = dpg.add_plot_axis(
                dpg.mvYAxis,
                label="log X² (pseudo)",
                log_scale=False,
                no_gridlines=True,
            )

        dpg.bind_item_theme(self._plot, themes.plot)
        dpg.bind_item_handler_registry(self._plot, self._item_handler)
        self.min_num_RC: int = -1
        self.max_num_RC: int = -1
        self.min_log_pseudo_chisqr: float = -inf
        self.max_log_pseudo_chisqr: float = inf

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
            series: Tag
            for i, series in enumerate(dpg.get_item_children(self._y_axis, slot=1)):
                self._series[i]["num_RC"] = array([])
                self._series[i]["pseudo_chisqr"] = array([])
                dpg.set_value(series, [[], []])

        self.min_num_RC = -1
        self.max_num_RC = -1
        self.min_log_pseudo_chisqr = -inf
        self.max_log_pseudo_chisqr = inf

    def update(self, index: int, *args, **kwargs):
        assert isinstance(index, int) and index >= 0, index
        assert len(self._series) > index, (
            index,
            len(self._series),
        )
        assert len(args) == 0, args

        num_RC: List[int] = kwargs["num_RC"]
        pseudo_chisqr: List[float] = kwargs["pseudo_chisqr"]
        label: Optional[str] = kwargs.get("label")

        assert isinstance(num_RC, list), num_RC
        assert isinstance(pseudo_chisqr, list), pseudo_chisqr

        i: int
        series: Tag
        for i, series in enumerate(dpg.get_item_children(self._y_axis, slot=1)):
            if i != index:
                continue

            self._series[index].update(kwargs)
            dpg.set_value(
                series,
                [
                    num_RC,
                    pseudo_chisqr,
                ],
            )
            if label is not None:
                dpg.set_item_label(series, label)

            dpg.show_item(series)
            break

    def plot(self, *args, **kwargs) -> Tuple[int, int]:
        assert len(args) == 0, args

        num_RC: List[int] = kwargs["num_RC"]
        pseudo_chisqr: List[float] = kwargs["pseudo_chisqr"]
        self.min_num_RC = kwargs.get(
            "min_num_RC",
            self.min_num_RC,
        )
        self.max_num_RC = kwargs.get(
            "max_num_RC",
            self.max_num_RC,
        )
        self.min_log_pseudo_chisqr = kwargs.get(
            "min_log_pseudo_chisqr",
            self.min_log_pseudo_chisqr,
        )
        self.max_log_pseudo_chisqr = kwargs.get(
            "max_log_pseudo_chisqr",
            self.max_log_pseudo_chisqr,
        )
        label: str = kwargs["label"]
        line: bool = kwargs.get("line", False)
        theme: Optional[Tuple[int, int]] = kwargs.get("theme")

        assert isinstance(num_RC, list), num_RC
        assert isinstance(pseudo_chisqr, list), pseudo_chisqr
        assert isinstance(self.max_num_RC, int), self.max_num_RC
        assert isinstance(label, str), label
        assert isinstance(line, bool), line
        assert isinstance(theme, int) or theme is None, theme

        self._series.append(kwargs)
        func: Callable = dpg.add_scatter_series if not line else dpg.add_line_series

        x: list = num_RC
        y: list = pseudo_chisqr
        tag_pseudo_chisqr: int = func(
            x=x,
            y=y,
            label=label if label != "" else None,
            parent=self._y_axis,
        )
        if theme is not None:
            dpg.bind_item_theme(tag_pseudo_chisqr, theme)

        return tag_pseudo_chisqr

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
            num_RC: List[int] = kwargs["num_RC"]
            if len(num_RC) > 0:
                if x_min is None or min(num_RC) < x_min:
                    x_min = min(num_RC)
                if x_max is None or max(num_RC) > x_max:
                    x_max = max(num_RC)

            pseudo_chisqr: List[float] = kwargs["pseudo_chisqr"]
            if len(pseudo_chisqr) > 0:
                if y_min is None or min(pseudo_chisqr) < y_min:
                    y_min = min(pseudo_chisqr)
                if y_max is None or max(pseudo_chisqr) > y_max:
                    y_max = max(pseudo_chisqr)

        if self.min_num_RC > 0:
            x_min = self.min_num_RC
        if self.max_num_RC > 0:
            x_max = self.max_num_RC
        if not isneginf(self.min_log_pseudo_chisqr):
            y_min = self.min_log_pseudo_chisqr
        if not isposinf(self.max_log_pseudo_chisqr):
            y_max = self.max_log_pseudo_chisqr

        if x_min is None:
            x_min = 0.0
            x_max = 1.0
            y_min = 0.0
            y_max = 1.0
        else:
            dx: int = 1
            x_min -= dx
            x_max += dx

            y_min = floor(y_min)
            y_max = ceil(y_max)
            dy: float = abs(y_max - y_min) / 10
            y_min -= dy
            y_max += dy

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
