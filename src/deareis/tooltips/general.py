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


general = SimpleNamespace(
    **{
        "apply_settings": """
Apply the settings that were used to generate the currently selected result.
    """.strip(),
        "apply_mask": """
Apply the mask that was used to generate the currently selected result.
    """.strip(),
        "copy_plot_data_as_csv": """
Copy the data in the plot to the clipboard as character-separated values.
    """.strip(),
        "copy_output": """
Copy the chosen output to the clipboard.
    """.strip(),
        "open_circuit_editor": """
Open the circuit editor.
    """.strip(),
        "adjust_plot_limits": """
Automatically adjust the limits of the plot to fit the data.
    """.strip(),
        "adjust_nyquist_limits": """
Automatically adjust the limits of the Nyquist plot to fit the data.
    """.strip(),
        "adjust_bode_limits": """
Automatically adjust the limits of the Bode plot to fit the data.
    """.strip(),
        "adjust_residuals_limits": """
Automatically adjust the limits of the residuals plot to fit the data.
    """.strip(),
        "adjust_drt_limits": """
Automatically adjust the limits of the DRT plot to fit the data.
    """.strip(),
        "adjust_impedance_limits": """
Automatically adjust the limits of the impedance plot to fit the data.
    """.strip(),
        "adjust_limits": """
Automatically adjust the limits of the plots to fit the data.
    """.strip(),
        "palette": """
The options can be navigated using the following keys:

- Home - first option
- Page up - five steps up
- Up arrow - one step up
- Down arrow - one step down
- Page down - five steps down
- End - last option

The highlighted option can be selected by pressing Enter. The window can be closed by pressing Esc.
    """.strip(),
        "auto_backup_interval": """
The number of actions between automatically saving a backup of the current state of a project in case of, e.g., crashes or power outages.

Setting this interval to zero disables automatic backups.
    """.strip(),
        "num_procs": """
The number of parallel processes to use when performing, e.g., circuit fitting. A value greater than 0 results in that specific number of processes being used. A value of 0 results in N-1 processes (minimum of 1) being used where N = {} at the moment. The value of N is based on the detected linear algebra libraries that are used by NumPy and by the values of some environment variables used by those libraries.
    """.strip(),
        "plot_admittance": """
Plot the admittance representation of the immittance data.
    """.strip(),
        "plot_drt_frequency": """
Plot the distribution of relaxation times as a function of frequency.
    """.strip(),
    }
)
