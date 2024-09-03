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
from functools import cached_property
from typing import (
    Callable,
    Dict,
    List,
    Optional,
    Tuple,
)
from numpy import (
    angle,
    array,
    mean,
    sum as array_sum,
    logical_and,
    nan,
    std,
)
import pyimpspec
from pyimpspec import (
    Capacitor,
    Circuit,
    ComplexImpedances,
    ComplexResiduals,
    Element,
    Frequencies,
    Impedances,
    Inductor,
    KramersKronigAdmittanceRC,
    KramersKronigRC,
    Parallel,
    Phases,
    Residuals,
    Resistor,
    Series,
    TimeConstants,
)
from pyimpspec.analysis.utility import _interpolate
from deareis.enums import (
    CNLSMethod,
    KramersKronigTest,
    KramersKronigMode,
    KramersKronigRepresentation,
    test_to_value,
)
from deareis.utility import (
    format_timestamp,
    rename_dict_entry,
)
from deareis.data import DataSet
from pyimpspec.typing.helpers import _is_integer


VERSION: int = 3


def _parse_suggestion_settings_v3(state: dict) -> dict:
    return state


@dataclass(frozen=True)
class KramersKronigSuggestionSettings:
    """
    Singleton that is used to maintain the exploratory window's settings while
    DearEIS is running.

    methods: List[int]
        The 1-based identifiers of suggestion methods:
        - 1: mu-criterion (modified)
        - 2: norm of fitted variables
        - 3: norm of curvatures
        - 4: number of sign changes in curvatures
        - 5: mean distance between sign changes in curvatures
        - 6: log(sum(tau_k/var_k)) inflection point

    use_mean: bool
        Use the mean of the number of RC elements suggested by different methods.

    use_ranking: bool
        Let the different methods rank the number of RC elements, assign scores, and pick the highest-scoring number of RC elements.

    use_sum: bool
        Add the score from each method together and pick the highest-scoring number of RC elements.

    lower_limit: int
        If greater than zero, then this value is used as the lower limit instead of trying to estimate the lower limit algorithmically.

    upper_limit: int
        If greater than zero, then this value is used as the upper limit instead of trying to estimate the upper limit algorithmically.

    limit_delta: int
        The upper limit can also be defined as the lower limit plus some delta.

    m1_mu_criterion: float
        The threshold value used in the method described by Schönleber et al. (2014).

    m1_beta: float
        The exponent that affects the penalty imposed based on the distance between |mu|-criterion and |mu| in the score calculated as part of the modified |mu|-criterion method.
    """

    methods: List[int]
    use_mean: bool
    use_ranking: bool
    use_sum: bool
    lower_limit: int
    upper_limit: int
    limit_delta: int
    m1_mu_criterion: float
    m1_beta: float

    @classmethod
    def from_dict(Class, dictionary: dict):
        assert type(dictionary) is dict, type(dictionary)
        assert "version" in dictionary

        version: int = dictionary["version"]
        del dictionary["version"]

        assert version >= 3 and version <= VERSION, (
            version,
            VERSION,
        )

        parsers: Dict[int, Callable] = {
            3: _parse_suggestion_settings_v3,
        }
        assert version in parsers, f"{version=} not in {parsers.keys()=}"

        v: int
        p: Callable
        for v, p in parsers.items():
            if v < version:
                continue

            dictionary = p(dictionary)

        assert "methods" in dictionary
        assert "use_mean" in dictionary
        assert "use_ranking" in dictionary
        assert "use_sum" in dictionary
        assert "lower_limit" in dictionary
        assert "upper_limit" in dictionary
        assert "limit_delta" in dictionary
        assert "m1_mu_criterion" in dictionary
        assert "m1_beta" in dictionary
        
        assert [
            dictionary["use_mean"],
            dictionary["use_ranking"],
            dictionary["use_sum"],
        ].count(True) <= 1

        return Class(**dictionary)

    def to_dict(self) -> dict:
        return {
            "version": VERSION,
            "methods": self.methods,
            "use_mean": self.use_mean,
            "use_ranking": self.use_ranking,
            "use_sum": self.use_sum,
            "lower_limit": self.lower_limit,
            "upper_limit": self.upper_limit,
            "limit_delta": self.limit_delta,
            "m1_mu_criterion": self.m1_mu_criterion,
            "m1_beta": self.m1_beta,
        }


