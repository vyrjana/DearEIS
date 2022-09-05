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

from typing import (
    Dict,
    List,
)
import dearpygui.dearpygui as dpg
from deareis.enums import (
    Action,
    DRTMethod,
    DRTMode,
    CNLSMethod,
    TestMode,
    PlotLegendLocation,
    PlotPreviewLimit,
    PlotUnits,
    RBFShape,
    RBFType,
    Test,
    Weight,
)
from deareis.keybindings import Keybinding
from deareis.data.plotting import PlotExportSettings
from deareis.data import (
    DRTSettings,
    FitSettings,
    SimulationSettings,
    TestSettings,
)

DEFAULT_KEYBINDINGS: List[Keybinding] = [
    Keybinding(
        dpg.mvKey_N,
        False,
        True,
        False,
        Action.NEW_PROJECT,
    ),
    Keybinding(
        dpg.mvKey_O,
        False,
        True,
        False,
        Action.LOAD_PROJECT,
    ),
    Keybinding(
        dpg.mvKey_Q,
        False,
        True,
        False,
        Action.EXIT,
    ),
    Keybinding(
        dpg.mvKey_Next,
        False,
        False,
        True,
        Action.NEXT_PROGRAM_TAB,
    ),
    Keybinding(
        dpg.mvKey_Prior,
        False,
        False,
        True,
        Action.PREVIOUS_PROGRAM_TAB,
    ),
    Keybinding(
        dpg.mvKey_F1,
        False,
        False,
        False,
        Action.SHOW_SETTINGS_APPEARANCE,
    ),
    Keybinding(
        dpg.mvKey_F2,
        False,
        False,
        False,
        Action.SHOW_SETTINGS_DEFAULTS,
    ),
    Keybinding(
        dpg.mvKey_F3,
        False,
        False,
        False,
        Action.SHOW_SETTINGS_KEYBINDINGS,
    ),
    Keybinding(
        dpg.mvKey_F11,
        False,
        False,
        False,
        Action.SHOW_HELP_LICENSES,
    ),
    Keybinding(
        dpg.mvKey_F12,
        False,
        False,
        False,
        Action.SHOW_HELP_ABOUT,
    ),
    Keybinding(
        dpg.mvKey_P,
        False,
        True,
        False,
        Action.SHOW_COMMAND_PALETTE,
    ),
    Keybinding(
        dpg.mvKey_S,
        False,
        True,
        False,
        Action.SAVE_PROJECT,
    ),
    Keybinding(
        dpg.mvKey_S,
        False,
        True,
        True,
        Action.SAVE_PROJECT_AS,
    ),
    Keybinding(
        dpg.mvKey_W,
        False,
        True,
        False,
        Action.CLOSE_PROJECT,
    ),
    Keybinding(
        dpg.mvKey_Z,
        False,
        True,
        False,
        Action.UNDO,
    ),
    Keybinding(
        dpg.mvKey_Y if dpg.get_platform() == dpg.mvPlatform_Windows else dpg.mvKey_Z,
        False,
        True,
        False if dpg.get_platform() == dpg.mvPlatform_Windows else True,
        Action.REDO,
    ),
    Keybinding(
        dpg.mvKey_Next,
        False,
        True,
        False,
        Action.NEXT_PROJECT_TAB,
    ),
    Keybinding(
        dpg.mvKey_Prior,
        False,
        True,
        False,
        Action.PREVIOUS_PROJECT_TAB,
    ),
    Keybinding(
        dpg.mvKey_D,
        True,
        True,
        False,
        Action.SELECT_DATA_SETS_TAB,
    ),
    Keybinding(
        dpg.mvKey_F,
        True,
        True,
        False,
        Action.SELECT_FITTING_TAB,
    ),
    Keybinding(
        dpg.mvKey_K,
        True,
        True,
        False,
        Action.SELECT_KRAMERS_KRONIG_TAB,
    ),
    Keybinding(
        dpg.mvKey_O,
        True,
        True,
        False,
        Action.SELECT_OVERVIEW_TAB,
    ),
    Keybinding(
        dpg.mvKey_P,
        True,
        True,
        False,
        Action.SELECT_PLOTTING_TAB,
    ),
    Keybinding(
        dpg.mvKey_S,
        True,
        True,
        False,
        Action.SELECT_SIMULATION_TAB,
    ),
    Keybinding(
        dpg.mvKey_Return,
        False if dpg.get_platform() == dpg.mvPlatform_Windows else True,
        True if dpg.get_platform() == dpg.mvPlatform_Windows else False,
        False,
        Action.PERFORM_ACTION,
    ),
    Keybinding(
        dpg.mvKey_Delete,
        True,
        False,
        False,
        Action.DELETE_RESULT,
    ),
    Keybinding(
        dpg.mvKey_Next,
        False,
        False,
        False,
        Action.NEXT_PRIMARY_RESULT,
    ),
    Keybinding(
        dpg.mvKey_Prior,
        False,
        False,
        False,
        Action.PREVIOUS_PRIMARY_RESULT,
    ),
    Keybinding(
        dpg.mvKey_Next,
        True,
        False,
        False,
        Action.NEXT_SECONDARY_RESULT,
    ),
    Keybinding(
        dpg.mvKey_Prior,
        True,
        False,
        False,
        Action.PREVIOUS_SECONDARY_RESULT,
    ),
    Keybinding(
        dpg.mvKey_A,
        True,
        False,
        False,
        Action.APPLY_SETTINGS,
    ),
    Keybinding(
        dpg.mvKey_M,
        True,
        False,
        False,
        Action.APPLY_MASK,
    ),
    Keybinding(
        dpg.mvKey_N,
        True,
        False,
        False,
        Action.SHOW_ENLARGED_NYQUIST,
    ),
    Keybinding(
        dpg.mvKey_D,
        True,
        False,
        False,
        Action.SHOW_ENLARGED_DRT,
    ),
    Keybinding(
        dpg.mvKey_I,
        True,
        False,
        False,
        Action.SHOW_ENLARGED_IMPEDANCE,
    ),
    Keybinding(
        dpg.mvKey_B,
        True,
        False,
        False,
        Action.SHOW_ENLARGED_BODE,
    ),
    Keybinding(
        dpg.mvKey_R,
        True,
        False,
        False,
        Action.SHOW_ENLARGED_RESIDUALS,
    ),
    Keybinding(
        dpg.mvKey_E,
        True,
        False,
        False,
        Action.SHOW_CIRCUIT_EDITOR,
    ),
    Keybinding(
        dpg.mvKey_D,
        True,
        False,
        True,
        Action.COPY_DRT_DATA,
    ),
    Keybinding(
        dpg.mvKey_I,
        True,
        False,
        True,
        Action.COPY_IMPEDANCE_DATA,
    ),
    Keybinding(
        dpg.mvKey_N,
        True,
        False,
        True,
        Action.COPY_NYQUIST_DATA,
    ),
    Keybinding(
        dpg.mvKey_B,
        True,
        False,
        True,
        Action.COPY_BODE_DATA,
    ),
    Keybinding(
        dpg.mvKey_R,
        True,
        False,
        True,
        Action.COPY_RESIDUALS_DATA,
    ),
    Keybinding(
        dpg.mvKey_C,
        True,
        False,
        False,
        Action.COPY_OUTPUT,
    ),
    Keybinding(
        dpg.mvKey_A,
        True,
        False,
        False,
        Action.AVERAGE_DATA_SETS,
    ),
    Keybinding(
        dpg.mvKey_T,
        True,
        False,
        False,
        Action.TOGGLE_DATA_POINTS,
    ),
    Keybinding(
        dpg.mvKey_C,
        True,
        False,
        False,
        Action.COPY_DATA_SET_MASK,
    ),
    Keybinding(
        dpg.mvKey_S,
        True,
        False,
        False,
        Action.SUBTRACT_IMPEDANCE,
    ),
    Keybinding(
        dpg.mvKey_A,
        True,
        False,
        False,
        Action.SELECT_ALL_PLOT_SERIES,
    ),
    Keybinding(
        dpg.mvKey_A,
        True,
        False,
        True,
        Action.UNSELECT_ALL_PLOT_SERIES,
    ),
    Keybinding(
        dpg.mvKey_C,
        True,
        False,
        False,
        Action.COPY_PLOT_APPEARANCE,
    ),
    Keybinding(
        dpg.mvKey_C,
        True,
        False,
        True,
        Action.COPY_PLOT_DATA,
    ),
    Keybinding(
        dpg.mvKey_E,
        True,
        False,
        False,
        Action.EXPAND_COLLAPSE_SIDEBAR,
    ),
    Keybinding(
        dpg.mvKey_P,
        True,
        False,
        False,
        Action.EXPORT_PLOT,
    ),
]

