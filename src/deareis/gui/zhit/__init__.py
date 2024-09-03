# DearEIS is licensed under the GPLv3 or later (https://www.gnu.org/licenses/gpl-3.0.html).
# Copyright 2024 DearEIS developers
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

from typing import (
    Callable,
    Dict,
    List,
    Optional,
    Tuple,
)
from numpy import (
    array,
    allclose,
    complex128,
    log10 as log,
    ndarray,
)
from pyimpspec import ComplexResiduals
from pyimpspec.analysis.utility import _calculate_residuals
import dearpygui.dearpygui as dpg
from deareis.signals import Signal
import deareis.signals as signals
import deareis.tooltips as tooltips
from deareis.tooltips import (
    attach_tooltip,
    update_tooltip,
)
from deareis.enums import (
    Context,
    ZHITInterpolation,
    ZHITSmoothing,
    ZHITRepresentation,
    ZHITWindow,
    label_to_zhit_interpolation,
    label_to_zhit_representation,
    label_to_zhit_smoothing,
    label_to_zhit_window,
    value_to_zhit_interpolation,
    value_to_zhit_smoothing,
    value_to_zhit_window,
    zhit_interpolation_to_label,
    zhit_representation_to_label,
    zhit_smoothing_to_label,
    zhit_window_to_label,
)
from deareis.data import (
    DataSet,
    ZHITResult,
    ZHITSettings,
)
import deareis.themes as themes
from deareis.gui.plots import (
    Bode,
    Impedance,
    Nyquist,
    Plot,
    Residuals,
)
from deareis.gui.shared import (
    DataSetsCombo,
    ResultsCombo,
)
from deareis.utility import pad_tab_labels
from deareis.gui.widgets.combo import Combo
from deareis.typing.helpers import Tag


