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

from traceback import format_exc
from typing import (
    List,
    Optional,
    Tuple,
    Union,
)
import dearpygui.dearpygui as dpg
from pyimpspec.exceptions import (
    KramersKronigError,
    FittingError,
    DRTError,
    ZHITError,
)
from deareis.data import (
    DRTSettings,
    DataSet,
    FitSettings,
    Project,
    TestSettings,
    ZHITSettings,
)
from .kramers_kronig import perform_test
from .zhit import perform_zhit
from .drt import perform_drt
from .fitting import perform_fit
from deareis.gui.batch_analysis import BatchAnalysis
from deareis.signals import Signal
import deareis.signals as signals
from deareis.state import STATE


Settings = Union[TestSettings, ZHITSettings, DRTSettings, FitSettings]


def batch_perform_analyses(data_sets: List[DataSet], settings: Settings):
    errors: List[Tuple[DataSet, str]] = []
    kwargs = {
        "settings": settings,
        "batch": True,
    }
    data: DataSet
    for data in data_sets:
        if isinstance(settings, TestSettings):
            try:
                perform_test(data=data, **kwargs)
            except (FittingError, KramersKronigError):
                errors.append((data, format_exc()))
        elif isinstance(settings, ZHITSettings):
            try:
                perform_zhit(data=data, **kwargs)
            except ZHITError:
                errors.append((data, format_exc()))
        elif isinstance(settings, DRTSettings):
            try:
                perform_drt(data=data, **kwargs)
            except DRTError:
                errors.append((data, format_exc()))
        elif isinstance(settings, FitSettings):
            try:
                perform_fit(data=data, **kwargs)
            except FittingError:
                errors.append((data, format_exc()))
        dpg.split_frame(delay=60)
    signals.emit(Signal.CREATE_PROJECT_SNAPSHOT)
    if len(errors) == 0:
        return
    report: str = "Encountered error(s) while processing the following data sets:\n"
    for (data, err) in errors:
        report += f"- {data.get_label()}\n"
    report += "\n"
    err: str
    for (data, err) in errors:
        label: str = data.get_label()
        report += f"\n{label}\n"
        report += "-" * len(label) + "\n"
        report += f"{err}\n\n"
    signals.emit(
        Signal.SHOW_ERROR_MESSAGE,
        traceback=report,
        message=f"Encountered {len(errors)} error(s) during batch analysis.",
    )


def select_batch_data_sets(*args, **kwargs):
    settings: Optional[Settings]
    settings = kwargs.get("settings")
    if settings is None:
        return
    elif type(settings) not in (TestSettings, ZHITSettings, DRTSettings, FitSettings):
        raise NotImplementedError(f"Unsupported setting: {type(settings)}")
    project: Optional[Project] = STATE.get_active_project()
    if project is None:
        return
    data_sets: List[DataSet] = project.get_data_sets()
    if len(data_sets) == 0:
        return
    batch_window: BatchAnalysis = BatchAnalysis(
        data_sets=data_sets,
        callback=lambda d: batch_perform_analyses(data_sets=d, settings=settings),
    )
    signals.emit(
        Signal.BLOCK_KEYBINDINGS,
        window=batch_window.window,
        window_object=batch_window,
    )
