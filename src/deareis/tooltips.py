# Copyright 2022 DearEIS developers
# DearEIS is licensed under the GPLv3 or later (https://www.gnu.org/licenses/gpl-3.0.html).
# The licenses of DearEIS' dependencies and/or sources of portions of code are included in
# the LICENSES folder.

BOUKAMP1995: str = "Bernard A. Boukamp, 'A Linear Kronig-Kramers Transform Test for Immittance Data Validation', Journal of the Electrochemical Society, 1995, vol. 142, no. 6, pp. 1885-1894."
SCHONLEBER2014: str = "M. Schönleber, D. Klotz, and E. Ivers-Tiffée, 'A Method for Improving the Robustness of linear Kramers-Kronig Validity Tests', Electrochimica Acta, 2014, vol. 131, pp. 20-27."

datasets_load: str = "Select files to load as new data sets."

datasets_remove: str = "Remove the current data set."

datasets_average: str = "Create a new data set by averaging multiple data sets."

datasets_toggle: str = "Toggle a range of points."

datasets_copy: str = "Copy the mask from another data set."

datasets_subtract: str = "Subtract impedance from the current spectrum."

kramers_kronig_test: str = f"""
Fit an equivalent circuit (Voigt circuit, fig. 1) to an impedance spectrum.

CNLS: Use complex non-linear least squares fitting.

Complex: Use a set of linear equations to fit to the complex impedance (eq. 12).

Imaginary: Use a set of linear equations to fit to the imaginary part of the complex impedance (eqs. 4 and 7).

Real: Use a set of linear equations to fit to the real part of the complex impedance (eqs. 8 and 10).

{BOUKAMP1995}
""".strip()

kramers_kronig_mode: str = f"""
Auto: Increment the number of parallel RC circuits, calculate the µ-value (eq. 21), and use the µ-criterion to determine when to stop.

Exploratory: Test multiple numbers of parallel RC circuits similarly to the 'Auto' setting, show all the results, and let the user choose one.

Manual: Choose a specific number of parallel RC circuits to use.

{SCHONLEBER2014}
""".strip()

kramers_kronig_num_RC: str = """
The (maximum) number of parallel RC circuits connected in series in the equivalent circuit.

WARNING! If the test is set to 'CNLS' and the mode is set to 'Exploratory', then it may take a long time to perform the test. It is recommended that you initially lower this setting to e.g. thirty if there are more measured frequencies than that in your data set.
""".strip()

kramers_kronig_add_cap: str = """
Add a capacitor in series to the equivalent circuit. This may be necessary in some circumstances such as if the imaginary part of the spectrum does not approach zero when the frequency is decreased.
""".strip()

kramers_kronig_add_ind: str = """
Add an inductor in series to the equivalent circuit. This may be necessary in some circumstances and is enabled by default for all but the 'CNLS' test.
""".strip()

kramers_kronig_mu_crit: str = f"""
The µ-value represents how the equivalent circuit fits the data (eq. 21). µ-values range from zero to one with the extremes representing over-fitting and under-fitting, respectively. Over-fitting is undesirable since the equivalent circuit could end up reproducing any noise that may be present in the data. However, too much under-fitting means that the equivalent circuit is unable to reproduce the data.

The µ-criterion defines the threshold at which no more parallel RC circuits are added to the equivalent circuit. Note that in some cases the calculated µ-value may prematurely and temporarily drop below the threshold set by the µ-criterion when performing the test using the 'Auto' mode.

The 'Exploratory' mode is recommended since you can inspect the µ-value produced by various other equivalent circuits and see if the number of RC circuits by the 'Auto' mode was erroneous. Note that the number of RC circuits initially suggested by the 'Exploratory' mode also takes into account factors other than the µ-value. Thus, the two modes may suggest different values for the number of RC circuits.

This setting is only used when the mode setting is set to either 'Auto' or 'Exploratory'.

{SCHONLEBER2014}
""".strip()

kramers_kronig_method: str = """
The iterative method used to perform the fitting.

This setting is only used when the test setting is set to 'CNLS'.
""".strip()

kramers_kronig_nfev: str = """
The maximum number of function evaluations to use when fitting. This can be used to limit the amount of time spent performing a fit. A value of zero means that there is no limit.

This setting is only used when the test setting is set to 'CNLS'.
""".strip()

kramers_kronig_perform: str = f"""
The purpose of the Kramers-Kronig test is to help validate the linearity and time-invariance of impedance spectra. Multiple variants of the linear Kramers-Kronig test are implemented in this program. This test involves fitting an equivalent circuit, which is known to be Kramers-Kronig transformable, to an impedance spectrum.

The default settings (i.e. 'Complex' test and 'Exploratory' mode) are recommended at least as a starting point.

Valid spectra typically exhibit:
- Residuals that are randomly distributed.
- Residuals that are centered along the x-axis.
- Residuals of relatively small magnitude e.g. less than one percent. Note that the residuals of noisy impedance spectra may be greater and the spectra may still be valid.

Invalid spectra typically exhibit:
- Residuals that are not randomly distributed. Note that if the number of RC circuits used to perform the test is too small, then the residuals may form a sinusoidal pattern.
- Residuals that are clearly biased away from the x-axis. For example, residuals may increasinly diverge from the x-axis (e.g. trending up or down as the frequency is decreased).

See the following references for more information about the linear Kramers-Kronig tests:
- {BOUKAMP1995}
- {SCHONLEBER2014}

Analysing the contribution of higher order harmonics to the response signal is another way of checking for non-linearity. However, this requires access to the response signal data itself rather than the final impedance data produced from the excitation and response signals.
""".strip()

