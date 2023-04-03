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
    List,
    Optional,
    Tuple,
    Union,
)
from numpy import (
    angle,
    array,
    integer,
    isnan,
    issubdtype,
    log10 as log,
    nan,
)
from pandas import DataFrame
import pyimpspec
from pyimpspec.analysis.utility import _calculate_pseudo_chisqr
from pyimpspec import (
    Circuit,
    ComplexImpedances,
    ComplexResiduals,
    Element,
    Frequencies,
    Impedances,
    Phases,
    Residuals,
)
from pyimpspec.analysis.utility import _interpolate
from deareis.enums import (
    CNLSMethod,
    Weight,
    cnls_method_to_label,
    weight_to_label,
)
from deareis.utility import (
    format_timestamp,
    rename_dict_entry,
)
from deareis.data import DataSet


VERSION: int = 2


def _parse_fitted_parameter_v2(dictionary: dict) -> dict:
    return dictionary


def _parse_fitted_parameter_v1(dictionary: dict) -> dict:
    stderr: Optional[float] = dictionary.get("stderr")
    dictionary["stderr"] = stderr if stderr is not None else nan
    dictionary["unit"] = ""
    return dictionary


class FittedParameter(pyimpspec.FittedParameter):
    @classmethod
    def from_dict(Class, dictionary: dict) -> "FittedParameter":
        """
        Create a FittedParameter object from a dictionary.

        Parameters
        ----------
        dictionary: dict
            The dictionary to turn into a FittedParameter object.

        Returns
        -------
        FittedParameter
        """
        assert isinstance(dictionary, dict), dictionary
        assert "version" in dictionary
        version: int = dictionary["version"]
        del dictionary["version"]
        assert version <= VERSION, f"{version=} > {VERSION=}"
        parsers: Dict[int, Callable] = {
            1: _parse_fitted_parameter_v1,
            2: _parse_fitted_parameter_v2,
        }
        assert version in parsers, f"{version=} not in {parsers.keys()=}"
        v: int
        p: Callable
        for v, p in parsers.items():
            if v < version:
                continue
            dictionary = p(dictionary)
        assert "value" in dictionary
        assert "stderr" in dictionary
        assert "fixed" in dictionary
        assert "unit" in dictionary
        return Class(**dictionary)

    def to_dict(self) -> dict:
        """
        Generate a dictionary that can be used to recreate this object.

        Returns
        -------
        dict
        """
        return {
            "version": VERSION,
            "value": self.value,
            "stderr": self.stderr,
            "fixed": self.fixed,
            "unit": self.unit,
        }


def _parse_settings_v2(dictionary: dict) -> dict:
    return dictionary


