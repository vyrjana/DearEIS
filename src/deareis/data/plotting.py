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

from dataclasses import dataclass
from typing import (
    Callable,
    Dict,
    List,
    Optional,
    Union,
)
import dearpygui.dearpygui as dpg
from numpy import ndarray
from deareis.data import DataSet
from deareis.data.kramers_kronig import TestResult
from deareis.data.fitting import FitResult
from deareis.data.simulation import SimulationResult
from deareis.enums import PlotType
from deareis.themes import (
    create_plot_series_theme,
    get_random_color_marker,
    update_plot_series_theme_color,
    update_plot_series_theme_marker,
)


@dataclass(frozen=True)
class PlotSeries:
    """
    A class that represents the data used to plot an item/series.
    """

    label: str
    scatter_data: List[ndarray]
    line_data: List[ndarray]
    color: List[float]
    marker: int
    line: bool
    legend: bool

    def __repr__(self) -> str:
        return f"PlotSeries ({self.get_label()}, {hex(id(self))})"

    def get_label(self) -> str:
        return self.label

    def get_scatter_data(self) -> List[ndarray]:
        return self.scatter_data

    def get_line_data(self) -> List[ndarray]:
        return self.line_data

    def get_color(self) -> List[float]:
        return self.color

    def get_marker(self) -> int:
        return self.marker

    def has_markers(self) -> bool:
        return self.marker >= 0

    def has_line(self) -> bool:
        return self.line

    def has_legend(self) -> bool:
        return self.legend


VERSION: int = 1


