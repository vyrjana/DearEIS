# DearEIS is licensed under the GPLv3 or later (https://www.gnu.org/licenses/gpl-3.0.html).
# Copyright 2024 DearEIS developers
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
    Optional,
)
from numpy import (
    angle,
    array,
    floating,
    full,
    isnan,
    issubdtype,
    nan,
)
from scipy.signal import find_peaks
from pandas import DataFrame
from pyimpspec.analysis.utility import _calculate_pseudo_chisqr
from pyimpspec import (
    ComplexImpedances,
    ComplexResiduals,
    Frequencies,
    Gamma,
    Gammas,
    Impedances,
    Indices,
    Phases,
    Residuals,
    TimeConstant,
    TimeConstants,
)
from deareis.data.fitting import FitResult
from deareis.enums import (
    DRTMethod,
    DRTMode,
    RBFShape,
    RBFType,
    drt_method_to_label,
    drt_mode_to_label,
    label_to_drt_method,
    label_to_drt_mode,
    label_to_rbf_shape,
    label_to_rbf_type,
    rbf_shape_to_label,
    rbf_type_to_label,
)
from deareis.utility import (
    format_timestamp,
    rename_dict_entry,
)
from deareis.data import DataSet


VERSION: int = 3


def _parse_settings_v3(dictionary: dict) -> dict:
    if "fit" not in dictionary:
        dictionary["fit"] = None
    if "circuit" in dictionary:
        del dictionary["circuit"]
    if "timeout" not in dictionary:
        dictionary["timeout"] = 60
    return dictionary


def _parse_settings_v2(dictionary: dict) -> dict:
    rename_dict_entry(dictionary, "W", "gaussian_width")
    dictionary["fit"] = None
    del dictionary["circuit"]
    return dictionary


def _parse_settings_v1(dictionary: dict) -> dict:
    dictionary["circuit"] = ""
    dictionary["W"] = 0.15
    dictionary["num_per_decade"] = 100
    return dictionary


