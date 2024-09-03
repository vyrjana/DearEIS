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
    join,
)
from typing import (
    Dict,
    List,
    Optional,
    Tuple,
    Type,
)
from unittest import TestCase
from pandas import DataFrame
from numpy import (
    allclose,
    angle,
    isclose,
    isnan,
    ndarray,
)
import matplotlib
import pyimpspec
import deareis

matplotlib.use("Agg")


TEST_PROJECT_PATH: str = join(dirname(__file__), "example-project-v5.json")
TEST_DATA_PATH: str = join(dirname(__file__), "data-1.idf")


class TestData(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.control_data_sets: List[pyimpspec.DataSet] = pyimpspec.parse_data(
            TEST_DATA_PATH
        )
        cls.data_sets: List[deareis.DataSet] = deareis.parse_data(TEST_DATA_PATH)

    def test_return_type(self):
        self.assertEqual(type(self.control_data_sets), type(self.data_sets))
        self.assertTrue(
            all(map(lambda _: type(_) is pyimpspec.DataSet, self.control_data_sets))
        )
        self.assertTrue(all(map(lambda _: type(_) is deareis.DataSet, self.data_sets)))
        self.assertTrue(isinstance(self.data_sets[0], pyimpspec.DataSet))

    def test_return_values(self):
        self.assertEqual(len(self.control_data_sets), 1)
        self.assertEqual(len(self.control_data_sets), len(self.data_sets))

    def test_num_points(self):
        self.assertEqual(
            self.control_data_sets[0].get_num_points(),
            self.data_sets[0].get_num_points(),
        )

    def test_frequency(self):
        self.assertTrue(
            allclose(
                self.control_data_sets[0].get_frequencies(),
                self.data_sets[0].get_frequencies(),
            )
        )

    def test_impedance(self):
        self.assertTrue(
            allclose(
                self.control_data_sets[0].get_impedances(),
                self.data_sets[0].get_impedances(),
            )
        )


class TestElements(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.control_elements: Dict[
            str, Type[pyimpspec.Element]
        ] = pyimpspec.get_elements()
        cls.elements: Dict[str, Type[deareis.Element]] = deareis.get_elements()

    def test_return_type(self):
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

    def test_return_values(self):
        self.assertGreater(len(self.control_elements), 0)
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

    def test_return_type(self):
        self.assertEqual(type(self.control_circuit), type(self.circuit))

    def test_to_string(self):
        self.assertEqual(str(self.control_circuit), str(self.circuit))
        self.assertEqual(self.control_circuit.to_string(6), self.circuit.to_string(6))
        self.assertTrue(str(self.control_circuit) == str(self.circuit) == "[R([RW]C)]")
        self.assertEqual(
            self.circuit.to_string(1),
            "[R{R=5.3E+01/0.0E+00/inf:sol}([R{R=3.3E+02/0.0E+00/inf:ct}W{Y=1.0E-03/1.0E-24/inf}]C{C=1.7E-11/1.0E-24/1.0E+03:dl})]",
        )

    def test_circuit_builder(self):
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
        with deareis.CircuitBuilder() as builder:
            builder += deareis.Resistor(R=53.2).set_label("sol")
            with builder.parallel() as parallel:
                with parallel.series() as series:
                    series += deareis.Resistor(R=325.162).set_label("ct")
                    series += deareis.Warburg()
                parallel += deareis.Capacitor(C=1.68e-11).set_label("dl")
        self.assertEqual(builder.to_string(), self.circuit.to_string())


# TODO: Update tests
class TestKramersKronig(TestCase):
    @classmethod
    def setUpClass(cls):
        control_data: pyimpspec.DataSet = pyimpspec.parse_data(TEST_DATA_PATH)[0]
        cls.data: deareis.DataSet = deareis.parse_data(TEST_DATA_PATH)[0]

        suggestion_settings: deareis.KramersKronigSuggestionSettings 
        suggestion_settings = deareis.KramersKronigSuggestionSettings(
            methods=[],
            use_mean=False,
            use_ranking=False,
            use_sum=False,
            lower_limit=0,
            upper_limit=0,
            limit_delta=0,
            m1_mu_criterion=0.7,
            m1_beta=0.75,
        )

        test_settings: deareis.KramersKronigSettings
        test_settings = deareis.KramersKronigSettings(
            test=deareis.KramersKronigTest.COMPLEX_LEASTSQ,
            mode=deareis.KramersKronigMode.AUTO,
            representation=deareis.KramersKronigRepresentation.AUTO,
            add_capacitance=True,
            add_inductance=True,
            num_RC=0,
            min_log_F_ext=-1.0,
            max_log_F_ext=1.0,
            log_F_ext=0.0,
            num_F_ext_evaluations=20,
            rapid_F_ext_evaluations=True,
            cnls_method=deareis.CNLSMethod.LEASTSQ,
            max_nfev=50,
            timeout=60,
            suggestion_settings=suggestion_settings,
        )
        
        cls.control_result: deareis.KramersKronigResult = pyimpspec.perform_kramers_kronig_test(
            control_data,
            test="complex",
            admittance=None,
            add_capacitance=True,
            add_inductance=True,
            num_RC=0,
            min_log_F_ext=-1.0,
            max_log_F_ext=1.0,
            log_F_ext=0.0,
            num_F_ext_evaluations=20,
            rapid_F_ext_evaluations=True,
            cnls_method="leastsq",
            max_nfev=50,
            timeout=60,
        )
        
        cls.result: deareis.KramersKronigResult = deareis.perform_kramers_kronig_test(
            cls.data,
            settings=test_settings,
        )
        
        test_settings = deareis.KramersKronigSettings(
            test=deareis.KramersKronigTest.COMPLEX_LEASTSQ,
            mode=deareis.KramersKronigMode.EXPLORATORY,
            representation=deareis.KramersKronigRepresentation.AUTO,
            num_RC=cls.data.get_num_points(),
            add_capacitance=True,
            add_inductance=False,
            min_log_F_ext=-1.0,
            max_log_F_ext=1.0,
            log_F_ext=0.0,
            num_F_ext_evaluations=20,
            rapid_F_ext_evaluations=True,
            cnls_method=deareis.CNLSMethod.LEASTSQ,
            max_nfev=50,
            timeout=60,
            suggestion_settings=suggestion_settings,
        )
        
        cls.control_exploratory_results: List[
            pyimpspec.KramersKronigResult
        ] = pyimpspec.perform_exploratory_kramers_kronig_tests(
            cls.data,
            test="complex",
            num_RCs=None,
            mu_criterion=0.7,
            add_capacitance=True,
            add_inductance=True,
            method="leastsq",
            max_nfev=50,
        )
        
        cls.exploratory_results: List[
            deareis.KramersKronigResult
        ] = deareis.perform_exploratory_kramers_kronig_tests(
            cls.data,
            settings=test_settings,
        )

    def test_result(self):
        self.assertIsInstance(self.control_result, pyimpspec.KramersKronigResult)
        self.assertIsInstance(self.result, deareis.KramersKronigResult)

    def test_settings(self):
        self.assertEqual(self.result.settings.test, deareis.KramersKronigTest.COMPLEX_LEASTSQ)
        self.assertEqual(self.result.settings.mode, deareis.KramersKronigMode.AUTO)
        self.assertEqual(self.result.settings.representation, deareis.KramersKronigRepresentation.AUTO)
        self.assertEqual(self.result.settings.add_capacitance, True)
        self.assertEqual(self.result.settings.add_inductance, True)
        self.assertEqual(self.result.settings.cnls_method, deareis.CNLSMethod.LEASTSQ)
        self.assertEqual(self.result.settings.max_nfev, 50)

    def test_num_RC(self):
        self.assertEqual(self.control_result.num_RC, self.result.num_RC)
        # Because the data is not noisy and the test implementation is set to
        # complex (least squares).
        self.assertGreater(self.result.num_RC, self.data.get_num_points())

    def test_pseudo_chisqr(self):
        self.assertEqual(self.control_result.pseudo_chisqr, self.result.pseudo_chisqr)

    def test_impedance(self):
        data_impedance: ndarray = self.data.get_impedances()
        test_impedance: ndarray = self.result.get_impedances()
        self.assertTrue(type(data_impedance) == type(test_impedance))
        self.assertEqual(type(test_impedance), ndarray)
        self.assertEqual(len(test_impedance), len(data_impedance))
        self.assertLess(abs(sum(data_impedance.real - test_impedance.real)), 6e-2)
        self.assertLess(abs(sum(data_impedance.imag - test_impedance.imag)), 2e-1)

    def test_exploratory_results(self):
        self.assertIsInstance(self.control_exploratory_results, tuple)
        self.assertIsInstance(self.exploratory_results, tuple)

        self.assertEqual(len(self.control_exploratory_results), 2)
        self.assertEqual(len(self.exploratory_results), 2)

        self.assertIsInstance(self.control_exploratory_results[0], list)
        self.assertIsInstance(self.exploratory_results[0], list)
        self.assertEqual(len(self.control_exploratory_results[0]), len(self.exploratory_results[0]))

        self.assertIsInstance(self.control_exploratory_results[1], tuple)
        self.assertIsInstance(self.exploratory_results[1], tuple)
        self.assertEqual(len(self.control_exploratory_results[1]), 4)
        self.assertEqual(len(self.exploratory_results[1]), 4)
        self.assertIsInstance(self.control_exploratory_results[1][0], pyimpspec.KramersKronigResult)
        self.assertIsInstance(self.exploratory_results[1][0], deareis.KramersKronigResult)
        self.assertIsInstance(self.control_exploratory_results[1][1], dict)
        self.assertIsInstance(self.exploratory_results[1][1], dict)
        self.assertIsInstance(self.control_exploratory_results[1][2], int)
        self.assertIsInstance(self.exploratory_results[1][2], int)
        self.assertIsInstance(self.control_exploratory_results[1][3], int)
        self.assertIsInstance(self.exploratory_results[1][3], int)

        for i in range(0, len(self.exploratory_results[0])):
            self.assertEqual(
                self.control_exploratory_results[0][i].num_RC,
                self.exploratory_results[0][i].num_RC,
            )

    def test_to_statistics_dataframe(self):
        df: DataFrame = self.result.to_statistics_dataframe()
        self.assertIsInstance(df, DataFrame)
        markdown_lines: List[str] = df.to_markdown().strip().split("\n")[2:]
        label_lines: List[str] = [
            "Log pseudo chi-squared",
            "Number of RC elements",
            "Log Fext (extension factor for time constant range)",
            "Parallel resistance (ohm)",
            "Parallel capacitance (F)",
            "Parallel inductance (H)",
            "Mean of residuals, real (% of |Z|)",
            "Mean of residuals, imag. (% of |Z|)",
            "SD of residuals, real (% of |Z|)",
            "SD of residuals, imag. (% of |Z|)",
            "Residuals within 1 SD, real (%)",
            "Residuals within 1 SD, imag. (%)",
            "Residuals within 2 SD, real (%)",
            "Residuals within 2 SD, imag. (%)",
            "Residuals within 3 SD, real (%)",
            "Residuals within 3 SD, imag. (%)",
            "Lilliefors test p-value, real",
            "Lilliefors test p-value, imag.",
            "Shapiro-Wilk test p-value, real",
            "Shapiro-Wilk test p-value, imag.",
            "Estimated SD of Gaussian noise (% of |Z|)",
            "One-sample Kolmogorov-Smirnov test p-value, real",
            "One-sample Kolmogorov-Smirnov test p-value, imag.",
        ]
        self.assertEqual(len(markdown_lines), len(label_lines))

        md: str
        label: str
        for md, label in zip(markdown_lines, label_lines):
            self.assertTrue(label in md)


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
            timeout=60,
        )
        cls.control_result: deareis.FitResult = deareis.fit_circuit(
            cls.control_data, cls.settings
        )
        cls.result: deareis.FitResult = deareis.fit_circuit(cls.data, cls.settings)

    def test_return_type(self):
        self.assertIsInstance(self.control_result, deareis.FitResult)
        self.assertIsInstance(self.result, deareis.FitResult)

    def test_settings(self):
        res: deareis.FitResult
        for res in [self.result, self.control_result]:
            self.assertEqual(res.settings.cdc, self.settings.cdc)
            self.assertEqual(res.settings.method, self.settings.method)
            self.assertEqual(res.settings.weight, self.settings.weight)
            self.assertEqual(res.settings.max_nfev, self.settings.max_nfev)

    def test_statistics(self):
        self.assertEqual(self.control_result.pseudo_chisqr, self.result.pseudo_chisqr)

    def test_fitted_parameters(self):
        self.assertAlmostEqual(
            deareis.FittedParameter.from_dict(
                self.result.parameters["R_1"]["R"].to_dict()
            ).get_relative_error(),
            3.7e-4,
            delta=1e-3,
        )
        expected: Dict[str, Dict[str, Tuple[float, float, bool, str]]] = {
            "R_1": {
                "R": (1.00e2, 2e0, False, "ohm"),
            },
            "R_2": {
                "R": (2.00e2, 2e0, False, "ohm"),
            },
            "C_1": {
                "C": (8.00e-7, 1e-8, False, "F"),
            },
            "R_3": {
                "R": (5.00e2, 2e0, False, "ohm"),
            },
            "W_1": {
                "Y": (4.00e-4, 1e-5, False, "S*s^(1/2)"),
                "n": (0.5, 0.1, True, ""),
            },
            "C_2": {
                "C": (1e6, 1e-7, True, "F"),
            },
        }
        for element_label, parameters in self.result.parameters.items():
            self.assertIsInstance(element_label, str)
            self.assertTrue("_" in element_label)
            self.assertIsInstance(parameters, dict)
            for parameter_label, param in parameters.items():
                self.assertIsInstance(parameter_label, str)
                self.assertIsInstance(param, deareis.FittedParameter)
                value: float
                delta: float
                fixed: bool
                unit: str
                value, delta, fixed, unit = expected[element_label][parameter_label]
                self.assertAlmostEqual(param.get_value(), value, delta=delta)
                self.assertEqual(param.is_fixed(), fixed)
                self.assertEqual(param.get_unit(), unit)
                if not isnan(param.get_error()):
                    self.assertEqual(
                        param.get_relative_error(),
                        param.get_error() / param.get_value(),
                    )

    def test_impedance(self):
        data_impedance: ndarray = self.data.get_impedances()
        fit_impedance: ndarray = self.result.get_impedances()
        self.assertTrue(type(data_impedance) == type(fit_impedance))
        self.assertEqual(type(fit_impedance), ndarray)
        self.assertEqual(len(fit_impedance), len(data_impedance))
        self.assertLess(abs(sum(data_impedance.real - fit_impedance.real)), 2)
        self.assertLess(abs(sum(data_impedance.imag - fit_impedance.imag)), 2)

    def test_markdown(self):
        markdown: str = self.result.to_parameters_dataframe().to_markdown()
        lines: List[str] = markdown.split("\n")
        self.assertTrue(lines[0].startswith("|    | Element   | Parameter   |"))
        self.assertTrue(
            lines[0].endswith("Value |   Std. err. (%) | Unit      | Fixed   |")
        )
        self.assertTrue(lines[1].startswith("|---:|:----------|:------------|"))
        self.assertTrue(lines[1].endswith(":|----------------:|:----------|:--------|"))
        self.assertTrue(lines[2].startswith("|  0 | R_1       | R           |"))
        self.assertTrue(lines[2].endswith("| ohm       | No      |"))
        self.assertTrue(lines[3].startswith("|  1 | R_2       | R           |"))
        self.assertTrue(lines[3].endswith("| ohm       | No      |"))
        self.assertTrue(lines[4].startswith("|  2 | C_1       | C           |"))
        self.assertTrue(lines[4].endswith("| F         | No      |"))
        self.assertTrue(lines[5].startswith("|  3 | R_3       | R           |"))
        self.assertTrue(lines[5].endswith("| ohm       | No      |"))
        self.assertTrue(lines[6].startswith("|  4 | W_1       | Y           |"))
        self.assertTrue(lines[6].endswith("| S*s^(1/2) | No      |"))

    def test_latex(self):
        latex: str = (
            self.result.to_parameters_dataframe()
            .style.format(precision=1)
            .format_index(axis=1, escape="latex")
            .to_latex(hrules=True)
        )
        lines: List[str] = latex.split("\n")
        self.assertEqual(lines[0], r"\begin{tabular}{lllrrll}")
        self.assertEqual(lines[1], r"\toprule")
        self.assertEqual(
            lines[2],
            r" & Element & Parameter & Value & Std. err. (\%) & Unit & Fixed \\",
        )
        self.assertEqual(lines[3], r"\midrule")
        self.assertTrue(lines[4].startswith(r"0 & R_1 & R & "))
        self.assertTrue(lines[4].endswith(r" & ohm & No \\"))
        self.assertTrue(lines[5].startswith(r"1 & R_2 & R & "))
        self.assertTrue(lines[5].endswith(r" & ohm & No \\"))
        self.assertTrue(lines[6].startswith(r"2 & C_1 & C & "))
        self.assertTrue(lines[6].endswith(r" & F & No \\"))
        self.assertTrue(lines[7].startswith(r"3 & R_3 & R & "))
        self.assertTrue(lines[7].endswith(r" & ohm & No \\"))
        self.assertTrue(lines[8].startswith(r"4 & W_1 & Y & "))
        self.assertTrue(lines[8].endswith(r" & S*s^(1/2) & No \\"))
        self.assertEqual(lines[9], r"\bottomrule")
        self.assertEqual(lines[10], r"\end{tabular}")

    def test_to_statistics_dataframe(self):
        df: DataFrame = self.result.to_statistics_dataframe()
        self.assertIsInstance(df, DataFrame)
        markdown: str = df.to_markdown()
        self.assertTrue("Log pseudo chi-squared" in markdown)
        self.assertTrue("Log chi-squared" in markdown)
        self.assertTrue("Log chi-squared (reduced)" in markdown)
        self.assertTrue("Akaike info. criterion" in markdown)
        self.assertTrue("Bayesian info. criterion" in markdown)
        self.assertTrue("Degrees of freedom" in markdown)
        self.assertTrue("Number of data points" in markdown)
        self.assertTrue("Number of function evaluations" in markdown)
        self.assertTrue("Method" in markdown)
        self.assertTrue("Weight" in markdown)


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

    def test_return_type(self):
        self.assertEqual(type(self.simulation), deareis.SimulationResult)

    def test_frequencies(self):
        self.assertEqual(
            len(self.simulation.get_frequencies()),
            len(
                pyimpspec.analysis.utility._interpolate(
                    [self.settings.min_frequency, self.settings.max_frequency],
                    self.settings.num_per_decade,
                )
            ),
        )
        frequency: ndarray = self.simulation.get_frequencies()
        self.assertEqual(type(frequency), ndarray)

    def test_impedance(self):
        impedance: ndarray = self.simulation.get_impedances()
        self.assertEqual(type(impedance), ndarray)
        frequency: ndarray = self.simulation.get_frequencies()
        num_points: int = len(frequency)
        self.assertEqual(num_points, len(impedance))

    def test_nyquist_data(self):
        nyquist_data: Tuple[ndarray, ndarray] = self.simulation.get_nyquist_data()
        self.assertEqual(type(nyquist_data), tuple)
        self.assertEqual(len(nyquist_data), 2)
        self.assertTrue(all(map(lambda _: type(_) is ndarray, nyquist_data)))
        impedance: ndarray = self.simulation.get_impedances()
        num_points: int = impedance.size
        self.assertEqual(num_points, len(nyquist_data[0]))
        self.assertEqual(num_points, len(nyquist_data[1]))
        self.assertTrue(allclose(impedance.real, nyquist_data[0]))
        self.assertTrue(allclose(-impedance.imag, nyquist_data[1]))

    def test_bode_data(self):
        bode_data: Tuple[ndarray, ndarray, ndarray] = self.simulation.get_bode_data()
        self.assertEqual(type(bode_data), tuple)
        self.assertEqual(len(bode_data), 3)
        self.assertTrue(all(map(lambda _: type(_) is ndarray, bode_data)))
        impedance: ndarray = self.simulation.get_impedances()
        num_points: int = impedance.size
        self.assertEqual(num_points, len(bode_data[0]))
        self.assertEqual(num_points, len(bode_data[1]))
        self.assertEqual(num_points, len(bode_data[2]))
        frequency: ndarray = self.simulation.get_frequencies()
        self.assertTrue(allclose(frequency, bode_data[0]))
        self.assertTrue(allclose(abs(impedance), bode_data[1]))
        self.assertTrue(allclose(-angle(impedance, deg=True), bode_data[2]))

    def test_markdown(self):
        markdown: str = self.simulation.to_dataframe().to_markdown()
        lines: List[str] = markdown.split("\n")
        self.assertTrue(lines[0].startswith("|    | Element   | Parameter   |"))
        self.assertTrue(lines[0].endswith(" |"))
        self.assertTrue(lines[1].startswith("|---:|:----------|:------------|"))
        self.assertTrue(lines[1].endswith(":|"))
        self.assertTrue(lines[2].startswith("|  0 | R_1       | R           |"))
        self.assertTrue(lines[2].endswith(" |"))
        self.assertTrue(lines[3].startswith("|  1 | R_2       | R           |"))
        self.assertTrue(lines[3].endswith(" |"))
        self.assertTrue(lines[4].startswith("|  2 | C_1       | C           |"))
        self.assertTrue(lines[4].endswith(" |"))

    def test_latex(self):
        latex: str = (
            self.simulation.to_dataframe()
            .style.format(precision=1)
            .format_index(axis=1, escape="latex")
            .to_latex(hrules=True)
        )
        lines: List[str] = latex.split("\n")
        self.assertEqual(lines[0], r"\begin{tabular}{lllr}")
        self.assertEqual(lines[1], r"\toprule")
        self.assertEqual(lines[2], r" & Element & Parameter & Value \\")
        self.assertEqual(lines[3], r"\midrule")
        self.assertTrue(lines[4].startswith(r"0 & R_1 & R & "))
        self.assertTrue(lines[4].endswith(r" \\"))
        self.assertTrue(lines[5].startswith(r"1 & R_2 & R & "))
        self.assertTrue(lines[5].endswith(r" \\"))
        self.assertTrue(lines[6].startswith(r"2 & C_1 & C & "))
        self.assertTrue(lines[6].endswith(r" \\"))
        self.assertEqual(lines[7], r"\bottomrule")
        self.assertEqual(lines[8], r"\end{tabular}")


class TestMPL(TestCase):
    def test_mpl(self):
        project: deareis.Project = deareis.Project.from_file(TEST_PROJECT_PATH)
        plots: List[deareis.PlotSettings] = project.get_plots()
        fig, axis = deareis.mpl.plot(plots[0], project)


# TODO: Update tests
class TestDRT(TestCase):
    @classmethod
    def setUpClass(cls):
        control_data: pyimpspec.DataSet = pyimpspec.parse_data(TEST_DATA_PATH)[0]
        cls.data: deareis.DataSet = deareis.parse_data(TEST_DATA_PATH)[0]
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
            timeout=60,
            num_samples=2000,
            num_attempts=10,
            maximum_symmetry=0.5,
            fit=None,
            gaussian_width=0.15,
            num_per_decade=100,
            cross_validation_method=deareis.CrossValidationMethod.MGCV,
            tr_nnls_lambda_method=deareis.TRNNLSLambdaMethod.CUSTOM,
        )
        cls.drt: deareis.DRTResult = deareis.calculate_drt(cls.data, settings)

    def test_final_lambda_value(self):
        self.assertEqual(self.control_drt.lambda_value, self.drt.lambda_value)

    def test_pseudo_chisqr(self):
        self.assertEqual(self.control_drt.pseudo_chisqr, self.drt.pseudo_chisqr)

    def test_get_time_constants(self):
        self.assertTrue(
            allclose(
                self.control_drt.get_time_constants(),
                self.drt.get_time_constants(),
            )
        )

    def test_get_gammas(self):
        self.assertEqual(self.control_drt.get_gammas().shape, (29,))
        self.assertIsInstance(self.drt.get_gammas(), tuple)
        self.assertEqual(len(self.drt.get_gammas()), 2)
        self.assertTrue(
            allclose(
                self.control_drt.get_gammas(),
                self.drt.get_gammas()[0],
            )
        )
        self.assertEqual(self.drt.get_gammas()[1].shape, (0,))

    def test_to_peaks_dataframe(self):
        df: DataFrame = self.drt.to_peaks_dataframe()
        self.assertIsInstance(df, DataFrame)
        markdown: str = df.to_markdown()
        self.assertTrue("tau (s)" in markdown)
        self.assertTrue("gamma (ohm)" in markdown)

    def test_to_scores_dataframe(self):
        df: Optional[DataFrame] = self.drt.to_scores_dataframe()
        if self.drt.settings.method != deareis.DRTMethod.BHT:
            self.assertTrue(df is None)
            return

    def test_tr_rbf(self):
        deareis.calculate_drt(
            self.data,
            settings=deareis.DRTSettings(
                method=deareis.DRTMethod.TR_RBF,
                mode=deareis.DRTMode.COMPLEX,
                lambda_value=-1.0,
                rbf_type=deareis.RBFType.GAUSSIAN,
                derivative_order=1,
                rbf_shape=deareis.RBFShape.FWHM,
                shape_coeff=0.5,
                inductance=False,
                credible_intervals=False,
                timeout=60,
                num_samples=2000,
                num_attempts=10,
                maximum_symmetry=0.5,
                fit=None,
                gaussian_width=0.15,
                num_per_decade=100,
                cross_validation_method=deareis.CrossValidationMethod.MGCV,
                tr_nnls_lambda_method=deareis.TRNNLSLambdaMethod.CUSTOM,
            )
        )

    def test_bht(self):
        deareis.calculate_drt(
            self.data,
            settings=deareis.DRTSettings(
                method=deareis.DRTMethod.BHT,
                mode=deareis.DRTMode.COMPLEX,
                lambda_value=-1.0,
                rbf_type=deareis.RBFType.GAUSSIAN,
                derivative_order=1,
                rbf_shape=deareis.RBFShape.FWHM,
                shape_coeff=0.5,
                inductance=False,
                credible_intervals=False,
                timeout=60,
                num_samples=2000,
                num_attempts=10,
                maximum_symmetry=0.5,
                fit=None,
                gaussian_width=0.15,
                num_per_decade=100,
                cross_validation_method=deareis.CrossValidationMethod.MGCV,
                tr_nnls_lambda_method=deareis.TRNNLSLambdaMethod.CUSTOM,
            )
        )

    def test_mrq_fit(self):
        fit: deareis.FitResult = deareis.fit_circuit(
            data=self.data,
            settings=deareis.FitSettings(
                cdc="R(RQ)(RQ)",
                method=deareis.CNLSMethod.LEAST_SQUARES,
                weight=deareis.Weight.PROPORTIONAL,
                max_nfev=200,
                timeout=60,
            )
        )
        deareis.calculate_drt(
            self.data,
            settings=deareis.DRTSettings(
                method=deareis.DRTMethod.BHT,
                mode=deareis.DRTMode.COMPLEX,
                lambda_value=-1.0,
                rbf_type=deareis.RBFType.GAUSSIAN,
                derivative_order=1,
                rbf_shape=deareis.RBFShape.FWHM,
                shape_coeff=0.5,
                inductance=False,
                credible_intervals=False,
                timeout=60,
                num_samples=2000,
                num_attempts=10,
                maximum_symmetry=0.5,
                fit=fit,
                gaussian_width=0.15,
                num_per_decade=100,
                cross_validation_method=deareis.CrossValidationMethod.MGCV,
                tr_nnls_lambda_method=deareis.TRNNLSLambdaMethod.CUSTOM,
            )
        )


