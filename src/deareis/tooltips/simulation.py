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

from types import SimpleNamespace


simulation = SimpleNamespace(
    **{
        "cdc": """
The equivalent circuit to simulate. A circuit description code (CDC) can be typed in to define the equivalent circuit. Alternatively, the circuit editor can be used to construct the equivalent circuit.
    """.strip(),
        "min_freq": """
The minimum frequency to simulate.
    """.strip(),
        "max_freq": """
The maximum frequency to simulate.
    """.strip(),
        "per_decade": """
The number of frequencies per decade in the frequency range.
    """.strip(),
        "element": """
An element in the circuit.
    """.strip(),
        "parameter": """
A parameter in the element.
    """.strip(),
        "parameter_value": """
The value of the parameter.
    """.strip(),
        "remove": """
Remove the current simulation result.
    """.strip(),
    }
)
