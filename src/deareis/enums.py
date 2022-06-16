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

    # Project-level
    SAVE_PROJECT = auto()
    SAVE_PROJECT_AS = auto()
    CLOSE_PROJECT = auto()
    UNDO = auto()
    REDO = auto()
    NEXT_PROJECT_TAB = auto()
    PREVIOUS_PROJECT_TAB = auto()
    SELECT_DATA_SETS_TAB = auto()
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
    # - Fitting tab
    # - Simulation tab
    APPLY_MASK = auto()
    # - Kramers-Kronig tab
    # - Fitting tab
    SHOW_ENLARGED_NYQUIST = auto()
    SHOW_ENLARGED_BODE = auto()
    SHOW_ENLARGED_RESIDUALS = auto()
    SHOW_CIRCUIT_EDITOR = auto()
    # - Fitting tab
    # - Simulation tab
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
    Action.SAVE_PROJECT: [Context.PROJECT],
    Action.SAVE_PROJECT_AS: [Context.PROJECT],
    Action.CLOSE_PROJECT: [Context.PROJECT],
    Action.UNDO: [Context.PROJECT],
    Action.REDO: [Context.PROJECT],
    Action.NEXT_PROJECT_TAB: [Context.PROJECT],
    Action.PREVIOUS_PROJECT_TAB: [Context.PROJECT],
    Action.SELECT_DATA_SETS_TAB: [Context.PROJECT],
    Action.SELECT_FITTING_TAB: [Context.PROJECT],
    Action.SELECT_KRAMERS_KRONIG_TAB: [Context.PROJECT],
    Action.SELECT_OVERVIEW_TAB: [Context.PROJECT],
    Action.SELECT_PLOTTING_TAB: [Context.PROJECT],
    Action.SELECT_SIMULATION_TAB: [Context.PROJECT],
    Action.PERFORM_ACTION: [
        Context.DATA_SETS_TAB,
        Context.KRAMERS_KRONIG_TAB,
        Context.FITTING_TAB,
        Context.SIMULATION_TAB,
        Context.PLOTTING_TAB,
    ],
    Action.DELETE_RESULT: [
        Context.DATA_SETS_TAB,
        Context.KRAMERS_KRONIG_TAB,
        Context.FITTING_TAB,
        Context.SIMULATION_TAB,
        Context.PLOTTING_TAB,
    ],
    Action.NEXT_PRIMARY_RESULT: [
        Context.DATA_SETS_TAB,
        Context.KRAMERS_KRONIG_TAB,
        Context.FITTING_TAB,
        Context.SIMULATION_TAB,
        Context.PLOTTING_TAB,
    ],
    Action.PREVIOUS_PRIMARY_RESULT: [
        Context.DATA_SETS_TAB,
        Context.KRAMERS_KRONIG_TAB,
        Context.FITTING_TAB,
        Context.SIMULATION_TAB,
        Context.PLOTTING_TAB,
    ],
    Action.NEXT_SECONDARY_RESULT: [
        Context.KRAMERS_KRONIG_TAB,
        Context.FITTING_TAB,
        Context.SIMULATION_TAB,
        Context.PLOTTING_TAB,
    ],
    Action.PREVIOUS_SECONDARY_RESULT: [
        Context.KRAMERS_KRONIG_TAB,
        Context.FITTING_TAB,
        Context.SIMULATION_TAB,
        Context.PLOTTING_TAB,
    ],
    Action.APPLY_SETTINGS: [
        Context.KRAMERS_KRONIG_TAB,
        Context.FITTING_TAB,
        Context.SIMULATION_TAB,
    ],
    Action.APPLY_MASK: [
        Context.KRAMERS_KRONIG_TAB,
        Context.FITTING_TAB,
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
        Context.FITTING_TAB,
    ],
    Action.SHOW_CIRCUIT_EDITOR: [
        Context.FITTING_TAB,
        Context.SIMULATION_TAB,
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
        Context.FITTING_TAB,
    ],
    Action.COPY_OUTPUT: [
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
}


