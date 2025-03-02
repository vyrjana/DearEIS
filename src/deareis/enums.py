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

from enum import (
    IntEnum,
    auto,
)
from typing import (
    Dict,
    List,
    Optional,
)


class Context(IntEnum):
    PROGRAM = auto()
    PROJECT = auto()
    OVERVIEW_TAB = auto()
    DATA_SETS_TAB = auto()
    KRAMERS_KRONIG_TAB = auto()
    ZHIT_TAB = auto()
    DRT_TAB = auto()
    FITTING_TAB = auto()
    SIMULATION_TAB = auto()
    PLOTTING_TAB = auto()


class Action(IntEnum):
    CANCEL = auto()
    CUSTOM = auto()
    # Program-level
    NEW_PROJECT = auto()
    LOAD_PROJECT = auto()
    EXIT = auto()
    NEXT_PROGRAM_TAB = auto()
    PREVIOUS_PROGRAM_TAB = auto()
    SELECT_HOME_TAB = auto()
    SHOW_HELP_ABOUT = auto()
    SHOW_HELP_LICENSES = auto()
    SHOW_SETTINGS_APPEARANCE = auto()
    SHOW_SETTINGS_DEFAULTS = auto()
    SHOW_SETTINGS_KEYBINDINGS = auto()
    SHOW_COMMAND_PALETTE = auto()
    SHOW_DATA_SET_PALETTE = auto()
    SHOW_RESULT_PALETTE = auto()
    SHOW_CHANGELOG = auto()
    CHECK_UPDATES = auto()

    # Project-level
    SAVE_PROJECT = auto()
    SAVE_PROJECT_AS = auto()
    CLOSE_PROJECT = auto()
    UNDO = auto()
    REDO = auto()
    NEXT_PROJECT_TAB = auto()
    PREVIOUS_PROJECT_TAB = auto()
    SELECT_DATA_SETS_TAB = auto()
    SELECT_DRT_TAB = auto()
    SELECT_FITTING_TAB = auto()
    SELECT_KRAMERS_KRONIG_TAB = auto()
    SELECT_OVERVIEW_TAB = auto()
    SELECT_PLOTTING_TAB = auto()
    SELECT_SIMULATION_TAB = auto()
    SELECT_ZHIT_TAB = auto()
    NEXT_PLOT_TAB = auto()
    PREVIOUS_PLOT_TAB = auto()

    # Project-level: multiple tabs
    BATCH_PERFORM_ACTION = auto()
    PERFORM_ACTION = auto()
    # - Load data set
    # - Perform test
    # - Perform fit
    # - Perform simulation
    # - Create plot
    DELETE_RESULT = auto()
    # - Data set
    # - Test result
    # - Z-HIT result
    # - DRT result
    # - Fit result
    # - Simulation result
    # - Plot
    NEXT_PRIMARY_RESULT = auto()
    PREVIOUS_PRIMARY_RESULT = auto()
    # - Data set
    # - Plot
    NEXT_SECONDARY_RESULT = auto()
    PREVIOUS_SECONDARY_RESULT = auto()
    # - Test result
    # - Z-HIT result
    # - DRT result
    # - Fit result
    # - Simulation result
    # - Plot type
    APPLY_SETTINGS = auto()
    # - Kramers-Kronig tab
    # - Z-HIT tab
    # - DRT tab
    # - Fitting tab
    # - Simulation tab
    APPLY_MASK = auto()
    # - Kramers-Kronig tab
    LOAD_TEST_AS_DATA_SET = auto()
    # - DRT tab
    # - Fitting tab
    SHOW_ENLARGED_NYQUIST = auto()
    SHOW_ENLARGED_BODE = auto()
    SHOW_ENLARGED_RESIDUALS = auto()
    SHOW_ENLARGED_DRT = auto()
    SHOW_ENLARGED_IMPEDANCE = auto()
    SHOW_CIRCUIT_EDITOR = auto()
    # - Fitting tab
    # - Simulation tab
    COPY_DRT_DATA = auto()
    COPY_IMPEDANCE_DATA = auto()
    COPY_NYQUIST_DATA = auto()
    COPY_BODE_DATA = auto()
    COPY_RESIDUALS_DATA = auto()
    COPY_OUTPUT = auto()
    ADJUST_PARAMETERS = auto()  # Deprecated as of version 5.0.0
    # - Fit output
    # - Simulation output
    LOAD_SIMULATION_AS_DATA_SET = auto()
    LOAD_ZHIT_AS_DATA_SET = auto()

    # Project-level: data sets tab
    AVERAGE_DATA_SETS = auto()
    COPY_DATA_SET_MASK = auto()
    INTERPOLATE_POINTS = auto()
    PARALLEL_IMPEDANCE = auto()
    SUBTRACT_IMPEDANCE = auto()
    TOGGLE_DATA_POINTS = auto()

    # Project-level: Z-HIT tab
    PREVIEW_ZHIT_WEIGHTS = auto()

    # Project-level: plotting tab
    SELECT_ALL_PLOT_SERIES = auto()
    UNSELECT_ALL_PLOT_SERIES = auto()
    COPY_PLOT_APPEARANCE = auto()
    COPY_PLOT_DATA = auto()
    EXPAND_COLLAPSE_SIDEBAR = auto()
    EXPORT_PLOT = auto()
    DUPLICATE_PLOT = auto()


