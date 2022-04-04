# Copyright 2022 DearEIS developers
# DearEIS is licensed under the GPLv3 or later (https://www.gnu.org/licenses/gpl-3.0.html).
# The licenses of DearEIS' dependencies and/or sources of portions of code are included in
# the LICENSES folder.

from typing import Dict, List, Tuple, Union
import dearpygui.dearpygui as dpg
from deareis.config import CONFIG


Color = Union[Tuple[int, int, int, int], List[float], List[int]]

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
# The vibrant color scheme is from https://personal.sron.nl/~pault/
VIBRANT_COLORS: List[Color] = [
    (
        0.0,
        119.0,
        187.0,
        255.0,
    ),
    (
        0.0,
        153.0,
        136.0,
        255.0,
    ),
    (
        238.0,
        119.0,
        51.0,
        255.0,
    ),
    (
        238.0,
        51.0,
        119.0,
        255.0,
    ),
    (
        204.0,
        51.0,
        17.0,
        255.0,
    ),
    (
        187.0,
        187.0,
        187.0,
        255.0,
    ),
    (
        51.0,
        187.0,
        238.0,
        255.0,
    ),
]

# Themes
# - Plots
plot_theme: int = -1
real_error: int = -1
imag_error: int = -1
nyquist_data: int = -1
nyquist_sim: int = -1
bode_magnitude_data: int = -1
bode_magnitude_sim: int = -1
bode_phase_data: int = -1
bode_phase_sim: int = -1
exploratory_mu_criterion: int = -1
exploratory_mu: int = -1
exploratory_mu_highlight: int = -1
exploratory_xps: int = -1
exploratory_xps_highlight: int = -1
#
valid_cdc: int = -1
invalid_cdc: int = -1
valid_node: int = -1
invalid_node: int = -1


