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

from importlib.machinery import SourceFileLoader
from os import getcwd
from os.path import (
    dirname,
    exists,
    isdir,
)
from types import ModuleType
from typing import (
    Callable,
    Dict,
    Optional,
    Type,
)
import dearpygui.dearpygui as dpg
import pyimpspec.circuit.registry as registry
from pyimpspec import (
    Element,
    get_elements,
)
from deareis.utility import calculate_window_position_dimensions
from deareis.signals import Signal
import deareis.signals as signals
from deareis.tooltips import attach_tooltip
import deareis.themes as themes
from deareis.gui.file_dialog import FileDialog
from deareis.enums import Action
from deareis.keybindings import (
    Keybinding,
    TemporaryKeybindingHandler,
)
from deareis.typing.helpers import Tag


DEFAULT_ELEMENTS: Dict[str, Type[Element]] = get_elements()
USER_DEFINED_ELEMENTS: Dict[str, Type[Element]] = {}


def update_path(path: str, path_input: int = -1):
    if path_input < 1:
        return

    assert isinstance(path, str), path

    if path == "" or exists(path):
        dpg.bind_item_theme(path_input, themes.path.valid)
    else:
        dpg.bind_item_theme(path_input, themes.path.invalid)

    dpg.set_value(path_input, path)


def update_table(table: int, elements: Dict[str, Type[Element]]):
    if table < 1:
        return

    dpg.delete_item(table, children_only=True, slot=1)

    Class: Type[Element]
    for Class in elements.values():
        with dpg.table_row(parent=table):
            dpg.add_text(Class.get_description())
            attach_tooltip(Class.get_extended_description())


def refresh(
    path: str = "",
    path_input: int = -1,
    close_window: Optional[Callable] = None,
):
    global USER_DEFINED_ELEMENTS
    key: str
    for key in USER_DEFINED_ELEMENTS:
        del registry._ELEMENTS[key]

    USER_DEFINED_ELEMENTS.clear()

    update_path(path, path_input)

    if close_window is not None:
        close_window()
        dpg.split_frame(delay=33)

    if path != "" and exists(path):
        signals.emit(
            Signal.SHOW_BUSY_MESSAGE,
            message="Loading user-defined elements...",
        )
        dpg.split_frame(delay=1000)
        loader = SourceFileLoader("user_defined_elements", path)
        mod = ModuleType(loader.name)
        loader.exec_module(mod)
        USER_DEFINED_ELEMENTS = {
            k: v for k, v in get_elements().items() if k not in DEFAULT_ELEMENTS
        }
        signals.emit(Signal.HIDE_BUSY_MESSAGE)

    if close_window is not None:
        signals.emit(Signal.SHOW_SETTINGS_USER_DEFINED_ELEMENTS)


def select_script(path_input: int, window: int, close_window: Callable):
    dir_path: str = dpg.get_value(path_input)
    if dir_path != "":
        if not isdir(dir_path):
            dir_path = dirname(dir_path)

    if dir_path == "" or not exists(dir_path):
        dir_path = getcwd()

    dpg.hide_item(window)
    dpg.split_frame(delay=33)

    FileDialog(
        cwd=dir_path,
        label="Select Python script",
        callback=lambda paths, *a, **k: refresh(
            paths[0] if len(paths) > 0 else "",
            path_input=path_input,
            close_window=close_window,
        ),
        cancel_callback=lambda: dpg.show_item(window),
        extensions=[".py"],
        multiple=False,
    )