class SettingsMenu:
    def __init__(
        self,
        default_settings: ZHITSettings,
        label_pad: int,
    ):
        with dpg.group(horizontal=True):
            dpg.add_text("Smoothing".rjust(label_pad))
            attach_tooltip(tooltips.zhit.smoothing)

            smoothing_items: List[str] = list(label_to_zhit_smoothing.keys())
            self.smoothing_combo: Combo = Combo(
                items=smoothing_items,
                default_value=zhit_smoothing_to_label[default_settings.smoothing],
                callback=lambda s, a, u: self.update_settings(),
                user_data=label_to_zhit_smoothing,
                width=-1,
            )

        with dpg.group(horizontal=True):
            dpg.add_text("Number of points".rjust(label_pad))
            attach_tooltip(tooltips.zhit.num_points)

            self.num_points_input: Tag = dpg.generate_uuid()
            dpg.add_input_int(
                default_value=default_settings.num_points,
                min_value=2,
                min_clamped=True,
                step=0,
                on_enter=True,
                width=-1,
                tag=self.num_points_input,
            )

        with dpg.group(horizontal=True):
            dpg.add_text("Polynomial order".rjust(label_pad))
            attach_tooltip(tooltips.zhit.polynomial_order)

            self.polynomial_order_input: Tag = dpg.generate_uuid()
            dpg.add_input_int(
                default_value=default_settings.polynomial_order,
                min_value=1,
                min_clamped=True,
                step=0,
                on_enter=True,
                width=-1,
                tag=self.polynomial_order_input,
            )

        with dpg.group(horizontal=True):
            dpg.add_text("Number of iterations".rjust(label_pad))
            attach_tooltip(tooltips.zhit.num_iterations)

            self.num_iterations_input: Tag = dpg.generate_uuid()
            dpg.add_input_int(
                default_value=default_settings.num_iterations,
                min_value=1,
                min_clamped=True,
                step=0,
                on_enter=True,
                width=-1,
                tag=self.num_iterations_input,
            )

        with dpg.group(horizontal=True):
            dpg.add_text("Interpolation".rjust(label_pad))
            attach_tooltip(tooltips.zhit.interpolation)

            interpolation_items: List[str] = list(label_to_zhit_interpolation.keys())
            self.interpolation_combo: Combo = Combo(
                items=interpolation_items,
                default_value=zhit_interpolation_to_label[
                    default_settings.interpolation
                ],
                user_data=label_to_zhit_interpolation,
                width=-1,
            )

        with dpg.group(horizontal=True):
            dpg.add_text("Window".rjust(label_pad))
            attach_tooltip(tooltips.zhit.window)

            window_items: List[str] = list(label_to_zhit_window.keys())
            self.window_combo: Combo = Combo(
                items=window_items,
                default_value=zhit_window_to_label[default_settings.window],
                user_data=label_to_zhit_window,
                width=-1,
            )

        with dpg.group(horizontal=True):
            dpg.add_text("Window center".rjust(label_pad))
            attach_tooltip(tooltips.zhit.window_center)

            self.window_center_input: Tag = dpg.generate_uuid()
            dpg.add_input_float(
                default_value=default_settings.window_center,
                step=0.0,
                format="%.3g",
                on_enter=True,
                width=-1,
                tag=self.window_center_input,
            )

        with dpg.group(horizontal=True):
            dpg.add_text("Window width".rjust(label_pad))
            attach_tooltip(tooltips.zhit.window_width)

            self.window_width_input: Tag = dpg.generate_uuid()
            dpg.add_input_float(
                default_value=default_settings.window_width,
                min_value=1e-12,
                min_clamped=True,
                step=0.0,
                format="%.3g",
                on_enter=True,
                width=-1,
                tag=self.window_width_input,
            )

        with dpg.group(horizontal=True):
            dpg.add_text("Representation".rjust(label_pad))
            attach_tooltip(tooltips.zhit.representation)

            self.representation_combo: Combo = Combo(
                items=list(label_to_zhit_representation.keys()),
                default_value=zhit_representation_to_label[default_settings.representation],
                user_data=label_to_zhit_representation,
                width=-1,
            )

        self.set_settings(default_settings)

    def update_settings(self, settings: Optional[ZHITSettings] = None):
        if settings is None:
            settings = self.get_settings()

        if settings.smoothing == ZHITSmoothing.NONE:
            dpg.disable_item(self.num_points_input)
        else:
            dpg.enable_item(self.num_points_input)

        if settings.smoothing == ZHITSmoothing.AUTO:
            dpg.enable_item(self.polynomial_order_input)
            dpg.enable_item(self.num_iterations_input)
        elif settings.smoothing == ZHITSmoothing.NONE:
            dpg.disable_item(self.polynomial_order_input)
            dpg.disable_item(self.num_iterations_input)
        elif settings.smoothing == ZHITSmoothing.LOWESS:
            dpg.disable_item(self.polynomial_order_input)
            dpg.enable_item(self.num_iterations_input)
        elif settings.smoothing in (
            ZHITSmoothing.SAVGOL,
            ZHITSmoothing.WHITHEND,
            ZHITSmoothing.MODSINC,
        ):
            dpg.enable_item(self.polynomial_order_input)
            dpg.disable_item(self.num_iterations_input)
        else:
            raise NotImplementedError(
                f"Unsupported smoothing type: {settings.smoothing}"
            )

    def get_settings(self) -> ZHITSettings:
        smoothing: ZHITSmoothing = self.smoothing_combo.get_value()
        num_points: int = dpg.get_value(self.num_points_input)
        polynomial_order: int = dpg.get_value(self.polynomial_order_input)
        num_iterations: int = dpg.get_value(self.num_iterations_input)
        interpolation: ZHITInterpolation = self.interpolation_combo.get_value()
        window: ZHITWindow = self.window_combo.get_value()
        window_center: float = dpg.get_value(self.window_center_input)
        window_width: float = dpg.get_value(self.window_width_input)
        representation: ZHITRepresentation = self.representation_combo.get_value()

        return ZHITSettings(
            smoothing=smoothing,
            num_points=num_points,
            polynomial_order=polynomial_order,
            num_iterations=num_iterations,
            interpolation=interpolation,
            window=window,
            window_center=window_center,
            window_width=window_width,
            representation=representation,
        )

    def set_settings(self, settings: ZHITSettings):
        assert isinstance(settings, ZHITSettings), settings
        self.smoothing_combo.set_value(settings.smoothing)
        if settings.num_points > 1:
            dpg.set_value(self.num_points_input, settings.num_points)

        if 0 < settings.polynomial_order < settings.num_points:
            dpg.set_value(self.polynomial_order_input, settings.polynomial_order)

        if settings.num_iterations > 0:
            dpg.set_value(self.num_iterations_input, settings.num_iterations)

        self.interpolation_combo.set_value(settings.interpolation)
        self.window_combo.set_value(settings.window)
        dpg.set_value(self.window_center_input, settings.window_center)
        dpg.set_value(self.window_width_input, settings.window_width)
        self.representation_combo.set_value(settings.representation)

        self.update_settings(settings)

    def has_active_input(self) -> bool:
        # TODO
        return False


class ZHITResultsCombo(ResultsCombo):
    def selection_callback(self, sender: int, app_data: str, user_data: tuple):
        signals.emit(
            Signal.SELECT_ZHIT_RESULT,
            zhit=user_data[0].get(app_data),
            data=user_data[1],
        )

    def adjust_label(self, old: str, longest: int) -> str:
        return old


