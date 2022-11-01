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

from math import isclose
from os import getcwd
from os.path import (
    exists,
    join,
)
from threading import Timer
from time import (
    sleep,
    time,
)
from traceback import format_exc
from typing import (
    Callable,
    Dict,
    List,
    Optional,
)
import dearpygui.dearpygui as dpg
import deareis.signals as signals
from deareis.signals import Signal
from deareis.state import STATE
from deareis.enums import (
    Action,
    CNLSMethod,
    Context,
    DRTMethod,
    DRTMode,
    TestMode,
    PlotType,
    RBFShape,
    RBFType,
    Test,
    Weight,
)
from deareis.data import (
    DRTResult,
    DRTSettings,
    DataSet,
    FitResult,
    FitSettings,
    PlotSettings,
    Project,
    SimulationResult,
    SimulationSettings,
    TestResult,
    TestSettings,
)
from deareis.gui import ProjectTab


"""
Signal.AVERAGE_DATA_SETS
Signal.BLOCK_KEYBINDINGS
Signal.CLEAR_RECENT_PROJECTS
Signal.COPY_OUTPUT
Signal.COPY_PLOT_APPEARANCE_SETTINGS
Signal.COPY_PLOT_DATA
Signal.CREATE_PROJECT_SNAPSHOT
Signal.MODIFY_DATA_SET_PATH
Signal.MODIFY_PLOT_SERIES_THEME
Signal.NEW_PROJECT
Signal.PERFORM_SIMULATION
Signal.REDO_PROJECT_ACTION
Signal.RESTORE_PROJECT_STATE
Signal.SAVE_PROJECT
Signal.SAVE_PROJECT_AS
Signal.SELECT_DATA_POINTS_TO_TOGGLE
Signal.SELECT_DATA_SETS_TO_AVERAGE
Signal.SELECT_DATA_SET_FILES
Signal.SELECT_DATA_SET_MASK_TO_COPY
Signal.SELECT_FIT_RESULT
Signal.SELECT_HOME_TAB
Signal.SELECT_IMPEDANCE_TO_SUBTRACT
Signal.SELECT_PLOT_APPEARANCE_SETTINGS
Signal.SELECT_PLOT_SETTINGS
Signal.SELECT_PROJECT_FILES
Signal.SELECT_PROJECT_TAB
Signal.SELECT_SIMULATION_RESULT
Signal.SELECT_TEST_RESULT
Signal.SHOW_BUSY_MESSAGE
Signal.SHOW_COMMAND_PALETTE
Signal.SHOW_ENLARGED_PLOT
Signal.SHOW_ERROR_MESSAGE
Signal.SHOW_HELP_ABOUT
Signal.SHOW_HELP_LICENSES
Signal.SHOW_SETTINGS_APPEARANCE
Signal.SHOW_SETTINGS_DEFAULTS
Signal.SHOW_SETTINGS_KEYBINDINGS
Signal.TOGGLE_DATA_POINT
Signal.UNBLOCK_KEYBINDINGS
Signal.UNDO_PROJECT_ACTION
Signal.VIEWPORT_RESIZED
"""

# TODO
# - Tests copying plot data as CSV
# - (Un)select groups of plottable series
# - Edit plot series appearance
# - Adjust limits checkbox and its impact on modal plot windows


START_TIME: float = 0.0


def next_step(next_func: Callable, delay: float = 1.0) -> Callable:
    def outer_wrapper(func: Callable) -> Callable:
        def inner_wrapper():
            func()
            if delay > 0.0:
                Timer(delay, next_func).start()
            else:
                next_func()

        return inner_wrapper

    return outer_wrapper


def finish_tests():
    signals.emit(Signal.CLOSE_PROJECT, force=True)
    print(f"\nFinished in {time() - START_TIME:.2f} s")
    Timer(1.0, dpg.stop_dearpygui).start()


