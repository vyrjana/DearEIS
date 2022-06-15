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


plotting = SimpleNamespace(
    **{
        "dataset_checkbox": """
Whether or not this data set is included in the plot.
    """.strip(),
        "dataset_label": """
The label assigned to this data set in the 'Data sets' tab.
    """.strip(),
        "test_checkbox": """
Whether or not this test result is included in the plot.
    """.strip(),
        "fit_checkbox": """
Whether or not this fit result is included in the plot.
    """.strip(),
        "simulation_checkbox": """
Whether or not this simulation result is included in the plot.
    """.strip(),
        "filter": """
Hide items that do not contain the string of text, which is entered into the input field to the right, in their labels. Test and fit results are considered to also contain the labels of their corresponding data sets.
    """.strip(),
        "select_all": """
Add all of the items listed above to the plot.
    """.strip(),
        "unselect_all": """
Remove all of the items listed above from the plot.
    """.strip(),
        "create": """
Create a new plot.
    """.strip(),
        "remove": """
Remove the current plot.
    """.strip(),
        "copy_appearance": """
Copy color, marker, and line settings from another plot and apply them to the active items.
    """.strip(),
        "item_type": """
The type of item.
    """.strip(),
        "label": """
The label used in the legend of the plot to identify the corresponding item.

This value defaults to the label of the item but it can be overridden by typing in a new label. Overriding the label with only blank space(s) will result in no entry in the legend but the data will still plotted.
    """.strip(),
        "appearance": """
The settings that define the appearance of the item in the plot.
    """.strip(),
        "position": """
Change the order in which items are added to the plot. This affects both the order of the items in the legend as well as the order in which markers and/or lines are plotted.

The two buttons can be used to adjust the position of the corresponding item.
    """.strip(),
        "collapse_sidebar": """
Collapse the sidebar.
    """.strip(),
        "expand_sidebar": """
Expand the sidebar.
    """.strip(),
        "copy_appearance_toggle": """
Toggle this to set whether or not this series should copy settings from the chosen source.
    """.strip(),
        "copy_appearance_labels": """
Toggle whether or not labels should be copied.
    """.strip(),
        "copy_appearance_colors": """
Toggle whether or not colors should be copied.
    """.strip(),
        "copy_appearance_markers": """
Toggle whether or not markers should be copied.
    """.strip(),
        "copy_appearance_lines": """
Toggle whether or not lines should be copied.
    """.strip(),
    }
)
