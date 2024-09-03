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

from time import time as _time
from typing import (
    Dict,
    List,
    Optional,
    Tuple,
)
from uuid import uuid4 as _uuid4
from numpy import (
    integer as _integer,
    issubdtype as _issubdtype,
)
import pyimpspec as _pyimpspec
from deareis.data import (
    DataSet,
    KramersKronigResult,
    KramersKronigSettings,
    KramersKronigSuggestionSettings,
)
from deareis.enums import (
    CNLSMethod,
    KramersKronigTest,
    KramersKronigMode,
    KramersKronigRepresentation,
    cnls_method_to_value as _cnls_method_to_value,
    test_to_value as _test_to_value,
    test_representation_to_value as _test_representation_to_value,
)


def evaluate_log_F_ext(
    data: DataSet,
    settings: KramersKronigSettings,
    num_procs: int = -1,
) -> List[Tuple[float, List[KramersKronigResult], float]]:
    """
    Wrapper for the `pyimpspec.analysis.kramers_kronig.evaluate_log_F_ext` function.

    Parameters
    ----------
    data: DataSet
        The data set to be tested.

    settings: KramersKronigSettings
        The settings that determine how the test is performed.
        Note that only `Test.EXPLORATORY` is supported by this function.

    num_procs: int, optional
        See |perform_kramers_kronig_test| for details.

    Returns
    -------
    List[Tuple[float, List[KramersKronigResult], float]]
    """
    if not isinstance(settings, KramersKronigSettings):
        raise TypeError(f"Expected a KramersKronigSettings instance instead of {settings=}")

    admittance: bool = _test_representation_to_value[settings.representation]
    if not isinstance(admittance, bool):
        raise TypeError(f"Expected a boolean instead of {admittance=}")

    if not _pyimpspec.typing.helpers._is_integer(num_procs):
        raise TypeError(f"Expected an integer instead of {num_procs=}")

    evaluations: List[Tuple[float, List[_pyimpspec.KramersKronigResult], float]]
    evaluations = _pyimpspec.analysis.kramers_kronig.evaluate_log_F_ext(
        data=data,
        test=_test_to_value[settings.test],
        add_capacitance=settings.add_capacitance,
        add_inductance=settings.add_inductance,
        admittance=admittance,
        min_log_F_ext=settings.min_log_F_ext,
        max_log_F_ext=settings.max_log_F_ext,
        log_F_ext=settings.log_F_ext,
        num_F_ext_evaluations=settings.num_F_ext_evaluations,
        rapid_F_ext_evaluations=settings.rapid_F_ext_evaluations,
        cnls_method=_cnls_method_to_value[settings.cnls_method],
        max_nfev=settings.max_nfev,
        timeout=settings.timeout,
        num_procs=num_procs,
    )

    time: float = _time()
    mask: Dict[int, bool] = {i: False for i in range(0, len(data.get_frequencies(masked=None)))}
    mask.update(data.get_mask())


    converted_evaluations: List[Tuple[float, List[KramersKronigResult], float]] = []

    log_F_ext: float
    results: List[_pyimpspec.KramersKronigResult]
    statistic: float
    for log_F_ext, results, statistic in evaluations:
        converted_evaluations.append(
            (
                log_F_ext,
                list(
                    map(
                        lambda t: KramersKronigResult(
                            uuid=_uuid4().hex,
                            timestamp=time,
                            circuit=t.circuit,
                            pseudo_chisqr=t.pseudo_chisqr,
                            frequencies=t.frequencies,
                            impedances=t.impedances,
                            residuals=t.residuals,
                            mask=mask.copy(),
                            settings=settings,
                        ),
                        results,
                    )
                ),
                statistic,
            )
        )

    return converted_evaluations


def suggest_representation(
    suggestions: List[Tuple[KramersKronigResult, Dict[int, float], int, int]]
) -> Tuple[KramersKronigResult, Dict[int, float], int, int]:
    """
    Wrapper for the `pyimpspec.analysis.kramers_kronig.suggest_representation` function.

    Parameters
    ----------
    suggestions: List[Tuple[KramersKronigResult, Dict[int, float], int, int]]
        The return values of multiple |suggest_num_RC| calls.
    """
    return _pyimpspec.analysis.kramers_kronig.suggest_representation(suggestions)


