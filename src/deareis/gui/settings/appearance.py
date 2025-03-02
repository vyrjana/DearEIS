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

from uuid import uuid4
from time import time
import dearpygui.dearpygui as dpg
import deareis.themes as themes
from deareis.themes import PLOT_MARKERS
from typing import (
    Dict,
    List,
    Optional,
    Tuple,
)
from deareis.utility import calculate_window_position_dimensions
from deareis.tooltips import attach_tooltip
from deareis.state import STATE
from deareis.gui.plots import (
    Bode,
    DRT,
    Impedance,
    Nyquist,
    Residuals,
)
from numpy import (
    array,
    exp,
    log10 as log,
    logspace,
    ndarray,
)
from numpy.random import normal
from pyimpspec import Circuit
from deareis.data import (
    DRTResult,
    DRTSettings,
    DataSet,
)
from deareis.enums import (
    CrossValidationMethod,
    DRTMethod,
    DRTMode,
    RBFShape,
    RBFType,
    TRNNLSLambdaMethod,
)
import pyimpspec
from deareis.signals import Signal
import deareis.signals as signals
from deareis.config.defaults import (
    DEFAULT_COLORS,
    DEFAULT_MARKERS,
)
from deareis.typing.helpers import Tag



# TODO: Refactor color and marker widgets to reduce code duplication
# TODO: Refactor update_*_* functions to reduce code duplication


