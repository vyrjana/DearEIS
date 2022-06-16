# Copyright 2022 DearEIS developers
# DearEIS is licensed under the GPLv3 or later (https://www.gnu.org/licenses/gpl-3.0.html).
# The licenses of DearEIS' dependencies and/or sources of portions of code are included in
# the LICENSES folder.

from unittest import TestCase
from os.path import dirname, exists, join
from numpy import ndarray
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
from typing import List


test_file_paths: List[str] = list(
    map(
        lambda _: join(dirname(__file__), _),
        [
            "example-project-v1.json",
            "example-project-v2.json",
            "example-project-v3.json",
        ],
    )
)


class TestUtility(TestCase):
    def test_01_parsing(self):
        path: str
        for path in test_file_paths:
            self.assertTrue(exists(path))
            project: Project = Project.from_file(path)

    def test_02_version_1(self):
        # TODO: Add more detailed tests
        path: str = test_file_paths[0]
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

    def test_03_version_2(self):
        # TODO: Add more detailed tests
        path: str = test_file_paths[1]
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
        self.assertEqual(type(series.get_scatter_data()), tuple)
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
        self.assertEqual(type(series.get_scatter_data()), tuple)
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
        self.assertEqual(series.get_label(), "2022-03-21 07:23:37")
        self.assertEqual(type(series.get_scatter_data()), tuple)
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
        self.assertEqual(series.get_label(), "[R(RC)(RW)] (2022-03-21 07:24:08)")
        self.assertEqual(type(series.get_scatter_data()), tuple)
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
        series = plot_series[1]
        self.assertEqual(series.get_label(), "Noisy data")
        self.assertEqual(type(series.get_scatter_data()), tuple)
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
        self.assertEqual(series.get_label(), "2022-03-21 07:23:35")
        self.assertEqual(type(series.get_scatter_data()), tuple)
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

    def test_04_version_3(self):
        # TODO: Add more detailed tests
        path: str = test_file_paths[2]
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
        self.assertEqual(type(series.get_scatter_data()), tuple)
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
        self.assertEqual(type(series.get_scatter_data()), tuple)
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
        self.assertEqual(series.get_label(), "2022-03-21 07:23:37")
        self.assertEqual(type(series.get_scatter_data()), tuple)
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
        self.assertEqual(series.get_label(), "[R(RC)(RW)] (2022-03-21 07:24:08)")
        self.assertEqual(type(series.get_scatter_data()), tuple)
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
        series = plot_series[1]
        self.assertEqual(series.get_label(), "Noisy data")
        self.assertEqual(type(series.get_scatter_data()), tuple)
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
        self.assertEqual(series.get_label(), "2022-03-21 07:23:35")
        self.assertEqual(type(series.get_scatter_data()), tuple)
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
