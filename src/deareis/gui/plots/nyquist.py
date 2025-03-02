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

from typing import Callable, List, Optional
import dearpygui.dearpygui as dpg
from numpy import (
    array,
    complex128,
    ndarray,
)
import deareis.themes as themes
from deareis.gui.plots.base import Plot
from deareis.typing.helpers import Tag


DPG_VERSION_1: bool = dpg.get_dearpygui_version().startswith("1.")


class Nyquist(Plot):
    def __init__(self, width: int = -1, height: int = -1, *args, **kwargs):
        assert type(width) is int, width
        assert type(height) is int, height
        super().__init__()
        self._admittance: bool = False

        plot_kwargs = {}
        if DPG_VERSION_1:
            plot_kwargs["anti_aliased"] = True

        with dpg.plot(
            crosshairs=True,
            equal_aspects=True,
            width=width,
            height=height,
            tag=self._plot,
            **plot_kwargs,
        ):
            dpg.add_plot_legend(
                horizontal=kwargs.get("legend_horizontal", True),
                location=kwargs.get("legend_location", dpg.mvPlot_Location_North),
                outside=kwargs.get("legend_outside", True),
            )

            self._x_axis: Tag = dpg.add_plot_axis(
                dpg.mvXAxis,
                label="Re(Z) (ohm)",
                no_gridlines=True,
            )

            self._y_axis: Tag = dpg.add_plot_axis(
                dpg.mvYAxis,
                label="-Im(Z) (ohm)",
                no_gridlines=True,
            )

            if kwargs.get("add_tooltip", False) is True:
                self.tooltip: Tag = dpg.generate_uuid()
                with dpg.tooltip(
                    parent=self._y_axis,
                    show=False,
                    tag=self.tooltip,
                ):
                    self.tooltip_text: Tag = dpg.add_text("")

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
                self._series[i]["impedances"] = array([], dtype=complex128)
                dpg.set_value(series, [[], []])

    def update(self, index: int, *args, **kwargs):
        assert type(index) is int and index >= 0, index
        assert len(self._series) > index, (
            index,
            len(self._series),
        )
        assert len(args) == 0, args

        X: ndarray = kwargs["impedances"] ** (-1 if self._admittance is True else 1)
        real: ndarray = X.real
        imag: ndarray = X.imag * (1 if self._admittance is True else -1)
        assert type(real) is ndarray, real
        assert type(imag) is ndarray, imag

        i: int
        series: Tag
        for i, series in enumerate(dpg.get_item_children(self._y_axis, slot=1)):
            if i != index:
                continue

            self._series[index].update(kwargs)
            dpg.set_value(
                series,
                [
                    list(real),
                    list(imag),
                ],
            )
            dpg.show_item(series)
            break

    def plot(self, *args, **kwargs) -> int:
        assert len(args) == 0, args
        X: ndarray = kwargs["impedances"] ** (-1 if self._admittance is True else 1)
        real: ndarray = X.real
        imag: ndarray = X.imag * (1 if self._admittance is True else -1)
        label: str = kwargs["label"]
        simulation: bool = kwargs.get("simulation", False)
        fit: bool = kwargs.get("fit", False)
        line: bool = kwargs.get("line", False)
        theme: Optional[int] = kwargs.get("theme")
        show_label: bool = kwargs.get("show_label", True)

        assert type(real) is ndarray, real
        assert type(imag) is ndarray, imag
        assert type(label) is str, label
        assert type(simulation) is bool, simulation
        assert type(fit) is bool, fit
        assert type(line) is bool, line
        assert type(theme) is int or theme is None, theme
        assert type(show_label) is bool, show_label

        self._series.append(kwargs)
        func: Callable = dpg.add_scatter_series if not line else dpg.add_line_series
        tag: int = func(
            x=list(real),
            y=list(imag),
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

        dpg.split_frame()
        dpg.fit_axis_data(self._x_axis)
        dpg.fit_axis_data(self._y_axis)
        dpg.split_frame()

        x_min: float
        x_max: float
        x_min, x_max = dpg.get_axis_limits(self._x_axis)
        dx: float = (x_max - x_min) * 0.05
        dpg.set_axis_limits(self._x_axis, x_min - dx, x_max + dx)

        y_min: float
        y_max: float
        y_min, y_max = dpg.get_axis_limits(self._y_axis)
        dy: float = (y_max - y_min) * 0.05
        dpg.set_axis_limits(self._y_axis, y_min - dy, y_max + dy)

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

    def set_admittance(self, admittance: bool, adjust_limits: bool = True):
        if self._admittance == admittance:
            return
        else:
            self._admittance = admittance

        dpg.set_item_label(
            self._x_axis,
            "Re(Y) (S)" if self._admittance is True else "Re(Z) (ohm)",
        )
        dpg.set_item_label(
            self._y_axis,
            "Im(Y) (S)" if self._admittance is True else "-Im(Z) (ohm)",
        )

        for i, kwargs in enumerate(self.get_series()):
            self.update(index=i, **kwargs)

        if adjust_limits:
            dpg.split_frame(delay=33)
            self.queue_limits_adjustment()
            self.adjust_limits()

    @property
    def admittance(self) -> bool:
        return self._admittance
