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

from os.path import exists, dirname
from typing import (
    Dict,
    List,
    Optional,
    Tuple,
    Union,
)
from uuid import uuid4
import dearpygui.dearpygui as dpg
from deareis.enums import (
    PlotType,
)
from deareis.data import (
    DataSet,
    DRTResult,
    FitResult,
    PlotSettings,
    Project,
    SimulationResult,
    TestResult,
)
from deareis.gui import ProjectTab
from deareis.gui.file_dialog import FileDialog
from deareis.gui.plotting.copy_appearance import CopyPlotAppearance
from deareis.signals import Signal
from deareis.state import STATE
from deareis.themes import get_random_color_marker
from deareis.utility import calculate_window_position_dimensions
import deareis.signals as signals
import deareis.themes as themes


def new_plot_settings(*args, **kwargs):
    project: Optional[Project] = STATE.get_active_project()
    project_tab: Optional[ProjectTab] = STATE.get_active_project_tab()
    if project is None or project_tab is None:
        return
    existing_labels: List[str] = list(map(lambda _: _.get_label(), project.get_plots()))
    i: int = 1
    label: str = "Plot"
    while label in existing_labels:
        i += 1
        label = f"Plot ({i})"
    settings: PlotSettings = PlotSettings(
        label,
        PlotType.NYQUIST,
        [],
        {},
        {},
        {},
        {},
        {},
        uuid4().hex,
    )
    project.add_plot(settings)
    project_tab.populate_plots(project)
    signals.emit(Signal.SELECT_PLOT_SETTINGS, settings=settings)
    signals.emit(Signal.CREATE_PROJECT_SNAPSHOT)


def rename_plot_settings(*args, **kwargs):
    project: Optional[Project] = STATE.get_active_project()
    project_tab: Optional[ProjectTab] = STATE.get_active_project_tab()
    if project is None or project_tab is None:
        return
    settings: Optional[PlotSettings] = kwargs.get("settings")
    label: Optional[str] = kwargs.get("label")
    if settings is None or label is None:
        return
    project.edit_plot_label(settings, label)
    project_tab.populate_plots(project)
    signals.emit(Signal.SELECT_PLOT_SETTINGS, settings=settings)
    signals.emit(Signal.CREATE_PROJECT_SNAPSHOT)


def rename_plot_series(*args, **kwargs):
    project: Optional[Project] = STATE.get_active_project()
    project_tab: Optional[ProjectTab] = STATE.get_active_project_tab()
    if project is None or project_tab is None:
        return
    label: Optional[str] = kwargs.get("label")
    settings: Optional[PlotSettings] = kwargs.get("settings")
    uuid: Optional[str] = kwargs.get("uuid")
    series: Optional[Union[DataSet, TestResult, FitResult, SimulationResult]]
    series = kwargs.get("series")
    if label is None or settings is None or uuid is None or series is None:
        return
    settings.set_series_label(uuid, label)
    if label == "":
        label = series.get_label()
    elif label.strip() == "":
        label = ""
    project_tab.set_series_label(uuid, label)
    signals.emit(Signal.CREATE_PROJECT_SNAPSHOT)


def reorder_plot_series(*args, **kwargs):
    project: Optional[Project] = STATE.get_active_project()
    project_tab: Optional[ProjectTab] = STATE.get_active_project_tab()
    if project is None or project_tab is None:
        return
    settings: Optional[PlotSettings] = kwargs.get("settings")
    uuid: Optional[str] = kwargs.get("uuid")
    step: Optional[int] = kwargs.get("step")
    if step is None or settings is None or uuid is None:
        return
    assert abs(step) == 1
    assert uuid in settings.series_order
    index: int = settings.series_order.index(uuid)
    if index + step < 0 or index + step > len(settings.series_order) - 1:
        return
    settings.series_order.insert(index + step, settings.series_order.pop(index))
    signals.emit(Signal.SELECT_PLOT_SETTINGS, settings=settings, adjust_limits=False)
    signals.emit(Signal.CREATE_PROJECT_SNAPSHOT)


