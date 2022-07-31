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

from math import floor
from typing import (
    Dict,
    List,
    Optional,
    Tuple,
)
import dearpygui.dearpygui as dpg
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
from numpy import asarray, float32
from deareis.data import (
    PlotSettings,
    Project,
)
from deareis.gui.plots import Image
from deareis.signals import Signal
from deareis.tooltips import (
    attach_tooltip,
    update_tooltip,
)
from deareis.utility import format_number
from deareis.utility import calculate_window_position_dimensions
import deareis.api.plot.mpl as mpl
import deareis.signals as signals
import deareis.tooltips as tooltips
from deareis.keybindings import (
    is_alt_down,
    is_control_down,
)


PREVIEW_LIMITS: Dict[str, int] = {
    "No limit": -1,
    "256 px": 2**8,
    "512 px": 2**9,
    "1024 px": 2**10,
    "2048 px": 2**11,
    "4096 px": 2**12,
    "8192 px": 2**13,
}


UNITS_PER_INCH: Dict[str, float] = {
    "Centimeters": 2.54,
    "Inches": 1.0,
}


LEGEND_LOCATIONS: Dict[str, int] = {
    "Automatic": 0,
    "Upper right": 1,
    "Upper left": 2,
    "Lower left": 3,
    "Lower right": 4,
    "Right": 5,
    "Center left": 6,
    "Center right": 7,
    "Lower center": 8,
    "Upper center": 9,
    "Center": 10,
}


EXTENSIONS: List[str] = [
    ".eps",
    ".jpg",
    ".pdf",
    ".pgf",
    ".png",
    ".ps",
    ".svg",
]


