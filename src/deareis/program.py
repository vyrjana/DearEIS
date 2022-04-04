# Copyright 2022 DearEIS developers
# DearEIS is licensed under the GPLv3 or later (https://www.gnu.org/licenses/gpl-3.0.html).
# The licenses of DearEIS' dependencies and/or sources of portions of code are included in
# the LICENSES folder.

from numpy.random import seed
from deareis.arguments import Namespace, parse
from multiprocessing import set_start_method
from deareis.project import Project, restore_state
import deareis.themes as themes
import dearpygui.dearpygui as dpg
from deareis.file_dialog import file_dialog
from deareis.utility import (
    attach_tooltip,
    is_alt_down,
    is_control_down,
    is_shift_down,
    window_pos_dims,
)
from traceback import format_exc
from typing import Dict, IO, List, Tuple, Optional
from os import remove
from os.path import basename, dirname, exists, splitext
from deareis.config import CONFIG
from deareis.state import STATE
from deareis.licenses import show_license_window
from deareis.settings.defaults_settings import show_defaults_settings_window
from deareis.settings.appearance_settings import show_appearance_settings_window
import deareis.keyboard_shortcuts as keyboard_shortcuts
from deareis.version import PACKAGE_VERSION


seed(42)


class ErrorMessage:
    def __init__(self):
        self.window: int = dpg.generate_uuid()
        self.width: int = 720
        self.height: int = 540

    def show(self, msg: str) -> int:
        assert type(msg) is str
        if msg.strip() == "":
            return -1
        dpg.split_frame(delay=100)
        x: int
        y: int
        w: int
        h: int
        x, y, w, h = window_pos_dims(self.width, self.height)
        if dpg.does_item_exist(self.window):
            dpg.delete_item(self.window, children_only=True)
            dpg.show_item(self.window)
            dpg.configure_item(
                self.window,
                pos=(
                    x,
                    y,
                ),
                width=w,
                height=h,
            )
        else:
            dpg.add_window(
                label="ERROR",
                tag=self.window,
                no_resize=True,
                modal=True,
                pos=(
                    x,
                    y,
                ),
                width=w,
                height=h,
            )
        with dpg.group(parent=self.window):
            dpg.add_text(
                "The very end of the traceback (see below) may offer a hint on how to solve the cause for the error that just occurred. If it doesn't, then please copy the traceback to your clipboard and include it in a bug report. Bug reports can be submitted at github.com/vyrjana/DearEIS/issues.",
                wrap=700,
            )
            with dpg.child_window(width=-1, height=-24):
                dpg.add_text(msg, wrap=700)
            dpg.add_button(
                label="Copy to clipboard",
                callback=lambda: dpg.set_clipboard_text(msg),
            )
        return self.window


class WorkingIndicator:
    def __init__(self):
        self.window: int = dpg.generate_uuid()
        self.message_spacer: int = dpg.generate_uuid()
        self.message_text: int = dpg.generate_uuid()
        self.progress_bar: int = dpg.generate_uuid()
        self.width: int = 159
        self.height: int = 159
        self.message_wrap: int = 140
        self.x: int = -1
        self.y: int = -1
        self._assemble()

    def _assemble(self):
        with dpg.window(
            tag=self.window,
            show=False,
            no_move=True,
            no_resize=True,
            no_close=True,
            modal=True,
            no_background=True,
            menubar=False,
            autosize=True,
            no_title_bar=True,
        ):
            dpg.add_loading_indicator(
                radius=11,
                style=0,
                speed=2,
                color=(
                    66,
                    139,
                    255,
                    190,
                ),
            )
            with dpg.group(horizontal=True):
                dpg.add_spacer(tag=self.message_spacer)
                dpg.add_text(tag=self.message_text, wrap=self.message_wrap)
            dpg.add_progress_bar(
                width=self.width - 16,
                height=12,
                tag=self.progress_bar,
            )

    def resize(self, width: int, height: int):
        assert type(width) is int
        assert type(height) is int
        self.x = round((width - self.width) / 2)
        self.y = round((height - self.height) / 2)
        dpg.configure_item(
            self.window,
            pos=(
                self.x,
                self.y,
            ),
        )

    def show(self, message: str = "", progress: float = -1.0) -> int:
        assert type(message) is str
        assert type(progress) is float and progress <= 1.0
        if not dpg.is_item_shown(self.window):
            dpg.split_frame(delay=100)
            dpg.show_item(self.window)
        if self.x < 0:
            self.resize(dpg.get_viewport_width(), dpg.get_viewport_height())
            dpg.configure_item(
                self.window,
                pos=(
                    self.x,
                    self.y,
                ),
            )
        if message == "":
            dpg.hide_item(self.message_text)
        else:
            dpg.show_item(self.message_text)
            dpg.set_item_width(
                self.message_spacer,
                max(
                    0,
                    (
                        self.width
                        - dpg.get_text_size(message, wrap_width=self.message_wrap)[0]
                    )
                    / 2
                    - 16,
                ),
            )
            dpg.set_value(self.message_text, message)
        if progress < 0.0:
            dpg.hide_item(self.progress_bar)
        else:
            dpg.show_item(self.progress_bar)
            dpg.configure_item(
                self.progress_bar,
                default_value=progress,
            )
        return self.window

    def hide(self):
        dpg.hide_item(self.window)
        # Trying to show another modal window immediately afterwards might not work unless we wait
        dpg.split_frame(delay=100)


