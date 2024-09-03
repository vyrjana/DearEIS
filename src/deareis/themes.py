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

from random import choice
from types import SimpleNamespace
from typing import Dict, List, Set, Tuple
import dearpygui.dearpygui as dpg
from deareis.typing.helpers import Tag


PLOT_MARKERS: Dict[str, int] = {
    "Arrow down": dpg.mvPlotMarker_Down,
    "Arrow left": dpg.mvPlotMarker_Left,
    "Arrow right": dpg.mvPlotMarker_Right,
    "Arrow up": dpg.mvPlotMarker_Up,
    "Asterisk": dpg.mvPlotMarker_Asterisk,
    "Circle": dpg.mvPlotMarker_Circle,
    "Cross": dpg.mvPlotMarker_Cross,
    "Diamond": dpg.mvPlotMarker_Diamond,
    "Plus": dpg.mvPlotMarker_Plus,
    "Square": dpg.mvPlotMarker_Square,
}


VIBRANT_COLORS: List[List[float]] = [
    [  # Blue
        0.0,
        119.0,
        187.0,
        255.0,
    ],
    [  # Teal
        0.0,
        153.0,
        136.0,
        255.0,
    ],
    [  # Orange
        238.0,
        119.0,
        51.0,
        255.0,
    ],
    [  # Magenta
        238.0,
        51.0,
        119.0,
        255.0,
    ],
    [  # Red
        204.0,
        51.0,
        17.0,
        255.0,
    ],
    [  # Gray
        187.0,
        187.0,
        187.0,
        255.0,
    ],
    [  # Cyan
        51.0,
        187.0,
        238.0,
        255.0,
    ],
]


def get_plot_series_theme_color(parent: int) -> List[float]:
    assert type(parent) is int, parent
    color: List[float] = []

    item: int
    for item in dpg.get_item_children(parent, slot=1):
        i: int
        for i in dpg.get_item_children(item, slot=1):
            if not dpg.get_item_type(i).endswith("::mvThemeColor"):
                continue
            
            color = dpg.get_value(i)

    assert (
        type(color) is list and len(color) == 4 and all(map(lambda _: _ >= 0.0, color))
    ), color
    
    return color


def get_plot_series_theme_marker(parent: int) -> int:
    assert type(parent) is int, parent
    marker: int = -1
    
    item: int
    for item in dpg.get_item_children(parent, slot=1):
        i: int
        for i in dpg.get_item_children(item, slot=1):
            if not dpg.get_item_type(i).endswith("::mvThemeStyle"):
                continue
            
            marker = int(dpg.get_value(i)[0])
    
    assert type(marker) is int and (
        marker in PLOT_MARKERS.values() or marker == -1
    ), marker
    
    return marker


def get_random_color_marker(existing_themes: Dict[str, int]) -> Tuple[List[float], int]:
    available_colors: List[List[float]] = VIBRANT_COLORS[:]
    available_markers: List[int] = list(PLOT_MARKERS.values())
    existing_colors: List[List[float]] = []
    existing_markers: List[int] = []
    existing_combinations: List[str] = []
    
    color: List[float]
    marker: int
    
    uuid: str
    item: int
    for uuid, item in existing_themes.items():
        color = get_plot_series_theme_color(item)
        marker = get_plot_series_theme_marker(item)
        existing_colors.append(color)
        existing_markers.append(marker)
        existing_combinations.append(",".join(map(str, color)) + str(marker))
    
    if len(available_markers) > len(existing_markers):
        available_markers = list(set(available_markers) - set(existing_markers))
        ac: Set[str] = set(map(lambda _: ",".join(map(str, _)), available_colors))
        ec: Set[str] = set(map(lambda _: ",".join(map(str, _)), existing_colors))
        ac = ac - ec
        if len(ac) > 0:
            available_colors = list(map(lambda _: list(map(float, _.split(","))), ac))
            return (
                choice(available_colors),
                choice(available_markers),
            )
    
    possible_combinations: Dict[str, Tuple[List[float], int]] = {}
    combination: str
    
    for marker in PLOT_MARKERS.values():
        for color in VIBRANT_COLORS:
            combination = ",".join(map(str, color)) + str(marker)
            if combination not in existing_combinations:
                possible_combinations[combination] = (
                    color,
                    marker,
                )
    
    if len(possible_combinations) > 0:
        return choice(list(possible_combinations.values()))
    
    return (
        [255.0, 255.0, 255.0, 255.0],
        dpg.mvPlotMarker_Circle,
    )


