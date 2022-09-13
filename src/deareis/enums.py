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

from enum import IntEnum, auto
from typing import Dict, List


class Context(IntEnum):
    PROGRAM = auto()
    PROJECT = auto()
    OVERVIEW_TAB = auto()
    DATA_SETS_TAB = auto()
    KRAMERS_KRONIG_TAB = auto()
    DRT_TAB = auto()
    FITTING_TAB = auto()
    SIMULATION_TAB = auto()
    PLOTTING_TAB = auto()


class Action(IntEnum):
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

    # Project-level: multiple tabs
    PERFORM_ACTION = auto()
    # - Load data set
    # - Perform test
    # - Perform fit
    # - Perform simulation
    # - Create plot
    DELETE_RESULT = auto()
    # - Data set
    # - Test result
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
    # - Fit result
    # - Simulation result
    # - Plot type
    APPLY_SETTINGS = auto()
    # - Kramers-Kronig tab
    # - DRT tab
    # - Fitting tab
    # - Simulation tab
    APPLY_MASK = auto()
    # - Kramers-Kronig tab
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
    # - Fit output
    # - Simulation output

    # Project-level: data sets tab
    AVERAGE_DATA_SETS = auto()
    TOGGLE_DATA_POINTS = auto()
    COPY_DATA_SET_MASK = auto()
    SUBTRACT_IMPEDANCE = auto()

    # Project-level: plotting tab
    SELECT_ALL_PLOT_SERIES = auto()
    UNSELECT_ALL_PLOT_SERIES = auto()
    COPY_PLOT_APPEARANCE = auto()
    COPY_PLOT_DATA = auto()
    EXPAND_COLLAPSE_SIDEBAR = auto()
    EXPORT_PLOT = auto()