action_contexts: Dict[Action, List[Context]] = {
    Action.CANCEL: [],
    Action.CUSTOM: [],
    Action.NEW_PROJECT: [Context.PROGRAM],
    Action.LOAD_PROJECT: [Context.PROGRAM],
    Action.EXIT: [Context.PROGRAM],
    Action.NEXT_PROGRAM_TAB: [Context.PROGRAM],
    Action.PREVIOUS_PROGRAM_TAB: [Context.PROGRAM],
    Action.SELECT_HOME_TAB: [Context.PROGRAM],
    Action.SHOW_HELP_ABOUT: [Context.PROGRAM],
    Action.SHOW_HELP_LICENSES: [Context.PROGRAM],
    Action.SHOW_SETTINGS_APPEARANCE: [Context.PROGRAM],
    Action.SHOW_SETTINGS_DEFAULTS: [Context.PROGRAM],
    Action.SHOW_SETTINGS_KEYBINDINGS: [Context.PROGRAM],
    Action.SHOW_COMMAND_PALETTE: [Context.PROGRAM],
    Action.SHOW_DATA_SET_PALETTE: [Context.PROJECT],
    Action.SHOW_RESULT_PALETTE: [Context.PROJECT],
    Action.SHOW_CHANGELOG: [Context.PROGRAM],
    Action.CHECK_UPDATES: [Context.PROGRAM],
    Action.SAVE_PROJECT: [Context.PROJECT],
    Action.SAVE_PROJECT_AS: [Context.PROJECT],
    Action.CLOSE_PROJECT: [Context.PROJECT],
    Action.UNDO: [Context.PROJECT],
    Action.REDO: [Context.PROJECT],
    Action.NEXT_PROJECT_TAB: [Context.PROJECT],
    Action.PREVIOUS_PROJECT_TAB: [Context.PROJECT],
    Action.NEXT_PLOT_TAB: [
        Context.DATA_SETS_TAB,
        Context.KRAMERS_KRONIG_TAB,
        Context.ZHIT_TAB,
        Context.DRT_TAB,
        Context.FITTING_TAB,
        Context.SIMULATION_TAB,
        Context.PLOTTING_TAB,
    ],
    Action.PREVIOUS_PLOT_TAB: [
        Context.DATA_SETS_TAB,
        Context.KRAMERS_KRONIG_TAB,
        Context.ZHIT_TAB,
        Context.DRT_TAB,
        Context.FITTING_TAB,
        Context.SIMULATION_TAB,
        Context.PLOTTING_TAB,
    ],
    Action.SELECT_DATA_SETS_TAB: [Context.PROJECT],
    Action.SELECT_DRT_TAB: [Context.PROJECT],
    Action.SELECT_FITTING_TAB: [Context.PROJECT],
    Action.SELECT_KRAMERS_KRONIG_TAB: [Context.PROJECT],
    Action.SELECT_OVERVIEW_TAB: [Context.PROJECT],
    Action.SELECT_PLOTTING_TAB: [Context.PROJECT],
    Action.SELECT_SIMULATION_TAB: [Context.PROJECT],
    Action.SELECT_ZHIT_TAB: [Context.PROJECT],
    Action.PERFORM_ACTION: [
        Context.DATA_SETS_TAB,
        Context.KRAMERS_KRONIG_TAB,
        Context.ZHIT_TAB,
        Context.DRT_TAB,
        Context.FITTING_TAB,
        Context.SIMULATION_TAB,
        Context.PLOTTING_TAB,
    ],
    Action.BATCH_PERFORM_ACTION: [
        Context.KRAMERS_KRONIG_TAB,
        Context.ZHIT_TAB,
        Context.DRT_TAB,
        Context.FITTING_TAB,
    ],
    Action.DELETE_RESULT: [
        Context.DATA_SETS_TAB,
        Context.KRAMERS_KRONIG_TAB,
        Context.ZHIT_TAB,
        Context.DRT_TAB,
        Context.FITTING_TAB,
        Context.SIMULATION_TAB,
        Context.PLOTTING_TAB,
    ],
    Action.NEXT_PRIMARY_RESULT: [
        Context.DATA_SETS_TAB,
        Context.KRAMERS_KRONIG_TAB,
        Context.ZHIT_TAB,
        Context.DRT_TAB,
        Context.FITTING_TAB,
        Context.SIMULATION_TAB,
        Context.PLOTTING_TAB,
    ],
    Action.PREVIOUS_PRIMARY_RESULT: [
        Context.DATA_SETS_TAB,
        Context.KRAMERS_KRONIG_TAB,
        Context.ZHIT_TAB,
        Context.DRT_TAB,
        Context.FITTING_TAB,
        Context.SIMULATION_TAB,
        Context.PLOTTING_TAB,
    ],
    Action.NEXT_SECONDARY_RESULT: [
        Context.KRAMERS_KRONIG_TAB,
        Context.ZHIT_TAB,
        Context.DRT_TAB,
        Context.FITTING_TAB,
        Context.SIMULATION_TAB,
        Context.PLOTTING_TAB,
    ],
    Action.PREVIOUS_SECONDARY_RESULT: [
        Context.KRAMERS_KRONIG_TAB,
        Context.ZHIT_TAB,
        Context.DRT_TAB,
        Context.FITTING_TAB,
        Context.SIMULATION_TAB,
        Context.PLOTTING_TAB,
    ],
    Action.APPLY_SETTINGS: [
        Context.KRAMERS_KRONIG_TAB,
        Context.ZHIT_TAB,
        Context.DRT_TAB,
        Context.FITTING_TAB,
        Context.SIMULATION_TAB,
    ],
    Action.APPLY_MASK: [
        Context.KRAMERS_KRONIG_TAB,
        Context.ZHIT_TAB,
        Context.DRT_TAB,
        Context.FITTING_TAB,
    ],
    Action.SHOW_ENLARGED_IMPEDANCE: [
        Context.DATA_SETS_TAB,
        Context.KRAMERS_KRONIG_TAB,
        Context.ZHIT_TAB,
        Context.DRT_TAB,
        Context.FITTING_TAB,
        Context.SIMULATION_TAB,
    ],
    Action.SHOW_ENLARGED_DRT: [
        Context.DRT_TAB,
    ],
    Action.SHOW_ENLARGED_NYQUIST: [
        Context.DATA_SETS_TAB,
        Context.KRAMERS_KRONIG_TAB,
        Context.ZHIT_TAB,
        Context.DRT_TAB,
        Context.FITTING_TAB,
        Context.SIMULATION_TAB,
    ],
    Action.SHOW_ENLARGED_BODE: [
        Context.DATA_SETS_TAB,
        Context.KRAMERS_KRONIG_TAB,
        Context.ZHIT_TAB,
        Context.DRT_TAB,
        Context.FITTING_TAB,
        Context.SIMULATION_TAB,
    ],
    Action.SHOW_ENLARGED_RESIDUALS: [
        Context.KRAMERS_KRONIG_TAB,
        Context.ZHIT_TAB,
        Context.DRT_TAB,
        Context.FITTING_TAB,
    ],
    Action.SHOW_CIRCUIT_EDITOR: [
        Context.FITTING_TAB,
        Context.SIMULATION_TAB,
    ],
    Action.COPY_DRT_DATA: [
        Context.DRT_TAB,
    ],
    Action.COPY_IMPEDANCE_DATA: [
        Context.DRT_TAB,
    ],
    Action.COPY_NYQUIST_DATA: [
        Context.KRAMERS_KRONIG_TAB,
        Context.FITTING_TAB,
        Context.SIMULATION_TAB,
    ],
    Action.COPY_BODE_DATA: [
        Context.KRAMERS_KRONIG_TAB,
        Context.FITTING_TAB,
        Context.SIMULATION_TAB,
    ],
    Action.COPY_RESIDUALS_DATA: [
        Context.KRAMERS_KRONIG_TAB,
        Context.DRT_TAB,
        Context.FITTING_TAB,
    ],
    Action.COPY_OUTPUT: [
        Context.DRT_TAB,
        Context.FITTING_TAB,
        Context.SIMULATION_TAB,
    ],
    Action.LOAD_TEST_AS_DATA_SET: [Context.KRAMERS_KRONIG_TAB],
    Action.LOAD_SIMULATION_AS_DATA_SET: [Context.SIMULATION_TAB],
    Action.LOAD_ZHIT_AS_DATA_SET: [Context.ZHIT_TAB],
    Action.AVERAGE_DATA_SETS: [Context.DATA_SETS_TAB],
    Action.TOGGLE_DATA_POINTS: [Context.DATA_SETS_TAB],
    Action.COPY_DATA_SET_MASK: [Context.DATA_SETS_TAB],
    Action.INTERPOLATE_POINTS: [Context.DATA_SETS_TAB],
    Action.PARALLEL_IMPEDANCE: [Context.DATA_SETS_TAB],
    Action.SUBTRACT_IMPEDANCE: [Context.DATA_SETS_TAB],
    Action.SELECT_ALL_PLOT_SERIES: [Context.PLOTTING_TAB],
    Action.UNSELECT_ALL_PLOT_SERIES: [Context.PLOTTING_TAB],
    Action.COPY_PLOT_APPEARANCE: [Context.PLOTTING_TAB],
    Action.COPY_PLOT_DATA: [Context.PLOTTING_TAB],
    Action.EXPAND_COLLAPSE_SIDEBAR: [Context.PLOTTING_TAB],
    Action.EXPORT_PLOT: [Context.PLOTTING_TAB],
    Action.PREVIEW_ZHIT_WEIGHTS: [Context.ZHIT_TAB],
    Action.DUPLICATE_PLOT: [Context.PLOTTING_TAB],
    Action.ADJUST_PARAMETERS: [Context.FITTING_TAB, Context.SIMULATION_TAB],
}