# TODO: Refactor into a class(?)
def modify_plot_series_theme(*args, **kwargs):
    project: Optional[Project] = STATE.get_active_project()
    project_tab: Optional[ProjectTab] = STATE.get_active_project_tab()
    if project is None or project_tab is None:
        return
    series: Optional[
        Union[DataSet, TestResult, FitResult, SimulationResult]
    ] = kwargs.get("series")
    settings: Optional[PlotSettings] = kwargs.get("settings")
    if series is None or settings is None:
        return
    window: int = dpg.generate_uuid()
    handler: int = dpg.generate_uuid()
    states: List[str] = []

    def accept_plot_series_theme():
        assert type(states) is list and len(states) == 2
        dpg.hide_item(window)
        dpg.delete_item(window)
        dpg.delete_item(handler)
        before: str
        after: str
        before, after = states
        if before == after:
            return
        signals.emit(Signal.SELECT_PLOT_SETTINGS, settings=settings)
        signals.emit(Signal.CREATE_PROJECT_SNAPSHOT)

    uuid: str = series.uuid
    marker_lookup: Dict[int, str] = {v: k for k, v in themes.PLOT_MARKERS.items()}
    color: List[float] = settings.get_series_color(uuid)
    marker: int = settings.get_series_marker(uuid)
    show_line: bool = settings.get_series_line(uuid)

    def hash_state() -> str:
        return f"{','.join(map(str, color))};{str(marker)};{str(show_line)}"

    states.extend([hash_state(), hash_state()])

    def update_color(new_color: List[float]):
        nonlocal states
        nonlocal color
        new_color = list(map(lambda _: _ * 255.0, new_color))
        color = new_color[:]
        settings.set_series_color(uuid, new_color)  # type: ignore
        states[1] = hash_state()

    color_edit: int = dpg.generate_uuid()

    def randomize_color():
        nonlocal states
        nonlocal color
        new_color: List[float]
        new_color, _ = get_random_color_marker({})
        while new_color == color:
            new_color, _ = get_random_color_marker({})
        color = new_color[:]
        settings.set_series_color(uuid, new_color)  # type: ignore
        states[1] = hash_state()
        dpg.set_value(color_edit, color)

    def update_marker(label: str):
        assert project is not None
        assert project_tab is not None
        assert settings is not None
        nonlocal states
        nonlocal marker
        marker = themes.PLOT_MARKERS.get(label, -1)
        settings.set_series_marker(uuid, marker)  # type: ignore
        project_tab.update_plots(
            settings,
            project.get_data_sets(),
            project.get_all_tests(),
            project.get_all_drts(),
            project.get_all_fits(),
            project.get_simulations(),
        )
        states[1] = hash_state()

    def update_line(state: bool):
        assert project is not None
        assert project_tab is not None
        assert settings is not None
        nonlocal states
        nonlocal show_line
        show_line = state
        settings.set_series_line(uuid, state)  # type: ignore
        project_tab.update_plots(
            settings,
            project.get_data_sets(),
            project.get_all_tests(),
            project.get_all_drts(),
            project.get_all_fits(),
            project.get_simulations(),
        )
        states[1] = hash_state()

    x: int
    y: int
    w: int
    h: int
    x, y, w, h = calculate_window_position_dimensions(200, 100)
    x, y = dpg.get_mouse_pos()
    y += 80
    with dpg.window(
        label="Edit appearance",
        modal=True,
        no_move=True,
        no_resize=True,
        pos=(
            x,
            y,
        ),
        width=w,
        height=h,
        on_close=accept_plot_series_theme,
        tag=window,
    ):
        with dpg.group(horizontal=True):
            dpg.add_text(" Color")
            dpg.add_color_edit(
                default_value=color,
                alpha_preview=dpg.mvColorEdit_AlphaPreviewHalf,
                no_inputs=True,
                alpha_bar=True,
                callback=lambda s, a, u: update_color(a),
                tag=color_edit,
            )
            dpg.add_button(
                label="Randomize",
                callback=randomize_color,
            )
        with dpg.group(horizontal=True):
            dpg.add_text("Marker")
            dpg.add_combo(
                items=["None"] + list(themes.PLOT_MARKERS.keys()),
                default_value=marker_lookup.get(marker, "None"),
                width=-1,
                callback=lambda s, a, u: update_marker(a),
            )
        with dpg.group(horizontal=True):
            dpg.add_text("  Line")
            dpg.add_checkbox(
                default_value=settings.get_series_line(uuid),
                callback=lambda s, a, u: update_line(a),
            )
    dpg.bind_item_theme(window, themes.transparent_modal_background)

    with dpg.handler_registry(tag=handler):
        dpg.add_key_release_handler(
            key=dpg.mvKey_Escape,
            callback=accept_plot_series_theme,
        )
    signals.emit(Signal.BLOCK_KEYBINDINGS, window=window, window_object=None)


