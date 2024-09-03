# DearEIS is licensed under the GPLv3 or later (https://www.gnu.org/licenses/gpl-3.0.html).
# Copyright 2024 DearEIS developers
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


zhit = SimpleNamespace(
    **{
        "smoothing": """
The type of smoothing to apply to the phase data. LOWESS is the default smoothing algorithm since Savitzky-Golay expects evenly spaced data, but the latter may provide better results in some cases. Setting this to 'Auto' results in attempts to use all of them separately and choosing the result with the best fit.
    """.strip(),
        "num_points": """
The number of points to take into consideration when smoothing any given point.
    """.strip(),
        "polynomial_order": """
The order of the polynomial that is used in the Savitzky-Golay algorithm.
    """.strip(),
        "num_iterations": """
The number of iterations to perform in the LOWESS algorithm.
    """.strip(),
        "interpolation": """
The type of spline to use for interpolation. The Akima spline should be a good choice in most cases. Setting this to 'Auto' results in attempts to use all of them separately and choosing the result with the best fit.
    """.strip(),
        "window": """
The type of window function that is used to generate weights for offset adjustment. Setting this to 'Auto' results in attempts to use all of them separately and choosing the result with the best fit.
    """.strip(),
        "window_center": """
The center of the window function on the logarithmic frequency scale. For example, a value of 2.0 would center the window on 100 Hz.
    """.strip(),
        "window_width": """
The total width of the window on the logarithmic frequency scale. For example, if the center is 2.0 (i.e., 100 Hz) and the width is 2.0, then the window would cover the frequency range from 10 Hz to 1000 Hz.
    """.strip(),
        "preview_weights": """
Preview the position and width of the window, and the resulting weights that will be applied to the residuals when adjusting the offset of the reconstructed modulus data. The residuals for the frequencies outside of the window will have a weight of 0.0 applied to them.
    """.strip(),
        "select_window_function": """
Click one of these checkboxes to preview a window function.
    """.strip(),
        "perform": """
The Z-HIT algorithm ('impedance-Hilbert transformation' or 'Zweipol-Hilbert transformation' depending on the source) reconstructs the modulus data of an impedance spectrum based on the phase data (see references below for more information). The results can be used to check the validity of an impedance spectrum.

For example, the sample's composition may change irreversibly over time and result in an impedance response that changes during a single frequency sweep. This would be most apparent at low frequencies where each data point can take, e.g., several seconds or minutes to measure depending on the frequency. Improper arrangement of the electrode cables can result in mutual induction that becomes apparent at high frequencies and particularly when working with low-impedance samples.

The final step of the Z-HIT algorithm requires an offset adjustment of the reconstructed modulus data, which is done by fitting the reconstructed modulus data to a part of the experimental modulus data. The window settings determine which part of the recorded data is used and 1 Hz to 1000 Hz is typically less affected by artifacts like drift and/or mutual induction.

Note that if some settings are set to 'Auto', then the various combinations are tested and the final result is chosen based on how good the fit is.

References:

- W. Ehm, H. Göhr, R. Kaus, B. Röseler, and C.A. Schiller, 2000, Acta Chimica Hungarica, 137 (2-3), 145-157.
- W. Ehm, R. Kaus, C.A. Schiller, and W. Strunz, 2001, in "New Trends in Electrochemical Impedance Spectroscopy and Electrochemical Noise Analysis".
- C.A. Schiller, F. Richter, E. Gülzow, and N. Wagner, 2001, 3, 374-378 (https://doi.org/10.1039/B007678N)
    """.strip(),
        "delete": """
Setting this to 'Auto' results in attempts to use all of them separately and choosing the result with the best fit.
    """.strip(),
        "load_as_data_set": """
Load the current Z-HIT analysis result as a data set.
    """.strip(),
        "representation": """
Perform the Z-HIT analysis using this immittance representation.
    """.strip(),
    },
)
