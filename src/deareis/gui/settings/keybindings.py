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

from threading import Timer
from traceback import format_exc
from typing import Any, List, Optional
import dearpygui.dearpygui as dpg
from deareis.tooltips import attach_tooltip
from deareis.utility import calculate_window_position_dimensions
from deareis.enums import Action, action_descriptions
from deareis.signals import Signal
import deareis.signals as signals
from deareis.keybindings import Keybinding, dpg_to_string
from deareis.config import DEFAULT_KEYBINDINGS


class KeybindingTable:
    def __init__(self, key_filter_input: int, description_filter_input: int, state):
        self.key_filter_input: int = key_filter_input
        self.description_filter_input: int = description_filter_input
        self.state = state
        self.remapping: bool = False
        self.info_window: int = dpg.generate_uuid()
        with dpg.child_window(width=-1, height=-26, tag=self.info_window):
            self.info_text: int = dpg.generate_uuid()
            dpg.add_text(
                "",
                tag=self.info_text,
                user_data="Press a key or Esc to clear the current key mapping...",
                wrap=680,
            )
        self.table: int = dpg.generate_uuid()
        with dpg.table(
            borders_outerV=True,
            borders_outerH=True,
            borders_innerV=True,
            borders_innerH=True,
            scrollY=True,
            height=18 + 23 * 19,
            freeze_rows=1,
            tag=self.table,
        ):
            dpg.add_table_column(
                label=" A",
                width_fixed=True,
            )
            attach_tooltip("Whether or not the Alt modifier key is required.")
            dpg.add_table_column(
                label=" C",
                width_fixed=True,
            )
            attach_tooltip("Whether or not the Ctrl modifier key is required.")
            dpg.add_table_column(
                label=" S",
                width_fixed=True,
            )
            attach_tooltip("Whether or not the Shift modifier key is required.")
            self.key_padding: int = max(list(map(len, list(dpg_to_string.values()))))
            dpg.add_table_column(
                label="Key".ljust(self.key_padding),
                width_fixed=True,
            )
            attach_tooltip(
                "Press a button in this column to remap the key. Note that not all keys are supported. Press 'Esc' while remapping to clear the key instead of remapping it to another key."
            )
            dpg.add_table_column(
                label="Description",
            )
        self.reset()

    def is_remapping(self) -> bool:
        return self.remapping

    def populate(self):
        dpg.delete_item(self.table, children_only=True, slot=1)
        action: Action
        description: str
        for action, description in action_descriptions.items():
            kb: Optional[Keybinding] = self.find_keybinding(action)
            filter_key: str = "|".join(
                [str(kb) if kb else "", description.lower()]
            ).lower()
            with dpg.table_row(
                filter_key=filter_key,
                user_data=action,
                parent=self.table,
            ):
                dpg.add_checkbox(
                    default_value=kb.mod_alt if kb else False,
                    callback=lambda s, a, u: self.toggle_mod_key(s, a, u["kb"]),
                    user_data={
                        "kb": kb,
                        "mod": "alt",
                    },
                )
                dpg.add_checkbox(
                    default_value=kb.mod_ctrl if kb else False,
                    callback=lambda s, a, u: self.toggle_mod_key(s, a, u["kb"]),
                    user_data={
                        "kb": kb,
                        "mod": "ctrl",
                    },
                )
                dpg.add_checkbox(
                    default_value=kb.mod_shift if kb else False,
                    callback=lambda s, a, u: self.toggle_mod_key(s, a, u["kb"]),
                    user_data={
                        "kb": kb,
                        "mod": "shift",
                    },
                )
                dpg.add_button(
                    label=(dpg_to_string.get(kb.key, "") if kb else "").ljust(
                        self.key_padding
                    ),
                    callback=lambda s, a, u: self.begin_remap(**u),
                    user_data={
                        "kb": kb,
                        "action": action,
                    },
                )
                short_description: str = description.split("\n")[0]
                description_limit: int = 64
                if len(short_description) > description_limit:
                    short_description = short_description[:description_limit] + "..."
                if short_description.endswith(":"):
                    short_description = short_description[:-1] + "..."
                dpg.add_text(short_description)
                attach_tooltip(description)
        self.filter()

    def filter(self):
        key: str = dpg.get_value(self.key_filter_input).strip().lower()
        description: str = dpg.get_value(self.description_filter_input).strip().lower()
        row: int
        for row in dpg.get_item_children(self.table, slot=1):
            key_filter: str
            description_filter: str
            key_filter, description_filter = dpg.get_item_filter_key(row).split("|")
            if key and description:
                if key in key_filter and description in description_filter:
                    dpg.show_item(row)
                else:
                    dpg.hide_item(row)
            elif key:
                if key in key_filter:
                    dpg.show_item(row)
                else:
                    dpg.hide_item(row)
            elif description:
                if description in description_filter:
                    dpg.show_item(row)
                else:
                    dpg.hide_item(row)
            else:
                dpg.show_item(row)

    def find_keybinding(self, action: Action) -> Optional[Keybinding]:
        kb: Keybinding
        for kb in self.state.config.keybindings:
            if kb.action == action:
                return kb
        return None

    def toggle_mod_key(self, sender: int, state: bool, kb: Optional[Keybinding]):
        if kb is None:
            return
        keybindings: List[Keybinding] = self.state.config.keybindings.copy()
        keybindings.remove(kb)
        keybindings.append(
            Keybinding(
                kb.key,
                self.has_mod_alt(kb.action),
                self.has_mod_ctrl(kb.action),
                self.has_mod_shift(kb.action),
                kb.action,
            )
        )
        try:
            self.state.config.validate_keybindings(keybindings)
        except Exception as e:
            dpg.hide_item(self.table)
            dpg.set_value(self.info_text, str(e))
            dpg.show_item(self.info_window)
            # dpg.set_value(self.info_text, format_exc())
            t: Timer = Timer(5, self.reset)
            t.start()
            return
        try:
            self.state.config.keybindings = keybindings
            self.state.keybinding_handler.register(keybindings)
            self.reset()
        except Exception:
            signals.emit(Signal.SHOW_ERROR_MESSAGE, traceback=format_exc())

    def has_mod_alt(self, action: Action) -> bool:
        return self.has_mod(action, "alt")

    def has_mod_ctrl(self, action: Action) -> bool:
        return self.has_mod(action, "ctrl")

    def has_mod_shift(self, action: Action) -> bool:
        return self.has_mod(action, "shift")

    def has_mod(self, action: Action, mod: str) -> bool:
        row: int
        for row in dpg.get_item_children(self.table, slot=1):
            if dpg.get_item_user_data(row) != action:
                continue
            cell: int
            for cell in dpg.get_item_children(row, slot=1):
                user_data: Any = dpg.get_item_user_data(cell)
                if type(user_data) is not dict:
                    continue
                elif user_data.get("mod") == mod:
                    return dpg.get_value(cell)
        return False

    def begin_remap(self, kb: Optional[Keybinding], action: Action):
        self.remapping = True
        self.key_handler: int = dpg.generate_uuid()
        with dpg.handler_registry(tag=self.key_handler):
            key: int
            for key in dpg_to_string:
                dpg.add_key_release_handler(
                    key=key,
                    callback=lambda s, a, u: self.end_remap(a, kb, action),
                )
        dpg.hide_item(self.table)
        dpg.show_item(self.info_window)

    def end_remap(self, key: int, kb: Optional[Keybinding], action: Action):
        if dpg.does_item_exist(self.key_handler):
            dpg.delete_item(self.key_handler)
        self.remapping = False
        keybindings: List[Keybinding] = self.state.config.keybindings.copy()
        if kb is not None:
            keybindings.remove(kb)
        if key != dpg.mvKey_Escape:
            kb = Keybinding(
                key,
                self.has_mod_alt(action),
                self.has_mod_ctrl(action),
                self.has_mod_shift(action),
                action,
            )
            keybindings.append(kb)  # type: ignore
        try:
            self.state.config.validate_keybindings(keybindings)
        except Exception as e:
            dpg.set_value(self.info_text, str(e))
            # dpg.set_value(self.info_text, format_exc())
            t: Timer = Timer(5, self.reset)
            t.start()
            return
        try:
            self.state.config.keybindings = keybindings
            self.state.keybinding_handler.register(keybindings)
            self.reset()
        except Exception:
            signals.emit(Signal.SHOW_ERROR_MESSAGE, traceback=format_exc())

    def reset(self):
        dpg.set_value(self.info_text, dpg.get_item_user_data(self.info_text))
        dpg.hide_item(self.info_window)
        dpg.show_item(self.table)
        self.populate()


