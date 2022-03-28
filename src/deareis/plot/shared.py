# Copyright 2022 DearEIS developers
# DearEIS is licensed under the GPLv3 or later (https://www.gnu.org/licenses/gpl-3.0.html).
# The licenses of DearEIS' dependencies and/or sources of portions of code are included in
# the LICENSES folder.

import dearpygui.dearpygui as dpg
from typing import List, Optional
from deareis.utility import window_pos_dims
import deareis.themes as themes


# TODO: Add resize handler to check when the viewport is resized


def line(
    x,
    y,
    label: Optional[str],
    parent: int,
    theme: int,
    before: int = -1,
) -> int:
    assert type(label) is str or label is None
    assert type(parent) is int and parent > 0
    assert type(before) is int
    if x is None or y is None:
        return -1
    if type(x) is not list:
        x = list(x)
    if type(y) is not list:
        y = list(y)
    line: int
    if before < 0:
        line = dpg.add_line_series(x, y, label=label, parent=parent)
    else:
        line = dpg.add_line_series(x, y, label=label, parent=parent, before=before)
    dpg.bind_item_theme(line, theme)
    return line


def scatter(
    x,
    y,
    label: Optional[str],
    parent: int,
    theme: int,
    before: int = -1,
) -> int:
    assert type(label) is str or label is None
    assert type(parent) is int and parent > 0
    assert type(before) is int
    if x is None or y is None:
        return -1
    if type(x) is not list:
        x = list(x)
    elif type(y) is not list:
        y = list(y)
    scatter: int
    if before < 0:
        scatter = dpg.add_scatter_series(x, y, label=label, parent=parent)
    else:
        scatter = dpg.add_scatter_series(
            x, y, label=label, parent=parent, before=before
        )
    dpg.bind_item_theme(scatter, theme)
    return scatter


def auto_limits(axes: List[int]):
    assert type(axes) is list
    for axis in axes:
        assert type(axis) is int
        if not dpg.does_item_exist(axis):
            return
        dpg.set_axis_limits_auto(axis)


def modal_window(label: str = "") -> int:
    assert type(label) is str
    window: int = dpg.add_window(label=label, modal=True)
    x: int
    y: int
    w: int
    h: int
    x, y, w, h = window_pos_dims()
    dpg.set_item_pos(
        window,
        (
            x,
            y,
        ),
    )
    dpg.configure_item(
        window,
        width=w,
        height=h,
    )
    return window


class Plot:
    def __init__(self, plot: int):
        assert type(plot) is int and plot > 0
        self.plot: int = plot
        dpg.bind_item_theme(self.plot, themes.plot_theme)

    def resize(self, width: int, height: int):
        assert type(width) is int, width
        assert type(height) is int, height
        dpg.configure_item(self.plot, width=width, height=height)

    def _setup_keybindings(self, plot: int):
        assert type(plot) is int and plot > 0
        handler: int = dpg.generate_uuid()
        window: int = dpg.get_item_parent(plot)

        def close_window_callback():
            dpg.hide_item(window)
            dpg.delete_item(handler)

        with dpg.handler_registry(tag=handler):
            dpg.add_key_release_handler(
                key=dpg.mvKey_Escape, callback=close_window_callback
            )
