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

from typing import Dict, List, Set, Tuple, Optional
import dearpygui.dearpygui as dpg
from numpy import array, ndarray
from deareis.signals import Signal
import deareis.signals as signals
from deareis.enums import Action, Context, action_contexts, action_descriptions
from deareis.utility import calculate_window_position_dimensions
from deareis.data.project import Project
from deareis.gui.project import ProjectTab
from deareis.keybindings import KeybindingHandler
import deareis.themes as themes
from deareis.tooltips import attach_tooltip
import deareis.tooltips as tooltips


class CommandPalette:
    def __init__(self, keybinding_handler: KeybindingHandler):
        assert type(keybinding_handler), keybinding_handler
        self.keybinding_handler: KeybindingHandler = keybinding_handler
        self.action_contexts: Dict[Action, Set[Context]] = {
            k: set(v)
            for k, v in action_contexts.items()
            if k != Action.SHOW_COMMAND_PALETTE
        }
        self.valid_actions: List[Tuple[Action, str]] = []
        self.action_history: List[Action] = []
        self.window: int = dpg.generate_uuid()
        with dpg.window(
            label="Command palette",
            no_close=True,
            modal=True,
            no_resize=True,
            show=False,
            tag=self.window,
        ):
            self.filter_input: int = dpg.generate_uuid()
            dpg.add_input_text(
                hint="Search...",
                tag=self.filter_input,
                width=-1,
                callback=lambda s, a, u: self.filter_results(a.strip().lower()),
            )
            attach_tooltip(tooltips.general.command_palette)
            self.results_table: int = dpg.generate_uuid()
            self.num_rows: int = 9
            with dpg.table(
                borders_outerV=True,
                borders_outerH=True,
                borders_innerV=True,
                borders_innerH=True,
                header_row=False,
                height=self.num_rows * 23,
                tag=self.results_table,
            ):
                dpg.add_table_column()
                for i in range(0, self.num_rows):
                    with dpg.table_row():
                        dpg.add_button(
                            label="",
                            callback=lambda s, a, u: self.perform_action(u, True),
                            width=-1,
                        )

    def show(self, contexts: List[Context], project: Project, tab: ProjectTab):
        self.current_contexts = contexts
        self.current_project: Project = project
        self.current_tab: ProjectTab = tab
        self.valid_actions = []
        contexts_set: Set[Context] = set(contexts)
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
            self.valid_actions.append(
                (
                    action,
                    description,
                )
            )
        signals.emit(Signal.BLOCK_KEYBINDINGS, window=self.window, window_object=self)
        dpg.show_item(self.window)
        dpg.split_frame()
        x: int
        y: int
        w: int
        h: int = 24 + self.num_rows * 23 + 34
        x, y, w, h = calculate_window_position_dimensions(720, h)
        dpg.configure_item(
            self.window,
            pos=(
                x,
                y,
            ),
            width=w,
            height=h,
        )
        dpg.set_value(self.filter_input, "")
        self.filter_results("")
        self.key_handler: int = dpg.generate_uuid()
        with dpg.handler_registry(tag=self.key_handler):
            dpg.add_key_release_handler(
                key=dpg.mvKey_Escape,
                callback=self.hide,
            )
            dpg.add_key_release_handler(
                key=dpg.mvKey_Return,
                callback=lambda s, a, u: self.perform_action(),
            )
            dpg.add_key_release_handler(
                key=dpg.mvKey_Up,
                callback=lambda: self.navigate_result(step=-1),
            )
            dpg.add_key_release_handler(
                key=dpg.mvKey_Prior,
                callback=lambda: self.navigate_result(step=-5),
            )
            dpg.add_key_release_handler(
                key=dpg.mvKey_Home,
                callback=lambda: self.navigate_result(index=0),
            )
            dpg.add_key_release_handler(
                key=dpg.mvKey_Down,
                callback=lambda: self.navigate_result(step=1),
            )
            dpg.add_key_release_handler(
                key=dpg.mvKey_Next,
                callback=lambda: self.navigate_result(step=5),
            )
            dpg.add_key_release_handler(
                key=dpg.mvKey_End,
                callback=lambda: self.navigate_result(
                    index=len(self.valid_actions) - 1
                ),
            )
        dpg.split_frame()
        dpg.focus_item(self.filter_input)

    def hide(self):
        dpg.delete_item(self.key_handler)
        dpg.hide_item(self.window)
        dpg.split_frame()
        signals.emit(Signal.UNBLOCK_KEYBINDINGS)

    def get_consecutive_letter_indices(self, source: str, target: str) -> List[int]:
        indices: List[int] = []
        letter: str
        for letter in source:
            index: int = -1
            if not indices or indices[-1] >= 0:
                index = target.find(letter, indices[-1] if indices else 0)
            indices.append(index)
        return indices

    def get_distances_from_word_beginning(
        self, letter_indices: List[int], target: str
    ) -> Tuple[List[int], List[int]]:
        if not letter_indices:
            return (
                [],
                [],
            )
        words: List[str] = target.split(" ")
        if not words:
            return (
                [],
                [],
            )
        distances: List[int] = []
        word_lengths: List[int] = []
        letter_index: int
        for letter_index in letter_indices:
            space_index: int = letter_index - 1
            letter: str = target[space_index]
            while letter != " " and space_index > 0:
                space_index -= 1
                letter = target[space_index]
            space_index += 1
            distances.append(letter_index - space_index)
            end_index: int = target.find(" ", space_index)
            if end_index < 0:
                end_index = len(target)
            word_lengths.append(end_index - space_index)
        return (
            distances,
            word_lengths,
        )

    def score_result(self, source: str, target: str, action: Action) -> float:
        score: float = 0.0
        num_valid_actions: int = len(self.valid_actions)
        if source == "":
            score -= int(action) + 1
            if action in self.action_history:
                recency_bonus: float = float(num_valid_actions)
                score += (
                    len(self.action_history) - self.action_history.index(action)
                ) * recency_bonus
        else:
            if source in target:
                score += 100
            len_source: int = len(source)
            len_target: int = len(target)
            indices: List[int] = self.get_consecutive_letter_indices(source, target)
            num_matches: int = len(list(filter(lambda _: _ >= 0, indices)))
            # Penalize for source letters not found in the target
            score -= abs(sum(filter(lambda _: _ < 0, indices))) * 25.0
            # Reward for source letters found in the target based on proximity to the beginning
            score += (
                sum(
                    map(
                        lambda _: (len_target - _) / len_target,
                        filter(lambda _: _ >= 0, indices),
                    )
                )
                * 100.0
            )
            # Penalize the difference between the number of found source letters and the length
            # of the target and normalize using the length of the source
            score -= (len_target - num_matches) / len_source * 10.0
            # Reward for the proximity of found source letters to the beginning of the word in
            # which the letter was found
            distances: List[int]
            word_lengths: List[int]
            distances, word_lengths = self.get_distances_from_word_beginning(
                list(filter(lambda _: _ >= 0, indices)), target
            )
            for distance, word_length in zip(distances, word_lengths):
                score += (word_length - distance) / word_length * 15.0
        return score

    def filter_results(self, string: str):
        self.result_index = 0
        scores: Dict[Action, float] = {}
        for (action, description) in self.valid_actions:
            scores[action] = self.score_result(
                string,
                description.lower(),
                action,
            )
        self.valid_actions.sort(key=lambda _: scores[_[0]], reverse=True)
        self.update_results()

    def update_results(self):
        i: int
        row: int
        cell: int
        action: Optional[Action]
        description: str
        index: int
        for i, row in enumerate(dpg.get_item_children(self.results_table, slot=1)):
            cell = dpg.get_item_children(row, slot=1)[0]
            action = None
            description = ""
            if self.result_index < 4:
                # A row in the upper half
                index = i
                dpg.bind_item_theme(
                    cell,
                    themes.command_palette.result_highlighted
                    if i == self.result_index
                    else themes.command_palette.result,
                )
            elif len(self.valid_actions) - self.result_index < 5:
                # A row in the lower half
                index = len(self.valid_actions) + i - self.num_rows
                dpg.bind_item_theme(
                    cell,
                    themes.command_palette.result_highlighted
                    if i
                    == self.num_rows - (len(self.valid_actions) - self.result_index)
                    else themes.command_palette.result,
                )
            else:
                # The row in the middle
                index = self.result_index + i - 4
                dpg.bind_item_theme(
                    cell,
                    themes.command_palette.result_highlighted
                    if i == 4
                    else themes.command_palette.result,
                )
            if index >= 0 and index < len(self.valid_actions):
                action, description = self.valid_actions[index]
            dpg.set_item_label(cell, description)
            dpg.set_item_user_data(cell, action)

    def navigate_result(self, index: Optional[int] = None, step: Optional[int] = None):
        assert type(index) is int or index is None, index
        assert type(step) is int or step is None, step
        if index is None and step is None:
            return
        elif index is not None:
            if index >= len(self.valid_actions):
                return
        elif step is not None:
            index = self.result_index + step
            if index < 0:
                index = 0
            elif index >= len(self.valid_actions):
                index = len(self.valid_actions) - 1
        assert index is not None
        self.result_index = index
        self.update_results()

    def perform_action(self, action: Optional[Action] = None, click: bool = False):
        if click and action is None:
            return
        self.hide()
        if not click:
            action = self.valid_actions[self.result_index][0]
        assert type(action) is Action, action
        if action in self.action_history:
            self.action_history.remove(action)
        self.action_history.insert(0, action)
        self.keybinding_handler.perform_action(
            action,
            self.current_contexts[-1],
            self.current_project,
            self.current_tab,
        )
