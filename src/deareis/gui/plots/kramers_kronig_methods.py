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
    List,
    Optional,
)
from numpy import (
    ceil,
    floating,
    floor,
    integer,
    issubdtype,
)
import dearpygui.dearpygui as dpg
import deareis.themes as themes
from deareis.gui.plots.base import Plot
from deareis.typing.helpers import Tag


class Method1(Plot):
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
            self._x_axis: Tag = dpg.add_plot_axis(
                dpg.mvXAxis,
                label="Number of RC elements",
            )
            self._y_axis_1: Tag = dpg.add_plot_axis(
                dpg.mvYAxis,
                label="µ",
                no_gridlines=True,
            )
            self._y_axis_2: Tag = dpg.add_plot_axis(
                dpg.mvYAxis,
                label="S",
                no_gridlines=True,
            )
            self._y_axis_3: Tag = dpg.add_plot_axis(
                dpg.mvYAxis,
                label=None,
                no_gridlines=True,
                no_tick_labels=True,
                no_tick_marks=True,
            )

        dpg.bind_item_theme(self._plot, themes.plot)
        dpg.bind_item_handler_registry(self._plot, self._item_handler)

    def clear(self, *args, **kwargs):
        dpg.delete_item(self._y_axis_1, children_only=True)
        dpg.delete_item(self._y_axis_2, children_only=True)
        dpg.delete_item(self._y_axis_3, children_only=True)
        self._series.clear()

    def update(self, num_RC: int):
        assert type(num_RC) is int and num_RC >= 0, num_RC
        if len(self._series) < 1:
            return

        x: list = self._series[0]["num_RCs"]
        y: list = self._series[0]["mu"]
        dpg.set_value(
            dpg.get_item_children(self._y_axis_1, slot=1)[1],
            [[num_RC], [y[x.index(num_RC)]]],
        )

        if self._series[0]["beta"] <= 0.0:
            return

        y = self._series[0]["scores"]
        dpg.set_value(
            dpg.get_item_children(self._y_axis_2, slot=1)[1],
            [[num_RC], [y[x.index(num_RC)]]],
        )

    def plot(self, *args, **kwargs):
        assert len(args) == 0, args

        num_RCs: List[int] = kwargs["num_RCs"]
        mu: List[float] = kwargs["mu"]
        scores: List[float] = kwargs["scores"]
        mu_criterion: float = kwargs["mu_criterion"]
        beta: float = kwargs["beta"]
        num_RC: int = kwargs["num_RC"]
        lower_limit: int = kwargs["lower_limit"]
        upper_limit: int = kwargs["upper_limit"]

        assert type(num_RCs) is list, num_RCs
        assert type(scores) is list, scores
        assert type(mu) is list, mu
        assert issubdtype(type(mu_criterion), floating), mu_criterion
        assert issubdtype(type(beta), floating), beta
        assert issubdtype(type(num_RC), integer), (type(num_RC), num_RC)
        assert num_RC >= min(num_RCs), (num_RC, num_RCs)
        assert num_RC <= max(num_RCs), (num_RC, num_RCs)
        assert type(lower_limit) is int, lower_limit
        assert type(upper_limit) is int, upper_limit
        assert "max_x" in kwargs

        self._series.append(kwargs)
        x: list = num_RCs

        y: list = mu
        dpg.bind_item_theme(
            dpg.add_scatter_series(
                x=x,
                y=y,
                label="µ",
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
            dpg.add_line_series(
                x=[min(x) - 2, max(x) + 2],
                y=[mu_criterion] * 2,
                label="µ-crit.",
                parent=self._y_axis_1,
            ),
            themes.suggestion_method.highlight,
        )

        dpg.bind_item_theme(
            dpg.add_shade_series(
                x=[lower_limit, upper_limit],
                y1=[-0.1] * 2,
                y2=[1.1] * 2,
                label="Limits",
                parent=self._y_axis_3,
            ),
            themes.suggestion_method.range,
        )

        if beta <= 0.0:
            return

        y = scores
        dpg.bind_item_theme(
            dpg.add_scatter_series(
                x=x,
                y=y,
                label="S",
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

        if len(self._series) < 1:
            return

        min_num_RC: int = 1
        max_num_RC: int = 2
        min_score: Optional[float] = None
        max_score: Optional[float] = None

        for kwargs in self._series:
            num_RCs: List[int] = kwargs["num_RCs"]
            min_num_RC = min(num_RCs) - 1
            max_num_RC = kwargs["max_x"]

            scores: List[float] = kwargs["scores"]
            if min_score is None or min(scores) < min_score:
                min_score = floor(min(scores))
            if max_score is None or max(scores) > max_score:
                max_score = ceil(max(scores))

        if min_score is None:
            min_score = 0.0

        if max_score is None:
            max_score = 1.0

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
            ymin=min_score - 0.1,
            ymax=max_score + 0.1,
        )
        dpg.set_axis_limits(
            self._y_axis_3,
            ymin=0.0,
            ymax=1.0,
        )

        dpg.split_frame(delay=33)
        dpg.set_axis_limits_auto(self._x_axis)
        dpg.set_axis_limits_auto(self._y_axis_1)
        dpg.set_axis_limits_auto(self._y_axis_2)


class Method2(Plot):
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
            self._x_axis: Tag = dpg.add_plot_axis(
                dpg.mvXAxis,
                label="Number of RC elements",
            )
            self._y_axis_1: Tag = dpg.add_plot_axis(
                dpg.mvYAxis,
                label="Norm of fitted variables",
                no_gridlines=True,
                log_scale=True,
            )
            self._y_axis_2: Tag = dpg.add_plot_axis(
                dpg.mvYAxis,
                label=None,
                no_gridlines=True,
                no_tick_labels=True,
                no_tick_marks=True,
            )

        dpg.bind_item_theme(self._plot, themes.plot)
        dpg.bind_item_handler_registry(self._plot, self._item_handler)

    def clear(self, *args, **kwargs):
        dpg.delete_item(self._y_axis_1, children_only=True)
        dpg.delete_item(self._y_axis_2, children_only=True)
        self._series.clear()

    def update(self, num_RC: int):
        assert type(num_RC) is int and num_RC >= 0, num_RC
        if len(self._series) < 1:
            return

        x: list = self._series[0]["num_RCs"]
        y: list = self._series[0]["norms"]
        dpg.set_value(
            dpg.get_item_children(self._y_axis_1, slot=1)[1],
            [[num_RC], [y[x.index(num_RC)]]],
        )

    def plot(self, *args, **kwargs):
        assert len(args) == 0, args

        num_RCs: List[int] = kwargs["num_RCs"]
        norms: List[float] = kwargs["norms"]
        num_RC: int = kwargs["num_RC"]
        lower_limit: int = kwargs["lower_limit"]
        upper_limit: int = kwargs["upper_limit"]

        assert type(num_RCs) is list, num_RCs
        assert type(norms) is list, norms
        assert issubdtype(type(num_RC), integer), (type(num_RC), num_RC)
        assert num_RC >= min(num_RCs), (num_RC, num_RCs)
        assert num_RC <= max(num_RCs), (num_RC, num_RCs)
        assert type(lower_limit) is int, lower_limit
        assert type(upper_limit) is int, upper_limit
        assert "max_x" in kwargs

        self._series.append(kwargs)
        x: list = num_RCs

        y: list = norms
        dpg.bind_item_theme(
            dpg.add_scatter_series(
                x=x,
                y=y,
                label="Norm",
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
                y1=[-0.1] * 2,
                y2=[1.1] * 2,
                label="Limits",
                parent=self._y_axis_2,
            ),
            themes.suggestion_method.range,
        )

    def adjust_limits(self):
        if not self.is_visible():
            self.queue_limits_adjustment()
            return
        elif self.are_limits_adjusted():
            return
        else:
            self.limits_adjusted()

        if len(self._series) < 1:
            return

        min_num_RC: int = 1
        max_num_RC: int = 2
        minimum: Optional[float] = None
        maximum: Optional[float] = None

        for kwargs in self._series:
            num_RCs: List[int] = kwargs["num_RCs"]
            min_num_RC = min(num_RCs) - 1
            max_num_RC = kwargs["max_x"]

            norms: List[float] = kwargs["norms"]
            if minimum is None or min(norms) < minimum:
                minimum = min(norms)
            if maximum is None or max(norms) > maximum:
                maximum = max(norms)

        if minimum is None:
            minimum = 1e-1

        if maximum is None:
            maximum = 1e1

        dpg.split_frame()
        dpg.set_axis_limits(
            self._x_axis,
            ymin=min_num_RC,
            ymax=max_num_RC,
        )
        dpg.set_axis_limits(
            self._y_axis_1,
            ymin=minimum / 10,
            ymax=maximum * 10,
        )
        dpg.set_axis_limits(
            self._y_axis_2,
            ymin=0.0,
            ymax=1.0,
        )

        dpg.split_frame(delay=33)
        dpg.set_axis_limits_auto(self._x_axis)
        dpg.set_axis_limits_auto(self._y_axis_1)


class Method3(Plot):
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
            self._x_axis: Tag = dpg.add_plot_axis(
                dpg.mvXAxis,
                label="Number of RC elements",
            )
            self._y_axis_1: Tag = dpg.add_plot_axis(
                dpg.mvYAxis,
                label="Norm of curvatures",
                no_gridlines=True,
                log_scale=True,
            )
            self._y_axis_2: Tag = dpg.add_plot_axis(
                dpg.mvYAxis,
                label=None,
                no_gridlines=True,
                no_tick_labels=True,
                no_tick_marks=True,
            )

        dpg.bind_item_theme(self._plot, themes.plot)
        dpg.bind_item_handler_registry(self._plot, self._item_handler)

    def clear(self, *args, **kwargs):
        dpg.delete_item(self._y_axis_1, children_only=True)
        dpg.delete_item(self._y_axis_2, children_only=True)
        self._series.clear()

    def update(self, num_RC: int):
        assert type(num_RC) is int and num_RC >= 0, num_RC
        if len(self._series) < 1:
            return

        x: list = self._series[0]["num_RCs"]
        y: list = self._series[0]["norms"]
        dpg.set_value(
            dpg.get_item_children(self._y_axis_1, slot=1)[1],
            [[num_RC], [y[x.index(num_RC)]]],
        )

    def plot(self, *args, **kwargs):
        assert len(args) == 0, args

        num_RCs: List[int] = kwargs["num_RCs"]
        norms: List[float] = kwargs["norms"]
        num_RC: int = kwargs["num_RC"]
        lower_limit: int = kwargs["lower_limit"]
        upper_limit: int = kwargs["upper_limit"]

        assert type(num_RCs) is list, num_RCs
        assert type(norms) is list, norms
        assert issubdtype(type(num_RC), integer), (type(num_RC), num_RC)
        assert num_RC >= min(num_RCs), (num_RC, num_RCs)
        assert num_RC <= max(num_RCs), (num_RC, num_RCs)
        assert type(lower_limit) is int, lower_limit
        assert type(upper_limit) is int, upper_limit
        assert "max_x" in kwargs

        self._series.append(kwargs)
        x: list = num_RCs

        y: list = norms
        dpg.bind_item_theme(
            dpg.add_scatter_series(
                x=x,
                y=y,
                label="Norm",
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
                y1=[-0.1] * 2,
                y2=[1.1] * 2,
                label="Limits",
                parent=self._y_axis_2,
            ),
            themes.suggestion_method.range,
        )

    def adjust_limits(self):
        if not self.is_visible():
            self.queue_limits_adjustment()
            return
        elif self.are_limits_adjusted():
            return
        else:
            self.limits_adjusted()

        if len(self._series) < 1:
            return

        min_num_RC: int = 1
        max_num_RC: int = 2
        minimum: Optional[float] = None
        maximum: Optional[float] = None

        for kwargs in self._series:
            num_RCs: List[int] = kwargs["num_RCs"]
            min_num_RC = min(num_RCs) - 1
            max_num_RC = kwargs["max_x"]

            norms: List[float] = kwargs["norms"]
            if minimum is None or min(norms) < minimum:
                minimum = floor(min(norms))
            if maximum is None or max(norms) > maximum:
                maximum = ceil(max(norms))

        if minimum is None:
            minimum = 1e-1

        if maximum is None:
            maximum = 1e1

        dpg.split_frame()
        dpg.set_axis_limits(
            self._x_axis,
            ymin=min_num_RC,
            ymax=max_num_RC,
        )
        dpg.set_axis_limits(
            self._y_axis_1,
            ymin=minimum / 10,
            ymax=maximum * 10,
        )
        dpg.set_axis_limits(
            self._y_axis_2,
            ymin=0.0,
            ymax=1.0,
        )

        dpg.split_frame(delay=33)
        dpg.set_axis_limits_auto(self._x_axis)
        dpg.set_axis_limits_auto(self._y_axis_1)


class Method4(Plot):
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
            self._x_axis: Tag = dpg.add_plot_axis(
                dpg.mvXAxis,
                label="Number of RC elements",
            )
            self._y_axis_1: Tag = dpg.add_plot_axis(
                dpg.mvYAxis,
                label="Number of sign changes",
                no_gridlines=True,
            )
            self._y_axis_2: Tag = dpg.add_plot_axis(
                dpg.mvYAxis,
                label=None,
                no_gridlines=True,
                no_tick_labels=True,
                no_tick_marks=True,
            )

        dpg.bind_item_theme(self._plot, themes.plot)
        dpg.bind_item_handler_registry(self._plot, self._item_handler)

    def clear(self, *args, **kwargs):
        dpg.delete_item(self._y_axis_1, children_only=True)
        dpg.delete_item(self._y_axis_2, children_only=True)
        self._series.clear()

    def update(self, num_RC: int):
        assert type(num_RC) is int and num_RC >= 0, num_RC
        if len(self._series) < 1:
            return

        x: list = self._series[0]["num_RCs"]
        y: list = self._series[0]["num_sign_changes"]
        dpg.set_value(
            dpg.get_item_children(self._y_axis_1, slot=1)[1],
            [[num_RC], [y[x.index(num_RC)]]],
        )

    def plot(self, *args, **kwargs):
        assert len(args) == 0, args

        num_RCs: List[int] = kwargs["num_RCs"]
        num_sign_changes: List[float] = kwargs["num_sign_changes"]
        num_RC: int = kwargs["num_RC"]
        lower_limit: int = kwargs["lower_limit"]
        upper_limit: int = kwargs["upper_limit"]

        assert type(num_RCs) is list, num_RCs
        assert type(num_sign_changes) is list, num_sign_changes
        assert issubdtype(type(num_RC), integer), (type(num_RC), num_RC)
        assert num_RC >= min(num_RCs), (num_RC, num_RCs)
        assert num_RC <= max(num_RCs), (num_RC, num_RCs)
        assert type(lower_limit) is int, lower_limit
        assert type(upper_limit) is int, upper_limit
        assert "max_x" in kwargs

        self._series.append(kwargs)
        x: list = num_RCs

        y: list = num_sign_changes
        dpg.bind_item_theme(
            dpg.add_scatter_series(
                x=x,
                y=y,
                label="Num. sign changes",
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
                y1=[-0.1] * 2,
                y2=[1.1] * 2,
                label="Limits",
                parent=self._y_axis_2,
            ),
            themes.suggestion_method.range,
        )

    def adjust_limits(self):
        if not self.is_visible():
            self.queue_limits_adjustment()
            return
        elif self.are_limits_adjusted():
            return
        else:
            self.limits_adjusted()

        if len(self._series) < 1:
            return

        min_num_RC: int = 1
        max_num_RC: int = 2
        minimum: float = 0.0
        maximum: Optional[float] = None

        for kwargs in self._series:
            num_RCs: List[int] = kwargs["num_RCs"]
            min_num_RC = min(num_RCs) - 1
            max_num_RC = kwargs["max_x"]

            num_sign_changes: List[float] = kwargs["num_sign_changes"]
            if maximum is None or max(num_sign_changes) > maximum:
                maximum = ceil(max(num_sign_changes))

        if maximum is None:
            maximum = 1.0

        dpg.split_frame()
        dpg.set_axis_limits(
            self._x_axis,
            ymin=min_num_RC,
            ymax=max_num_RC,
        )
        dpg.set_axis_limits(
            self._y_axis_1,
            ymin=minimum,
            ymax=maximum + 1,
        )
        dpg.set_axis_limits(
            self._y_axis_2,
            ymin=0.0,
            ymax=1.0,
        )

        dpg.split_frame(delay=33)
        dpg.set_axis_limits_auto(self._x_axis)
        dpg.set_axis_limits_auto(self._y_axis_1)


class Method5(Plot):
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
            self._x_axis: Tag = dpg.add_plot_axis(
                dpg.mvXAxis,
                label="Number of RC elements",
            )
            self._y_axis_1: Tag = dpg.add_plot_axis(
                dpg.mvYAxis,
                label="Mean sign change distance",
                no_gridlines=True,
            )
            self._y_axis_2: Tag = dpg.add_plot_axis(
                dpg.mvYAxis,
                label=None,
                no_gridlines=True,
                no_tick_labels=True,
                no_tick_marks=True,
            )

        dpg.bind_item_theme(self._plot, themes.plot)
        dpg.bind_item_handler_registry(self._plot, self._item_handler)

    def clear(self, *args, **kwargs):
        dpg.delete_item(self._y_axis_1, children_only=True)
        dpg.delete_item(self._y_axis_2, children_only=True)
        self._series.clear()

    def update(self, num_RC: int):
        assert type(num_RC) is int and num_RC >= 0, num_RC
        if len(self._series) < 1:
            return

        x: list = self._series[0]["num_RCs"]
        y: list = self._series[0]["mean_distances"]
        dpg.set_value(
            dpg.get_item_children(self._y_axis_1, slot=1)[1],
            [[num_RC], [y[x.index(num_RC)]]],
        )

    def plot(self, *args, **kwargs):
        assert len(args) == 0, args

        num_RCs: List[int] = kwargs["num_RCs"]
        mean_distances: List[float] = kwargs["mean_distances"]
        num_RC: int = kwargs["num_RC"]
        lower_limit: int = kwargs["lower_limit"]
        upper_limit: int = kwargs["upper_limit"]

        assert type(num_RCs) is list, num_RCs
        assert type(mean_distances) is list, mean_distances
        assert issubdtype(type(num_RC), integer), (type(num_RC), num_RC)
        assert num_RC >= min(num_RCs), (num_RC, num_RCs)
        assert num_RC <= max(num_RCs), (num_RC, num_RCs)
        assert type(lower_limit) is int, lower_limit
        assert type(upper_limit) is int, upper_limit
        assert "max_x" in kwargs

        self._series.append(kwargs)
        x: list = num_RCs

        y: list = mean_distances
        dpg.bind_item_theme(
            dpg.add_scatter_series(
                x=x,
                y=y,
                label="Mean",
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
                y1=[-0.1] * 2,
                y2=[1.1] * 2,
                label="Limits",
                parent=self._y_axis_2,
            ),
            themes.suggestion_method.range,
        )

    def adjust_limits(self):
        if not self.is_visible():
            self.queue_limits_adjustment()
            return
        elif self.are_limits_adjusted():
            return
        else:
            self.limits_adjusted()

        if len(self._series) < 1:
            return

        min_num_RC: int = 1
        max_num_RC: int = 2
        minimum: float = 0.0
        maximum: Optional[float] = None

        for kwargs in self._series:
            num_RCs: List[int] = kwargs["num_RCs"]
            min_num_RC = min(num_RCs) - 1
            max_num_RC = kwargs["max_x"]

            mean_distances: List[float] = kwargs["mean_distances"]
            if maximum is None or max(mean_distances) > maximum:
                maximum = ceil(max(mean_distances))

        if maximum is None:
            maximum = 1.0

        dpg.split_frame()
        dpg.set_axis_limits(
            self._x_axis,
            ymin=min_num_RC,
            ymax=max_num_RC,
        )
        dpg.set_axis_limits(
            self._y_axis_1,
            ymin=minimum,
            ymax=maximum + 1,
        )
        dpg.set_axis_limits(
            self._y_axis_2,
            ymin=0.0,
            ymax=1.0,
        )

        dpg.split_frame(delay=33)
        dpg.set_axis_limits_auto(self._x_axis)
        dpg.set_axis_limits_auto(self._y_axis_1)


class Method6(Plot):
    def __init__(self, width: int = -1, height: int = -1, *args, **kwargs):
        assert type(width) is int, width
        assert type(height) is int, height
        super().__init__()
        admittance: bool = kwargs.get("admittance", False)
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
            )
            self._y_axis_1: Tag = dpg.add_plot_axis(
                dpg.mvYAxis,
                label="?",
                no_gridlines=True,
            )
            self._y_axis_2: Tag = dpg.add_plot_axis(
                dpg.mvYAxis,
                label=None,
                no_gridlines=True,
                no_tick_labels=True,
                no_tick_marks=True,
            )

        dpg.bind_item_theme(self._plot, themes.plot)
        dpg.bind_item_handler_registry(self._plot, self._item_handler)

    def clear(self, *args, **kwargs):
        dpg.delete_item(self._y_axis_1, children_only=True)
        dpg.delete_item(self._y_axis_2, children_only=True)
        self._series.clear()

    def update(self, num_RC: int):
        assert type(num_RC) is int and num_RC >= 0, num_RC
        if len(self._series) < 1:
            return

        x: list = self._series[0]["num_RCs"]
        y: list = self._series[0]["data"]
        dpg.set_value(
            dpg.get_item_children(self._y_axis_1, slot=1)[1],
            [[num_RC], [y[x.index(num_RC)]]],
        )

    def plot(self, *args, **kwargs):
        assert len(args) == 0, args

        num_RCs: List[int] = kwargs["num_RCs"]
        data: List[float] = kwargs["data"]
        fit_x: List[float] = kwargs["fit_x"]
        fit_y: List[float] = kwargs["fit_y"]
        num_RC: int = kwargs["num_RC"]
        lower_limit: int = kwargs["lower_limit"]
        upper_limit: int = kwargs["upper_limit"]
        admittance: bool = kwargs["admittance"]

        assert type(num_RCs) is list, num_RCs
        assert type(data) is list, data
        assert type(fit_x) is list, fit_x
        assert type(fit_y) is list, fit_y
        assert issubdtype(type(num_RC), integer), (type(num_RC), num_RC)
        assert num_RC >= min(num_RCs), (num_RC, num_RCs)
        assert num_RC <= max(num_RCs), (num_RC, num_RCs)
        assert type(lower_limit) is int, lower_limit
        assert type(upper_limit) is int, upper_limit
        assert type(admittance) is bool, admittance
        assert "max_x" in kwargs

        dpg.set_item_label(
            self._y_axis_1,
            "log(sum(abs(tau_k/C_k)))"
            if admittance is True
            else "log(sum(abs(tau_k/R_k)))",
        )

        self._series.append(kwargs)
        x: list = num_RCs

        y: list = data
        dpg.bind_item_theme(
            dpg.add_scatter_series(
                x=x,
                y=y,
                label="Data",
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
            dpg.add_line_series(
                x=fit_x,
                y=fit_y,
                label="Fit",
                parent=self._y_axis_1,
            ),
            themes.pseudo_chisqr.default,
        )

        dpg.bind_item_theme(
            dpg.add_shade_series(
                x=[lower_limit, upper_limit],
                y1=[-0.1] * 2,
                y2=[1.1] * 2,
                label="Limits",
                parent=self._y_axis_2,
            ),
            themes.suggestion_method.range,
        )

    def adjust_limits(self):
        if not self.is_visible():
            self.queue_limits_adjustment()
            return
        elif self.are_limits_adjusted():
            return
        else:
            self.limits_adjusted()

        if len(self._series) < 1:
            return

        min_num_RC: int = 1
        max_num_RC: int = 2
        minimum: Optional[float] = None
        maximum: Optional[float] = None

        for kwargs in self._series:
            num_RCs: List[int] = kwargs["num_RCs"]
            min_num_RC = min(num_RCs) - 1
            max_num_RC = kwargs["max_x"]

            data: List[float] = kwargs["data"]
            if minimum is None or min(data) < minimum:
                minimum = floor(min(data))
            if maximum is None or max(data) > maximum:
                maximum = ceil(max(data))

        if minimum is None:
            minimum = 1e-1

        if maximum is None:
            maximum = 1e1

        dpg.split_frame()
        dpg.set_axis_limits(
            self._x_axis,
            ymin=min_num_RC,
            ymax=max_num_RC,
        )
        dpg.set_axis_limits(
            self._y_axis_1,
            ymin=minimum - 1,
            ymax=maximum + 1,
        )
        dpg.set_axis_limits(
            self._y_axis_2,
            ymin=0.0,
            ymax=1.0,
        )

        dpg.split_frame(delay=33)
        dpg.set_axis_limits_auto(self._x_axis)
        dpg.set_axis_limits_auto(self._y_axis_1)
