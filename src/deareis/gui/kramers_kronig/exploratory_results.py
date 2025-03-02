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

from threading import Timer
from traceback import format_exc
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Tuple,
)
from numpy import (
    array,
    asarray,
    complex128,
    float32,
    float64,
    floor,
    inf,
    int64,
    isclose,
    isneginf,
    isposinf,
    log10 as log,
    log2,
    ndarray,
)
from numpy.typing import NDArray
import matplotlib.pyplot as plt
from matplotlib import colormaps
from matplotlib.axes import Axes
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.colors import (
    Colormap,
    Normalize,
)
from matplotlib.cm import ScalarMappable
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator
from deareis.data import DataSet
from deareis.data.kramers_kronig import (
    KramersKronigSuggestionSettings,
    KramersKronigResult,
    KramersKronigSettings,
)
from deareis.data.plotting import PlotExportSettings
from deareis.signals import Signal
from deareis.tooltips import (
    attach_tooltip,
    update_tooltip,
)
import deareis.tooltips as tooltips
from deareis.utility import (
    calculate_window_position_dimensions,
    render_math,
)
import deareis.signals as signals
import deareis.themes as themes
import dearpygui.dearpygui as dpg
from deareis.gui.plots import (
    Bode,
    Image,
    Impedance,
    LogFextStatistic,
    Method1,
    Method2,
    Method3,
    Method4,
    Method5,
    Method6,
    Nyquist,
    Plot,
    PseudoChisqr,
    PseudoChisqrAndScore,
    Residuals,
)
from deareis.state import STATE
from deareis.enums import Action
from deareis.keybindings import (
    Keybinding,
    TemporaryKeybindingHandler,
)
import deareis.api.kramers_kronig as api
from deareis.utility import pad_tab_labels
import pyimpspec.analysis.kramers_kronig.algorithms as algorithms
import pyimpspec.analysis.kramers_kronig.algorithms.utility as algorithm_utilities
from pyimpspec import (
    Circuit,
    Frequencies,
)
from deareis.typing.helpers import Tag


METHOD_TOOLTIPS: List[str] = [
    tooltips.kramers_kronig.method_1,
    tooltips.kramers_kronig.method_2,
    tooltips.kramers_kronig.method_3,
    tooltips.kramers_kronig.method_4,
    tooltips.kramers_kronig.method_5,
    tooltips.kramers_kronig.method_6,
]

SUGGESTION_METHOD_COMBINING: Dict[str, Dict[str, bool]] = {
    "default": {},
    "mean": {"use_mean": True},
    "ranking": {"use_ranking": True},
    "sum": {"use_sum": True},
}


MATH_METHOD_1_MU: int = -1
MATH_METHOD_1_SCORE: int = -1
MATH_METHOD_6_TAU: int = -1
MATH_METHOD_6_SUM_ABS_TAU_VAR: int = -1


def process_math():
    global MATH_METHOD_1_MU
    global MATH_METHOD_1_SCORE
    global MATH_METHOD_6_TAU
    global MATH_METHOD_6_SUM_ABS_TAU_VAR
    MATH_METHOD_1_MU = render_math(
        r"$\mu = 1 - \frac{\Sigma_{R_k < 0} |R_k|}{\Sigma_{R_k \geq 0} |R_k|}$",
        width=200,
        height=40,
    )
    MATH_METHOD_1_SCORE = render_math(
        r"$S = \frac{-\log{\chi^2_{\mathrm{ps}}}}{(\mu_{\mathrm{crit}} - \mu)^\beta}$",
        width=200,
        height=40,
    )
    MATH_METHOD_6_TAU = render_math(
        r"$\tau = RC$",
        width=200,
        height=40,
    )
    MATH_METHOD_6_SUM_ABS_TAU_VAR = render_math(
        r"$\Sigma_{k=1}^{N_\tau} |\frac{\tau_k}{R_k}|"
        + r"\mathrm{\ or\ }"
        + r"\Sigma_{k=1}^{N_\tau} |\frac{\tau_k}{C_k}|$",
        width=230,
        height=40,
    )


signals.register(Signal.RENDER_MATH, process_math)


def format_and_attach_tooltip(tooltip: str) -> int:
    lines: List[str] = tooltip.split("\n")
    if not any(map(lambda s: s.startswith("%") and s.endswith("%"), lines)):
        return attach_tooltip(tooltip)

    replacements: Dict[str, int] = {
        "MU_EQUATION": MATH_METHOD_1_MU,
        "SCORE_EQUATION": MATH_METHOD_1_SCORE,
        "TAU_EQUATION": MATH_METHOD_6_TAU,
        "SUM_ABS_TAU_VAR_EQUATION": MATH_METHOD_6_SUM_ABS_TAU_VAR,
    }
    parent: Tag = dpg.last_item()

    tag: int
    with dpg.tooltip(parent=parent) as tag:
        fragments: List[str] = []

        while len(lines) > 0:
            line: str = lines.pop(0)
            if not (line.startswith("%") and line.endswith("%")):
                fragments.append(line)
                continue

            update_tooltip(
                tag=dpg.add_text(""),
                msg="\n".join(fragments),
            )
            fragments.clear()

            math: int = replacements.get(line[1:-1], -1)
            assert math > 0, f"Unsupported key: {line=}"
            dpg.add_spacer(height=8)
            dpg.add_image(math)

        if len(fragments) > 0:
            update_tooltip(
                tag=dpg.add_text(""),
                msg="\n".join(fragments),
            )

    return tag