action_to_string: Dict[Action, str] = {
    Action.CANCEL: "cancel",
    Action.CUSTOM: "custom",
    Action.APPLY_MASK: "apply-mask",
    Action.APPLY_SETTINGS: "apply-settings",
    Action.AVERAGE_DATA_SETS: "average-data-sets",
    Action.CHECK_UPDATES: "check-updates",
    Action.CLOSE_PROJECT: "close-project",
    Action.COPY_BODE_DATA: "copy-bode-data",
    Action.COPY_DATA_SET_MASK: "copy-data-set-mask",
    Action.COPY_DRT_DATA: "copy-drt-data",
    Action.COPY_IMPEDANCE_DATA: "copy-impedance-data",
    Action.COPY_NYQUIST_DATA: "copy-nyquist-data",
    Action.COPY_OUTPUT: "copy-output",
    Action.COPY_PLOT_APPEARANCE: "copy-plot-appearance",
    Action.COPY_PLOT_DATA: "copy-plot-data",
    Action.COPY_RESIDUALS_DATA: "copy-residuals-data",
    Action.DELETE_RESULT: "delete-result",
    Action.EXIT: "exit-program",
    Action.EXPAND_COLLAPSE_SIDEBAR: "expand-collapse-sidebar",
    Action.EXPORT_PLOT: "export-plot",
    Action.INTERPOLATE_POINTS: "interpolate-points",
    Action.LOAD_TEST_AS_DATA_SET: "load-test-as-data-set",
    Action.LOAD_PROJECT: "load-project",
    Action.LOAD_SIMULATION_AS_DATA_SET: "load-simulation-as-data-set",
    Action.LOAD_ZHIT_AS_DATA_SET: "load-zhit-as-data-set",
    Action.NEW_PROJECT: "new-project",
    Action.NEXT_PRIMARY_RESULT: "next-primary-result",
    Action.NEXT_PROGRAM_TAB: "next-program-tab",
    Action.NEXT_PROJECT_TAB: "next-project-tab",
    Action.NEXT_SECONDARY_RESULT: "next-secondary-result",
    Action.BATCH_PERFORM_ACTION: "batch-perform-action",
    Action.PERFORM_ACTION: "perform-action",
    Action.PREVIOUS_PRIMARY_RESULT: "previous-primary-result",
    Action.PREVIOUS_PROGRAM_TAB: "previous-program-tab",
    Action.PREVIOUS_PROJECT_TAB: "previous-project-tab",
    Action.PREVIOUS_SECONDARY_RESULT: "previous-secondary-result",
    Action.REDO: "redo",
    Action.SAVE_PROJECT: "save-project",
    Action.SAVE_PROJECT_AS: "save-project-as",
    Action.SELECT_ALL_PLOT_SERIES: "select-all-plot-series",
    Action.SELECT_DATA_SETS_TAB: "select-data-sets-tab",
    Action.SELECT_DRT_TAB: "select-drt-tab",
    Action.SELECT_FITTING_TAB: "select-fitting-tab",
    Action.SELECT_HOME_TAB: "select-home-tab",
    Action.SELECT_KRAMERS_KRONIG_TAB: "select-kramers-kronig-tab",
    Action.SELECT_ZHIT_TAB: "select-zhit-tab",
    Action.SELECT_OVERVIEW_TAB: "select-overview-tab",
    Action.SELECT_PLOTTING_TAB: "select-plotting-tab",
    Action.SELECT_SIMULATION_TAB: "select-simulation-tab",
    Action.SHOW_CHANGELOG: "show-changelog",
    Action.SHOW_CIRCUIT_EDITOR: "show-circuit-editor",
    Action.SHOW_COMMAND_PALETTE: "show-command-palette",
    Action.SHOW_DATA_SET_PALETTE: "show-data-set-palette",
    Action.SHOW_RESULT_PALETTE: "show-result-palette",
    Action.SHOW_ENLARGED_BODE: "show-enlarged-bode",
    Action.SHOW_ENLARGED_DRT: "show-enlarged-drt",
    Action.SHOW_ENLARGED_IMPEDANCE: "show-enlarged-impedance",
    Action.SHOW_ENLARGED_NYQUIST: "show-enlarged-nyquist",
    Action.SHOW_ENLARGED_RESIDUALS: "show-enlarged-residuals",
    Action.SHOW_HELP_ABOUT: "show-help-about",
    Action.SHOW_HELP_LICENSES: "show-help-licenses",
    Action.SHOW_SETTINGS_APPEARANCE: "show-settings-appearance",
    Action.SHOW_SETTINGS_DEFAULTS: "show-settings-defaults",
    Action.SHOW_SETTINGS_KEYBINDINGS: "show-settings-keybindings",
    Action.PARALLEL_IMPEDANCE: "parallel-impedance",
    Action.SUBTRACT_IMPEDANCE: "subtract-impedance",
    Action.TOGGLE_DATA_POINTS: "toggle-data-points",
    Action.UNDO: "undo",
    Action.UNSELECT_ALL_PLOT_SERIES: "unselect-all-plot-series",
    Action.PREVIEW_ZHIT_WEIGHTS: "preview-zhit-weights",
    Action.DUPLICATE_PLOT: "duplicate-plot",
    Action.ADJUST_PARAMETERS: "adjust-parameters",
    Action.NEXT_PLOT_TAB: "next-plot-tab",
    Action.PREVIOUS_PLOT_TAB: "previous-plot-tab",
}
string_to_action: Dict[str, Action] = {v: k for k, v in action_to_string.items()}
# Check that there are no duplicate keys
assert len(action_to_string) == len(set(action_to_string.values())) and len(
    action_to_string
) == len(string_to_action), "Duplicate action string keys detected!"


action_descriptions: Dict[Action, str] = {
    Action.CANCEL: """
Cancel and close the current modal window.
""".strip(),
    Action.CUSTOM: "",
    Action.NEW_PROJECT: """
Create a new project.
""".strip(),
    Action.LOAD_PROJECT: """
Select project(s) to load.
""".strip(),
    Action.EXIT: """
Close the program.
""".strip(),
    Action.NEXT_PROGRAM_TAB: """
Go to the next project.
""".strip(),
    Action.PREVIOUS_PROGRAM_TAB: """
Go to the previous project.
""".strip(),
    Action.SELECT_HOME_TAB: """
Go to the 'Home' tab.
""".strip(),
    Action.SHOW_HELP_ABOUT: """
Show the 'About' window.
""".strip(),
    Action.SHOW_HELP_LICENSES: """
Show the 'Licenses' window.
""".strip(),
    Action.SHOW_SETTINGS_APPEARANCE: """
Show the 'Settings - appearance' window.
""".strip(),
    Action.SHOW_SETTINGS_DEFAULTS: """
Show the 'Settings - defaults' window.
""".strip(),
    Action.SHOW_SETTINGS_KEYBINDINGS: """
Show the 'Settings - keybindings' window.
""".strip(),
    Action.SHOW_COMMAND_PALETTE: """
Show the command palette, which can be used as an alternative to other keybindings for performing actions.
""".strip(),
    Action.SHOW_DATA_SET_PALETTE: """
Show the data set palette, which can be used to switch between data sets.
""".strip(),
    Action.SHOW_RESULT_PALETTE: """
Show the result palette, which can be used to switch between, e.g., Kramers-Kronig test results.
""".strip(),
    Action.SHOW_CHANGELOG: """
Show the changelog.
""".strip(),
    Action.CHECK_UPDATES: """
Check for updates.
""".strip(),
    Action.SAVE_PROJECT: """
Save the current project.
""".strip(),
    Action.SAVE_PROJECT_AS: """
Save the current project as a new file.
""".strip(),
    Action.CLOSE_PROJECT: """
Close the current project.
""".strip(),
    Action.UNDO: """
Undo the latest action.
""".strip(),
    Action.REDO: """
Redo the latest action.
""".strip(),
    Action.NEXT_PROJECT_TAB: """
Go to the next project tab.
""".strip(),
    Action.PREVIOUS_PROJECT_TAB: """
Go to the previous project tab.
""".strip(),
    Action.SELECT_DATA_SETS_TAB: """
Go to the 'Data sets' tab.
""".strip(),
    Action.SELECT_DRT_TAB: """
Go to the 'DRT analysis' tab.
""".strip(),
    Action.SELECT_FITTING_TAB: """
Go to the 'Fitting' tab.
""".strip(),
    Action.SELECT_KRAMERS_KRONIG_TAB: """
Go to the 'Kramers-Kronig' tab.
""".strip(),
    Action.SELECT_ZHIT_TAB: """
Go to the 'Z-HIT analysis' tab.
""".strip(),
    Action.SELECT_OVERVIEW_TAB: """
Go to the 'Overview' tab.
""".strip(),
    Action.SELECT_PLOTTING_TAB: """
Go to the 'Plotting' tab.
""".strip(),
    Action.SELECT_SIMULATION_TAB: """
Go to the 'Simulation' tab.
""".strip(),
    Action.BATCH_PERFORM_ACTION: """
Batch perform the primary action of the current project tab:
- Kramers-Kronig: perform tests.
- Z-HIT analysis: perform analyses.
- DRT analysis: perform analyses.
- Fitting: perform fits.
""".strip(),
    Action.PERFORM_ACTION: """
Perform the primary action of the current project tab:
- Data sets: select files to load.
- Kramers-Kronig: perform test.
- Z-HIT analysis: perform analysis.
- DRT analysis: perform analysis.
- Fitting: perform fit.
- Simulation: perform simulation.
- Plotting: create a new plot.
""".strip(),
    Action.DELETE_RESULT: """
Delete the current result in the current project tab:
- Data sets: delete the current data set.
- Kramers-Kronig: delete the current test result.
- Z-HIT analysis: delete the current analysis result.
- DRT analysis: delete the current analysis result.
- Fitting: delete the current fit result.
- Simulation: delete the current simulation result.
- Plotting: delete the current plot.
""".strip(),
    Action.NEXT_PRIMARY_RESULT: """
Select the next primary result of the current project tab:
- Data sets: data set.
- Kramers-Kronig: data set.
- Z-HIT analysis: data set.
- DRT analysis: data set.
- Fitting: data set.
- Simulation: data set.
- Plotting: plot.
""".strip(),
    Action.PREVIOUS_PRIMARY_RESULT: """
Select the previous primary result of the current project tab:
- Data sets: data set.
- Kramers-Kronig: data set.
- Z-HIT analysis: data set.
- DRT analysis: data set.
- Fitting: data set.
- Simulation: data set.
- Plotting: plot.
""".strip(),
    Action.NEXT_SECONDARY_RESULT: """
Select the next secondary result of the current project tab:
- Kramers-Kronig: test result.
- Z-HIT analysis: analysis result.
- DRT analysis: analysis result.
- Fitting: fit result.
- Simulation: simulation result.
- Plotting: plot series tab.
""".strip(),
    Action.PREVIOUS_SECONDARY_RESULT: """
Select the previous secondary result of the current project tab:
- Kramers-Kronig: test result.
- Z-HIT analysis: analysis result.
- DRT analysis: analysis result.
- Fitting: fit result.
- Simulation: simulation result.
- Plotting: plot series tab.
""".strip(),
    Action.APPLY_SETTINGS: """
Apply the settings used in the current secondary result of the current project tab:
- Kramers-Kronig: test result.
- Z-HIT analysis: analysis result.
- DRT analysis: analysis result.
- Fitting: fit result.
- Simulation: simulation result.
""".strip(),
    Action.APPLY_MASK: """
Apply the mask used in the current secondary result of the current project tab:
- Kramers-Kronig: test result.
- Z-HIT analysis: analysis result.
- DRT analysis: analysis result.
- Fitting: fit result.
""".strip(),
    Action.SHOW_ENLARGED_DRT: """
Show an enlarged DRT plot.
""".strip(),
    Action.SHOW_ENLARGED_IMPEDANCE: """
Show an enlarged impedance plot.
""".strip(),
    Action.SHOW_ENLARGED_NYQUIST: """
Show an enlarged Nyquist plot.
""".strip(),
    Action.SHOW_ENLARGED_BODE: """
Show an enlarged Bode plot.
""".strip(),
    Action.SHOW_ENLARGED_RESIDUALS: """
Show an enlarged residuals plot.
""".strip(),
    Action.SHOW_CIRCUIT_EDITOR: """
Show the circuit editor window.
""".strip(),
    Action.COPY_DRT_DATA: """
Copy the data from the DRT plot.
""".strip(),
    Action.COPY_IMPEDANCE_DATA: """
Copy the data from the impedance plot.
""".strip(),
    Action.COPY_NYQUIST_DATA: """
Copy the data from the Nyquist plot.
""".strip(),
    Action.COPY_BODE_DATA: """
Copy the data from the Bode plot.
""".strip(),
    Action.COPY_RESIDUALS_DATA: """
Copy the data from the residuals plot.
""".strip(),
    Action.COPY_OUTPUT: """
Copy the chosen output while in the 'DRT analysis', 'Fitting', or the 'Simulation' tab.
""".strip(),
    Action.AVERAGE_DATA_SETS: """
Select data sets to average.
""".strip(),
    Action.TOGGLE_DATA_POINTS: """
Select data points to toggle.
""".strip(),
    Action.COPY_DATA_SET_MASK: """
Select which data set's mask to copy.
""".strip(),
    Action.INTERPOLATE_POINTS: """
Interpolate one or more data points in the current data set.
""".strip(),
    Action.PARALLEL_IMPEDANCE: """
Select the impedance to add in parallel to the current data set.
""".strip(),
    Action.SUBTRACT_IMPEDANCE: """
Select the impedance to subtract from the current data set.
""".strip(),
    Action.SELECT_ALL_PLOT_SERIES: """
Select all data sets and test/fit/simulation results.
""".strip(),
    Action.UNSELECT_ALL_PLOT_SERIES: """
Unselect all data sets and test/fit/simulation results.
""".strip(),
    Action.COPY_PLOT_APPEARANCE: """
Select which plot's appearance settings to copy.
""".strip(),
    Action.COPY_PLOT_DATA: """
Copy the data from the current plot while in the 'Plotting' tab.
""".strip(),
    Action.EXPAND_COLLAPSE_SIDEBAR: """
Collapse/expand the sidebar while in the 'Plotting' tab.
""".strip(),
    Action.EXPORT_PLOT: """
Export the current plot using matplotlib.
""".strip(),
    Action.LOAD_TEST_AS_DATA_SET: """
Load the current Kramers-Kronig test result as a data set.
""".strip(),
    Action.LOAD_SIMULATION_AS_DATA_SET: """
Load the current simulation as a data set.
""".strip(),
    Action.LOAD_ZHIT_AS_DATA_SET: """
Load the current Z-HIT analysis result as a data set.
""".strip(),
    Action.PREVIEW_ZHIT_WEIGHTS: """
Preview the weights for the Z-HIT offset adjustment.
""".strip(),
    Action.DUPLICATE_PLOT: """
Duplicate the current plot.
""".strip(),
    Action.ADJUST_PARAMETERS: """
DEPRECATED: Adjust the (initial) values of circuit parameters prior to fitting or simulation.
""".strip(),
    Action.NEXT_PLOT_TAB: """
Select the next plot type.
""".strip(),
    Action.PREVIOUS_PLOT_TAB: """
Select the previous plot type.
""".strip(),
}
# Check that every action has a description
assert set(action_to_string.keys()) == set(
    action_descriptions.keys()
), "Missing action descriptions detected!"


