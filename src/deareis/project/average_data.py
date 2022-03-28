# Copyright 2022 DearEIS developers
# DearEIS is licensed under the GPLv3 or later (https://www.gnu.org/licenses/gpl-3.0.html).
# The licenses of DearEIS' dependencies and/or sources of portions of code are included in
# the LICENSES folder.

from pyimpspec import DataSet
from typing import Callable, List, Optional
import dearpygui.dearpygui as dpg
from deareis.plot import NyquistPlot
import deareis.themes as themes
from deareis.utility import attach_tooltip, window_pos_dims
from deareis.themes import PLOT_MARKERS, VIBRANT_COLORS


# TODO: Add resize handler to check when the viewport is resized


class AverageData:
    def __init__(self, datasets: List[DataSet], callback: Callable):
        assert type(datasets) is list and all(
            map(lambda _: type(_) is DataSet, datasets)
        )
        assert callback is not None
        self.datasets: List[DataSet] = datasets
        self.callback: Callable = callback
        self.preview_data: DataSet
        self.window: int = dpg.generate_uuid()
        self.label_input: int = dpg.generate_uuid()
        self.dataset_table: int = dpg.generate_uuid()
        self.nyquist_plot: NyquistPlot = None  # type: ignore
        self.key_handler: int = dpg.generate_uuid()
        self._assemble()
        self._setup_keybindings()
        self.plot_themes: List[int] = list(
            map(
                lambda _: self.get_plot_theme(_, dpg.mvPlotColormap_Pastel),
                range(0, 12),
            )
        )
        self.final_data: Optional[DataSet] = None
        self.update_preview([])

    def _setup_keybindings(self):
        with dpg.handler_registry(tag=self.key_handler):
            dpg.add_key_release_handler(
                key=dpg.mvKey_Escape,
                callback=self.close,
            )
            dpg.add_key_release_handler(
                key=dpg.mvKey_Return,
                callback=self.accept,
            )

    def _assemble(self):
        x: int
        y: int
        w: int
        h: int
        x, y, w, h = window_pos_dims()
        with dpg.window(
            label="Average of multiple data sets",
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
                with dpg.group():
                    with dpg.child_window(border=False, width=300, height=-24):
                        with dpg.group(horizontal=True):
                            dpg.add_text("Label")
                            dpg.add_input_text(
                                hint="REQUIRED",
                                default_value="Average",
                                width=-1,
                                tag=self.label_input,
                                callback=lambda: self.update_preview([]),
                            )
                        with dpg.table(
                            borders_outerV=True,
                            borders_outerH=True,
                            borders_innerV=True,
                            borders_innerH=True,
                            scrollY=True,
                            freeze_rows=1,
                            width=-1,
                            height=-1,
                            tag=self.dataset_table,
                        ):
                            dpg.add_table_column(label="", width_fixed=True)
                            dpg.add_table_column(label="Label", width_fixed=True)
                            data: DataSet
                            for data in self.datasets:
                                with dpg.table_row():
                                    dpg.add_checkbox(callback=lambda: self.update_preview([]))
                                    label: str = data.get_label()
                                    dpg.add_text(label)
                                    attach_tooltip(label)
                    dpg.add_button(label="Accept", callback=self.accept)
                self.nyquist_plot = NyquistPlot(
                    dpg.add_plot(
                        equal_aspects=True,
                        width=-1,
                        height=-12,
                        anti_aliased=True,
                    )
                )

    def close(self):
        dpg.hide_item(self.window)
        dpg.delete_item(self.key_handler)

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
        datasets: List[DataSet] = []
        i: int
        row: int
        for i, row in enumerate(dpg.get_item_children(self.dataset_table, slot=1)):
            column: int
            for column in dpg.get_item_children(row, slot=1):
                assert dpg.get_item_type(column).endswith("mvCheckbox")
                if dpg.get_value(column) is True:
                    datasets.append(self.datasets[i])
                break
        return datasets

    def get_plot_theme(self, index: int, colormap: int) -> int:
        assert type(index) is int
        assert type(colormap) is int
        R: int
        G: int
        B: int
        A: int
        R, G, B, A = VIBRANT_COLORS[index % len(VIBRANT_COLORS)]
        marker: int = list(PLOT_MARKERS.values())[index % len(PLOT_MARKERS)]
        with dpg.theme() as theme:
            with dpg.theme_component(dpg.mvScatterSeries):
                dpg.add_theme_color(
                    dpg.mvPlotCol_Line,
                    (
                        R,
                        G,
                        B,
                        190,
                    ),
                    category=dpg.mvThemeCat_Plots,
                )
                dpg.add_theme_color(
                    dpg.mvPlotCol_MarkerFill,
                    (
                        R,
                        G,
                        B,
                        0,
                    ),
                    category=dpg.mvThemeCat_Plots,
                )
                dpg.add_theme_color(
                    dpg.mvPlotCol_MarkerOutline,
                    (
                        R,
                        G,
                        B,
                        190,
                    ),
                    category=dpg.mvThemeCat_Plots,
                )
                dpg.add_theme_style(
                    dpg.mvPlotStyleVar_Marker, marker, category=dpg.mvThemeCat_Plots
                )
        return theme

    def update_preview(self, datasets: List[DataSet]):
        assert type(datasets) is list and all(map(lambda _: type(_) is DataSet, datasets)), datasets
        self.nyquist_plot.clear_plot()
        dpg.add_plot_legend(parent=self.nyquist_plot.plot)
        selection: List[DataSet] = self.get_selection()
        i: int
        data: DataSet
        for i, data in enumerate(selection):
            self.nyquist_plot._plot(
                *data.get_nyquist_data(masked=None),
                data.get_label(),
                False,
                True,
                self.plot_themes[i % 12],
                -1,
                self.nyquist_plot.x_axis,
                self.nyquist_plot.y_axis,
            )
        if len(selection) > 1:
            try:
                self.final_data = DataSet.average(
                    selection,
                    label=dpg.get_value(self.label_input),
                )
                self.nyquist_plot._plot(
                    *self.final_data.get_nyquist_data(masked=None),
                    self.final_data.get_label(),
                    True,
                    False,
                    themes.nyquist_data,
                    -1,
                    self.nyquist_plot.x_axis,
                    self.nyquist_plot.y_axis,
                )
            except AssertionError:
                self.final_data = None
        self.nyquist_plot.adjust_limits()
