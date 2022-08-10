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
from deareis.utility import calculate_window_position_dimensions
from deareis.tooltips import attach_tooltip
import deareis.tooltips as tooltips
from deareis.enums import (
    Method,
    Mode,
    Test,
    Weight,
    label_to_method,
    label_to_mode,
    label_to_test,
    label_to_weight,
    method_to_label,
    mode_to_label,
    test_to_label,
    weight_to_label,
)
from deareis.data import (
    FitSettings,
    SimulationSettings,
    TestSettings,
)
from deareis.config import (
    DEFAULT_TEST_SETTINGS,
    DEFAULT_FIT_SETTINGS,
    DEFAULT_SIMULATION_SETTINGS,
)
from deareis.gui.plotting.export import (
    EXTENSIONS,
    LEGEND_LOCATIONS,
    PREVIEW_LIMITS,
    UNITS_PER_INCH,
)
from deareis.signals import Signal
import deareis.signals as signals


def section_spacer():
    dpg.add_spacer(height=8)


def general_settings(label_pad: int, state):
    with dpg.collapsing_header(label="General", default_open=True):
        auto_backup_interval: int = dpg.generate_uuid()

        def update_auto_backup_interval(value: int):
            state.config.auto_backup_interval = value

        with dpg.group(horizontal=True):
            dpg.add_text("Auto-backup interval".rjust(label_pad))
            attach_tooltip(tooltips.general.auto_backup_interval)
            dpg.add_input_int(
                default_value=state.config.auto_backup_interval,
                label="actions",
                min_value=0,
                min_clamped=True,
                step=0,
                on_enter=True,
                callback=lambda s, a, u: update_auto_backup_interval(a),
                width=-54,
                tag=auto_backup_interval,
            )
        section_spacer()


