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

from datetime import datetime
from hashlib import sha1
from os.path import exists
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Set,
    Tuple,
    Union,
)
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
import dearpygui.dearpygui as dpg
from numpy import (
    all as array_all,
    array,
    asarray,
    float32,
    floating,
    floor,
    integer,
    isclose,
    isnan,
    isneginf,
    isposinf,
    issubdtype,
    log10 as log,
    ndarray,
    pad,
)
from pyimpspec import (
    Circuit,
    Connection,
    Container,
    Element,
    ImpedanceError,
    InvalidParameterKey,
    ParsingError,
    TokenizingError,
    parse_cdc as _parse_cdc,
)
from deareis.typing.helpers import Tag


MATH_REGISTRY: Tag = dpg.add_texture_registry()


def rename_dict_entry(dictionary: dict, old: str, new: str):
    assert new not in dictionary
    dictionary[new] = dictionary[old]
    del dictionary[old]


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
    width: Union[int, float] = 0.96,
    height: Union[int, float] = 0.96,
) -> Tuple[int, int, int, int]:
    assert (issubdtype(type(width), floating) and width > 0.0 and width < 1.0) or (
        issubdtype(type(width), integer) and width > 0
    )
    assert (issubdtype(type(height), floating) and height > 0.0 and height < 1.0) or (
        issubdtype(type(width), integer) and height > 0
    )

    viewport_width: Tag = dpg.get_viewport_width()
    x: int
    if issubdtype(type(width), floating):
        x = floor(viewport_width * (1.0 - width) / 2)
        width = floor(viewport_width * width)
    else:
        x = floor((viewport_width - width) / 2)

    viewport_height: Tag = dpg.get_viewport_height()
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

    def adjust_width(string: str) -> str:
        if width > 0:
            return string.rjust(width)
        return string

    if isnan(value):
        return adjust_width("NaN")
    elif isposinf(value):
        return adjust_width("INF")
    elif isneginf(value):
        return adjust_width("-INF")

    fmt: str = "{:." + str(decimals) + "f}"
    if significants > 0:
        fmt = "{:." + str(significants) + "g}"

    string: str
    if exponent:
        if value == 0.0:
            return adjust_width("0")
        else:
            # Convert value to scientific format in nearest SI prefix
            # (e.g., 47311.0 -> 47e+3 or 0.000851 -> 850e-6
            # if num. significants is equal to two)
            exp: int = int(floor(log(abs(value)) / 3) * 3)
            coeff: float = value / 10**exp
            string = fmt.format(coeff).lower()
            # Convert string from, e.g., 8.5e+2 to 850
            if "e+" in string or "e-" in string:
                string = str(
                    int(
                        float(string[: string.find("e")])
                        * float("1" + string[string.find("e") :])
                    )
                )
            if exp > 0:
                string += "e+{:02d}".format(exp)
            elif exp < 0:
                string += "e-{:02d}".format(abs(exp))
    else:
        string = fmt.format(value)

    if significants > 0:
        i: int = string.find("e") if "e" in string else len(string)
        if "." not in string and i < significants:
            string = (string[:i] + ".").ljust(significants + 1, "0") + string[i:]
        elif "." in string and i < significants + 1:
            string = string[:i].ljust(significants + 1, "0") + string[i:]

    return adjust_width(string)


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


def render_math(
    math: str,
    width: int,
    height: int,
    dpi: int = 100,
    fontsize: int = 12,
    alpha: float = 0.0,
    print_dimensions: bool = False,
) -> int:
    fig: Figure = plt.figure(
        figsize=(
            width / dpi,
            height / dpi,
        ),
        dpi=dpi,
    )
    canvas: FigureCanvasAgg = FigureCanvasAgg(fig)
    fig.patch.set_alpha(alpha)
    ax: Axes = fig.gca()
    ax.text(
        0.0,
        0.5,
        math,
        va="center",
        color="white",
        fontsize=fontsize,
    )
    ax.set_axis_off()
    fig.subplots_adjust(
        left=0.0,
        bottom=0.0,
        right=1.0,
        top=1.0,
        wspace=0.0,
        hspace=0.0,
    )
    canvas.draw()
    buffer: ndarray = asarray(canvas.buffer_rgba()).astype(float32) / 255

    if print_dimensions:
        min_x: int = 0
        max_x: int = buffer.shape[1] - 1
        min_y: int = 0
        max_y: int = buffer.shape[0] - 1

        i: int
        row: ndarray
        col: ndarray
        rgba_sums: ndarray
        for i, row in enumerate(buffer):
            rgba_sums = row.sum(1)
            if isclose(rgba_sums[0], 3.0 + alpha, atol=1e-2) and array_all(
                isclose(rgba_sums, rgba_sums[0])
            ):
                # All pixels in this row are just the background (1.0, 1.0, 1.0, alpha)
                min_y = i
            else:
                break

        for i, row in reversed(list(enumerate(buffer))):
            rgba_sums = row.sum(1)
            if isclose(rgba_sums[0], 3.0 + alpha, atol=1e-2) and array_all(
                isclose(rgba_sums, rgba_sums[0])
            ):
                # All pixels in this row are just the background (1.0, 1.0, 1.0, alpha)
                max_y = i + 1
            else:
                break

        for i in range(buffer.shape[1]):
            col = buffer[:, i]
            rgba_sums = col.sum(1)
            if isclose(rgba_sums[0], 3.0 + alpha, atol=1e-2) and array_all(
                isclose(rgba_sums, rgba_sums[0])
            ):
                # All pixels in this column are just the background (1.0, 1.0, 1.0, alpha)
                min_x = i
            else:
                break

        for i in reversed(range(buffer.shape[1])):
            col = buffer[:, i]
            rgba_sums = col.sum(1)
            if isclose(rgba_sums[0], 3.0 + alpha, atol=1e-2) and array_all(
                isclose(rgba_sums, rgba_sums[0])
            ):
                # All pixels in this column are just the background (1.0, 1.0, 1.0, alpha)
                max_x = i + 1
            else:
                break

        print(f"{math}\n- width: {max_x - min_x}\n- height: {max_y - min_y}")

    tag: Tag = dpg.add_raw_texture(
        buffer.shape[1],
        buffer.shape[0],
        buffer,
        format=dpg.mvFormat_Float_rgba,
        parent=MATH_REGISTRY,
    )
    plt.close(fig)

    return tag