def _parse_settings_v1(dictionary: dict) -> dict:
    return dictionary


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

        Parameters
        ----------
        dictionary: dict
            The dictionary to turn into a FitSettings object.

        Returns
        -------
        FitSettings
        """
        assert type(dictionary) is dict
        assert "version" in dictionary
        version: int = dictionary["version"]
        del dictionary["version"]
        assert version <= VERSION, f"{version=} > {VERSION=}"
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
        assert "cdc" in dictionary
        assert "method" in dictionary
        assert "weight" in dictionary
        assert "max_nfev" in dictionary
        dictionary["method"] = CNLSMethod(dictionary["method"])
        dictionary["weight"] = Weight(dictionary["weight"])
        return Class(**dictionary)

    def to_dict(self) -> dict:
        """
        Return a dictionary that can be used to recreate an instance.

        Returns
        -------
        dict
        """
        return {
            "version": VERSION,
            "cdc": self.cdc,
            "method": self.method,
            "weight": self.weight,
            "max_nfev": self.max_nfev,
        }


def _parse_result_v2(dictionary: dict) -> dict:
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
    old_parameters: dict = dictionary["parameters"]
    new_parameters: dict = {}
    counts: Dict[str, int] = {}
    key: str
    for key in sorted(old_parameters.keys()):
        name: str = key.split("_", 1)[0]
        if name not in counts:
            counts[name] = 0
        counts[name] += 1
        new_parameters[f"{name}_{counts[name]}"] = old_parameters[key]
    dictionary["parameters"] = new_parameters
    return dictionary


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

    frequencies: Frequencies
        The frequencies used to perform the fit.

    impedances: ComplexImpedances
        The complex impedances of the fitted circuit at each of the frequencies.

    residuals: ComplexResiduals
        The residuals of the real and imaginary parts of the fit.

    mask: Dict[int, bool]
        The mask that was applied to the DataSet that the circuit was fitted to.

    pseudo_chisqr: float
        The calculated |pseudo chi-squared| (eq. 14 in Boukamp, 1995).

    chisqr: float
        The |chi-squared| calculated for the result.

    red_chisqr: float
        The reduced |chi-squared| calculated for the result.

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
    frequencies: Frequencies
    impedances: ComplexImpedances
    residuals: ComplexResiduals
    mask: Dict[int, bool]
    pseudo_chisqr: float
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
        self._cached_frequencies: Dict[int, Frequencies] = {}
        self._cached_impedances: Dict[int, ComplexImpedances] = {}

    def __hash__(self) -> int:
        return int(self.uuid, 16)

    def __repr__(self) -> str:
        return f"FitResult ({self.get_label()}, {hex(id(self))})"

    @classmethod
    def from_dict(
        Class,
        dictionary: dict,
        data: Optional[DataSet] = None,
    ) -> "FitResult":
        """
        Create an instance from a dictionary.

        Parameters
        ----------
        dictionary: dict
            The dictionary to turn into a FitResult object.

        data: Optional[DataSet], optional
            The DataSet object that this result is for.

        Returns
        -------
        FitResult
        """
        assert isinstance(dictionary, dict), dictionary
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
        assert "parameters" in dictionary
        assert "frequencies" in dictionary
        assert "real_residuals" in dictionary
        assert "imaginary_residuals" in dictionary
        assert "mask" in dictionary
        assert "pseudo_chisqr" in dictionary
        assert "chisqr" in dictionary
        assert "red_chisqr" in dictionary
        assert "aic" in dictionary
        assert "bic" in dictionary
        assert "ndata" in dictionary
        assert "nfree" in dictionary
        assert "nfev" in dictionary
        assert "method" in dictionary
        assert "weight" in dictionary
        assert "settings" in dictionary
        dictionary["circuit"] = pyimpspec.parse_cdc(dictionary["circuit"])
        dictionary["parameters"] = {
            element_label: {
                parameter_label: FittedParameter.from_dict(param)
                for parameter_label, param in parameters.items()
            }
            for element_label, parameters in dictionary["parameters"].items()
        }
        dictionary["frequencies"] = array(dictionary["frequencies"])
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
        mask: Dict[str, bool] = dictionary["mask"]
        dictionary["mask"] = {
            i: mask.get(str(i), False) for i in range(0, len(dictionary["frequencies"]))
        }
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
        dictionary["settings"] = FitSettings.from_dict(dictionary["settings"])
        if isnan(dictionary["pseudo_chisqr"]):
            dictionary["pseudo_chisqr"] = _calculate_pseudo_chisqr(
                Z_exp=data.get_impedances(),
                Z_fit=dictionary["impedances"],
            )
        return Class(**dictionary)

    def to_dict(self, session: bool) -> dict:
        """
        Return a dictionary that can be used to recreate an instance.

        Parameters
        ----------
        session: bool
            If False, then a minimal dictionary is generated to reduce file size.

        Returns
        -------
        dict
        """
        assert type(session) is bool, session
        dictionary: dict = {
            "version": VERSION,
            "uuid": self.uuid,
            "timestamp": self.timestamp,
            "circuit": self.circuit.serialize(),
            "parameters": {
                element_label: {
                    parameter_label: param.to_dict()
                    for parameter_label, param in parameters.items()
                }
                for element_label, parameters in self.parameters.items()
            },
            "frequencies": list(self.frequencies),
            "mask": {k: True for k, v in self.mask.items() if v is True},
            "real_residuals": list(self.residuals.real),
            "imaginary_residuals": list(self.residuals.imag),
            "pseudo_chisqr": self.pseudo_chisqr,
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
                    "real_impedances": list(self.impedances.real),
                    "imaginary_impedances": list(self.impedances.imag),
                }
            )
        return dictionary

    def to_statistics_dataframe(self) -> DataFrame:
        """
        Get the statistics related to the fit as a pandas.DataFrame object.

        Returns
        -------
        DataFrame
        """
        statistics: Dict[str, Union[int, float, str]] = {
            "Log pseudo chi-squared": log(self.pseudo_chisqr),
            "Log chi-squared": log(self.chisqr),
            "Log chi-squared (reduced)": log(self.red_chisqr),
            "Akaike info. criterion": self.aic,
            "Bayesian info. criterion": self.bic,
            "Degrees of freedom": self.nfree,
            "Number of data points": self.ndata,
            "Number of function evaluations": self.nfev,
            "Method": cnls_method_to_label[self.method],
            "Weight": weight_to_label[self.weight],
        }
        return DataFrame.from_dict(
            {
                "Label": list(statistics.keys()),
                "Value": list(statistics.values()),
            }
        )

    def to_parameters_dataframe(self, running: bool = False) -> DataFrame:
        """
        Get a `pandas.DataFrame` instance containing a table of fitted element parameters.

        Parameters
        ----------
        running: bool, optional
            Whether or not to use running counts as the lower indices of elements.

        Returns
        -------
        pandas.DataFrame
        """
        assert isinstance(running, bool), running
        element_labels: List[str] = []
        parameter_labels: List[str] = []
        fitted_values: List[float] = []
        stderr_values: List[Union[float, str]] = []
        fixed: List[str] = []
        units: List[str] = []
        internal_identifiers: Dict[
            Element, int
        ] = self.circuit.generate_element_identifiers(running=True)
        external_identifiers: Dict[
            Element, int
        ] = self.circuit.generate_element_identifiers(running=False)
        element_label: str
        parameters: Union[Dict[str, FittedParameter], Dict[int, Dict[str, float]]]
        element: Element
        ident: int
        for (element, ident) in sorted(
            internal_identifiers.items(),
            key=lambda _: _[1],
        ):
            element_label = self.circuit.get_element_name(
                element,
                identifiers=external_identifiers,
            )
            parameters = self.parameters[element_label]
            parameter_label: str
            param: FittedParameter
            for parameter_label in sorted(parameters.keys()):
                param = parameters[parameter_label]
                element_labels.append(
                    self.circuit.get_element_name(
                        element,
                        identifiers=external_identifiers
                        if running is False
                        else internal_identifiers,
                    )
                )
                parameter_labels.append(parameter_label)
                fitted_values.append(param.value)
                stderr_values.append(
                    param.stderr / param.value * 100
                    if param.stderr is not None
                    else "-"
                )
                fixed.append("Yes" if param.fixed else "No")
                units.append(param.unit)
        return DataFrame.from_dict(
            {
                "Element": element_labels,
                "Parameter": parameter_labels,
                "Value": fitted_values,
                "Std. err. (%)": stderr_values,
                "Unit": units,
                "Fixed": fixed,
            }
        )

    def get_label(self) -> str:
        """
        Generate a label for the result.

        Returns
        -------
        str
        """
        cdc: str = self.circuit.to_string()
        if cdc.startswith("[") and cdc.endswith("]"):
            cdc = cdc[1:-1]
        timestamp: str = format_timestamp(self.timestamp)
        return f"{cdc} ({timestamp})"

    def get_frequencies(self, num_per_decade: int = -1) -> Frequencies:
        """
        Get an array of frequencies within the range of frequencies in the data set.

        Parameters
        ----------
        num_per_decade: int, optional
            If the value is greater than zero, then logarithmically distributed frequencies will be generated within the range of fitted frequencies.

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
        Get the complex impedances produced by the fitted circuit within the range of frequencies in the data set.

        Parameters
        ----------
        num_per_decade: int, optional
            If the value is greater than zero, then logarithmically distributed frequencies will be generated within the range of fitted frequencies and used to calculate the impedance produced by the fitted circuit.

        Returns
        -------
        ComplexImpedances
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
            If the value is greater than zero, then logarithmically distributed frequencies will be generated within the range of frequencies in the data set and used to calculate the impedance produced by the fitted circuit.

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
        self, num_per_decade: int = -1
    ) -> Tuple[Frequencies, Impedances, Phases]:
        """
        Get the data required to plot the results as a Bode plot (Mod(Z) and -Phase(Z) vs f).

        Parameters
        ----------
        num_per_decade: int, optional
            If the value is greater than zero, then logarithmically distributed frequencies will be generated within the range of frequencies in the data set and used to calculate the impedance produced by the fitted circuit.

        Returns
        -------
        Tuple[Frequencies, Impedancesy, Phases]
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
