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
    Set,
    Type,
)
from pyimpspec import (
    get_default_num_procs,
    set_default_num_procs,
)
import dearpygui.dearpygui as dpg
from deareis.utility import calculate_window_position_dimensions
from deareis.tooltips import attach_tooltip
import deareis.tooltips as tooltips
from deareis.gui.project import ProjectTab
from deareis.data.plotting import PlotExportSettings
from deareis.data import (
    DRTSettings,
    FitSettings,
    KramersKronigSettings,
    KramersKronigSuggestionSettings,
    SimulationSettings,
    ZHITSettings,
)
from deareis.config import (
    DEFAULT_KRAMERS_KRONIG_SETTINGS,
    DEFAULT_ZHIT_SETTINGS,
    DEFAULT_DRT_SETTINGS,
    DEFAULT_FIT_SETTINGS,
    DEFAULT_SIMULATION_SETTINGS,
    DEFAULT_PLOT_EXPORT_SETTINGS,
)
from deareis.gui.kramers_kronig import SettingsMenu as KramersKronigSettingsMenu
from deareis.gui.kramers_kronig.exploratory_results import SuggestionSettingsMenu as KramersKronigSuggestionSettingsMenu
from deareis.gui.zhit import SettingsMenu as ZHITSettingsMenu
from deareis.gui.drt import SettingsMenu as DRTSettingsMenu
from deareis.gui.fitting import SettingsMenu as FitSettingsMenu
from deareis.gui.simulation import SettingsMenu as SimulationSettingsMenu
from deareis.gui.plotting.export import SettingsMenu as PlotExportSettingsMenu
from deareis.signals import Signal
import deareis.signals as signals
from pyimpspec import (
    Element,
    get_elements,
)
from pyimpspec.circuit.registry import reset_default_parameter_values
from deareis.typing.helpers import Tag



def section_spacer():
    dpg.add_spacer(height=8)


def general_settings(label_pad: int, state):
    with dpg.collapsing_header(label="General", default_open=True):
        auto_backup_interval: Tag = dpg.generate_uuid()
        num_procs_input: Tag = dpg.generate_uuid()

        def update_auto_backup_interval(value: int):
            state.config.auto_backup_interval = value
            set_default_num_procs(value)

        with dpg.group(horizontal=True):
            dpg.add_text("Auto-backup interval".rjust(label_pad))
            attach_tooltip(tooltips.general.auto_backup_interval)
            dpg.add_input_int(
                default_value=state.config.auto_backup_interval,
                label="actions",
                min_value=0,
                min_clamped=True,
                step=0,
                on_enter=True,
                callback=lambda s, a, u: update_auto_backup_interval(a),
                width=-54,
                tag=auto_backup_interval,
            )

        def update_num_procs(value: int):
            state.config.num_procs = value

        with dpg.group(horizontal=True):
            dpg.add_text("Number of processes".rjust(label_pad))
            attach_tooltip(tooltips.general.num_procs.format(get_default_num_procs()))
            dpg.add_input_int(
                default_value=state.config.num_procs,
                min_value=0,
                min_clamped=True,
                step=0,
                on_enter=True,
                callback=lambda s, a, u: update_num_procs(a),
                width=-54,
                tag=num_procs_input,
            )
        section_spacer()


def kramers_kronig_tab_settings(label_pad: int, state) -> Callable:
    project_tab: Optional[ProjectTab] = state.get_active_project_tab()

    default_settings: KramersKronigSettings
    if project_tab is not None:
        default_settings = project_tab.get_test_settings()
    else:
        default_settings = state.config.default_kramers_kronig_settings

    with dpg.collapsing_header(label="Kramers-Kronig tab", default_open=True):
        settings_menu: KramersKronigSettingsMenu = KramersKronigSettingsMenu(
            default_settings=default_settings,
            label_pad=label_pad,
            suggestion_settings=None,
            limited=True,
            state=state,
        )

        with dpg.group(horizontal=True):
            dpg.add_text("".rjust(label_pad))
            dpg.add_button(
                label="Restore defaults",
                callback=lambda s, a, u: settings_menu.set_settings(
                    DEFAULT_KRAMERS_KRONIG_SETTINGS,
                ),
            )

        section_spacer()

        suggestion_settings_menu: KramersKronigSuggestionSettingsMenu = (
            KramersKronigSuggestionSettingsMenu(
                default_settings=default_settings.suggestion_settings,
                label_pad=label_pad,
            )
        )

        with dpg.group(horizontal=True):
            dpg.add_text("".rjust(label_pad))
            dpg.add_button(
                label="Restore defaults",
                callback=lambda s, a, u: suggestion_settings_menu.set_settings(
                    DEFAULT_KRAMERS_KRONIG_SETTINGS.suggestion_settings,
                ),
            )

        section_spacer()

    def callback():
        suggestion_settings: KramersKronigSuggestionSettings = (
            suggestion_settings_menu.get_settings()
        )
        state.config.default_kramers_kronig_suggestion_settings = suggestion_settings
        state.kramers_kronig_suggestion_settings = suggestion_settings

        settings: KramersKronigSettings = settings_menu.get_settings()
        state.config.default_kramers_kronig_settings = settings

        project_tab: ProjectTab
        for project_tab in state.project_tabs.values():
            project_tab.set_test_settings(settings)

    return callback