def test_undo_redo():
    project: Optional[Project] = STATE.get_active_project()
    project_tab: Optional[ProjectTab] = STATE.get_active_project_tab()
    tests: Dict[str, List[TestResult]]
    drts: Dict[str, List[DRTResult]]
    fits: Dict[str, List[FitResult]]
    sims: List[SimulationResult]
    plots: List[PlotSettings]
    undo_steps: int = 0

    @next_step(finish_tests)
    def validate_redo():
        assert project.get_label() == "New project label"
        data_sets: List[DataSet] = project.get_data_sets()
        assert len(data_sets) == 1
        assert data_sets[0].get_label() == "Noisier data"
        assert sum(data_sets[0].get_mask().values()) == 14
        tests = project.get_all_tests()
        assert len(tests) == 1
        assert sum(map(len, tests.values())) == 2
        drts = project.get_all_drts()
        assert len(drts) == 1
        assert sum(map(len, drts.values())) == 4
        fits = project.get_all_fits()
        assert len(fits) == 1
        assert sum(map(len, fits.values())) == 2
        sims = project.get_simulations()
        assert len(sims) == 1
        plots = project.get_plots()
        assert len(plots) == 5
        assert plots[0].get_label() == "Ideal"
        assert plots[1].get_label() == "Ideal - DRT"
        assert plots[2].get_label() == "Noisy"
        assert plots[3].get_label() == "Noisy - DRT"
        assert plots[4].get_label() == "Test plot"

    def redo():
        nonlocal undo_steps
        print(f"  - Redo ({undo_steps})")
        undo_steps -= 1
        signals.emit(Signal.REDO_PROJECT_ACTION)
        Timer(
            1.0,
            redo if undo_steps > 0 else validate_redo,
        ).start()

    @next_step(redo)
    def validate_undo():
        assert project.get_label() == "Example project - Version 4"
        data_sets: List[DataSet] = project.get_data_sets()
        assert len(data_sets) == 2
        assert data_sets[0].get_label() == "Ideal data"
        assert not any(data_sets[0].get_mask().values())
        assert data_sets[1].get_label() == "Noisy data"
        assert not any(data_sets[1].get_mask().values())
        tests = project.get_all_tests()
        assert len(tests) == 2
        assert sum(map(len, tests.values())) == 2
        drts = project.get_all_drts()
        assert len(drts) == 2
        assert sum(map(len, drts.values())) == 8
        fits = project.get_all_fits()
        assert len(fits) == 2
        assert sum(map(len, fits.values())) == 2
        sims = project.get_simulations()
        assert len(sims) == 2
        plots = project.get_plots()
        assert len(plots) == 5
        assert plots[0].get_label() == "Appearance template"
        assert plots[1].get_label() == "Ideal"
        assert plots[2].get_label() == "Ideal - DRT"
        assert plots[3].get_label() == "Noisy"
        assert plots[4].get_label() == "Noisy - DRT"

    def undo():
        nonlocal undo_steps
        undo_steps += 1
        print(f"  - Undo ({undo_steps})")
        signals.emit(Signal.UNDO_PROJECT_ACTION)
        Timer(
            1.0,
            undo if STATE.is_project_dirty(project) else validate_undo,
        ).start()

    print("\n- Undo/redo")
    assert STATE.is_project_dirty(project) is True
    undo()


def test_plotting():
    project: Optional[Project] = STATE.get_active_project()
    project_tab: Optional[ProjectTab] = STATE.get_active_project_tab()

    @next_step(test_undo_redo)
    def validate_unselect_all():
        assert len(project_tab.get_active_plot().series_order) == 0

    @next_step(validate_unselect_all)
    def unselect_all():
        print("  - Unselect all")
        signals.emit(
            Signal.TOGGLE_PLOT_SERIES,
            enabled=False,
            **dpg.get_item_user_data(project_tab.plotting_tab.select_all_button),
        )

    @next_step(unselect_all)
    def export_plot_2():
        assert STATE.active_modal_window_object is not None
        STATE.active_modal_window_object.close()

    @next_step(export_plot_2)
    def export_plot_1():
        print("  - Export plot")
        signals.emit(
            Signal.EXPORT_PLOT,
            **dpg.get_item_user_data(project_tab.plotting_tab.export_button),
        )

    @next_step(export_plot_1)
    def validate_reorder_series():
        data: DataSet = project.get_data_sets()[0]
        assert data is not None
        settings: PlotSettings = project_tab.get_active_plot()
        assert settings.series_order.index(data.uuid) == 1
        series: int = dpg.get_item_children(
            project_tab.plotting_tab.plot_types[PlotType.BODE_PHASE]._y_axis, slot=1
        )[
            2
        ]  # 2 because 0 and 1 are for a Kramers-Kronig test result (scatter and line)
        assert dpg.get_item_label(series) == data.get_label(), (
            data.get_label(),
            dpg.get_item_label(series),
        )

    @next_step(validate_reorder_series)
    def reorder_series():
        print("  - Reorder series")
        settings: PlotSettings = project_tab.get_active_plot()
        signals.emit(
            Signal.REORDER_PLOT_SERIES,
            settings=settings,
            **{
                "uuid": settings.series_order[0],
                "step": 1,
            },
        )

    @next_step(reorder_series)
    def validate_select_plot_type():
        assert project_tab.get_active_plot().get_type() == PlotType.BODE_PHASE
        assert dpg.get_value(project_tab.plotting_tab.type_combo) == "Bode - phase"

    @next_step(validate_select_plot_type)
    def select_plot_type():
        print("  - Select plot type")
        settings: PlotSettings = project_tab.get_active_plot()
        signals.emit(
            Signal.SELECT_PLOT_TYPE, settings=settings, plot_type=PlotType.BODE_PHASE
        )

    @next_step(select_plot_type)
    def validate_copy_appearance():
        # TODO: Implement
        pass

    @next_step(validate_copy_appearance)
    def copy_appearance_2():
        assert STATE.active_modal_window_object is not None
        STATE.active_modal_window_object.accept()

    @next_step(copy_appearance_2)
    def copy_appearance_1():
        print("  - Copy appearance")
        signals.emit(
            Signal.SELECT_PLOT_APPEARANCE_SETTINGS,
            settings=dpg.get_item_user_data(project_tab.plotting_tab.delete_button),
        )

    @next_step(copy_appearance_1)
    def validate_select_all():
        assert len(project_tab.get_active_plot().series_order) == 10

    @next_step(validate_select_all)
    def select_all():
        print("  - Select all")
        signals.emit(
            Signal.TOGGLE_PLOT_SERIES,
            enabled=True,
            **dpg.get_item_user_data(project_tab.plotting_tab.select_all_button),
        )

    @next_step(select_all)
    def validate_rename_plot():
        assert len(project.get_plots()) == 5
        assert project_tab.get_active_plot().get_label() == "Test plot"
        assert dpg.get_value(project_tab.plotting_tab.label_input) == "Test plot"
        assert (
            dpg.get_item_label(
                project_tab.plotting_tab.plot_types[PlotType.NYQUIST]._plot
            )
            == "Test plot"
        )

    @next_step(validate_rename_plot)
    def rename_plot():
        print("  - Rename plot")
        settings: PlotSettings = project_tab.get_active_plot()
        signals.emit(Signal.RENAME_PLOT_SETTINGS, settings=settings, label="Test plot")

    @next_step(rename_plot)
    def validate_new_plot():
        plot: PlotSettings = project_tab.get_active_plot()
        assert len(project.get_plots()) == 5
        assert plot.get_label() == "Plot"
        assert len(plot.series_order) == 0
        assert dpg.get_value(project_tab.plotting_tab.label_input) == "Plot"
        assert (
            dpg.get_item_label(
                project_tab.plotting_tab.plot_types[PlotType.NYQUIST]._plot
            )
            == "Plot"
        )

    @next_step(validate_new_plot)
    def new_plot():
        print("  - New plot")
        signals.emit(Signal.NEW_PLOT_SETTINGS)

    @next_step(new_plot)
    def validate_delete_plot():
        assert len(project.get_plots()) == 4
        assert project_tab.get_active_plot().get_label() == "Ideal"

    @next_step(validate_delete_plot)
    def delete_plot():
        print("  - Delete plot")
        settings: PlotSettings = project_tab.get_active_plot()
        signals.emit(Signal.DELETE_PLOT_SETTINGS, settings=settings)

    STATE.keybinding_handler.perform_action(
        Action.SELECT_PLOTTING_TAB,
        Context.PROJECT,
        STATE.get_active_project(),
        STATE.get_active_project_tab(),
    )
    print("\n- Plotting")
    Timer(1.0, delete_plot).start()


