# DearEIS is licensed under the GPLv3 or later (https://www.gnu.org/licenses/gpl-3.0.html).
# Copyright 2025 DearEIS developers
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

from typing import (
    Optional,
)
import pyimpspec
from deareis.data import (
    DataSet,
    PlotSettings,
    Project,
    SimulationResult,
    SimulationSettings,
)
import deareis.api.simulation as api
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

    is_busy_message_visible: bool = STATE.is_busy_message_visible()
    if not is_busy_message_visible:
        signals.emit(Signal.SHOW_BUSY_MESSAGE, message="Loading simulation result")

    project_tab.select_simulation_result(simulation, data)
    if not is_busy_message_visible:
        signals.emit(Signal.HIDE_BUSY_MESSAGE)


def delete_simulation_result(*args, **kwargs):
    project: Optional[Project] = STATE.get_active_project()
    project_tab: Optional[ProjectTab] = STATE.get_active_project_tab()
    if project is None or project_tab is None:
        return

    simulation: Optional[SimulationResult] = kwargs.get("simulation")
    if simulation is None:
        return

    signals.emit(Signal.SHOW_BUSY_MESSAGE, message="Deleting simulation result")
    settings: Optional[PlotSettings] = project_tab.get_active_plot()
    update_plot: bool = (
        simulation.uuid in settings.series_order if settings is not None else False
    )
    project.delete_simulation(simulation)
    project_tab.populate_simulations(project)

    if settings is not None:
        project_tab.plotting_tab.populate_simulations(
            project.get_simulations(),
            settings,
        )

    if update_plot:
        signals.emit(Signal.SELECT_PLOT_SETTINGS, settings=settings)

    signals.emit(Signal.CREATE_PROJECT_SNAPSHOT)
    signals.emit(Signal.HIDE_BUSY_MESSAGE)


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
    circuit: pyimpspec.Circuit = pyimpspec.parse_cdc(settings.cdc)
    if len(circuit.get_elements()) == 0:
        return

    signals.emit(Signal.SHOW_BUSY_MESSAGE, message="Performing simulation")
    simulation: SimulationResult = api.simulate_spectrum(settings)
    project.add_simulation(simulation)
    project_tab.populate_simulations(project)
    signals.emit(
        Signal.SELECT_SIMULATION_RESULT,
        simulation=simulation,
        data=project_tab.get_active_data_set(context=Context.SIMULATION_TAB),
    )
    project_tab.plotting_tab.populate_simulations(
        project.get_simulations(),
        project_tab.get_active_plot(),
    )
    signals.emit(Signal.CREATE_PROJECT_SNAPSHOT)
    signals.emit(Signal.HIDE_BUSY_MESSAGE)
