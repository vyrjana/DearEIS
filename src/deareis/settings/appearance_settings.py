# Copyright 2022 DearEIS developers
# DearEIS is licensed under the GPLv3 or later (https://www.gnu.org/licenses/gpl-3.0.html).
# The licenses of DearEIS' dependencies and/or sources of portions of code are included in
# the LICENSES folder.

import dearpygui.dearpygui as dpg
import deareis.themes as themes
from deareis.themes import PLOT_MARKERS
from typing import Dict, List, Optional, Tuple
from deareis.utility import attach_tooltip, window_pos_dims
from deareis.config import CONFIG
from deareis.plot import (
    BodePlot,
    NyquistPlot,
    ResidualsPlot,
    MuXpsPlot,
)
from numpy import array, logspace, log10 as log, ndarray
from numpy.random import normal
from pyimpspec import DataSet, Circuit
import pyimpspec


noise: Optional[ndarray] = None
data: Optional[DataSet] = None
sim_data: Optional[DataSet] = None
smooth_data: Optional[DataSet] = None
real_residual: Optional[ndarray] = None
imag_residual: Optional[ndarray] = None


# TODO: Split up into smaller functions
def show_appearance_settings_window(self):
    x: int
    y: int
    w: int
    h: int
    x, y, w, h = window_pos_dims(600)

    window: int = dpg.generate_uuid()
    key_handler: int = dpg.generate_uuid()

    def close_window():
        if dpg.does_item_exist(window):
            dpg.delete_item(window)
        if dpg.does_item_exist(key_handler):
            dpg.delete_item(key_handler)

    with dpg.handler_registry(tag=key_handler):
        dpg.add_key_release_handler(
            key=dpg.mvKey_Escape,
            callback=close_window,
        )

    with dpg.window(
        label="Settings - appearance",
        modal=True,
        pos=(
            x,
            y,
        ),
        width=w,
        height=h,
        no_move=True,
        no_resize=True,
        on_close=close_window,
        tag=window,
    ):

        def generate_data(
            noise: Optional[ndarray],
        ) -> Tuple[DataSet, DataSet, DataSet, ndarray, ndarray]:
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
            sim_data: DataSet = pyimpspec.simulate_spectrum(
                circuit, data.get_frequency()
            )
            smooth_data: DataSet = pyimpspec.simulate_spectrum(
                circuit,
                logspace(0, 5, num=5 * CONFIG.num_per_decade_in_simulated_lines + 1),
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
            return (
                data,
                noise,
                sim_data,
                smooth_data,
                real_residual,
                imag_residual,
            )

        global data
        global noise
        global sim_data
        global smooth_data
        global real_residual
        global imag_residual
        if data is None:
            (
                data,
                noise,
                sim_data,
                smooth_data,
                real_residual,
                imag_residual,
            ) = generate_data(None)
        marker_items: List[str] = list(PLOT_MARKERS.keys())
        marker_label_lookup: Dict[int, str] = {v: k for k, v in PLOT_MARKERS.items()}
        bode_plot: BodePlot = None
        nyquist_plot: NyquistPlot = None
        muxps_plot: MuXpsPlot = None
        residuals_plot: ResidualsPlot = None
        label_pad: int = 56
        with dpg.collapsing_header(label="General", default_open=True):

            def update_simulated_num_per_decade(sender: int, value: int):
                CONFIG.num_per_decade_in_simulated_lines = value
                global data
                global noise
                global sim_data
                global smooth_data
                global real_residual
                global imag_residual
                (
                    data,
                    _,
                    sim_data,
                    smooth_data,
                    real_residual,
                    imag_residual,
                ) = generate_data(noise)
                update_bode_plot()
                update_nyquist_plot()
                update_residuals_plot()
                update_muxps_plot()

            with dpg.group(horizontal=True):
                dpg.add_text(
                    "Number of points per decade in simulated response".rjust(label_pad)
                )
                attach_tooltip(
                    "This affects how smooth the lines will look but it may also affect "
                    "performance when rendering the graphical user interface. Changes made "
                    "to this setting will take effect the next time a plot is redrawn."
                )
                dpg.add_slider_int(
                    default_value=CONFIG.num_per_decade_in_simulated_lines,
                    min_value=1,
                    max_value=200,
                    clamped=True,
                    callback=update_simulated_num_per_decade,
                    width=-1,
                )
            dpg.add_spacer(height=8)

        with dpg.collapsing_header(label="Bode plots", default_open=True):
            bode_plot = BodePlot(
                dpg.add_plot(
                    height=200,
                    width=-1,
                    anti_aliased=True,
                )
            )

            # bode_show_legend_checkbox: int = dpg.generate_uuid()
            # bode_legend_outside_checkbox: int = dpg.generate_uuid()
            # bode_horizontal_legend_checkbox: int = dpg.generate_uuid()
            # bode_legend_location_combo: int = dpg.generate_uuid()
            bode_data_mag_color: int = dpg.generate_uuid()
            bode_data_phase_color: int = dpg.generate_uuid()
            bode_sim_mag_color: int = dpg.generate_uuid()
            bode_sim_phase_color: int = dpg.generate_uuid()
            bode_data_mag_marker: int = dpg.generate_uuid()
            bode_data_phase_marker: int = dpg.generate_uuid()
            bode_sim_mag_marker: int = dpg.generate_uuid()
            bode_sim_phase_marker: int = dpg.generate_uuid()

            def update_bode_plot(adjust_limits: bool = False):
                bode_plot.clear_plot()
                before = bode_plot.plot_smooth(*smooth_data.get_bode_data(), False)
                before = bode_plot.plot_sim(*sim_data.get_bode_data(), False, before)
                bode_plot.plot_data(*data.get_bode_data(), before, True)
                if adjust_limits:
                    bode_plot.adjust_limits()

            def update_bode_color(sender: int, _, theme: int):
                assert type(sender) is int
                assert type(theme) is int
                color: List[float] = dpg.get_value(sender)
                themes.update_plot_theme_color(theme, color)
                CONFIG.colors[
                    {
                        themes.bode_magnitude_data: "bode_magnitude_data",
                        themes.bode_phase_data: "bode_phase_data",
                        themes.bode_magnitude_sim: "bode_magnitude_sim",
                        themes.bode_phase_sim: "bode_phase_sim",
                    }[theme]
                ] = color

            def update_bode_marker(sender: int, label: str, theme: int):
                assert type(sender) is int
                assert type(label) is str
                assert type(theme) is int
                marker: int = PLOT_MARKERS[label]
                themes.update_plot_theme_marker(theme, marker)
                CONFIG.markers[
                    {
                        themes.bode_magnitude_data: "bode_magnitude_data",
                        themes.bode_phase_data: "bode_phase_data",
                        themes.bode_magnitude_sim: "bode_magnitude_sim",
                        themes.bode_phase_sim: "bode_phase_sim",
                    }[theme]
                ] = marker

            def reset_bode_plot():
                dpg.set_value(
                    bode_data_mag_color,
                    (
                        51,
                        187,
                        238,
                        190,
                    ),
                )
                dpg.set_value(
                    bode_data_phase_color,
                    (
                        238,
                        119,
                        51,
                        190,
                    ),
                )
                dpg.set_value(
                    bode_sim_mag_color,
                    (
                        238,
                        51,
                        119,
                        190,
                    ),
                )
                dpg.set_value(
                    bode_sim_phase_color,
                    (
                        0,
                        153,
                        136,
                        190,
                    ),
                )
                update_bode_color(bode_data_mag_color, None, themes.bode_magnitude_data)
                update_bode_color(bode_data_phase_color, None, themes.bode_phase_data)
                update_bode_color(bode_sim_mag_color, None, themes.bode_magnitude_sim)
                update_bode_color(bode_sim_phase_color, None, themes.bode_phase_sim)
                dpg.set_value(bode_data_mag_marker, "Circle")
                dpg.set_value(bode_data_phase_marker, "Square")
                dpg.set_value(bode_sim_mag_marker, "Cross")
                dpg.set_value(bode_sim_phase_marker, "Plus")
                update_bode_marker(
                    bode_data_mag_marker,
                    dpg.get_value(bode_data_mag_marker),
                    themes.bode_magnitude_data,
                )
                update_bode_marker(
                    bode_data_phase_marker,
                    dpg.get_value(bode_data_phase_marker),
                    themes.bode_phase_data,
                )
                update_bode_marker(
                    bode_sim_mag_marker,
                    dpg.get_value(bode_sim_mag_marker),
                    themes.bode_magnitude_sim,
                )
                update_bode_marker(
                    bode_sim_phase_marker,
                    dpg.get_value(bode_sim_phase_marker),
                    themes.bode_phase_sim,
                )

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
                dpg.add_text("Data - magnitude".rjust(label_pad))
                dpg.add_color_edit(
                    default_value=CONFIG.colors["bode_magnitude_data"],
                    alpha_preview=dpg.mvColorEdit_AlphaPreviewHalf,
                    no_inputs=True,
                    alpha_bar=True,
                    callback=update_bode_color,
                    user_data=themes.bode_magnitude_data,
                    tag=bode_data_mag_color,
                )
                dpg.add_combo(
                    items=marker_items,
                    default_value=marker_label_lookup[
                        CONFIG.markers["bode_magnitude_data"]
                    ],
                    callback=update_bode_marker,
                    user_data=themes.bode_magnitude_data,
                    tag=bode_data_mag_marker,
                    width=-1,
                )
            with dpg.group(horizontal=True):
                dpg.add_text("Data - phase".rjust(label_pad))
                dpg.add_color_edit(
                    default_value=CONFIG.colors["bode_phase_data"],
                    alpha_preview=dpg.mvColorEdit_AlphaPreviewHalf,
                    no_inputs=True,
                    alpha_bar=True,
                    callback=update_bode_color,
                    user_data=themes.bode_phase_data,
                    tag=bode_data_phase_color,
                )
                dpg.add_combo(
                    items=marker_items,
                    default_value=marker_label_lookup[
                        CONFIG.markers["bode_phase_data"]
                    ],
                    callback=update_bode_marker,
                    user_data=themes.bode_phase_data,
                    tag=bode_data_phase_marker,
                    width=-1,
                )
            # Sim/fit colors and markers
            with dpg.group(horizontal=True):
                dpg.add_text("Fit/simulation - magnitude".rjust(label_pad))
                dpg.add_color_edit(
                    default_value=CONFIG.colors["bode_magnitude_sim"],
                    alpha_preview=dpg.mvColorEdit_AlphaPreviewHalf,
                    no_inputs=True,
                    alpha_bar=True,
                    callback=update_bode_color,
                    user_data=themes.bode_magnitude_sim,
                    tag=bode_sim_mag_color,
                )
                dpg.add_combo(
                    items=marker_items,
                    default_value=marker_label_lookup[
                        CONFIG.markers["bode_magnitude_sim"]
                    ],
                    callback=update_bode_marker,
                    user_data=themes.bode_magnitude_sim,
                    tag=bode_sim_mag_marker,
                    width=-1,
                )
            with dpg.group(horizontal=True):
                dpg.add_text("Fit/simulation - phase".rjust(label_pad))
                dpg.add_color_edit(
                    default_value=CONFIG.colors["bode_phase_sim"],
                    alpha_preview=dpg.mvColorEdit_AlphaPreviewHalf,
                    no_inputs=True,
                    alpha_bar=True,
                    callback=update_bode_color,
                    user_data=themes.bode_phase_sim,
                    tag=bode_sim_phase_color,
                )
                dpg.add_combo(
                    items=marker_items,
                    default_value=marker_label_lookup[CONFIG.markers["bode_phase_sim"]],
                    callback=update_bode_marker,
                    user_data=themes.bode_phase_sim,
                    tag=bode_sim_phase_marker,
                    width=-1,
                )
            with dpg.group(horizontal=True):
                dpg.add_text("".rjust(label_pad))
                dpg.add_button(
                    label="Restore defaults", callback=reset_bode_plot, width=-1
                )

            update_bode_plot(True)
            dpg.add_spacer(height=8)

        with dpg.collapsing_header(label="Nyquist plots", default_open=True):
            nyquist_plot = NyquistPlot(
                dpg.add_plot(
                    height=200,
                    width=-1,
                    equal_aspects=True,
                    anti_aliased=True,
                )
            )

            # nyquist_show_legend_checkbox: int = dpg.generate_uuid()
            # nyquist_legend_outside_checkbox: int = dpg.generate_uuid()
            # nyquist_horizontal_legend_checkbox: int = dpg.generate_uuid()
            # nyquist_legend_location_combo: int = dpg.generate_uuid()
            nyquist_data_color: int = dpg.generate_uuid()
            nyquist_sim_color: int = dpg.generate_uuid()
            nyquist_data_marker: int = dpg.generate_uuid()
            nyquist_sim_marker: int = dpg.generate_uuid()

            def update_nyquist_plot(adjust_limits: bool = False):
                nyquist_plot.clear_plot()
                before = nyquist_plot.plot_smooth(
                    *smooth_data.get_nyquist_data(), False
                )
                before = nyquist_plot.plot_sim(
                    *sim_data.get_nyquist_data(), False, before
                )
                nyquist_plot.plot_data(*data.get_nyquist_data(), before, True)
                if adjust_limits:
                    nyquist_plot.adjust_limits()

            def update_nyquist_color(sender: int, _, theme: int):
                assert type(sender) is int
                assert type(theme) is int
                color: List[float] = dpg.get_value(sender)
                themes.update_plot_theme_color(theme, color)
                CONFIG.colors[
                    {
                        themes.nyquist_data: "nyquist_data",
                        themes.nyquist_sim: "nyquist_sim",
                    }[theme]
                ] = color

            def update_nyquist_marker(sender: int, label: str, theme: int):
                assert type(sender) is int
                assert type(label) is str
                assert type(theme) is int
                marker: int = PLOT_MARKERS[label]
                themes.update_plot_theme_marker(theme, marker)
                CONFIG.markers[
                    {
                        themes.nyquist_data: "nyquist_data",
                        themes.nyquist_sim: "nyquist_sim",
                    }[theme]
                ] = marker

            def reset_nyquist_plot():
                dpg.set_value(
                    nyquist_data_color,
                    (
                        51,
                        187,
                        238,
                        190,
                    ),
                )
                dpg.set_value(
                    nyquist_sim_color,
                    (
                        238,
                        51,
                        119,
                        190,
                    ),
                )
                update_nyquist_color(nyquist_data_color, None, themes.nyquist_data)
                update_nyquist_color(nyquist_sim_color, None, themes.nyquist_sim)
                dpg.set_value(nyquist_data_marker, "Circle")
                dpg.set_value(nyquist_sim_marker, "Cross")
                update_nyquist_marker(
                    nyquist_data_marker,
                    dpg.get_value(nyquist_data_marker),
                    themes.nyquist_data,
                )
                update_nyquist_marker(
                    nyquist_sim_marker,
                    dpg.get_value(nyquist_sim_marker),
                    themes.nyquist_sim,
                )

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
                dpg.add_text("Data".rjust(label_pad))
                dpg.add_color_edit(
                    default_value=CONFIG.colors["nyquist_data"],
                    alpha_preview=dpg.mvColorEdit_AlphaPreviewHalf,
                    no_inputs=True,
                    alpha_bar=True,
                    callback=update_nyquist_color,
                    user_data=themes.nyquist_data,
                    tag=nyquist_data_color,
                )
                dpg.add_combo(
                    items=marker_items,
                    default_value=marker_label_lookup[CONFIG.markers["nyquist_data"]],
                    callback=update_nyquist_marker,
                    user_data=themes.nyquist_data,
                    tag=nyquist_data_marker,
                    width=-1,
                )
            # Sim/fit colors and markers
            with dpg.group(horizontal=True):
                dpg.add_text("Fit/simulation".rjust(label_pad))
                dpg.add_color_edit(
                    default_value=CONFIG.colors["nyquist_sim"],
                    alpha_preview=dpg.mvColorEdit_AlphaPreviewHalf,
                    no_inputs=True,
                    alpha_bar=True,
                    callback=update_nyquist_color,
                    user_data=themes.nyquist_sim,
                    tag=nyquist_sim_color,
                )
                dpg.add_combo(
                    items=marker_items,
                    default_value=marker_label_lookup[CONFIG.markers["nyquist_sim"]],
                    callback=update_nyquist_marker,
                    user_data=themes.nyquist_sim,
                    tag=nyquist_sim_marker,
                    width=-1,
                )
            with dpg.group(horizontal=True):
                dpg.add_text("".rjust(label_pad))
                dpg.add_button(
                    label="Restore defaults", callback=reset_nyquist_plot, width=-1
                )

            update_nyquist_plot(True)
            dpg.add_spacer(height=8)

        with dpg.collapsing_header(label="Residuals plots", default_open=True):
            residuals_plot = ResidualsPlot(
                dpg.add_plot(
                    height=200,
                    width=-1,
                    anti_aliased=True,
                )
            )

            # residuals_show_legend_checkbox: int = dpg.generate_uuid()
            # residuals_legend_outside_checkbox: int = dpg.generate_uuid()
            # residuals_horizontal_legend_checkbox: int = dpg.generate_uuid()
            # residuals_legend_location_combo: int = dpg.generate_uuid()
            residuals_real_color: int = dpg.generate_uuid()
            residuals_imag_color: int = dpg.generate_uuid()
            residuals_real_marker: int = dpg.generate_uuid()
            residuals_imag_marker: int = dpg.generate_uuid()

            def update_residuals_plot(adjust_limits: bool = False):
                residuals_plot.clear_plot()
                residuals_plot.plot_data(
                    log(data.get_frequency()), real_residual, imag_residual
                )
                if adjust_limits:
                    residuals_plot.adjust_limits()

            def update_residuals_color(sender: int, _, theme: int):
                assert type(sender) is int
                assert type(theme) is int
                color: List[float] = dpg.get_value(sender)
                themes.update_plot_theme_color(theme, color)
                CONFIG.colors[
                    {
                        themes.real_error: "real_error",
                        themes.imag_error: "imag_error",
                    }[theme]
                ] = color

            def update_residuals_marker(sender: int, label: str, theme: int):
                assert type(sender) is int
                assert type(label) is str
                assert type(theme) is int
                marker: int = PLOT_MARKERS[label]
                themes.update_plot_theme_marker(theme, marker)
                CONFIG.markers[
                    {
                        themes.real_error: "real_error",
                        themes.imag_error: "imag_error",
                    }[theme]
                ] = marker

            def reset_residuals_plot():
                dpg.set_value(
                    residuals_real_color,
                    (
                        238,
                        51,
                        119,
                        190,
                    ),
                )
                dpg.set_value(
                    residuals_imag_color,
                    (
                        0,
                        153,
                        136,
                        190,
                    ),
                )
                update_residuals_color(residuals_real_color, None, themes.real_error)
                update_residuals_color(residuals_imag_color, None, themes.imag_error)
                dpg.set_value(residuals_real_marker, "Circle")
                dpg.set_value(residuals_imag_marker, "Square")
                update_residuals_marker(
                    residuals_real_marker,
                    dpg.get_value(residuals_real_marker),
                    themes.real_error,
                )
                update_residuals_marker(
                    residuals_imag_marker,
                    dpg.get_value(residuals_imag_marker),
                    themes.imag_error,
                )

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
                dpg.add_text("Z' error".rjust(label_pad))
                dpg.add_color_edit(
                    default_value=CONFIG.colors["real_error"],
                    alpha_preview=dpg.mvColorEdit_AlphaPreviewHalf,
                    no_inputs=True,
                    alpha_bar=True,
                    callback=update_residuals_color,
                    user_data=themes.real_error,
                    tag=residuals_real_color,
                )
                dpg.add_combo(
                    items=marker_items,
                    default_value=marker_label_lookup[CONFIG.markers["real_error"]],
                    callback=update_residuals_marker,
                    user_data=themes.real_error,
                    tag=residuals_real_marker,
                    width=-1,
                )
            # Zim color and marker
            with dpg.group(horizontal=True):
                dpg.add_text('Z" error'.rjust(label_pad))
                dpg.add_color_edit(
                    default_value=CONFIG.colors["imag_error"],
                    alpha_preview=dpg.mvColorEdit_AlphaPreviewHalf,
                    no_inputs=True,
                    alpha_bar=True,
                    callback=update_residuals_color,
                    user_data=themes.imag_error,
                    tag=residuals_imag_color,
                )
                dpg.add_combo(
                    items=marker_items,
                    default_value=marker_label_lookup[CONFIG.markers["imag_error"]],
                    callback=update_residuals_marker,
                    user_data=themes.imag_error,
                    tag=residuals_imag_marker,
                    width=-1,
                )
            with dpg.group(horizontal=True):
                dpg.add_text("".rjust(label_pad))
                dpg.add_button(
                    label="Restore defaults", callback=reset_residuals_plot, width=-1
                )

            update_residuals_plot(True)
            dpg.add_spacer(height=8)

        with dpg.collapsing_header(label="µ-X² (pseudo) plots", default_open=True):
            muxps_plot = MuXpsPlot(
                dpg.add_plot(
                    height=200,
                    width=-1,
                    anti_aliased=True,
                )
            )

            # muxps_show_legend_checkbox: int = dpg.generate_uuid()
            # muxps_legend_outside_checkbox: int = dpg.generate_uuid()
            # muxps_horizontal_legend_checkbox: int = dpg.generate_uuid()
            # muxps_legend_location_combo: int = dpg.generate_uuid()
            muxps_mu_criterion_color: int = dpg.generate_uuid()
            muxps_mu_color: int = dpg.generate_uuid()
            muxps_mu_highlight_color: int = dpg.generate_uuid()
            muxps_xps_color: int = dpg.generate_uuid()
            muxps_xps_highlight_color: int = dpg.generate_uuid()
            muxps_mu_marker: int = dpg.generate_uuid()
            muxps_xps_marker: int = dpg.generate_uuid()

            def update_muxps_plot():
                muxps_plot.clear_plot()
                muxps_plot.plot_data(
                    array([1, 2, 3, 4, 5, 6]),
                    array([1.0, 0.8, 0.6, 0.4, 0.2, 0.0]),
                    array([0, -1, -1.5, -1.8, -2, -1.4]),
                    0.7,
                    3,
                )

            def update_muxps_color(sender: int, _, theme: int):
                assert type(sender) is int
                assert type(theme) is int
                color: List[float] = dpg.get_value(sender)
                themes.update_plot_theme_color(theme, color)
                CONFIG.colors[
                    {
                        themes.exploratory_mu_criterion: "exploratory_mu_criterion",
                        themes.exploratory_mu: "exploratory_mu",
                        themes.exploratory_mu_highlight: "exploratory_mu_highlight",
                        themes.exploratory_xps: "exploratory_xps",
                        themes.exploratory_xps_highlight: "exploratory_xps_highlight",
                    }[theme]
                ] = color

            def update_muxps_marker(sender: int, label: str, theme: int):
                assert type(sender) is int
                assert type(label) is str
                assert type(theme) is int
                marker: int = PLOT_MARKERS[label]
                themes.update_plot_theme_marker(theme, marker)
                CONFIG.markers[
                    {
                        themes.exploratory_mu: "exploratory_mu",
                        themes.exploratory_xps: "exploratory_xps",
                    }[theme]
                ] = marker
                theme = {
                    themes.exploratory_mu: themes.exploratory_mu_highlight,
                    themes.exploratory_xps: themes.exploratory_xps_highlight,
                }[theme]
                themes.update_plot_theme_marker(theme, marker)
                CONFIG.markers[
                    {
                        themes.exploratory_mu_highlight: "exploratory_mu_highlight",
                        themes.exploratory_xps_highlight: "exploratory_xps_highlight",
                    }[theme]
                ] = marker

            def reset_muxps_plot():
                dpg.set_value(
                    muxps_mu_criterion_color,
                    (
                        255,
                        255,
                        255,
                        128,
                    ),
                )
                dpg.set_value(
                    muxps_mu_color,
                    (
                        238,
                        51,
                        119,
                        190,
                    ),
                )
                dpg.set_value(
                    muxps_mu_highlight_color,
                    (
                        51,
                        187,
                        238,
                        190,
                    ),
                )
                dpg.set_value(
                    muxps_xps_color,
                    (
                        0,
                        153,
                        136,
                        190,
                    ),
                )
                dpg.set_value(
                    muxps_xps_highlight_color,
                    (
                        238,
                        119,
                        51,
                        190,
                    ),
                )
                update_muxps_color(
                    muxps_mu_criterion_color, None, themes.exploratory_mu_criterion
                )
                update_muxps_color(muxps_mu_color, None, themes.exploratory_mu)
                update_muxps_color(
                    muxps_mu_highlight_color, None, themes.exploratory_mu_highlight
                )
                update_muxps_color(muxps_xps_color, None, themes.exploratory_xps)
                update_muxps_color(
                    muxps_xps_highlight_color,
                    None,
                    themes.exploratory_xps_highlight,
                )
                dpg.set_value(muxps_mu_marker, "Circle")
                dpg.set_value(muxps_xps_marker, "Square")
                update_muxps_marker(
                    muxps_mu_marker,
                    dpg.get_value(muxps_mu_marker),
                    themes.exploratory_mu,
                )
                update_muxps_marker(
                    muxps_xps_marker,
                    dpg.get_value(muxps_xps_marker),
                    themes.exploratory_xps,
                )

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
                dpg.add_text("µ-criterion".rjust(label_pad))
                dpg.add_color_edit(
                    default_value=CONFIG.colors["exploratory_mu_criterion"],
                    alpha_preview=dpg.mvColorEdit_AlphaPreviewHalf,
                    no_inputs=True,
                    alpha_bar=True,
                    callback=update_muxps_color,
                    user_data=themes.exploratory_mu_criterion,
                    tag=muxps_mu_criterion_color,
                )
            # Mu color and marker
            with dpg.group(horizontal=True):
                dpg.add_text("µ".rjust(label_pad))
                dpg.add_color_edit(
                    default_value=CONFIG.colors["exploratory_mu"],
                    alpha_preview=dpg.mvColorEdit_AlphaPreviewHalf,
                    no_inputs=True,
                    alpha_bar=True,
                    callback=update_muxps_color,
                    user_data=themes.exploratory_mu,
                    tag=muxps_mu_color,
                )
                dpg.add_color_edit(
                    default_value=CONFIG.colors["exploratory_mu_highlight"],
                    alpha_preview=dpg.mvColorEdit_AlphaPreviewHalf,
                    no_inputs=True,
                    alpha_bar=True,
                    callback=update_muxps_color,
                    user_data=themes.exploratory_mu_highlight,
                    tag=muxps_mu_highlight_color,
                )
                dpg.add_combo(
                    items=marker_items,
                    default_value=marker_label_lookup[CONFIG.markers["exploratory_mu"]],
                    callback=update_muxps_marker,
                    user_data=themes.exploratory_mu,
                    tag=muxps_mu_marker,
                    width=-1,
                )
            # Xps color and marker
            with dpg.group(horizontal=True):
                dpg.add_text("X² (pseudo)".rjust(label_pad))
                dpg.add_color_edit(
                    default_value=CONFIG.colors["exploratory_xps"],
                    alpha_preview=dpg.mvColorEdit_AlphaPreviewHalf,
                    no_inputs=True,
                    alpha_bar=True,
                    callback=update_muxps_color,
                    user_data=themes.exploratory_xps,
                    tag=muxps_xps_color,
                )
                dpg.add_color_edit(
                    default_value=CONFIG.colors["exploratory_xps_highlight"],
                    alpha_preview=dpg.mvColorEdit_AlphaPreviewHalf,
                    no_inputs=True,
                    alpha_bar=True,
                    callback=update_muxps_color,
                    user_data=themes.exploratory_xps_highlight,
                    tag=muxps_xps_highlight_color,
                )
                dpg.add_combo(
                    items=marker_items,
                    default_value=marker_label_lookup[
                        CONFIG.markers["exploratory_xps"]
                    ],
                    callback=update_muxps_marker,
                    user_data=themes.exploratory_xps,
                    tag=muxps_xps_marker,
                    width=-1,
                )
            with dpg.group(horizontal=True):
                dpg.add_text("".rjust(label_pad))
                dpg.add_button(
                    label="Restore defaults", callback=reset_muxps_plot, width=-1
                )

            update_muxps_plot()