def kramers_kronig_tab_settings(label_pad: int, state):
    with dpg.collapsing_header(label="Kramers-Kronig tab", default_open=True):
        test_test_combo: int = dpg.generate_uuid()
        test_mode_combo: int = dpg.generate_uuid()
        test_mu_crit_slider: int = dpg.generate_uuid()
        test_add_cap_checkbox: int = dpg.generate_uuid()
        test_add_ind_checkbox: int = dpg.generate_uuid()
        test_method_combo: int = dpg.generate_uuid()
        test_max_nfev_input: int = dpg.generate_uuid()

        def update_default_test_settings():
            state.config.default_test_settings = TestSettings(
                label_to_test.get(dpg.get_value(test_test_combo), Test.COMPLEX),
                label_to_mode.get(dpg.get_value(test_mode_combo), Mode.EXPLORATORY),
                999,
                dpg.get_value(test_mu_crit_slider),
                dpg.get_value(test_add_cap_checkbox),
                dpg.get_value(test_add_ind_checkbox),
                label_to_method.get(dpg.get_value(test_method_combo), Method.LEASTSQ),
                dpg.get_value(test_max_nfev_input),
            )

        def restore_default_test_settings():
            dpg.set_value(test_test_combo, test_to_label[DEFAULT_TEST_SETTINGS.test])
            dpg.set_value(test_mode_combo, mode_to_label[DEFAULT_TEST_SETTINGS.mode])
            dpg.set_value(test_mu_crit_slider, DEFAULT_TEST_SETTINGS.mu_criterion)
            dpg.set_value(test_add_cap_checkbox, DEFAULT_TEST_SETTINGS.add_capacitance)
            dpg.set_value(test_add_ind_checkbox, DEFAULT_TEST_SETTINGS.add_inductance)
            dpg.set_value(
                test_method_combo, method_to_label[DEFAULT_TEST_SETTINGS.method]
            )
            dpg.set_value(test_max_nfev_input, DEFAULT_TEST_SETTINGS.max_nfev)
            update_default_test_settings()

        with dpg.group(horizontal=True):
            dpg.add_text("Test".rjust(label_pad))
            attach_tooltip(tooltips.kramers_kronig.test)
            dpg.add_combo(
                items=list(label_to_test.keys()),
                default_value=test_to_label.get(
                    state.config.default_test_settings.test
                ),
                callback=update_default_test_settings,
                tag=test_test_combo,
                width=-1,
            )
        with dpg.group(horizontal=True):
            dpg.add_text("Mode".rjust(label_pad))
            attach_tooltip(tooltips.kramers_kronig.mode)
            dpg.add_combo(
                items=list(label_to_mode.keys()),
                default_value=mode_to_label.get(
                    state.config.default_test_settings.mode
                ),
                callback=update_default_test_settings,
                tag=test_mode_combo,
                width=-1,
            )
        with dpg.group(horizontal=True):
            dpg.add_text("Add capacitor".rjust(label_pad))
            attach_tooltip(tooltips.kramers_kronig.add_capacitance)
            dpg.add_checkbox(
                default_value=state.config.default_test_settings.add_capacitance,
                callback=update_default_test_settings,
                tag=test_add_cap_checkbox,
            )
        with dpg.group(horizontal=True):
            dpg.add_text("Add inductor".rjust(label_pad))
            attach_tooltip(tooltips.kramers_kronig.add_inductance)
            dpg.add_checkbox(
                default_value=state.config.default_test_settings.add_inductance,
                callback=update_default_test_settings,
                tag=test_add_ind_checkbox,
            )
        with dpg.group(horizontal=True):
            dpg.add_text("Mu-criterion".rjust(label_pad))
            attach_tooltip(tooltips.kramers_kronig.mu_criterion)
            dpg.add_slider_float(
                default_value=state.config.default_test_settings.mu_criterion,
                min_value=0.01,
                max_value=0.99,
                clamped=True,
                format="%.2f",
                callback=update_default_test_settings,
                tag=test_mu_crit_slider,
                width=-1,
            )
        with dpg.group(horizontal=True):
            dpg.add_text("Fitting method".rjust(label_pad))
            attach_tooltip(tooltips.kramers_kronig.method)
            dpg.add_combo(
                items=list(label_to_method.keys()),
                default_value=method_to_label.get(
                    state.config.default_test_settings.method
                ),
                callback=update_default_test_settings,
                tag=test_method_combo,
                width=-1,
            )
        with dpg.group(horizontal=True):
            dpg.add_text("Max. num. func. eval.".rjust(label_pad))
            attach_tooltip(tooltips.kramers_kronig.nfev)
            dpg.add_input_int(
                default_value=state.config.default_test_settings.max_nfev,
                min_value=0,
                min_clamped=True,
                step=0,
                on_enter=True,
                callback=update_default_test_settings,
                tag=test_max_nfev_input,
                width=-1,
            )
        with dpg.group(horizontal=True):
            dpg.add_text("".rjust(label_pad))
            dpg.add_button(
                label="Restore defaults",
                callback=restore_default_test_settings,
            )
        section_spacer()


