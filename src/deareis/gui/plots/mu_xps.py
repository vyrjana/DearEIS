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
    Optional,
)
import dearpygui.dearpygui as dpg
from numpy import (
    ceil,
    floor,
    ndarray,
)
import deareis.themes as themes
from deareis.gui.plots.base import Plot


class MuXps(Plot):
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
                label="number of RC elements",
            )
            self._y_axis_1: int = dpg.add_plot_axis(
                dpg.mvYAxis,
                label="µ",
                no_gridlines=True,
            )
            self._y_axis_2: int = dpg.add_plot_axis(
                dpg.mvYAxis,
                label="log X² (pseudo)",
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
        dpg.delete_item(self._y_axis_1, children_only=True)
        dpg.delete_item(self._y_axis_2, children_only=True)
        self._series.clear()

    def update(self, num_RC: int):
        assert type(num_RC) is int and num_RC >= 0, num_RC
        assert len(self._series) == 1, len(self._series)
        num_RCs: ndarray = self._series[0]["num_RCs"]
        mu: ndarray = self._series[0]["mu"]
        Xps: ndarray = self._series[0]["Xps"]
        x: list = list(num_RCs)
        y: list = list(mu)
        dpg.set_value(
            dpg.get_item_children(self._y_axis_1, slot=1)[1],
            [[num_RC], y[x.index(num_RC)]],
        )
        y = list(Xps)
        dpg.set_value(
            dpg.get_item_children(self._y_axis_2, slot=1)[1],
            [[num_RC], y[x.index(num_RC)]],
        )

    def plot(self, *args, **kwargs):
        assert len(args) == 0, args
        num_RCs: ndarray = kwargs["num_RCs"]
        mu: ndarray = kwargs["mu"]
        Xps: ndarray = kwargs["Xps"]
        mu_criterion: float = kwargs["mu_criterion"]
        num_RC: int = kwargs["num_RC"]
        assert type(num_RCs) is ndarray, num_RCs
        assert type(mu) is ndarray, mu
        assert type(Xps) is ndarray, Xps
        assert type(mu_criterion) is float, mu_criterion
        assert (
            type(num_RC) is int and num_RC >= min(num_RCs) and num_RC <= max(num_RCs)
        ), num_RC
        self._series.append(kwargs)
        x: list = list(num_RCs)
        y: list = list(mu)
        dpg.bind_item_theme(
            dpg.add_scatter_series(
                x=x,
                y=y,
                label="µ",
                user_data=(
                    num_RCs,
                    mu,
                    Xps,
                ),
                parent=self._y_axis_1,
            ),
            themes.mu_Xps.mu,
        )
        dpg.bind_item_theme(
            dpg.add_scatter_series(
                x=[num_RC],
                y=[y[x.index(num_RC)]],
                parent=self._y_axis_1,
            ),
            themes.mu_Xps.mu_highlight,
        )
        dpg.bind_item_theme(
            dpg.add_line_series(
                x=x,
                y=y,
                user_data=(
                    num_RCs,
                    mu,
                    Xps,
                ),
                parent=self._y_axis_1,
            ),
            themes.mu_Xps.mu,
        )
        dpg.bind_item_theme(
            dpg.add_line_series(
                x=[x[0] - 2, x[-1] + 2],
                y=[mu_criterion, mu_criterion],
                label="µ-crit.",
                parent=self._y_axis_1,
            ),
            themes.mu_Xps.mu_criterion,
        )
        y = list(Xps)
        dpg.bind_item_theme(
            dpg.add_scatter_series(
                x=x,
                y=y,
                label="X²",
                parent=self._y_axis_2,
            ),
            themes.mu_Xps.Xps,
        )
        dpg.bind_item_theme(
            dpg.add_scatter_series(
                x=[num_RC],
                y=[y[x.index(num_RC)]],
                parent=self._y_axis_2,
            ),
            themes.mu_Xps.Xps_highlight,
        )
        dpg.bind_item_theme(
            dpg.add_line_series(
                x=x,
                y=y,
                parent=self._y_axis_2,
            ),
            themes.mu_Xps.Xps,
        )

    def adjust_limits(self):
        if not self.is_visible():
            self.queue_limits_adjustment()
            return
        elif self.are_limits_adjusted():
            return
        else:
            self.limits_adjusted()
        max_Xps: Optional[float] = None
        min_Xps: Optional[float] = None
        for kwargs in self._series:
            num_RCs: ndarray = kwargs["num_RCs"]
            Xps: ndarray = kwargs["Xps"]
            if max_Xps is None or max(Xps) > max_Xps:
                max_Xps = ceil(max(Xps))
            if min_Xps is None or min(Xps) > min_Xps:
                min_Xps = floor(min(Xps))
        if max_Xps is None:
            max_Xps = 1.0
        if min_Xps is None:
            min_Xps = 0.0
        dpg.split_frame()
        dpg.set_axis_limits(self._x_axis, ymin=min(num_RCs) - 1, ymax=max(num_RCs) + 1)
        dpg.set_axis_limits(self._y_axis_1, ymin=-0.1, ymax=1.1)
        dpg.set_axis_limits(self._y_axis_2, ymin=min_Xps - 0.1, ymax=max_Xps + 0.1)

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
