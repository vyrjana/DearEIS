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
from time import time
from traceback import format_exc
from typing import (
    List,
    Optional,
)
from uuid import uuid4
from numpy import (
    array,
    ndarray,
)
import pyimpspec
from pyimpspec import (
    KramersKronigResult,
    FittingError,
)
import deareis.api.kramers_kronig as api
from deareis.data import (
    DataSet,
    Project,
    TestResult,
    TestSettings,
)
from deareis.enums import (
    Mode,
    test_to_value,
    method_to_value,
)
from deareis.gui import ProjectTab
from deareis.gui.exploratory_results import ExploratoryResults
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
    project_tab.select_test_result(test, data)


def delete_test_result(*args, **kwargs):
    project: Optional[Project] = STATE.get_active_project()
    project_tab: Optional[ProjectTab] = STATE.get_active_project_tab()
    if project is None or project_tab is None:
        return
    test: Optional[TestResult] = kwargs.get("test")
    data: Optional[DataSet] = kwargs.get("data")
    if data is None or test is None:
        return
    project.delete_test(data, test)
    project_tab.populate_tests(project, data)
    signals.emit(Signal.SELECT_PLOT_SETTINGS, settings=project_tab.get_active_plot())
    signals.emit(Signal.CREATE_PROJECT_SNAPSHOT)


def apply_test_settings(*args, **kwargs):
    project: Optional[Project] = STATE.get_active_project()
    project_tab: Optional[ProjectTab] = STATE.get_active_project_tab()
    if project is None or project_tab is None:
        return
    settings: Optional[TestSettings] = kwargs.get("settings")
    if settings is None:
        return
    project_tab.set_test_settings(settings)


def accept_exploratory_result(
    data: DataSet, result: KramersKronigResult, settings: TestSettings
):
    assert type(data) is DataSet
    assert type(result) is KramersKronigResult
    assert type(settings) is TestSettings
    project: Optional[Project] = STATE.get_active_project()
    if project is None:
        return
    test: TestResult = TestResult(
        uuid4().hex,
        time(),
        result.circuit,
        result.num_RC,
        result.mu,
        result.pseudo_chisqr,
        result.frequency,
        result.impedance,
        result.real_residual,
        result.imaginary_residual,
        data.get_mask().copy(),
        settings,
    )
    project.add_test(
        data=data,
        test=test,
    )
    signals.emit(Signal.SELECT_DATA_SET, data=data)
    signals.emit(Signal.CREATE_PROJECT_SNAPSHOT)


def show_exploratory_results(
    data: DataSet,
    results: List[KramersKronigResult],
    settings: TestSettings,
    num_RCs: ndarray,
):
    assert type(data) is DataSet
    assert type(results) is list and all(
        map(lambda _: type(_) is KramersKronigResult, results)
    )
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
    if settings.mode == Mode.AUTO or settings.mode == Mode.MANUAL:
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
        signals.emit(Signal.SELECT_DATA_SET, data=data)
        signals.emit(Signal.CREATE_PROJECT_SNAPSHOT)
    elif settings.mode == Mode.EXPLORATORY:
        num_RCs: List[int] = list(range(1, settings.num_RC + 1))
        if not num_RCs:
            return
        signals.emit(Signal.SHOW_BUSY_MESSAGE, message="Performing test(s)")
        try:
            results: List[KramersKronigResult] = pyimpspec.perform_exploratory_tests(
                data=data,
                test=test_to_value[settings.test],
                num_RCs=num_RCs,
                mu_criterion=settings.mu_criterion,
                add_capacitance=settings.add_capacitance,
                add_inductance=settings.add_inductance,
                method=method_to_value[settings.method],
                max_nfev=settings.max_nfev,
                num_procs=num_procs,
            )
        except FittingError:
            signals.emit(Signal.SHOW_ERROR_MESSAGE, traceback=format_exc())
            return
        signals.emit(Signal.HIDE_BUSY_MESSAGE)
        show_exploratory_results(
            data,
            results,
            settings,
            array(num_RCs),
        )
    else:
        raise Exception("Unsupported mode!")
