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
from deareis.tooltips.kramers_kronig import boukamp1995


fitting = SimpleNamespace(
    **{
        "cdc": """
The equivalent circuit to fit to the data. A circuit description code (CDC) can be typed in to define the equivalent circuit. Alternatively, the graphical circuit editor can be used to construct the equivalent circuit.
    """.strip(),
        "method": """
See the documentation for the 'lmfit' Python package for information about the fitting methods.

The 'Auto' setting performs parallel fits with each of the fitting methods and returns the result with the smallest chi-squared value.
    """.strip(),
        "weight": f"""
The 'Auto' setting performs parallel fits with each of the weight functions listed above and returns the results with the smallest chi-squared value.

Reference: {boukamp1995}
    """.strip(),
        "nfev": """
The maximum number of function evaluations to perform. This setting can be used to limit the amount of time spent performing a fit. If this setting is set to zero, then no limit is applied.
    """.strip(),
        "perform": """
Sometimes a circuit, which ostensibly should be capable of providing a good fit, does not fit well. If the starting values of the parameters have been left at their default values, then rough adjustments may be all that is required. For example, if a circuit contains two parallel RC subcircuits in series (i.e. the CDC contains '(RC)(RC)'), then setting one of the capacitances to be one order of magnitude greater than the other may be sufficient.

Setting both the fitting method and weight function to 'Auto' is recommended as the starting point. Some of the various combinations of fitting methods and weight functions may be more forgiving than others regarding starting values for a particular circuit and thus require less work on the part of the user to achieve a good fit.

The fitting is performed using the Python package called lmfit. That package provides estimates for the error of the fitted parameters whenever possible. Circumstances when it is not possible to provide such estimates include e.g. when a parameter is near its lower/upper limit if such a limit has been defined. A parameter with a large error estimate is indicative of that parameter not really affecting the fit at all. For example, an unnecessary Warburg diffusion element may have its admittance parameter, Y, set to be a very large value and thus the element contributes very little to the overall impedance of the circuit within the frequency range of the experimental data.
    """.strip(),
        "chisqr": """
The chi-squared value of the fit.
    """.strip(),
        "red_chisqr": """
The reduced chi-squared value of the fit.
    """.strip(),
        "aic": """
The Akaike information criterion.
    """.strip(),
        "bic": """
The Bayesian information criterion.
    """.strip(),
        "nfree": """
The degrees of freedom in the fit.
    """.strip(),
        "ndata": """
The number of data points in the fit.
    """.strip(),
        "element": """
An element in the equivalent circuit.
    """.strip(),
        "parameter": """
A parameter in the element.
    """.strip(),
        "parameter_value": """
The fitted value of the parameter.
    """.strip(),
        "error": """
The estimated standard error of the fitted value.
    """.strip(),
        "delete": """
Delete the current fit result.
    """.strip(),
    }
)
