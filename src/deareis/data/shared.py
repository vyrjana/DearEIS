# Copyright 2022 DearEIS developers
# DearEIS is licensed under the GPLv3 or later (https://www.gnu.org/licenses/gpl-3.0.html).
# The licenses of DearEIS' dependencies and/or sources of portions of code are included in
# the LICENSES folder.

from enum import IntEnum, auto as auto_enum
from typing import Dict


class Weight(IntEnum):
    AUTO = auto_enum()
    UNITY = auto_enum()
    PROPORTIONAL = auto_enum()
    MODULUS = auto_enum()
    BOUKAMP = auto_enum()


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


class Method(IntEnum):
    AUTO = auto_enum()
    LEASTSQ = auto_enum()
    LEAST_SQUARES = auto_enum()
    DIFFERENTIAL_EVOLUTION = auto_enum()
    BRUTE = auto_enum()
    BASINHOPPING = auto_enum()
    AMPGO = auto_enum()
    NELDER = auto_enum()
    LBFGSB = auto_enum()
    POWELL = auto_enum()
    CG = auto_enum()
    NEWTON = auto_enum()
    COBYLA = auto_enum()
    BFGS = auto_enum()
    TNC = auto_enum()
    TRUST_NCG = auto_enum()
    TRUST_EXACT = auto_enum()
    TRUST_KRYLOV = auto_enum()
    TRUST_CONSTR = auto_enum()
    DOGLEG = auto_enum()
    SLSQP = auto_enum()
    EMCEE = auto_enum()
    SHGO = auto_enum()
    DUAL_ANNEALING = auto_enum()


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


class Output:
    CDC_BASIC = auto_enum()
    CDC_EXTENDED = auto_enum()
    CSV_DATA_TABLE = auto_enum()
    CSV_PARAMETERS_TABLE = auto_enum()
    JSON_PARAMETERS_TABLE = auto_enum()
    LATEX_DIAGRAM = auto_enum()
    LATEX_EXPR = auto_enum()
    LATEX_PARAMETERS_TABLE = auto_enum()
    MARKDOWN_PARAMETERS_TABLE = auto_enum()
    SYMPY_EXPR = auto_enum()
    SYMPY_EXPR_VALUES = auto_enum()


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
