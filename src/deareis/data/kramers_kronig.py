# DearEIS is licensed under the GPLv3 or later (https://www.gnu.org/licenses/gpl-3.0.html).
# Copyright 2023 DearEIS developers
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

from dataclasses import dataclass
from typing import (
    Callable,
    Dict,
    Optional,
    Tuple,
    Union,
)
from numpy import (
    angle,
    array,
    inf,
    integer,
    issubdtype,
    log10 as log,
    nan,
)
from pandas import DataFrame
import pyimpspec
from pyimpspec import (
    Capacitor,
    Circuit,
    ComplexImpedances,
    ComplexResiduals,
    Frequencies,
    Impedances,
    Inductor,
    Phases,
    Residuals,
    Resistor,
    Series,
)
from pyimpspec.analysis.utility import _interpolate
from deareis.enums import (
    CNLSMethod,
    TestMode,
    Test,
)
from deareis.utility import (
    format_timestamp,
    rename_dict_entry,
)
from deareis.data import DataSet


VERSION: int = 2


def _parse_settings_v2(dictionary: dict) -> dict:
    return dictionary


def _parse_settings_v1(dictionary: dict) -> dict:
    return dictionary


@dataclass(frozen=True)
class TestSettings:
    """
    A class to store the settings used to perform a Kramers-Kronig test.

    Parameters
    ----------
    test: Test
        The type of test to perform: complex, real, imaginary, or CNLS.
        See pyimpspec and its documentation for details about the different types of tests.

    mode: TestMode
        How to perform the test: automatic, exploratory, or manual.
        The automatic mode uses the procedure described by Schönleber et al. (2014) to determine a suitable number of parallel RC circuits connected in series.
        The exploratory mode is similar to the automatic mode except the user is allowed to choose which of the results to accept and the initial suggestion has additional weighting applied to it in an effort to reduce false negatives that would lead to the conclusion that the data is invalid.
        The manual mode requires the user to pick the number of parallel RC circuits connected in series.

    num_RC: int
        The (maximum) number of parallel RC circuits connected in series.

    mu_criterion: float
        The threshold value used in the procedure described by Schönleber et al. (2014).

    add_capacitance: bool
        Add a capacitance in series to the Voigt circuit.

    add_inductance: bool
        Add an inductance in series to the Voigt circuit.

    method: CNLSMethod
        The iterative method to use if the CNLS test is chosen.

    max_nfev: int
        The maximum number of function evaluations to use if the CNLS test is chosen.
    """

    test: Test
    mode: TestMode
    num_RC: int
    mu_criterion: float
    add_capacitance: bool
    add_inductance: bool
    method: CNLSMethod
    max_nfev: int

    def __repr__(self) -> str:
        return f"TestSettings ({hex(id(self))})"

    @classmethod
    def from_dict(Class, dictionary: dict) -> "TestSettings":
        """
        Create an instance from a dictionary.
        """
        assert type(dictionary) is dict, type(dictionary)
        assert "version" in dictionary
        version: int = dictionary["version"]
        del dictionary["version"]
        assert version >= 1 and version <= VERSION, (
            version,
            VERSION,
        )
        parsers: Dict[int, Callable] = {
            1: _parse_settings_v1,
            2: _parse_settings_v2,
        }
        assert version in parsers, f"{version=} not in {parsers.keys()=}"
        v: int
        p: Callable
        for v, p in parsers.items():
            if v < version:
                continue
            dictionary = p(dictionary)
        assert "test" in dictionary
        assert "mode" in dictionary
        assert "num_RC" in dictionary
        assert "mu_criterion" in dictionary
        assert "add_capacitance" in dictionary
        assert "add_inductance" in dictionary
        assert "method" in dictionary
        assert "max_nfev" in dictionary
        dictionary["test"] = Test(dictionary["test"])
        dictionary["mode"] = TestMode(dictionary["mode"])
        dictionary["method"] = CNLSMethod(dictionary["method"])
        return Class(**dictionary)

    def to_dict(self) -> dict:
        """
        Return a dictionary that can be used to recreate an instance.
        """
        return {
            "version": VERSION,
            "test": self.test,
            "mode": self.mode,
            "num_RC": self.num_RC,
            "mu_criterion": self.mu_criterion,
            "add_capacitance": self.add_capacitance,
            "add_inductance": self.add_inductance,
            "method": self.method,
            "max_nfev": self.max_nfev,
        }