class CNLSMethod(IntEnum):
    """
    Iterative methods used during complex non-linear least-squares fitting:

    - AUTO: try each method
    - BFGS
    - CG
    - LBFGSB
    - LEASTSQ
    - LEAST_SQUARES
    - NELDER
    - POWELL
    - SLSQP
    - TNC
    """

    AUTO = 1
    LEASTSQ = 2
    LEAST_SQUARES = 3
    DIFFERENTIAL_EVOLUTION = 4
    BRUTE = 5
    BASINHOPPING = 6
    AMPGO = 7
    NELDER = 8
    LBFGSB = 9
    POWELL = 10
    CG = 11
    NEWTON = 12
    COBYLA = 13
    BFGS = 14
    TNC = 15
    TRUST_NCG = 16
    TRUST_EXACT = 17
    TRUST_KRYLOV = 18
    TRUST_CONSTR = 19
    DOGLEG = 20
    SLSQP = 21
    EMCEE = 22
    SHGO = 23
    DUAL_ANNEALING = 24


label_to_cnls_method: Dict[str, CNLSMethod] = {
    "Auto": CNLSMethod.AUTO,
    "Levenberg-Marquardt": CNLSMethod.LEASTSQ,
    "Least-squares (trust-region reflective)": CNLSMethod.LEAST_SQUARES,
    "Powell": CNLSMethod.POWELL,  # Had some problem fitting
    "BFGS": CNLSMethod.BFGS,  # Had some problem fitting
    "Nelder-Mead": CNLSMethod.NELDER,  # Had some problem fitting
    "Conjugate Gradient": CNLSMethod.CG,  # Had some problem fitting
    "Truncated Newton": CNLSMethod.TNC,  # Had some problem fitting
    "L-BFGS-B": CNLSMethod.LBFGSB,  # NaN errors
    # "COBYLA": CNLSMethod.COBYLA,  # Had some problem fitting
    "Sequential Linear Squares Programming": CNLSMethod.SLSQP,  # Had some problem fitting
    # "Basin hopping": CNLSMethod.BASINHOPPING,  # NaN errors
    # "Differential Evolution": CNLSMethod.DIFFERENTIAL_EVOLUTION,  # Requires finite bounds for all mutable parameters
    # "Brute force method": CNLSMethod.BRUTE,  # Requires that brute_step is defined for mutable parameters
    # "Adaptive Memory Programming for Global Optimization": CNLSMethod.AMPGO,  # NaN errors
    # "Newton": CNLSMethod.NEWTON,  # Requires Jacobian
    # "Newton CG": CNLSMethod.TRUST_NCG,  # Requires Jacobian for trust region
    # "Exact trust-region": CNLSMethod.TRUST_EXACT,  # Requires Jacobian for trust region
    # "Newton GLTR trust-region": CNLSMethod.TRUST_KRYLOV,  # Requires Jacobian for trust region
    # "Constrained trust-region": CNLSMethod.TRUST_CONSTR,  # NaN errors
    # "Dog-leg trust-region": CNLSMethod.DOGLEG,  # Requires Jacobian
    # "Simplicial Homology Global Optimization": CNLSMethod.SHGO,  # NaN errors
    # "Dual Annealing": CNLSMethod.DUAL_ANNEALING,  # Requires finite bounds for all mutable parameters
    # "Maximum likelyhood via Monte-Carlo Markov chain": CNLSMethod.EMCEE,  # Requires the emcee package (version 3)
}
cnls_method_to_label: Dict[CNLSMethod, str] = {
    v: k for k, v in label_to_cnls_method.items()
}
cnls_method_to_label[CNLSMethod.AUTO] = "Auto"
cnls_method_to_value: Dict[CNLSMethod, str] = {
    CNLSMethod.AUTO: "auto",
    CNLSMethod.LEASTSQ: "leastsq",
    CNLSMethod.LEAST_SQUARES: "least_squares",
    CNLSMethod.DIFFERENTIAL_EVOLUTION: "differential_evolution",
    CNLSMethod.BRUTE: "brute",
    CNLSMethod.BASINHOPPING: "basinhopping",
    CNLSMethod.AMPGO: "ampgo",
    CNLSMethod.NELDER: "nelder",
    CNLSMethod.LBFGSB: "lbfgsb",
    CNLSMethod.POWELL: "powell",
    CNLSMethod.CG: "cg",
    CNLSMethod.NEWTON: "newton",
    CNLSMethod.COBYLA: "cobyla",
    CNLSMethod.BFGS: "bfgs",
    CNLSMethod.TNC: "tnc",
    CNLSMethod.TRUST_NCG: "trust-ncg",
    CNLSMethod.TRUST_EXACT: "trust-exact",
    CNLSMethod.TRUST_KRYLOV: "trust-krylov",
    CNLSMethod.TRUST_CONSTR: "trust-constr",
    CNLSMethod.DOGLEG: "dogleg",
    CNLSMethod.SLSQP: "slsqp",
    CNLSMethod.EMCEE: "emcee",
    CNLSMethod.SHGO: "shgo",
    CNLSMethod.DUAL_ANNEALING: "dual_annealing",
}
value_to_cnls_method: Dict[str, CNLSMethod] = {
    v: k for k, v in cnls_method_to_value.items()
}
assert set(cnls_method_to_value.keys()) == set(
    value_to_cnls_method.values()
), "Duplicate method string keys detected!"


