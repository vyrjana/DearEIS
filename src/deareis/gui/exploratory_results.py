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

from deareis.data.kramers_kronig import TestSettings
from deareis.tooltips import attach_tooltip
from deareis.utility import calculate_window_position_dimensions
from numpy import array, floor, log10 as log, ndarray
from pyimpspec import KramersKronigResult
from typing import Callable, Dict, List, Tuple
import deareis.themes as themes
import deareis.tooltips as tooltips
import dearpygui.dearpygui as dpg
from deareis.signals import Signal
import deareis.signals as signals
from deareis.data import DataSet
import pyimpspec
from deareis.gui.plots import (
    Bode,
    MuXps,
    Nyquist,
    Residuals,
)


class ExploratoryResults:
    def __init__(
        self,
        data: DataSet,
        results: List[KramersKronigResult],
        settings: TestSettings,
        num_RCs: ndarray,
        callback: Callable,
        state,
    ):
        assert type(data) is DataSet
        assert type(results) is list and all(
            map(lambda _: type(_) is KramersKronigResult, results)
        )
        assert type(settings) is TestSettings
        assert type(num_RCs) is ndarray
        self.state = state
        dpg.split_frame(delay=33)
        self.callback: Callable = callback
        self.window: int = dpg.generate_uuid()
        self.result_combo: int = dpg.generate_uuid()
        self.accept_button: int = dpg.generate_uuid()
        self.mu_xps_plot: MuXps = None
        self.residuals_plot: Residuals = None
        self.nyquist_plot: Nyquist = None
        self.bode_plot: Bode = None
        self.key_handler: int = dpg.generate_uuid()
        self._assemble()
        self._setup_keybindings()
        self.data: DataSet = data
        results.sort(key=lambda _: _.num_RC)
        self.results: List[KramersKronigResult] = results
        self.settings: TestSettings = settings
        self.num_RCs: ndarray = num_RCs
        self.mu_crit: float = settings.mu_criterion
        default_result: KramersKronigResult = pyimpspec.score_test_results(
            results, self.mu_crit
        )[0][1]
        default_label: str = ""
        self.label_to_result: Dict[str, KramersKronigResult] = {}
        result: KramersKronigResult
        for result in results:
            label: str = (
                f"{result.num_RC}: µ = {result.mu:.3f}, "
                + f"log X² (ps.) = {log(result.pseudo_chisqr):.3f}"
            )
            if result == default_result:
                label += " *"
                default_label = label
            self.label_to_result[label] = result
        assert default_label != ""
        self.labels: List[str] = list(self.label_to_result.keys())
        self.result_index: int = self.labels.index(default_label)
        dpg.configure_item(
            self.result_combo,
            items=self.labels,
            default_value=default_label,
        )
        self.mu: ndarray = array(list(map(lambda _: _.mu, results)))
        self.Xps: ndarray = log(array(list(map(lambda _: _.pseudo_chisqr, results))))
        self.plot(default_label)
        signals.register(Signal.VIEWPORT_RESIZED, self.resize)

    def _setup_keybindings(self):
        with dpg.handler_registry(tag=self.key_handler):
            dpg.add_key_release_handler(
                key=dpg.mvKey_Escape,
                callback=self.close,
            )
            dpg.add_key_release_handler(
                key=dpg.mvKey_Return,
                callback=lambda: self.accept(
                    dpg.get_item_user_data(self.accept_button)
                ),
            )
            dpg.add_key_release_handler(
                key=dpg.mvKey_Prior,
                callback=lambda: self.plot(
                    self.labels[(self.result_index - 1) % len(self.labels)]
                ),
            )
            dpg.add_key_release_handler(
                key=dpg.mvKey_Next,
                callback=lambda: self.plot(
                    self.labels[(self.result_index + 1) % len(self.labels)]
                ),
            )

    def _assemble(self):
        x: int
        y: int
        w: int
        h: int
        x, y, w, h = calculate_window_position_dimensions()
        with dpg.window(
            label="Exploratory test results",
            modal=True,
            pos=(
                x,
                y,
            ),
            width=w,
            height=h,
            no_resize=True,
            tag=self.window,
            on_close=self.close,
        ):
            with dpg.group(horizontal=True):
                dpg.add_text("Num. RC circuits")
                attach_tooltip(tooltips.kramers_kronig.exploratory_result)
                dpg.add_combo(
                    width=-100,
                    tag=self.result_combo,
                )
                dpg.add_button(
                    label="Accept",
                    width=-1,
                    tag=self.accept_button,
                )
            with dpg.child_window(
                border=True,
                width=-1,
                height=-1,
            ):
                with dpg.group(horizontal=True):
                    self.mu_xps_plot = MuXps()
                    self.residuals_plot = Residuals()
                with dpg.group(horizontal=True):
                    self.nyquist_plot = Nyquist()
                    self.bode_plot = Bode()
        dpg.set_item_callback(self.result_combo, lambda s, a: self.plot(a))
        dpg.set_item_callback(
            self.accept_button,
            lambda s, a, u: self.accept(u),
        )
        self.resize(1, 1)

    def plot(self, label: str):
        self.result_index = self.labels.index(label)
        dpg.set_value(self.result_combo, label)
        # Clear plots
        self.mu_xps_plot.clear()
        self.residuals_plot.clear()
        self.nyquist_plot.clear()
        self.bode_plot.clear()
        # Retrieve the chosen result
        result: KramersKronigResult = self.label_to_result[label]
        dpg.set_item_user_data(self.accept_button, result)
        # Mu-Xps vs num RC
        self.mu_xps_plot.plot(
            num_RCs=self.num_RCs,
            mu=self.mu,
            Xps=self.Xps,
            mu_criterion=self.mu_crit,
            num_RC=result.num_RC,
        )
        # Residuals
        freq: ndarray
        real: ndarray
        imag: ndarray
        freq, real, imag = result.get_residual_data()
        self.residuals_plot.plot(
            frequency=freq,
            real=real,
            imaginary=imag,
        )
        # Data and fit
        # - Nyquist
        real, imag = self.data.get_nyquist_data()
        self.nyquist_plot.plot(
            real=real,
            imaginary=imag,
            label="Data",
            theme=themes.nyquist.data,
        )
        real, imag = result.get_nyquist_data(
            num_per_decade=self.state.config.num_per_decade_in_simulated_lines
        )
        self.nyquist_plot.plot(
            real=real,
            imaginary=imag,
            label="Fit",
            show_label=False,
            line=True,
            theme=themes.nyquist.simulation,
        )
        real, imag = result.get_nyquist_data()
        self.nyquist_plot.plot(
            real=real,
            imaginary=imag,
            label="Fit",
            theme=themes.nyquist.simulation,
        )
        # Bode
        mag: ndarray
        phase: ndarray
        freq, mag, phase = self.data.get_bode_data()
        self.bode_plot.plot(
            frequency=freq,
            magnitude=mag,
            phase=phase,
            labels=(
                "|Z| (d)",
                "phi (d)",
            ),
            themes=(
                themes.bode.magnitude_data,
                themes.bode.phase_data,
            ),
        )
        freq, mag, phase = result.get_bode_data(
            num_per_decade=self.state.config.num_per_decade_in_simulated_lines
        )
        self.bode_plot.plot(
            frequency=freq,
            magnitude=mag,
            phase=phase,
            labels=("|Z| (f)", "phi (f)"),
            show_labels=False,
            line=True,
            themes=(
                themes.bode.magnitude_simulation,
                themes.bode.phase_simulation,
            ),
        )
        freq, mag, phase = result.get_bode_data()
        self.bode_plot.plot(
            frequency=freq,
            magnitude=mag,
            phase=phase,
            labels=("|Z| (f)", "phi (f)"),
            themes=(
                themes.bode.magnitude_simulation,
                themes.bode.phase_simulation,
            ),
        )
        dpg.split_frame()
        self.mu_xps_plot.queue_limits_adjustment()
        self.residuals_plot.queue_limits_adjustment()
        self.nyquist_plot.queue_limits_adjustment()
        self.bode_plot.queue_limits_adjustment()

    def resize(self, width: int, height: int):
        x: int
        y: int
        w: int
        h: int
        x, y, w, h = calculate_window_position_dimensions()
        dpg.configure_item(
            self.window,
            pos=(
                x,
                y,
            ),
            width=w,
            height=h,
        )
        dpg.split_frame()
        width, height = dpg.get_item_rect_size(self.window)
        width -= 56
        height -= 80
        width = int(floor(width / 2))
        height = int(floor(height / 2))
        self.mu_xps_plot.resize(width, height)
        self.residuals_plot.resize(width, height)
        self.nyquist_plot.resize(width, height)
        self.bode_plot.resize(width, height)

    def close(self):
        dpg.hide_item(self.window)
        dpg.delete_item(self.window)
        dpg.delete_item(self.key_handler)
        signals.emit(Signal.UNBLOCK_KEYBINDINGS)
        signals.unregister(Signal.VIEWPORT_RESIZED, self.resize)

    def accept(self, result: KramersKronigResult):
        self.callback(self.data, result, self.settings)
        self.close()
