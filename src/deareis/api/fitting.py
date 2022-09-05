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
from typing import Optional
from uuid import uuid4 as _uuid4
from numpy import (
    integer as _integer,
    issubdtype as _issubdtype,
)
import pyimpspec as _pyimpspec
from pyimpspec import (
    Circuit,
    FittedParameter,
    FittingError,
)
from deareis.data import (
    DataSet,
    FitResult,
    FitSettings,
)
from deareis.enums import (
    CNLSMethod,
    Weight,
    value_to_cnls_method as _value_to_cnls_method,
    value_to_weight as _value_to_weight,
    cnls_method_to_value as _cnls_method_to_value,
    weight_to_value as _weight_to_value,
)


def fit_circuit(
    data: DataSet,
    settings: FitSettings,
    num_procs: int = -1,
) -> FitResult:
    """
    Wrapper for the `pyimpspec.fit_circuit` function.

    Fit a circuit to a data set.

    Parameters
    ----------
    data: DataSet
        The data set that the circuit will be fitted to.

    settings: FitSettings
        The settings that determine the circuit and how the fit is performed.

    num_procs: int = -1
        The maximum number of parallel processes to use when method is `CNLSMethod.AUTO` and/or weight is `Weight.AUTO`.

    Returns
    -------
    FitResult
    """
    assert isinstance(data, _pyimpspec.DataSet), data
    assert type(settings) is FitSettings, settings
    assert _issubdtype(type(num_procs), _integer), num_procs
    circuit: Circuit = _pyimpspec.parse_cdc(settings.cdc)
    result: _pyimpspec.FitResult = _pyimpspec.fit_circuit(
        circuit=circuit,
        data=data,
        method=_cnls_method_to_value.get(settings.method, "auto"),
        weight=_weight_to_value.get(settings.weight, "auto"),
        max_nfev=settings.max_nfev,
        num_procs=num_procs,
    )
    method: Optional[CNLSMethod] = _value_to_cnls_method.get(result.method)
    weight: Optional[Weight] = _value_to_weight.get(result.weight)
    assert method is not None
    assert weight is not None
    return FitResult(
        _uuid4().hex,
        _time(),
        result.circuit,
        result.parameters,
        result.frequency,
        result.impedance,
        result.real_residual,
        result.imaginary_residual,
        data.get_mask(),
        result.minimizer_result.chisqr,
        result.minimizer_result.redchi,
        result.minimizer_result.aic,
        result.minimizer_result.bic,
        result.minimizer_result.ndata,
        result.minimizer_result.nfree,
        result.minimizer_result.nfev,
        method,
        weight,
        settings,
    )
