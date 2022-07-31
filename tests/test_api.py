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

from math import isclose
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
    log10 as log,
    ndarray,
)
import pyimpspec
import deareis


TEST_PROJECT_PATH: str = join(dirname(__file__), "example-project-v3.json")
TEST_DATA_PATH: str = join(dirname(__file__), "data-1.idf")


class TestAPI(TestCase):
    def test_01_parse_data(self):
        control_data_sets: List[pyimpspec.DataSet] = pyimpspec.parse_data(
            TEST_DATA_PATH
        )
        data_sets: List[deareis.DataSet] = deareis.parse_data(TEST_DATA_PATH)
        self.assertEqual(type(control_data_sets), type(data_sets))
        self.assertEqual(len(control_data_sets), 1)
        self.assertEqual(len(control_data_sets), len(data_sets))
        self.assertEqual(type(control_data_sets[0]), pyimpspec.DataSet)
        self.assertEqual(type(data_sets[0]), deareis.DataSet)
        self.assertTrue(isinstance(data_sets[0], pyimpspec.DataSet))
        self.assertNotEqual(type(control_data_sets[0]), type(data_sets[0]))
        control_data: pyimpspec.DataSet = control_data_sets[0]
        data: deareis.DataSet = data_sets[0]
        self.assertEqual(control_data.get_num_points(), data.get_num_points())
        self.assertTrue(allclose(control_data.get_frequency(), data.get_frequency()))
        self.assertTrue(allclose(control_data.get_impedance(), data.get_impedance()))

    def test_02_get_elements(self):
        control_elements: Dict[str, Type[pyimpspec.Element]] = pyimpspec.get_elements()
        elements: Dict[str, Type[deareis.Element]] = deareis.get_elements()
        self.assertEqual(type(control_elements), type(elements))
        self.assertTrue(len(control_elements) > 0)
        self.assertEqual(len(control_elements), len(elements))
        self.assertEqual(list(control_elements.keys()), list(elements.keys()))
        self.assertEqual(list(control_elements.values()), list(elements.values()))

    def test_03_string_to_circuit(self):
        cdc: str = "R{R=53.2:sol}([R{R=325.162:ct}W]C{C=1.68E-11:dl})"
        control_circuit: pyimpspec.Circuit = pyimpspec.string_to_circuit(cdc)
        circuit: deareis.Circuit = deareis.string_to_circuit(cdc)
        self.assertEqual(type(control_circuit), type(circuit))
        self.assertEqual(str(control_circuit), str(circuit))
        self.assertEqual(control_circuit.to_string(6), circuit.to_string(6))
        self.assertTrue(str(control_circuit) == str(circuit) == "[R([RW]C)]")
        self.assertEqual(
            circuit.to_string(1),
            "[R{R=5.3E+01:sol}([R{R=3.3E+02:ct}W{Y=1.0E+00/0.0E+00}]C{C=1.7E-11:dl})]",
        )

    def test_04_perform_test(self):
        control_data: pyimpspec.DataSet = pyimpspec.parse_data(TEST_DATA_PATH)[0]
        data: deareis.DataSet = deareis.parse_data(TEST_DATA_PATH)[0]
        test: deareis.Test = deareis.Test.COMPLEX
        mode: deareis.Mode = deareis.Mode.AUTO
        mu_criterion: float = 0.7
        add_capacitance: bool = True
        add_inductance: bool = False
        method: deareis.Method = deareis.Method.LEASTSQ
        max_nfev: int = 50
        settings: deareis.TestSettings = deareis.TestSettings(
            test,
            mode,
            data.get_num_points(),
            mu_criterion,
            add_capacitance,
            add_inductance,
            method,
            max_nfev,
        )
        control_result: deareis.TestResult = deareis.perform_test(
            control_data, settings
        )
        result: deareis.TestResult = deareis.perform_test(data, settings)
        self.assertTrue(type(control_result) == type(result) == deareis.TestResult)
        res: deareis.TestResult
        for res in [result, control_result]:
            self.assertEqual(res.settings.test, test)
            self.assertEqual(res.settings.mode, mode)
            self.assertEqual(res.settings.mu_criterion, mu_criterion)
            self.assertEqual(res.settings.add_capacitance, add_capacitance)
            self.assertEqual(res.settings.add_inductance, add_inductance)
            self.assertEqual(res.settings.method, method)
            self.assertEqual(res.settings.max_nfev, max_nfev)
        self.assertEqual(control_result.num_RC, result.num_RC)
        self.assertTrue(result.num_RC < data.get_num_points())
        self.assertEqual(control_result.pseudo_chisqr, result.pseudo_chisqr)
        data_impedance: ndarray = data.get_impedance()
        test_impedance: ndarray = result.get_impedance()
        self.assertTrue(type(data_impedance) == type(test_impedance))
        self.assertEqual(type(test_impedance), ndarray)
        self.assertEqual(len(test_impedance), len(data_impedance))
        self.assertTrue(abs(sum(data_impedance.real - test_impedance.real)) < 6e-2)
        self.assertTrue(abs(sum(data_impedance.imag - test_impedance.imag)) < 2e-1)

    def test_05_fit_circuit_to_data(self):
        control_data: pyimpspec.DataSet = pyimpspec.parse_data(TEST_DATA_PATH)[0]
        data: deareis.DataSet = deareis.parse_data(TEST_DATA_PATH)[0]
        cdc: str = "R(RC)(RW)"
        method: deareis.Method = deareis.Method.LEAST_SQUARES
        weight: deareis.Weight = deareis.Weight.PROPORTIONAL
        max_nfev: int = 200
        settings: deareis.FitSettings = deareis.FitSettings(
            cdc,
            method,
            weight,
            max_nfev,
        )
        control_result: deareis.FitResult = deareis.fit_circuit_to_data(
            control_data, settings
        )
        result: deareis.FitResult = deareis.fit_circuit_to_data(data, settings)
        self.assertTrue(type(control_result) == type(result) == deareis.FitResult)
        res: deareis.FitResult
        for res in [result, control_result]:
            self.assertEqual(res.settings.cdc, cdc)
            self.assertEqual(res.settings.method, method)
            self.assertEqual(res.settings.weight, weight)
            self.assertEqual(res.settings.max_nfev, max_nfev)
        self.assertEqual(control_result.chisqr, result.chisqr)
        self.assertTrue(isclose(result.parameters["R_0"]["R"].value, 100, abs_tol=1e-1))
        self.assertTrue(isclose(result.parameters["R_1"]["R"].value, 200, abs_tol=1e-1))
        self.assertTrue(
            isclose(result.parameters["C_2"]["C"].value, 800e-9, abs_tol=1e-8)
        )
        self.assertTrue(isclose(result.parameters["R_3"]["R"].value, 500, abs_tol=1e-1))
        self.assertTrue(
            isclose(result.parameters["W_4"]["Y"].value, 400e-6, abs_tol=1e-5)
        )
        data_impedance: ndarray = data.get_impedance()
        fit_impedance: ndarray = result.get_impedance()
        self.assertTrue(type(data_impedance) == type(fit_impedance))
        self.assertEqual(type(fit_impedance), ndarray)
        self.assertEqual(len(fit_impedance), len(data_impedance))
        self.assertTrue(abs(sum(data_impedance.real - fit_impedance.real)) < 3e-1)
        self.assertTrue(abs(sum(data_impedance.imag - fit_impedance.imag)) < 8e-2)

    def test_06_simulate_spectrum(self):
        cdc: str = "R{R=25}(R{R=100}C{C=1.5E-6})"
        min_frequency: float = 2.5e-1
        max_frequency: float = 5e5
        num_per_decade: int = 5
        settings: deareis.SimulationSettings = deareis.SimulationSettings(
            cdc,
            min_frequency,
            max_frequency,
            num_per_decade,
        )
        simulation: deareis.SimulationResult = deareis.simulate_spectrum(settings)
        self.assertEqual(type(simulation), deareis.SimulationResult)
        self.assertEqual(
            len(simulation.get_frequency()),
            len(
                pyimpspec.analysis.fitting._interpolate(
                    [min_frequency, max_frequency], num_per_decade
                )
            ),
        )
        frequency: ndarray = simulation.get_frequency()
        self.assertEqual(type(frequency), ndarray)
        impedance: ndarray = simulation.get_impedance()
        self.assertEqual(type(impedance), ndarray)
        num_points: int = len(frequency)
        self.assertEqual(num_points, len(impedance))
        nyquist_data: Tuple[ndarray, ndarray] = simulation.get_nyquist_data()
        self.assertEqual(type(nyquist_data), tuple)
        self.assertEqual(len(nyquist_data), 2)
        self.assertTrue(all(map(lambda _: type(_) is ndarray, nyquist_data)))
        self.assertEqual(num_points, len(nyquist_data[0]))
        self.assertEqual(num_points, len(nyquist_data[1]))
        self.assertTrue(allclose(impedance.real, nyquist_data[0]))
        self.assertTrue(allclose(-impedance.imag, nyquist_data[1]))
        bode_data: Tuple[ndarray, ndarray, ndarray] = simulation.get_bode_data()
        self.assertEqual(type(bode_data), tuple)
        self.assertEqual(len(bode_data), 3)
        self.assertTrue(all(map(lambda _: type(_) is ndarray, bode_data)))
        self.assertEqual(num_points, len(bode_data[0]))
        self.assertEqual(num_points, len(bode_data[1]))
        self.assertEqual(num_points, len(bode_data[2]))
        self.assertTrue(allclose(log(frequency), bode_data[0]))
        self.assertTrue(allclose(log(abs(impedance)), bode_data[1]))
        self.assertTrue(allclose(-angle(impedance, deg=True), bode_data[2]))

    def test_07_mpl(self):
        project: deareis.Project = deareis.Project.from_file(TEST_PROJECT_PATH)
        plots: List[deareis.PlotSettings] = project.get_plots()
        fig, axis = deareis.mpl.plot(plots[0], project)
