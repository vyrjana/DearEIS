# DearEIS is licensed under the GPLv3 or later (https://www.gnu.org/licenses/gpl-3.0.html).
# Copyright 2023 DearEIS developers
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

from dataclasses import dataclass
from typing import (
    Callable,
    Dict,
    List,
    Optional,
)
import dearpygui.dearpygui as dpg
from deareis.data import DataSet
from deareis.utility import (
    calculate_window_position_dimensions,
    is_filtered_item_visible,
)
from deareis.signals import Signal
import deareis.signals as signals
import deareis.tooltips as tooltips
from deareis.tooltips import attach_tooltip
from deareis.state import STATE
from deareis.enums import Action
from deareis.keybindings import (
    Keybinding,
    TemporaryKeybindingHandler,
)


@dataclass
class Entry:
    data: DataSet
    row: int
    checkbox: int

    def __hash__(self) -> int:
        return int(self.data.uuid, 16)

    def is_visible(self, filter_string: str) -> bool:
        return is_filtered_item_visible(self.row, filter_string)

    def is_ticked(self) -> bool:
        return dpg.get_value(self.checkbox)

    def toggle(self, flag: Optional[bool] = None):
        dpg.set_value(
            self.checkbox,
            flag if flag is not None else not dpg.get_value(self.checkbox),
        )


class BatchAnalysis:
    def __init__(self, data_sets: List[DataSet], callback: Callable):
        self.callback: Callable = callback
        self.create_window()
        self.entries: List[Entry] = []
        self.populate(data_sets)
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
        # Accept
        for kb in STATE.config.keybindings:
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
        callbacks[kb] = self.accept
        # Select filtered
        for kb in STATE.config.keybindings:
            if kb.action is Action.SELECT_ALL_PLOT_SERIES:
                break
        else:
            kb = Keybinding(
                key=dpg.mvKey_A,
                mod_alt=True,
                mod_ctrl=False,
                mod_shift=False,
                action=Action.SELECT_ALL_PLOT_SERIES,
            )
        callbacks[kb] = lambda: self.select_unselect(flag=True)
        # Unselect filtered
        for kb in STATE.config.keybindings:
            if kb.action is Action.UNSELECT_ALL_PLOT_SERIES:
                break
        else:
            kb = Keybinding(
                key=dpg.mvKey_A,
                mod_alt=True,
                mod_ctrl=False,
                mod_shift=True,
                action=Action.UNSELECT_ALL_PLOT_SERIES,
            )
        callbacks[kb] = lambda: self.select_unselect(flag=False)
        # Focus filter input
        kb: Keybinding = Keybinding(
            key=dpg.mvKey_F,
            mod_alt=False,
            mod_ctrl=True,
            mod_shift=False,
            action=Action.CUSTOM,
        )
        callbacks[kb] = self.focus_filter_input
        # Create the handler
        self.keybinding_handler: TemporaryKeybindingHandler = (
            TemporaryKeybindingHandler(callbacks=callbacks)
        )

    def create_window(self):
        x: int
        y: int
        w: int
        h: int
        x, y, w, h = calculate_window_position_dimensions(width=500, height=400)
        self.window: int = dpg.generate_uuid()
        with dpg.window(
            label="Batch analysis",
            modal=True,
            pos=(x, y),
            width=w,
            height=h,
            tag=self.window,
            on_close=self.close,
            no_resize=True,
        ):
            with dpg.group(horizontal=True):
                self.filter_input: int = dpg.generate_uuid()
                dpg.add_input_text(
                    hint="Filter...",
                    width=-80,
                    callback=lambda s, a, u: self.filter_possible_series(a.lower()),
                    tag=self.filter_input,
                )
                attach_tooltip(tooltips.batch_analysis.filter)
                self.select_unselect_button: int = dpg.generate_uuid()
                dpg.add_button(
                    label="Select",
                    width=-1,
                    callback=self.select_unselect,
                    tag=self.select_unselect_button,
                )
                attach_tooltip(tooltips.batch_analysis.select)
            self.table: int = dpg.generate_uuid()
            with dpg.table(
                borders_outerV=True,
                borders_outerH=True,
                borders_innerV=True,
                borders_innerH=True,
                scrollY=True,
                freeze_rows=1,
                tag=self.table,
                height=-24,
            ):
                dpg.add_table_column(
                    label=" ?",
                    width_fixed=True,
                )
                attach_tooltip(tooltips.batch_analysis.checkbox)
                dpg.add_table_column(
                    label="Label",
                    width_fixed=False,
                )
            self.accept_button: int = dpg.generate_uuid()
            dpg.add_button(
                label="Cancel",
                callback=self.accept,
                width=-1,
                tag=self.accept_button,
            )

    def populate(self, data_sets: List[DataSet]):
        self.entries.clear()
        data: DataSet
        for data in data_sets:
            label: str = data.get_label()
            row: int
            with dpg.table_row(
                filter_key=label.lower(),
                parent=self.table,
            ) as row:
                checkbox: int = dpg.add_checkbox(
                    default_value=False,
                    user_data=data,
                    callback=lambda s, a, u: self.toggle(),
                )
                dpg.add_text(label)
                attach_tooltip(label)
                self.entries.append(
                    Entry(
                        data=data,
                        row=row,
                        checkbox=checkbox,
                    )
                )

    def select_unselect(self, flag: Optional[bool] = None):
        selection: Dict[Entry, bool] = {}
        filter_string: str = dpg.get_value(self.filter_input).strip()
        for entry in self.entries:
            if filter_string != "" and not entry.is_visible(filter_string):
                continue
            selection[entry] = entry.is_ticked()
        if not isinstance(flag, bool):
            flag = not all(map(lambda _: _ is True, selection.values()))
        for entry in selection:
            dpg.set_value(entry.checkbox, flag)
        self.toggle()

    def toggle(self, index: int = -1):
        if index >= 0:
            # This is primarily for use in the GUI tests.
            row: int = dpg.get_item_children(self.table, slot=1)[index]
            checkbox: int = dpg.get_item_children(row, slot=1)[0]
            dpg.set_value(checkbox, not dpg.get_value(checkbox))
        num_data_sets: int = len(self.get_selection())
        dpg.set_item_label(
            self.accept_button,
            "Cancel" if num_data_sets == 0 else f"Accept ({num_data_sets})",
        )
        self.update_select_button_label(dpg.get_value(self.filter_input).strip())

    def update_select_button_label(self, filter_string: str):
        selection: List[Entry] = list(
            filter(lambda _: _.is_visible(filter_string), self.entries)
        )
        dpg.set_item_label(
            self.select_unselect_button,
            "Unselect"
            if all(map(lambda _: _.is_ticked() is True, selection))
            else "Select",
        )

    def get_selection(self) -> List[Entry]:
        selection: List[Entry] = []
        for entry in self.entries:
            if entry.is_ticked():
                selection.append(entry)
        return selection

    def filter_possible_series(self, filter_string: str):
        filter_string = filter_string.strip()
        dpg.set_value(self.table, filter_string)
        self.update_select_button_label(filter_string)

    def close(self):
        dpg.hide_item(self.window)
        dpg.delete_item(self.window)
        self.keybinding_handler.delete()
        signals.emit(Signal.UNBLOCK_KEYBINDINGS)

    def accept(self):
        selection: List[Entry] = self.get_selection()
        if not selection:
            self.close()
            return
        self.close()
        dpg.split_frame(delay=60)
        self.callback([_.data for _ in selection])

    def focus_filter_input(self):
        if dpg.is_item_active(self.filter_input):
            return
        dpg.focus_item(self.filter_input)
