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

from typing import Union
import dearpygui.dearpygui as dpg
from deareis.signals import Signal
import deareis.signals as signals
from deareis.utility import calculate_window_position_dimensions
from .bode import Bode, BodeMagnitude, BodePhase
from .nyquist import Nyquist
from .mu_xps import MuXps
from .residuals import Residuals
from .base import Plot


def show_modal_plot_window(original: Plot, adjust_limits: bool = True):
    assert hasattr(original, "duplicate"), type(original)
    labels: dict = {
        Bode: "Bode",
        BodeMagnitude: "Bode - magnitude",
        BodePhase: "Bode - phase",
        Nyquist: "Nyquist",
        Residuals: "Residuals",
    }
    x: int
    y: int
    w: int
    h: int
    x, y, w, h = calculate_window_position_dimensions()
    window: int = dpg.generate_uuid()
    key_handler = dpg.generate_uuid()

    def close():
        dpg.delete_item(window)
        dpg.delete_item(key_handler)
        signals.emit(Signal.UNBLOCK_KEYBINDINGS)

    with dpg.window(
        label=labels.get(type(original), "Unknown plot type"),
        modal=True,
        pos=(
            x,
            y,
        ),
        width=w,
        height=h,
        on_close=close,
        tag=window,
    ):
        copy: Plot = type(original).duplicate(original)
        if adjust_limits:
            copy.queue_limits_adjustment()
        else:
            copy.copy_limits(original)
    with dpg.handler_registry(tag=key_handler):
        dpg.add_key_release_handler(key=dpg.mvKey_Escape, callback=close)
    signals.emit(Signal.BLOCK_KEYBINDINGS, window=window)
