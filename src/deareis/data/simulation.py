# Copyright 2022 DearEIS developers
# DearEIS is licensed under the GPLv3 or later (https://www.gnu.org/licenses/gpl-3.0.html).
# The licenses of DearEIS' dependencies and/or sources of portions of code are included in
# the LICENSES folder.

from pyimpspec import Circuit, Element, string_to_circuit
from dataclasses import dataclass
from typing import Callable, Dict, List, Tuple
from numpy import angle, log10 as log, ndarray
from pandas import DataFrame
from deareis.utility import format_timestamp
from pyimpspec.analysis.fitting import _interpolate


VERSION: int = 1


@dataclass(frozen=True)
class SimulationSettings:
    cdc: str
    min_frequency: float
    max_frequency: float
    num_freq_per_dec: int

    @staticmethod
    def _parse_v1(dictionary: dict) -> dict:
        assert type(dictionary) is dict
        return {
            "cdc": dictionary["cdc"],
            "min_frequency": dictionary["min_frequency"],
            "max_frequency": dictionary["max_frequency"],
            "num_freq_per_dec": dictionary["num_freq_per_dec"],
        }

    @classmethod
    def from_dict(Class, dictionary: dict) -> "SimulationSettings":
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
            "min_frequency": self.min_frequency,
            "max_frequency": self.max_frequency,
            "num_freq_per_dec": self.num_freq_per_dec,
        }


@dataclass(frozen=True)
class SimulationResult:
    uuid: str
    timestamp: float
    circuit: Circuit
    settings: SimulationSettings

    @staticmethod
    def _parse_v1(dictionary: dict) -> dict:
        assert type(dictionary) is dict
        return {
            "uuid": dictionary["uuid"],
            "timestamp": dictionary["timestamp"],
            "circuit": string_to_circuit(dictionary["circuit"]),
            "settings": SimulationSettings.from_dict(dictionary["settings"]),
        }

    @classmethod
    def from_dict(Class, dictionary: dict) -> "SimulationResult":
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
            "settings": self.settings.to_dict(),
        }

    def to_dataframe(self) -> DataFrame:
        element_labels: List[str] = []
        parameter_labels: List[str] = []
        values: List[float] = []
        element: Element
        for element in self.circuit.get_elements():
            i: int
            parameter_label: str
            for i, (parameter_label, value) in enumerate(
                element.get_parameters().items()
            ):
                element_labels.append(element.get_label())
                parameter_labels.append(parameter_label)
                values.append(value)
        return DataFrame.from_dict(
            {
                "Element": element_labels,
                "Parameter": parameter_labels,
                "Value": values,
            }
        )

    def get_label(self) -> str:
        cdc: str = self.settings.cdc
        while "{" in cdc:
            i: int = cdc.find("{")
            j: int = cdc.find("}")
            cdc = cdc.replace(cdc[i : j + 1], "")
        return f"{cdc} ({format_timestamp(self.timestamp)})"

    def get_frequency(self, num_per_decade: int = -1) -> ndarray:
        assert type(num_per_decade) is int
        return _interpolate(
            [self.settings.min_frequency, self.settings.max_frequency],
            self.settings.num_freq_per_dec if num_per_decade < 1 else num_per_decade,
        )

    def get_impedance(self, num_per_decade: int = -1) -> ndarray:
        assert type(num_per_decade) is int
        return self.circuit.impedances(self.get_frequency(num_per_decade))

    def get_nyquist_data(self, num_per_decade: int = -1) -> Tuple[ndarray, ndarray]:
        assert type(num_per_decade) is int
        Z: ndarray = self.circuit.impedances(self.get_frequency(num_per_decade))
        return (
            Z.real,
            -Z.imag,
        )

    def get_bode_data(
        self, num_per_decade: int = -1
    ) -> Tuple[ndarray, ndarray, ndarray]:
        assert type(num_per_decade) is int
        f: ndarray = self.get_frequency(num_per_decade)
        Z: ndarray = self.circuit.impedances(f)
        return (
            log(f),
            log(abs(Z)),
            -angle(Z, deg=True),
        )