def export_plot(*args, **kwargs):
    project: Optional[Project] = STATE.get_active_project()
    project_tab: Optional[ProjectTab] = STATE.get_active_project_tab()
    if project is None or project_tab is None:
        return
    settings: Optional[PlotSettings] = kwargs.get("settings")
    if settings is None:
        return
    # TODO: Get current x- and y-limits
    STATE.show_plot_exporter(settings, project)


def save_plot(*args, **kwargs):
    fig = kwargs["figure"]  # Optional[matplotlib.figure.Figure]
    if fig is None:
        return
    STATE.close_plot_exporter()

    def save(*args, **kwargs):
        path: str = kwargs["path"]
        directory: str = dirname(path)
        if exists(directory):
            STATE.latest_plot_directory = directory
        fig.savefig(path)

    FileDialog(
        cwd=STATE.latest_plot_directory,
        label="Select file path",
        callback=lambda *a, **k: save(*a, **k),
        default_extension=kwargs["default_extension"],
        extensions=kwargs["extensions"],
        save=True,
    )


def select_plot_appearance_settings(*args, **kwargs):
    project: Optional[Project] = STATE.get_active_project()
    project_tab: Optional[ProjectTab] = STATE.get_active_project_tab()
    if project is None or project_tab is None:
        return
    settings: Optional[PlotSettings] = kwargs.get("settings")
    if settings is None or len(settings.series_order) == 0:
        return
    if len(project.get_plots()) < 2:
        return
    CopyPlotAppearance(settings, project)


def copy_plot_appearance_settings(*args, **kwargs):
    project: Optional[Project] = STATE.get_active_project()
    project_tab: Optional[ProjectTab] = STATE.get_active_project_tab()
    if project is None or project_tab is None:
        return
    changes: Optional[Dict[str, Tuple[str, List[float], int, bool]]] = kwargs.get(
        "changes"
    )
    settings: Optional[PlotSettings] = kwargs.get("settings")
    if changes is None or settings is None:
        return
    signals.emit(Signal.SHOW_BUSY_MESSAGE, message="Updating plots")
    uuid: str
    label: str
    color: List[float]
    marker: str
    line: bool
    for uuid, (label, color, marker, line) in changes.items():
        settings.set_series_label(uuid, label)
        settings.set_series_color(uuid, color)
        themes.update_plot_series_theme_color(
            settings.get_series_theme(uuid), settings.get_series_color(uuid)
        )
        settings.set_series_marker(uuid, marker)
        themes.update_plot_series_theme_marker(
            settings.get_series_theme(uuid), settings.get_series_marker(uuid)
        )
        settings.set_series_line(uuid, line)
    signals.emit(Signal.SELECT_PLOT_SETTINGS, settings=settings)
    signals.emit(Signal.CREATE_PROJECT_SNAPSHOT)
    signals.emit(Signal.HIDE_BUSY_MESSAGE)


def select_plot_settings(*args, **kwargs):
    project: Optional[Project] = STATE.get_active_project()
    project_tab: Optional[ProjectTab] = STATE.get_active_project_tab()
    if project is None or project_tab is None:
        return
    settings: Optional[PlotSettings] = kwargs.get("settings")
    if settings is None:
        return
    is_busy_message_visible: bool = STATE.is_busy_message_visible()
    if not is_busy_message_visible:
        signals.emit(Signal.SHOW_BUSY_MESSAGE, message="Updating plots")
    project_tab.select_plot(
        settings,
        project.get_data_sets(),
        project.get_all_tests(),
        project.get_all_drts(),
        project.get_all_fits(),
        project.get_simulations(),
        adjust_limits=kwargs.get("adjust_limits", True),
        plot_only=kwargs.get("plot_only", False),
    )
    if not is_busy_message_visible:
        signals.emit(Signal.HIDE_BUSY_MESSAGE)