action_to_string: Dict[Action, str] = {
    Action.NEW_PROJECT: "new-project",
    Action.LOAD_PROJECT: "load-project",
    Action.EXIT: "exit-program",
    Action.NEXT_PROGRAM_TAB: "next-program-tab",
    Action.PREVIOUS_PROGRAM_TAB: "previous-program-tab",
    Action.SELECT_HOME_TAB: "select-home-tab",
    Action.SHOW_HELP_ABOUT: "show-help-about",
    Action.SHOW_HELP_LICENSES: "show-help-licenses",
    Action.SHOW_SETTINGS_APPEARANCE: "show-settings-appearance",
    Action.SHOW_SETTINGS_DEFAULTS: "show-settings-defaults",
    Action.SHOW_SETTINGS_KEYBINDINGS: "show-settings-keybindings",
    Action.SHOW_COMMAND_PALETTE: "show-command-palette",
    Action.SAVE_PROJECT: "save-project",
    Action.SAVE_PROJECT_AS: "save-project-as",
    Action.CLOSE_PROJECT: "close-project",
    Action.UNDO: "undo",
    Action.REDO: "redo",
    Action.NEXT_PROJECT_TAB: "next-project-tab",
    Action.PREVIOUS_PROJECT_TAB: "previous-project-tab",
    Action.SELECT_DATA_SETS_TAB: "select-data-sets-tab",
    Action.SELECT_FITTING_TAB: "select-fitting-tab",
    Action.SELECT_KRAMERS_KRONIG_TAB: "select-kramers-kronig-tab",
    Action.SELECT_OVERVIEW_TAB: "select-overview-tab",
    Action.SELECT_PLOTTING_TAB: "select-plotting-tab",
    Action.SELECT_SIMULATION_TAB: "select-simulation-tab",
    Action.PERFORM_ACTION: "perform-action",
    Action.DELETE_RESULT: "delete-result",
    Action.NEXT_PRIMARY_RESULT: "next-primary-result",
    Action.PREVIOUS_PRIMARY_RESULT: "previous-primary-result",
    Action.NEXT_SECONDARY_RESULT: "next-secondary-result",
    Action.PREVIOUS_SECONDARY_RESULT: "previous-secondary-result",
    Action.APPLY_SETTINGS: "apply-settings",
    Action.APPLY_MASK: "apply-mask",
    Action.SHOW_ENLARGED_NYQUIST: "show-enlarged-nyquist",
    Action.SHOW_ENLARGED_BODE: "show-enlarged-bode",
    Action.SHOW_ENLARGED_RESIDUALS: "show-enlarged-residuals",
    Action.SHOW_CIRCUIT_EDITOR: "show-circuit-editor",
    Action.COPY_NYQUIST_DATA: "copy-nyquist-data",
    Action.COPY_BODE_DATA: "copy-bode-data",
    Action.COPY_RESIDUALS_DATA: "copy-residuals-data",
    Action.COPY_OUTPUT: "copy-output",
    Action.AVERAGE_DATA_SETS: "average-data-sets",
    Action.TOGGLE_DATA_POINTS: "toggle-data-points",
    Action.COPY_DATA_SET_MASK: "copy-data-set-mask",
    Action.SUBTRACT_IMPEDANCE: "subtract-impedance",
    Action.SELECT_ALL_PLOT_SERIES: "select-all-plot-series",
    Action.UNSELECT_ALL_PLOT_SERIES: "unselect-all-plot-series",
    Action.COPY_PLOT_APPEARANCE: "copy-plot-appearance",
    Action.COPY_PLOT_DATA: "copy-plot-data",
    Action.EXPAND_COLLAPSE_SIDEBAR: "expand-collapse-sidebar",
}
string_to_action: Dict[str, Action] = {v: k for k, v in action_to_string.items()}


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
- Fitting: perform fit.
- Simulation: perform simulation.
- Plotting: create a new plot.
""".strip(),
    Action.DELETE_RESULT: """
Delete the current result in the current project tab:
- Data sets: delete the current data set.
- Kramers-Kronig: delete the current test result.
- Fitting: delete the current fit result.
- Simulation: delete the current simulation result.
- Plotting: delete the current plot.
""".strip(),
    Action.NEXT_PRIMARY_RESULT: """
Select the next primary result of the current project tab:
- Data sets: data set.
- Kramers-Kronig: data set.
- Fitting: data set.
- Simulation: data set.
- Plotting: plot.
""".strip(),
    Action.PREVIOUS_PRIMARY_RESULT: """
Select the previous primary result of the current project tab:
- Data sets: data set.
- Kramers-Kronig: data set.
- Fitting: data set.
- Simulation: data set.
- Plotting: plot.
""".strip(),
    Action.NEXT_SECONDARY_RESULT: """
Select the next secondary result of the current project tab:
- Kramers-Kronig: test result.
- Fitting: fit result.
- Simulation: simulation result.
- Plotting: plot type.
""".strip(),
    Action.PREVIOUS_SECONDARY_RESULT: """