def test_simulation():
    project: Optional[Project] = STATE.get_active_project()
    project_tab: Optional[ProjectTab] = STATE.get_active_project_tab()

    @next_step(test_plotting)
    def validate_select_previous_data_set():
        assert project_tab.get_active_data_set() is not None

    @next_step(validate_select_previous_data_set)
    def select_previous_data_set():
        print("  - Select previous data set")
        STATE.keybinding_handler.perform_action(
            Action.PREVIOUS_PRIMARY_RESULT,
            Context.SIMULATION_TAB,
            STATE.get_active_project(),
            STATE.get_active_project_tab(),
        )

    @next_step(select_previous_data_set)
    def validate_perform_simulation():
        assert len(project.get_simulations()) == 1
        assert project_tab.get_active_simulation() is not None

    @next_step(validate_perform_simulation)
    def perform_simulation():
        print("  - Perform simulation")
        settings: SimulationSettings = project_tab.simulation_tab.get_settings()
        signals.emit(Signal.PERFORM_SIMULATION, settings=settings)

    @next_step(perform_simulation)
    def validate_delete_result():
        assert len(project.get_simulations()) == 0
        assert project_tab.get_active_simulation() is None

    @next_step(validate_delete_result)
    def delete_result():
        print("  - Delete result")
        simulation: Optional[SimulationResult] = project_tab.get_active_simulation()
        signals.emit(Signal.DELETE_SIMULATION_RESULT, simulation=simulation)
        sleep(1.0)
        simulation = project_tab.get_active_simulation()
        signals.emit(Signal.DELETE_SIMULATION_RESULT, simulation=simulation)

    @next_step(delete_result)
    def validate_apply_settings():
        assert (
            dpg.get_value(project_tab.simulation_tab.settings_menu.cdc_input)
            == "[R(RC)(RW)]"
        )
        assert isclose(
            dpg.get_value(project_tab.simulation_tab.settings_menu.max_freq_input),
            1e5,
            rel_tol=1e-6,
        ), dpg.get_value(project_tab.simulation_tab.settings_menu.max_freq_input)
        assert isclose(
            dpg.get_value(project_tab.simulation_tab.settings_menu.min_freq_input),
            1e-2,
            rel_tol=1e-6,
        ), dpg.get_value(project_tab.simulation_tab.settings_menu.min_freq_input)
        assert (
            dpg.get_value(project_tab.simulation_tab.settings_menu.per_decade_input)
            == 1
        )

    @next_step(validate_apply_settings)
    def apply_settings():
        print("  - Apply settings")
        simulation: Optional[SimulationResult] = project_tab.get_active_simulation()
        signals.emit(Signal.APPLY_SIMULATION_SETTINGS, settings=simulation.settings)

    STATE.keybinding_handler.perform_action(
        Action.SELECT_SIMULATION_TAB,
        Context.PROJECT,
        STATE.get_active_project(),
        STATE.get_active_project_tab(),
    )
    print("\n- Simulation")
    Timer(1.0, apply_settings).start()