def _parse_settings_v3(dictionary: dict) -> dict:
    return dictionary


def _parse_settings_v2(dictionary: dict) -> dict:
    if "suggestion_settings" not in dictionary:
        dictionary["suggestion_settings"] = KramersKronigSuggestionSettings(
            methods=[1],
            use_mean=False,
            use_ranking=False,
            use_sum=False,
            lower_limit=0,
            upper_limit=0,
            limit_delta=0,
            m1_mu_criterion=dictionary.pop("mu_criterion"),
            m1_beta=0.75,
        ).to_dict()

    if "min_log_F_ext" not in dictionary:
        dictionary["min_log_F_ext"] = -1.0

    if "max_log_F_ext" not in dictionary:
        dictionary["max_log_F_ext"] = 1.0

    if "log_F_ext" not in dictionary:
        dictionary["log_F_ext"] = 0.0

    if "num_F_ext_evaluations" not in dictionary:
        dictionary["num_F_ext_evaluations"] = 0

    if "rapid_F_ext_evaluations" not in dictionary:
        dictionary["rapid_F_ext_evaluations"] = True

    if "representation" not in dictionary:
        if "admittance" in dictionary:
            dictionary["representation"] = (
                KramersKronigRepresentation.ADMITTANCE
                if dictionary.pop("admittance")
                else KramersKronigRepresentation.IMPEDANCE
            )
        else:
            dictionary["representation"] = KramersKronigRepresentation.IMPEDANCE

    if "cnls_method" not in dictionary:
        if "method" in dictionary:
            dictionary["cnls_method"] = dictionary.pop("method")
        else:
            dictionary["cnls_method"] = CNLSMethod.LEASTSQ

    dictionary["timeout"] = 60

    return dictionary


def _parse_settings_v1(dictionary: dict) -> dict:
    return dictionary


@dataclass(frozen=True)
class KramersKronigSettings:
    """
    A class to store the settings used to perform a Kramers-Kronig test.

    Parameters
    ----------
    test: KramersKronigTest
        The type of test to perform: complex, real, imaginary, or CNLS.
        See pyimpspec and its documentation for details about the different types of tests.

    mode: KramersKronigMode
        How to perform the test: automatic, exploratory, or manual.
        The automatic mode uses one or more methods to determine a suitable number of RC circuits.
        The exploratory mode is similar to the automatic mode except the user is allowed to choose which of the results to accept, which can help with avoiding false positives or false negatives.
        The manual mode requires the user to pick the number of RC circuits.

    representation: KramersKronigRepresentation
        Use a specific representation of the immittance data for validation or automatically select one.

    add_capacitance: bool
        Add a capacitance in series or in parallel when validating impedance or admittance data, respectively.

    add_inductance: bool
        Add an inductance in series or in parallel when validating impedance or admittance data, respectively.

    num_RC: int
        The (maximum) number of RC circuits.

    min_log_F_ext: float
        The lower limit for log Fext values to evaluate during optimization.

    max_log_F_ext: float
        The upper limit for log Fext values to evaluate during optimization.

    log_F_ext: float
        The log Fext value to use if the number of Fext evluations is set to zero.

    num_F_ext_evaluations: int
        The number of evaluations to perform when automatically determining the number of decades to extend the range of time constants in both directions.

    rapid_F_ext_evaluations: bool
        Reduce the time spent optimizing Fext by evaluating a narrower range of RC elements.

    cnls_method: CNLSMethod
        The iterative method to use if the CNLS test is chosen.

    max_nfev: int
        The maximum number of function evaluations to use if the CNLS test is chosen.

    timeout: int
        The number of seconds to wait for a single fit to be performed.

    suggestion_settings: KramersKronigSuggestionSettings
        The settings used to define how to suggest the optimum number of RC elements.
    """

    test: KramersKronigTest
    mode: KramersKronigMode
    representation: KramersKronigRepresentation
    add_capacitance: bool
    add_inductance: bool
    # Manual mode
    num_RC: int
    # Optimum range of time constants
    min_log_F_ext: float
    max_log_F_ext: float
    log_F_ext: float
    num_F_ext_evaluations: int
    rapid_F_ext_evaluations: bool
    # CNLS-specific
    cnls_method: CNLSMethod
    max_nfev: int
    timeout: int
    suggestion_settings: KramersKronigSuggestionSettings

    def __repr__(self) -> str:
        return f"KramersKronigSettings ({hex(id(self))})"

    @classmethod
    def from_dict(Class, dictionary: dict) -> "KramersKronigSettings":
        """
        Create an instance from a dictionary.
        """
        assert type(dictionary) is dict, type(dictionary)
        assert "version" in dictionary

        version: int = dictionary["version"]
        del dictionary["version"]
        assert version >= 1 and version <= VERSION, (
            version,
            VERSION,
        )
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

        assert "test" in dictionary
        assert "mode" in dictionary
        assert "representation" in dictionary
        assert "add_capacitance" in dictionary
        assert "add_inductance" in dictionary
        assert "min_log_F_ext" in dictionary
        assert "max_log_F_ext" in dictionary
        assert "log_F_ext" in dictionary
        assert "num_F_ext_evaluations" in dictionary
        assert "rapid_F_ext_evaluations" in dictionary
        assert "num_RC" in dictionary
        assert "cnls_method" in dictionary
        assert "max_nfev" in dictionary
        assert "timeout" in dictionary
        assert "mu_criterion" not in dictionary
        assert "suggestion_settings" in dictionary

        dictionary["test"] = KramersKronigTest(dictionary["test"])
        dictionary["mode"] = KramersKronigMode(dictionary["mode"])
        dictionary["representation"] = KramersKronigRepresentation(dictionary["representation"])
        dictionary["cnls_method"] = CNLSMethod(dictionary["cnls_method"])
        dictionary["suggestion_settings"] = KramersKronigSuggestionSettings.from_dict(dictionary["suggestion_settings"])

        return Class(**dictionary)

    def to_dict(self) -> dict:
        """
        Return a dictionary that can be used to recreate an instance.
        """
        return {
            "version": VERSION,
            "test": self.test,
            "mode": self.mode,
            "representation": self.representation,
            "add_capacitance": self.add_capacitance,
            "add_inductance": self.add_inductance,
            # Manual mode
            "num_RC": self.num_RC,
            # Optimum range of time constants
            "min_log_F_ext": self.min_log_F_ext,
            "max_log_F_ext": self.max_log_F_ext,
            "log_F_ext": self.log_F_ext,
            "num_F_ext_evaluations": self.num_F_ext_evaluations,
            "rapid_F_ext_evaluations": self.rapid_F_ext_evaluations,
            # CNLS-specific
            "cnls_method": self.cnls_method,
            "max_nfev": self.max_nfev,
            "timeout": self.timeout,
            # Num RC suggestion settings
            "suggestion_settings": self.suggestion_settings.to_dict(),
        }