def suggest_num_RC(
    tests: List[KramersKronigResult],
    settings: KramersKronigSuggestionSettings,
    **kwargs,
) -> Tuple[KramersKronigResult, Dict[int, float], int, int]:
    """
    Wrapper for the `pyimpspec.analysis.kramers_kronig.suggest_num_RC` function.

    Parameters
    ----------
    tests: List[|KramersKronigResult|]
        The test results to evaluate.

    settings: KramersKronigSuggestionSettings
        The settings that determine how the optimal number of RC elements is suggested.

    **kwargs

    Returns
    -------
    Tuple[|KramersKronigResult|, Dict[int, float], int, int]
    """
    if not isinstance(settings, KramersKronigSuggestionSettings):
        raise TypeError(
            f"Expected an KramersKronigSuggestionSettings instance instead of {settings=}"
        )

    result: _pyimpspec.KramersKronigResult
    scores: Dict[int, float]
    lower_limit: int
    upper_limit: int
    result, scores, lower_limit, upper_limit = (
        _pyimpspec.analysis.kramers_kronig.suggest_num_RC(
            tests=tests,
            methods=settings.methods,
            use_mean=settings.use_mean,
            use_ranking=settings.use_ranking,
            use_sum=settings.use_sum,
            lower_limit=settings.lower_limit,
            upper_limit=settings.upper_limit,
            limit_delta=settings.limit_delta,
            mu_criterion=settings.m1_mu_criterion,
            beta=settings.m1_beta,
            **kwargs,
        )
    )

    return (
        result,
        scores,
        lower_limit,
        upper_limit,
    )


def perform_kramers_kronig_test(
    data: DataSet,
    settings: KramersKronigSettings,
    num_procs: int = -1,
) -> KramersKronigResult:
    """
    Wrapper for the `pyimpspec.perform_kramers_kronig_test` function.

    Parameters
    ----------
    data: DataSet
        The data to be tested.

    settings: KramersKronigSettings
        The settings that determine how the test is performed.
        Note that `Test.EXPLORATORY` is not supported by this function.

    num_procs: int, optional
        The maximum number of parallel processes to use when performing a test.
        A value less than 1 will result in an attempt to automatically figure out a suitable value.
        Negative values are used as offsets relative to the number of cores detected.
        Applies only to the `KramersKronigMode.CNLS` test.

    Returns
    -------
    KramersKronigResult
    """
    if not isinstance(settings, KramersKronigSettings):
        raise TypeError(f"Expected a KramersKronigSettings instance instead of {settings=}")
    elif settings.mode == KramersKronigMode.EXPLORATORY:
        raise ValueError(f"Expected {settings.mode=} != KramersKronigMode.EXPLORATORY")

    if not _pyimpspec.typing.helpers._is_integer(num_procs):
        raise TypeError(f"Expected an integer instead of {num_procs=}")

    result: _pyimpspec.KramersKronigResult = _pyimpspec.perform_kramers_kronig_test(
        data=data,
        test=_test_to_value[settings.test],
        num_RC=settings.num_RC * (0 if settings.mode == KramersKronigMode.AUTO else 1),
        add_capacitance=settings.add_capacitance,
        add_inductance=settings.add_inductance,
        admittance=_test_representation_to_value[settings.representation],
        min_log_F_ext=settings.min_log_F_ext,
        max_log_F_ext=settings.max_log_F_ext,
        log_F_ext=settings.log_F_ext,
        num_F_ext_evaluations=settings.num_F_ext_evaluations,
        rapid_F_ext_evaluations=settings.rapid_F_ext_evaluations,
        cnls_method=_cnls_method_to_value[settings.cnls_method],
        max_nfev=settings.max_nfev,
        timeout=settings.timeout,
        num_procs=num_procs,
        # Num RC suggestion settings
        methods=settings.suggestion_settings.methods,
        use_mean=settings.suggestion_settings.use_mean,
        use_ranking=settings.suggestion_settings.use_ranking,
        use_sum=settings.suggestion_settings.use_sum,
        lower_limit=settings.suggestion_settings.lower_limit,
        upper_limit=settings.suggestion_settings.upper_limit,
        limit_delta=settings.suggestion_settings.limit_delta,
        mu_criterion=settings.suggestion_settings.m1_mu_criterion,
        beta=settings.suggestion_settings.m1_beta,
    )

    return KramersKronigResult(
        uuid=_uuid4().hex,
        timestamp=_time(),
        circuit=result.circuit,
        pseudo_chisqr=result.pseudo_chisqr,
        frequencies=result.frequencies,
        impedances=result.impedances,
        residuals=result.residuals,
        mask=data.get_mask().copy(),
        settings=settings,
    )