@dataclass(frozen=True)
class DRTSettings:
    """
    The settings to use when performing a DRT analysis.

    Parameters
    ----------
    method: DRTMethod
        The method to use to perform the analysis.

    mode: DRTMode
        The mode or type of data  (i.e., complex, real, or imaginary) to use.
        TR-NNLS and TR-RBF methods only.

    lambda_value: float
        The Tikhonov regularization parameter to use.
        TR-NNLS and TR-RBF methods only.

    rbf_type: RBFType
        The radial basis function to use for discretization.
        BHT and TR-RBF methods only.

    derivative_order: int
        The derivative order to use when calculating the penalty in the Tikhonov regularization.
        BHT and TR-RBF methods only.

    rbf_shape: RBFShape
        The shape to use with the radial basis function discretization.
        BHT and TR-RBF methods only.

    shape_coeff: float
        The shape coefficient.
        BHT and TR-RBF methods only.

    inductance: bool
        Whether or not to include an inductive term in the calculations.
        TR-RBF method only.

    credible_intervals: bool
        Whether or not to calculate Bayesian credible intervals.
        TR-RBF method only.

    timeout: int
        The number of seconds to wait for the calculation of credible intervals to complete.
        TR-RBF method only.

    num_samples: int
        The number of samples to use when calculating:
        - the Bayesian credible intervals (TR-RBF method)
        - the Jensen-Shannon distance (BHT method)

    num_attempts: int
        The number of attempts to make to find a solution.
        BHT method only.

    maximum_symmetry: float
        The maximum vertical peak-to-peak symmetry allowed.
        Used to discard results with strong oscillations.
        Smaller values provide stricter conditions.
        BHT and TR-RBF methods only.

    fit: Optional[FitResult]
        The FitResult for a circuit that contains one or more "(RQ)" or "(RC)" elements connected in series.
        An optional series resistance may also be included.
        For example, a circuit with a CDC representation of "R(RQ)(RQ)(RC)" would be a valid circuit.
        m(RQ)fit method only.

    gaussian_width: float
        The width of the Gaussian curve that is used to approximate the DRT of an "(RC)" element.
        m(RQ)fit method only.

    num_per_decade: int
        The number of points per decade to use when calculating a DRT.
        m(RQ)fit method only.
    """

    method: DRTMethod
    mode: DRTMode
    lambda_value: float
    rbf_type: RBFType
    derivative_order: int
    rbf_shape: RBFShape
    shape_coeff: float
    inductance: bool
    credible_intervals: bool
    timeout: int
    num_samples: int
    num_attempts: int
    maximum_symmetry: float
    fit: Optional[FitResult]
    gaussian_width: float
    num_per_decade: int

    def __repr__(self) -> str:
        return f"DRTSettings ({hex(id(self))})"

    def to_dict(self) -> dict:
        return {
            "version": VERSION,
            "method": int(self.method),
            "mode": int(self.mode),
            "lambda_value": self.lambda_value,
            "rbf_type": int(self.rbf_type),
            "derivative_order": self.derivative_order,
            "rbf_shape": int(self.rbf_shape),
            "shape_coeff": self.shape_coeff,
            "inductance": self.inductance,
            "credible_intervals": self.credible_intervals,
            "timeout": self.timeout,
            "num_samples": self.num_samples,
            "num_attempts": self.num_attempts,
            "maximum_symmetry": self.maximum_symmetry,
            "fit": self.fit.to_dict(session=False) if self.fit is not None else None,
            "gaussian_width": self.gaussian_width,
            "num_per_decade": self.num_per_decade,
        }

    @classmethod
    def from_dict(Class, dictionary: dict) -> "DRTSettings":
        assert type(dictionary) is dict
        assert "version" in dictionary
        version: int = dictionary["version"]
        del dictionary["version"]
        assert version <= VERSION, f"{version=} > {VERSION=}"
        parsers: Dict[int, Callable] = {
            1: _parse_settings_v1,
            2: _parse_settings_v2,
            3: _parse_settings_v3,
        }
        assert version in parsers, f"{version=} not in {parsers.keys()=}"
        v: int
        p: Callable
        for v, p in parsers.items():
            if v < version:
                continue
            dictionary = p(dictionary)
        assert "method" in dictionary
        assert "mode" in dictionary
        assert "lambda_value" in dictionary
        assert "rbf_type" in dictionary
        assert "derivative_order" in dictionary
        assert "rbf_shape" in dictionary
        assert "shape_coeff" in dictionary
        assert "inductance" in dictionary
        assert "credible_intervals" in dictionary
        assert "timeout" in dictionary
        assert "num_samples" in dictionary
        assert "num_attempts" in dictionary
        assert "maximum_symmetry" in dictionary
        assert "fit" in dictionary
        assert "gaussian_width" in dictionary
        assert "num_per_decade" in dictionary
        dictionary["method"] = DRTMethod(dictionary["method"])
        dictionary["mode"] = DRTMode(dictionary["mode"])
        dictionary["rbf_type"] = RBFType(dictionary["rbf_type"])
        dictionary["rbf_shape"] = RBFShape(dictionary["rbf_shape"])
        if dictionary["fit"] is not None:
            dictionary["fit"] = FitResult.from_dict(dictionary["fit"])
        return Class(**dictionary)


def _parse_result_v3(dictionary: dict) -> dict:
    if "pseudo_chisqr" not in dictionary:
        dictionary["pseudo_chisqr"] = nan
    if "chisqr" in dictionary:
        del dictionary["chisqr"]
    return dictionary


def _parse_result_v2(dictionary: dict) -> dict:
    rename_dict_entry(dictionary, "tau", "time_constants")
    rename_dict_entry(dictionary, "gamma", "real_gammas")
    rename_dict_entry(dictionary, "imaginary_gamma", "imaginary_gammas")
    rename_dict_entry(dictionary, "real_impedance", "real_impedances")
    rename_dict_entry(dictionary, "imaginary_impedance", "imaginary_impedances")
    rename_dict_entry(dictionary, "frequency", "frequencies")
    rename_dict_entry(dictionary, "real_residual", "real_residuals")
    rename_dict_entry(dictionary, "imaginary_residual", "imaginary_residuals")
    rename_dict_entry(dictionary, "mean_gamma", "mean_gammas")
    rename_dict_entry(dictionary, "lower_bound", "lower_bounds")
    rename_dict_entry(dictionary, "upper_bound", "upper_bounds")
    dictionary["chisqr"] = nan
    return dictionary


