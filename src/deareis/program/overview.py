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
from typing import (
    List,
    Optional,
)
from deareis.data import Project
from deareis.gui import ProjectTab
from deareis.signals import Signal
from deareis.state import STATE
import deareis.signals as signals


def rename_project(*args, **kwargs):
    project: Optional[Project] = STATE.get_active_project()
    project_tab: Optional[ProjectTab] = STATE.get_active_project_tab()
    if project is None or project_tab is None:
        return
    label: Optional[str] = kwargs.get("label")
    if label is None:
        return
    label = label.strip()
    if label == project.get_label():
        return
    elif label == "":
        project_tab.set_label(project.get_label())
        return
    project.set_label(label)
    project_tab.set_label(label)
    signals.emit(Signal.CREATE_PROJECT_SNAPSHOT)


def modify_project_notes(*args, **kwargs):
    timers: Optional[List[Timer]] = kwargs.get("timers")
    assert timers is not None, timers
    while timers:
        timers.pop(0).cancel()
    project: Optional[Project] = STATE.get_active_project()
    project_tab: Optional[ProjectTab] = STATE.get_active_project_tab()
    if project is None or project_tab is None:
        return

    def create_snapshot():
        project.set_notes(project_tab.get_notes())
        signals.emit(Signal.CREATE_PROJECT_SNAPSHOT)

    t: Timer = Timer(0.5, create_snapshot)
    timers.append(t)
    t.start()
