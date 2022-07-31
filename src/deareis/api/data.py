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

from typing import List, Optional
import pyimpspec
from pyimpspec.data import (
    UnsupportedFileFormat,
)
from deareis.api._utility import _copy_docstring
from deareis.data import (
    DataSet,
)


@_copy_docstring(pyimpspec.parse_data)
def parse_data(
    path: str,
    file_format: Optional[str] = None,
    **kwargs,
) -> List[DataSet]:
    return list(
        map(
            lambda _: DataSet.from_dict(_.to_dict()),
            pyimpspec.parse_data(path, file_format, **kwargs),
        )
    )