class AppearanceSettings:
    def __init__(self):
        self.create_window()
        self.register_keybindings()
        signals.emit(Signal.BLOCK_KEYBINDINGS, window=self.window, window_object=self)

    def create_window(self):
        self.marker_items: List[str] = list(PLOT_MARKERS.keys())
        self.marker_label_lookup: Dict[int, str] = {
            v: k for k, v in PLOT_MARKERS.items()
        }
        self.label_pad: int = 56
        self.data: DataSet
        self.sim_data: DataSet
        self.smooth_data: DataSet
        self.residuals: ndarray
        self.noise: ndarray
        self.drt: DRTResult
        (
            self.data,
            self.sim_data,
            self.smooth_data,
            self.residuals,
            self.noise,
            self.drt,
        ) = self.generate_data()
        x: int
        y: int
        w: int
        h: int

        x, y, w, h = calculate_window_position_dimensions(600, 540)
        self.window: Tag = dpg.generate_uuid()
        with dpg.window(
            label="Settings - appearance",
            modal=True,
            pos=(x, y),
            width=w,
            height=h,
            no_move=False,
            no_resize=True,
            on_close=self.close,
            tag=self.window,
        ):
            self.create_general_settings()
            self.create_bode_settings()
            self.create_drt_settings()
            self.create_impedance_settings()
            self.create_nyquist_settings()
            self.create_residuals_settings()
            self.create_exploratory_test_settings()
            # TODO: Settings for Z-HIT weights preview plot?

    def create_general_settings(self):
        with dpg.collapsing_header(label="General", default_open=True):
            with dpg.group(horizontal=True):
                dpg.add_text(
                    "Number of points per decade in simulated response".rjust(
                        self.label_pad
                    )
                )
                attach_tooltip(
                    """
This affects how smooth the lines will look when plotting the impedance response of, e.g., fitted circuits, but it may also affect performance when rendering the graphical user interface. This setting also affects how many points are included when copying plot data as character-separated values (CSV). Changes made to this setting will take effect the next time a plot is redrawn.
                    """.strip()
                )
                dpg.add_slider_int(
                    default_value=STATE.config.num_per_decade_in_simulated_lines,
                    min_value=1,
                    max_value=200,
                    clamped=True,
                    callback=self.update_simulated_num_per_decade,
                    width=-1,
                )
            dpg.add_spacer(height=8)

    def create_bode_settings(self):
        with dpg.collapsing_header(label="Bode plots", default_open=True):
            self.bode_plot = Bode(width=-1, height=200)
            self.bode_data_mag_color: Tag = dpg.generate_uuid()
            self.bode_data_phase_color: Tag = dpg.generate_uuid()
            self.bode_sim_mag_color: Tag = dpg.generate_uuid()
            self.bode_sim_phase_color: Tag = dpg.generate_uuid()
            self.bode_data_mag_marker: Tag = dpg.generate_uuid()
            self.bode_data_phase_marker: Tag = dpg.generate_uuid()
            self.bode_sim_mag_marker: Tag = dpg.generate_uuid()
            self.bode_sim_phase_marker: Tag = dpg.generate_uuid()
            # Data colors and markers
            with dpg.group(horizontal=True):
                dpg.add_text("Data - magnitude".rjust(self.label_pad))
                dpg.add_color_edit(
                    default_value=STATE.config.colors["bode_magnitude_data"],
                    alpha_preview=dpg.mvColorEdit_AlphaPreviewHalf,
                    no_inputs=True,
                    alpha_bar=True,
                    callback=self.update_bode_color,
                    user_data=themes.bode.magnitude_data,
                    tag=self.bode_data_mag_color,
                )
                dpg.add_combo(
                    items=self.marker_items,
                    default_value=self.marker_label_lookup[
                        STATE.config.markers["bode_magnitude_data"]
                    ],
                    callback=self.update_bode_marker,
                    user_data=themes.bode.magnitude_data,
                    tag=self.bode_data_mag_marker,
                    width=-1,
                )
            with dpg.group(horizontal=True):
                dpg.add_text("Data - phase".rjust(self.label_pad))
                dpg.add_color_edit(
                    default_value=STATE.config.colors["bode_phase_data"],
                    alpha_preview=dpg.mvColorEdit_AlphaPreviewHalf,
                    no_inputs=True,
                    alpha_bar=True,
                    callback=self.update_bode_color,
                    user_data=themes.bode.phase_data,
                    tag=self.bode_data_phase_color,
                )
                dpg.add_combo(
                    items=self.marker_items,
                    default_value=self.marker_label_lookup[
                        STATE.config.markers["bode_phase_data"]
                    ],
                    callback=self.update_bode_marker,
                    user_data=themes.bode.phase_data,
                    tag=self.bode_data_phase_marker,
                    width=-1,
                )
            # Sim/fit colors and markers
            with dpg.group(horizontal=True):
                dpg.add_text("Fit/simulation - magnitude".rjust(self.label_pad))
                dpg.add_color_edit(
                    default_value=STATE.config.colors["bode_magnitude_simulation"],
                    alpha_preview=dpg.mvColorEdit_AlphaPreviewHalf,
                    no_inputs=True,
                    alpha_bar=True,
                    callback=self.update_bode_color,
                    user_data=themes.bode.magnitude_simulation,
                    tag=self.bode_sim_mag_color,
                )
                dpg.add_combo(
                    items=self.marker_items,
                    default_value=self.marker_label_lookup[
                        STATE.config.markers["bode_magnitude_simulation"]
                    ],
                    callback=self.update_bode_marker,
                    user_data=themes.bode.magnitude_simulation,
                    tag=self.bode_sim_mag_marker,
                    width=-1,
                )
            with dpg.group(horizontal=True):
                dpg.add_text("Fit/simulation - phase".rjust(self.label_pad))
                dpg.add_color_edit(
                    default_value=STATE.config.colors["bode_phase_simulation"],
                    alpha_preview=dpg.mvColorEdit_AlphaPreviewHalf,
                    no_inputs=True,
                    alpha_bar=True,
                    callback=self.update_bode_color,
                    user_data=themes.bode.phase_simulation,
                    tag=self.bode_sim_phase_color,
                )
                dpg.add_combo(
                    items=self.marker_items,
                    default_value=self.marker_label_lookup[
                        STATE.config.markers["bode_phase_simulation"]
                    ],
                    callback=self.update_bode_marker,
                    user_data=themes.bode.phase_simulation,
                    tag=self.bode_sim_phase_marker,
                    width=-1,
                )
            with dpg.group(horizontal=True):
                dpg.add_text("".rjust(self.label_pad))
                dpg.add_button(
                    label="Restore defaults",
                    callback=self.reset_bode_plot,
                    width=-1,
                )
            self.update_bode_plot(True)
            dpg.add_spacer(height=8)

    def create_drt_settings(self):
        with dpg.collapsing_header(label="DRT plots", default_open=True):
            self.drt_plot = DRT(width=-1, height=200)
            self.drt_real_gamma_color: Tag = dpg.generate_uuid()
            self.drt_imaginary_gamma_color: Tag = dpg.generate_uuid()
            self.drt_mean_gamma_color: Tag = dpg.generate_uuid()
            self.drt_credible_intervals_color: Tag = dpg.generate_uuid()
            with dpg.group(horizontal=True):
                dpg.add_text("Gamma/real".rjust(self.label_pad))
                dpg.add_color_edit(
                    default_value=STATE.config.colors["drt_real_gamma"],
                    alpha_preview=dpg.mvColorEdit_AlphaPreviewHalf,
                    no_inputs=True,
                    alpha_bar=True,
                    callback=self.update_drt_color,
                    user_data=themes.drt.real_gamma,
                    tag=self.drt_real_gamma_color,
                )
            with dpg.group(horizontal=True):
                dpg.add_text("Imaginary".rjust(self.label_pad))
                dpg.add_color_edit(
                    default_value=STATE.config.colors["drt_imaginary_gamma"],
                    alpha_preview=dpg.mvColorEdit_AlphaPreviewHalf,
                    no_inputs=True,
                    alpha_bar=True,
                    callback=self.update_drt_color,
                    user_data=themes.drt.imaginary_gamma,
                    tag=self.drt_imaginary_gamma_color,
                )
            with dpg.group(horizontal=True):
                dpg.add_text("Mean and 3-sigma CI".rjust(self.label_pad))
                dpg.add_color_edit(
                    default_value=STATE.config.colors["drt_mean_gamma"],
                    alpha_preview=dpg.mvColorEdit_AlphaPreviewHalf,
                    no_inputs=True,
                    alpha_bar=True,
                    callback=self.update_drt_color,
                    user_data=themes.drt.mean_gamma,
                    tag=self.drt_mean_gamma_color,
                )
                dpg.add_color_edit(
                    default_value=STATE.config.colors["drt_credible_intervals"],
                    alpha_preview=dpg.mvColorEdit_AlphaPreviewHalf,
                    no_inputs=True,
                    alpha_bar=True,
                    callback=self.update_drt_color,
                    user_data=themes.drt.credible_intervals,
                    tag=self.drt_credible_intervals_color,
                )
            with dpg.group(horizontal=True):
                dpg.add_text("".rjust(self.label_pad))
                dpg.add_button(
                    label="Restore defaults",
                    callback=self.reset_drt_plot,
                    width=-1,
                )
            self.update_drt_plot(True)
            dpg.add_spacer(height=8)

    def create_impedance_settings(self):
        with dpg.collapsing_header(label="Impedance plots", default_open=True):
            self.impedance_plot = Impedance(width=-1, height=200)
            self.impedance_real_data_color: Tag = dpg.generate_uuid()
            self.impedance_real_simulation_color: Tag = dpg.generate_uuid()
            self.impedance_imaginary_data_color: Tag = dpg.generate_uuid()
            self.impedance_imaginary_simulation_color: Tag = dpg.generate_uuid()
            self.impedance_real_data_marker: Tag = dpg.generate_uuid()
            self.impedance_real_simulation_marker: Tag = dpg.generate_uuid()
            self.impedance_imaginary_data_marker: Tag = dpg.generate_uuid()
            self.impedance_imaginary_simulation_marker: Tag = dpg.generate_uuid()
            # Data colors and markers
            with dpg.group(horizontal=True):
                dpg.add_text("Data - real".rjust(self.label_pad))
                dpg.add_color_edit(
                    default_value=STATE.config.colors["impedance_real_data"],
                    alpha_preview=dpg.mvColorEdit_AlphaPreviewHalf,
                    no_inputs=True,
                    alpha_bar=True,
                    callback=self.update_impedance_color,
                    user_data=themes.impedance.real_data,
                    tag=self.impedance_real_data_color,
                )
                dpg.add_combo(
                    items=self.marker_items,
                    default_value=self.marker_label_lookup[
                        STATE.config.markers["impedance_real_data"]
                    ],
                    callback=self.update_impedance_marker,
                    user_data=themes.impedance.real_data,
                    tag=self.impedance_real_data_marker,
                    width=-1,
                )
            with dpg.group(horizontal=True):
                dpg.add_text("Data - imaginary".rjust(self.label_pad))
                dpg.add_color_edit(
                    default_value=STATE.config.colors["impedance_imaginary_data"],
                    alpha_preview=dpg.mvColorEdit_AlphaPreviewHalf,
                    no_inputs=True,
                    alpha_bar=True,
                    callback=self.update_impedance_color,
                    user_data=themes.impedance.imaginary_data,
                    tag=self.impedance_imaginary_data_color,
                )
                dpg.add_combo(
                    items=self.marker_items,
                    default_value=self.marker_label_lookup[
                        STATE.config.markers["impedance_imaginary_data"]
                    ],
                    callback=self.update_impedance_marker,
                    user_data=themes.impedance.imaginary_data,
                    tag=self.impedance_imaginary_data_marker,
                    width=-1,
                )
            # Sim/fit colors and markers
            with dpg.group(horizontal=True):
                dpg.add_text("Fit/simulation - real".rjust(self.label_pad))
                dpg.add_color_edit(
                    default_value=STATE.config.colors["impedance_real_simulation"],
                    alpha_preview=dpg.mvColorEdit_AlphaPreviewHalf,
                    no_inputs=True,
                    alpha_bar=True,
                    callback=self.update_impedance_color,
                    user_data=themes.impedance.real_simulation,
                    tag=self.impedance_real_simulation_color,
                )
                dpg.add_combo(
                    items=self.marker_items,
                    default_value=self.marker_label_lookup[
                        STATE.config.markers["impedance_real_simulation"]
                    ],
                    callback=self.update_impedance_marker,
                    user_data=themes.impedance.real_simulation,
                    tag=self.impedance_real_simulation_marker,
                    width=-1,
                )
            with dpg.group(horizontal=True):
                dpg.add_text("Fit/simulation - imaginary".rjust(self.label_pad))
                dpg.add_color_edit(
                    default_value=STATE.config.colors["impedance_imaginary_simulation"],
                    alpha_preview=dpg.mvColorEdit_AlphaPreviewHalf,
                    no_inputs=True,
                    alpha_bar=True,
                    callback=self.update_impedance_color,
                    user_data=themes.impedance.imaginary_simulation,
                    tag=self.impedance_imaginary_simulation_color,
                )
                dpg.add_combo(
                    items=self.marker_items,
                    default_value=self.marker_label_lookup[
                        STATE.config.markers["impedance_imaginary_simulation"]
                    ],
                    callback=self.update_impedance_marker,
                    user_data=themes.impedance.imaginary_simulation,
                    tag=self.impedance_imaginary_simulation_marker,
                    width=-1,
                )
            with dpg.group(horizontal=True):
                dpg.add_text("".rjust(self.label_pad))
                dpg.add_button(
                    label="Restore defaults",
                    callback=self.reset_impedance_plot,
                    width=-1,
                )
            self.update_impedance_plot(True)
            dpg.add_spacer(height=8)

    def create_nyquist_settings(self):
        with dpg.collapsing_header(label="Nyquist plots", default_open=True):
            self.nyquist_plot = Nyquist(width=-1, height=200)
            self.nyquist_data_color: Tag = dpg.generate_uuid()
            self.nyquist_sim_color: Tag = dpg.generate_uuid()
            self.nyquist_data_marker: Tag = dpg.generate_uuid()
            self.nyquist_sim_marker: Tag = dpg.generate_uuid()
            # Data colors and markers
            with dpg.group(horizontal=True):
                dpg.add_text("Data".rjust(self.label_pad))
                dpg.add_color_edit(
                    default_value=STATE.config.colors["nyquist_data"],
                    alpha_preview=dpg.mvColorEdit_AlphaPreviewHalf,
                    no_inputs=True,
                    alpha_bar=True,
                    callback=self.update_nyquist_color,
                    user_data=themes.nyquist.data,
                    tag=self.nyquist_data_color,
                )
                dpg.add_combo(
                    items=self.marker_items,
                    default_value=self.marker_label_lookup[
                        STATE.config.markers["nyquist_data"]
                    ],
                    callback=self.update_nyquist_marker,
                    user_data=themes.nyquist.data,
                    tag=self.nyquist_data_marker,
                    width=-1,
                )
            # Sim/fit colors and markers
            with dpg.group(horizontal=True):
                dpg.add_text("Fit/simulation".rjust(self.label_pad))
                dpg.add_color_edit(
                    default_value=STATE.config.colors["nyquist_simulation"],
                    alpha_preview=dpg.mvColorEdit_AlphaPreviewHalf,
                    no_inputs=True,
                    alpha_bar=True,
                    callback=self.update_nyquist_color,
                    user_data=themes.nyquist.simulation,
                    tag=self.nyquist_sim_color,
                )
                dpg.add_combo(
                    items=self.marker_items,
                    default_value=self.marker_label_lookup[
                        STATE.config.markers["nyquist_simulation"]
                    ],
                    callback=self.update_nyquist_marker,
                    user_data=themes.nyquist.simulation,
                    tag=self.nyquist_sim_marker,
                    width=-1,
                )
            with dpg.group(horizontal=True):
                dpg.add_text("".rjust(self.label_pad))
                dpg.add_button(
                    label="Restore defaults",
                    callback=self.reset_nyquist_plot,
                    width=-1,
                )
            self.update_nyquist_plot(True)
            dpg.add_spacer(height=8)

    def create_residuals_settings(self):
        with dpg.collapsing_header(label="Residuals plots", default_open=True):
            self.residuals_plot = Residuals(width=-1, height=200)
            self.residuals_real_color: Tag = dpg.generate_uuid()
            self.residuals_imag_color: Tag = dpg.generate_uuid()
            self.residuals_real_marker: Tag = dpg.generate_uuid()
            self.residuals_imag_marker: Tag = dpg.generate_uuid()
            # Re(Z) color and marker
            with dpg.group(horizontal=True):
                dpg.add_text("Re(Z) residual".rjust(self.label_pad))
                dpg.add_color_edit(
                    default_value=STATE.config.colors["residuals_real"],
                    alpha_preview=dpg.mvColorEdit_AlphaPreviewHalf,
                    no_inputs=True,
                    alpha_bar=True,
                    callback=self.update_residuals_color,
                    user_data=themes.residuals.real,
                    tag=self.residuals_real_color,
                )
                dpg.add_combo(
                    items=self.marker_items,
                    default_value=self.marker_label_lookup[
                        STATE.config.markers["residuals_real"]
                    ],
                    callback=self.update_residuals_marker,
                    user_data=themes.residuals.real,
                    tag=self.residuals_real_marker,
                    width=-1,
                )
            # Im(Z) color and marker
            with dpg.group(horizontal=True):
                dpg.add_text("Im(Z) residual".rjust(self.label_pad))
                dpg.add_color_edit(
                    default_value=STATE.config.colors["residuals_imaginary"],
                    alpha_preview=dpg.mvColorEdit_AlphaPreviewHalf,
                    no_inputs=True,
                    alpha_bar=True,
                    callback=self.update_residuals_color,
                    user_data=themes.residuals.imaginary,
                    tag=self.residuals_imag_color,
                )
                dpg.add_combo(
                    items=self.marker_items,
                    default_value=self.marker_label_lookup[
                        STATE.config.markers["residuals_imaginary"]
                    ],
                    callback=self.update_residuals_marker,
                    user_data=themes.residuals.imaginary,
                    tag=self.residuals_imag_marker,
                    width=-1,
                )
            with dpg.group(horizontal=True):
                dpg.add_text("".rjust(self.label_pad))
                dpg.add_button(
                    label="Restore defaults",
                    callback=self.reset_residuals_plot,
                    width=-1,
                )
            self.update_residuals_plot(True)
            dpg.add_spacer(height=8)

    # TODO: Replace with settings for plots only used in the exploratory results window
    def create_exploratory_test_settings(self):
        return

    def register_keybindings(self):
        self.key_handler: Tag = dpg.generate_uuid()
        with dpg.handler_registry(tag=self.key_handler):
            dpg.add_key_release_handler(
                key=dpg.mvKey_Escape,
                callback=self.close,
            )

    def close(self):
        if dpg.does_item_exist(self.window):
            dpg.delete_item(self.window)
        if dpg.does_item_exist(self.key_handler):
            dpg.delete_item(self.key_handler)
        signals.emit(Signal.UNBLOCK_KEYBINDINGS)

    def generate_data(
        self,
        noise: Optional[ndarray] = None,
    ) -> Tuple[DataSet, DataSet, DataSet, ndarray, ndarray, ndarray, DRTResult]:
        circuit: Circuit = pyimpspec.parse_cdc("R{R=100}(C{C=1e-6}[R{R=500}W{Y=4e-4}])")
        data: DataSet = pyimpspec.simulate_spectrum(
            circuit,
            logspace(
                0,
                5,
                num=23,
            ),
        )
        Z: complex
        sd: float = 0.01
        if noise is None:
            noise = array(
                list(
                    map(
                        lambda Z: complex(
                            abs(Z) * normal(0, sd, 1),
                            abs(Z) * normal(0, sd, 1),
                        ),
                        data.get_impedances(),
                    )
                )
            )
        data.subtract_impedances(-noise)
        sim_data: DataSet = pyimpspec.simulate_spectrum(
            circuit,
            data.get_frequencies(),
        )
        smooth_data: DataSet = pyimpspec.simulate_spectrum(
            circuit,
            logspace(
                0,
                5,
                num=5 * STATE.config.num_per_decade_in_simulated_lines + 1,
            ),
        )
        residuals: ndarray = array(
            list(
                map(
                    lambda _: complex(*_),
                    zip(
                        (data.get_impedances().real - sim_data.get_impedances().real)
                        / abs(data.get_impedances())
                        * 100,
                        (data.get_impedances().imag - sim_data.get_impedances().imag)
                        / abs(data.get_impedances())
                        * 100,
                    ),
                )
            )
        )
        f: ndarray = smooth_data.get_frequencies()
        tau: ndarray = 1 / f
        gamma: ndarray = array(
            list(
                map(
                    lambda _: complex(*_),
                    zip(
                        map(
                            lambda _, a=1.1, b=0.0001, c=0.00001: a
                            * exp(-((_ - b) ** 2) / (2 * c**2)),
                            tau,
                        ),
                        map(
                            lambda _, a=1.0, b=0.001, c=0.0001: a
                            * exp(-((_ - b) ** 2) / (2 * c**2)),
                            tau,
                        ),
                    ),
                )
            )
        )
        mean_gamma: ndarray = array(
            list(
                map(
                    lambda _, a=0.9, b=0.012, c=0.001: a
                    * exp(-((_ - b) ** 2) / (2 * c**2)),
                    tau,
                )
            )
        )
        lower_bound: ndarray = array(
            list(
                map(
                    lambda _, a=0.4, b=0.012, c=0.001: a
                    * exp(-((_ - b) ** 2) / (2 * c**2)),
                    tau,
                )
            )
        )
        upper_bound: ndarray = array(
            list(
                map(
                    lambda _, a=1.4, b=0.012, c=0.002: a
                    * exp(-((_ - b) ** 2) / (2 * c**2)),
                    tau,
                )
            )
        )
        drt: DRTResult = DRTResult(
            uuid=uuid4().hex,
            timestamp=time(),
            time_constants=tau,
            real_gammas=gamma.real,
            imaginary_gammas=gamma.imag,
            frequencies=f,
            impedances=sim_data.get_impedances(),
            residuals=residuals,
            mean_gammas=mean_gamma,
            lower_bounds=lower_bound,
            upper_bounds=upper_bound,
            scores={},
            pseudo_chisqr=0.0,
            lambda_value=0.0,
            mask={},
            settings=DRTSettings(
                method=DRTMethod.BHT,
                mode=DRTMode.COMPLEX,
                lambda_value=0.0,
                rbf_type=RBFType.GAUSSIAN,
                derivative_order=1,
                rbf_shape=RBFShape.FWHM,
                shape_coeff=0.5,
                inductance=False,
                credible_intervals=True,
                timeout=60,
                num_samples=2000,
                num_attempts=50,
                maximum_symmetry=0.5,
                fit=None,
                gaussian_width=0.15,
                num_per_decade=100,
                cross_validation_method=CrossValidationMethod.NONE,
                tr_nnls_lambda_method=TRNNLSLambdaMethod.NONE,
            ),
        )
        return (
            data,
            sim_data,
            smooth_data,
            residuals,
            noise,
            drt,
        )

    def update_simulated_num_per_decade(self, sender: int, value: int):
        STATE.config.num_per_decade_in_simulated_lines = value
        (
            self.data,
            self.sim_data,
            self.smooth_data,
            self.residuals,
            _,
            _,
        ) = self.generate_data(self.noise)
        self.update_bode_plot()
        self.update_drt_plot()
        self.update_impedance_plot()
        self.update_nyquist_plot()
        self.update_residuals_plot()
        #self.update_muxps_plot()  # TODO: Update

    def update_bode_plot(self, adjust_limits: bool = False):
        self.bode_plot.clear()
        freq: ndarray = self.data.get_frequencies()
        Z: ndarray = self.data.get_impedances()
        self.bode_plot.plot(
            frequencies=freq,
            impedances=Z,
            labels=(
                "Mod(data)",
                "Phase(data)",
            ),
            themes=(
                themes.bode.magnitude_data,
                themes.bode.phase_data,
            ),
        )

        freq = self.smooth_data.get_frequencies()
        Z = self.smooth_data.get_impedances()
        self.bode_plot.plot(
            frequencies=freq,
            impedances=Z,
            labels=(
                "Mod(sim.)",
                "Phase(sim.)",
            ),
            line=True,
            themes=(
                themes.bode.magnitude_simulation,
                themes.bode.phase_simulation,
            ),
        )

        freq = self.sim_data.get_frequencies()
        Z = self.sim_data.get_impedances()
        self.bode_plot.plot(
            frequencies=freq,
            impedances=Z,
            labels=(
                "Mod(fit)",
                "Phase(fit)",
            ),
            line=False,
            show_labels=False,
            themes=(
                themes.bode.magnitude_simulation,
                themes.bode.phase_simulation,
            ),
        )
        if adjust_limits:
            self.bode_plot.adjust_limits()

    def update_bode_color(self, sender: int, _, theme: int):
        assert type(sender) is int
        assert type(theme) is int
        color: List[float] = dpg.get_value(sender)
        themes.update_plot_series_theme_color(theme, color)
        STATE.config.colors[
            {
                themes.bode.magnitude_data: "bode_magnitude_data",
                themes.bode.phase_data: "bode_phase_data",
                themes.bode.magnitude_simulation: "bode_magnitude_simulation",
                themes.bode.phase_simulation: "bode_phase_simulation",
            }[theme]
        ] = color

    def update_bode_marker(self, sender: int, label: str, theme: int):
        assert type(sender) is int
        assert type(label) is str
        assert type(theme) is int
        marker: int = PLOT_MARKERS[label]
        themes.update_plot_series_theme_marker(theme, marker)
        STATE.config.markers[
            {
                themes.bode.magnitude_data: "bode_magnitude_data",
                themes.bode.phase_data: "bode_phase_data",
                themes.bode.magnitude_simulation: "bode_magnitude_simulation",
                themes.bode.phase_simulation: "bode_phase_simulation",
            }[theme]
        ] = marker

    def reset_bode_plot(self):
        dpg.set_value(
            self.bode_data_mag_color,
            DEFAULT_COLORS["bode_magnitude_data"].copy(),
        )
        dpg.set_value(
            self.bode_data_phase_color,
            DEFAULT_COLORS["bode_phase_data"].copy(),
        )
        dpg.set_value(
            self.bode_sim_mag_color,
            DEFAULT_COLORS["bode_magnitude_simulation"].copy(),
        )
        dpg.set_value(
            self.bode_sim_phase_color,
            DEFAULT_COLORS["bode_phase_simulation"].copy(),
        )
        self.update_bode_color(
            self.bode_data_mag_color, None, themes.bode.magnitude_data
        )
        self.update_bode_color(self.bode_data_phase_color, None, themes.bode.phase_data)
        self.update_bode_color(
            self.bode_sim_mag_color, None, themes.bode.magnitude_simulation
        )
        self.update_bode_color(
            self.bode_sim_phase_color, None, themes.bode.phase_simulation
        )
        dpg.set_value(self.bode_data_mag_marker, "Circle")
        dpg.set_value(self.bode_data_phase_marker, "Square")
        dpg.set_value(self.bode_sim_mag_marker, "Cross")
        dpg.set_value(self.bode_sim_phase_marker, "Plus")
        self.update_bode_marker(
            self.bode_data_mag_marker,
            dpg.get_value(self.bode_data_mag_marker),
            themes.bode.magnitude_data,
        )
        self.update_bode_marker(
            self.bode_data_phase_marker,
            dpg.get_value(self.bode_data_phase_marker),
            themes.bode.phase_data,
        )
        self.update_bode_marker(
            self.bode_sim_mag_marker,
            dpg.get_value(self.bode_sim_mag_marker),
            themes.bode.magnitude_simulation,
        )
        self.update_bode_marker(
            self.bode_sim_phase_marker,
            dpg.get_value(self.bode_sim_phase_marker),
            themes.bode.phase_simulation,
        )

    def update_drt_plot(self, adjust_limits: bool = False):
        self.drt_plot.clear()
        tau: ndarray
        real_gamma: ndarray
        imaginary_gamma: ndarray
        tau, real_gamma, imaginary_gamma = self.drt.get_drt_data()
        self.drt_plot.plot(
            tau=tau,
            gamma=real_gamma,
            label="gamma/real",
            theme=themes.drt.real_gamma,
        )
        self.drt_plot.plot(
            tau=tau,
            gamma=imaginary_gamma,
            label="imag.",
            theme=themes.drt.imaginary_gamma,
        )
        lower: ndarray
        upper: ndarray
        tau, gamma, lower, upper = self.drt.get_drt_credible_intervals_data()
        self.drt_plot.plot(
            tau=tau,
            gamma=gamma,
            label="mean",
            theme=themes.drt.mean_gamma,
        )
        self.drt_plot.plot(
            tau=tau,
            lower=lower,
            upper=upper,
            label="3-sigma CI",
            theme=themes.drt.credible_intervals,
        )
        if adjust_limits:
            self.drt_plot.adjust_limits()

    def update_drt_color(self, sender: int, _, theme: int):
        assert type(sender) is int
        assert type(theme) is int
        color: List[float] = dpg.get_value(sender)
        themes.update_plot_series_theme_color(theme, color)
        STATE.config.colors[
            {
                themes.drt.real_gamma: "drt_real_gamma",
                themes.drt.imaginary_gamma: "drt_imaginary_gamma",
                themes.drt.mean_gamma: "drt_mean_gamma",
                themes.drt.credible_intervals: "drt_credible_intervals",
            }[theme]
        ] = color

    def reset_drt_plot(self):
        dpg.set_value(
            self.drt_real_gamma_color,
            DEFAULT_COLORS["drt_real_gamma"].copy(),
        )
        dpg.set_value(
            self.drt_imaginary_gamma_color,
            DEFAULT_COLORS["drt_imaginary_gamma"].copy(),
        )
        dpg.set_value(
            self.drt_mean_gamma_color,
            DEFAULT_COLORS["drt_mean_gamma"].copy(),
        )
        dpg.set_value(
            self.drt_credible_intervals_color,
            DEFAULT_COLORS["drt_credible_intervals"].copy(),
        )
        self.update_drt_color(
            self.drt_real_gamma_color,
            None,
            themes.drt.real_gamma,
        )
        self.update_drt_color(
            self.drt_imaginary_gamma_color,
            None,
            themes.drt.imaginary_gamma,
        )
        self.update_drt_color(
            self.drt_mean_gamma_color,
            None,
            themes.drt.mean_gamma,
        )
        self.update_drt_color(
            self.drt_credible_intervals_color,
            None,
            themes.drt.credible_intervals,
        )

    def update_impedance_plot(self, adjust_limits: bool = False):
        self.impedance_plot.clear()
        f: ndarray = self.data.get_frequencies()
        Z: ndarray = self.data.get_impedances()
        self.impedance_plot.plot(
            frequencies=f,
            impedances=Z,
            labels=(
                "Re(data)",
                "Im(data)",
            ),
            themes=(
                themes.impedance.real_data,
                themes.impedance.imaginary_data,
            ),
        )

        f = self.sim_data.get_frequencies()
        Z = self.sim_data.get_impedances()
        self.impedance_plot.plot(
            frequencies=f,
            impedances=Z,
            labels=(
                "Re(fit)",
                "Im(fit)",
            ),
            fit=True,
            line=False,
            themes=(
                themes.impedance.real_simulation,
                themes.impedance.imaginary_simulation,
            ),
        )

        f = self.smooth_data.get_frequencies()
        Z = self.smooth_data.get_impedances()
        self.impedance_plot.plot(
            frequencies=f,
            impedances=Z,
            labels=(
                "Re(sim)",
                "Im(sim)",
            ),
            fit=True,
            line=True,
            themes=(
                themes.impedance.real_simulation,
                themes.impedance.imaginary_simulation,
            ),
            show_labels=False,
        )
        if adjust_limits:
            self.impedance_plot.adjust_limits()

    def update_impedance_color(self, sender: int, _, theme: int):
        assert type(sender) is int
        assert type(theme) is int
        color: List[float] = dpg.get_value(sender)
        themes.update_plot_series_theme_color(theme, color)
        STATE.config.colors[
            {
                themes.impedance.real_data: "impedance_real_data",
                themes.impedance.real_simulation: "impedance_real_simulation",
                themes.impedance.imaginary_data: "impedance_imaginary_data",
                themes.impedance.imaginary_simulation: "impedance_imaginary_simulation",
            }[theme]
        ] = color

    def update_impedance_marker(self, sender: int, label: str, theme: int):
        assert type(sender) is int
        assert type(label) is str
        assert type(theme) is int
        marker: int = PLOT_MARKERS[label]
        themes.update_plot_series_theme_marker(theme, marker)
        STATE.config.markers[
            {
                themes.impedance.real_data: "impedance_real_data",
                themes.impedance.real_simulation: "impedance_real_simulation",
                themes.impedance.imaginary_data: "impedance_imaginary_data",
                themes.impedance.imaginary_simulation: "impedance_imaginary_simulation",
            }[theme]
        ] = marker

    def reset_impedance_plot(self):
        dpg.set_value(
            self.impedance_real_data_color,
            DEFAULT_COLORS["impedance_real_data"].copy(),
        )
        dpg.set_value(
            self.impedance_real_simulation_color,
            DEFAULT_COLORS["impedance_real_simulation"].copy(),
        )
        dpg.set_value(
            self.impedance_imaginary_data_color,
            DEFAULT_COLORS["impedance_imaginary_data"].copy(),
        )
        dpg.set_value(
            self.impedance_imaginary_simulation_color,
            DEFAULT_COLORS["impedance_imaginary_simulation"].copy(),
        )
        self.update_impedance_color(
            self.impedance_real_data_color,
            None,
            themes.impedance.real_data,
        )
        self.update_impedance_color(
            self.impedance_real_simulation_color,
            None,
            themes.impedance.real_simulation,
        )
        self.update_impedance_color(
            self.impedance_imaginary_data_color,
            None,
            themes.impedance.imaginary_data,
        )
        self.update_impedance_color(
            self.impedance_imaginary_simulation_color,
            None,
            themes.impedance.imaginary_simulation,
        )
        dpg.set_value(self.impedance_real_data_marker, "Circle")
        dpg.set_value(self.impedance_real_simulation_marker, "Cross")
        dpg.set_value(self.impedance_imaginary_data_marker, "Square")
        dpg.set_value(self.impedance_imaginary_simulation_marker, "Plus")
        self.update_impedance_marker(
            self.impedance_real_data_marker,
            dpg.get_value(self.impedance_real_data_marker),
            themes.impedance.real_data,
        )
        self.update_impedance_marker(
            self.impedance_real_simulation_marker,
            dpg.get_value(self.impedance_real_simulation_marker),
            themes.impedance.real_simulation,
        )
        self.update_impedance_marker(
            self.impedance_imaginary_data_marker,
            dpg.get_value(self.impedance_imaginary_data_marker),
            themes.impedance.imaginary_data,
        )
        self.update_impedance_marker(
            self.impedance_imaginary_simulation_marker,
            dpg.get_value(self.impedance_imaginary_simulation_marker),
            themes.impedance.imaginary_simulation,
        )

    def update_nyquist_plot(self, adjust_limits: bool = False):
        self.nyquist_plot.clear()
        Z: ndarray = self.data.get_impedances()
        self.nyquist_plot.plot(
            impedances=Z,
            label="Data",
            theme=themes.nyquist.data,
        )

        Z = self.smooth_data.get_impedances()
        self.nyquist_plot.plot(
            impedances=Z,
            label="Sim.",
            line=True,
            theme=themes.nyquist.simulation,
        )

        Z = self.sim_data.get_impedances()
        self.nyquist_plot.plot(
            impedances=Z,
            label="Fit",
            show_label=False,
            theme=themes.nyquist.simulation,
        )
        if adjust_limits:
            self.nyquist_plot.adjust_limits()

    def update_nyquist_color(self, sender: int, _, theme: int):
        assert type(sender) is int
        assert type(theme) is int
        color: List[float] = dpg.get_value(sender)
        themes.update_plot_series_theme_color(theme, color)
        STATE.config.colors[
            {
                themes.nyquist.data: "nyquist_data",
                themes.nyquist.simulation: "nyquist_simulation",
            }[theme]
        ] = color

    def update_nyquist_marker(self, sender: int, label: str, theme: int):
        assert type(sender) is int
        assert type(label) is str
        assert type(theme) is int
        marker: int = PLOT_MARKERS[label]
        themes.update_plot_series_theme_marker(theme, marker)
        STATE.config.markers[
            {
                themes.nyquist.data: "nyquist_data",
                themes.nyquist.simulation: "nyquist_simulation",
            }[theme]
        ] = marker

    def reset_nyquist_plot(self):
        dpg.set_value(
            self.nyquist_data_color,
            DEFAULT_COLORS["nyquist_data"].copy(),
        )
        dpg.set_value(
            self.nyquist_sim_color,
            DEFAULT_COLORS["nyquist_simulation"].copy(),
        )
        self.update_nyquist_color(
            self.nyquist_data_color,
            None,
            themes.nyquist.data,
        )
        self.update_nyquist_color(
            self.nyquist_sim_color,
            None,
            themes.nyquist.simulation,
        )
        dpg.set_value(self.nyquist_data_marker, "Circle")
        dpg.set_value(self.nyquist_sim_marker, "Cross")
        self.update_nyquist_marker(
            self.nyquist_data_marker,
            dpg.get_value(self.nyquist_data_marker),
            themes.nyquist.data,
        )
        self.update_nyquist_marker(
            self.nyquist_sim_marker,
            dpg.get_value(self.nyquist_sim_marker),
            themes.nyquist.simulation,
        )

    def update_residuals_plot(self, adjust_limits: bool = False):
        self.residuals_plot.clear()
        self.residuals_plot.plot(
            frequencies=self.data.get_frequencies(),
            real=self.residuals.real,
            imaginary=self.residuals.imag,
        )
        if adjust_limits:
            self.residuals_plot.adjust_limits()

    def update_residuals_color(self, sender: int, _, theme: int):
        assert type(sender) is int
        assert type(theme) is int
        color: List[float] = dpg.get_value(sender)
        themes.update_plot_series_theme_color(theme, color)
        STATE.config.colors[
            {
                themes.residuals.real: "residuals_real",
                themes.residuals.imaginary: "residuals_imaginary",
            }[theme]
        ] = color

    def update_residuals_marker(self, sender: int, label: str, theme: int):
        assert type(sender) is int
        assert type(label) is str
        assert type(theme) is int
        marker: int = PLOT_MARKERS[label]
        themes.update_plot_series_theme_marker(theme, marker)
        STATE.config.markers[
            {
                themes.residuals.real: "residuals_real",
                themes.residuals.imaginary: "residuals_imaginary",
            }[theme]
        ] = marker

    def reset_residuals_plot(self):
        dpg.set_value(
            self.residuals_real_color,
            DEFAULT_COLORS["residuals_real"].copy(),
        )
        dpg.set_value(
            self.residuals_imag_color,
            DEFAULT_COLORS["residuals_imaginary"].copy(),
        )
        self.update_residuals_color(
            self.residuals_real_color,
            None,
            themes.residuals.real,
        )
        self.update_residuals_color(
            self.residuals_imag_color,
            None,
            themes.residuals.imaginary,
        )
        dpg.set_value(self.residuals_real_marker, "Circle")
        dpg.set_value(self.residuals_imag_marker, "Square")
        self.update_residuals_marker(
            self.residuals_real_marker,
            dpg.get_value(self.residuals_real_marker),
            themes.residuals.real,
        )
        self.update_residuals_marker(
            self.residuals_imag_marker,
            dpg.get_value(self.residuals_imag_marker),
            themes.residuals.imaginary,
        )

    # TODO: Update
    def update_muxps_plot(self):
        self.muxps_plot.clear()
        self.muxps_plot.plot(
            num_RCs=array([1, 2, 3, 4, 5, 6]),
            mu=array([1.0, 0.8, 0.6, 0.4, 0.2, 0.0]),
            Xps=array([0, -1, -1.5, -1.8, -2, -1.4]),
            mu_criterion=0.7,
            num_RC=3,
        )
        self.muxps_plot.adjust_limits()

    def update_muxps_color(self, sender: int, _, theme: int):
        assert type(sender) is int
        assert type(theme) is int
        color: List[float] = dpg.get_value(sender)
        themes.update_plot_series_theme_color(theme, color)
        STATE.config.colors[
            {
                themes.mu_Xps.mu_criterion: "mu_Xps_mu_criterion",
                themes.mu_Xps.mu: "mu_Xps_mu",
                themes.mu_Xps.mu_highlight: "mu_Xps_mu_highlight",
                themes.mu_Xps.Xps: "mu_Xps_Xps",
                themes.mu_Xps.Xps_highlight: "mu_Xps_Xps_highlight",
            }[theme]
        ] = color

    def update_muxps_marker(self, sender: int, label: str, theme: int):
        assert type(sender) is int
        assert type(label) is str
        assert type(theme) is int
        marker: int = PLOT_MARKERS[label]
        themes.update_plot_series_theme_marker(theme, marker)
        STATE.config.markers[
            {
                themes.mu_Xps.mu: "mu_Xps_mu",
                themes.mu_Xps.Xps: "mu_Xps_Xps",
            }[theme]
        ] = marker
        theme = {
            themes.mu_Xps.mu: themes.mu_Xps.mu_highlight,
            themes.mu_Xps.Xps: themes.mu_Xps.Xps_highlight,
        }[theme]
        themes.update_plot_series_theme_marker(theme, marker)
        STATE.config.markers[
            {
                themes.mu_Xps.mu_highlight: "mu_Xps_mu_highlight",
                themes.mu_Xps.Xps_highlight: "mu_Xps_Xps_highlight",
            }[theme]
        ] = marker

    def reset_muxps_plot(self):
        dpg.set_value(
            self.muxps_mu_criterion_color,
            (
                255,
                255,
                255,
                128,
            ),
        )
        dpg.set_value(
            self.muxps_mu_color,
            (
                238,
                51,
                119,
                190,
            ),
        )
        dpg.set_value(
            self.muxps_mu_highlight_color,
            (
                51,
                187,
                238,
                190,
            ),
        )
        dpg.set_value(
            self.muxps_xps_color,
            (
                0,
                153,
                136,
                190,
            ),
        )
        dpg.set_value(
            self.muxps_xps_highlight_color,
            (
                238,
                119,
                51,
                190,
            ),
        )
        self.update_muxps_color(
            self.muxps_mu_criterion_color, None, themes.mu_Xps.mu_criterion
        )
        self.update_muxps_color(self.muxps_mu_color, None, themes.mu_Xps.mu)
        self.update_muxps_color(
            self.muxps_mu_highlight_color, None, themes.mu_Xps.mu_highlight
        )
        self.update_muxps_color(self.muxps_xps_color, None, themes.mu_Xps.Xps)
        self.update_muxps_color(
            self.muxps_xps_highlight_color,
            None,
            themes.mu_Xps.Xps_highlight,
        )
        dpg.set_value(self.muxps_mu_marker, "Circle")
        dpg.set_value(self.muxps_xps_marker, "Square")
        self.update_muxps_marker(
            self.muxps_mu_marker,
            dpg.get_value(self.muxps_mu_marker),
            themes.mu_Xps.mu,
        )
        self.update_muxps_marker(
            self.muxps_xps_marker,
            dpg.get_value(self.muxps_xps_marker),
            themes.mu_Xps.Xps,
        )
