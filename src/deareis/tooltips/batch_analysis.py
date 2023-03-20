# DearEIS is licensed under the GPLv3 or later (https://www.gnu.org/licenses/gpl-3.0.html).
# Copyright 2023 DearEIS developers
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

from types import SimpleNamespace


batch_analysis = SimpleNamespace(
    **{
        "checkbox": """
Data sets with ticked checkboxes are included in the batch analysis.
    """.strip(),
        "select": """
Select or unselect all of the data sets listed below.
    """.strip(),
        "filter": """
The data sets listed below can be filtered by typing in a substring into the input to the left. Multiple substrings can be separated with commas. A hyphen can be used as a prefix that acts as a logical not (i.e., exclude anything matching the substring).
    """.strip(),
    }
)