def fitting_tab_settings(label_pad: int, state):
    with dpg.collapsing_header(label="Fitting tab", default_open=True):
        fit_cdc_input: int = dpg.generate_uuid()
        fit_method_combo: int = dpg.generate_uuid()
        fit_weight_combo: int = dpg.generate_uuid()
        fit_max_nfev_input: int = dpg.generate_uuid()

        def update_default_fit_settings():
            state.config.default_fit_settings = FitSettings(
                dpg.get_value(fit_cdc_input),
                label_to_method.get(dpg.get_value(fit_method_combo), Method.AUTO),
                label_to_weight.get(dpg.get_value(fit_weight_combo), Weight.AUTO),
                dpg.get_value(fit_max_nfev_input),
            )

        def restore_default_fit_settings():
            dpg.set_value(fit_cdc_input, DEFAULT_FIT_SETTINGS.cdc)
            dpg.set_value(
                fit_method_combo,
                method_to_label.get(DEFAULT_FIT_SETTINGS.method, "Auto"),
            )
            dpg.set_value(
                fit_weight_combo,
                weight_to_label.get(DEFAULT_FIT_SETTINGS.weight, "Auto"),
            )
            dpg.set_value(fit_max_nfev_input, DEFAULT_FIT_SETTINGS.max_nfev)
            update_default_fit_settings()

        with dpg.group(horizontal=True):
            dpg.add_text("Circuit".rjust(label_pad))
            attach_tooltip(tooltips.fitting.cdc)
            dpg.add_input_text(
                default_value=state.config.default_fit_settings.cdc,
                on_enter=True,
                callback=update_default_fit_settings,
                width=-1,
                tag=fit_cdc_input,
            )
        with dpg.group(horizontal=True):
            dpg.add_text("Method".rjust(label_pad))
            attach_tooltip(tooltips.fitting.method)
            dpg.add_combo(
                items=["Auto"] + list(label_to_method.keys()),
                default_value=method_to_label.get(
                    state.config.default_fit_settings.method, "Auto"
                ),
                width=-1,
                callback=update_default_fit_settings,
                tag=fit_method_combo,
            )
        with dpg.group(horizontal=True):
            dpg.add_text("Weight function".rjust(label_pad))
            attach_tooltip(tooltips.fitting.weight)
            dpg.add_combo(
                items=["Auto"] + list(label_to_weight.keys()),
                default_value=weight_to_label.get(
                    state.config.default_fit_settings.weight, "Auto"
                ),
                width=-1,
                callback=update_default_fit_settings,
                tag=fit_weight_combo,
            )
        with dpg.group(horizontal=True):
            dpg.add_text("Max. num. func. eval.".rjust(label_pad))
            attach_tooltip(tooltips.fitting.nfev)
            dpg.add_input_int(
                default_value=state.config.default_fit_settings.max_nfev,
                min_value=0,
                min_clamped=True,
                step=0,
                on_enter=True,
                callback=update_default_fit_settings,
                tag=fit_max_nfev_input,
                width=-1,
            )
        with dpg.group(horizontal=True):
            dpg.add_text("".rjust(label_pad))
            dpg.add_button(
                label="Restore defaults",
                callback=restore_default_fit_settings,
            )
        section_spacer()


def simulation_tab_settings(label_pad: int, state):
    with dpg.collapsing_header(label="Simulation tab", default_open=True):
        sim_cdc_input: int = dpg.generate_uuid()
        sim_max_freq_input: int = dpg.generate_uuid()
        sim_min_freq_input: int = dpg.generate_uuid()
        sim_per_decade_input: int = dpg.generate_uuid()

        def update_default_sim_settings():
            state.config.default_simulation_settings = SimulationSettings(
                dpg.get_value(sim_cdc_input),
                dpg.get_value(sim_min_freq_input),
                dpg.get_value(sim_max_freq_input),
                dpg.get_value(sim_per_decade_input),
            )

        def restore_default_sim_settings():
            dpg.set_value(sim_cdc_input, DEFAULT_SIMULATION_SETTINGS.cdc)
            dpg.set_value(sim_min_freq_input, DEFAULT_SIMULATION_SETTINGS.min_frequency)
            dpg.set_value(sim_max_freq_input, DEFAULT_SIMULATION_SETTINGS.max_frequency)
            dpg.set_value(
                sim_per_decade_input, DEFAULT_SIMULATION_SETTINGS.num_per_decade
            )
            update_default_sim_settings()

        with dpg.group(horizontal=True):
            dpg.add_text("Circuit".rjust(label_pad))
            attach_tooltip(tooltips.simulation.cdc)
            dpg.add_input_text(
                default_value=state.config.default_simulation_settings.cdc,
                on_enter=True,
                callback=update_default_sim_settings,
                width=-1,
                tag=sim_cdc_input,
            )
        with dpg.group(horizontal=True):
            dpg.add_text("Max. frequency".rjust(label_pad))
            attach_tooltip(tooltips.simulation.max_freq)
            dpg.add_input_float(
                label="Hz",
                default_value=state.config.default_simulation_settings.max_frequency,
                min_value=1e-20,
                max_value=1e20,
                min_clamped=True,
                max_clamped=True,
                on_enter=True,
                format="%.3E",
                step=0.0,
                width=-22,
                callback=update_default_sim_settings,
                tag=sim_max_freq_input,
            )
        with dpg.group(horizontal=True):
            dpg.add_text("Min. frequency".rjust(label_pad))
            attach_tooltip(tooltips.simulation.min_freq)
            dpg.add_input_float(
                label="Hz",
                default_value=state.config.default_simulation_settings.min_frequency,
                min_value=1e-20,
                max_value=1e20,
                min_clamped=True,
                max_clamped=True,
                on_enter=True,
                format="%.3E",
                step=0.0,
                width=-22,
                callback=update_default_sim_settings,
                tag=sim_min_freq_input,
            )
        with dpg.group(horizontal=True):
            dpg.add_text("Num. points per decade".rjust(label_pad))
            attach_tooltip(tooltips.simulation.per_decade)
            dpg.add_input_int(
                default_value=state.config.default_simulation_settings.num_per_decade,
                min_value=1,
                min_clamped=True,
                step=0,
                on_enter=True,
                callback=update_default_sim_settings,
                tag=sim_per_decade_input,
                width=-1,
            )
        with dpg.group(horizontal=True):
            dpg.add_text("".rjust(label_pad))
            dpg.add_button(
                label="Restore defaults",
                callback=restore_default_sim_settings,
            )
        section_spacer()