def zhit_tab_settings(label_pad: int, state) -> Callable:
    project_tab: Optional[ProjectTab] = state.get_active_project_tab()

    default_settings: ZHITSettings
    if project_tab is not None:
        default_settings = project_tab.get_zhit_settings()
    else:
        default_settings = state.config.default_zhit_settings

    with dpg.collapsing_header(label="Z-HIT analysis tab", default_open=True):
        settings_menu: ZHITSettingsMenu = ZHITSettingsMenu(
            default_settings=default_settings,
            label_pad=label_pad,
        )

        with dpg.group(horizontal=True):
            dpg.add_text("".rjust(label_pad))
            dpg.add_button(
                label="Restore defaults",
                callback=lambda s, a, u: settings_menu.set_settings(
                    DEFAULT_ZHIT_SETTINGS,
                ),
            )

        section_spacer()

    def callback():
        settings: ZHITSettings = settings_menu.get_settings()
        state.config.default_zhit_settings = settings

        project_tab: ProjectTab
        for project_tab in state.project_tabs.values():
            project_tab.set_zhit_settings(settings)

    return callback


def drt_tab_settings(label_pad: int, state) -> Callable:
    project_tab: Optional[ProjectTab] = state.get_active_project_tab()

    default_settings:DRTSettings 
    if project_tab is not None:
        default_settings = project_tab.get_drt_settings()
    else:
        default_settings = state.config.default_drt_settings

    with dpg.collapsing_header(label="DRT analysis tab", default_open=True):
        settings_menu: DRTSettingsMenu = DRTSettingsMenu(
            default_settings=default_settings,
            label_pad=label_pad,
        )

        with dpg.group(horizontal=True):
            dpg.add_text("".rjust(label_pad))
            dpg.add_button(
                label="Restore defaults",
                callback=lambda s, a, u: settings_menu.set_settings(
                    DEFAULT_DRT_SETTINGS
                ),
            )
        
        section_spacer()

    def callback():
        settings: DRTSettings = settings_menu.get_settings()
        state.config.default_drt_settings = settings

        project_tab: ProjectTab
        for project_tab in state.project_tabs.values():
            project_tab.set_drt_settings(settings)

    return callback


def fitting_tab_settings(label_pad: int, state) -> Callable:
    project_tab: Optional[ProjectTab] = state.get_active_project_tab()

    default_settings: FitSettings
    if project_tab is not None:
        default_settings = project_tab.get_fit_settings()
    else:
        default_settings = state.config.default_fit_settings

    with dpg.collapsing_header(label="Fitting tab", default_open=True):
        settings_menu: FitSettingsMenu = FitSettingsMenu(
            default_settings=default_settings,
            label_pad=label_pad,
        )

        with dpg.group(horizontal=True):
            dpg.add_text("".rjust(label_pad))
            dpg.add_button(
                label="Restore defaults",
                callback=lambda s, a, u: settings_menu.set_settings(
                    DEFAULT_FIT_SETTINGS,
                ),
            )
        section_spacer()

    def callback():
        settings: FitSettings = settings_menu.get_settings()
        state.config.default_fit_settings = settings

        project_tab: ProjectTab
        for project_tab in state.project_tabs.values():
            project_tab.set_fit_settings(settings)

    return callback


def simulation_tab_settings(label_pad: int, state) -> Callable:
    project_tab: Optional[ProjectTab] = state.get_active_project_tab()

    default_settings: SimulationSettings
    if project_tab is not None:
        default_settings = project_tab.get_simulation_settings()
    else:
        default_settings = state.config.default_simulation_settings

    with dpg.collapsing_header(label="Simulation tab", default_open=True):
        settings_menu: SimulationSettingsMenu = SimulationSettingsMenu(
            default_settings=default_settings,
            label_pad=label_pad,
        )

        with dpg.group(horizontal=True):
            dpg.add_text("".rjust(label_pad))
            dpg.add_button(
                label="Restore defaults",
                callback=lambda s, a, u: settings_menu.set_settings(
                    DEFAULT_SIMULATION_SETTINGS,
                ),
            )

        section_spacer()

    def callback():
        settings: SimulationSettings = settings_menu.get_settings()
        state.config.default_simulation_settings = settings

        project_tab: ProjectTab
        for project_tab in state.project_tabs.values():
            project_tab.set_simulation_settings(settings)

    return callback


