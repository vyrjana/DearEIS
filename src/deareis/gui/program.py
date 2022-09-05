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

from os.path import basename
from typing import List, Optional
import dearpygui.dearpygui as dpg
from deareis.gui.busy_message import BusyMessage
from deareis.gui.error_message import ErrorMessage
from deareis.gui.project import ProjectTab
from deareis.signals import Signal
import deareis.signals as signals
from deareis.tooltips import attach_tooltip
import deareis.tooltips as tooltips


class HomeTab:
    def __init__(self):
        self.tab: int = dpg.generate_uuid()
        with dpg.tab(
            label="Home",
            order_mode=dpg.mvTabOrder_Fixed,
            tag=self.tab,
        ):
            dpg.add_text("Recent projects")
            self.recent_projects_table: int = dpg.generate_uuid()
            with dpg.child_window(border=False, width=-1, height=-24):
                with dpg.table(
                    borders_outerV=True,
                    borders_outerH=True,
                    borders_innerV=True,
                    borders_innerH=True,
                    scrollY=True,
                    freeze_rows=1,
                    height=-1,
                    tag=self.recent_projects_table,
                ):
                    dpg.add_table_column(width_fixed=True)
                    dpg.add_table_column(label="Filename")
                    dpg.add_table_column(width_fixed=True)
            with dpg.child_window(border=False):
                with dpg.group(horizontal=True):
                    dpg.add_button(
                        label="New project",
                        callback=lambda: signals.emit(Signal.NEW_PROJECT),
                    )
                    attach_tooltip(tooltips.home.new_project)
                    self.load_projects_button: int = dpg.generate_uuid()
                    dpg.add_button(
                        label="Load project(s)",
                        callback=lambda: signals.emit(Signal.SELECT_PROJECT_FILES),
                        tag=self.load_projects_button,
                    )
                    attach_tooltip(tooltips.home.load_projects)
                    self.merge_projects_button: int = dpg.generate_uuid()
                    dpg.add_button(
                        label="Merge projects",
                        callback=lambda: signals.emit(
                            Signal.SELECT_PROJECT_FILES,
                            merge=True,
                        ),
                        tag=self.merge_projects_button,
                    )
                    attach_tooltip(tooltips.home.merge_projects)
                    self.clear_recent_projects_button: int = dpg.generate_uuid()
                    dpg.add_button(
                        label="Clear recent projects",
                        callback=lambda: signals.emit(
                            Signal.CLEAR_RECENT_PROJECTS,
                            selected_projects=self.get_selected_projects(),
                        ),
                        tag=self.clear_recent_projects_button,
                    )
                    attach_tooltip(tooltips.home.clear_recent_projects)

    def update_recent_projects_table(self, paths: List[str]):
        assert type(paths) is list, paths
        dpg.delete_item(self.recent_projects_table, children_only=True, slot=1)
        for path in paths:
            with dpg.table_row(
                parent=self.recent_projects_table,
            ):
                dpg.add_button(
                    label="Load",
                    callback=lambda s, a, u: signals.emit(
                        Signal.LOAD_PROJECT_FILES,
                        paths=[u],
                    ),
                    user_data=path,
                )
                attach_tooltip(tooltips.home.load)
                dpg.add_text(basename(path))
                attach_tooltip(path)
                dpg.add_checkbox(
                    user_data=path,
                    callback=lambda s, a, u: self.updated_selection(),
                )
                attach_tooltip(tooltips.recent_projects.checkbox)

    def updated_selection(self):
        paths: List[str] = self.get_selected_projects()
        if len(paths) > 1:
            dpg.set_item_label(
                self.load_projects_button,
                "Load selected projects",
            )
            dpg.set_item_label(
                self.merge_projects_button,
                "Merge selected projects",
            )
            dpg.set_item_label(
                self.clear_recent_projects_button,
                "Clear selected recent projects",
            )
        elif len(paths) == 1:
            dpg.set_item_label(
                self.load_projects_button,
                "Load selected project",
            )
            dpg.set_item_label(
                self.merge_projects_button,
                "Merge selected projects",
            )
            dpg.set_item_label(
                self.clear_recent_projects_button,
                "Clear selected recent project",
            )
        else:
            dpg.set_item_label(
                self.load_projects_button,
                "Load project(s)",
            )
            dpg.set_item_label(
                self.merge_projects_button,
                "Merge projects",
            )
            dpg.set_item_label(
                self.clear_recent_projects_button,
                "Clear recent projects",
            )

    def get_selected_projects(self) -> List[str]:
        paths: List[str] = []
        row: int
        for row in dpg.get_item_children(self.recent_projects_table, slot=1):
            checkbox: int = dpg.get_item_children(row, slot=1)[-2]
            assert "Checkbox" in dpg.get_item_type(checkbox), dpg.get_item_type(
                checkbox
            )
            if dpg.get_value(checkbox):
                path: Optional[str] = dpg.get_item_user_data(checkbox)
                assert type(path) is str, path
                paths.append(path)
        return paths


class ProjectTabBar:
    def __init__(self):
        self.tab_bar: int = dpg.generate_uuid()
        with dpg.tab_bar(
            callback=lambda s, a, u: signals.emit(
                Signal.SELECT_PROJECT_TAB
                if dpg.get_item_user_data(a) is not None
                else Signal.SELECT_HOME_TAB,
                uuid=dpg.get_item_user_data(a),
            ),
            tag=self.tab_bar,
        ):
            self.home_tab: HomeTab = HomeTab()

    def select_tab(self, project_tab: ProjectTab):
        dpg.set_value(self.tab_bar, project_tab.tab)

    def select_home_tab(self):
        dpg.set_value(self.tab_bar, self.home_tab.tab)

    def select_next_tab(self):
        tabs: List[int] = dpg.get_item_children(self.tab_bar, slot=1)
        index: int = tabs.index(dpg.get_value(self.tab_bar)) + 1
        dpg.set_value(self.tab_bar, tabs[index % len(tabs)])

    def select_previous_tab(self):
        tabs: List[int] = dpg.get_item_children(self.tab_bar, slot=1)
        index: int = tabs.index(dpg.get_value(self.tab_bar)) - 1
        dpg.set_value(self.tab_bar, tabs[index % len(tabs)])