def find_parent_containers(circuit: Circuit) -> Dict[Element, Container]:
    parent_containers: Dict[Element, Container] = {}

    def mark_elements(connection: Connection, container: Optional[Container]):
        nonlocal parent_containers

        elem_or_con: Union[Element, Connection]
        for elem_or_con in connection:
            if isinstance(elem_or_con, Connection):
                mark_elements(connection=elem_or_con, container=container)
            elif isinstance(elem_or_con, Container):
                if container is not None:
                    parent_containers[elem_or_con] = container

                con: Optional[Connection]
                for con in elem_or_con.get_subcircuits().values():
                    if con is None:
                        continue

                    mark_elements(connection=con, container=elem_or_con)

            elif container is not None:
                parent_containers[elem_or_con] = container

    mark_elements(
        connection=circuit.get_connections(recursive=False)[0],
        container=None,
    )

    return parent_containers


def process_cdc(cdc: str) -> Tuple[Optional[Circuit], str]:
    try:
        circuit: Circuit = _parse_cdc(cdc)
    except (TokenizingError, ParsingError, InvalidParameterKey) as err:
        return (None, str(err))

    try:
        circuit.get_impedances(array([1e-3, 1e0, 1e3]))
    except (ImpedanceError, NotImplementedError) as err:
        return (None, str(err))

    return (circuit, "")


def format_latex_value(value: Any, fmt: str = "{:.3g}") -> str:
    if isinstance(value, bool):
        return str(value)

    try:
        float(value)
    except ValueError:
        return str(value)

    return fmt.format(value)


def format_latex_unit(unit: str) -> str:
    assert isinstance(unit, str), unit
    unit = unit.strip()
    if unit == "":
        return unit

    chars: List[str] = []
    c: str
    for c in unit:
        if c == "*":
            chars.append(r" \times ")
        elif c == "/":
            chars.append(" / ")
        elif c == "(":
            chars.append("{")
        elif c == ")":
            chars.append("}")
        else:
            chars.append(c)

    unit = "".join(chars)
    return f"$\\rm {unit}$"


def format_latex_element(label: str) -> str:
    assert isinstance(label, str), label
    if "_" not in label:
        return f"$\\rm {label}$"

    assert label.count("_") == 1
    pre, post = label.split("_")

    return f"$\\rm {pre}_{{{post}}}$"


def pad_tab_labels(tab_bar: Tag):
    labels: Dict[int, str] = {}

    tab: Tag
    for tab in dpg.get_item_children(tab_bar, slot=1):
        labels[tab] = dpg.get_item_label(tab)

    longest_length: int = max(map(len, labels.values()))

    label: str
    for tab, label in labels.items():
        dpg.set_item_label(tab, label.ljust(longest_length))


class HorizontalWidgets:
    def __init__(self):
        self.table: Tag = dpg.add_table(
            header_row=False,
            policy=dpg.mvTable_SizingStretchProp,
        )
        self.stage: Tag = dpg.add_stage()
        dpg.push_container_stack(self.stage)

    def __enter__(self) -> "HorizontalWidgets":
        return self

    def __exit__(self, *args, **kwargs):
        dpg.pop_container_stack()
        with dpg.table_row(parent=self.table):
            dpg.unstage(self.stage)

    def add(self, tag: int, fraction: float):
        assert isinstance(tag, int), tag
        assert tag > 0
        assert isinstance(fraction, float), fraction
        assert 0.0 < fraction < 1.0
        dpg.add_table_column(
            init_width_or_weight=fraction,
            parent=self.table,
        )
        dpg.set_item_width(tag, -1)
