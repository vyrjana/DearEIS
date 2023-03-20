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

import webbrowser
from typing import (
    Callable,
    Dict,
)
import dearpygui.dearpygui as dpg
from deareis.signals import Signal
from deareis.utility import calculate_window_position_dimensions
from deareis.version import PACKAGE_VERSION
import deareis.signals as signals
import deareis.themes as themes
from deareis.state import STATE
from deareis.enums import Action
from deareis.keybindings import (
    Keybinding,
    TemporaryKeybindingHandler,
)


class AboutWindow:
    def __init__(self):
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
        # Create the handler
        self.keybinding_handler: TemporaryKeybindingHandler = (
            TemporaryKeybindingHandler(callbacks=callbacks)
        )

    def create_window(self):
        x: int
        y: int
        w: int
        h: int
        x, y, w, h = calculate_window_position_dimensions(270, 100)
        self.window: int = dpg.generate_uuid()
        with dpg.window(
            label="About",
            modal=True,
            pos=(x, y),
            width=w,
            height=h,
            no_resize=True,
            on_close=self.close,
            tag=self.window,
        ):
            dpg.add_text(f"DearEIS ({PACKAGE_VERSION})")
            url: str
            for url in [
                "https://vyrjana.github.io/DearEIS",
                "https://github.com/vyrjana/DearEIS",
            ]:
                dpg.bind_item_theme(
                    dpg.add_button(
                        label=url,
                        callback=lambda s, a, u: webbrowser.open(u),
                        user_data=url,
                        width=-1,
                    ),
                    themes.url_theme,
                )
        signals.emit(Signal.BLOCK_KEYBINDINGS, window=self.window, window_object=self)

    def close(self):
        if dpg.does_item_exist(self.window):
            dpg.delete_item(self.window)
        self.keybinding_handler.delete()
        signals.emit(Signal.UNBLOCK_KEYBINDINGS)


def show_help_about(*args, **kwargs):
    AboutWindow()