class UserDefinedElementsSettings:
    def __init__(self, state):
        self.config = state.config
        self.create_window()
        self.register_keybindings()
        signals.emit(Signal.BLOCK_KEYBINDINGS, window=self.window, window_object=self)

    def create_window(self):
        x: int
        y: int
        w: int
        h: int
        x, y, w, h = calculate_window_position_dimensions(600, 540)

        self.window: Tag = dpg.generate_uuid()
        with dpg.window(
            label="Settings - User-defined elements",
            modal=True,
            pos=(
                x,
                y,
            ),
            width=w,
            height=h,
            no_resize=True,
            on_close=self.close,
            tag=self.window,
        ):
            attach_tooltip(
                """
The definitions for user-defined elements are NOT stored inside of project files. If a project depends on a user-defined element (e.g., the element is used in the circuit of a fit or simulation result), then the script defining the user-defined element must be loaded before opening the project.
""".strip(),
                parent=dpg.add_text(
                    "IMPORTANT! HOVER MOUSE CURSOR OVER THIS PART FOR DETAILS!"
                ),
            )

            with dpg.group(horizontal=True):
                self.path_input: Tag = dpg.generate_uuid()
                dpg.add_input_text(
                    default_value=self.config.user_defined_elements_path,
                    hint="Path to Python script/package",
                    width=-64,
                    on_enter=True,
                    callback=lambda s, a, u: update_path(a, s),
                    tag=self.path_input,
                )
                dpg.add_button(
                    label="Browse",
                    callback=lambda s, a, u: select_script(
                        path_input=self.path_input,
                        window=self.window,
                        close_window=self.close,
                    ),
                    width=-1,
                )

            update_path(dpg.get_value(self.path_input), self.path_input)
            attach_tooltip(
                """
An absolute path to a Python script/package that when loaded defines new elements using pyimpspec's API. See pyimpspec's API documentation for details and examples. User-defined elements can also be used to implement circuits that cannot be implemented using circuit description codes (CDCs).

Detected user-defined elements will be listed in the table below this input field. If there are no entries in the table below, then you may need to press the "Refresh" button or the path might be invalid.
    """.strip()
            )

            table: Tag = dpg.generate_uuid()
            with dpg.child_window(
                border=False,
                width=-2,
                height=-24,
                show=True,
            ):
                with dpg.table(
                    borders_outerV=True,
                    borders_outerH=True,
                    borders_innerV=True,
                    borders_innerH=True,
                    scrollY=True,
                    freeze_rows=1,
                    tag=table,
                ):
                    dpg.add_table_column(
                        label="Description",
                        width_fixed=False,
                    )
            update_table(table, USER_DEFINED_ELEMENTS)
            dpg.add_button(
                label="Refresh",
                width=-1,
                callback=self.refresh,
            )
            attach_tooltip(
                "Reload the Python script/package that contains the definitions for the user-defined elements."
            )

    def register_keybindings(self):
        callbacks: Dict[Keybinding, Callable] = {}
        # Cancel
        kb: Keybinding = Keybinding(
            key=dpg.mvKey_Escape,
            mod_alt=False,
            mod_ctrl=False,
            mod_shift=False,
            action=Action.CANCEL,
        )

        callbacks[kb] = self.close

        # Accept
        for kb in self.config.keybindings:
            if kb.action is Action.PERFORM_ACTION:
                break
        else:
            kb = Keybinding(
                key=dpg.mvKey_Return,
                mod_alt=True,
                mod_ctrl=False,
                mod_shift=False,
                action=Action.PERFORM_ACTION,
            )

        callbacks[kb] = self.refresh

        # Create the handler
        self.keybinding_handler: TemporaryKeybindingHandler = (
            TemporaryKeybindingHandler(callbacks=callbacks)
        )

    def close(self):
        path: str = dpg.get_value(self.path_input)
        if isinstance(path, str) and (path == "" or exists(path)):
            self.config.user_defined_elements_path = path

        if dpg.does_item_exist(self.window):
            dpg.delete_item(self.window)

        self.keybinding_handler.delete()

        signals.emit(Signal.UNBLOCK_KEYBINDINGS)

    def refresh(self):
        signals.emit(
            Signal.REFRESH_USER_DEFINED_ELEMENTS,
            path=dpg.get_value(self.path_input),
            path_input=self.path_input,
            close_window=self.close,
        )


def show_user_defined_elements_window(state):
    UserDefinedElementsSettings(state)
