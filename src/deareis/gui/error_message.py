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

from typing import (
    Callable,
    Dict,
    Optional,
)
import dearpygui.dearpygui as dpg
from deareis.utility import calculate_window_position_dimensions
from deareis.signals import Signal
import deareis.signals as signals
from deareis.enums import Action
from deareis.keybindings import (
    Keybinding,
    TemporaryKeybindingHandler,
)
from deareis.typing.helpers import Tag


class ErrorMessage:
    def __init__(self):
        self.keybinding_handler: Optional[TemporaryKeybindingHandler] = None
        self.create_window()

    def create_window(self):
        self.window: Tag = dpg.generate_uuid()
        with dpg.window(
            label="ERROR",
            modal=True,
            no_resize=True,
            show=False,
            width=720,
            height=540,
            on_close=self.hide,
            tag=self.window,
        ):
            with dpg.child_window(width=-1, height=-24, horizontal_scrollbar=True):
                self.traceback_text: Tag = dpg.generate_uuid()
                dpg.add_text(tag=self.traceback_text)

            dpg.add_button(
                label="Copy to clipboard",
                callback=lambda: dpg.set_clipboard_text(
                    dpg.get_value(self.traceback_text)
                ),
            )

    def is_visible(self) -> bool:
        return dpg.is_item_visible(self.window) or False

    def show(self, traceback: str, message: str = ""):
        assert type(traceback) is str
        assert type(message) is str
        print(f"\n{traceback}")

        dpg.split_frame(delay=33)
        if message.strip() == "":
            message = """
An exception has been raised! The very end of the traceback (see below) may offer a hint on how to solve the cause for the error that just occurred. If it doesn't, then please copy the traceback to your clipboard and include it in a bug report. Bug reports can be submitted at github.com/vyrjana/DearEIS/issues.
            """.strip()

        if not self.is_visible():
            dpg.show_item(self.window)
            dpg.split_frame()
            self.register_keybindings()
            traceback = f"{message}\n\n{traceback}"
        else:
            traceback = (
                f"{dpg.get_value(self.traceback_text)}\n\n{message}\n\n{traceback}"
            )

        dpg.set_value(self.traceback_text, traceback)
        dpg.split_frame()
        self.resize(-1, -1)

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
        callbacks[kb] = self.hide

        # Create the handler
        self.keybinding_handler = TemporaryKeybindingHandler(callbacks=callbacks)

    def hide(self):
        if self.keybinding_handler is not None:
            self.keybinding_handler.delete()

        if dpg.is_item_visible(self.window):
            dpg.hide_item(self.window)

        signals.emit(Signal.UNBLOCK_KEYBINDINGS)

    def resize(self, width: int, height: int):
        assert type(width) is int
        assert type(height) is int

        x: int
        y: int
        x, y, width, height = calculate_window_position_dimensions()

        dpg.configure_item(
            self.window,
            pos=(
                x,
                y,
            ),
            width=width,
            height=height,
        )

        dpg.split_frame()

        width, _ = dpg.get_item_rect_size(self.window)
        dpg.configure_item(self.traceback_text, wrap=width - 40)
