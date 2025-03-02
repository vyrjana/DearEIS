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

A lower limit can be defined by appending a forward slash and then a numeric value (e.g. 'R{R=25e3/20e3}' sets 20 kiloohms as the lower limit). An upper limit can be defined in a similar way as a lower limit (e.g. 'R{R=25e3/20e3/30e3}' sets 30 kiloohms as the upper limit and 20 kiloohms as the lower limit). Unconstrained limits can be defined with 'inf' (e.g., 'R{R=2e3/inf/1e4}').

Some elements have multiple parameters and in that case multiple parameter definitions can be included in the CDC by separating the parameter definitions with commas (e.g. 'Q{Y=1e-5//1e-4,n=0.8F}').

A label can be defined by appending a colon and then a string of text (e.g. 'R{R=25e3//30e3:example}'). The parameter values need not be defined at all (i.e. 'R{:another example}' is also valid).
    """.strip(),
        "element_combo": """
This drop-down list can be used to select an element that you want to add as a node to the window below once the 'Add' button is clicked.
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
        "parse_cdc": """
Parse the circuit description code (CDC) defined in the input field to the left, generate the corresponding circuit element nodes in the editor below, and connect all of the nodes.
    """.strip(),
        "add_element": """
Add a node that represents the circuit element that is currently selected in the combo box to the left.
    """.strip(),
        "clear": """
Remove all of the circuit element nodes.
    """.strip(),
        "dummy_node": """
A dummy node that does not affect the impedance of the equivalent circuit model. It can be used as a junction to connect, e.g., two parallel connections together in series.
    """.strip(),
        "node_help": """
Circuits can be constructed either using the node editor to the right or by parsing a circuit description code (CDC).

Nodes corresponding to circuit elements can be added to the node editor by going to the 'Element' tab and clicking on a button corresponding to the desired type of circuit element. The node can then be moved around by clicking and holding onto the lower part of the node. One can also simply click and hold one of the buttons in the 'Elements' tab and then drag-and-drop the element directly to the desired position on the node editor.

Nodes can be connected by left-clicking on the input/output of one node, dragging to the output/input of another node, and releasing. Connections can be deleted by left-clicking a connection while holding down the Ctrl key.

Clicking on the upper part of a node brings up the ability to specify an optional label to the left of the node editor. There is also a 'Delete' button to the left of the node editor for deleting the selected node, but it is also possible to delete the selected node using the appropriate keyboard shortcut (Alt+Delete by default). The keyboard shortcut can also be used to delete multiple nodes that have been selected by clicking and holding to draw a box. Note that the 'WE' and 'CE+RE' nodes, which represent the terminals of the circuit, cannot be deleted.

The status of the validity of the circuit is shown below the node editor. Nodes that are highlighted in red have some kind of issue (e.g. a missing connection). Circuit description codes are generated and shown below the node editor (the upper CDC is a basic CDC while the one below it is an extended CDC that includes parameter values, labels, etc.).

The initial parameters of the elements included in the circuit can be altered in the 'Parameters' tab that appears at the top of the window once a valid circuit has been created. It is highly recommended to make use of this feature to provide suitable starting values since it will increase the chances of obtaining a good fit. It is also possible to perform a fit, use the fitted parameters (click on the 'Apply fitted values as initial values' in the 'Fitting' tab), adjust the initial values if necessary, and perform another fit. In some cases such as when using constant phase elements (CPEs), it may be a good idea to set, e.g., the 'n' parameter to be fixed parameters for the initial fit (i.e., treat each CPE as something close to an ideal capacitor), apply the fitted values as initial values, set the 'n' parameters to no longer be fixed parameters, and then perform another fit. The initial fit will then be simpler due to the reduced number of variables and is used to obtain approximate values. The second fit will then start with most of the variables fairly close to their optimal values.
    """.strip(),
    }
)
