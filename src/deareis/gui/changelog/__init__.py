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

from os.path import (
    abspath,
    dirname,
    exists,
    join,
)
from typing import (
    Callable,
    Dict,
    IO,
    List,
)
from deareis.signals import Signal
from deareis.utility import calculate_window_position_dimensions
import deareis.signals as signals
import dearpygui.dearpygui as dpg
from deareis.state import STATE
from deareis.enums import Action
from deareis.keybindings import (
    Keybinding,
    TemporaryKeybindingHandler,
)


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


class ChangelogWindow:
    def __init__(self):
        changelog_path: str = join(dirname(abspath(__file__)), "CHANGELOG.md")
        assert exists(changelog_path), changelog_path
        versions: List[List[str]] = self.parse_changelog(changelog_path)
        self.create_window(versions)
        self.register_keybindings()
        signals.emit(Signal.BLOCK_KEYBINDINGS, window=self.window, window_object=self)

    def parse_changelog(self, path: str) -> List[List[str]]:
        fp: IO
        with open(path, "r") as fp:
            lines: List[str] = fp.readlines()
        versions: List[List[str]] = []
        while lines:
            line: str = lines.pop(0).strip()
            if line == "":
                continue
            elif line.startswith("# "):
                tmp: List[str] = [line]
                while lines:
                    line = lines.pop(0).strip()
                    if line.startswith("# "):
                        lines.insert(0, line)
                        break
                    tmp.append(line)
                versions.append(tmp)
            else:
                raise NotImplementedError(f"Unsupported changelog format: {line}")
        return versions

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

    def create_window(self, versions: List[List[str]]):
        self.window: int = dpg.generate_uuid()
        x: int
        y: int
        w: int
        h: int
        x, y, w, h = calculate_window_position_dimensions(640, 540)
        with dpg.window(
            label="Changelog",
            modal=True,
            no_resize=True,
            pos=(x, y),
            width=w,
            height=h,
            on_close=self.close,
            tag=self.window,
        ):
            i: int
            for i, lines in enumerate(versions):
                label: str = lines.pop(0)
                assert label.startswith("# "), label
                with dpg.collapsing_header(
                    label=label[2:].strip(),
                    default_open=i == 0,
                ):
                    changelog: str = "\n".join(lines).strip()
                    dpg.add_text(format_changelog(changelog, w - 40))
                    dpg.add_spacer(height=8)

    def close(self):
        if dpg.does_item_exist(self.window):
            dpg.delete_item(self.window)
        self.keybinding_handler.delete()
        signals.emit(Signal.UNBLOCK_KEYBINDINGS)


def show_changelog():
    ChangelogWindow()
