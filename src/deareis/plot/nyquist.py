# Copyright 2022 DearEIS developers
# DearEIS is licensed under the GPLv3 or later (https://www.gnu.org/licenses/gpl-3.0.html).
# The licenses of DearEIS' dependencies and/or sources of portions of code are included in
# the LICENSES folder.

import dearpygui.dearpygui as dpg
from numpy import ndarray
from typing import Dict, Optional, Set, Tuple
from deareis.plot.shared import Plot, line, scatter, modal_window
import deareis.themes as themes
from deareis.utility import dict_to_csv
from dataclasses import dataclass


@dataclass
class NyquistSettings:
    show_legend: bool
    outside_legend: bool
    horizontal_legend: bool
    legend_location: int
    data_theme: int
    sim_fit_theme: int


class NyquistPlot(Plot):
    def __init__(self, plot: int):
        assert type(plot) is int and plot >= 0
        super().__init__(plot)
        self.x_axis: int
        self.y_axis: int
        self.x_axis, self.y_axis = self._setup_plot(self.plot)
        self.data_real: Optional[ndarray] = None
        self.data_imag: Optional[ndarray] = None
        self.sim_real: Optional[ndarray] = None
        self.sim_imag: Optional[ndarray] = None
        self.smooth_real: Optional[ndarray] = None
        self.smooth_imag: Optional[ndarray] = None
        self.is_simulation: bool = False

    def _setup_plot(self, plot: int) -> Tuple[int, int]:
        assert type(plot) is int and plot >= 0
        dpg.add_plot_legend(
            outside=False,
            horizontal=True,
            location=dpg.mvPlot_Location_North,
            parent=plot,
        )
        x_axis: int = dpg.add_plot_axis(dpg.mvXAxis, label="Z' (ohm)", parent=plot)
        y_axis: int = dpg.add_plot_axis(dpg.mvYAxis, label='-Z" (ohm)', parent=plot)
        dpg.configure_item(plot, crosshairs=True)
        return (
            x_axis,
            y_axis,
        )

    def clear_plot(self):
        self.data_real, self.data_imag = None, None
        self.sim_real, self.sim_imag = None, None
        self.smooth_real, self.smooth_imag = None, None
        dpg.delete_item(self.y_axis, children_only=True)

    def _plot(
        self,
        real: ndarray,
        imag: ndarray,
        label: Optional[str],
        plot_line: bool,
        plot_scatter: bool,
        theme: int,
        before: int,
        x_axis: int,
        y_axis: int,
    ) -> int:
        assert type(real) is ndarray or real is None
        assert type(imag) is ndarray or imag is None
        assert type(label) is str or label is None
        assert type(plot_line) is bool
        assert type(plot_scatter) is bool
        assert type(theme) is int and theme >= 0
        assert type(before) is int
        assert type(x_axis) is int
        assert type(y_axis) is int
        if plot_line and plot_scatter:
            scatter(real, imag, label, y_axis, theme, before)
            return line(real, imag, None, y_axis, theme, before)
        elif plot_line:
            return line(real, imag, label, y_axis, theme, before)
        elif plot_scatter:
            return scatter(real, imag, label, y_axis, theme, before)
        raise Exception("Invalid plot settings!")

    def adjust_limits(self, x_axis: int = -1, y_axis: int = -1):
        assert type(x_axis) is int
        assert type(y_axis) is int
        if x_axis == -1:
            x_axis, y_axis = self.x_axis, self.y_axis
        dpg.fit_axis_data(x_axis)
        dpg.fit_axis_data(y_axis)

    def plot_data(
        self,
        real: ndarray,
        imag: ndarray,
        before: int,
        no_line: bool = False,
        x_axis: int = -1,
        y_axis: int = -1,
    ):
        assert type(real) is ndarray or real is None
        assert type(imag) is ndarray or imag is None
        assert type(before) is int
        assert type(no_line) is bool
        assert type(x_axis) is int
        assert type(y_axis) is int
        if x_axis == -1:
            self.data_real, self.data_imag = real, imag
            x_axis, y_axis = self.x_axis, self.y_axis
        scatter_only: bool = (
            True
            if no_line
            else (self.sim_real is not None or self.smooth_real is not None)
        )
        label: str = "Data"
        self._plot(
            real,
            imag,
            label,
            not scatter_only,
            True,
            themes.nyquist_data,
            before,
            x_axis,
            y_axis,
        )

    def plot_sim(
        self,
        real: ndarray,
        imag: ndarray,
        is_simulation: bool,
        before: int,
        x_axis: int = -1,
        y_axis: int = -1,
    ) -> int:
        assert type(real) is ndarray
        assert type(imag) is ndarray
        assert type(is_simulation) is bool
        assert type(before) is int
        assert type(x_axis) is int
        assert type(y_axis) is int
        if x_axis == -1:
            self.sim_real, self.sim_imag, self.is_simulation = real, imag, is_simulation
            x_axis, y_axis = self.x_axis, self.y_axis
        scatter_only: bool = self.smooth_real is not None
        label: Optional[str] = None
        if not scatter_only:
            label = "Sim." if is_simulation else "Fit"
        return self._plot(
            real,
            imag,
            label,
            not scatter_only,
            True,
            themes.nyquist_sim,
            before,
            x_axis,
            y_axis,
        )

    def plot_smooth(
        self,
        real: ndarray,
        imag: ndarray,
        is_simulation: bool,
        x_axis: int = -1,
        y_axis: int = -1,
    ) -> int:
        assert type(real) is ndarray
        assert type(imag) is ndarray
        assert type(is_simulation) is bool
        assert type(x_axis) is int
        assert type(y_axis) is int
        if x_axis == -1:
            self.smooth_real, self.smooth_imag, self.is_simulation = (
                real,
                imag,
                is_simulation,
            )
            x_axis, y_axis = self.x_axis, self.y_axis
        label: str = "Sim." if is_simulation else "Fit"
        return self._plot(
            real, imag, label, True, False, themes.nyquist_sim, -1, x_axis, y_axis
        )

    def show_modal_window(self, no_data_line: bool = True) -> int:
        if (
            self.data_real is None
            and self.sim_real is None
            and self.smooth_real is None
        ):
            return -1
        parent: int = modal_window("Nyquist")
        plot: int = dpg.add_plot(
            width=-1,
            height=-1,
            anti_aliased=True,
            equal_aspects=True,
            parent=parent,
        )
        dpg.bind_item_theme(plot, themes.plot_theme)
        x_axis: int
        y_axis: int
        x_axis, y_axis = self._setup_plot(plot)
        before: int = -1
        if self.smooth_real is not None:
            assert self.smooth_imag is not None
            before = self.plot_smooth(
                self.smooth_real, self.smooth_imag, self.is_simulation, x_axis, y_axis
            )
        if self.sim_real is not None:
            assert self.sim_imag is not None
            before = self.plot_sim(
                self.sim_real, self.sim_imag, self.is_simulation, before, x_axis, y_axis
            )
        assert self.data_real is not None
        assert self.data_imag is not None
        self.plot_data(
            self.data_real,
            self.data_imag,
            before,
            no_data_line if before < 0 else True,
            x_axis,
            y_axis,
        )
        self.adjust_limits(x_axis, y_axis)
        self._setup_keybindings(plot)
        return parent

    def copy_data(self):
        if (
            self.data_real is None
            and self.sim_real is None
            and self.smooth_real is None
        ):
            return
        dictionary: Dict[str, list] = {}
        if self.data_real is not None:
            dictionary["Zre_exp (ohm)"] = list(self.data_real)
            dictionary["-Zim_exp (ohm)"] = list(self.data_imag)
        suffix: str = "sim" if self.is_simulation else "fit"
        if self.sim_real is not None and self.smooth_real is not None:
            dictionary[f"Zre_{suffix} (ohm) - scatter"] = list(self.sim_real)
            dictionary[f"-Zim_{suffix} (ohm) - scatter"] = list(self.sim_imag)
            dictionary[f"Zre_{suffix} (ohm) - line"] = list(self.smooth_real)
            dictionary[f"-Zim_{suffix} (ohm) - line"] = list(self.smooth_imag)
        else:
            if self.sim_real is not None:
                dictionary[f"Zre_{suffix} (ohm)"] = list(self.sim_real)
                dictionary[f"-Zim_{suffix} (ohm)"] = list(self.sim_imag)
            elif self.smooth_real is not None:
                dictionary[f"Zre_{suffix} (ohm)"] = list(self.smooth_real)
                dictionary[f"-Zim_{suffix} (ohm)"] = list(self.smooth_imag)
        num_rows: Set[int] = set(map(len, dictionary.values()))
        if len(num_rows) > 1:
            max_length: int = max(num_rows)
            values: list
            for values in dictionary.values():
                if len(values) == max_length:
                    continue
                values.extend([""] * (max_length - len(values)))
        dpg.set_clipboard_text(dict_to_csv(dictionary))
