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
)
from uuid import uuid4 as _uuid4
from numpy import (
    integer as _integer,
    issubdtype as _issubdtype,
)
import pyimpspec as _pyimpspec
from deareis.data import (
    DataSet,
    TestResult,
    TestSettings,
)
from deareis.enums import (
    CNLSMethod,
    TestMode,
    Test,
    cnls_method_to_value as _cnls_method_to_value,
    test_to_value as _test_to_value,
)


def perform_test(
    data: DataSet,
    settings: TestSettings,
    num_procs: int = 0,
) -> TestResult:
    """
    Wrapper for the `pyimpspec.perform_test` function.

    Performs a linear Kramers-Kronig test as described by Boukamp (1995).
    The results can be used to check the validity of an impedance spectrum before performing equivalent circuit fitting.
    If the number of (RC) circuits is less than two, then a suitable number of (RC) circuits is determined using the procedure described by Schönleber et al. (2014) based on a criterion for the calculated |mu| (0.0 to 1.0).
    A |mu| of 1.0 represents underfitting and a |mu| of 0.0 represents overfitting.

    References:

    - B.A. Boukamp, 1995, J. Electrochem. Soc., 142, 1885-1894 (https://doi.org/10.1149/1.2044210)
    - M. Schönleber, D. Klotz, and E. Ivers-Tiffée, 2014, Electrochim. Acta, 131, 20-27 (https://doi.org/10.1016/j.electacta.2014.01.034)

    Parameters
    ----------
    data: DataSet
        The data to be tested.

    settings: TestSettings
        The settings that determine how the test is performed.
        Note that `Test.EXPLORATORY` is not supported by this function.

    num_procs: int, optional
        The maximum number of parallel processes to use when performing a test.
        A value less than 1 will result in an attempt to automatically figure out a suitable value.
        Applies only to the `TestMode.CNLS` test.

    Returns
    -------
    TestResult
    """
    assert isinstance(data, _pyimpspec.DataSet), data
    assert type(settings) is TestSettings, settings
    assert (
        settings.mode != TestMode.EXPLORATORY
    ), "Use deareis.perform_exploratory_tests to perform the tests!"
    assert _issubdtype(type(num_procs), _integer), num_procs
    result: _pyimpspec.TestResult = _pyimpspec.perform_test(
        data=data,
        test=_test_to_value[settings.test],
        num_RC=settings.num_RC * (-1 if settings.mode == TestMode.AUTO else 1),
        mu_criterion=settings.mu_criterion,
        add_capacitance=settings.add_capacitance,
        add_inductance=settings.add_inductance,
        method=_cnls_method_to_value[settings.method],
        max_nfev=settings.max_nfev,
        num_procs=num_procs,
    )
    return TestResult(
        uuid=_uuid4().hex,
        timestamp=_time(),
        circuit=result.circuit,
        num_RC=result.num_RC,
        mu=result.mu,
        pseudo_chisqr=result.pseudo_chisqr,
        frequencies=result.frequencies,
        impedances=result.impedances,
        residuals=result.residuals,
        mask=data.get_mask().copy(),
        settings=settings,
    )


def perform_exploratory_tests(
    data: DataSet,
    settings: TestSettings,
    num_procs: int = 0,
) -> List[TestResult]:
    """
    Wrapper for the `pyimpspec.perform_exploratory_tests` function.

    Performs a batch of linear Kramers-Kronig tests, which are then scored and sorted from best to worst before they are returned.

    Parameters
    ----------
    data: DataSet
        The data set to be tested.

    settings: TestSettings
        The settings that determine how the test is performed.
        Note that only `Test.EXPLORATORY` is supported by this function.

    num_procs: int, optional
        See perform_test for details.

    Returns
    -------
    List[TestResult]
    """
    assert (
        settings.mode == TestMode.EXPLORATORY
    ), "Use deareis.perform_test to perform the test!"
    assert settings.method != CNLSMethod.AUTO
    num_RCs: List[int] = list(range(1, settings.num_RC + 1))
    assert len(num_RCs) > 0, "Invalid settings!"
    results: List[_pyimpspec.TestResult] = _pyimpspec.perform_exploratory_tests(
        data=data,
        test=_test_to_value[settings.test],
        num_RCs=num_RCs,
        mu_criterion=settings.mu_criterion,
        add_capacitance=settings.add_capacitance,
        add_inductance=settings.add_inductance,
        method=_cnls_method_to_value[settings.method],
        max_nfev=settings.max_nfev,
        num_procs=num_procs,
    )
    time: float = _time()
    mask: Dict[int, bool] = data.get_mask()
    return list(
        map(
            lambda _: TestResult(
                uuid=_uuid4().hex,
                timestamp=time,
                circuit=_.circuit,
                num_RC=_.num_RC,
                mu=_.mu,
                pseudo_chisqr=_.pseudo_chisqr,
                frequencies=_.frequencies,
                impedances=_.impedances,
                residuals=_.residuals,
                mask=mask.copy(),
                settings=settings,
            ),
            results,
        )
    )
