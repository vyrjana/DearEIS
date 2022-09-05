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

from json import (
    dumps as dump_json,
    loads as parse_json,
)
from os.path import (
    dirname,
    exists,
)
from traceback import format_exc
from typing import (
    Dict,
    List,
    Optional,
)
import dearpygui.dearpygui as dpg
from deareis.data import (
    DataSet,
    PlotSettings,
    Project,
    SimulationResult,
)
from deareis.enums import Context
from deareis.gui import ProjectTab
from deareis.gui.file_dialog import FileDialog
from deareis.signals import Signal
from deareis.state import STATE
from deareis.utility import calculate_window_position_dimensions
import deareis.signals as signals


def new_project(*args, **kwargs):
    signals.emit(Signal.SHOW_BUSY_MESSAGE, message="Creating new project")
    project: Project = Project()
    project_tab: ProjectTab
    existing_tab: bool
    project_tab, existing_tab = STATE.add_project(project)
    STATE.program_window.select_tab(project_tab)
    signals.emit(Signal.SELECT_PROJECT_TAB, uuid=project.uuid)
    if not existing_tab:
        STATE.snapshot_project_state(project)
        signals.emit(
            Signal.RESTORE_PROJECT_STATE,
            project=project,
            project_tab=project_tab,
            state_snapshot="{}",
        )
        assert STATE.is_project_dirty(project) is True
    paths: List[str] = kwargs.get("data", [])
    if paths:
        signals.emit(Signal.LOAD_DATA_SET_FILES, paths=paths)
    signals.emit(Signal.HIDE_BUSY_MESSAGE)


def select_project_files(*args, **kwargs):
    merge: bool = kwargs.get("merge", False)
    # Check if any recent projects have been selected in the home tab
    paths: List[str] = STATE.program_window.get_selected_projects()
    if paths:
        signals.emit(
            Signal.LOAD_PROJECT_FILES,
            paths=paths,
            merge=merge,
        )
        return
    FileDialog(
        cwd=STATE.latest_project_directory,
        label="Select project file(s)",
        callback=lambda *a, **k: signals.emit(
            Signal.LOAD_PROJECT_FILES,
            **k,
        ),
        extensions=[".json"],
        merge=merge,
    )


def load_project_files(*args, **kwargs):
    paths: List[str] = kwargs.get("paths", [])
    merge: bool = kwargs.get("merge", False)
    assert type(paths) is list, paths
    assert type(merge) is bool, merge
    project: Project
    project_tab: ProjectTab
    existing_tab: bool
    assert paths, len(paths)
    parsing_errors: Dict[str, str] = {}
    path: str
    assert len(paths) >= 1, paths
    if merge:
        signals.emit(Signal.SHOW_BUSY_MESSAGE, message="Merging projects")
        projects: List[Project] = []
        for path in paths:
            try:
                projects.append(Project.from_file(path))
            except Exception:
                parsing_errors[path] = format_exc()
                continue
        if not parsing_errors:
            project = Project.merge(projects)
            project_tab, existing_tab = STATE.add_project(project)
            STATE.program_window.select_tab(project_tab)
            signals.emit(Signal.SELECT_PROJECT_TAB, uuid=project.uuid)
            if not existing_tab:
                STATE.snapshot_project_state(project)
                signals.emit(
                    Signal.RESTORE_PROJECT_STATE,
                    project=project,
                    project_tab=project_tab,
                    state_snapshot=dump_json(project.to_dict(session=True)),
                )
                project_tab.set_dirty(STATE.is_project_dirty(project))
                assert STATE.is_project_dirty(project) is True
        STATE.set_recent_projects(paths=[])
    else:
        signals.emit(Signal.SHOW_BUSY_MESSAGE, message="Loading project(s)")
        for path in paths:
            try:
                project: Project = Project.from_file(path)
            except Exception:
                parsing_errors[path] = format_exc()
                continue
            project_tab, existing_tab = STATE.add_project(project)
            STATE.program_window.select_tab(project_tab)
            signals.emit(Signal.SELECT_PROJECT_TAB, uuid=project.uuid)
            if not existing_tab:
                STATE.snapshot_project_state(project)
                signals.emit(
                    Signal.RESTORE_PROJECT_STATE,
                    project=project,
                    project_tab=project_tab,
                    state_snapshot=dump_json(project.to_dict(session=True)),
                )
                STATE.update_project_state_saved_index(project)
                project_tab.set_dirty(STATE.is_project_dirty(project))
                assert STATE.is_project_dirty(project) is False
                assert (
                    STATE.get_project_state_snapshot_index(project) == 0
                ), STATE.get_project_state_snapshot_index(project)
        STATE.set_recent_projects(
            paths=list(filter(lambda _: _ not in parsing_errors, paths))
        )
    STATE.latest_project_directory = dirname(path)
    if parsing_errors:
        total_traceback: str = ""
        traceback: str
        for path, traceback in parsing_errors.items():
            total_traceback += f"{traceback}\nThe exception above was encountered while parsing '{path}'.\n\n"
        signals.emit(
            Signal.SHOW_ERROR_MESSAGE,
            traceback=total_traceback.strip(),
            message="""
Encountered error(s) while parsing project file(s). The file(s) might be malformed, corrupted, or simply a newer version than is supported by this version of DearEIS.
            """.strip(),
        )
    signals.emit(Signal.HIDE_BUSY_MESSAGE)


