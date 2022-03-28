# Copyright 2022 DearEIS developers
# DearEIS is licensed under the GPLv3 or later (https://www.gnu.org/licenses/gpl-3.0.html).
# The licenses of DearEIS' dependencies and/or sources of portions of code are included in
# the LICENSES folder.

import dearpygui.dearpygui as dpg
from numpy import floor, log10 as log, logspace
from pandas import DataFrame
from pyimpspec import DataSet, simulate_spectrum, string_to_circuit
from datetime import datetime
from typing import List, Tuple, Union, Optional


def format_timestamp(timestamp: float) -> str:
    assert type(timestamp) is float
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")


def number_formatter(
    value: float,
    decimals: int = 1,
    width: int = -1,
    exponent: bool = True,
    significants: int = 0,
) -> str:
    assert type(decimals) is int
    assert type(width) is int
    assert type(exponent) is bool
    assert type(significants) is int and significants >= 0
    fmt: str = "{:." + str(decimals) + "f}"
    if significants > 0:
        fmt = "{:." + str(significants) + "g}"
    string: str
    if exponent:
        if value == 0.0:
            string = "0"
        else:
            exp: int = int(floor(log(abs(value)) / 3) * 3)
            coeff: float = value / 10**exp
            string = fmt.format(coeff)
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


def window_pos_dims(
    w: Union[int, float] = 0.9, h: Union[int, float] = 0.9
) -> Tuple[int, int, int, int]:
    assert (type(w) is float and w > 0.0 and w < 1.0) or (type(w) is int and w > 0)
    assert (type(h) is float and h > 0.0 and h < 1.0) or (type(w) is int and h > 0)
    width: int = dpg.get_viewport_width()
    x: int
    if type(w) is float:
        x = floor(width * (1.0 - w) / 2)
        width = floor(width * w)
    else:
        x = floor((width - w) / 2)
        width = w  # type: ignore
    height: int = dpg.get_viewport_height()
    y: int
    if type(h) is float:
        y = floor(height * (1.0 - h) / 2)
        height = floor(height * h)
    else:
        y = floor((height - h) / 2)
        height = h  # type: ignore
    return (
        int(x),
        int(y),
        int(width),
        int(height),
    )


def update_tooltip(tag: int, msg: str, wrap: bool = True):
    assert type(tag) is int
    assert type(msg) is str
    assert type(wrap) is bool
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
    assert type(msg) is str
    assert type(parent) is int
    assert type(tag) is int
    assert type(wrap) is bool
    if parent < 0:
        parent = dpg.last_item()
    if tag < 0:
        tag = dpg.generate_uuid()
    with dpg.tooltip(parent):
        dpg.add_text("", tag=tag)
    update_tooltip(tag, msg, wrap)
    return tag


def dict_to_csv(dictionary: dict) -> str:
    assert type(dictionary) is dict
    return DataFrame.from_dict(dictionary).to_csv(index=False, float_format="%.6E")


def generate_test_data() -> DataSet:
    return simulate_spectrum(
        string_to_circuit("R{R=100}(R{R=200}C{C=0.8e-6})(R{R=500}W{Y=4e-4})"),
        logspace(0, 4, num=41),
        "Boukamp test data",
    )


def is_shift_down() -> bool:
    return dpg.is_key_down(dpg.mvKey_Shift) or dpg.is_key_down(dpg.mvKey_RShift)


def is_control_down() -> bool:
    return (
        dpg.is_key_down(dpg.mvKey_Control)
        or dpg.is_key_down(dpg.mvKey_LControl)
        or dpg.is_key_down(dpg.mvKey_RControl)
    )


def is_alt_down() -> bool:
    return dpg.is_key_down(dpg.mvKey_Alt)


def get_item_pos(item: int, relative: int = -1) -> Tuple[int, int]:
    assert type(item) is int
    assert type(relative) is int
    x: int
    y: int
    x, y = dpg.get_item_pos(item)
    parent: Optional[int] = dpg.get_item_parent(item)
    while parent is not None:
        if parent == relative:
            break
        pos: Tuple[int, int] = dpg.get_item_pos(parent)
        x += pos[0]
        y += pos[1]
        parent = dpg.get_item_parent(parent)
    return (
        x,
        y,
    )
