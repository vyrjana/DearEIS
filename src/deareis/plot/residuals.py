# Copyright 2022 DearEIS developers
# DearEIS is licensed under the GPLv3 or later (https://www.gnu.org/licenses/gpl-3.0.html).
# The licenses of DearEIS' dependencies and/or sources of portions of code are included in
# the LICENSES folder.

import dearpygui.dearpygui as dpg
from numpy import ndarray
from typing import Optional, Tuple
from math import ceil
from threading import Timer
from deareis.plot.shared import Plot, line, scatter, auto_limits, modal_window
import deareis.themes as themes
from deareis.utility import dict_to_csv
from dataclasses import dataclass


@dataclass
class ResidualsSettings:
    show_legend: bool
    outside_legend: bool
    horizontal_legend: bool
    legend_location: int
    real_theme: int
    imag_theme: int


class ResidualsPlot(Plot):
    def __init__(self, plot: int):
        assert type(plot) is int
        self.plot: int = plot
        dpg.bind_item_theme(self.plot, themes.plot_theme)
        self.x_axis: int
        self.y_axis_1: int
        self.y_axis_2: int
        self.x_axis, self.y_axis_1, self.y_axis_2 = self._setup_plot(self.plot)
        self.freq: Optional[ndarray] = None
        self.real: Optional[ndarray] = None
        self.imag: Optional[ndarray] = None

    def _setup_plot(self, plot: int) -> Tuple[int, int, int]:
        assert type(plot) is int
        dpg.add_plot_legend(
            outside=False,
            horizontal=True,
            location=dpg.mvPlot_Location_North,
            parent=plot,
        )
        x_axis: int = dpg.add_plot_axis(dpg.mvXAxis, label="log f", parent=plot)
        y_axis_1: int = dpg.add_plot_axis(
            dpg.mvYAxis, label="Z' error (%)", parent=plot
        )
        y_axis_2: int = dpg.add_plot_axis(
            dpg.mvYAxis, label='Z" error (%)', parent=plot
        )
        dpg.configure_item(plot, crosshairs=True)
        return (
            x_axis,
            y_axis_1,
            y_axis_2,
        )

    def clear_plot(self):
        self.freq, self.real, self.imag = None, None, None
        dpg.delete_item(self.y_axis_1, children_only=True)
        dpg.delete_item(self.y_axis_2, children_only=True)

    def adjust_limits(self, x_axis: int = -1, y_axis_1: int = -1, y_axis_2: int = -1):
        assert type(x_axis) is int
        assert type(y_axis_1) is int
        assert type(y_axis_2) is int
        if x_axis == -1:
            x_axis, y_axis_1, y_axis_2 = self.x_axis, self.y_axis_1, self.y_axis_2
        if self.freq is None:
            dpg.set_axis_limits(x_axis, ymin=-1, ymax=1)
            dpg.set_axis_limits(y_axis_1, ymin=-1, ymax=1)
            dpg.set_axis_limits(y_axis_2, ymin=-1, ymax=1)
        else:
            error_lim: float = max(  # type: ignore
                map(
                    abs,
                    [
                        min(self.real),  # type: ignore
                        max(self.real),  # type: ignore
                        min(self.imag),  # type: ignore
                        max(self.imag),  # type: ignore
                    ],
                )
            )
            if error_lim <= 0.5:
                error_lim = 0.5
            elif error_lim <= 5:
                error_lim = ceil(error_lim)
            else:
                error_lim = ceil(error_lim / 5.0) * 5
            dpg.set_axis_limits(
                x_axis, ymin=min(self.freq) - 0.1, ymax=max(self.freq) + 0.1
            )
            dpg.set_axis_limits(y_axis_1, ymin=-error_lim, ymax=error_lim)
            dpg.set_axis_limits(y_axis_2, ymin=-error_lim, ymax=error_lim)
        t: Timer = Timer(0.5, lambda: auto_limits([y_axis_1, y_axis_2]))
        t.start()

    def plot_data(
        self,
        freq: ndarray,
        real: ndarray,
        imag: ndarray,
        x_axis: int = -1,
        y_axis_1: int = -1,
        y_axis_2: int = -1,
    ):
        assert type(freq) is ndarray
        assert type(real) is ndarray
        assert type(imag) is ndarray
        assert type(x_axis) is int
        assert type(y_axis_1) is int
        assert type(y_axis_2) is int
        if x_axis == -1:
            self.freq, self.real, self.imag = freq, real, imag
            x_axis, y_axis_1, y_axis_2 = self.x_axis, self.y_axis_1, self.y_axis_2
        # Real residual
        line(freq, real, "Z'", y_axis_1, themes.real_error)
        scatter(freq, real, None, y_axis_1, themes.real_error)
        # Imaginary residual
        line(freq, imag, 'Z"', y_axis_2, themes.imag_error)
        scatter(freq, imag, None, y_axis_2, themes.imag_error)
        # Update limits
        self.adjust_limits(x_axis, y_axis_1, y_axis_2)

    def show_modal_window(self) -> int:
        if self.freq is None:
            return -1
        parent: int = modal_window("Residuals")
        plot: int = dpg.add_plot(width=-1, height=-1, anti_aliased=True, parent=parent)
        dpg.bind_item_theme(plot, themes.plot_theme)
        x_axis: int
        y_axis_1: int
        y_axis_2: int
        x_axis, y_axis_1, y_axis_2 = self._setup_plot(plot)
        assert self.real is not None
        assert self.imag is not None
        self.plot_data(self.freq, self.real, self.imag, x_axis, y_axis_1, y_axis_2)
        self._setup_keybindings(plot)
        return parent

    def copy_data(self):
        if self.freq is None:
            return
        dpg.set_clipboard_text(
            dict_to_csv(
                {
                    "log f_exp": self.freq,
                    "resid_Zre (%)": self.real,
                    "resid_Zim (%)": self.imag,
                }
            )
        )
