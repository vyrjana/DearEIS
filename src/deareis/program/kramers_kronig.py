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

from multiprocessing import cpu_count
from traceback import format_exc
from typing import (
    List,
    Optional,
)
from numpy import (
    array,
    ndarray,
)
from pyimpspec import FittingError
import deareis.api.kramers_kronig as api
from deareis.data import (
    DataSet,
    PlotSettings,
    Project,
    TestResult,
    TestSettings,
)
from deareis.enums import (
    TestMode,
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
    test: Optional[TestResult] = kwargs.get("test")
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
    test: Optional[TestResult] = kwargs.get("test")
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
    settings: Optional[TestSettings] = kwargs.get("settings")
    if settings is None:
        return
    project_tab.set_test_settings(settings)


def accept_exploratory_result(data: DataSet, test: TestResult, settings: TestSettings):
    assert type(data) is DataSet
    assert type(test) is TestResult
    assert type(settings) is TestSettings
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
    results: List[TestResult],
    settings: TestSettings,
    num_RCs: ndarray,
):
    assert type(data) is DataSet
    assert type(results) is list and all(map(lambda _: type(_) is TestResult, results))
    assert type(settings) is TestSettings
    assert type(num_RCs) is ndarray
    exploratory_results: ExploratoryResults = ExploratoryResults(
        data=data,
        results=results,
        settings=settings,
        num_RCs=num_RCs,
        callback=accept_exploratory_result,
        state=STATE,
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
    settings: Optional[TestSettings] = kwargs.get("settings")
    if data is None or settings is None:
        return
    assert data.get_num_points() > 0, "There are no data points to test!"
    # Prevent the GUI from becoming unresponsive or sluggish
    num_procs: int = max(2, cpu_count() - 1)
    if settings.mode == TestMode.AUTO or settings.mode == TestMode.MANUAL:
        signals.emit(Signal.SHOW_BUSY_MESSAGE, message="Performing test(s)")
        try:
            test: TestResult = api.perform_test(
                data=data,
                settings=settings,
                num_procs=num_procs,
            )
        except FittingError:
            signals.emit(Signal.SHOW_ERROR_MESSAGE, traceback=format_exc())
            return
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
        signals.emit(Signal.CREATE_PROJECT_SNAPSHOT)
    elif settings.mode == TestMode.EXPLORATORY:
        signals.emit(Signal.SHOW_BUSY_MESSAGE, message="Performing test")
        try:
            results: List[TestResult] = api.perform_exploratory_tests(
                data=data,
                settings=settings,
                num_procs=num_procs,
            )
        except FittingError:
            signals.emit(Signal.SHOW_ERROR_MESSAGE, traceback=format_exc())
            return
        signals.emit(Signal.HIDE_BUSY_MESSAGE)
        num_RCs: ndarray = array(list(range(1, settings.num_RC + 1)))
        show_exploratory_results(
            data,
            results,
            settings,
            num_RCs,
        )
    else:
        raise Exception("Unsupported mode!")
