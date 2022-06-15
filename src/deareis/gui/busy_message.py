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


class BusyMessage:
    def __init__(self):
        self.width: int = 159
        self.height: int = 159
        self.window: int = dpg.generate_uuid()
        with dpg.window(
            autosize=True,
            menubar=False,
            modal=True,
            no_background=True,
            no_close=True,
            no_move=True,
            no_resize=True,
            no_title_bar=True,
            show=False,
            tag=self.window,
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
                self.message_spacer: int = dpg.generate_uuid()
                dpg.add_spacer(tag=self.message_spacer)
                self.message_wrap: int = 140
                self.message_text: int = dpg.generate_uuid()
                dpg.add_text(tag=self.message_text, wrap=self.message_wrap)
            self.progress_bar: int = dpg.generate_uuid()
            dpg.add_progress_bar(
                width=self.width - 16,
                height=12,
                tag=self.progress_bar,
            )

    def is_visible(self) -> bool:
        return dpg.is_item_shown(self.window)

    def show(self, message: str = "", progress: float = -1.0):
        assert type(message) is str, message
        assert type(progress) is float and progress <= 1.0, progress
        dpg.split_frame(delay=33)
        if not self.is_visible():
            dpg.split_frame()
            dpg.show_item(self.window)
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

    def hide(self):
        dpg.hide_item(self.window)
        dpg.split_frame()

    def resize(self, width: int, height: int):
        assert type(width) is int
        assert type(height) is int
        x: int = round((width - self.width) / 2)
        y: int = round((height - self.height) / 2)
        dpg.configure_item(
            self.window,
            pos=(
                x,
                y,
            ),
        )