class SuggestionSettingsMenu:
    def __init__(
        self,
        default_settings: KramersKronigSuggestionSettings,
        label_pad: int,
    ):
        with dpg.group(horizontal=True):
            self.suggestion_settings_window: Tag = dpg.generate_uuid()
            with dpg.child_window(
                width=-1,
                height=-1,
                border=False,
                tag=self.suggestion_settings_window,
            ):
                dpg.add_text("Auto/exploratory settings")
                attach_tooltip(tooltips.kramers_kronig.suggestion_settings)

                dpg.add_separator()
                with dpg.group(horizontal=True):
                    dpg.add_text("Lower limit".rjust(label_pad))
                    attach_tooltip(tooltips.kramers_kronig.lower_limit)

                    self.lower_limit_input: Tag = dpg.generate_uuid()
                    dpg.add_input_int(
                        default_value=default_settings.lower_limit,
                        min_value=0,
                        min_clamped=True,
                        step=0,
                        on_enter=True,
                        width=-1,
                        tag=self.lower_limit_input,
                    )

                with dpg.group(horizontal=True):
                    dpg.add_text("Upper limit".rjust(label_pad))
                    attach_tooltip(tooltips.kramers_kronig.upper_limit)

                    self.upper_limit_input: Tag = dpg.generate_uuid()
                    dpg.add_input_int(
                        default_value=default_settings.upper_limit,
                        step=0,
                        on_enter=True,
                        width=-1,
                        tag=self.upper_limit_input,
                    )

                with dpg.group(horizontal=True):
                    dpg.add_text("Limit delta".rjust(label_pad))
                    attach_tooltip(tooltips.kramers_kronig.limit_delta)

                    self.limit_delta_input: Tag = dpg.generate_uuid()
                    dpg.add_input_int(
                        default_value=default_settings.limit_delta,
                        min_value=0,
                        min_clamped=True,
                        step=0,
                        on_enter=True,
                        width=-1,
                        tag=self.limit_delta_input,
                    )

                dpg.add_separator()
                with dpg.group(horizontal=True):
                    dpg.add_text("Use".rjust(label_pad))
                    attach_tooltip(
                        tooltips.kramers_kronig.combining_suggestion_methods
                    )

                    self.method_combination_combo: Tag = dpg.generate_uuid()
                    dpg.add_combo(
                        default_value=list(SUGGESTION_METHOD_COMBINING.keys())[0],
                        items=list(SUGGESTION_METHOD_COMBINING.keys()),
                        width=-1,
                        callback=self.select_method_combination,
                        tag=self.method_combination_combo,
                    )

                self.suggestion_methods_table: Tag = dpg.generate_uuid()
                with dpg.table(
                    borders_outerV=True,
                    borders_outerH=True,
                    borders_innerV=True,
                    borders_innerH=True,
                    scrollY=True,
                    freeze_rows=1,
                    tag=self.suggestion_methods_table,
                ):
                    dpg.add_table_column(
                        label="",
                        width_fixed=True,
                    )
                    dpg.add_table_column(
                        label="Suggestion methods",
                        width_fixed=True,
                    )
                    attach_tooltip(tooltips.kramers_kronig.suggestion_methods)

                i: int
                tooltip: str
                for i, tooltip in enumerate(METHOD_TOOLTIPS, start=1):
                    with dpg.table_row(parent=self.suggestion_methods_table):
                        dpg.add_checkbox(
                            default_value=i in default_settings.methods,
                            callback=self.toggle_suggestion_method,
                            user_data=i,
                        )
                        dpg.add_text(f"Method {i}")
                        format_and_attach_tooltip(tooltip)

        dpg.add_separator()
        with dpg.group(horizontal=True):
            dpg.add_text("µ-criterion".rjust(label_pad))
            format_and_attach_tooltip(tooltips.kramers_kronig.method_1_mu_criterion)

            self.m1_mu_crit_slider: Tag = dpg.generate_uuid()
            dpg.add_slider_float(
                default_value=default_settings.m1_mu_criterion,
                min_value=0.01,
                max_value=0.99,
                clamped=True,
                format="%.2f",
                width=-1,
                tag=self.m1_mu_crit_slider,
            )

        with dpg.group(horizontal=True):
            dpg.add_text("Beta".rjust(label_pad))
            format_and_attach_tooltip(tooltips.kramers_kronig.method_1_beta)

            self.m1_beta_slider: Tag = dpg.generate_uuid()
            dpg.add_slider_float(
                default_value=default_settings.m1_beta,
                min_value=0.00,
                max_value=2.00,
                clamped=True,
                format="%.2f",
                width=-1,
                tag=self.m1_beta_slider,
            )

        self.set_settings(default_settings)

    def toggle_suggestion_method(self, sender: int, flag: bool, method: int):
        # This method is replaced by another method when the exploratory results
        # window is opened (see ExploratoryResults._assemble_optimum_num_RC).
        pass

    def get_method_checkbox_tags(self) -> List[int]:
        tags: List[int] = []

        i: int
        row: int
        for i, row in enumerate(
            dpg.get_item_children(self.suggestion_methods_table, slot=1),
            start=1,
        ):
            cells: List[Tag] = dpg.get_item_children(row, slot=1)
            cell: Tag
            for cell in cells:
                if "checkbox" in dpg.get_item_type(cell).lower():
                    tags.append(cell)
                    break

        return tags

    def get_suggestion_methods(
        self,
        method_combination_kwargs: Dict[str, bool],
    ) -> List[int]:
        results: List[int] = []
        if not any(method_combination_kwargs.values()):
            return results

        tag: int
        for tag in self.get_method_checkbox_tags():
            if dpg.get_value(tag) is True:
                results.append(dpg.get_item_user_data(tag))

        return results

    def set_suggestion_methods(self, suggestion_methods: List[int]):
        i: int
        row: Tag
        for i, row in enumerate(
            dpg.get_item_children(self.suggestion_methods_table, slot=1),
            start=1,
        ):
            cells: List[Tag] = dpg.get_item_children(row, slot=1)
            cell: Tag
            for cell in cells:
                if "checkbox" in dpg.get_item_type(cell).lower():
                    dpg.set_value(cell, i in suggestion_methods)
                    break

    def select_method_combination(self, sender: int, value: str):
        label: str
        kwargs: Dict[str, bool]
        for label, kwargs in SUGGESTION_METHOD_COMBINING.items():
            if label != value:
                continue

            if len(kwargs) == 0:
                dpg.hide_item(self.suggestion_methods_table)
                dpg.set_item_height(
                    self.suggestion_settings_window,
                    5 * 24,
                )
                return

            for k, v in kwargs.items():
                if v:
                    dpg.show_item(self.suggestion_methods_table)
                    dpg.set_item_height(
                        self.suggestion_settings_window,
                        5 * 24 + len(METHOD_TOOLTIPS) * 24 + 18,
                    )
                    return

        raise ValueError(f"Unsupported method combination: '{value}'")

    def get_method_combination(self) -> Dict[str, bool]:
        results: Dict[str, bool] = {}

        kwargs: Dict[str, bool]
        for kwargs in SUGGESTION_METHOD_COMBINING.values():
            key: str
            for key in kwargs:
                results[key] = False

        key = dpg.get_value(self.method_combination_combo)
        results.update(SUGGESTION_METHOD_COMBINING[key])

        return results

    def set_method_combination(self, settings: KramersKronigSuggestionSettings):
        label: str
        kwargs: Dict[str, bool]
        for label, kwargs in SUGGESTION_METHOD_COMBINING.items():
            key: str
            value: bool
            for key, value in kwargs.items():
                if getattr(settings, key):
                    dpg.set_value(self.method_combination_combo, label)
                    self.select_method_combination(-1, label)
                    return

        label = list(SUGGESTION_METHOD_COMBINING.keys())[0]
        dpg.set_value(self.method_combination_combo, label)
        self.select_method_combination(-1, label)

    def get_settings(self) -> KramersKronigSuggestionSettings:
        method_combination_kwargs: Dict[str, bool] = self.get_method_combination()
        settings: KramersKronigSuggestionSettings = KramersKronigSuggestionSettings(
            methods=self.get_suggestion_methods(method_combination_kwargs),
            lower_limit=dpg.get_value(self.lower_limit_input),
            upper_limit=dpg.get_value(self.upper_limit_input),
            limit_delta=dpg.get_value(self.limit_delta_input),
            m1_mu_criterion=dpg.get_value(self.m1_mu_crit_slider),
            m1_beta=dpg.get_value(self.m1_beta_slider),
            **method_combination_kwargs,
        )

        return settings

    def set_settings(self, settings: KramersKronigSuggestionSettings):
        self.set_suggestion_methods(settings.methods)
        self.set_method_combination(settings)
        dpg.set_value(self.lower_limit_input, settings.lower_limit)
        dpg.set_value(self.upper_limit_input, settings.upper_limit)
        dpg.set_value(self.m1_mu_crit_slider, settings.m1_mu_criterion)
        dpg.set_value(self.m1_beta_slider, settings.m1_beta)