def restore_project_state(*args, **kwargs):
    project: Optional[Project] = kwargs.get("project", STATE.get_active_project())
    project_tab: Optional[ProjectTab] = kwargs.get(
        "project_tab", STATE.get_active_project_tab()
    )
    state_snapshot: Optional[str] = kwargs.get("state_snapshot")
    if project is None or project_tab is None or state_snapshot is None:
        return
    project_state: dict = parse_json(state_snapshot)
    project.update(**project_state)
    project_tab.set_label(project_state.get("label", "Project"))
    project_tab.set_notes(project_state.get("notes", ""))
    project_tab.populate_plots(project)
    plot: Optional[PlotSettings] = project_tab.get_active_plot()
    plots: List[PlotSettings] = project.get_plots()
    if plot is None or plot.uuid not in list(map(lambda _: _.uuid, plots)):
        assert len(plots) > 0
        plot = plots[0]
    else:
        # The PlotSettings returned by ProjectTab.get_active_plot is potentially out of date.
        # Look for the up-to-date version among those returned by Project.get_plots.
        plot = list(filter(lambda _: _.uuid == plot.uuid, plots))[0]
    signals.emit(
        Signal.SELECT_PLOT_SETTINGS,
        settings=plot,
    )
    project_tab.populate_data_sets(project)
    data: Optional[DataSet] = project_tab.get_active_data_set(
        context=Context.DATA_SETS_TAB
    )
    data_sets: List[DataSet] = project.get_data_sets()
    if data is None and data_sets:
        data = data_sets[0]
    elif data_sets:
        # This is done because the DataSet instance returned by get_active_data_set is outdated.
        found_data: bool = False
        for _ in data_sets:
            if _.uuid == data.uuid:
                data = _
                found_data = True
                break
        if not found_data:
            data = data_sets[0]
    else:
        data = None
    signals.emit(
        Signal.SELECT_DATA_SET,
        data=data,
    )
    project_tab.populate_simulations(project)
    simulation: Optional[SimulationResult] = project_tab.get_active_simulation()
    simulations: List[SimulationResult] = project.get_simulations()
    if simulation is None and simulations:
        simulation = simulations[0]
    elif simulations:
        found_sim: bool = False
        for _ in simulations:
            if _.uuid == simulation.uuid:
                simulation = _
                found_sim = True
                break
        if not found_sim:
            simulation = simulations[0]
    else:
        simulation = None
    signals.emit(
        Signal.SELECT_SIMULATION_RESULT,
        simulation=simulation,
        data=project_tab.get_active_data_set(context=Context.SIMULATION_TAB),
    )
    project_tab.set_dirty(STATE.is_project_dirty(project))