def test_fitting():
    project: Optional[Project] = STATE.get_active_project()
    project_tab: Optional[ProjectTab] = STATE.get_active_project_tab()
    data: Optional[DataSet]
    fit: Optional[FitResult]
    fits: List[FitResult]

    @next_step(test_simulation)
    def validate_select_next_result():
        data = project_tab.get_active_data_set()
        assert data is not None
        fits = project.get_fits(data)
        assert len(fits) == 2
        assert project_tab.get_active_fit() == fits[1]

    @next_step(validate_select_next_result)
    def select_next_result():
        print("  - Select next result")
        STATE.keybinding_handler.perform_action(
            Action.NEXT_SECONDARY_RESULT,
            Context.FITTING_TAB,
            STATE.get_active_project(),
            STATE.get_active_project_tab(),
        )

    @next_step(select_next_result)
    def validate_perform_fit():
        data = project_tab.get_active_data_set()
        assert data is not None
        assert project_tab.get_active_fit() is not None
        assert len(project.get_fits(data)) == 2

    @next_step(validate_perform_fit)
    def perform_fit(*args, **kwargs):
        print("  - Perform fit")
        data = project_tab.get_active_data_set()
        settings: FitSettings = FitSettings(
            "[(RC)]",
            CNLSMethod.LEAST_SQUARES,
            Weight.BOUKAMP,
            1000,
        )
        signals.emit(Signal.PERFORM_FIT, data=data, settings=settings)
        sleep(1.0)
        settings = FitSettings(
            "[R(RC)(RW)]",
            CNLSMethod.LEAST_SQUARES,
            Weight.BOUKAMP,
            1000,
        )
        signals.emit(Signal.PERFORM_FIT, data=data, settings=settings)

    @next_step(perform_fit)
    def validate_delete_result():
        data = project_tab.get_active_data_set()
        assert data is not None
        assert project_tab.get_active_fit() is None
        assert len(project.get_fits(data)) == 0

    @next_step(validate_delete_result)
    def delete_result(*args, **kwargs):
        print("  - Delete settings")
        data = project_tab.get_active_data_set()
        fit = project_tab.get_active_fit()
        signals.emit(Signal.DELETE_FIT_RESULT, data=data, fit=fit)

    @next_step(delete_result)
    def validate_apply_settings():
        assert (
            dpg.get_value(project_tab.fitting_tab.settings_menu.cdc_input)
            == "[R(RC)(RW)]"
        )
        assert (
            dpg.get_value(project_tab.fitting_tab.settings_menu.method_combo) == "Auto"
        )
        assert (
            dpg.get_value(project_tab.fitting_tab.settings_menu.weight_combo) == "Auto"
        )
        assert (
            dpg.get_value(project_tab.fitting_tab.settings_menu.max_nfev_input) == 1000
        )

    @next_step(validate_apply_settings)
    def apply_settings():
        print("  - Apply settings")
        fit = project_tab.get_active_fit()
        signals.emit(Signal.APPLY_FIT_SETTINGS, settings=fit.settings)

    STATE.keybinding_handler.perform_action(
        Action.SELECT_FITTING_TAB,
        Context.PROJECT,
        STATE.get_active_project(),
        STATE.get_active_project_tab(),
    )
    print("\n- Fitting")
    Timer(1.0, apply_settings).start()


