# Copyright 2022 DearEIS developers
# DearEIS is licensed under the GPLv3 or later (https://www.gnu.org/licenses/gpl-3.0.html).
# The licenses of DearEIS' dependencies and/or sources of portions of code are included in
# the LICENSES folder.

from dataclasses import dataclass
from enum import IntEnum, auto as auto_enum
from typing import Callable, Dict, List, Set, Tuple, Union, Optional
from random import choice
import dearpygui.dearpygui as dpg
from numpy import ndarray
from pyimpspec import DataSet
from deareis.data.kramers_kronig import TestResult
from deareis.data.fitting import FitResult
from deareis.data.simulation import SimulationResult
from deareis.themes import (
    PLOT_MARKERS,
    VIBRANT_COLORS,
    create_plot_theme,
    get_plot_theme_color,
    get_plot_theme_marker,
    update_plot_theme_color,
    update_plot_theme_marker,
)


class PlotType(IntEnum):
    NYQUIST = auto_enum()
    BODE_MAGNITUDE = auto_enum()
    BODE_PHASE = auto_enum()


label_to_plot_type: Dict[str, PlotType] = {
    "Nyquist": PlotType.NYQUIST,
    "Bode - magnitude": PlotType.BODE_MAGNITUDE,
    "Bode - phase": PlotType.BODE_PHASE,
}
plot_type_to_label: Dict[PlotType, str] = {v: k for k, v in label_to_plot_type.items()}


@dataclass(frozen=True)
class PlotSeries:
    label: str
    data: List[ndarray]
    color: List[float]
    markers: bool
    line: bool
    legend: bool

    def get_label(self) -> str:
        return self.label

    def get_data(self) -> List[ndarray]:
        return self.data

    def get_color(self) -> List[float]:
        return self.color

    def has_markers(self) -> bool:
        return self.markers

    def has_line(self) -> bool:
        return self.line

    def has_legend(self) -> bool:
        return self.legend


VERSION: int = 1


def get_color_marker(themes: Dict[str, int]) -> Tuple[List[float], int]:
    available_colors: List[List[float]] = VIBRANT_COLORS[:]
    available_markers: List[int] = list(PLOT_MARKERS.values())
    existing_colors: List[List[float]] = []
    existing_markers: List[int] = []
    existing_combinations: List[str] = []
    color: List[float]
    marker: int
    for uuid, item in themes.items():
        color = get_plot_theme_color(item)
        marker = get_plot_theme_marker(item)
        existing_colors.append(color)
        existing_markers.append(marker)
        existing_combinations.append(",".join(map(str, color)) + str(marker))
    if len(available_markers) > len(existing_markers):
        available_markers = list(set(available_markers) - set(existing_markers))
        ac: Set[str] = set(map(lambda _: ",".join(map(str, _)), available_colors))
        ec: Set[str] = set(map(lambda _: ",".join(map(str, _)), existing_colors))
        ac = ac - ec
        if len(ac) > 0:
            available_colors = list(map(lambda _: list(map(float, _.split(","))), ac))
            return (
                choice(available_colors),
                choice(available_markers),
            )
    possible_combinations: Dict[str, Tuple[List[float], int]] = {}
    combination: str
    for marker in PLOT_MARKERS.values():
        for color in VIBRANT_COLORS:
            combination = ",".join(map(str, color)) + str(marker)
            if combination not in existing_combinations:
                possible_combinations[combination] = (
                    color,
                    marker,
                )
    if len(possible_combinations) > 0:
        return choice(list(possible_combinations.values()))
    return (
        [255.0, 255.0, 255.0, 255.0],
        dpg.mvPlotMarker_Circle,
    )


