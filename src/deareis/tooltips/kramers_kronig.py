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


boukamp1995: str = "DOI:10.1149/1.2044210"
schonleber2014: str = "DOI:10.1016/j.electacta.2014.01.034"
plank2022: str = "DOI:10.1109/IWIS57888.2022.9975131"
yrjana2024: str = "DOI:10.1016/j.electacta.2024.144951"
lilliefors1967: str = "DOI:10.1080/01621459.1967.10482916"
massey1951: str = "DOI:10.2307/2280095"
shapiro1965: str = "DOI:10.1093/biomet/52.3-4.591"

kramers_kronig = SimpleNamespace(
    **{
        "test": f"""
Fit an equivalent circuit to the impedance (fig. 1) or admittance (fig. 13) representation of the immittance data.

- CNLS: Use complex non-linear least squares fitting.
- Complex: Use a set of linear equations to fit to the complex impedance (eq. 12).
- Imaginary: Use a set of linear equations to fit to the imaginary part of the complex impedance (eqs. 4 and 7).
- Real: Use a set of linear equations to fit to the real part of the complex impedance (eqs. 8 and 10).

The last three are available as implementations that use either least squares fitting or matrix inversion. The complex and the real test are recommended as the ones to use primarily. The real test is more sensitive than the complex test, but it may also be too sensitive at times. The CNLS and imaginary tests are included primarily for the sake of completeness. The CNLS test is slower than any of the other tests and it may be more challenging to obtain a good fit with the imaginary test even when the immittance spectrum is valid.

References:
- Boukamp (1995, {boukamp1995})
    """.strip(),
        "mode": f"""
Auto: Apply the latest settings from the Exploratory mode or the default settings. The suggested result is automatically accepted.

Exploratory: Perform linear Kramers-Kronig tests and then present the intermediate results. The manner in which the optimal number of RC elements are suggested can be adjusted when using this mode. The main purpose of this mode is to allow for troubleshooting and for making corrections in case one of the algorithmic approaches to suggesting the optimal log Fext and/or the optimal number of RC elements is producing strange results.

Manual: Choose a specific number of RC elements to use.
    """.strip(),
        "num_RC": """
The number of RC elements to include in the equivalent circuit when the mode is set to 'Manual'.
    """.strip(),
        "add_capacitance": """
Add a capacitor in series or in parallel to the equivalent circuit when using the impedance or admittance representation, respectively, of the immittance data. This may be necessary in circumstances where the imaginary part of an impedance spectrum does not approach zero when the frequency is decreased.
    """.strip(),
        "add_inductance": """
Add an inductor in series or in parallel to the equivalent circuit when using the impedance or admittance representation, respectively, of the immittance data. This may be necessary when the imaginary part of an impedance spectrum does not approach zero when the frequency is increased.
    """.strip(),
        "min_log_F_ext": """
The lower limit to use when optimizing log Fext.
    """.strip(),
        "max_log_F_ext": """
The upper limit to use when optimizing log Fext.
    """.strip(),
        "log_F_ext": f"""
Log Fext is a factor that can be used to extend (log Fext > 0) or contract (log Fext < 0) the range of time constants in both directions. This setting can be modified once the number of Fext evaluations is set to 0.

References:
- Boukamp (1995, {boukamp1995})
    """.strip(),
        "num_F_ext_evaluations": """
The number of evaluations to perform when optimizing log Fext. If set to a non-zero value, then the minimum and maximum log Fext limits are imposed and the log Fext value is estimated automatically. If set to zero, then the provided log Fext value is used directly.
    """.strip(),
        "rapid_F_ext_evaluations": """
If enabled, then a smaller number of RC elements are evaluated whenever possible in order to reduce the time spent optimizing log Fext.
    """.strip(),
        "cnls_method": """
The iterative method used to perform the fitting.

This setting is only used when the test setting is set to 'CNLS'.
    """.strip(),
        "nfev": """
The maximum number of function evaluations to use when fitting. This can be used to limit the amount of time spent performing a fit. A value of zero means that there is no limit.

This setting is only used when the test setting is set to 'CNLS'.
    """.strip(),
        "timeout": """
The number of seconds that the fitting is allowed to take for each number of RC elements before terminating.

This setting is only used when the test setting is set to 'CNLS'.
    """.strip(),
        "perform": f"""
The purpose of the linear Kramers-Kronig test is to help validate immittance spectra. Multiple variants of the linear Kramers-Kronig test are implemented in this program. This test involves fitting an equivalent circuit, which is known to be Kramers-Kronig transformable, to an impedance spectrum.

The default settings are recommended as a starting point.

Valid spectra typically exhibit:
- Randomly distributed residuals that are centered along the x-axis.
- Residuals with small magnitudes (e.g. less than half of a percent). Note that the residuals of noisy impedance spectra may have a greater magnitude and still be valid but the noise may also hide non-linear behavior.

Invalid spectra typically exhibit:
- Residuals that are not randomly distributed. Note that if the number of RC elements used to perform the test is too small, then the residuals may form a sinusoidal pattern.
- Residuals that are clearly biased away from the x-axis. For example, residuals may increasinly diverge from the x-axis as the frequency is decreased or they may form a convex/concave shape.

See the following references for more information about the linear Kramers-Kronig tests:

- Boukamp (1995, {boukamp1995})
- Schönleber et al. (2014, {schonleber2014})
- Plank et al. (2022, {plank2022})
- Yrjänä and Bobacka (2024, {yrjana2024})

Analysing the contributions of higher-order harmonics to the response signal is another way of checking for non-linearity. Potentiostat/galvanostat manufacturers may implement this in different ways and use different terminology may be used in their documentation. For example, 'total harmonic distortion' (THD) may be available as a setting in the measurement method. Alternatively, it may be possible to record the response signal for processing and analysis (e.g., Fourier transform).
    """.strip(),
        "delete": """
Delete the current test result.
    """.strip(),
        "pseudo_chisqr": f"""
Pseudo chi-squared value calculated according to eq. 14.

References:
- Boukamp (1995, {boukamp1995})
    """.strip(),
        "exploratory_result": """
The result to highlight and ultimately save.
    """.strip(),
        "mu": f"""
The µ value represents how the equivalent circuit fits the data (eq. 21). µ values range from zero to one with the extremes representing over-fitting and under-fitting, respectively.

References:
- Schönleber et al. (2014, {schonleber2014})
    """.strip(),
        "num_RC": """
The number of RC elements connected in series in the equivalent circuit.
    """.strip(),
        "series_resistance": """
The fitted series resistance ([R] = ohm).
    """.strip(),
        "series_capacitance": """
The fitted series capacitance ([C] = F).
    """.strip(),
        "series_inductance": """
The fitted series inductance ([L] = H).
    """.strip(),
        "parallel_resistance": """
The fitted parallel resistance ([R] = ohm).
    """.strip(),
        "parallel_capacitance": """
The fitted parallel capacitance ([C] = F).
    """.strip(),
        "parallel_inductance": """
The fitted parallel inductance ([L] = H).
    """.strip(),
        "representation": """
The representation of the immittance spectrum that was tested.
    """.strip(),
        "representation_setting": """
Perform the Kramers-Kronig tests using a specific representation of the immittance data or automatically pick one.
    """.strip(),
        "suggestion_settings": """
The settings below are used when the Kramers-Kronig test mode is set to either 'Auto' or 'Exploratory'. These settings can be changed either in the window for defining default settings or the 'Exploratory test results' window.
    """.strip(),
        "method_1": f"""
A value µ is calculated using the fitted variables. Limits of 1.0 and 0.0 correspond to under- and overfitting, respectively.

%MU_EQUATION%

The number of RC elements is incremented until µ drops below a threshold called the µ-criterion. The final number of RC elements that was reached is considered to be the optimal number of RC elements.

This method has been modified to:

- add support for operating on the admittance representation of the immittance data
- add measures to deal with issues related to fluctuating µ values
- reverse the iteration direction (i.e., the number of RC elements is decremented)

The two last modifications can be disabled by setting the 'beta' setting to 0.0 (see settings below).

This modified method decrements the number of RC elements until the µ-criterion is crossed and considers that point to be the lower limit for the optimal number of RC elements. A score S is then calculated for each number of RC elements based on the chosen µ-criterion, the µ value, and the corresponding pseudo chi-squared value.

%SCORE_EQUATION%

The number of RC elements that is greater than or equal to the lower limit and has the highest score is considered to be the optimal number of RC elements.

References:
- Schönleber et al. (2014, {schonleber2014})
- Yrjänä and Bobacka (2024, {yrjana2024})
    """.strip(),
        "method_1_mu_criterion": f"""
NOTE: ONLY APPLIES TO METHOD 1!

The µ value represents how the equivalent circuit fits the data (eq. 21).

%MU_EQUATION%

µ values range from zero to one with the extremes representing over-fitting and under-fitting, respectively. Over-fitting is undesirable since the equivalent circuit could end up reproducing any noise that may be present in the data. However, too much under-fitting means that the equivalent circuit is unable to reproduce the data. A modified version of the equation that substitutes capacitances for resistances is used when operating on the admittance representation of the immittance data.

The µ-criterion defines the threshold at which no more RC elements are added to the equivalent circuit. Note that in some cases the calculated µ value may prematurely and temporarily drop below the threshold set by the µ-criterion.

References:
- Schönleber et al. (2014, {schonleber2014})
    """.strip(),
        "method_1_beta": f"""
NOTE: ONLY APPLIES TO METHOD 1!

An exponent used when calculating an additional score S based on µ, µ-criterion, and pseudo chi-squared.

%SCORE_EQUATION%

The exponent affects the penalty applied based on the difference between µ-criterion and µ.

This calculation is a modification to method 1. Setting the value of beta to 0.0 applies method 1 as described originally by Schönleber et al. (2014).

References:
- Yrjänä and Bobacka (2024, {yrjana2024})
- Schönleber et al. (2014, {schonleber2014})
    """.strip(),
        "method_2": f"""
The norm of the fitted variables. The minimum is considered to correspond to the optimal number of RC elements.

References:
- Plank et al. (2022, {plank2022})
    """.strip(),
        "method_3": f"""
The norm of all curvatures of the fitted impedance spectrum. The minimum is considered to correspond to the optimal number of RC elements.

This method has been modified to also take intermediate frequencies into account by inserting additional frequencies between each excitation frequency before calculating curvatures.

References:
- Plank et al. (2022, {plank2022})
- Yrjänä and Bobacka (2024, {yrjana2024})
    """.strip(),
        "method_4": f"""
The number of sign changes across the curvatures of the fitted impedance spectrum. The optimal number of RC elements should correspond to a minimum number of sign changes since this reduces the amount of fluctuation in the fitted impedance spectrum.

This method has been modified to get rid of plateaus, which may form in some cases since the values are integers, by adding real number offsets (smaller than 1.0) with magnitudes that are based on the relative pseudo chi-squared values corresponding to the number of RC elements.

References:
- Plank et al. (2022, {plank2022})
- Yrjänä and Bobacka (2024, {yrjana2024})
    """.strip(),
        "method_5": f"""
The mean distance between sign changes across the curvatures of the fitted impedance spectrum. Significant under- or overfitting tends to cause the mean distance to be large or small, respectively. A local maximum somewhere between these two extremes should correspond to the optimal number of RC elements.

References:
- Yrjänä and Bobacka (2024, {yrjana2024})
- Plank et al. (2022, {plank2022})
    """.strip(),
        "method_6": f"""
The number of fitted variables and their corresponding magnitudes tend to increase as the number of RC elements is incremented. The fitted variables and their corresponding predefined time constants can be used to calculate capacitances or resistances when operating on the impedance or admittance representation, respectively, of the immittance data by using the equation:

%TAU_EQUATION%

The sum of the absolute values of these calculated capacitances or resistances tends to increase initially as the number of RC elements is incremented since there are more values to add together.

%SUM_ABS_TAU_VAR_EQUATION%

The average magnitude of these calculated capacitances or resistances tends to decrease as the number of RC elements is incremented, which causes the sum of the absolute values to stagnate and finally begin decreasing instead. For example, plotting the base-10 logarithms of these sums as a function of the number of RC elements forms an apex that corresponds to a suitable ratio of positive and negative fitted variables.

References:
- Yrjänä and Bobacka (2024, {yrjana2024})
    """.strip(),
        "suggestion_methods": """
Select one or more methods for suggesting the optimal number of RC elements. The pseudo chi-squared values may be used as tiebreakers if there is no clear optimum number of RC elements based on the various methods.
    """.strip(),
        "combining_suggestion_methods": """
The various suggestion methods can be combined in different ways:

- mean: each method suggests one candidate and the mean number of RC elements is considered to be the optimum.

- ranking: each method ranks the number of RC elements, an exponential decay function is used to assign scores, the scores are added up, and the highest-scoring candidate is considered to be the optimal number of RC elements.

- sum: the different numbers of RC elements are assigned scores ([0.0,1.0]) by each method, the scores from each method are added together, and the highest-scoring candidate is considered to be the optimal number of RC elements.

The default approach uses method 4 to obtain an initial list of candidates. If more than one candidate exists, then the list is narrowed down iteratively. Method 3 is used first, then method 5 is used, and finally the pseudo chi-squared values are used. If a lower number of RC elements provides a lower pseudo chi-squared value, then this will ultimately be chosen.
    """.strip(),
        "lower_limit": f"""
The lower limit for the range where the optimal number of RC elements should exist can be estimated algorithmically or it can be defined manually. If this limit is too low, then some methods may provide suggestions that lead to significant underfitting.

The lower limit should at the very least be at or above the number of RC elements where the corresponding pseudo chi-squared values stop decreasing by significant amounts as the number of RC elements is incremented further.

If this value is set to zero, then the lower limit is estimated algorithmically.

References:
- Yrjänä and Bobacka (2024, {yrjana2024})
    """.strip(),
        "upper_limit": f"""
The upper limit for the range where the optimal number of RC elements should exist can be estimated algorithmically or it can be defined manually. If this limit is too high, then some methods may provide suggestions that lead to significant overfitting.

If this value is set to zero, then the upper is estimated algorithmically.

References:
- Yrjänä and Bobacka (2024, {yrjana2024})
    """.strip(),
        "limit_delta": """
The upper limit can also be defined as the lower limit plus this value, if this value is greater than zero.
    """.strip(),
        "apply_suggestion_settings": """
Apply the chosen settings and refresh the suggestions.
    """.strip(),
        "residuals_means": """
The mean of the residuals of the real/imaginary part (% of |Z|).
    """.strip(),
        "residuals_sd": """
The sample standard deviation of the residuals of the real/imaginary part (% of |Z|).
    """.strip(),
        "residuals_within_n_sd": """
The percentage of residuals of the real/imaginary part located within N standard deviations of the mean.
    """.strip(),
        "lilliefors": f"""
The p-value that was obtained when the Lilliefors normality test was performed on the residuals of the real/imaginary part. If the p-value is below a threshold (e.g., 0.05), then the null hypothesis (i.e., that the sample comes from a normal distribution) is rejected.

Note that the p-values may also be lower than the threshold if the noise in the immittance spectrum is very low. The complex variant of the Kramers-Kronig test is less susceptible to this issue than the real and imaginary tests.

References:
- Lilliefors (1967, {lilliefors1967})
- Yrjänä and Bobacka (2024, {yrjana2024})
    """.strip(),
        "shapiro_wilk": f"""
The p-value that was obtained when the Shapiro-Wilk normality test was performed on the residuals of the real/imaginary part. If the p-value is below a threshold (e.g., 0.05), then the null hypothesis (i.e., that the sample comes from a normal distribution) is rejected.

Note that the p-values may also be lower than the threshold if the noise in the immittance spectrum is very low. The complex variant of the Kramers-Kronig test is less susceptible to this issue than the real and imaginary tests.

References:
- Shapiro and Wilk (1965, {shapiro1965})
- Yrjänä and Bobacka (2024, {yrjana2024})
    """.strip(),
        "estimated_noise_sd": f"""
The estimated standard deviation of the noise (% of |Z|). The error is assumed to be distributed evenly across the real and imaginary parts of the immittance spectrum. The value was obtained using the pseudo chi-squared value and the number of excitation frequencies:

SD ~ sqrt(5000 * X²ps / #f)

References:
- Yrjänä and Bobacka (2024, {yrjana2024})
    """.strip(),
        "kolmogorov_smirnov": f"""
The p-value that was obtained when the one-sample Kolmogorov-Smirnov test was performed on the residuals of the real/imaginary part. The residuals were compared against a normal distribution with a mean of zero and a standard deviation equal to the estimated noise SD. If the p-value is below a threshold (e.g., 0.05), then the null hypothesis (i.e., that the sample comes from a normal distribution with the expected mean and standard deviation) is rejected.

Note that the p-values may also be lower than the threshold if the noise in the immittance spectrum is very low. The complex variant of the Kramers-Kronig test is less susceptible to this issue than the real and imaginary tests.

References:
- Massey (1951, {massey1951})
- Yrjänä and Bobacka (2024, {yrjana2024})
    """.strip(),
        "load_as_data_set": """
Load the current Kramers-Kronig result as a data set.
    """.strip(),
        "copy_cdc": """
Copy the circuit description code (CDC) for the fitted circuit.
    """.strip(),
    }
)
