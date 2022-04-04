# Copyright 2022 DearEIS developers
# DearEIS is licensed under the GPLv3 or later (https://www.gnu.org/licenses/gpl-3.0.html).
# The licenses of DearEIS' dependencies and/or sources of portions of code are included in
# the LICENSES folder.

from enum import IntEnum, auto as auto_enum
from pyimpspec import DataSet, Circuit, string_to_circuit
from dataclasses import dataclass
from typing import Callable, Dict, Tuple, Optional
from numpy import angle, array, log10 as log, ndarray
from pyimpspec.analysis.fitting import _interpolate
from deareis.data.shared import (
    Method,
    label_to_method,
    method_to_label,
    method_to_value,
)
from deareis.utility import format_timestamp


class Test(IntEnum):
    CNLS = auto_enum()
    COMPLEX = auto_enum()
    IMAGINARY = auto_enum()
    REAL = auto_enum()


label_to_test: Dict[str, Test] = {
    "CNLS": Test.CNLS,
    "Complex": Test.COMPLEX,
    "Imaginary": Test.IMAGINARY,
    "Real": Test.REAL,
}
test_to_label: Dict[Test, str] = {v: k for k, v in label_to_test.items()}
test_to_value: Dict[Test, str] = {
    Test.CNLS: "cnls",
    Test.COMPLEX: "complex",
    Test.IMAGINARY: "imaginary",
    Test.REAL: "real",
}


class Mode(IntEnum):
    AUTO = auto_enum()
    EXPLORATORY = auto_enum()
    MANUAL = auto_enum()


label_to_mode: Dict[str, Mode] = {
    "Auto": Mode.AUTO,
    "Exploratory": Mode.EXPLORATORY,
    "Manual": Mode.MANUAL,
}
mode_to_label: Dict[Mode, str] = {v: k for k, v in label_to_mode.items()}


VERSION: int = 1


@dataclass(frozen=True)
class TestSettings:
    test: Test
    mode: Mode
    num_RC: int
    mu_criterion: float
    add_capacitance: bool
    add_inductance: bool
    method: Method
    max_nfev: int

    @staticmethod
    def _parse_v1(dictionary: dict) -> dict:
        assert type(dictionary) is dict
        return {
            "test": Test(dictionary["test"]),
            "mode": Mode(dictionary["mode"]),
            "num_RC": dictionary["num_RC"],
            "mu_criterion": dictionary["mu_criterion"],
            "add_capacitance": dictionary["add_capacitance"],
            "add_inductance": dictionary["add_inductance"],
            "method": Method(dictionary["method"]),
            "max_nfev": dictionary["max_nfev"],
        }

    @classmethod
    def from_dict(Class, dictionary: dict) -> "TestSettings":
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
            "test": self.test,
            "mode": self.mode,
            "num_RC": self.num_RC,
            "mu_criterion": self.mu_criterion,
            "add_capacitance": self.add_capacitance,
            "add_inductance": self.add_inductance,
            "method": self.method,
            "max_nfev": self.max_nfev,
        }


@dataclass(frozen=True)
class TestResult:
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

    @staticmethod
    def _parse_v1(dictionary: dict) -> dict:
        assert type(dictionary) is dict
        return {
            "uuid": dictionary["uuid"],
            "timestamp": dictionary["timestamp"],
            "circuit": string_to_circuit(dictionary["circuit"]),
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

    @classmethod
    def from_dict(Class, dictionary: dict) -> "TestResult":
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
            "num_RC": self.num_RC,
            "mu": self.mu,
            "pseudo_chisqr": self.pseudo_chisqr,
            "frequency": list(self.frequency),
            "real_impedance": list(self.impedance.real),
            "imaginary_impedance": list(self.impedance.imag),
            "real_residual": list(self.real_residual),
            "imaginary_residual": list(self.imaginary_residual),
            "mask": self.mask,
            "settings": self.settings.to_dict(),
        }

    def get_label(self) -> str:
        return format_timestamp(self.timestamp)

    def get_info(self, data: Optional[DataSet]) -> str:
        assert type(data) is DataSet or data is None
        if data is not None:
            i: int
            state: bool
            for i, state in data.get_mask().items():
                if state != self.mask[i]:
                    return "DATA SET MASK HAS CHANGED AFTER THE TEST!"
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
