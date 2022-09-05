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

from os.path import (
    dirname,
    join,
)
from typing import (
    Dict,
    List,
    Tuple,
    Type,
)
from unittest import TestCase
from numpy import (
    allclose,
    angle,
    ndarray,
)
import pyimpspec
import deareis


TEST_PROJECT_PATH: str = join(dirname(__file__), "example-project-v4.json")
TEST_DATA_PATH: str = join(dirname(__file__), "data-1.idf")


class TestData(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.control_data_sets: List[pyimpspec.DataSet] = pyimpspec.parse_data(
            TEST_DATA_PATH
        )
        cls.data_sets: List[deareis.DataSet] = deareis.parse_data(TEST_DATA_PATH)

    def test_01_return_type(self):
        self.assertEqual(type(self.control_data_sets), type(self.data_sets))
        self.assertTrue(
            all(map(lambda _: type(_) is pyimpspec.DataSet, self.control_data_sets))
        )
        self.assertTrue(all(map(lambda _: type(_) is deareis.DataSet, self.data_sets)))
        self.assertTrue(isinstance(self.data_sets[0], pyimpspec.DataSet))

    def test_02_return_values(self):
        self.assertEqual(len(self.control_data_sets), 1)
        self.assertEqual(len(self.control_data_sets), len(self.data_sets))

    def test_03_num_points(self):
        self.assertEqual(
            self.control_data_sets[0].get_num_points(),
            self.data_sets[0].get_num_points(),
        )

    def test_04_frequency(self):
        self.assertTrue(
            allclose(
                self.control_data_sets[0].get_frequency(),
                self.data_sets[0].get_frequency(),
            )
        )

    def test_05_impedance(self):
        self.assertTrue(
            allclose(
                self.control_data_sets[0].get_impedance(),
                self.data_sets[0].get_impedance(),
            )
        )


class TestElements(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.control_elements: Dict[
            str, Type[pyimpspec.Element]
        ] = pyimpspec.get_elements()
        cls.elements: Dict[str, Type[deareis.Element]] = deareis.get_elements()

    def test_01_return_type(self):
        self.assertEqual(type(self.control_elements), dict)
        self.assertTrue(
            all(map(lambda _: type(_) is str, self.control_elements.keys()))
        )
        self.assertTrue(
            all(
                map(
                    lambda _: issubclass(_, pyimpspec.Element),
                    self.control_elements.values(),
                )
            )
        )
        self.assertEqual(type(self.elements), dict)
        self.assertTrue(all(map(lambda _: type(_) is str, self.elements.keys())))
        self.assertTrue(
            all(
                map(
                    lambda _: issubclass(_, deareis.Element),
                    self.elements.values(),
                )
            )
        )
        self.assertEqual(type(self.control_elements), type(self.elements))

    def test_02_return_values(self):
        self.assertTrue(len(self.control_elements) > 0)
        self.assertEqual(len(self.control_elements), len(self.elements))
        self.assertEqual(list(self.control_elements.keys()), list(self.elements.keys()))
        self.assertEqual(
            list(self.control_elements.values()), list(self.elements.values())
        )


class TestCDC(TestCase):
    @classmethod
    def setUpClass(cls):
        cdc: str = "R{R=53.2:sol}([R{R=325.162:ct}W]C{C=1.68E-11:dl})"
        cls.control_circuit: pyimpspec.Circuit = pyimpspec.parse_cdc(cdc)
        cls.circuit: deareis.Circuit = deareis.parse_cdc(cdc)

    def test_01_return_type(self):
        self.assertEqual(type(self.control_circuit), type(self.circuit))

    def test_02_to_string(self):
        self.assertEqual(str(self.control_circuit), str(self.circuit))
        self.assertEqual(self.control_circuit.to_string(6), self.circuit.to_string(6))
        self.assertTrue(str(self.control_circuit) == str(self.circuit) == "[R([RW]C)]")
        self.assertEqual(
            self.circuit.to_string(1),
            "[R{R=5.3E+01:sol}([R{R=3.3E+02:ct}W{Y=1.0E+00/0.0E+00}]C{C=1.7E-11:dl})]",
        )

    def test_03_circuit_builder(self):
        cdc: str = "R{R=53.2:sol}([R{R=325.162:ct}W]C{C=1.68E-11:dl})"
        with deareis.CircuitBuilder() as builder:
            R: deareis.Resistor = deareis.Resistor(R=53.2)
            R.set_label("sol")
            builder.add(R)
            with builder.parallel() as parallel:
                with parallel.series() as series:
                    R: deareis.Resistor = deareis.Resistor(R=325.162)
                    R.set_label("ct")
                    series.add(R)
                    series.add(deareis.Warburg())
                C: deareis.Capacitor = deareis.Capacitor(C=1.68e-11)
                C.set_label("dl")
                parallel.add(C)
        self.assertEqual(builder.to_string(), self.circuit.to_string())


class TestKramersKronig(TestCase):
    @classmethod
    def setUpClass(cls):
        control_data: pyimpspec.DataSet = pyimpspec.parse_data(TEST_DATA_PATH)[0]
        cls.data: deareis.DataSet = deareis.parse_data(TEST_DATA_PATH)[0]
        settings: deareis.TestSettings = deareis.TestSettings(
            test=deareis.Test.COMPLEX,
            mode=deareis.TestMode.AUTO,
            num_RC=cls.data.get_num_points(),
            mu_criterion=0.7,
            add_capacitance=True,
            add_inductance=False,
            method=deareis.CNLSMethod.LEASTSQ,
            max_nfev=50,
        )
        cls.control_result: deareis.TestResult = deareis.perform_test(
            control_data,
            settings,
        )
        cls.result: deareis.TestResult = deareis.perform_test(cls.data, settings)
        settings = deareis.TestSettings(
            test=deareis.Test.COMPLEX,
            mode=deareis.TestMode.EXPLORATORY,
            num_RC=cls.data.get_num_points(),
            mu_criterion=0.7,
            add_capacitance=True,
            add_inductance=False,
            method=deareis.CNLSMethod.LEASTSQ,
            max_nfev=50,
        )
        cls.control_exploratory_results: List[
            pyimpspec.TestResult
        ] = pyimpspec.perform_exploratory_tests(
            cls.data,
            test="complex",
            num_RCs=list([_ for _ in range(1, cls.data.get_num_points() + 1)]),
            mu_criterion=0.7,
            add_capacitance=True,
            add_inductance=False,
            method="leastsq",
            max_nfev=50,
        )
        cls.exploratory_results: List[
            deareis.TestResult
        ] = deareis.perform_exploratory_tests(
            cls.data,
            settings,
        )

    def test_01_return_type(self):
        self.assertTrue(
            type(self.control_result) == type(self.result) == deareis.TestResult
        )
        self.assertTrue(
            type(self.control_exploratory_results) is list
            and all(
                map(
                    lambda _: type(_) is pyimpspec.TestResult,
                    self.control_exploratory_results,
                )
            )
        )
        self.assertTrue(
            type(self.exploratory_results) is list
            and all(
                map(lambda _: type(_) is deareis.TestResult, self.exploratory_results)
            )
        )

    def test_02_settings(self):
        res: deareis.TestResult
        for res in [self.result, self.control_result]:
            self.assertEqual(res.settings.test, deareis.Test.COMPLEX)
            self.assertEqual(res.settings.mode, deareis.TestMode.AUTO)
            self.assertEqual(res.settings.mu_criterion, 0.7)
            self.assertEqual(res.settings.add_capacitance, True)
            self.assertEqual(res.settings.add_inductance, False)
            self.assertEqual(res.settings.method, deareis.CNLSMethod.LEASTSQ)
            self.assertEqual(res.settings.max_nfev, 50)

    def test_03_num_RC(self):
        self.assertEqual(self.control_result.num_RC, self.result.num_RC)
        self.assertTrue(self.result.num_RC < self.data.get_num_points())

    def test_04_chisqr(self):
        self.assertEqual(self.control_result.pseudo_chisqr, self.result.pseudo_chisqr)

    def test_05_impedance(self):
        data_impedance: ndarray = self.data.get_impedance()
        test_impedance: ndarray = self.result.get_impedance()
        self.assertTrue(type(data_impedance) == type(test_impedance))
        self.assertEqual(type(test_impedance), ndarray)
        self.assertEqual(len(test_impedance), len(data_impedance))
        self.assertTrue(abs(sum(data_impedance.real - test_impedance.real)) < 6e-2)
        self.assertTrue(abs(sum(data_impedance.imag - test_impedance.imag)) < 2e-1)

    def test_06_exploratory_results(self):
        self.assertEqual(
            len(self.control_exploratory_results), len(self.exploratory_results)
        )
        for i in range(0, len(self.exploratory_results)):
            self.assertEqual(
                self.control_exploratory_results[i].num_RC,
                self.exploratory_results[i].num_RC,
            )
        self.assertEqual(self.exploratory_results[0].settings.mu_criterion, 0.7)
        self.assertEqual(
            self.exploratory_results[0].calculate_score(0.7),
            self.control_exploratory_results[0].calculate_score(0.7),
        )
        control_scores: List[float] = list(
            map(
                lambda _: _.calculate_score(0.7),
                self.control_exploratory_results,
            )
        )
        scores: List[float] = list(
            map(lambda _: _.calculate_score(0.7), self.exploratory_results)
        )
        self.assertTrue(allclose(scores, control_scores))
        self.assertEqual(scores[0], max(scores))


class TestFitting(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.control_data: pyimpspec.DataSet = pyimpspec.parse_data(TEST_DATA_PATH)[0]
        cls.data: deareis.DataSet = deareis.parse_data(TEST_DATA_PATH)[0]
        cls.settings: deareis.FitSettings = deareis.FitSettings(
            cdc="R{R=90}(R{R=230}C{C=7.8E-7})(R{R=570}W{Y=4.25E-4})",
            method=deareis.CNLSMethod.LEAST_SQUARES,
            weight=deareis.Weight.PROPORTIONAL,
            max_nfev=200,
        )
        cls.control_result: deareis.FitResult = deareis.fit_circuit(
            cls.control_data, cls.settings
        )
        cls.result: deareis.FitResult = deareis.fit_circuit(cls.data, cls.settings)

    def test_01_return_type(self):
        self.assertTrue(
            type(self.control_result) == type(self.result) == deareis.FitResult
        )

    def test_02_settings(self):
        res: deareis.FitResult
        for res in [self.result, self.control_result]:
            self.assertEqual(res.settings.cdc, self.settings.cdc)
            self.assertEqual(res.settings.method, self.settings.method)
            self.assertEqual(res.settings.weight, self.settings.weight)
            self.assertEqual(res.settings.max_nfev, self.settings.max_nfev)

    def test_03_statistics(self):
        self.assertEqual(self.control_result.chisqr, self.result.chisqr)

    def test_04_fitted_parameters(self):
        self.assertAlmostEqual(self.result.parameters["R_0"]["R"].value, 100, delta=1e0)
        self.assertAlmostEqual(self.result.parameters["R_1"]["R"].value, 200, delta=1e0)
        self.assertAlmostEqual(
            self.result.parameters["C_2"]["C"].value, 800e-9, delta=1e-8
        )
        self.assertAlmostEqual(self.result.parameters["R_3"]["R"].value, 500, delta=1e0)
        self.assertAlmostEqual(
            self.result.parameters["W_4"]["Y"].value, 400e-6, delta=1e-5
        )

    def test_05_impedance(self):
        data_impedance: ndarray = self.data.get_impedance()
        fit_impedance: ndarray = self.result.get_impedance()
        self.assertTrue(type(data_impedance) == type(fit_impedance))
        self.assertEqual(type(fit_impedance), ndarray)
        self.assertEqual(len(fit_impedance), len(data_impedance))
        self.assertTrue(abs(sum(data_impedance.real - fit_impedance.real)) < 5e-1)
        self.assertTrue(abs(sum(data_impedance.imag - fit_impedance.imag)) < 5e-1)

    def test_06_markdown(self):
        lines: List[str] = self.result.to_dataframe().to_markdown().split("\n")
        self.assertEqual(len(lines), 7)
        line: str = lines.pop(0)
        self.assertTrue(
            0
            < line.index("Element")
            < line.index("Parameter")
            < line.index("Value")
            < line.index("Std. err. (%)")
            < line.index("Fixed")
        )
        lines.pop(0)
        i: int = 0
        while lines:
            line = lines.pop(0)
            columns: List[str] = list(
                filter(lambda _: _ != "", map(str.strip, line.split("|")))
            )
            self.assertEqual(len(columns), 6)
            self.assertEqual(int(columns[0]), i)
            self.assertTrue(columns[1].endswith(f"_{i}"))
            self.assertTrue(columns[1] in self.result.parameters)
            self.assertAlmostEqual(
                float(columns[3]),
                self.result.parameters[columns[1]][columns[2]].value,
                delta=0.1 * self.result.parameters[columns[1]][columns[2]].value,
            )
            self.assertEqual(
                columns[5],
                "Yes"
                if self.result.parameters[columns[1]][columns[2]].fixed is True
                else "No",
            )
            i += 1

    def test_07_latex(self):
        lines = self.result.to_dataframe().to_latex().split("\n")
        self.assertEqual(lines.pop(0), r"\begin{tabular}{lllrrl}")
        self.assertEqual(lines.pop(0), r"\toprule")
        line = lines.pop(0)
        self.assertTrue(
            0
            < line.index("Element")
            < line.index("Parameter")
            < line.index("Value")
            < line.index(r"Std. err. (\%)")
            < line.index("Fixed")
        )
        self.assertEqual(lines.pop(0), r"\midrule")
        self.assertEqual(lines.pop(), "")
        self.assertEqual(lines.pop(), r"\end{tabular}")
        self.assertEqual(lines.pop(), r"\bottomrule")
        i = 0
        while lines:
            line = lines.pop(0).replace(r"\\", "").strip()
            if line == "":
                continue
            columns: List[str] = list(
                filter(lambda _: _ != "", map(str.strip, line.split("&")))
            )
            self.assertEqual(len(columns), 6)
            self.assertEqual(int(columns[0]), i)
            self.assertTrue(columns[1].endswith(f"_{i}"))
            self.assertTrue(columns[1].replace(r"\_", "_") in self.result.parameters)
            self.assertAlmostEqual(
                float(columns[3]),
                self.result.parameters[columns[1].replace(r"\_", "_")][
                    columns[2]
                ].value,
                delta=0.1
                * self.result.parameters[columns[1].replace(r"\_", "_")][
                    columns[2]
                ].value,
            )
            self.assertEqual(
                columns[5],
                "Yes"
                if self.result.parameters[columns[1].replace(r"\_", "_")][
                    columns[2]
                ].fixed
                is True
                else "No",
            )
            i += 1


class TestSimulation(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parameter_values: List[float] = [
            25.0,  # R_0
            100.0,  # R_1
            1.5e-6,  # C_2
        ]
        cls.settings: deareis.SimulationSettings = deareis.SimulationSettings(
            cdc=f"R{{R={cls.parameter_values[0]}}}(R{{R={cls.parameter_values[1]}}}C{{C={cls.parameter_values[2]}}})",
            min_frequency=2.5e-1,
            max_frequency=5e5,
            num_per_decade=5,
        )
        cls.simulation: deareis.SimulationResult = deareis.simulate_spectrum(
            cls.settings
        )

    def test_01_return_type(self):
        self.assertEqual(type(self.simulation), deareis.SimulationResult)

    def test_02_frequencies(self):
        self.assertEqual(
            len(self.simulation.get_frequency()),
            len(
                pyimpspec.analysis.fitting._interpolate(
                    [self.settings.min_frequency, self.settings.max_frequency],
                    self.settings.num_per_decade,
                )
            ),
        )
        frequency: ndarray = self.simulation.get_frequency()
        self.assertEqual(type(frequency), ndarray)

    def test_03_impedance(self):
        impedance: ndarray = self.simulation.get_impedance()
        self.assertEqual(type(impedance), ndarray)
        frequency: ndarray = self.simulation.get_frequency()
        num_points: int = len(frequency)
        self.assertEqual(num_points, len(impedance))

    def test_04_nyquist_data(self):
        nyquist_data: Tuple[ndarray, ndarray] = self.simulation.get_nyquist_data()
        self.assertEqual(type(nyquist_data), tuple)
        self.assertEqual(len(nyquist_data), 2)
        self.assertTrue(all(map(lambda _: type(_) is ndarray, nyquist_data)))
        impedance: ndarray = self.simulation.get_impedance()
        num_points: int = impedance.size
        self.assertEqual(num_points, len(nyquist_data[0]))
        self.assertEqual(num_points, len(nyquist_data[1]))
        self.assertTrue(allclose(impedance.real, nyquist_data[0]))
        self.assertTrue(allclose(-impedance.imag, nyquist_data[1]))

    def test_05_bode_data(self):
        bode_data: Tuple[ndarray, ndarray, ndarray] = self.simulation.get_bode_data()
        self.assertEqual(type(bode_data), tuple)
        self.assertEqual(len(bode_data), 3)
        self.assertTrue(all(map(lambda _: type(_) is ndarray, bode_data)))
        impedance: ndarray = self.simulation.get_impedance()
        num_points: int = impedance.size
        self.assertEqual(num_points, len(bode_data[0]))
        self.assertEqual(num_points, len(bode_data[1]))
        self.assertEqual(num_points, len(bode_data[2]))
        frequency: ndarray = self.simulation.get_frequency()
        self.assertTrue(allclose(frequency, bode_data[0]))
        self.assertTrue(allclose(abs(impedance), bode_data[1]))
        self.assertTrue(allclose(-angle(impedance, deg=True), bode_data[2]))

    def test_06_markdown(self):
        lines: List[str] = self.simulation.to_dataframe().to_markdown().split("\n")
        self.assertEqual(len(lines), 5)
        line: str = lines.pop(0)
        self.assertTrue(
            0 < line.index("Element") < line.index("Parameter") < line.index("Value")
        )
        lines.pop(0)
        i: int = 0
        while lines:
            line = lines.pop(0)
            columns: List[str] = list(
                filter(lambda _: _ != "", map(str.strip, line.split("|")))
            )
            self.assertEqual(len(columns), 4)
            self.assertEqual(int(columns[0]), i)
            self.assertTrue(columns[1].endswith(f"_{i}"))
            self.assertAlmostEqual(
                float(columns[3]),
                self.parameter_values[i],
                delta=0.1 * self.parameter_values[i],
            )
            i += 1

    def test_07_latex(self):
        lines = self.simulation.to_dataframe().to_latex().split("\n")
        self.assertEqual(lines.pop(0), r"\begin{tabular}{lllr}")
        self.assertEqual(lines.pop(0), r"\toprule")
        line = lines.pop(0)
        self.assertTrue(
            0 < line.index("Element") < line.index("Parameter") < line.index("Value")
        )
        self.assertEqual(lines.pop(0), r"\midrule")
        self.assertEqual(lines.pop(), "")
        self.assertEqual(lines.pop(), r"\end{tabular}")
        self.assertEqual(lines.pop(), r"\bottomrule")
        i = 0
        while lines:
            line = lines.pop(0).replace(r"\\", "").strip()
            columns: List[str] = list(
                filter(lambda _: _ != "", map(str.strip, line.split("&")))
            )
            self.assertEqual(len(columns), 4)
            self.assertEqual(int(columns[0]), i)
            self.assertTrue(columns[1].endswith(f"_{i}"))
            self.assertAlmostEqual(
                float(columns[3]),
                self.parameter_values[i],
                delta=0.35 * self.parameter_values[i],
            )
            i += 1


class TestMPL(TestCase):
    def test_01_mpl(self):
        project: deareis.Project = deareis.Project.from_file(TEST_PROJECT_PATH)
        plots: List[deareis.PlotSettings] = project.get_plots()
        fig, axis = deareis.mpl.plot(plots[0], project)


class TestDRT(TestCase):
    @classmethod
    def setUpClass(cls):
        control_data: pyimpspec.DataSet = pyimpspec.parse_data(TEST_DATA_PATH)[0]
        data: deareis.DataSet = deareis.parse_data(TEST_DATA_PATH)[0]
        cls.control_drt: pyimpspec.DRTResult = pyimpspec.calculate_drt(control_data)
        settings: deareis.DRTSettings = deareis.DRTSettings(
            method=deareis.DRTMethod.TR_NNLS,
            mode=deareis.DRTMode.REAL,
            lambda_value=-1.0,
            rbf_type=deareis.RBFType.GAUSSIAN,
            derivative_order=1,
            rbf_shape=deareis.RBFShape.FWHM,
            shape_coeff=0.5,
            inductance=False,
            credible_intervals=False,
            num_samples=2000,
            num_attempts=10,
            maximum_symmetry=0.5,
        )
        cls.drt: deareis.DRTResult = deareis.calculate_drt(data, settings)

    def test_01_final_lambda_value(self):
        self.assertEqual(self.control_drt.lambda_value, self.drt.lambda_value)

    def test_02_chisqr(self):
        self.assertEqual(self.control_drt.chisqr, self.drt.chisqr)

    def test_03_tau(self):
        self.assertTrue(allclose(self.control_drt.get_tau(), self.drt.get_tau()))

    def test_04_gamma(self):
        self.assertTrue(allclose(self.control_drt.get_gamma(), self.drt.get_gamma()))
