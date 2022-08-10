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

from datetime import datetime
from hashlib import sha1
from os.path import exists
from typing import (
    List,
    Optional,
    Set,
    Tuple,
    Union,
)
import dearpygui.dearpygui as dpg
from numpy import (
    floating,
    floor,
    inf,
    integer,
    issubdtype,
    log10 as log,
    nan,
    pad,
)


def calculate_checksum(*args, **kwargs) -> str:
    string: str = kwargs.get("string", "")
    path: str = kwargs.get("path", "")
    assert type(string) is str, string
    assert type(path) is str, path
    assert string != "" or (path != "" and exists(path)), (
        string,
        path,
    )
    checksum: str
    if string:
        checksum = sha1(string.encode()).hexdigest()
    elif path:
        with open(path, "rb") as fp:
            checksum = sha1(fp.read()).hexdigest()
    return checksum


def calculate_window_position_dimensions(
    width: Union[int, float] = 0.9, height: Union[int, float] = 0.9
) -> Tuple[int, int, int, int]:
    assert (issubdtype(type(width), floating) and width > 0.0 and width < 1.0) or (
        issubdtype(type(width), integer) and width > 0
    )
    assert (issubdtype(type(height), floating) and height > 0.0 and height < 1.0) or (
        issubdtype(type(width), integer) and height > 0
    )
    viewport_width: int = dpg.get_viewport_width()
    x: int
    if issubdtype(type(width), floating):
        x = floor(viewport_width * (1.0 - width) / 2)
        width = floor(viewport_width * width)
    else:
        x = floor((viewport_width - width) / 2)
    viewport_height: int = dpg.get_viewport_height()
    y: int
    if issubdtype(type(height), floating):
        y = floor(viewport_height * (1.0 - height) / 2)
        height = floor(viewport_height * height)
    else:
        y = floor((viewport_height - height) / 2)
    return (
        int(x),
        int(y),
        int(width),
        int(height),
    )


def format_timestamp(timestamp: float) -> str:
    assert issubdtype(type(timestamp), floating), timestamp
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")


def format_number(
    value: float,
    decimals: int = 1,
    width: int = -1,
    exponent: bool = True,
    significants: int = 0,
) -> str:
    float(value)  # Make sure that the value can at least be converted to a float
    assert issubdtype(type(decimals), integer), decimals
    assert issubdtype(type(width), integer), width
    assert type(exponent) is bool, exponent
    assert issubdtype(type(significants), integer) and significants >= 0, significants
    fmt: str = "{:." + str(decimals) + "f}"
    if significants > 0:
        fmt = "{:." + str(significants) + "g}"
    string: str
    if value is nan:
        string = "-"
    elif value == inf:
        string = "INF"
    elif value == -inf:
        string = "-INF"
    elif exponent:
        if value == 0.0:
            string = "0"
        else:
            exp: int = int(floor(log(abs(value)) / 3) * 3)
            coeff: float = value / 10**exp
            string = fmt.format(coeff).lower()
            if "e+03" in string:
                string = string[: string.find("e")]
                exp += 3
            if exp >= 0:
                string += "E+{:02d}".format(exp)
            else:
                string += "E-{:02d}".format(abs(exp))
    else:
        string = fmt.format(value)
    if "e" in string:
        string = string.replace("e", "E")
    if significants > 0:
        i: int = string.find("E") if "E" in string else len(string)
        if "." not in string and i < significants:
            string = (string[:i] + ".").ljust(significants + 1, "0") + string[i:]
        elif "." in string and i < significants + 1:
            string = string[:i].ljust(significants + 1, "0") + string[i:]
    if width > 1:
        string = string.rjust(width)
    if string.endswith("E+00"):
        string = string.replace("E+00", "    ")
    return string


def align_numbers(values: List[str]) -> List[str]:
    assert type(values) is list and all(map(lambda _: type(_) is str, values))
    has_negative_values: bool = any(map(lambda _: _.strip().startswith("-"), values))
    values = list(
        map(
            lambda _: _
            if not has_negative_values
            else ((" " if not _.startswith("-") else "") + _),
            map(str.strip, values),
        )
    )
    indices: List[int] = list(
        map(
            lambda _: max(
                _.find("."),
                _.lower().find("e") if "." not in _ else 0,
                len(_) if "." not in _ and "e" not in _.lower() else 0,
            ),
            values,
        )
    )
    max_index: int = max(indices)
    for i, index in enumerate(indices):
        value = values[i]
        values[i] = value.rjust(max_index - index + len(value))
    return values


def pad_dataframe_dictionary(dictionary: dict) -> Optional[dict]:
    lengths: Set[int] = set(map(len, dictionary.values()))
    max_len: int = max(lengths)
    if max_len == 0:
        return None
    elif len(lengths) > 1:
        padded_dictionary: dict = dictionary.copy()
        for label in padded_dictionary.keys():
            padded_dictionary[label] = pad(
                padded_dictionary[label],
                (
                    0,
                    max_len - len(padded_dictionary[label]),
                ),
                constant_values=None,
            )
        return padded_dictionary
    return dictionary


def is_filtered_item_visible(item: int, filter_string: str) -> bool:
    filter_string = filter_string.strip()
    if filter_string == "":
        return True
    filter_key: Optional[str] = dpg.get_item_filter_key(item)
    if filter_key is None:
        return False
    visible: bool = False
    for fragment in map(str.strip, filter_string.split(",")):
        if fragment.startswith("-"):
            visible = True
            if fragment[1:] in filter_key:
                return False
        else:
            visible = False
            if fragment in filter_key:
                return True
    return visible