class KramersKronigMode(IntEnum):
    """
    Types of modes that determine how the number of RC elements is chosen:

    - AUTO: automatically suggest the number of using the selected method(s)
    - EXPLORATORY: same procedure as AUTO but present intermediate results to user
    - MANUAL: manually choose the number
    """

    AUTO = 1
    EXPLORATORY = 2
    MANUAL = 3


test_mode_to_label: Dict[KramersKronigMode, str] = {
    KramersKronigMode.AUTO: "Auto",
    KramersKronigMode.EXPLORATORY: "Exploratory",
    KramersKronigMode.MANUAL: "Manual",
}
label_to_test_mode: Dict[str, KramersKronigMode] = {v: k for k, v in test_mode_to_label.items()}
assert set(test_mode_to_label.keys()) == set(
    label_to_test_mode.values()
), "Duplicate test mode string labels detected!"


class KramersKronigRepresentation(IntEnum):
    """
    - AUTO: Automatically suggest the most suitable immittance representation
    - IMPEDANCE
    - ADMITTANCE
    """
    AUTO = 1
    IMPEDANCE = 2
    ADMITTANCE = 3


test_representation_to_label: Dict[KramersKronigRepresentation, str] = {
    KramersKronigRepresentation.AUTO: "Auto",
    KramersKronigRepresentation.IMPEDANCE: "Impedance",
    KramersKronigRepresentation.ADMITTANCE: "Admittance",
}
label_to_test_representation: Dict[str, KramersKronigRepresentation] = {
    v: k for k, v in test_representation_to_label.items()
}
test_representation_to_value: Dict[KramersKronigRepresentation, Optional[bool]] = {
    KramersKronigRepresentation.AUTO: None,
    KramersKronigRepresentation.IMPEDANCE: False,
    KramersKronigRepresentation.ADMITTANCE: True,
}
assert set(test_representation_to_label.keys()) == set(
    label_to_test_representation.values()
), "Duplicate test representation string labels detected!"
assert set(test_representation_to_value.keys()) == set(
    test_representation_to_value.keys()
), "Missing test representation value detected!"


class FitSimOutput(IntEnum):
    CDC_BASIC = auto()
    CDC_EXTENDED = auto()
    CSV_DATA_TABLE = auto()
    CSV_PARAMETERS_TABLE = auto()
    CSV_STATISTICS_TABLE = auto()
    JSON_PARAMETERS_TABLE = auto()
    JSON_STATISTICS_TABLE = auto()
    LATEX_DIAGRAM = auto()
    LATEX_EXPR = auto()
    LATEX_PARAMETERS_TABLE = auto()
    LATEX_STATISTICS_TABLE = auto()
    MARKDOWN_PARAMETERS_TABLE = auto()
    MARKDOWN_STATISTICS_TABLE = auto()
    SVG_DIAGRAM = auto()
    SVG_DIAGRAM_NO_LABELS = auto()
    SYMPY_EXPR = auto()
    SYMPY_EXPR_VALUES = auto()


fit_sim_output_to_label: Dict[FitSimOutput, str] = {
    FitSimOutput.CDC_BASIC: "CDC - basic",
    FitSimOutput.CDC_EXTENDED: "CDC - extended",
    FitSimOutput.CSV_DATA_TABLE: "CSV - impedance table",
    FitSimOutput.CSV_PARAMETERS_TABLE: "CSV - parameters table",
    FitSimOutput.CSV_STATISTICS_TABLE: "CSV - statistics table",
    FitSimOutput.JSON_PARAMETERS_TABLE: "JSON - parameters table",
    FitSimOutput.JSON_STATISTICS_TABLE: "JSON - statistics table",
    FitSimOutput.LATEX_DIAGRAM: "LaTeX - circuit diagram",
    FitSimOutput.LATEX_EXPR: "LaTeX - expression",
    FitSimOutput.LATEX_PARAMETERS_TABLE: "LaTeX - parameters table",
    FitSimOutput.LATEX_STATISTICS_TABLE: "LaTeX - statistics table",
    FitSimOutput.MARKDOWN_PARAMETERS_TABLE: "Markdown - parameters table",
    FitSimOutput.MARKDOWN_STATISTICS_TABLE: "Markdown - statistics table",
    FitSimOutput.SVG_DIAGRAM: "SVG - circuit diagram",
    FitSimOutput.SVG_DIAGRAM_NO_LABELS: "SVG - circuit diagram without any labels",
    FitSimOutput.SYMPY_EXPR: "SymPy - expression",
    FitSimOutput.SYMPY_EXPR_VALUES: "SymPy - expression and values",
}
label_to_fit_sim_output: Dict[str, FitSimOutput] = {
    v: k for k, v in fit_sim_output_to_label.items()
}
assert set(fit_sim_output_to_label.keys()) == set(
    label_to_fit_sim_output.values()
), "Duplicate output string labels detected!"


# TODO: Add DRT with frequency rather than time constant?
class PlotType(IntEnum):
    """
    Types of plots:

    - NYQUIST_IMPEDANCE: -Im(Z) vs Re(Z)
    - BODE_IMPEDANCE_MAGNITUDE: Mod(Z) vs f
    - BODE_IMPEDANCE_PHASE: -Phase(Z) vs f
    - IMPEDANCE_REAL: Re(Z) vs f
    - IMPEDANCE_IMAGINARY: -Im(Z) vs f
    - DRT: gamma vs tau
    - NYQUIST_ADMITTANCE: Im(Y) vs Re(Y)
    - BODE_ADMITTANCE_MAGNITUDE: Mod(Y) vs f
    - BODE_ADMITTANCE_PHASE: Phase(Y) vs f
    - ADMITTANCE_REAL: Re(Y) vs f
    - ADMITTANCE_IMAGINARY: Im(Y) vs f
    - DRT_FREQUENCY: gamma vs f
    """

    NYQUIST_IMPEDANCE = 1
    BODE_IMPEDANCE_MAGNITUDE = 2
    BODE_IMPEDANCE_PHASE = 3
    IMPEDANCE_REAL = 4
    IMPEDANCE_IMAGINARY = 5
    DRT = 6
    NYQUIST_ADMITTANCE = 7
    BODE_ADMITTANCE_MAGNITUDE = 8
    BODE_ADMITTANCE_PHASE = 9
    ADMITTANCE_REAL = 10
    ADMITTANCE_IMAGINARY = 11
    DRT_FREQUENCY = 12


plot_type_to_label: Dict[PlotType, str] = {
    PlotType.ADMITTANCE_IMAGINARY: "Admittance - imaginary",
    PlotType.ADMITTANCE_REAL: "Admittance - real",
    PlotType.BODE_ADMITTANCE_MAGNITUDE: "Bode - admittance magnitude",
    PlotType.BODE_ADMITTANCE_PHASE: "Bode - admittance phase",
    PlotType.BODE_IMPEDANCE_MAGNITUDE: "Bode - impedance magnitude",
    PlotType.BODE_IMPEDANCE_PHASE: "Bode - impedance phase",
    PlotType.DRT: "Distribution of relaxation times",
    PlotType.DRT_FREQUENCY: "Distribution of relaxation times (vs frequency)",
    PlotType.IMPEDANCE_IMAGINARY: "Impedance - imaginary",
    PlotType.IMPEDANCE_REAL: "Impedance - real",
    PlotType.NYQUIST_ADMITTANCE: "Nyquist - admittance",
    PlotType.NYQUIST_IMPEDANCE: "Nyquist - impedance",
}
label_to_plot_type: Dict[str, PlotType] = {v: k for k, v in plot_type_to_label.items()}
assert set(plot_type_to_label.keys()) == set(
    label_to_plot_type.values()
), "Duplicate plot type string labels detected!"


class KramersKronigTest(IntEnum):
    """
    Types of Kramers-Kronig tests:

    - CNLS: complex non-linear least-squares fit of circuit (fig. 1, Boukamp, 1995) with a distribution of fixed time constants
    - COMPLEX: eqs. 11 and 12, Boukamp, 1995
    - IMAGINARY: eqs. 4, 6, and 7, Boukamp, 1995
    - REAL: eqs. 5, 8, 9, and 10, Boukamp, 1995

    The `_LEASTSQ` variants use numpy.linalg.lstsq instead of pseudo-inverse matrices.
    """

    CNLS = 1
    COMPLEX = 2
    IMAGINARY = 3
    REAL = 4
    COMPLEX_LEASTSQ = 5
    IMAGINARY_LEASTSQ = 6
    REAL_LEASTSQ = 7


