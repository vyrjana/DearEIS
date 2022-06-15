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

from time import time
from typing import Optional
from uuid import uuid4
import pyimpspec
from pyimpspec import Circuit
from deareis.data import (
    DataSet,
    Project,
    SimulationResult,
    SimulationSettings,
)
from deareis.enums import Context
from deareis.gui import ProjectTab
from deareis.signals import Signal
from deareis.state import STATE
import deareis.signals as signals


def select_simulation_result(*args, **kwargs):
    project: Optional[Project] = STATE.get_active_project()
    project_tab: Optional[ProjectTab] = STATE.get_active_project_tab()
    if project is None or project_tab is None:
        return
    simulation: Optional[SimulationResult] = kwargs.get("simulation")
    data: Optional[DataSet] = kwargs.get("data")
    project_tab.select_simulation_result(simulation, data)


def delete_simulation_result(*args, **kwargs):
    project: Optional[Project] = STATE.get_active_project()
    project_tab: Optional[ProjectTab] = STATE.get_active_project_tab()
    if project is None or project_tab is None:
        return
    simulation: Optional[SimulationResult] = kwargs.get("simulation")
    if simulation is None:
        return
    project.delete_simulation(simulation)
    project_tab.populate_simulations(project)
    simulations: List[SimulationResult] = project.get_simulations()
    signals.emit(
        Signal.SELECT_SIMULATION_RESULT,
        simulation=simulations[0] if simulations else None,
        data=project_tab.get_active_data_set(context=Context.SIMULATION_TAB),
    )
    signals.emit(Signal.SELECT_PLOT_SETTINGS, settings=project_tab.get_active_plot())
    signals.emit(Signal.CREATE_PROJECT_SNAPSHOT)


def apply_simulation_settings(*args, **kwargs):
    project: Optional[Project] = STATE.get_active_project()
    project_tab: Optional[ProjectTab] = STATE.get_active_project_tab()
    if project is None or project_tab is None:
        return
    settings: Optional[SimulationSettings] = kwargs.get("settings")
    if settings is None:
        return
    project_tab.set_simulation_settings(settings)


def perform_simulation(*args, **kwargs):
    project: Optional[Project] = STATE.get_active_project()
    project_tab: Optional[ProjectTab] = STATE.get_active_project_tab()
    if project is None or project_tab is None:
        return
    settings: Optional[SimulationSettings] = kwargs.get("settings")
    if settings is None:
        return
    assert (
        settings.min_frequency != settings.max_frequency
    ), "The minimum and maximum frequencies cannot be the same!"
    circuit: Circuit = pyimpspec.string_to_circuit(settings.cdc)
    pyimpspec.analysis.fitting.validate_circuit(circuit)
    signals.emit(Signal.SHOW_BUSY_MESSAGE, message="Performing simulation")
    simulation: SimulationResult = SimulationResult(
        uuid4().hex,
        time(),
        circuit,
        settings,
    )
    project.add_simulation(simulation)
    project_tab.populate_simulations(project)
    signals.emit(
        Signal.SELECT_SIMULATION_RESULT,
        simulation=simulation,
        data=project_tab.get_active_data_set(context=Context.SIMULATION_TAB),
    )
    signals.emit(Signal.SELECT_PLOT_SETTINGS, settings=project_tab.get_active_plot())
    signals.emit(Signal.CREATE_PROJECT_SNAPSHOT)
    signals.emit(Signal.HIDE_BUSY_MESSAGE)