# TODO: Make it possible to (re)store the limits of plots (e.g. from session to session)?
@dataclass
class PlotSettings:
    """
    A class representing a complex plot that can contain one or more data sets, Kramers-Kronig test results, equivalent circuit fitting results, and simulation results.
    """

    plot_label: str
    plot_type: PlotType
    series_order: List[str]  # UUID
    labels: Dict[str, str]  # UUID: label
    colors: Dict[str, List[float]]  # UUID: RGBA
    markers: Dict[str, int]  # UUID: enum
    # TODO: Add a toggle for filled markers
    # filled_markers: Dict[str, bool]
    # TODO: Replace show_lines with lines (UUID: enum)?
    # lines: Dict[str, int]
    show_lines: Dict[str, bool]  # UUID: flag
    themes: Dict[str, int]  # UUID: DPG UUID
    uuid: str

    def __eq__(self, other) -> bool:
        try:
            assert isinstance(other, type(self)), other
            assert self.uuid == other.uuid, (
                self.uuid,
                other.uuid,
            )
            assert self.get_label() == other.get_label(), (
                self.get_label(),
                other.get_label(),
            )
            assert self.get_type() == other.get_type(), (
                self.get_type(),
                other.get_type(),
            )
            assert ",".join(self.series_order) == ",".join(other.series_order), (
                self.series_order,
                other.series_order,
            )
            key: str
            for key in self.labels:
                assert key in other.labels
                assert self.labels[key] == other.labels[key]
            for key in self.colors:
                assert key in other.colors
                assert self.colors[key] == other.colors[key]
            for key in self.markers:
                assert key in other.markers
                assert self.markers[key] == other.markers[key]
            for key in self.show_lines:
                assert key in other.show_lines
                assert self.show_lines[key] == other.show_lines[key]
        except AssertionError:
            return False
        return True

    def __repr__(self) -> str:
        return f"PlotSettings ({self.get_label()}, {hex(id(self))})"

    @staticmethod
    def _parse_v1(dictionary: dict) -> dict:
        assert type(dictionary) is dict, dictionary
        return {
            "uuid": dictionary["uuid"],
            "plot_label": dictionary["plot_label"],
            "plot_type": PlotType(dictionary["plot_type"]),
            "series_order": dictionary["series_order"],
            "labels": dictionary["labels"],
            "colors": dictionary["colors"],
            "markers": dictionary["markers"],
            "show_lines": dictionary["show_lines"],
            "themes": dictionary["themes"],
        }

    def recreate_themes(self):
        uuid: str
        for uuid in list(self.themes.keys()):
            item: int = self.themes[uuid]
            if item < 0:
                self.themes[uuid] = dpg.generate_uuid()
                create_plot_series_theme(
                    self.colors[uuid],
                    self.markers[uuid] if self.markers[uuid] >= 0 else 0,
                    self.themes[uuid],
                )
            else:
                if not dpg.does_item_exist(self.themes[uuid]):
                    del self.labels[uuid]
                    del self.colors[uuid]
                    del self.markers[uuid]
                    del self.show_lines[uuid]
                    del self.themes[uuid]
                else:
                    update_plot_series_theme_color(self.themes[uuid], self.colors[uuid])
                    update_plot_series_theme_marker(
                        self.themes[uuid], self.markers[uuid]
                    )

    @classmethod
    def from_dict(Class, dictionary: dict) -> "PlotSettings":
        assert type(dictionary) is dict, dictionary
        assert "version" in dictionary
        version: int = dictionary["version"]
        assert version <= VERSION, f"{version=} > {VERSION=}"
        parsers: Dict[int, Callable] = {
            1: Class._parse_v1,
        }
        assert version in parsers, f"{version=} not in {parsers.keys()=}"
        settings = Class(**parsers[version](dictionary))
        settings.recreate_themes()
        return settings

    def to_dict(self, session: bool) -> dict:
        return {
            "uuid": self.uuid,
            "version": VERSION,
            "plot_label": self.plot_label,
            "plot_type": self.plot_type,
            "series_order": self.series_order.copy(),
            "labels": self.labels.copy(),
            "colors": {k: v[:] for k, v in self.colors.items()},
            "markers": self.markers.copy(),
            "show_lines": self.show_lines.copy(),
            "themes": self.themes.copy() if session else {k: -1 for k in self.themes},
        }

    def get_label(self) -> str:
        return self.plot_label

    def set_label(self, label: str):
        if label.strip() == "":
            return
        self.plot_label = label

    def get_type(self) -> PlotType:
        return self.plot_type

    def set_type(self, plot_type: PlotType):
        self.plot_type = plot_type

    def get_series_label(self, uuid: str) -> str:
        assert type(uuid) is str, uuid
        return self.labels.get(uuid, "")

    def set_series_label(self, uuid: str, label: str):
        assert type(uuid) is str, uuid
        assert type(label) is str, label
        self.labels[uuid] = label

    def get_series_theme(self, uuid: str) -> int:
        assert type(uuid) is str, uuid
        return self.themes.get(uuid, -1)

    def get_series_color(self, uuid: str) -> List[float]:
        assert type(uuid) is str, uuid
        color: Optional[List[float]] = self.colors.get(uuid)
        if color is None:
            return [255.0, 255.0, 255.0, 255.0]
        return color

    def set_series_color(self, uuid: str, color: List[float]):
        assert type(uuid) is str, uuid
        if type(color) is tuple:
            color = list(color)
        assert type(color) is list and len(color) == 4, color
        theme: int = self.themes[uuid]
        update_plot_series_theme_color(theme, color)
        self.colors[uuid] = color

    def get_series_marker(self, uuid: str) -> int:
        assert type(uuid) is str, uuid
        return self.markers.get(uuid, -1)

    def set_series_marker(self, uuid: str, marker: int):
        assert type(uuid) is str, uuid
        assert type(marker) is int, marker
        theme: int = self.themes[uuid]
        if marker >= 0:
            update_plot_series_theme_marker(theme, marker)
        self.markers[uuid] = marker

    def get_series_line(self, uuid: str) -> bool:
        assert type(uuid) is str, uuid
        return self.show_lines.get(uuid, False)

    def set_series_line(self, uuid: str, state: bool):
        assert type(uuid) is str, uuid
        assert type(state) is bool, state
        self.show_lines[uuid] = state

    def add_series(
        self,
        series: Union[DataSet, TestResult, FitResult, SimulationResult],
    ):
        # TODO: Refactor so that series is replaced by uuid?
        # Include the type as another argument to determine whether or not a line should be drawn?
        assert (
            type(series) is DataSet
            or type(series) is TestResult
            or type(series) is FitResult
            or type(series) is SimulationResult
        ), series
        uuid: str = series.uuid
        if uuid in self.series_order:
            return
        if uuid not in self.themes:
            self.labels[uuid] = ""
            color: List[float]
            marker: int
            color, marker = get_random_color_marker(self.themes)
            self.colors[uuid] = color
            self.markers[uuid] = marker
            self.themes[uuid] = dpg.generate_uuid()
            create_plot_series_theme(
                self.colors[uuid],
                self.markers[uuid] if self.markers[uuid] >= 0 else 0,
                self.themes[uuid],
            )
            self.show_lines[uuid] = type(series) is not DataSet
        self.series_order.append(uuid)

    def remove_series(self, uuid: str):
        assert type(uuid) is str, uuid
        if uuid not in self.series_order:
            return
        self.series_order.remove(uuid)

    def find_series(
        self,
        uuid: str,
        datasets: List[DataSet],
        tests: Dict[str, List[TestResult]],
        fits: Dict[str, List[FitResult]],
        simulations: List[SimulationResult],
    ) -> Optional[Union[DataSet, TestResult, FitResult, SimulationResult]]:
        def find_dataset() -> Optional[DataSet]:
            data: DataSet
            for data in datasets:
                if data.uuid == uuid:
                    return data
            return None

        def find_test() -> Optional[TestResult]:
            test: TestResult
            for test in [test for _ in tests.values() for test in _]:
                if test.uuid == uuid:
                    return test
            return None

        def find_fit() -> Optional[FitResult]:
            fit: FitResult
            for fit in [fit for _ in fits.values() for fit in _]:
                if fit.uuid == uuid:
                    return fit
            return None

        def find_simulation() -> Optional[SimulationResult]:
            sim: SimulationResult
            for sim in simulations:
                if sim.uuid == uuid:
                    return sim
            return None

        data: Optional[DataSet] = find_dataset()
        if data is not None:
            return data
        test: Optional[TestResult] = find_test()
        if test is not None:
            return test
        fit: Optional[FitResult] = find_fit()
        if fit is not None:
            return fit
        return find_simulation()