def create_plot_theme(
    tag: int,
    color: Color,
    marker: int,
):
    assert type(tag) is int
    assert (
        (type(color) is tuple or type(color) is list)
        and len(color) == 4
        and all(map(lambda _: type(_) is int or type(_) is float, color))
    )
    assert type(marker) is int
    R: int
    G: int
    B: int
    A: int
    R, G, B, A = color
    with dpg.theme(tag=tag):
        with dpg.theme_component(dpg.mvScatterSeries):
            dpg.add_theme_color(
                dpg.mvPlotCol_MarkerFill,
                (
                    R,
                    G,
                    B,
                    0,
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


def update_plot_theme_color(parent: int, color: List[float]):
    assert type(parent) is int
    if type(color) is tuple:
        color = list(color)
    assert (
        type(color) is list
        and len(color) == 4
        and all(map(lambda _: type(_) is float, color))
    )
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


def update_plot_theme_marker(parent: int, marker: int):
    assert type(parent) is int
    assert type(marker) is int
    item: int
    for item in dpg.get_item_children(parent, slot=1):
        i: int
        for i in dpg.get_item_children(item, slot=1):
            if not dpg.get_item_type(i).endswith("::mvThemeStyle"):
                continue
            dpg.set_value(i, [marker, -1])


def get_plot_theme_color(parent: int) -> List[float]:
    assert type(parent) is int
    color: List[float] = []
    item: int
    for item in dpg.get_item_children(parent, slot=1):
        i: int
        for i in dpg.get_item_children(item, slot=1):
            if not dpg.get_item_type(i).endswith("::mvThemeColor"):
                continue
            color = dpg.get_value(i)
    assert type(color) is list and len(color) == 4
    return color


def get_plot_theme_marker(parent: int) -> int:
    assert type(parent) is int
    marker: int = -1
    item: int
    for item in dpg.get_item_children(parent, slot=1):
        i: int
        for i in dpg.get_item_children(item, slot=1):
            if not dpg.get_item_type(i).endswith("::mvThemeStyle"):
                continue
            marker = int(dpg.get_value(i)[0])
    assert type(marker) is int and marker >= 0, marker
    return marker


def initialize():
    global plot_theme
    global real_error
    global imag_error
    global nyquist_data
    global nyquist_sim
    global bode_magnitude_data
    global bode_magnitude_sim
    global bode_phase_data
    global bode_phase_sim
    global exploratory_mu_criterion
    global exploratory_mu
    global exploratory_mu_highlight
    global exploratory_xps
    global exploratory_xps_highlight
    global valid_cdc
    global invalid_cdc
    global valid_node
    global invalid_node
    plot_theme = dpg.generate_uuid()
    real_error = dpg.generate_uuid()
    imag_error = dpg.generate_uuid()
    nyquist_data = dpg.generate_uuid()
    nyquist_sim = dpg.generate_uuid()
    bode_magnitude_data = dpg.generate_uuid()
    bode_magnitude_sim = dpg.generate_uuid()
    bode_phase_data = dpg.generate_uuid()
    bode_phase_sim = dpg.generate_uuid()
    exploratory_mu_criterion = dpg.generate_uuid()
    exploratory_mu = dpg.generate_uuid()
    exploratory_mu_highlight = dpg.generate_uuid()
    exploratory_xps = dpg.generate_uuid()
    exploratory_xps_highlight = dpg.generate_uuid()
    valid_cdc = dpg.generate_uuid()
    invalid_cdc = dpg.generate_uuid()
    valid_node = dpg.generate_uuid()
    invalid_node = dpg.generate_uuid()
    # Themes
    # - Plots
    with dpg.theme(tag=plot_theme):
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(
                dpg.mvPlotCol_FrameBg,
                (
                    255,
                    255,
                    255,
                    0,
                ),
                category=dpg.mvThemeCat_Plots,
            )
    definitions: List[Tuple[int, Color, int]] = [
        (
            real_error,
            CONFIG.colors["real_error"],
            CONFIG.markers["real_error"],
        ),
        (
            imag_error,
            CONFIG.colors["imag_error"],
            CONFIG.markers["imag_error"],
        ),
        (
            nyquist_data,
            CONFIG.colors["nyquist_data"],
            CONFIG.markers["nyquist_data"],
        ),
        (
            nyquist_sim,
            CONFIG.colors["nyquist_sim"],
            CONFIG.markers["nyquist_sim"],
        ),
        (
            bode_magnitude_data,
            CONFIG.colors["bode_magnitude_data"],
            CONFIG.markers["bode_magnitude_data"],
        ),
        (
            bode_magnitude_sim,
            CONFIG.colors["bode_magnitude_sim"],
            CONFIG.markers["bode_magnitude_sim"],
        ),
        (
            bode_phase_data,
            CONFIG.colors["bode_phase_data"],
            CONFIG.markers["bode_phase_data"],
        ),
        (
            bode_phase_sim,
            CONFIG.colors["bode_phase_sim"],
            CONFIG.markers["bode_phase_sim"],
        ),
        (
            exploratory_mu_criterion,
            CONFIG.colors["exploratory_mu_criterion"],
            CONFIG.markers["exploratory_mu"],
        ),
        (
            exploratory_mu,
            CONFIG.colors["exploratory_mu"],
            CONFIG.markers["exploratory_mu"],
        ),
        (
            exploratory_mu_highlight,
            CONFIG.colors["exploratory_mu_highlight"],
            CONFIG.markers["exploratory_mu"],
        ),
        (
            exploratory_xps,
            CONFIG.colors["exploratory_xps"],
            CONFIG.markers["exploratory_xps"],
        ),
        (
            exploratory_xps_highlight,
            CONFIG.colors["exploratory_xps_highlight"],
            CONFIG.markers["exploratory_xps"],
        ),
    ]
    tag: int
    color: Color
    marker: int
    for (tag, color, marker) in definitions:
        create_plot_theme(tag, color, marker)
    # - Circuit editor
    with dpg.theme(tag=valid_cdc):
        with dpg.theme_component(dpg.mvInputText, enabled_state=True):
            dpg.add_theme_color(
                dpg.mvThemeCol_Text,
                (
                    255,
                    255,
                    255,
                ),
            )
        with dpg.theme_component(dpg.mvInputText, enabled_state=False):
            dpg.add_theme_color(
                dpg.mvThemeCol_Text,
                (
                    255,
                    255,
                    255,
                ),
            )
    with dpg.theme(tag=invalid_cdc):
        with dpg.theme_component(dpg.mvInputText, enabled_state=True):
            dpg.add_theme_color(
                dpg.mvThemeCol_Text,
                (
                    255,
                    0,
                    0,
                ),
            )
        with dpg.theme_component(dpg.mvInputText, enabled_state=False):
            dpg.add_theme_color(
                dpg.mvThemeCol_Text,
                (
                    255,
                    0,
                    0,
                ),
            )
    with dpg.theme(tag=valid_node):
        with dpg.theme_component(dpg.mvNode):
            dpg.add_theme_color(
                dpg.mvNodeCol_NodeBackground,
                (
                    255,
                    255,
                    255,
                ),
            )
    with dpg.theme(tag=invalid_node):
        with dpg.theme_component(dpg.mvNode):
            dpg.add_theme_color(
                dpg.mvNodeCol_NodeBackground,
                (
                    255,
                    0,
                    0,
                ),
            )
    # - Global theme
    greyed_out: Tuple[int, int, int] = (
        100,
        100,
        100,
    )
    rounding: int = 2
    global_theme: int
    with dpg.theme() as global_theme:
        # Enabled
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_style(
                dpg.mvStyleVar_WindowRounding, rounding, category=dpg.mvThemeCat_Core
            )
            dpg.add_theme_style(
                dpg.mvStyleVar_ChildRounding, rounding, category=dpg.mvThemeCat_Core
            )
            dpg.add_theme_style(
                dpg.mvStyleVar_FrameRounding, rounding, category=dpg.mvThemeCat_Core
            )
            dpg.add_theme_style(
                dpg.mvStyleVar_PopupRounding, rounding, category=dpg.mvThemeCat_Core
            )
            dpg.add_theme_style(
                dpg.mvStyleVar_ScrollbarRounding, rounding, category=dpg.mvThemeCat_Core
            )
            dpg.add_theme_style(
                dpg.mvStyleVar_GrabRounding, rounding, category=dpg.mvThemeCat_Core
            )
            dpg.add_theme_style(
                dpg.mvStyleVar_TabRounding, rounding, category=dpg.mvThemeCat_Core
            )

            # Plots
            dpg.add_theme_style(
                dpg.mvPlotStyleVar_PlotPadding, 8, 8, category=dpg.mvThemeCat_Plots
            )
            dpg.add_theme_style(
                dpg.mvPlotStyleVar_LabelPadding, 5, 2, category=dpg.mvThemeCat_Plots
            )
            dpg.add_theme_style(
                dpg.mvPlotStyleVar_LegendPadding, 5, 5, category=dpg.mvThemeCat_Plots
            )
            dpg.add_theme_style(
                dpg.mvPlotStyleVar_LegendInnerPadding,
                4,
                4,
                category=dpg.mvThemeCat_Plots,
            )
            dpg.add_theme_style(
                dpg.mvPlotStyleVar_MousePosPadding, 8, 8, category=dpg.mvThemeCat_Plots
            )
            dpg.add_theme_style(
                dpg.mvPlotStyleVar_LineWeight, 1.5, category=dpg.mvThemeCat_Plots
            )
            dpg.add_theme_style(
                dpg.mvPlotStyleVar_MarkerSize, 4.5, category=dpg.mvThemeCat_Plots
            )
            dpg.add_theme_style(
                dpg.mvPlotStyleVar_MarkerWeight, 2.0, category=dpg.mvThemeCat_Plots
            )

            # Nodes
            dpg.add_theme_color(
                dpg.mvNodeCol_GridLine,
                (255, 255, 255, 15),
                category=dpg.mvThemeCat_Nodes,
            )

        # Disabled
        with dpg.theme_component(dpg.mvText, enabled_state=False):
            dpg.add_theme_color(dpg.mvThemeCol_Text, greyed_out)

        with dpg.theme_component(dpg.mvSliderFloat, enabled_state=False):
            dpg.add_theme_color(dpg.mvThemeCol_Text, greyed_out)
            dpg.add_theme_color(dpg.mvThemeCol_SliderGrab, greyed_out)

        with dpg.theme_component(dpg.mvCombo, enabled_state=False):
            dpg.add_theme_color(dpg.mvThemeCol_Text, greyed_out)

        with dpg.theme_component(dpg.mvCheckbox, enabled_state=False):
            dpg.add_theme_color(dpg.mvThemeCol_Text, greyed_out)
            dpg.add_theme_color(dpg.mvThemeCol_CheckMark, greyed_out)

        with dpg.theme_component(dpg.mvInputFloat, enabled_state=False):
            dpg.add_theme_color(dpg.mvThemeCol_Text, greyed_out)
            dpg.add_theme_color(dpg.mvThemeCol_Button, greyed_out)

        with dpg.theme_component(dpg.mvInputInt, enabled_state=False):
            dpg.add_theme_color(dpg.mvThemeCol_Text, greyed_out)
            dpg.add_theme_color(dpg.mvThemeCol_Button, greyed_out)

        with dpg.theme_component(dpg.mvInputText, enabled_state=False):
            dpg.add_theme_color(dpg.mvThemeCol_Text, greyed_out)
            dpg.add_theme_color(dpg.mvThemeCol_Button, greyed_out)

        with dpg.theme_component(dpg.mvButton, enabled_state=False):
            dpg.add_theme_color(dpg.mvThemeCol_Text, greyed_out)

    dpg.bind_theme(global_theme)
    # dpg.show_style_editor()
