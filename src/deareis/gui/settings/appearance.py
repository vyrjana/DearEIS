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

import dearpygui.dearpygui as dpg
import deareis.themes as themes
from deareis.themes import PLOT_MARKERS
from typing import Dict, List, Optional, Tuple
from deareis.utility import calculate_window_position_dimensions
from deareis.tooltips import attach_tooltip
from deareis.state import STATE
from deareis.gui.plots import (
    Bode,
    Nyquist,
    Residuals,
    MuXps,
)
from numpy import array, logspace, log10 as log, ndarray
from numpy.random import normal
from pyimpspec import Circuit
from deareis.data import DataSet
import pyimpspec
from deareis.signals import Signal
import deareis.signals as signals


class AppearanceSettings:
    def __init__(self):
        self.marker_items: List[str] = list(PLOT_MARKERS.keys())
        self.marker_label_lookup: Dict[int, str] = {
            v: k for k, v in PLOT_MARKERS.items()
        }
        self.label_pad: int = 56
        self.data: DataSet
        self.sim_data: DataSet
        self.smooth_data: DataSet
        self.real_residual: ndarray
        self.imag_residual: ndarray
        self.noise: ndarray
        (
            self.data,
            self.sim_data,
            self.smooth_data,
            self.real_residual,
            self.imag_residual,
            self.noise,
        ) = self.generate_data()
        x: int
        y: int
        w: int
        h: int
        x, y, w, h = calculate_window_position_dimensions(600, 540)
        self.window: int = dpg.generate_uuid()
        with dpg.window(
            label="Settings - appearance",
            modal=True,
            pos=(
                x,
                y,
            ),
            width=w,
            height=h,
            no_move=False,
            no_resize=True,
            on_close=self.close_window,
            tag=self.window,
        ):
            with dpg.collapsing_header(label="General", default_open=True):
                with dpg.group(horizontal=True):
                    dpg.add_text(
                        "Number of points per decade in simulated response".rjust(
                            self.label_pad
                        )
                    )
                    attach_tooltip(
                        """
This affects how smooth the lines will look but it may also affect performance when rendering the graphical user interface. This setting also affects how many points are included when copying plot data as character-separated values (CSV). Changes made to this setting will take effect the next time a plot is redrawn.
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
            with dpg.collapsing_header(label="Bode plots", default_open=True):
                self.bode_plot = Bode(width=-1, height=200)
                # bode_show_legend_checkbox: int = dpg.generate_uuid()
                # bode_legend_outside_checkbox: int = dpg.generate_uuid()
                # bode_horizontal_legend_checkbox: int = dpg.generate_uuid()
                # bode_legend_location_combo: int = dpg.generate_uuid()
                self.bode_data_mag_color: int = dpg.generate_uuid()
                self.bode_data_phase_color: int = dpg.generate_uuid()
                self.bode_sim_mag_color: int = dpg.generate_uuid()
                self.bode_sim_phase_color: int = dpg.generate_uuid()
                self.bode_data_mag_marker: int = dpg.generate_uuid()
                self.bode_data_phase_marker: int = dpg.generate_uuid()
                self.bode_sim_mag_marker: int = dpg.generate_uuid()
                self.bode_sim_phase_marker: int = dpg.generate_uuid()
                # Legend checkbox
                # with dpg.group(horizontal=True):
                #    dpg.add_text("Show legend".rjust(label_pad))
                #    dpg.add_checkbox(callback=update_bode_plot)
                # Legend outside
                # with dpg.group(horizontal=True):
                #    dpg.add_text("Legend outside plot".rjust(label_pad))
                #    dpg.add_checkbox(callback=update_bode_plot)
                # Legend horizontal checkbox
                # with dpg.group(horizontal=True):
                #    dpg.add_text("Horizontal legend".rjust(label_pad))
                #    dpg.add_checkbox(callback=update_bode_plot)
                # Legend location combo
                # with dpg.group(horizontal=True):
                #    dpg.add_text("Legend location".rjust(label_pad))
                #    dpg.add_combo(width=-1, callback=update_bode_plot)
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
            with dpg.collapsing_header(label="Nyquist plots", default_open=True):
                self.nyquist_plot = Nyquist(width=-1, height=200)
                # nyquist_show_legend_checkbox: int = dpg.generate_uuid()
                # nyquist_legend_outside_checkbox: int = dpg.generate_uuid()
                # nyquist_horizontal_legend_checkbox: int = dpg.generate_uuid()
                # nyquist_legend_location_combo: int = dpg.generate_uuid()
                self.nyquist_data_color: int = dpg.generate_uuid()
                self.nyquist_sim_color: int = dpg.generate_uuid()
                self.nyquist_data_marker: int = dpg.generate_uuid()
                self.nyquist_sim_marker: int = dpg.generate_uuid()
                # Legend checkbox
                # with dpg.group(horizontal=True):
                #    dpg.add_text("Show legend".rjust(label_pad))
                #    dpg.add_checkbox(callback=update_nyquist_plot)
                # Legend outside
                # with dpg.group(horizontal=True):
                #    dpg.add_text("Legend outside plot".rjust(label_pad))
                #    dpg.add_checkbox(callback=update_nyquist_plot)
                # Legend horizontal checkbox
                # with dpg.group(horizontal=True):
                #    dpg.add_text("Horizontal legend".rjust(label_pad))
                #    dpg.add_checkbox(callback=update_nyquist_plot)
                # Legend location combo
                # with dpg.group(horizontal=True):
                #    dpg.add_text("Legend location".rjust(label_pad))
                #    dpg.add_combo(width=-1, callback=update_nyquist_plot)
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
            with dpg.collapsing_header(label="Residuals plots", default_open=True):
                self.residuals_plot = Residuals(width=-1, height=200)
                # residuals_show_legend_checkbox: int = dpg.generate_uuid()
                # residuals_legend_outside_checkbox: int = dpg.generate_uuid()
                # residuals_horizontal_legend_checkbox: int = dpg.generate_uuid()
                # residuals_legend_location_combo: int = dpg.generate_uuid()
                self.residuals_real_color: int = dpg.generate_uuid()
                self.residuals_imag_color: int = dpg.generate_uuid()
                self.residuals_real_marker: int = dpg.generate_uuid()
                self.residuals_imag_marker: int = dpg.generate_uuid()
                # Legend checkbox
                # with dpg.group(horizontal=True):
                #    dpg.add_text("Show legend".rjust(label_pad))
                #    dpg.add_checkbox(callback=update_residuals_plot)
                # Legend outside
                # with dpg.group(horizontal=True):
                #    dpg.add_text("Legend outside plot".rjust(label_pad))
                #    dpg.add_checkbox(callback=update_residuals_plot)
                # Legend horizontal checkbox
                # with dpg.group(horizontal=True):
                #    dpg.add_text("Horizontal legend".rjust(label_pad))
                #    dpg.add_checkbox(callback=update_residuals_plot)
                # Legend location combo
                # with dpg.group(horizontal=True):
                #    dpg.add_text("Legend location".rjust(label_pad))
                #    dpg.add_combo(width=-1, callback=update_residuals_plot)
                # Zre color and marker
                with dpg.group(horizontal=True):
                    dpg.add_text("Z' error".rjust(self.label_pad))
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
                # Zim color and marker
                with dpg.group(horizontal=True):
                    dpg.add_text('Z" error'.rjust(self.label_pad))
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
            with dpg.collapsing_header(label="??-X?? (pseudo) plots", default_open=True):
                self.muxps_plot = MuXps(width=-1, height=200)
                # muxps_show_legend_checkbox: int = dpg.generate_uuid()
                # muxps_legend_outside_checkbox: int = dpg.generate_uuid()
                # muxps_horizontal_legend_checkbox: int = dpg.generate_uuid()
                # muxps_legend_location_combo: int = dpg.generate_uuid()
                self.muxps_mu_criterion_color: int = dpg.generate_uuid()
                self.muxps_mu_color: int = dpg.generate_uuid()
                self.muxps_mu_highlight_color: int = dpg.generate_uuid()
                self.muxps_xps_color: int = dpg.generate_uuid()
                self.muxps_xps_highlight_color: int = dpg.generate_uuid()
                self.muxps_mu_marker: int = dpg.generate_uuid()
                self.muxps_xps_marker: int = dpg.generate_uuid()
                # Legend checkbox
                # with dpg.group(horizontal=True):
                #    dpg.add_text("Show legend".rjust(label_pad))
                #    dpg.add_checkbox(callback=update_muxps_plot)
                # Legend outside
                # with dpg.group(horizontal=True):
                #    dpg.add_text("Legend outside plot".rjust(label_pad))
                #    dpg.add_checkbox(callback=update_muxps_plot)
                # Legend horizontal checkbox
                # with dpg.group(horizontal=True):
                #    dpg.add_text("Horizontal legend".rjust(label_pad))
                #    dpg.add_checkbox(callback=update_muxps_plot)
                # Legend location combo
                # with dpg.group(horizontal=True):
                #    dpg.add_text("Legend location".rjust(label_pad))
                #    dpg.add_combo(width=-1, callback=update_muxps_plot)
                # Mu-criterion color
                with dpg.group(horizontal=True):
                    dpg.add_text("??-criterion".rjust(self.label_pad))
                    dpg.add_color_edit(
                        default_value=STATE.config.colors["mu_Xps_mu_criterion"],
                        alpha_preview=dpg.mvColorEdit_AlphaPreviewHalf,
                        no_inputs=True,
                        alpha_bar=True,
                        callback=self.update_muxps_color,
                        user_data=themes.mu_Xps.mu_criterion,
                        tag=self.muxps_mu_criterion_color,
                    )
                # Mu color and marker
                with dpg.group(horizontal=True):
                    dpg.add_text("??".rjust(self.label_pad))
                    dpg.add_color_edit(
                        default_value=STATE.config.colors["mu_Xps_mu"],
                        alpha_preview=dpg.mvColorEdit_AlphaPreviewHalf,
                        no_inputs=True,
                        alpha_bar=True,
                        callback=self.update_muxps_color,
                        user_data=themes.mu_Xps.mu,
                        tag=self.muxps_mu_color,
                    )
                    dpg.add_color_edit(
                        default_value=STATE.config.colors["mu_Xps_mu_highlight"],
                        alpha_preview=dpg.mvColorEdit_AlphaPreviewHalf,
                        no_inputs=True,
                        alpha_bar=True,
                        callback=self.update_muxps_color,
                        user_data=themes.mu_Xps.mu_highlight,
                        tag=self.muxps_mu_highlight_color,
                    )
                    dpg.add_combo(
                        items=self.marker_items,
                        default_value=self.marker_label_lookup[
                            STATE.config.markers["mu_Xps_mu"]
                        ],
                        callback=self.update_muxps_marker,
                        user_data=themes.mu_Xps.mu,
                        tag=self.muxps_mu_marker,
                        width=-1,
                    )
                # Xps color and marker
                with dpg.group(horizontal=True):
                    dpg.add_text("X?? (pseudo)".rjust(self.label_pad))
                    dpg.add_color_edit(
                        default_value=STATE.config.colors["mu_Xps_Xps"],
                        alpha_preview=dpg.mvColorEdit_AlphaPreviewHalf,
                        no_inputs=True,
                        alpha_bar=True,
                        callback=self.update_muxps_color,
                        user_data=themes.mu_Xps.Xps,
                        tag=self.muxps_xps_color,
                    )
                    dpg.add_color_edit(
                        default_value=STATE.config.colors["mu_Xps_Xps_highlight"],
                        alpha_preview=dpg.mvColorEdit_AlphaPreviewHalf,
                        no_inputs=True,
                        alpha_bar=True,
                        callback=self.update_muxps_color,
                        user_data=themes.mu_Xps.Xps_highlight,
                        tag=self.muxps_xps_highlight_color,
                    )
                    dpg.add_combo(
                        items=self.marker_items,
                        default_value=self.marker_label_lookup[
                            STATE.config.markers["mu_Xps_Xps"]
                        ],
                        callback=self.update_muxps_marker,
                        user_data=themes.mu_Xps.Xps,
                        tag=self.muxps_xps_marker,
                        width=-1,
                    )
                with dpg.group(horizontal=True):
                    dpg.add_text("".rjust(self.label_pad))
                    dpg.add_button(
                        label="Restore defaults",
                        callback=self.reset_muxps_plot,
                        width=-1,
                    )
                self.update_muxps_plot()
        self.key_handler: int = dpg.generate_uuid()
        with dpg.handler_registry(tag=self.key_handler):
            dpg.add_key_release_handler(
                key=dpg.mvKey_Escape,
                callback=self.close_window,
            )
        signals.emit(Signal.BLOCK_KEYBINDINGS, window=self.window)

    def close_window(self):
        if dpg.does_item_exist(self.window):
            dpg.delete_item(self.window)
        if dpg.does_item_exist(self.key_handler):
            dpg.delete_item(self.key_handler)
        signals.emit(Signal.UNBLOCK_KEYBINDINGS)

    def generate_data(
        self,
        noise: Optional[ndarray] = None,
    ) -> Tuple[DataSet, DataSet, DataSet, ndarray, ndarray, ndarray]:
        circuit: Circuit = pyimpspec.string_to_circuit(
            "R{R=100}(C{C=1e-6}[R{R=500}W{Y=4e-4}])"
        )
        data: DataSet = pyimpspec.simulate_spectrum(circuit, logspace(0, 5, num=20))
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
                        data.get_impedance(),
                    )
                )
            )
        data.subtract_impedance(-noise)
        sim_data: DataSet = pyimpspec.simulate_spectrum(circuit, data.get_frequency())
        smooth_data: DataSet = pyimpspec.simulate_spectrum(
            circuit,
            logspace(0, 5, num=5 * STATE.config.num_per_decade_in_simulated_lines + 1),
        )
        real_residual: ndarray = (
            (data.get_impedance().real - sim_data.get_impedance().real)
            / abs(data.get_impedance())
            * 100
        )
        imag_residual: ndarray = (
            (data.get_impedance().imag - sim_data.get_impedance().imag)
            / abs(data.get_impedance())
            * 100
        )
        return (data, sim_data, smooth_data, real_residual, imag_residual, noise)

    def update_simulated_num_per_decade(self, sender: int, value: int):
        STATE.config.num_per_decade_in_simulated_lines = value
        (
            self.data,
            self.sim_data,
            self.smooth_data,
            self.real_residual,
            self.imag_residual,
            _,
        ) = self.generate_data(self.noise)
        self.update_bode_plot()
        self.update_nyquist_plot()
        self.update_residuals_plot()
        self.update_muxps_plot()

    def update_bode_plot(self, adjust_limits: bool = False):
        self.bode_plot.clear()
        freq, mag, phase = self.data.get_bode_data()
        self.bode_plot.plot(
            frequency=freq,
            magnitude=mag,
            phase=phase,
            labels=(
                "|Z| (d)",
                "phi (d)",
            ),
            themes=(
                themes.bode.magnitude_data,
                themes.bode.phase_data,
            ),
        )
        freq, mag, phase = self.smooth_data.get_bode_data()
        self.bode_plot.plot(
            frequency=freq,
            magnitude=mag,
            phase=phase,
            labels=(
                "|Z| (fit/sim.)",
                "phi (fit/sim.)",
            ),
            line=True,
            themes=(
                themes.bode.magnitude_simulation,
                themes.bode.phase_simulation,
            ),
        )
        freq, mag, phase = self.sim_data.get_bode_data()
        self.bode_plot.plot(
            frequency=freq,
            magnitude=mag,
            phase=phase,
            labels=(
                "|Z| (fit/sim.)",
                "phi (fit/sim.)",
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
            (
                51,
                187,
                238,
                190,
            ),
        )
        dpg.set_value(
            self.bode_data_phase_color,
            (
                238,
                119,
                51,
                190,
            ),
        )
        dpg.set_value(
            self.bode_sim_mag_color,
            (
                238,
                51,
                119,
                190,
            ),
        )
        dpg.set_value(
            self.bode_sim_phase_color,
            (
                0,
                153,
                136,
                190,
            ),
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

    def update_nyquist_plot(self, adjust_limits: bool = False):
        self.nyquist_plot.clear()
        real, imag = self.data.get_nyquist_data()
        self.nyquist_plot.plot(
            real=real,
            imaginary=imag,
            label="Data",
            theme=themes.nyquist.data,
        )
        real, imag = self.smooth_data.get_nyquist_data()
        self.nyquist_plot.plot(
            real=real,
            imaginary=imag,
            label="Fit/sim.",
            line=True,
            theme=themes.nyquist.simulation,
        )
        real, imag = self.sim_data.get_nyquist_data()
        self.nyquist_plot.plot(
            real=real,
            imaginary=imag,
            label="Fit/sim.",
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
            (
                51,
                187,
                238,
                190,
            ),
        )
        dpg.set_value(
            self.nyquist_sim_color,
            (
                238,
                51,
                119,
                190,
            ),
        )
        self.update_nyquist_color(self.nyquist_data_color, None, themes.nyquist.data)
        self.update_nyquist_color(
            self.nyquist_sim_color, None, themes.nyquist.simulation
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
            frequency=log(self.data.get_frequency()),
            real=self.real_residual,
            imaginary=self.imag_residual,
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
            (
                238,
                51,
                119,
                190,
            ),
        )
        dpg.set_value(
            self.residuals_imag_color,
            (
                0,
                153,
                136,
                190,
            ),
        )
        self.update_residuals_color(
            self.residuals_real_color, None, themes.residuals.real
        )
        self.update_residuals_color(
            self.residuals_imag_color, None, themes.residuals.imaginary
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
