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

from typing import (
    Dict,
    List,
    Optional,
    Set,
    Tuple,
)
from deareis.keybindings import KeybindingHandler
from deareis.enums import (
    Action,
    Context,
    action_contexts,
    action_descriptions,
)
from deareis.data.project import Project
from deareis.gui.project import ProjectTab
from .base import (
    BasePalette,
    Option,
)


class CommandPalette(BasePalette):
    def __init__(self, keybinding_handler: KeybindingHandler):
        super().__init__(
            title="Command palette",
            tooltip="Select an action to perform.\n\n",
        )
        self.keybinding_handler: KeybindingHandler = keybinding_handler
        self.action_contexts: Dict[Action, Set[Context]] = {
            k: set(v)
            for k, v in action_contexts.items()
            if k
            not in (
                Action.SHOW_COMMAND_PALETTE,
                Action.SHOW_DATA_SET_PALETTE,
                Action.SHOW_RESULT_PALETTE,
            )
        }
        self.valid_actions: List[Tuple[Action, str]] = []
        self.action_history: List[Action] = []

    def show(
        self,
        contexts: List[Context],
        project: Optional[Project],
        tab: Optional[ProjectTab],
    ):
        self.context: Context = contexts[-1]
        self.project: Optional[Project] = project
        self.tab: Optional[ProjectTab] = tab
        contexts_set: Set[Context] = set(contexts)
        self.options = []
        action: Action
        cons: Set[Context]
        for action, cons in self.action_contexts.items():
            if len(cons.intersection(contexts_set)) == 0:
                continue
            description: str = action_descriptions[action].split("\n")[0]
            if description.endswith(":"):
                description = description[:-1]
            elif description.endswith("."):
                description = description[:-1]
            self.options.append(
                Option(
                    description=description,
                    rank=int(action),
                    data=action,
                )
            )
        super().show()

    def select_option(self, option: Optional[Option] = None, click: bool = False):
        if option is None:
            return
        self.hide()
        if option in self.options_history:
            self.options_history.remove(option)
        self.options_history.insert(0, option)
        self.keybinding_handler.perform_action(
            option.data,
            self.context,
            self.project,
            self.tab,
        )
