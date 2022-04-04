# Copyright 2022 DearEIS developers
# DearEIS is licensed under the GPLv3 or later (https://www.gnu.org/licenses/gpl-3.0.html).
# The licenses of DearEIS' dependencies and/or sources of portions of code are included in
# the LICENSES folder.

from deareis.data.kramers_kronig import TestSettings
from deareis.utility import attach_tooltip, window_pos_dims
from numpy import array, log10 as log, ndarray
from pyimpspec import DataSet, KramersKronigResult
from typing import Callable, Dict, List, Tuple, Union
import deareis.tooltips as tooltips
import dearpygui.dearpygui as dpg
import pyimpspec
from deareis.plot import (
    BodePlot,
    MuXpsPlot,
    NyquistPlot,
    ResidualsPlot,
)

# TODO: Argument type assertions

# TODO: Add resize handler to check when the viewport is resized


class ExploratoryResults:
    def __init__(
        self,
        data: DataSet,
        results: List[KramersKronigResult],
        settings: TestSettings,
        num_RCs: ndarray,
        callback: Callable,
    ):
        assert type(data) is DataSet
        assert type(results) is list and all(
            map(lambda _: type(_) is KramersKronigResult, results)
        )
        assert type(settings) is TestSettings
        assert type(num_RCs) is ndarray
        assert callback is not None
        self.callback: Callable = callback
        self.window: int = dpg.generate_uuid()
        self.result_combo: int = dpg.generate_uuid()
        self.accept_button: int = dpg.generate_uuid()
        self.muxps_plot: MuXpsPlot = None
        self.residuals_plot: ResidualsPlot = None
        self.nyquist_plot: NyquistPlot = None
        self.bode_plot: BodePlot = None
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
                f"{result.num_RC}: mu = {result.mu:.3f}, "
                + f"log Xps = {log(result.pseudo_chisqr):.3f}"
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
        self.xps: ndarray = log(array(list(map(lambda _: _.pseudo_chisqr, results))))
        self.plot(default_label)

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
        x, y, w, h = window_pos_dims()
        with dpg.window(
            label="Exploratory test results",
            modal=True,
            pos=(
                x,
                y,
            ),
            width=w,
            height=h,
            tag=self.window,
            on_close=self.close,
        ):
            with dpg.group(horizontal=True):
                dpg.add_text("Num. RC circuits")
                attach_tooltip(tooltips.kramers_kronig_exploratory_result)
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
                self.muxps_plot = MuXpsPlot(
                    dpg.add_plot(
                        width=-1,
                        height=250,
                        anti_aliased=True,
                    )
                )
                self.residuals_plot = ResidualsPlot(
                    dpg.add_plot(
                        width=-1,
                        height=250,
                        anti_aliased=True,
                    )
                )
                self.nyquist_plot = NyquistPlot(
                    dpg.add_plot(
                        width=-1,
                        height=400,
                        anti_aliased=True,
                        equal_aspects=True,
                    )
                )
                self.bode_plot = BodePlot(
                    dpg.add_plot(
                        width=-1,
                        height=400,
                        anti_aliased=True,
                    )
                )
        dpg.set_item_callback(self.result_combo, lambda s, a: self.plot(a))
        dpg.set_item_callback(
            self.accept_button,
            lambda s, a, u: self.accept(u),
        )

    def plot(self, label: str):
        self.result_index = self.labels.index(label)
        dpg.set_value(self.result_combo, label)
        # Clear plots
        self.muxps_plot.clear_plot()
        self.residuals_plot.clear_plot()
        self.nyquist_plot.clear_plot()
        self.bode_plot.clear_plot()
        # Retrieve the chosen result
        result: KramersKronigResult = self.label_to_result[label]
        dpg.set_item_user_data(self.accept_button, result)
        # Mu-Xps vs num RC
        self.muxps_plot.plot_data(
            self.num_RCs, self.mu, self.xps, self.mu_crit, result.num_RC
        )
        # Residuals
        self.residuals_plot.plot_data(*result.get_residual_data())
        # Data and fit
        # - Nyquist
        self.nyquist_plot.plot_data(*self.data.get_nyquist_data(), -1, True)
        self.nyquist_plot.plot_sim(*result.get_nyquist_data(), False, -1)
        self.nyquist_plot.adjust_limits()
        # Bode
        before: Tuple[int, int] = self.bode_plot.plot_sim(
            *result.get_bode_data(),
            False,
            (
                -1,
                -1,
            ),
        )  # type: ignore
        self.bode_plot.plot_data(*self.data.get_bode_data(), before)
        self.bode_plot.adjust_limits()

    def close(self):
        dpg.hide_item(self.window)
        dpg.delete_item(self.window)
        dpg.delete_item(self.key_handler)

    def accept(self, result: KramersKronigResult):
        self.callback(self.data, result, self.settings)
        self.close()
