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

from dataclasses import dataclass
from typing import (
    Callable,
    Dict,
    Tuple,
)
from numpy import (
    angle,
    array,
    inf,
    integer,
    issubdtype,
    log10 as log,
    ndarray,
)
import pyimpspec
from pyimpspec import Circuit
from deareis.data.data_sets import DataSet
from pyimpspec.analysis.fitting import _interpolate
from deareis.enums import (
    CNLSMethod,
    TestMode,
    Test,
)
from deareis.utility import format_timestamp


VERSION: int = 1


def _parse_settings_v1(dictionary: dict) -> dict:
    assert type(dictionary) is dict
    return {
        "test": Test(dictionary["test"]),
        "mode": TestMode(dictionary["mode"]),
        "num_RC": dictionary["num_RC"],
        "mu_criterion": dictionary["mu_criterion"],
        "add_capacitance": dictionary["add_capacitance"],
        "add_inductance": dictionary["add_inductance"],
        "method": CNLSMethod(dictionary["method"]),
        "max_nfev": dictionary["max_nfev"],
    }


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
        }
        assert version in parsers, (
            version,
            parsers,
        )
        assert version in parsers, f"{version=} not in {parsers.keys()=}"
        return Class(**parsers[version](dictionary))

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


def _parse_result_v1(dictionary: dict) -> dict:
    assert type(dictionary) is dict
    return {
        "uuid": dictionary["uuid"],
        "timestamp": dictionary["timestamp"],
        "circuit": pyimpspec.parse_cdc(dictionary["circuit"]),
        "num_RC": dictionary["num_RC"],
        "mu": dictionary["mu"],
        "pseudo_chisqr": dictionary["pseudo_chisqr"],
        "frequency": array(dictionary["frequency"]),
        "real_residual": array(dictionary["real_residual"]),
        "imaginary_residual": array(dictionary["imaginary_residual"]),
        "mask": {int(k): v for k, v in dictionary.get("mask", {}).items()},
        "impedance": array(
            list(
                map(
                    lambda _: complex(*_),
                    zip(
                        dictionary["real_impedance"],
                        dictionary["imaginary_impedance"],
                    ),
                )
            )
        ),
        "settings": TestSettings.from_dict(dictionary["settings"]),
    }


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
        The mu-value that was calculated for the result.

    pseudo_chisqr: float
        The pseudo chi-squared value calculated according to eq. N in Boukamp (1995).

    frequency: ndarray
        The frequencies used to perform the test.

    impedance: ndarray
        The complex impedances of the fitted circuit at each of the frequencies.

    real_residual: ndarray
        The residuals of the real part of the complex impedances.

    imaginary_residual: ndarray
        The residuals of the imaginary part of the complex impedances.

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
    frequency: ndarray
    impedance: ndarray
    real_residual: ndarray
    imaginary_residual: ndarray
    mask: Dict[int, bool]
    settings: TestSettings

    def __post_init__(self):
        self._cached_frequency: Dict[int, ndarray] = {}
        self._cached_impedance: Dict[int, ndarray] = {}

    def __repr__(self) -> str:
        return f"TestResult ({self.get_label()}, {hex(id(self))})"

    @classmethod
    def from_dict(Class, dictionary: dict) -> "TestResult":
        """
        Create an instance from a dictionary.
        """
        assert type(dictionary) is dict
        assert "version" in dictionary
        version: int = dictionary["version"]
        assert version <= VERSION, f"{version=} > {VERSION=}"
        parsers: Dict[int, Callable] = {
            1: _parse_result_v1,
        }
        assert version in parsers, f"{version=} not in {parsers.keys()=}"
        mask: Dict[str, bool] = dictionary["mask"]
        if len(mask) < len(dictionary["frequency"]):
            i: int
            for i in range(0, len(dictionary["frequency"])):
                if mask.get(str(i)) is not True:
                    mask[str(i)] = False
        if (
            "real_impedance" not in dictionary
            or "imaginary_impedance" not in dictionary
        ):
            Z: ndarray = pyimpspec.parse_cdc(dictionary["circuit"]).impedances(
                dictionary["frequency"]
            )
            dictionary["real_impedance"] = list(Z.real)
            dictionary["imaginary_impedance"] = list(Z.imag)
        return Class(**parsers[version](dictionary))

    def to_dict(self, session: bool) -> dict:
        """
        Return a dictionary that can be used to recreate an instance.
        """
        dictionary: dict = {
            "version": VERSION,
            "uuid": self.uuid,
            "timestamp": self.timestamp,
            "circuit": self.circuit.to_string(12),
            "num_RC": self.num_RC,
            "mu": self.mu,
            "pseudo_chisqr": self.pseudo_chisqr,
            "frequency": list(self.frequency),
            "real_residual": list(self.real_residual),
            "imaginary_residual": list(self.imaginary_residual),
            "mask": {k: True for k, v in self.mask.items() if v is True},
            "settings": self.settings.to_dict(),
        }
        if session:
            dictionary.update(
                {
                    "real_impedance": list(self.impedance.real),
                    "imaginary_impedance": list(self.impedance.imag),
                }
            )
        return dictionary

    def get_label(self) -> str:
        """
        Generate a label for the result.
        """
        circuit: str = f"R(RC){self.num_RC}"
        if self.settings.add_capacitance:
            circuit += "C"
        if self.settings.add_inductance:
            circuit += "L"
        timestamp: str = format_timestamp(self.timestamp)
        return f"{circuit} ({timestamp})"

    def get_frequency(self, num_per_decade: int = -1) -> ndarray:
        """
        Get an array of frequencies within the range of tested frequencies.

        Parameters
        ----------
        num_per_decade: int = -1
            If the value is greater than zero, then logarithmically distributed frequencies will be generated within the range of tested frequencies.
        """
        assert issubdtype(type(num_per_decade), integer), num_per_decade
        if num_per_decade > 0:
            if num_per_decade not in self._cached_frequency:
                self._cached_frequency.clear()
                self._cached_frequency[num_per_decade] = _interpolate(
                    self.frequency, num_per_decade
                )
            return self._cached_frequency[num_per_decade]
        return self.frequency

    def get_impedance(self, num_per_decade: int = -1) -> ndarray:
        """
        Get the complex impedances produced by the fitted circuit within the range of tested frequencies.

        Parameters
        ----------
        num_per_decade: int = -1
            If the value is greater than zero, then logarithmically distributed frequencies will be generated within the range of tested frequencies and used to calculate the impedance produced by the fitted circuit.
        """
        assert issubdtype(type(num_per_decade), integer), num_per_decade
        if num_per_decade > 0:
            if num_per_decade not in self._cached_impedance:
                self._cached_impedance.clear()
                self._cached_impedance[num_per_decade] = self.circuit.impedances(
                    self.get_frequency(num_per_decade)
                )
            return self._cached_impedance[num_per_decade]
        return self.impedance

    def get_nyquist_data(self, num_per_decade: int = -1) -> Tuple[ndarray, ndarray]:
        """
        Get the data required to plot the results as a Nyquist plot (-Z\" vs Z').

        Parameters
        ----------
        num_per_decade: int = -1
            If the value is greater than zero, then logarithmically distributed frequencies will be generated within the range of tested frequencies and used to calculate the impedance produced by the fitted circuit.
        """
        assert issubdtype(type(num_per_decade), integer), num_per_decade
        if num_per_decade > 0:
            Z: ndarray = self.get_impedance(num_per_decade)
            return (
                Z.real,
                -Z.imag,
            )
        return (
            self.impedance.real,
            -self.impedance.imag,
        )

    def get_bode_data(
        self, num_per_decade: int = -1
    ) -> Tuple[ndarray, ndarray, ndarray]:
        """
        Get the data required to plot the results as a Bode plot (|Z| and phi vs f).

        Parameters
        ----------
        num_per_decade: int = -1
            If the value is greater than zero, then logarithmically distributed frequencies will be generated within the range of tested frequencies and used to calculate the impedance produced by the fitted circuit.
        """
        assert issubdtype(type(num_per_decade), integer), num_per_decade
        if num_per_decade > 0:
            freq: ndarray = self.get_frequency(num_per_decade)
            Z: ndarray = self.get_impedance(num_per_decade)
            return (
                freq,
                abs(Z),
                -angle(Z, deg=True),
            )
        return (
            self.frequency,
            abs(self.impedance),
            -angle(self.impedance, deg=True),
        )

    def get_residual_data(self) -> Tuple[ndarray, ndarray, ndarray]:
        """
        Get the data required to plot the residuals (real and imaginary vs f).
        """
        return (
            self.frequency,
            self.real_residual * 100,
            self.imaginary_residual * 100,
        )

    def calculate_score(self, mu_criterion: float) -> float:
        """
        Calculate a score based on the provided mu-criterion and the statistics of the result.
        A result with a mu-value greater than or equal to the mu-criterion will get a score of -numpy.inf.

        Parameters
        ----------
        mu_criterion: float
            The mu-criterion to apply.
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
