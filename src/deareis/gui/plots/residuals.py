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

from typing import (
    List,
    Optional,
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
from deareis.typing.helpers import Tag


DPG_VERSION_1: bool = dpg.get_dearpygui_version().startswith("1.")


class Residuals(Plot):
    def __init__(self, width: int = -1, height: int = -1, *args, **kwargs):
        assert type(width) is int, width
        assert type(height) is int, height
        super().__init__()
        self._limit: Optional[float] = kwargs.get("limit", None)
        assert isinstance(self._limit, float) or self._limit is None

        plot_kwargs = {}
        if DPG_VERSION_1:
            plot_kwargs["anti_aliased"] = True

        with dpg.plot(
            crosshairs=True,
            width=width,
            height=height,
            tag=self._plot,
            **plot_kwargs,
        ):
            dpg.add_plot_legend(
                horizontal=True,
                location=dpg.mvPlot_Location_North,
                outside=kwargs.get("legend_outside", True),
            )

            if DPG_VERSION_1:
                self._x_axis: Tag = dpg.add_plot_axis(
                    dpg.mvXAxis,
                    label="f (Hz)",
                    no_gridlines=True,
                    log_scale=True,
                )
            else:
                self._x_axis: Tag = dpg.add_plot_axis(
                    dpg.mvXAxis,
                    label="f (Hz)",
                    no_gridlines=True,
                    scale=dpg.mvPlotScale_Log10,
                )

            self._y_axis_1: Tag = dpg.add_plot_axis(
                dpg.mvYAxis,
                label="Residual (%)",
            )

        dpg.bind_item_theme(self._plot, themes.plot)
        dpg.bind_item_handler_registry(self._plot, self._item_handler)

    @classmethod
    def duplicate(Class, original, *args, **kwargs) -> Plot:
        copy: Plot = Class(*args, **kwargs)
        for kwargs in original.get_series():
            copy.plot(**kwargs)

        return copy

    def is_blank(self) -> bool:
        return len(dpg.get_item_children(self._y_axis_1, slot=1)) == 0


    def clear(self, *args, **kwargs):
        delete: bool = kwargs.get("delete", True)
        if delete:
            dpg.delete_item(self._y_axis_1, children_only=True)
            self._series.clear()
            return

        i: int = 0
        j: int = 0

        series: int
        for series in dpg.get_item_children(self._y_axis_1, slot=1):
            if i < len(self._series) and j == 0:
                self._series[i]["frequencies"] = array([])
                self._series[i]["real"] = array([])
                self._series[i]["imaginary"] = array([])

            dpg.set_value(series, [[], []])

            j += 1
            if j > 3:
                i += 1
                j = 0

    def update(self, index: int, *args, **kwargs):
        assert type(index) is int and index >= 0, index
        assert len(self._series) > index, (
            index,
            len(self._series),
        )
        assert len(args) == 0, args
        freq: ndarray = kwargs["frequencies"]
        real: ndarray = kwargs["real"]
        imag: ndarray = kwargs["imaginary"]

        assert type(freq) is ndarray, freq
        assert type(real) is ndarray, real
        assert type(imag) is ndarray, imag

        i: int = 0
        j: int = 0

        series: int
        for series in dpg.get_item_children(self._y_axis_1, slot=1):
            if i != index:
                continue

            if i == index and j == 0:
                self._series[index].update(kwargs)

            if j in (0, 1):
                dpg.set_value(series, [list(freq), list(real)])
                dpg.show_item(series)
            elif j in (2, 3):
                dpg.set_value(series, [list(freq), list(imag)])
                dpg.show_item(series)

            j += 1
            if j > 3:  # Real scatter + line and imaginary scatter + line
                i += 1
                j = 0

    def plot(self, *args, **kwargs):
        assert len(args) == 0, args
        freq: ndarray = kwargs["frequencies"]
        real: ndarray = kwargs["real"]
        imag: ndarray = kwargs["imaginary"]

        assert type(freq) is ndarray, freq
        assert type(real) is ndarray, real
        assert type(imag) is ndarray, imag

        self._series.append(kwargs)
        x: list = list(freq)
        y: list = list(real)
        dpg.bind_item_theme(
            dpg.add_scatter_series(
                x=x,
                y=y,
                label="Re(Z)",
                user_data=(
                    freq,
                    real,
                    imag,
                ),
                parent=self._y_axis_1,
            ),
            themes.residuals.real,
        )
        dpg.bind_item_theme(
            dpg.add_line_series(
                x=x,
                y=y,
                user_data=(
                    freq,
                    real,
                    imag,
                ),
                parent=self._y_axis_1,
            ),
            themes.residuals.real,
        )

        y = list(imag)
        dpg.bind_item_theme(
            dpg.add_scatter_series(
                x=x,
                y=y,
                label="Im(Z)",
                parent=self._y_axis_1,
            ),
            themes.residuals.imaginary,
        )
        dpg.bind_item_theme(
            dpg.add_line_series(
                x=x,
                y=y,
                parent=self._y_axis_1,
            ),
            themes.residuals.imaginary,
        )

    def adjust_limits(self):
        if not self.is_visible():
            self.queue_limits_adjustment()
            return
        elif self.are_limits_adjusted():
            return
        else:
            self.limits_adjusted()

        error_lim: float = 0.0
        freq: Optional[ndarray] = None
        for kwargs in self._series:
            freq = kwargs["frequencies"]
            if self._limit is not None:
                break

            if not freq.size > 0:
                continue

            real: ndarray = kwargs["real"]
            imag: ndarray = kwargs["imaginary"]
            if max(real) > error_lim:
                error_lim = max(real)

            if abs(min(real)) > error_lim:
                error_lim = abs(min(real))

            if max(imag) > error_lim:
                error_lim = max(imag)

            if abs(min(imag)) > error_lim:
                error_lim = abs(min(imag))

        if self._limit is not None:
            error_lim = 0.5
        else:
            if error_lim <= 0.5:
                if 0.5 - error_lim > 0.1:
                    error_lim = 0.5
                else:
                    error_lim = 1.0
            elif error_lim <= 5:
                if ceil(error_lim) - error_lim > 0.1:
                    error_lim = ceil(error_lim)
                else:
                    error_lim = ceil(error_lim) + 1.0
            else:
                n: int = 5
                error_lim = ceil(error_lim / n) * n + n

        dpg.split_frame()
        min_x: float = min(freq) if freq.size > 0 else 0.5
        max_x: float = max(freq) if freq.size > 0 else 1.0
        if min_x == 0.0:
            min_x = 1e-1

        dx: float = 0.1
        dpg.set_axis_limits(
            self._x_axis,
            ymin=10 ** (floor(log(min_x) / dx) * dx - dx)
            if (freq is not None and freq.size > 0)
            else 0,
            ymax=10 ** (ceil(log(max_x) / dx) * dx + dx)
            if (freq is not None and freq.size > 0)
            else 1,
        )
        dpg.set_axis_limits(self._y_axis_1, ymin=-error_lim, ymax=error_lim)

        dpg.split_frame()
        dpg.set_axis_limits_auto(self._y_axis_1)

    def copy_limits(self, other: Plot):
        src: int
        dst: int
        for src, dst in zip(
            [
                other._x_axis,
                other._y_axis_1,
            ],
            [
                self._x_axis,
                self._y_axis_1,
            ],
        ):
            limits: List[float] = dpg.get_axis_limits(src)
            dpg.set_axis_limits(dst, *limits)

        dpg.split_frame()
        dpg.set_axis_limits_auto(self._x_axis)
        dpg.set_axis_limits_auto(self._y_axis_1)
