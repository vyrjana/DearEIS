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

import dearpygui.dearpygui as dpg
from deareis.signals import Signal
import deareis.signals as signals
from deareis.utility import calculate_window_position_dimensions
from .base import Plot
from .bode import (
    Bode,
    BodeMagnitude,
    BodePhase,
)
from .image import Image
from .pseudo_chisqr import PseudoChisqrAndScore
from .kramers_kronig_methods import (
    Method1,
    Method2,
    Method3,
    Method4,
    Method5,
    Method6,
)
from .nyquist import Nyquist
from .residuals import Residuals
from .drt import DRT
from .impedance import (
    Impedance,
    ImpedanceReal,
    ImpedanceImaginary,
)
from .log_F_ext import (
    LogFextStatistic,
    PseudoChisqr,
)
from deareis.typing.helpers import Tag


class ModalPlotWindow:
    def __init__(
        self,
        original: Plot,
        adjust_limits: bool,
        admittance: bool,
        frequency: bool,
    ):
        labels: dict = {
            Bode: "Bode",
            BodeMagnitude: "Bode - magnitude",
            BodePhase: "Bode - phase",
            Nyquist: "Nyquist",
            Residuals: "Residuals",
            DRT: "Distribution of relaxation times",
            Impedance: "Real and imaginary impedance",
            ImpedanceImaginary: "Imaginary impedance",
            ImpedanceReal: "Real impedance",
        }

        x: int
        y: int
        w: int
        h: int
        x, y, w, h = calculate_window_position_dimensions()

        self.window: Tag = dpg.generate_uuid()
        self.key_handler: Tag = dpg.generate_uuid()
        
        with dpg.window(
            label=labels.get(type(original), "Unknown plot type"),
            modal=True,
            pos=(x, y),
            width=w,
            height=h,
            on_close=self.close,
            tag=self.window,
        ):
            copy: Plot = type(original).duplicate(original)
            if adjust_limits:
                copy.queue_limits_adjustment()
            else:
                copy.copy_limits(original)

        if hasattr(copy, "set_admittance") and callable(copy.set_admittance):
            copy.set_admittance(admittance, adjust_limits=False)

        if hasattr(copy, "set_frequency") and callable(copy.set_frequency):
            copy.set_frequency(frequency, adjust_limits=False)

        with dpg.handler_registry(tag=self.key_handler):
            dpg.add_key_release_handler(key=dpg.mvKey_Escape, callback=self.close)

    def close(self):
        dpg.delete_item(self.key_handler)
        dpg.delete_item(self.window)
        signals.emit(Signal.UNBLOCK_KEYBINDINGS)


def show_modal_plot_window(
    original: Plot,
    adjust_limits: bool = True,
    admittance: bool = False,
    frequency: bool = False,
):
    assert hasattr(original, "duplicate"), type(original)
    assert callable(original.duplicate), type(original)
    assert isinstance(adjust_limits, bool), adjust_limits
    assert isinstance(admittance, bool), admittance
    assert isinstance(frequency, bool), frequency

    modal_window: ModalPlotWindow = ModalPlotWindow(
        original,
        adjust_limits=adjust_limits,
        admittance=admittance,
        frequency=frequency,
    )

    signals.emit(
        Signal.BLOCK_KEYBINDINGS,
        window=modal_window.window,
        window_object=modal_window,
    )