class MenuBar:
    def __init__(self):
        button: int
        with dpg.menu_bar():
            with dpg.menu(label="File"):
                dpg.add_menu_item(
                    label="New project",
                    callback=lambda: signals.emit(Signal.NEW_PROJECT),
                )
                dpg.add_menu_item(
                    label="Load project",
                    callback=lambda: signals.emit(Signal.SELECT_PROJECT_FILES),
                )
                button = dpg.add_menu_item(
                    label="Save project",
                    enabled=False,
                    callback=lambda: signals.emit(Signal.SAVE_PROJECT),
                )
                signals.register(
                    Signal.SELECT_HOME_TAB,
                    lambda b=button, *args, **kwargs: dpg.disable_item(b),
                )
                signals.register(
                    Signal.SELECT_PROJECT_TAB,
                    lambda b=button, *args, **kwargs: dpg.enable_item(b),
                )
                button = dpg.add_menu_item(
                    label="Save project as",
                    enabled=False,
                    callback=lambda: signals.emit(Signal.SAVE_PROJECT_AS),
                )
                signals.register(
                    Signal.SELECT_HOME_TAB,
                    lambda b=button, *args, **kwargs: dpg.disable_item(b),
                )
                signals.register(
                    Signal.SELECT_PROJECT_TAB,
                    lambda b=button, *args, **kwargs: dpg.enable_item(b),
                )
                button = dpg.add_menu_item(
                    label="Close project",
                    enabled=False,
                    callback=lambda: signals.emit(Signal.CLOSE_PROJECT),
                )
                signals.register(
                    Signal.SELECT_HOME_TAB,
                    lambda b=button, *args, **kwargs: dpg.disable_item(b),
                )
                signals.register(
                    Signal.SELECT_PROJECT_TAB,
                    lambda b=button, *args, **kwargs: dpg.enable_item(b),
                )
                dpg.add_menu_item(label="Exit", callback=dpg.stop_dearpygui)
            with dpg.menu(label="Edit"):
                dpg.add_menu_item(
                    label="Undo",
                    enabled=False,
                    callback=lambda s, a, u: signals.emit(Signal.UNDO_PROJECT_ACTION),
                )
                button = dpg.last_item()
                signals.register(
                    Signal.SELECT_HOME_TAB,
                    lambda b=button, *args, **kwargs: dpg.disable_item(b),
                )
                signals.register(
                    Signal.SELECT_PROJECT_TAB,
                    lambda b=button, *args, **kwargs: dpg.enable_item(b),
                )
                dpg.add_menu_item(
                    label="Redo",
                    enabled=False,
                    callback=lambda s, a, u: signals.emit(Signal.REDO_PROJECT_ACTION),
                )
                button = dpg.last_item()
                signals.register(
                    Signal.SELECT_HOME_TAB,
                    lambda b=button, *args, **kwargs: dpg.disable_item(b),
                )
                signals.register(
                    Signal.SELECT_PROJECT_TAB,
                    lambda b=button, *args, **kwargs: dpg.enable_item(b),
                )
            with dpg.menu(label="Settings"):
                dpg.add_menu_item(
                    label="Appearance",
                    callback=lambda: signals.emit(Signal.SHOW_SETTINGS_APPEARANCE),
                )
                dpg.add_menu_item(
                    label="Defaults",
                    callback=lambda: signals.emit(Signal.SHOW_SETTINGS_DEFAULTS),
                )
                dpg.add_menu_item(
                    label="Keybindings",
                    callback=lambda: signals.emit(Signal.SHOW_SETTINGS_KEYBINDINGS),
                )
            with dpg.menu(label="Help"):
                dpg.add_menu_item(
                    label="About", callback=lambda: signals.emit(Signal.SHOW_HELP_ABOUT)
                )
                dpg.add_menu_item(
                    label="Changelog",
                    callback=lambda: signals.emit(Signal.SHOW_CHANGELOG),
                )
                dpg.add_menu_item(
                    label="Check for updates",
                    callback=lambda: signals.emit(Signal.CHECK_UPDATES),
                )
                dpg.add_menu_item(
                    label="Licenses",
                    callback=lambda: signals.emit(Signal.SHOW_HELP_LICENSES),
                )


class ProgramWindow:
    def __init__(self):
        self.window: int = dpg.generate_uuid()
        with dpg.window(tag=self.window):
            self.menu_bar: MenuBar = MenuBar()
            self.project_tab_bar: ProjectTabBar = ProjectTabBar()
        self.busy_message: BusyMessage = BusyMessage()
        self.error_message: ErrorMessage = ErrorMessage()

    def select_tab(self, project_tab: ProjectTab):
        self.project_tab_bar.select_tab(project_tab)

    def select_home_tab(self):
        self.project_tab_bar.select_home_tab()

    def select_next_tab(self):
        self.project_tab_bar.select_next_tab()

    def select_previous_tab(self):
        self.project_tab_bar.select_previous_tab()

    def get_selected_projects(self) -> List[str]:
        return self.project_tab_bar.home_tab.get_selected_projects()