def select_plot_type(*args, **kwargs):
    project: Optional[Project] = STATE.get_active_project()
    project_tab: Optional[ProjectTab] = STATE.get_active_project_tab()
    if project is None or project_tab is None:
        return
    settings: Optional[PlotSettings] = kwargs.get("settings")
    if settings is None:
        return
    plot_type: Optional[PlotType] = kwargs.get("plot_type")
    if plot_type is None:
        return
    signals.emit(Signal.SHOW_BUSY_MESSAGE, message="Updating plots")
    settings.set_type(plot_type)
    signals.emit(Signal.SELECT_PLOT_SETTINGS, settings=settings, plot_only=True)
    signals.emit(Signal.CREATE_PROJECT_SNAPSHOT)
    signals.emit(Signal.HIDE_BUSY_MESSAGE)


def toggle_plot_series(*args, **kwargs):
    project: Optional[Project] = STATE.get_active_project()
    project_tab: Optional[ProjectTab] = STATE.get_active_project_tab()
    if project is None or project_tab is None:
        return
    settings: Optional[PlotSettings] = kwargs.get("settings")
    if settings is None:
        return
    signals.emit(Signal.SHOW_BUSY_MESSAGE, message="Updating plots")
    enabled: bool = kwargs.get("enabled", False)
    data_sets: Optional[List[DataSet]] = kwargs.get("data_sets")
    tests: Optional[List[TestResult]] = kwargs.get("tests")
    drts: Optional[List[DRTResult]] = kwargs.get("drts")
    fits: Optional[List[FitResult]] = kwargs.get("fits")
    simulations: Optional[List[SimulationResult]] = kwargs.get("simulations")
    if data_sets is not None:
        if enabled:
            list(map(settings.add_series, data_sets))
        else:
            list(map(lambda _: settings.remove_series(_.uuid), data_sets))
    if tests is not None:
        if enabled:
            list(map(settings.add_series, tests))
        else:
            list(map(lambda _: settings.remove_series(_.uuid), tests))
    if drts is not None:
        if enabled:
            list(map(settings.add_series, drts))
        else:
            list(map(lambda _: settings.remove_series(_.uuid), drts))
    if fits is not None:
        if enabled:
            list(map(settings.add_series, fits))
        else:
            list(map(lambda _: settings.remove_series(_.uuid), fits))
    if simulations is not None:
        if enabled:
            list(map(settings.add_series, simulations))
        else:
            list(map(lambda _: settings.remove_series(_.uuid), simulations))
    signals.emit(Signal.SELECT_PLOT_SETTINGS, settings=settings)
    signals.emit(Signal.CREATE_PROJECT_SNAPSHOT)
    signals.emit(Signal.HIDE_BUSY_MESSAGE)


def delete_plot_settings(*args, **kwargs):
    project: Optional[Project] = STATE.get_active_project()
    project_tab: Optional[ProjectTab] = STATE.get_active_project_tab()
    if project is None or project_tab is None:
        return
    settings: Optional[PlotSettings] = kwargs.get("settings")
    if settings is None:
        return
    signals.emit(Signal.SHOW_BUSY_MESSAGE, message="Deleting plot")
    project.delete_plot(settings)
    plots: List[PlotSettings] = project.get_plots()
    if not plots:
        signals.emit(Signal.NEW_PLOT_SETTINGS)
    else:
        project_tab.populate_plots(project)
        signals.emit(Signal.SELECT_PLOT_SETTINGS, settings=plots[0])
    signals.emit(Signal.CREATE_PROJECT_SNAPSHOT)
    signals.emit(Signal.HIDE_BUSY_MESSAGE)
