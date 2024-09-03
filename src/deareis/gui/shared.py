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

from typing import (
    Any,
    Dict,
    List,
    Optional,
)
import dearpygui.dearpygui as dpg
from deareis.signals import Signal
import deareis.signals as signals
from deareis.data import DataSet
from deareis.typing.helpers import Tag



class DataSetsCombo:
    def __init__(self, label: str, width: int):
        self.labels: List[str] = []
        dpg.add_text(label)
        self.tag: Tag = dpg.generate_uuid()
        dpg.add_combo(
            callback=lambda s, a, u: signals.emit(
                Signal.SELECT_DATA_SET,
                data=u.get(a),
            ),
            user_data={},
            width=width,
            tag=self.tag,
        )

    def populate(self, labels: List[str], lookup: Dict[str, DataSet]):
        self.labels.clear()
        self.labels.extend(labels)
        label: str = dpg.get_value(self.tag) or ""
        if labels and label not in labels:
            label = labels[0]
        dpg.configure_item(
            self.tag,
            default_value=label,
            items=labels,
            user_data=lookup,
        )

    def get(self) -> Optional[DataSet]:
        return dpg.get_item_user_data(self.tag).get(dpg.get_value(self.tag))

    def set(self, label: str):
        assert type(label) is str, label
        assert label in self.labels, (
            label,
            self.labels,
        )
        dpg.set_value(self.tag, label)

    def get_next(self) -> Optional[DataSet]:
        lookup: Dict[str, DataSet] = dpg.get_item_user_data(self.tag)
        if not lookup:
            return None
        labels: List[str] = list(lookup.keys())
        index: int = labels.index(dpg.get_value(self.tag)) + 1
        return lookup[labels[index % len(labels)]]

    def get_previous(self) -> Optional[DataSet]:
        lookup: Dict[str, DataSet] = dpg.get_item_user_data(self.tag)
        if not lookup:
            return None
        labels: List[str] = list(lookup.keys())
        index: int = labels.index(dpg.get_value(self.tag)) - 1
        return lookup[labels[index % len(labels)]]

    def clear(self):
        dpg.configure_item(
            self.tag,
            default_value="",
        )


class ResultsCombo:
    def __init__(self, label: str, width: int):
        self.labels: Dict[str, str] = {}
        dpg.add_text(label)
        self.tag: Tag = dpg.generate_uuid()
        dpg.add_combo(
            callback=self.selection_callback,
            user_data=(
                {},
                None,
            ),
            width=width,
            tag=self.tag,
        )

    def selection_callback(self, sender: int, app_data: str, user_data: tuple):
        raise NotImplementedError()

    def adjust_label(self, old: str, longest: int) -> str:
        raise NotImplementedError()

    def populate(self, lookup: Dict[str, Any], data: Optional[DataSet]):
        self.labels.clear()
        labels: List[str] = list(lookup.keys())
        longest_label: int = max(
            list(map(lambda _: len(_[: _.find(" (")]), labels)) + [1]
        )
        old_key: str
        for old_key in labels:
            result: Any = lookup[old_key]
            del lookup[old_key]
            new_key = self.adjust_label(old_key, longest_label)
            self.labels[old_key] = new_key
            lookup[new_key] = result
        labels = list(lookup.keys())
        dpg.configure_item(
            self.tag,
            default_value=labels[0] if labels else "",
            items=labels,
            user_data=(
                lookup,
                data,
            ),
        )

    def get(self) -> Optional[Any]:
        return dpg.get_item_user_data(self.tag)[0].get(dpg.get_value(self.tag))

    def set(self, label: str):
        assert type(label) is str, label
        assert label in self.labels, (
            label,
            list(self.labels.keys()),
        )
        dpg.set_value(self.tag, label)

    def clear(self):
        dpg.configure_item(
            self.tag,
            default_value="",
        )

    def get_next(self) -> Optional[Any]:
        lookup: Dict[str, Any] = dpg.get_item_user_data(self.tag)[0]
        if not lookup:
            return None
        labels: List[str] = list(lookup.keys())
        index: int = labels.index(self.labels[dpg.get_value(self.tag)]) + 1
        return lookup[labels[index % len(labels)]]

    def get_previous(self) -> Optional[Any]:
        lookup: Dict[str, Any] = dpg.get_item_user_data(self.tag)[0]
        if not lookup:
            return None
        labels: List[str] = list(lookup.keys())
        index: int = labels.index(self.labels[dpg.get_value(self.tag)]) - 1
        return lookup[labels[index % len(labels)]]
