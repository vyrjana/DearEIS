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
    isnan,
    log10 as log,
)
from pandas import DataFrame
from pyimpspec.analysis.utility import _calculate_pseudo_chisqr
from pyimpspec import (
    ComplexImpedances,
    ComplexResiduals,
    Frequencies,
    Impedances,
    Phases,
    Residuals,
)
from deareis.enums import (
    ZHITInterpolation,
    ZHITSmoothing,
    ZHITWindow,
    value_to_zhit_interpolation,
    value_to_zhit_smoothing,
    value_to_zhit_window,
    zhit_interpolation_to_label,
    zhit_smoothing_to_label,
    zhit_window_to_label,
)
from deareis.utility import format_timestamp
from deareis.data import DataSet

VERSION: int = 1


def _parse_settings_v1(dictionary: dict) -> dict:
    return dictionary


@dataclass(frozen=True)
class ZHITSettings:
    """
    A class to store the settings used to perform a Z-HIT analysis.

    Parameters
    ----------
    smoothing: ZHITSmoothing
        The smoothing algorithm to use.

    num_points: int
        The number of points to consider when smoothing a point.
        
    polynomial_order: int
        The order of the polynomial to use in the Savitzky-Golay algorithm.

    num_iterations: int
        The number of iterations to use in the LOWESS algorithm.

    interpolation: ZHITInterpolation
        The spline to use when interpolating the phase data.

    window: ZHITWindow
        The window function to use when generating weights for the offset adjustment.

    window_center: float
        The center of the window function on the logarithmic frequency scale (e.g., 100 Hz -> 2.0).

    window_width: float
        The width of the window function on the logarithmic frequency scale (e.g., 2.0 means 1 decade on each side of the window center).
    """

    smoothing: ZHITSmoothing
    num_points: int
    polynomial_order: int
    num_iterations: int
    interpolation: ZHITInterpolation
    window: ZHITWindow
    window_center: float
    window_width: float

    def __repr__(self) -> str:
        return f"ZHITSettings ({hex(id(self))})"

    @classmethod
    def from_dict(Class, dictionary: dict) -> "ZHITSettings":
        """
        Create an instance from a dictionary.

        Parameters
        ----------
        dictionary: dict
            The dictionary to turn into a ZHITSettings object.

        Returns
        -------
        ZHITSettings
        """
        assert type(dictionary) is dict
        assert "version" in dictionary
        version: int = dictionary["version"]
        del dictionary["version"]
        assert version <= VERSION, f"{version=} > {VERSION=}"
        parsers: Dict[int, Callable] = {
            1: _parse_settings_v1,
        }
        assert version in parsers, f"{version=} not in {parsers.keys()=}"
        v: int
        p: Callable
        for v, p in parsers.items():
            if v < version:
                continue
            dictionary = p(dictionary)
        assert "smoothing" in dictionary
        assert "num_points" in dictionary
        assert "polynomial_order" in dictionary
        assert "num_iterations" in dictionary
        assert "interpolation" in dictionary
        assert "window" in dictionary
        assert "window_center" in dictionary
        assert "window_width" in dictionary
        dictionary["smoothing"] = ZHITSmoothing(dictionary["smoothing"])
        dictionary["interpolation"] = ZHITInterpolation(dictionary["interpolation"])
        dictionary["window"] = ZHITWindow(dictionary["window"])
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
            "smoothing": self.smoothing,
            "num_points": self.num_points,
            "polynomial_order": self.polynomial_order,
            "num_iterations": self.num_iterations,
            "interpolation": self.interpolation,
            "window": self.window,
            "window_center": self.window_center,
            "window_width": self.window_width,
        }


def _parse_result_v1(dictionary: dict) -> dict:
    return dictionary


