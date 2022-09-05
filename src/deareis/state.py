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

from json import dumps as dump_json
from os import (
    getcwd,
    makedirs,
    remove,
    walk,
)
from os.path import (
    exists,
    join,
)
from typing import (
    Any,
    Dict,
    IO,
    List,
    Optional,
    Tuple,
)
from xdg import (
    xdg_state_home,  # User-specific state data files
)
import dearpygui.dearpygui as dpg
from deareis.version import PACKAGE_VERSION
from deareis.config import Config
from deareis.data import (
    PlotSettings,
    Project,
)
from deareis.enums import (
    Context,
)
from deareis.gui.project import ProjectTab
from deareis.gui.program import ProgramWindow
from deareis.gui.command_palette import CommandPalette
from deareis.keybindings import KeybindingHandler
from deareis.utility import calculate_checksum
from deareis.gui.plotting.export import PlotExporter
from deareis.signals import Signal
import deareis.signals as signals


class State:
    def __init__(self):
        self.state_directory_path: str = join(xdg_state_home(), "DearEIS")
        if not exists(self.state_directory_path):
            makedirs(self.state_directory_path)
        self.snapshots_directory_path: str = join(
            self.state_directory_path, "snapshots"
        )
        if not exists(self.snapshots_directory_path):
            makedirs(self.snapshots_directory_path)
        self.recent_projects_path: str = join(
            self.state_directory_path, "recent_projects"
        )
        self.recent_projects: List[str] = []
        self.config: Config = Config()
        self.program_window: ProgramWindow = ProgramWindow()
        self.latest_project_directory: str = getcwd()
        self.latest_data_set_directory: str = getcwd()
        self.latest_plot_directory: str = getcwd()
        self.projects: List[Project] = []
        self.project_tabs: Dict[str, ProjectTab] = {}
        self.project_lookup: Dict[str, Tuple[Project, ProjectTab]] = {}
        self.active_project: Optional[Project] = None
        self.keybinding_handler: KeybindingHandler = KeybindingHandler(
            self.config.keybindings, self
        )
        self.active_modal_window: Optional[int] = None
        self.active_modal_window_object: Any = None
        self.project_state_snapshots: Dict[str, List[str]] = {}
        self.project_state_snapshot_indices: Dict[str, int] = {}
        self.project_state_saved_indices: Dict[str, int] = {}
        self.command_palette: CommandPalette = CommandPalette(self.keybinding_handler)
        self.plot_exporter: PlotExporter = PlotExporter(self.config)

    def set_active_modal_window(self, window: int, window_object: Any):
        assert type(window) is int
        if dpg.does_item_exist(window):
            self.active_modal_window = window
            self.active_modal_window_object = window_object
        else:
            self.active_modal_window = None
            self.active_modal_window_object = None

    def get_active_modal_window(self) -> Optional[int]:
        return self.active_modal_window

    def add_project(self, project: Project) -> Tuple[ProjectTab, bool]:
        existing_tab: bool = project.uuid in self.project_lookup
        if existing_tab:
            return (
                self.project_tabs[project.uuid],
                existing_tab,
            )
        project_tab: ProjectTab = ProjectTab(
            project.uuid,
            self.program_window.project_tab_bar.tab_bar,
            self,
        )
        self.projects.append(project)
        self.project_tabs[project.uuid] = project_tab
        self.project_lookup[project.uuid] = (
            project,
            project_tab,
        )
        return (
            project_tab,
            existing_tab,
        )

    def remove_project(self, project: Project):
        assert project in self.projects
        self.projects.remove(project)
        del self.project_tabs[project.uuid]
        del self.project_lookup[project.uuid]
        del self.project_state_snapshots[project.uuid]
        del self.project_state_snapshot_indices[project.uuid]
        del self.project_state_saved_indices[project.uuid]

    def set_active_project(self, uuid: Optional[str]):
        assert (type(uuid) is str and uuid.strip() != "") or uuid is None
        if uuid is None:
            self.active_project = None
        else:
            self.active_project = self.project_lookup[uuid][0]

    def get_active_project(self) -> Optional[Project]:
        return self.active_project

    def get_active_project_tab(self) -> Optional[ProjectTab]:
        if self.active_project is None:
            return None
        return self.project_tabs[self.active_project.uuid]

    def get_project_tab(self, project: Project) -> Optional[ProjectTab]:
        return self.project_tabs.get(project.uuid)

    def update_project_state_saved_index(self, project: Project):
        assert type(project) is Project, project
        index: int = self.project_state_snapshot_indices[project.uuid]
        self.project_state_saved_indices[project.uuid] = index

    def is_project_dirty(self, project: Project) -> bool:
        assert type(project) is Project, project
        index: int = self.project_state_saved_indices[project.uuid]
        return index < 0 or self.get_project_state_snapshot_index(project) != index

    def get_project_state_snapshot_index(self, project: Project) -> int:
        assert type(project) is Project, project
        return self.project_state_snapshot_indices[project.uuid]

    def snapshot_project_state(self, project: Project):
        assert type(project) is Project, project
        if project.uuid not in self.project_state_snapshots:
            self.project_state_snapshots[project.uuid] = []
            self.project_state_snapshot_indices[project.uuid] = 0
            self.project_state_saved_indices[project.uuid] = -1
        snapshots: List[str] = self.project_state_snapshots[project.uuid]
        index: int = self.get_project_state_snapshot_index(project)
        while len(snapshots) - 1 > index:
            snapshots.pop()
        if index < self.project_state_saved_indices[project.uuid]:
            self.project_state_saved_indices[project.uuid] = -1
        snapshots.append(
            dump_json(project.to_dict(session=True)),
        )
        self.project_state_snapshot_indices[project.uuid] = len(snapshots) - 1
        if (
            index > 0
            and self.config.auto_backup_interval > 0
            and index % self.config.auto_backup_interval == 0
        ):
            self.serialize_project_snapshots([project], auto_backup=True)

    def get_previous_project_state_snapshot(self, project: Project) -> Optional[str]:
        assert type(project) is Project, project
        if project.uuid not in self.project_state_snapshots:
            return None
        snapshots: List[str] = self.project_state_snapshots[project.uuid]
        if not snapshots:
            return None
        index: int = self.get_project_state_snapshot_index(project)
        if index < 1:
            return None
        self.project_state_snapshot_indices[project.uuid] = index - 1
        return snapshots[index - 1]

    def get_next_project_state_snapshot(self, project: Project) -> Optional[str]:
        assert type(project) is Project, project
        if project.uuid not in self.project_state_snapshots:
            return None
        snapshots: List[str] = self.project_state_snapshots[project.uuid]
        if not snapshots:
            return None
        index: int = self.get_project_state_snapshot_index(project)
        if index >= len(snapshots) - 1:
            return None
        self.project_state_snapshot_indices[project.uuid] = index + 1
        return snapshots[index + 1]

    def get_recent_projects(self) -> List[str]:
        if not self.recent_projects and exists(self.recent_projects_path):
            fp: IO
            with open(self.recent_projects_path, "r") as fp:
                self.recent_projects.extend(
                    list(filter(exists, map(str.strip, fp.readlines())))
                )
        return self.recent_projects.copy()

    def set_recent_projects(self, *args, **kwargs):
        paths: List[str] = kwargs.get("paths")
        assert type(paths) is list, paths
        for path in reversed(paths):
            if path in self.recent_projects:
                self.recent_projects.remove(path)
            self.recent_projects.insert(0, path)
        self.program_window.project_tab_bar.home_tab.update_recent_projects_table(
            self.recent_projects
        )

    def clear_recent_projects(self, selected_projects: List[str]):
        assert type(selected_projects) is list and all(
            map(lambda _: type(_) is str, selected_projects)
        ), selected_projects
        if len(selected_projects) > 0:
            for path in selected_projects:
                if path in self.recent_projects:
                    self.recent_projects.remove(path)
        else:
            self.recent_projects.clear()
        self.program_window.project_tab_bar.home_tab.update_recent_projects_table(
            self.recent_projects
        )

    def save_recent_projects(self):
        contents: str = "\n".join(
            list(filter(lambda _: exists(_), self.recent_projects))
        )
        if exists(self.recent_projects_path) and contents != "":
            new_checksum: str = calculate_checksum(string=contents)
            old_checksum: str = calculate_checksum(path=self.recent_projects_path)
            if new_checksum == old_checksum:
                return
        fp: IO
        with open(self.recent_projects_path, "w") as fp:
            fp.write(contents)

    def serialize_project_snapshots(
        self, projects: List[Project], auto_backup: bool = False
    ):
        project: Project
        for project in projects:
            snapshot: dict = project.to_dict(session=False)
            snapshot["path"] = project.get_path()
            path: str = join(
                self.snapshots_directory_path,
                f"{project.uuid}{'-auto-backup' if auto_backup else ''}.json",
            )
            fp: IO
            with open(path, "w") as fp:
                fp.write(dump_json(snapshot))
        if not auto_backup:
            self.clear_project_backups(projects)

    def get_unsaved_project_snapshots(self) -> List[str]:
        root: str
        paths: List[str]
        for root, _, paths in walk(self.snapshots_directory_path):
            break
        return list(
            sorted(
                map(
                    lambda _: join(root, _),
                    filter(lambda _: _.endswith(".json"), paths),
                )
            )
        )

    def clear_project_backups(self, projects: List[Project]):
        project: Project
        for project in projects:
            path: str = join(
                self.snapshots_directory_path, f"{project.uuid}-auto-backup.json"
            )
            if not exists(path):
                continue
            remove(path)

    def show_command_palette(self):
        project: Optional[Project] = self.get_active_project()
        project_tab: Optional[ProjectTab] = self.get_active_project_tab()
        contexts: List[Context] = [Context.PROGRAM]
        if project is not None and project_tab is not None:
            contexts.extend([Context.PROJECT, project_tab.get_active_context()])
        self.command_palette.show(contexts, project, project_tab)

    def show_plot_exporter(self, settings: PlotSettings, project: Project):
        self.plot_exporter.show(settings, project)

    def close_plot_exporter(self):
        self.plot_exporter.close()

    def is_busy_message_visible(self) -> bool:
        return self.program_window.busy_message.is_visible()

    def check_version(self):
        recent_version_path: str = join(self.state_directory_path, "recent_version")
        fp: IO
        if not exists(recent_version_path):
            with open(recent_version_path, "w") as fp:
                fp.write(PACKAGE_VERSION)
            return
        version: str = ""
        with open(recent_version_path, "r") as fp:
            version = fp.read().strip()
        if version != PACKAGE_VERSION:
            with open(recent_version_path, "w") as fp:
                fp.write(PACKAGE_VERSION)
            signals.emit(Signal.SHOW_CHANGELOG)


STATE: State = State()