Select the previous secondary result of the current project tab:
- Kramers-Kronig: test result.
- Fitting: fit result.
- Simulation: simulation result.
- Plotting: plot type.
""".strip(),
    Action.APPLY_SETTINGS: """
Apply the settings used in the current secondary result of the current project tab:
- Kramers-Kronig: test result.
- Fitting: fit result.
- Simulation: simulation result.
""".strip(),
    Action.APPLY_MASK: """
Apply the mask used in the current secondary result of the current project tab:
- Kramers-Kronig: test result.
- Fitting: fit result.
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
Copy the chosen output while in the 'Fitting' or the 'Simulation' tab.
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
}


class Method(IntEnum):
    AUTO = auto()
    LEASTSQ = auto()
    LEAST_SQUARES = auto()
    DIFFERENTIAL_EVOLUTION = auto()
    BRUTE = auto()
    BASINHOPPING = auto()
    AMPGO = auto()
    NELDER = auto()
    LBFGSB = auto()
    POWELL = auto()
    CG = auto()
    NEWTON = auto()
    COBYLA = auto()
    BFGS = auto()
    TNC = auto()
    TRUST_NCG = auto()
    TRUST_EXACT = auto()
    TRUST_KRYLOV = auto()
    TRUST_CONSTR = auto()
    DOGLEG = auto()
    SLSQP = auto()
    EMCEE = auto()
    SHGO = auto()
    DUAL_ANNEALING = auto()


label_to_method: Dict[str, Method] = {
    "Levenberg-Marquardt": Method.LEASTSQ,
    "Least-squares (trust-region reflective)": Method.LEAST_SQUARES,
    "Powell": Method.POWELL,  # Had some problem fitting
    "BFGS": Method.BFGS,  # Had some problem fitting
    "Nelder-Mead": Method.NELDER,  # Had some problem fitting
    "Conjugate Gradient": Method.CG,  # Had some problem fitting
    "Truncated Newton": Method.TNC,  # Had some problem fitting
    "L-BFGS-B": Method.LBFGSB,  # NaN errors
    # "COBYLA": Method.COBYLA,  # Had some problem fitting
    "Sequential Linear Squares Programming": Method.SLSQP,  # Had some problem fitting
    # "Basin hopping": Method.BASINHOPPING,  # NaN errors
    # "Differential Evolution": Method.DIFFERENTIAL_EVOLUTION,  # Requires finite bounds for all mutable parameters
    # "Brute force method": Method.BRUTE,  # Requires that brute_step is defined for mutable parameters
    # "Adaptive Memory Programming for Global Optimization": Method.AMPGO,  # NaN errors
    # "Newton": Method.NEWTON,  # Requires Jacobian
    # "Newton CG": Method.TRUST_NCG,  # Requires Jacobian for trust region
    # "Exact trust-region": Method.TRUST_EXACT,  # Requires Jacobian for trust region
    # "Newton GLTR trust-region": Method.TRUST_KRYLOV,  # Requires Jacobian for trust region
    # "Constrained trust-region": Method.TRUST_CONSTR,  # NaN errors
    # "Dog-leg trust-region": Method.DOGLEG,  # Requires Jacobian
    # "Simplicial Homology Global Optimization": Method.SHGO,  # NaN errors
    # "Dual Annealing": Method.DUAL_ANNEALING,  # Requires finite bounds for all mutable parameters
    # "Maximum likelyhood via Monte-Carlo Markov chain": Method.EMCEE,  # Requires the emcee package (version 3)
}
method_to_label: Dict[Method, str] = {v: k for k, v in label_to_method.items()}
method_to_label[Method.AUTO] = "Auto"
method_to_value: Dict[Method, str] = {
    Method.AUTO: "auto",
    Method.LEASTSQ: "leastsq",
    Method.LEAST_SQUARES: "least_squares",
    Method.DIFFERENTIAL_EVOLUTION: "differential_evolution",
    Method.BRUTE: "brute",
    Method.BASINHOPPING: "basinhopping",
    Method.AMPGO: "ampgo",
    Method.NELDER: "nelder",
    Method.LBFGSB: "lbfgsb",
    Method.POWELL: "powell",
    Method.CG: "cg",
    Method.NEWTON: "newton",
    Method.COBYLA: "cobyla",
    Method.BFGS: "bfgs",
    Method.TNC: "tnc",
    Method.TRUST_NCG: "trust-ncg",
    Method.TRUST_EXACT: "trust-exact",
    Method.TRUST_KRYLOV: "trust-krylov",
    Method.TRUST_CONSTR: "trust-constr",
    Method.DOGLEG: "dogleg",
    Method.SLSQP: "slsqp",
    Method.EMCEE: "emcee",
    Method.SHGO: "shgo",
    Method.DUAL_ANNEALING: "dual_annealing",
}
value_to_method: Dict[str, Method] = {v: k for k, v in method_to_value.items()}


