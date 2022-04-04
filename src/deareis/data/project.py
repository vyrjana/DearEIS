# Copyright 2022 DearEIS developers
# DearEIS is licensed under the GPLv3 or later (https://www.gnu.org/licenses/gpl-3.0.html).
# The licenses of DearEIS' dependencies and/or sources of portions of code are included in
# the LICENSES folder.

from json import loads as load_json
from os.path import exists
from typing import Dict, List, Tuple, Union
from numpy import ndarray
from pyimpspec import DataSet
from deareis.data.fitting import FitResult
from deareis.data.kramers_kronig import TestResult
from deareis.data.plotting import (
    PlotSettings,
    # PlotType,
    # PlotSeries,
)
from deareis.data.simulation import SimulationResult


VERSION: int = 2


def _parse_state_v1(old: dict) -> dict:
    assert type(old) is dict
    # TODO: Update whenever VERSION is incremented
    new: dict = old
    new["active_plot_uuid"] = ""
    new["plots"] = []
    return new


def _parse_state_v2(old: dict) -> dict:
    assert type(old) is dict
    # TODO: Update whenever VERSION is incremented
    new: dict = old
    return new


def _parse_old_state(old: dict) -> dict:
    assert type(old) is dict
    version: int = old["version"]
    del old["version"]
    parsers: Dict[int, Callable] = {
        1: _parse_state_v1,
        2: _parse_state_v2,
    }
    assert version in parsers
    return parsers[version](old)


class Project:
    def __init__(self, dictionary: dict):
        assert type(dictionary) is dict
        self.label: str = dictionary.get("label", "")
        self.path: str = ""
        self.datasets: List[DataSet] = list(
            map(DataSet.from_dict, dictionary.get("datasets", []))
        )
        self.tests: Dict[str, List[TestResult]] = {
            k: list(map(TestResult.from_dict, v))
            for k, v in dictionary.get("tests", {}).items()
        }
        self.fits: Dict[str, List[FitResult]] = {
            k: list(map(FitResult.from_dict, v))
            for k, v in dictionary.get("fits", {}).items()
        }
        self.simulations: List[SimulationResult] = list(
            map(SimulationResult.from_dict, dictionary.get("simulations", []))
        )
        # TODO: Implement API for PlotSettings
        """
        self.plots: List[PlotSettings] = list(
            map(PlotSettings.from_dict, dictionary.get("plots", []))
        )
        """
        self._uuid_lookup: Dict[
            str, Tuple[DataSet, TestResult, FitResult, SimulationResult]
        ] = {}
        data: DataSet
        for data in self.datasets:
            self._uuid_lookup[data.uuid] = data
            test: TestResult
            for test in self.tests.get(data.uuid, []):
                self._uuid_lookup[test.uuid] = test
            fit: FitResult
            for fit in self.fits.get(data.uuid, []):
                self._uuid_lookup[fit.uuid] = fit
        self._uuid_lookup.update({_.uuid: _ for _ in self.simulations})
        assert len(self._uuid_lookup) == sum(
            [
                len(self.datasets),
                len(self.tests.values()),
                len(self.fits.values()),
                len(self.simulations),
            ]
        )

    @classmethod
    def from_file(Class, path: str) -> "Project":
        assert type(path) is str and exists(path)
        with open(path, "r") as fp:
            project: Project = Class.from_json(fp.read())
            project.path = path
            return project

    @classmethod
    def from_json(Class, json: str) -> "Project":
        assert type(json) is str
        dictionary: dict = load_json(json)
        return Class(_parse_old_state(dictionary))

    def get_label(self) -> str:
        return self.label

    def get_path(self) -> str:
        return self.path

    def get_datasets(self) -> List[DataSet]:
        return self.datasets.copy()

    def get_tests(self, data: DataSet) -> List[TestResult]:
        assert type(data) is DataSet
        return self.tests.get(data.uuid, []).copy()

    def get_fits(self, data: DataSet) -> List[FitResult]:
        assert type(data) is DataSet
        return self.fits.get(data.uuid, []).copy()

    def get_simulations(self) -> List[SimulationResult]:
        return self.simulations.copy()


"""
    def get_plots(self) -> List[PlotSettings]:
        return self.plots.copy()

    def get_plot_series(self, plot: PlotSettings, num_per_decade: int = 100) -> List[PlotSeries]:
        assert type(plot) is PlotSettings
        series: List[PlotSeries] = []
        uuid: str
        for uuid in plot.series_order:
            item: Optional[Union[DataSet, TestResult, FitResult, SimulationResult]]
            assert uuid in self._uuid_lookup
            item = self._uuid_lookup[uuid]
            label: str = plot.get_series_label(uuid) or item.get_label()
            data: List[ndarray]
            if plot.plot_type == PlotType.NYQUIST:
                if type(item) is DataSet:
                    data = [*item.get_nyquist_data()]
                else:
                    data = [*item.get_nyquist_data(num_per_decade=num_per_decade)]
            elif plot.plot_type == PlotType.BODE_MAGNITUDE:
                if type(item) is DataSet:
                    data = [*item.get_bode_data()]
                else:
                    data = [*item.get_bode_data(num_per_decade=num_per_decade)]
                data.pop(2)
            elif plot.plot_type == PlotType.BODE_PHASE:
                if type(item) is DataSet:
                    data = [*item.get_bode_data()]
                else:
                    data = [*item.get_bode_data(num_per_decade=num_per_decade)]
                data.pop(1)
            series.append(
                PlotSeries(
                    label,
                    data,
                    list(map(lambda _: _ / 255.0, plot.colors.get(uuid, [0.0, 0.0, 0.0, 255.0]))),
                    plot.markers.get(uuid, -1) >= 0,
                    plot.show_lines.get(uuid, False),
                    label.strip() != "",
                )
            )
        return series
"""
