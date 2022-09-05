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

from typing import (
    Callable,
    Dict,
    List,
    Optional,
    Tuple,
    Union,
)
import dearpygui.dearpygui as dpg
from deareis.signals import Signal
import deareis.signals as signals
from deareis.data import (
    DRTResult,
    DataSet,
    FitResult,
    PlotSettings,
    SimulationResult,
    TestResult,
)
from deareis.utility import calculate_window_position_dimensions
from deareis.tooltips import attach_tooltip
import deareis.tooltips as tooltips
from deareis.data import Project
import deareis.themes as themes
from deareis.keybindings import (
    is_alt_down,
    is_control_down,
)


class SeriesBefore:
    def __init__(
        self,
        series: Union[DataSet, TestResult, DRTResult, FitResult, SimulationResult],
        settings: PlotSettings,
        marker_lookup: Dict[int, str],
        toggle_callback: Callable,
    ):
        assert type(series) in [
            DRTResult,
            DataSet,
            FitResult,
            SimulationResult,
            TestResult,
        ], series
        assert type(settings) is PlotSettings, settings
        assert type(marker_lookup) is dict, marker_lookup
        with dpg.table_row(user_data=series.uuid):
            dpg.add_checkbox(
                default_value=True,
                callback=lambda s, a, u: toggle_callback(a, u),
                user_data=series.uuid,
            )
            attach_tooltip(tooltips.plotting.copy_appearance_toggle)
            label = settings.get_series_label(series.uuid) or series.get_label()
            dpg.add_text(label)
            attach_tooltip(
                label
                + ("" if label == series.get_label() else f"\n{series.get_label()}")
            )
            dpg.add_color_edit(
                default_value=settings.get_series_color(series.uuid),
                enabled=False,
                no_picker=True,
                alpha_preview=dpg.mvColorEdit_AlphaPreviewHalf,
                no_inputs=True,
            )
            dpg.add_text(
                marker_lookup.get(settings.get_series_marker(series.uuid), "None")
            )
            dpg.add_checkbox(
                default_value=settings.get_series_line(series.uuid),
                enabled=False,
            )


class SeriesAfter:
    def __init__(
        self,
        series,
        source,
        destination,
        copy_labels,
        copy_colors,
        copy_markers,
        copy_lines,
        marker_lookup,
        parent,
    ):
        with dpg.table_row(parent=parent, user_data=series.uuid):
            label: str = (
                source.get_series_label(series.uuid)
                if copy_labels
                else destination.get_series_label(series.uuid)
            )
            dpg.add_text(
                label or series.get_label(),
                user_data=label,
            )
            attach_tooltip(
                label
                or series.get_label()
                + (
                    ""
                    if (label or series.get_label()) == series.get_label()
                    else f"\n{series.get_label()}"
                )
            )
            color: List[float] = (
                source.get_series_color(series.uuid)
                if copy_colors
                else destination.get_series_color(series.uuid)
            )
            dpg.add_color_edit(
                default_value=color,
                enabled=False,
                no_picker=True,
                alpha_preview=dpg.mvColorEdit_AlphaPreviewHalf,
                no_inputs=True,
                user_data=color,
            )
            marker: int = (
                source.get_series_marker(series.uuid)
                if copy_markers
                else destination.get_series_marker(series.uuid)
            )
            dpg.add_text(
                marker_lookup.get(marker, "None"),
                user_data=marker,
            )
            show_line: bool = (
                source.get_series_line(series.uuid)
                if copy_lines
                else destination.get_series_line(series.uuid)
            )
            dpg.add_checkbox(
                default_value=show_line,
                enabled=False,
                user_data=show_line,
            )


