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


circuit_editor = SimpleNamespace(
    **{
        "cdc_input": """
Circuit description code (CDC) is a text-based representation of a circuit. The inputted value will be validated and then recreated below using nodes. Note that not all circuits can be defined using a CDC.

---- Basic syntax ----
Elements are represented with one or more letters (e.g. 'R' is a resistor). Elements defined using the basic syntax will have the default initial values for parameters and lower/upper limits for those parameters.

Two or more elements that are connected in series are placed one after another and enclosed with square brackets (e.g. '[RC]' is a resistor and a capacitor connected in series).

Two or more elements that are connected in parallel are placed one after another and enclosed with parentheses (e.g. '(RC)' is a resistor and a capacitor connected in parallel).

Series and parallel connections can be nested inside other series and parallel connections (e.g. "R([RW]C)" is the CDC for the Randles circuit).


---- Extended syntax ----
DearEIS supports an extended syntax for CDCs and thus values, lower/upper limits, and labels can also be defined for each element in a CDC.

A resistor with an initial value of 25 kiloohms can de defined as 'R{R=25e3}' or 'R{R=2.5e4}'. Note that numeric values must use periods/dots as decimal separators and no thousands separators are allowed at all.

The initial value can be defined as a fixed value by appending the numeric value with the lower- or upper-case letter 'f' (i.e. 'R{R=25e3f}' or 'R{R=25e3F}').

A lower limit can be defined by appending a forward slash and then a numeric value (e.g. 'R{R=25e3/20e3}' sets 20 kiloohms as the lower limit).

An upper limit can be defined in a similar way as a lower limit (e.g. 'R{R=25e3/20e3/30e3}' sets 30 kiloohms as the upper limit and 20 kiloohms as the lower limit). The lower limit can also be omitted (e.g. 'R{R=25e3//30e3}' sets 30 kiloohms as the upper limit while leaving the lower boundary unlimited).

Some elements have multiple parameters and in that case multiple parameter definitions can be included in the CDC by separating the parameter definitions with commas (e.g. 'Q{Y=1e-5//1e-4,n=0.8F}').

A label can be defined by appending a colon and then a string of text (e.g. 'R{R=25e3//30e3:example}'). The parameter values need not be defined at all (i.e. 'R{:another example}' is also valid).
    """.strip(),
        "element_combo": """
This drop-down list can be used to select an element that you want to add as a node to the window below once the 'Add' button is clicked.

The 'Add dummy' button adds a dummy node that can be used as a junction point, which may be necessary when representing certain circuits using nodes.
    """.strip(),
        "basic_cdc": """
This is the basic CDC output generated based on the nodes and connections in the window above.

This output may be accepted by another program that accepts a CDC as input. However, some programs may use different identifiers for some elements. Thus, this output may require adjustments for it to be accepted by some other programs.
    """.strip(),
        "extended_cdc": """
This is the extended CDC output generated based on the nodes and connections in the window above.

This output is unlikely to be accepted by another program that accepts a CDC as input.
    """.strip(),
        "status": """
Potential issues with the circuit, which is defined using nodes and connections in the window above, are presented here.
    """.strip(),
    }
)
