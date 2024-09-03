# DearEIS is licensed under the GPLv3 or later (https://www.gnu.org/licenses/gpl-3.0.html).
# Copyright 2024 DearEIS developers
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
from typing import (
    Callable,
    Dict,
    IO,
    List,
)
from deareis.signals import Signal
import deareis.signals as signals
from deareis.state import STATE
from deareis.enums import Action
from deareis.keybindings import (
    Keybinding,
    TemporaryKeybindingHandler,
)
from deareis.typing.helpers import Tag


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


class LicensesWindow:
    def __init__(self):
        self.licenses: Dict[str, str] = get_licenses(dirname(abspath(__file__)))
        self.create_window()
        self.register_keybindings()

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
        # Previous tab
        for kb in STATE.config.keybindings:
            if kb.action is Action.PREVIOUS_PROJECT_TAB:
                break
        else:
            kb = Keybinding(
                key=dpg.mvKey_Prior,
                mod_alt=False,
                mod_ctrl=True,
                mod_shift=False,
                action=Action.PREVIOUS_PROJECT_TAB,
            )
        callbacks[kb] = lambda: self.cycle_tabs(step=-1)
        # Next tab
        for kb in STATE.config.keybindings:
            if kb.action is Action.NEXT_PROJECT_TAB:
                break
        else:
            kb = Keybinding(
                key=dpg.mvKey_Next,
                mod_alt=False,
                mod_ctrl=True,
                mod_shift=False,
                action=Action.NEXT_PROJECT_TAB,
            )
        callbacks[kb] = lambda: self.cycle_tabs(step=1)
        # Previous license
        for kb in STATE.config.keybindings:
            if kb.action is Action.PREVIOUS_PRIMARY_RESULT:
                break
        else:
            kb = Keybinding(
                key=dpg.mvKey_Prior,
                mod_alt=False,
                mod_ctrl=False,
                mod_shift=False,
                action=Action.PREVIOUS_PRIMARY_RESULT,
            )
        callbacks[kb] = lambda: self.cycle_licenses(step=-1)
        # Next license
        for kb in STATE.config.keybindings:
            if kb.action is Action.NEXT_PRIMARY_RESULT:
                break
        else:
            kb = Keybinding(
                key=dpg.mvKey_Next,
                mod_alt=False,
                mod_ctrl=False,
                mod_shift=False,
                action=Action.NEXT_PRIMARY_RESULT,
            )
        callbacks[kb] = lambda: self.cycle_licenses(step=1)
        # Create the handler
        self.keybinding_handler: TemporaryKeybindingHandler = (
            TemporaryKeybindingHandler(callbacks=callbacks)
        )

    def create_window(self):
        x: int
        y: int
        w: int
        h: int
        x, y, w, h = calculate_window_position_dimensions(640, 540)
        self.window: Tag = dpg.generate_uuid()
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
            on_close=self.close,
            tag=self.window,
        ):
            self.tab_bar: Tag = dpg.generate_uuid()
            with dpg.tab_bar(tag=self.tab_bar):
                with dpg.tab(label="DearEIS"):
                    with dpg.child_window(border=False):
                        dpg.add_text(self.licenses["DearEIS"], wrap=w)
                    del self.licenses["DearEIS"]
                with dpg.tab(label="Dependencies"):
                    self.text_widget: Tag = dpg.generate_uuid()
                    self.license_combo: Tag = dpg.generate_uuid()

                    items: List[str] = list(sorted(self.licenses.keys()))
                    dpg.add_combo(
                        items=items,
                        default_value=items[0],
                        width=-1,
                        callback=self.show_dependency_license,
                        tag=self.license_combo,
                    )
                    with dpg.child_window(border=False):
                        dpg.add_text(
                            self.licenses[items[0]],
                            wrap=w,
                            tag=self.text_widget,
                        )
        signals.emit(
            Signal.BLOCK_KEYBINDINGS,
            window=self.window,
            window_object=self,
        )

    def show_dependency_license(self, sender: int, label: str):
        dpg.set_value(self.text_widget, self.licenses[label])

    def cycle_tabs(self, step: int):
        tabs: List[Tag] = dpg.get_item_children(self.tab_bar, slot=1)
        index: int = tabs.index(dpg.get_value(self.tab_bar)) + step
        dpg.set_value(self.tab_bar, tabs[index % len(tabs)])

    def cycle_licenses(self, step: int):
        labels: List[str] = list(self.licenses.keys())
        index: int = labels.index(dpg.get_value(self.license_combo)) + step
        dpg.set_value(self.license_combo, labels[index % len(labels)])
        self.show_dependency_license(self.license_combo, labels[index % len(labels)])

    def close(self):
        if dpg.does_item_exist(self.window):
            dpg.delete_item(self.window)
        self.keybinding_handler.delete()
        signals.emit(Signal.UNBLOCK_KEYBINDINGS)


def show_license_window():
    LicensesWindow()