def test_drt_analysis():
    project: Optional[Project] = STATE.get_active_project()
    project_tab: Optional[ProjectTab] = STATE.get_active_project_tab()
    data: Optional[DataSet]
    drt: Optional[DRTResult]
    settings: DRTSettings

    @next_step(test_fitting)
    def close_impedance():
        assert STATE.active_modal_window_object is not None
        STATE.active_modal_window_object.close()

    @next_step(close_impedance)
    def enlarge_impedance():
        print("  - Enlarge impedance")
        project_tab.drt_tab.show_enlarged_impedance()

    @next_step(enlarge_impedance)
    def close_drt():
        assert STATE.active_modal_window_object is not None
        STATE.active_modal_window_object.close()

    @next_step(close_drt)
    def enlarge_drt():
        print("  - Enlarge DRT")
        project_tab.drt_tab.show_enlarged_drt()

    @next_step(enlarge_drt)
    def validate_select_next_result():
        data = project_tab.get_active_data_set()
        assert data is not None
        drts = project.get_drts(data)
        assert project_tab.get_active_drt() == drts[1]

    @next_step(validate_select_next_result)
    def select_next_result():
        print("  - Select next DRT result")
        STATE.keybinding_handler.perform_action(
            Action.NEXT_SECONDARY_RESULT,
            Context.DRT_TAB,
            STATE.get_active_project(),
            STATE.get_active_project_tab(),
        )

    @next_step(select_next_result)
    def validate_perform_analysis():
        data = project_tab.get_active_data_set()
        assert len(project.get_drts(data)) == 4

    @next_step(validate_perform_analysis)
    def perform_analysis():
        print("  - Perform analysis")
        data = project_tab.get_active_data_set()
        settings = DRTSettings(
            method=DRTMethod.TR_NNLS,
            mode=DRTMode.IMAGINARY,
            lambda_value=1e-2,
            rbf_type=RBFType.CAUCHY,
            derivative_order=1,
            rbf_shape=RBFShape.FACTOR,
            shape_coeff=0.4,
            inductance=False,
            credible_intervals=True,
            num_samples=3000,
            num_attempts=12,
            maximum_symmetry=0.4,
            circuit=None,
            W=0.15,
            num_per_decade=100,
        )
        signals.emit(Signal.PERFORM_DRT, data=data, settings=settings)

    @next_step(perform_analysis)
    def validate_delete_result():
        data = project_tab.get_active_data_set()
        assert len(project.get_drts(data)) == 3

    @next_step(validate_delete_result)
    def delete_result():
        print("  - Delete DRT result")
        data = project_tab.get_active_data_set()
        drt = project_tab.get_active_drt()
        signals.emit(Signal.DELETE_DRT_RESULT, data=data, drt=drt)

    @next_step(delete_result)
    def validate_apply_settings():
        assert dpg.get_value(project_tab.drt_tab.settings_menu.method_combo) == "BHT"
        assert dpg.get_value(project_tab.drt_tab.settings_menu.mode_combo) == "Complex"
        assert dpg.get_value(project_tab.drt_tab.settings_menu.lambda_checkbox) is True
        assert (
            dpg.get_value(project_tab.drt_tab.settings_menu.derivative_order_combo)
            == "1st"
        )
        assert (
            dpg.get_value(project_tab.drt_tab.settings_menu.rbf_type_combo)
            == "Gaussian"
        )
        assert (
            dpg.get_value(project_tab.drt_tab.settings_menu.rbf_shape_combo) == "FWHM"
        )
        assert isclose(
            dpg.get_value(project_tab.drt_tab.settings_menu.shape_coeff_input),
            0.5,
            abs_tol=1e-3,
        )
        assert (
            dpg.get_value(project_tab.drt_tab.settings_menu.num_samples_input) == 10000
        )
        assert dpg.get_value(project_tab.drt_tab.settings_menu.num_attempts_input) == 50
        assert isclose(
            dpg.get_value(project_tab.drt_tab.settings_menu.maximum_symmetry_input),
            0.5,
            abs_tol=1e-3,
        )
        settings = project_tab.drt_tab.settings_menu.get_settings()
        assert settings.method == DRTMethod.BHT
        assert settings.mode == DRTMode.COMPLEX
        assert settings.lambda_value <= 0.0
        assert settings.derivative_order == 1
        assert settings.rbf_type == RBFType.GAUSSIAN
        assert settings.rbf_shape == RBFShape.FWHM
        assert isclose(
            settings.shape_coeff,
            0.5,
            abs_tol=1e-3,
        )
        assert settings.num_samples == 10000
        assert settings.num_attempts == 50
        assert isclose(
            settings.maximum_symmetry,
            0.5,
            abs_tol=1e-3,
        )

    @next_step(validate_apply_settings)
    def apply_settings():
        print("  - Apply DRT settings")
        drt = project_tab.get_active_drt()
        assert drt is not None
        signals.emit(Signal.APPLY_DRT_SETTINGS, settings=drt.settings)

    STATE.keybinding_handler.perform_action(
        Action.SELECT_DRT_TAB,
        Context.PROJECT,
        STATE.get_active_project(),
        STATE.get_active_project_tab(),
    )
    print("\n- DRT analysis")
    Timer(1.0, apply_settings).start()