class Program:
    def __init__(self):
        self.window: int = dpg.generate_uuid()
        self.tab_bar: int = dpg.generate_uuid()
        self.home_tab: int = dpg.generate_uuid()
        self.recent_projects_table: int = dpg.generate_uuid()
        # State
        self.error_message: ErrorMessage = None
        self.working_indicator: WorkingIndicator = None
        self.projects: List[Project] = []
        self.modal_window: int = -1
        #
        self._assemble()
        self._assign_handlers()
        dpg.set_exit_callback(self.exit_callback)

    def _assemble(self):
        with dpg.window(tag=self.window):
            with dpg.menu_bar():
                with dpg.menu(label="File"):
                    dpg.add_menu_item(label="New project", callback=self.new_project)
                    dpg.add_menu_item(
                        label="Load project", callback=self.select_project_files
                    )
                    dpg.add_menu_item(
                        label="Save project",
                        callback=lambda: self.save_project(False),
                    )
                    dpg.add_menu_item(
                        label="Save project as",
                        callback=lambda: self.save_project(True),
                    )
                    dpg.add_menu_item(
                        label="Close project", callback=lambda: self.close_project()
                    )
                    dpg.add_menu_item(label="Exit", callback=self.exit_program)
                with dpg.menu(label="Edit"):
                    dpg.add_menu_item(
                        label="Undo",
                        callback=self.undo,
                    )
                    dpg.add_menu_item(
                        label="Redo",
                        callback=self.redo,
                    )
                with dpg.menu(label="Settings"):
                    dpg.add_menu_item(
                        label="Appearance",
                        callback=show_appearance_settings_window,
                    )
                    dpg.add_menu_item(
                        label="Defaults",
                        callback=show_defaults_settings_window,
                    )
                with dpg.menu(label="Help"):
                    dpg.add_menu_item(
                        label="Keybindings", callback=self.show_keybindings_window
                    )
                    dpg.add_menu_item(label="Licenses", callback=show_license_window)
                    dpg.add_menu_item(label="About", callback=self.show_about_window)
            with dpg.tab_bar(tag=self.tab_bar):
                with dpg.tab(label="Home", tag=self.home_tab):
                    dpg.add_text("Recent projects")
                    with dpg.table(
                        borders_outerV=True,
                        borders_outerH=True,
                        borders_innerV=True,
                        borders_innerH=True,
                        scrollY=True,
                        freeze_rows=1,
                        height=-40,
                        tag=self.recent_projects_table,
                    ):
                        pass
                    with dpg.child_window():
                        with dpg.group(horizontal=True):
                            dpg.add_button(
                                label="New project", callback=self.new_project
                            )
                            dpg.add_button(
                                label="Load project",
                                callback=self.select_project_files,
                            )
        self.update_recent_projects_table()
        self.error_message = ErrorMessage()
        self.working_indicator = WorkingIndicator()
        dpg.set_viewport_resize_callback(self.viewport_resized)

    def _assign_handlers(self):
        keys: List[int] = [
            dpg.mvKey_0,
            dpg.mvKey_1,
            dpg.mvKey_2,
            dpg.mvKey_3,
            dpg.mvKey_4,
            dpg.mvKey_5,
            dpg.mvKey_6,
            dpg.mvKey_7,
            dpg.mvKey_8,
            dpg.mvKey_9,
            dpg.mvKey_Down,
            dpg.mvKey_F1,
            dpg.mvKey_N,
            dpg.mvKey_O,
            dpg.mvKey_Up,
        ]
        with dpg.handler_registry():
            key: int
            for key in keys:
                dpg.add_key_release_handler(
                    key=key,
                    callback=self.keybinding_handler,
                )

    def keybinding_handler(self, sender: int, key: int):
        assert type(sender) is int
        assert type(key) is int
        if self.modal_window >= 0:
            modal_window_exists: bool = dpg.does_item_exist(self.modal_window)
            if modal_window_exists and dpg.is_item_shown(self.modal_window):
                return
            elif (
                modal_window_exists
                and self.modal_window != self.error_message.window
                and self.modal_window != self.working_indicator.window
            ):
                dpg.delete_item(self.modal_window)
            self.modal_window = -1
        if is_control_down() and is_shift_down():
            pass
        elif is_control_down() and is_alt_down():
            pass
        elif is_alt_down() and is_shift_down():
            pass
        elif is_control_down():
            if key == dpg.mvKey_N:  # Create a new project
                self.new_project()
            elif key == dpg.mvKey_O:
                self.select_project_files()
        elif is_alt_down():
            if (  # Go to the nth project tab
                key == dpg.mvKey_1
                or key == dpg.mvKey_2
                or key == dpg.mvKey_3
                or key == dpg.mvKey_4
                or key == dpg.mvKey_5
                or key == dpg.mvKey_6
                or key == dpg.mvKey_7
                or key == dpg.mvKey_8
            ):
                keyboard_shortcuts.go_to_top_tab(
                    self,
                    index=[
                        dpg.mvKey_1,
                        dpg.mvKey_2,
                        dpg.mvKey_3,
                        dpg.mvKey_4,
                        dpg.mvKey_5,
                        dpg.mvKey_6,
                        dpg.mvKey_7,
                        dpg.mvKey_8,
                    ].index(key),
                )
            elif key == dpg.mvKey_9:  # Go to the last project tab
                keyboard_shortcuts.go_to_top_tab(self, index=-1)
            elif key == dpg.mvKey_0:  # Go to the home tab
                keyboard_shortcuts.go_to_home_tab(self)
            elif key == dpg.mvKey_Down:  # Cycle top-level tabs
                keyboard_shortcuts.go_to_top_tab(self, step=1)
            elif key == dpg.mvKey_Up:  # Cycle top-level tabs
                keyboard_shortcuts.go_to_top_tab(self, step=-1)
        elif is_shift_down():
            pass
        else:
            if key == dpg.mvKey_F1:
                self.show_keybindings_window()

    def viewport_resized(self, sender: int, dims: Tuple[int, int, int, int]):
        assert type(sender) is int
        assert (
            type(dims) is tuple
            and len(dims) == 4
            and all(map(lambda _: type(_) is int, dims))
        )
        width: int
        height: int
        width, height, _, _ = dims
        self.working_indicator.resize(width, height)

    def update_recent_projects_table(self, paths: List[str] = []):
        assert type(paths) is list and all(map(lambda _: type(_) is str, paths))
        recent_paths: List[str] = STATE.get_recent_projects()
        old: str = "\n".join(recent_paths)
        path: str
        for path in paths:
            while path in recent_paths:
                recent_paths.remove(path)
            recent_paths.insert(0, path)
        if "\n".join(recent_paths) != old:
            STATE.update_recent_projects(recent_paths)
        if not dpg.does_item_exist(self.recent_projects_table):
            return
        dpg.delete_item(self.recent_projects_table, children_only=True)
        dpg.add_table_column(
            label="", width_fixed=True, parent=self.recent_projects_table
        )
        dpg.add_table_column(label="Filename", parent=self.recent_projects_table)
        for path in recent_paths:
            with dpg.table_row(parent=self.recent_projects_table):
                dpg.add_button(
                    label="Load",
                    callback=lambda s, a, u: self.load_projects([u]),
                    user_data=path,
                )
                dpg.add_text(splitext(basename(path))[0])
                attach_tooltip(path)

    def new_project(self) -> Project:
        project: Project = Project(self.tab_bar)
        project.error_message = self.error_message
        project.working_indicator = self.working_indicator
        project.close_callback = self.close_project
        project.save_callback = self.project_saved
        dpg.set_value(self.tab_bar, project.tab)
        self.projects.append(project)
        return project

    def project_saved(self, project: Project):
        assert type(project) is Project
        self.update_recent_projects_table([project.path])

    def close_project(self, project: Optional[Project] = None):
        assert type(project) is Project or project is None
        if project is not None:
            if project not in self.projects:
                return
            self.projects.remove(project)
            if project.path != "" and exists(project.path):
                self.update_recent_projects_table([project.path])
        else:
            if len(self.projects) == 0:
                return
            tab: int = dpg.get_value(self.tab_bar)
            for project in self.projects:
                if project.tab == tab:
                    project.close()
                    break

    def undo(self):
        if len(self.projects) == 0:
            return
        tab: int = dpg.get_value(self.tab_bar)
        for project in self.projects:
            if project.tab == tab:
                project.undo()
                break

    def redo(self):
        if len(self.projects) == 0:
            return
        tab: int = dpg.get_value(self.tab_bar)
        for project in self.projects:
            if project.tab == tab:
                project.redo()
                break

    def exit_callback(self):
        # Called on the last frame (i.e. no going back from here).
        serialization_queue: List[Project] = []
        recent_projects_queue: List[str] = []
        while self.projects:
            project: Project = self.projects.pop()
            if project.is_dirty:
                serialization_queue.append(project)
            if project.path != "" and exists(project.path):
                recent_projects_queue.append(project.path)
        if len(serialization_queue) > 0:
            STATE.serialize_projects(serialization_queue)
        if len(recent_projects_queue) > 0:
            self.update_recent_projects_table(recent_projects_queue)

    def exit_program(self):
        # Gracefully exiting the program
        project: Project
        for project in self.projects:
            if not project.is_dirty:
                continue
            dpg.set_value(self.tab_bar, project.tab)
            project.close()
            return
        dpg.stop_dearpygui()

    def load_projects(self, paths: List[str], sender: int = -1):
        assert type(paths) is list and all(map(lambda _: type(_) is str, paths)), paths
        assert type(sender) is int
        if sender >= 0:
            dpg.delete_item(sender)
        loaded_projects: List[str] = []
        num_paths: int = len(paths)
        try:
            n: int
            path: str
            for n, path in enumerate(paths):
                self.modal_window = self.working_indicator.show(
                    f"Loading projects: {n + 1}/{num_paths}", n / num_paths
                )
                if not exists(path):
                    continue
                already_open: bool = False
                project: Project
                for project in self.projects:
                    if project.path == path:
                        dpg.set_value(self.tab_bar, project.tab)
                        already_open = True
                        break
                if already_open:
                    continue
                project = self.new_project()
                fp: IO
                with open(path, "r") as fp:
                    try:
                        restore_state(fp.read(), project)
                    except Exception:
                        self.modal_window = self.error_message.show(format_exc())
                        print(format_exc())
                        project.close()
                        continue
                    project.path = path
                    project.recent_directory = dirname(path)
                loaded_projects.append(path)
        except Exception:
            self.modal_window = self.error_message.show(format_exc())
            print(format_exc())
            self.working_indicator.hide()
            return
        self.working_indicator.hide()
        if len(loaded_projects) > 0:
            self.update_recent_projects_table(loaded_projects)

    def select_project_files(self):
        recent_projects: List[str] = STATE.get_recent_projects()
        self.modal_window = file_dialog(
            recent_projects[0]
            if len(recent_projects) > 0
            else STATE.get_data_directory(),
            "Select project to load",
            lambda s, a, u: self.load_projects(
                list(a.get("selections", {}).values()), s
            ),
            [".json"],
        )
        project: Project
        for project in self.projects:
            project.modal_window = self.modal_window

    def save_project(self, save_as: bool = False):
        assert type(save_as) is bool
        if len(self.projects) == 0:
            return
        tab: int = dpg.get_value(self.tab_bar)
        project: Project
        for project in self.projects:
            if project.tab == tab:
                project.save(save_as)
                break

    def import_data_files(self, paths: List[str]):
        assert type(paths) is list and all(map(lambda _: type(_) is str, paths))
        self.new_project().parse_dataset_files(paths)

    def show_keybindings_window(self):
        x: int
        y: int
        w: int
        h: int
        x, y, w, h = window_pos_dims(720)
        window: int = dpg.generate_uuid()
        key_handler: int = dpg.generate_uuid()

        def close_window():
            if dpg.does_item_exist(window):
                dpg.delete_item(window)
            if dpg.does_item_exist(key_handler):
                dpg.delete_item(key_handler)

        with dpg.handler_registry(tag=key_handler):
            dpg.add_key_release_handler(
                key=dpg.mvKey_Escape,
                callback=close_window,
            )

        with dpg.window(
            label="Keybindings",
            modal=True,
            pos=(
                x,
                y,
            ),
            width=w,
            height=h,
            no_move=True,
            no_resize=True,
            on_close=close_window,
            tag=window,
        ):
            header_height: int = 18
            row_height: int = 23
            definitions: Dict[str, Dict[str, str]] = {
                "Program": {
                    "F1": "Open up the keybindings window.",
                    "Alt+Arrow down": "Go to the next project tab.",
                    "Alt+Arrow up": "Go to the previous project tab.",
                    "Alt+1-8": "Go to the nth project tab.",
                    "Alt+9": "Go to the last project tab.",
                    "Alt+0": "Go to the home tab.",
                    "Ctrl+N": "Create a new project tab.",
                    "Ctrl+O": "Open project.",
                    "Escape": "Close modal window.",
                    "Enter": "Confirm/accept changes.",
                },
                "Project": {
                    "Page down": "Go to the next data set.",
                    "Page up": "Go to the previous data set.",
                    "Alt+Shift+Arrow down": "Go to the next tab.",
                    "Alt+Shift+Arrow up": "Go to the previous tab.",
                    "Alt+Shift+1-8": "Go to the nth tab.",
                    "Alt+Shift+9": "Go to the last tab.",
                    "Alt+Shift+0": "Go to the first tab.",
                    "Ctrl+Shift+S": "Save project to a new path.",
                    "Ctrl+S": "Save project.",
                    "Ctrl+W": "Close project.",
                    "Ctrl+Y": "Redo the latest action.",
                    "Ctrl+Shift+Z": "Redo the latest action.",
                    "Ctrl+Z": "Undo the latest action.",
                    # "": "",
                },
                "Data sets tab": {
                    "Alt+A": "Create an average of multiple data sets.",
                    "Alt+B": "Show enlarged Bode plot.",
                    "Alt+C": "Copy the mask from another data set.",
                    "Alt+N": "Show enlarged Nyquist plot.",
                    "Alt+S": "Subtract impedance from the current data set.",
                    "Alt+T": "Toggle multiple points in the mask of the current data set.",
                    "Alt+L": "Load data files.",
                    "Alt+Delete": "Delete the current data set.",
                    "Alt+Shift+B": "Copy data from Bode plot as CSV.",
                    "Alt+Shift+N": "Copy data from Nyquist plot as CSV.",
                    "Page up": "Go to the next data set.",
                    "Page down": "Go to the previous data set.",
                    # "": "",
                },
                "Kramers-Kronig tab": {
                    "Alt+A": "Apply settings from the current result.",
                    "Alt+B": "Show enlarged Bode plot.",
                    "Alt+C": "Copy the selected output of the current result.",
                    "Alt+N": "Show enlarged Nyquist plot.",
                    "Alt+R": "Show enlarged residuals plot.",
                    "Alt+Delete": "Delete the current result.",
                    "Alt+Enter": "Perform a test.",
                    "Ctrl+Enter": "Perform a test.",
                    "Alt+Page down": "Go to the next result.",
                    "Alt+Page up": "Go to the previous result.",
                    "Alt+Shift+B": "Copy data from Bode plot as CSV.",
                    "Alt+Shift+N": "Copy data from Nyquist plot as CSV.",
                    "Alt+Shift+R": "Copy data from residuals plot as CSV.",
                    "Page up": "Go to the next data set.",
                    "Page up_1": "Go to the next test result (while in the exploratory results window).",
                    "Page down": "Go to the previous data set.",
                    "Page down_2": "Go to the previous test result (while in the exploratory results window).",
                    # "": "",
                },
                "Fitting tab": {
                    "Alt+A": "Apply settings from the current result.",
                    "Alt+B": "Show enlarged Bode plot.",
                    "Alt+C": "Copy the selected output of the current result.",
                    "Alt+E": "Open circuit editor.",
                    "Alt+N": "Show enlarged Nyquist plot.",
                    "Alt+R": "Show enlarged residuals plot.",
                    "Alt+Delete": "Delete the current result.",
                    "Alt+Enter": "Perform a fit.",
                    "Alt+Enter_": "Accept the current circuit (while in the circuit editor window).",
                    "Ctrl+Enter": "Perform a fit.",
                    "Ctrl+Enter_": "Accept the current circuit (while in the circuit editor window).",
                    "Alt+Page down": "Go to the next result.",
                    "Alt+Page up": "Go to the previous result.",
                    "Alt+Shift+B": "Copy data from Bode plot as CSV.",
                    "Alt+Shift+N": "Copy data from Nyquist plot as CSV.",
                    "Alt+Shift+R": "Copy data from residuals plot as CSV.",
                    "Ctrl+Spacebar": "Show suggestions/information related to CDC input.",
                    "Page up": "Go to the next data set.",
                    "Page down": "Go to the previous data set.",
                    # "": "",
                },
                "Simulation tab": {
                    "Alt+Shift+B": "Copy data from Bode plot as CSV.",
                    "Alt+Shift+N": "Copy data from Nyquist plot as CSV.",
                    "Alt+A": "Apply settings from the current result.",
                    "Alt+B": "Show enlarged Bode plot.",
                    "Alt+C": "Copy the selected output of the current result.",
                    "Alt+E": "Open circuit editor.",
                    "Alt+N": "Show enlarged Nyquist plot.",
                    "Alt+Enter": "Perform a simulation.",
                    "Ctrl+Enter": "Perform a simulation.",
                    "Alt+Delete": "Delete the current result.",
                    "Alt+Page down": "Go to the next result.",
                    "Alt+Page up": "Go to the previous result.",
                    "Ctrl+Spacebar": "Show suggestions/information related to CDC input.",
                    "Page up": "Go to the next data set.",
                    "Page down": "Go to the previous data set.",
                    # "": "",
                },
                "Plotting tab": {
                    "Alt+S": "Select all possible plot items.",
                    "Alt+Shift+S": "Unselect all possible plot items.",
                    "Alt+C": "Copy appearance settings from another plot.",
                    "Alt+Shift+C": "Copy data from plot as CSV.",
                    "Alt+Enter": "Create a new plot.",
                    "Ctrl+Enter": "Create a new plot.",
                    "Alt+Delete": "Delete the current plot.",
                    "Alt+Page down": "Go to the next plot type.",
                    "Alt+Page up": "Go to the previous plot type.",
                    "Page up": "Go to the next data set.",
                    "Page down": "Go to the previous data set.",
                    # "": "",
                },
            }
            key_header: str = "Key combination"
            description_header: str = "Description"
            key_pad: int = max(
                max(
                    list(
                        map(
                            lambda _: max(list(map(len, _.keys()))),
                            definitions.values(),
                        )
                    )
                ),
                len(key_header),
            )
            section: str
            keys_to_descriptions: Dict[str, str]
            for section, keys_to_descriptions in definitions.items():
                with dpg.collapsing_header(label=section, default_open=True):
                    with dpg.table(
                        borders_outerV=True,
                        borders_outerH=True,
                        borders_innerV=True,
                        borders_innerH=True,
                        scrollY=True,
                        freeze_rows=1,
                        height=header_height + row_height * len(keys_to_descriptions),
                    ):
                        dpg.add_table_column(
                            label=key_header.rjust(key_pad), width_fixed=True
                        )
                        dpg.add_table_column(label=description_header, width_fixed=True)
                        key: str
                        for key in sorted(
                            keys_to_descriptions.keys(),
                            key=lambda _: (
                                _.count("+"),
                                _,
                            ),
                        ):
                            description: str = keys_to_descriptions[key]
                            with dpg.table_row():
                                dpg.add_text(
                                    (key if "_" not in key else "").rjust(key_pad)
                                )
                                dpg.add_text(description)
                                assert description.endswith("."), (
                                    key,
                                    description,
                                )
                                attach_tooltip(description)
                    dpg.add_spacer(height=8)
        self.modal_window = window
        project: Project
        for project in self.projects:
            project.modal_window = self.modal_window

    def show_about_window(self):
        x: int
        y: int
        w: int
        h: int
        x, y, w, h = window_pos_dims(210, 110)
        window: int = dpg.generate_uuid()
        key_handler: int = dpg.generate_uuid()

        def close_window():
            if dpg.does_item_exist(window):
                dpg.delete_item(window)
            if dpg.does_item_exist(key_handler):
                dpg.delete_item(key_handler)

        with dpg.handler_registry(tag=key_handler):
            dpg.add_key_release_handler(
                key=dpg.mvKey_Escape,
                callback=close_window,
            )

        with dpg.window(
            label="About",
            modal=True,
            pos=(
                x,
                y,
            ),
            width=w,
            height=h,
            no_move=True,
            no_resize=True,
            on_close=close_window,
            tag=window,
        ):
            dpg.add_text(
                f"DearEIS\n\nVersion: {PACKAGE_VERSION}\n\ngithub.com/vyrjana/DearEIS"
            )