def create_plot_series_theme(
    color: List[float],
    marker: int,
    tag: int = -1,
) -> int:
    assert (
        type(color) is list
        and len(color) == 4
        and all(map(lambda _: type(_) is float, color))
    ), color
    assert type(marker) is int and marker in PLOT_MARKERS.values(), marker
    assert type(tag) is int

    if tag < 0:
        tag = dpg.generate_uuid()

    R: float
    G: float
    B: float
    A: float
    R, G, B, A = color

    with dpg.theme(tag=tag):
        with dpg.theme_component(dpg.mvScatterSeries):
            dpg.add_theme_color(
                dpg.mvPlotCol_MarkerFill,
                (
                    R,
                    G,
                    B,
                    0.0,
                ),
                category=dpg.mvThemeCat_Plots,
            )
            dpg.add_theme_color(
                dpg.mvPlotCol_Line,
                color,
                category=dpg.mvThemeCat_Plots,
            )
            dpg.add_theme_color(
                dpg.mvPlotCol_MarkerOutline,
                color,
                category=dpg.mvThemeCat_Plots,
            )
            dpg.add_theme_style(
                dpg.mvPlotStyleVar_Marker, marker, category=dpg.mvThemeCat_Plots
            )

        with dpg.theme_component(dpg.mvLineSeries):
            dpg.add_theme_color(
                dpg.mvPlotCol_Line,
                color,
                category=dpg.mvThemeCat_Plots,
            )

        with dpg.theme_component(dpg.mvShadeSeries):
            dpg.add_theme_color(
                dpg.mvPlotCol_Fill,
                color,
                category=dpg.mvThemeCat_Plots,
            )

    return tag


def update_plot_series_theme_color(parent: int, color: List[float]):
    assert type(parent) is int, parent
    
    if type(color) is tuple:
        color = list(color)

    assert (
        type(color) is list
        and len(color) == 4
        and all(map(lambda _: type(_) is float, color))
    ), color
    
    uuids: List[int] = []
    
    item: int
    for item in dpg.get_item_children(parent, slot=1):
        i: int
        for i in dpg.get_item_children(item, slot=1):
            if not dpg.get_item_type(i).endswith("::mvThemeColor"):
                continue
            
            uuids.append(i)

    if len(uuids) == 0:
        return

    alpha: float = color[-1]
    color[-1] = 0
    dpg.set_value(uuids.pop(0), color)
    color[-1] = alpha
    
    while uuids:
        dpg.set_value(uuids.pop(0), color)


def update_plot_series_theme_marker(parent: int, marker: int):
    assert type(parent) is int, parent
    assert type(marker) is int, marker
    
    item: int
    for item in dpg.get_item_children(parent, slot=1):
        i: int
        for i in dpg.get_item_children(item, slot=1):
            if not dpg.get_item_type(i).endswith("::mvThemeStyle"):
                continue
            
            dpg.set_value(i, [marker, -1])


nyquist: SimpleNamespace = SimpleNamespace(
    **{
        "data": create_plot_series_theme(
            [51.0, 187.0, 238.0, 190.0],
            dpg.mvPlotMarker_Circle,
        ),
        "simulation": create_plot_series_theme(
            [238.0, 51.0, 119.0, 190.0],
            dpg.mvPlotMarker_Cross,
        ),
    }
)

bode: SimpleNamespace = SimpleNamespace(
    **{
        "magnitude_data": create_plot_series_theme(
            [51.0, 187.0, 238.0, 190.0],
            dpg.mvPlotMarker_Circle,
        ),
        "magnitude_simulation": create_plot_series_theme(
            [238.0, 51.0, 119.0, 190.0],
            dpg.mvPlotMarker_Cross,
        ),
        "phase_data": create_plot_series_theme(
            [238.0, 119.0, 51.0, 190.0],
            dpg.mvPlotMarker_Square,
        ),
        "phase_simulation": create_plot_series_theme(
            [0.0, 153.0, 136.0, 190.0],
            dpg.mvPlotMarker_Plus,
        ),
    }
)


zhit: SimpleNamespace = SimpleNamespace(
    **{
        "magnitude": create_plot_series_theme(
            [51.0, 187.0, 238.0, 190.0],
            dpg.mvPlotMarker_Circle,
        ),
        "weight": create_plot_series_theme(
            [238.0, 119.0, 51.0, 190.0],
            dpg.mvPlotMarker_Square,
        ),
        "window": create_plot_series_theme(
            [238.0, 119.0, 51.0, 60.0],
            dpg.mvPlotMarker_Plus,
        ),
    }
)


drt: SimpleNamespace = SimpleNamespace(
    **{
        "real_gamma": create_plot_series_theme(
            [51.0, 187.0, 238.0, 190.0],
            dpg.mvPlotMarker_Circle,
        ),
        "mean_gamma": create_plot_series_theme(
            [238.0, 119.0, 51.0, 190.0],
            dpg.mvPlotMarker_Circle,
        ),
        "credible_intervals": create_plot_series_theme(
            [238.0, 119.0, 51.0, 48.0],
            dpg.mvPlotMarker_Circle,
        ),
        "imaginary_gamma": create_plot_series_theme(
            [238.0, 119.0, 51.0, 190.0],
            dpg.mvPlotMarker_Circle,
        ),
    }
)