def test_kramers_kronig():
    project: Optional[Project] = STATE.get_active_project()
    project_tab: Optional[ProjectTab] = STATE.get_active_project_tab()
    data: Optional[DataSet]
    test: Optional[TestResult]
    settings: TestSettings
    tests: List[TestResult]

    @next_step(test_drt_analysis)
    def close_residuals():
        assert STATE.active_modal_window_object is not None
        STATE.active_modal_window_object.close()

    @next_step(close_residuals)
    def enlarge_residuals():
        print("  - Enlarge residuals")
        project_tab.kramers_kronig_tab.show_enlarged_residuals()

    @next_step(enlarge_residuals)
    def validate_apply_settings():
        assert (
            dpg.get_value(project_tab.kramers_kronig_tab.settings_menu.test_combo)
            == "Complex"
        )
        assert (
            dpg.get_value(project_tab.kramers_kronig_tab.settings_menu.mode_combo)
            == "Auto"
        )
        assert (
            dpg.get_value(project_tab.kramers_kronig_tab.settings_menu.num_RC_slider)
            == 15
        )
        assert (
            dpg.get_value(project_tab.kramers_kronig_tab.settings_menu.add_cap_checkbox)
            is True
        )
        assert (
            dpg.get_value(project_tab.kramers_kronig_tab.settings_menu.add_ind_checkbox)
            is True
        )
        assert isclose(
            dpg.get_value(project_tab.kramers_kronig_tab.settings_menu.mu_crit_slider),
            0.85,
            rel_tol=1e-6,
        )
        assert (
            dpg.get_value(project_tab.kramers_kronig_tab.settings_menu.method_combo)
            == "Auto"
        )
        assert (
            dpg.get_value(project_tab.kramers_kronig_tab.settings_menu.max_nfev_input)
            == 1000
        )
        settings = project_tab.kramers_kronig_tab.settings_menu.get_settings()
        assert settings.test == Test.COMPLEX
        assert settings.mode == TestMode.AUTO
        assert settings.num_RC == 15
        assert settings.add_capacitance is True
        assert settings.add_inductance is True
        assert isclose(
            settings.mu_criterion,
            0.85,
            rel_tol=1e-6,
        )
        assert settings.method == CNLSMethod.AUTO
        assert settings.max_nfev == 1000

    @next_step(validate_apply_settings)
    def apply_settings():
        print("  - Apply test settings")
        test = project_tab.get_active_test()
        signals.emit(Signal.APPLY_TEST_SETTINGS, settings=test.settings)

    @next_step(apply_settings)
    def validate_select_next_result():
        data = project_tab.get_active_data_set()
        assert data is not None
        tests = project.get_tests(data)
        assert project_tab.get_active_test() == tests[1]

    @next_step(validate_select_next_result)
    def select_next_result():
        print("  - Select next result")
        STATE.keybinding_handler.perform_action(
            Action.NEXT_SECONDARY_RESULT,
            Context.KRAMERS_KRONIG_TAB,
            STATE.get_active_project(),
            STATE.get_active_project_tab(),
        )

    @next_step(select_next_result)
    def validate_perform_test():
        data = project_tab.get_active_data_set()
        assert len(project.get_tests(data)) == 2

    @next_step(validate_perform_test)
    def perform_test():
        print("  - Perform test")
        data = project_tab.get_active_data_set()
        settings = TestSettings(
            Test.COMPLEX,
            TestMode.AUTO,
            data.get_num_points(),
            0.85,
            True,
            True,
            CNLSMethod.AUTO,
            1000,
        )
        signals.emit(Signal.PERFORM_TEST, data=data, settings=settings)
        sleep(1.0)
        settings = TestSettings(
            Test.COMPLEX,
            TestMode.AUTO,
            int(data.get_num_points() / 3),
            0.85,
            True,
            True,
            CNLSMethod.AUTO,
            1000,
        )
        signals.emit(Signal.PERFORM_TEST, data=data, settings=settings)

    @next_step(perform_test)
    def validate_delete_result():
        data = project_tab.get_active_data_set()
        assert len(project.get_tests(data)) == 0

    @next_step(validate_delete_result)
    def delete_result():
        print("  - Delete test result")
        data = project_tab.get_active_data_set()
        test = project_tab.get_active_test()
        signals.emit(Signal.DELETE_TEST_RESULT, data=data, test=test)

    STATE.keybinding_handler.perform_action(
        Action.SELECT_KRAMERS_KRONIG_TAB,
        Context.PROJECT,
        STATE.get_active_project(),
        STATE.get_active_project_tab(),
    )
    print("\n- Kramers-Kronig")
    Timer(1.0, delete_result).start()