action_contexts: Dict[Action, List[Context]] = {
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
    Action.SHOW_CHANGELOG: [Context.PROGRAM],
    Action.CHECK_UPDATES: [Context.PROGRAM],
    Action.SAVE_PROJECT: [Context.PROJECT],
    Action.SAVE_PROJECT_AS: [Context.PROJECT],
    Action.CLOSE_PROJECT: [Context.PROJECT],
    Action.UNDO: [Context.PROJECT],
    Action.REDO: [Context.PROJECT],
    Action.NEXT_PROJECT_TAB: [Context.PROJECT],
    Action.PREVIOUS_PROJECT_TAB: [Context.PROJECT],
    Action.SELECT_DATA_SETS_TAB: [Context.PROJECT],
    Action.SELECT_DRT_TAB: [Context.PROJECT],
    Action.SELECT_FITTING_TAB: [Context.PROJECT],
    Action.SELECT_KRAMERS_KRONIG_TAB: [Context.PROJECT],
    Action.SELECT_OVERVIEW_TAB: [Context.PROJECT],
    Action.SELECT_PLOTTING_TAB: [Context.PROJECT],
    Action.SELECT_SIMULATION_TAB: [Context.PROJECT],
    Action.PERFORM_ACTION: [
        Context.DATA_SETS_TAB,
        Context.KRAMERS_KRONIG_TAB,
        Context.DRT_TAB,
        Context.FITTING_TAB,
        Context.SIMULATION_TAB,
        Context.PLOTTING_TAB,
    ],
    Action.DELETE_RESULT: [
        Context.DATA_SETS_TAB,
        Context.KRAMERS_KRONIG_TAB,
        Context.DRT_TAB,
        Context.FITTING_TAB,
        Context.SIMULATION_TAB,
        Context.PLOTTING_TAB,
    ],
    Action.NEXT_PRIMARY_RESULT: [
        Context.DATA_SETS_TAB,
        Context.KRAMERS_KRONIG_TAB,
        Context.DRT_TAB,
        Context.FITTING_TAB,
        Context.SIMULATION_TAB,
        Context.PLOTTING_TAB,
    ],
    Action.PREVIOUS_PRIMARY_RESULT: [
        Context.DATA_SETS_TAB,
        Context.KRAMERS_KRONIG_TAB,
        Context.DRT_TAB,
        Context.FITTING_TAB,
        Context.SIMULATION_TAB,
        Context.PLOTTING_TAB,
    ],
    Action.NEXT_SECONDARY_RESULT: [
        Context.KRAMERS_KRONIG_TAB,
        Context.DRT_TAB,
        Context.FITTING_TAB,
        Context.SIMULATION_TAB,
        Context.PLOTTING_TAB,
    ],
    Action.PREVIOUS_SECONDARY_RESULT: [
        Context.KRAMERS_KRONIG_TAB,
        Context.DRT_TAB,
        Context.FITTING_TAB,
        Context.SIMULATION_TAB,
        Context.PLOTTING_TAB,
    ],
    Action.APPLY_SETTINGS: [
        Context.KRAMERS_KRONIG_TAB,
        Context.DRT_TAB,
        Context.FITTING_TAB,
        Context.SIMULATION_TAB,
    ],
    Action.APPLY_MASK: [
        Context.KRAMERS_KRONIG_TAB,
        Context.DRT_TAB,
        Context.FITTING_TAB,
    ],
    Action.SHOW_ENLARGED_IMPEDANCE: [
        Context.DRT_TAB,
    ],
    Action.SHOW_ENLARGED_DRT: [
        Context.DRT_TAB,
    ],
    Action.SHOW_ENLARGED_NYQUIST: [
        Context.DATA_SETS_TAB,
        Context.KRAMERS_KRONIG_TAB,
        Context.FITTING_TAB,
        Context.SIMULATION_TAB,
    ],
    Action.SHOW_ENLARGED_BODE: [
        Context.DATA_SETS_TAB,
        Context.KRAMERS_KRONIG_TAB,
        Context.FITTING_TAB,
        Context.SIMULATION_TAB,
    ],
    Action.SHOW_ENLARGED_RESIDUALS: [
        Context.KRAMERS_KRONIG_TAB,
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
    Action.AVERAGE_DATA_SETS: [Context.DATA_SETS_TAB],
    Action.TOGGLE_DATA_POINTS: [Context.DATA_SETS_TAB],
    Action.COPY_DATA_SET_MASK: [Context.DATA_SETS_TAB],
    Action.SUBTRACT_IMPEDANCE: [Context.DATA_SETS_TAB],
    Action.SELECT_ALL_PLOT_SERIES: [Context.PLOTTING_TAB],
    Action.UNSELECT_ALL_PLOT_SERIES: [Context.PLOTTING_TAB],
    Action.COPY_PLOT_APPEARANCE: [Context.PLOTTING_TAB],
    Action.COPY_PLOT_DATA: [Context.PLOTTING_TAB],
    Action.EXPAND_COLLAPSE_SIDEBAR: [Context.PLOTTING_TAB],
    Action.EXPORT_PLOT: [Context.PLOTTING_TAB],
}


action_to_string: Dict[Action, str] = {
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
    Action.LOAD_PROJECT: "load-project",
    Action.NEW_PROJECT: "new-project",
    Action.NEXT_PRIMARY_RESULT: "next-primary-result",
    Action.NEXT_PROGRAM_TAB: "next-program-tab",
    Action.NEXT_PROJECT_TAB: "next-project-tab",
    Action.NEXT_SECONDARY_RESULT: "next-secondary-result",
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
    Action.SELECT_OVERVIEW_TAB: "select-overview-tab",
    Action.SELECT_PLOTTING_TAB: "select-plotting-tab",
    Action.SELECT_SIMULATION_TAB: "select-simulation-tab",
    Action.SHOW_CHANGELOG: "show-changelog",
    Action.SHOW_CIRCUIT_EDITOR: "show-circuit-editor",
    Action.SHOW_COMMAND_PALETTE: "show-command-palette",
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
    Action.SUBTRACT_IMPEDANCE: "subtract-impedance",
    Action.TOGGLE_DATA_POINTS: "toggle-data-points",
    Action.UNDO: "undo",
    Action.UNSELECT_ALL_PLOT_SERIES: "unselect-all-plot-series",
}
string_to_action: Dict[str, Action] = {v: k for k, v in action_to_string.items()}
# Check that there are no duplicate keys
assert len(action_to_string) == len(set(action_to_string.values())) and len(
    action_to_string
) == len(string_to_action), "Duplicate action string keys detected!"


action_descriptions: Dict[Action, str] = {
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
    Action.SELECT_OVERVIEW_TAB: """
Go to the 'Overview' tab.
""".strip(),
    Action.SELECT_PLOTTING_TAB: """
Go to the 'Plotting' tab.
""".strip(),
    Action.SELECT_SIMULATION_TAB: """
Go to the 'Simulation' tab.
""".strip(),
    Action.PERFORM_ACTION: """
Perform the primary action of the current project tab:
- Data sets: select files to load.
- Kramers-Kronig: perform test.
- DRT analysis: perform analysis.
- Fitting: perform fit.
- Simulation: perform simulation.
- Plotting: create a new plot.
""".strip(),
    Action.DELETE_RESULT: """
Delete the current result in the current project tab:
- Data sets: delete the current data set.
- Kramers-Kronig: delete the current test result.
- DRT analysis: delete the current analysis result.
- Fitting: delete the current fit result.
- Simulation: delete the current simulation result.
- Plotting: delete the current plot.
""".strip(),
    Action.NEXT_PRIMARY_RESULT: """
Select the next primary result of the current project tab:
- Data sets: data set.
- Kramers-Kronig: data set.
- DRT analysis: data set.
- Fitting: data set.
- Simulation: data set.
- Plotting: plot.
""".strip(),
    Action.PREVIOUS_PRIMARY_RESULT: """
Select the previous primary result of the current project tab:
- Data sets: data set.
- Kramers-Kronig: data set.
- DRT analysis: data set.
- Fitting: data set.
- Simulation: data set.
- Plotting: plot.
""".strip(),
    Action.NEXT_SECONDARY_RESULT: """
Select the next secondary result of the current project tab:
- Kramers-Kronig: test result.
- DRT analysis: analysis result.
- Fitting: fit result.
- Simulation: simulation result.
- Plotting: plot type.
""".strip(),
    Action.PREVIOUS_SECONDARY_RESULT: """
Select the previous secondary result of the current project tab:
- Kramers-Kronig: test result.
- DRT analysis: analysis result.
- Fitting: fit result.
- Simulation: simulation result.
- Plotting: plot type.
""".strip(),
    Action.APPLY_SETTINGS: """
Apply the settings used in the current secondary result of the current project tab:
- Kramers-Kronig: test result.
- DRT analysis: analysis result.
- Fitting: fit result.
- Simulation: simulation result.
""".strip(),
    Action.APPLY_MASK: """
Apply the mask used in the current secondary result of the current project tab:
- Kramers-Kronig: test result.
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
}
# Check that every action has a description
assert set(action_to_string.keys()) == set(
    action_descriptions.keys()
), "Missing action descriptions detected!"


class CNLSMethod(IntEnum):
    """
    Iterative methods used during complex non-linear least-squares fitting:

    - AUTO: try each method
    - AMPGO
    - BASINHOPPING
    - BFGS
    - BRUTE
    - CG
    - COBYLA
    - DIFFERENTIAL_EVOLUTION
    - DOGLEG
    - DUAL_ANNEALING
    - EMCEE
    - LBFGSB
    - LEASTSQ
    - LEAST_SQUARES
    - NELDER
    - NEWTON
    - POWELL
    - SHGO
    - SLSQP
    - TNC
    - TRUST_CONSTR
    - TRUST_EXACT
    - TRUST_KRYLOV
    - TRUST_NCG
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


class TestMode(IntEnum):
    """
    Types of modes that determine how the number of Voigt elements (capacitor connected in parallel with resistor) is chosen:

    - AUTO: follow procedure described by Schönleber, Klotz, and Ivers-Tiffée (2014)
    - EXPLORATORY: same procedure as AUTO but present intermediate results to user and apply additional weighting to the initial suggestion
    - MANUAL: manually choose the number
    """

    AUTO = 1
    EXPLORATORY = 2
    MANUAL = 3


test_mode_to_label: Dict[TestMode, str] = {
    TestMode.AUTO: "Auto",
    TestMode.EXPLORATORY: "Exploratory",
    TestMode.MANUAL: "Manual",
}
label_to_test_mode: Dict[str, TestMode] = {v: k for k, v in test_mode_to_label.items()}
assert set(test_mode_to_label.keys()) == set(
    label_to_test_mode.values()
), "Duplicate test mode string labels detected!"


class FitSimOutput(IntEnum):
    CDC_BASIC = auto()
    CDC_EXTENDED = auto()
    CSV_DATA_TABLE = auto()
    CSV_PARAMETERS_TABLE = auto()
    JSON_PARAMETERS_TABLE = auto()
    LATEX_DIAGRAM = auto()
    LATEX_EXPR = auto()
    LATEX_PARAMETERS_TABLE = auto()
    MARKDOWN_PARAMETERS_TABLE = auto()
    SVG_DIAGRAM = auto()
    SYMPY_EXPR = auto()
    SYMPY_EXPR_VALUES = auto()


fit_sim_output_to_label: Dict[FitSimOutput, str] = {
    FitSimOutput.CDC_BASIC: "CDC - basic",
    FitSimOutput.CDC_EXTENDED: "CDC - extended",
    FitSimOutput.CSV_DATA_TABLE: "CSV - impedance table",
    FitSimOutput.CSV_PARAMETERS_TABLE: "CSV - parameters table",
    FitSimOutput.JSON_PARAMETERS_TABLE: "JSON - parameters table",
    FitSimOutput.LATEX_DIAGRAM: "LaTeX - circuit diagram",
    FitSimOutput.LATEX_EXPR: "LaTeX - expression",
    FitSimOutput.LATEX_PARAMETERS_TABLE: "LaTeX - parameters table",
    FitSimOutput.MARKDOWN_PARAMETERS_TABLE: "Markdown - parameters table",
    FitSimOutput.SVG_DIAGRAM: "SVG - circuit diagram",
    FitSimOutput.SYMPY_EXPR: "SymPy - expression",
    FitSimOutput.SYMPY_EXPR_VALUES: "SymPy - expression and values",
}
label_to_fit_sim_output: Dict[str, FitSimOutput] = {
    v: k for k, v in fit_sim_output_to_label.items()
}
assert set(fit_sim_output_to_label.keys()) == set(
    label_to_fit_sim_output.values()
), "Duplicate output string labels detected!"


class PlotType(IntEnum):
    """
    Types of plots:

    - NYQUIST: -Zim vs Zre
    - BODE_MAGNITUDE: |Z| vs f
    - BODE_PHASE: phi vs f
    - DRT: gamma vs tau
    - IMPEDANCE_REAL: Zre vs f
    - IMPEDANCE_IMAGINARY: Zim vs f
    """

    NYQUIST = 1
    BODE_MAGNITUDE = 2
    BODE_PHASE = 3
    IMPEDANCE_REAL = 4
    IMPEDANCE_IMAGINARY = 5
    DRT = 6


plot_type_to_label: Dict[PlotType, str] = {
    PlotType.NYQUIST: "Nyquist",
    PlotType.BODE_MAGNITUDE: "Bode - magnitude",
    PlotType.BODE_PHASE: "Bode - phase",
    PlotType.IMPEDANCE_REAL: "Impedance - real",
    PlotType.IMPEDANCE_IMAGINARY: "Impedance - imaginary",
    PlotType.DRT: "Distribution of relaxation times",
}
label_to_plot_type: Dict[str, PlotType] = {v: k for k, v in plot_type_to_label.items()}
assert set(plot_type_to_label.keys()) == set(
    label_to_plot_type.values()
), "Duplicate plot type string labels detected!"


class Test(IntEnum):
    """
    Types of Kramers-Kronig tests:

    - CNLS: complex non-linear least-squares fit of circuit (fig. 1, Boukamp, 1995) with a distribution of fixed time constants
    - COMPLEX: eqs. 11 and 12, Boukamp, 1995
    - IMAGINARY: eqs. 4, 6, and 7, Boukamp, 1995
    - REAL: eqs. 5, 8, 9, and 10, Boukamp, 1995
    """

    CNLS = 1
    COMPLEX = 2
    IMAGINARY = 3
    REAL = 4


test_to_label: Dict[Test, str] = {
    Test.CNLS: "CNLS",
    Test.COMPLEX: "Complex",
    Test.IMAGINARY: "Imaginary",
    Test.REAL: "Real",
}
label_to_test: Dict[str, Test] = {v: k for k, v in test_to_label.items()}
test_to_value: Dict[Test, str] = {
    Test.CNLS: "cnls",
    Test.COMPLEX: "complex",
    Test.IMAGINARY: "imaginary",
    Test.REAL: "real",
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
    - BOUKAMP: 1 / (Zre^2 + Zim^2) (eq. 13, Boukamp, 1995)
    - MODULUS: 1 / |Z|
    - PROPORTIONAL: 1 / Zre^2, 1 / Zim^2
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
    """
    TR_NNLS = 1
    TR_RBF = 2
    BHT = 3


drt_method_to_label: Dict[DRTMethod, str] = {
    DRTMethod.BHT: "BHT",
    DRTMethod.TR_NNLS: "TR-NNLS",
    DRTMethod.TR_RBF: "TR-RBF",
}
label_to_drt_method: Dict[str, DRTMethod] = {
    v: k for k, v in drt_method_to_label.items()
}
drt_method_to_value: Dict[DRTMethod, str] = {
    DRTMethod.BHT: "bht",
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
