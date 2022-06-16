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


data_sets = SimpleNamespace(
    **{
        "load": """
Select files to load as new data sets.
    """.strip(),
        "delete": """
Delete the current data set.
    """.strip(),
        "average": """
Create a new data set by averaging multiple data sets.
    """.strip(),
        "toggle": """
Toggle a range of points.
    """.strip(),
        "copy": """
Copy the mask from another data set.
    """.strip(),
        "copy_mask_source": """
Select the data set to copy the mask from. The 'Page up' and 'Page down' keys can also be used for to cycle between data sets.
    """.strip(),
        "subtract": """
Subtract impedance from the current spectrum.
    """.strip(),
        "mask": """
If checked, then the corresponding data point will be omitted from plots, tests, and fits.
    """.strip(),
        "frequency": """
The excitation frequency that was applied when recording the data point.
    """.strip(),
        "real": """
The real part of the complex impedance.
    """.strip(),
        "imaginary": """
The negative imaginary part of the complex impedance.
    """.strip(),
        "magnitude": """
The magnitude of the complex impedance.
    """.strip(),
        "phase": """
The negative phase shift of the complex impedance.
    """.strip(),
    }
)