impedance: SimpleNamespace = SimpleNamespace(
    **{
        "real_data": create_plot_series_theme(
            [51.0, 187.0, 238.0, 190.0],
            dpg.mvPlotMarker_Circle,
        ),
        "real_simulation": create_plot_series_theme(
            [0.0, 153.0, 136.0, 190.0],
            dpg.mvPlotMarker_Cross,
        ),
        "imaginary_data": create_plot_series_theme(
            [238.0, 119.0, 51.0, 190.0],
            dpg.mvPlotMarker_Square,
        ),
        "imaginary_simulation": create_plot_series_theme(
            [238.0, 51.0, 119.0, 190.0],
            dpg.mvPlotMarker_Plus,
        ),
    }
)

residuals: SimpleNamespace = SimpleNamespace(
    **{
        "real": create_plot_series_theme(
            [0.0, 153.0, 136.0, 190.0],
            dpg.mvPlotMarker_Circle,
        ),
        "imaginary": create_plot_series_theme(
            [238.0, 51.0, 119.0, 190.0],
            dpg.mvPlotMarker_Square,
        ),
    }
)

# TODO: Replace this (and any uses of it) with the two namespaces below
mu_Xps: SimpleNamespace = SimpleNamespace(
    **{
        "mu": create_plot_series_theme(
            [238.0, 51.0, 119.0, 190.0],
            dpg.mvPlotMarker_Circle,
        ),
        "mu_highlight": create_plot_series_theme(
            [51.0, 187.0, 238.0, 190.0],
            dpg.mvPlotMarker_Circle,
        ),
        "Xps": create_plot_series_theme(
            [0.0, 153.0, 136.0, 190.0],
            dpg.mvPlotMarker_Square,
        ),
        "Xps_highlight": create_plot_series_theme(
            [238.0, 119.0, 51.0, 190.0],
            dpg.mvPlotMarker_Square,
        ),
        "mu_criterion": create_plot_series_theme(
            [255.0, 255.0, 255.0, 128.0],
            dpg.mvPlotMarker_Circle,
        ),
    }
)


pseudo_chisqr: SimpleNamespace = SimpleNamespace(
    **{
        "default": create_plot_series_theme(
            [0.0, 153.0, 136.0, 190.0],
            dpg.mvPlotMarker_Square,
        ),
        "highlight": create_plot_series_theme(
            [238.0, 119.0, 51.0, 190.0],
            dpg.mvPlotMarker_Square,
        ),
        "default_log_F_ext": create_plot_series_theme(
            [0.0, 153.0, 136.0, 190.0],
            dpg.mvPlotMarker_Circle,
        ),
        "highlight_log_F_ext": create_plot_series_theme(
            [51.0, 187.0, 238.0, 190.0],
            dpg.mvPlotMarker_Circle,
        ),
    }
)


suggestion_method: SimpleNamespace = SimpleNamespace(
    **{
        "default": create_plot_series_theme(
            [238.0, 51.0, 119.0, 190.0],
            dpg.mvPlotMarker_Circle,
        ),
        "highlight": create_plot_series_theme(
            [51.0, 187.0, 238.0, 190.0],
            dpg.mvPlotMarker_Circle,
        ),
        "threshold": create_plot_series_theme(
            [0.0, 153.0, 136.0, 190.0],
            dpg.mvPlotMarker_Square,
        ),
        "range": create_plot_series_theme(
            [0.0, 136.0, 255.0, 32.0],
            dpg.mvPlotMarker_Circle,
        ),
    }
)


plot: Tag
with dpg.theme() as plot:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(
            dpg.mvPlotCol_FrameBg,
            [
                255.0,
                255.0,
                255.0,
                0.0,
            ],
            category=dpg.mvThemeCat_Plots,
        )


_clean_tab: Tag = dpg.generate_uuid()
_dirty_tab: Tag = dpg.generate_uuid()
with dpg.theme(tag=_clean_tab):
    with dpg.theme_component(dpg.mvTab):
        dpg.add_theme_color(
            dpg.mvThemeCol_TabActive,
            [
                0.0,
                119.0,
                200.0,
                153.0,
            ],
        )
        dpg.add_theme_color(
            dpg.mvThemeCol_TabHovered,
            [
                29.0,
                151.0,
                236.0,
                103.0,
            ],
        )
        dpg.add_theme_color(
            dpg.mvThemeCol_Tab,
            [
                51.0,
                51.0,
                55.0,
                255.0,
            ],
        )
        dpg.add_theme_color(
            dpg.mvThemeCol_TabUnfocused,
            [
                51.0,
                51.0,
                55.0,
                255.0,
            ],
        )
        dpg.add_theme_color(
            dpg.mvThemeCol_TabUnfocusedActive,
            [
                0.0,
                119.0,
                200.0,
                153.0,
            ],
        )
