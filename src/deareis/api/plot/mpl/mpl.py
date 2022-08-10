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

from inspect import signature
from typing import (
    Dict,
    List,
    Optional,
    Tuple,
    Union,
)
import dearpygui.dearpygui as dpg
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from numpy import (
    floating,
    integer,
    issubdtype,
    ndarray,
)
from deareis.data import (
    DataSet,
    FitResult,
    PlotSeries,
    PlotSettings,
    Project,
    SimulationResult,
    TestResult,
)
from deareis.enums import PlotType


MPL_MARKERS: Dict[int, str] = {
    dpg.mvPlotMarker_Down: "v",
    dpg.mvPlotMarker_Left: "<",
    dpg.mvPlotMarker_Right: ">",
    dpg.mvPlotMarker_Up: "^",
    dpg.mvPlotMarker_Asterisk: "*",
    dpg.mvPlotMarker_Circle: "o",
    dpg.mvPlotMarker_Cross: "x",
    dpg.mvPlotMarker_Diamond: "D",
    dpg.mvPlotMarker_Plus: "+",
    dpg.mvPlotMarker_Square: "s",
}

_UNFILLED_MARKERS: List[int] = [
    dpg.mvPlotMarker_Cross,
    dpg.mvPlotMarker_Plus,
]


def plot(
    settings: PlotSettings,
    project: Project,
    x_limits: Optional[Tuple[Optional[float], Optional[float]]] = None,
    y_limits: Optional[Tuple[Optional[float], Optional[float]]] = None,
    show_title: bool = True,
    show_legend: Optional[bool] = None,
    legend_loc: Union[int, str] = 0,
    show_grid: bool = False,
    tight_layout: bool = False,
    fig: Optional[Figure] = None,
    axis: Optional[Axes] = None,
    num_per_decade: int = 100,
) -> Tuple[Figure, Axes]:
    """
    Plot a complex plot containing one or more items from a project based on the provided settings.

    Parameters
    ----------
    settings: PlotSettings
        The settings for the plot.

    project: Project
        The project that the plot is a part of.

    x_limits: Optional[Tuple[Optional[float], Optional[float]]] = None
        The lower and upper limits of the x-axis.

    y_limits: Optional[Tuple[Optional[float], Optional[float]]] = None
        The lower and upper limits of the y-axis.

    show_title: bool = True
        Whether or not to include the title in the figure.

    show_legend: Optional[bool] = None
        Whether or not to include a legend in the figure.

    legend_loc: Union[int, str] = 0
        The position of the legend in the figure. See matplotlib's documentation for valid values.

    show_grid: bool = False
        Whether or not to include a grid in the figure.

    tight_layout: bool = False
        Whether or not to apply a tight layout that the sizes of the reduces margins.

    fig: Optional[Figure] = None
        The matplotlib.figure.Figure instance to use when plotting the data.

    axis: Optional[Axes] = None
        The matplotlib.axes.Axes instance to use when plotting the data.

    num_per_decade: int = 100
        If any circuit fits, circuit simulations, or Kramers-Kronig test results are included in the plot, then this parameter can be used to change how many points are used to draw the line (i.e. how smooth or angular the line looks).
    """
    assert type(settings) is PlotSettings, settings
    assert type(project) is Project, project
    assert x_limits is None or (
        type(x_limits) is tuple
        and len(x_limits) == 2
        and all(
            map(
                lambda _: _ is None
                or issubdtype(type(_), integer)
                or issubdtype(type(_), floating),
                x_limits,
            )
        )
    ), x_limits
    assert y_limits is None or (
        type(y_limits) is tuple
        and len(y_limits) == 2
        and all(
            map(
                lambda _: _ is None
                or issubdtype(type(_), integer)
                or issubdtype(type(_), floating),
                y_limits,
            )
        )
    ), y_limits
    assert type(show_title) is bool, show_title
    assert type(show_legend) is bool or show_legend is None, show_legend
    assert issubdtype(type(legend_loc), integer) or type(legend_loc) is str, legend_loc
    assert type(show_grid) is bool, show_grid
    assert type(tight_layout) is bool, tight_layout
    assert type(fig) is Figure or fig is None
    if fig is None:
        fig, axis = plt.subplots()
    assert axis is not None
    assert (
        issubdtype(type(num_per_decade), integer) and num_per_decade >= 1
    ), num_per_decade
    plot_type: PlotType = settings.get_type()
    uuid: str
    for uuid in settings.series_order:
        series: Optional[Union[DataSet, TestResult, FitResult, SimulationResult]]
        series = settings.find_series(
            uuid,
            project.get_data_sets(),
            project.get_all_tests(),
            project.get_all_fits(),
            project.get_simulations(),
        )
        if series is None:
            continue
        label: Optional[str] = settings.get_series_label(uuid) or series.get_label()
        if label.strip() == "" and label != "":  # type: ignore
            label = None
        if label is not None and show_legend is None:
            show_legend = True
        color: List[float] = list(
            map(lambda _: _ / 255.0, settings.get_series_color(uuid))
        )
        has_line: bool = settings.get_series_line(uuid)
        marker: Optional[str] = MPL_MARKERS.get(settings.get_series_marker(uuid))
        scatter_data: List[ndarray] = []
        line_data: List[ndarray] = []
        if plot_type == PlotType.NYQUIST:
            if "num_per_decade" in signature(series.get_nyquist_data).parameters:
                x, y = series.get_nyquist_data(num_per_decade=num_per_decade)  # type: ignore
                line_data = [x, y]
                x, y = series.get_nyquist_data()
                scatter_data = [x, y]
            else:
                x, y = series.get_nyquist_data()
                line_data = [x, y]
                scatter_data = [x, y]
        elif plot_type == PlotType.BODE_MAGNITUDE:
            if "num_per_decade" in signature(series.get_bode_data).parameters:
                x, y, _ = series.get_bode_data(num_per_decade=num_per_decade)  # type: ignore
                line_data = [x, y]
                x, y, _ = series.get_bode_data()
                scatter_data = [x, y]
            else:
                x, y, _ = series.get_bode_data()
                line_data = [x, y]
                scatter_data = [x, y]
        elif plot_type == PlotType.BODE_PHASE:
            if "num_per_decade" in signature(series.get_bode_data).parameters:
                x, _, y = series.get_bode_data(num_per_decade=num_per_decade)  # type: ignore
                line_data = [x, y]
                x, _, y = series.get_bode_data()
                scatter_data = [x, y]
            else:
                x, _, y = series.get_bode_data()
                line_data = [x, y]
                scatter_data = [x, y]
        else:
            raise Exception(f"Unsupported plot type: {plot_type}")
        assert len(line_data) > 0 or len(scatter_data) > 0
        colors: dict = {}
        if settings.get_series_marker(uuid) in _UNFILLED_MARKERS:
            colors.update(
                {
                    "color": color,
                }
            )
        else:
            colors.update(
                {
                    "edgecolor": color,
                    "facecolor": "none",
                }
            )
        if marker is not None and has_line:
            axis.plot(*line_data, label=label, color=color)
            axis.scatter(
                *scatter_data,
                marker=marker,
                **colors,
            )
        elif has_line:
            axis.plot(*line_data, label=label, color=color)
        elif marker is not None:
            axis.scatter(
                *scatter_data,
                label=label,
                marker=marker,
                **colors,
            )
    if x_limits is not None:
        axis.set_xlim(x_limits)
    if y_limits is not None:
        axis.set_ylim(y_limits)
    if show_title and settings.get_label() != "":
        fig.suptitle(settings.get_label())
    if plot_type == PlotType.NYQUIST:
        axis.set_xlabel(r"$Z_{\rm re}$ ($\Omega$)")
        axis.set_ylabel(r"$-Z_{\rm im}$ ($\Omega$)")
        axis.set_aspect("equal")
    elif plot_type == PlotType.BODE_MAGNITUDE:
        axis.set_xlabel(r"$\log{f}$")
        axis.set_ylabel(r"$\log{|Z|}$")
    elif plot_type == PlotType.BODE_PHASE:
        axis.set_xlabel(r"$\log{f}$")
        axis.set_ylabel(r"$-\phi$ ($^\circ$)")
    if show_legend:
        axis.legend(loc=legend_loc)
    axis.grid(visible=show_grid)
    if tight_layout:
        fig.tight_layout()
    return (
        fig,
        axis,
    )