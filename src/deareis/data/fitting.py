# Copyright 2022 DearEIS developers
# DearEIS is licensed under the GPLv3 or later (https://www.gnu.org/licenses/gpl-3.0.html).
# The licenses of DearEIS' dependencies and/or sources of portions of code are included in
# the LICENSES folder.

from collections import OrderedDict
from dataclasses import dataclass
from pyimpspec import DataSet, Circuit, string_to_circuit, FittedParameter
from pyimpspec.analysis.fitting import _interpolate
from pandas import DataFrame
from numpy import angle, array, log10 as log, ndarray
from typing import Callable, Dict, List, Optional, Tuple, Union
from deareis.data.shared import (
    Weight,
    label_to_weight,
    weight_to_label,
    weight_to_value,
    Method,
    label_to_method,
    method_to_label,
    method_to_value,
    value_to_method,
    value_to_weight,
)
from deareis.utility import format_timestamp


VERSION: int = 1


@dataclass(frozen=True)
class FitSettings:
    cdc: str
    method: Method
    weight: Weight
    max_nfev: int

    @staticmethod
    def _parse_v1(dictionary: dict) -> dict:
        assert type(dictionary) is dict
        return {
            "cdc": dictionary["cdc"],
            "method": Method(dictionary["method"]),
            "weight": Weight(dictionary["weight"]),
            "max_nfev": dictionary["max_nfev"],
        }

    @classmethod
    def from_dict(Class, dictionary: dict) -> "FitSettings":
        assert type(dictionary) is dict
        assert "version" in dictionary
        version: int = dictionary["version"]
        assert version <= VERSION, f"{version=} > {VERSION=}"
        parsers: Dict[int, Callable] = {
            1: Class._parse_v1,
        }
        assert version in parsers, f"{version=} not in {parsers.keys()=}"
        return Class(**parsers[version](dictionary))

    def to_dict(self) -> dict:
        return {
            "version": VERSION,
            "cdc": self.cdc,
            "method": self.method,
            "weight": self.weight,
            "max_nfev": self.max_nfev,
        }


@dataclass(frozen=True)
class FitResult:
    uuid: str
    timestamp: float
    circuit: Circuit
    parameters: Dict[str, Dict[str, FittedParameter]]
    frequency: ndarray
    impedance: ndarray
    mask: Dict[int, bool]
    real_residual: ndarray
    imaginary_residual: ndarray
    chisqr: float
    red_chisqr: float
    aic: float
    bic: float
    ndata: int
    nfree: int
    nfev: int
    method: str
    weight: str
    settings: FitSettings

    @staticmethod
    def _parse_v1(dictionary: dict) -> dict:
        assert type(dictionary) is dict
        return {
            "uuid": dictionary["uuid"],
            "timestamp": dictionary["timestamp"],
            "circuit": string_to_circuit(dictionary["circuit"]),
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

    @classmethod
    def from_dict(Class, dictionary: dict) -> "FitResult":
        assert type(dictionary) is dict
        assert "version" in dictionary
        version: int = dictionary["version"]
        assert version <= VERSION, f"{version=} > {VERSION=}"
        parsers: Dict[int, Callable] = {
            1: Class._parse_v1,
        }
        assert version in parsers, f"{version=} not in {parsers.keys()=}"
        return Class(**parsers[version](dictionary))

    def to_dict(self) -> dict:
        return {
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
            "real_impedance": list(self.impedance.real),
            "imaginary_impedance": list(self.impedance.imag),
            "mask": self.mask,
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

    def to_dataframe(self) -> DataFrame:
        element_labels: List[str] = []
        parameter_labels: List[str] = []
        fitted_values: List[float] = []
        stderr_values: List[Union[float, str]] = []
        fixed: List[str] = []
        element_label: str
        parameters: Union[
            Dict[str, FittedParameter], Dict[int, OrderedDict[str, float]]
        ]
        for element_label, parameters in self.parameters.items():
            parameter_label: str
            parameter: FittedParameter
            for parameter_label, parameter in parameters.items():
                element_labels.append(element_label)
                parameter_labels.append(parameter_label)
                fitted_values.append(parameter.value)
                stderr_values.append(
                    parameter.stderr / parameter.value * 100
                    if parameter.stderr is not None
                    else "-"
                )
                fixed.append("Yes" if parameter.fixed else "No")
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
        cdc: str = self.settings.cdc
        while "{" in cdc:
            i: int = cdc.find("{")
            j: int = cdc.find("}")
            cdc = cdc.replace(cdc[i : j + 1], "")
        return f"{cdc} ({format_timestamp(self.timestamp)})"

    def get_info(self, data: Optional[DataSet]) -> str:
        assert type(data) is DataSet or data is None
        if data is not None:
            i: int
            state: bool
            for i, state in data.get_mask().items():
                if state != self.mask[i]:
                    return "DATA SET MASK HAS CHANGED AFTER THE FIT!"
        return ""

    def get_frequency(self, num_per_decade: int = -1) -> ndarray:
        assert type(num_per_decade) is int
        if num_per_decade > 0:
            return _interpolate(self.frequency, num_per_decade)
        return self.frequency

    def get_impedance(self, num_per_decade: int = -1) -> ndarray:
        assert type(num_per_decade) is int
        if num_per_decade > 0:
            return self.circuit.impedances(self.get_frequency(num_per_decade))
        return self.impedance

    def get_nyquist_data(self, num_per_decade: int = -1) -> Tuple[ndarray, ndarray]:
        assert type(num_per_decade) is int
        if num_per_decade > 0:
            freq: ndarray = self.get_frequency(num_per_decade)
            Z: ndarray = self.circuit.impedances(freq)
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
        assert type(num_per_decade) is int
        if num_per_decade > 0:
            freq: ndarray = self.get_frequency(num_per_decade)
            Z: ndarray = self.circuit.impedances(freq)
            return (
                log(freq),
                log(abs(Z)),
                -angle(Z, deg=True),
            )
        return (
            log(self.frequency),
            log(abs(self.impedance)),
            -angle(self.impedance, deg=True),
        )

    def get_residual_data(self) -> Tuple[ndarray, ndarray, ndarray]:
        return (
            log(self.frequency),
            self.real_residual * 100,
            self.imaginary_residual * 100,
        )
