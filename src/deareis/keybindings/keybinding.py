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

from typing import Dict
from dataclasses import dataclass
import dearpygui.dearpygui as dpg
from deareis.enums import Action, action_to_string, string_to_action


dpg_to_string: Dict[int, str] = {
    dpg.mvKey_A: "A",
    dpg.mvKey_B: "B",
    dpg.mvKey_C: "C",
    dpg.mvKey_D: "D",
    dpg.mvKey_E: "E",
    dpg.mvKey_F: "F",
    dpg.mvKey_G: "G",
    dpg.mvKey_H: "H",
    dpg.mvKey_I: "I",
    dpg.mvKey_J: "J",
    dpg.mvKey_K: "K",
    dpg.mvKey_L: "L",
    dpg.mvKey_M: "M",
    dpg.mvKey_N: "N",
    dpg.mvKey_O: "O",
    dpg.mvKey_P: "P",
    dpg.mvKey_Q: "Q",
    dpg.mvKey_R: "R",
    dpg.mvKey_S: "S",
    dpg.mvKey_T: "T",
    dpg.mvKey_U: "U",
    dpg.mvKey_V: "V",
    dpg.mvKey_W: "W",
    dpg.mvKey_X: "X",
    dpg.mvKey_Y: "Y",
    dpg.mvKey_Z: "Z",
    dpg.mvKey_0: "0",
    dpg.mvKey_1: "1",
    dpg.mvKey_2: "2",
    dpg.mvKey_3: "3",
    dpg.mvKey_4: "4",
    dpg.mvKey_5: "5",
    dpg.mvKey_6: "6",
    dpg.mvKey_7: "7",
    dpg.mvKey_8: "8",
    dpg.mvKey_9: "9",
    # dpg.mvKey_Back: "",Back
    dpg.mvKey_Tab: "Tab",
    # dpg.mvKey_Clear: "",Clear
    dpg.mvKey_Return: "Enter",
    # dpg.mvKey_Shift: "Shift",
    # dpg.mvKey_Control: "Control",
    # dpg.mvKey_Alt: "",Alt
    # dpg.mvKey_Pause: "",Pause
    # dpg.mvKey_Capital: "",Capital
    dpg.mvKey_Escape: "Esc",
    dpg.mvKey_Spacebar: "Spacebar",
    dpg.mvKey_Prior: "Page up",
    dpg.mvKey_Next: "Page down",
    dpg.mvKey_End: "End",
    dpg.mvKey_Home: "Home",
    dpg.mvKey_Left: "Left",
    dpg.mvKey_Up: "Up",
    dpg.mvKey_Right: "Right",
    dpg.mvKey_Down: "Down",
    # dpg.mvKey_Select: "",Select
    # dpg.mvKey_Print: "",Print
    # dpg.mvKey_Execute: "",Execute
    # dpg.mvKey_PrintScreen: "Print screen",
    dpg.mvKey_Insert: "Insert",
    dpg.mvKey_Delete: "Delete",
    # dpg.mvKey_Help: "",Help
    # dpg.mvKey_LWin: "",LWin
    # dpg.mvKey_RWin: "",RWin
    # dpg.mvKey_Apps: "",Apps
    # dpg.mvKey_Sleep: "",Sleep
    dpg.mvKey_NumPad0: "Numpad 0",
    dpg.mvKey_NumPad1: "Numpad 1",
    dpg.mvKey_NumPad2: "Numpad 2",
    dpg.mvKey_NumPad3: "Numpad 3",
    dpg.mvKey_NumPad4: "Numpad 4",
    dpg.mvKey_NumPad5: "Numpad 5",
    dpg.mvKey_NumPad6: "Numpad 6",
    dpg.mvKey_NumPad7: "Numpad 7",
    dpg.mvKey_NumPad8: "Numpad 8",
    dpg.mvKey_NumPad9: "Numpad 9",
    # dpg.mvKey_Multiply: "",Multiply
    # dpg.mvKey_Add: "",Add
    # dpg.mvKey_Separator: "",Separator
    # dpg.mvKey_Subtract: "",Subtract
    # dpg.mvKey_Decimal: "",Decimal
    # dpg.mvKey_Divide: "",Divide
    dpg.mvKey_F1: "F1",
    dpg.mvKey_F2: "F2",
    dpg.mvKey_F3: "F3",
    dpg.mvKey_F4: "F4",
    dpg.mvKey_F5: "F5",
    dpg.mvKey_F6: "F6",
    dpg.mvKey_F7: "F7",
    dpg.mvKey_F8: "F8",
    dpg.mvKey_F9: "F9",
    dpg.mvKey_F10: "F10",
    dpg.mvKey_F11: "F11",
    dpg.mvKey_F12: "F12",
    dpg.mvKey_F13: "F13",
    dpg.mvKey_F14: "F14",
    dpg.mvKey_F15: "F15",
    dpg.mvKey_F16: "F16",
    dpg.mvKey_F17: "F17",
    dpg.mvKey_F18: "F18",
    dpg.mvKey_F19: "F19",
    dpg.mvKey_F20: "F20",
    dpg.mvKey_F21: "F21",
    dpg.mvKey_F22: "F22",
    dpg.mvKey_F23: "F23",
    dpg.mvKey_F24: "F24",
    dpg.mvKey_F25: "F25",
    dpg.mvKey_NumLock: "Num lock",
    dpg.mvKey_ScrollLock: "Scroll lock",
    dpg.mvKey_LShift: "Shift (left)",
    dpg.mvKey_RShift: "Shift (right)",
    dpg.mvKey_LControl: "Control (left)",
    dpg.mvKey_RControl: "Control (right)",
    # dpg.mvKey_LMenu: "",LMenu
    # dpg.mvKey_RMenu: "",RMenu
    # dpg.mvKey_Browser_Back: "",Browser_Back
    # dpg.mvKey_Browser_Forward: "",Browser_Forward
    # dpg.mvKey_Browser_Refresh: "",Browser_Refresh
    # dpg.mvKey_Browser_Stop: "",Browser_Stop
    # dpg.mvKey_Browser_Search: "",Browser_Search
    # dpg.mvKey_Browser_Favorites: "",Browser_Favorites
    # dpg.mvKey_Browser_Home: "",Browser_Home
    # dpg.mvKey_Volume_Mute: "",Volume_Mute
    # dpg.mvKey_Volume_Down: "",Volume_Down
    # dpg.mvKey_Volume_Up: "",Volume_Up
    # dpg.mvKey_Media_Next_Track: "",Media_Next_Track
    # dpg.mvKey_Media_Prev_Track: "",Media_Prev_Track
    # dpg.mvKey_Media_Stop: "",Media_Stop
    # dpg.mvKey_Media_Play_Pause: "",Media_Play_Pause
    # dpg.mvKey_Launch_Mail: "",Launch_Mail
    # dpg.mvKey_Launch_Media_Select: "",Launch_Media_Select
    # dpg.mvKey_Launch_App1: "",Launch_App1
    # dpg.mvKey_Launch_App2: "",Launch_App2
    # dpg.mvKey_Colon: ":",
    # dpg.mvKey_Plus: "+",
    # dpg.mvKey_Comma: ",",
    # dpg.mvKey_Minus: "-",
    # dpg.mvKey_Period: ".",
    # dpg.mvKey_Slash: "/",
    # dpg.mvKey_Tilde: "~",
    # dpg.mvKey_Open_Brace: "",Open_Brace
    # dpg.mvKey_Backslash: "\\",
    # dpg.mvKey_Close_Brace: "",Close_Brace
    # dpg.mvKey_Quote: "",Quote
    # dpg.mvKey_: "",
}
string_to_dpg: Dict[str, int] = {v: k for k, v in dpg_to_string.items()}


