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
    ZHITInterpolation,
    ZHITSmoothing,
    ZHITWindow,
)
from deareis.keybindings import Keybinding
from deareis.data.plotting import PlotExportSettings
from deareis.data import (
    DRTSettings,
    FitSettings,
    SimulationSettings,
    TestSettings,
    ZHITSettings,
)

DEFAULT_KEYBINDINGS: List[Keybinding] = [
    Keybinding(
        key=dpg.mvKey_N,
        mod_alt=False,
        mod_ctrl=True,
        mod_shift=False,
        action=Action.NEW_PROJECT,
    ),
    Keybinding(
        key=dpg.mvKey_O,
        mod_alt=False,
        mod_ctrl=True,
        mod_shift=False,
        action=Action.LOAD_PROJECT,
    ),
    Keybinding(
        key=dpg.mvKey_Q,
        mod_alt=False,
        mod_ctrl=True,
        mod_shift=False,
        action=Action.EXIT,
    ),
    Keybinding(
        key=dpg.mvKey_Next,
        mod_alt=False,
        mod_ctrl=False,
        mod_shift=True,
        action=Action.NEXT_PROGRAM_TAB,
    ),
    Keybinding(
        key=dpg.mvKey_Prior,
        mod_alt=False,
        mod_ctrl=False,
        mod_shift=True,
        action=Action.PREVIOUS_PROGRAM_TAB,
    ),
    Keybinding(
        key=dpg.mvKey_F1,
        mod_alt=False,
        mod_ctrl=False,
        mod_shift=False,
        action=Action.SHOW_SETTINGS_APPEARANCE,
    ),
    Keybinding(
        key=dpg.mvKey_F2,
        mod_alt=False,
        mod_ctrl=False,
        mod_shift=False,
        action=Action.SHOW_SETTINGS_DEFAULTS,
    ),
    Keybinding(
        key=dpg.mvKey_F3,
        mod_alt=False,
        mod_ctrl=False,
        mod_shift=False,
        action=Action.SHOW_SETTINGS_KEYBINDINGS,
    ),
    Keybinding(
        key=dpg.mvKey_F11,
        mod_alt=False,
        mod_ctrl=False,
        mod_shift=False,
        action=Action.SHOW_HELP_LICENSES,
    ),
    Keybinding(
        key=dpg.mvKey_F12,
        mod_alt=False,
        mod_ctrl=False,
        mod_shift=False,
        action=Action.SHOW_HELP_ABOUT,
    ),
    Keybinding(
        key=dpg.mvKey_P,
        mod_alt=False,
        mod_ctrl=True,
        mod_shift=False,
        action=Action.SHOW_COMMAND_PALETTE,
    ),
    Keybinding(
        key=dpg.mvKey_P,
        mod_alt=False,
        mod_ctrl=True,
        mod_shift=True,
        action=Action.SHOW_DATA_SET_PALETTE,
    ),
    Keybinding(
        key=dpg.mvKey_P,
        mod_alt=True,
        mod_ctrl=True,
        mod_shift=True,
        action=Action.SHOW_RESULT_PALETTE,
    ),
    Keybinding(
        key=dpg.mvKey_S,
        mod_alt=False,
        mod_ctrl=True,
        mod_shift=False,
        action=Action.SAVE_PROJECT,
    ),
    Keybinding(
        key=dpg.mvKey_S,
        mod_alt=False,
        mod_ctrl=True,
        mod_shift=True,
        action=Action.SAVE_PROJECT_AS,
    ),
    Keybinding(
        key=dpg.mvKey_W,
        mod_alt=False,
        mod_ctrl=True,
        mod_shift=False,
        action=Action.CLOSE_PROJECT,
    ),
    Keybinding(
        key=dpg.mvKey_Z,
        mod_alt=False,
        mod_ctrl=True,
        mod_shift=False,
        action=Action.UNDO,
    ),
    Keybinding(
        key=dpg.mvKey_Y if dpg.get_platform() == dpg.mvPlatform_Windows else dpg.mvKey_Z,
        mod_alt=False,
        mod_ctrl=True,
        mod_shift=False if dpg.get_platform() == dpg.mvPlatform_Windows else True,
        action=Action.REDO,
    ),
    Keybinding(
        key=dpg.mvKey_Next,
        mod_alt=False,
        mod_ctrl=True,
        mod_shift=False,
        action=Action.NEXT_PROJECT_TAB,
    ),
    Keybinding(
        key=dpg.mvKey_Prior,
        mod_alt=False,
        mod_ctrl=True,
        mod_shift=False,
        action=Action.PREVIOUS_PROJECT_TAB,
    ),
    Keybinding(
        key=dpg.mvKey_D,
        mod_alt=True,
        mod_ctrl=True,
        mod_shift=False,
        action=Action.SELECT_DATA_SETS_TAB,
    ),
    Keybinding(
        key=dpg.mvKey_F,
        mod_alt=True,
        mod_ctrl=True,
        mod_shift=False,
        action=Action.SELECT_FITTING_TAB,
    ),
    Keybinding(
        key=dpg.mvKey_K,
        mod_alt=True,
        mod_ctrl=True,
        mod_shift=False,
        action=Action.SELECT_KRAMERS_KRONIG_TAB,
    ),
    Keybinding(
        key=dpg.mvKey_Z,
        mod_alt=True,
        mod_ctrl=True,
        mod_shift=False,
        action=Action.SELECT_ZHIT_TAB,
    ),
    Keybinding(
        key=dpg.mvKey_T,
        mod_alt=True,
        mod_ctrl=True,
        mod_shift=False,
        action=Action.SELECT_DRT_TAB,
    ),
    Keybinding(
        key=dpg.mvKey_Home,
        mod_alt=False,
        mod_ctrl=False,
        mod_shift=False,
        action=Action.SELECT_HOME_TAB,
    ),
    Keybinding(
        key=dpg.mvKey_O,
        mod_alt=True,
        mod_ctrl=True,
        mod_shift=False,
        action=Action.SELECT_OVERVIEW_TAB,
    ),
    Keybinding(
        key=dpg.mvKey_P,
        mod_alt=True,
        mod_ctrl=True,
        mod_shift=False,
        action=Action.SELECT_PLOTTING_TAB,
    ),
    Keybinding(
        key=dpg.mvKey_S,
        mod_alt=True,
        mod_ctrl=True,
        mod_shift=False,
        action=Action.SELECT_SIMULATION_TAB,
    ),
    Keybinding(
        key=dpg.mvKey_Return,
        mod_alt=False if dpg.get_platform() == dpg.mvPlatform_Windows else True,
        mod_ctrl=True if dpg.get_platform() == dpg.mvPlatform_Windows else False,
        mod_shift=False,
        action=Action.PERFORM_ACTION,
    ),
    Keybinding(
        key=dpg.mvKey_Return,
        mod_alt=False if dpg.get_platform() == dpg.mvPlatform_Windows else True,
        mod_ctrl=True if dpg.get_platform() == dpg.mvPlatform_Windows else False,
        mod_shift=True,
        action=Action.BATCH_PERFORM_ACTION,
    ),
    Keybinding(
        key=dpg.mvKey_Delete,
        mod_alt=True,
        mod_ctrl=False,
        mod_shift=False,
        action=Action.DELETE_RESULT,
    ),
    Keybinding(
        key=dpg.mvKey_Next,
        mod_alt=False,
        mod_ctrl=False,
        mod_shift=False,
        action=Action.NEXT_PRIMARY_RESULT,
    ),
    Keybinding(
        key=dpg.mvKey_Prior,
        mod_alt=False,
        mod_ctrl=False,
        mod_shift=False,
        action=Action.PREVIOUS_PRIMARY_RESULT,
    ),
    Keybinding(
        key=dpg.mvKey_Next,
        mod_alt=True,
        mod_ctrl=False,
        mod_shift=False,
        action=Action.NEXT_SECONDARY_RESULT,
    ),
    Keybinding(
        key=dpg.mvKey_Prior,
        mod_alt=True,
        mod_ctrl=False,
        mod_shift=False,
        action=Action.PREVIOUS_SECONDARY_RESULT,
    ),
    Keybinding(
        key=dpg.mvKey_A,
        mod_alt=True,
        mod_ctrl=False,
        mod_shift=False,
        action=Action.APPLY_SETTINGS,
    ),
    Keybinding(
        key=dpg.mvKey_M,
        mod_alt=True,
        mod_ctrl=False,
        mod_shift=False,
        action=Action.APPLY_MASK,
    ),
    Keybinding(
        key=dpg.mvKey_N,
        mod_alt=True,
        mod_ctrl=False,
        mod_shift=False,
        action=Action.SHOW_ENLARGED_NYQUIST,
    ),
    Keybinding(
        key=dpg.mvKey_D,
        mod_alt=True,
        mod_ctrl=False,
        mod_shift=False,
        action=Action.SHOW_ENLARGED_DRT,
    ),
    Keybinding(
        key=dpg.mvKey_R,
        mod_alt=True,
        mod_ctrl=False,
        mod_shift=False,
        action=Action.SHOW_ENLARGED_IMPEDANCE,
    ),
    Keybinding(
        key=dpg.mvKey_B,
        mod_alt=True,
        mod_ctrl=False,
        mod_shift=False,
        action=Action.SHOW_ENLARGED_BODE,
    ),
    Keybinding(
        key=dpg.mvKey_E,
        mod_alt=True,
        mod_ctrl=False,
        mod_shift=False,
        action=Action.SHOW_CIRCUIT_EDITOR,
    ),
    Keybinding(
        key=dpg.mvKey_D,
        mod_alt=True,
        mod_ctrl=False,
        mod_shift=True,
        action=Action.COPY_DRT_DATA,
    ),
    Keybinding(
        key=dpg.mvKey_I,
        mod_alt=True,
        mod_ctrl=False,
        mod_shift=True,
        action=Action.COPY_IMPEDANCE_DATA,
    ),
    Keybinding(
        key=dpg.mvKey_N,
        mod_alt=True,
        mod_ctrl=False,
        mod_shift=True,
        action=Action.COPY_NYQUIST_DATA,
    ),
    Keybinding(
        key=dpg.mvKey_B,
        mod_alt=True,
        mod_ctrl=False,
        mod_shift=True,
        action=Action.COPY_BODE_DATA,
    ),
    Keybinding(
        key=dpg.mvKey_R,
        mod_alt=True,
        mod_ctrl=False,
        mod_shift=True,
        action=Action.COPY_RESIDUALS_DATA,
    ),
    Keybinding(
        key=dpg.mvKey_C,
        mod_alt=True,
        mod_ctrl=False,
        mod_shift=False,
        action=Action.COPY_OUTPUT,
    ),
    Keybinding(
        key=dpg.mvKey_A,
        mod_alt=True,
        mod_ctrl=False,
        mod_shift=False,
        action=Action.AVERAGE_DATA_SETS,
    ),
    Keybinding(
        key=dpg.mvKey_T,
        mod_alt=True,
        mod_ctrl=False,
        mod_shift=False,
        action=Action.TOGGLE_DATA_POINTS,
    ),
    Keybinding(
        key=dpg.mvKey_C,
        mod_alt=True,
        mod_ctrl=False,
        mod_shift=False,
        action=Action.COPY_DATA_SET_MASK,
    ),
    Keybinding(
        key=dpg.mvKey_S,
        mod_alt=True,
        mod_ctrl=False,
        mod_shift=False,
        action=Action.SUBTRACT_IMPEDANCE,
    ),
    Keybinding(
        key=dpg.mvKey_I,
        mod_alt=True,
        mod_ctrl=False,
        mod_shift=False,
        action=Action.INTERPOLATE_POINTS,
    ),
    Keybinding(
        key=dpg.mvKey_A,
        mod_alt=True,
        mod_ctrl=False,
        mod_shift=False,
        action=Action.SELECT_ALL_PLOT_SERIES,
    ),
    Keybinding(
        key=dpg.mvKey_A,
        mod_alt=True,
        mod_ctrl=False,
        mod_shift=True,
        action=Action.UNSELECT_ALL_PLOT_SERIES,
    ),
    Keybinding(
        key=dpg.mvKey_C,
        mod_alt=True,
        mod_ctrl=False,
        mod_shift=False,
        action=Action.COPY_PLOT_APPEARANCE,
    ),
    Keybinding(
        key=dpg.mvKey_C,
        mod_alt=True,
        mod_ctrl=False,
        mod_shift=True,
        action=Action.COPY_PLOT_DATA,
    ),
    Keybinding(
        key=dpg.mvKey_E,
        mod_alt=True,
        mod_ctrl=False,
        mod_shift=False,
        action=Action.EXPAND_COLLAPSE_SIDEBAR,
    ),
    Keybinding(
        key=dpg.mvKey_P,
        mod_alt=True,
        mod_ctrl=False,
        mod_shift=False,
        action=Action.EXPORT_PLOT,
    ),
    Keybinding(
        key=dpg.mvKey_P,
        mod_alt=True,
        mod_ctrl=False,
        mod_shift=False,
        action=Action.ADJUST_PARAMETERS,
    ),
    Keybinding(
        key=dpg.mvKey_L,
        mod_alt=True,
        mod_ctrl=False,
        mod_shift=False,
        action=Action.LOAD_SIMULATION_AS_DATA_SET,
    ),
    Keybinding(
        key=dpg.mvKey_L,
        mod_alt=True,
        mod_ctrl=False,
        mod_shift=False,
        action=Action.LOAD_ZHIT_AS_DATA_SET,
    ),
    Keybinding(
        key=dpg.mvKey_W,
        mod_alt=True,
        mod_ctrl=False,
        mod_shift=False,
        action=Action.PREVIEW_ZHIT_WEIGHTS,
    ),
    Keybinding(
        key=dpg.mvKey_D,
        mod_alt=True,
        mod_ctrl=False,
        mod_shift=False,
        action=Action.DUPLICATE_PLOT,
    ),
    Keybinding(
        key=dpg.mvKey_Next,
        mod_alt=True,
        mod_ctrl=False,
        mod_shift=True,
        action=Action.NEXT_PLOT_TAB,
    ),
    Keybinding(
        key=dpg.mvKey_Prior,
        mod_alt=True,
        mod_ctrl=False,
        mod_shift=True,
        action=Action.PREVIOUS_PLOT_TAB,
    ),
]

# TODO: Replace string keys with int keys (e.g. themes.nyquist.data) and use strings only in the
# config file?
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
        0.0,
        153.0,
        136.0,
        190.0,
    ],
    "residuals_imaginary": [
        238.0,
        51.0,
        119.0,
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
        238.0,
        119.0,
        51.0,
        190.0,
    ],
    "impedance_real_simulation": [
        0.0,
        153.0,
        136.0,
        190.0,
    ],
    "impedance_imaginary_data": [
        51.0,
        187.0,
        238.0,
        190.0,
    ],
    "impedance_imaginary_simulation": [
        238.0,
        51.0,
        119.0,
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
    timeout=60,
    num_samples=2000,
    num_attempts=10,
    maximum_symmetry=0.5,
    fit=None,
    gaussian_width=0.15,
    num_per_decade=100,
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


DEFAULT_ZHIT_SETTINGS: ZHITSettings = ZHITSettings(
    smoothing=ZHITSmoothing.LOWESS,
    num_points=5,
    polynomial_order=2,
    num_iterations=3,
    interpolation=ZHITInterpolation.AKIMA,
    window=ZHITWindow.HANN,
    window_center=1.5,
    window_width=3.0,
)
