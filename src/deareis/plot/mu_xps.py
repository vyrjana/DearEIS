# Copyright 2022 DearEIS developers
# DearEIS is licensed under the GPLv3 or later (https://www.gnu.org/licenses/gpl-3.0.html).
# The licenses of DearEIS' dependencies and/or sources of portions of code are included in
# the LICENSES folder.

import dearpygui.dearpygui as dpg
from numpy import ndarray
from typing import List, Optional, Tuple
from deareis.plot.shared import Plot, line, scatter
import deareis.themes as themes
from dataclasses import dataclass


@dataclass
class MuXpsSettings:
    show_legend: bool
    outside_legend: bool
    horizontal_legend: bool
    legend_location: int
    mu_crit_theme: int
    mu_theme: int
    xps_theme: int


class MuXpsPlot(Plot):
    def __init__(self, plot: int):
        assert type(plot) is int and plot >= 0
        super().__init__(plot)
        self.x_axis: int
        self.y_axis_1: int
        self.y_axis_2: int
        self.x_axis, self.y_axis_1, self.y_axis_2 = self._setup_plot(self.plot)
        self.freq: Optional[ndarray] = None
        self.real: Optional[ndarray] = None
        self.imag: Optional[ndarray] = None

    def _setup_plot(self, plot: int) -> Tuple[int, int, int]:
        assert type(plot) is int and plot >= 0
        dpg.add_plot_legend(
            outside=False,
            horizontal=True,
            location=dpg.mvPlot_Location_North,
            parent=plot,
        )
        x_axis: int = dpg.add_plot_axis(
            dpg.mvXAxis, label="num. RC circuits", parent=plot
        )
        y_axis_1: int = dpg.add_plot_axis(dpg.mvYAxis, label="µ", parent=plot)
        y_axis_2: int = dpg.add_plot_axis(
            dpg.mvYAxis, label="log X² (pseudo)", parent=plot
        )
        dpg.configure_item(plot, crosshairs=True)
        return (
            x_axis,
            y_axis_1,
            y_axis_2,
        )

    def clear_plot(self):
        self.num_RCs, self.mu, self.xps = None, None, None
        self.mu_criterion, self.highlighted_num_RC = None, None
        dpg.delete_item(self.x_axis, children_only=True)
        dpg.delete_item(self.y_axis_1, children_only=True)
        dpg.delete_item(self.y_axis_2, children_only=True)

    def plot_data(
        self,
        num_RCs: ndarray,
        mu: ndarray,
        xps: ndarray,
        mu_criterion: float,
        highlighted_num_RC: int,
    ):
        assert type(num_RCs) is ndarray
        assert type(mu) is ndarray
        assert type(xps) is ndarray
        assert type(mu_criterion) is float
        assert type(highlighted_num_RC) is int
        # Mu-value
        line(num_RCs, mu, "µ", self.y_axis_1, themes.exploratory_mu)
        scatter(num_RCs, mu, None, self.y_axis_1, themes.exploratory_mu)
        line(
            [num_RCs[0] - 1, num_RCs[-1] + 1],
            [mu_criterion, mu_criterion],
            "µ-criterion",
            self.y_axis_1,
            themes.exploratory_mu_criterion,
        )
        # Pseudo chi-squared
        line(
            num_RCs,
            xps,
            "X²",
            self.y_axis_2,
            themes.exploratory_xps,
        )
        scatter(num_RCs, xps, None, self.y_axis_2, themes.exploratory_xps)
        # Highlight
        x: List[int] = [highlighted_num_RC, highlighted_num_RC]
        line(x, [-0.1, 1.1], None, self.y_axis_1, themes.exploratory_mu_criterion)
        index: int = [i for i, _ in enumerate(num_RCs) if _ == highlighted_num_RC][0]
        x = [highlighted_num_RC]
        scatter(x, [mu[index]], None, self.y_axis_1, themes.exploratory_mu_highlight)
        scatter(x, [xps[index]], None, self.y_axis_2, themes.exploratory_xps_highlight)
        # Update limits
        dpg.set_axis_limits(self.x_axis, ymin=num_RCs[0] - 0.5, ymax=num_RCs[-1] + 0.5)
        dpg.set_axis_limits(self.y_axis_1, ymin=-0.1, ymax=1.1)
        dpg.set_axis_limits(self.y_axis_2, ymin=min(xps) - 0.2, ymax=max(xps) + 0.2)
