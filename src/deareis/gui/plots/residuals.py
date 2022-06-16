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

from typing import List
import dearpygui.dearpygui as dpg
from numpy import ceil, ndarray
import deareis.themes as themes
from deareis.gui.plots.base import Plot


class Residuals(Plot):
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
            self._x_axis: int = dpg.add_plot_axis(dpg.mvXAxis, label="log f")
            self._y_axis_1: int = dpg.add_plot_axis(dpg.mvYAxis, label="Z' error (%)")
            self._y_axis_2: int = dpg.add_plot_axis(dpg.mvYAxis, label='Z" error (%)')
        dpg.bind_item_theme(self._plot, themes.plot)
        dpg.bind_item_handler_registry(self._plot, self._item_handler)

    @classmethod
    def duplicate(Class, original: "Residuals", *args, **kwargs) -> "Residuals":
        copy: "Residuals" = Class(*args, **kwargs)
        for kwargs in original.get_series():
            copy.plot(**kwargs)
        return copy

    def is_blank(self) -> bool:
        return (
            len(dpg.get_item_children(self._y_axis_1, slot=1)) == 0
            and len(dpg.get_item_children(self._y_axis_2, slot=1)) == 0
        )

    def clear(self):
        dpg.delete_item(self._y_axis_1, children_only=True)
        dpg.delete_item(self._y_axis_2, children_only=True)
        self._series.clear()

    def plot(self, *args, **kwargs):
        assert len(args) == 0, args
        freq: ndarray = kwargs["frequency"]
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
                label="Z'",
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
                label='Z"',
                parent=self._y_axis_2,
            ),
            themes.residuals.imaginary,
        )
        dpg.bind_item_theme(
            dpg.add_line_series(
                x=x,
                y=y,
                parent=self._y_axis_2,
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
            freq = kwargs["frequency"]
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
        dpg.set_axis_limits(
            self._x_axis,
            ymin=min(freq) - 0.1 if freq is not None else 0,
            ymax=max(freq) + 0.1 if freq is not None else 1,
        )
        dpg.set_axis_limits(self._y_axis_1, ymin=-error_lim, ymax=error_lim)
        dpg.set_axis_limits(self._y_axis_2, ymin=-error_lim, ymax=error_lim)
        dpg.split_frame()
        dpg.set_axis_limits_auto(self._y_axis_1)
        dpg.set_axis_limits_auto(self._y_axis_2)

    def copy_limits(self, other: "Residuals"):
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