class Mode(IntEnum):
    AUTO = auto()
    EXPLORATORY = auto()
    MANUAL = auto()


label_to_mode: Dict[str, Mode] = {
    "Auto": Mode.AUTO,
    "Exploratory": Mode.EXPLORATORY,
    "Manual": Mode.MANUAL,
}
mode_to_label: Dict[Mode, str] = {v: k for k, v in label_to_mode.items()}


class Output:
    CDC_BASIC = auto()
    CDC_EXTENDED = auto()
    CSV_DATA_TABLE = auto()
    CSV_PARAMETERS_TABLE = auto()
    JSON_PARAMETERS_TABLE = auto()
    LATEX_DIAGRAM = auto()
    LATEX_EXPR = auto()
    LATEX_PARAMETERS_TABLE = auto()
    MARKDOWN_PARAMETERS_TABLE = auto()
    SYMPY_EXPR = auto()
    SYMPY_EXPR_VALUES = auto()


label_to_output: Dict[str, Output] = {
    "CDC - basic": Output.CDC_BASIC,
    "CDC - extended": Output.CDC_EXTENDED,
    "CSV - impedance table": Output.CSV_DATA_TABLE,
    "CSV - parameters table": Output.CSV_PARAMETERS_TABLE,
    "JSON - parameters table": Output.JSON_PARAMETERS_TABLE,
    "LaTeX - circuit diagram": Output.LATEX_DIAGRAM,
    "LaTeX - expression": Output.LATEX_EXPR,
    "LaTeX - parameters table": Output.LATEX_PARAMETERS_TABLE,
    "Markdown - parameters table": Output.MARKDOWN_PARAMETERS_TABLE,
    "SymPy - expression": Output.SYMPY_EXPR,
    "SymPy - expression and values": Output.SYMPY_EXPR_VALUES,
}
output_to_label: Dict[Output, str] = {v: k for k, v in label_to_output.items()}


class PlotType(IntEnum):
    """
Types of plots:

- NYQUIST
- BODE_MAGNITUDE
- BODE_PHASE
    """
    NYQUIST = auto()
    BODE_MAGNITUDE = auto()
    BODE_PHASE = auto()


label_to_plot_type: Dict[str, PlotType] = {
    "Nyquist": PlotType.NYQUIST,
    "Bode - magnitude": PlotType.BODE_MAGNITUDE,
    "Bode - phase": PlotType.BODE_PHASE,
}
plot_type_to_label: Dict[PlotType, str] = {v: k for k, v in label_to_plot_type.items()}


class Test(IntEnum):
    CNLS = auto()
    COMPLEX = auto()
    IMAGINARY = auto()
    REAL = auto()


label_to_test: Dict[str, Test] = {
    "CNLS": Test.CNLS,
    "Complex": Test.COMPLEX,
    "Imaginary": Test.IMAGINARY,
    "Real": Test.REAL,
}
test_to_label: Dict[Test, str] = {v: k for k, v in label_to_test.items()}
test_to_value: Dict[Test, str] = {
    Test.CNLS: "cnls",
    Test.COMPLEX: "complex",
    Test.IMAGINARY: "imaginary",
    Test.REAL: "real",
}


class Weight(IntEnum):
    AUTO = auto()
    UNITY = auto()
    PROPORTIONAL = auto()
    MODULUS = auto()
    BOUKAMP = auto()


label_to_weight: Dict[str, Weight] = {
    "Modulus": Weight.MODULUS,
    "Proportional": Weight.PROPORTIONAL,
    "Unity": Weight.UNITY,
    "Boukamp": Weight.BOUKAMP,
}
weight_to_label: Dict[Weight, str] = {v: k for k, v in label_to_weight.items()}
weight_to_label[Weight.AUTO] = "Auto"
weight_to_value: Dict[Weight, str] = {
    Weight.AUTO: "auto",
    Weight.UNITY: "unity",
    Weight.PROPORTIONAL: "proportional",
    Weight.MODULUS: "modulus",
    Weight.BOUKAMP: "boukamp",
}
value_to_weight: Dict[str, Weight] = {v: k for k, v in weight_to_value.items()}
