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

from traceback import format_exc
from typing import (
    Dict,
    List,
    Optional,
    Tuple,
)
import pyimpspec
from pyimpspec.exceptions import FittingError
import deareis.api.kramers_kronig as api
from deareis.data import (
    DataSet,
    PlotSettings,
    Project,
    KramersKronigSuggestionSettings,
    KramersKronigResult,
    KramersKronigSettings,
)
from deareis.enums import (
    KramersKronigMode,
    KramersKronigRepresentation,
)
from deareis.gui import ProjectTab
from deareis.gui.kramers_kronig.exploratory_results import ExploratoryResults
from deareis.signals import Signal
import deareis.signals as signals
from deareis.state import STATE


def select_test_result(*args, **kwargs):
    project: Optional[Project] = STATE.get_active_project()
    project_tab: Optional[ProjectTab] = STATE.get_active_project_tab()
    if project is None or project_tab is None:
        return

    test: Optional[KramersKronigResult] = kwargs.get("test")
    data: Optional[DataSet] = kwargs.get("data")
    if data is None or test is None:
        return

    is_busy_message_visible: bool = STATE.is_busy_message_visible()
    if not is_busy_message_visible:
        signals.emit(Signal.SHOW_BUSY_MESSAGE, message="Loading test result")

    project_tab.select_test_result(test, data)
    if not is_busy_message_visible:
        signals.emit(Signal.HIDE_BUSY_MESSAGE)


def delete_test_result(*args, **kwargs):
    project: Optional[Project] = STATE.get_active_project()
    project_tab: Optional[ProjectTab] = STATE.get_active_project_tab()
    if project is None or project_tab is None:
        return

    test: Optional[KramersKronigResult] = kwargs.get("test")
    data: Optional[DataSet] = kwargs.get("data")
    if data is None or test is None:
        return

    signals.emit(Signal.SHOW_BUSY_MESSAGE, message="Deleting test result")
    settings: Optional[PlotSettings] = project_tab.get_active_plot()
    update_plot: bool = (
        test.uuid in settings.series_order if settings is not None else False
    )
    project.delete_test(
        data=data,
        test=test,
    )

    project_tab.populate_tests(project, data)
    if settings is not None:
        project_tab.plotting_tab.populate_tests(
            project.get_all_tests(),
            project.get_data_sets(),
            settings,
        )

    if update_plot:
        signals.emit(Signal.SELECT_PLOT_SETTINGS, settings=settings)

    signals.emit(Signal.CREATE_PROJECT_SNAPSHOT)
    signals.emit(Signal.HIDE_BUSY_MESSAGE)


def apply_test_settings(*args, **kwargs):
    project: Optional[Project] = STATE.get_active_project()
    project_tab: Optional[ProjectTab] = STATE.get_active_project_tab()
    if project is None or project_tab is None:
        return

    settings: Optional[KramersKronigSettings] = kwargs.get("settings")
    if settings is None:
        return

    project_tab.set_test_settings(settings)
    STATE.kramers_kronig_suggestion_settings = settings.suggestion_settings


def accept_exploratory_result(
    data: DataSet,
    test: KramersKronigResult,
):
    assert type(data) is DataSet
    assert type(test) is KramersKronigResult
    project: Optional[Project] = STATE.get_active_project()
    project_tab: Optional[ProjectTab] = STATE.get_active_project_tab()
    if project is None or project_tab is None:
        return

    project.add_test(
        data=data,
        test=test,
    )
    project_tab.populate_tests(project, data)
    project_tab.plotting_tab.populate_tests(
        project.get_all_tests(),
        project.get_data_sets(),
        project_tab.get_active_plot(),
    )
    signals.emit(Signal.CREATE_PROJECT_SNAPSHOT)


def show_exploratory_results(
    data: DataSet,
    suggested_admittance: bool,
    Z_suggestion: Optional[Tuple[KramersKronigResult, Dict[int, float], int, int]],
    Y_suggestion: Optional[Tuple[KramersKronigResult, Dict[int, float], int, int]],
    Z_evaluations: Optional[List[Tuple[float, List[KramersKronigResult], float]]],
    Y_evaluations: Optional[List[Tuple[float, List[KramersKronigResult], float]]],
    admittance: bool,
):
    exploratory_results: ExploratoryResults = ExploratoryResults(
        data=data,
        suggested_admittance=suggested_admittance,
        Z_suggestion=Z_suggestion,
        Y_suggestion=Y_suggestion,
        Z_evaluations=Z_evaluations,
        Y_evaluations=Y_evaluations,
        callback=accept_exploratory_result,
        admittance=admittance,
    )

    signals.emit(
        Signal.BLOCK_KEYBINDINGS,
        window=exploratory_results.window,
        window_object=exploratory_results,
    )


