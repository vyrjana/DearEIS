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

from os.path import (
    dirname,
    exists,
    join,
)
from typing import (
    Callable,
    Dict,
    List,
)
from unittest import TestCase
import deareis
from deareis import (
    DRTResult,
    DataSet,
    FitResult,
    PlotSeries,
    PlotSettings,
    Project,
    SimulationResult,
    TestResult,
    ZHITResult,
)


class TestProject(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.example_data_paths: List[str] = list(
            map(
                lambda _: join(dirname(__file__), _),
                [
                    "data-1.idf",
                    "data-2.csv",
                ],
            )
        )
        cls.example_project_paths: List[str] = list(
            map(
                lambda _: join(dirname(__file__), _),
                [
                    "example-project-v1.json",
                    "example-project-v2.json",
                    "example-project-v3.json",
                    "example-project-v4.json",
                    "example-project-v5.json",
                ],
            )
        )
        cls.project: Project = Project.from_file(cls.example_project_paths[-1])

    def test_new_project(self):
        project: Project = Project()
        self.assertEqual(len(project.get_data_sets()), 0)
        self.assertEqual(len(project.get_all_tests()), 0)
        self.assertEqual(len(project.get_all_zhits()), 0)
        self.assertEqual(len(project.get_all_drts()), 0)
        self.assertEqual(len(project.get_all_fits()), 0)
        self.assertEqual(len(project.get_simulations()), 0)
        self.assertEqual(len(project.get_plots()), 1)

    def test_parse_different_versions(self):
        path: str
        for path in self.example_project_paths:
            self.assertTrue(exists(path))
            Project.from_file(path)

    def test_merge(self):
        methods: Dict[str, Callable] = {
            "data_sets": lambda _: _.get_data_sets(),
            "tests": lambda _: _.get_all_tests(),
            "zhits": lambda _: _.get_all_zhits(),
            "drts": lambda _: _.get_all_drts(),
            "fits": lambda _: _.get_all_fits(),
            "simulations": lambda _: _.get_simulations(),
            "plots": lambda _: _.get_plots(),
        }
        num_assets: Dict[str, int] = {_: 0 for _ in methods}
        projects: List[Project] = []
        path: str
        for path in self.example_project_paths:
            project: Project = Project.from_file(path)
            key: str
            func: Callable
            for key, func in methods.items():
                num_assets[key] += len(func(project))
            projects.append(project)
        num_assets["plots"] += 1  # Every project starts with one
        project = Project.merge(projects)
        for key, func in methods.items():
            self.assertEqual(len(func(project)), num_assets[key], msg=key)

    def test_label(self):
        old_label: str = self.project.get_label()
        self.assertEqual(old_label, "Example project - Version 5")
        new_label: str = "Test label"
        self.project.set_label(new_label)
        self.assertEqual(self.project.get_label(), new_label)
        with self.assertRaises(AssertionError):
            self.project.set_label("")
        with self.assertRaises(AssertionError):
            self.project.set_label("  \t")

    def test_path(self):
        old_path: str = self.project.get_path()
        self.assertTrue(old_path.endswith("example-project-v5.json"))
        new_path: str = "Testing"
        self.project.set_path(new_path)
        self.assertEqual(self.project.get_path(), new_path)

    def test_get_notes(self):
        old_notes: str = self.project.get_notes()
        self.assertEqual(old_notes, "This is for keeping notes about the project.")

    def test_set_notes(self):
        new_notes: str = "Lorem ipsum"
        self.project.set_notes(new_notes)
        self.assertEqual(self.project.get_notes(), new_notes)

    def test_get_data_sets(self):
        data_sets: List[DataSet] = self.project.get_data_sets()
        self.assertIsInstance(data_sets, list)
        self.assertTrue(all([isinstance(_, DataSet) for _ in data_sets]))

    def test_add_data_set(self):
        num_data_sets: int = len(self.project.get_data_sets())
        data: DataSet = deareis.parse_data(self.example_data_paths[0])[0]
        self.project.add_data_set(data)
        data_sets: List[DataSet] = self.project.get_data_sets()
        self.assertEqual(len(data_sets), num_data_sets + 1)

    def test_edit_data_set_label(self):
        data: DataSet = self.project.get_data_sets()[0]
        new_label: str = "ABC"
        self.assertNotEqual(data.get_label(), new_label)
        self.project.edit_data_set_label(data, new_label)
        self.assertEqual(data.get_label(), new_label)

    def test_edit_data_set_path(self):
        data: DataSet = self.project.get_data_sets()[0]
        new_path: str = "XYZ"
        self.assertNotEqual(data.get_path(), new_path)
        self.project.edit_data_set_path(data, new_path)
        self.assertEqual(data.get_path(), new_path)

    def test_get_all_tests(self):
        tests: Dict[str, List[TestResult]] = self.project.get_all_tests()
        self.assertIsInstance(tests, dict)
        self.assertTrue(all([isinstance(_, str) for _ in tests.keys()]))
        self.assertTrue(all([isinstance(_, list) for _ in tests.values()]))
        uuids: List[str] = [_.uuid for _ in self.project.get_data_sets()]
        self.assertTrue(all([_ in uuids for _ in tests.keys()]))

    def test_get_tests(self):
        data: DataSet
        for data in self.project.get_data_sets():
            tests: List[TestResult] = self.project.get_tests(data)
            self.assertIsInstance(tests, list)
            self.assertTrue(all([isinstance(_, TestResult) for _ in tests]))

    def test_add_test(self):
        data: DataSet
        for data in self.project.get_data_sets():
            tests: List[TestResult] = self.project.get_tests(data)
            if len(tests) == 0:
                continue
            break
        else:
            raise NotImplementedError("No suitable test data available in the project!")
        test: TestResult = tests[0]
        with self.assertRaises(AssertionError):
            # Attempt to add a duplicate (checked using the UUIDs of the tests)
            self.project.add_test(data, test)
        # Add the test to another data set's list of tests
        data = [_ for _ in self.project.get_data_sets() if _ != data][0]
        num_tests: int = len(self.project.get_tests(data))
        self.project.add_test(data, test)
        tests = self.project.get_tests(data)
        self.assertEqual(len(tests), num_tests + 1)
        self.assertTrue(test in tests)

    def test_delete_test(self):
        data: DataSet
        for data in self.project.get_data_sets():
            tests: List[TestResult] = self.project.get_tests(data)
            if len(tests) < 2:
                continue
            break
        else:
            raise NotImplementedError("No suitable test data available in the project!")
        test: TestResult = tests[0]
        num_tests: int = len(tests)
        self.project.delete_test(data, test)
        tests = self.project.get_tests(data)
        self.assertEqual(len(tests), num_tests - 1)
        data = [_ for _ in self.project.get_data_sets() if _ != data][0]
        self.assertTrue(test not in tests)
        with self.assertRaises(AssertionError):
            # Attempt to remove test from a data set that the test does not belong to
            self.project.delete_test(data, tests[0])

    def test_get_all_zhits(self):
        zhits: Dict[str, List[ZHITResult]] = self.project.get_all_zhits()
        self.assertIsInstance(zhits, dict)
        self.assertTrue(all([isinstance(_, str) for _ in zhits.keys()]))
        self.assertTrue(all([isinstance(_, list) for _ in zhits.values()]))
        uuids: List[str] = [_.uuid for _ in self.project.get_data_sets()]
        self.assertTrue(all([_ in uuids for _ in zhits.keys()]))

    def test_get_zhits(self):
        data: DataSet
        for data in self.project.get_data_sets():
            zhits: List[ZHITResult] = self.project.get_zhits(data)
            self.assertIsInstance(zhits, list)
            self.assertTrue(all([isinstance(_, ZHITResult) for _ in zhits]))

    def test_add_zhit(self):
        data: DataSet
        for data in self.project.get_data_sets():
            zhits: List[ZHITResult] = self.project.get_zhits(data)
            if len(zhits) == 0:
                continue
            break
        else:
            raise NotImplementedError(
                "No suitable Z-HIT data available in the project!"
            )
        zhit: ZHITResult = zhits[0]
        with self.assertRaises(AssertionError):
            # Attempt to add a duplicate (checked using the UUIDs of the Z-HITs)
            self.project.add_zhit(data, zhit)
        # Add the Z-HIT to another data set's list of Z-HITs
        data = [_ for _ in self.project.get_data_sets() if _ != data][0]
        num_zhits: int = len(self.project.get_zhits(data))
        self.project.add_zhit(data, zhit)
        zhits = self.project.get_zhits(data)
        self.assertEqual(len(zhits), num_zhits + 1)
        self.assertTrue(zhit in zhits)

    def test_delete_zhit(self):
        data: DataSet
        for data in self.project.get_data_sets():
            zhits: List[ZHITResult] = self.project.get_zhits(data)
            if len(zhits) < 2:
                continue
            break
        else:
            raise NotImplementedError(
                "No suitable Z-HIT data available in the project!"
            )
        zhit: ZHITResult = zhits[0]
        num_zhits: int = len(zhits)
        self.project.delete_zhit(data, zhit)
        zhits = self.project.get_zhits(data)
        self.assertEqual(len(zhits), num_zhits - 1)
        self.assertTrue(zhit not in zhits)
        data = [_ for _ in self.project.get_data_sets() if _ != data][0]
        with self.assertRaises(AssertionError):
            # Attempt to remove Z-HIT from a data set that the Z-HIT does not belong to
            self.project.delete_zhit(data, zhits[0])

    def test_get_all_drts(self):
        drts: Dict[str, List[DRTResult]] = self.project.get_all_drts()
        self.assertIsInstance(drts, dict)
        self.assertTrue(all([isinstance(_, str) for _ in drts.keys()]))
        self.assertTrue(all([isinstance(_, list) for _ in drts.values()]))
        uuids: List[str] = [_.uuid for _ in self.project.get_data_sets()]
        self.assertTrue(all([_ in uuids for _ in drts.keys()]))

    def test_get_drts(self):
        data: DataSet
        for data in self.project.get_data_sets():
            drts: List[DRTResult] = self.project.get_drts(data)
            self.assertIsInstance(drts, list)
            self.assertTrue(all([isinstance(_, DRTResult) for _ in drts]))

    def test_add_drt(self):
        data: DataSet
        for data in self.project.get_data_sets():
            drts: List[DRTResult] = self.project.get_drts(data)
            if len(drts) == 0:
                continue
            break
        else:
            raise NotImplementedError("No suitable DRT data available in the project!")
        drt: DRTResult = drts[0]
        with self.assertRaises(AssertionError):
            # Attempt to add a duplicate (checked using the UUIDs of the DRTs)
            self.project.add_drt(data, drt)
        # Add the DRT to another data set's list of DRTs
        data = [_ for _ in self.project.get_data_sets() if _ != data][0]
        num_drts: int = len(self.project.get_drts(data))
        self.project.add_drt(data, drt)
        drts = self.project.get_drts(data)
        self.assertEqual(len(drts), num_drts + 1)
        self.assertTrue(drt in drts)

    def test_delete_drt(self):
        data: DataSet
        for data in self.project.get_data_sets():
            drts: List[DRTResult] = self.project.get_drts(data)
            if len(drts) < 2:
                continue
            break
        else:
            raise NotImplementedError("No suitable DRT data available in the project!")
        drt: DRTResult = drts[0]
        num_drts: int = len(drts)
        self.project.delete_drt(data, drt)
        drts = self.project.get_drts(data)
        self.assertEqual(len(drts), num_drts - 1)
        self.assertTrue(drt not in drts)
        data = [_ for _ in self.project.get_data_sets() if _ != data][0]
        with self.assertRaises(AssertionError):
            # Attempt to remove DRT from a data set that the DRT does not belong to
            self.project.delete_drt(data, drts[0])

    def test_get_all_fits(self):
        fits: Dict[str, List[FitResult]] = self.project.get_all_fits()
        self.assertIsInstance(fits, dict)
        self.assertTrue(all([isinstance(_, str) for _ in fits.keys()]))
        self.assertTrue(all([isinstance(_, list) for _ in fits.values()]))
        uuids: List[str] = [_.uuid for _ in self.project.get_data_sets()]
        self.assertTrue(all([_ in uuids for _ in fits.keys()]))

    def test_get_fits(self):
        data: DataSet
        for data in self.project.get_data_sets():
            fits: List[FitResult] = self.project.get_fits(data)
            self.assertIsInstance(fits, list)
            self.assertTrue(all([isinstance(_, FitResult) for _ in fits]))

    def test_add_fit(self):
        data: DataSet
        for data in self.project.get_data_sets():
            fits: List[FitResult] = self.project.get_fits(data)
            if len(fits) == 0:
                continue
            break
        else:
            raise NotImplementedError("No suitable fit data available in the project!")
        fit: FitResult = fits[0]
        with self.assertRaises(AssertionError):
            # Attempt to add a duplicate (checked using the UUIDs of the fits)
            self.project.add_fit(data, fit)
        # Add the fit to another data set's list of fits
        data = [_ for _ in self.project.get_data_sets() if _ != data][0]
        num_fits: int = len(self.project.get_fits(data))
        self.project.add_fit(data, fit)
        fits = self.project.get_fits(data)
        self.assertEqual(len(fits), num_fits + 1)
        self.assertTrue(fit in fits)

    def test_delete_fit(self):
        data: DataSet
        for data in self.project.get_data_sets():
            fits: List[FitResult] = self.project.get_fits(data)
            if len(fits) < 2:
                continue
            break
        else:
            raise NotImplementedError("No suitable fit data available in the project!")
        fit: FitResult = fits[0]
        num_fits: int = len(fits)
        self.project.delete_fit(data, fit)
        fits = self.project.get_fits(data)
        self.assertEqual(len(fits), num_fits - 1)
        self.assertTrue(fit not in fits)
        data = [_ for _ in self.project.get_data_sets() if _ != data][0]
        with self.assertRaises(AssertionError):
            # Attempt to remove fit from a data set that the fit does not belong to
            self.project.delete_fit(data, fits[0])

    def test_get_simulations(self):
        simulations: List[SimulationResult] = self.project.get_simulations()
        self.assertIsInstance(simulations, list)
        self.assertTrue(all([isinstance(_, SimulationResult) for _ in simulations]))

    def test_add_simulation(self):
        simulations: List[SimulationResult] = self.project.get_simulations()
        num_simulations: int = len(simulations)
        sim: SimulationResult = simulations[0]
        dictionary = sim.to_dict()
        dictionary["uuid"] += "_test"
        sim = SimulationResult.from_dict(dictionary)
        self.project.add_simulation(sim)
        simulations = self.project.get_simulations()
        self.assertEqual(len(simulations), num_simulations + 1)
        self.assertTrue(sim in simulations)
        with self.assertRaises(AssertionError):
            self.project.add_simulation(sim)

    def test_delete_simulation(self):
        simulations: List[SimulationResult] = self.project.get_simulations()
        sim: SimulationResult = simulations[0]
        num_simulations: int = len(simulations)
        self.project.delete_simulation(sim)
        simulations = self.project.get_simulations()
        self.assertEqual(len(simulations), num_simulations - 1)
        self.assertTrue(sim not in simulations)
        with self.assertRaises(AssertionError):
            self.project.delete_simulation(sim)

    def test_get_plots(self):
        plots: List[PlotSettings] = self.project.get_plots()
        self.assertIsInstance(plots, list)
        self.assertTrue(all([isinstance(_, PlotSettings) for _ in plots]))

    def test_edit_plot_label(self):
        plot: PlotSettings = self.project.get_plots()[0]
        new_label: str = "Test"
        self.assertNotEqual(plot.get_label(), new_label)
        self.project.edit_plot_label(plot, new_label)
        self.assertEqual(plot.get_label(), new_label)

    def test_add_plot(self):
        plots: List[PlotSettings] = self.project.get_plots()
        num_plots: int = len(plots)
        plot: PlotSettings = plots[0]
        with self.assertRaises(AssertionError):
            self.project.add_plot(plot)
        dictionary = plot.to_dict(session=False)
        dictionary["uuid"] += "_test"
        plot = PlotSettings.from_dict(dictionary)
        self.project.add_plot(plot)
        plots = self.project.get_plots()
        self.assertEqual(len(plots), num_plots + 1)
        self.assertTrue(plot in plots)

    def test_delete_plot(self):
        plots: List[PlotSettings] = self.project.get_plots()
        num_plots: int = len(plots)
        plot: PlotSettings = plots[0]
        self.project.delete_plot(plot)
        plots = self.project.get_plots()
        self.assertEqual(len(plots), num_plots - 1)
        self.assertTrue(plot not in plots)

    def test_get_plot_series(self):
        plot: PlotSettings
        for plot in self.project.get_plots():
            series: List[PlotSeries] = self.project.get_plot_series(plot)
            self.assertIsInstance(series, list)
            self.assertTrue(all([isinstance(_, PlotSeries) for _ in series]))