def test_data_sets():
    project: Optional[Project] = STATE.get_active_project()
    project_tab: Optional[ProjectTab] = STATE.get_active_project_tab()
    data: Optional[DataSet]
    mask: Dict[int, bool]

    @next_step(test_kramers_kronig)
    def close_bode():
        assert STATE.active_modal_window_object is not None
        STATE.active_modal_window_object.close()

    @next_step(close_bode)
    def enlarge_bode():
        print("  - Enlarge Bode")
        project_tab.data_sets_tab.show_enlarged_bode()

    @next_step(enlarge_bode)
    def close_nyquist():
        assert STATE.active_modal_window_object is not None
        STATE.active_modal_window_object.close()

    @next_step(close_nyquist)
    def enlarge_nyquist():
        print("  - Enlarge Nyquist")
        project_tab.data_sets_tab.show_enlarged_nyquist()

    @next_step(enlarge_nyquist)
    def validate_delete_data_set():
        data = project_tab.get_active_data_set()
        assert len(project.get_data_sets()) == 1
        assert len(project.get_all_tests()) == 1
        assert len(project.get_all_fits()) == 1
        assert data.get_label() == "Noisier data"

    @next_step(validate_delete_data_set)
    def delete_data_set():
        print("  - Delete data set")
        data = project_tab.get_active_data_set()
        signals.emit(Signal.DELETE_DATA_SET, data=data)

    @next_step(delete_data_set)
    def validate_copy_mask():
        data = project_tab.get_active_data_set()
        assert data.get_num_points() == 15

    @next_step(validate_copy_mask)
    def copy_mask_2():
        assert STATE.active_modal_window_object is not None
        STATE.active_modal_window_object.accept()

    @next_step(copy_mask_2)
    def copy_mask_1():
        print("  - Copy mask")
        signals.emit(
            Signal.SELECT_DATA_SET_MASK_TO_COPY,
            data=project_tab.get_active_data_set(),
        )

    @next_step(copy_mask_1)
    def validate_toggle_data_points():
        data = project_tab.get_active_data_set()
        assert data.get_num_points() == 0

    @next_step(validate_toggle_data_points)
    def toggle_data_points_2():
        assert STATE.active_modal_window_object is not None
        STATE.active_modal_window_object.accept()

    @next_step(toggle_data_points_2)
    def toggle_data_points_1():
        print("  - Toggle data points")
        signals.emit(
            Signal.SELECT_DATA_POINTS_TO_TOGGLE,
            data=project_tab.get_active_data_set(),
        )

    @next_step(toggle_data_points_1)
    def validate_subtract_impedance():
        data = project_tab.get_active_data_set()
        assert isclose(data.get_impedance()[0].real, 59, abs_tol=1e-1)

    @next_step(validate_subtract_impedance)
    def subtract_impedance_4():
        STATE.active_modal_window_object.accept()

    @next_step(subtract_impedance_4)
    def subtract_impedance_3():
        assert STATE.active_modal_window_object is not None
        dpg.set_value(STATE.active_modal_window_object.constant_real, 50)
        STATE.active_modal_window_object.update_preview()

    @next_step(subtract_impedance_3)
    def subtract_impedance_2():
        signals.emit(
            Signal.SELECT_IMPEDANCE_TO_SUBTRACT,
            data=project_tab.get_active_data_set(),
        )

    @next_step(subtract_impedance_2)
    def subtract_impedance_1():
        print("  - Subtract impedance")
        STATE.keybinding_handler.perform_action(
            Action.NEXT_PRIMARY_RESULT,
            Context.DATA_SETS_TAB,
            STATE.get_active_project(),
            STATE.get_active_project_tab(),
        )

    @next_step(subtract_impedance_1)
    def validate_apply_mask():
        data = project_tab.get_active_data_set()
        assert len(data.get_impedance(masked=None)) == 29
        assert len(data.get_impedance(masked=False)) == len(data.get_impedance()) == 15
        assert len(data.get_impedance(masked=True)) == 14

    @next_step(validate_apply_mask)
    def apply_mask():
        print("  - Apply data set mask")
        data = project_tab.get_active_data_set()
        mask = {_: _ % 2 == 1 for _ in range(0, data.get_num_points())}
        signals.emit(Signal.APPLY_DATA_SET_MASK, data=data, mask=mask)

    @next_step(apply_mask)
    def validate_rename_data_set():
        data = project_tab.get_active_data_set()
        assert data.get_label() == "Noisier data"

    @next_step(validate_rename_data_set)
    def rename_data_set():
        print("  - Rename data set")
        data = project_tab.get_active_data_set()
        signals.emit(Signal.RENAME_DATA_SET, label="Noisier data", data=data)

    @next_step(rename_data_set)
    def validate_select_data_set():
        data = project_tab.get_active_data_set()
        assert data.get_label() == "Noisy data"

    @next_step(validate_select_data_set)
    def select_data_set():
        print("  - Select data set")
        data = project_tab.get_active_data_set()
        signals.emit(Signal.SELECT_DATA_SET, data=data)

    @next_step(select_data_set)
    def validate_modify_path():
        data = project_tab.get_active_data_set()
        assert data.get_path() == "A path"

    @next_step(validate_modify_path)
    def modify_path():
        print("  - Modify data set path")
        data = project_tab.get_active_data_set()
        signals.emit(Signal.MODIFY_DATA_SET_PATH, path="A path", data=data)

    @next_step(modify_path)
    def validate_select_next_data_set():
        data = project_tab.get_active_data_set()
        assert data.get_label() == "Noisy data"

    @next_step(validate_select_next_data_set)
    def select_next_data_set():
        print("  - Select next data set")
        STATE.keybinding_handler.perform_action(
            Action.NEXT_PRIMARY_RESULT,
            Context.DATA_SETS_TAB,
            STATE.get_active_project(),
            STATE.get_active_project_tab(),
        )

    @next_step(select_next_data_set)
    def validate_average_data_sets():
        data = project_tab.get_active_data_set()
        assert data.get_label() == "Average"
        assert len(project.get_data_sets()) == 3
        signals.emit(Signal.DELETE_DATA_SET, data=data)

    @next_step(validate_average_data_sets)
    def average_data_sets_3():
        STATE.active_modal_window_object.accept()

    @next_step(average_data_sets_3)
    def average_data_sets_2():
        assert STATE.active_modal_window_object is not None
        row: int
        for row in dpg.get_item_children(
            STATE.active_modal_window_object.dataset_table,
            slot=1,
        ):
            dpg.set_value(dpg.get_item_children(row, slot=1)[0], True)
        STATE.active_modal_window_object.update_preview([])

    @next_step(average_data_sets_2)
    def average_data_sets_1():
        print("  - Average data sets")
        signals.emit(Signal.SELECT_DATA_SETS_TO_AVERAGE)

    STATE.keybinding_handler.perform_action(
        Action.SELECT_DATA_SETS_TAB,
        Context.PROJECT,
        STATE.get_active_project(),
        STATE.get_active_project_tab(),
    )
    print("\n- Data sets")
    Timer(1.0, average_data_sets_1).start()