with dpg.theme(tag=_dirty_tab):
    with dpg.theme_component(dpg.mvTab):
        dpg.add_theme_color(
            dpg.mvThemeCol_TabActive,
            [
                236.0,
                32.0,
                29.0,
                103.0,
            ],
        )
        dpg.add_theme_color(
            dpg.mvThemeCol_TabHovered,
            [
                236.0,
                80.0,
                80.0,
                153.0,
            ],
        )
        dpg.add_theme_color(
            dpg.mvThemeCol_Tab,
            [
                138.0,
                61.0,
                61.0,
                100.0,
            ],
        )
        dpg.add_theme_color(
            dpg.mvThemeCol_TabUnfocused,
            [
                138.0,
                61.0,
                61.0,
                100.0,
            ],
        )
        dpg.add_theme_color(
            dpg.mvThemeCol_TabUnfocusedActive,
            [
                236.0,
                32.0,
                29.0,
                103.0,
            ],
        )
tab: SimpleNamespace = SimpleNamespace(
    **{
        "clean": _clean_tab,
        "dirty": _dirty_tab,
    }
)


_valid_cdc: Tag = dpg.generate_uuid()
_invalid_cdc: Tag = dpg.generate_uuid()
_normal_cdc: Tag = dpg.generate_uuid()
with dpg.theme(tag=_valid_cdc):
    with dpg.theme_component(dpg.mvInputText, enabled_state=True):
        dpg.add_theme_color(
            dpg.mvThemeCol_Text,
            [
                255.0,
                255.0,
                255.0,
                255.0,
            ],
        )
    with dpg.theme_component(dpg.mvInputText, enabled_state=False):
        dpg.add_theme_color(
            dpg.mvThemeCol_Text,
            [
                255.0,
                255.0,
                255.0,
                255.0,
            ],
        )
with dpg.theme(tag=_invalid_cdc):
    with dpg.theme_component(dpg.mvInputText, enabled_state=True):
        dpg.add_theme_color(
            dpg.mvThemeCol_Text,
            [
                255.0,
                0.0,
                0.0,
                255.0,
            ],
        )
    with dpg.theme_component(dpg.mvInputText, enabled_state=False):
        dpg.add_theme_color(
            dpg.mvThemeCol_Text,
            [
                255.0,
                0.0,
                0.0,
                255.0,
            ],
        )
with dpg.theme(tag=_normal_cdc):
    with dpg.theme_component(dpg.mvInputText, enabled_state=True):
        dpg.add_theme_color(
            dpg.mvThemeCol_Text,
            [
                255.0,
                255.0,
                255.0,
                255.0,
            ],
        )
    with dpg.theme_component(dpg.mvInputText, enabled_state=False):
        dpg.add_theme_color(
            dpg.mvThemeCol_Text,
            [
                100.0,
                100.0,
                100.0,
                255.0,
            ],
        )
cdc: SimpleNamespace = SimpleNamespace(
    **{
        "valid": _valid_cdc,
        "invalid": _invalid_cdc,
        "normal": _normal_cdc,
    }
)


_valid_result: Tag = dpg.generate_uuid()
_invalid_result: Tag = dpg.generate_uuid()
with dpg.theme(tag=_valid_result):
    with dpg.theme_component(dpg.mvText, enabled_state=True):
        dpg.add_theme_color(
            dpg.mvThemeCol_Text,
            [
                255.0,
                255.0,
                255.0,
                255.0,
            ],
        )
    with dpg.theme_component(dpg.mvText, enabled_state=False):
        dpg.add_theme_color(
            dpg.mvThemeCol_Text,
            [
                255.0,
                255.0,
                255.0,
                255.0,
            ],
        )
with dpg.theme(tag=_invalid_result):
    with dpg.theme_component(dpg.mvText, enabled_state=True):
        dpg.add_theme_color(
            dpg.mvThemeCol_Text,
            [
                255.0,
                0.0,
                0.0,
                255.0,
            ],
        )
    with dpg.theme_component(dpg.mvText, enabled_state=False):
        dpg.add_theme_color(
            dpg.mvThemeCol_Text,
            [
                255.0,
                0.0,
                0.0,
                255.0,
            ],
        )
result: SimpleNamespace = SimpleNamespace(
    **{
        "valid": _valid_result,
        "invalid": _invalid_result,
    }
)


_default_background_color = (
    62.0,
    62.0,
    62.0,
    255.0,
)
_default_title_bar_color = (
    37.0,
    37.0,
    37.0,
    255.0,
)
_default_outline_color = (
    100.0,
    100.0,
    100.0,
    255.0,
)
_invalid_color = (
    151.0,
    29.0,
    29.0,
    255.0,
)

