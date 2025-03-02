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

from time import time as _time
from typing import Dict
from uuid import uuid4 as _uuid4
import pyimpspec as _pyimpspec
from deareis.data import (
    DataSet,
    ZHITResult,
    ZHITSettings,
)
from deareis.enums import (
    ZHITSmoothing,
    ZHITInterpolation,
    ZHITWindow,
    ZHITRepresentation,
    zhit_smoothing_to_value as _zhit_smoothing_to_value,
    zhit_interpolation_to_value as _zhit_interpolation_to_value,
    zhit_window_to_value as _zhit_window_to_value,
    zhit_representation_to_value as _zhit_representation_to_value,
)


def perform_zhit(
    data: DataSet,
    settings: ZHITSettings,
    num_procs: int = -1,
) -> ZHITResult:
    """
    Wrapper for the `pyimpspec.perform_zhit` function.

    Performs a reconstruction of the modulus data of an impedance spectrum based on the phase data of that impedance spectrum using the Z-HIT algorithm described by Ehm et al. (2000).
    The results can be used to, e.g., check the validity of an impedance spectrum by detecting non-steady state issues like drift at low frequencies.
    See the references below for more information about the algorithm and its applications.
    The algorithm involves an offset adjustment of the reconstructed modulus data, which is done by fitting the reconstructed modulus data to the experimental modulus data in a frequency range that is unaffected (or minimally affected) by artifacts.
    This frequency range is typically around 1 Hz to 1000 Hz, which is why the default window function is a "boxcar" window that is centered around :math:`\\log{f} = 1.5` and has a width of 3.0.
    Multiple window functions are supported and a custom array of weights can also be used.

    References:

    - W. Ehm, H. Göhr, R. Kaus, B. Röseler, and C.A. Schiller, 2000, Acta Chimica Hungarica, 137 (2-3), 145-157.
    - W. Ehm, R. Kaus, C.A. Schiller, and W. Strunz, 2001, in "New Trends in Electrochemical Impedance Spectroscopy and Electrochemical Noise Analysis".
    - C.A. Schiller, F. Richter, E. Gülzow, and N. Wagner, 2001, 3, 374-378 (https://doi.org/10.1039/B007678N)


    Parameters
    ----------
    data: DataSet
        The data to be tested.

    settings: ZHITSettings
        The settings that determine how the Z-HIT computation is performed.

    num_procs: int, optional
        The maximum number of parallel processes to use when performing the computations.
        A value less than 1 will result in an attempt to automatically figure out a suitable value.
        Negative values are used as offsets relative to the number of cores detected.
        Applies only when there are multiple possible options for smoothing, interpolation, or window function.

    Returns
    -------
    ZHITResult
    """
    assert isinstance(data, _pyimpspec.DataSet), data
    assert isinstance(settings, ZHITSettings), settings

    result: _pyimpspec.ZHITResult = _pyimpspec.perform_zhit(
        data=data,
        smoothing=_zhit_smoothing_to_value[settings.smoothing],
        interpolation=_zhit_interpolation_to_value[settings.interpolation],
        window=_zhit_window_to_value[settings.window],
        num_points=settings.num_points,
        polynomial_order=settings.polynomial_order,
        num_iterations=settings.num_iterations,
        center=settings.window_center,
        width=settings.window_width,
        weights=None,
        admittance=_zhit_representation_to_value[settings.representation],
        num_procs=num_procs,
    )


    time: float = _time()
    mask: Dict[int, bool] = data.get_mask().copy()

    return ZHITResult(
        uuid=_uuid4().hex,
        timestamp=time,
        frequencies=result.frequencies,
        impedances=result.impedances,
        residuals=result.residuals,
        pseudo_chisqr=result.pseudo_chisqr,
        mask=mask,
        smoothing=result.smoothing,
        interpolation=result.interpolation,
        window=result.window,
        settings=settings,
    )