def plotting_tab_settings(label_pad: int, state):
    with dpg.collapsing_header(label="Plotting tab - Export plot", default_open=True):
        export_units: int = dpg.generate_uuid()
        export_width: int = dpg.generate_uuid()
        export_height: int = dpg.generate_uuid()
        export_dpi: int = dpg.generate_uuid()
        export_preview: int = dpg.generate_uuid()
        export_title: int = dpg.generate_uuid()
        export_legend: int = dpg.generate_uuid()
        export_legend_location: int = dpg.generate_uuid()
        export_grid: int = dpg.generate_uuid()
        export_tight: int = dpg.generate_uuid()
        export_num_per_decade: int = dpg.generate_uuid()
        export_extension: int = dpg.generate_uuid()
        export_experimental_clear_registry: int = dpg.generate_uuid()
        export_experimental_disable_previews: int = dpg.generate_uuid()

        def restore_default_export_settings():
            state.config.export_units = 1
            state.config.export_width = 10.0
            state.config.export_height = 6.0
            state.config.export_dpi = 100
            state.config.export_preview = 4
            state.config.export_title = True
            state.config.export_legend = True
            state.config.export_legend_location = 0
            state.config.export_grid = False
            state.config.export_tight = False
            state.config.export_num_per_decade = 100
            state.config.export_extension = ".png"
            state.config.export_experimental_clear_registry = True
            state.config.export_experimental_disable_previews = False
            dpg.set_value(export_units, list(UNITS_PER_INCH)[state.config.export_units])
            dpg.set_value(export_width, state.config.export_width)
            dpg.set_value(export_height, state.config.export_height)
            dpg.set_value(export_dpi, state.config.export_dpi)
            dpg.set_value(
                export_preview, list(PREVIEW_LIMITS)[state.config.export_preview]
            )
            dpg.set_value(export_title, state.config.export_title)
            dpg.set_value(export_legend, state.config.export_legend)
            dpg.set_value(
                export_legend_location,
                list(LEGEND_LOCATIONS)[state.config.export_legend_location],
            )
            dpg.set_value(export_grid, state.config.export_grid)
            dpg.set_value(export_tight, state.config.export_tight)
            dpg.set_value(export_num_per_decade, state.config.export_num_per_decade)
            dpg.set_value(export_extension, state.config.export_extension)
            dpg.set_value(
                export_experimental_clear_registry,
                state.config.export_experimental_clear_registry,
            )
            dpg.set_value(
                export_experimental_disable_previews,
                state.config.export_experimental_disable_previews,
            )
            state.plot_exporter.update_settings(state.config)

        def update_export_units(unit: str):
            state.config.export_units = list(UNITS_PER_INCH).index(unit)
            state.plot_exporter.update_settings(state.config)

        def update_export_width(width: float):
            state.config.export_width = width
            state.plot_exporter.update_settings(state.config)

        def update_export_height(height: float):
            state.config.export_height = height
            state.plot_exporter.update_settings(state.config)

        def update_export_dpi(dpi: float):
            state.config.export_dpi = dpi
            state.plot_exporter.update_settings(state.config)

        def update_export_preview(limit: str):
            state.config.export_preview = list(PREVIEW_LIMITS).index(limit)
            state.plot_exporter.update_settings(state.config)

        def update_export_title(flag: bool):
            state.config.export_title = flag
            state.plot_exporter.update_settings(state.config)

        def update_export_legend(flag: bool):
            state.config.export_legend = flag
            state.plot_exporter.update_settings(state.config)

        def update_export_legend_location(location: str):
            state.config.export_legend_location = LEGEND_LOCATIONS[location]
            state.plot_exporter.update_settings(state.config)

        def update_export_grid(flag: bool):
            state.config.export_grid = flag
            state.plot_exporter.update_settings(state.config)

        def update_export_tight(flag: bool):
            state.config.export_tight = flag
            state.plot_exporter.update_settings(state.config)

        def update_export_num_per_decade(num: int):
            state.config.export_num_per_decade = num
            state.plot_exporter.update_settings(state.config)

        def update_export_extension(ext: str):
            state.config.export_extension = EXTENSIONS.index(ext)
            state.plot_exporter.update_settings(state.config)

        def update_export_experimental_clear_registry(flag: bool):
            state.config.export_experimental_clear_registry = flag
            state.plot_exporter.update_settings(state.config)

        def update_export_experimental_disable_previews(flag: bool):
            state.config.export_experimental_disable_previews = flag
            state.plot_exporter.update_settings(state.config)

        with dpg.group(horizontal=True):
            dpg.add_text("Units".rjust(label_pad))
            attach_tooltip(tooltips.plotting.export_units)
            dpg.add_combo(
                width=-1,
                items=list(UNITS_PER_INCH.keys()),
                default_value=list(UNITS_PER_INCH.keys())[state.config.export_units],
                callback=lambda s, a, u: update_export_units(a),
                tag=export_units,
            )
        with dpg.group(horizontal=True):
            dpg.add_text("Width".rjust(label_pad))
            attach_tooltip(tooltips.plotting.export_width)
            dpg.add_input_float(
                width=-1,
                default_value=state.config.export_width,
                min_value=0.01,
                min_clamped=True,
                step=0.0,
                format="%.2f",
                on_enter=True,
                callback=lambda s, a, u: update_export_width(a),
                tag=export_width,
            )
        with dpg.group(horizontal=True):
            dpg.add_text("Height".rjust(label_pad))
            attach_tooltip(tooltips.plotting.export_height)
            dpg.add_input_float(
                width=-1,
                default_value=state.config.export_height,
                min_value=0.01,
                min_clamped=True,
                step=0.0,
                format="%.2f",
                on_enter=True,
                callback=lambda s, a, u: update_export_height(a),
                tag=export_height,
            )
        with dpg.group(horizontal=True):
            dpg.add_text("DPI".rjust(label_pad))
            attach_tooltip(tooltips.plotting.export_dpi)
            dpg.add_input_int(
                width=-1,
                default_value=state.config.export_dpi,
                min_value=1,
                min_clamped=True,
                step=0,
                on_enter=True,
                callback=lambda s, a, u: update_export_dpi(a),
                tag=export_dpi,
            )
        with dpg.group(horizontal=True):
            dpg.add_text("Preview".rjust(label_pad))
            attach_tooltip(tooltips.plotting.export_preview)
            dpg.add_combo(
                width=-1,
                items=list(PREVIEW_LIMITS.keys()),
                default_value=list(PREVIEW_LIMITS.keys())[state.config.export_preview],
                callback=lambda s, a, u: update_export_preview(a),
                tag=export_preview,
            )
        with dpg.group(horizontal=True):
            dpg.add_text("Title".rjust(label_pad))
            attach_tooltip(tooltips.plotting.export_title)
            dpg.add_checkbox(
                default_value=state.config.export_title,
                callback=lambda s, a, u: update_export_title(a),
                tag=export_title,
            )
        with dpg.group(horizontal=True):
            dpg.add_text("Legend".rjust(label_pad))
            attach_tooltip(tooltips.plotting.export_legend)
            dpg.add_checkbox(
                default_value=state.config.export_legend,
                callback=lambda s, a, u: update_export_legend(a),
                tag=export_legend,
            )
            dpg.add_combo(
                width=-1,
                items=list(LEGEND_LOCATIONS.keys()),
                default_value=list(LEGEND_LOCATIONS.keys())[0],
                callback=lambda s, a, u: update_export_legend_location(a),
                tag=export_legend_location,
            )
        with dpg.group(horizontal=True):
            dpg.add_text("Grid".rjust(label_pad))
            attach_tooltip(tooltips.plotting.export_grid)
            dpg.add_checkbox(
                default_value=state.config.export_grid,
                callback=lambda s, a, u: update_export_grid(a),
                tag=export_grid,
            )
        with dpg.group(horizontal=True):
            dpg.add_text("Tight".rjust(label_pad))
            attach_tooltip(tooltips.plotting.export_tight)
            dpg.add_checkbox(
                default_value=state.config.export_tight,
                callback=lambda s, a, u: update_export_tight(a),
                tag=export_tight,
            )
        with dpg.group(horizontal=True):
            dpg.add_text("Points per decade".rjust(label_pad))
            attach_tooltip(tooltips.plotting.export_num_per_decade)
            dpg.add_input_int(
                width=-1,
                default_value=state.config.export_num_per_decade,
                min_value=1,
                min_clamped=True,
                step=0,
                on_enter=True,
                callback=lambda s, a, u: update_export_num_per_decade(a),
                tag=export_num_per_decade,
            )
        with dpg.group(horizontal=True):
            dpg.add_text("Extension".rjust(label_pad))
            attach_tooltip(tooltips.plotting.export_extension)
            dpg.add_combo(
                width=-1,
                items=EXTENSIONS,
                default_value=EXTENSIONS[state.config.export_extension],
                callback=lambda s, a, u: update_export_extension(a),
                tag=export_extension,
            )
        with dpg.group(horizontal=True):
            dpg.add_text("Clear texture registry".rjust(label_pad))
            attach_tooltip(tooltips.plotting.export_experimental_clear_registry)
            dpg.add_checkbox(
                default_value=state.config.export_experimental_clear_registry,
                callback=lambda s, a, u: update_export_experimental_clear_registry(a),
                tag=export_experimental_clear_registry,
            )
        with dpg.group(horizontal=True):
            dpg.add_text("Disable plot previews".rjust(label_pad))
            attach_tooltip(tooltips.plotting.export_experimental_disable_previews)
            dpg.add_checkbox(
                default_value=state.config.export_experimental_disable_previews,
                callback=lambda s, a, u: update_export_experimental_disable_previews(a),
                tag=export_experimental_disable_previews,
            )
        with dpg.group(horizontal=True):
            dpg.add_text("".rjust(label_pad))
            dpg.add_button(
                label="Restore defaults",
                callback=restore_default_export_settings,
            )
        section_spacer()


def show_defaults_settings_window(state):
    x: int
    y: int
    w: int
    h: int
    x, y, w, h = calculate_window_position_dimensions(374, 540)

    window: int = dpg.generate_uuid()
    key_handler: int = dpg.generate_uuid()

    def close_window():
        if dpg.does_item_exist(window):
            dpg.delete_item(window)
        if dpg.does_item_exist(key_handler):
            dpg.delete_item(key_handler)
        signals.emit(Signal.UNBLOCK_KEYBINDINGS)

    with dpg.handler_registry(tag=key_handler):
        dpg.add_key_release_handler(
            key=dpg.mvKey_Escape,
            callback=close_window,
        )

    with dpg.window(
        label="Settings - defaults",
        modal=True,
        pos=(
            x,
            y,
        ),
        width=w,
        height=h,
        no_resize=True,
        on_close=close_window,
        tag=window,
    ):
        label_pad: int = 22
        general_settings(label_pad, state)
        kramers_kronig_tab_settings(label_pad, state)
        fitting_tab_settings(label_pad, state)
        simulation_tab_settings(label_pad, state)
        plotting_tab_settings(label_pad, state)
    signals.emit(Signal.BLOCK_KEYBINDINGS, window=window)