class ExploratoryResults:
    def __init__(
        self,
        data: DataSet,
        suggested_admittance: bool,
        Z_suggestion: Optional[Tuple[KramersKronigResult, Dict[int, float], int, int]],
        Y_suggestion: Optional[Tuple[KramersKronigResult, Dict[int, float], int, int]],
        Z_evaluations: Optional[List[Tuple[float, List[KramersKronigResult], float]]],
        Y_evaluations: Optional[List[Tuple[float, List[KramersKronigResult], float]]],
        callback: Callable,
        admittance: bool,
    ):
        assert type(data) is DataSet, data
        assert type(suggested_admittance) is bool, suggested_admittance
        assert (
            type(Z_suggestion) is tuple and len(Z_suggestion) == 4
        ) or Z_suggestion is None, Z_suggestion
        assert (
            type(Y_suggestion) is tuple and len(Y_suggestion) == 4
        ) or Y_suggestion is None, Y_suggestion
        assert (
            type(Z_evaluations) is list
            and all(map(lambda _: type(_) is tuple, Z_evaluations))
        ) or Z_evaluations is None, Z_evaluations
        assert (
            type(Y_evaluations) is list
            and all(map(lambda _: type(_) is tuple, Y_evaluations))
        ) or Y_evaluations is None, Y_evaluations
        dpg.split_frame(delay=33)
        self.callback: Callable = callback

        self.window: Tag = dpg.generate_uuid()
        # TODO: Refactor combos to use the custom Combo class?
        self.num_RC_combo: Tag = dpg.generate_uuid()
        self.representation_combo: Tag = dpg.generate_uuid()
        self.log_F_ext_combo: Tag = dpg.generate_uuid()
        self.accept_button: Tag = dpg.generate_uuid()
        self.pseudo_chisqr_and_score_plot: Optional[PseudoChisqrAndScore] = None
        self.pseudo_chisqr_vs_num_RC_plot: Optional[PseudoChisqr] = None
        self.image_plot: Optional[Image] = None
        self.texture_registry: Tag = dpg.generate_uuid()
        self.log_F_ext_plot: Optional[LogFextStatistic] = None
        self.method_plots: Dict[int, Plot] = {}
        self.residuals_plot: Optional[Residuals] = None
        self.nyquist_plot: Optional[Nyquist] = None
        self.bode_plot: Optional[Bode] = None
        self.impedance_plot: Optional[Impedance] = None
        self._assemble(admittance=admittance)
        self.register_keybindings()

        self.previous_suggestion_settings: KramersKronigSuggestionSettings = (
            self.settings_menu.get_settings()
        )

        # These caches are used to speed things up instead of always calling
        # e.g., pyimpspec.analysis.kramers_kronig.suggest_num_RC.
        self.suggestion_cache: Dict[
            bool, Dict[int, Tuple[KramersKronigResult, Dict[int, float], int, int]]
        ] = {
            False: {},
            True: {},
        }
        optimum_index: int = 0
        if Z_suggestion is not None:
            self.suggestion_cache[False][optimum_index] = Z_suggestion
        if Y_suggestion is not None:
            self.suggestion_cache[True][optimum_index] = Y_suggestion

        self.method_score_cache: Dict[bool, Dict[int, Dict[int, Any]]] = {
            False: {},
            True: {},
        }

        self.data: DataSet = data
        self.Z_suggestion: Optional[Tuple[KramersKronigResult, Dict[int, float], int, int]] = (
            Z_suggestion
        )
        self.Y_suggestion: Optional[Tuple[KramersKronigResult, Dict[int, float], int, int]] = (
            Y_suggestion
        )
        self.Z_evaluations: Optional[List[Tuple[float, List[KramersKronigResult], float]]] = (
            Z_evaluations
        )
        self.Y_evaluations: Optional[List[Tuple[float, List[KramersKronigResult], float]]] = (
            Y_evaluations
        )

        self.min_num_RC: int = -1
        self.max_num_RC: int = -1
        self.min_log_pseudo_chisqr: float = -inf
        self.max_log_pseudo_chisqr: float = inf
        self._find_pseudo_chisqr_plot_limits()

        self.log_F_ext_plot.plot(
            log_F_ext=[],
            statistic=[],
            label="",
            line=False,
            theme=themes.suggestion_method.default,
        )
        self.log_F_ext_plot.plot(
            log_F_ext=[],
            statistic=[],
            label="",
            line=False,
            theme=themes.pseudo_chisqr.default_log_F_ext,
        )
        self.log_F_ext_plot.plot(
            log_F_ext=[],
            statistic=[],
            label="",
            line=False,
            theme=themes.pseudo_chisqr.highlight_log_F_ext,
        )

        self.pseudo_chisqr_vs_num_RC_plot.plot(
            num_RC=[],
            pseudo_chisqr=[],
            min_num_RC=self.min_num_RC,
            max_num_RC=self.max_num_RC,
            min_log_pseudo_chisqr=self.min_log_pseudo_chisqr,
            max_log_pseudo_chisqr=self.max_log_pseudo_chisqr,
            label="",
            line=False,
            theme=themes.pseudo_chisqr.default_log_F_ext,
        )
        self.pseudo_chisqr_vs_num_RC_plot.plot(
            num_RC=[],
            pseudo_chisqr=[],
            min_num_RC=self.min_num_RC,
            max_num_RC=self.max_num_RC,
            min_log_pseudo_chisqr=self.min_log_pseudo_chisqr,
            max_log_pseudo_chisqr=self.max_log_pseudo_chisqr,
            label="",
            line=False,
            theme=themes.pseudo_chisqr.highlight_log_F_ext,
        )

        self.log_F_ext_index: int = 0
        self.log_F_ext_label_index: int = 0
        self.log_F_ext_labels: List[str] = []
        self.num_RC_results: List[KramersKronigResult] = []
        self.num_RCs: List[int] = []
        self.max_num_RC_length: int = 0
        self.num_RC_label_to_result: Dict[str, KramersKronigResult] = {}
        self.num_RC_labels: List[str] = []
        self.num_RC_index: int = 0
        self.pseudo_chisqr: List[float] = []

        self.representation_lookup: dict = {}
        self.representation_labels: List[str] = []
        self.representation_index: int = 0
        self.representation_3d_plots: Dict[str, Tag] = {}
        self.dimensions_3d_plots: Optional[Tuple[int, int]] = None
        self.representation_3d_plots_resize_timers: List[Timer] = []
        self._setup_representation_combo(suggested_admittance)

        signals.register(Signal.VIEWPORT_RESIZED, self.resize)
        self.toggle_plot_admittance(admittance)

    def _find_pseudo_chisqr_plot_limits(self) -> int:
        representation: Optional[List[Tuple[float, List[KramersKronigResult], float]]]
        for representation in (self.Z_evaluations, self.Y_evaluations):
            if representation is None:
                continue

            results: List[KramersKronigResult]
            for _, results, _ in representation:
                num_RC: int = min(results, key=lambda t: t.num_RC).num_RC
                if num_RC < self.min_num_RC or self.min_num_RC < 0:
                    self.min_num_RC = num_RC

                num_RC = max(results, key=lambda t: t.num_RC).num_RC
                if num_RC > self.max_num_RC or self.max_num_RC < 0:
                    self.max_num_RC = num_RC

                log_pseudo_chisqr: float = log(
                    min(results, key=lambda t: t.pseudo_chisqr).pseudo_chisqr
                )
                if log_pseudo_chisqr < self.min_log_pseudo_chisqr or isneginf(
                    self.min_log_pseudo_chisqr
                ):
                    self.min_log_pseudo_chisqr = log_pseudo_chisqr

                log_pseudo_chisqr = log(
                    max(results, key=lambda t: t.pseudo_chisqr).pseudo_chisqr
                )
                if log_pseudo_chisqr > self.max_log_pseudo_chisqr or isposinf(
                    self.max_log_pseudo_chisqr
                ):
                    self.max_log_pseudo_chisqr = log_pseudo_chisqr

    def _setup_representation_combo(self, suggested_admittance: bool):
        if self.Z_evaluations is not None:
            self.representation_lookup[
                "Impedance (Z)" + (", suggested" if not suggested_admittance else "")
            ] = self.Z_evaluations
            if not suggested_admittance:
                self.representation_index = 0

        if self.Y_evaluations is not None:
            self.representation_lookup[
                "Admittance (Y)" + (", suggested" if suggested_admittance else "")
            ] = self.Y_evaluations
            if suggested_admittance:
                self.representation_index = -1

        self.representation_labels = list(self.representation_lookup.keys())
        representation_label: str = list(self.representation_lookup.keys())[
            self.representation_index
        ]

        dpg.configure_item(
            self.representation_combo,
            items=self.representation_labels,
            default_value=representation_label,
            user_data=self.representation_lookup,
        )

        self.select_representation(label=representation_label)

    def register_keybindings(self):
        callbacks: Dict[Keybinding, Callable] = {}

        # Cancel
        kb: Keybinding = Keybinding(
            key=dpg.mvKey_Escape,
            mod_alt=False,
            mod_ctrl=False,
            mod_shift=False,
            action=Action.CANCEL,
        )
        callbacks[kb] = self.close

        # Accept
        for kb in STATE.config.keybindings:
            if kb.action is Action.PERFORM_ACTION:
                break
        else:
            kb = Keybinding(
                key=dpg.mvKey_Return,
                mod_alt=True,
                mod_ctrl=False,
                mod_shift=False,
                action=Action.PERFORM_ACTION,
            )
        callbacks[kb] = lambda: self.accept(
            dpg.get_item_user_data(self.accept_button),
        )

        # Previous num RC result
        for kb in STATE.config.keybindings:
            if kb.action is Action.PREVIOUS_PRIMARY_RESULT:
                break
        else:
            kb = Keybinding(
                key=dpg.mvKey_Prior,
                mod_alt=False,
                mod_ctrl=False,
                mod_shift=False,
                action=Action.PREVIOUS_PRIMARY_RESULT,
            )
        callbacks[kb] = lambda: self.plot_num_RC(
            self.num_RC_labels[(self.num_RC_index - 1) % len(self.num_RC_labels)]
        )

        # Previous log Fext result
        for kb in STATE.config.keybindings:
            if kb.action is Action.PREVIOUS_SECONDARY_RESULT:
                break
        else:
            kb = Keybinding(
                key=dpg.mvKey_Prior,
                mod_alt=True,
                mod_ctrl=False,
                mod_shift=False,
                action=Action.PREVIOUS_SECONDARY_RESULT,
            )
        callbacks[kb] = lambda: self.select_log_F_ext(
            self.log_F_ext_labels[
                (self.log_F_ext_label_index - 1) % len(self.log_F_ext_labels)
            ]
        )

        # Previous representation result
        for kb in STATE.config.keybindings:
            if kb.action is Action.PREVIOUS_PROGRAM_TAB:
                break
        else:
            kb = Keybinding(
                key=dpg.mvKey_Prior,
                mod_alt=False,
                mod_ctrl=False,
                mod_shift=True,
                action=Action.PREVIOUS_PROGRAM_TAB,
            )
        callbacks[kb] = lambda: self.select_representation(
            list(self.representation_lookup.keys())[
                (self.representation_index - 1) % len(self.representation_lookup)
            ]
        )

        # Previous plot type
        for kb in STATE.config.keybindings:
            if kb.action is Action.PREVIOUS_PLOT_TAB:
                break
        else:
            kb = Keybinding(
                key=dpg.mvKey_Prior,
                mod_alt=True,
                mod_ctrl=False,
                mod_shift=True,
                action=Action.PREVIOUS_PLOT_TAB,
            )
        callbacks[kb] = lambda: self.set_data_plot_type(
            (
                dpg.get_item_user_data(self.immittance_plot_type_combo).index(
                    dpg.get_value(self.immittance_plot_type_combo)
                )
                - 1
            )
            % len(dpg.get_item_user_data(self.immittance_plot_type_combo))
        )

        # Previous tab
        for kb in STATE.config.keybindings:
            if kb.action is Action.PREVIOUS_PROJECT_TAB:
                break
        else:
            kb = Keybinding(
                key=dpg.mvKey_Prior,
                mod_alt=False,
                mod_ctrl=True,
                mod_shift=False,
                action=Action.PREVIOUS_PROJECT_TAB,
            )
        callbacks[kb] = lambda: self.select_parameter_tab(step=-1)

        # Next num RC result
        for kb in STATE.config.keybindings:
            if kb.action is Action.NEXT_PRIMARY_RESULT:
                break
        else:
            kb = Keybinding(
                key=dpg.mvKey_Next,
                mod_alt=False,
                mod_ctrl=False,
                mod_shift=False,
                action=Action.NEXT_PRIMARY_RESULT,
            )
        callbacks[kb] = lambda: self.plot_num_RC(
            self.num_RC_labels[(self.num_RC_index + 1) % len(self.num_RC_labels)]
        )

        # Next log Fext result
        for kb in STATE.config.keybindings:
            if kb.action is Action.NEXT_SECONDARY_RESULT:
                break
        else:
            kb = Keybinding(
                key=dpg.mvKey_Next,
                mod_alt=True,
                mod_ctrl=False,
                mod_shift=False,
                action=Action.NEXT_SECONDARY_RESULT,
            )
        callbacks[kb] = lambda: self.select_log_F_ext(
            self.log_F_ext_labels[
                (self.log_F_ext_label_index + 1) % len(self.log_F_ext_labels)
            ]
        )

        # Next representation result
        for kb in STATE.config.keybindings:
            if kb.action is Action.NEXT_PROGRAM_TAB:
                break
        else:
            kb = Keybinding(
                key=dpg.mvKey_Prior,
                mod_alt=False,
                mod_ctrl=False,
                mod_shift=True,
                action=Action.NEXT_PROGRAM_TAB,
            )
        callbacks[kb] = lambda: self.select_representation(
            list(self.representation_lookup.keys())[
                (self.representation_index - 1) % len(self.representation_lookup)
            ]
        )

        # Next plot type
        for kb in STATE.config.keybindings:
            if kb.action is Action.NEXT_PLOT_TAB:
                break
        else:
            kb = Keybinding(
                key=dpg.mvKey_Next,
                mod_alt=True,
                mod_ctrl=False,
                mod_shift=True,
                action=Action.NEXT_PLOT_TAB,
            )
        callbacks[kb] = lambda: self.set_data_plot_type(
            (
                dpg.get_item_user_data(self.immittance_plot_type_combo).index(
                    dpg.get_value(self.immittance_plot_type_combo)
                )
                + 1
            )
            % len(dpg.get_item_user_data(self.immittance_plot_type_combo))
        )

        # Next tab
        for kb in STATE.config.keybindings:
            if kb.action is Action.NEXT_PROJECT_TAB:
                break
        else:
            kb = Keybinding(
                key=dpg.mvKey_Next,
                mod_alt=False,
                mod_ctrl=True,
                mod_shift=False,
                action=Action.NEXT_PROJECT_TAB,
            )
        callbacks[kb] = lambda: self.select_parameter_tab(step=1)

        # Create the handler
        self.keybinding_handler: TemporaryKeybindingHandler = (
            TemporaryKeybindingHandler(callbacks=callbacks)
        )

    def _assemble(self, admittance: bool):
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
                dpg.add_text("         Representation")
                dpg.add_combo(
                    width=-1,
                    tag=self.representation_combo,
                )

            with dpg.group(horizontal=True):
                dpg.add_text("Range of time constants")
                dpg.add_combo(
                    width=-1,
                    tag=self.log_F_ext_combo,
                )

            with dpg.group(horizontal=True):
                dpg.add_text("  Number of RC elements")
                attach_tooltip(tooltips.kramers_kronig.exploratory_result)

                dpg.add_combo(
                    width=-1,
                    tag=self.num_RC_combo,
                )

            with dpg.child_window(border=False, width=-1, height=-24):
                self.parameter_tab_bar: Tag = dpg.generate_uuid()
                with dpg.tab_bar(tag=self.parameter_tab_bar):
                    self._assemble_log_F_ext_representation()
                    self._assemble_optimum_num_RC(admittance=admittance)

            dpg.add_button(
                label="Accept",
                width=-1,
                tag=self.accept_button,
            )

            pad_tab_labels(self.parameter_tab_bar)
            self.select_parameter_tab(index=1)

        dpg.set_item_callback(
            self.num_RC_combo,
            lambda s, a: self.plot_num_RC(a),
        )
        dpg.set_item_callback(
            self.representation_combo,
            lambda s, a, u: self.select_representation(a),
        )
        dpg.set_item_callback(
            self.log_F_ext_combo,
            lambda s, a, u: self.select_log_F_ext(a),
        )
        dpg.set_item_callback(
            self.accept_button,
            lambda s, a, u: self.accept(u),
        )
        self.resize(1, 1)

    def _assemble_log_F_ext_representation(self):
        with dpg.tab(label="Range of time constants"):
            plot_settings: PlotExportSettings = STATE.config.default_plot_export_settings
            if plot_settings.disable_preview or not plot_settings.clear_registry:
                self.log_F_ext_plot = LogFextStatistic(height=200)
                self.pseudo_chisqr_vs_num_RC_plot = PseudoChisqr()
            else:
                tab_bar: Tag
                with dpg.tab_bar() as tab_bar:
                    with dpg.tab(label="2D (dynamic)"):
                        self.log_F_ext_plot = LogFextStatistic(height=200)
                        self.pseudo_chisqr_vs_num_RC_plot = PseudoChisqr()

                    plot_tab_3d: Tag
                    with dpg.tab(label="3D (static)") as plot_tab_3d:
                        self.image_plot: Image = Image()
                        dpg.add_texture_registry(tag=self.texture_registry)

                pad_tab_labels(tab_bar)

                plot_tab_handler: Tag
                with dpg.item_handler_registry() as plot_tab_handler:
                    dpg.add_item_clicked_handler(
                        callback=lambda s, a, u: self._generate_3d_plot(
                            tab_clicked=True
                        )
                    )

                dpg.bind_item_handler_registry(plot_tab_3d, plot_tab_handler)

    def _refresh_3d_plot(self):
        self.representation_3d_plots.clear()
        self.dimensions_3d_plots = None
        if not dpg.does_item_exist(self.texture_registry):
            return

        dpg.delete_item(self.texture_registry, children_only=True)
        self._generate_3d_plot()

    def _generate_3d_plot(self, tab_clicked: bool = False):
        label: str = dpg.get_value(self.representation_combo)
        tag: Optional[Tag] = self.representation_3d_plots.get(label)

        pixel_width: int
        pixel_height: int
        if self.dimensions_3d_plots is None:
            pixel_width: int = dpg.get_item_width(self.window) - 36
            pixel_height: int = dpg.get_item_height(self.window) - 192

            pixel_width = 2**int(floor(log2(pixel_width)) + 1)
            pixel_height = 2**int(floor(log2(pixel_height)) + 1)
            
            self.dimensions_3d_plots = (pixel_width, pixel_height)
        else:
            pixel_width, pixel_height = self.dimensions_3d_plots

        if tag is not None:
            if tab_clicked is True:
                return

            self.image_plot.clear()
            self.image_plot.plot(
                texture=tag,
                bounds_min=(
                    0,
                    0,
                ),
                bounds_max=(
                    pixel_width,
                    pixel_height,
                ),
            )
            self.image_plot.queue_limits_adjustment()
            return

        evaluations: List[Tuple[float, List[KramersKronigResult], float]]
        evaluations = self.representation_lookup[label]

        dpi: int = 100
        width = pixel_width / dpi
        height = pixel_height / dpi

        figure: Figure = plt.figure(figsize=(width, height), dpi=dpi)
        ax: Axes3D = figure.add_subplot(111, projection="3d")
        canvas: FigureCanvasAgg = FigureCanvasAgg(figure)

        rc: dict = {
            "axes.edgecolor": "white",
            "axes.labelcolor": "white",
        }
        with plt.rc_context(rc):
            count: int = len(evaluations)
            cmap: Colormap = colormaps.get_cmap("rainbow")
            colors: List[Tuple[float, float, float, float]] = [
                cmap(i / count) for i in range(0, count)
            ]

            log_F_ext: float
            tests: List[KramersKronigResult]
            statistic: float
            color: Tuple[float, float, float, float]
            for (log_F_ext, tests, statistic), color in zip(
                evaluations,
                colors,
            ):
                scatter_kwargs = dict(
                    label=f"{log_F_ext:.3g}",
                    marker=".",
                    color=color,
                )

                x: NDArray[int64] = array([t.num_RC for t in tests], dtype=int64)
                y: NDArray[float64] = array([log_F_ext] * len(x), dtype=float64)
                z: NDArray[float64] = log([t.pseudo_chisqr for t in tests])

                ax.plot(
                    x,
                    y,
                    z,
                    color="white",
                    alpha=0.25,
                )

                ax.scatter(
                    x,
                    y,
                    z,
                    **scatter_kwargs,
                )

            cbar = figure.colorbar(
                ScalarMappable(norm=Normalize(0, 1), cmap=cmap),
                ax=ax,
                location="bottom",
                fraction=0.05,
                shrink=0.5,
                label="Best to worst (left to right)",
                pad=0.0,
            )
            cbar.set_ticks([])

            dim: str
            for dim in ("x", "y", "z"):
                ax.tick_params(axis=dim, colors="white")
                dim_axis = getattr(ax, f"{dim}axis")
                dim_axis.label.set_color("white")
                dim_axis.line.set_color("white")
                dim_axis.set_pane_color((1.0, 1.0, 1.0, 0.0))
                dim_axis._axinfo["grid"]["color"] = (1.0, 1.0, 1.0, 0.15)

            ax.set_xlabel("Number of RC elements")
            ax.set_ylabel(r"$\log{F_{\rm ext}}$")
            ax.set_zlabel(r"$\log{\chi^{2}_{\rm ps}}$")
            ax.xaxis.set_major_locator(MaxNLocator(integer=True))
            ax.patch.set_alpha(0.0)

            figure.patch.set_alpha(0.0)
            figure.tight_layout()

            canvas.draw()
            buffer: NDArray[float32] = asarray(canvas.buffer_rgba()).astype(float32) / 255

        tag = dpg.add_raw_texture(
            pixel_width,
            pixel_height,
            buffer,
            format=dpg.mvFormat_Float_rgba,
            parent=self.texture_registry,
        )
        self.representation_3d_plots[label] = tag
        self.image_plot.clear()
        self.image_plot.plot(
            texture=tag,
            bounds_min=(
                0,
                0,
            ),
            bounds_max=(
                pixel_width,
                pixel_height,
            ),
        )
        plt.close(figure)
        self.image_plot.queue_limits_adjustment()

    def _assemble_optimum_num_RC(self, admittance: bool):
        with dpg.tab(label="Number of RC elements"):
            with dpg.group(horizontal=True):
                with dpg.child_window(width=220):
                    self.settings_menu: SuggestionSettingsMenu = (
                        SuggestionSettingsMenu(
                            default_settings=STATE.kramers_kronig_suggestion_settings,
                            label_pad=12,
                        )
                    )
                    # Reassign toggle_suggestion_method
                    tag: int
                    for tag in self.settings_menu.get_method_checkbox_tags():
                        dpg.set_item_callback(tag, self.toggle_suggestion_method)

                    # Reassign select_method_combination
                    dpg.set_item_callback(
                        self.settings_menu.method_combination_combo,
                        self.select_method_combination,
                    )

                    dpg.add_separator()
                    with dpg.group(horizontal=True):
                        dpg.add_text("?")
                        attach_tooltip(
                            tooltips.kramers_kronig.apply_suggestion_settings
                        )

                        self.apply_settings_button: Tag = dpg.generate_uuid()
                        dpg.add_button(
                            label="Apply and refresh",
                            callback=lambda s, a, u: self.refresh_wrapper(),
                            width=-1,
                            tag=self.apply_settings_button,
                        )

                settings: KramersKronigSuggestionSettings = self.settings_menu.get_settings()

                with dpg.child_window(
                    border=False,
                    width=-1,
                    height=-1,
                ):
                    with dpg.group(horizontal=False):
                        self.method_plot_type_combo: Tag = dpg.generate_uuid()
                        dpg.add_combo(
                            width=-1,
                            callback=lambda s, a, u: self.set_method_plot_type(
                                u.index(a) if a in u else -1
                            ),
                            user_data=[],
                            tag=self.method_plot_type_combo,
                        )

                        self.pseudo_chisqr_and_score_plot = PseudoChisqrAndScore()

                        i: int
                        Class: Plot
                        for i, Class in enumerate(
                            (
                                Method1,
                                Method2,
                                Method3,
                                Method4,
                                Method5,
                                Method6,
                            ),
                            start=1,
                        ):
                            self.method_plots[i] = Class()
                            if not (
                                (len(settings.methods) == 1)
                                and (i in settings.methods)
                            ):
                                self.method_plots[i].hide()

                        i = 0
                        if len(settings.methods) == 1:
                            i = settings.methods[0]
                            self.pseudo_chisqr_and_score_plot.hide()

                        items = ["Scores and log X² (pseudo)"] + [
                            f"Method {k}" for k in self.method_plots.keys()
                        ]
                        dpg.configure_item(
                            self.method_plot_type_combo,
                            default_value=items[i],
                            items=items,
                            user_data=items,
                        )

                    with dpg.group(horizontal=False):
                        self.residuals_plot = Residuals(limit=0.5)
                        self.residuals_plot.plot(
                            frequencies=array([]),
                            real=array([]),
                            imaginary=array([]),
                        )

                    with dpg.group(horizontal=False):
                        with dpg.group(horizontal=True):
                            self.immittance_plot_type_combo: Tag = dpg.generate_uuid()
                            items = [
                                "Bode",
                                "Nyquist",
                                "Real & imag.",
                            ]
                            dpg.add_combo(
                                default_value=items[1],
                                items=items,
                                width=-180,
                                callback=lambda s, a, u: self.set_data_plot_type(
                                    u.index(a) if a in u else -1
                                ),
                                user_data=items,
                                tag=self.immittance_plot_type_combo,
                            )

                            self.adjust_limits_checkbox: Tag = dpg.generate_uuid()
                            dpg.add_checkbox(
                                label="Adjust limits",
                                default_value=True,
                                tag=self.adjust_limits_checkbox,
                            )

                            self.admittance_checkbox: Tag = dpg.generate_uuid()
                            dpg.add_checkbox(
                                label="Y",
                                default_value=admittance,
                                callback=lambda s, a, u: self.toggle_plot_admittance(a),
                                tag=self.admittance_checkbox,
                            )
                            attach_tooltip(tooltips.general.plot_admittance)

                        self.nyquist_plot = Nyquist()
                        self.nyquist_plot.plot(
                            impedances=array([], dtype=complex128),
                            label="Data",
                            theme=themes.nyquist.data,
                        )
                        self.nyquist_plot.plot(
                            impedances=array([], dtype=complex128),
                            label="Fit",
                            show_label=False,
                            line=True,
                            theme=themes.nyquist.simulation,
                        )
                        self.nyquist_plot.plot(
                            impedances=array([], dtype=complex128),
                            label="Fit",
                            theme=themes.nyquist.simulation,
                        )

                        self.bode_plot = Bode()
                        self.bode_plot.plot(
                            frequencies=array([]),
                            impedances=array([], dtype=complex128),
                            labels=(
                                "Mod(data)",
                                "Phase(data)",
                            ),
                            themes=(
                                themes.bode.magnitude_data,
                                themes.bode.phase_data,
                            ),
                        )
                        self.bode_plot.plot(
                            frequencies=array([]),
                            impedances=array([], dtype=complex128),
                            labels=(
                                "Mod(fit)",
                                "Phase(fit)",
                            ),
                            show_labels=False,
                            line=True,
                            themes=(
                                themes.bode.magnitude_simulation,
                                themes.bode.phase_simulation,
                            ),
                        )
                        self.bode_plot.plot(
                            frequencies=array([]),
                            impedances=array([], dtype=complex128),
                            labels=(
                                "Mod(fit)",
                                "Phase(fit)",
                            ),
                            themes=(
                                themes.bode.magnitude_simulation,
                                themes.bode.phase_simulation,
                            ),
                        )
                        self.bode_plot.hide()

                        self.impedance_plot = Impedance()
                        self.impedance_plot.plot(
                            frequencies=array([]),
                            impedances=array([], dtype=complex128),
                            labels=(
                                "Re(data)",
                                "Im(data)",
                            ),
                            line=False,
                            themes=(
                                themes.impedance.real_data,
                                themes.impedance.imaginary_data,
                            ),
                        )
                        self.impedance_plot.plot(
                            frequencies=array([]),
                            impedances=array([], dtype=complex128),
                            labels=(
                                "Re(fit)",
                                "Im(fit)",
                            ),
                            line=True,
                            fit=True,
                            themes=(
                                themes.impedance.real_simulation,
                                themes.impedance.imaginary_simulation,
                            ),
                            show_labels=False,
                        )
                        self.impedance_plot.plot(
                            frequencies=array([]),
                            impedances=array([], dtype=complex128),
                            labels=(
                                "Re(fit)",
                                "Im(fit)",
                            ),
                            line=False,
                            fit=True,
                            themes=(
                                themes.impedance.real_simulation,
                                themes.impedance.imaginary_simulation,
                            ),
                        )
                        self.impedance_plot.hide()

    def set_method_plot_type(self, index: int):
        if (index < 0) or (index > max(self.method_plots.keys())):
            return
        elif index == 0:
            self.pseudo_chisqr_and_score_plot.show()
        else:
            self.pseudo_chisqr_and_score_plot.hide()

        i: int
        plot: Plot
        for i, plot in self.method_plots.items():
            if i == index:
                plot.show()
            else:
                plot.hide()

        items: List[str] = dpg.get_item_configuration(self.method_plot_type_combo).get(
            "items", []
        )
        dpg.set_value(self.method_plot_type_combo, items[index])

    def get_method_plot_type(self) -> int:
        items: List[str] = dpg.get_item_configuration(self.method_plot_type_combo).get(
            "items", []
        )
        current_value: str = dpg.get_value(self.method_plot_type_combo)
        if len(items) == 0 or current_value not in items:
            return -1

        return items.index(current_value)

    def set_data_plot_type(self, index: int):
        if index < 0:
            return

        dpg.set_value(
            self.immittance_plot_type_combo,
            dpg.get_item_user_data(self.immittance_plot_type_combo)[index],
        )

        i: int
        plot: Plot
        for i, plot in enumerate(
            (
                self.bode_plot,
                self.nyquist_plot,
                self.impedance_plot,
            )
        ):
            if i == index:
                plot.show()
            else:
                plot.hide()

    def select_method_combination(self, sender: int, value: str):
        self.settings_menu.select_method_combination(sender, value)

        label: str
        kwargs: Dict[str, bool]
        for label, kwargs in SUGGESTION_METHOD_COMBINING.items():
            if label != value:
                continue

            if len(kwargs) == 0:
                dpg.enable_item(self.apply_settings_button)
            else:
                self.toggle_suggestion_method(sender=-1, flag=False, method=-1)

    def toggle_suggestion_method(self, sender: int, flag: bool, method: int):
        self.settings_menu.toggle_suggestion_method(sender, flag, method)

        settings: KramersKronigSuggestionSettings = self.settings_menu.get_settings()
        if (
            any(
                (
                    settings.use_mean,
                    settings.use_ranking,
                    settings.use_sum,
                )
            )
            and len(settings.methods) == 0
        ):
            dpg.disable_item(self.apply_settings_button)
        else:
            dpg.enable_item(self.apply_settings_button)

    def refresh_wrapper(self, *args, **kwargs):
        try:
            self.refresh(*args, **kwargs)
        except:
            self.close()
            dpg.split_frame(delay=60)
            signals.emit(Signal.SHOW_ERROR_MESSAGE, traceback=format_exc())

    # TODO: Hide and show busy message?
    # TODO: Delete window if an exception is encountered!
    def refresh(
        self,
        suggestion: Optional[Tuple[KramersKronigResult, Dict[int, float], int, int]] = None,
    ):
        self.keybinding_handler.block()
        dpg.disable_item(self.representation_combo)
        dpg.disable_item(self.log_F_ext_combo)
        dpg.disable_item(self.num_RC_combo)
        dpg.disable_item(self.accept_button)

        settings: KramersKronigSuggestionSettings = self.settings_menu.get_settings()
        self.latest_settings: KramersKronigSuggestionSettings = settings

        if settings != self.previous_suggestion_settings:
            self.previous_suggestion_settings = settings
            self.suggestion_cache[False].clear()
            self.suggestion_cache[True].clear()
            suggestion = None

            self.method_score_cache[False].clear()
            self.method_score_cache[True].clear()

        methods_to_plot: List[int] = []
        if len(settings.methods) > 0:
            methods_to_plot.extend(settings.methods)
        elif not any((settings.use_mean, settings.use_ranking, settings.use_sum)):
            methods_to_plot.extend([3, 4, 5])

        subdivided_frequencies: Optional[Frequencies] = None
        curvatures: Optional[Dict[int, NDArray[float64]]] = None
        if suggestion is None and any((i in methods_to_plot for i in (3, 4, 5))):
            circuits: Dict[int, Circuit] = {
                t.num_RC: t.circuit for t in self.num_RC_results
            }
            subdivided_frequencies = algorithm_utilities.subdivide_frequencies(
                self.num_RC_results[0].get_frequencies()
            )
            curvatures = {
                num_RC: algorithm_utilities.calculate_curvatures(
                    circuit.get_impedances(subdivided_frequencies)
                )
                for num_RC, circuit in circuits.items()
            }

        if suggestion is None:
            suggestion = api.suggest_num_RC(
                self.num_RC_results,
                settings,
                subdivided_frequencies=subdivided_frequencies,
                curvatures=curvatures,
            )
            self.suggestion_cache[suggestion[0].admittance][
                self.log_F_ext_index
            ] = suggestion

        default_result: KramersKronigResult
        scores: Dict[int, float]
        lower_limit: int
        upper_limit: int
        default_result, scores, lower_limit, upper_limit = suggestion

        admittance: bool = default_result.admittance

        num_RC: int = default_result.num_RC
        scores = {t.num_RC: scores.get(t.num_RC, 0.0) for t in self.num_RC_results}

        max_score: float = max(scores.values())
        if max_score != 0.0:
            scores = {k: v / max_score for k, v in scores.items()}
        self.scores: List[float] = [
            _[1] for _ in sorted(scores.items(), key=lambda kv: kv[0])
        ]

        default_label: str = ""
        self.num_RC_labels.clear()
        self.num_RC_label_to_result.clear()

        result: KramersKronigResult
        for result in self.num_RC_results:
            label: str = (
                str(result.num_RC).rjust(self.max_num_RC_length)
                + f": log X² (ps.) = {log(result.pseudo_chisqr):.3f}, "
                + f" score = {scores[result.num_RC]:.4f}"
            )

            if result.num_RC == lower_limit:
                if settings.lower_limit < 1:
                    label += ", estimated lower limit"
                else:
                    label += ", chosen lower limit"
            elif result.num_RC == upper_limit:
                if settings.upper_limit < 1:
                    label += ", estimated upper limit"
                else:
                    label += ", chosen upper limit"

            if result == default_result:
                label += ", suggested optimum"
                default_label = label

            self.num_RC_label_to_result[label] = result

        assert default_label != ""
        self.num_RC_labels.extend(self.num_RC_label_to_result.keys())
        self.num_RC_index = self.num_RC_labels.index(default_label)
        dpg.configure_item(
            self.num_RC_combo,
            items=self.num_RC_labels,
            default_value=default_label,
        )

        assert self.pseudo_chisqr_and_score_plot is not None
        self.pseudo_chisqr_and_score_plot.clear()

        plot: Plot
        for plot in self.method_plots.values():
            plot.clear()

        max_x: int = min((max(self.num_RCs) + 1, upper_limit + 10))

        dpg.split_frame(delay=33)
        self.log_F_ext_plot.queue_limits_adjustment()
        self.pseudo_chisqr_vs_num_RC_plot.queue_limits_adjustment()
        self.pseudo_chisqr_and_score_plot.plot(
            num_RCs=self.num_RCs,
            pseudo_chisqr=self.pseudo_chisqr,
            scores=self.scores,
            num_RC=num_RC,
            lower_limit=lower_limit,
            upper_limit=upper_limit,
            max_x=max_x,
        )

        for i, plot in self.method_plots.items():
            if i not in methods_to_plot:
                continue

            method_scores: Any = self.method_score_cache[admittance].get(self.log_F_ext_index)
            if method_scores is None:
                self.method_score_cache[admittance][self.log_F_ext_index] = {}
            method_scores = self.method_score_cache[admittance][self.log_F_ext_index].get(i, None)

            if i == 1:
                if method_scores is not None:
                    mu, scores = method_scores
                else:
                    mu = algorithms.suggest_num_RC_method_1(
                        tests=self.num_RC_results,
                        mu_criterion=settings.m1_mu_criterion,
                        beta=0.0,
                        relative_scores=False,
                    )
                    scores = algorithms.suggest_num_RC_method_1(
                        tests=self.num_RC_results,
                        mu_criterion=settings.m1_mu_criterion,
                        beta=settings.m1_beta,
                        relative_scores=False,
                    )
                    self.method_score_cache[admittance][self.log_F_ext_index][i] = (mu, scores)

                plot.plot(
                    num_RCs=self.num_RCs,
                    mu=[mu[t.num_RC] for t in self.num_RC_results],
                    scores=[scores[t.num_RC] for t in self.num_RC_results],
                    mu_criterion=settings.m1_mu_criterion,
                    beta=settings.m1_beta,
                    num_RC=num_RC,
                    lower_limit=lower_limit,
                    upper_limit=upper_limit,
                    max_x=max_x,
                )
            elif i == 2:
                if method_scores is not None:
                    norms = method_scores
                else:
                    norms = [
                        _[1]
                        for _ in sorted(
                            algorithms.suggest_num_RC_method_2(
                                tests=self.num_RC_results,
                                relative_scores=False,
                            ).items(),
                            key=lambda kv: kv[0],
                        )
                    ]
                    self.method_score_cache[admittance][self.log_F_ext_index][i] = norms

                plot.plot(
                    num_RCs=self.num_RCs,
                    norms=norms,
                    num_RC=num_RC,
                    lower_limit=lower_limit,
                    upper_limit=upper_limit,
                    max_x=max_x,
                )
            elif i == 3:
                if method_scores is not None:
                    norms = method_scores
                else:
                    norms = [
                        _[1]
                        for _ in sorted(
                            algorithms.suggest_num_RC_method_3(
                                tests=self.num_RC_results,
                                relative_scores=False,
                                subdivided_frequencies=subdivided_frequencies,
                                curvatures=curvatures,
                            ).items(),
                            key=lambda kv: kv[0],
                        )
                    ]
                    self.method_score_cache[admittance][self.log_F_ext_index][i] = norms

                plot.plot(
                    num_RCs=self.num_RCs,
                    norms=norms,
                    num_RC=num_RC,
                    lower_limit=lower_limit,
                    upper_limit=upper_limit,
                    max_x=max_x,
                )
            elif i == 4:
                if method_scores is not None:
                    num_sign_changes = method_scores
                else:
                    num_sign_changes = [
                        _[1]
                        for _ in sorted(
                            algorithms.suggest_num_RC_method_4(
                                tests=self.num_RC_results,
                                relative_scores=False,
                                subdivided_frequencies=subdivided_frequencies,
                                curvatures=curvatures,
                            ).items(),
                            key=lambda kv: kv[0],
                        )
                    ]
                    self.method_score_cache[admittance][self.log_F_ext_index][i] = num_sign_changes

                plot.plot(
                    num_RCs=self.num_RCs,
                    num_sign_changes=num_sign_changes,
                    num_RC=num_RC,
                    lower_limit=lower_limit,
                    upper_limit=upper_limit,
                    max_x=max_x,
                )
            elif i == 5:
                if method_scores is not None:
                    mean_distances = method_scores
                else:
                    mean_distances = [
                        _[1]
                        for _ in sorted(
                            algorithms.suggest_num_RC_method_5(
                                tests=self.num_RC_results,
                                relative_scores=False,
                                subdivided_frequencies=subdivided_frequencies,
                                curvatures=curvatures,
                            ).items(),
                            key=lambda kv: kv[0],
                        )
                    ]
                    self.method_score_cache[admittance][self.log_F_ext_index][i] = mean_distances

                plot.plot(
                    num_RCs=self.num_RCs,
                    mean_distances=mean_distances,
                    num_RC=num_RC,
                    lower_limit=lower_limit,
                    upper_limit=upper_limit,
                    max_x=max_x,
                )
            elif i == 6:
                if method_scores is not None:
                    log_sum_abs_tau_var, x, y = method_scores
                else:
                    x = self.num_RCs[:]
                    y = algorithms.suggest_num_RC_method_6(
                        tests=self.num_RC_results,
                        relative_scores=False,
                    )
                    y = [y[t.num_RC] for t in self.num_RC_results]
                    for k in range(0, len(y)):
                        if y[k] < y[0]:
                            break
                    else:
                        while ((y[k] - y[k - 1]) > 0.0) and (k > 1):
                            k -= 1
                        if k < 2:
                            k = len(y) - 1

                    log_sum_abs_tau_var = list(
                        map(
                            lambda t: algorithms.method_6._calculate_log_sum_abs_tau_var(
                                t.circuit
                            ),
                            self.num_RC_results,
                        )
                    )
                    x = x[:k]
                    y = y[:k]
                    self.method_score_cache[admittance][self.log_F_ext_index][i] = (log_sum_abs_tau_var, x, y)

                plot.plot(
                    num_RCs=self.num_RCs,
                    data=log_sum_abs_tau_var,
                    fit_x=x,
                    fit_y=y,
                    admittance=self.num_RC_results[0].admittance,
                    num_RC=num_RC,
                    lower_limit=lower_limit,
                    upper_limit=upper_limit,
                    max_x=max_x,
                )
            else:
                raise NotImplementedError(f"Unsupported method: {i=}")

        if len(settings.methods) == 1:
            current_method_plot_type: int = self.get_method_plot_type()
            if current_method_plot_type != settings.methods[0]:
                self.set_method_plot_type(settings.methods[0])
        else:
            self.set_method_plot_type(0)

        self.plot_num_RC(default_label)

        dpg.split_frame(delay=33)
        self.pseudo_chisqr_and_score_plot.queue_limits_adjustment()
        for plot in self.method_plots.values():
            plot.queue_limits_adjustment()

        dpg.enable_item(self.representation_combo)
        dpg.enable_item(self.log_F_ext_combo)
        dpg.enable_item(self.num_RC_combo)
        dpg.enable_item(self.accept_button)
        self.keybinding_handler.unblock()

    def select_parameter_tab(
        self,
        index: Optional[int] = None,
        step: Optional[int] = None,
    ):
        tabs: List[Tag] = dpg.get_item_children(self.parameter_tab_bar, slot=1)

        if step is not None:
            current_tab: Tag = dpg.get_value(self.parameter_tab_bar)
            index = (tabs.index(current_tab) + step) % len(tabs)

        dpg.set_value(self.parameter_tab_bar, tabs[index])

    def select_representation(self, label: str):
        dpg.set_value(self.representation_combo, label)
        self.representation_index = self.representation_labels.index(label)

        evaluations: List[Tuple[float, List[KramersKronigResult], float]]
        evaluations = self.representation_lookup[label]

        self.log_F_ext_plot.update(
            index=0,
            log_F_ext=[e[0] for e in evaluations],
            statistic=[e[2] for e in evaluations],
        )
        self.log_F_ext_plot.update(
            index=2,
            log_F_ext=[evaluations[0][0]],
            statistic=[evaluations[0][2]],
        )

        optimum_index: int = 0
        log_F_ext_lookup: dict = {
            f"log Fext = {e[0]:.3g}, statistic = {e[2]:.3g}"
            + (", suggested optimum" if e == evaluations[optimum_index] else ""): e[1]
            for e in sorted(evaluations, key=lambda e: e[0])
        }
        self.log_F_ext_labels.clear()
        self.log_F_ext_labels.extend(log_F_ext_lookup.keys())

        log_F_ext_label: str = [
            kv[0]
            for kv in log_F_ext_lookup.items()
            if kv[1] == evaluations[optimum_index][1]
        ][0]

        dpg.configure_item(
            self.log_F_ext_combo,
            items=list(log_F_ext_lookup.keys()),
            default_value=log_F_ext_label,
            user_data=log_F_ext_lookup,
        )

        log_F_ext, results, statistic  = min(evaluations, key=lambda e: abs(e[0]))
        if isclose(log_F_ext, 0.0):
            self.log_F_ext_plot.update(
                index=1,
                log_F_ext=[log_F_ext],
                statistic=[statistic],
            )

            self.pseudo_chisqr_vs_num_RC_plot.show_series(index=1)
            self.pseudo_chisqr_vs_num_RC_plot.update(
                index=0,
                num_RC=[t.num_RC for t in results],
                pseudo_chisqr=[log(t.pseudo_chisqr) for t in results],
                label=f"log Fext = {log_F_ext:.3g}",
            )
        else:
            self.pseudo_chisqr_vs_num_RC_plot.hide_series(index=1)

        if len(self.representation_3d_plots) > 0:
            self._generate_3d_plot()

        self.select_log_F_ext(label=log_F_ext_label)

    def select_log_F_ext(self, label: str):
        dpg.set_value(self.log_F_ext_combo, label)

        results: List[KramersKronigResult] = dpg.get_item_user_data(self.log_F_ext_combo)[label]
        admittance: bool = results[0].admittance

        index: int
        evaluation: Tuple[float, List[KramersKronigResult], float]
        for index, evaluation in enumerate(
            self.Y_evaluations if admittance else self.Z_evaluations
        ):
            if evaluation[1] is results:
                self.log_F_ext_index = index
                break
        else:
            raise IndexError()

        self.log_F_ext_label_index = self.log_F_ext_labels.index(label)
        suggestion: Optional[Tuple[KramersKronigResult, Dict[int, float], int, int]]
        suggestion = self.suggestion_cache[admittance].get(index, None)

        self.num_RC_results = results
        self.num_RCs = [t.num_RC for t in self.num_RC_results]
        self.max_num_RC_length = len(str(max(self.num_RCs)))
        self.num_RC_label_to_result = {}
        self.num_RC_labels = []
        self.num_RC_index = 0
        self.pseudo_chisqr = list(
            map(
                lambda t: log(t.pseudo_chisqr),
                self.num_RC_results,
            )
        )

        log_F_ext: float
        statistic: float
        log_F_ext, _, statistic = (
            self.Y_evaluations if admittance else self.Z_evaluations
        )[index]

        self.log_F_ext_plot.update(
            index=2,
            log_F_ext=[log_F_ext],
            statistic=[statistic],
        )

        self.pseudo_chisqr_vs_num_RC_plot.update(
            index=1,
            num_RC=self.num_RCs,
            pseudo_chisqr=self.pseudo_chisqr,
            label=f"log Fext = {log_F_ext:.3g}",
        )

        self.refresh_wrapper(suggestion=suggestion)

    def plot_num_RC(self, label: str):
        assert self.pseudo_chisqr_and_score_plot is not None
        assert self.residuals_plot is not None
        assert self.nyquist_plot is not None
        assert self.bode_plot is not None
        assert self.impedance_plot is not None

        self.num_RC_index = self.num_RC_labels.index(label)
        dpg.set_value(self.num_RC_combo, label)

        # Clear plots
        self.residuals_plot.clear(delete=False)
        self.nyquist_plot.clear(delete=False)
        self.bode_plot.clear(delete=False)

        # Retrieve the chosen result
        result: KramersKronigResult = self.num_RC_label_to_result[label]
        dpg.set_item_user_data(self.accept_button, result)

        self.pseudo_chisqr_and_score_plot.update(num_RC=result.num_RC)
        plot: Plot
        for plot in self.method_plots.values():
            plot.update(num_RC=result.num_RC)

        freq: ndarray
        real: ndarray
        imag: ndarray
        freq, real, imag = result.get_residuals_data()
        self.residuals_plot.update(
            index=0,
            frequencies=freq,
            real=real,
            imaginary=imag,
        )

        # Data and fit
        # - Nyquist
        Z_exp: ndarray = self.data.get_impedances()
        Z_markers: ndarray = result.get_impedances()
        Z_line: ndarray = result.get_impedances(
            num_per_decade=STATE.config.num_per_decade_in_simulated_lines
        )

        self.nyquist_plot.update(
            index=0,
            impedances=Z_exp,
        )
        self.nyquist_plot.update(
            index=1,
            impedances=Z_line,
        )
        self.nyquist_plot.update(
            index=2,
            impedances=Z_markers,
        )

        # - Bode
        freq_exp: ndarray = self.data.get_frequencies()
        freq_markers: ndarray = result.get_frequencies()
        freq_line: ndarray = result.get_frequencies(
            num_per_decade=STATE.config.num_per_decade_in_simulated_lines
        )
        self.bode_plot.update(
            index=0,
            frequencies=freq_exp,
            impedances=Z_exp,
        )
        self.bode_plot.update(
            index=1,
            frequencies=freq_line,
            impedances=Z_line,
        )
        self.bode_plot.update(
            index=2,
            frequencies=freq_markers,
            impedances=Z_markers,
        )

        # - Impedance
        self.impedance_plot.update(
            index=0,
            frequencies=freq_exp,
            impedances=Z_exp,
        )
        self.impedance_plot.update(
            index=1,
            frequencies=freq_line,
            impedances=Z_line,
        )
        self.impedance_plot.update(
            index=2,
            frequencies=freq_markers,
            impedances=Z_markers,
        )

        dpg.split_frame()
        self.residuals_plot.queue_limits_adjustment()

        if dpg.get_value(self.adjust_limits_checkbox) is False:
            return

        self.nyquist_plot.queue_limits_adjustment()
        self.bode_plot.queue_limits_adjustment()
        self.impedance_plot.queue_limits_adjustment()

    def toggle_plot_admittance(self, admittance: bool):
        self.nyquist_plot.set_admittance(admittance, adjust_limits=False)
        self.bode_plot.set_admittance(admittance, adjust_limits=False)
        self.impedance_plot.set_admittance(admittance, adjust_limits=False)

        dpg.split_frame(delay=33)
        for plot in (self.nyquist_plot, self.bode_plot, self.impedance_plot):
            plot.queue_limits_adjustment()
            plot.adjust_limits()

    def resize(self, width: int, height: int):
        assert self.pseudo_chisqr_and_score_plot is not None
        assert self.residuals_plot is not None
        assert self.nyquist_plot is not None
        assert self.bode_plot is not None

        x: int
        y: int
        w: int
        h: int
        x, y, w, h = calculate_window_position_dimensions()
        desired_width: int = 980
        if w > desired_width:
            x, y, w, h = calculate_window_position_dimensions(width=desired_width)
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
        height_sum: int = 0
        width = -1
        height = 200
        height_sum += height

        self.pseudo_chisqr_and_score_plot.resize(width, height)
        for plot in self.method_plots.values():
            plot.resize(width, height)

        height += 20
        self.residuals_plot.resize(width, height)
        height_sum += height

        width, height = dpg.get_item_rect_size(self.window)
        width = -1
        height = max(
            (
                200,
                height - (height_sum + 2 * 12 + 186),
            )
        )
        self.nyquist_plot.resize(width, height)
        self.bode_plot.resize(width, height)
        self.impedance_plot.resize(width, height)

        if hasattr(self, "representation_3d_plots") and len(self.representation_3d_plots) > 0:
            while self.representation_3d_plots_resize_timers:
                self.representation_3d_plots_resize_timers.pop(0).cancel()

            t: Timer = Timer(1.0, self._refresh_3d_plot)
            self.representation_3d_plots_resize_timers.append(t)
            t.start()

    def close(self):
        STATE.kramers_kronig_suggestion_settings = self.latest_settings
        
        dpg.hide_item(self.window)
        
        if len(self.representation_3d_plots) > 0:
            while self.representation_3d_plots_resize_timers:
                self.representation_3d_plots_resize_timers.pop(0).cancel()

            dpg.delete_item(self.texture_registry)

        dpg.delete_item(self.window)
        self.keybinding_handler.delete()

        signals.emit(Signal.UNBLOCK_KEYBINDINGS)
        signals.unregister(Signal.VIEWPORT_RESIZED, self.resize)

    def accept(self, result: KramersKronigResult):
        settings: dict = result.settings.to_dict()
        settings["suggestion_settings"] = self.latest_settings.to_dict()
        result.settings = KramersKronigSettings.from_dict(settings)

        self.callback(self.data, result)
        self.close()