# TODO: Move to separate file and re-use in other tabs?
class StatisticsTable:
    def __init__(self):
        label_pad: int = 23
        self._header: Tag = dpg.generate_uuid()
        with dpg.collapsing_header(label=" Statistics", leaf=True, tag=self._header):
            self._table: Tag = dpg.generate_uuid()
            with dpg.table(
                borders_outerV=True,
                borders_outerH=True,
                borders_innerV=True,
                borders_innerH=True,
                scrollY=True,
                freeze_rows=1,
                height=18 + 23 * 4,
                tag=self._table,
            ):
                dpg.add_table_column(
                    label="Label".rjust(label_pad),
                    width_fixed=True,
                )
                dpg.add_table_column(
                    label="Value",
                    width_fixed=True,
                )
                label: str
                tooltip: str
                for label, tooltip in [
                    (
                        "log X² (pseudo)",
                        tooltips.fitting.pseudo_chisqr,
                    ),
                    (
                        "Smoothing",
                        tooltips.zhit.smoothing,
                    ),
                    (
                        "Interpolation",
                        tooltips.zhit.interpolation,
                    ),
                    (
                        "Window",
                        tooltips.zhit.window,
                    ),
                ]:
                    with dpg.table_row():
                        dpg.add_text(label.rjust(label_pad))
                        attach_tooltip(tooltip)

                        tooltip_tag: Tag = dpg.generate_uuid()
                        dpg.add_text("", user_data=tooltip_tag)
                        attach_tooltip("", tag=tooltip_tag)

    def clear(self, hide: bool):
        if hide:
            dpg.hide_item(self._header)
        row: int
        for row in dpg.get_item_children(self._table, slot=1):
            tag: Tag = dpg.get_item_children(row, slot=1)[2]
            dpg.set_value(tag, "")
            dpg.hide_item(dpg.get_item_parent(dpg.get_item_user_data(tag)))

    def populate(self, zhit: ZHITResult):
        dpg.show_item(self._header)
        cells: List[int] = []
        row: int
        for row in dpg.get_item_children(self._table, slot=1):
            cells.append(dpg.get_item_children(row, slot=1)[2])
        assert len(cells) == 4, cells
        tag: int
        value: str
        for tag, value in [
            (
                cells[0],
                f"{log(zhit.pseudo_chisqr):.3f}",
            ),
            (
                cells[1],
                zhit_smoothing_to_label.get(
                    value_to_zhit_smoothing.get(
                        zhit.smoothing,
                        zhit.smoothing,
                    ),
                    zhit.smoothing,
                ),
            ),
            (
                cells[2],
                zhit_interpolation_to_label.get(
                    value_to_zhit_interpolation.get(
                        zhit.interpolation,
                        zhit.interpolation,
                    ),
                    zhit.interpolation,
                ),
            ),
            (
                cells[3],
                zhit_window_to_label.get(
                    value_to_zhit_window.get(
                        zhit.window,
                        zhit.window,
                    ),
                    zhit.window,
                ),
            ),
        ]:
            dpg.set_value(tag, value)
            update_tooltip(dpg.get_item_user_data(tag), value)
            dpg.show_item(dpg.get_item_parent(dpg.get_item_user_data(tag)))
        dpg.set_item_height(self._table, 18 + 23 * len(cells))


