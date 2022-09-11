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

from traceback import format_exc
from typing import List, Optional, Set
import dearpygui.dearpygui as dpg
import deareis.signals as signals
from deareis.signals import Signal
from .keybinding import Keybinding, dpg_to_string
from deareis.enums import Action, Context, action_contexts
from deareis.data import DataSet, TestResult, FitResult, SimulationResult


def is_shift_down() -> bool:
    return dpg.is_key_down(dpg.mvKey_Shift) or dpg.is_key_down(dpg.mvKey_RShift)


def is_control_down() -> bool:
    return (
        dpg.is_key_down(dpg.mvKey_Control)
        or dpg.is_key_down(dpg.mvKey_LControl)
        or dpg.is_key_down(dpg.mvKey_RControl)
    )


def is_alt_down() -> bool:
    return dpg.is_key_down(dpg.mvKey_Alt)


class KeybindingHandler:
    def __init__(self, keybindings: List[Keybinding], state):
        self.block_events: bool = False
        self.state = state
        self.keybindings: List[Keybinding] = keybindings
        if not keybindings:
            return
        self.key_handler: int = -1
        self.register(self.keybindings)

    def register(self, keybindings: List[Keybinding]):
        self.keybindings = keybindings
        registered_keys: Set[int] = set()
        if self.key_handler > 0 and dpg.does_item_exist(self.key_handler):
            dpg.delete_item(self.key_handler)
        self.key_handler = dpg.generate_uuid()
        with dpg.handler_registry(tag=self.key_handler):
            kb: Keybinding
            for kb in keybindings:
                if kb.key in registered_keys:
                    continue
                registered_keys.add(kb.key)
                dpg.add_key_release_handler(
                    key=kb.key,
                    callback=lambda s, a, u: self.process(a),
                )

    def block(self):
        self.block_events = True

    def unblock(self):
        self.block_events = False

    def process(self, key: int):
        if self.block_events:
            # TODO: Remove this workaround when no longer required by the file dialog window?
            window: Optional[int] = self.state.get_active_modal_window()
            if (
                window is None
                or not dpg.does_item_exist(window)
                or not dpg.is_item_shown(window)
            ):
                signals.emit(Signal.UNBLOCK_KEYBINDINGS)
            else:
                return
        filtered_keybindings: List[Keybinding] = list(
            filter(lambda _: key in _, self.keybindings)
        )
        if not filtered_keybindings:
            return
        if is_alt_down():
            filtered_keybindings = list(
                filter(lambda _: _.mod_alt is True, filtered_keybindings)
            )
        else:
            filtered_keybindings = list(
                filter(lambda _: _.mod_alt is False, filtered_keybindings)
            )
        if not filtered_keybindings:
            return
        if is_control_down():
            filtered_keybindings = list(
                filter(lambda _: _.mod_ctrl is True, filtered_keybindings)
            )
        else:
            filtered_keybindings = list(
                filter(lambda _: _.mod_ctrl is False, filtered_keybindings)
            )
        if not filtered_keybindings:
            return
        if is_shift_down():
            filtered_keybindings = list(
                filter(lambda _: _.mod_shift is True, filtered_keybindings)
            )
        else:
            filtered_keybindings = list(
                filter(lambda _: _.mod_shift is False, filtered_keybindings)
            )
        if not filtered_keybindings:
            return
        project = self.state.get_active_project()  # Optional[Project]
        project_tab = self.state.get_active_project_tab()  # Optional[ProjectTab]
        context: Context
        if project is not None and project_tab is not None:
            context = project_tab.get_active_context()
            filtered_keybindings = list(
                filter(
                    lambda _: context in action_contexts[_.action]
                    or Context.PROJECT in action_contexts[_.action]
                    or Context.PROGRAM in action_contexts[_.action],
                    filtered_keybindings,
                )
            )
        else:
            filtered_keybindings = list(
                filter(
                    lambda _: Context.PROGRAM in action_contexts[_.action],
                    filtered_keybindings,
                )
            )
        if not filtered_keybindings:
            return
        context = (
            project_tab.get_active_context()
            if project_tab is not None
            else Context.PROGRAM
        )
        # Check for active input fields
        if project_tab is not None and project_tab.has_active_input(context):
            return
        try:
            self.validate_keybindings(filtered_keybindings)
            self.perform_action(
                filtered_keybindings[0].action,
                context,
                project,
                project_tab,
            )
        except Exception:
            signals.emit(Signal.SHOW_ERROR_MESSAGE, traceback=format_exc())

    def validate_keybindings(self, keybindings: List[Keybinding]):
        assert len(set(list(map(str, keybindings)))) == 1, (
            "The same keybinding has been applied to multiple actions:\n- "
            + "\n- ".join(list(map(str, keybindings)))
        )

    def perform_action(
        self,
        action: Action,
        context: Context,
        project,  # Optional["Project"]
        project_tab,  # Optional["ProjectTab"]
    ):
        assert type(action) is Action, action
        assert type(context) is Context, context
        # Program-level
        if action == Action.NEW_PROJECT:
            signals.emit(Signal.NEW_PROJECT)
        elif action == Action.LOAD_PROJECT:
            signals.emit(Signal.SELECT_PROJECT_FILES)
        elif action == Action.EXIT:
            dpg.stop_dearpygui()
        elif action == Action.NEXT_PROGRAM_TAB:
            self.state.program_window.select_next_tab()
        elif action == Action.PREVIOUS_PROGRAM_TAB:
            self.state.program_window.select_previous_tab()
        elif action == Action.SELECT_HOME_TAB:
            self.state.program_window.select_home_tab()
        elif action == Action.SHOW_HELP_ABOUT:
            signals.emit(Signal.SHOW_HELP_ABOUT)
        elif action == Action.SHOW_HELP_LICENSES:
            signals.emit(Signal.SHOW_HELP_LICENSES)
        elif action == Action.SHOW_SETTINGS_APPEARANCE:
            signals.emit(Signal.SHOW_SETTINGS_APPEARANCE)
        elif action == Action.SHOW_SETTINGS_DEFAULTS:
            signals.emit(Signal.SHOW_SETTINGS_DEFAULTS)
        elif action == Action.SHOW_SETTINGS_KEYBINDINGS:
            signals.emit(Signal.SHOW_SETTINGS_KEYBINDINGS)
        elif action == Action.SHOW_COMMAND_PALETTE:
            signals.emit(Signal.SHOW_COMMAND_PALETTE)
        elif action == Action.SHOW_CHANGELOG:
            signals.emit(Signal.SHOW_CHANGELOG)
        elif action == Action.CHECK_UPDATES:
            signals.emit(Signal.CHECK_UPDATES)
        elif project is not None:
            assert project is not None
            assert project_tab is not None
            # Project-level
            test: Optional[TestResult]
            fit: Optional[FitResult]
            if action == Action.SAVE_PROJECT:
                signals.emit(Signal.SAVE_PROJECT)
            elif action == Action.SAVE_PROJECT_AS:
                signals.emit(Signal.SAVE_PROJECT_AS)
            elif action == Action.CLOSE_PROJECT:
                signals.emit(Signal.CLOSE_PROJECT)
            elif action == Action.UNDO:
                if not (
                    context == Context.OVERVIEW_TAB
                    and dpg.is_item_focused(project_tab.overview_tab.notes_input)
                ):
                    signals.emit(Signal.UNDO_PROJECT_ACTION)
            elif action == Action.REDO:
                signals.emit(Signal.REDO_PROJECT_ACTION)
            elif action == Action.NEXT_PROJECT_TAB:
                project_tab.select_next_tab()
            elif action == Action.PREVIOUS_PROJECT_TAB:
                project_tab.select_previous_tab()
            elif action == Action.SELECT_OVERVIEW_TAB:
                project_tab.select_overview_tab()
            elif action == Action.SELECT_DATA_SETS_TAB:
                project_tab.select_data_sets_tab()
            elif action == Action.SELECT_KRAMERS_KRONIG_TAB:
                project_tab.select_kramers_kronig_tab()
            elif action == Action.SELECT_DRT_TAB:
                project_tab.select_drt_tab()
            elif action == Action.SELECT_FITTING_TAB:
                project_tab.select_fitting_tab()
            elif action == Action.SELECT_SIMULATION_TAB:
                project_tab.select_simulation_tab()
            elif action == Action.SELECT_PLOTTING_TAB:
                project_tab.select_plotting_tab()
            # Project-level: multiple tabs
            elif action == Action.PERFORM_ACTION:
                if context == Context.DATA_SETS_TAB:
                    signals.emit(Signal.SELECT_DATA_SET_FILES)
                elif context == Context.KRAMERS_KRONIG_TAB:
                    signals.emit(
                        Signal.PERFORM_TEST,
                        data=project_tab.get_active_data_set(),
                        settings=project_tab.get_test_settings(),
                    ),
                elif context == Context.DRT_TAB:
                    signals.emit(
                        Signal.PERFORM_DRT,
                        data=project_tab.get_active_data_set(),
                        settings=project_tab.get_drt_settings(),
                    )
                elif context == Context.FITTING_TAB:
                    signals.emit(
                        Signal.PERFORM_FIT,
                        data=project_tab.get_active_data_set(),
                        settings=project_tab.get_fit_settings(),
                    ),
                elif context == Context.SIMULATION_TAB:
                    signals.emit(
                        Signal.PERFORM_SIMULATION,
                        data=project_tab.get_active_data_set(),
                        settings=project_tab.get_simulation_settings(),
                    ),
                elif context == Context.PLOTTING_TAB:
                    signals.emit(Signal.NEW_PLOT_SETTINGS)
                # - Create plot
            elif action == Action.DELETE_RESULT:
                if context == Context.DATA_SETS_TAB:
                    signals.emit(
                        Signal.DELETE_DATA_SET,
                        data=project_tab.get_active_data_set(),
                    )
                elif context == Context.KRAMERS_KRONIG_TAB:
                    signals.emit(
                        Signal.DELETE_TEST_RESULT,
                        test=project_tab.get_active_test(),
                        data=project_tab.get_active_data_set(),
                    )
                elif context == Context.DRT_TAB:
                    signals.emit(
                        Signal.DELETE_DRT_RESULT,
                        drt=project_tab.get_active_drt(),
                        data=project_tab.get_active_data_set(),
                    )
                elif context == Context.FITTING_TAB:
                    signals.emit(
                        Signal.DELETE_FIT_RESULT,
                        fit=project_tab.get_active_fit(),
                        data=project_tab.get_active_data_set(),
                    )
                elif context == Context.SIMULATION_TAB:
                    signals.emit(
                        Signal.DELETE_SIMULATION_RESULT,
                        simulation=project_tab.get_active_simulation(),
                        data=project_tab.get_active_data_set(),
                    )
                elif context == Context.PLOTTING_TAB:
                    signals.emit(
                        Signal.DELETE_PLOT_SETTINGS,
                        settings=project_tab.get_active_plot(),
                    )
                # - Plot
            elif action == Action.NEXT_PRIMARY_RESULT:
                if (
                    context == Context.DATA_SETS_TAB
                    or context == Context.KRAMERS_KRONIG_TAB
                    or context == Context.DRT_TAB
                    or context == Context.FITTING_TAB
                ):
                    signals.emit(
                        Signal.SELECT_DATA_SET,
                        data=project_tab.get_next_data_set(context),
                    )
                elif context == Context.SIMULATION_TAB:
                    signals.emit(
                        Signal.SELECT_SIMULATION_RESULT,
                        simulation=project_tab.get_active_simulation(),
                        data=project_tab.get_next_simulation_data_set(),
                    )
                elif context == Context.PLOTTING_TAB:
                    signals.emit(
                        Signal.SELECT_PLOT_SETTINGS,
                        settings=project_tab.get_next_plot(),
                    )
                # - Plot
            elif action == Action.PREVIOUS_PRIMARY_RESULT:
                if (
                    context == Context.DATA_SETS_TAB
                    or context == Context.KRAMERS_KRONIG_TAB
                    or context == Context.DRT_TAB
                    or context == Context.FITTING_TAB
                ):
                    signals.emit(
                        Signal.SELECT_DATA_SET,
                        data=project_tab.get_previous_data_set(context),
                    )
                elif context == Context.SIMULATION_TAB:
                    signals.emit(
                        Signal.SELECT_SIMULATION_RESULT,
                        simulation=project_tab.get_active_simulation(),
                        data=project_tab.get_previous_simulation_data_set(),
                    )
                elif context == Context.PLOTTING_TAB:
                    signals.emit(
                        Signal.SELECT_PLOT_SETTINGS,
                        settings=project_tab.get_previous_plot(),
                    )
                # - Plot
            elif action == Action.NEXT_SECONDARY_RESULT:
                if context == Context.KRAMERS_KRONIG_TAB:
                    signals.emit(
                        Signal.SELECT_TEST_RESULT,
                        test=project_tab.get_next_test_result(),
                        data=project_tab.get_active_data_set(),
                    )
                elif context == Context.DRT_TAB:
                    signals.emit(
                        Signal.SELECT_DRT_RESULT,
                        drt=project_tab.get_next_drt_result(),
                        data=project_tab.get_active_data_set(),
                    )
                elif context == Context.FITTING_TAB:
                    signals.emit(
                        Signal.SELECT_FIT_RESULT,
                        fit=project_tab.get_next_fit_result(),
                        data=project_tab.get_active_data_set(),
                    )
                elif context == Context.SIMULATION_TAB:
                    signals.emit(
                        Signal.SELECT_SIMULATION_RESULT,
                        simulation=project_tab.get_next_simulation_result(),
                        data=project_tab.get_active_data_set(),
                    )
                elif context == Context.PLOTTING_TAB:
                    signals.emit(
                        Signal.SELECT_PLOT_TYPE,
                        settings=project_tab.get_active_plot(),
                        plot_type=project_tab.get_next_plot_type(),
                    )
                # - Plot type
            elif action == Action.PREVIOUS_SECONDARY_RESULT:
                if context == Context.KRAMERS_KRONIG_TAB:
                    signals.emit(
                        Signal.SELECT_TEST_RESULT,
                        test=project_tab.get_previous_test_result(),
                        data=project_tab.get_active_data_set(),
                    )
                elif context == Context.DRT_TAB:
                    signals.emit(
                        Signal.SELECT_DRT_RESULT,
                        drt=project_tab.get_previous_drt_result(),
                        data=project_tab.get_active_data_set(),
                    )
                elif context == Context.FITTING_TAB:
                    signals.emit(
                        Signal.SELECT_FIT_RESULT,
                        fit=project_tab.get_previous_fit_result(),
                        data=project_tab.get_active_data_set(),
                    )
                elif context == Context.SIMULATION_TAB:
                    signals.emit(
                        Signal.SELECT_SIMULATION_RESULT,
                        simulation=project_tab.get_previous_simulation_result(),
                        data=project_tab.get_active_data_set(),
                    )
                elif context == Context.PLOTTING_TAB:
                    signals.emit(
                        Signal.SELECT_PLOT_TYPE,
                        settings=project_tab.get_active_plot(),
                        plot_type=project_tab.get_previous_plot_type(),
                    )
                # - Plot type
            elif action == Action.APPLY_SETTINGS:
                if context == Context.KRAMERS_KRONIG_TAB:
                    test = project_tab.get_active_test()
                    signals.emit(
                        Signal.APPLY_TEST_SETTINGS,
                        settings=test.settings if test is not None else None,
                    )
                elif context == Context.DRT_TAB:
                    drt = project_tab.get_active_drt()
                    signals.emit(
                        Signal.APPLY_DRT_SETTINGS,
                        settings=drt.settings if drt is not None else None,
                    )
                elif context == Context.FITTING_TAB:
                    fit = project_tab.get_active_fit()
                    signals.emit(
                        Signal.APPLY_FIT_SETTINGS,
                        settings=fit.settings if fit is not None else None,
                    )
                elif context == Context.SIMULATION_TAB:
                    simulation: Optional[
                        SimulationResult
                    ] = project_tab.get_active_simulation()
                    signals.emit(
                        Signal.APPLY_SIMULATION_SETTINGS,
                        settings=simulation.settings
                        if simulation is not None
                        else None,
                    )
            elif action == Action.APPLY_MASK:
                if context == Context.KRAMERS_KRONIG_TAB:
                    test = project_tab.get_active_test()
                    signals.emit(
                        Signal.APPLY_DATA_SET_MASK,
                        mask=test.mask if test is not None else None,
                        test=test,
                        data=project_tab.get_active_data_set(),
                    )
                elif context == Context.DRT_TAB:
                    drt = project_tab.get_active_drt()
                    signals.emit(
                        Signal.APPLY_DATA_SET_MASK,
                        mask=drt.mask if drt is not None else None,
                        drt=drt,
                        data=project_tab.get_active_data_set(),
                    )
                elif context == Context.FITTING_TAB:
                    fit = project_tab.get_active_fit()
                    signals.emit(
                        Signal.APPLY_DATA_SET_MASK,
                        mask=fit.mask if fit is not None else None,
                        fit=fit,
                        data=project_tab.get_active_data_set(),
                    )
            elif action == Action.SHOW_ENLARGED_DRT:
                project_tab.show_enlarged_drt()
            elif action == Action.SHOW_ENLARGED_IMPEDANCE:
                project_tab.show_enlarged_impedance()
            elif action == Action.SHOW_ENLARGED_NYQUIST:
                project_tab.show_enlarged_nyquist()
            elif action == Action.SHOW_ENLARGED_BODE:
                project_tab.show_enlarged_bode()
            elif action == Action.SHOW_ENLARGED_RESIDUALS:
                project_tab.show_enlarged_residuals()
            elif action == Action.SHOW_CIRCUIT_EDITOR:
                if context == Context.FITTING_TAB:
                    project_tab.fitting_tab.show_circuit_editor()
                elif context == Context.SIMULATION_TAB:
                    project_tab.simulation_tab.show_circuit_editor()
            elif action == Action.COPY_DRT_DATA:
                signals.emit(
                    Signal.COPY_PLOT_DATA,
                    plot=project_tab.get_drt_plot(context),
                    context=context,
                )
            elif action == Action.COPY_IMPEDANCE_DATA:
                signals.emit(
                    Signal.COPY_PLOT_DATA,
                    plot=project_tab.get_impedance_plot(context),
                    context=context,
                )
            elif action == Action.COPY_NYQUIST_DATA:
                signals.emit(
                    Signal.COPY_PLOT_DATA,
                    plot=project_tab.get_nyquist_plot(context),
                    context=context,
                )
            elif action == Action.COPY_BODE_DATA:
                signals.emit(
                    Signal.COPY_PLOT_DATA,
                    plot=project_tab.get_bode_plot(context),
                    context=context,
                )
            elif action == Action.COPY_RESIDUALS_DATA:
                signals.emit(
                    Signal.COPY_PLOT_DATA,
                    plot=project_tab.get_residuals_plot(context),
                    context=context,
                )
            elif action == Action.COPY_OUTPUT:
                if context == Context.DRT_TAB:
                    signals.emit(
                        Signal.COPY_OUTPUT,
                        output=project_tab.drt_tab.get_active_output(),
                        drt=project_tab.get_active_drt(),
                    )
                elif context == Context.FITTING_TAB:
                    signals.emit(
                        Signal.COPY_OUTPUT,
                        output=project_tab.get_active_output(context),
                        fit_or_sim=project_tab.get_active_fit(),
                    )
                elif context == Context.SIMULATION_TAB:
                    signals.emit(
                        Signal.COPY_OUTPUT,
                        output=project_tab.get_active_output(context),
                        fit_or_sim=project_tab.get_active_simulation(),
                    )
                else:
                    raise Exception(f"Unsupported context: {context=}")
            elif context == Context.DATA_SETS_TAB:
                data: Optional[DataSet] = project_tab.get_active_data_set()
                # Project-level: data sets tab
                if action == Action.AVERAGE_DATA_SETS:
                    signals.emit(
                        Signal.SELECT_DATA_SETS_TO_AVERAGE,
                    )
                elif action == Action.TOGGLE_DATA_POINTS:
                    signals.emit(
                        Signal.SELECT_DATA_POINTS_TO_TOGGLE,
                        data=data,
                    )
                elif action == Action.COPY_DATA_SET_MASK:
                    signals.emit(
                        Signal.SELECT_DATA_SET_MASK_TO_COPY,
                        data=data,
                    )
                elif action == Action.SUBTRACT_IMPEDANCE:
                    signals.emit(
                        Signal.SELECT_IMPEDANCE_TO_SUBTRACT,
                        data=data,
                    )
            elif context == Context.PLOTTING_TAB:
                settings = project_tab.get_active_plot()  # Optional[PlotSettings]
                # Project-level: plotting tab
                data_sets: List[DataSet]
                tests: List[TestResult]
                fits: List[FitResult]
                simulations: List[SimulationResult]
                if action == Action.SELECT_ALL_PLOT_SERIES:
                    (
                        data_sets,
                        tests,
                        fits,
                        simulations,
                    ) = project_tab.get_filtered_plot_series()
                    signals.emit(
                        Signal.TOGGLE_PLOT_SERIES,
                        enabled=True,
                        data_sets=data_sets,
                        tests=tests,
                        fits=fits,
                        simulations=simulations,
                        settings=settings,
                    )
                elif action == Action.UNSELECT_ALL_PLOT_SERIES:
                    (
                        data_sets,
                        tests,
                        fits,
                        simulations,
                    ) = project_tab.get_filtered_plot_series()
                    signals.emit(
                        Signal.TOGGLE_PLOT_SERIES,
                        enabled=False,
                        data_sets=data_sets,
                        tests=tests,
                        fits=fits,
                        simulations=simulations,
                        settings=settings,
                    )
                elif action == Action.COPY_PLOT_APPEARANCE:
                    signals.emit(
                        Signal.SELECT_PLOT_APPEARANCE_SETTINGS,
                        settings=settings,
                    )
                elif action == Action.COPY_PLOT_DATA:
                    signals.emit(
                        Signal.COPY_PLOT_DATA,
                        plot=project_tab.plotting_tab.plot_types[settings.get_type()]
                        if settings is not None
                        else None,
                        context=context,
                    )
                elif action == Action.EXPAND_COLLAPSE_SIDEBAR:
                    project_tab.plotting_tab.collapse_expand_sidebar()
                elif action == Action.EXPORT_PLOT:
                    signals.emit(
                        Signal.EXPORT_PLOT,
                        settings=settings,
                    )