def perform_test(*args, **kwargs):
    project: Optional[Project] = STATE.get_active_project()
    project_tab: Optional[ProjectTab] = STATE.get_active_project_tab()
    if project is None or project_tab is None:
        return

    data: Optional[DataSet] = kwargs.get("data")
    settings: Optional[KramersKronigSettings] = kwargs.get("settings")
    if data is None or settings is None:
        return

    assert data.get_num_points() > 0, "There are no data points to test!"
    batch: bool = kwargs.get("batch", False)
    if settings.mode == KramersKronigMode.AUTO or settings.mode == KramersKronigMode.MANUAL:
        signals.emit(Signal.SHOW_BUSY_MESSAGE, message="Performing test(s)")
        test: KramersKronigResult = api.perform_kramers_kronig_test(
            data=data,
            settings=settings,
            num_procs=STATE.config.num_procs or -1,
        )

        signals.emit(Signal.HIDE_BUSY_MESSAGE)
        project.add_test(
            data=data,
            test=test,
        )

        project_tab.populate_tests(project, data)
        project_tab.plotting_tab.populate_tests(
            project.get_all_tests(),
            project.get_data_sets(),
            project_tab.get_active_plot(),
        )

        if batch is False:
            signals.emit(Signal.CREATE_PROJECT_SNAPSHOT)

    elif settings.mode == KramersKronigMode.EXPLORATORY:
        signals.emit(Signal.SHOW_BUSY_MESSAGE, message="Performing test")
        # TODO: Override busy message to specify which representation is being processed?

        Z_evaluations: Optional[List[Tuple[float, List[KramersKronigResult], float]]] = None
        Z_suggestion: Optional[Tuple[KramersKronigResult, Dict[int, float], int, int]] = None
        if settings.representation in (
            KramersKronigRepresentation.AUTO,
            KramersKronigRepresentation.IMPEDANCE,
        ):
            tmp = settings.to_dict()
            tmp["representation"] = KramersKronigRepresentation.IMPEDANCE

            Z_evaluations = api.evaluate_log_F_ext(
                data=data,
                settings=KramersKronigSettings.from_dict(tmp),
                num_procs=STATE.config.num_procs or -1,
            )

            signals.emit(
                Signal.SHOW_BUSY_MESSAGE,
                message="Suggesting optimum number of time constants",
            )
            Z_suggestion = api.suggest_num_RC(
                Z_evaluations[0][1],
                settings=settings.suggestion_settings,
            )

            evaluation: Tuple[float, List[KramersKronigResult], float]
            for evaluation in Z_evaluations:
                result: KramersKronigResult
                for result in evaluation[1]:
                    result.settings = settings

        Y_evaluations: Optional[List[Tuple[float, List[KramersKronigResult], float]]] = None
        Y_suggestion: Optional[Tuple[KramersKronigResult, Dict[int, float], int, int]] = None
        if settings.representation in (
            KramersKronigRepresentation.AUTO,
            KramersKronigRepresentation.ADMITTANCE,
        ):
            tmp = settings.to_dict()
            tmp["representation"] = KramersKronigRepresentation.ADMITTANCE

            Y_evaluations = api.evaluate_log_F_ext(
                data=data,
                settings=KramersKronigSettings.from_dict(tmp),
                num_procs=STATE.config.num_procs or -1,
            )

            for evaluation in Y_evaluations:
                for result in evaluation[1]:
                    result.settings = settings

            signals.emit(
                Signal.SHOW_BUSY_MESSAGE,
                message="Suggesting optimum number of time constants",
            )
            Y_suggestion = api.suggest_num_RC(
                Y_evaluations[0][1],
                settings=settings.suggestion_settings,
            )

        X_suggestion: Optional[Tuple[KramersKronigResult, Dict[int, float], int, int]] = None
        if Z_suggestion is not None and Y_suggestion is not None:
            signals.emit(
                Signal.SHOW_BUSY_MESSAGE,
                message="Suggesting optimum immittance representation",
            )
            X_suggestion = api.suggest_representation([Z_suggestion, Y_suggestion])
        elif Z_suggestion is not None:
            X_suggestion = Z_suggestion
        elif Y_suggestion is not None:
            X_suggestion = Y_suggestion

        signals.emit(Signal.HIDE_BUSY_MESSAGE)
        if batch is False:
            show_exploratory_results(
                data=data,
                suggested_admittance=X_suggestion[0].admittance,
                Z_suggestion=Z_suggestion,
                Y_suggestion=Y_suggestion,
                Z_evaluations=Z_evaluations,
                Y_evaluations=Y_evaluations,
                admittance=project_tab.show_admittance_plots(),
            )
        else:
            project.add_test(
                data=data,
                test=X_suggestion[0],
            )
            project_tab.populate_tests(project, data)
            project_tab.plotting_tab.populate_tests(
                project.get_all_tests(),
                project.get_data_sets(),
                project_tab.get_active_plot(),
            )
    else:
        raise Exception("Unsupported mode!")
