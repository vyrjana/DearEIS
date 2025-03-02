# DearEIS is licensed under the GPLv3 or later (https://www.gnu.org/licenses/gpl-3.0.html).
# Copyright 2025 DearEIS developers
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
    Callable,
    List,
    Optional,
)
import dearpygui.dearpygui as dpg
from deareis.typing.helpers import Tag


class Combo:
    def __init__(self, items: List[str], tag: int = -1, **kwargs):
        self.tag: Tag = dpg.generate_uuid() if tag < 0 else tag

        kwargs["default_value"] = kwargs.get(
            "default_value",
            items[0] if len(items) > 0 else "",
        )

        dpg.add_combo(
            items=items,
            tag=self.tag,
            **kwargs,
        )

    def get_items(self) -> List[str]:
        dictionary = dpg.get_item_configuration(self.tag)

        return dictionary.get("items", [])

    def set_items(self, items: List[str]) -> "Combo":
        assert len(items) == len(set(items)) > 0, items
        dpg.configure_item(
            self.tag,
            items=items,
            default_value=items[0],
        )

        return self

    def get_label(self) -> str:
        return dpg.get_value(self.tag)

    def set_label(self, label: str):
        items: List[str] = self.get_items()
        assert label in items, (label, items)
        dpg.set_value(self.tag, label)

    def get_value(self) -> Any:
        label: str = self.get_label()
        user_data: Any = self.get_user_data()
        if user_data is None:
            return None
        elif isinstance(user_data, dict):
            return user_data.get(label, None)
        elif isinstance(user_data, list):
            items: List[str] = self.get_items()
            assert len(items) == len(user_data), (items, user_data)
            return user_data[items.index(label)]

        raise NotImplementedError(
            f"Expected a dictionary or list instead of {user_data=}"
        )

    def set_value(self, value: Any) -> str:
        user_data: Any = self.get_user_data()
        if isinstance(user_data, dict):
            k: str
            v: Any
            for k, v in user_data.items():
                if v == value:
                    self.set_label(k)

                    return k
            else:
                raise ValueError(f"Could not find {value=} in {user_data=}")

        elif isinstance(user_data, list):
            items: List[str] = self.get_items()
            assert len(items) == len(user_data), (items, user_data)
            if value not in user_data:
                raise ValueError(f"Could not find {value=} in {user_data=}")

            label: str = items[user_data.index(value)]
            self.set_label(label)

            return label

        raise NotImplementedError(
            f"Expected a dictionary or list instead of {user_data=}"
        )

    def get_user_data(self) -> Any:
        return dpg.get_item_user_data(self.tag)

    def set_user_data(self, user_data: Any) -> "Combo":
        dpg.set_item_user_data(self.tag, user_data)

        return self

    def get_callback(self) -> Optional[Callable]:
        return dpg.get_item_callback(self.tag)

    def set_callback(self, callback: Optional[Callable]) -> "Combo":
        dpg.set_item_callback(self.tag, callback)

        return self

    def select_index(self, index: int) -> "Combo":
        items: List[str] = self.get_items()
        dpg.set_value(self.tag, items[index])

        return self

    def cycle(self, step: int) -> "Combo":
        label: str = self.get_label()
        items: List[str] = self.get_items()
        index: int = (items.index(label) + step) % len(items)
        dpg.set_value(self.tag, items[index])

        return self

    def hide(self):
        dpg.hide_item(self.tag)

    def show(self):
        dpg.show_item(self.tag)

    def disable(self):
        dpg.disable_item(self.tag)

    def enable(self):
        dpg.enable_item(self.tag)