# TODO: Move to separate file and re-use in other tabs?
class SettingsTable:
    def __init__(self):
        label_pad: int = 23
        self._header: Tag = dpg.generate_uuid()
        with dpg.collapsing_header(label=" Settings", leaf=True, tag=self._header):
            self._table: Tag = dpg.generate_uuid()
            with dpg.table(
                borders_outerV=True,
                borders_outerH=True,
                borders_innerV=True,
                borders_innerH=True,
                scrollY=True,
                freeze_rows=1,
                height=18 + 23,
                tag=self._table,
            ):
                dpg.add_table_column(
                    label="Label".rjust(label_pad),
                    width_fixed=True,
                )
                dpg.add_table_column(
                    label="Value",
                    width_fixed=True,
                )
                label: str
                for label in [
                    "Smoothing",
                    "Number of points",
                    "Polynomial order",
                    "Number of iterations",
                    "Interpolation",
                    "Window",
                    "Center",
                    "Width",
                    "Representation",
                ]:
                    with dpg.table_row():
                        dpg.add_text(label.rjust(label_pad))
                        tooltip_tag: Tag = dpg.generate_uuid()
                        dpg.add_text("", user_data=tooltip_tag)
                        attach_tooltip("", tag=tooltip_tag)

            dpg.add_spacer(height=8)
            with dpg.group(horizontal=True):
                self._apply_settings_button: Tag = dpg.generate_uuid()
                dpg.add_button(
                    label="Apply settings",
                    callback=lambda s, a, u: signals.emit(
                        Signal.APPLY_ZHIT_SETTINGS,
                        **u,
                    ),
                    tag=self._apply_settings_button,
                    width=154,
                )
                attach_tooltip(tooltips.general.apply_settings)

                self._apply_mask_button: Tag = dpg.generate_uuid()
                dpg.add_button(
                    label="Apply mask",
                    callback=lambda s, a, u: signals.emit(
                        Signal.APPLY_DATA_SET_MASK,
                        **u,
                    ),
                    tag=self._apply_mask_button,
                    width=-1,
                )
                attach_tooltip(tooltips.general.apply_mask)

            with dpg.group(horizontal=True):
                self._load_as_data_button: Tag = dpg.generate_uuid()
                dpg.add_button(
                    label="Load as data set",
                    callback=lambda s, a, u: signals.emit(
                        Signal.LOAD_ZHIT_AS_DATA_SET,
                        **u,
                    ),
                    tag=self._load_as_data_button,
                    width=-1,
                )
                attach_tooltip(tooltips.zhit.load_as_data_set)

    def clear(self, hide: bool):
        if hide:
            dpg.hide_item(self._header)
        row: int
        for row in dpg.get_item_children(self._table, slot=1):
            tag: Tag = dpg.get_item_children(row, slot=1)[1]
            dpg.set_value(tag, "")
            dpg.hide_item(dpg.get_item_parent(dpg.get_item_user_data(tag)))

    def populate(self, zhit: ZHITResult, data: DataSet):
        dpg.show_item(self._header)
        rows: List[int] = []
        cells: List[Tuple[int, int]] = []
        row: int
        for row in dpg.get_item_children(self._table, slot=1):
            rows.append(row)
            cells.append(dpg.get_item_children(row, slot=1))

        assert len(rows) == len(cells) == 9, (
            rows,
            cells,
        )

        tag: int
        value: str
        for row, tag, value in [
            (
                rows[0],
                cells[0][1],
                zhit_smoothing_to_label[zhit.settings.smoothing],
            ),
            (
                rows[1],
                cells[1][1],
                str(zhit.settings.num_points),
            ),
            (
                rows[2],
                cells[2][1],
                str(zhit.settings.polynomial_order),
            ),
            (
                rows[3],
                cells[3][1],
                str(zhit.settings.num_iterations),
            ),
            (
                rows[4],
                cells[4][1],
                zhit_interpolation_to_label[zhit.settings.interpolation],
            ),
            (
                rows[5],
                cells[5][1],
                zhit_window_to_label[zhit.settings.window],
            ),
            (
                rows[6],
                cells[6][1],
                f"{zhit.settings.window_center:.3f}",
            ),
            (
                rows[7],
                cells[7][1],
                f"{zhit.settings.window_width:.3f}",
            ),
            (
                rows[8],
                cells[8][1],
                zhit_representation_to_label[zhit.settings.representation],
            ),
        ]:
            dpg.set_value(tag, value.split("\n")[0])
            update_tooltip(dpg.get_item_user_data(tag), value)
            dpg.show_item(dpg.get_item_parent(dpg.get_item_user_data(tag)))

        dpg.set_item_height(self._table, 18 + 23 * len(rows))
        dpg.set_item_user_data(
            self._apply_settings_button,
            {"settings": zhit.settings},
        )
        dpg.set_item_user_data(
            self._apply_mask_button,
            {
                "data": data,
                "mask": zhit.mask,
                "zhit": zhit,
            },
        )
        dpg.set_item_user_data(
            self._load_as_data_button,
            {
                "zhit": zhit,
                "data": data,
            },
        )