_invalid_unselected_node: Tag = dpg.generate_uuid()
with dpg.theme(tag=_invalid_unselected_node):
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(
            dpg.mvNodeCol_NodeBackground,
            _invalid_color,
            category=dpg.mvThemeCat_Nodes,
        )
        dpg.add_theme_color(
            dpg.mvNodeCol_NodeBackgroundHovered,
            _invalid_color,
            category=dpg.mvThemeCat_Nodes,
        )
        dpg.add_theme_color(
            dpg.mvNodeCol_NodeBackgroundSelected,
            _invalid_color,
            category=dpg.mvThemeCat_Nodes,
        )
        dpg.add_theme_color(
            dpg.mvNodeCol_TitleBar,
            _default_title_bar_color,
            category=dpg.mvThemeCat_Nodes,
        )
        dpg.add_theme_color(
            dpg.mvNodeCol_TitleBarHovered,
            _default_title_bar_color,
            category=dpg.mvThemeCat_Nodes,
        )
        dpg.add_theme_color(
            dpg.mvNodeCol_TitleBarSelected,
            _default_title_bar_color,
            category=dpg.mvThemeCat_Nodes,
        )
        dpg.add_theme_color(
            dpg.mvNodeCol_NodeOutline,
            _default_outline_color,
            category=dpg.mvThemeCat_Nodes,
        )
        dpg.add_theme_color(
            dpg.mvThemeCol_Text,
            (
                255.0,
                0.0,
                0.0,
                255.0,
            ),
            category=dpg.mvThemeCat_Core,
        )

_invalid_selected_node: Tag = dpg.generate_uuid()
with dpg.theme(tag=_invalid_selected_node):
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(
            dpg.mvNodeCol_NodeBackground,
            _invalid_color,
            category=dpg.mvThemeCat_Nodes,
        )
        dpg.add_theme_color(
            dpg.mvNodeCol_NodeBackgroundHovered,
            _invalid_color,
            category=dpg.mvThemeCat_Nodes,
        )
        dpg.add_theme_color(
            dpg.mvNodeCol_NodeBackgroundSelected,
            _invalid_color,
            category=dpg.mvThemeCat_Nodes,
        )
        dpg.add_theme_color(
            dpg.mvNodeCol_TitleBar,
            _default_title_bar_color,
            category=dpg.mvThemeCat_Nodes,
        )
        dpg.add_theme_color(
            dpg.mvNodeCol_TitleBarHovered,
            _default_title_bar_color,
            category=dpg.mvThemeCat_Nodes,
        )
        dpg.add_theme_color(
            dpg.mvNodeCol_TitleBarSelected,
            _default_title_bar_color,
            category=dpg.mvThemeCat_Nodes,
        )
        dpg.add_theme_color(
            dpg.mvNodeCol_NodeOutline,
            _invalid_color,
            category=dpg.mvThemeCat_Nodes,
        )
        dpg.add_theme_color(
            dpg.mvThemeCol_Text,
            (
                255.0,
                0.0,
                0.0,
                255.0,
            ),
            category=dpg.mvThemeCat_Core,
        )

_valid_color = (
    15.0,
    86.0,
    135.0,
    255.0,
)

_valid_selected_node: Tag = dpg.generate_uuid()
with dpg.theme(tag=_valid_selected_node):
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(
            dpg.mvNodeCol_NodeBackground,
            _valid_color,
            category=dpg.mvThemeCat_Nodes,
        )
        dpg.add_theme_color(
            dpg.mvNodeCol_NodeBackgroundHovered,
            _valid_color,
            category=dpg.mvThemeCat_Nodes,
        )
        dpg.add_theme_color(
            dpg.mvNodeCol_NodeBackgroundSelected,
            _valid_color,
            category=dpg.mvThemeCat_Nodes,
        )
        dpg.add_theme_color(
            dpg.mvNodeCol_TitleBar,
            _default_title_bar_color,
            category=dpg.mvThemeCat_Nodes,
        )
        dpg.add_theme_color(
            dpg.mvNodeCol_TitleBarHovered,
            _default_title_bar_color,
            category=dpg.mvThemeCat_Nodes,
        )
        dpg.add_theme_color(
            dpg.mvNodeCol_TitleBarSelected,
            _default_title_bar_color,
            category=dpg.mvThemeCat_Nodes,
        )
        dpg.add_theme_color(
            dpg.mvNodeCol_NodeOutline,
            _valid_color,
            category=dpg.mvThemeCat_Nodes,
        )
        dpg.add_theme_color(
            dpg.mvThemeCol_Text,
            (
                255.0,
                255.0,
                255.0,
                255.0,
            ),
            category=dpg.mvThemeCat_Core,
        )

