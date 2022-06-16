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
from typing import (
    Optional,
)
from uuid import uuid4
import pyimpspec
from pyimpspec import (
    Circuit,
    FittingResult,
)
from deareis.enums import (
    method_to_value,
    weight_to_value,
    value_to_method,
    value_to_weight,
)
from deareis.data import (
    DataSet,
    FitResult,
    FitSettings,
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
    project_tab.select_fit_result(fit, data)


def delete_fit_result(*args, **kwargs):
    project: Optional[Project] = STATE.get_active_project()
    project_tab: Optional[ProjectTab] = STATE.get_active_project_tab()
    if project is None or project_tab is None:
        return
    fit: Optional[FitResult] = kwargs.get("fit")
    data: Optional[DataSet] = kwargs.get("data")
    if data is None or fit is None:
        return
    project.delete_fit(data, fit)
    project_tab.populate_fits(project, data)
    signals.emit(Signal.SELECT_PLOT_SETTINGS, settings=project_tab.get_active_plot())
    signals.emit(Signal.CREATE_PROJECT_SNAPSHOT)


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
    circuit: Circuit = pyimpspec.string_to_circuit(settings.cdc)
    signals.emit(Signal.SHOW_BUSY_MESSAGE, message="Performing fit(s)")
    result: FittingResult = pyimpspec.fit_circuit_to_data(
        circuit=circuit,
        data=data,
        method=method_to_value.get(settings.method, "auto"),
        weight=weight_to_value.get(settings.weight, "auto"),
        max_nfev=settings.max_nfev,
        num_procs=num_procs,
    )
    fit: FitResult = FitResult(
        uuid4().hex,
        time(),
        result.circuit,
        result.parameters,
        result.frequency,
        result.impedance,
        result.real_residual,
        result.imaginary_residual,
        data.get_mask(),
        result.minimizer_result.chisqr,
        result.minimizer_result.redchi,
        result.minimizer_result.aic,
        result.minimizer_result.bic,
        result.minimizer_result.ndata,
        result.minimizer_result.nfree,
        result.minimizer_result.nfev,
        value_to_method.get(result.method),
        value_to_weight.get(result.weight),
        settings,
    )
    project.add_fit(data, fit)
    signals.emit(Signal.SELECT_DATA_SET, data=data)
    signals.emit(Signal.CREATE_PROJECT_SNAPSHOT)
    signals.emit(Signal.HIDE_BUSY_MESSAGE)
