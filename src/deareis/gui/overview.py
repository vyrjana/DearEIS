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
from deareis.signals import Signal
import deareis.signals as signals
import deareis.themes as themes


class OverviewTab:
    def __init__(self):
        self.tab: int = dpg.generate_uuid()
        self.label_input: int = dpg.generate_uuid()
        self.notes_input: int = dpg.generate_uuid()
        with dpg.tab(label="Overview", tag=self.tab):
            with dpg.group(horizontal=True):
                dpg.add_text("Label")
                dpg.add_input_text(
                    on_enter=True,
                    callback=lambda s, a, u: signals.emit(
                        Signal.RENAME_PROJECT, label=a
                    ),
                    width=-1,
                    tag=self.label_input,
                )
            dpg.add_text("Notes")
            dpg.add_input_text(
                multiline=True,
                tab_input=True,
                callback=lambda s, a, u: signals.emit(
                    Signal.MODIFY_PROJECT_NOTES, timers=u
                ),
                user_data=[],
                width=-1,
                height=-1,
                tag=self.notes_input,
            )

    def resize(self, width: int, height: int):
        pass

    def set_label(self, label: str):
        assert type(label) is str, label
        dpg.set_value(self.label_input, label)

    def set_notes(self, notes: str):
        assert type(notes) is str, notes
        dpg.set_value(self.notes_input, notes)

    def get_notes(self) -> str:
        return dpg.get_value(self.notes_input)

    def has_active_input(self) -> bool:
        return dpg.is_item_active(self.label_input) or dpg.is_item_active(
            self.notes_input
        )
