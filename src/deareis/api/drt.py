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

from uuid import uuid4 as _uuid4
from time import time as _time
import pyimpspec as _pyimpspec
from pyimpspec import (
    DRTError,
)
from deareis.data import DataSet
from deareis.data.drt import (
    DRTResult,
    DRTSettings,
)
from deareis.enums import (
    DRTMethod,
    DRTMode,
    RBFShape,
    RBFType,
    drt_method_to_value as _drt_method_to_value,
    drt_mode_to_value as _drt_mode_to_value,
    rbf_shape_to_value as _rbf_shape_to_value,
    rbf_type_to_value as _rbf_type_to_value,
)


def calculate_drt(
    data: DataSet,
    settings: DRTSettings,
    num_procs: int = -1,
) -> DRTResult:
    """
    Wrapper for the `pyimpspec.calculate_drt` function.

    Calculates the distribution of relaxation times (DRT) for a given data set.

    References:

    - Kulikovsky, A., 2020, Phys. Chem. Chem. Phys., 22, 19131-19138 (https://doi.org/10.1039/D0CP02094J)
    - Wan, T. H., Saccoccio, M., Chen, C., and Ciucci, F., 2015, Electrochim. Acta, 184, 483-499 (https://doi.org/10.1016/j.electacta.2015.09.097).
    - Ciucci, F. and Chen, C., 2015, Electrochim. Acta, 167, 439-454 (https://doi.org/10.1016/j.electacta.2015.03.123)
    - Effat, M. B. and Ciucci, F., 2017, Electrochim. Acta, 247, 1117-1129 (https://doi.org/10.1016/j.electacta.2017.07.050)
    - Liu, J., Wan, T. H., and Ciucci, F., 2020, Electrochim. Acta, 357, 136864 (https://doi.org/10.1016/j.electacta.2020.136864)

    Parameters
    ----------
    data: DataSet
        The data set to use in the calculations.

    settings: DRTSettings
        The settings to use.

    num_procs: int = -1
        The maximum number of processes to use.
        A value below one results in using the total number of CPU cores present.
    """
    result: _pyimpspec.DRTResult = _pyimpspec.calculate_drt(
        data=data,
        method=_drt_method_to_value[settings.method],
        mode=_drt_mode_to_value[settings.mode],
        lambda_value=settings.lambda_value,
        rbf_type=_rbf_type_to_value[settings.rbf_type],
        derivative_order=settings.derivative_order,
        rbf_shape=_rbf_shape_to_value[settings.rbf_shape],
        shape_coeff=settings.shape_coeff,
        inductance=settings.inductance,
        credible_intervals=settings.credible_intervals,
        num_samples=settings.num_samples,
        num_attempts=settings.num_attempts,
        maximum_symmetry=settings.maximum_symmetry,
        num_procs=num_procs,
    )
    return DRTResult(
        _uuid4().hex,
        _time(),
        result.tau,
        result.gamma,
        result.frequency,
        result.impedance,
        result.real_residual,
        result.imaginary_residual,
        result.mean_gamma,
        result.lower_bound,
        result.upper_bound,
        result.imaginary_gamma,
        result.scores,
        result.chisqr,
        result.lambda_value,
        data.get_mask().copy(),
        settings,
    )