class PlotExporter:
    def __init__(self, config: "Config"):
        self.key_handler: int = -1
        self.settings: Optional[PlotSettings] = None
        self.project: Optional[Project] = None
        self.texture_registry: int = dpg.generate_uuid()
        self.experimental_clear_registry: bool = True
        self.experimental_disable_previews: bool = False
        dpg.add_texture_registry(tag=self.texture_registry)
        self.window: int = dpg.generate_uuid()
        with dpg.window(
            label="Export plot",
            show=False,
            modal=True,
            on_close=self.close,
            tag=self.window,
        ):
            with dpg.group(horizontal=True):
                dpg.add_spacer(width=8)
                self.sidebar: int = dpg.generate_uuid()
                with dpg.child_window(
                    width=250,
                    height=-1,
                    border=False,
                    tag=self.sidebar,
                ):
                    dpg.add_spacer(height=4)
                    with dpg.child_window(
                        border=False,
                        height=-32,
                    ):
                        self.unit_combo: int = dpg.generate_uuid()
                        self.width_input: int = dpg.generate_uuid()
                        self.height_input: int = dpg.generate_uuid()
                        self.dpi_input: int = dpg.generate_uuid()
                        self.label_padding: int = 10
                        with dpg.collapsing_header(label=" Dimensions", leaf=True):
                            with dpg.group(horizontal=True):
                                dpg.add_text("Units".rjust(self.label_padding))
                                attach_tooltip(tooltips.plotting.export_units)
                                dpg.add_combo(
                                    width=-1,
                                    items=list(UNITS_PER_INCH.keys()),
                                    default_value="",
                                    callback=lambda s, a, u: self.refresh(),
                                    tag=self.unit_combo,
                                )
                            with dpg.group(horizontal=True):
                                dpg.add_text("Width".rjust(self.label_padding))
                                attach_tooltip(tooltips.plotting.export_width)
                                dpg.add_input_float(
                                    width=-1,
                                    default_value=0.0,
                                    min_value=0.01,
                                    min_clamped=True,
                                    step=0.0,
                                    format="%.2f",
                                    on_enter=True,
                                    callback=lambda s, a, u: self.refresh(),
                                    tag=self.width_input,
                                )
                            with dpg.group(horizontal=True):
                                dpg.add_text("Height".rjust(self.label_padding))
                                attach_tooltip(tooltips.plotting.export_height)
                                dpg.add_input_float(
                                    width=-1,
                                    default_value=0.0,
                                    min_value=0.01,
                                    min_clamped=True,
                                    step=0.0,
                                    format="%.2f",
                                    on_enter=True,
                                    callback=lambda s, a, u: self.refresh(),
                                    tag=self.height_input,
                                )
                            with dpg.group(horizontal=True):
                                dpg.add_text("DPI".rjust(self.label_padding))
                                attach_tooltip(tooltips.plotting.export_dpi)
                                dpg.add_input_int(
                                    width=-1,
                                    default_value=0,
                                    min_value=1,
                                    min_clamped=True,
                                    step=0,
                                    on_enter=True,
                                    callback=lambda s, a, u: self.refresh(),
                                    tag=self.dpi_input,
                                )
                            with dpg.group(horizontal=True):
                                dpg.add_text("Result".rjust(self.label_padding))
                                attach_tooltip(tooltips.plotting.export_result)
                                tooltip_tag: int = dpg.generate_uuid()
                                self.dimensions_output: int = dpg.add_text(
                                    "", user_data=tooltip_tag
                                )
                                attach_tooltip("", tag=tooltip_tag)
                            with dpg.group(horizontal=True):
                                dpg.add_text("Preview".rjust(self.label_padding))
                                attach_tooltip(tooltips.plotting.export_preview)
                                self.preview_combo: int = dpg.generate_uuid()
                                dpg.add_combo(
                                    items=list(PREVIEW_LIMITS.keys()),
                                    default_value="",
                                    callback=lambda s, a, u: self.refresh(),
                                    tag=self.preview_combo,
                                )
                        with dpg.collapsing_header(label=" Limits", leaf=True):
                            with dpg.group(horizontal=True):
                                dpg.add_text("Min. X".rjust(self.label_padding))
                                attach_tooltip(tooltips.plotting.export_min_x)
                                self.x_min_enabled: int = dpg.generate_uuid()
                                dpg.add_checkbox(
                                    default_value=False,
                                    callback=lambda s, a, u: self.refresh(),
                                    tag=self.x_min_enabled,
                                )
                                self.x_min: int = dpg.generate_uuid()
                                dpg.add_input_float(
                                    width=-1,
                                    step=0.0,
                                    format="%.2f",
                                    on_enter=True,
                                    callback=lambda s, a, u: self.refresh(),
                                    tag=self.x_min,
                                )
                            with dpg.group(horizontal=True):
                                dpg.add_text("Max. X".rjust(self.label_padding))
                                attach_tooltip(tooltips.plotting.export_max_x)
                                self.x_max_enabled: int = dpg.generate_uuid()
                                dpg.add_checkbox(
                                    default_value=False,
                                    callback=lambda s, a, u: self.refresh(),
                                    tag=self.x_max_enabled,
                                )
                                self.x_max: int = dpg.generate_uuid()
                                dpg.add_input_float(
                                    width=-1,
                                    step=0.0,
                                    format="%.2f",
                                    on_enter=True,
                                    callback=lambda s, a, u: self.refresh(),
                                    tag=self.x_max,
                                )
                            with dpg.group(horizontal=True):
                                dpg.add_text("Min. Y".rjust(self.label_padding))
                                attach_tooltip(tooltips.plotting.export_min_y)
                                self.y_min_enabled: int = dpg.generate_uuid()
                                dpg.add_checkbox(
                                    default_value=False,
                                    callback=lambda s, a, u: self.refresh(),
                                    tag=self.y_min_enabled,
                                )
                                self.y_min: int = dpg.generate_uuid()
                                dpg.add_input_float(
                                    width=-1,
                                    step=0.0,
                                    format="%.2f",
                                    on_enter=True,
                                    callback=lambda s, a, u: self.refresh(),
                                    tag=self.y_min,
                                )
                            with dpg.group(horizontal=True):
                                dpg.add_text("Max. Y".rjust(self.label_padding))
                                attach_tooltip(tooltips.plotting.export_max_y)
                                self.y_max_enabled: int = dpg.generate_uuid()
                                dpg.add_checkbox(
                                    default_value=False,
                                    callback=lambda s, a, u: self.refresh(),
                                    tag=self.y_max_enabled,
                                )
                                self.y_max: int = dpg.generate_uuid()
                                dpg.add_input_float(
                                    width=-1,
                                    step=0.0,
                                    format="%.2f",
                                    on_enter=True,
                                    callback=lambda s, a, u: self.refresh(),
                                    tag=self.y_max,
                                )
                        with dpg.collapsing_header(label=" Layout", leaf=True):
                            with dpg.group(horizontal=True):
                                dpg.add_text("Title".rjust(self.label_padding))
                                attach_tooltip(tooltips.plotting.export_title)
                                self.show_title: int = dpg.generate_uuid()
                                dpg.add_checkbox(
                                    default_value=True,
                                    callback=lambda s, a, u: self.refresh(),
                                    tag=self.show_title,
                                )
                            with dpg.group(horizontal=True):
                                dpg.add_text("Legend".rjust(self.label_padding))
                                attach_tooltip(tooltips.plotting.export_legend)
                                self.show_legend: int = dpg.generate_uuid()
                                dpg.add_checkbox(
                                    default_value=True,
                                    callback=lambda s, a, u: self.refresh(),
                                    tag=self.show_legend,
                                )
                                self.legend_combo: int = dpg.generate_uuid()
                                dpg.add_combo(
                                    items=list(LEGEND_LOCATIONS.keys()),
                                    default_value=list(LEGEND_LOCATIONS.keys())[0],
                                    callback=lambda s, a, u: self.refresh(),
                                    width=-1,
                                    tag=self.legend_combo,
                                )
                            with dpg.group(horizontal=True):
                                dpg.add_text("Grid".rjust(self.label_padding))
                                attach_tooltip(tooltips.plotting.export_grid)
                                self.grid: int = dpg.generate_uuid()
                                dpg.add_checkbox(
                                    default_value=False,
                                    callback=lambda s, a, u: self.refresh(),
                                    tag=self.grid,
                                )
                            with dpg.group(horizontal=True):
                                dpg.add_text("Tight".rjust(self.label_padding))
                                attach_tooltip(tooltips.plotting.export_tight)
                                self.tight_layout: int = dpg.generate_uuid()
                                dpg.add_checkbox(
                                    default_value=False,
                                    callback=lambda s, a, u: self.refresh(),
                                    tag=self.tight_layout,
                                )
                        with dpg.collapsing_header(label=" Miscellaneous", leaf=True):
                            with dpg.group(horizontal=True):
                                dpg.add_text(
                                    "Points per decade".rjust(self.label_padding)
                                )
                                attach_tooltip(tooltips.plotting.export_num_per_decade)
                                self.num_per_decade: int = dpg.generate_uuid()
                                dpg.add_input_int(
                                    width=-1,
                                    default_value=0,
                                    min_value=1,
                                    min_clamped=True,
                                    step=0,
                                    on_enter=True,
                                    callback=lambda s, a, u: self.refresh(),
                                    tag=self.num_per_decade,
                                )
                    with dpg.child_window(border=False):
                        self.save_button: int = dpg.add_button(
                            label="Save as",
                            callback=lambda s, a, u: self.save(u),
                            user_data=None,
                            width=-1,
                        )
                        attach_tooltip(tooltips.plotting.export_file)
                self.image_plot: Image = Image()
        self.update_settings(config)

    def clear(self):
        fig: Optional[Figure] = dpg.get_item_user_data(self.save_button)
        if fig is not None:
            plt.close(fig)
            dpg.set_item_user_data(self.save_button, None)
        if not self.experimental_disable_previews:
            self.image_plot.clear()
            if self.experimental_clear_registry:
                dpg.delete_item(self.texture_registry, children_only=True)

    def close(self):
        if dpg.does_item_exist(self.key_handler):
            dpg.delete_item(self.key_handler)
        dpg.hide_item(self.window)
        self.clear()
        signals.emit(Signal.UNBLOCK_KEYBINDINGS)
        # dpg.delete_item(self.key_handler)

    def update_settings(self, config: "Config"):
        dpg.set_value(self.unit_combo, list(UNITS_PER_INCH.keys())[config.export_units])
        dpg.set_value(self.width_input, config.export_width)
        dpg.set_value(self.height_input, config.export_height)
        dpg.set_value(self.dpi_input, config.export_dpi)
        dpg.set_value(
            self.preview_combo, list(PREVIEW_LIMITS.keys())[config.export_preview]
        )
        dpg.set_value(self.show_title, config.export_title)
        dpg.set_value(self.show_legend, config.export_legend)
        dpg.set_value(
            self.legend_combo,
            list(LEGEND_LOCATIONS.keys())[config.export_legend_location],
        )
        dpg.set_value(self.grid, config.export_grid)
        dpg.set_value(self.tight_layout, config.export_tight)
        dpg.set_value(self.num_per_decade, config.export_num_per_decade)
        self.experimental_clear_registry = config.export_experimental_clear_registry
        self.experimental_disable_previews = config.export_experimental_disable_previews

    def initialize_keybindings(self):
        self.key_handler = dpg.generate_uuid()
        with dpg.handler_registry(tag=self.key_handler):
            dpg.add_key_release_handler(
                key=dpg.mvKey_Escape,
                callback=self.close,
            )
            dpg.add_key_release_handler(
                key=dpg.mvKey_Return,
                callback=lambda: self.save(
                    dpg.get_item_user_data(self.save_button), keybinding=True
                ),
            )

    def show(self, settings: PlotSettings, project: Project):
        self.initialize_keybindings()
        self.settings = settings
        self.project = project
        dpg.show_item(self.window)
        dpg.split_frame()
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
        signals.emit(Signal.BLOCK_KEYBINDINGS, window=self.window)
        self.refresh()

    def create_preview_figure(
        self, width: float, height: float, dpi: int
    ) -> Tuple[Figure, int, int]:
        assert type(width) is float and width > 0.0, width
        assert type(height) is float and height > 0.0, height
        assert type(dpi) is int and dpi > 0, dpi
        pixel_width: int = floor(width * dpi)
        pixel_height: int = floor(height * dpi)
        preview_limit: int = PREVIEW_LIMITS.get(dpg.get_value(self.preview_combo), -1)
        if preview_limit > 0 and (
            pixel_width > preview_limit or pixel_height > preview_limit
        ):
            if pixel_width >= pixel_height:
                pixel_height = floor(pixel_height / pixel_width * preview_limit)
                pixel_width = preview_limit
            else:
                pixel_width = floor(pixel_width / pixel_height * preview_limit)
                pixel_height = preview_limit
        width = pixel_width / dpi
        height = pixel_height / dpi
        fig: Figure = plt.figure(
            figsize=(
                width,
                height,
            ),
            dpi=dpi,
        )
        return (
            fig,
            pixel_width,
            pixel_height,
        )

    def create_final_figure(self, width: float, height: float, dpi: int) -> Figure:
        assert type(width) is float and width > 0.0, width
        assert type(height) is float and height > 0.0, height
        assert type(dpi) is int and dpi > 0, dpi
        pixel_width: int = floor(width * dpi)
        pixel_height: int = floor(height * dpi)
        pixel_dimensions: List[str] = [
            format_number(float(pixel_width), decimals=0, exponent=False),
            format_number(float(pixel_height), decimals=0, exponent=False),
        ]
        dpg.set_value(
            self.dimensions_output,
            f"{pixel_dimensions[0]} px * {pixel_dimensions[1]} px",
        )
        update_tooltip(
            dpg.get_item_user_data(self.dimensions_output),
            f"{pixel_dimensions[0]} px * {pixel_dimensions[1]} px",
        )
        fig: Figure = plt.figure(
            figsize=(
                width,
                height,
            ),
            dpi=dpi,
        )
        return fig

    def plot(self, fig: Figure):
        assert type(fig) is Figure, type(fig)
        assert self.settings is not None
        assert self.project is not None
        x_limits: Optional[Tuple[Optional[float], Optional[float]]] = None
        if dpg.get_value(self.x_min_enabled) or dpg.get_value(self.x_max_enabled):
            x_limits = (
                dpg.get_value(self.x_min)
                if dpg.get_value(self.x_min_enabled)
                else None,
                dpg.get_value(self.x_max)
                if dpg.get_value(self.x_max_enabled)
                else None,
            )
        y_limits: Optional[Tuple[Optional[float], Optional[float]]] = None
        if dpg.get_value(self.y_min_enabled) or dpg.get_value(self.y_max_enabled):
            y_limits = (
                dpg.get_value(self.y_min)
                if dpg.get_value(self.y_min_enabled)
                else None,
                dpg.get_value(self.y_max)
                if dpg.get_value(self.y_max_enabled)
                else None,
            )
        mpl.plot(
            self.settings,
            self.project,
            x_limits=x_limits,
            y_limits=y_limits,
            show_title=dpg.get_value(self.show_title),
            show_legend=dpg.get_value(self.show_legend),
            legend_loc=LEGEND_LOCATIONS.get(dpg.get_value(self.legend_combo), 0),
            tight_layout=dpg.get_value(self.tight_layout),
            show_grid=dpg.get_value(self.grid),
            fig=fig,
            axis=fig.gca(),
            num_per_decade=dpg.get_value(self.num_per_decade),
        )

    def refresh(self):
        width: float = dpg.get_value(self.width_input)
        height: float = dpg.get_value(self.height_input)
        dpi: int = dpg.get_value(self.dpi_input)
        upi: float = UNITS_PER_INCH.get(dpg.get_value(self.unit_combo))
        assert type(width) is float and width > 0.0, width
        assert type(height) is float and height > 0.0, height
        assert type(dpi) is int and dpi > 0, dpi
        assert type(upi) is float and upi > 0.0, upi
        self.clear()
        width = width / upi
        height = height / upi
        final_fig: Figure = self.create_final_figure(width, height, dpi)
        dpg.set_item_user_data(self.save_button, final_fig)
        self.plot(final_fig)
        # Preview
        if not self.experimental_disable_previews:
            preview_fig: Figure
            pixel_width: int
            pixel_height: int
            preview_fig, pixel_width, pixel_height = self.create_preview_figure(
                width, height, dpi
            )
            canvas: FigureCanvasAgg = FigureCanvasAgg(preview_fig)
            self.plot(preview_fig)
            canvas.draw()
            tag: int = dpg.add_raw_texture(
                pixel_width,
                pixel_height,
                asarray(canvas.buffer_rgba()).astype(float32) / 255,
                format=dpg.mvFormat_Float_rgba,
                parent=self.texture_registry,
            )
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
            plt.close(preview_fig)
            self.image_plot.queue_limits_adjustment()
        x_min: float
        x_max: float
        y_min: float
        y_max: float
        x_min, x_max = final_fig.gca().get_xlim()
        y_min, y_max = final_fig.gca().get_ylim()
        if dpg.get_value(self.x_min_enabled):
            dpg.enable_item(self.x_min)
        else:
            dpg.disable_item(self.x_min)
            dpg.set_value(self.x_min, x_min)
        if dpg.get_value(self.x_max_enabled):
            dpg.enable_item(self.x_max)
        else:
            dpg.disable_item(self.x_max)
            dpg.set_value(self.x_max, x_max)
        if dpg.get_value(self.y_min_enabled):
            dpg.enable_item(self.y_min)
        else:
            dpg.disable_item(self.y_min)
            dpg.set_value(self.y_min, y_min)
        if dpg.get_value(self.y_max_enabled):
            dpg.enable_item(self.y_max)
        else:
            dpg.disable_item(self.y_max)
            dpg.set_value(self.y_max, y_max)
        if dpg.get_value(self.show_legend):
            dpg.enable_item(self.legend_combo)
        else:
            dpg.disable_item(self.legend_combo)

    def save(self, fig: Optional[Figure], keybinding: bool = False):
        if fig is None:
            return
        elif keybinding is True and not (
            is_control_down()
            if dpg.get_platform() == dpg.mvPlatform_Windows
            else is_alt_down()
        ):
            return
        self.close()
        dpg.split_frame()
        signals.emit(Signal.SAVE_PLOT, figure=fig)