# TODO: Make it possible to (re)store the limits of plots (e.g. from session to session)
@dataclass
class PlotSettings:
    plot_label: str
    plot_type: PlotType
    series_order: List[str]  # UUID
    labels: Dict[str, str]  # UUID: label
    colors: Dict[str, List[float]]  # UUID: RGBA
    markers: Dict[str, int]  # UUID: enum
    show_lines: Dict[str, bool]  # UUID: flag
    themes: Dict[str, int]  # UUID: DPG UUID
    uuid: str

    @staticmethod
    def _parse_v1(dictionary: dict) -> dict:
        assert type(dictionary) is dict
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
        for uuid in self.themes:
            item: int = self.themes[uuid]
            if item < 0:
                self.themes[uuid] = dpg.generate_uuid()
                create_plot_theme(
                    self.themes[uuid],
                    self.colors[uuid],
                    self.markers[uuid] if self.markers[uuid] >= 0 else 0,
                )
            else:
                if not dpg.does_item_exist(self.themes[uuid]):
                    del self.labels[uuid]
                    del self.colors[uuid]
                    del self.markers[uuid]
                    del self.show_lines[uuid]
                    del self.themes[uuid]
                else:
                    update_plot_theme_color(self.themes[uuid], self.colors[uuid])
                    update_plot_theme_marker(self.themes[uuid], self.markers[uuid])

    @classmethod
    def from_dict(Class, dictionary: dict) -> "PlotSettings":
        assert type(dictionary) is dict
        assert "version" in dictionary
        version: int = dictionary["version"]
        assert version <= VERSION, f"{version=} > {VERSION=}"
        parsers: Dict[int, Callable] = {
            1: Class._parse_v1,
        }
        assert version in parsers, f"{version=} not in {parsers.keys()=}"
        return Class(**parsers[version](dictionary))

    def to_dict(self) -> dict:
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
            "themes": self.themes.copy(),
        }

    def get_label(self) -> str:
        return self.plot_label

    def set_label(self, label: str):
        if label.strip() == "":
            return
        self.plot_label = label

    def get_type(self) -> PlotType:
        return self.plot_type

    def get_series_label(self, uuid: str) -> str:
        assert type(uuid) is str
        return self.labels.get(uuid, "")

    def set_series_label(self, uuid: str, label: str):
        assert type(uuid) is str
        assert type(label) is str
        self.labels[uuid] = label

    def get_series_theme(self, uuid: str) -> int:
        assert type(uuid) is str
        return self.themes.get(uuid, -1)

    def get_series_color(self, uuid: str) -> List[float]:
        assert type(uuid) is str
        color: Optional[List[float]] = self.colors.get(uuid)
        if color is None:
            return [255.0, 255.0, 255.0, 255.0]
        return color

    def set_series_color(self, uuid: str, color: List[float]):
        assert type(uuid) is str
        if type(color) is tuple:
            color = list(color)
        assert type(color) is list and len(color) == 4, color
        theme: int = self.themes[uuid]
        update_plot_theme_color(theme, color)
        self.colors[uuid] = color

    def get_series_marker(self, uuid: str) -> int:
        assert type(uuid) is str
        return self.markers.get(uuid, -1)

    def set_series_marker(self, uuid: str, marker: int):
        assert type(uuid) is str
        assert type(marker) is int
        theme: int = self.themes[uuid]
        if marker >= 0:
            update_plot_theme_marker(theme, marker)
        self.markers[uuid] = marker

    def get_series_line(self, uuid: str) -> bool:
        assert type(uuid) is str
        return self.show_lines.get(uuid, False)

    def set_series_line(self, uuid: str, state: bool):
        assert type(uuid) is str
        assert type(state) is bool
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
        )
        uuid: str = series.uuid
        if uuid in self.series_order:
            return
        if uuid not in self.themes:
            self.labels[uuid] = ""
            color: List[float]
            marker: int
            color, marker = get_color_marker(self.themes)
            self.colors[uuid] = color
            self.markers[uuid] = marker
            self.themes[uuid] = dpg.generate_uuid()
            create_plot_theme(
                self.themes[uuid],
                self.colors[uuid],
                self.markers[uuid] if self.markers[uuid] >= 0 else 0,
            )
            self.show_lines[uuid] = type(series) is not DataSet
        self.series_order.append(uuid)

    def remove_series(self, uuid: str):
        assert type(uuid) is str
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

        series: Union[DataSet, TestResult, FitResult, SimulationResult]
        series = find_dataset()
        if series is not None:
            return series
        series = find_test()
        if series is not None:
            return series
        series = find_fit()
        if series is not None:
            return series
        return find_simulation()