def test_project():
    project: Optional[Project]
    project_tab: Optional[ProjectTab]
    data_sets: List[DataSet]
    path: str

    # TODO: Implement, if possible
    # print("  - Modify notes")
    @next_step(test_data_sets)
    def validate_rename():
        project = STATE.get_active_project()
        project_tab = STATE.get_active_project_tab()
        assert (
            project.get_label()
            == dpg.get_item_label(project_tab.tab)
            == "New project label"
        )

    @next_step(validate_rename)
    def rename():
        print("  - Rename")
        signals.emit(Signal.RENAME_PROJECT, label="New project label")

    @next_step(rename)
    def validate_load():
        project = STATE.get_active_project()
        project_tab = STATE.get_active_project_tab()
        assert (
            project.get_label()
            == dpg.get_item_label(project_tab.tab)
            == "Example project - Version 4"
        )
        assert len(project.get_data_sets()) == 2
        assert len(project.get_all_tests()) == 2
        assert len(project.get_all_drts()) == 2
        assert len(project.get_all_fits()) == 2
        assert len(project.get_simulations()) == 2

    @next_step(validate_load)
    def load():
        print("  - Load")
        path: str = join(getcwd(), "example-project-v4.json")
        assert exists(path), path
        signals.emit(Signal.LOAD_PROJECT_FILES, paths=[path])

    @next_step(load)
    def validate_close():
        project_tab = STATE.get_active_project_tab()
        assert project_tab is None

    @next_step(validate_close)
    def close():
        print("  - Close")
        signals.emit(Signal.CLOSE_PROJECT, force=True)

    @next_step(close)
    def validate_load_data():
        project = STATE.get_active_project()
        data_sets = project.get_data_sets()
        assert len(data_sets) == 6
        assert len(project.get_all_tests()) == 6
        assert len(project.get_all_fits()) == 6
        assert data_sets[4].get_label() == "Test", data_sets[4].get_label()
        assert data_sets[5].get_label() == "data-2", data_sets[5].get_label()

    @next_step(validate_load_data)
    def load_data():
        print("  - Load data")
        signals.emit(
            Signal.LOAD_DATA_SET_FILES,
            paths=[
                join(getcwd(), "data-1.idf"),
                join(getcwd(), "data-2.csv"),
            ],
        )

    def validate_merge():
        project = STATE.get_active_project()
        project_tab = STATE.get_active_project_tab()
        assert (
            project.get_label()
            == dpg.get_item_label(project_tab.tab)
            == "Merged project"
        )
        assert len(project.get_data_sets()) == 4
        assert len(project.get_all_tests()) == 4
        assert len(project.get_all_fits()) == 4
        load_data()

    @next_step(validate_merge)
    def merge():
        print("  - Merge")
        path = join(getcwd(), "example-project-v3.json")
        assert exists(path), path
        signals.emit(Signal.LOAD_PROJECT_FILES, paths=[path, path], merge=True)

    print("\n- Project")
    Timer(1.0, merge).start()


def test_overlay():
    @next_step(test_project)
    def progress_bar():
        print("  - Progress bar")
        i: int
        num: int = 5
        for i in range(0, num):
            signals.emit(
                Signal.SHOW_BUSY_MESSAGE,
                message=f"Progress {i + 1}/{num}",
                progress=i / num,
            )
            sleep(0.2)
        signals.emit(Signal.HIDE_BUSY_MESSAGE)

    @next_step(progress_bar)
    def message():
        print("  - Message only")
        signals.emit(Signal.SHOW_BUSY_MESSAGE, message="Just a message")

    print("\n- Overlay")
    Timer(1.0, message).start()


def run_tests():
    try:
        assert len(STATE.projects) == 0
    except AssertionError:
        message: str = "Detected open projects! Try running the tests again once all open projects have been closed."
        signals.emit(
            Signal.SHOW_ERROR_MESSAGE,
            traceback=format_exc(),
            message=message,
        )
        print(message)
        return
    print("\nRunning GUI tests...")
    project: Optional[Project] = STATE.get_active_project()
    assert project is None
    global START_TIME
    START_TIME = time()
    test_overlay()


def setup_tests():
    dpg.set_frame_callback(60, run_tests)
