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
        "drt_checkbox": """
Whether or not this DRT analysis result is included in the plot.
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
        "collapse_expand_sidebar": """
Collapse/expand the sidebar.
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
        "export_plot": """
Export the current plot using matplotlib.
    """.strip(),
        "export_units": """
The units used for the width and height.
    """.strip(),
        "export_width": """
The width of the figure.
    """.strip(),
        "export_height": """
The height of the figure.
    """.strip(),
        "export_dpi": """
The number of dots (or points) per inch.
    """.strip(),
        "export_result": """
The final dimensions.
    """.strip(),
        "export_preview": """
The maximum limit for either dimension in the preview. For example, if the limit is set to 1024 and the figure is 1920 px by 1080 px, then the preview will be 1024 px by 576 px.

Note that using a limit may cause the preview to look slightly or even very different compared to the final saved figure but helps to maintain acceptable performance.
However, choosing to not use a limit may cause the program to become unresponsive and use a lot of memory if the figure dimensions are very large.
    """.strip(),
        "export_min_x": """
The minimum limit for the x-axis.
    """.strip(),
        "export_max_x": """
The maximum limit for the x-axis.
    """.strip(),
        "export_min_y": """
The minimum limit for the y-axis.
    """.strip(),
        "export_max_y": """
The maximum limit for the y-axis.
    """.strip(),
        "export_title": """
Show the figure title.
    """.strip(),
        "export_legend": """
Show the figure legend.
    """.strip(),
        "export_grid": """
Show the grid.
    """.strip(),
        "export_tight": """
Use a tight layout that reduces the size of the margins.
    """.strip(),
        "export_file": """
Save the figure as a file.
    """.strip(),
        "export_num_per_decade": """
The number of points per decade in lines.
    """.strip(),
        "export_extension": """
The default extension to use when exporting a plot.
    """.strip(),
        "clear_registry": """
NOTE! Clearing the texture registry can cause DearEIS to crash on some systems. The cause is not known for certain at the moment but it may be a bug in the GUI framework and/or a certain GPU driver.

If enabled, then the texture registry is cleared to free memory. Disabling will cause memory to not be freed until DearEIS is closed, which may be an issue if a lot of plot previews are generated during a single session.
    """.strip(),
        "disable_preview": """
NOTE! If the texture registry is not allowed to be cleared, then DearEIS will not be able to free the memory used by the generated plot previews. The plot previews can be disabled completely with this setting to avoid such a memory leak.
    """.strip(),
    }
)
