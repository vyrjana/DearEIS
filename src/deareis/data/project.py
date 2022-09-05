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

from json import (
    dumps as dump_json,
    load as load_json,
    loads as parse_json,
)
from os import (
    remove,
    rename,
)
from os.path import (
    dirname,
    exists,
    islink,
)
from pathlib import Path
from typing import (
    Callable,
    Dict,
    IO,
    List,
    Optional,
    Tuple,
    Union,
)
from uuid import uuid4
from numpy import (
    ndarray,
)
from deareis.data import DataSet
from deareis.data.fitting import FitResult
from deareis.data.drt import DRTResult
from deareis.data.kramers_kronig import TestResult
from deareis.data.simulation import SimulationResult
from deareis.data.plotting import (
    PlotSettings,
    PlotSeries,
)
from deareis.enums import PlotType


VERSION: int = 4


def _parse_v4(state: dict) -> dict:
    # TODO: Update implementation when VERSION is incremented
    return state


def _parse_v3(state: dict) -> dict:
    state["drts"] = {_["uuid"]: [] for _ in state["data_sets"]}
    return _parse_v4(state)


def _parse_v2(state: dict) -> dict:
    state["data_sets"] = state["datasets"]
    key: str
    for key in [
        "active_data_uuid",
        "active_fit_uuid",
        "active_plot_uuid",
        "active_simulation_data_uuid",
        "active_simulation_uuid",
        "active_test_uuid",
        "datasets",
        "latest_fit_circuit",
        "latest_simulation_circuit",
    ]:
        if key in state:
            del state[key]
    if not state["plots"]:
        state["plots"].append(
            PlotSettings(
                "Plot",
                PlotType.NYQUIST,
                [],
                {},
                {},
                {},
                {},
                {},
                uuid4().hex,
            ).to_dict(session=False)
        )
    return _parse_v3(state)


def _parse_v1(state: dict) -> dict:
    state["active_plot_uuid"] = ""
    state["plots"] = []
    return _parse_v2(state)


