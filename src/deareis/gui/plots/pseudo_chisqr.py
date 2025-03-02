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
    ceil,
    floor,
    integer,
    issubdtype,
)
import deareis.themes as themes
from deareis.gui.plots.base import Plot
from deareis.typing.helpers import Tag


DPG_VERSION_1: bool = dpg.get_dearpygui_version().startswith("1.")


class PseudoChisqrAndScore(Plot):
    def __init__(self, width: int = -1, height: int = -1, *args, **kwargs):
        assert type(width) is int, width
        assert type(height) is int, height
        super().__init__()

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

            y2_axis_kwargs = {}
            if not DPG_VERSION_1:
                y2_axis_kwargs["opposite"] = True

            self._x_axis: Tag = dpg.add_plot_axis(
                dpg.mvXAxis,
                label="Number of RC elements",
            )
            self._y_axis_1: Tag = dpg.add_plot_axis(
                dpg.mvYAxis,
                label="Score",
                no_gridlines=True,
                no_tick_labels=True,
            )
            self._y_axis_2: Tag = dpg.add_plot_axis(
                dpg.mvYAxis if DPG_VERSION_1 else dpg.mvYAxis2,
                label="log X² (pseudo)",
                no_gridlines=True,
                **y2_axis_kwargs,
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

        x: list = self._series[0]["num_RCs"]
        y: list = self._series[0]["scores"]
        dpg.set_value(
            dpg.get_item_children(self._y_axis_1, slot=1)[1],
            [[num_RC], [y[x.index(num_RC)]]],
        )

        y = self._series[0]["pseudo_chisqr"]
        dpg.set_value(
            dpg.get_item_children(self._y_axis_2, slot=1)[1],
            [[num_RC], [y[x.index(num_RC)]]],
        )

    def plot(self, *args, **kwargs):
        assert len(args) == 0, args
        num_RCs: List[int] = kwargs["num_RCs"]
        scores: List[float] = kwargs["scores"]
        pseudo_chisqr: List[float] = kwargs["pseudo_chisqr"]
        num_RC: int = kwargs["num_RC"]
        lower_limit: int = kwargs["lower_limit"]
        upper_limit: int = kwargs["upper_limit"]

        assert type(num_RCs) is list, num_RCs
        assert type(scores) is list, scores
        assert type(pseudo_chisqr) is list, pseudo_chisqr
        assert issubdtype(type(num_RC), integer), (type(num_RC), num_RC)
        assert num_RC >= min(num_RCs), (num_RC, num_RCs)
        assert num_RC <= max(num_RCs), (num_RC, num_RCs)
        assert type(lower_limit) is int, lower_limit
        assert type(upper_limit) is int, upper_limit

        self._series.append(kwargs)
        x: list = num_RCs

        y: list = scores
        dpg.bind_item_theme(
            dpg.add_scatter_series(
                x=x,
                y=y,
                label="Score",
                parent=self._y_axis_1,
            ),
            themes.suggestion_method.default,
        )
        dpg.bind_item_theme(
            dpg.add_scatter_series(
                x=[num_RC],
                y=[y[x.index(num_RC)]],
                parent=self._y_axis_1,
            ),
            themes.suggestion_method.highlight,
        )
        dpg.bind_item_theme(
            dpg.add_line_series(
                x=x,
                y=y,
                parent=self._y_axis_1,
            ),
            themes.suggestion_method.default,
        )

        dpg.bind_item_theme(
            dpg.add_shade_series(
                x=[lower_limit, upper_limit],
                y1=[-2.0] * 2,
                y2=[2.0] * 2,
                label="Limits",
                parent=self._y_axis_1,
            ),
            themes.suggestion_method.range,
        )

        y = pseudo_chisqr
        dpg.bind_item_theme(
            dpg.add_scatter_series(
                x=x,
                y=y,
                label="X²",
                parent=self._y_axis_2,
            ),
            themes.pseudo_chisqr.default,
        )
        dpg.bind_item_theme(
            dpg.add_scatter_series(
                x=[num_RC],
                y=[y[x.index(num_RC)]],
                parent=self._y_axis_2,
            ),
            themes.pseudo_chisqr.highlight,
        )
        dpg.bind_item_theme(
            dpg.add_line_series(
                x=x,
                y=y,
                parent=self._y_axis_2,
            ),
            themes.pseudo_chisqr.default,
        )

    def adjust_limits(self):
        if not self.is_visible():
            self.queue_limits_adjustment()
            return
        elif self.are_limits_adjusted():
            return
        else:
            self.limits_adjusted()

        min_num_RC: int = 1
        max_num_RC: int = 2
        max_pseudo_chisqr: Optional[float] = None
        min_pseudo_chisqr: Optional[float] = None

        for kwargs in self._series:
            num_RCs: List[int] = kwargs["num_RCs"]
            min_num_RC = min(num_RCs) - 1
            max_num_RC = kwargs["max_x"]

            pseudo_chisqr: List[float] = kwargs["pseudo_chisqr"]
            if min_pseudo_chisqr is None or min(pseudo_chisqr) > min_pseudo_chisqr:
                min_pseudo_chisqr = floor(min(pseudo_chisqr))
            if max_pseudo_chisqr is None or max(pseudo_chisqr) > max_pseudo_chisqr:
                max_pseudo_chisqr = ceil(max(pseudo_chisqr))

        if max_pseudo_chisqr is None:
            max_pseudo_chisqr = 1.0

        if min_pseudo_chisqr is None:
            min_pseudo_chisqr = 0.0

        dpg.split_frame()
        dpg.set_axis_limits(
            self._x_axis,
            ymin=min_num_RC,
            ymax=max_num_RC,
        )
        dpg.set_axis_limits(
            self._y_axis_1,
            ymin=-0.1,
            ymax=1.1,
        )
        dpg.set_axis_limits(
            self._y_axis_2,
            ymin=min_pseudo_chisqr - 0.1,
            ymax=max_pseudo_chisqr + 0.1,
        )

        dpg.split_frame(delay=33)
        dpg.set_axis_limits_auto(self._x_axis)
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