test_to_label: Dict[KramersKronigTest, str] = {
    KramersKronigTest.CNLS: "CNLS",
    KramersKronigTest.COMPLEX_LEASTSQ: "Complex (least sq.)",
    KramersKronigTest.COMPLEX: "Complex (mat. inv.)",
    KramersKronigTest.IMAGINARY_LEASTSQ: "Imaginary (least sq.)",
    KramersKronigTest.IMAGINARY: "Imaginary (mat. inv.)",
    KramersKronigTest.REAL_LEASTSQ: "Real (least sq.)",
    KramersKronigTest.REAL: "Real (mat. inv.)",
}
label_to_test: Dict[str, KramersKronigTest] = {v: k for k, v in test_to_label.items()}
test_to_value: Dict[KramersKronigTest, str] = {
    KramersKronigTest.CNLS: "cnls",
    KramersKronigTest.COMPLEX: "complex-inv",
    KramersKronigTest.IMAGINARY: "imaginary-inv",
    KramersKronigTest.REAL: "real-inv",
    KramersKronigTest.COMPLEX_LEASTSQ: "complex",
    KramersKronigTest.IMAGINARY_LEASTSQ: "imaginary",
    KramersKronigTest.REAL_LEASTSQ: "real",
}
assert set(test_to_label.keys()) == set(
    label_to_test.values()
), "Duplicate test string keys detected!"
assert set(test_to_label.keys()) == set(
    test_to_value.keys()
), "Missing test string values detected!"


class Weight(IntEnum):
    """
    Types of weights to use during complex non-linear least squares fitting:

    - AUTO: try each weight
    - BOUKAMP: :math:`1 / ({\\rm Re}(Z)^2 + {\\rm Im}(Z)^2)` (eq. 13, Boukamp, 1995)
    - MODULUS: :math:`1 / |Z|`
    - PROPORTIONAL: :math:`1 / {\\rm Re}(Z)^2, 1 / {\\rm Im}(Z)^2`
    - UNITY: 1
    """

    AUTO = 1
    UNITY = 2
    PROPORTIONAL = 3
    MODULUS = 4
    BOUKAMP = 5


weight_to_label: Dict[Weight, str] = {
    Weight.AUTO: "Auto",
    Weight.MODULUS: "Modulus",
    Weight.PROPORTIONAL: "Proportional",
    Weight.UNITY: "Unity",
    Weight.BOUKAMP: "Boukamp",
}
label_to_weight: Dict[str, Weight] = {v: k for k, v in weight_to_label.items()}
weight_to_value: Dict[Weight, str] = {
    Weight.AUTO: "auto",
    Weight.UNITY: "unity",
    Weight.PROPORTIONAL: "proportional",
    Weight.MODULUS: "modulus",
    Weight.BOUKAMP: "boukamp",
}
value_to_weight: Dict[str, Weight] = {v: k for k, v in weight_to_value.items()}
assert set(weight_to_label.keys()) == set(
    label_to_weight.values()
), "Duplicate weight string labels detected!"
assert set(weight_to_label.keys()) == set(
    weight_to_value.keys()
), "Missing weight string values detected!"
assert set(weight_to_value.keys()) == set(
    value_to_weight.values()
), "Duplicate weight string values detected!"


class DRTMethod(IntEnum):
    """
    The method to use for calculating the DRT:

    - TR_NNLS
    - TR_RBF
    - BHT
    - MRQ_FIT
    """

    TR_NNLS = 1
    TR_RBF = 2
    BHT = 3
    MRQ_FIT = 4


drt_method_to_label: Dict[DRTMethod, str] = {
    DRTMethod.BHT: "BHT",
    DRTMethod.TR_NNLS: "TR-NNLS",
    DRTMethod.TR_RBF: "TR-RBF",
    DRTMethod.MRQ_FIT: "m(RQ)fit",
}
label_to_drt_method: Dict[str, DRTMethod] = {
    v: k for k, v in drt_method_to_label.items()
}
drt_method_to_value: Dict[DRTMethod, str] = {
    DRTMethod.BHT: "bht",
    DRTMethod.MRQ_FIT: "mrq-fit",
    DRTMethod.TR_NNLS: "tr-nnls",
    DRTMethod.TR_RBF: "tr-rbf",
}
assert set(drt_method_to_label.keys()) == set(
    label_to_drt_method.values()
), "Duplicate DRT method string labels detected!"
assert set(drt_method_to_label.keys()) == set(
    drt_method_to_value.keys()
), "Missing DRT method string values detected!"


class DRTMode(IntEnum):
    """
    The parts of the impedance data to use:

    - COMPLEX
    - REAL
    - IMAGINARY
    """

    COMPLEX = 1
    REAL = 2
    IMAGINARY = 3


drt_mode_to_label: Dict[DRTMode, str] = {
    DRTMode.COMPLEX: "Complex",
    DRTMode.REAL: "Real",
    DRTMode.IMAGINARY: "Imaginary",
}
label_to_drt_mode: Dict[str, DRTMode] = {v: k for k, v in drt_mode_to_label.items()}
drt_mode_to_value: Dict[DRTMode, str] = {
    DRTMode.COMPLEX: "complex",
    DRTMode.REAL: "real",
    DRTMode.IMAGINARY: "imaginary",
}
assert set(drt_mode_to_label.keys()) == set(
    label_to_drt_mode.values()
), "Duplicate DRT mode string labels detected!"
assert set(drt_mode_to_label.keys()) == set(
    drt_mode_to_value.keys()
), "Missing DRT mode string values detected!"


class TRNNLSLambdaMethod(IntEnum):
    """
    - NONE
    - CUSTOM - Custom approach
    - LC - L-curve corner search
    """
    NONE = 1
    CUSTOM = 2
    LC = 3


tr_nnls_lambda_method_to_label: Dict[TRNNLSLambdaMethod, str] = {
    TRNNLSLambdaMethod.NONE: "NONE",
    TRNNLSLambdaMethod.CUSTOM: "Custom",
    TRNNLSLambdaMethod.LC: "L-curve corner search",
}
label_to_tr_nnls_lambda_method: Dict[str, TRNNLSLambdaMethod] = {v: k for k, v in tr_nnls_lambda_method_to_label.items()}
tr_nnls_lambda_method_to_value: Dict[TRNNLSLambdaMethod, float] = {
    TRNNLSLambdaMethod.NONE: 0.0,
    TRNNLSLambdaMethod.CUSTOM: -1.0,
    TRNNLSLambdaMethod.LC: -2.0,
}
assert set(tr_nnls_lambda_method_to_label.keys()) == set(
    label_to_tr_nnls_lambda_method.values()
), "Duplicate TR-NNLS lambda method string labels detected!"
assert set(tr_nnls_lambda_method_to_label.keys()) == set(
    tr_nnls_lambda_method_to_value.keys()
), "Missing TR-NNLS lambda method string values detected!"


class RBFType(IntEnum):
    """
    The radial basis function to use for discretization (or piecewise linear discretization):

    - C0_MATERN
    - C2_MATERN
    - C4_MATERN
    - C6_MATERN
    - CAUCHY
    - GAUSSIAN
    - INVERSE_QUADRATIC
    - INVERSE_QUADRIC
    - PIECEWISE_LINEAR
    """

    C0_MATERN = 1
    C2_MATERN = 2
    C4_MATERN = 3
    C6_MATERN = 4
    CAUCHY = 5
    GAUSSIAN = 6
    INVERSE_QUADRATIC = 7
    INVERSE_QUADRIC = 8
    PIECEWISE_LINEAR = 9


rbf_type_to_label: Dict[RBFType, str] = {
    RBFType.C0_MATERN: "C^0 Matérn",
    RBFType.C2_MATERN: "C^2 Matérn",
    RBFType.C4_MATERN: "C^4 Matérn",
    RBFType.C6_MATERN: "C^6 Matérn",
    RBFType.CAUCHY: "Cauchy",
    RBFType.GAUSSIAN: "Gaussian",
    RBFType.INVERSE_QUADRATIC: "Inverse quadratic",
    RBFType.INVERSE_QUADRIC: "Inverse quadric",
    RBFType.PIECEWISE_LINEAR: "Piecewise linear",
}
label_to_rbf_type: Dict[str, RBFType] = {v: k for k, v in rbf_type_to_label.items()}
rbf_type_to_value: Dict[RBFType, str] = {
    RBFType.C0_MATERN: "c0-matern",
    RBFType.C2_MATERN: "c2-matern",
    RBFType.C4_MATERN: "c4-matern",
    RBFType.C6_MATERN: "c6-matern",
    RBFType.CAUCHY: "cauchy",
    RBFType.GAUSSIAN: "gaussian",
    RBFType.INVERSE_QUADRATIC: "inverse-quadratic",
    RBFType.INVERSE_QUADRIC: "inverse-quadric",
    RBFType.PIECEWISE_LINEAR: "piecewise-linear",
}
assert set(rbf_type_to_label.keys()) == set(
    label_to_rbf_type.values()
), "Duplicate RBF type string labels detected!"
assert set(rbf_type_to_label.keys()) == set(
    rbf_type_to_value.keys()
), "Missing RBF type string values detected!"


