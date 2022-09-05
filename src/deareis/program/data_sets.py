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

from os.path import dirname
from traceback import format_exc
from typing import (
    Dict,
    List,
    Optional,
)
from pyimpspec.data.formats import UnsupportedFileFormat
from pyimpspec.data import get_parsers
import pyimpspec
from deareis.data import (
    DRTResult,
    DataSet,
    FitResult,
    Project,
    TestResult,
)
from deareis.enums import Context
from deareis.gui import ProjectTab
from deareis.gui.data_sets.average_data_sets import AverageDataSets
from deareis.gui.data_sets.copy_mask import CopyMask
from deareis.gui.data_sets.subtract_impedance import SubtractImpedance
from deareis.gui.data_sets.toggle_data_points import ToggleDataPoints
from deareis.gui.file_dialog import FileDialog
from deareis.signals import Signal
from deareis.state import STATE
import deareis.signals as signals


def select_data_set(*args, **kwargs):
    project: Optional[Project] = STATE.get_active_project()
    project_tab: Optional[ProjectTab] = STATE.get_active_project_tab()
    if project is None or project_tab is None:
        return
    is_busy_message_visible: bool = STATE.is_busy_message_visible()
    if not is_busy_message_visible:
        signals.emit(Signal.SHOW_BUSY_MESSAGE, message="Loading data set")
    data: Optional[DataSet] = kwargs.get("data")
    project_tab.select_data_set(data)
    project_tab.populate_tests(project, data)
    project_tab.populate_drts(project, data)
    project_tab.populate_fits(project, data)
    project_tab.populate_simulations(project)
    if not is_busy_message_visible:
        signals.emit(Signal.HIDE_BUSY_MESSAGE)


def load_data_set_files(*args, **kwargs):
    project: Optional[Project] = STATE.get_active_project()
    project_tab: Optional[ProjectTab] = STATE.get_active_project_tab()
    if project is None or project_tab is None:
        return
    paths: List[str] = kwargs.get("paths")
    if not paths:
        return
    existing_labels: List[str] = list(
        map(lambda _: _.get_label(), project.get_data_sets())
    )
    parsing_errors: Dict[str, str] = {}
    loaded_data: bool = False
    num_paths: int = len(paths)
    n: int
    path: str
    for n, path in enumerate(paths):
        signals.emit(
            Signal.SHOW_BUSY_MESSAGE,
            message=f"Loading data: {n + 1}/{num_paths}",
            progress=n / num_paths,
        )
        try:
            data_sets: List[pyimpspec.DataSet] = pyimpspec.parse_data(path)
        except UnsupportedFileFormat:
            parsing_errors[path] = "Unsupported file type!\n"
            continue
        except Exception:
            parsing_errors[path] = format_exc()
            continue
        data: DataSet
        for data in map(lambda _: DataSet.from_dict(_.to_dict()), data_sets):
            label: str = data.get_label().strip()
            if label == "":
                label = "Data set"
            i: int = 0
            while label in existing_labels:
                i += 1
                label = f"{data.get_label()} ({i})"
            existing_labels.append(label)
            data.set_label(label)
            project.add_data_set(data)
        loaded_data = True
    signals.emit(Signal.HIDE_BUSY_MESSAGE)
    STATE.latest_data_set_directory = dirname(path)
    if loaded_data:
        project_tab.populate_data_sets(project)
        signals.emit(Signal.SELECT_DATA_SET, data=data)
        signals.emit(
            Signal.SELECT_PLOT_SETTINGS,
            settings=project_tab.get_active_plot(),
        )
        signals.emit(Signal.CREATE_PROJECT_SNAPSHOT)
    if parsing_errors:
        total_traceback: str = ""
        traceback: str
        for path, traceback in parsing_errors.items():
            total_traceback += f"{traceback}\nThe exception above was encountered while parsing '{path}'.\n\n"
        signals.emit(
            Signal.SHOW_ERROR_MESSAGE,
            traceback=total_traceback.strip(),
            message="""
Encountered error(s) while parsing data file(s). The file(s) might be malformed, corrupted, or not supported by this version of DearEIS.
            """.strip(),
        )


def select_data_set_files(*args, **kwargs):
    project: Optional[Project] = STATE.get_active_project()
    project_tab: Optional[ProjectTab] = STATE.get_active_project_tab()
    if project is None or project_tab is None:
        return
    FileDialog(
        cwd=STATE.latest_data_set_directory,
        label="Select data file(s)",
        callback=lambda *a, **k: signals.emit(Signal.LOAD_DATA_SET_FILES, *a, **k),
        extensions=[".*"] + list(get_parsers().keys()),
    )


