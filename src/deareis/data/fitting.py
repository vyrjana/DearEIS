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

from collections import OrderedDict
from dataclasses import dataclass
from typing import (
    Callable,
    Dict,
    List,
    Tuple,
    Union,
)
from numpy import (
    angle,
    array,
    integer,
    issubdtype,
    ndarray,
)
from pandas import DataFrame
import pyimpspec
from pyimpspec import (
    Circuit,
    Element,
    FittedParameter,
)
from pyimpspec.analysis.fitting import _interpolate
from deareis.enums import (
    CNLSMethod,
    Weight,
)
from deareis.utility import format_timestamp


VERSION: int = 1


def _parse_settings_v1(dictionary: dict) -> dict:
    assert type(dictionary) is dict
    return {
        "cdc": dictionary["cdc"],
        "method": CNLSMethod(dictionary["method"]),
        "weight": Weight(dictionary["weight"]),
        "max_nfev": dictionary["max_nfev"],
    }


@dataclass(frozen=True)
class FitSettings:
    """
    A class to store the settings used to perform a circuit fit.

    Parameters
    ----------
    cdc: str
        The circuit description code (CDC) for the circuit to fit.

    method: CNLSMethod
        The iterative method to use when performing the fit.

    weight: Weight
        The weight function to use when performing the fit.

    max_nfev: int
        The maximum number of function evaluations to use when performing the fit.
    """

    cdc: str
    method: CNLSMethod
    weight: Weight
    max_nfev: int

    def __repr__(self) -> str:
        return f"FitSettings ({hex(id(self))})"

    @classmethod
    def from_dict(Class, dictionary: dict) -> "FitSettings":
        """
        Create an instance from a dictionary.
        """
        assert type(dictionary) is dict
        assert "version" in dictionary
        version: int = dictionary["version"]
        assert version <= VERSION, f"{version=} > {VERSION=}"
        parsers: Dict[int, Callable] = {
            1: _parse_settings_v1,
        }
        assert version in parsers, f"{version=} not in {parsers.keys()=}"
        return Class(**parsers[version](dictionary))

    def to_dict(self) -> dict:
        """
        Return a dictionary that can be used to recreate an instance.
        """
        return {
            "version": VERSION,
            "cdc": self.cdc,
            "method": self.method,
            "weight": self.weight,
            "max_nfev": self.max_nfev,
        }


def _parse_result_v1(dictionary: dict) -> dict:
    assert type(dictionary) is dict
    return {
        "uuid": dictionary["uuid"],
        "timestamp": dictionary["timestamp"],
        "circuit": pyimpspec.parse_cdc(dictionary["circuit"]),
        "parameters": {
            element_label: {
                parameter_label: FittedParameter.from_dict(param)
                for parameter_label, param in parameters.items()
            }
            for element_label, parameters in dictionary["parameters"].items()
        },
        "frequency": array(dictionary["frequency"]),
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
        "mask": {int(k): v for k, v in dictionary.get("mask", {}).items()},
        "real_residual": array(dictionary["real_residual"]),
        "imaginary_residual": array(dictionary["imaginary_residual"]),
        "chisqr": dictionary["chisqr"],
        "red_chisqr": dictionary["red_chisqr"],
        "aic": dictionary["aic"],
        "bic": dictionary["bic"],
        "ndata": dictionary["ndata"],
        "nfree": dictionary["nfree"],
        "nfev": dictionary["nfev"],
        "method": dictionary["method"],
        "weight": dictionary["weight"],
        "settings": FitSettings.from_dict(dictionary["settings"]),
    }