class RBFShape(IntEnum):
    """
    The shape to use with the radial basis function discretization:

    - FWHM
    - FACTOR
    """

    FWHM = 1
    FACTOR = 2


rbf_shape_to_label: Dict[RBFShape, str] = {
    RBFShape.FACTOR: "Factor",
    RBFShape.FWHM: "FWHM",
}
label_to_rbf_shape: Dict[str, RBFShape] = {v: k for k, v in rbf_shape_to_label.items()}
rbf_shape_to_value: Dict[RBFShape, str] = {
    RBFShape.FACTOR: "factor",
    RBFShape.FWHM: "fwhm",
}
assert set(rbf_shape_to_label.keys()) == set(
    label_to_rbf_shape.values()
), "Duplicate RBF shape string labels detected!"
assert set(rbf_shape_to_label.keys()) == set(
    rbf_shape_to_value.keys()
), "Missing RBF shape string values detected!"


derivative_order_to_label: Dict[int, str] = {
    1: "1st",
    2: "2nd",
}
label_to_derivative_order: Dict[str, int] = {
    v: k for k, v in derivative_order_to_label.items()
}


class CrossValidationMethod(IntEnum):
    """
    Cross-validation method used by the TR-RBF method for automatically
    determining a suitable lambda value.
    """

    NONE = 1
    GCV = 2
    MGCV = 3
    RGCV = 4
    RE_IM = 5
    LC = 6


cross_validation_method_to_label: Dict[CrossValidationMethod, str] = {
    CrossValidationMethod.NONE: "None",
    CrossValidationMethod.GCV: "GCV",
    CrossValidationMethod.MGCV: "mGCV",
    CrossValidationMethod.RGCV: "rGCV",
    CrossValidationMethod.RE_IM: "Re-Im",
    CrossValidationMethod.LC: "L-curve",
}

label_to_cross_validation_method: Dict[str, CrossValidationMethod] = {
    v: k for k, v in cross_validation_method_to_label.items()
}

cross_validation_method_to_value: Dict[CrossValidationMethod, str] = {
    CrossValidationMethod.NONE: "",
    CrossValidationMethod.GCV: "gcv",
    CrossValidationMethod.MGCV: "mgcv",
    CrossValidationMethod.RGCV: "rgcv",
    CrossValidationMethod.RE_IM: "re-im",
    CrossValidationMethod.LC: "lc",
}
assert set(cross_validation_method_to_label.keys()) == set(
    label_to_cross_validation_method.values()
), "Duplicate cross-validation method string labels detected!"
assert set(cross_validation_method_to_label.keys()) == set(
    cross_validation_method_to_value.keys()
), "Missing cross-validation method string values detected!"


class DRTOutput(IntEnum):
    CSV_SCORES = auto()
    JSON_SCORES = auto()
    LATEX_SCORES = auto()
    MARKDOWN_SCORES = auto()


drt_output_to_label: Dict[DRTOutput, str] = {
    DRTOutput.CSV_SCORES: "CSV - scores",
    DRTOutput.JSON_SCORES: "JSON - scores",
    DRTOutput.LATEX_SCORES: "LaTeX - scores",
    DRTOutput.MARKDOWN_SCORES: "Markdown - scores",
}
label_to_drt_output: Dict[str, DRTOutput] = {
    v: k for k, v in drt_output_to_label.items()
}
assert set(drt_output_to_label.keys()) == set(
    label_to_drt_output.values()
), "Duplicate DRT output string labels detected!"


class PlotUnits(IntEnum):
    """
    The units of the plot dimensions:

    - INCHES
    - CENTIMETERS
    """

    INCHES = 1
    CENTIMETERS = 2


plot_units_to_label: Dict[PlotUnits, str] = {
    PlotUnits.INCHES: "Inches",
    PlotUnits.CENTIMETERS: "Centimeters",
}
label_to_plot_units: Dict[str, PlotUnits] = {
    v: k for k, v in plot_units_to_label.items()
}
plot_units_per_inch: Dict[PlotUnits, float] = {
    PlotUnits.INCHES: 1.0,
    PlotUnits.CENTIMETERS: 2.54,
}
assert set(plot_units_to_label.keys()) == set(
    label_to_plot_units.values()
), "Duplicate plot unit string labels detected!"
assert set(plot_units_to_label.keys()) == set(
    plot_units_per_inch.keys()
), "Missing plot unit string values detected!"


# DEPRECATED
# TODO: Remove at some point
class PlotPreviewLimit(IntEnum):
    """
    The limits of the plot preview:

    - NONE
    - PX256
    - PX512
    - PX1024
    - PX2048
    - PX4096
    - PX8192
    - PX16384
    """

    NONE = 0
    PX256 = 8
    PX512 = 9
    PX1024 = 10
    PX2048 = 11
    PX4096 = 12
    PX8192 = 13
    PX16384 = 14


# DEPRECATED
# TODO: Remove at some point
plot_preview_limit_to_label: Dict[PlotPreviewLimit, str] = {
    PlotPreviewLimit.NONE: "No limit",
    PlotPreviewLimit.PX256: f"{2**8} px",
    PlotPreviewLimit.PX512: f"{2**9} px",
    PlotPreviewLimit.PX1024: f"{2**10} px",
    PlotPreviewLimit.PX2048: f"{2**11} px",
    PlotPreviewLimit.PX4096: f"{2**12} px",
    PlotPreviewLimit.PX8192: f"{2**13} px",
    PlotPreviewLimit.PX16384: f"{2**14} px",
}
label_to_plot_preview_limit: Dict[str, PlotPreviewLimit] = {
    v: k for k, v in plot_preview_limit_to_label.items()
}
assert set(plot_preview_limit_to_label.keys()) == set(
    label_to_plot_preview_limit.values()
), "Duplicate plot preview limit string labels detected!"


class PlotLegendLocation(IntEnum):
    """
    The position of the plot legend:

    - AUTO
    - UPPER_RIGHT
    - UPPER_LEFT
    - LOWER_LEFT
    - LOWER_RIGHT
    - RIGHT
    - CENTER_LEFT
    - CENTER_RIGHT
    - LOWER_CENTER
    - UPPER_CENTER
    - CENTER
    """

    AUTO = 0
    UPPER_RIGHT = 1
    UPPER_LEFT = 2
    LOWER_LEFT = 3
    LOWER_RIGHT = 4
    RIGHT = 5
    CENTER_LEFT = 6
    CENTER_RIGHT = 7
    LOWER_CENTER = 8
    UPPER_CENTER = 9
    CENTER = 10


plot_legend_location_to_label: Dict[PlotLegendLocation, str] = {
    PlotLegendLocation.AUTO: "Automatic",
    PlotLegendLocation.UPPER_RIGHT: "Upper right",
    PlotLegendLocation.UPPER_LEFT: "Upper left",
    PlotLegendLocation.LOWER_LEFT: "Lower left",
    PlotLegendLocation.LOWER_RIGHT: "Lower right",
    PlotLegendLocation.RIGHT: "Right",
    PlotLegendLocation.CENTER_LEFT: "Center left",
    PlotLegendLocation.CENTER_RIGHT: "Center right",
    PlotLegendLocation.LOWER_CENTER: "Lower center",
    PlotLegendLocation.UPPER_CENTER: "Upper center",
    PlotLegendLocation.CENTER: "Center",
}
label_to_plot_legend_location: Dict[str, PlotLegendLocation] = {
    v: k for k, v in plot_legend_location_to_label.items()
}
assert set(plot_legend_location_to_label.keys()) == set(
    label_to_plot_legend_location.values()
), "Duplicate plot legend location string labels detected!"


PLOT_EXTENSIONS: List[str] = [
    ".eps",
    ".jpg",
    ".pdf",
    ".pgf",
    ".png",
    ".ps",
    ".svg",
]