# TODO: Replace string keys with int keys (e.g. themes.nyquist.data) and use strings only in the
# config file
DEFAULT_MARKERS: Dict[str, int] = {
    "bode_magnitude_data": dpg.mvPlotMarker_Circle,
    "bode_magnitude_simulation": dpg.mvPlotMarker_Cross,
    "bode_phase_data": dpg.mvPlotMarker_Square,
    "bode_phase_simulation": dpg.mvPlotMarker_Plus,
    "impedance_imaginary_data": dpg.mvPlotMarker_Square,
    "impedance_imaginary_simulation": dpg.mvPlotMarker_Plus,
    "impedance_real_data": dpg.mvPlotMarker_Circle,
    "impedance_real_simulation": dpg.mvPlotMarker_Cross,
    "mu_Xps_Xps": dpg.mvPlotMarker_Square,
    "mu_Xps_mu": dpg.mvPlotMarker_Circle,
    "nyquist_data": dpg.mvPlotMarker_Circle,
    "nyquist_simulation": dpg.mvPlotMarker_Cross,
    "residuals_imaginary": dpg.mvPlotMarker_Square,
    "residuals_real": dpg.mvPlotMarker_Circle,
}

DEFAULT_COLORS: Dict[str, List[float]] = {
    "residuals_real": [
        238.0,
        51.0,
        119.0,
        190.0,
    ],
    "residuals_imaginary": [
        0.0,
        153.0,
        136.0,
        190.0,
    ],
    "nyquist_data": [
        51.0,
        187.0,
        238.0,
        190.0,
    ],
    "nyquist_simulation": [
        238.0,
        51.0,
        119.0,
        190.0,
    ],
    "bode_magnitude_data": [
        51.0,
        187.0,
        238.0,
        190.0,
    ],
    "bode_magnitude_simulation": [
        238.0,
        51.0,
        119.0,
        190.0,
    ],
    "bode_phase_data": [
        238.0,
        119.0,
        51.0,
        190.0,
    ],
    "bode_phase_simulation": [
        0.0,
        153.0,
        136.0,
        190.0,
    ],
    "mu_Xps_mu_criterion": [
        255.0,
        255.0,
        255.0,
        128.0,
    ],
    "mu_Xps_mu": [
        238.0,
        51.0,
        119.0,
        190.0,
    ],
    "mu_Xps_mu_highlight": [
        51.0,
        187.0,
        238.0,
        190.0,
    ],
    "mu_Xps_Xps": [
        0.0,
        153.0,
        136.0,
        190.0,
    ],
    "mu_Xps_Xps_highlight": [
        238.0,
        119.0,
        51.0,
        190.0,
    ],
    "impedance_real_data": [
        51.0,
        187.0,
        238.0,
        190.0,
    ],
    "impedance_real_simulation": [
        238.0,
        51.0,
        119.0,
        190.0,
    ],
    "impedance_imaginary_data": [
        238.0,
        119.0,
        51.0,
        190.0,
    ],
    "impedance_imaginary_simulation": [
        0.0,
        153.0,
        136.0,
        190.0,
    ],
    "drt_real_gamma": [
        51.0,
        187.0,
        238.0,
        190.0,
    ],
    "drt_mean_gamma": [
        238.0,
        119.0,
        51.0,
        190.0,
    ],
    "drt_credible_intervals": [
        238.0,
        119.0,
        51.0,
        48.0,
    ],
    "drt_imaginary_gamma": [
        238.0,
        119.0,
        51.0,
        190.0,
    ],
}

