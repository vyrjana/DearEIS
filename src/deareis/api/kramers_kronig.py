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

from time import time as _time
from uuid import uuid4 as _uuid4
import pyimpspec
from deareis.data import (
    DataSet,
    TestResult,
    TestSettings,
)
from deareis.enums import (
    Method,
    Mode,
    Test,
    method_to_value,
    test_to_value,
)


def perform_test(
    data: DataSet,
    settings: TestSettings,
    num_procs: int = -1,
) -> TestResult:
    """
    Wrapper for `pyimpspec.perform_test` function.

    Performs a linear Kramers-Kronig test as described by Boukamp (1995).
    The results can be used to check the validity of an impedance spectrum before performing equivalent circuit fitting.
    If the number of (RC) circuits is less than two, then a suitable number of (RC) circuits is determined using the procedure described by Schönleber et al. (2014) based on a criterion for the calculated mu-value (zero to one).
    A mu-value of one represents underfitting and a mu-value of zero represents overfitting.

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

    num_procs: int = -1
        The maximum number of parallel processes to use when performing a test.
        A value less than one results in using the number of cores returned by multiprocessing.cpu_count.
        Applies only to the `Mode.CNLS` test.

    Returns
    -------
    TestResult
    """
    assert isinstance(data, pyimpspec.DataSet), data
    assert type(settings) is TestSettings, settings
    assert (
        settings.mode != Mode.EXPLORATORY
    ), "Use pyimpspec.perform_exploratory_tests and pyimpspec.score_test_results to perform the tests, and then create a deareis.TestResult instance from your chosen pyimpspec.KramersKronigResult."
    assert type(num_procs) is int, num_procs
    result: pyimpspec.KramersKronigResult = pyimpspec.perform_test(
        data=data,
        test=test_to_value[settings.test],
        num_RC=settings.num_RC * (-1 if settings.mode == Mode.AUTO else 1),
        mu_criterion=settings.mu_criterion,
        add_capacitance=settings.add_capacitance,
        add_inductance=settings.add_inductance,
        method=method_to_value[settings.method],
        max_nfev=settings.max_nfev,
        num_procs=num_procs,
    )
    return TestResult(
        _uuid4().hex,
        _time(),
        result.circuit,
        result.num_RC,
        result.mu,
        result.pseudo_chisqr,
        result.frequency,
        result.impedance,
        result.real_residual,
        result.imaginary_residual,
        data.get_mask().copy(),
        settings,
    )