class Project:
    """
    A class representing a collection of notes, data sets, test results, fit results, simulation results, and complex plots.
    """

    def __init__(self, *args, **kwargs):
        self._path: str = ""
        self.update(*args, **kwargs)

    def __repr(self) -> str:
        return f"Project ({self.get_label()}, {hex(id(self))})"

    def update(self, *args, **kwargs):
        """
        Used when restoring project states.
        """
        if not hasattr(self, "uuid"):
            self.uuid: str = kwargs.get("uuid", uuid4().hex)
        self._data_sets: List[DataSet] = list(
            map(DataSet.from_dict, kwargs.get("data_sets", []))
        )
        self._drts: Dict[str, List[DRTResult]] = {
            k: list(map(DRTResult.from_dict, v))
            for k, v in kwargs.get("drts", {}).items()
        }
        self._fits: Dict[str, List[FitResult]] = {
            k: list(map(FitResult.from_dict, v))
            for k, v in kwargs.get("fits", {}).items()
        }
        self._label: str = kwargs.get("label", "Project")
        self._notes: str = kwargs.get("notes", "")
        path: str = kwargs.get("path", "").strip()
        if path != "":
            self.set_path(path)
        self._plots: List[PlotSettings] = list(
            map(PlotSettings.from_dict, kwargs.get("plots", []))
        )
        if len(self._plots) == 0:
            self._plots.append(
                PlotSettings(
                    "Plot",
                    PlotType.NYQUIST,
                    [],
                    {},
                    {},
                    {},
                    {},
                    {},
                    uuid4().hex,
                )
            )
        self._simulations: List[SimulationResult] = list(
            map(SimulationResult.from_dict, kwargs.get("simulations", []))
        )
        self._tests: Dict[str, List[TestResult]] = {
            k: list(map(TestResult.from_dict, v))
            for k, v in kwargs.get("tests", {}).items()
        }

    @staticmethod
    def parse(state: dict) -> dict:
        """
        Used when deserializing project files.
        """
        assert type(state) is dict, type(state)
        if "version" in state:
            version: int = state["version"]
            assert type(version) is int, version
            assert version >= 1 and version <= VERSION, (
                version,
                VERSION,
            )
            del state["version"]
            parsers: Dict[int, Callable] = {
                1: _parse_v1,
                2: _parse_v2,
                3: _parse_v3,
                4: _parse_v4,
            }
            assert version in parsers, (
                version,
                parsers,
            )
            state = parsers[version](state)
            assert type(state["uuid"]) is str
        # Basic validation
        assert type(state["data_sets"]) is list
        assert type(state["fits"]) is dict
        assert type(state["drts"]) is dict
        assert type(state["label"]) is str
        assert type(state["notes"]) is str
        assert type(state["plots"]) is list
        assert type(state["simulations"]) is list
        assert type(state["tests"]) is dict
        return state

    @classmethod
    def from_dict(Class, state: dict) -> "Project":
        """
        Create an instance from a dictionary.

        Parameters
        ----------
        state: dict
            A dictionary-based representation of a project state.
        """
        return Class(**Class.parse(state))

    @classmethod
    def from_file(Class, path: str) -> "Project":
        """
        Create an instance by parsing a file containing a Project that has been serialized using JSON.

        Parameters
        ----------
        path: str
            The path to a file containing a serialized project state.
        """
        assert type(path) is str and exists(path)
        fp: IO
        with open(path, "r") as fp:
            state: dict = load_json(fp)
        state["path"] = path
        return Class.from_dict(state)

    @classmethod
    def from_json(Class, json: str) -> "Project":
        """
        Create an instance by parsing a JSON string.

        Parameters
        ----------
        json: str
            A JSON representation of a project state.
        """
        assert type(json) is str
        return Class.from_dict(parse_json(json))

    @classmethod
    def merge(Class, projects: List["Project"]) -> "Project":
        """
        Create an instance by merging multiple Project instances.
        All UUIDs are replaced to avoid collisions.
        The labels of some objects are also replaced to avoid collisions.
        """
        assert type(projects) is list and all(
            map(lambda _: type(_) is Class, projects)
        ), projects

        def extract_uuids(dictionary: dict) -> List[str]:
            assert type(dictionary) is dict, dictionary
            uuids: List[str] = []
            for k, v in dictionary.items():
                if type(v) is dict:
                    uuids.extend(extract_uuids(v))
                elif type(v) is list:
                    for v in filter(lambda _: type(_) is dict, v):
                        uuids.extend(extract_uuids(v))
                elif k == "uuid":
                    assert type(v) is str, v
                    uuids.append(v)
            # print(uuids)
            return list(set(uuids))

        def replace_uuids(dictionary: dict) -> dict:
            assert type(dictionary) is dict, dictionary
            uuids: List[str] = extract_uuids(dictionary)
            json: str = dump_json(dictionary)
            uuid: str
            for uuid in uuids:
                json = json.replace(uuid, uuid4().hex)
            return parse_json(json)

        # Merge the various items into one large dictionary.
        # Replace the old UUIDs with new ones to reduce the chance of collisions
        # (e.g. in case one or more of the projects were initially identical copies
        # that were modified in different ways).
        state: dict = Class().to_dict(session=True)
        project: "Project"
        for project in projects:
            other: dict = replace_uuids(project.to_dict(session=True))
            state["data_sets"].extend(other["data_sets"])
            state["fits"].update(other["fits"])
            state["drts"].update(other["drts"])
            state["notes"] = state["notes"] + "\n\n" + other["notes"]
            state["plots"].extend(other["plots"])
            state["simulations"].extend(other["simulations"])
            state["tests"].update(other["tests"])
            state["label"] = other["label"]
        state["notes"] = state["notes"].strip()
        # Check for UUID collisions.
        uuids: List[str] = []
        uuids.extend(list(map(lambda _: _["uuid"], state["data_sets"])))
        for fits in state["fits"].values():
            uuids.extend(list(map(lambda _: _["uuid"], fits)))
        for drts in state["drts"].values():
            uuids.extend(list(map(lambda _: _["uuid"], drts)))
        uuids.extend(list(map(lambda _: _["uuid"], state["plots"])))
        uuids.extend(list(map(lambda _: _["uuid"], state["simulations"])))
        for tests in state["tests"].values():
            uuids.extend(list(map(lambda _: _["uuid"], tests)))
        assert all(map(lambda _: type(_) is str, uuids)), uuids
        assert len(uuids) == len(set(uuids)), "Encountered UUID collision!"
        if len(projects) > 1:
            # Make sure that labels are unique.
            # - Data sets
            labels: List[str] = []
            i: int
            label: str
            data: dict
            for data in state["data_sets"]:
                label = data["label"]
                i = 1
                while label in labels:
                    i += 1
                    label = f"{data['label']} ({i})"
                labels.append(label)
                data["label"] = label
            # - Plot settings
            labels = []
            for plot in state["plots"]:
                label = plot["plot_label"]
                i = 1
                while label in labels:
                    i += 1
                    label = f"{plot['plot_label']} ({i})"
                labels.append(label)
                plot["plot_label"] = label
            # Change the project label
            state["label"] = "Merged project"
        return Class.from_dict(state)

    def to_dict(self, session: bool) -> dict:
        """
        Return a dictionary containing the project state.
        The dictionary can be used to recreate a project or to restore a project state.

        Parameters
        ----------
        session: bool
            If true, then data minimization is not performed.
        """
        return {
            "data_sets": list(
                map(lambda _: _.to_dict(session=session), self._data_sets)
            ),
            "fits": {
                k: list(map(lambda _: _.to_dict(session=session), v))
                for k, v in self._fits.items()
            },
            "drts": {
                k: list(map(lambda _: _.to_dict(), v)) for k, v in self._drts.items()
            },
            "label": self._label,
            "notes": self._notes,
            "plots": list(map(lambda _: _.to_dict(session=session), self._plots)),
            "simulations": list(map(lambda _: _.to_dict(), self._simulations)),
            "tests": {
                k: list(map(lambda _: _.to_dict(session=session), v))
                for k, v in self._tests.items()
            },
            "uuid": self.uuid,
            "version": VERSION,
        }

    def get_label(self) -> str:
        """
        Get the project's label.
        """
        return self._label

    def set_label(self, label: str):
        """
        Set the project's label.

        Parameters
        ----------
        label: str
            The new label.
        """
        assert type(label) is str
        assert label.strip() != ""
        self._label = label

    def set_path(self, path: str):
        """
        Set the path to use when calling the `save` method without arguments.

        Parameters
        ----------
        path: str
            The path where the project's state should be saved.
        """
        assert type(path) is str, path
        self._path = path

    def get_path(self) -> str:
        """
        Get the project's currrent path.
        An empty string signifies that no path has been set previously.
        """
        return self._path

    def get_notes(self) -> str:
        """
        Get the project's notes.
        """
        return self._notes

    def set_notes(self, notes: str):
        """
        Set the project's notes.

        Parameters
        ----------
        notes: str
            The project notes.
        """
        assert type(notes) is str, notes
        self._notes = notes

    def save(self, path: Optional[str] = None):
        """
        Serialize the project as a file containing a JSON string.

        Parameters
        ----------
        path: Optional[str] = None
            The path to write the project state to.
            If this is None, then the most recently defined path is used.
        """
        assert type(path) is str or path is None, path
        if path is None:
            path = self.get_path()
        else:
            self.set_path(path)
        assert path != ""
        assert exists(dirname(path)), path
        suffix: str = f".bak-{uuid4().hex}"
        tmp_path: str = path + suffix
        if exists(path):
            if islink(path):
                tmp_path = str(Path(path).resolve()) + suffix
            rename(path, tmp_path)
        dictionary: dict = self.to_dict(session=False)
        fp: IO
        with open(path, "w") as fp:
            fp.write(dump_json(dictionary, sort_keys=True, indent=1))
        if exists(tmp_path):
            remove(tmp_path)

    def get_data_sets(self) -> List[DataSet]:
        """
        Get the project's data sets.
        """
        return self._data_sets

    def add_data_set(self, data: DataSet):
        """
        Add a data set to the project.

        Parameters
        ----------
        data: DataSet
            The data set to add.
        """
        assert type(data) is DataSet, data
        assert data.uuid not in list(map(lambda _: _.uuid, self._data_sets))
        label: str = data.get_label()
        existing_labels: List[str] = list(map(lambda _: _.get_label(), self._data_sets))
        if label in existing_labels:
            i: int = 1
            while label in existing_labels:
                i += 1
                label = f"{data.get_label()} ({i})"
            data.set_label(label)
        self._data_sets.append(data)
        self._fits[data.uuid] = []
        self._drts[data.uuid] = []
        self._tests[data.uuid] = []
        self._data_sets.sort(key=lambda _: _.get_label())

    def edit_data_set_label(self, data: DataSet, label: str):
        """
        Edit the label of a data set in the project.
        Ensures that each data set has a unique label.

        Parameters
        ----------
        data: DataSet
            The data set to rename.

        label: str
            The new label.
        """
        assert type(data) is DataSet, data
        assert data.uuid in list(map(lambda _: _.uuid, self._data_sets)), data
        label = label.strip()
        if label == data.get_label():
            return
        assert label != "", "The label of a data set cannot be an empty string!"
        assert label not in list(
            map(lambda _: _.get_label(), self.get_data_sets())
        ), f"Another data set already has the label '{label}'!"
        data.set_label(label)
        self._data_sets.sort(key=lambda _: _.get_label())

    def edit_data_set_path(self, data: DataSet, path: str):
        """
        Edit the path of a data set in the project.

        Parameters
        ----------
        data: DataSet
            The data set to edit.

        path: str
            The new path.
        """
        assert type(data) is DataSet, data
        assert data.uuid in list(map(lambda _: _.uuid, self._data_sets)), data
        assert type(path) is str, path
        data.set_path(path)

    def delete_data_set(self, data: DataSet):
        """
        Delete a data set (and its associated test and fit results) from the project.

        Parameters
        ----------
        data: DataSet
            The data set to remove.
        """
        assert type(data) is DataSet, data
        assert data.uuid in list(map(lambda _: _.uuid, self._data_sets)), data
        self._data_sets.remove(data)
        del self._fits[data.uuid]
        del self._drts[data.uuid]
        del self._tests[data.uuid]
        list(map(lambda _: _.remove_series(data.uuid), self._plots))

    def replace_data_set(self, old: DataSet, new: DataSet):
        """
        Replace a data set in the project with another one.

        Parameters
        ----------
        old: DataSet
            The data set to be replaced.

        new: DataSet
            The replacement data set.
        """
        assert type(old) is DataSet, old
        assert type(new) is DataSet, new
        assert old.uuid in list(map(lambda _: _.uuid, self._data_sets))
        assert old.uuid == new.uuid, (
            old.uuid,
            new.uuid,
        )
        self._data_sets.remove(old)
        self._data_sets.append(new)
        self._data_sets.sort(key=lambda _: _.get_label())

    def get_all_tests(self) -> Dict[str, List[TestResult]]:
        """
        Get a mapping of data set UUIDs to the corresponding Kramers-Kronig test results of those data sets.
        """
        return self._tests

    def get_tests(self, data: DataSet) -> List[TestResult]:
        """
        Get the Kramers-Kronig test results associated with a specific data set.

        Parameters
        ----------
        data: DataSet
            The data set whose tests to get.
        """
        assert type(data) is DataSet, data
        assert data.uuid in list(map(lambda _: _.uuid, self._data_sets)), data
        return self._tests[data.uuid]

    def add_test(self, data: DataSet, test: TestResult):
        """
        Add the provided Kramers-Kronig test result to the provided data set's list of Kramers-Kronig test results.

        Parameters
        ----------
        data: DataSet
            The data set that was tested.

        test: TestResult
            The result of the test.
        """
        assert type(data) is DataSet, data
        assert data.uuid in list(map(lambda _: _.uuid, self._data_sets)), data
        assert type(test) is TestResult, test
        assert test.uuid not in list(map(lambda _: _.uuid, self._tests[data.uuid]))
        self._tests[data.uuid].insert(0, test)

    def delete_test(self, data: DataSet, test: TestResult):
        """
        Delete the provided Kramers-Kronig test result from the provided data set's list of Kramers-Kronig test results.

        Parameters
        ----------
        data: DataSet
            The data set associated with the test result.

        test: TestResult
            The test result to delete.
        """
        assert type(data) is DataSet, data
        assert data.uuid in list(map(lambda _: _.uuid, self._data_sets)), data
        assert type(test) is TestResult, test
        assert test in self._tests[data.uuid], test
        self._tests[data.uuid].remove(test)
        list(map(lambda _: _.remove_series(test.uuid), self._plots))

    def get_all_drts(self) -> Dict[str, List[DRTResult]]:
        """
        Get a mapping of data set UUIDs to the corresponding DRT analysis results of those data sets.
        """
        return self._drts

    def get_drts(self, data: DataSet) -> List[DRTResult]:
        """
        Get the DRT analysis results associated with a specific data set.

        Parameters
        ----------
        data: DataSet
            The data set whose analyses to get.
        """
        assert type(data) is DataSet, data
        assert data.uuid in list(map(lambda _: _.uuid, self._data_sets)), data
        return self._drts[data.uuid]

    def add_drt(self, data: DataSet, drt: DRTResult):
        """
        Add the provided DRT analysis result to the provided data set's list of DRT analysis results.

        Parameters
        ----------
        data: DataSet
            The data set that was analyzed.

        drt: DRTResult
            The result of the analysis.
        """
        assert type(data) is DataSet, data
        assert data.uuid in list(map(lambda _: _.uuid, self._data_sets)), data
        assert type(drt) is DRTResult, drt
        assert drt.uuid not in list(map(lambda _: _.uuid, self._drts[data.uuid]))
        self._drts[data.uuid].insert(0, drt)

    def delete_drt(self, data: DataSet, drt: DRTResult):
        """
        Delete the provided DRT analysis result from the provided data set's list of DRT analysis results.

        Parameters
        ----------
        data: DataSet
            The data set associated with the analysis result.

        drt: DRTResult
            The analysis result to delete.
        """
        assert type(data) is DataSet, data
        assert data.uuid in list(map(lambda _: _.uuid, self._data_sets)), data
        assert type(drt) is DRTResult, drt
        assert drt in self._drts[data.uuid], drt
        self._drts[data.uuid].remove(drt)
        list(map(lambda _: _.remove_series(drt.uuid), self._plots))

    def get_all_fits(self) -> Dict[str, List[FitResult]]:
        """
        Get a mapping of data set UUIDs to the corresponding list of fit results of those data sets.
        """
        return self._fits

    def get_fits(self, data: DataSet) -> List[FitResult]:
        """
        Get fit results associated with a specific data set.

        Parameters
        ----------
        data: DataSet
            The data set whose fits to get.
        """
        assert type(data) is DataSet, data
        assert data.uuid in list(map(lambda _: _.uuid, self._data_sets)), data
        return self._fits[data.uuid]

    def add_fit(self, data: DataSet, fit: FitResult):
        """
        Add the provided fit result to the provided data set.

        Parameters
        ----------
        data: DataSet
            The data set that a circuit was fit to.

        fit: FitResult
            The result of the circuit fit.
        """
        assert type(data) is DataSet, data
        assert data.uuid in list(map(lambda _: _.uuid, self._data_sets)), data
        assert type(fit) is FitResult, fit
        assert fit.uuid not in list(map(lambda _: _.uuid, self._fits[data.uuid]))
        self._fits[data.uuid].insert(0, fit)

    def delete_fit(self, data: DataSet, fit: FitResult):
        """
        Delete the provided fit result from the provided data set's list of fit results.

        Parameters
        ----------
        data: DataSet
            The data set associated with the fit result.

        fit: FitResult
            The fit result to delete.
        """
        assert type(data) is DataSet, data
        assert data.uuid in list(map(lambda _: _.uuid, self._data_sets)), data
        assert type(fit) is FitResult, fit
        assert fit in self._fits[data.uuid], fit
        self._fits[data.uuid].remove(fit)
        list(map(lambda _: _.remove_series(fit.uuid), self._plots))

    def get_simulations(self) -> List[SimulationResult]:
        """
        Get all of the simulation results.
        """
        return self._simulations

    def add_simulation(self, simulation: SimulationResult):
        """
        Add the provided simulation result to the list of simulation results.

        Parameters
        ----------
        simulation: SimulationResult
            The result of the simulation.
        """
        assert type(simulation) is SimulationResult, simulation
        assert simulation.uuid not in list(map(lambda _: _.uuid, self._simulations))
        self._simulations.insert(0, simulation)

    def delete_simulation(self, simulation: SimulationResult):
        """
        Remove the provided simulation result from the list of simulation results.

        Parameters
        ----------
        simulation: SimulationResult
            The simulation result to delete.
        """
        assert type(simulation) is SimulationResult, simulation
        assert simulation in self._simulations
        self._simulations.remove(simulation)
        list(map(lambda _: _.remove_series(simulation.uuid), self._plots))

    def get_plots(self) -> List[PlotSettings]:
        """
        Get all of the plots.
        """
        return self._plots

    def add_plot(self, plot: PlotSettings):
        """
        Add the provided plot to the list of plots.

        Parameters
        ----------
        plot: PlotSettings
            The settings for the plot.
        """
        assert type(plot) is PlotSettings, plot
        assert plot.uuid not in list(map(lambda _: _.uuid, self._plots))
        self._plots.append(plot)
        self._plots.sort(key=lambda _: _.get_label())

    def edit_plot_label(self, plot: PlotSettings, label: str):
        """
        Edit the label of a plot in the project.
        Ensures that each plot has a unique label.

        Parameters
        ----------
        plot: PlotSettings
            The plot settings to edit.

        label: str
            The new label.
        """
        assert type(plot) is PlotSettings, plot
        assert plot in self._plots, plot
        label = label.strip()
        if label == plot.get_label():
            return
        assert label != "", "The label of a plot cannot be an empty string!"
        assert label not in list(
            map(lambda _: _.get_label(), self.get_plots())
        ), f"Another plot already has the label '{label}'!"
        plot.set_label(label)
        self._plots.sort(key=lambda _: _.get_label())

    def delete_plot(self, plot: PlotSettings):
        """
        Delete the provided plot from the list of plots.

        Parameters
        ----------
        plot: PlotSettings
            The plot settings to delete.
        """
        assert type(plot) is PlotSettings, plot
        assert plot in self._plots, plot
        self._plots.remove(plot)

    def get_plot_series(
        self,
        plot: PlotSettings,
    ) -> List[PlotSeries]:
        """
        Get PlotSeries instances of each of the plotted items/series in a specific plot.

        Parameters
        ----------
        plot: PlotSettings
            The plot whose items/series to get.
        """
        assert type(plot) is PlotSettings, plot
        data_sets: List[DataSet] = self.get_data_sets()
        tests: Dict[str, List[TestResult]] = self.get_all_tests()
        drts: Dict[str, List[DRTResult]] = self.get_all_drts()
        fits: Dict[str, List[FitResult]] = self.get_all_fits()
        simulations: List[SimulationResult] = self.get_simulations()
        results: List[PlotSeries] = []
        uuid: str
        for uuid in plot.series_order:
            series: Optional[
                Union[DataSet, TestResult, DRTResult, FitResult, SimulationResult]
            ]
            series = plot.find_series(uuid, data_sets, tests, drts, fits, simulations)
            if series is None:
                continue
            label: str = plot.get_series_label(uuid) or series.get_label()
            scatter_data: Tuple[ndarray, ndarray]
            line_data: Tuple[ndarray, ndarray]
            fill_data: Tuple[ndarray, ndarray, ndarray]
            color: Tuple[float, float, float, float] = tuple(
                map(
                    lambda _: _ / 255.0,
                    plot.get_series_color(uuid) or [0.0, 0.0, 0.0, 255.0],
                )
            )
            marker: int = plot.get_series_marker(uuid)
            line: bool = plot.get_series_line(uuid)
            results.append(
                PlotSeries(
                    series,
                    label,
                    color,
                    marker,
                    line,
                    label.strip() != "",
                )
            )
        return results
