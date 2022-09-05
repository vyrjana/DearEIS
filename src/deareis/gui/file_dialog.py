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

from os import (
    getcwd,
    makedirs,
    walk,
)
from os.path import (
    basename,
    exists,
    getmtime,
    getsize,
    islink,
    join,
    split,
    splitext,
)
from pathlib import Path
from typing import (
    Callable,
    Dict,
    List,
    Optional,
)
import dearpygui.dearpygui as dpg
from deareis.tooltips import attach_tooltip
from deareis.utility import (
    calculate_window_position_dimensions,
    format_timestamp,
    is_filtered_item_visible,
)
from deareis.keybindings import is_control_down, is_shift_down
from deareis.signals import Signal
import deareis.signals as signals
import deareis.themes as themes


class FileDialog:
    def __init__(
        self,
        *args,
        **kwargs,
    ):
        cwd: str = kwargs.get("cwd", getcwd())
        assert type(cwd) is str, cwd
        if not exists(cwd):
            cwd = getcwd()
        self._cwd: str = cwd
        label: str = kwargs.get("label", "File dialog")
        assert type(label) is str, label
        extensions: List[str] = kwargs.get("extensions", [".*"])
        assert type(extensions) is list and len(extensions) > 0, extensions
        default_extension: str = kwargs.get("default_extension", extensions[0])
        assert default_extension in extensions, (
            default_extension,
            extensions,
        )
        self._callback: Callable = kwargs["callback"]
        self._save: bool = kwargs.get("save", False)
        self._merge: bool = kwargs.get("merge", False)
        self._window: int = dpg.generate_uuid()
        x: int
        y: int
        w: int
        h: int
        x, y, w, h = calculate_window_position_dimensions()
        with dpg.window(
            label=label,
            modal=True,
            pos=(
                x,
                y,
            ),
            width=w,
            height=h,
            show=False,
            on_close=self.close,
            tag=self._window,
        ):
            with dpg.group(horizontal=True):
                if self._save:
                    dpg.add_button(label="N", callback=lambda: self.create_directory())
                    attach_tooltip("Create a new directory.")
                dpg.add_button(
                    label="R",
                    callback=lambda: self.reset_path(),
                )
                attach_tooltip(f"Reset to current working directory: '{self._cwd}'.")
                dpg.add_button(label="E", callback=lambda: self.edit_path())
                attach_tooltip("Edit the path via input.")
                self._path_combo: int = dpg.generate_uuid()
                dpg.add_combo(
                    tag=self._path_combo,
                    width=-1,
                    callback=lambda s, a, u: self.update_current_path(
                        u.get(a, self._cwd)
                    ),
                )
                self._path_input: int = dpg.generate_uuid()
                dpg.add_input_text(
                    hint="Path...",
                    callback=lambda s, a, u: self.update_current_path(a),
                    on_enter=True,
                    show=False,
                    width=-1,
                    tag=self._path_input,
                )
            with dpg.group(horizontal=True):
                dpg.add_button(label="C", callback=lambda: self.clear_search())
                attach_tooltip("Clear the search input.")
                self._search_input: int = dpg.generate_uuid()
                dpg.add_input_text(
                    hint="Search...",
                    width=-100 if not self._save else -1,
                    tag=self._search_input,
                    callback=lambda s, a, u: dpg.set_value(self._table, a.lower()),
                )
                self._extension_combo: int = dpg.generate_uuid()
                dpg.add_combo(
                    default_value=default_extension,
                    items=extensions,
                    callback=lambda: self.update_current_path(self.get_current_path()),
                    show=not self._save,
                    tag=self._extension_combo,
                    width=-1,
                )
            self._table: int = dpg.generate_uuid()
            with dpg.table(
                borders_outerV=True,
                borders_outerH=True,
                borders_innerV=True,
                borders_innerH=True,
                scrollY=True,
                freeze_rows=1,
                height=-24,
                tag=self._table,
            ):
                if not self._save:
                    dpg.add_table_column(
                        label="",
                        width_fixed=True,
                        width=24,
                    )
                dpg.add_table_column(
                    label="",
                    width_fixed=True,
                    width=24,
                )
                dpg.add_table_column(
                    label="Name",
                )
                dpg.add_table_column(
                    label="Size",
                    width_fixed=True,
                    width=200,
                )
                dpg.add_table_column(
                    label="Modified",
                    width_fixed=True,
                    width=200,
                )
            with dpg.group(horizontal=True):
                if not self._save:
                    dpg.add_button(
                        label=("Merge" if self._merge else "Load"),
                        callback=lambda: self.load_files(),
                    )
                    dpg.add_button(
                        label="Select all",
                        callback=lambda: self.select_files(state=True),
                    )
                    dpg.add_button(
                        label="Unselect all",
                        callback=lambda: self.select_files(state=False),
                    )
                else:
                    dpg.add_button(label="Save", callback=lambda: self.save_file())
                    self._name_input: int = dpg.generate_uuid()
                    dpg.add_input_text(
                        hint="Name...",
                        callback=lambda: self.save_file(),
                        on_enter=True,
                        width=-100,
                        tag=self._name_input,
                    )
                    self._name_extension_combo: int = dpg.generate_uuid()
                    dpg.add_combo(
                        default_value=default_extension,
                        items=extensions,
                        width=-1,
                        callback=lambda: self.update_current_path(
                            self.get_current_path()
                        ),
                        tag=self._name_extension_combo,
                    )
        self.update_current_path(self._cwd)
        self.show()

    def hide(self):
        dpg.hide_item(self._window)
        if dpg.does_item_exist(self._key_handler):
            dpg.delete_item(self._key_handler)
        signals.emit(Signal.UNBLOCK_KEYBINDINGS)

    def show(self):
        self._key_handler: int = dpg.generate_uuid()
        with dpg.handler_registry(tag=self._key_handler):
            dpg.add_key_release_handler(
                key=dpg.mvKey_Escape,
                callback=self.close,
            )
            if self._save:
                dpg.add_key_release_handler(
                    key=dpg.mvKey_N,
                    callback=lambda: self.create_directory(keybinding=True),
                )
            else:
                dpg.add_key_release_handler(
                    key=dpg.mvKey_A,
                    callback=lambda: self.select_files(keybinding=True),
                )
            dpg.add_key_release_handler(
                key=dpg.mvKey_R,
                callback=lambda: self.reset_path(keybinding=True),
            )
            dpg.add_key_release_handler(
                key=dpg.mvKey_E,
                callback=lambda: self.edit_path(keybinding=True),
            )
            dpg.add_key_release_handler(
                key=dpg.mvKey_F,
                callback=lambda: self.focus_search(keybinding=True),
            )
            dpg.add_key_release_handler(
                key=dpg.mvKey_C,
                callback=lambda: self.clear_search(keybinding=True),
            )
        dpg.show_item(self._window)
        if self._save:
            dpg.focus_item(self._name_input)
        signals.emit(Signal.BLOCK_KEYBINDINGS, window=self._window, window_object=None)

    def close(self):
        self.hide()
        dpg.delete_item(self._window)

    def create_directory(self, keybinding: bool = False):
        assert type(keybinding) is bool, keybinding
        if keybinding and not is_control_down():
            return
        self.hide()
        dpg.split_frame(delay=33)
        x: int
        y: int
        w: int
        h: int
        x, y, w, h = calculate_window_position_dimensions(400, 50)
        key_handler: int = dpg.generate_uuid()
        window: int = dpg.generate_uuid()
        name_input: int = dpg.generate_uuid()

        def close(path: str = ""):
            dpg.delete_item(window)
            dpg.delete_item(key_handler)
            dpg.split_frame()
            self.show()
            if path != "":
                self.update_current_path(path)

        def accept():
            name: str = dpg.get_value(name_input).strip()
            path: str = join(self.get_current_path(), name)
            if name != "" and not exists(path):
                try:
                    makedirs(path)
                except Exception:
                    pass
                close(path)
            else:
                close()

        with dpg.handler_registry(tag=key_handler):
            dpg.add_key_release_handler(
                key=dpg.mvKey_Escape,
                callback=close,
            )
            dpg.add_key_release_handler(
                key=dpg.mvKey_Return,
                callback=accept,
            )

        with dpg.window(
            label="Create folder",
            modal=True,
            pos=(
                x,
                y,
            ),
            width=w,
            height=h,
            show=False,
            on_close=close,
            tag=window,
        ):
            dpg.add_input_text(hint="Name...", width=-1, tag=name_input)
            dpg.add_button(label="Accept", callback=accept)

        dpg.show_item(window)
        dpg.split_frame()
        dpg.focus_item(name_input)
        signals.emit(Signal.BLOCK_KEYBINDINGS, window=window, window_object=None)

    def clear_search(self, keybinding: bool = False):
        assert type(keybinding) is bool, keybinding
        if keybinding and not is_control_down():
            return
        dpg.set_value(self._table, "")
        dpg.set_value(self._search_input, "")

    def focus_search(self, keybinding: bool = False):
        if keybinding and not is_control_down():
            return
        dpg.focus_item(self._search_input)

    def select_files(self, state: Optional[bool] = None, keybinding: bool = False):
        assert type(state) is bool or state is None, state
        assert type(keybinding) is bool, keybinding
        if keybinding:
            if not is_control_down():
                return
            if dpg.is_item_focused(self._path_input) or dpg.is_item_focused(
                self._search_input
            ):
                return
            state = not is_shift_down()
        assert state is not None
        filter_key: str = dpg.get_value(self._search_input).lower()
        files: Dict[int, Optional[str]] = {}
        row: int
        for row in dpg.get_item_children(self._table, slot=1):
            if not is_filtered_item_visible(row, filter_key):
                continue
            size_text: int = dpg.get_item_children(row, slot=1)[-2]
            if dpg.get_value(size_text) == "":
                continue
            files[row] = dpg.get_item_user_data(row)
        path: Optional[str]
        for row, path in files.items():
            checkbox: int = dpg.get_item_children(row, slot=1)[0]
            assert "mvCheckbox" in dpg.get_item_type(checkbox), dpg.get_item_type(
                checkbox
            )
            if state and path is None:
                dpg.set_value(checkbox, state)
                dpg.set_item_user_data(row, dpg.get_item_user_data(checkbox)[1])
            elif not state and path is not None:
                dpg.set_value(checkbox, state)
                dpg.set_item_user_data(row, None)

    def get_current_path(self) -> str:
        return dpg.get_value(self._path_combo)

    def reset_path(self, keybinding: bool = False):
        assert type(keybinding) is bool, keybinding
        if keybinding and not is_control_down():
            return
        self.update_current_path(self._cwd)

    def edit_path(self, keybinding: bool = False):
        assert type(keybinding) is bool, keybinding
        if keybinding and not is_control_down():
            return
        dpg.hide_item(self._path_combo)
        dpg.show_item(self._path_input)
        dpg.set_value(self._path_input, self.get_current_path())
        dpg.focus_item(self._path_input)

    def update_current_path(self, path: str):
        if not exists(path):
            return
        self.clear_search()
        self.update_path_combo(path)
        self.update_contents_table(path)

    def update_path_combo(self, path: str):
        dpg.hide_item(self._path_input)
        lookup: Dict[str, str] = {}
        items: List[str] = []
        a: str
        b: str
        suffix: str = ""
        a, b = split(path)
        while b != "":
            items.insert(0, b + suffix)
            lookup[b + suffix] = join(a, b)
            a, b = split(a)
            suffix += " "
        items.insert(0, a + suffix)
        lookup[a + suffix] = a
        dpg.configure_item(
            self._path_combo,
            default_value=path,
            items=items,
            user_data=lookup,
        )
        dpg.show_item(self._path_combo)

    def update_contents_table(self, root: str):
        extension_filter: str = dpg.get_value(
            self._extension_combo if not self._save else self._name_extension_combo
        ).lower()
        dpg.delete_item(self._table, children_only=True, slot=1)
        for _, dirs, files in walk(root):
            break
        dirs.sort()
        files.sort()
        dpg.push_container_stack(self._table)
        path: str
        directory: str
        for directory in dirs:
            path = join(root, directory)
            with dpg.table_row(filter_key=directory.lower()):
                if not self._save:
                    dpg.add_checkbox(enabled=False, show=False)
                if islink(path):
                    path = str(Path(path).resolve())
                    dpg.add_text("L")
                    attach_tooltip(f"Link to directory: '{path}'")
                else:
                    dpg.add_text("D")
                    attach_tooltip("Directory")
                dpg.bind_item_theme(
                    dpg.add_button(
                        label=directory,
                        callback=lambda s, a, u: self.update_current_path(u),
                        user_data=path,
                        width=-1,
                    ),
                    themes.file_dialog.folder_button,
                )
                dpg.add_text("", show=False)
                dpg.add_text("", show=False)
        for file in files:
            if not (
                extension_filter == ".*" or file.lower().endswith(extension_filter)
            ):
                continue
            path = join(root, file)
            link: bool = False
            if islink(path):
                path = str(Path(path).resolve())
                if not exists(path):
                    continue
                link = True
            row: int
            with dpg.table_row(filter_key=file.lower()) as row:
                if not self._save:
                    dpg.add_checkbox(
                        callback=lambda s, a, u: dpg.set_item_user_data(
                            u[0], u[1] if a else None
                        ),
                        user_data=(
                            row,
                            path,
                        ),
                    )
                    attach_tooltip(
                        "Select multiple files to "
                        + ("merge." if self._merge else "load.")
                    )
                if link:
                    dpg.add_text("L")
                    attach_tooltip(f"Link to file: '{path}'")
                else:
                    dpg.add_text("F")
                    attach_tooltip("File")
                dpg.bind_item_theme(
                    dpg.add_button(
                        label=file,
                        callback=lambda s, a, u: self.click_file(u),
                        user_data=path,
                        width=-1,
                    ),
                    themes.file_dialog.file_button,
                )
                dpg.add_text(self.format_size(getsize(path)))
                dpg.add_text(format_timestamp(getmtime(path)))
        dpg.pop_container_stack()

    def format_size(self, num_bytes: int) -> str:
        suffixes: List[str] = [
            "B",
            "KiB",
            "MiB",
            "GiB",
            "TiB",
            "PiB",
            "EiB",
            "ZiB",
            "YiB",
        ]
        i: int = 0
        value: float = float(num_bytes)
        while value > 1.0:
            i += 1
            value /= 1024
        i -= 1
        if i < 0:
            i = 0
        return f"{float(num_bytes) / pow(1024, i):.3g} {suffixes[i]}".ljust(9)

    def click_file(self, path: str):
        if not self._save:
            if self._merge:
                return
            self.hide()
            self._callback(paths=[path])
            self.close()
        else:
            dpg.set_value(self._name_input, splitext(basename(path))[0])

    def load_files(self):
        paths: List[str] = list(
            filter(
                lambda _: _ is not None,
                map(
                    lambda _: dpg.get_item_user_data(_),
                    dpg.get_item_children(self._table, slot=1),
                ),
            )
        )
        if not paths:
            return
        self.hide()
        self._callback(paths=paths, merge=self._merge)
        self.close()

    def save_file(self):
        name: str = dpg.get_value(self._name_input).strip()
        if name == "":
            dpg.focus_item(self._name_input)
            return
        self.hide()
        path: str = join(self.get_current_path(), name)
        extension: str = dpg.get_value(self._name_extension_combo)
        if not path.endswith(extension):
            path += extension
        self._callback(path=path)
        self.close()
