# DearEIS is licensed under the GPLv3 or later (https://www.gnu.org/licenses/gpl-3.0.html).
# Copyright 2023 DearEIS developers
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

kulikovsky2021: str = "DOI:10.1149/1945-7111/abf508"
wan2015: str = "DOI:10.1016/j.electacta.2015.09.097"
ciucci2015: str = "DOI:10.1016/j.electacta.2015.03.123"
effat2017: str = "DOI:10.1016/j.electacta.2017.07.050"
liu2020: str = "DOI:10.1016/j.electacta.2020.136864"
boukamp2015: str = "DOI:10.1016/j.electacta.2014.12.059"
boukamp2017: str = "DOI:10.1016/j.ssi.2016.10.009"
cultrera2020: str = "DOI:10.1088/2633-1357/abad0d"

drt = SimpleNamespace(
    **{
        "method": f"""
The method to use when calculating the distribution of relaxation times.

BHT: Bayesian Hilbert transform method.
- {liu2020}

TR-NNLS: Tikhonov regularization combined with non-negative least squares fitting.
- {kulikovsky2021}

TR-RBF: Tikhonov regularization combined with radial basis function (or piecewise linear) discretization and convex optimization.
- {wan2015}
- {ciucci2015}
- {effat2017}

m(RQ)fit: multi-(RQ) complex non-linear least squares fit.
- {boukamp2015}
- {boukamp2017}

The TR-NNLS method is very fast while the slower TR-RBF method provides the ability to optionally also calculate Bayesian credible intervals. The BHT method, while temperamental due to randomization of initial values, is able to provide numerical scores that can be used to assess the quality of an impedance spectrum. The m(RQ)fit method requires a suitable fitted circuit but may be able to distinguish peaks that are in close proximity and would only show up as broad peaks in some other methods.
    """.strip(),
        "mode": """
The data to use when performing the calculations:
- Complex
- Real
- Imaginary

This is only used when the method setting is set to TR-NNLS or TR-RBF.
    """.strip(),
        "lambda_value": f"""
The regularization parameter to use as part of the Tikhonov regularization. If the checkbox next to the input field is ticked, then an attempt will be made to automatically find a suitable value. However, further tweaking of the value manually is recommended.

More than one approach for suggesting a suitable regularization parameter may be available (e.g., 'L-curve corner search' from {cultrera2020}). It may be necessary to use a lower value for the 'Maximum symmetry' setting (e.g., 0.1) when using the TR-RBF method and the 'L-curve corner search' algorithm to suggest a suitable regularization parameter.

This is only used when the method setting is set to TR-NNLS or TR-RBF.
    """.strip(),
        "shape_coeff": """
The input value, k, for the shape coefficient used in the shape type (see the setting above).

This is only used when the method setting is set to BHT or TR-RBF.
    """.strip(),
        "credible_intervals": """
Whether or not the Bayesican credible intervals are calculated when using the TR-RBF method. The number of samples to use can also be defined. More accurate results can be obtained with a greater number of samples albeit at the expense of requiring more time.
    """.strip(),
        "credible_intervals_timeout": """
How many seconds to wait for the calculation of credible intervals to finish before timing out.
    """.strip(),
        "num_samples": """
The number of samples to use when:
- calculating Bayesian credible intervals (TR-RBF method)
- calculating Jensen-Shannon distances (BHT method)

A greater number of samples provide greater accuracy at the expense of time.
    """.strip(),
        "num_attempts": """
The number of attempts to make to find a solution using the BHT method. The initial values are randomized so a greater number of attempts is more likely to yield reasonable results at the expense of requiring more time. If poor results (e.g., significant oscillation in the DRT plot) are obtained, then try repeating the calculations and possibly also tweak the settings.
    """.strip(),
        "maximum_symmetry": """
Poor results with significant oscillation can be discarded automatically by defining a limit for the ratio of the vertical peak-to-peak symmetry allowed in the DRT plot. The limit is defined as a ratio from 0.0 to 1.0. A smaller value provides a stricter condition as the absolute value of the most positive peak must be greater than the absolute value of the most negative peak.

This is only used when the method setting is set to BHT or TR-RBF.
    """.strip(),
        "perform": f"""
DRT analyses work best with data sets where the imaginary part of the impedance approaches zero at both the low- and high-frequency ends of the recorded frequency range. Thus, some data sets may require some processing if they exhibit, e.g., inductive behavior at high frequencies and/or increasing impedance at low frequencies due to diffusion.

If the BHT or TR-RBF methods are used for the first time, then keeping the number of samples and attempts modest at first is recommended. It may take quite a long time depending on the computer's performance.

If the BHT method is used, then scores for the consistency of the data will be included. The scores range from 0 to 100 %.
    """.strip(),
        "delete": """
Delete the current analysis result.
    """.strip(),
        "score_mean": """
The similarity of the means of the Hilbert transformed impedances and the DRT impedances (i.e., without the high-frequency resistance and inductance).
    """.strip(),
        "score_residuals": """
The amount of experimental points that fall within one, two, or three standard deviations of the prediction of the Hilbert transform.
    """.strip(),
        "score_hd": """
The Hellinger distance between the Hilbert transformed impedances and the DRT impedances (i.e., without the high-frequency resistance and inductance).
    """.strip(),
        "score_jsd": """
The Jensen-Shannon distance between the Hilbert transformed impedances and the DRT impedances (i.e., without the high-frequency resistance and inductance).
    """.strip(),
        "circuit": """
The fitted circuit to use to calculate the distribution of relaxation times.

Valid circuits consist of one or more parallel RQ (or RC) circuits in series. An optional series resistance may also be included. For example, the following circuits would be valid:
- (RC)
- (RQ)
- (RQ)(RQ)
- R(RQ)
- R(RQ)(RQ)(RC)

This is only used when the method is set to m(RQ)fit.
    """.strip(),
        "gaussian_width": """
The width of the Gauss function used to calculate the distribution of relaxation times for (RC) circuits (or (RQ) circuits where n ~ 1).

This is only used when the method is set to m(RQ)fit.
    """.strip(),
        "num_per_decade": """
The number of points per decade to use when calculating the distribution of relaxation times. This affects the final step where the distribution of relaxation times are calculated using the analytical solutions (or approximations in the case of (RC) circuits) when using the m(RQ)fit method.

This is only used when the method is set to m(RQ)fit.
    """.strip(),
    }
)
