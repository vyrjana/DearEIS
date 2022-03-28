# Copyright 2022 DearEIS developers
# DearEIS is licensed under the GPLv3 or later (https://www.gnu.org/licenses/gpl-3.0.html).
# The licenses of DearEIS' dependencies and/or sources of portions of code are included in
# the LICENSES folder.

import dearpygui.dearpygui as dpg
from deareis.utility import attach_tooltip, window_pos_dims
import deareis.tooltips as tooltips
from deareis.config import CONFIG
from deareis.data.kramers_kronig import (
    TestSettings,
    Method,
    Mode,
    Test,
    label_to_method,
    label_to_mode,
    label_to_test,
    method_to_label,
    mode_to_label,
    test_to_label,
)
from deareis.data.fitting import (
    FitSettings,
    Weight,
    label_to_weight,
    weight_to_label,
)
from deareis.data.simulation import SimulationSettings


def show_defaults_settings_window(self):
    x: int
    y: int
    w: int
    h: int
    x, y, w, h = window_pos_dims(366)
    if h > 492:
        x, y, w, h = window_pos_dims(w, 492)

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
        label="Settings - defaults",
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
        label_pad: int
        with dpg.collapsing_header(label="Kramers-Kronig tab", default_open=True):
            test_test_combo: int = dpg.generate_uuid()
            test_mode_combo: int = dpg.generate_uuid()
            test_mu_crit_slider: int = dpg.generate_uuid()
            test_add_cap_checkbox: int = dpg.generate_uuid()
            test_add_ind_checkbox: int = dpg.generate_uuid()
            test_method_combo: int = dpg.generate_uuid()
            test_max_nfev_input: int = dpg.generate_uuid()

            def update_default_test_settings():
                CONFIG.default_test_settings = TestSettings(
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
                dpg.set_value(test_test_combo, list(label_to_test.keys())[1])
                dpg.set_value(test_mode_combo, list(label_to_mode.keys())[1])
                dpg.set_value(test_mu_crit_slider, 0.85)
                dpg.set_value(test_add_cap_checkbox, True)
                dpg.set_value(test_add_ind_checkbox, True)
                dpg.set_value(test_method_combo, list(label_to_method.keys())[0])
                dpg.set_value(test_max_nfev_input, 1000)
                update_default_test_settings()

            label_pad = 22
            with dpg.child_window(border=False, width=350, height=180):
                with dpg.group(horizontal=True):
                    dpg.add_text("Test".rjust(label_pad))
                    attach_tooltip(tooltips.kramers_kronig_test)
                    dpg.add_combo(
                        items=list(label_to_test.keys()),
                        default_value=test_to_label.get(
                            CONFIG.default_test_settings.test
                        ),
                        callback=update_default_test_settings,
                        tag=test_test_combo,
                        width=-1,
                    )
                with dpg.group(horizontal=True):
                    dpg.add_text("Mode".rjust(label_pad))
                    attach_tooltip(tooltips.kramers_kronig_mode)
                    dpg.add_combo(
                        items=list(label_to_mode.keys()),
                        default_value=mode_to_label.get(
                            CONFIG.default_test_settings.mode
                        ),
                        callback=update_default_test_settings,
                        tag=test_mode_combo,
                        width=-1,
                    )
                with dpg.group(horizontal=True):
                    dpg.add_text("Add capacitor".rjust(label_pad))
                    attach_tooltip(tooltips.kramers_kronig_add_cap)
                    dpg.add_checkbox(
                        default_value=CONFIG.default_test_settings.add_capacitance,
                        callback=update_default_test_settings,
                        tag=test_add_cap_checkbox,
                    )
                with dpg.group(horizontal=True):
                    dpg.add_text("Add inductor".rjust(label_pad))
                    attach_tooltip(tooltips.kramers_kronig_add_ind)
                    dpg.add_checkbox(
                        default_value=CONFIG.default_test_settings.add_inductance,
                        callback=update_default_test_settings,
                        tag=test_add_ind_checkbox,
                    )
                with dpg.group(horizontal=True):
                    dpg.add_text("Mu-criterion".rjust(label_pad))
                    attach_tooltip(tooltips.kramers_kronig_mu_crit)
                    dpg.add_slider_float(
                        default_value=CONFIG.default_test_settings.mu_criterion,
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
                    attach_tooltip(tooltips.kramers_kronig_method)
                    dpg.add_combo(
                        items=list(label_to_method.keys()),
                        default_value=method_to_label.get(
                            CONFIG.default_test_settings.method
                        ),
                        callback=update_default_test_settings,
                        tag=test_method_combo,
                        width=-1,
                    )
                with dpg.group(horizontal=True):
                    dpg.add_text("Max. num. func. eval.".rjust(label_pad))
                    attach_tooltip(tooltips.kramers_kronig_nfev)
                    dpg.add_input_int(
                        default_value=CONFIG.default_test_settings.max_nfev,
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
            fit_method_combo: int = dpg.generate_uuid()
            fit_weight_combo: int = dpg.generate_uuid()
            fit_max_nfev_input: int = dpg.generate_uuid()

            def update_default_fit_settings():
                CONFIG.default_fit_settings = FitSettings(
                    "",
                    label_to_method.get(dpg.get_value(fit_method_combo), Method.AUTO),
                    label_to_weight.get(dpg.get_value(fit_weight_combo), Weight.AUTO),
                    dpg.get_value(fit_max_nfev_input),
                )

            def restore_default_fit_settings():
                dpg.set_value(fit_method_combo, "Auto")
                dpg.set_value(fit_weight_combo, "Auto")
                dpg.set_value(fit_max_nfev_input, 1000)
                update_default_fit_settings()

            label_pad = 22
            with dpg.child_window(border=False, width=350, height=88):
                with dpg.group(horizontal=True):
                    dpg.add_text("Method".rjust(label_pad))
                    attach_tooltip(tooltips.fitting_method)
                    dpg.add_combo(
                        items=["Auto"] + list(label_to_method.keys()),
                        default_value=method_to_label.get(
                            CONFIG.default_fit_settings.method, "Auto"
                        ),
                        width=-1,
                        callback=update_default_fit_settings,
                        tag=fit_method_combo,
                    )
                with dpg.group(horizontal=True):
                    dpg.add_text("Weight function".rjust(label_pad))
                    attach_tooltip(tooltips.fitting_weight)
                    dpg.add_combo(
                        items=["Auto"] + list(label_to_weight.keys()),
                        default_value=weight_to_label.get(
                            CONFIG.default_fit_settings.weight, "Auto"
                        ),
                        width=-1,
                        callback=update_default_fit_settings,
                        tag=fit_weight_combo,
                    )
                with dpg.group(horizontal=True):
                    dpg.add_text("Max. num. func. eval.".rjust(label_pad))
                    attach_tooltip(tooltips.fitting_nfev)
                    dpg.add_input_int(
                        default_value=CONFIG.default_fit_settings.max_nfev,
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
            sim_max_freq_input: int = dpg.generate_uuid()
            sim_min_freq_input: int = dpg.generate_uuid()
            sim_per_decade_input: int = dpg.generate_uuid()

            def update_default_sim_settings():
                CONFIG.default_simulation_settings = SimulationSettings(
                    "",
                    dpg.get_value(sim_min_freq_input),
                    dpg.get_value(sim_max_freq_input),
                    dpg.get_value(sim_per_decade_input),
                )

            def restore_default_sim_settings():
                dpg.set_value(sim_min_freq_input, 1e-2),
                dpg.set_value(sim_max_freq_input, 1e5),
                dpg.set_value(sim_per_decade_input, 1),
                update_default_sim_settings()

            label_pad = 22
            with dpg.child_window(border=False, width=350, height=88):
                with dpg.group(horizontal=True):
                    dpg.add_text("Max. frequency".rjust(label_pad))
                    attach_tooltip(tooltips.simulation_max_freq)
                    dpg.add_input_float(
                        label="Hz",
                        default_value=CONFIG.default_simulation_settings.max_frequency,
                        min_value=1e-20,
                        max_value=1e20,
                        min_clamped=True,
                        max_clamped=True,
                        on_enter=True,
                        format="%.3E",
                        step=0.0,
                        width=-1,
                        callback=update_default_sim_settings,
                        tag=sim_max_freq_input,
                    )
                with dpg.group(horizontal=True):
                    dpg.add_text("Min. frequency".rjust(label_pad))
                    attach_tooltip(tooltips.simulation_min_freq)
                    dpg.add_input_float(
                        label="Hz",
                        default_value=CONFIG.default_simulation_settings.min_frequency,
                        min_value=1e-20,
                        max_value=1e20,
                        min_clamped=True,
                        max_clamped=True,
                        on_enter=True,
                        format="%.3E",
                        step=0.0,
                        width=-1,
                        callback=update_default_sim_settings,
                        tag=sim_min_freq_input,
                    )
                with dpg.group(horizontal=True):
                    dpg.add_text("Num. points per decade".rjust(label_pad))
                    attach_tooltip(tooltips.simulation_per_decade)
                    dpg.add_input_int(
                        default_value=CONFIG.default_simulation_settings.num_freq_per_dec,
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
