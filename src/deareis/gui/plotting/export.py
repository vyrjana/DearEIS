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

from math import floor
from typing import (
    Callable,
    Dict,
    List,
    Optional,
    Tuple,
)
import dearpygui.dearpygui as dpg
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
from numpy import asarray, float32
from numpy.typing import NDArray
from deareis.data import (
    PlotSettings,
    Project,
)
from deareis.data.plotting import PlotExportSettings
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
from deareis.config import Config
from deareis.enums import (
    PLOT_EXTENSIONS,
    PlotPreviewLimit,  # DEPRECATED
    plot_legend_location_to_label,
    label_to_plot_legend_location,
    plot_units_to_label,
    plot_units_per_inch,
    plot_preview_limit_to_label,  # DEPRECATED
    label_to_plot_preview_limit,  # DEPRECATED
    label_to_plot_units,
)
from deareis.enums import Action
from deareis.keybindings import (
    Keybinding,
    TemporaryKeybindingHandler,
)
from deareis.typing.helpers import Tag


class SettingsMenu:
    def __init__(
        self,
        default_settings: PlotExportSettings,
        label_pad: int,
        refresh_callback: Optional[Callable] = None,
    ):
        callback_kwarg: dict = {}
        if refresh_callback is not None:
            callback_kwarg.update(
                {"callback": lambda s, a, u: refresh_callback(self.get_settings())}
            )

        with dpg.collapsing_header(label=" Dimensions", leaf=True):
            with dpg.group(horizontal=True):
                dpg.add_text("Units".rjust(label_pad))
                attach_tooltip(tooltips.plotting.export_units)
                
                self.unit_combo: Tag = dpg.generate_uuid()
                dpg.add_combo(
                    width=-1,
                    default_value=plot_units_to_label[default_settings.units],
                    items=list(label_to_plot_units.keys()),
                    **callback_kwarg,
                    tag=self.unit_combo,
                )

            with dpg.group(horizontal=True):
                dpg.add_text("Width".rjust(label_pad))
                attach_tooltip(tooltips.plotting.export_width)
                
                self.width_input: Tag = dpg.generate_uuid()
                dpg.add_input_float(
                    width=-1,
                    default_value=default_settings.width,
                    min_value=0.01,
                    min_clamped=True,
                    step=0.0,
                    format="%.2f",
                    on_enter=True,
                    **callback_kwarg,
                    tag=self.width_input,
                )

            with dpg.group(horizontal=True):
                dpg.add_text("Height".rjust(label_pad))
                attach_tooltip(tooltips.plotting.export_height)
                
                self.height_input: Tag = dpg.generate_uuid()
                dpg.add_input_float(
                    width=-1,
                    default_value=default_settings.height,
                    min_value=0.01,
                    min_clamped=True,
                    step=0.0,
                    format="%.2f",
                    on_enter=True,
                    **callback_kwarg,
                    tag=self.height_input,
                )

            with dpg.group(horizontal=True):
                dpg.add_text("DPI".rjust(label_pad))
                attach_tooltip(tooltips.plotting.export_dpi)
                
                self.dpi_input: Tag = dpg.generate_uuid()
                dpg.add_input_int(
                    width=-1,
                    default_value=default_settings.dpi,
                    min_value=1,
                    min_clamped=True,
                    step=0,
                    on_enter=True,
                    **callback_kwarg,
                    tag=self.dpi_input,
                )

            if refresh_callback is not None:
                with dpg.group(horizontal=True):
                    dpg.add_text("Result".rjust(label_pad))
                    attach_tooltip(tooltips.plotting.export_result)
                    
                    tooltip_tag: Tag = dpg.generate_uuid()
                    self.dimensions_output: Tag = dpg.add_text(
                        "",
                        user_data=tooltip_tag,
                    )
                    attach_tooltip("", tag=tooltip_tag)

            # DEPRECATED
            # TODO: Remove at some point
            # with dpg.group(horizontal=True):
            #     dpg.add_text("Preview".rjust(label_pad))
            #     attach_tooltip(tooltips.plotting.export_preview)
            #     
            #     self.preview_combo: Tag = dpg.generate_uuid()
            #     dpg.add_combo(
            #         width=-1,
            #         default_value=plot_preview_limit_to_label[
            #             default_settings.preview_limit
            #         ],
            #         items=list(label_to_plot_preview_limit.keys()),
            #         **callback_kwarg,
            #         tag=self.preview_combo,
            #     )

        with dpg.collapsing_header(
            label=" Limits",
            leaf=True,
            show=refresh_callback is not None,
        ):
            with dpg.group(horizontal=True):
                dpg.add_text("Min. X".rjust(label_pad))
                attach_tooltip(tooltips.plotting.export_min_x)
                
                self.x_min_checkbox: Tag = dpg.generate_uuid()
                dpg.add_checkbox(
                    default_value=False,
                    **callback_kwarg,
                    tag=self.x_min_checkbox,
                )
                
                self.x_min_input: Tag = dpg.generate_uuid()
                dpg.add_input_float(
                    width=-1,
                    step=0.0,
                    format="%.2e",
                    on_enter=True,
                    **callback_kwarg,
                    tag=self.x_min_input,
                )

            with dpg.group(horizontal=True):
                dpg.add_text("Max. X".rjust(label_pad))
                attach_tooltip(tooltips.plotting.export_max_x)
                
                self.x_max_checkbox: Tag = dpg.generate_uuid()
                dpg.add_checkbox(
                    default_value=False,
                    **callback_kwarg,
                    tag=self.x_max_checkbox,
                )
                
                self.x_max_input: Tag = dpg.generate_uuid()
                dpg.add_input_float(
                    width=-1,
                    step=0.0,
                    format="%.2e",
                    on_enter=True,
                    **callback_kwarg,
                    tag=self.x_max_input,
                )

            with dpg.group(horizontal=True):
                dpg.add_text("Min. Y".rjust(label_pad))
                attach_tooltip(tooltips.plotting.export_min_y)
                
                self.y_min_checkbox: Tag = dpg.generate_uuid()
                dpg.add_checkbox(
                    default_value=False,
                    **callback_kwarg,
                    tag=self.y_min_checkbox,
                )
                
                self.y_min_input: Tag = dpg.generate_uuid()
                dpg.add_input_float(
                    width=-1,
                    step=0.0,
                    format="%.2e",
                    on_enter=True,
                    **callback_kwarg,
                    tag=self.y_min_input,
                )

            with dpg.group(horizontal=True):
                dpg.add_text("Max. Y".rjust(label_pad))
                attach_tooltip(tooltips.plotting.export_max_y)
                
                self.y_max_checkbox: Tag = dpg.generate_uuid()
                dpg.add_checkbox(
                    default_value=False,
                    **callback_kwarg,
                    tag=self.y_max_checkbox,
                )
                
                self.y_max_input: Tag = dpg.generate_uuid()
                dpg.add_input_float(
                    width=-1,
                    step=0.0,
                    format="%.2e",
                    on_enter=True,
                    **callback_kwarg,
                    tag=self.y_max_input,
                )

        with dpg.collapsing_header(label=" Layout", leaf=True):
            with dpg.group(horizontal=True):
                dpg.add_text("Title".rjust(label_pad))
                attach_tooltip(tooltips.plotting.export_title)
                
                self.show_title_checkbox: Tag = dpg.generate_uuid()
                dpg.add_checkbox(
                    default_value=default_settings.show_title,
                    **callback_kwarg,
                    tag=self.show_title_checkbox,
                )

            with dpg.group(horizontal=True):
                dpg.add_text("Legend".rjust(label_pad))
                attach_tooltip(tooltips.plotting.export_legend)
                
                self.show_legend_checkbox: Tag = dpg.generate_uuid()
                dpg.add_checkbox(
                    default_value=default_settings.show_legend,
                    **callback_kwarg,
                    tag=self.show_legend_checkbox,
                )
                
                self.legend_combo: Tag = dpg.generate_uuid()
                dpg.add_combo(
                    default_value=plot_legend_location_to_label[
                        default_settings.legend_location
                    ],
                    items=list(label_to_plot_legend_location.keys()),
                    **callback_kwarg,
                    width=-1,
                    tag=self.legend_combo,
                )

            with dpg.group(horizontal=True):
                dpg.add_text("Grid".rjust(label_pad))
                attach_tooltip(tooltips.plotting.export_grid)
                
                self.show_grid_checkbox: Tag = dpg.generate_uuid()
                dpg.add_checkbox(
                    default_value=default_settings.show_grid,
                    **callback_kwarg,
                    tag=self.show_grid_checkbox,
                )

            with dpg.group(horizontal=True):
                dpg.add_text("Tight".rjust(label_pad))
                attach_tooltip(tooltips.plotting.export_tight)
                
                self.has_tight_layout_checkbox: Tag = dpg.generate_uuid()
                dpg.add_checkbox(
                    default_value=default_settings.has_tight_layout,
                    **callback_kwarg,
                    tag=self.has_tight_layout_checkbox,
                )

        with dpg.collapsing_header(label=" Miscellaneous", leaf=True):
            with dpg.group(horizontal=True):
                dpg.add_text("Points per decade".rjust(label_pad))
                attach_tooltip(tooltips.plotting.export_num_per_decade)
                
                self.num_per_decade_input: Tag = dpg.generate_uuid()
                dpg.add_input_int(
                    width=-1,
                    default_value=default_settings.num_per_decade,
                    min_value=1,
                    min_clamped=True,
                    step=0,
                    on_enter=True,
                    **callback_kwarg,
                    tag=self.num_per_decade_input,
                )

            with dpg.group(horizontal=True, show=refresh_callback is None):
                dpg.add_text("Default extension".rjust(label_pad))
                
                self.extension_combo: Tag = dpg.generate_uuid()
                dpg.add_combo(
                    width=-1,
                    default_value=default_settings.extension
                    if default_settings.extension in PLOT_EXTENSIONS
                    else ".png",
                    items=PLOT_EXTENSIONS,
                    tag=self.extension_combo,
                )

            with dpg.group(horizontal=True, show=refresh_callback is None):
                dpg.add_text("Clear texture registry".rjust(label_pad))
                attach_tooltip(tooltips.plotting.clear_registry)
                
                self.clear_registry_checkbox: Tag = dpg.generate_uuid()
                dpg.add_checkbox(
                    default_value=default_settings.clear_registry,
                    tag=self.clear_registry_checkbox,
                )

            with dpg.group(horizontal=True, show=refresh_callback is None):
                dpg.add_text("Disable plot preview".rjust(label_pad))
                attach_tooltip(tooltips.plotting.disable_preview)
                
                self.disable_preview_checkbox: Tag = dpg.generate_uuid()
                dpg.add_checkbox(
                    default_value=default_settings.disable_preview,
                    tag=self.disable_preview_checkbox,
                )

    def get_settings(self) -> PlotExportSettings:
        return PlotExportSettings(
            units=label_to_plot_units[dpg.get_value(self.unit_combo)],
            width=dpg.get_value(self.width_input),
            height=dpg.get_value(self.height_input),
            dpi=dpg.get_value(self.dpi_input),
            preview_limit=PlotPreviewLimit.NONE,
            # DEPRECATED
            # TODO: Remove at some point
            # preview_limit=label_to_plot_preview_limit[
            #     dpg.get_value(self.preview_combo)
            # ],
            show_title=dpg.get_value(self.show_title_checkbox),
            show_legend=dpg.get_value(self.show_legend_checkbox),
            legend_location=label_to_plot_legend_location[
                dpg.get_value(self.legend_combo)
            ],
            show_grid=dpg.get_value(self.show_grid_checkbox),
            has_tight_layout=dpg.get_value(self.has_tight_layout_checkbox),
            num_per_decade=dpg.get_value(self.num_per_decade_input),
            extension=dpg.get_value(self.extension_combo),
            clear_registry=dpg.get_value(self.clear_registry_checkbox),
            disable_preview=dpg.get_value(self.disable_preview_checkbox),
        )

    def set_settings(self, settings: PlotExportSettings):
        dpg.set_value(self.unit_combo, plot_units_to_label[settings.units])
        dpg.set_value(self.width_input, settings.width)
        dpg.set_value(self.height_input, settings.height)
        dpg.set_value(self.dpi_input, settings.dpi)
        # DEPRECATED
        # TODO: Remove at some point
        # dpg.set_value(
        #     self.preview_combo,
        #     plot_preview_limit_to_label[settings.preview_limit],
        # )
        dpg.set_value(self.show_title_checkbox, settings.show_title)
        dpg.set_value(self.show_legend_checkbox, settings.show_legend)

        if dpg.get_value(self.show_legend_checkbox):
            dpg.enable_item(self.legend_combo)
        else:
            dpg.disable_item(self.legend_combo)
        
        dpg.set_value(
            self.legend_combo,
            plot_legend_location_to_label[settings.legend_location],
        )
        dpg.set_value(self.show_grid_checkbox, settings.show_grid)
        dpg.set_value(self.has_tight_layout_checkbox, settings.has_tight_layout)
        dpg.set_value(self.num_per_decade_input, settings.num_per_decade)
        dpg.set_value(self.extension_combo, settings.extension)
        dpg.set_value(self.clear_registry_checkbox, settings.clear_registry)
        dpg.set_value(self.disable_preview_checkbox, settings.disable_preview)
        
        if dpg.get_value(self.x_min_checkbox):
            dpg.enable_item(self.x_min_input)
        else:
            dpg.disable_item(self.x_min_input)
        
        if dpg.get_value(self.x_max_checkbox):
            dpg.enable_item(self.x_max_input)
        else:
            dpg.disable_item(self.x_max_input)
        
        if dpg.get_value(self.y_min_checkbox):
            dpg.enable_item(self.y_min_input)
        else:
            dpg.disable_item(self.y_min_input)
        
        if dpg.get_value(self.y_max_checkbox):
            dpg.enable_item(self.y_max_input)
        else:
            dpg.disable_item(self.y_max_input)

    def update_plot_limits(
        self, x_min: float, x_max: float, y_min: float, y_max: float
    ):
        if not dpg.get_value(self.x_min_checkbox):
            dpg.set_value(self.x_min_input, x_min)
        
        if not dpg.get_value(self.x_max_checkbox):
            dpg.set_value(self.x_max_input, x_max)
        
        if not dpg.get_value(self.y_min_checkbox):
            dpg.set_value(self.y_min_input, y_min)
        
        if not dpg.get_value(self.y_max_checkbox):
            dpg.set_value(self.y_max_input, y_max)

    def get_x_limits(self) -> Optional[Tuple[Optional[float], Optional[float]]]:
        if dpg.get_value(self.x_min_checkbox) or dpg.get_value(self.x_max_checkbox):
            return (
                dpg.get_value(self.x_min_input)
                if dpg.get_value(self.x_min_checkbox)
                else None,
                dpg.get_value(self.x_max_input)
                if dpg.get_value(self.x_max_checkbox)
                else None,
            )
        
        return None

    def get_y_limits(self) -> Optional[Tuple[Optional[float], Optional[float]]]:
        if dpg.get_value(self.y_min_checkbox) or dpg.get_value(self.y_max_checkbox):
            return (
                dpg.get_value(self.y_min_input)
                if dpg.get_value(self.y_min_checkbox)
                else None,
                dpg.get_value(self.y_max_input)
                if dpg.get_value(self.y_max_checkbox)
                else None,
            )
        
        return None

    def update_dimensions_output(self, pixel_dimensions: List[str]):
        dpg.set_value(
            self.dimensions_output,
            f"{pixel_dimensions[0]} px * {pixel_dimensions[1]} px",
        )
        update_tooltip(
            dpg.get_item_user_data(self.dimensions_output),
            f"{pixel_dimensions[0]} px * {pixel_dimensions[1]} px",
        )