class CopyPlotAppearance:
    def __init__(self, settings: PlotSettings, project: Project):
        assert type(settings) is PlotSettings, settings
        assert type(project) is Project, project
        self.settings: PlotSettings = settings
        self.marker_lookup: Dict[int, str] = {
            v: k for k, v in themes.PLOT_MARKERS.items()
        }
        self.plot_lookup: Dict[str, PlotSettings] = {
            _.get_label(): _ for _ in project.get_plots() if _ != settings
        }
        self.labels: List[str] = list(sorted(self.plot_lookup.keys()))
        self.series_checkboxes: Dict[str, bool] = {
            _: True for _ in settings.series_order
        }
        self.data_sets: List[DataSet] = project.get_data_sets()
        self.tests: Dict[str, List[TestResult]] = project.get_all_tests()
        self.drts: Dict[str, List[DRTResult]] = project.get_all_drts()
        self.fits: Dict[str, List[FitResult]] = project.get_all_fits()
        self.simulations: List[SimulationResult] = project.get_simulations()
        x: int
        y: int
        w: int
        h: int
        x, y, w, h = calculate_window_position_dimensions(720, 540)
        self.window: int = dpg.generate_uuid()
        with dpg.window(
            label="Copy appearance settings",
            modal=True,
            no_resize=True,
            pos=(
                x,
                y,
            ),
            width=w,
            height=h,
            on_close=self.close,
            tag=self.window,
        ):
            with dpg.group(horizontal=True):
                dpg.add_text("Source")
                self.source_combo: int = dpg.generate_uuid()
                dpg.add_combo(
                    items=self.labels,
                    default_value=self.labels[0],
                    width=-1,
                    callback=self.change_source,
                    tag=self.source_combo,
                )
            with dpg.group(horizontal=True):
                with dpg.group():
                    dpg.add_text("Before")
                    with dpg.child_window(width=348, height=-24):
                        with dpg.table(
                            borders_outerV=True,
                            borders_outerH=True,
                            borders_innerV=True,
                            borders_innerH=True,
                            scrollY=True,
                            freeze_rows=1,
                            width=-1,
                            height=18 + 23 * len(self.settings.series_order),
                        ):
                            dpg.add_table_column(label="", width_fixed=True)
                            dpg.add_table_column(label="Label")
                            dpg.add_table_column(label="Color", width_fixed=True)
                            dpg.add_table_column(label="Marker", width_fixed=True)
                            dpg.add_table_column(label="Line", width_fixed=True)
                            uuid: str
                            for uuid in settings.series_order:
                                series: Optional[
                                    Union[
                                        DataSet, TestResult, FitResult, SimulationResult
                                    ]
                                ]
                                series = settings.find_series(
                                    uuid,
                                    self.data_sets,
                                    self.tests,
                                    self.drts,
                                    self.fits,
                                    self.simulations,
                                )
                                assert series is not None
                                SeriesBefore(
                                    series,
                                    settings,
                                    self.marker_lookup,
                                    self.toggle_series,
                                )
                with dpg.group():
                    dpg.add_text("After")
                    with dpg.child_window(width=348, height=-24):
                        self.preview_table: int = dpg.generate_uuid()
                        with dpg.table(
                            borders_outerV=True,
                            borders_outerH=True,
                            borders_innerV=True,
                            borders_innerH=True,
                            scrollY=True,
                            freeze_rows=1,
                            width=-1,
                            height=18 + 23 * len(self.settings.series_order),
                            tag=self.preview_table,
                        ):
                            dpg.add_table_column(label="Label")
                            dpg.add_table_column(label="Color", width_fixed=True)
                            dpg.add_table_column(label="Marker", width_fixed=True)
                            dpg.add_table_column(label="Line", width_fixed=True)
            with dpg.group(horizontal=True):
                dpg.add_button(
                    label="Accept",
                    callback=self.accept,
                )
                dpg.add_spacer(width=354)
                self.labels_checkbox: int = dpg.generate_uuid()
                dpg.add_checkbox(
                    label="Labels",
                    default_value=True,
                    tag=self.labels_checkbox,
                    callback=lambda s, a, u: self.change_source(),
                )
                attach_tooltip(tooltips.plotting.copy_appearance_labels)
                self.colors_checkbox: int = dpg.generate_uuid()
                dpg.add_checkbox(
                    label="Colors",
                    default_value=True,
                    tag=self.colors_checkbox,
                    callback=lambda s, a, u: self.change_source(),
                )
                attach_tooltip(tooltips.plotting.copy_appearance_colors)
                self.markers_checkbox: int = dpg.generate_uuid()
                dpg.add_checkbox(
                    label="Markers",
                    default_value=True,
                    tag=self.markers_checkbox,
                    callback=lambda s, a, u: self.change_source(),
                )
                attach_tooltip(tooltips.plotting.copy_appearance_markers)
                self.lines_checkbox: int = dpg.generate_uuid()
                dpg.add_checkbox(
                    label="Lines",
                    default_value=True,
                    tag=self.lines_checkbox,
                    callback=lambda s, a, u: self.change_source(),
                )
                attach_tooltip(tooltips.plotting.copy_appearance_lines)
        self.key_handler: int = dpg.generate_uuid()
        with dpg.handler_registry(tag=self.key_handler):
            dpg.add_key_release_handler(
                key=dpg.mvKey_Escape,
                callback=self.close,
            )
            dpg.add_key_release_handler(
                key=dpg.mvKey_Return,
                callback=lambda: self.accept(keybinding=True),
            )
            dpg.add_key_release_handler(
                key=dpg.mvKey_Prior,
                callback=lambda: self.cycle_source(-1),
            )
            dpg.add_key_release_handler(
                key=dpg.mvKey_Next,
                callback=lambda: self.cycle_source(1),
            )
        signals.emit(Signal.BLOCK_KEYBINDINGS, window=self.window, window_object=self)
        self.change_source()

    def close(self):
        signals.emit(Signal.UNBLOCK_KEYBINDINGS)
        dpg.delete_item(self.window)
        dpg.delete_item(self.key_handler)

    def accept(self, keybinding: bool = False):
        if keybinding is True and not (
            is_control_down()
            if dpg.get_platform() == dpg.mvPlatform_Windows
            else is_alt_down()
        ):
            return
        dpg.hide_item(self.window)
        changes: Dict[str, Tuple[str, List[float], int, bool]] = {}
        row: int
        for row in dpg.get_item_children(self.preview_table, slot=1):
            uuid: str = dpg.get_item_user_data(row)
            label: str = ""
            color: List[float] = [255.0, 255.0, 255.0, 255.0]
            marker: int = -1
            line: bool = False
            i: int
            item: int
            for i, item in enumerate(dpg.get_item_children(row, slot=1)):
                item_type: str = dpg.get_item_type(item)
                if i == 0:
                    assert "::mvText" in item_type, item_type
                    label = dpg.get_item_user_data(item)
                elif i == 1:
                    assert "::mvTooltip" in item_type, item_type
                elif i == 2:
                    assert "::mvColorEdit" in item_type, item_type
                    color = dpg.get_item_user_data(item)
                elif i == 3:
                    assert "::mvText" in item_type, item_type
                    marker = dpg.get_item_user_data(item)
                elif i == 4:
                    assert "::mvCheckbox" in item_type, item_type
                    line = dpg.get_item_user_data(item)
            changes[uuid] = (
                label,
                color,
                marker,
                line,
            )
        signals.emit(
            Signal.COPY_PLOT_APPEARANCE_SETTINGS,
            changes=changes,
            settings=self.settings,
        )
        self.close()

    def cycle_source(self, step: int):
        assert type(step) is int, step
        index: int = self.labels.index(dpg.get_value(self.source_combo)) + step
        dpg.set_value(self.source_combo, self.labels[index % len(self.labels)])
        self.change_source()

    def change_source(self):
        label: str = dpg.get_value(self.source_combo)
        source: PlotSettings = self.plot_lookup[label]
        dpg.delete_item(self.preview_table, children_only=True, slot=1)
        copy_labels: bool = dpg.get_value(self.labels_checkbox)
        copy_colors: bool = dpg.get_value(self.colors_checkbox)
        copy_markers: bool = dpg.get_value(self.markers_checkbox)
        copy_lines: bool = dpg.get_value(self.lines_checkbox)
        for uuid in self.settings.series_order:
            SeriesAfter(
                self.settings.find_series(
                    uuid,
                    self.data_sets,
                    self.tests,
                    self.drts,
                    self.fits,
                    self.simulations,
                ),
                source
                if uuid in source.themes and self.series_checkboxes[uuid]
                else self.settings,
                self.settings,
                copy_labels,
                copy_colors,
                copy_markers,
                copy_lines,
                self.marker_lookup,
                self.preview_table,
            )

    def toggle_series(self, state: bool, uuid: str):
        self.series_checkboxes[uuid] = state
        self.change_source()
