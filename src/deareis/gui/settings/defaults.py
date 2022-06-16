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
from deareis.signals import Signal
import deareis.signals as signals


def show_defaults_settings_window(state):
    x: int
    y: int
    w: int
    h: int
    x, y, w, h = calculate_window_position_dimensions(366, 540)

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
        label_pad: int
        # TODO: Timeout when generating certain outputs (e.g. SymPy and LaTeX expressions)
        # with dpg.collapsing_header(label="General", default_open=True):
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
                    label_to_method.get(
                        dpg.get_value(test_method_combo), Method.LEASTSQ
                    ),
                    dpg.get_value(test_max_nfev_input),
                )

            def restore_default_test_settings():
                dpg.set_value(
                    test_test_combo, test_to_label[DEFAULT_TEST_SETTINGS.test]
                )
                dpg.set_value(
                    test_mode_combo, mode_to_label[DEFAULT_TEST_SETTINGS.mode]
                )
                dpg.set_value(test_mu_crit_slider, DEFAULT_TEST_SETTINGS.mu_criterion)
                dpg.set_value(
                    test_add_cap_checkbox, DEFAULT_TEST_SETTINGS.add_capacitance
                )
                dpg.set_value(
                    test_add_ind_checkbox, DEFAULT_TEST_SETTINGS.add_inductance
                )
                dpg.set_value(
                    test_method_combo, method_to_label[DEFAULT_TEST_SETTINGS.method]
                )
                dpg.set_value(test_max_nfev_input, DEFAULT_TEST_SETTINGS.max_nfev)
                update_default_test_settings()

            label_pad = 22
            with dpg.child_window(border=False, width=350, height=180):
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
            dpg.add_spacer(height=8)

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

            label_pad = 22
            with dpg.child_window(border=False, width=350, height=112):
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
            dpg.add_spacer(height=8)

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
                dpg.set_value(
                    sim_min_freq_input, DEFAULT_SIMULATION_SETTINGS.min_frequency
                )
                dpg.set_value(
                    sim_max_freq_input, DEFAULT_SIMULATION_SETTINGS.max_frequency
                )
                dpg.set_value(
                    sim_per_decade_input, DEFAULT_SIMULATION_SETTINGS.num_freq_per_dec
                )
                update_default_sim_settings()

            label_pad = 22
            with dpg.child_window(border=False, width=350, height=112):
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
                        default_value=state.config.default_simulation_settings.num_freq_per_dec,
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
    signals.emit(Signal.BLOCK_KEYBINDINGS, window=window)