_valid_unselected_node: Tag = dpg.generate_uuid()
with dpg.theme(tag=_valid_unselected_node):
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(
            dpg.mvNodeCol_NodeBackground,
            _default_background_color,
            category=dpg.mvThemeCat_Nodes,
        )
        dpg.add_theme_color(
            dpg.mvNodeCol_NodeBackgroundHovered,
            _default_background_color,
            category=dpg.mvThemeCat_Nodes,
        )
        dpg.add_theme_color(
            dpg.mvNodeCol_NodeBackgroundSelected,
            _default_background_color,
            category=dpg.mvThemeCat_Nodes,
        )
        dpg.add_theme_color(
            dpg.mvNodeCol_TitleBar,
            _default_title_bar_color,
            category=dpg.mvThemeCat_Nodes,
        )
        dpg.add_theme_color(
            dpg.mvNodeCol_TitleBarHovered,
            _default_title_bar_color,
            category=dpg.mvThemeCat_Nodes,
        )
        dpg.add_theme_color(
            dpg.mvNodeCol_TitleBarSelected,
            _default_title_bar_color,
            category=dpg.mvThemeCat_Nodes,
        )
        dpg.add_theme_color(
            dpg.mvNodeCol_NodeOutline,
            _default_outline_color,
            category=dpg.mvThemeCat_Nodes,
        )
        dpg.add_theme_color(
            dpg.mvThemeCol_Text,
            (
                255.0,
                255.0,
                255.0,
                255.0,
            ),
            category=dpg.mvThemeCat_Core,
        )

_preview_node: Tag = dpg.generate_uuid()
_link_color = (255, 255, 255, 200)
_pin_color = (255, 255, 255, 0)

with dpg.theme(tag=_preview_node):
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(
            dpg.mvNodeCol_NodeBackground,
            _default_background_color,
            category=dpg.mvThemeCat_Nodes,
        )
        dpg.add_theme_color(
            dpg.mvNodeCol_NodeBackgroundHovered,
            _default_background_color,
            category=dpg.mvThemeCat_Nodes,
        )
        dpg.add_theme_color(
            dpg.mvNodeCol_NodeBackgroundSelected,
            _default_background_color,
            category=dpg.mvThemeCat_Nodes,
        )
        dpg.add_theme_color(
            dpg.mvNodeCol_TitleBar,
            _default_title_bar_color,
            category=dpg.mvThemeCat_Nodes,
        )
        dpg.add_theme_color(
            dpg.mvNodeCol_TitleBarHovered,
            _default_title_bar_color,
            category=dpg.mvThemeCat_Nodes,
        )
        dpg.add_theme_color(
            dpg.mvNodeCol_TitleBarSelected,
            _default_title_bar_color,
            category=dpg.mvThemeCat_Nodes,
        )
        dpg.add_theme_color(
            dpg.mvNodeCol_NodeOutline,
            _default_outline_color,
            category=dpg.mvThemeCat_Nodes,
        )
        dpg.add_theme_color(
            dpg.mvThemeCol_Text,
            (
                255.0,
                255.0,
                255.0,
                255.0,
            ),
            category=dpg.mvThemeCat_Core,
        )
        dpg.add_theme_color(
            dpg.mvNodeCol_Link,
            _link_color,
            category=dpg.mvThemeCat_Nodes,
        )
        dpg.add_theme_color(
            dpg.mvNodeCol_LinkHovered,
            _link_color,
            category=dpg.mvThemeCat_Nodes,
        )
        dpg.add_theme_color(
            dpg.mvNodeCol_LinkSelected,
            _link_color,
            category=dpg.mvThemeCat_Nodes,
        )
        dpg.add_theme_color(
            dpg.mvNodeCol_Pin,
            _pin_color,
            category=dpg.mvThemeCat_Nodes,
        )
        dpg.add_theme_color(
            dpg.mvNodeCol_PinHovered,
            _pin_color,
            category=dpg.mvThemeCat_Nodes,
        )
        dpg.add_theme_style(
            dpg.mvNodeStyleVar_NodePadding,
            x=8,
            y=4,
            category=dpg.mvThemeCat_Nodes,
        )

circuit_editor: SimpleNamespace = SimpleNamespace(
    **{
        "valid_selected_node": _valid_selected_node,
        "valid_unselected_node": _valid_unselected_node,
        "invalid_selected_node": _invalid_selected_node,
        "invalid_unselected_node": _invalid_unselected_node,
        "preview_node": _preview_node,
    }
)


_limited_parameter: Tag = dpg.generate_uuid()
with dpg.theme(tag=_limited_parameter):
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(
            dpg.mvThemeCol_Text,
            (
                255.0,
                0.0,
                0.0,
                255.0,
            ),
            category=dpg.mvThemeCat_Core,
        )

_huge_error: Tag = dpg.generate_uuid()
with dpg.theme(tag=_huge_error):
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(
            dpg.mvThemeCol_Text,
            (
                255.0,
                0.0,
                0.0,
                255.0,
            ),
            category=dpg.mvThemeCat_Core,
        )