class ZHITSmoothing(IntEnum):
    """
    The algorithm to use when smoothing the phase data:

    - AUTO: try all of the options
    - NONE: no smoothing
    - LOWESS: `Local Weighted Scatterplot Smoothing <https://www.statsmodels.org/dev/generated/statsmodels.nonparametric.smoothers_lowess.lowess.html#statsmodels.nonparametric.smoothers_lowess.lowess>`_
    - SAVGOL: `Savitzky-Golay <https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.savgol_filter.html>`_
    - WHITHEND: `Whittaker-Henderson <https://doi.org/10.1021/acsmeasuresciau.1c00054>`_
    - MODSINC: `Modified sinc kernel <https://doi.org/10.1021/acsmeasuresciau.1c00054>`_
    """

    AUTO = 1
    NONE = 2
    LOWESS = 3
    SAVGOL = 4  # Savitzky-Golay
    WHITHEND = 5  # Whittaker-Henderson
    MODSINC = 6  # Modifiec sinc kernel


label_to_zhit_smoothing: Dict[str, ZHITSmoothing] = {
    "Auto": ZHITSmoothing.AUTO,
    "None": ZHITSmoothing.NONE,
    "LOWESS": ZHITSmoothing.LOWESS,
    "Savitzky-Golay": ZHITSmoothing.SAVGOL,
    "Whittaker-Henderson": ZHITSmoothing.WHITHEND,
    "Modified sinc kernel": ZHITSmoothing.MODSINC,
}
zhit_smoothing_to_label: Dict[ZHITSmoothing, str] = {
    v: k for k, v in label_to_zhit_smoothing.items()
}
zhit_smoothing_to_value: Dict[ZHITSmoothing, str] = {
    ZHITSmoothing.AUTO: "auto",
    ZHITSmoothing.NONE: "none",
    ZHITSmoothing.LOWESS: "lowess",
    ZHITSmoothing.SAVGOL: "savgol",
    ZHITSmoothing.WHITHEND: "whithend",
    ZHITSmoothing.MODSINC: "modsinc",
}
value_to_zhit_smoothing: Dict[str, ZHITSmoothing] = {
    v: k for k, v in zhit_smoothing_to_value.items()
}
assert set(zhit_smoothing_to_label.keys()) == set(
    label_to_zhit_smoothing.values()
), "Duplicate ZHIT smoothing string labels detected!"
assert set(zhit_smoothing_to_label.keys()) == set(
    zhit_smoothing_to_value.keys()
), "Missing ZHIT smoothing string value detected!"


class ZHITInterpolation(IntEnum):
    """
    The spline to use for interpolating the smoothed phase data:

    - AUTO: try all of the options
    - AKIMA: `Akima spline <https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.Akima1DInterpolator.html#scipy.interpolate.Akima1DInterpolator>`_
    - CUBIC: `cubic spline <https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.CubicSpline.html#scipy.interpolate.CubicSpline>`_
    - PCHIP: `Piecewise Cubic Hermite Interpolating Polynomial <https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.PchipInterpolator.html#scipy.interpolate.PchipInterpolator>`_
    - MAKIMA: `Modified Akima spline <https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.Akima1DInterpolator.html#scipy.interpolate.Akima1DInterpolator>`_
    """

    AUTO = 1
    AKIMA = 2
    CUBIC = 3
    PCHIP = 4
    MAKIMA = 5


label_to_zhit_interpolation: Dict[str, ZHITInterpolation] = {
    "Auto": ZHITInterpolation.AUTO,
    "Akima": ZHITInterpolation.AKIMA,
    "Cubic": ZHITInterpolation.CUBIC,
    "PCHIP": ZHITInterpolation.PCHIP,
    "Modified Akima": ZHITInterpolation.MAKIMA,
}
zhit_interpolation_to_label: Dict[ZHITInterpolation, str] = {
    v: k for k, v in label_to_zhit_interpolation.items()
}
zhit_interpolation_to_value: Dict[ZHITInterpolation, str] = {
    ZHITInterpolation.AUTO: "auto",
    ZHITInterpolation.AKIMA: "akima",
    ZHITInterpolation.CUBIC: "cubic",
    ZHITInterpolation.PCHIP: "pchip",
    ZHITInterpolation.MAKIMA: "makima",
}
value_to_zhit_interpolation: Dict[str, ZHITInterpolation] = {
    v: k for k, v in zhit_interpolation_to_value.items()
}
assert set(zhit_interpolation_to_label.keys()) == set(
    label_to_zhit_interpolation.values()
), "Duplicate ZHIT interpolation string labels detected!"
assert set(zhit_interpolation_to_label.keys()) == set(
    zhit_interpolation_to_value.keys()
), "Missing ZHIT interpolation string value detected!"


class ZHITWindow(IntEnum):
    """
    The window functions to use for determining the weights when adjusting the Mod(Z) offset:

    - AUTO: try all of the options
    - BARTHANN
    - BARTLETT
    - BLACKMAN
    - BLACKMANHARRIS
    - BOHMAN
    - BOXCAR
    - COSINE
    - FLATTOP
    - HAMMING
    - HANN
    - LANCZOS
    - NUTTALL
    - PARZEN
    - TRIANG

    See `scipy.signal.windows <https://docs.scipy.org/doc/scipy/reference/signal.windows.html>`_ for information about these.
    """

    AUTO = 1
    BARTHANN = 2
    BARTLETT = 3
    BLACKMAN = 4
    BLACKMANHARRIS = 5
    BOHMAN = 6
    BOXCAR = 7
    COSINE = 8
    FLATTOP = 9
    HAMMING = 10
    HANN = 11
    NUTTALL = 12
    PARZEN = 13
    TRIANG = 14
    LANCZOS = 15


zhit_window_to_label: Dict[ZHITWindow, str] = {
    ZHITWindow.AUTO: "Auto",
    ZHITWindow.BARTHANN: "Barthann",
    ZHITWindow.BARTLETT: "Bartlett",
    ZHITWindow.BLACKMAN: "Blackman",
    ZHITWindow.BLACKMANHARRIS: "Blackman-Harris",
    ZHITWindow.BOHMAN: "Bohman",
    ZHITWindow.BOXCAR: "Boxcar",
    ZHITWindow.COSINE: "Cosine",
    ZHITWindow.FLATTOP: "Flat top",
    ZHITWindow.HAMMING: "Hamming",
    ZHITWindow.HANN: "Hann",
    ZHITWindow.LANCZOS: "Lanczos",
    ZHITWindow.NUTTALL: "Nuttall",
    ZHITWindow.PARZEN: "Parzen",
    ZHITWindow.TRIANG: "Triangular",
}
label_to_zhit_window: Dict[str, ZHITWindow] = {
    v: k for k, v in zhit_window_to_label.items()
}
zhit_window_to_value: Dict[ZHITWindow, str] = {
    ZHITWindow.AUTO: "auto",
    ZHITWindow.BARTHANN: "barthann",
    ZHITWindow.BARTLETT: "bartlett",
    ZHITWindow.BLACKMAN: "blackman",
    ZHITWindow.BLACKMANHARRIS: "blackmanharris",
    ZHITWindow.BOHMAN: "bohman",
    ZHITWindow.BOXCAR: "boxcar",
    ZHITWindow.COSINE: "cosine",
    ZHITWindow.FLATTOP: "flattop",
    ZHITWindow.HAMMING: "hamming",
    ZHITWindow.HANN: "hann",
    ZHITWindow.LANCZOS: "lanczos",
    ZHITWindow.NUTTALL: "nuttall",
    ZHITWindow.PARZEN: "parzen",
    ZHITWindow.TRIANG: "triang",
}
value_to_zhit_window: Dict[str, ZHITWindow] = {
    v: k for k, v in zhit_window_to_value.items()
}
assert set(zhit_window_to_label.keys()) == set(
    label_to_zhit_window.values()
), "Duplicate ZHIT window string labels detected!"
assert set(zhit_window_to_label.keys()) == set(
    zhit_window_to_value.keys()
), "Missing ZHIT window string value detected!"


class ZHITRepresentation(IntEnum):
    """
    - IMPEDANCE
    - ADMITTANCE
    """
    #AUTO = 1
    IMPEDANCE = 2
    ADMITTANCE = 3


zhit_representation_to_label: Dict[ZHITRepresentation, str] = {
    #ZHITRepresentation.AUTO: "Auto",
    ZHITRepresentation.IMPEDANCE: "Impedance",
    ZHITRepresentation.ADMITTANCE: "Admittance",
}
label_to_zhit_representation: Dict[str, ZHITRepresentation] = {
    v: k for k, v in zhit_representation_to_label.items()
}
zhit_representation_to_value: Dict[ZHITRepresentation, Optional[bool]] = {
    ZHITRepresentation.IMPEDANCE: False,
    ZHITRepresentation.ADMITTANCE: True,
}
assert set(zhit_representation_to_label.keys()) == set(
    label_to_zhit_representation.values()
), "Duplicate ZHIT representation string labels detected!"
assert set(zhit_representation_to_value.keys()) == set(
    zhit_representation_to_value.keys()
), "Missing ZHIT representation value detected!"