kramers_kronig_pseudo_chisqr: str = f"""
Pseudo chi-squared value calculated according to eq. 14.

{BOUKAMP1995}
""".strip()

kramers_kronig_exploratory_result: str = "The result to highlight and ultimately save."

fitting_cdc: str = """
The equivalent circuit to fit to data. A circuit description code (CDC) can be typed in to define the equivalent circuit. Alternatively, the circuit editor can be used to construct the equivalent circuit.
""".strip()

fitting_method: str = """
See the documentation for the 'lmfit' Python package for information about the fitting methods.

The 'Auto' setting performs parallel fits with each of the fitting methods and returns the result with the lowest chi-squared value.
""".strip()

fitting_weight: str = f"""
The weight function used when calculating residuals during fitting.

Modulus: (1/|Z_fit|, 1/|Z_fit|)

Proportional: (1/Z_fit'^2, 1/Z_fit\"^2)

Unity: (1, 1)

Boukamp: (1/Z_exp'^2 + 1/Z_exp\"^2, 1/Z_exp'^2 + 1/Z_exp\"^2) (eq. 13)

The 'Auto' setting performs parallel fits with each of the weight functions listed above and returns the results with the lowest chi-squared value.

{BOUKAMP1995}
""".strip()

fitting_nfev: str = """
The maximum number of function evaluations to perform. This setting can be used to limit the amount of time spent performing a fit. If this setting is set to zero, then no limit is applied.
""".strip()

fitting_perform: str = """
Sometimes a circuit, which ostensibly should be capable of providing a good fit, does not fit well. If the starting values of the parameters have been left at their default values, then rough adjustments may be all that is required. For example, if a circuit contains two parallel RC subcircuits in series (i.e. the CDC contains '(RC)(RC)'), then setting one of the capacitances to be one order of magnitude greater than the other may be sufficient.

Setting both the fitting method and weight function to 'Auto' is recommended as the starting point. Some of the various combinations of fitting methods and weight functions may be more forgiving than others regarding starting values for a particular circuit and thus require less work on the part of the user to achieve a good fit.

The fitting is performed using the Python package called lmfit. That package provides estimates for the error of the fitted parameters whenever possible. Circumstances when it is not possible to provide such estimates include e.g. when a parameter is near its lower/upper limit if such a limit has been defined. A parameter with a large error estimate is indicative of that parameter not really affecting the fit at all. For example, an unnecessary Warburg diffusion element may have its admittance parameter, Y, set to be a very large value and thus the element contributes very little to the overall impedance of the circuit within the frequency range of the experimental data.
""".strip()

fitting_chisqr: str = """
The chi-squared value of the fit.
""".strip()

fitting_red_chisqr: str = """
The reduced chi-squared value of the fit.
""".strip()

fitting_aic: str = """
The Akaike information criterion.
""".strip()

fitting_bic: str = """
The Bayesian information criterion.
""".strip()

fitting_nfree: str = """
The degrees of freedom in the fit.
""".strip()

fitting_ndata: str = """
The number of data points in the fit.
""".strip()

simulation_cdc: str = """
The equivalent circuit to simulate. A circuit description code (CDC) can be typed in to define the equivalent circuit. Alternatively, the circuit editor can be used to construct the equivalent circuit.
""".strip()

simulation_min_freq: str = """
The minimum frequency to simulate.
""".strip()

simulation_max_freq: str = """
The maximum frequency to simulate.
""".strip()

simulation_per_decade: str = """
The number of frequencies per decade in the frequency range.
""".strip()

circuit_editor_cdc_input: str = """
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
""".strip()

circuit_editor_element_combo: str = """
This drop-down list can be used to select an element that you want to add as a node to the window below once the 'Add' button is clicked.

The 'Add dummy' button adds a dummy node that can be used as a junction point, which may be necessary when representing certain circuits using nodes.
""".strip()

circuit_editor_simple_cdc: str = """
This is the basic CDC output generated based on the nodes and connections in the window above.

This output may be accepted by another program that accepts a CDC as input. However, some programs may use different identifiers for some elements. Thus, this output may require adjustments for it to be accepted by some other programs.
""".strip()

circuit_editor_detailed_cdc: str = """
This is the extended CDC output generated based on the nodes and connections in the window above.

This output is unlikely to be accepted by another program that accepts a CDC as input.
""".strip()


circuit_editor_status: str = """
Potential issues with the circuit, which is defined using nodes and connections in the window above, are presented here.
""".strip()