def rename_data_set(*args, **kwargs):
    project: Optional[Project] = STATE.get_active_project()
    project_tab: Optional[ProjectTab] = STATE.get_active_project_tab()
    if project is None or project_tab is None:
        return
    label: Optional[str] = kwargs.get("label")
    data: Optional[DataSet] = kwargs.get("data")
    if label is None or data is None:
        return
    if label.strip() == data.get_label():
        return
    project.edit_data_set_label(data, label)
    project_tab.populate_data_sets(project)
    signals.emit(Signal.SELECT_PLOT_SETTINGS, settings=project_tab.get_active_plot())
    signals.emit(Signal.SELECT_DATA_SET, data=data)
    signals.emit(
        Signal.SELECT_SIMULATION_RESULT,
        simulation=project_tab.get_active_simulation(),
        data=project_tab.get_active_data_set(context=Context.SIMULATION_TAB),
    )
    signals.emit(Signal.CREATE_PROJECT_SNAPSHOT)


def modify_data_set_path(*args, **kwargs):
    project: Optional[Project] = STATE.get_active_project()
    project_tab: Optional[ProjectTab] = STATE.get_active_project_tab()
    if project is None or project_tab is None:
        return
    path: Optional[str] = kwargs.get("path")
    data: Optional[DataSet] = kwargs.get("data")
    if path is None or data is None:
        return
    project.edit_data_set_path(data, path.strip())
    signals.emit(Signal.CREATE_PROJECT_SNAPSHOT)


def delete_data_set(*args, **kwargs):
    project: Optional[Project] = STATE.get_active_project()
    project_tab: Optional[ProjectTab] = STATE.get_active_project_tab()
    if project is None or project_tab is None:
        return
    data: Optional[DataSet] = kwargs.get("data")
    if data is None:
        return
    signals.emit(Signal.SHOW_BUSY_MESSAGE, message="Deleting data set")
    project.delete_data_set(data)
    project_tab.populate_data_sets(project)
    signals.emit(Signal.SELECT_PLOT_SETTINGS, settings=project_tab.get_active_plot())
    lookup: Dict[str, DataSet] = {_.get_label(): _ for _ in project.get_data_sets()}
    labels: List[str] = list(lookup.keys())
    signals.emit(
        Signal.SELECT_DATA_SET,
        data=lookup[labels[0]] if labels else None,
    )
    data = project_tab.get_active_data_set(context=Context.SIMULATION_TAB)
    if data is not None and data.get_label() not in labels:
        data = None
    signals.emit(
        Signal.SELECT_SIMULATION_RESULT,
        simulation=project_tab.get_active_simulation(),
        data=data,
    )
    signals.emit(Signal.CREATE_PROJECT_SNAPSHOT)
    signals.emit(Signal.HIDE_BUSY_MESSAGE)


def toggle_data_point(*args, **kwargs):
    project: Optional[Project] = STATE.get_active_project()
    project_tab: Optional[ProjectTab] = STATE.get_active_project_tab()
    if project is None or project_tab is None:
        return
    state: Optional[bool] = kwargs.get("state")
    index: Optional[int] = kwargs.get("index")
    data: Optional[DataSet] = kwargs.get("data")
    if state is None or index is None or data is None:
        return
    signals.emit(
        Signal.SHOW_BUSY_MESSAGE,
        message="Toggling data point",
    )
    mask: Dict[int, bool] = data.get_mask()
    mask[index] = state
    data.set_mask(mask)
    signals.emit(Signal.SELECT_PLOT_SETTINGS, settings=project_tab.get_active_plot())
    signals.emit(Signal.SELECT_DATA_SET, data=data)
    signals.emit(Signal.CREATE_PROJECT_SNAPSHOT)
    signals.emit(Signal.HIDE_BUSY_MESSAGE)