_large_error: Tag = dpg.generate_uuid()
with dpg.theme(tag=_large_error):
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(
            dpg.mvThemeCol_Text,
            (
                255.0,
                115.0,
                0.0,
                255.0,
            ),
            category=dpg.mvThemeCat_Core,
        )

_default_statistic: Tag = dpg.generate_uuid()
with dpg.theme(tag=_default_statistic):
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(
            dpg.mvThemeCol_Text,
            (
                255.0,
                255.0,
                255.0,
                255.0,
            ),
            category=dpg.mvThemeCat_Core,
        )

_highlighted_statistic: Tag = dpg.generate_uuid()
with dpg.theme(tag=_highlighted_statistic):
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(
            dpg.mvThemeCol_Text,
            (
                255.0,
                115.0,
                0.0,
                255.0,
            ),
            category=dpg.mvThemeCat_Core,
        )

fitting: SimpleNamespace = SimpleNamespace(
    **{
        "limited_parameter": _limited_parameter,
        "huge_error": _huge_error,
        "large_error": _large_error,
        "highlighted_statistc": _highlighted_statistic,
        "default_statistic": _default_statistic,
    }
)


_palette_option_highlighted: int
with dpg.theme() as _palette_option_highlighted:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(
            dpg.mvThemeCol_Text,
            [255.0, 255.0, 255.0, 255.0],
            category=dpg.mvThemeCat_Core,
        )
        dpg.add_theme_color(
            dpg.mvThemeCol_Button,
            [0.0, 119.0, 200.0, 100.0],
            category=dpg.mvThemeCat_Core,
        )
        dpg.add_theme_style(
            dpg.mvStyleVar_ButtonTextAlign,
            0.0,
            0.5,
            category=dpg.mvThemeCat_Core,
        )

_palette_option: int
with dpg.theme() as _palette_option:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(
            dpg.mvThemeCol_Text,
            [255.0, 255.0, 255.0, 255.0],
            category=dpg.mvThemeCat_Core,
        )
        dpg.add_theme_color(
            dpg.mvThemeCol_Button,
            [51.0, 51.0, 55.0, 255.0],
            category=dpg.mvThemeCat_Core,
        )
        dpg.add_theme_style(
            dpg.mvStyleVar_ButtonTextAlign,
            0.0,
            0.5,
            category=dpg.mvThemeCat_Core,
        )

palette: SimpleNamespace = SimpleNamespace(
    **{
        "option": _palette_option,
        "option_highlighted": _palette_option_highlighted,
    }
)


_file_dialog_folder: int
with dpg.theme() as _file_dialog_folder:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_style(
            dpg.mvStyleVar_ButtonTextAlign,
            0.0,
            0.5,
            category=dpg.mvThemeCat_Core,
        )

_file_dialog_file: int
with dpg.theme() as _file_dialog_file:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_style(
            dpg.mvStyleVar_ButtonTextAlign,
            0.0,
            0.5,
            category=dpg.mvThemeCat_Core,
        )

file_dialog: SimpleNamespace = SimpleNamespace(
    **{
        "folder_button": _file_dialog_folder,
        "file_button": _file_dialog_file,
    }
)


transparent_modal_background: int
with dpg.theme() as transparent_modal_background:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(
            dpg.mvThemeCol_ModalWindowDimBg,
            [0.0, 0.0, 0.0, 0.0],
            category=dpg.mvThemeCat_Core,
        )

_valid_path: Tag = dpg.generate_uuid()
_invalid_path: Tag = dpg.generate_uuid()
with dpg.theme(tag=_valid_path):
    with dpg.theme_component(dpg.mvInputText, enabled_state=True):
        dpg.add_theme_color(
            dpg.mvThemeCol_Text,
            [
                255.0,
                255.0,
                255.0,
                255.0,
            ],
        )
    with dpg.theme_component(dpg.mvInputText, enabled_state=False):
        dpg.add_theme_color(
            dpg.mvThemeCol_Text,
            [
                255.0,
                255.0,
                255.0,
                255.0,
            ],
        )

with dpg.theme(tag=_invalid_path):
    with dpg.theme_component(dpg.mvInputText, enabled_state=True):
        dpg.add_theme_color(
            dpg.mvThemeCol_Text,
            [
                255.0,
                0.0,
                0.0,
                255.0,
            ],
        )
    with dpg.theme_component(dpg.mvInputText, enabled_state=False):
        dpg.add_theme_color(
            dpg.mvThemeCol_Text,
            [
                255.0,
                0.0,
                0.0,
                255.0,
            ],
        )

path: SimpleNamespace = SimpleNamespace(
    **{
        "valid": _valid_path,
        "invalid": _invalid_path,
    }
)


# URL theme
url_theme: int
with dpg.theme() as url_theme:
    with dpg.theme_component(dpg.mvAll, enabled_state=True):
        dpg.add_theme_style(
            dpg.mvStyleVar_ButtonTextAlign,
            0.0,
            0.5,
            category=dpg.mvThemeCat_Core,
        )