def _parse_result_v3(dictionary: dict) -> dict:
    return dictionary


def _parse_result_v2(dictionary: dict) -> dict:
    if "mu" in dictionary:
        del dictionary["mu"]

    if "num_RC" in dictionary:
        del dictionary["num_RC"]

    if "chisqr" in dictionary:
        dictionary["pseudo_chisqr"] = dictionary["chisqr"]
        del dictionary["chisqr"]

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

    return dictionary


@dataclass
class KramersKronigResult:
    """
    A class containing the result of a Kramers-Kronig test.

    Parameters
    ----------
    uuid: str
        The universally unique identifier assigned to this result.

    timestamp: float
        The Unix time (in seconds) for when the test was performed.

    circuit: Circuit
        The final, fitted circuit.

    pseudo_chisqr: float
        The calculated |pseudo chi-squared| (eq. 14 in Boukamp, 1995).

    frequencies: Frequencies
        The frequencies used to perform the test.

    impedances: ComplexImpedances
        The complex impedances of the fitted circuit at each of the frequencies.

    residuals: ComplexResiduals
        The residuals of the real and the imaginary parts of the fit.

    mask: Dict[int, bool]
        The mask that was applied to the DataSet that was tested.

    settings: KramersKronigSettings
        The settings that were used to perform the test.
    """

    uuid: str
    timestamp: float
    circuit: Circuit
    pseudo_chisqr: float
    frequencies: Frequencies
    impedances: ComplexImpedances
    residuals: ComplexResiduals
    mask: Dict[int, bool]
    settings: KramersKronigSettings

    def __post_init__(self):
        self._cached_frequencies: Dict[int, Frequencies] = {}
        self._cached_impedances: Dict[int, ComplexImpedances] = {}

    def __hash__(self) -> int:
        return int(self.uuid, 16)

    def __repr__(self) -> str:
        return f"KramersKronigResult ({self.label}, {hex(id(self))})"

    @cached_property
    def test(self) -> str:
        return test_to_value[self.settings.test]

    @cached_property
    def num_RC(self) -> int:
        return self.get_num_RC()

    @cached_property
    def admittance(self) -> bool:
        return self.was_tested_on_admittance()

    @cached_property
    def label(self) -> str:
        return self.get_label()

    @cached_property
    def time_constants(self) -> TimeConstants:
        return self.get_time_constants()

    @cached_property
    def log_F_ext(self) -> float:
        return self.get_log_F_ext()

    @cached_property
    def series_resistance(self) -> float:
        return self.get_series_resistance()

    @cached_property
    def series_capacitance(self) -> float:
        return self.get_series_capacitance()

    @cached_property
    def series_inductance(self) -> float:
        return self.get_series_inductance()

    @cached_property
    def parallel_resistance(self) -> float:
        return self.get_parallel_resistance()

    @cached_property
    def parallel_capacitance(self) -> float:
        return self.get_parallel_capacitance()

    @cached_property
    def parallel_inductance(self) -> float:
        return self.get_parallel_inductance()

    def get_label(self) -> str:
        """
        Generate a label for the result.

        Returns
        -------
        str
        """
        label: str = f"#(RC)={self.num_RC}"

        if self.settings.add_capacitance:
            label += ", C"
            if self.settings.add_inductance:
                label += "+L"
        elif self.settings.add_inductance:
            label += ", L"

        if self.admittance:
            label += ", Y"
        else:
            label += ", Z"

        label += f", log Fext={self.log_F_ext:.3f}"

        timestamp: str = format_timestamp(self.timestamp)

        return f"{label} ({timestamp})"

    @cached_property
    def residuals_means(self) -> Tuple[float, float]:
        _, real, imag = self.get_residuals_data()

        return (
            mean(real),
            mean(imag),
        )

    @cached_property
    def residuals_sd(self) -> Tuple[float, float]:
        _, real, imag = self.get_residuals_data()

        return (
            std(real, ddof=1),
            std(imag, ddof=1),
        )

    @cached_property
    def residuals_within_1sd(self) -> Tuple[float, float]:
        return self.get_residuals_within(n=1)

    @cached_property
    def residuals_within_2sd(self) -> Tuple[float, float]:
        return self.get_residuals_within(n=2)

    @cached_property
    def residuals_within_3sd(self) -> Tuple[float, float]:
        return self.get_residuals_within(n=3)

    @cached_property
    def lilliefors(self) -> Tuple[float, float]:
        return self.perform_lilliefors_test()

    @cached_property
    def shapiro_wilk(self) -> Tuple[float, float]:
        return self.perform_shapiro_wilk_test()

    @cached_property
    def kolmogorov_smirnov(self) -> Tuple[float, float]:
        return self.perform_kolmogorov_smirnov_test()

    @classmethod
    def from_dict(
        Class,
        dictionary: dict,
        data: Optional[DataSet] = None,
    ) -> "KramersKronigResult":
        """
        Create an instance from a dictionary.

        Parameters
        ----------
        dictionary: dict
            The dictionary to turn into a KramersKronigResult object.

        data: Optional[DataSet], optional
            The DataSet object that this result is for.

        Returns
        -------
        KramersKronigResult
        """
        assert isinstance(dictionary, dict), dict
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
        assert "circuit" in dictionary
        assert "pseudo_chisqr" in dictionary
        assert "frequencies" in dictionary
        assert "real_residuals" in dictionary
        assert "imaginary_residuals" in dictionary
        assert "settings" in dictionary
        dictionary["circuit"] = pyimpspec.parse_cdc(dictionary["circuit"])
        dictionary["frequencies"] = array(dictionary["frequencies"])
        dictionary["settings"] = KramersKronigSettings.from_dict(dictionary["settings"])

        mask: Dict[str, bool] = dictionary["mask"]
        if data is not None:
            mask = {
                i: mask.get(str(i), False)
                for i in range(0, len(data.get_frequencies(masked=None)))
            }
        else:
            mask = {
                i: mask.get(str(i), False)
                for i in range(0, len(dictionary["frequencies"]))
            }
        dictionary["mask"] = mask

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

        return Class(**dictionary)

    def to_dict(self, session: bool = True) -> dict:
        """
        Return a dictionary that can be used to recreate an instance.

        Parameters
        ----------
        session: bool, optional
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
            "pseudo_chisqr": self.pseudo_chisqr,
            "frequencies": list(self.frequencies),
            "real_residuals": list(self.residuals.real),
            "imaginary_residuals": list(self.residuals.imag),
            "mask": self.mask.copy(),
            "settings": self.settings.to_dict(),
        }

        if session:
            # Used during a session for plots since time would otherwise
            # have to be spent recalculating the impedances when switching
            # between results.
            dictionary.update(
                {
                    "real_impedances": list(self.impedances.real),
                    "imaginary_impedances": list(self.impedances.imag),
                }
            )

        if not session:
            # This helps to reduce the file sizes of projects.
            dictionary["mask"] = {
                k: v for k, v in dictionary["mask"].items() if v is True
            }

        return dictionary

    def get_frequencies(self, num_per_decade: int = -1) -> Frequencies:
        """
        Get an array of frequencies within the range of tested frequencies.

        Parameters
        ----------
        num_per_decade: int, optional
            If the value is greater than zero, then logarithmically distributed frequencies will be generated within the range of tested frequencies.

        Returns
        -------
        Frequencies
        """
        if not _is_integer(num_per_decade):
            raise TypeError(f"Expected an integer instead of {num_per_decade=}")

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
        Get the complex impedances produced by the fitted circuit within the range of tested frequencies.

        Parameters
        ----------
        num_per_decade: int, optional
            If the value is greater than zero, then logarithmically distributed frequencies will be generated within the range of tested frequencies and used to calculate the impedance produced by the fitted circuit.

        Returns
        -------
        Frequencies
        """
        if not _is_integer(num_per_decade):
            raise TypeError(f"Expected an integer instead of {num_per_decade=}")

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
            If the value is greater than zero, then logarithmically distributed frequencies will be generated within the range of tested frequencies and used to calculate the impedance produced by the fitted circuit.

        Returns
        -------
        Tuple[Impedances, Impedances]
        """
        if not _is_integer(num_per_decade):
            raise TypeError(f"Expected an integer instead of {num_per_decade=}")

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
        self,
        num_per_decade: int = -1,
    ) -> Tuple[Frequencies, Impedances, Phases]:
        """
        Get the data required to plot the results as a Bode plot (Mode(Z) and -Phase(Z) vs f).

        Parameters
        ----------
        num_per_decade: int, optional
            If the value is greater than zero, then logarithmically distributed frequencies will be generated within the range of tested frequencies and used to calculate the impedance produced by the fitted circuit.

        Returns
        -------
        Tuple[Frequencies, Impedances, Phases]
        """
        if not _is_integer(num_per_decade):
            raise TypeError(f"Expected an integer instead of {num_per_decade=}")

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

    def get_residuals_within(self, n: int) -> Tuple[float, float]:
        results = []
        _, real, imag = self.get_residuals_data()

        for samples in (real, imag):
            sample_mean = mean(samples)
            sample_sd = std(samples, ddof=1)
            results.append(
                array_sum(
                    logical_and(
                        samples < sample_mean + (n + 1) * sample_sd,
                        samples > sample_mean - (n + 1) * sample_sd,
                    )
                )
                / len(samples)
                * 100
            )

        return tuple(results)


# Dynamically copy methods from pyimpspec's KramersKronigResult class
for attribute in (
    "get_estimated_percent_noise",
    "get_log_F_ext",
    "get_num_RC",
    "get_parallel_capacitance",
    "get_parallel_inductance",
    "get_parallel_resistance",
    "get_residuals_data",
    "get_series_capacitance",
    "get_series_inductance",
    "get_series_resistance",
    "get_time_constants",
    "perform_kolmogorov_smirnov_test",
    "perform_lilliefors_test",
    "perform_shapiro_wilk_test",
    "_calculate_residuals_statistics",
    "to_statistics_dataframe",
    "was_tested_on_admittance",
):
    setattr(
        KramersKronigResult,
        attribute,
        getattr(pyimpspec.KramersKronigResult, attribute),
    )
KramersKronigResult.to_statistics_dataframe = (
    pyimpspec.KramersKronigResult.to_statistics_dataframe
)
KramersKronigResult.get_estimated_percent_noise = (
    pyimpspec.KramersKronigResult.get_estimated_percent_noise
)
