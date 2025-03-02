# DearEIS is licensed under the GPLv3 or later (https://www.gnu.org/licenses/gpl-3.0.html).
# Copyright 2025 DearEIS developers
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
    Tuple,
)
from numpy import (
    angle,
    integer,
    issubdtype,
)
from pandas import DataFrame
from pyimpspec import (
    Circuit,
    Element,
)
import pyimpspec
from pyimpspec import (
    ComplexImpedances,
    Frequencies,
    Impedances,
    Phases,
)
from pyimpspec.analysis.utility import _interpolate
from deareis.utility import format_timestamp


VERSION: int = 2


def _parse_settings_v2(dictionary: dict) -> dict:
    assert type(dictionary) is dict
    return {
        "cdc": dictionary["cdc"],
        "min_frequency": dictionary["min_frequency"],
        "max_frequency": dictionary["max_frequency"],
        "num_per_decade": dictionary["num_per_decade"],
    }


def _parse_settings_v1(dictionary: dict) -> dict:
    assert type(dictionary) is dict
    return {
        "cdc": dictionary["cdc"],
        "min_frequency": dictionary["min_frequency"],
        "max_frequency": dictionary["max_frequency"],
        "num_per_decade": dictionary["num_freq_per_dec"],
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

    num_per_decade: int
        The number of frequencies per decade to simulate.
        The frequencies are distributed logarithmically within the inclusive boundaries defined by `min_frequency` and `max_frequency`.
    """

    cdc: str
    min_frequency: float
    max_frequency: float
    num_per_decade: int

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
            2: _parse_settings_v2,
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
            "num_per_decade": self.num_per_decade,
        }


def _parse_result_v2(dictionary: dict) -> dict:
    assert type(dictionary) is dict
    return {
        "uuid": dictionary["uuid"],
        "timestamp": dictionary["timestamp"],
        "circuit": pyimpspec.parse_cdc(dictionary["circuit"]),
        "settings": SimulationSettings.from_dict(dictionary["settings"]),
    }


def _parse_result_v1(dictionary: dict) -> dict:
    assert type(dictionary) is dict
    return {
        "uuid": dictionary["uuid"],
        "timestamp": dictionary["timestamp"],
        "circuit": pyimpspec.parse_cdc(dictionary["circuit"]),
        "settings": SimulationSettings.from_dict(dictionary["settings"]),
    }


@dataclass
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

    def __post_init__(self):
        self._cached_frequencies: Dict[int, Frequencies] = {}
        self._cached_impedances: Dict[int, ComplexImpedances] = {}
        self._frequency: Frequencies = self.get_frequencies(
            num_per_decade=self.settings.num_per_decade
        )
        self._impedance: ComplexImpedances = self.get_impedances(
            num_per_decade=self.settings.num_per_decade
        )

    def __hash__(self) -> int:
        return int(self.uuid, 16)

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
            2: _parse_result_v2,
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
            "circuit": self.circuit.serialize(),
            "settings": self.settings.to_dict(),
        }

    def to_dataframe(self) -> DataFrame:
        """
        Get a `pandas.DataFrame` instance containing a table of element parameters.
        """
        element_labels: List[str] = []
        parameter_labels: List[str] = []
        values: List[float] = []
        internal_identifiers: Dict[int, Element] = {
            v: k
            for k, v in self.circuit.generate_element_identifiers(running=True).items()
        }
        external_identifiers: Dict[
            Element, int
        ] = self.circuit.generate_element_identifiers(running=False)

        element: Element
        ident: int
        for (ident, element) in sorted(
            internal_identifiers.items(),
            key=lambda _: _[0],
        ):
            element_label: str = self.circuit.get_element_name(
                element, identifiers=external_identifiers
            )

            parameters: Dict[str, float] = element.get_values()
            parameter_label: str
            for parameter_label in sorted(parameters.keys()):
                element_labels.append(element_label)
                parameter_labels.append(parameter_label)
                values.append(parameters[parameter_label])

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
        cdc: str = self.circuit.to_string()
        if cdc.startswith("[") and cdc.endswith("]"):
            cdc = cdc[1:-1]

        timestamp: str = format_timestamp(self.timestamp)

        return f"{cdc} ({timestamp})"

    def get_frequencies(self, num_per_decade: int = -1) -> Frequencies:
        """
        Get an array of frequencies within the range of simulated frequencies.

        Parameters
        ----------
        num_per_decade: int = -1
            If the value is greater than zero, then logarithmically distributed frequencies will be generated within the range of frequencies defined by the minimum and maximum frequencies used to generate the original simulation result.

        Returns
        -------
        Frequencies
        """
        assert issubdtype(type(num_per_decade), integer), num_per_decade

        if num_per_decade > 0:
            if num_per_decade not in self._cached_frequencies:
                self._cached_frequencies.clear()
                self._cached_frequencies[num_per_decade] = _interpolate(
                    [self.settings.min_frequency, self.settings.max_frequency],
                    num_per_decade,
                )

            return self._cached_frequencies[num_per_decade]

        return self._frequency

    def get_impedances(
        self,
        num_per_decade: int = -1,
    ) -> ComplexImpedances:
        """
        Get the complex impedances produced by the simulated circuit within the range of frequencies used to generate the original simulation result.

        Parameters
        ----------
        num_per_decade: int = -1
            If the value is greater than zero, then logarithmically distributed frequencies will be generated within the range of simulated frequencies and used to calculate the impedance produced by the simulated circuit.
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

        return self._impedance

    def get_nyquist_data(
        self,
        num_per_decade: int = -1,
    ) -> Tuple[Impedances, Impedances]:
        """
        Get the data required to plot the results as a Nyquist plot (-Im(Z) vs Re(Z)).

        Parameters
        ----------
        num_per_decade: int = -1
            If the value is greater than zero, then logarithmically distributed frequencies will be generated within the range of frequencies and used to calculate the impedance produced by the simulated circuit.

        Returns
        -------
        Tuple[Impedances, Impedances]
        """
        assert issubdtype(type(num_per_decade), integer), num_per_decade

        Z: ComplexImpedances = self.get_impedances(num_per_decade)

        return (
            Z.real,
            -Z.imag,
        )

    def get_bode_data(
        self,
        num_per_decade: int = -1,
    ) -> Tuple[Frequencies, Impedances, Phases]:
        """
        Get the data required to plot the results as a Bode plot (Mod(Z) and -Phase(Z) vs f).

        Parameters
        ----------
        num_per_decade: int = -1
            If the value is greater than zero, then logarithmically distributed frequencies will be generated within the range of frequencies and used to calculate the impedance produced by the fitted circuit.

        Returns
        -------
        Tuple[Frequencies, Impedances, Phases]
        """
        assert issubdtype(type(num_per_decade), integer), num_per_decade
        f: Frequencies = self.get_frequencies(num_per_decade)
        Z: ComplexImpedances = self.get_impedances(num_per_decade)
        return (
            f,
            abs(Z),
            -angle(Z, deg=True),
        )

    def to_parameters_dataframe(self) -> DataFrame:
        """
        Get a `pandas.DataFrame` instance containing a table of element parameters.

        Returns
        -------
        pandas.DataFrame
        """
        element_labels: List[str] = []
        parameter_labels: List[str] = []
        values: List[float] = []
        units: List[str] = []
        internal_identifiers: Dict[int, Element] = {
            v: k
            for k, v in self.circuit.generate_element_identifiers(running=True).items()
        }
        external_identifiers: Dict[
            Element, int
        ] = self.circuit.generate_element_identifiers(running=False)
        element_label: str
        parameters: Dict[int, Dict[str, float]]

        element: Element
        ident: int
        for (ident, element) in sorted(
            internal_identifiers.items(),
            key=lambda _: _[0],
        ):
            element_label = self.circuit.get_element_name(
                element,
                identifiers=external_identifiers,
            )
            parameters = element.get_values()

            parameter_label: str
            for parameter_label in sorted(parameters.keys()):
                element_labels.append(element_label)
                parameter_labels.append(parameter_label)
                values.append(parameters[parameter_label])
                units.append(element.get_unit(parameter_label))

        return DataFrame.from_dict(
            {
                "Element": element_labels,
                "Parameter": parameter_labels,
                "Value": values,
                "Unit": units,
            }
        )