DEFAULT_TEST_SETTINGS: TestSettings = TestSettings(
    test=Test.COMPLEX,
    mode=TestMode.EXPLORATORY,
    num_RC=999,
    mu_criterion=0.85,
    add_capacitance=True,
    add_inductance=True,
    method=CNLSMethod.LEASTSQ,
    max_nfev=1000,
)

DEFAULT_FIT_SETTINGS: FitSettings = FitSettings(
    cdc="R([RW]C)",
    method=CNLSMethod.AUTO,
    weight=Weight.AUTO,
    max_nfev=1000,
)

DEFAULT_SIMULATION_SETTINGS: SimulationSettings = SimulationSettings(
    cdc="R([RW]C)",
    min_frequency=1.0e-2,
    max_frequency=1.0e5,
    num_per_decade=1,
)

DEFAULT_DRT_SETTINGS: DRTSettings = DRTSettings(
    method=DRTMethod.TR_RBF,
    mode=DRTMode.COMPLEX,
    lambda_value=1e-3,
    rbf_type=RBFType.GAUSSIAN,
    derivative_order=1,
    rbf_shape=RBFShape.FWHM,
    shape_coeff=0.5,
    inductance=False,
    credible_intervals=False,
    num_samples=2000,
    num_attempts=10,
    maximum_symmetry=0.5,
)

DEFAULT_PLOT_EXPORT_SETTINGS: PlotExportSettings = PlotExportSettings(
    units=PlotUnits.INCHES,
    width=10.0,
    height=6.0,
    dpi=100,
    preview_limit=PlotPreviewLimit.PX1024,
    show_title=True,
    show_legend=True,
    legend_location=PlotLegendLocation.AUTO,
    show_grid=False,
    has_tight_layout=True,
    num_per_decade=100,
    extension=".png",
    clear_registry=True,
    disable_preview=False,
)