@dataclass
class FitResult:
    """
    A class containing the result of a circuit fit.

    Parameters
    ----------
    uuid: str
        The universally unique identifier assigned to this result.

    timestamp: float
        The Unix time (in seconds) for when the test was performed.

    circuit: Circuit
        The final, fitted circuit.

    parameters: Dict[str, Dict[str, FittedParameter]]
        The mapping to the mappings of the final, fitted values of the element parameters.

    frequency: ndarray
        The frequencies used to perform the fit.

    impedance: ndarray
        The complex impedances of the fitted circuit at each of the frequencies.

    real_residual: ndarray
        The residuals of the real part of the complex impedances.

    imaginary_residual: ndarray
        The residuals of the imaginary part of the complex impedances.

    mask: Dict[int, bool]
        The mask that was applied to the DataSet that the circuit was fitted to.

    chisqr: float
        The chi-squared value calculated for the result.

    red_chisqr: float
        The reduced chi-squared value calculated for the result.

    aic: float
        The calculated Akaike information criterion.

    bic: float
        The calculated Bayesian information criterion.

    ndata: int
        The number of data points.

    nfree: int
        The degrees of freedom.

    nfev: int
        The number of function evaluations.

    method: CNLSMethod
        The iterative method that produced the result.

    weight: Weight
        The weight function that produced the result.

    settings: FitSettings
        The settings that were used to perform the fit.
    """

    uuid: str
    timestamp: float
    circuit: Circuit
    parameters: Dict[str, Dict[str, FittedParameter]]
    frequency: ndarray
    impedance: ndarray
    real_residual: ndarray
    imaginary_residual: ndarray
    mask: Dict[int, bool]
    chisqr: float
    red_chisqr: float
    aic: float
    bic: float
    ndata: int
    nfree: int
    nfev: int
    method: CNLSMethod
    weight: Weight
    settings: FitSettings

    def __post_init__(self):
        self._cached_frequency: Dict[int, ndarray] = {}
        self._cached_impedance: Dict[int, ndarray] = {}

    def __repr__(self) -> str:
        return f"FitResult ({self.get_label()}, {hex(id(self))})"

    # TODO: Refactor
    @classmethod
    def from_dict(Class, dictionary: dict) -> "FitResult":
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
        dictionary = parsers[version](dictionary)
        return Class(**dictionary)

    def to_dict(self, session: bool) -> dict:
        """
        Return a dictionary that can be used to recreate an instance.
        """
        assert type(session) is bool, session
        dictionary: dict = {
            "version": VERSION,
            "uuid": self.uuid,
            "timestamp": self.timestamp,
            "circuit": self.circuit.to_string(12),
            "parameters": {
                element_label: {
                    parameter_label: param.to_dict()
                    for parameter_label, param in parameters.items()
                }
                for element_label, parameters in self.parameters.items()
            },
            "frequency": list(self.frequency),
            "mask": {k: True for k, v in self.mask.items() if v is True},
            "real_residual": list(self.real_residual),
            "imaginary_residual": list(self.imaginary_residual),
            "chisqr": self.chisqr,
            "red_chisqr": self.red_chisqr,
            "aic": self.aic,
            "bic": self.bic,
            "ndata": self.ndata,
            "nfree": self.nfree,
            "nfev": self.nfev,
            "method": self.method,
            "weight": self.weight,
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

    def to_dataframe(self) -> DataFrame:
        """
        Get a `pandas.DataFrame` instance containing a table of fitted element parameters.
        """
        element_labels: List[str] = []
        parameter_labels: List[str] = []
        fitted_values: List[float] = []
        stderr_values: List[Union[float, str]] = []
        fixed: List[str] = []
        element_label: str
        parameters: Union[
            Dict[str, FittedParameter], Dict[int, OrderedDict[str, float]]
        ]
        element: Element
        for element in sorted(
            self.circuit.get_elements(flattened=True),
            key=lambda _: _.get_identifier(),
        ):
            element_label = element.get_label()
            parameters = self.parameters[element_label]
            parameter_label: str
            param: FittedParameter
            for parameter_label in sorted(parameters.keys()):
                param = parameters[parameter_label]
                element_labels.append(element_label)
                parameter_labels.append(parameter_label)
                fitted_values.append(param.value)
                stderr_values.append(
                    param.stderr / param.value * 100
                    if param.stderr is not None
                    else "-"
                )
                fixed.append("Yes" if param.fixed else "No")
        return DataFrame.from_dict(
            {
                "Element": element_labels,
                "Parameter": parameter_labels,
                "Value": fitted_values,
                "Std. err. (%)": stderr_values,
                "Fixed": fixed,
            }
        )

    def get_label(self) -> str:
        """
        Generate a label for the result.
        """
        cdc: str = self.settings.cdc
        while "{" in cdc:
            i: int = cdc.find("{")
            j: int = cdc.find("}")
            cdc = cdc.replace(cdc[i : j + 1], "")
        if cdc.startswith("[") and cdc.endswith("]"):
            cdc = cdc[1:-1]
        timestamp: str = format_timestamp(self.timestamp)
        return f"{cdc} ({timestamp})"

    def get_frequency(self, num_per_decade: int = -1) -> ndarray:
        """
        Get an array of frequencies within the range of frequencies in the data set.

        Parameters
        ----------
        num_per_decade: int = -1
            If the value is greater than zero, then logarithmically distributed frequencies will be generated within the range of fitted frequencies.
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
        Get the complex impedances produced by the fitted circuit within the range of frequencies in the data set.

        Parameters
        ----------
        num_per_decade: int = -1
            If the value is greater than zero, then logarithmically distributed frequencies will be generated within the range of fitted frequencies and used to calculate the impedance produced by the fitted circuit.
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
            If the value is greater than zero, then logarithmically distributed frequencies will be generated within the range of frequencies in the data set and used to calculate the impedance produced by the fitted circuit.
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
            If the value is greater than zero, then logarithmically distributed frequencies will be generated within the range of frequencies in the data set and used to calculate the impedance produced by the fitted circuit.
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