def _parse_result_v2(dictionary: dict) -> dict:
    if "chisqr" in dictionary:
        dictionary["pseudo_chisqr"] = dictionary["chisqr"]
        del dictionary["chisqr"]
    if "pseudo_chisqr" not in dictionary:
        dictionary["pseudo_chisqr"] = nan
    return dictionary


def _parse_result_v1(dictionary: dict) -> dict:
    rename_dict_entry(dictionary, "frequency", "frequencies")
    if "real_impedance" in dictionary:
        rename_dict_entry(dictionary, "real_impedance", "real_impedances")
    if "imaginary_impedance" in dictionary:
        rename_dict_entry(dictionary, "imaginary_impedance", "imaginary_impedances")
    rename_dict_entry(dictionary, "real_residual", "real_residuals")
    rename_dict_entry(dictionary, "imaginary_residual", "imaginary_residuals")
    return dictionary


@dataclass
class TestResult:
    """
    A class containing the result of a Kramers-Kronig test.

    Parameters
    ----------
    uuid: str
        The universally unique identifier assigned to this result.

    timestamp: float
        The Unix time (in seconds) for when the test was performed.

    circuit: Circuit
        The final, fitted circuit.

    num_RC: int
        The final number of parallel RC circuits connected in series.

    mu: float
        The |mu| that was calculated for the result (eq. 21 in Schönleber et al., 2014).

    pseudo_chisqr: float
        The calculated |pseudo chi-squared| (eq. 14 in Boukamp, 1995).

    frequencies: Frequencies
        The frequencies used to perform the test.

    impedances: ComplexImpedances
        The complex impedances of the fitted circuit at each of the frequencies.

    residuals: ComplexResiduals
        The residuals of the real and the imaginary parts of the fit.

    mask: Dict[int, bool]
        The mask that was applied to the DataSet that was tested.

    settings: TestSettings
        The settings that were used to perform the test.
    """

    uuid: str
    timestamp: float
    circuit: Circuit
    num_RC: int
    mu: float
    pseudo_chisqr: float
    frequencies: Frequencies
    impedances: ComplexImpedances
    residuals: ComplexResiduals
    mask: Dict[int, bool]
    settings: TestSettings

    def __post_init__(self):
        self._cached_frequencies: Dict[int, Frequencies] = {}
        self._cached_impedances: Dict[int, ComplexImpedances] = {}

    def __hash__(self) -> int:
        return int(self.uuid, 16)

    def __repr__(self) -> str:
        return f"TestResult ({self.get_label()}, {hex(id(self))})"

    @classmethod
    def from_dict(Class, dictionary: dict, data: Optional[DataSet] = None) -> "TestResult":
        """
        Create an instance from a dictionary.

        Parameters
        ----------
        dictionary: dict
            The dictionary to turn into a TestResult object.

        data: Optional[DataSet], optional
            The DataSet object that this result is for.

        Returns
        -------
        TestResult
        """
        assert isinstance(dictionary, dict), dict
        assert data is None or isinstance(data, DataSet), data
        assert "version" in dictionary
        version: int = dictionary["version"]
        del dictionary["version"]
        assert version <= VERSION, f"{version=} > {VERSION=}"
        parsers: Dict[int, Callable] = {
            1: _parse_result_v1,
            2: _parse_result_v2,
        }
        assert version in parsers, f"{version=} not in {parsers.keys()=}"
        v: int
        p: Callable
        for v, p in parsers.items():
            if v < version:
                continue
            dictionary = p(dictionary)

        assert "uuid" in dictionary
        assert "timestamp" in dictionary
        assert "circuit" in dictionary
        assert "num_RC" in dictionary
        assert "mu" in dictionary
        assert "pseudo_chisqr" in dictionary
        assert "frequencies" in dictionary
        assert "real_residuals" in dictionary
        assert "imaginary_residuals" in dictionary
        assert "settings" in dictionary
        dictionary["circuit"] = pyimpspec.parse_cdc(dictionary["circuit"])
        dictionary["frequencies"] = array(dictionary["frequencies"])
        dictionary["settings"] = TestSettings.from_dict(dictionary["settings"])
        mask: Dict[str, bool] = dictionary["mask"]
        dictionary["mask"] = {
            i: mask.get(str(i), False) for i in range(0, len(dictionary["frequencies"]))
        }
        if (
            "real_impedances" not in dictionary
            or "imaginary_impedances" not in dictionary
        ):
            dictionary["impedances"] = dictionary["circuit"].get_impedances(
                dictionary["frequencies"]
            )
        else:
            dictionary["impedances"] = array(
                list(
                    map(
                        lambda _: complex(*_),
                        zip(
                            dictionary["real_impedances"],
                            dictionary["imaginary_impedances"],
                        ),
                    )
                )
            )
            del dictionary["real_impedances"]
            del dictionary["imaginary_impedances"]
        dictionary["residuals"] = array(
            list(
                map(
                    lambda _: complex(*_),
                    zip(
                        dictionary["real_residuals"],
                        dictionary["imaginary_residuals"],
                    ),
                )
            )
        )
        del dictionary["real_residuals"]
        del dictionary["imaginary_residuals"]
        return Class(**dictionary)

    def to_dict(self, session: bool) -> dict:
        """
        Return a dictionary that can be used to recreate an instance.

        Parameters
        ----------
        session: bool
            If False, then a minimal dictionary will be generated to reduce file size.

        Returns
        -------
        dict
        """
        dictionary: dict = {
            "version": VERSION,
            "uuid": self.uuid,
            "timestamp": self.timestamp,
            "circuit": self.circuit.serialize(),
            "num_RC": self.num_RC,
            "mu": self.mu,
            "pseudo_chisqr": self.pseudo_chisqr,
            "frequencies": list(self.frequencies),
            "real_residuals": list(self.residuals.real),
            "imaginary_residuals": list(self.residuals.imag),
            "mask": {k: True for k, v in self.mask.items() if v is True},
            "settings": self.settings.to_dict(),
        }
        if session:
            dictionary.update(
                {
                    "real_impedances": list(self.impedances.real),
                    "imaginary_impedances": list(self.impedances.imag),
                }
            )
        return dictionary

    def get_label(self) -> str:
        """
        Generate a label for the result.

        Returns
        -------
        str
        """
        label: str = f"#(RC)={self.num_RC}"
        if self.settings.add_capacitance:
            label += ", C"
            if self.settings.add_inductance:
                label += "+L"
        elif self.settings.add_inductance:
            label += ", L"
        timestamp: str = format_timestamp(self.timestamp)
        return f"{label} ({timestamp})"

    def get_frequencies(self, num_per_decade: int = -1) -> Frequencies:
        """
        Get an array of frequencies within the range of tested frequencies.

        Parameters
        ----------
        num_per_decade: int, optional
            If the value is greater than zero, then logarithmically distributed frequencies will be generated within the range of tested frequencies.

        Returns
        -------
        Frequencies
        """
        assert issubdtype(type(num_per_decade), integer), num_per_decade
        if num_per_decade > 0:
            if num_per_decade not in self._cached_frequencies:
                self._cached_frequencies.clear()
                self._cached_frequencies[num_per_decade] = _interpolate(
                    self.frequencies, num_per_decade
                )
            return self._cached_frequencies[num_per_decade]
        return self.frequencies

    def get_impedances(self, num_per_decade: int = -1) -> ComplexImpedances:
        """
        Get the complex impedances produced by the fitted circuit within the range of tested frequencies.

        Parameters
        ----------
        num_per_decade: int, optional
            If the value is greater than zero, then logarithmically distributed frequencies will be generated within the range of tested frequencies and used to calculate the impedance produced by the fitted circuit.

        Returns
        -------
        Frequencies
        """
        assert issubdtype(type(num_per_decade), integer), num_per_decade
        if num_per_decade > 0:
            if num_per_decade not in self._cached_impedances:
                self._cached_impedances.clear()
                self._cached_impedances[num_per_decade] = self.circuit.get_impedances(
                    self.get_frequencies(num_per_decade)
                )
            return self._cached_impedances[num_per_decade]
        return self.impedances

    def get_nyquist_data(
        self, num_per_decade: int = -1
    ) -> Tuple[Impedances, Impedances]:
        """
        Get the data required to plot the results as a Nyquist plot (-Im(Z) vs Re(Z)).

        Parameters
        ----------
        num_per_decade: int, optional
            If the value is greater than zero, then logarithmically distributed frequencies will be generated within the range of tested frequencies and used to calculate the impedance produced by the fitted circuit.

        Returns
        -------
        Tuple[Impedances, Impedances]
        """
        assert issubdtype(type(num_per_decade), integer), num_per_decade
        if num_per_decade > 0:
            Z: ComplexImpedances = self.get_impedances(num_per_decade)
            return (
                Z.real,
                -Z.imag,
            )
        return (
            self.impedances.real,
            -self.impedances.imag,
        )

    def get_bode_data(
        self,
        num_per_decade: int = -1,
    ) -> Tuple[Frequencies, Impedances, Phases]:
        """
        Get the data required to plot the results as a Bode plot (Mode(Z) and -Phase(Z) vs f).

        Parameters
        ----------
        num_per_decade: int, optional
            If the value is greater than zero, then logarithmically distributed frequencies will be generated within the range of tested frequencies and used to calculate the impedance produced by the fitted circuit.

        Returns
        -------
        Tuple[Frequencies, Impedances, Phases]
        """
        assert issubdtype(type(num_per_decade), integer), num_per_decade
        if num_per_decade > 0:
            f: Frequencies = self.get_frequencies(num_per_decade)
            Z: ComplexImpedances = self.get_impedances(num_per_decade)
            return (
                f,
                abs(Z),
                -angle(Z, deg=True),
            )
        return (
            self.frequencies,
            abs(self.impedances),
            -angle(self.impedances, deg=True),
        )

    def get_residuals_data(self) -> Tuple[Frequencies, Residuals, Residuals]:
        """
        Get the data required to plot the residuals (real and imaginary vs f).

        Returns
        -------
        Tuple[Frequencies, Residuals, Residuals]
        """
        return (
            self.frequencies,
            self.residuals.real * 100,
            self.residuals.imag * 100,
        )

    def calculate_score(self, mu_criterion: float) -> float:
        """
        Calculate a score based on the provided |mu|-criterion and the statistics of the result.
        A result with a |mu| greater than or equal to the |mu|-criterion will get a score of -numpy.inf.

        Parameters
        ----------
        mu_criterion: float
            The |mu|-criterion to apply.
            See perform_test for details.

        Returns
        -------
        float
        """
        return (
            -inf
            if self.mu >= mu_criterion
            else -log(self.pseudo_chisqr) / (abs(mu_criterion - self.mu) ** 0.75)
        )

    def get_series_resistance(self) -> float:
        """
        Get the value of the series resistance.

        Returns
        -------
        float
        """
        series: Series = self.circuit.get_elements(flattened=False)[0]
        assert isinstance(series, Series)
        for elem_con in series.get_elements(flattened=False):
            if isinstance(elem_con, Resistor):
                return elem_con.get_value("R")
        return nan

    def get_series_capacitance(self) -> float:
        """
        Get the value of the series capacitance (or numpy.nan if not included in the circuit).

        Returns
        -------
        float
        """
        series: Series = self.circuit.get_elements(flattened=False)[0]
        assert isinstance(series, Series)
        for elem_con in series.get_elements(flattened=False):
            if isinstance(elem_con, Capacitor):
                return elem_con.get_value("C")
        return nan

    def get_series_inductance(self) -> float:
        """
        Get the value of the series inductance (or numpy.nan if not included in the circuit).

        Returns
        -------
        float
        """
        series: Series = self.circuit.get_elements(flattened=False)[0]
        assert isinstance(series, Series)
        for elem_con in series.get_elements(flattened=False):
            if isinstance(elem_con, Inductor):
                return elem_con.get_value("L")
        return nan

    def to_statistics_dataframe(self) -> DataFrame:
        """
        Get the statistics related to the test as a pandas.DataFrame object.

        Returns
        -------
        DataFrame
        """
        statistics: Dict[str, Union[int, float, str]] = {
            "Log pseudo chi-squared": log(self.pseudo_chisqr),
            "Mu": self.mu,
            "Number of parallel RC elements": self.num_RC,
            "Series resistance (ohm)": self.get_series_resistance(),
            "Series capacitance (F)": self.get_series_capacitance(),
            "Series inductance (H)": self.get_series_inductance(),
        }
        return DataFrame.from_dict(
            {
                "Label": list(statistics.keys()),
                "Value": list(statistics.values()),
            }
        )
