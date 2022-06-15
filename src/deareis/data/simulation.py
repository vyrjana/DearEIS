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
from typing import Callable, Dict, List, Tuple
from numpy import angle, log10 as log, ndarray
from pandas import DataFrame
from pyimpspec import Circuit, Element
import pyimpspec
from pyimpspec.analysis.fitting import _interpolate
from deareis.utility import format_timestamp


VERSION: int = 1


def _parse_settings_v1(dictionary: dict) -> dict:
    assert type(dictionary) is dict
    return {
        "cdc": dictionary["cdc"],
        "min_frequency": dictionary["min_frequency"],
        "max_frequency": dictionary["max_frequency"],
        "num_freq_per_dec": dictionary["num_freq_per_dec"],
    }


@dataclass(frozen=True)
class SimulationSettings:
    """
A class to store the settings used to perform a simulation.

Parameters
----------
cdc: str
    The circuit description code (CDC) for the circuit to simulate.

min_frequency: float
    The minimum frequency (in hertz) to simulate.

max_frequency: float
    The maximum frequency (in hertz) to simulate.

num_freq_per_dec: int
    The number of frequencies per decade to simulate.
    The frequencies are distributed logarithmically within the inclusive boundaries defined by `min_frequency` and `max_frequency`.
    """
    cdc: str
    min_frequency: float
    max_frequency: float
    num_freq_per_dec: int

    def __repr__(self) -> str:
        return f"SimulationSettings ({hex(id(self))})"

    @classmethod
    def from_dict(Class, dictionary: dict) -> "SimulationSettings":
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
            "min_frequency": self.min_frequency,
            "max_frequency": self.max_frequency,
            "num_freq_per_dec": self.num_freq_per_dec,
        }


def _parse_result_v1(dictionary: dict) -> dict:
    assert type(dictionary) is dict
    return {
        "uuid": dictionary["uuid"],
        "timestamp": dictionary["timestamp"],
        "circuit": pyimpspec.string_to_circuit(dictionary["circuit"]),
        "settings": SimulationSettings.from_dict(dictionary["settings"]),
    }


@dataclass(frozen=True)
class SimulationResult:
    """
A class containing the result of a simulation.

Parameters
----------
uuid: str
    The universally unique identifier assigned to this result.

timestamp: float
    The Unix time (in seconds) for when the simulation was performed.

circuit: Circuit
    The simulated circuit.

settings: SimulationSettings
    The settings that were used to perform the simulation.
    """
    uuid: str
    timestamp: float
    circuit: Circuit
    settings: SimulationSettings

    def __repr__(self) -> str:
        return f"SimulationResult ({self.get_label()}, {hex(id(self))})"

    @classmethod
    def from_dict(Class, dictionary: dict) -> "SimulationResult":
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
        return Class(**parsers[version](dictionary))

    def to_dict(self) -> dict:
        """
Return a dictionary that can be used to recreate an instance.
        """
        return {
            "version": VERSION,
            "uuid": self.uuid,
            "timestamp": self.timestamp,
            "circuit": self.circuit.to_string(12),
            "settings": self.settings.to_dict(),
        }

    def to_dataframe(self) -> DataFrame:
        """
Get a `pandas.DataFrame` instance containing a table of element parameters.
        """
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
        """
Generate a label for the result.
        """
        cdc: str = self.settings.cdc
        while "{" in cdc:
            i: int = cdc.find("{")
            j: int = cdc.find("}")
            cdc = cdc.replace(cdc[i : j + 1], "")
        return f"{cdc} ({format_timestamp(self.timestamp)})"

    def get_frequency(self, num_per_decade: int = -1) -> ndarray:
        """
Get an array of frequencies within the range of simulated frequencies.

Parameters
----------
num_per_decade: int = -1
    If the value is greater than zero, then logarithmically distributed frequencies will be generated within the range of frequencies defined by the minimum and maximum frequencies used to generate the original simulation result.
        """
        assert type(num_per_decade) is int
        return _interpolate(
            [self.settings.min_frequency, self.settings.max_frequency],
            self.settings.num_freq_per_dec if num_per_decade < 1 else num_per_decade,
        )

    def get_impedance(self, num_per_decade: int = -1) -> ndarray:
        """
Get the complex impedances produced by the simulated circuit within the range of frequencies used to generate the original simulation result.

Parameters
----------
num_per_decade: int = -1
    If the value is greater than zero, then logarithmically distributed frequencies will be generated within the range of simulated frequencies and used to calculate the impedance produced by the simulated circuit.
        """
        assert type(num_per_decade) is int
        return self.circuit.impedances(self.get_frequency(num_per_decade))

    def get_nyquist_data(self, num_per_decade: int = -1) -> Tuple[ndarray, ndarray]:
        """
Get the data required to plot the results as a Nyquist plot (-Z\" vs Z').

Parameters
----------
num_per_decade: int = -1
    If the value is greater than zero, then logarithmically distributed frequencies will be generated within the range of frequencies and used to calculate the impedance produced by the simulated circuit.
        """
        assert type(num_per_decade) is int
        Z: ndarray = self.circuit.impedances(self.get_frequency(num_per_decade))
        return (
            Z.real,
            -Z.imag,
        )

    def get_bode_data(
        self, num_per_decade: int = -1
    ) -> Tuple[ndarray, ndarray, ndarray]:
        """
Get the data required to plot the results as a Bode plot (log |Z| and phi vs log f).

Parameters
----------
num_per_decade: int = -1
    If the value is greater than zero, then logarithmically distributed frequencies will be generated within the range of frequencies and used to calculate the impedance produced by the fitted circuit.
        """
        assert type(num_per_decade) is int
        f: ndarray = self.get_frequency(num_per_decade)
        Z: ndarray = self.circuit.impedances(f)
        return (
            log(f),
            log(abs(Z)),
            -angle(Z, deg=True),
        )