@dataclass
class Keybinding:
    key: int
    mod_alt: bool
    mod_ctrl: bool
    mod_shift: bool
    action: Action

    def __contains__(self, key: int) -> bool:
        assert key in dpg_to_string, key
        if self.key == key:
            return True
        elif self.mod_alt and key == dpg.mvKey_Alt:
            return True
        elif self.mod_ctrl and (
            key == dpg.mvKey_Control
            or key == dpg.mvKey_LControl
            or key == dpg.mvKey_RControl
        ):
            return True
        elif self.mod_shift and (key == dpg.mvKey_Shift or key == dpg.mvKey_RShift):
            return True
        return False

    def __str__(self) -> str:
        string: str = self.__repr__()
        return string[: string.find(":")]

    def __repr__(self) -> str:
        string: str = dpg_to_string[self.key]
        if self.mod_shift:
            string = f"Shift+{string}"
        if self.mod_ctrl:
            string = f"Ctrl+{string}"
        if self.mod_alt:
            string = f"Alt+{string}"
        string = f"{string}: {action_to_string[self.action]}"
        return string

    def to_dict(self) -> dict:
        return {
            "key": dpg_to_string[self.key],
            "mod_alt": self.mod_alt,
            "mod_ctrl": self.mod_ctrl,
            "mod_shift": self.mod_shift,
            "action": action_to_string[self.action],
        }

    @classmethod
    def from_dict(Class, dictionary) -> "Keybinding":
        dictionary["key"] = string_to_dpg[dictionary["key"]]
        dictionary["action"] = string_to_action[dictionary["action"]]
        return Class(**dictionary)
