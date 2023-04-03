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

from dataclasses import dataclass
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Tuple,
)
import dearpygui.dearpygui as dpg
from deareis.signals import Signal
import deareis.signals as signals
from deareis.utility import calculate_window_position_dimensions
import deareis.themes as themes
from deareis.tooltips import attach_tooltip
import deareis.tooltips as tooltips


@dataclass(frozen=True)
class Option:
    description: str
    rank: int
    data: Any


class BasePalette:
    def __init__(self, title: str, tooltip: str):
        self.create_window(title=title, tooltip=tooltip)
        self.options: List[Option] = []
        self.options_history: List[Option] = []

    def create_window(self, title: str, tooltip: str):
        self.window: int = dpg.generate_uuid()
        with dpg.window(
            label=title,
            no_close=True,
            modal=True,
            no_resize=True,
            show=False,
            tag=self.window,
        ):
            self.filter_input: int = dpg.generate_uuid()
            dpg.add_input_text(
                tag=self.filter_input,
                width=-1,
                callback=lambda s, a, u: self.filter_options(a.strip().lower()),
            )
            attach_tooltip(tooltip + tooltips.general.palette)
            self.options_table: int = dpg.generate_uuid()
            self.num_rows: int = 9
            with dpg.table(
                borders_outerV=True,
                borders_outerH=True,
                borders_innerV=True,
                borders_innerH=True,
                header_row=False,
                height=self.num_rows * 23,
                tag=self.options_table,
            ):
                dpg.add_table_column()
                for i in range(0, self.num_rows):
                    with dpg.table_row():
                        dpg.add_button(
                            label="",
                            callback=lambda s, a, u: self.select_option(u, click=True),
                            width=-1,
                        )

    def register_keybindings(self):
        self.key_handler: int = dpg.generate_uuid()
        with dpg.handler_registry(tag=self.key_handler):
            dpg.add_key_release_handler(
                key=dpg.mvKey_Escape,
                callback=self.hide,
            )
            dpg.add_key_release_handler(
                key=dpg.mvKey_Return,
                callback=lambda s, a, u: self.select_option(
                    option=self.options[self.option_index]
                ),
            )
            dpg.add_key_release_handler(
                key=dpg.mvKey_Up,
                callback=lambda: self.navigate_option(step=-1),
            )
            dpg.add_key_release_handler(
                key=dpg.mvKey_Prior,
                callback=lambda: self.navigate_option(step=-5),
            )
            dpg.add_key_release_handler(
                key=dpg.mvKey_Home,
                callback=lambda: self.navigate_option(index=0),
            )
            dpg.add_key_release_handler(
                key=dpg.mvKey_Down,
                callback=lambda: self.navigate_option(step=1),
            )
            dpg.add_key_release_handler(
                key=dpg.mvKey_Next,
                callback=lambda: self.navigate_option(step=5),
            )
            dpg.add_key_release_handler(
                key=dpg.mvKey_End,
                callback=lambda: self.navigate_option(index=len(self.options) - 1),
            )

    def show(self):
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
            pos=(x, y),
            width=w,
            height=h,
        )
        self.register_keybindings()
        dpg.configure_item(
            self.filter_input,
            default_value="",
            hint="Search..."
            if len(self.options) > 0
            else "No (other) options to select!",
        )
        self.filter_options("")
        dpg.split_frame()
        dpg.focus_item(self.filter_input)

    def hide(self):
        dpg.delete_item(self.key_handler)
        dpg.hide_item(self.window)
        dpg.split_frame()
        signals.emit(Signal.UNBLOCK_KEYBINDINGS)

    def get_consecutive_letter_indices(
        self,
        source: str,
        target: str,
    ) -> List[int]:
        indices: List[int] = []
        letter: str
        for letter in source:
            index: int = -1
            if not indices or indices[-1] >= 0:
                index = target.find(letter, indices[-1] if indices else 0)
            indices.append(index)
        return indices

    def get_distances_from_word_beginning(
        self,
        letter_indices: List[int],
        target: str,
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

    def score_option(
        self,
        source: str,
        option: Option,
    ) -> float:
        assert isinstance(source, str), source
        assert isinstance(option, Option), option
        target: str = option.description.lower()
        score: float = 0.0
        if source == "":
            score -= option.rank + 1
            if option in self.options_history:
                recency_bonus: float = float(len(self.options))
                score += (
                    len(self.options_history) - self.options_history.index(option)
                ) * recency_bonus * 2
        else:
            if source in target:
                score += 100
            len_source: int = len(source)
            len_target: int = len(target)
            indices: List[int] = self.get_consecutive_letter_indices(source, target)
            num_matches: int = len(list(filter(lambda _: _ >= 0, indices)))
            # Penalize for source letters not found in the target
            score -= abs(sum(filter(lambda _: _ < 0, indices))) * 25.0
            # Reward for source letters found in the target based on proximity
            # to the beginning
            score += (
                sum(
                    map(
                        lambda _: (len_target - _) / len_target,
                        filter(lambda _: _ >= 0, indices),
                    )
                )
                * 100.0
            )
            # Penalize the difference between the number of found source
            # letters and the length of the target and normalize using the
            # length of the source
            score -= (len_target - num_matches) / len_source * 10.0
            # Reward for the proximity of found source letters to the beginning
            # of the word in which the letter was found
            distances: List[int]
            word_lengths: List[int]
            distances, word_lengths = self.get_distances_from_word_beginning(
                list(filter(lambda _: _ >= 0, indices)), target
            )
            for distance, word_length in zip(distances, word_lengths):
                score += (word_length - distance) / word_length * 15.0
        return score

    def filter_options(self, string: str):
        self.option_index = 0
        scores: Dict[Option, float] = {}
        for option in self.options:
            scores[option] = self.score_option(
                string,
                option,
            )
        self.options.sort(key=lambda _: scores[_], reverse=True)
        self.update_options()

    def update_options(self):
        i: int
        row: int
        cell: int
        option: Optional[Option]
        index: int
        for i, row in enumerate(dpg.get_item_children(self.options_table, slot=1)):
            cell = dpg.get_item_children(row, slot=1)[0]
            option = None
            if len(self.options) < self.num_rows or self.option_index < 4:
                # A row in the upper half
                index = i
                dpg.bind_item_theme(
                    cell,
                    themes.palette.option_highlighted
                    if i == self.option_index
                    else themes.palette.option,
                )
            elif len(self.options) - self.option_index < 5:
                # A row in the lower half
                index = len(self.options) + i - self.num_rows
                dpg.bind_item_theme(
                    cell,
                    themes.palette.option_highlighted
                    if i == self.num_rows - (len(self.options) - self.option_index)
                    else themes.palette.option,
                )
            else:
                # The row in the middle
                index = self.option_index + i - 4
                dpg.bind_item_theme(
                    cell,
                    themes.palette.option_highlighted
                    if i == 4
                    else themes.palette.option,
                )
            if index >= 0 and index < len(self.options):
                option = self.options[index]
            dpg.set_item_label(cell, option.description if option is not None else "")
            dpg.set_item_user_data(cell, option)

    def navigate_option(self, index: Optional[int] = None, step: Optional[int] = None):
        assert type(index) is int or index is None, index
        assert type(step) is int or step is None, step
        if index is None and step is None:
            return
        elif index is not None:
            if index >= len(self.options):
                return
        elif step is not None:
            index = self.option_index + step
            if index < 0:
                index = 0
            elif index >= len(self.options):
                index = len(self.options) - 1
        assert index is not None
        self.option_index = index
        self.update_options()

    def select_option(self, option: Optional[Option] = None, click: bool = False):
        raise NotImplementedError("NOT YET IMPLEMENTED FOR THIS PALETTE")