@dataclass
class ZHITResult:
    """
    A class containing the result of a Z-HIT analysis.

    Parameters
    ----------
    uuid: str
        The universally unique identifier assigned to this result.

    timestamp: float
        The Unix time (in seconds) for when the test was performed.

    frequencies: Frequencies
        The frequencies used to perform the analysis.

    impedances: ComplexImpedances
        The reconstructed impedances.

    residuals: ComplexResiduals
        The residuals of the reconstructed impedances and the original impedances.

    mask: Dict[int, bool]
        The mask that was applied to the original data set.

    pseudo_chisqr: float
        The calculated |pseudo chi-squared| (eq. 14 in Boukamp, 1995).

    smoothing: str
        The smoothing algorithm that was used (relevant if this setting was set to 'auto').

    interpolation: str
        The spline that was used to interpolate the data (relevant if this setting was set to 'auto').
    window: str
        The window function that was used to generate weights for the offset adjustment (relevant if this setting was set to 'auto').

    settings: ZHITSettings
        The settings that were used to perform the analysis.
    """

    uuid: str
    timestamp: float
    frequencies: Frequencies
    impedances: ComplexImpedances
    residuals: ComplexResiduals
    mask: Dict[int, bool]
    pseudo_chisqr: float
    smoothing: str
    interpolation: str
    window: str
    settings: ZHITSettings

    def __repr__(self) -> str:
        return f"ZHITResult ({hex(id(self))})"

    @classmethod
    def from_dict(
        Class,
        dictionary: dict,
        data: Optional[DataSet] = None,
    ) -> "ZHITResult":
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
        ZHITResult
        """
        assert isinstance(dictionary, dict), dictionary
        assert data is None or isinstance(data, DataSet), data
        assert "version" in dictionary
        version: int = dictionary["version"]
        del dictionary["version"]
        assert version <= VERSION, f"{version=} > {VERSION=}"
        parsers: Dict[int, Callable] = {
            1: _parse_result_v1,
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
        assert "frequencies" in dictionary
        assert "real_impedances" in dictionary
        assert "imaginary_impedances" in dictionary
        assert "real_residuals" in dictionary
        assert "imaginary_residuals" in dictionary
        assert "mask" in dictionary
        assert "pseudo_chisqr" in dictionary
        assert "smoothing" in dictionary
        assert "interpolation" in dictionary
        assert "window" in dictionary
        assert "settings" in dictionary
        dictionary["frequencies"] = array(dictionary["frequencies"])
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
        if isnan(dictionary["pseudo_chisqr"]):
            dictionary["pseudo_chisqr"] = _calculate_pseudo_chisqr(
                Z_exp=data.get_impedances(),
                Z_fit=dictionary["impedances"],
            )
        dictionary["settings"] = ZHITSettings.from_dict(dictionary["settings"])
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
            "uuid": self.uuid,
            "timestamp": self.timestamp,
            "frequencies": list(self.frequencies),
            "real_impedances": list(self.impedances.real),
            "imaginary_impedances": list(self.impedances.imag),
            "real_residuals": list(self.residuals.real),
            "imaginary_residuals": list(self.residuals.imag),
            "mask": {k: True for k, v in self.mask.items() if v is True},
            "pseudo_chisqr": self.pseudo_chisqr,
            "smoothing": self.smoothing,
            "interpolation": self.interpolation,
            "window": self.window,
            "settings": self.settings.to_dict(),
        }

    def to_statistics_dataframe(self) -> DataFrame:
        """
        Get the statistics related to the modulus reconstruction as a pandas.DataFrame object.

        Returns
        -------
        DataFrame
        """
        statistics: Dict[str, Union[float, str]] = {
            "Log pseudo chi-squared": log(self.pseudo_chisqr),
            "Smoothing": zhit_smoothing_to_label[
                value_to_zhit_smoothing[self.smoothing]
            ],
            "Interpolation": zhit_interpolation_to_label[
                value_to_zhit_interpolation[self.interpolation]
            ],
            "Window": zhit_window_to_label.get(
                value_to_zhit_window.get(
                    self.window,
                    self.window,
                ),
                self.window,
            ),
        }
        return DataFrame.from_dict(
            {
                "Label": list(statistics.keys()),
                "Value": list(statistics.values()),
            }
        )

    def get_label(self) -> str:
        timestamp: str = format_timestamp(self.timestamp)
        return f"Z-HIT ({timestamp})"

    def get_frequencies(self) -> Frequencies:
        """
        Get an array of frequencies within the range of frequencies in the data set.

        Returns
        -------
        Frequencies
        """
        return self.frequencies

    def get_impedances(self) -> ComplexImpedances:
        """
        Get the complex impedances produced by the fitted circuit within the range of frequencies in the data set.

        Returns
        -------
        ComplexImpedances
        """
        return self.impedances

    def get_nyquist_data(self) -> Tuple[Impedances, Impedances]:
        """
        Get the data required to plot the results as a Nyquist plot (-Im(Z) vs Re(Z)).

        Returns
        -------
        Tuple[Impedances, Impedances]
        """
        return (
            self.impedances.real,
            -self.impedances.imag,
        )

    def get_bode_data(self) -> Tuple[Frequencies, Impedances, Phases]:
        """
        Get the data required to plot the results as a Bode plot (Mod(Z) and -Phase(Z) vs f).

        Returns
        -------
        Tuple[Frequencies, Impedancesy, Phases]
        """
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