def apply_data_set_mask(*args, **kwargs):
    project: Optional[Project] = STATE.get_active_project()
    project_tab: Optional[ProjectTab] = STATE.get_active_project_tab()
    if project is None or project_tab is None:
        return
    mask: Optional[Dict[int, bool]] = kwargs.get("mask")
    data: Optional[DataSet] = kwargs.get("data")
    if mask is None or data is None:
        return
    data.set_mask(mask)
    signals.emit(Signal.SELECT_PLOT_SETTINGS, settings=project_tab.get_active_plot())
    signals.emit(Signal.SELECT_DATA_SET, data=data)
    test: Optional[TestResult] = kwargs.get("test")
    drt: Optional[DRTResult] = kwargs.get("drt")
    fit: Optional[FitResult] = kwargs.get("fit")
    if test is not None:
        signals.emit(Signal.SELECT_TEST_RESULT, data=data, test=test)
    elif drt is not None:
        signals.emit(Signal.SELECT_DRT_RESULT, data=data, drt=drt)
    elif fit is not None:
        signals.emit(Signal.SELECT_FIT_RESULT, data=data, fit=fit)
    signals.emit(Signal.CREATE_PROJECT_SNAPSHOT)


def select_data_sets_to_average(*args, **kwargs):
    project: Optional[Project] = STATE.get_active_project()
    project_tab: Optional[ProjectTab] = STATE.get_active_project_tab()
    if project is None or project_tab is None:
        return

    def add_data(data: DataSet):
        assert project is not None
        assert project_tab is not None
        project.add_data_set(data)
        project_tab.populate_data_sets(project)
        signals.emit(
            Signal.SELECT_PLOT_SETTINGS, settings=project_tab.get_active_plot()
        )
        signals.emit(Signal.SELECT_DATA_SET, data=data)
        signals.emit(Signal.CREATE_PROJECT_SNAPSHOT)

    data_sets: List[DataSet] = project.get_data_sets()
    if len(data_sets) < 2:
        return

    average_data_sets_window: AverageDataSets = AverageDataSets(
        data_sets=data_sets,
        callback=add_data,
    )
    signals.emit(
        Signal.BLOCK_KEYBINDINGS,
        window=average_data_sets_window.window,
        window_object=average_data_sets_window,
    )


def select_data_points_to_toggle(*args, **kwargs):
    project: Optional[Project] = STATE.get_active_project()
    project_tab: Optional[ProjectTab] = STATE.get_active_project_tab()
    data: Optional[DataSet] = kwargs.get("data")
    if project is None or project_tab is None or data is None:
        return
    toggle_data_points_window: ToggleDataPoints = ToggleDataPoints(
        data=data,
        callback=lambda m: signals.emit(
            Signal.APPLY_DATA_SET_MASK,
            mask=m,
            data=data,
        ),
    )
    signals.emit(
        Signal.BLOCK_KEYBINDINGS,
        window=toggle_data_points_window.window,
        window_object=toggle_data_points_window,
    )


def select_data_set_mask_to_copy(*args, **kwargs):
    project: Optional[Project] = STATE.get_active_project()
    project_tab: Optional[ProjectTab] = STATE.get_active_project_tab()
    data: Optional[DataSet] = kwargs.get("data")
    if project is None or project_tab is None or data is None:
        return
    data_sets: List[DataSet] = project.get_data_sets()
    if len(data_sets) < 2:
        return
    copy_mask_window: CopyMask = CopyMask(
        data=data,
        data_sets=data_sets,
        callback=lambda m: signals.emit(
            Signal.APPLY_DATA_SET_MASK,
            mask=m,
            data=data,
        ),
    )
    signals.emit(
        Signal.BLOCK_KEYBINDINGS,
        window=copy_mask_window.window,
        window_object=copy_mask_window,
    )


def select_impedance_to_subtract(*args, **kwargs):
    project: Optional[Project] = STATE.get_active_project()
    project_tab: Optional[ProjectTab] = STATE.get_active_project_tab()
    data: Optional[DataSet] = kwargs.get("data")
    if project is None or project_tab is None or data is None:
        return

    def replace_data(new: DataSet):
        assert project is not None
        assert project_tab is not None
        assert data is not None
        project.replace_data_set(data, new)
        project_tab.populate_data_sets(project)
        signals.emit(
            Signal.SELECT_PLOT_SETTINGS, settings=project_tab.get_active_plot()
        )
        signals.emit(Signal.SELECT_DATA_SET, data=new)
        signals.emit(
            Signal.SELECT_SIMULATION_RESULT,
            simulation=project_tab.get_active_simulation(),
            data=project_tab.get_active_data_set(context=Context.SIMULATION_TAB),
        )
        signals.emit(Signal.CREATE_PROJECT_SNAPSHOT)

    subtract_impedance_window: SubtractImpedance = SubtractImpedance(
        data=data,
        data_sets=project.get_data_sets(),
        callback=replace_data,
    )
    signals.emit(
        Signal.BLOCK_KEYBINDINGS,
        window=subtract_impedance_window.window,
        window_object=subtract_impedance_window,
    )