def _parse_result_v1(dictionary: dict) -> dict:
    return dictionary


@dataclass
class DRTResult:
    """
    An object representing the results of calculating the distribution of relaxation times in a  data set.

    Parameters
    ----------
    uuid: str
        The universally unique identifier assigned to this result.

    timestamp: float
        The Unix time (in seconds) for when the test was performed.

    time_constants: TimeConstants
        The time constants (in seconds).

    real_gammas: Gammas
        The corresponding gamma values (in ohms).

    imaginary_gammas: Gammas
        The gamma values calculated based the imaginary part of the impedance data.
        Only non-empty when the BHT method has been used.

    frequencies: Frequencies
        The frequencies of the analyzed data set.

    impedances: ComplexImpedances
        The modeled impedances.

    residuals: ComplexResiduals
        The residuals for the real and imaginary parts of the modeled impedances.

    mean_gammas: Gammas
        The mean values for gamma(tau).
        Only non-empty when the TR-RBF method has been used and the Bayesian credible intervals have been calculated.

    lower_bounds: Gammas
        The lower bound for the gamma(tau) values.
        Only non-empty when the TR-RBF method has been used and the Bayesian credible intervals have been calculated.

    upper_bounds: Gammas
        The upper bound for the gamma(tau) values.
        Only non-empty when the TR-RBF method has been used and the Bayesian credible intervals have been calculated.

    scores: Dict[str, complex]
        The scores calculated for the analyzed data set.
        Only non-empty when the BHT method has been used.

    pseudo_chisqr: float
        The calculated |pseudo chi-squared| (eq. 14 in Boukamp, 1995).

    lambda_value: float
        The regularization parameter used as part of the Tikhonov regularization.
        Only valid (i.e., positive) when the TR-NNLS or TR-RBF methods have been used.

    mask: Dict[int, bool]
        The mask that was applied to the analyzed data set.

    settings: DRTSettings
        The settings used to perform this analysis.
    """

    uuid: str
    timestamp: float
    time_constants: TimeConstants
    real_gammas: Gammas
    imaginary_gammas: Gammas
    frequencies: Frequencies
    impedances: ComplexImpedances
    residuals: ComplexResiduals
    mean_gammas: Gammas
    lower_bounds: Gammas
    upper_bounds: Gammas
    scores: Dict[str, complex]
    pseudo_chisqr: float
    lambda_value: float
    mask: Dict[int, bool]
    settings: DRTSettings

    def __repr__(self) -> str:
        return f"DRTResult ({self.get_label()}, {hex(id(self))})"

    def __hash__(self) -> int:
        return int(self.uuid, 16)

    @classmethod
    def from_dict(
        Class, dictionary: dict, data: Optional[DataSet] = None
    ) -> "DRTResult":
        """
        Create an instance from a dictionary.

        Parameters
        ----------
        dictionary: dict
            The dictionary to turn into a DRTResult object.

        data: Optional[DataSet], optional
            The DataSet object that this result is for.

        Returns
        -------
        DRTResult
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
            3: _parse_result_v3,
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
        assert "time_constants" in dictionary
        assert "real_gammas" in dictionary
        assert "imaginary_gammas" in dictionary
        assert "real_impedances" in dictionary
        assert "imaginary_impedances" in dictionary
        assert "frequencies" in dictionary
        assert "real_residuals" in dictionary
        assert "imaginary_residuals" in dictionary
        assert "mean_gammas" in dictionary
        assert "lower_bounds" in dictionary
        assert "upper_bounds" in dictionary
        assert "real_scores" in dictionary
        assert "imaginary_scores" in dictionary
        assert "pseudo_chisqr" in dictionary
        assert "lambda_value" in dictionary
        assert "mask" in dictionary
        assert "settings" in dictionary
        dictionary["time_constants"] = array(dictionary["time_constants"])
        dictionary["real_gammas"] = array(dictionary["real_gammas"])
        dictionary["imaginary_gammas"] = array(dictionary["imaginary_gammas"])
        dictionary["frequencies"] = array(dictionary["frequencies"])
        dictionary["mean_gammas"] = array(dictionary["mean_gammas"])
        dictionary["lower_bounds"] = array(dictionary["lower_bounds"])
        dictionary["upper_bounds"] = array(dictionary["upper_bounds"])
        dictionary["settings"] = DRTSettings.from_dict(dictionary["settings"])
        mask: Dict[str, bool] = dictionary["mask"]
        dictionary["mask"] = {
            i: mask.get(str(i), False) for i in range(0, len(dictionary["frequencies"]))
        }
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
        dictionary["scores"] = {
            k: complex(
                dictionary["real_scores"][k],
                dictionary["imaginary_scores"][k],
            )
            for k in dictionary["real_scores"]
        }
        del dictionary["real_scores"]
        del dictionary["imaginary_scores"]
        if isnan(dictionary["pseudo_chisqr"]):
            dictionary["pseudo_chisqr"] = _calculate_pseudo_chisqr(
                Z_exp=data.get_impedances(),
                Z_fit=dictionary["impedances"],
            )
        return Class(**dictionary)

    def to_dict(self) -> dict:
        """
        Return a dictionary that can be used to recreate an instance.

        Returns
        -------
        dict
        """
        dictionary: dict = {
            "version": VERSION,
            "uuid": self.uuid,
            "timestamp": self.timestamp,
            "time_constants": list(self.time_constants),
            "real_gammas": list(self.real_gammas),
            "imaginary_gammas": list(self.imaginary_gammas),
            "real_impedances": list(self.impedances.real),
            "imaginary_impedances": list(self.impedances.imag),
            "frequencies": list(self.frequencies),
            "real_residuals": list(self.residuals.real),
            "imaginary_residuals": list(self.residuals.imag),
            "mean_gammas": list(self.mean_gammas),
            "lower_bounds": list(self.lower_bounds),
            "upper_bounds": list(self.upper_bounds),
            "real_scores": {k: v.real for k, v in self.scores.items()},
            "imaginary_scores": {k: v.imag for k, v in self.scores.items()},
            "pseudo_chisqr": self.pseudo_chisqr,
            "lambda_value": self.lambda_value,
            "mask": {k: True for k, v in self.mask.items() if v is True},
            "settings": self.settings.to_dict(),
        }
        return dictionary

    def get_label(self) -> str:
        """
        Generate a label for the result.

        Returns
        -------
        str
        """
        method: str = drt_method_to_label[self.settings.method]
        timestamp: str = format_timestamp(self.timestamp)
        return f"{method} ({timestamp})"

    def get_frequencies(self) -> Frequencies:
        """
        Get the frequencies (in hertz) of the data set.

        Returns
        -------
        Frequencies
        """
        return self.frequencies

    def get_impedances(self) -> ComplexImpedances:
        """
        Get the complex impedance of the model.

        Returns
        -------
        ComplexImpedances
        """
        return self.impedances

    def get_time_constants(self) -> TimeConstants:
        """
        Get the time constants.

        Returns
        -------
        TimeConstants
        """
        return self.time_constants

    def get_gammas(self) -> Tuple[Gammas, Gammas]:
        """
        Get the gamma values.

        Returns
        -------
        Tuple[Gammas, Gammas]
        """
        return (
            self.real_gammas,
            self.imaginary_gammas,
        )

    def to_peaks_dataframe(
        self,
        threshold: float = 0.0,
        columns: Optional[List[str]] = None,
    ) -> DataFrame:
        """
        Get the peaks as a pandas.DataFrame object that can be used to generate, e.g., a Markdown table.

        Parameters
        ----------
        threshold: float, optional
            The minimum peak height threshold (relative to the height of the tallest peak) for a peak to be included.

        columns: Optional[List[str]], optional
            The labels to use as the column headers for real time constants, real gammas, imaginary time constants, and imaginary gammas.

        Returns
        -------
        DataFrame
        """
        if columns is None:
            if self.settings.method == DRTMethod.BHT:
                columns = [
                    "tau, real (s)",
                    "gamma, real (ohm)",
                    "tau, imag. (s)",
                    "gamma, imag. (ohm)",
                ]
            else:
                columns = [
                    "tau (s)",
                    "gamma (ohm)",
                ]
        assert isinstance(columns, list)
        if self.settings.method == DRTMethod.BHT:
            assert len(columns) >= 4
        else:
            assert len(columns) >= 2
        real_taus: TimeConstants
        real_gammas: Gammas
        imag_taus: TimeConstants
        imag_gammas: Gammas
        (real_taus, real_gammas, imag_taus, imag_gammas) = self.get_peaks(
            threshold=threshold
        )
        if self.settings.method != DRTMethod.BHT:
            dictionary: dict = {
                columns[0]: real_taus,
                columns[1]: real_gammas,
            }
        else:
            dictionary: dict = {
                columns[0]: real_taus,
                columns[1]: real_gammas,
                columns[2]: imag_taus,
                columns[3]: imag_gammas,
            }
        return DataFrame.from_dict(dictionary)

    def get_peaks(
        self,
        threshold: float = 0.0,
    ) -> Tuple[TimeConstants, Gammas, TimeConstants, Gammas]:
        """
        Get the time constants (in seconds) and gamma (in ohms) of peaks with magnitudes greater than the threshold.
        The threshold and the magnitudes are all relative to the magnitude of the highest peak.

        Parameters
        ----------
        threshold: float, optional
            The threshold for the relative magnitude (0.0 to 1.0).

        Returns
        -------
        Tuple[TimeConstants, Gammas, TimeConstants, Gammas]
        """
        assert issubdtype(type(threshold), floating), type(threshold)
        assert 0.0 <= threshold <= 1.0, threshold

        def filter_indices(gammas: Gammas) -> Indices:
            max_g: Gamma = max(gammas)
            indices: Indices = find_peaks(gammas)[0]
            return array(
                list(
                    filter(
                        lambda _: gammas[_] / max_g > threshold and gammas[_] > 0.0,
                        indices,
                    ),
                )
            )

        real_indices: Indices = filter_indices(self.real_gammas)
        real_taus: TimeConstants
        real_gammas: Gammas
        if real_indices.size > 0:
            real_taus = self.time_constants[real_indices]
            real_gammas = self.real_gammas[real_indices]
        else:
            real_taus = array([])
            real_gammas = array([])
        imag_indices: Indices
        if self.imaginary_gammas.size > 0:
            imag_indices = filter_indices(self.imaginary_gammas)
            imag_taus: TimeConstants
            imag_gammas: Gammas
            if imag_indices.size > 0:
                imag_taus = self.time_constants[imag_indices]
                imag_gammas = self.imaginary_gammas[imag_indices]
            else:
                imag_taus = array([])
                imag_gammas = array([])
        else:
            imag_taus = array([])
            imag_gammas = array([])
        if real_taus.size != imag_taus.size:

            def pad(
                t: TimeConstants,
                g: Gammas,
                w: int,
            ) -> Tuple[TimeConstants, Gammas]:
                tmp_taus: TimeConstants = full(w, nan, dtype=TimeConstant)
                tmp_gammas: Gammas = full(w, nan, dtype=Gamma)
                tmp_taus[: t.size] = t
                tmp_gammas[: g.size] = g
                return (
                    tmp_taus,
                    tmp_gammas,
                )

            max_size: int = max(real_taus.size, imag_taus.size)
            real_taus, real_gammas = pad(real_taus, real_gammas, max_size)
            imag_taus, imag_gammas = pad(imag_taus, imag_gammas, max_size)
        return (
            real_taus,
            real_gammas,
            imag_taus,
            imag_gammas,
        )

    def get_nyquist_data(self) -> Tuple[Impedances, Impedances]:
        """
        Get the data necessary to plot this DataSet as a Nyquist plot: the real and the negative imaginary parts of the impedances.

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
        Get the data necessary to plot this DataSet as a Bode plot: the frequencies, the absolute magnitudes of the impedances, and the negative phase angles/shifts of the impedances in degrees.

        Returns
        -------
        Tuple[Frequencies, Impedances, Phases]
        """
        return (
            self.frequencies,
            abs(self.impedances),
            -angle(self.impedances, deg=True),
        )

    def get_drt_data(self) -> Tuple[TimeConstants, Gammas, Gammas]:
        """
        Get the data necessary to plot this DRTResult as a DRT plot: the time constants and the corresponding gamma values.

        Returns
        -------
        Tuple[TimeConstants, Gammas, Gammas]
        """
        return (
            self.time_constants,
            self.real_gammas,
            self.imaginary_gammas,
        )

    def get_drt_credible_intervals_data(
        self,
    ) -> Tuple[TimeConstants, Gammas, Gammas, Gammas]:
        """
        Get the data necessary to plot the Bayesian credible intervals for this DRTResult: the time constants, the mean gamma values, the lower bound gamma values, and the upper bound gamma values.

        Returns
        -------
        Tuple[TimeConstants, Gammas, Gammas, Gammas]
        """
        if not self.mean_gammas.any():
            return (
                array([]),
                array([]),
                array([]),
                array([]),
            )
        return (
            self.time_constants,
            self.mean_gammas,
            self.lower_bounds,
            self.upper_bounds,
        )

    def get_residuals_data(self) -> Tuple[Frequencies, Residuals, Residuals]:
        """
        Get the data necessary to plot the relative residuals for this DRTResult: the frequencies and the relative residuals for the real and imaginary parts of the impedances in percents.

        Returns
        -------
        Tuple[Frequencies, Residuals, Residuals]
        """
        return (
            self.frequencies,
            self.residuals.real * 100,
            self.residuals.imag * 100,
        )

    def get_scores(self) -> Dict[str, complex]:
        """
        Get the scores for the data set.
        The scores are represented as complex values where the real and imaginary parts have magnitudes ranging from 0.0 to 1.0.
        A consistent impedance spectrum should score high.
        BHT method only.

        Returns
        -------
        Dict[str, complex]
        """
        return self.scores

    def to_scores_dataframe(
        self,
        columns: Optional[List[str]] = None,
        rows: Optional[List[str]] = None,
    ) -> Optional[DataFrame]:
        """
        Get the scores for the data set as a pandas.DataFrame object that can be used to generate, e.g., a Markdown table.
        BHT method only.

        Parameters
        ----------
        columns: Optional[List[str]], optional
            The labels for the column headers.

        rows: Optional[List[str]], optional
            The labels for the rows.

        Returns
        -------
        Optional[pandas.DataFrame]
        """
        if self.settings.method != DRTMethod.BHT:
            return None
        if columns is None:
            columns = [
                "Score",
                "Real (%)",
                "Imag. (%)",
            ]
        assert isinstance(columns, list), columns
        assert len(columns) == 3
        if rows is None:
            rows = [
                "Mean",
                "Residuals, 1 sigma",
                "Residuals, 2 sigma",
                "Residuals, 3 sigma",
                "Hellinger distance",
                "Jensen-Shannon distance",
            ]
        assert isinstance(rows, list), rows
        assert len(rows) == 6
        return DataFrame.from_dict(
            {
                columns[0]: rows,
                columns[1]: [
                    self.scores["mean"].real * 100,
                    self.scores["residuals_1sigma"].real * 100,
                    self.scores["residuals_2sigma"].real * 100,
                    self.scores["residuals_3sigma"].real * 100,
                    self.scores["hellinger_distance"].real * 100,
                    self.scores["jensen_shannon_distance"].real * 100,
                ],
                columns[2]: [
                    self.scores["mean"].imag * 100,
                    self.scores["residuals_1sigma"].imag * 100,
                    self.scores["residuals_2sigma"].imag * 100,
                    self.scores["residuals_3sigma"].imag * 100,
                    self.scores["hellinger_distance"].imag * 100,
                    self.scores["jensen_shannon_distance"].imag * 100,
                ],
            }
        )
