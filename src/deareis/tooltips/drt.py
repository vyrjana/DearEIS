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

kulikovsky2020: str = "DOI:10.1039/D0CP02094J"
wan2015: str = "DOI:10.1016/j.electacta.2015.09.097"
ciucci2015: str = "DOI:10.1016/j.electacta.2015.03.123"
effat2017: str = "DOI:10.1016/j.electacta.2017.07.050"
liu2020: str = "DOI:10.1016/j.electacta.2020.136864"

drt = SimpleNamespace(
    **{
        "method": f"""
The method to use when calculating the distribution of relaxation times.

TR-NNLS: Tikhonov regularization combined with non-negative least squares fitting.

TR-RBF: Tikhonov regularization combined with radial basis function (or piecewise linear) discretization and convex optimization.

BHT: Bayesian Hilbert transform method.

The TR-NNLS method is very fast while the slower TR-RBF method provides the ability to optionally also calculate Bayesian credible intervals. The BHT method, while temperamental due to randomization of initial values, is able to provide numerical scores that can be used to assess the quality of an impedance spectrum.

References:

- {kulikovsky2020}

- {wan2015}

- {ciucci2015}

- {effat2017}

- {liu2020}
    """.strip(),
        "mode": """
The data to use when performing the calculations:
- Complex
- Real
- Imaginary

This is only used when the method setting is set to TR-NNLS or TR-RBF.
    """.strip(),
        "lambda_value": """
The regularization parameter to use as part of the Tikhonov regularization. If the checkbox next to the input field is ticked, then an attempt will be made to automatically find a suitable value. However, further tweaking of the value manually is recommended.

This is only used when the method setting is set to TR-NNLS or TR-RBF.
    """.strip(),
        "shape_coeff": """
The input value, k, for the shape coefficient used in the shape type (see the setting above).

This is only used when the method setting is set to BHT or TR-RBF.
    """.strip(),
        "credible_intervals": """
Whether or not the Bayesican credible intervals are calculated when using the TR-RBF method. The number of samples to use can also be defined. More accurate results can be obtained with a greater number of samples albeit at the expense of requiring more time.
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
If the BHT or TR-RBF methods are used for the first time, then keeping the number of samples and attempts modest at first is recommended. It may take quite a long time depending on the computer's performance.

If the BHT method is used, then scores for the consistency of the data will be included. The scores range from 0 to 100 %.

Reference: {liu2020}
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
    }
)