def create_project_snapshot(*args, **kwargs):
    project: Optional[Project] = STATE.get_active_project()
    project_tab: Optional[ProjectTab] = STATE.get_active_project_tab()
    if project is None or project_tab is None:
        return
    STATE.snapshot_project_state(project)
    project_tab.set_dirty(kwargs.get("dirty", True))


def save_project_as(*args, **kwargs):
    project: Optional[Project] = STATE.get_active_project()
    project_tab: Optional[ProjectTab] = STATE.get_active_project_tab()
    if project is None or project_tab is None:
        return
    FileDialog(
        cwd=STATE.latest_project_directory,
        label="Select project path",
        callback=lambda *a, **k: signals.emit(
            Signal.SAVE_PROJECT,
            close_project=kwargs.get("close_project", False),
            **k,
        ),
        extensions=[".json"],
        save=True,
    )


def save_project(*args, **kwargs):
    project: Optional[Project] = STATE.get_active_project()
    project_tab: Optional[ProjectTab] = STATE.get_active_project_tab()
    if project is None or project_tab is None:
        return
    path: Optional[str] = kwargs.get("path", "").strip() or None
    if path is None and project.get_path().strip() == "":
        signals.emit(
            Signal.SAVE_PROJECT_AS, close_project=kwargs.get("close_project", False)
        )
        return
    assert path is None or exists(
        dirname(path)
    ), f"Folder does not exist: '{dirname(path)}'"
    project.save(path)
    STATE.update_project_state_saved_index(project)
    project_tab.set_dirty(STATE.is_project_dirty(project))
    STATE.set_recent_projects(paths=[project.get_path()])
    STATE.clear_project_backups([project])
    if kwargs.get("close_project", False):
        STATE.remove_project(project)
        dpg.delete_item(project_tab.tab)


def close_project(*args, **kwargs):
    project: Optional[Project] = STATE.get_active_project()
    project_tab: Optional[ProjectTab] = STATE.get_active_project_tab()
    if project is None or project_tab is None:
        return
    if not STATE.is_project_dirty(project) or kwargs.get("force", False):
        STATE.remove_project(project)
        dpg.delete_item(project_tab.tab)
        STATE.clear_project_backups([project])
        return
    window: int = dpg.generate_uuid()
    key_handler: int = dpg.generate_uuid()

    def close():
        if dpg.does_item_exist(window):
            dpg.delete_item(window)
        if dpg.does_item_exist(key_handler):
            dpg.delete_item(key_handler)

    def discard():
        close()
        STATE.remove_project(project)
        dpg.delete_item(project_tab.tab)
        STATE.clear_project_backups([project])

    def save():
        close()
        signals.emit(Signal.SAVE_PROJECT, close_project=True)

    x: int
    y: int
    w: int
    h: int
    x, y, w, h = calculate_window_position_dimensions(300, 56)
    with dpg.window(
        label="Unsaved changes",
        pos=(
            x,
            y,
        ),
        width=w,
        height=h,
        no_resize=True,
        modal=True,
        tag=window,
    ):
        dpg.add_text(
            "Do you wish to save the changes, discard the changes, or cancel?",
            wrap=260,
        )
        dpg.add_spacer(height=8)
        with dpg.group(horizontal=True):
            dpg.add_button(
                label="Save",
                callback=save,
            )
            dpg.add_button(label="Discard", callback=discard)
            dpg.add_button(label="Cancel", callback=close)
    with dpg.handler_registry(tag=key_handler):
        dpg.add_key_release_handler(
            key=dpg.mvKey_Escape,
            callback=close,
        )
    signals.emit(Signal.BLOCK_KEYBINDINGS, window=window, window_object=None)
