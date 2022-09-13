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
    Optional,
)
from numpy import (
    angle,
    array,
    floating,
    issubdtype,
    ndarray,
)
from scipy.signal import find_peaks
from pandas import DataFrame
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
from deareis.utility import format_timestamp


VERSION: int = 1


def _parse_settings_v1(dictionary: dict) -> dict:
    # TODO: Update implementation once VERSION is incremented
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
        TR-RBF methods only.

    credible_intervals: bool
        Whether or not to calculate Bayesian credible intervals.
        TR-RBF methods only.

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
    num_samples: int
    num_attempts: int
    maximum_symmetry: float

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
            "num_samples": self.num_samples,
            "num_attempts": self.num_attempts,
            "maximum_symmetry": self.maximum_symmetry,
        }

    @classmethod
    def from_dict(Class, dictionary: dict) -> "DRTSettings":
        assert type(dictionary) is dict
        assert "version" in dictionary
        version: int = dictionary["version"]
        assert version <= VERSION, f"{version=} > {VERSION=}"
        parsers: Dict[int, Callable] = {
            1: _parse_settings_v1,
        }
        assert version in parsers, f"{version=} not in {parsers.keys()=}"
        del dictionary["version"]
        dictionary = parsers[version](dictionary)
        dictionary["method"] = DRTMethod(dictionary["method"])
        dictionary["mode"] = DRTMode(dictionary["mode"])
        dictionary["rbf_type"] = RBFType(dictionary["rbf_type"])
        dictionary["rbf_shape"] = RBFShape(dictionary["rbf_shape"])
        return Class(**dictionary)


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

    tau: ndarray
        The time constants (in seconds).

    gamma: ndarray
        The corresponding gamma(tau) values (in ohms).
        These are the gamma(tau) for the real part when the BHT method has been used.

    frequency: ndarray
        The frequencies of the analyzed data set.

    impedance: ndarray
        The modeled impedances.

    real_residual: ndarray
        The residuals for the real parts of the modeled and experimental impedances.

    imaginary_residual: ndarray
        The residuals for the imaginary parts of the modeled and experimental impedances.

    mean_gamma: ndarray
        The mean values for gamma(tau).
        Only non-empty when the TR-RBF method has been used and the Bayesian credible intervals have been calculated.

    lower_bound: ndarray
        The lower bound for the gamma(tau) values.
        Only non-empty when the TR-RBF method has been used and the Bayesian credible intervals have been calculated.

    upper_bound: ndarray
        The upper bound for the gamma(tau) values.
        Only non-empty when the TR-RBF method has been used and the Bayesian credible intervals have been calculated.

    imaginary_gamma: ndarray
        These are the gamma(tau) for the imaginary part when the BHT method has been used.
        Only non-empty when the BHT method has been used.

    scores: Dict[str, complex]
        The scores calculated for the analyzed data set.
        Only non-empty when the BHT method has been used.

    chisqr: float
        The chi-square goodness of fit value for the modeled impedance.

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
    tau: ndarray
    gamma: ndarray
    frequency: ndarray
    impedance: ndarray
    real_residual: ndarray
    imaginary_residual: ndarray
    mean_gamma: ndarray
    lower_bound: ndarray
    upper_bound: ndarray
    imaginary_gamma: ndarray
    scores: Dict[str, complex]
    chisqr: float
    lambda_value: float
    mask: Dict[int, bool]
    settings: DRTSettings

    def __repr__(self) -> str:
        return f"DRTResult ({self.get_label()}, {hex(id(self))})"

    @classmethod
    def from_dict(Class, dictionary: dict) -> "DRTResult":
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
        dictionary = parsers[version](dictionary)
        dictionary["tau"] = array(dictionary["tau"])
        dictionary["gamma"] = array(dictionary["gamma"])
        dictionary["frequency"] = array(dictionary["frequency"])
        dictionary["real_residual"] = array(dictionary["real_residual"])
        dictionary["imaginary_residual"] = array(dictionary["imaginary_residual"])
        dictionary["mean_gamma"] = array(dictionary["mean_gamma"])
        dictionary["lower_bound"] = array(dictionary["lower_bound"])
        dictionary["upper_bound"] = array(dictionary["upper_bound"])
        dictionary["imaginary_gamma"] = array(dictionary["imaginary_gamma"])
        dictionary["settings"] = DRTSettings.from_dict(dictionary["settings"])
        del dictionary["version"]
        mask: Dict[str, bool] = dictionary["mask"]
        if len(mask) < len(dictionary["frequency"]):
            i: int
            for i in range(0, len(dictionary["frequency"])):
                flag: bool = mask.get(str(i), False)
                if flag is True:
                    del mask[str(i)]
                mask[i] = flag  # Converting str keys to int
        dictionary["impedance"] = array(
            list(
                map(
                    lambda _: complex(*_),
                    zip(
                        dictionary["real_impedance"],
                        dictionary["imaginary_impedance"],
                    ),
                )
            )
        )
        del dictionary["real_impedance"]
        del dictionary["imaginary_impedance"]
        dictionary["scores"] = {
            k: complex(
                dictionary["real_scores"][k],
                dictionary["imaginary_scores"][k],
            )
            for k in dictionary["real_scores"]
        }
        del dictionary["real_scores"]
        del dictionary["imaginary_scores"]
        return Class(**dictionary)

    def to_dict(self) -> dict:
        """
        Return a dictionary that can be used to recreate an instance.
        """
        dictionary: dict = {
            "version": VERSION,
            "uuid": self.uuid,
            "timestamp": self.timestamp,
            "tau": list(self.tau),
            "gamma": list(self.gamma),
            "real_impedance": list(self.impedance.real),
            "imaginary_impedance": list(self.impedance.imag),
            "frequency": list(self.frequency),
            "real_residual": list(self.real_residual),
            "imaginary_residual": list(self.imaginary_residual),
            "mean_gamma": list(self.mean_gamma),
            "lower_bound": list(self.lower_bound),
            "upper_bound": list(self.upper_bound),
            "imaginary_gamma": list(self.imaginary_gamma),
            "real_scores": {k: v.real for k, v in self.scores.items()},
            "imaginary_scores": {k: v.imag for k, v in self.scores.items()},
            "chisqr": self.chisqr,
            "lambda_value": self.lambda_value,
            "mask": {k: True for k, v in self.mask.items() if v is True},
            "settings": self.settings.to_dict(),
        }
        return dictionary

    def get_label(self) -> str:
        """
        Generate a label for the result.
        """
        method: str = drt_method_to_label[self.settings.method]
        timestamp: str = format_timestamp(self.timestamp)
        return f"{method} ({timestamp})"

    def get_frequency(self) -> ndarray:
        """
        Get the frequencies (in hertz) of the data set.

        Returns
        -------
        ndarray
        """
        return self.frequency

    def get_impedance(self) -> ndarray:
        """
        Get the complex impedance of the model.

        Returns
        -------
        ndarray
        """
        return self.impedance

    def get_tau(self) -> ndarray:
        """
        Get the time constants.

        Returns
        -------
        ndarray
        """
        return self.tau

    def get_gamma(self, imaginary: bool = False) -> ndarray:
        """
        Get the gamma values.

        Parameters
        ----------
        imaginary: bool = False
            Get the imaginary gamma (non-empty only when using the BHT method).

        Returns
        -------
        ndarray
        """
        if imaginary is True:
            return self.imaginary_gamma
        return self.gamma

    def to_dataframe(
        self,
        threshold: float = 0.0,
        imaginary: bool = False,
        latex_labels: bool = False,
        include_frequency: bool = False,
    ) -> DataFrame:
        """
        Get the peaks as a pandas.DataFrame object that can be used to generate, e.g., a Markdown table.

        Parameters
        ----------
        threshold: float = 0.0
            The threshold for the peaks (0.0 to 1.0 relative to the highest peak).

        imaginary: bool = False
            Use the imaginary gamma (non-empty only when using the BHT method).

        latex_labels: bool = False
            Whether or not to use LaTeX macros in the labels.

        include_frequency: bool = False
            Whether or not to also include a column with the frequencies corresponding to the time constants.

        Returns
        -------
        DataFrame
        """
        tau: ndarray
        gamma: ndarray
        tau, gamma = self.get_peaks(threshold=threshold, imaginary=imaginary)
        f: ndarray = 1 / tau
        dictionary: dict = {}
        dictionary["tau (s)" if not latex_labels else r"$\tau$ (s)"] = tau
        if include_frequency is True:
            dictionary["f (Hz)" if not latex_labels else r"$f$ (Hz)"] = f
        dictionary[
            "gamma (ohms)" if not latex_labels else r"$\gamma\ (\Omega)$"
        ] = gamma
        return DataFrame.from_dict(dictionary)

    def get_peaks(
        self,
        threshold: float = 0.0,
        imaginary: bool = False,
    ) -> Tuple[ndarray, ndarray]:
        """
        Get the time constants (in seconds) and gamma (in ohms) of peaks with magnitudes greater than the threshold.
        The threshold and the magnitudes are all relative to the magnitude of the highest peak.

        Parameters
        ----------
        threshold: float = 0.0
            The threshold for the relative magnitude (0.0 to 1.0).

        imaginary: bool = False
            Use the imaginary gamma (non-empty only when using the BHT method).

        Returns
        -------
        Tuple[ndarray, ndarray]
        """
        assert (
            issubdtype(type(threshold), floating) and 0.0 <= threshold <= 1.0
        ), threshold
        assert type(imaginary) is bool, imaginary
        gamma: ndarray = self.gamma if not imaginary else self.imaginary_gamma
        assert type(gamma) is ndarray, gamma
        if not gamma.any():
            return (
                array([]),
                array([]),
            )
        indices: ndarray
        indices, _ = find_peaks(gamma)
        if not indices.any():
            return (
                array([]),
                array([]),
            )
        max_g: float = max(gamma)
        if max_g == 0.0:
            return (
                array([]),
                array([]),
            )
        indices = array(
            list(
                filter(
                    lambda _: gamma[_] / max_g > threshold and gamma[_] > 0.0, indices
                )
            )
        )
        if indices.any():
            return (
                self.tau[indices],
                gamma[indices],
            )
        return (
            array([]),
            array([]),
        )

    def get_nyquist_data(self) -> Tuple[ndarray, ndarray]:
        """
        Get the data necessary to plot this DataSet as a Nyquist plot: the real and the negative imaginary parts of the impedances.

        Returns
        -------
        Tuple[ndarray, ndarray]
        """
        return (
            self.impedance.real,
            -self.impedance.imag,
        )

    def get_bode_data(self) -> Tuple[ndarray, ndarray, ndarray]:
        """
        Get the data necessary to plot this DataSet as a Bode plot: the frequencies, the absolute magnitudes of the impedances, and the negative phase angles/shifts of the impedances in degrees.

        Returns
        -------
        Tuple[ndarray, ndarray, ndarray]
        """
        return (
            self.frequency,
            abs(self.impedance),
            -angle(self.impedance, deg=True),
        )

    def get_drt_data(self, imaginary: bool = False) -> Tuple[ndarray, ndarray]:
        """
        Get the data necessary to plot this DRTResult as a DRT plot: the time constants and the corresponding gamma values.

        Parameters
        ----------
        imaginary: bool = False
            Get the imaginary gamma (non-empty only when using the BHT method).

        Returns
        -------
        Tuple[ndarray, ndarray]
        """
        gamma: ndarray = self.gamma if not imaginary else self.imaginary_gamma
        if not gamma.any():
            return (
                array([]),
                array([]),
            )
        return (
            self.tau,
            gamma,
        )

    def get_drt_credible_intervals(self) -> Tuple[ndarray, ndarray, ndarray, ndarray]:
        """
        Get the data necessary to plot the Bayesian credible intervals for this DRTResult: the time constants, the mean gamma values, the lower bound gamma values, and the upper bound gamma values.

        Returns
        -------
        Tuple[ndarray, ndarray, ndarray, ndarray]
        """
        if not self.mean_gamma.any():
            return (
                array([]),
                array([]),
                array([]),
                array([]),
            )
        return (
            self.tau,
            self.mean_gamma,
            self.lower_bound,
            self.upper_bound,
        )

    def get_residual_data(self) -> Tuple[ndarray, ndarray, ndarray]:
        """
        Get the data necessary to plot the relative residuals for this DRTResult: the frequencies, the relative residuals for the real parts of the impedances in percents, and the relative residuals for the imaginary parts of the impedances in percents.

        Returns
        -------
        Tuple[ndarray, ndarray, ndarray]
        """
        return (
            self.frequency,
            self.real_residual * 100,
            self.imaginary_residual * 100,
        )

    def get_scores(self) -> Dict[str, complex]:
        """
        Get the scores (BHT method) for the data set.
        The scores are represented as complex values where the real and imaginary parts have magnitudes ranging from 0.0 to 1.0.
        A consistent impedance spectrum should score high.

        Returns
        -------
        Dict[str, complex]
        """
        return self.scores

    def get_score_dataframe(self, latex_labels: bool = False) -> Optional[DataFrame]:
        """
        Get the scores (BHT) method for the data set as a pandas.DataFrame object that can be used to generate, e.g., a Markdown table.

        Parameters
        ----------
        latex_labels: bool = False
            Whether or not to use LaTeX macros in the labels.

        Returns
        -------
        Optional[DataFrame]
        """
        if not self.scores:
            return None
        return DataFrame.from_dict(
            {
                "Score": [
                    "Mean" if not latex_labels else r"$s_\mu$",
                    "Residuals, 1 sigma" if not latex_labels else r"$s_{1\sigma}$",
                    "Residuals, 2 sigma" if not latex_labels else r"$s_{2\sigma}$",
                    "Residuals, 3 sigma" if not latex_labels else r"$s_{3\sigma}$",
                    "Hellinger distance" if not latex_labels else r"$s_{\rm HD}$",
                    "Jensen-Shannon distance" if not latex_labels else r"$s_{\rm JSD}$",
                ],
                ("Real (%)" if not latex_labels else r"Real (\%)"): [
                    self.scores["mean"].real * 100,
                    self.scores["residuals_1sigma"].real * 100,
                    self.scores["residuals_2sigma"].real * 100,
                    self.scores["residuals_3sigma"].real * 100,
                    self.scores["hellinger_distance"].real * 100,
                    self.scores["jensen_shannon_distance"].real * 100,
                ],
                ("Imaginary (%)" if not latex_labels else r"Imaginary (\%)"): [
                    self.scores["mean"].imag * 100,
                    self.scores["residuals_1sigma"].imag * 100,
                    self.scores["residuals_2sigma"].imag * 100,
                    self.scores["residuals_3sigma"].imag * 100,
                    self.scores["hellinger_distance"].imag * 100,
                    self.scores["jensen_shannon_distance"].imag * 100,
                ],
            }
        )