# TODO: Update tests
class TestZHIT(TestCase):
    @classmethod
    def setUpClass(cls):
        control_data: pyimpspec.DataSet = pyimpspec.parse_data(TEST_DATA_PATH)[0]
        data: deareis.DataSet = deareis.parse_data(TEST_DATA_PATH)[0]
        cls.control_zhit: pyimpspec.ZHITResult = pyimpspec.perform_zhit(control_data)
        settings: deareis.ZHITSettings = deareis.ZHITSettings(
            smoothing=deareis.ZHITSmoothing.MODSINC,
            num_points=3,
            polynomial_order=2,
            num_iterations=3,
            interpolation=deareis.ZHITInterpolation.AKIMA,
            window=deareis.ZHITWindow.AUTO,
            window_center=1.5,
            window_width=3.0,
            representation=deareis.ZHITRepresentation.IMPEDANCE,
        )
        cls.zhit: deareis.ZHITResult = deareis.perform_zhit(data, settings)

    def test_get_label(self):
        self.assertTrue(self.zhit.get_label().startswith("Z-HIT ("))

    def test_pseudo_chisqr(self):
        self.assertTrue(
            isclose(
                self.control_zhit.pseudo_chisqr,
                self.zhit.pseudo_chisqr,
            )
        )

    def test_modulus(self):
        self.assertTrue(
            allclose(
                abs(self.control_zhit.get_impedances()),
                abs(self.zhit.get_impedances()),
            )
        )

    def test_phase(self):
        self.assertTrue(
            allclose(
                -angle(self.control_zhit.get_impedances()),
                -angle(self.zhit.get_impedances()),
            )
        )

    def test_final_settings(self):
        self.assertEqual(self.control_zhit.smoothing, self.zhit.smoothing)
        self.assertEqual(self.control_zhit.interpolation, self.zhit.interpolation)
        self.assertEqual(self.control_zhit.window, self.zhit.window)

    def test_to_statistics_dataframe(self):
        df: DataFrame = self.zhit.to_statistics_dataframe()
        self.assertIsInstance(df, DataFrame)
        markdown: str = df.to_markdown()
        self.assertTrue("Log pseudo chi-squared" in markdown)
        self.assertTrue("Smoothing" in markdown)
        self.assertTrue("Interpolation" in markdown)
        self.assertTrue("Window" in markdown)