# Global theme
_greyed_out: List[float] = [
    100.0,
    100.0,
    100.0,
    255.0,
]
_rounding: int = 2

global_theme: int
with dpg.theme() as global_theme:
    # Enabled
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_style(
            dpg.mvStyleVar_WindowRounding,
            _rounding,
            category=dpg.mvThemeCat_Core,
        )
        dpg.add_theme_style(
            dpg.mvStyleVar_ChildRounding,
            _rounding,
            category=dpg.mvThemeCat_Core,
        )
        dpg.add_theme_style(
            dpg.mvStyleVar_FrameRounding,
            _rounding,
            category=dpg.mvThemeCat_Core,
        )
        dpg.add_theme_style(
            dpg.mvStyleVar_PopupRounding,
            _rounding,
            category=dpg.mvThemeCat_Core,
        )
        dpg.add_theme_style(
            dpg.mvStyleVar_ScrollbarRounding,
            _rounding,
            category=dpg.mvThemeCat_Core,
        )
        dpg.add_theme_style(
            dpg.mvStyleVar_GrabRounding,
            _rounding,
            category=dpg.mvThemeCat_Core,
        )
        dpg.add_theme_style(
            dpg.mvStyleVar_TabRounding,
            _rounding,
            category=dpg.mvThemeCat_Core,
        )

        # Plots
        dpg.add_theme_style(
            dpg.mvPlotStyleVar_PlotPadding,
            8,
            8,
            category=dpg.mvThemeCat_Plots,
        )
        dpg.add_theme_style(
            dpg.mvPlotStyleVar_LabelPadding,
            5,
            2,
            category=dpg.mvThemeCat_Plots,
        )
        dpg.add_theme_style(
            dpg.mvPlotStyleVar_LegendPadding,
            5,
            5,
            category=dpg.mvThemeCat_Plots,
        )
        dpg.add_theme_style(
            dpg.mvPlotStyleVar_LegendInnerPadding,
            4,
            4,
            category=dpg.mvThemeCat_Plots,
        )
        dpg.add_theme_style(
            dpg.mvPlotStyleVar_MousePosPadding,
            8,
            8,
            category=dpg.mvThemeCat_Plots,
        )
        dpg.add_theme_style(
            dpg.mvPlotStyleVar_LineWeight,
            1.5,
            category=dpg.mvThemeCat_Plots,
        )
        dpg.add_theme_style(
            dpg.mvPlotStyleVar_MarkerSize,
            4.5,
            category=dpg.mvThemeCat_Plots,
        )
        dpg.add_theme_style(
            dpg.mvPlotStyleVar_MarkerWeight,
            2.0,
            category=dpg.mvThemeCat_Plots,
        )

        # Nodes
        dpg.add_theme_color(
            dpg.mvNodeCol_GridLine,
            [255.0, 255.0, 255.0, 15.0],
            category=dpg.mvThemeCat_Nodes,
        )

    # Disabled
    with dpg.theme_component(dpg.mvText, enabled_state=False):
        dpg.add_theme_color(dpg.mvThemeCol_Text, _greyed_out)

    with dpg.theme_component(dpg.mvSliderFloat, enabled_state=False):
        dpg.add_theme_color(dpg.mvThemeCol_Text, _greyed_out)
        dpg.add_theme_color(dpg.mvThemeCol_SliderGrab, _greyed_out)

    with dpg.theme_component(dpg.mvCombo, enabled_state=False):
        dpg.add_theme_color(dpg.mvThemeCol_Text, _greyed_out)

    with dpg.theme_component(dpg.mvCheckbox, enabled_state=False):
        dpg.add_theme_color(dpg.mvThemeCol_Text, _greyed_out)
        dpg.add_theme_color(dpg.mvThemeCol_CheckMark, _greyed_out)

    with dpg.theme_component(dpg.mvInputFloat, enabled_state=False):
        dpg.add_theme_color(dpg.mvThemeCol_Text, _greyed_out)
        dpg.add_theme_color(dpg.mvThemeCol_Button, _greyed_out)

    with dpg.theme_component(dpg.mvInputInt, enabled_state=False):
        dpg.add_theme_color(dpg.mvThemeCol_Text, _greyed_out)
        dpg.add_theme_color(dpg.mvThemeCol_Button, _greyed_out)

    with dpg.theme_component(dpg.mvInputText, enabled_state=False):
        dpg.add_theme_color(dpg.mvThemeCol_Text, _greyed_out)
        dpg.add_theme_color(dpg.mvThemeCol_Button, _greyed_out)

    with dpg.theme_component(dpg.mvButton, enabled_state=False):
        dpg.add_theme_color(dpg.mvThemeCol_Text, _greyed_out)

dpg.bind_theme(global_theme)
