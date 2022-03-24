# Copyright 2022 DearEIS developers
# DearEIS is licensed under the GPLv3 or later (https://www.gnu.org/licenses/gpl-3.0.html).
# The licenses of DearEIS' dependencies and/or sources of portions of code are included in
# the LICENSES folder.

from pyimpspec import DataSet
from deareis.project import _parse_old_state
from json import loads as load_json
from os.path import exists
from typing import Dict, List
from deareis.data.kramers_kronig import TestResult
from deareis.data.fitting import FitResult
from deareis.data.simulation import SimulationResult


class Project:
    def __init__(self, dictionary: dict):
        assert type(dictionary) is dict
        self.label: str = dictionary["label"]
        self.path: str = ""
        self.datasets: List[DataSet] = list(
            map(DataSet.from_dict, dictionary["datasets"])
        )
        self.tests: Dict[str, List[TestResult]] = {
            k: list(map(TestResult.from_dict, v))
            for k, v in dictionary["tests"].items()
        }
        self.fits: Dict[str, List[FitResult]] = {
            k: list(map(FitResult.from_dict, v)) for k, v in dictionary["fits"].items()
        }
        self.simulations: List[SimulationResult] = list(
            map(SimulationResult.from_dict, dictionary["simulations"])
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