def handle_args(args: Namespace, program: Program):
    if args.data_files:
        try:
            program.import_data_files(list(filter(exists, args.data_files)))
        except Exception:
            program.modal_window = program.error_message.show(format_exc())
            print(format_exc())
            return
    if args.project_files:
        try:
            program.load_projects(list(filter(exists, args.project_files)))
        except Exception:
            program.modal_window = program.error_message.show(format_exc())
            print(format_exc())
            return
    snapshots: List[Tuple[str, str, str]] = STATE.get_serialized_projects()
    num_snapshots: int = len(snapshots)
    n: int
    snapshot_path: str
    project_path: str
    state: str
    for n, (snapshot_path, project_path, state) in enumerate(snapshots):
        program.modal_window = program.working_indicator.show(
            f"Recovering snapshots: {n + 1}/{num_snapshots}",
            n / num_snapshots,
        )
        project: Project = program.new_project()
        try:
            restore_state(state, project, True)
            project.path = project_path
            project.recent_directory = dirname(project_path)
            remove(snapshot_path)
        except Exception:
            program.modal_window = program.error_message.show(format_exc())
            print(format_exc())
            project.close()
    program.working_indicator.hide()


def main():
    set_start_method("spawn")
    args: Namespace = parse()
    dpg.create_context()
    dpg.create_viewport(title="DearEIS")
    dpg.set_viewport_min_width(800)
    dpg.set_viewport_min_height(600)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    try:
        themes.initialize()
        program: Program = Program()
        dpg.set_frame_callback(1, lambda: handle_args(args, program))
        dpg.set_primary_window(program.window, True)
        dpg.start_dearpygui()
    except Exception:
        print(format_exc())
    finally:
        dpg.destroy_context()
        CONFIG.save()


if __name__ == "__main__":
    main()
