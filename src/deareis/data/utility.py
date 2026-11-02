# DearEIS is licensed under the GPLv3 or later (https://www.gnu.org/licenses/gpl-3.0.html).
# Copyright 2026 DearEIS developers
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

from typing import Dict
from numpy import (
    argmin,
    float64,
    isclose,
)
from numpy.typing import NDArray
from deareis.data import DataSet


def deserialize_mask(
    mask: Dict[str, bool],
    frequencies: NDArray[float64],
    data: DataSet,
) -> Dict[int, bool]:
    """
    mask:
        The serialized mask of an analysis result.
        It may not have been serialized (correctly) at some point in the past.
        If the data set's mask has changed, then there could be issues when
        deserializing the analysis result.

    frequencies:
        The serialized frequencies of an analysis result.
        Only contains values that were not masked in the corresponding
        data set at the time of performing the analysis.

    data:
        The data set that was originally analyzed.
        Its mask may have changed after the analysis was performed.

    The tasks of this function are to:
    - Convert the type of the mask's keys from str to int
      (i.e., serialized to in-memory)
    - Correct/update the mask in case there was an issue with the old
      serialized mask.
    """
    new_mask: Dict[int, bool] = {}

    i: int
    f: float64
    for i, f in enumerate(data.get_frequencies(masked=None)):
        if str(i) in mask:
            new_mask[i] = mask[str(i)]
            continue

        j: int = int(argmin(abs(frequencies - f)))
        new_mask[i] = not isclose(f, frequencies[j])

    return new_mask
