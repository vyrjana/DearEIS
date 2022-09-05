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
from .general import general
from .data_sets import data_sets
from .kramers_kronig import kramers_kronig
from .fitting import fitting
from .simulation import simulation
from .plotting import plotting
from .circuit_editor import circuit_editor
from .recent_projects import recent_projects
from .home import home
from .drt import drt


def update_tooltip(tag: int, msg: str, wrap: bool = True):
    assert type(tag) is int, tag
    assert type(msg) is str, msg
    assert type(wrap) is bool, wrap
    wrap_limit: int = -1
    if wrap:
        max_line_length: int
        if "\n" in msg:
            max_line_length = max(map(len, msg.split("\n")))
        else:
            max_line_length = len(msg)
        wrap_limit = min([8 * max_line_length, 500])
    dpg.configure_item(tag, default_value=msg, wrap=wrap_limit)


def attach_tooltip(msg: str, parent: int = -1, tag: int = -1, wrap: bool = True) -> int:
    assert type(msg) is str, msg
    assert type(parent) is int, parent
    assert type(tag) is int, tag
    assert type(wrap) is bool, wrap
    if parent < 0:
        parent = dpg.last_item()
    if tag < 0:
        tag = dpg.generate_uuid()
    with dpg.tooltip(parent, user_data=tag):
        dpg.add_text("", tag=tag)
    update_tooltip(tag, msg, wrap)
    return tag
