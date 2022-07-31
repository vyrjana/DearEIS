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
from os.path import exists, join
from threading import Timer
from time import sleep, time
from traceback import format_exc
from typing import Dict, List, Optional
import dearpygui.dearpygui as dpg
import deareis.signals as signals
from deareis.signals import Signal
from deareis.state import STATE
from deareis.enums import (
    Action,
    Context,
    Method,
    Mode,
    PlotType,
    Test,
    Weight,
)
from deareis.data import (
    DataSet,
    FitResult,
    FitSettings,
    Project,
    SimulationResult,
    SimulationSettings,
    TestResult,
    TestSettings,
    PlotSettings,
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
# - Test subtracting impedance to see if plots, etc. are updated
# - Test undoing impedance subtraction after KK tests and/or fits have been performed


START_TIME: float = 0.0


def finish_tests():
    signals.emit(Signal.CLOSE_PROJECT, force=True)
    print(f"\nFinished in {time() - START_TIME:.2f} s")
    t: Timer = Timer(1.0, dpg.stop_dearpygui)
    t.start()


def test_undo_redo():
    project: Optional[Project] = STATE.get_active_project()
    project_tab: Optional[ProjectTab] = STATE.get_active_project_tab()

    def validate_redo():
        assert project.get_label() == "New project label"
        data_sets: List[DataSet] = project.get_data_sets()
        assert len(data_sets) == 1
        assert data_sets[0].get_label() == "Noisier data"
        assert sum(data_sets[0].get_mask().values()) == 14
        tests: Dict[str, List[TestResult]] = project.get_all_tests()
        assert len(tests) == 1
        assert sum(map(len, tests.values())) == 2
        fits: Dict[str, List[FitResult]] = project.get_all_fits()
        assert len(fits) == 1
        assert sum(map(len, fits.values())) == 2
        sims: List[SimulationResult] = project.get_simulations()
        assert len(sims) == 1
        plots: List[PlotSettings] = project.get_plots()
        assert len(plots) == 3
        assert plots[0].get_label() == "Ideal"
        assert plots[1].get_label() == "Noisy"
        assert plots[2].get_label() == "Test plot"
        finish_tests()

    def redo():
        print("  - Redo")
        signals.emit(Signal.REDO_PROJECT_ACTION)
        t: Timer = Timer(
            1.0,
            redo
            if STATE.get_next_project_state_snapshot(project) is not None
            else validate_redo,
        )
        t.start()

    def validate_undo():
        assert project.get_label() == "Example project - Version 3"
        data_sets: List[DataSet] = project.get_data_sets()
        assert len(data_sets) == 2
        assert data_sets[0].get_label() == "Ideal data"
        assert not any(data_sets[0].get_mask().values())
        assert data_sets[1].get_label() == "Noisy data"
        assert not any(data_sets[1].get_mask().values())
        tests: Dict[str, List[TestResult]] = project.get_all_tests()
        assert len(tests) == 2
        assert sum(map(len, tests.values())) == 2
        fits: Dict[str, List[FitResult]] = project.get_all_fits()
        assert len(fits) == 2
        assert sum(map(len, fits.values())) == 2
        sims: List[SimulationResult] = project.get_simulations()
        assert len(sims) == 2
        plots: List[PlotSettings] = project.get_plots()
        assert len(plots) == 3
        assert plots[0].get_label() == "Appearance template"
        assert plots[1].get_label() == "Ideal"
        assert plots[2].get_label() == "Noisy"
        redo()

    def undo():
        print("  - Undo")
        signals.emit(Signal.UNDO_PROJECT_ACTION)
        t: Timer = Timer(
            1.0,
            undo
            if STATE.get_previous_project_state_snapshot(project) is not None
            else validate_undo,
        )
        t.start()

    print("\n- Undo/redo")
    assert STATE.is_project_dirty(project) is True
    undo()


def test_plotting():
    project: Optional[Project] = STATE.get_active_project()
    project_tab: Optional[ProjectTab] = STATE.get_active_project_tab()

    def validate_unselect_all():
        assert len(project_tab.get_active_plot().series_order) == 0
        test_undo_redo()

    def unselect_all():
        print("  - Unselect all")
        signals.emit(
            Signal.TOGGLE_PLOT_SERIES,
            enabled=False,
            settings=project_tab.get_active_plot(),
            **dpg.get_item_user_data(project_tab.plotting_tab.select_all_button),
        )
        t: Timer = Timer(1.0, validate_unselect_all)
        t.start()

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
        unselect_all()

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
        t: Timer = Timer(1.0, validate_reorder_series)
        t.start()

    def validate_select_plot_type():
        assert project_tab.get_active_plot().get_type() == PlotType.BODE_PHASE
        assert dpg.get_value(project_tab.plotting_tab.type_combo) == "Bode - phase"
        reorder_series()

    def select_plot_type():
        print("  - Select plot type")
        settings: PlotSettings = project_tab.get_active_plot()
        signals.emit(
            Signal.SELECT_PLOT_TYPE, settings=settings, plot_type=PlotType.BODE_PHASE
        )
        t: Timer = Timer(1.0, validate_select_plot_type)
        t.start()

    def validate_select_all():
        assert len(project_tab.get_active_plot().series_order) == 6
        select_plot_type()

    def select_all():
        print("  - Select all")
        signals.emit(
            Signal.TOGGLE_PLOT_SERIES,
            enabled=True,
            settings=project_tab.get_active_plot(),
            **dpg.get_item_user_data(project_tab.plotting_tab.select_all_button),
        )
        t: Timer = Timer(1.0, validate_select_all)
        t.start()

    def validate_rename_plot():
        assert len(project.get_plots()) == 3
        assert project_tab.get_active_plot().get_label() == "Test plot"
        assert dpg.get_value(project_tab.plotting_tab.label_input) == "Test plot"
        assert (
            dpg.get_item_label(
                project_tab.plotting_tab.plot_types[PlotType.NYQUIST]._plot
            )
            == "Test plot"
        )
        select_all()

    def rename_plot():
        print("  - Rename plot")
        settings: PlotSettings = project_tab.get_active_plot()
        signals.emit(Signal.RENAME_PLOT_SETTINGS, settings=settings, label="Test plot")
        t: Timer = Timer(1.0, validate_rename_plot)
        t.start()

    def validate_new_plot():
        plot: PlotSettings = project_tab.get_active_plot()
        assert len(project.get_plots()) == 3
        assert plot.get_label() == "Plot"
        assert len(plot.series_order) == 0
        assert dpg.get_value(project_tab.plotting_tab.label_input) == "Plot"
        assert (
            dpg.get_item_label(
                project_tab.plotting_tab.plot_types[PlotType.NYQUIST]._plot
            )
            == "Plot"
        )
        rename_plot()

    def new_plot():
        print("  - New plot")
        signals.emit(Signal.NEW_PLOT_SETTINGS)
        t: Timer = Timer(1.0, validate_new_plot)
        t.start()

    def validate_delete_plot():
        assert len(project.get_plots()) == 2
        assert project_tab.get_active_plot().get_label() == "Ideal"
        new_plot()

    def delete_plot():
        print("  - Delete plot")
        settings: PlotSettings = project_tab.get_active_plot()
        signals.emit(Signal.DELETE_PLOT_SETTINGS, settings=settings)
        t: Timer = Timer(1.0, validate_delete_plot)
        t.start()

    STATE.keybinding_handler.perform_action(
        Action.SELECT_PLOTTING_TAB,
        Context.PROJECT,
        STATE.get_active_project(),
        STATE.get_active_project_tab(),
    )
    print("\n- Plotting")
    t: Timer = Timer(1.0, delete_plot)
    t.start()


def test_simulation():
    project: Optional[Project] = STATE.get_active_project()
    project_tab: Optional[ProjectTab] = STATE.get_active_project_tab()

    def validate_select_previous_data_set():
        assert project_tab.get_active_data_set() is not None
        test_plotting()

    def select_previous_data_set():
        print("  - Select previous data set")
        STATE.keybinding_handler.perform_action(
            Action.PREVIOUS_PRIMARY_RESULT,
            Context.SIMULATION_TAB,
            STATE.get_active_project(),
            STATE.get_active_project_tab(),
        )
        t: Timer = Timer(1.0, validate_select_previous_data_set)
        t.start()

    def validate_perform_simulation():
        assert len(project.get_simulations()) == 1
        assert project_tab.get_active_simulation() is not None
        select_previous_data_set()

    def perform_simulation():
        print("  - Perform simulation")
        settings: SimulationSettings = project_tab.simulation_tab.get_settings()
        signals.emit(Signal.PERFORM_SIMULATION, settings=settings)
        t: Timer = Timer(1.0, validate_perform_simulation)
        t.start()

    def validate_delete_result():
        assert len(project.get_simulations()) == 0
        assert project_tab.get_active_simulation() is None
        perform_simulation()

    def delete_result():
        print("  - Delete result")
        simulation: Optional[SimulationResult] = project_tab.get_active_simulation()
        signals.emit(Signal.DELETE_SIMULATION_RESULT, simulation=simulation)
        sleep(1.0)
        simulation = project_tab.get_active_simulation()
        signals.emit(Signal.DELETE_SIMULATION_RESULT, simulation=simulation)
        t: Timer = Timer(1.0, validate_delete_result)
        t.start()

    def validate_apply_settings():
        assert dpg.get_value(project_tab.simulation_tab.cdc_input) == "[R(RC)(RW)]"
        assert isclose(
            dpg.get_value(project_tab.simulation_tab.max_freq_input), 1e5, rel_tol=1e-6
        ), dpg.get_value(project_tab.simulation_tab.max_freq_input)
        assert isclose(
            dpg.get_value(project_tab.simulation_tab.min_freq_input), 1e-2, rel_tol=1e-6
        ), dpg.get_value(project_tab.simulation_tab.min_freq_input)
        assert dpg.get_value(project_tab.simulation_tab.per_decade_input) == 1
        delete_result()

    def apply_settings():
        print("  - Apply settings")
        simulation: Optional[SimulationResult] = project_tab.get_active_simulation()
        signals.emit(Signal.APPLY_SIMULATION_SETTINGS, settings=simulation.settings)
        t: Timer = Timer(1.0, validate_apply_settings)
        t.start()

    STATE.keybinding_handler.perform_action(
        Action.SELECT_SIMULATION_TAB,
        Context.PROJECT,
        STATE.get_active_project(),
        STATE.get_active_project_tab(),
    )
    print("\n- Simulation")
    t: Timer = Timer(1.0, apply_settings)
    t.start()


def test_fitting():
    project: Optional[Project] = STATE.get_active_project()
    project_tab: Optional[ProjectTab] = STATE.get_active_project_tab()

    def validate_select_next_result():
        data: Optional[DataSet] = project_tab.get_active_data_set()
        assert data is not None
        fits: List[FitResult] = project.get_fits(data)
        assert len(fits) == 2
        assert project_tab.get_active_fit() == fits[1]
        test_simulation()

    def select_next_result():
        print("  - Select next result")
        STATE.keybinding_handler.perform_action(
            Action.NEXT_SECONDARY_RESULT,
            Context.FITTING_TAB,
            STATE.get_active_project(),
            STATE.get_active_project_tab(),
        )
        t: Timer = Timer(1.0, validate_select_next_result)
        t.start()

    def validate_perform_fit():
        data: Optional[DataSet] = project_tab.get_active_data_set()
        assert data is not None
        assert project_tab.get_active_fit() is not None
        assert len(project.get_fits(data)) == 2
        select_next_result()

    def perform_fit(*args, **kwargs):
        print("  - Perform fit")
        data: Optional[DataSet] = project_tab.get_active_data_set()
        settings: FitSettings = FitSettings(
            "[(RC)]",
            Method.LEAST_SQUARES,
            Weight.BOUKAMP,
            1000,
        )
        signals.emit(Signal.PERFORM_FIT, data=data, settings=settings)
        sleep(1.0)
        settings = FitSettings(
            "[R(RC)(RW)]",
            Method.LEAST_SQUARES,
            Weight.BOUKAMP,
            1000,
        )
        signals.emit(Signal.PERFORM_FIT, data=data, settings=settings)
        t: Timer = Timer(1.0, validate_perform_fit)
        t.start()

    def validate_delete_result():
        data: Optional[DataSet] = project_tab.get_active_data_set()
        assert data is not None
        assert project_tab.get_active_fit() is None
        assert len(project.get_fits(data)) == 0
        perform_fit()

    def delete_result(*args, **kwargs):
        print("  - Delete settings")
        data: Optional[DataSet] = project_tab.get_active_data_set()
        fit: Optional[FitResult] = project_tab.get_active_fit()
        signals.emit(Signal.DELETE_FIT_RESULT, data=data, fit=fit)
        t: Timer = Timer(1.0, validate_delete_result)
        t.start()

    def validate_apply_settings():
        assert dpg.get_value(project_tab.fitting_tab.cdc_input) == "[R(RC)(RW)]"
        assert dpg.get_value(project_tab.fitting_tab.method_combo) == "Auto"
        assert dpg.get_value(project_tab.fitting_tab.weight_combo) == "Auto"
        assert dpg.get_value(project_tab.fitting_tab.max_nfev_input) == 1000
        delete_result()

    def apply_settings():
        print("  - Apply settings")
        fit: Optional[FitResult] = project_tab.get_active_fit()
        signals.emit(Signal.APPLY_FIT_SETTINGS, settings=fit.settings)
        t: Timer = Timer(1.0, validate_apply_settings)
        t.start()

    STATE.keybinding_handler.perform_action(
        Action.SELECT_FITTING_TAB,
        Context.PROJECT,
        STATE.get_active_project(),
        STATE.get_active_project_tab(),
    )
    print("\n- Fitting")
    t: Timer = Timer(1.0, apply_settings)
    t.start()


def test_kramers_kronig():
    project: Optional[Project] = STATE.get_active_project()
    project_tab: Optional[ProjectTab] = STATE.get_active_project_tab()

    def validate_apply_settings():
        assert dpg.get_value(project_tab.kramers_kronig_tab.test_combo) == "Complex"
        assert dpg.get_value(project_tab.kramers_kronig_tab.mode_combo) == "Auto"
        assert dpg.get_value(project_tab.kramers_kronig_tab.num_RC_slider) == 15
        assert dpg.get_value(project_tab.kramers_kronig_tab.add_cap_checkbox) is True
        assert dpg.get_value(project_tab.kramers_kronig_tab.add_ind_checkbox) is True
        assert isclose(
            dpg.get_value(project_tab.kramers_kronig_tab.mu_crit_slider),
            0.85,
            rel_tol=1e-6,
        )
        assert dpg.get_value(project_tab.kramers_kronig_tab.method_combo) == "Auto"
        assert dpg.get_value(project_tab.kramers_kronig_tab.max_nfev_input) == 1000
        test_fitting()

    def apply_settings():
        print("  - Apply test settings")
        test = project_tab.get_active_test()
        signals.emit(Signal.APPLY_TEST_SETTINGS, settings=test.settings)
        t: Timer = Timer(1.0, validate_apply_settings)
        t.start()

    def validate_select_next_result():
        data: Optional[DataSet] = project_tab.get_active_data_set()
        assert data is not None
        tests: List[TestResult] = project.get_tests(data)
        assert project_tab.get_active_test() == tests[1]
        apply_settings()

    def select_next_result():
        print("  - Select next result")
        STATE.keybinding_handler.perform_action(
            Action.NEXT_SECONDARY_RESULT,
            Context.KRAMERS_KRONIG_TAB,
            STATE.get_active_project(),
            STATE.get_active_project_tab(),
        )
        t: Timer = Timer(1.0, validate_select_next_result)
        t.start()

    def validate_perform_test():
        data: Optional[DataSet] = project_tab.get_active_data_set()
        assert len(project.get_tests(data)) == 2
        select_next_result()

    def perform_test():
        print("  - Perform test")
        data: Optional[DataSet] = project_tab.get_active_data_set()
        settings: TestSettings = TestSettings(
            Test.COMPLEX,
            Mode.AUTO,
            data.get_num_points(),
            0.85,
            True,
            True,
            Method.AUTO,
            1000,
        )
        signals.emit(Signal.PERFORM_TEST, data=data, settings=settings)
        sleep(1.0)
        settings = TestSettings(
            Test.COMPLEX,
            Mode.AUTO,
            int(data.get_num_points() / 3),
            0.85,
            True,
            True,
            Method.AUTO,
            1000,
        )
        signals.emit(Signal.PERFORM_TEST, data=data, settings=settings)
        t: Timer = Timer(1.0, validate_perform_test)
        t.start()

    def validate_delete_result():
        data: Optional[DataSet] = project_tab.get_active_data_set()
        assert len(project.get_tests(data)) == 0
        perform_test()

    def delete_result():
        print("  - Delete test result")
        data: Optional[DataSet] = project_tab.get_active_data_set()
        test: Optional[TestResult] = project_tab.get_active_test()
        signals.emit(Signal.DELETE_TEST_RESULT, data=data, test=test)
        t: Timer = Timer(1.0, validate_delete_result)
        t.start()

    STATE.keybinding_handler.perform_action(
        Action.SELECT_KRAMERS_KRONIG_TAB,
        Context.PROJECT,
        STATE.get_active_project(),
        STATE.get_active_project_tab(),
    )
    print("\n- Kramers-Kronig")
    t: Timer = Timer(1.0, delete_result)
    t.start()


def test_data_sets():
    project: Optional[Project] = STATE.get_active_project()
    project_tab: Optional[ProjectTab] = STATE.get_active_project_tab()

    def validate_delete_data_set():
        data: Optional[DataSet] = project_tab.get_active_data_set()
        assert len(project.get_data_sets()) == 1
        assert len(project.get_all_tests()) == 1
        assert len(project.get_all_fits()) == 1
        assert data.get_label() == "Noisier data"
        test_kramers_kronig()

    def delete_data_set_2():
        data: Optional[DataSet] = project_tab.get_active_data_set()
        signals.emit(Signal.DELETE_DATA_SET, data=data)
        t: Timer = Timer(1.0, validate_delete_data_set)
        t.start()

    def delete_data_set_1():
        print("  - Delete data set")
        STATE.keybinding_handler.perform_action(
            Action.NEXT_PRIMARY_RESULT,
            Context.DATA_SETS_TAB,
            STATE.get_active_project(),
            STATE.get_active_project_tab(),
        )
        t: Timer = Timer(1.0, delete_data_set_2)
        t.start()

    def validate_apply_mask():
        data: Optional[DataSet] = project_tab.get_active_data_set()
        assert len(data.get_impedance(masked=None)) == 29
        assert len(data.get_impedance(masked=False)) == len(data.get_impedance()) == 15
        assert len(data.get_impedance(masked=True)) == 14
        delete_data_set_1()

    def apply_mask():
        print("  - Apply data set mask")
        data: Optional[DataSet] = project_tab.get_active_data_set()
        mask: Dict[int, bool] = {_: _ % 2 == 1 for _ in range(0, data.get_num_points())}
        signals.emit(Signal.APPLY_DATA_SET_MASK, data=data, mask=mask)
        t: Timer = Timer(1.0, validate_apply_mask)
        t.start()

    def validate_rename_data_set():
        data: Optional[DataSet] = project_tab.get_active_data_set()
        assert data.get_label() == "Noisier data"
        apply_mask()

    def rename_data_set():
        print("  - Rename data set")
        data: Optional[DataSet] = project_tab.get_active_data_set()
        signals.emit(Signal.RENAME_DATA_SET, label="Noisier data", data=data)
        t: Timer = Timer(1.0, validate_rename_data_set)
        t.start()

    def validate_select_data_set():
        data: Optional[DataSet] = project_tab.get_active_data_set()
        assert data.get_label() == "Noisy data"
        rename_data_set()

    def select_data_set():
        print("  - Select data set")
        data: Optional[DataSet] = project_tab.get_active_data_set()
        signals.emit(Signal.SELECT_DATA_SET, data=data)
        t: Timer = Timer(1.0, validate_select_data_set)
        t.start()

    def validate_modify_path():
        data: Optional[DataSet] = project_tab.get_active_data_set()
        assert data.get_path() == "A path"
        select_data_set()

    def modify_path():
        print("  - Modify data set path")
        data: Optional[DataSet] = project_tab.get_active_data_set()
        signals.emit(Signal.MODIFY_DATA_SET_PATH, path="A path", data=data)
        t: Timer = Timer(1.0, validate_modify_path)
        t.start()

    def validate_select_next_data_set():
        data: Optional[DataSet] = project_tab.get_active_data_set()
        assert data.get_label() == "Noisy data"
        modify_path()

    def select_next_data_set():
        print("  - Select next data set")
        STATE.keybinding_handler.perform_action(
            Action.NEXT_PRIMARY_RESULT,
            Context.DATA_SETS_TAB,
            STATE.get_active_project(),
            STATE.get_active_project_tab(),
        )
        t: Timer = Timer(1.0, validate_select_next_data_set)
        t.start()

    STATE.keybinding_handler.perform_action(
        Action.SELECT_DATA_SETS_TAB,
        Context.PROJECT,
        STATE.get_active_project(),
        STATE.get_active_project_tab(),
    )
    print("\n- Data sets")
    t: Timer = Timer(1.0, select_next_data_set)
    t.start()


def test_project():
    # TODO: Implement, if possible
    # print("  - Modify notes")
    def validate_rename():
        project: Optional[Project] = STATE.get_active_project()
        project_tab: Optional[ProjectTab] = STATE.get_active_project_tab()
        assert (
            project.get_label()
            == dpg.get_item_label(project_tab.tab)
            == "New project label"
        )
        test_data_sets()

    def rename():
        print("  - Rename")
        signals.emit(Signal.RENAME_PROJECT, label="New project label")
        t: Timer = Timer(1.0, validate_rename)
        t.start()

    def validate_load():
        project: Optional[Project] = STATE.get_active_project()
        project_tab: Optional[ProjectTab] = STATE.get_active_project_tab()
        assert (
            project.get_label()
            == dpg.get_item_label(project_tab.tab)
            == "Example project - Version 3"
        )
        assert len(project.get_data_sets()) == 2
        assert len(project.get_all_tests()) == 2
        assert len(project.get_all_fits()) == 2
        rename()

    def load():
        print("  - Load")
        path: str = join(getcwd(), "example-project-v3.json")
        assert exists(path), path
        signals.emit(Signal.LOAD_PROJECT_FILES, paths=[path])
        t: Timer = Timer(1.0, validate_load)
        t.start()

    def validate_close():
        project_tab: Optional[ProjectTab] = STATE.get_active_project_tab()
        assert project_tab is None
        load()

    def close():
        print("  - Close")
        signals.emit(Signal.CLOSE_PROJECT, force=True)
        t: Timer = Timer(1.0, validate_close)
        t.start()

    def validate_load_data():
        project: Optional[Project] = STATE.get_active_project()
        data_sets: List[DataSet] = project.get_data_sets()
        assert len(data_sets) == 6
        assert len(project.get_all_tests()) == 6
        assert len(project.get_all_fits()) == 6
        assert data_sets[4].get_label() == "Test", data_sets[4].get_label()
        assert data_sets[5].get_label() == "data-2", data_sets[5].get_label()
        close()

    def load_data():
        print("  - Load data")
        signals.emit(
            Signal.LOAD_DATA_SET_FILES,
            paths=[
                join(getcwd(), "data-1.idf"),
                join(getcwd(), "data-2.csv"),
            ],
        )
        t: Timer = Timer(1.0, validate_load_data)
        t.start()

    def validate_merge():
        project: Optional[Project] = STATE.get_active_project()
        project_tab: Optional[ProjectTab] = STATE.get_active_project_tab()
        assert (
            project.get_label()
            == dpg.get_item_label(project_tab.tab)
            == "Merged project"
        )
        assert len(project.get_data_sets()) == 4
        assert len(project.get_all_tests()) == 4
        assert len(project.get_all_fits()) == 4
        load_data()

    def merge():
        print("  - Merge")
        path: str = join(getcwd(), "example-project-v3.json")
        assert exists(path), path
        signals.emit(Signal.LOAD_PROJECT_FILES, paths=[path, path], merge=True)
        t: Timer = Timer(1.0, validate_merge)
        t.start()

    print("\n- Project")
    t: Timer = Timer(1.0, merge)
    t.start()


def test_overlay():
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
        t: Timer = Timer(1.0, test_project)
        t.start()

    def message():
        print("  - Message only")
        signals.emit(Signal.SHOW_BUSY_MESSAGE, message="Just a message")
        t: Timer = Timer(1.0, progress_bar)
        t.start()

    print("\n- Overlay")
    t: Timer = Timer(1.0, message)
    t.start()


def run_tests():
    try:
        assert len(STATE.projects) == 0
    except AssertionError:
        signals.emit(
            Signal.SHOW_ERROR_MESSAGE,
            traceback=format_exc(),
            message="Detected open projects! Try running the tests again once all open projects have been closed.",
        )
        return
    print("\nRunning GUI tests...")
    project: Optional[Project] = STATE.get_active_project()
    assert project is None
    global START_TIME
    START_TIME = time()
    test_overlay()


def setup_tests():
    dpg.set_frame_callback(60, run_tests)