class PlotExporter:
    def __init__(self, config: Config):
        self.keybinding_handler: Optional[TemporaryKeybindingHandler] = None
        self.settings: Optional[PlotSettings] = None
        self.project: Optional[Project] = None
        self.texture_registry: Tag = dpg.generate_uuid()
        dpg.add_texture_registry(tag=self.texture_registry)
        
        self.window: Tag = dpg.generate_uuid()
        with dpg.window(
            label="Export plot",
            show=False,
            modal=True,
            on_close=self.close,
            tag=self.window,
        ):
            with dpg.group(horizontal=True):
                dpg.add_spacer(width=8)
                
                self.sidebar: Tag = dpg.generate_uuid()
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
                        self.settings_menu: SettingsMenu = SettingsMenu(
                            config.default_plot_export_settings,
                            label_pad=10,
                            refresh_callback=self.refresh,
                        )
                    
                    with dpg.child_window(border=False):
                        self.save_button: Tag = dpg.add_button(
                            label="Save as",
                            callback=lambda s, a, u: self.save(figure=u),
                            user_data=None,
                            width=-1,
                        )
                        attach_tooltip(tooltips.plotting.export_file)
                
                self.image_plot: Image = Image()

    def clear(self):
        figure: Optional[Figure] = dpg.get_item_user_data(self.save_button)
        if figure is not None:
            plt.close(figure)
            dpg.set_item_user_data(self.save_button, None)

        settings: PlotExportSettings = self.settings_menu.get_settings()
        if not settings.disable_preview:
            self.image_plot.clear()
            if settings.clear_registry:
                dpg.delete_item(self.texture_registry, children_only=True)

    def set_settings(self, settings: PlotExportSettings):
        self.settings_menu.set_settings(settings)

    def close(self):
        if self.keybinding_handler is not None:
            self.keybinding_handler.delete()
        
        dpg.hide_item(self.window)
        self.clear()
        signals.emit(Signal.UNBLOCK_KEYBINDINGS)

    def register_keybindings(self):
        from deareis.state import STATE

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
        callbacks[kb] = lambda: self.save(dpg.get_item_user_data(self.save_button))
        
        # Create the handler
        self.keybinding_handler = TemporaryKeybindingHandler(callbacks=callbacks)

    def show(self, settings: PlotSettings, project: Project):
        self.register_keybindings()
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
        signals.emit(Signal.BLOCK_KEYBINDINGS, window=self.window, window_object=self)
        self.refresh(self.settings_menu.get_settings())

    def create_preview_figure(
        self,
        width: float,
        height: float,
        dpi: int,
        preview_limit: int,
    ) -> Tuple[Figure, int, int]:
        assert isinstance(width, float) and width > 0.0, width
        assert isinstance(height, float) and height > 0.0, height
        assert isinstance(dpi, int) and dpi > 0, dpi
        
        pixel_width: int = floor(width * dpi)
        pixel_height: int = floor(height * dpi)

        # DEPRECATED
        # TODO: Remove at some point
        # if preview_limit > 0 and (
        #     pixel_width > preview_limit or pixel_height > preview_limit
        # ):
        #     if pixel_width >= pixel_height:
        #         pixel_height = floor(pixel_height / pixel_width * preview_limit)
        #         pixel_width = preview_limit
        #     else:
        #         pixel_width = floor(pixel_width / pixel_height * preview_limit)
        #         pixel_height = preview_limit
        
        width = pixel_width / dpi
        height = pixel_height / dpi
        figure: Figure = plt.figure(
            figsize=(
                width,
                height,
            ),
            dpi=dpi,
        )
        
        return (
            figure,
            pixel_width,
            pixel_height,
        )

    def create_final_figure(self, width: float, height: float, dpi: int) -> Figure:
        assert isinstance(width, float) and width > 0.0, width
        assert isinstance(height, float) and height > 0.0, height
        assert isinstance(dpi, int) and dpi > 0, dpi
        
        pixel_width: int = floor(width * dpi)
        pixel_height: int = floor(height * dpi)
        pixel_dimensions: List[str] = [
            format_number(float(pixel_width), decimals=0, exponent=False),
            format_number(float(pixel_height), decimals=0, exponent=False),
        ]
        self.settings_menu.update_dimensions_output(pixel_dimensions)
        
        figure: Figure = plt.figure(
            figsize=(
                width,
                height,
            ),
            dpi=dpi,
        )
        
        return figure

    def plot(self, figure: Figure, export_settings: PlotExportSettings):
        assert isinstance(figure, Figure), type(figure)
        assert isinstance(export_settings, PlotExportSettings), type(export_settings)
        assert self.settings is not None
        assert self.project is not None
        
        x_limits: Optional[
            Tuple[Optional[float], Optional[float]]
        ] = self.settings_menu.get_x_limits()
        
        y_limits: Optional[
            Tuple[Optional[float], Optional[float]]
        ] = self.settings_menu.get_y_limits()
        
        mpl.plot(
            self.settings,
            self.project,
            x_limits=x_limits,
            y_limits=y_limits,
            title=export_settings.show_title,
            legend=export_settings.show_legend,
            legend_loc=int(export_settings.legend_location),
            tight_layout=export_settings.has_tight_layout,
            grid=export_settings.show_grid,
            figure=figure,
            axes=[figure.gca()],
            num_per_decade=export_settings.num_per_decade,
        )

    def refresh(self, settings: PlotExportSettings):
        self.settings_menu.set_settings(settings)
        width: float = settings.width
        height: float = settings.height
        dpi: int = settings.dpi
        upi: float = plot_units_per_inch[settings.units]
        assert isinstance(width, float) and width > 0.0, width
        assert isinstance(height, float) and height > 0.0, height
        assert isinstance(dpi, int) and dpi > 0, dpi
        assert isinstance(upi, float) and upi > 0.0, upi
        
        self.clear()
        width = width / upi
        height = height / upi
        final_figure: Figure = self.create_final_figure(width, height, dpi)
        dpg.set_item_user_data(self.save_button, final_figure)
        self.plot(final_figure, settings)

        # Preview
        if not settings.disable_preview:
            preview_figure: Figure
            pixel_width: int
            pixel_height: int
            preview_figure, pixel_width, pixel_height = self.create_preview_figure(
                width,
                height,
                dpi=100,
                preview_limit=PlotPreviewLimit.NONE,
                # DEPRECATED
                # TODO: Remove at some point
                # preview_limit=(
                #     2 ** int(settings.preview_limit)
                #     if settings.preview_limit != PlotPreviewLimit.NONE
                #     else 0
                # ),
            )
            
            canvas: FigureCanvasAgg = FigureCanvasAgg(preview_figure)
            self.plot(preview_figure, settings)
            canvas.draw()
            buffer: NDArray[float32] = asarray(canvas.buffer_rgba()).astype(float32) / 255
            
            tag: Tag = dpg.add_raw_texture(
                pixel_width,
                pixel_height,
                buffer,
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
            plt.close(preview_figure)
            self.image_plot.queue_limits_adjustment()

        x_min: float
        x_max: float
        y_min: float
        y_max: float
        x_min, x_max = final_figure.gca().get_xlim()
        y_min, y_max = final_figure.gca().get_ylim()
        self.settings_menu.update_plot_limits(x_min, x_max, y_min, y_max)

    def save(self, figure: Optional[Figure], keybinding: bool = False):
        if figure is None:
            return

        extension: str = self.settings_menu.get_settings().extension
        self.close()
        dpg.split_frame(delay=33)
        signals.emit(
            Signal.SAVE_PLOT,
            figure=figure,
            default_extension=extension if extension in PLOT_EXTENSIONS else ".png",
            extensions=PLOT_EXTENSIONS,
        )