class KeybindingRemapping:
    def __init__(self, state):
        self.state = state
        x: int
        y: int
        w: int
        h: int
        x, y, w, h = calculate_window_position_dimensions(720, 540)
        self.window: int = dpg.generate_uuid()
        with dpg.window(
            label="Settings - keybindings",
            modal=True,
            pos=(
                x,
                y,
            ),
            width=w,
            height=h,
            no_move=False,
            no_resize=True,
            on_close=self.close_window,
            tag=self.window,
        ):
            key_filter_input: int = dpg.generate_uuid()
            description_filter_input: int = dpg.generate_uuid()
            with dpg.group(horizontal=True):
                dpg.add_input_text(
                    callback=lambda s, a, u: self.table.filter(),
                    hint="Filter key(s)",
                    width=200,
                    tag=key_filter_input,
                )
                attach_tooltip(
                    """
Filter based on keys or modifiers ('alt', 'ctrl', or 'shift'). Multiple modifiers and a key can be filtered by using '+' as a separator (e.g. 'alt+shift+n').
                """.strip()
                )
                dpg.add_input_text(
                    callback=lambda s, a, u: self.table.filter(),
                    hint="Filter description(s)",
                    width=-1,
                    tag=description_filter_input,
                )
                attach_tooltip(
                    """
Filter based on descriptions.
                """.strip()
                )
            self.table: KeybindingTable = KeybindingTable(
                key_filter_input, description_filter_input, state
            )
            with dpg.group(horizontal=True):
                dpg.add_button(label="Clear all", callback=self.clear_all)
                dpg.add_button(label="Reset", callback=self.reset)
        self.key_handler: int = dpg.generate_uuid()
        with dpg.handler_registry(tag=self.key_handler):
            dpg.add_key_release_handler(
                key=dpg.mvKey_Escape,
                callback=self.close_window,
            )
        signals.emit(Signal.BLOCK_KEYBINDINGS, window=self.window, window_object=self)

    def clear_all(self):
        self.state.config.keybindings = []
        self.state.keybinding_handler.register(self.state.config.keybindings)
        self.table.populate()

    def reset(self):
        self.state.config.keybindings = DEFAULT_KEYBINDINGS.copy()
        self.state.keybinding_handler.register(self.state.config.keybindings)
        self.table.populate()

    def close_window(self):
        if self.table.is_remapping():
            return
        if dpg.does_item_exist(self.window):
            dpg.delete_item(self.window)
        if dpg.does_item_exist(self.key_handler):
            dpg.delete_item(self.key_handler)
        signals.emit(Signal.UNBLOCK_KEYBINDINGS)