def perform_exploratory_kramers_kronig_tests(
    data: DataSet,
    settings: KramersKronigSettings,
    num_procs: int = -1,
) -> Tuple[List[KramersKronigResult], Tuple[KramersKronigResult, Dict[int, float], int, int]]:
    """
    Wrapper for the `pyimpspec.perform_exploratory_kramers_kronig_tests` function.

    Parameters
    ----------
    data: DataSet
        The data set to be tested.

    settings: KramersKronigSettings
        The settings that determine how the test is performed.
        Note that only `Test.EXPLORATORY` is supported by this function.

    num_procs: int, optional
        See perform_test for details.

    Returns
    -------
    Tuple[List[KramersKronigResult], Tuple[KramersKronigResult, Dict[int, float], int, int]]
    """
    if not isinstance(settings, KramersKronigSettings):
        raise TypeError(f"Expected a KramersKronigSettings instance instead of {settings=}")
    elif settings.mode != KramersKronigMode.EXPLORATORY:
        raise ValueError(f"Expected {settings.mode=} == KramersKronigMode.EXPLORATORY")
    elif settings.cnls_method == CNLSMethod.AUTO:
        raise ValueError(f"Expected {settings.cnls_method=} != CNLSMethod.AUTO")

    if not _pyimpspec.typing.helpers._is_integer(num_procs):
        raise TypeError(f"Expected an integer instead of {num_procs=}")

    results: List[_pyimpspec.KramersKronigResult]
    suggestion: Tuple[_pyimpspec.KramersKronigResult, Dict[int, float], int, int]
    results, suggestion = _pyimpspec.perform_exploratory_kramers_kronig_tests(
        data=data,
        test=_test_to_value[settings.test],
        add_capacitance=settings.add_capacitance,
        add_inductance=settings.add_inductance,
        admittance=_test_representation_to_value[settings.representation],
        min_log_F_ext=settings.min_log_F_ext,
        max_log_F_ext=settings.max_log_F_ext,
        log_F_ext=settings.log_F_ext,
        num_F_ext_evaluations=settings.num_F_ext_evaluations,
        rapid_F_ext_evaluations=settings.rapid_F_ext_evaluations,
        cnls_method=_cnls_method_to_value[settings.cnls_method],
        max_nfev=settings.max_nfev,
        timeout=settings.timeout,
        num_procs=num_procs,
        # Num RC suggestion settings
        methods=settings.suggestion_settings.methods,
        use_mean=settings.suggestion_settings.use_mean,
        use_ranking=settings.suggestion_settings.use_ranking,
        use_sum=settings.suggestion_settings.use_sum,
        lower_limit=settings.suggestion_settings.lower_limit,
        upper_limit=settings.suggestion_settings.upper_limit,
        limit_delta=settings.suggestion_settings.limit_delta,
        mu_criterion=settings.suggestion_settings.m1_mu_criterion,
        beta=settings.suggestion_settings.m1_beta,
    )

    time: float = _time()
    mask: Dict[int, bool] = data.get_mask()

    converted_results: List[KramersKronigResult] = list(
        map(
            lambda t: KramersKronigResult(
                uuid=_uuid4().hex,
                timestamp=time,
                circuit=t.circuit,
                pseudo_chisqr=t.pseudo_chisqr,
                frequencies=t.frequencies,
                impedances=t.impedances,
                residuals=t.residuals,
                mask=mask.copy(),
                settings=settings,
            ),
            results,
        )
    )

    test: _pyimpspec.KramersKronigResult
    scores: Dict[int, float]
    lower_limit: int
    upper_limit: int
    test, scores, lower_limit, upper_limit = suggestion

    return (
        converted_results,
        (
            min(converted_results, key=lambda t: abs(t.num_RC - test.num_RC)),
            scores,
            lower_limit,
            upper_limit,
        ),
    )
