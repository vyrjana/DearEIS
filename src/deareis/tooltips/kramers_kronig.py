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


boukamp1995: str = "DOI:10.1149/1.2044210"
schonleber2014: str = "DOI:10.1016/j.electacta.2014.01.034"

kramers_kronig = SimpleNamespace(
    **{
        "test": f"""
Fit an equivalent circuit (Voigt circuit, fig. 1) to an impedance spectrum.

CNLS: Use complex non-linear least squares fitting.

Complex: Use a set of linear equations to fit to the complex impedance (eq. 12).

Imaginary: Use a set of linear equations to fit to the imaginary part of the complex impedance (eqs. 4 and 7).

Real: Use a set of linear equations to fit to the real part of the complex impedance (eqs. 8 and 10).

Reference: {boukamp1995}
    """.strip(),
        "mode": f"""
Auto: Increment the number of RC elements, calculate the µ-value (eq. 21), and use the µ-criterion to determine when to stop.

Exploratory: Test multiple numbers of RC elements similarly to the 'Auto' setting, show all the results, and let the user choose one.

Manual: Choose a specific number of RC elements to use.

Reference: {schonleber2014}
    """.strip(),
        "max_num_RC": """
The (maximum) number of RC elements connected in series in the equivalent circuit.

WARNING! If the test is set to 'CNLS' and the mode is set to 'Exploratory', then it may take a long time to perform the test. It is recommended that you initially lower this setting to e.g. thirty if there are more measured frequencies than that in your data set.
    """.strip(),
        "add_capacitance": """
Add a capacitor in series to the equivalent circuit. This may be necessary in some circumstances such as if the imaginary part of the spectrum does not approach zero when the frequency is decreased.
    """.strip(),
        "add_inductance": """
Add an inductor in series to the equivalent circuit. This may be necessary in some circumstances and is enabled by default for all but the 'CNLS' test.
    """.strip(),
        "mu_criterion": f"""
The µ-value represents how the equivalent circuit fits the data (eq. 21). µ-values range from zero to one with the extremes representing over-fitting and under-fitting, respectively. Over-fitting is undesirable since the equivalent circuit could end up reproducing any noise that may be present in the data. However, too much under-fitting means that the equivalent circuit is unable to reproduce the data.

The µ-criterion defines the threshold at which no more RC elements are added to the equivalent circuit. Note that in some cases the calculated µ-value may prematurely and temporarily drop below the threshold set by the µ-criterion when performing the test using the 'Auto' mode.

The 'Exploratory' mode is recommended since you can inspect the µ-value produced by various other equivalent circuits and see if the number of RC elements by the 'Auto' mode was erroneous. Note that the number of RC elements initially suggested by the 'Exploratory' mode also takes into account factors other than the µ-value. Thus, the two modes may suggest different values for the number of RC elements.

This setting is only used when the mode setting is set to either 'Auto' or 'Exploratory'.

Reference: {schonleber2014}
    """.strip(),
        "method": """
The iterative method used to perform the fitting.

This setting is only used when the test setting is set to 'CNLS'.
    """.strip(),
        "nfev": """
The maximum number of function evaluations to use when fitting. This can be used to limit the amount of time spent performing a fit. A value of zero means that there is no limit.

This setting is only used when the test setting is set to 'CNLS'.
    """.strip(),
        "perform": f"""
The purpose of the Kramers-Kronig test is to help validate the linearity and time-invariance of impedance spectra. Multiple variants of the linear Kramers-Kronig test are implemented in this program. This test involves fitting an equivalent circuit, which is known to be Kramers-Kronig transformable, to an impedance spectrum.

The default settings (i.e. 'Complex' test and 'Exploratory' mode) are recommended at least as a starting point.

Valid spectra typically exhibit:
- Randomly distributed residuals that are centered along the x-axis.
- Residuals with small magnitudes (e.g. less than half of a percent). Note that the residuals of noisy impedance spectra may have a greater magnitude and still be valid.

Invalid spectra typically exhibit:
- Residuals that are not randomly distributed. Note that if the number of RC elements used to perform the test is too small, then the residuals may form a sinusoidal pattern.
- Residuals that are clearly biased away from the x-axis. For example, residuals may increasinly diverge from the x-axis as the frequency is decreased or they may form a convex/concave shape.

See the following references for more information about the linear Kramers-Kronig tests:

- {boukamp1995}

- {schonleber2014}

Analysing the contributions of higher-order harmonics to the response signal is another way of checking for non-linearity. Potentiostat/galvanostat manufacturers may implement this in different ways and use different terminology may be used in their documentation. For example, "total harmonic distortion" (THD) may be available as a setting in the measurement method. Alternatively, it may be possible to record the response signal for processing and analysis (e.g., Fourier transform).
    """.strip(),
        "delete": """
Delete the current test result.
    """.strip(),
        "pseudo_chisqr": f"""
Pseudo chi-squared value calculated according to eq. 14.

Reference: {boukamp1995}
    """.strip(),
        "exploratory_result": """
The result to highlight and ultimately save.
    """.strip(),
        "mu": f"""
The µ-value represents how the equivalent circuit fits the data (eq. 21). µ-values range from zero to one with the extremes representing over-fitting and under-fitting, respectively.

Reference: {schonleber2014}
    """.strip(),
        "num_RC": """
The number of RC elements connected in series in the equivalent circuit.
    """.strip(),
    }
)
