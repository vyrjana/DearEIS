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

from os.path import dirname, exists, join
from typing import (
    Dict,
    List,
)
from unittest import TestCase
from numpy import ndarray
import deareis
from deareis import (
    DataSet,
    FitResult,
    Project,
    TestResult,
    SimulationResult,
    PlotSettings,
    PlotSeries,
    PlotType,
)


TEST_PROJECT_PATHS: List[str] = list(
    map(
        lambda _: join(dirname(__file__), _),
        [
            "example-project-v1.json",
            "example-project-v2.json",
            "example-project-v3.json",
        ],
    )
)


TEST_DATA_PATHS: List[str] = list(
    map(
        lambda _: join(dirname(__file__), _),
        [
            "data-1.idf",
            "data-2.csv",
        ],
    )
)


class TestUtility(TestCase):
    def test_01_instantiation(self):
        project: Project = Project()
        self.assertEqual(len(project.get_data_sets()), 0)
        self.assertEqual(len(project.get_all_tests()), 0)
        self.assertEqual(len(project.get_all_fits()), 0)
        self.assertEqual(len(project.get_simulations()), 0)
        self.assertEqual(len(project.get_plots()), 1)
        path: str
        for path in TEST_PROJECT_PATHS:
            self.assertTrue(exists(path))
            project = Project.from_file(path)

    def test_02_merge(self):
        project: Project = Project.merge(
            list(map(lambda _: Project.from_file(_), TEST_PROJECT_PATHS))
        )

    def test_03_label(self):
        project: Project = Project.from_file(TEST_PROJECT_PATHS[-1])
        old_label: str = project.get_label()
        self.assertEqual(old_label, "Example project - Version 3")
        new_label: str = "Test label"
        project.set_label(new_label)
        self.assertEqual(project.get_label(), new_label)
        self.assertRaises(AssertionError, lambda: project.set_label(""))
        self.assertRaises(AssertionError, lambda: project.set_label("  \t"))

    def test_04_path(self):
        project: Project = Project.from_file(TEST_PROJECT_PATHS[-1])
        old_path: str = project.get_path()
        self.assertTrue(old_path.endswith("example-project-v3.json"))
        new_path: str = "Testing"
        project.set_path(new_path)
        self.assertEqual(project.get_path(), new_path)

    def test_05_notes(self):
        project: Project = Project.from_file(TEST_PROJECT_PATHS[-1])
        old_notes: str = project.get_notes()
        self.assertEqual(old_notes, "This is for keeping notes about the project.")
        new_notes: str = "Lorem ipsum"
        project.set_notes(new_notes)
        self.assertEqual(project.get_notes(), new_notes)

    def test_06_data_set(self):
        project: Project = Project.from_file(TEST_PROJECT_PATHS[-1])
        data_sets: List[DataSet] = project.get_data_sets()
        self.assertEqual(type(data_sets), list)
        self.assertTrue(all(map(lambda _: type(_) is DataSet, data_sets)))
        self.assertEqual(len(data_sets), 2)
        data: DataSet = deareis.parse_data(TEST_DATA_PATHS[0])[0]
        project.add_data_set(data)
        data_sets = project.get_data_sets()
        self.assertEqual(len(data_sets), 3)
        self.assertEqual(data_sets[2].get_label(), "Test")
        new_label: str = "ABC"
        project.edit_data_set_label(data, new_label)
        self.assertEqual(data.get_label(), new_label)
        data_sets = project.get_data_sets()
        self.assertEqual(len(data_sets), 3)
        self.assertTrue(data.get_label() == data_sets[0].get_label() == new_label)
        new_path: str = "XYZ"
        project.edit_data_set_path(data, new_path)
        self.assertTrue(data.get_path() == data_sets[0].get_path() == new_path)
        old_data: DataSet = data
        new_data: DataSet = deareis.parse_data(TEST_DATA_PATHS[1])[0]
        self.assertRaises(
            AssertionError, lambda: project.replace_data_set(old_data, new_data)
        )
        new_data.uuid = old_data.uuid
        project.replace_data_set(old_data, new_data)
        data_sets = project.get_data_sets()
        self.assertEqual(len(data_sets), 3)
        self.assertTrue(new_data.get_label() == data_sets[2].get_label() == "data-2")
        project.delete_data_set(new_data)
        data_sets = project.get_data_sets()
        self.assertEqual(len(data_sets), 2)

    def test_07_tests(self):
        project: Project = Project.from_file(TEST_PROJECT_PATHS[-1])
        tests: Dict[str, List[TestResult]] = project.get_all_tests()
        self.assertEqual(type(tests), dict)
        self.assertEqual(len(tests), 2)
        self.assertTrue(all(map(lambda _: type(_) is list, tests.values())))
        self.assertTrue(
            all(map(lambda _: type(_) is TestResult, list(tests.values())[0]))
        )
        data_sets: List[DataSet] = project.get_data_sets()
        data: DataSet
        for data in data_sets:
            self.assertTrue(data.uuid in tests)
        data_tests: List[TestResult] = project.get_tests(data_sets[0])
        self.assertEqual(type(data_tests), list)
        self.assertEqual(len(data_tests), 1)
        self.assertEqual(type(data_tests[0]), TestResult)
        project.delete_test(data_sets[0], data_tests[0])
        data_tests = project.get_tests(data_sets[0])
        self.assertEqual(len(data_tests), 0)
        project.delete_data_set(data_sets[0])
        tests = project.get_all_tests()
        self.assertEqual(len(tests), 1)
        data: DataSet = deareis.parse_data(TEST_DATA_PATHS[1])[0]
        project.add_data_set(data)
        project.add_test(data, list(tests.values())[0][0])
        tests = project.get_all_tests()
        self.assertEqual(len(tests), 2)
        self.assertEqual(len(list(tests.values())[1]), 1)

    def test_08_fits(self):
        project: Project = Project.from_file(TEST_PROJECT_PATHS[-1])
        fits: Dict[str, List[FitResult]] = project.get_all_fits()
        self.assertEqual(type(fits), dict)
        self.assertEqual(len(fits), 2)
        self.assertTrue(all(map(lambda _: type(_) is list, fits.values())))
        self.assertTrue(
            all(map(lambda _: type(_) is FitResult, list(fits.values())[0]))
        )
        data_sets: List[DataSet] = project.get_data_sets()
        data: DataSet
        for data in data_sets:
            self.assertTrue(data.uuid in fits)
        data_fits: List[FitResult] = project.get_fits(data_sets[0])
        self.assertEqual(type(data_fits), list)
        self.assertEqual(len(data_fits), 1)
        self.assertEqual(type(data_fits[0]), FitResult)
        project.delete_fit(data_sets[0], data_fits[0])
        data_fits = project.get_fits(data_sets[0])
        self.assertEqual(len(data_fits), 0)
        project.delete_data_set(data_sets[0])
        fits = project.get_all_fits()
        self.assertEqual(len(fits), 1)
        data: DataSet = deareis.parse_data(TEST_DATA_PATHS[1])[0]
        project.add_data_set(data)
        project.add_fit(data, list(fits.values())[0][0])
        fits = project.get_all_fits()
        self.assertEqual(len(fits), 2)
        self.assertEqual(len(list(fits.values())[1]), 1)

    def test_09_simulations(self):
        project: Project = Project.from_file(TEST_PROJECT_PATHS[-1])
        sims: List[SimulationResult] = project.get_simulations()
        self.assertEqual(type(sims), list)
        self.assertEqual(len(sims), 2)
        self.assertTrue(all(map(lambda _: type(_) is SimulationResult, sims)))
        sim: SimulationResult = sims[0]
        project.delete_simulation(sim)
        sims = project.get_simulations()
        self.assertEqual(len(sims), 1)
        project.add_simulation(sim)
        sims = project.get_simulations()
        self.assertEqual(len(sims), 2)

    def test_10_plots(self):
        project: Project = Project.from_file(TEST_PROJECT_PATHS[-1])
        plots: List[PlotSettings] = project.get_plots()
        self.assertEqual(type(plots), list)
        self.assertEqual(len(plots), 3)
        self.assertTrue(all(map(lambda _: type(_) is PlotSettings, plots)))
        new_label: str = "Test"
        project.edit_plot_label(plots[0], new_label)
        plots = project.get_plots()
        plot: PlotSettings = plots[2]
        self.assertEqual(plot.get_label(), new_label)
        project.delete_plot(plot)
        plots = project.get_plots()
        self.assertEqual(len(plots), 2)
        self.assertTrue(not any(map(lambda _: _.get_label() == new_label, plots)))
        project.add_plot(plot)
        plots = project.get_plots()
        self.assertEqual(len(plots), 3)
        self.assertEqual(plots[2].get_label(), new_label)
        series: List[PlotSeries] = project.get_plot_series(plot)
        self.assertEqual(type(series), list)
        self.assertEqual(len(series), 8)
        self.assertTrue(all(map(lambda _: type(_) is PlotSeries, series)))

    def test_11_version_1(self):
        # TODO: Add more detailed tests
        path: str = TEST_PROJECT_PATHS[0]
        project: Project = Project.from_file(path)
        self.assertEqual(project.get_path(), path)
        self.assertEqual(project.get_label(), "Example project - Version 1")
        # - data sets
        datasets: List[DataSet] = project.get_data_sets()
        self.assertEqual(type(datasets), list)
        self.assertEqual(len(datasets), 2)
        self.assertTrue(all(map(lambda _: type(_) is DataSet, datasets)))
        # - tests
        tests: List[TestResult] = project.get_tests(datasets[0])
        self.assertEqual(type(tests), list)
        self.assertEqual(len(tests), 1)
        self.assertTrue(all(map(lambda _: type(_) is TestResult, tests)))
        tests = project.get_tests(datasets[1])
        self.assertEqual(type(tests), list)
        self.assertEqual(len(tests), 1)
        self.assertTrue(all(map(lambda _: type(_) is TestResult, tests)))
        # - fits
        fits: List[FitResult] = project.get_fits(datasets[0])
        self.assertEqual(type(fits), list)
        self.assertEqual(len(fits), 1)
        self.assertTrue(all(map(lambda _: type(_) is FitResult, fits)))
        fits = project.get_fits(datasets[1])
        self.assertEqual(type(fits), list)
        self.assertEqual(len(fits), 1)
        self.assertTrue(all(map(lambda _: type(_) is FitResult, fits)))
        # - simulations
        simulations: List[SimulationResult] = project.get_simulations()
        self.assertEqual(type(simulations), list)
        self.assertEqual(len(simulations), 2)
        self.assertTrue(all(map(lambda _: type(_) is SimulationResult, simulations)))
        # - plots
        plots: List[PlotSettings] = project.get_plots()
        self.assertEqual(type(plots), list)
        self.assertEqual(len(plots), 1)

    def test_12_version_2(self):
        # TODO: Add more detailed tests
        path: str = TEST_PROJECT_PATHS[1]
        project: Project = Project.from_file(path)
        self.assertEqual(project.get_path(), path)
        self.assertEqual(project.get_label(), "Example project - Version 2")
        # - data sets
        datasets: List[DataSet] = project.get_data_sets()
        self.assertEqual(type(datasets), list)
        self.assertEqual(len(datasets), 2)
        self.assertTrue(all(map(lambda _: type(_) is DataSet, datasets)))
        # - tests
        tests: List[TestResult] = project.get_tests(datasets[0])
        self.assertEqual(type(tests), list)
        self.assertEqual(len(tests), 1)
        self.assertTrue(all(map(lambda _: type(_) is TestResult, tests)))
        tests = project.get_tests(datasets[1])
        self.assertEqual(type(tests), list)
        self.assertEqual(len(tests), 1)
        self.assertTrue(all(map(lambda _: type(_) is TestResult, tests)))
        # - fits
        fits: List[FitResult] = project.get_fits(datasets[0])
        self.assertEqual(type(fits), list)
        self.assertEqual(len(fits), 1)
        self.assertTrue(all(map(lambda _: type(_) is FitResult, fits)))
        fits = project.get_fits(datasets[1])
        self.assertEqual(type(fits), list)
        self.assertEqual(len(fits), 1)
        self.assertTrue(all(map(lambda _: type(_) is FitResult, fits)))
        # - simulations
        simulations: List[SimulationResult] = project.get_simulations()
        self.assertEqual(type(simulations), list)
        self.assertEqual(len(simulations), 2)
        self.assertTrue(all(map(lambda _: type(_) is SimulationResult, simulations)))
        # - plots
        plots: List[PlotSettings] = project.get_plots()
        self.assertEqual(type(plots), list)
        self.assertEqual(len(plots), 3)
        #
        plot: PlotSettings = plots[0]
        self.assertEqual(plot.get_label(), "Appearance template")
        self.assertEqual(plot.get_type(), PlotType.NYQUIST)
        plot_series: List[PlotSeries] = project.get_plot_series(plot)
        series: PlotSeries = plot_series[0]
        self.assertEqual(series.get_label(), "Ideal data")
        self.assertEqual(type(series.get_scatter_data()), list)
        self.assertEqual(len(series.get_scatter_data()), 2)
        self.assertTrue(
            all(
                map(
                    lambda _: type(_) is ndarray and len(_.shape) == 1,
                    series.get_scatter_data(),
                )
            )
        )
        self.assertEqual(type(series.get_color()), list)
        self.assertEqual(len(series.get_color()), 4)
        self.assertEqual(series.has_markers(), True)
        self.assertEqual(series.has_line(), False)
        series = plot_series[1]
        self.assertEqual(series.get_label(), "Noisy data")
        self.assertEqual(type(series.get_scatter_data()), list)
        self.assertEqual(len(series.get_scatter_data()), 2)
        self.assertTrue(
            all(
                map(
                    lambda _: type(_) is ndarray and len(_.shape) == 1,
                    series.get_scatter_data(),
                )
            )
        )
        self.assertEqual(type(series.get_color()), list)
        self.assertEqual(len(series.get_color()), 4)
        self.assertEqual(series.has_markers(), True)
        self.assertEqual(series.has_line(), False)
        series = plot_series[2]
        self.assertEqual(type(series.get_scatter_data()), list)
        self.assertEqual(len(series.get_scatter_data()), 2)
        self.assertTrue(
            all(
                map(
                    lambda _: type(_) is ndarray and len(_.shape) == 1,
                    series.get_scatter_data(),
                )
            )
        )
        self.assertEqual(type(series.get_color()), list)
        self.assertEqual(len(series.get_color()), 4)
        self.assertEqual(series.has_markers(), True)
        self.assertEqual(series.has_line(), True)
        #
        plot = plots[1]
        self.assertEqual(plot.get_label(), "Ideal")
        self.assertEqual(plot.get_type(), PlotType.NYQUIST)
        #
        plot = plots[2]
        self.assertEqual(plot.get_label(), "Noisy")
        self.assertEqual(plot.get_type(), PlotType.NYQUIST)
        plot_series = project.get_plot_series(plot)
        series = plot_series[0]
        self.assertTrue(series.get_label().startswith("[R(RC)(RW)] ("))
        self.assertEqual(type(series.get_scatter_data()), list)
        self.assertEqual(len(series.get_scatter_data()), 2)
        self.assertTrue(
            all(
                map(
                    lambda _: type(_) is ndarray and len(_.shape) == 1,
                    series.get_scatter_data(),
                )
            )
        )
        self.assertEqual(type(series.get_color()), list)
        self.assertEqual(len(series.get_color()), 4)
        self.assertEqual(series.has_markers(), False)
        self.assertEqual(series.has_line(), True)
        series = plot_series[1]
        self.assertTrue(series.get_label().startswith("[R(RC)(RW)] ("))
        self.assertEqual(type(series.get_scatter_data()), list)
        self.assertEqual(len(series.get_scatter_data()), 2)
        self.assertTrue(
            all(
                map(
                    lambda _: type(_) is ndarray and len(_.shape) == 1,
                    series.get_scatter_data(),
                )
            )
        )
        self.assertEqual(type(series.get_color()), list)
        self.assertEqual(len(series.get_color()), 4)
        self.assertEqual(series.has_markers(), True)
        self.assertEqual(series.has_line(), True)
        series = plot_series[2]
        self.assertEqual(series.get_label(), "Noisy data")
        self.assertEqual(type(series.get_scatter_data()), list)
        self.assertEqual(len(series.get_scatter_data()), 2)
        self.assertTrue(
            all(
                map(
                    lambda _: type(_) is ndarray and len(_.shape) == 1,
                    series.get_scatter_data(),
                )
            )
        )
        self.assertEqual(type(series.get_color()), list)
        self.assertEqual(len(series.get_color()), 4)
        self.assertEqual(series.has_markers(), True)
        self.assertEqual(series.has_line(), False)

    def test_13_version_3(self):
        # TODO: Add more detailed tests
        path: str = TEST_PROJECT_PATHS[2]
        project: Project = Project.from_file(path)
        self.assertEqual(project.get_path(), path)
        self.assertEqual(project.get_label(), "Example project - Version 3")
        # - data sets
        datasets: List[DataSet] = project.get_data_sets()
        self.assertEqual(type(datasets), list)
        self.assertEqual(len(datasets), 2)
        self.assertTrue(all(map(lambda _: type(_) is DataSet, datasets)))
        # - tests
        tests: List[TestResult] = project.get_tests(datasets[0])
        self.assertEqual(type(tests), list)
        self.assertEqual(len(tests), 1)
        self.assertTrue(all(map(lambda _: type(_) is TestResult, tests)))
        tests = project.get_tests(datasets[1])
        self.assertEqual(type(tests), list)
        self.assertEqual(len(tests), 1)
        self.assertTrue(all(map(lambda _: type(_) is TestResult, tests)))
        # - fits
        fits: List[FitResult] = project.get_fits(datasets[0])
        self.assertEqual(type(fits), list)
        self.assertEqual(len(fits), 1)
        self.assertTrue(all(map(lambda _: type(_) is FitResult, fits)))
        fits = project.get_fits(datasets[1])
        self.assertEqual(type(fits), list)
        self.assertEqual(len(fits), 1)
        self.assertTrue(all(map(lambda _: type(_) is FitResult, fits)))
        # - simulations
        simulations: List[SimulationResult] = project.get_simulations()
        self.assertEqual(type(simulations), list)
        self.assertEqual(len(simulations), 2)
        self.assertTrue(all(map(lambda _: type(_) is SimulationResult, simulations)))
        # - plots
        plots: List[PlotSettings] = project.get_plots()
        self.assertEqual(type(plots), list)
        self.assertEqual(len(plots), 3)
        #
        plot: PlotSettings = plots[0]
        self.assertEqual(plot.get_label(), "Appearance template")
        self.assertEqual(plot.get_type(), PlotType.NYQUIST)
        plot_series: List[PlotSeries] = project.get_plot_series(plot)
        series: PlotSeries = plot_series[0]
        self.assertEqual(series.get_label(), "Ideal data")
        self.assertEqual(type(series.get_scatter_data()), list)
        self.assertEqual(len(series.get_scatter_data()), 2)
        self.assertTrue(
            all(
                map(
                    lambda _: type(_) is ndarray and len(_.shape) == 1,
                    series.get_scatter_data(),
                )
            )
        )
        self.assertEqual(type(series.get_color()), list)
        self.assertEqual(len(series.get_color()), 4)
        self.assertEqual(series.has_markers(), True)
        self.assertEqual(series.has_line(), False)
        series = plot_series[1]
        self.assertEqual(series.get_label(), "Noisy data")
        self.assertEqual(type(series.get_scatter_data()), list)
        self.assertEqual(len(series.get_scatter_data()), 2)
        self.assertTrue(
            all(
                map(
                    lambda _: type(_) is ndarray and len(_.shape) == 1,
                    series.get_scatter_data(),
                )
            )
        )
        self.assertEqual(type(series.get_color()), list)
        self.assertEqual(len(series.get_color()), 4)
        self.assertEqual(series.has_markers(), True)
        self.assertEqual(series.has_line(), False)
        series = plot_series[2]
        self.assertEqual(type(series.get_scatter_data()), list)
        self.assertEqual(len(series.get_scatter_data()), 2)
        self.assertTrue(
            all(
                map(
                    lambda _: type(_) is ndarray and len(_.shape) == 1,
                    series.get_scatter_data(),
                )
            )
        )
        self.assertEqual(type(series.get_color()), list)
        self.assertEqual(len(series.get_color()), 4)
        self.assertEqual(series.has_markers(), True)
        self.assertEqual(series.has_line(), True)
        #
        plot = plots[1]
        self.assertEqual(plot.get_label(), "Ideal")
        self.assertEqual(plot.get_type(), PlotType.NYQUIST)
        #
        plot = plots[2]
        self.assertEqual(plot.get_label(), "Noisy")
        self.assertEqual(plot.get_type(), PlotType.NYQUIST)
        plot_series = project.get_plot_series(plot)
        series = plot_series[0]
        self.assertTrue(series.get_label().startswith("[R(RC)(RW)] ("))
        self.assertEqual(type(series.get_scatter_data()), list)
        self.assertEqual(len(series.get_scatter_data()), 2)
        self.assertTrue(
            all(
                map(
                    lambda _: type(_) is ndarray and len(_.shape) == 1,
                    series.get_scatter_data(),
                )
            )
        )
        self.assertEqual(type(series.get_color()), list)
        self.assertEqual(len(series.get_color()), 4)
        self.assertEqual(series.has_markers(), False)
        self.assertEqual(series.has_line(), True)
        series = plot_series[1]
        self.assertTrue(series.get_label().startswith("[R(RC)(RW)] ("))
        self.assertEqual(type(series.get_scatter_data()), list)
        self.assertEqual(len(series.get_scatter_data()), 2)
        self.assertTrue(
            all(
                map(
                    lambda _: type(_) is ndarray and len(_.shape) == 1,
                    series.get_scatter_data(),
                )
            )
        )
        self.assertEqual(type(series.get_color()), list)
        self.assertEqual(len(series.get_color()), 4)
        self.assertEqual(series.has_markers(), True)
        self.assertEqual(series.has_line(), True)
        series = plot_series[2]
        self.assertEqual(series.get_label(), "Noisy data")
        self.assertEqual(type(series.get_scatter_data()), list)
        self.assertEqual(len(series.get_scatter_data()), 2)
        self.assertTrue(
            all(
                map(
                    lambda _: type(_) is ndarray and len(_.shape) == 1,
                    series.get_scatter_data(),
                )
            )
        )
        self.assertEqual(type(series.get_color()), list)
        self.assertEqual(len(series.get_color()), 4)
        self.assertEqual(series.has_markers(), True)
        self.assertEqual(series.has_line(), False)
