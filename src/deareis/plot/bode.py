# Copyright 2022 DearEIS developers
# DearEIS is licensed under the GPLv3 or later (https://www.gnu.org/licenses/gpl-3.0.html).
# The licenses of DearEIS' dependencies and/or sources of portions of code are included in
# the LICENSES folder.

from math import ceil, floor
from threading import Timer
from typing import Dict, List, Optional, Set, Tuple
from numpy import ndarray
import deareis.themes as themes
import dearpygui.dearpygui as dpg
from deareis.plot.shared import Plot, line, scatter, auto_limits, modal_window
from deareis.utility import dict_to_csv
from dataclasses import dataclass


@dataclass
class BodeSettings:
    show_legend: bool
    outside_legend: bool
    horizontal_legend: bool
    legend_location: int
    data_mag_theme: int
    data_phase_theme: int
    sim_fit_mag_theme: int
    sim_fit_phase_theme: int


class BodePlot(Plot):
    def __init__(self, plot: int):
        assert type(plot) is int and plot >= 0
        super().__init__(plot)
        self.x_axis: int
        self.y_axis_1: int
        self.y_axis_2: int
        self.x_axis, self.y_axis_1, self.y_axis_2 = self._setup_plot(self.plot)
        self.data_freq: Optional[ndarray] = None
        self.data_mag: Optional[ndarray] = None
        self.data_phase: Optional[ndarray] = None
        self.sim_freq: Optional[ndarray] = None
        self.sim_mag: Optional[ndarray] = None
        self.sim_phase: Optional[ndarray] = None
        self.smooth_freq: Optional[ndarray] = None
        self.smooth_mag: Optional[ndarray] = None
        self.smooth_phase: Optional[ndarray] = None
        self.is_simulation: bool = False

    def _setup_plot(self, plot: int) -> Tuple[int, int, int]:
        assert type(plot) is int and plot >= 0
        dpg.add_plot_legend(
            outside=False,
            horizontal=True,
            location=dpg.mvPlot_Location_North,
            parent=plot,
        )
        x_axis: int = dpg.add_plot_axis(dpg.mvXAxis, label="log f", parent=plot)
        y_axis_1: int = dpg.add_plot_axis(dpg.mvYAxis, label="log |Z|", parent=plot)
        y_axis_2: int = dpg.add_plot_axis(dpg.mvYAxis, label="-phi (deg.)", parent=plot)
        dpg.configure_item(plot, crosshairs=True)
        return (
            x_axis,
            y_axis_1,
            y_axis_2,
        )

    def clear_plot(self):
        self.data_freq, self.data_mag, self.data_phase = None, None, None
        self.sim_freq, self.sim_mag, self.sim_phase = None, None, None
        self.smooth_freq, self.smooth_mag, self.smooth_phase = None, None, None
        dpg.delete_item(self.y_axis_1, children_only=True)
        dpg.delete_item(self.y_axis_2, children_only=True)

    def _plot(
        self,
        freq: ndarray,
        mag: ndarray,
        phase: ndarray,
        label_1: Optional[str],
        label_2: Optional[str],
        plot_line: bool,
        plot_scatter: bool,
        themes: Tuple[int, int],
        before: Tuple[int, int],
        x_axis: int,
        y_axis_1: int,
        y_axis_2: int,
    ) -> Tuple[int, int]:
        assert type(freq) is ndarray or freq is None
        assert type(mag) is ndarray or mag is None
        assert type(phase) is ndarray or phase is None
        assert type(label_1) is str or label_1 is None
        assert type(label_2) is str or label_2 is None
        assert type(plot_line) is bool
        assert type(plot_scatter) is bool
        assert type(themes) is tuple and all(
            map(lambda _: type(_) is int and _ >= 0, themes)
        )
        assert type(before) is tuple and all(map(lambda _: type(_) is int, before))
        assert type(x_axis) is int
        assert type(y_axis_1) is int
        assert type(y_axis_2) is int
        theme_1: int
        theme_2: int
        theme_1, theme_2 = themes
        before_1: int
        before_2: int
        before_1, before_2 = before
        tags: List[int] = []
        if plot_line and plot_scatter:
            tags.append(line(freq, mag, label_1, y_axis_1, theme_1, before_1))
            scatter(freq, mag, None, y_axis_1, theme_1, before_1)
            tags.append(line(freq, phase, label_2, y_axis_2, theme_2, before_2))
            scatter(freq, phase, None, y_axis_2, theme_2, before_2)
        elif plot_line:
            tags.append(line(freq, mag, label_1, y_axis_1, theme_1, before_1))
            tags.append(line(freq, phase, label_2, y_axis_2, theme_2, before_2))
        elif plot_scatter:
            tags.append(scatter(freq, mag, label_1, y_axis_1, theme_1, before_1))
            tags.append(scatter(freq, phase, label_2, y_axis_2, theme_2, before_2))
        else:
            raise Exception("Invalid plot settings!")
        assert len(tags) == 2
        return tuple(tags)  # type: ignore

    def adjust_limits(self, x_axis: int = -1, y_axis_1: int = -1, y_axis_2: int = -1):
        assert type(x_axis) is int
        assert type(y_axis_1) is int
        assert type(y_axis_2) is int
        if x_axis == -1:
            x_axis, y_axis_1, y_axis_2 = self.x_axis, self.y_axis_1, self.y_axis_2
        freqs: List[ndarray] = []
        mags: List[ndarray] = []
        phases: List[ndarray] = []
        if self.data_freq is not None and self.data_freq.any():
            assert self.data_mag is not None
            assert self.data_phase is not None
            freqs.append(self.data_freq)
            mags.append(self.data_mag)
            phases.append(self.data_phase)
        if self.sim_freq is not None and self.sim_freq.any():
            assert self.sim_mag is not None
            assert self.sim_phase is not None
            freqs.append(self.sim_freq)
            mags.append(self.sim_mag)
            phases.append(self.sim_phase)
        if self.smooth_freq is not None and self.smooth_freq.any():
            assert self.smooth_mag is not None
            assert self.smooth_phase is not None
            freqs.append(self.smooth_freq)
            mags.append(self.smooth_mag)
            phases.append(self.smooth_phase)
        if not freqs:
            dpg.set_axis_limits(x_axis, ymin=-1, ymax=1)
            dpg.set_axis_limits(y_axis_1, ymin=-1, ymax=1)
            dpg.set_axis_limits(y_axis_2, ymin=-1, ymax=1)
        else:
            freq_min: float = round(min(map(min, freqs)), 1) - 0.1
            freq_max: float = round(max(map(max, freqs)), 1) + 0.1
            mag_min: float = round(min(map(min, mags)), 1) - 0.1
            mag_max: float = round(max(map(max, mags)), 1) + 0.1
            n: int = 5
            phase_min: float = floor(min(map(min, phases)) / n) * n - n
            phase_max: float = ceil(max(map(max, phases)) / n) * n + n
            dpg.set_axis_limits(x_axis, ymin=freq_min, ymax=freq_max)
            dpg.set_axis_limits(y_axis_1, ymin=mag_min, ymax=mag_max)
            dpg.set_axis_limits(y_axis_2, ymin=phase_min, ymax=phase_max)
        t: Timer = Timer(0.5, lambda: auto_limits([x_axis, y_axis_1, y_axis_2]))
        t.start()

    def plot_data(
        self,
        freq: ndarray,
        mag: ndarray,
        phase: ndarray,
        before: Tuple[int, int],
        no_line: bool = False,
        x_axis: int = -1,
        y_axis_1: int = -1,
        y_axis_2: int = -1,
    ):
        assert type(freq) is ndarray or freq is None
        assert type(mag) is ndarray or mag is None
        assert type(phase) is ndarray or phase is None
        assert type(before) is tuple and all(map(lambda _: type(_) is int, before))
        assert type(no_line) is bool
        assert type(x_axis) is int
        assert type(y_axis_1) is int
        assert type(y_axis_2) is int
        if x_axis == -1:
            self.data_freq, self.data_mag, self.data_phase = freq, mag, phase
            x_axis, y_axis_1, y_axis_2 = self.x_axis, self.y_axis_1, self.y_axis_2
        scatter_only: bool = (
            True
            if no_line
            else (self.sim_freq is not None or self.smooth_freq is not None)
        )
        label_1: str = "|Z|"
        label_2: str = "phi"
        if before != (
            -1,
            -1,
        ):
            label_1 += " (d)"
            label_2 += " (d)"
        self._plot(
            freq,
            mag,
            phase,
            label_1,
            label_2,
            not scatter_only,
            True,
            (
                themes.bode_magnitude_data,
                themes.bode_phase_data,
            ),
            before,
            x_axis,
            y_axis_1,
            y_axis_2,
        )

    def plot_sim(
        self,
        freq: ndarray,
        mag: ndarray,
        phase: ndarray,
        is_simulation: bool,
        before: Tuple[int, int],
        x_axis: int = -1,
        y_axis_1: int = -1,
        y_axis_2: int = -1,
    ) -> Tuple[int, int]:
        assert type(freq) is ndarray
        assert type(mag) is ndarray
        assert type(phase) is ndarray
        assert type(is_simulation) is bool
        assert type(before) is tuple and all(map(lambda _: type(_) is int, before))
        assert type(x_axis) is int
        assert type(y_axis_1) is int
        assert type(y_axis_2) is int
        if x_axis == -1:
            self.sim_freq, self.sim_mag, self.sim_phase = freq, mag, phase
            self.is_simulation = is_simulation
            x_axis, y_axis_1, y_axis_2 = self.x_axis, self.y_axis_1, self.y_axis_2
        scatter_only: bool = self.smooth_freq is not None
        label_1: Optional[str] = None
        label_2: Optional[str] = None
        if not scatter_only:
            suffix: str = " (s)" if is_simulation else " (f)"
            label_1 = "log |Z|" + suffix
            label_2 = "phi" + suffix
        return self._plot(
            freq,
            mag,
            phase,
            label_1,
            label_2,
            not scatter_only,
            True,
            (
                themes.bode_magnitude_sim,
                themes.bode_phase_sim,
            ),
            before,
            x_axis,
            y_axis_1,
            y_axis_2,
        )

    def plot_smooth(
        self,
        freq: ndarray,
        mag: ndarray,
        phase: ndarray,
        is_simulation: bool,
        x_axis: int = -1,
        y_axis_1: int = -1,
        y_axis_2: int = -1,
    ) -> Tuple[int, int]:
        assert type(freq) is ndarray
        assert type(mag) is ndarray
        assert type(phase) is ndarray
        assert type(is_simulation) is bool
        assert type(x_axis) is int
        assert type(y_axis_1) is int
        assert type(y_axis_2) is int
        if x_axis == -1:
            self.smooth_freq, self.smooth_mag, self.smooth_phase = freq, mag, phase
            self.is_simulation = is_simulation
            x_axis, y_axis_1, y_axis_2 = self.x_axis, self.y_axis_1, self.y_axis_2
        suffix: str = "(s)" if is_simulation else "(f)"
        label_1: str = "|Z| " + suffix
        label_2: str = "phi " + suffix
        return self._plot(
            freq,
            mag,
            phase,
            label_1,
            label_2,
            True,
            False,
            (
                themes.bode_magnitude_sim,
                themes.bode_phase_sim,
            ),
            (
                -1,
                -1,
            ),
            x_axis,
            y_axis_1,
            y_axis_2,
        )

    def show_modal_window(self, no_data_line: bool = True) -> int:
        if (
            self.data_freq is None
            and self.sim_freq is None
            and self.smooth_freq is None
        ):
            return -1
        parent: int = modal_window("Bode")
        plot: int = dpg.add_plot(width=-1, height=-1, anti_aliased=True, parent=parent)
        dpg.bind_item_theme(plot, themes.plot_theme)
        x_axis: int
        y_axis_1: int
        y_axis_2: int
        x_axis, y_axis_1, y_axis_2 = self._setup_plot(plot)
        before: Tuple[int, int] = (
            -1,
            -1,
        )
        if self.smooth_freq is not None:
            assert self.smooth_mag is not None
            assert self.smooth_phase is not None
            before = self.plot_smooth(
                self.smooth_freq,
                self.smooth_mag,
                self.smooth_phase,
                self.is_simulation,
                x_axis,
                y_axis_1,
                y_axis_2,
            )
        if self.sim_freq is not None:
            assert self.sim_mag is not None
            assert self.sim_phase is not None
            before = self.plot_sim(
                self.sim_freq,
                self.sim_mag,
                self.sim_phase,
                self.is_simulation,
                before,
                x_axis,
                y_axis_1,
                y_axis_2,
            )
        assert self.data_freq is not None
        assert self.data_mag is not None
        assert self.data_phase is not None
        self.plot_data(
            self.data_freq,
            self.data_mag,
            self.data_phase,
            before,
            no_data_line if -1 in before else False,
            x_axis,
            y_axis_1,
            y_axis_2,
        )
        self.adjust_limits(x_axis, y_axis_1, y_axis_2)
        self._setup_keybindings(plot)
        return parent

    def copy_data(self):
        if (
            self.data_freq is None
            and self.sim_freq is None
            and self.smooth_freq is None
        ):
            return
        dictionary: Dict[str, list] = {}
        if self.data_freq is not None:
            dictionary["log f_exp"] = list(self.data_freq)
            dictionary["log |Z_exp|"] = list(self.data_mag)
            dictionary["-phase_exp (deg.)"] = list(self.data_phase)
        suffix: str = "sim" if self.is_simulation else "fit"
        if self.sim_freq is not None and self.smooth_freq is not None:
            dictionary[f"log f_{suffix} - scatter"] = list(self.sim_freq)
            dictionary[f"log |Z_{suffix}| - scatter"] = list(self.sim_mag)
            dictionary[f"-phase_{suffix} (deg.) - scatter"] = list(self.sim_phase)
            dictionary[f"log f_{suffix} - line"] = list(self.smooth_freq)
            dictionary[f"log |Z_{suffix}| - line"] = list(self.smooth_mag)
            dictionary[f"-phase_{suffix} (deg.) - line"] = list(self.smooth_phase)
        else:
            if self.sim_freq is not None:
                dictionary[f"log f_{suffix}"] = list(self.sim_freq)
                dictionary[f"log |Z_{suffix}|"] = list(self.sim_mag)
                dictionary[f"-phase_{suffix} (deg.)"] = list(self.sim_phase)
            elif self.smooth_freq is not None:
                dictionary[f"log f_{suffix}"] = list(self.smooth_freq)
                dictionary[f"log |Z_{suffix}|"] = list(self.smooth_mag)
                dictionary[f"-phase_{suffix} (deg.)"] = list(self.smooth_phase)
        num_rows: Set[int] = set(map(len, dictionary.values()))
        if len(num_rows) > 1:
            max_length: int = max(num_rows)
            values: list
            for values in dictionary.values():
                if len(values) == max_length:
                    continue
                values.extend([""] * (max_length - len(values)))
        dpg.set_clipboard_text(dict_to_csv(dictionary))
