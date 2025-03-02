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

from typing import (
    Callable,
    Dict,
    List,
    Optional,
)
from numpy import (
    allclose,
    ndarray,
)
import dearpygui.dearpygui as dpg
from deareis.gui.plots import (
    BodeMagnitude,
    BodePhase,
    Nyquist,
)
from deareis.tooltips import attach_tooltip
from deareis.themes import (
    PLOT_MARKERS,
    VIBRANT_COLORS,
    create_plot_series_theme,
)
import deareis.themes as themes
from deareis.utility import (
    calculate_window_position_dimensions,
    is_filtered_item_visible,
    pad_tab_labels,
)
from deareis.signals import Signal
import deareis.signals as signals
from deareis.data import DataSet
from deareis.state import STATE
from deareis.enums import Action
from deareis.keybindings import (
    Keybinding,
    TemporaryKeybindingHandler,
)
import deareis.tooltips as tooltips
from deareis.typing.helpers import Tag


class AverageDataSets:
    def __init__(self, data_sets: List[DataSet], callback: Callable, admittance: bool):
        assert type(data_sets) is list and all(
            map(lambda _: type(_) is DataSet, data_sets)
        )
        self.data_sets: List[DataSet] = data_sets
        self.callback: Callable = callback
        self.plot_themes: List[int] = list(
            map(
                self.get_plot_theme,
                range(0, 12),
            )
        )
        self.final_data: Optional[DataSet] = None
        self.create_window(admittance=admittance)
        self.register_keybindings()
        self.update_preview([])
        self.toggle_plot_admittance(admittance)

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
        callbacks[kb] = self.accept

        # Select filtered
        for kb in STATE.config.keybindings:
            if kb.action is Action.SELECT_ALL_PLOT_SERIES:
                break
        else:
            kb = Keybinding(
                key=dpg.mvKey_A,
                mod_alt=True,
                mod_ctrl=False,
                mod_shift=False,
                action=Action.SELECT_ALL_PLOT_SERIES,
            )
        callbacks[kb] = lambda: self.select_all(flag=True)

        # Unselect filtered
        for kb in STATE.config.keybindings:
            if kb.action is Action.UNSELECT_ALL_PLOT_SERIES:
                break
        else:
            kb = Keybinding(
                key=dpg.mvKey_A,
                mod_alt=True,
                mod_ctrl=False,
                mod_shift=True,
                action=Action.UNSELECT_ALL_PLOT_SERIES,
            )
        callbacks[kb] = lambda: self.select_all(flag=False)

        # Previous plot tab
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
        callbacks[kb] = lambda: self.cycle_plot_tab(step=-1)

        # Next plot tab
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
        callbacks[kb] = lambda: self.cycle_plot_tab(step=1)

        # Focus filter input
        kb = Keybinding(
            key=dpg.mvKey_F,
            mod_alt=False,
            mod_ctrl=True,
            mod_shift=False,
            action=Action.CUSTOM,
        )
        callbacks[kb] = self.focus_filter

        # Create the handler
        self.keybinding_handler: TemporaryKeybindingHandler = (
            TemporaryKeybindingHandler(callbacks=callbacks)
        )

    def create_window(self, admittance: bool):
        x: int
        y: int
        w: int
        h: int
        x, y, w, h = calculate_window_position_dimensions()
        self.window: Tag = dpg.generate_uuid()
        with dpg.window(
            label="Average of multiple data sets",
            modal=True,
            pos=(x, y),
            width=w,
            height=h,
            tag=self.window,
            on_close=self.close,
        ):
            with dpg.group(horizontal=True):
                with dpg.group():
                    with dpg.child_window(border=False, width=300, height=-1):
                        self.filter_input: Tag = dpg.generate_uuid()
                        with dpg.group(horizontal=True):
                            dpg.add_input_text(
                                hint="Filter...",
                                width=-1,
                                tag=self.filter_input,
                                callback=lambda s, a, u: self.filter_data_sets(a),
                            )

                        self.data_set_table: Tag = dpg.generate_uuid()
                        with dpg.table(
                            borders_outerV=True,
                            borders_outerH=True,
                            borders_innerV=True,
                            borders_innerH=True,
                            scrollY=True,
                            freeze_rows=1,
                            width=-1,
                            height=-48,
                            tag=self.data_set_table,
                        ):
                            dpg.add_table_column(label="", width_fixed=True)
                            dpg.add_table_column(label="Label", width_fixed=True)

                            data: DataSet
                            for data in self.data_sets:
                                with dpg.table_row(filter_key=data.get_label().lower()):
                                    dpg.add_checkbox(
                                        callback=lambda: self.update_preview([])
                                    )
                                    label: str = data.get_label()
                                    dpg.add_text(label)
                                    attach_tooltip(label)

                        with dpg.group(horizontal=True):
                            dpg.add_text("Label")
                            attach_tooltip(
                                "The label for the new data set that will be generated."
                            )

                            self.label_input: Tag = dpg.generate_uuid()
                            self.final_data_series: int = -1
                            dpg.add_input_text(
                                hint="REQUIRED",
                                default_value="Average",
                                width=-1,
                                tag=self.label_input,
                                callback=lambda s, a, u: self.update_label(a),
                            )

                        with dpg.group(horizontal=True):
                            dpg.add_button(
                                label=" Accept ",
                                callback=self.accept,
                            )
                            dpg.add_button(
                                label="Select all",
                                callback=lambda: self.select_all(True),
                            )
                            dpg.add_button(
                                label="Unselect all",
                                callback=lambda: self.select_all(False),
                            )

                            self.admittance_checkbox: Tag = dpg.generate_uuid()
                            dpg.add_checkbox(
                                label="Y",
                                default_value=admittance,
                                callback=lambda s, a, u: self.toggle_plot_admittance(a),
                                tag=self.admittance_checkbox,
                            )
                            attach_tooltip(tooltips.general.plot_admittance)

                with dpg.child_window(border=False, width=-1, height=-1):
                    self.plot_tab_bar: Tag = dpg.generate_uuid()
                    with dpg.tab_bar(tag=self.plot_tab_bar):
                        with dpg.tab(label="Nyquist"):
                            self.nyquist_plot: Nyquist = Nyquist(
                                width=-1,
                                height=-1,
                                legend_horizontal=False,
                                legend_outside=False,
                                legend_location=dpg.mvPlot_Location_NorthEast,
                            )

                        with dpg.tab(label="Bode - magnitude"):
                            self.magnitude_plot: BodeMagnitude = BodeMagnitude(
                                width=-1,
                                height=-1,
                                legend_horizontal=False,
                                legend_outside=False,
                                legend_location=dpg.mvPlot_Location_NorthEast,
                            )

                        with dpg.tab(label="Bode - phase"):
                            self.phase_plot: BodePhase = BodePhase(
                                width=-1,
                                height=-1,
                                legend_horizontal=False,
                                legend_outside=False,
                                legend_location=dpg.mvPlot_Location_NorthEast,
                            )

                    pad_tab_labels(self.plot_tab_bar)

    def toggle_plot_admittance(self, admittance: bool):
        self.nyquist_plot.set_admittance(admittance)
        self.magnitude_plot.set_admittance(admittance)
        self.phase_plot.set_admittance(admittance)

    def close(self):
        dpg.hide_item(self.window)
        dpg.delete_item(self.window)
        self.keybinding_handler.delete()
        signals.emit(Signal.UNBLOCK_KEYBINDINGS)

    def accept(self):
        if self.final_data is None:
            return

        label: str = dpg.get_value(self.label_input).strip()
        if label == "":
            return

        self.final_data.set_label(label)
        self.callback(self.final_data)
        self.close()

    def get_selection(self) -> List[DataSet]:
        indices: List[int] = []
        data_sets: List[DataSet] = []

        i: int
        row: int
        for i, row in enumerate(dpg.get_item_children(self.data_set_table, slot=1)):
            column: int
            for column in dpg.get_item_children(row, slot=1):
                assert dpg.get_item_type(column).endswith("Checkbox")
                if dpg.get_value(column) is True:
                    data_sets.append(self.data_sets[i])
                    indices.append(i)
                break

        if data_sets:
            frequency: ndarray = data_sets[0].get_frequencies(masked=None)
            for i, row in enumerate(dpg.get_item_children(self.data_set_table, slot=1)):
                if i in indices:
                    continue

                data: DataSet = self.data_sets[i]
                if not (
                    data.get_num_points(masked=None) == frequency.size
                    and allclose(
                        data.get_frequencies(masked=None),
                        frequency,
                        rtol=1e-3,
                    )
                ):
                    dpg.hide_item(dpg.get_item_children(row, slot=1)[0])
        else:
            for i, row in enumerate(dpg.get_item_children(self.data_set_table, slot=1)):
                dpg.show_item(dpg.get_item_children(row, slot=1)[0])

        return data_sets

    def get_plot_theme(self, index: int) -> int:
        assert type(index) is int, index
        return create_plot_series_theme(
            VIBRANT_COLORS[index % len(VIBRANT_COLORS)],
            list(PLOT_MARKERS.values())[index % len(PLOT_MARKERS)],
        )

    def update_preview(self, data_sets: List[DataSet]):
        assert type(data_sets) is list and all(
            map(lambda _: type(_) is DataSet, data_sets)
        ), data_sets
        from_empty: bool = False
        if len(self.nyquist_plot.get_series()) == 0:
            from_empty = True

        self.nyquist_plot.clear()
        self.magnitude_plot.clear()
        self.phase_plot.clear()
        selection: List[DataSet] = self.get_selection()

        i: int
        data: DataSet
        label: str
        theme: int
        Z: ndarray
        freq: ndarray
        for i, data in enumerate(selection):
            label = data.get_label()
            theme = self.plot_themes[i % 12]
            Z = data.get_impedances(masked=None)
            self.nyquist_plot.plot(
                impedances=Z,
                label=label,
                line=False,
                theme=theme,
            )
            freq = data.get_frequencies(masked=None)
            self.magnitude_plot.plot(
                frequencies=freq,
                impedances=Z,
                label=label,
                line=False,
                theme=theme,
            )
            self.phase_plot.plot(
                frequencies=freq,
                impedances=Z,
                label=label,
                line=False,
                theme=theme,
            )

        self.final_data_series = -1
        if len(selection) > 1:
            try:
                self.final_data = DataSet.average(
                    selection,
                    label=dpg.get_value(self.label_input),
                )
                assert self.final_data is not None
                label = self.final_data.get_label()
                theme = themes.nyquist.data
                Z = self.final_data.get_impedances(masked=None)
                self.final_data_series = self.nyquist_plot.plot(
                    impedances=Z,
                    label=label,
                    line=True,
                    theme=theme,
                )
                freq = self.final_data.get_frequencies(masked=None)
                self.magnitude_plot.plot(
                    frequencies=freq,
                    impedances=Z,
                    label=label,
                    line=True,
                    theme=theme,
                )
                self.phase_plot.plot(
                    frequencies=freq,
                    impedances=Z,
                    label=label,
                    line=True,
                    theme=theme,
                )
            except AssertionError:
                self.final_data = None

        if from_empty:
            self.nyquist_plot.queue_limits_adjustment()
            self.magnitude_plot.queue_limits_adjustment()
            self.phase_plot.queue_limits_adjustment()

    def update_label(self, label: str):
        assert type(label) is str, label
        if self.final_data_series < 0 or not dpg.does_item_exist(
            self.final_data_series
        ):
            return

        # TODO: Apply a theme that attracts attention when no label is provided?
        if label == "":
            pass
        else:
            pass

        dpg.set_item_label(self.final_data_series, label)

    def filter_data_sets(self, fltr: str):
        dpg.set_value(self.data_set_table, fltr)

    def select_all(self, flag: bool):
        data_sets: Dict[DataSet, int] = {}

        fltr: str = dpg.get_value(self.filter_input)
        i: int
        row: int
        for i, row in enumerate(dpg.get_item_children(self.data_set_table, slot=1)):
            if not is_filtered_item_visible(row, fltr):
                continue

            checkbox: Tag = dpg.get_item_children(row, slot=1)[0]
            if not dpg.is_item_visible(checkbox):
                continue

            if flag is True:
                data_sets[self.data_sets[i]] = checkbox
            else:
                dpg.set_value(checkbox, False)

        if flag is False:
            self.update_preview([])
            return

        frequencies: Optional[ndarray] = None
        data: DataSet
        for data, checkbox in data_sets.items():
            if frequencies is None:
                frequencies = data.get_frequencies(masked=None)
                dpg.set_value(checkbox, True)
                self.update_preview([])
            elif data.get_num_points(masked=None) == frequencies.size and allclose(
                data.get_frequencies(masked=None),
                frequencies,
                rtol=1e-3,
            ):
                dpg.set_value(checkbox, True)

        self.update_preview([])

    def focus_filter(self):
        dpg.focus_item(self.filter_input)

    def cycle_plot_tab(self, step: int):
        tabs: List[Tag] = dpg.get_item_children(self.plot_tab_bar, slot=1)
        index: int = tabs.index(dpg.get_value(self.plot_tab_bar)) + step
        dpg.set_value(self.plot_tab_bar, tabs[index % len(tabs)])
