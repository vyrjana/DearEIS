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

from os.path import (
    abspath,
    dirname,
    exists,
    join,
)
from typing import (
    IO,
    List,
)
from deareis.signals import Signal
from deareis.utility import calculate_window_position_dimensions
import deareis.signals as signals
import dearpygui.dearpygui as dpg


def format_changelog(changelog: str, width: int) -> str:
    lines: List[str] = []
    line: str
    for line in changelog.split("\n"):
        stripped_line: str = line.strip()
        if stripped_line.startswith("#"):
            lines.append(line)
            continue
        elif stripped_line == "":
            lines.append("")
            continue
        indentation: str = ""
        if line.lstrip() != line:
            indentation = line[: line.index(stripped_line)]
            indentation = indentation.replace("\t", "  ")
        fragments: List[str] = [indentation] if indentation != "" else []
        if stripped_line.startswith("- "):
            indentation += "  "
        words: List[str] = stripped_line.split(" ")
        while words:
            while words:
                fragments.append(words.pop(0))
                if dpg.get_text_size(" ".join(fragments), wrap_width=-1.0)[0] >= width:
                    words.insert(0, fragments.pop())
                    break
            lines.append(" ".join(fragments))
            fragments = [indentation] if indentation != "" else []
        if len(fragments) > 1:
            lines.append(" ".join(fragments))
    i: int
    for i in range(0, len(lines)):
        line = lines[i]
        if line == "":
            continue
        indentation = line[: line.index(line.strip())]
        while len(indentation) % 2 > 0:
            indentation = indentation[1:]
        lines[i] = indentation + line.strip()
    return "\n".join(lines)


def show_changelog():
    changelog_path: str = join(dirname(abspath(__file__)), "CHANGELOG.md")
    assert exists(changelog_path), changelog_path
    changelog: str = ""
    fp: IO
    with open(changelog_path, "r") as fp:
        changelog = fp.read()

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

    x: int
    y: int
    w: int
    h: int
    x, y, w, h = calculate_window_position_dimensions(640, 540)
    with dpg.window(
        label="Changelog",
        modal=True,
        no_resize=True,
        pos=(
            x,
            y,
        ),
        width=w,
        height=h,
        on_close=close_window,
        tag=window,
    ):
        dpg.add_text(format_changelog(changelog, w - 40))
    signals.emit(Signal.BLOCK_KEYBINDINGS, window=window, window_object=None)