class ZHITTab:
    def __init__(self, state):
        self.state = state
        self.queued_update: Optional[Callable] = None
        self.create_tab(state)

    def create_tab(self, state):
        self.tab: Tag = dpg.generate_uuid()
        label_pad: int = 24
        with dpg.tab(label="Z-HIT analysis", tag=self.tab):
            with dpg.child_window(border=False):
                with dpg.group(horizontal=True):
                    self.create_sidebar(state, label_pad)
                    self.create_plots()

    def create_sidebar(self, state, label_pad: int):
        self.sidebar_window: Tag = dpg.generate_uuid()
        self.sidebar_width: int = 350
        with dpg.child_window(
            border=False,
            width=self.sidebar_width,
            tag=self.sidebar_window,
        ):
            with dpg.child_window(width=-1, height=266):
                self.settings_menu: SettingsMenu = SettingsMenu(
                    state.config.default_zhit_settings,
                    label_pad,
                )
                with dpg.group(horizontal=True):
                    dpg.add_text("?".rjust(label_pad))
                    attach_tooltip(tooltips.zhit.preview_weights)

                    dpg.add_button(
                        label="Preview weights",
                        callback=lambda s, a, u: signals.emit(
                            Signal.PREVIEW_ZHIT_WEIGHTS,
                            settings=self.get_settings(),
                        ),
                        width=-1,
                    )
                with dpg.group(horizontal=True):
                    self.visibility_item: Tag = dpg.generate_uuid()
                    dpg.add_text(
                        "?".rjust(label_pad),
                        tag=self.visibility_item,
                    )
                    attach_tooltip(tooltips.zhit.perform)

                    self.perform_zhit_button: Tag = dpg.generate_uuid()
                    dpg.add_button(
                        label="Perform",
                        callback=lambda s, a, u: signals.emit(
                            Signal.PERFORM_ZHIT,
                            data=u,
                            settings=self.get_settings(),
                        ),
                        user_data=None,
                        width=-70,
                        tag=self.perform_zhit_button,
                    )
                    dpg.add_button(
                        label="Batch",
                        callback=lambda s, a, u: signals.emit(
                            Signal.BATCH_PERFORM_ANALYSIS,
                            settings=self.get_settings(),
                        ),
                        width=-1,
                    )
            with dpg.child_window(width=-1, height=58):
                label_pad = 8
                with dpg.group(horizontal=True):
                    self.data_sets_combo: DataSetsCombo = DataSetsCombo(
                        label="Data set".rjust(label_pad),
                        width=-60,
                    )
                with dpg.group(horizontal=True):
                    self.results_combo: ZHITResultsCombo = ZHITResultsCombo(
                        label="Result".rjust(label_pad),
                        width=-60,
                    )
                    self.delete_button: Tag = dpg.generate_uuid()
                    dpg.add_button(
                        label="Delete",
                        callback=lambda s, a, u: signals.emit(
                            Signal.DELETE_ZHIT_RESULT,
                            **u,
                        ),
                        width=-1,
                        tag=self.delete_button,
                    )
                    attach_tooltip(tooltips.zhit.delete)

            with dpg.child_window(width=-1, height=-1):
                with dpg.group(show=False):
                    self.validity_text: Tag = dpg.generate_uuid()
                    dpg.bind_item_theme(
                        dpg.add_text(
                            "",
                            wrap=self.sidebar_width - 24,
                            tag=self.validity_text,
                        ),
                        themes.result.invalid,
                    )
                    dpg.add_spacer(height=8)
                self.statistics_table: StatisticsTable = StatisticsTable()
                dpg.add_spacer(height=8)
                self.settings_table: SettingsTable = SettingsTable()

    def create_plots(self):
        self.plot_window: Tag = dpg.generate_uuid()
        with dpg.child_window(
            border=False,
            width=-1,
            height=-1,
            tag=self.plot_window,
        ):
            self.plot_tab_bar: Tag = dpg.generate_uuid()
            with dpg.tab_bar(tag=self.plot_tab_bar):
                self.create_nyquist_plot()
                bode_tab: int = self.create_bode_plot()
                self.create_impedance_plot()

            pad_tab_labels(self.plot_tab_bar)
            dpg.set_value(self.plot_tab_bar, bode_tab)
            dpg.add_spacer(height=4)
            dpg.add_separator()
            dpg.add_spacer(height=4)
            self.create_residuals_plot()

    def create_nyquist_plot(self):
        with dpg.tab(label="Nyquist"):
            self.nyquist_plot: Nyquist = Nyquist(width=-1, height=-24)
            self.nyquist_plot.plot(
                impedances=array([], dtype=complex128),
                label="Data",
                line=False,
                theme=themes.nyquist.data,
            )
            self.nyquist_plot.plot(
                impedances=array([], dtype=complex128),
                label="Fit",
                line=False,
                fit=True,
                theme=themes.nyquist.simulation,
            )
            self.nyquist_plot.plot(
                impedances=array([], dtype=complex128),
                label="Fit",
                line=True,
                fit=True,
                theme=themes.nyquist.simulation,
                show_label=False,
            )

            with dpg.group(horizontal=True):
                self.enlarge_nyquist_button: Tag = dpg.generate_uuid()
                dpg.add_button(
                    label="Enlarge plot",
                    callback=self.show_enlarged_nyquist,
                    tag=self.enlarge_nyquist_button,
                )

                dpg.add_button(
                    label="Copy as CSV",
                    callback=lambda s, a, u: signals.emit(
                        Signal.COPY_PLOT_DATA,
                        plot=self.nyquist_plot,
                        context=Context.ZHIT_TAB,
                    ),
                )
                attach_tooltip(tooltips.general.copy_plot_data_as_csv)

                self.adjust_nyquist_limits_checkbox: Tag = dpg.generate_uuid()
                dpg.add_checkbox(
                    label="Adjust limits",
                    default_value=True,
                    tag=self.adjust_nyquist_limits_checkbox,
                )
                attach_tooltip(tooltips.general.adjust_nyquist_limits)

                self.nyquist_admittance_checkbox: Tag = dpg.generate_uuid()
                dpg.add_checkbox(
                    label="Y",
                    callback=lambda s, a, u: self.toggle_plot_admittance(a),
                    tag=self.nyquist_admittance_checkbox,
                )
                attach_tooltip(tooltips.general.plot_admittance)

    def create_bode_plot(self) -> int:
        tab: int
        with dpg.tab(label="Bode") as tab:
            self.bode_plot: Bode = Bode(width=-1, height=-24)
            self.bode_plot.plot(
                frequencies=array([]),
                impedances=array([], dtype=complex128),
                labels=(
                    "Mod(data)",
                    "Phase(data)",
                ),
                line=False,
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
                line=False,
                fit=True,
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
                line=True,
                fit=True,
                themes=(
                    themes.bode.magnitude_simulation,
                    themes.bode.phase_simulation,
                ),
                show_labels=False,
            )

            with dpg.group(horizontal=True):
                self.enlarge_bode_button: Tag = dpg.generate_uuid()
                dpg.add_button(
                    label="Enlarge plot",
                    callback=self.show_enlarged_bode,
                    tag=self.enlarge_bode_button,
                )

                dpg.add_button(
                    label="Copy as CSV",
                    callback=lambda s, a, u: signals.emit(
                        Signal.COPY_PLOT_DATA,
                        plot=self.bode_plot,
                        context=Context.ZHIT_TAB,
                    ),
                )
                attach_tooltip(tooltips.general.copy_plot_data_as_csv)

                self.adjust_bode_limits_checkbox: Tag = dpg.generate_uuid()
                dpg.add_checkbox(
                    label="Adjust limits",
                    default_value=True,
                    tag=self.adjust_bode_limits_checkbox,
                )
                attach_tooltip(tooltips.general.adjust_bode_limits)

                self.bode_admittance_checkbox: Tag = dpg.generate_uuid()
                dpg.add_checkbox(
                    label="Y",
                    callback=lambda s, a, u: self.toggle_plot_admittance(a),
                    tag=self.bode_admittance_checkbox,
                )
                attach_tooltip(tooltips.general.plot_admittance)

        return tab

    def create_impedance_plot(self):
        with dpg.tab(label="Real & imag."):
            self.impedance_plot: Impedance = Impedance(
                width=-1,
                height=-24,
            )
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
                line=False,
                fit=True,
                themes=(
                    themes.impedance.real_simulation,
                    themes.impedance.imaginary_simulation,
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

            with dpg.group(horizontal=True):
                self.enlarge_impedance_button: Tag = dpg.generate_uuid()
                dpg.add_button(
                    label="Enlarge plot",
                    callback=self.show_enlarged_impedance,
                    tag=self.enlarge_impedance_button,
                )

                dpg.add_button(
                    label="Copy as CSV",
                    callback=lambda s, a, u: signals.emit(
                        Signal.COPY_PLOT_DATA,
                        plot=self.impedance_plot,
                        context=Context.ZHIT_TAB,
                    ),
                )
                attach_tooltip(tooltips.general.copy_plot_data_as_csv)

                self.adjust_impedance_limits_checkbox: Tag = dpg.generate_uuid()
                dpg.add_checkbox(
                    label="Adjust limits",
                    default_value=True,
                    tag=self.adjust_impedance_limits_checkbox,
                )
                attach_tooltip(tooltips.general.adjust_impedance_limits)

                self.impedance_admittance_checkbox: Tag = dpg.generate_uuid()
                dpg.add_checkbox(
                    label="Y",
                    callback=lambda s, a, u: self.toggle_plot_admittance(a),
                    tag=self.impedance_admittance_checkbox,
                )
                attach_tooltip(tooltips.general.plot_admittance)

    def create_residuals_plot(self):
        self.residuals_plot_height: int = 300
        self.residuals_plot: Residuals = Residuals(
            width=-1,
            height=self.residuals_plot_height,
        )
        self.residuals_plot.plot(
            frequencies=array([]),
            real=array([]),
            imaginary=array([]),
        )

        with dpg.group(horizontal=True):
            self.enlarge_residuals_button: Tag = dpg.generate_uuid()
            self.adjust_residuals_limits_checkbox: Tag = dpg.generate_uuid()
            dpg.add_button(
                label="Enlarge plot",
                callback=self.show_enlarged_residuals,
                tag=self.enlarge_residuals_button,
            )
            dpg.add_button(
                label="Copy as CSV",
                callback=lambda s, a, u: signals.emit(
                    Signal.COPY_PLOT_DATA,
                    plot=self.residuals_plot,
                    context=Context.ZHIT_TAB,
                ),
            )
            attach_tooltip(tooltips.general.copy_plot_data_as_csv)

            dpg.add_checkbox(
                label="Adjust limits",
                default_value=True,
                tag=self.adjust_residuals_limits_checkbox,
            )
            attach_tooltip(tooltips.general.adjust_residuals_limits)

    def is_visible(self) -> bool:
        return dpg.is_item_visible(self.visibility_item)

    def toggle_plot_admittance(self, admittance: bool):
        tag: int
        for tag in (
            self.nyquist_admittance_checkbox,
            self.bode_admittance_checkbox,
            self.impedance_admittance_checkbox,
        ):
            dpg.set_value(tag, admittance)

        self.nyquist_plot.set_admittance(admittance)
        self.bode_plot.set_admittance(admittance)
        self.impedance_plot.set_admittance(admittance)

    def resize(self, width: int, height: int):
        assert type(width) is int and width > 0
        assert type(height) is int and height > 0
        if not self.is_visible():
            return

        width, height = dpg.get_item_rect_size(self.plot_window)
        tmp: int = round(height / 2) - 24 * 2
        if tmp > 300:
            self.residuals_plot.resize(-1, 300)
            height -= 348 + 24 * 2 - 2
        else:
            height = tmp
            self.residuals_plot.resize(-1, height)

        plots: List[Plot] = [
            self.nyquist_plot,
            self.bode_plot,
            self.impedance_plot,
        ]
        for plot in plots:
            plot.resize(-1, height)

    def clear(self, hide: bool = True):
        self.data_sets_combo.clear()
        self.results_combo.clear()
        self.statistics_table.clear(hide=hide)
        self.settings_table.clear(hide=hide)
        dpg.set_item_user_data(self.perform_zhit_button, None)
        self.nyquist_plot.clear(delete=False)
        self.bode_plot.clear(delete=False)
        self.impedance_plot.clear(delete=False)
        self.residuals_plot.clear(delete=False)

    def get_settings(self) -> ZHITSettings:
        return self.settings_menu.get_settings()

    def set_settings(self, settings: ZHITSettings):
        self.settings_menu.set_settings(settings)

    def populate_data_sets(self, labels: List[str], lookup: Dict[str, DataSet]):
        assert type(labels) is list, labels
        assert type(lookup) is dict, lookup
        self.data_sets_combo.populate(labels, lookup)

    def populate_zhits(self, lookup: Dict[str, ZHITResult], data: Optional[DataSet]):
        assert type(lookup) is dict, lookup
        assert type(data) is DataSet or data is None, data
        self.results_combo.populate(lookup, data)
        dpg.hide_item(dpg.get_item_parent(self.validity_text))
        if data is not None and self.results_combo.labels:
            signals.emit(
                Signal.SELECT_ZHIT_RESULT,
                zhit=self.results_combo.get(),
                data=data,
            )
        else:
            self.statistics_table.clear(hide=True)
            self.settings_table.clear(hide=True)
            self.select_data_set(data)

    def get_next_data_set(self) -> Optional[DataSet]:
        return self.data_sets_combo.get_next()

    def get_previous_data_set(self) -> Optional[DataSet]:
        return self.data_sets_combo.get_previous()

    def get_next_result(self) -> Optional[ZHITResult]:
        return self.results_combo.get_next()

    def get_previous_result(self) -> Optional[ZHITResult]:
        return self.results_combo.get_previous()

    def select_data_set(self, data: Optional[DataSet]):
        assert type(data) is DataSet or data is None, data
        self.clear(hide=data is None)
        dpg.set_item_user_data(self.perform_zhit_button, data)
        if data is None:
            return

        self.data_sets_combo.set(data.get_label())
        Z: ndarray = data.get_impedances()
        self.nyquist_plot.update(
            index=0,
            impedances=Z,
        )

        freq: ndarray = data.get_frequencies()
        self.bode_plot.update(
            index=0,
            frequencies=freq,
            impedances=Z,
        )
        self.impedance_plot.update(
            index=0,
            frequencies=freq,
            impedances=Z,
        )

    def assert_zhit_up_to_date(self, zhit: ZHITResult, data: DataSet):
        # Check if the number of unmasked points is the same
        Z_exp: ndarray = data.get_impedances()
        Z_zhit: ndarray = zhit.get_impedances()
        assert Z_exp.shape == Z_zhit.shape, "The number of data points differ!"

        # Check if the masks are the same
        mask_exp: Dict[int, bool] = data.get_mask()
        mask_zhit: Dict[int, bool] = {
            k: zhit.mask.get(k, mask_exp.get(k, False)) for k in zhit.mask
        }
        num_masked_exp: int = list(data.get_mask().values()).count(True)
        num_masked_zhit: int = list(zhit.mask.values()).count(True)
        assert num_masked_exp == num_masked_zhit, "The masks are different sizes!"
        i: int
        for i in mask_zhit.keys():
            assert (
                i in mask_exp
            ), f"The data set does not have a point at index {i + 1}!"
            assert (
                mask_exp[i] == mask_zhit[i]
            ), f"The data set's mask differs at index {i + 1}!"

        # Check if the frequencies and impedances are the same
        assert allclose(
            zhit.get_frequencies(),
            data.get_frequencies(),
        ), "The frequencies differ!"

        residuals: ComplexResiduals = _calculate_residuals(Z_exp=Z_exp, Z_fit=Z_zhit)
        assert allclose(zhit.residuals.real, residuals.real) and allclose(
            zhit.residuals.imag, residuals.imag
        ), "The data set's impedances differ from what they were when the analysis was performed!"

    def select_zhit_result(self, zhit: Optional[ZHITResult], data: Optional[DataSet]):
        assert type(zhit) is ZHITResult or zhit is None, zhit
        assert type(data) is DataSet or data is None, data
        dpg.set_item_user_data(
            self.delete_button,
            {
                "zhit": zhit,
                "data": data,
            },
        )
        if not self.is_visible():
            self.queued_update = lambda: self.select_zhit_result(zhit, data)
            return

        self.queued_update = None
        self.select_data_set(data)
        if zhit is None or data is None:
            if dpg.get_value(self.adjust_nyquist_limits_checkbox):
                self.nyquist_plot.queue_limits_adjustment()

            if dpg.get_value(self.adjust_bode_limits_checkbox):
                self.bode_plot.queue_limits_adjustment()

            if dpg.get_value(self.adjust_impedance_limits_checkbox):
                self.impedance_plot.queue_limits_adjustment()

            if dpg.get_value(self.adjust_residuals_limits_checkbox):
                self.residuals_plot.queue_limits_adjustment()

            return

        self.results_combo.set(zhit.get_label())

        message: str
        try:
            self.assert_zhit_up_to_date(zhit, data)
            dpg.hide_item(dpg.get_item_parent(self.validity_text))
        except AssertionError as message:
            dpg.set_value(
                self.validity_text,
                f"Z-HIT result is not valid for the current state of the data set!\n\n{message}",
            )
            dpg.show_item(dpg.get_item_parent(self.validity_text))

        self.statistics_table.populate(zhit)
        self.settings_table.populate(
            zhit,
            data,
        )

        Z: ndarray = zhit.get_impedances()
        i: int
        for i in range(1, 3):
            self.nyquist_plot.update(
                index=i,
                impedances=Z,
            )

        freq: ndarray = zhit.get_frequencies()
        for i in range(1, 3):
            self.bode_plot.update(
                index=i,
                frequencies=freq,
                impedances=Z,
            )
            self.impedance_plot.update(
                index=i,
                frequencies=freq,
                impedances=Z,
            )

        freq, real, imag = zhit.get_residuals_data()
        self.residuals_plot.update(
            index=0,
            frequencies=freq,
            real=real,
            imaginary=imag,
        )

        if dpg.get_value(self.adjust_nyquist_limits_checkbox):
            self.nyquist_plot.queue_limits_adjustment()

        if dpg.get_value(self.adjust_bode_limits_checkbox):
            self.bode_plot.queue_limits_adjustment()

        if dpg.get_value(self.adjust_impedance_limits_checkbox):
            self.impedance_plot.queue_limits_adjustment()

        if dpg.get_value(self.adjust_residuals_limits_checkbox):
            self.residuals_plot.queue_limits_adjustment()

    def next_plot_tab(self):
        tabs: List[Tag] = dpg.get_item_children(self.plot_tab_bar, slot=1)
        index: int = tabs.index(dpg.get_value(self.plot_tab_bar)) + 1
        dpg.set_value(self.plot_tab_bar, tabs[index % len(tabs)])

    def previous_plot_tab(self):
        tabs: List[Tag] = dpg.get_item_children(self.plot_tab_bar, slot=1)
        index: int = tabs.index(dpg.get_value(self.plot_tab_bar)) - 1
        dpg.set_value(self.plot_tab_bar, tabs[index % len(tabs)])

    def show_enlarged_nyquist(self):
        signals.emit(
            Signal.SHOW_ENLARGED_PLOT,
            plot=self.nyquist_plot,
            adjust_limits=dpg.get_value(self.adjust_nyquist_limits_checkbox),
            admittance=dpg.get_value(self.nyquist_admittance_checkbox),
        )

    def show_enlarged_bode(self):
        signals.emit(
            Signal.SHOW_ENLARGED_PLOT,
            plot=self.bode_plot,
            adjust_limits=dpg.get_value(self.adjust_bode_limits_checkbox),
            admittance=dpg.get_value(self.bode_admittance_checkbox),
        )

    def show_enlarged_impedance(self):
        signals.emit(
            Signal.SHOW_ENLARGED_PLOT,
            plot=self.impedance_plot,
            adjust_limits=dpg.get_value(self.adjust_impedance_limits_checkbox),
            admittance=dpg.get_value(self.impedance_admittance_checkbox),
        )

    def show_enlarged_residuals(self):
        signals.emit(
            Signal.SHOW_ENLARGED_PLOT,
            plot=self.residuals_plot,
            adjust_limits=dpg.get_value(self.adjust_residuals_limits_checkbox),
        )

    def has_active_input(self) -> bool:
        return self.settings_menu.has_active_input()
