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
        "noise_pct": """
The standard deviation of the added noise expressed as a percentage of the absolute value of the impedance.
    """.strip(),
        "element": """
An element in the circuit. Elements marked with an asterisk, *, are nested within the subcircuit of a container element (e.g., a transmission line model (Tlm)). Hovering over the name will show a tooltip that includes information about which container element and the specific subcircuit.
    """.strip(),
        "parameter": """
A parameter in the element. Hovering over the name will show a tooltip with the parameter's unit if one has been specified.
    """.strip(),
        "parameter_value": """
The value of the parameter. Hovering over the value will show a tooltip that also contains the parameter's unit.
    """.strip(),
        "remove": """
Remove the current simulation result.
    """.strip(),
        "load_as_data_set": """
Load the current simulation as a data set.
    """.strip(),
    },
)
