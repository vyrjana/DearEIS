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
from typing import (
    Optional,
)
import deareis.api.fitting as api
from deareis.data import (
    DataSet,
    FitResult,
    FitSettings,
    PlotSettings,
    Project,
)
from deareis.gui import (
    ProjectTab,
)
from deareis.signals import Signal
import deareis.signals as signals
from deareis.state import STATE


def select_fit_result(*args, **kwargs):
    project: Optional[Project] = STATE.get_active_project()
    project_tab: Optional[ProjectTab] = STATE.get_active_project_tab()
    if project is None or project_tab is None:
        return
    fit: Optional[FitResult] = kwargs.get("fit")
    data: Optional[DataSet] = kwargs.get("data")
    if data is None or fit is None:
        return
    is_busy_message_visible: bool = STATE.is_busy_message_visible()
    if not is_busy_message_visible:
        signals.emit(Signal.SHOW_BUSY_MESSAGE, message="Loading fit result")
    project_tab.select_fit_result(fit, data)
    if not is_busy_message_visible:
        signals.emit(Signal.HIDE_BUSY_MESSAGE)


def delete_fit_result(*args, **kwargs):
    project: Optional[Project] = STATE.get_active_project()
    project_tab: Optional[ProjectTab] = STATE.get_active_project_tab()
    if project is None or project_tab is None:
        return
    fit: Optional[FitResult] = kwargs.get("fit")
    data: Optional[DataSet] = kwargs.get("data")
    if data is None or fit is None:
        return
    signals.emit(Signal.SHOW_BUSY_MESSAGE, message="Deleting fit result")
    settings: Optional[PlotSettings] = project_tab.get_active_plot()
    update_plot: bool = (
        fit.uuid in settings.series_order if settings is not None else False
    )
    project.delete_fit(data, fit)
    project_tab.populate_fits(project, data)
    if settings is not None:
        project_tab.plotting_tab.populate_fits(
            project.get_all_fits(),
            project.get_data_sets(),
            settings,
        )
    if update_plot:
        signals.emit(Signal.SELECT_PLOT_SETTINGS, settings=settings)
    signals.emit(Signal.CREATE_PROJECT_SNAPSHOT)
    signals.emit(Signal.HIDE_BUSY_MESSAGE)


def apply_fit_settings(*args, **kwargs):
    project: Optional[Project] = STATE.get_active_project()
    project_tab: Optional[ProjectTab] = STATE.get_active_project_tab()
    if project is None or project_tab is None:
        return
    settings: Optional[FitSettings] = kwargs.get("settings")
    if settings is None:
        return
    project_tab.set_fit_settings(settings)


def perform_fit(*args, **kwargs):
    project: Optional[Project] = STATE.get_active_project()
    project_tab: Optional[ProjectTab] = STATE.get_active_project_tab()
    if project is None or project_tab is None:
        return
    data: Optional[DataSet] = kwargs.get("data")
    settings: Optional[FitSettings] = kwargs.get("settings")
    if data is None or settings is None:
        return
    assert data.get_num_points() > 0, "There are no data points to fit the circuit to!"
    # Prevent the GUI from becoming unresponsive or sluggish
    num_procs: int = max(2, cpu_count() - 1)
    signals.emit(Signal.SHOW_BUSY_MESSAGE, message="Performing fit")
    fit: FitResult = api.fit_circuit(data=data, settings=settings, num_procs=num_procs)
    project.add_fit(data, fit)
    project_tab.populate_fits(project, data)
    project_tab.plotting_tab.populate_fits(
        project.get_all_fits(),
        project.get_data_sets(),
        project_tab.get_active_plot(),
    )
    signals.emit(Signal.CREATE_PROJECT_SNAPSHOT)
    signals.emit(Signal.HIDE_BUSY_MESSAGE)
