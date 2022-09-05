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

import dearpygui.dearpygui as dpg
from deareis.utility import calculate_window_position_dimensions
from os import walk
from os.path import abspath, exists, dirname, join
from typing import Dict, IO, List
from deareis.signals import Signal
import deareis.signals as signals


def read_file(path: str) -> str:
    assert type(path) is str
    assert exists(path), path
    fp: IO
    with open(path, "r") as fp:
        return fp.read()


def get_licenses(root: str) -> Dict[str, str]:
    assert type(root) is str
    assert exists(root), root
    files: List[str] = []
    for _, _, files in walk(root):
        break
    files = list(filter(lambda _: not _.endswith(".py"), files))
    assert len(files) > 0
    prefix: str = "LICENSE-"
    extension: str = ".txt"
    assert all(map(lambda _: _.startswith(prefix) and _.endswith(extension), files))
    files.sort()
    licenses: Dict[str, str] = {}
    file: str
    for file in files:
        key: str = file[len(prefix) : file.rfind(extension)]
        licenses[key] = read_file(join(root, file))
    return licenses


def show_license_window():
    licenses: Dict[str, str] = get_licenses(dirname(abspath(__file__)))
    x: int
    y: int
    w: int
    h: int
    x, y, w, h = calculate_window_position_dimensions(640, 540)
    window: int = dpg.generate_uuid()
    key_handler: int = dpg.generate_uuid()

    def close_window():
        if dpg.does_item_exist(window):
            dpg.delete_item(window)
        if dpg.does_item_exist(key_handler):
            dpg.delete_item(key_handler)
        signals.emit(Signal.UNBLOCK_KEYBINDINGS)

    with dpg.handler_registry(tag=key_handler):
        dpg.add_key_release_handler(
            key=dpg.mvKey_Escape,
            callback=close_window,
        )

    with dpg.window(
        label="Licenses",
        modal=True,
        pos=(
            x,
            y,
        ),
        width=w,
        height=h,
        no_move=False,
        no_resize=True,
        on_close=close_window,
        tag=window,
    ):
        with dpg.tab_bar():
            with dpg.tab(label="DearEIS"):
                with dpg.child_window(border=False):
                    dpg.add_text(licenses["DearEIS"], wrap=w)
                del licenses["DearEIS"]
            with dpg.tab(label="Dependencies"):
                text_widget: int = dpg.generate_uuid()

                def show_dependency_license(sender: int, label: str):
                    dpg.set_value(text_widget, licenses[label])

                items: List[str] = list(sorted(licenses.keys()))
                dpg.add_combo(
                    items=items,
                    default_value=items[0],
                    width=-1,
                    callback=show_dependency_license,
                )
                with dpg.child_window(border=False):
                    dpg.add_text(licenses[items[0]], wrap=w, tag=text_widget)
    signals.emit(Signal.BLOCK_KEYBINDINGS, window=window, window_object=None)
