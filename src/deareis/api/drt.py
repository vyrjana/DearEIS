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

from uuid import uuid4 as _uuid4
from time import time as _time
from typing import Dict
from numpy import array
import pyimpspec as _pyimpspec
from deareis.data import DataSet
from deareis.data.drt import (
    DRTResult,
    DRTSettings,
)
from deareis.enums import (
    CrossValidationMethod,
    DRTMethod,
    DRTMode,
    RBFShape,
    RBFType,
    TRNNLSLambdaMethod,
    cross_validation_method_to_value as _cross_validation_method_to_value,
    drt_method_to_value as _drt_method_to_value,
    drt_mode_to_value as _drt_mode_to_value,
    rbf_shape_to_value as _rbf_shape_to_value,
    rbf_type_to_value as _rbf_type_to_value,
    tr_nnls_lambda_method_to_value as _tr_nnls_lambda_method_to_value,
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

    - Kulikovsky, A., 2021, J. Electrochem. Soc., 168, 044512 (https://doi.org/10.1149/1945-7111/abf508)
    - Wan, T. H., Saccoccio, M., Chen, C., and Ciucci, F., 2015, Electrochim. Acta, 184, 483-499 (https://doi.org/10.1016/j.electacta.2015.09.097).
    - Ciucci, F. and Chen, C., 2015, Electrochim. Acta, 167, 439-454 (https://doi.org/10.1016/j.electacta.2015.03.123)
    - Effat, M. B. and Ciucci, F., 2017, Electrochim. Acta, 247, 1117-1129 (https://doi.org/10.1016/j.electacta.2017.07.050)
    - Liu, J., Wan, T. H., and Ciucci, F., 2020, Electrochim. Acta, 357, 136864 (https://doi.org/10.1016/j.electacta.2020.136864)
    - Boukamp, B.A., 2015, Electrochim. Acta, 154, 35-46, (https://doi.org/10.1016/j.electacta.2014.12.059)
    - Boukamp, B.A. and Rolle, A, 2017, Solid State Ionics, 302, 12-18 (https://doi.org/10.1016/j.ssi.2016.10.009)


    Parameters
    ----------
    data: DataSet
        The data set to use in the calculations.

    settings: DRTSettings
        The settings to use.

    num_procs: int, optional
        The maximum number of processes to use.
        A value less than 1 will result in an attempt to automatically figure out a suitable value.
        Negative values are used as offsets relative to the number of cores detected.
    """
    if settings.method == DRTMethod.MRQ_FIT:
        assert settings.fit is not None, "A fitted circuit has not been provided!"

    lambda_value: float = settings.lambda_value
    if settings.method is DRTMethod.TR_NNLS and settings.tr_nnls_lambda_method in (TRNNLSLambdaMethod.CUSTOM, TRNNLSLambdaMethod.LC):
        lambda_value = _tr_nnls_lambda_method_to_value[settings.tr_nnls_lambda_method]

    result: _pyimpspec.DRTResult = _pyimpspec.calculate_drt(
        data=data,
        method=_drt_method_to_value[settings.method],
        mode=_drt_mode_to_value[settings.mode],
        lambda_value=lambda_value,
        cross_validation=_cross_validation_method_to_value.get(settings.cross_validation_method, ""),
        rbf_type=_rbf_type_to_value[settings.rbf_type],
        derivative_order=settings.derivative_order,
        rbf_shape=_rbf_shape_to_value[settings.rbf_shape],
        shape_coeff=settings.shape_coeff,
        inductance=settings.inductance,
        credible_intervals=settings.credible_intervals,
        num_samples=settings.num_samples,
        num_attempts=settings.num_attempts,
        maximum_symmetry=settings.maximum_symmetry,
        circuit=settings.fit.circuit if settings.method == DRTMethod.MRQ_FIT else None,
        fit=settings.fit if settings.method == DRTMethod.MRQ_FIT else None,
        gaussian_width=settings.gaussian_width,
        timeout=settings.timeout,
        num_procs=num_procs,
    )
    real_gammas: _pyimpspec.Gammas = result.real_gammas if hasattr(result, "real_gammas") else result.gammas
    imaginary_gammas: _pyimpspec.Gammas = result.imaginary_gammas if hasattr(result, "imaginary_gammas") else array([])

    time: float = _time()
    mask: Dict[int, bool] = data.get_mask().copy()

    return DRTResult(
        uuid=_uuid4().hex,
        timestamp=time,
        time_constants=result.time_constants,
        real_gammas=real_gammas,
        imaginary_gammas=imaginary_gammas,
        frequencies=result.frequencies,
        impedances=result.impedances,
        residuals=result.residuals,
        mean_gammas=result.mean_gammas if hasattr(result, "mean_gammas") else array([]),
        lower_bounds=result.lower_bounds
        if hasattr(result, "lower_bounds")
        else array([]),
        upper_bounds=result.upper_bounds
        if hasattr(result, "upper_bounds")
        else array([]),
        scores=result.scores if hasattr(result, "scores") else {},
        pseudo_chisqr=result.pseudo_chisqr,
        lambda_value=result.lambda_value if hasattr(result, "lambda_value") else -1.0,
        mask=mask,
        settings=settings,
    )