def plotting_tab_settings(label_pad: int, state) -> Callable:
    with dpg.collapsing_header(label="Plotting tab - Export plot", default_open=True):
        settings_menu: PlotExportSettingsMenu = PlotExportSettingsMenu(
            default_settings=state.config.default_plot_export_settings,
            label_pad=label_pad,
            refresh_callback=None,
        )

        with dpg.group(horizontal=True):
            dpg.add_text("".rjust(label_pad))
            dpg.add_button(
                label="Restore defaults",
                callback=lambda s, a, u: settings_menu.set_settings(
                    DEFAULT_PLOT_EXPORT_SETTINGS,
                ),
            )
        
        section_spacer()

    def callback():
        settings: PlotExportSettings = settings_menu.get_settings()
        state.config.default_plot_export_settings = settings
        state.plot_exporter.set_settings(settings)

    return callback


def circuit_element_parameters_settings(label_pad: int, state) -> Callable:
    def reset_callback(element: Type[Element], input_tags: Dict[str, int]):
        reset_default_parameter_values(element)
        default_values: Dict[str, float] = element.get_default_values()

        key: str
        tag: int
        for key, tag in input_tags.items():
            dpg.set_value(tag, default_values[key])

    all_elements: Dict[str, Type[Element]] = get_elements(default_only=True)
    parameter_label_lengths: Set[int] = set()
    key: str
    element: Type[Element]
    for key, element in all_elements.items():
        parameter_label_lengths.update(
            [len(k) for k in element.get_default_values().keys()]
        )
    parameter_label_pad: int = max(parameter_label_lengths)

    with dpg.collapsing_header(label="Circuit element parameters", default_open=True):
        for key, element in all_elements.items():
            label: str = element.get_description()
            parameter_descriptions: Dict[str, str] = element.get_value_descriptions()
            parameter_units: Dict[str, str] = element.get_units()

            with dpg.collapsing_header(label=label, default_open=False):
                input_tags: List[int] = {}

                value: float
                for key, value in element.get_default_values().items():
                    description: str = parameter_descriptions.get(key, "N/A")
                    units: str = parameter_units.get(key, "")
                    with dpg.group(horizontal=True):
                        dpg.add_text(key.rjust(parameter_label_pad))
                        attach_tooltip(
                            description + (f"\n\nUnits: {units}" if units else "")
                        )
                        input_tags[key] = dpg.add_input_float(
                            format="%.4g",
                            step=0,
                            default_value=value,
                            callback=lambda s, a, u: u[0].set_default_values(
                                u[1],
                                a,
                            ),
                            user_data=(element, key),
                            width=-1,
                        )

                with dpg.group(horizontal=True):
                    dpg.add_text("".rjust(label_pad))
                    dpg.add_button(
                        label="Restore defaults",
                        callback=lambda s, a, u: reset_callback(*u),
                        user_data=(element, input_tags),
                    )
                section_spacer()

        section_spacer()

    def callback():
        key: str
        element: Type[Element]
        for key, element in get_elements().items():
            state.config.default_element_parameters[key] = element.get_default_values()

    return callback


class DefaultsSettings:
    def __init__(self, state):
        self.settings_update_callbacks: List[Callable] = []
        self.create_window(state)
        self.register_keybindings()

    def register_keybindings(self):
        self.key_handler: Tag = dpg.generate_uuid()
        with dpg.handler_registry(tag=self.key_handler):
            dpg.add_key_release_handler(
                key=dpg.mvKey_Escape,
                callback=self.close,
            )

    def create_window(self, state):
        x: int
        y: int
        w: int
        h: int
        x, y, w, h = calculate_window_position_dimensions(390, 540)
        self.window: Tag = dpg.generate_uuid()
        with dpg.window(
            label="Settings - defaults",
            modal=True,
            pos=(x, y),
            width=w,
            height=h,
            no_resize=True,
            on_close=self.close,
            tag=self.window,
        ):
            label_pad: int = 24
            general_settings(label_pad, state)
            self.settings_update_callbacks.append(
                kramers_kronig_tab_settings(label_pad, state)
            )
            self.settings_update_callbacks.append(
                zhit_tab_settings(
                    label_pad,
                    state,
                )
            )
            self.settings_update_callbacks.append(
                drt_tab_settings(
                    label_pad,
                    state,
                )
            )
            self.settings_update_callbacks.append(
                fitting_tab_settings(label_pad, state)
            )
            self.settings_update_callbacks.append(
                simulation_tab_settings(label_pad, state)
            )
            self.settings_update_callbacks.append(
                plotting_tab_settings(label_pad, state)
            )
            self.settings_update_callbacks.append(
                circuit_element_parameters_settings(label_pad, state)
            )

        signals.emit(Signal.BLOCK_KEYBINDINGS, window=self.window, window_object=self)

    def close(self):
        callback: Callable
        for callback in self.settings_update_callbacks:
            callback()

        if dpg.does_item_exist(self.window):
            dpg.delete_item(self.window)

        if dpg.does_item_exist(self.key_handler):
            dpg.delete_item(self.key_handler)

        signals.emit(Signal.UNBLOCK_KEYBINDINGS)


def show_defaults_settings_window(state):
    DefaultsSettings(state)
