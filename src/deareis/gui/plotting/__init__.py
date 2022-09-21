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

from inspect import signature
from itertools import chain
from typing import (
    Callable,
    Dict,
    List,
    Optional,
    Tuple,
    Union,
)
from numpy import ndarray
import dearpygui.dearpygui as dpg
import deareis.themes as themes
from deareis.tooltips import attach_tooltip
import deareis.tooltips as tooltips
from deareis.enums import (
    Context,
    DRTMethod,
    PlotType,
    label_to_plot_type,
    plot_type_to_label,
)
from deareis.data import (
    DRTResult,
    DataSet,
    FitResult,
    PlotSettings,
    SimulationResult,
    TestResult,
)
from deareis.gui.plots import (
    BodeMagnitude,
    BodePhase,
    DRT,
    ImpedanceImaginary,
    ImpedanceReal,
    Nyquist,
)
from deareis.gui.plots.base import Plot
from deareis.signals import Signal
import deareis.signals as signals
from deareis.utility import is_filtered_item_visible


TABLE_HEADER_HEIGHT: int = 18
TABLE_ROW_HEIGHT: int = 23


class DataSetsGroup:
    def __init__(self):
        self.header: int = dpg.generate_uuid()
        with dpg.collapsing_header(
            label="Data sets",
            tag=self.header,
        ):
            with dpg.group(horizontal=True, indent=8):
                self.select_all_button: int = dpg.generate_uuid()
                dpg.add_button(
                    label="Select all",
                    callback=lambda s, a, u: signals.emit(
                        Signal.TOGGLE_PLOT_SERIES, **u
                    ),
                    user_data={},
                    tag=self.select_all_button,
                )
                self.unselect_all_button: int = dpg.generate_uuid()
                dpg.add_button(
                    label="Unselect all",
                    callback=lambda s, a, u: signals.emit(
                        Signal.TOGGLE_PLOT_SERIES, **u
                    ),
                    user_data={},
                    tag=self.unselect_all_button,
                )
            self.table: int = dpg.generate_uuid()
            with dpg.group(indent=8):
                with dpg.table(
                    borders_outerV=True,
                    borders_outerH=True,
                    borders_innerV=True,
                    borders_innerH=True,
                    scrollY=True,
                    freeze_rows=1,
                    width=-1,
                    height=TABLE_HEADER_HEIGHT + TABLE_ROW_HEIGHT,
                    tag=self.table,
                ):
                    dpg.add_table_column(label="", width_fixed=True)
                    attach_tooltip(tooltips.plotting.dataset_checkbox)
                    dpg.add_table_column(label="Label", width_fixed=True)
                    attach_tooltip(tooltips.plotting.dataset_label)
            dpg.add_spacer(height=8)
        self.data_hash: str = ""
        self.active_hash: str = ""

    def clear(self):
        dpg.delete_item(self.table, children_only=True, slot=1)
        dpg.configure_item(self.table, height=TABLE_HEADER_HEIGHT + TABLE_ROW_HEIGHT)
        dpg.hide_item(self.header)
        self.data_hash = ""
        self.active_hash = ""

    def populate(self, data_sets: List[DataSet], settings: PlotSettings) -> bool:
        assert type(data_sets) is list, data_sets
        assert type(settings) is PlotSettings, settings
        data_hash: str = ",".join([_.uuid for _ in data_sets])
        if data_hash == self.data_hash:
            return False
        self.clear()
        self.data_hash = data_hash
        if not data_sets:
            dpg.configure_item(
                self.select_all_button,
                user_data={},
            )
            dpg.configure_item(
                self.unselect_all_button,
                user_data={},
            )
            return True
        data: DataSet
        for data in data_sets:
            with dpg.table_row(
                filter_key=data.get_label().lower(),
                parent=self.table,
            ):
                dpg.add_checkbox(
                    default_value=data.uuid in settings.series_order,
                    callback=lambda s, a, u: signals.emit(
                        Signal.TOGGLE_PLOT_SERIES, enabled=a, **u
                    ),
                    user_data={
                        "data_sets": [data],
                        "settings": settings,
                    },
                )
                dpg.add_text(data.get_label())
                attach_tooltip(data.get_label())
        dpg.configure_item(
            self.table,
            height=TABLE_HEADER_HEIGHT + TABLE_ROW_HEIGHT * max(1, len(data_sets)),
        )
        dpg.show_item(self.header)
        return True

    def update(
        self,
        active_hash: str,
        data_sets: List[DataSet],
        settings: PlotSettings,
    ):
        assert type(active_hash) is str, active_hash
        assert type(data_sets) is list, data_sets
        assert type(settings) is PlotSettings, settings
        if active_hash == self.active_hash:
            return
        self.active_hash = active_hash
        data: DataSet
        row: int
        for (data, row) in zip(data_sets, dpg.get_item_children(self.table, slot=1)):
            cells: List[int] = dpg.get_item_children(row, slot=1)
            dpg.configure_item(
                cells[0],
                default_value=data.uuid in settings.series_order,
                user_data={
                    "data_sets": [data],
                    "settings": settings,
                },
            )

    def filter(self, string: str, collapse: bool) -> List[DataSet]:
        assert type(string) is str, string
        stripped_string: str = string.strip()
        data_sets: List[DataSet] = []
        dpg.set_value(self.table, string)
        row: int
        for row in dpg.get_item_children(self.table, slot=1):
            filter_key: str = dpg.get_item_filter_key(row)
            subset: List[DataSet] = dpg.get_item_user_data(
                dpg.get_item_children(row, slot=1)[0]
            ).get("data_sets", [])
            if is_filtered_item_visible(row, stripped_string):
                data_sets.extend(subset)
        dpg.configure_item(
            self.table,
            height=TABLE_HEADER_HEIGHT + TABLE_ROW_HEIGHT * len(data_sets),
        )
        if data_sets:
            dpg.show_item(self.header)
            if collapse:
                dpg.set_value(self.header, not string == "")
        else:
            if collapse:
                dpg.set_value(self.header, False)
            dpg.hide_item(self.header)
        dpg.get_item_user_data(self.select_all_button).update({"data_sets": data_sets})
        dpg.get_item_user_data(self.unselect_all_button).update(
            {"data_sets": data_sets}
        )
        dpg.set_item_label(self.header, f"Data sets ({len(data_sets)})")
        return data_sets


class TestResultGroup:
    def __init__(self, parent: int):
        self.header: int = dpg.generate_uuid()
        with dpg.collapsing_header(
            label="PLACEHOLDER", show=False, tag=self.header, parent=parent, indent=8
        ):
            with dpg.group(horizontal=True, indent=8):
                self.select_all_button: int = dpg.generate_uuid()
                dpg.add_button(
                    label="Select all",
                    callback=lambda s, a, u: signals.emit(
                        Signal.TOGGLE_PLOT_SERIES, **u
                    ),
                    user_data={},
                    tag=self.select_all_button,
                )
                self.unselect_all_button: int = dpg.generate_uuid()
                dpg.add_button(
                    label="Unselect all",
                    callback=lambda s, a, u: signals.emit(
                        Signal.TOGGLE_PLOT_SERIES, **u
                    ),
                    user_data={},
                    tag=self.unselect_all_button,
                )
            with dpg.group(indent=8):
                self.table: int = dpg.generate_uuid()
                with dpg.table(
                    borders_outerV=True,
                    borders_outerH=True,
                    borders_innerV=True,
                    borders_innerH=True,
                    scrollY=True,
                    freeze_rows=1,
                    width=-1,
                    height=TABLE_HEADER_HEIGHT + TABLE_ROW_HEIGHT,
                    tag=self.table,
                ):
                    dpg.add_table_column(label="", width_fixed=True)
                    attach_tooltip(tooltips.plotting.test_checkbox)
                    dpg.add_table_column(label="Label", width_fixed=True)
            dpg.add_spacer(height=8)
        self.test_hash: str = ""
        self.active_hash: str = ""

    def clear(self):
        dpg.delete_item(self.table, children_only=True, slot=1)
        dpg.configure_item(self.table, height=TABLE_HEADER_HEIGHT + TABLE_ROW_HEIGHT)
        dpg.hide_item(self.header)
        self.test_hash = ""
        self.active_hash = ""

    def populate(
        self, tests: List[TestResult], data: DataSet, settings: PlotSettings
    ) -> bool:
        assert type(tests) is list, tests
        assert type(data) is DataSet, data
        assert type(settings) is PlotSettings, settings
        test_hash: str = ",".join([_.uuid for _ in tests])
        if test_hash == self.test_hash:
            return False
        self.clear()
        self.test_hash = test_hash
        dpg.set_item_label(self.header, data.get_label())
        test: TestResult
        for test in tests:
            with dpg.table_row(
                filter_key=f"{data.get_label().lower()} {test.get_label().lower()}",
                parent=self.table,
            ):
                dpg.add_checkbox(
                    default_value=test.uuid in settings.series_order,
                    callback=lambda s, a, u: signals.emit(
                        Signal.TOGGLE_PLOT_SERIES, enabled=a, **u
                    ),
                    user_data={
                        "tests": [test],
                        "settings": settings,
                    },
                )
                dpg.add_text(test.get_label())
                attach_tooltip(test.get_label())
        dpg.configure_item(
            self.table,
            height=TABLE_HEADER_HEIGHT + TABLE_ROW_HEIGHT * max(1, len(tests)),
        )
        dpg.show_item(self.header)
        return True

    def update(
        self,
        active_hash: str,
        tests: List[TestResult],
        data: DataSet,
        settings: PlotSettings,
    ):
        assert type(active_hash) is str, active_hash
        assert type(tests) is list, tests
        assert type(data) is DataSet, data
        assert type(settings) is PlotSettings, settings
        if active_hash == self.active_hash:
            return
        self.active_hash = active_hash
        test: TestResult
        row: int
        for (test, row) in zip(tests, dpg.get_item_children(self.table, slot=1)):
            cells: List[int] = dpg.get_item_children(row, slot=1)
            dpg.configure_item(
                cells[0],
                default_value=test.uuid in settings.series_order,
                user_data={
                    "tests": [test],
                    "settings": settings,
                },
            )

    def filter(self, string: str, collapse: bool) -> List[TestResult]:
        assert type(string) is str, string
        stripped_string: str = string.strip()
        dpg.set_value(self.table, string)
        tests: List[TestResult] = []
        row: int
        for row in dpg.get_item_children(self.table, slot=1):
            filter_key: str = dpg.get_item_filter_key(row)
            subset: List[DataSet] = dpg.get_item_user_data(
                dpg.get_item_children(row, slot=1)[0]
            ).get("tests", [])
            if is_filtered_item_visible(row, stripped_string):
                tests.extend(subset)
        dpg.configure_item(
            self.table, height=TABLE_HEADER_HEIGHT + TABLE_ROW_HEIGHT * len(tests)
        )
        if tests:
            dpg.show_item(self.header)
            if collapse:
                dpg.set_value(self.header, not string == "")
        else:
            if collapse:
                dpg.set_value(self.header, False)
            dpg.hide_item(self.header)
        dpg.get_item_user_data(self.select_all_button).update({"tests": tests})
        dpg.get_item_user_data(self.unselect_all_button).update({"tests": tests})
        return tests


class TestsGroup:
    def __init__(self):
        self.groups: Dict[str, TestResultGroup] = {}
        self.header: int = dpg.generate_uuid()
        with dpg.collapsing_header(
            label="Kramers-Kronig tests",
            tag=self.header,
        ):
            self.button_group: int = dpg.generate_uuid()
            with dpg.group(horizontal=True, indent=8, tag=self.button_group):
                dpg.add_button(
                    label="Expand all",
                    callback=lambda s, a, u: self.expand_subheaders(True),
                )
                dpg.add_button(
                    label="Collapse all",
                    callback=lambda s, a, u: self.expand_subheaders(False),
                )
                self.select_all_button: int = dpg.generate_uuid()
                dpg.add_button(
                    label="Select all",
                    callback=lambda s, a, u: signals.emit(
                        Signal.TOGGLE_PLOT_SERIES, **u
                    ),
                    user_data={},
                    tag=self.select_all_button,
                )
                self.unselect_all_button: int = dpg.generate_uuid()
                dpg.add_button(
                    label="Unselect all",
                    callback=lambda s, a, u: signals.emit(
                        Signal.TOGGLE_PLOT_SERIES, **u
                    ),
                    user_data={},
                    tag=self.unselect_all_button,
                )
            dpg.add_spacer(height=8)
        self.data_hash: str = ""

    def expand_subheaders(self, state: bool):
        assert type(state) is bool
        subheader: int
        for subheader in dpg.get_item_children(self.header, slot=1):
            if "::mvCollapsingHeader" not in dpg.get_item_type(subheader):
                continue
            dpg.set_value(subheader, state)

    def clear(self):
        group: TestResultGroup
        for group in self.groups.values():
            group.clear()
        dpg.hide_item(self.header)
        self.data_hash = ""

    def populate(
        self,
        tests: Dict[str, List[TestResult]],
        data_sets: List[DataSet],
        settings: PlotSettings,
    ):
        assert type(tests) is dict, tests
        assert type(data_sets) is list, data_sets
        assert type(settings) is PlotSettings, settings
        if not data_sets:
            self.clear()
            dpg.configure_item(
                self.select_all_button,
                user_data={},
            )
            dpg.configure_item(
                self.unselect_all_button,
                user_data={},
            )
            return
        data_hash: str = ",".join([_.uuid for _ in data_sets])
        if data_hash != self.data_hash:
            self.clear()
            self.data_hash = data_hash
        active_hash: str = ",".join(sorted(settings.series_order)) + f",{settings.uuid}"
        all_tests: List[TestResult] = []
        data: DataSet
        for data in data_sets:
            if not tests[data.uuid]:
                if data.uuid in self.groups:
                    self.groups[data.uuid].clear()
                continue
            if data.uuid not in self.groups:
                self.groups[data.uuid] = TestResultGroup(self.header)
            group: TestResultGroup = self.groups[data.uuid]
            if not group.populate(tests[data.uuid], data, settings):
                group.update(active_hash, tests[data.uuid], data, settings)
            dpg.get_item_user_data(group.select_all_button).update(
                {
                    "enabled": True,
                    "tests": tests,
                    "settings": settings,
                }
            )
            dpg.get_item_user_data(group.unselect_all_button).update(
                {
                    "enabled": False,
                    "tests": tests,
                    "settings": settings,
                }
            )
            all_tests.extend(tests[data.uuid])
        if all_tests:
            dpg.show_item(self.header)
        dpg.get_item_user_data(self.select_all_button).update(
            {
                "enabled": True,
                "tests": all_tests,
                "settings": settings,
            }
        )
        dpg.get_item_user_data(self.unselect_all_button).update(
            {
                "enabled": False,
                "tests": all_tests,
                "settings": settings,
            }
        )

    def filter(self, string: str, collapse: bool) -> List[TestResult]:
        assert type(string) is str, string
        tests: List[TestResult] = []
        group: TestResultGroup
        for group in self.groups.values():
            tests.extend(group.filter(string, collapse))
        if tests:
            dpg.show_item(self.header)
            if collapse:
                dpg.set_value(self.header, not string == "")
        else:
            if collapse:
                dpg.set_value(self.header, False)
            dpg.hide_item(self.header)
        dpg.get_item_user_data(self.select_all_button).update({"tests": tests})
        dpg.get_item_user_data(self.unselect_all_button).update({"tests": tests})
        dpg.set_item_label(self.header, f"Kramers-Kronig tests ({len(tests)})")
        return tests


class DRTResultGroup:
    def __init__(self, parent: int):
        self.header: int = dpg.generate_uuid()
        with dpg.collapsing_header(
            label="PLACEHOLDER", show=False, tag=self.header, parent=parent, indent=8
        ):
            with dpg.group(horizontal=True, indent=8):
                self.select_all_button: int = dpg.generate_uuid()
                dpg.add_button(
                    label="Select all",
                    callback=lambda s, a, u: signals.emit(
                        Signal.TOGGLE_PLOT_SERIES, **u
                    ),
                    user_data={},
                    tag=self.select_all_button,
                )
                self.unselect_all_button: int = dpg.generate_uuid()
                dpg.add_button(
                    label="Unselect all",
                    callback=lambda s, a, u: signals.emit(
                        Signal.TOGGLE_PLOT_SERIES, **u
                    ),
                    user_data={},
                    tag=self.unselect_all_button,
                )
            with dpg.group(indent=8):
                self.table: int = dpg.generate_uuid()
                with dpg.table(
                    borders_outerV=True,
                    borders_outerH=True,
                    borders_innerV=True,
                    borders_innerH=True,
                    scrollY=True,
                    freeze_rows=1,
                    width=-1,
                    height=TABLE_HEADER_HEIGHT + TABLE_ROW_HEIGHT,
                    tag=self.table,
                ):
                    dpg.add_table_column(label="", width_fixed=True)
                    attach_tooltip(tooltips.plotting.drt_checkbox)
                    dpg.add_table_column(label="Label", width_fixed=True)
            dpg.add_spacer(height=8)
        self.drt_hash: str = ""
        self.active_hash: str = ""

    def clear(self):
        dpg.delete_item(self.table, children_only=True, slot=1)
        dpg.configure_item(self.table, height=TABLE_HEADER_HEIGHT + TABLE_ROW_HEIGHT)
        dpg.hide_item(self.header)
        self.drt_hash = ""
        self.active_hash = ""

    def populate(
        self,
        drts: List[DRTResult],
        data: DataSet,
        settings: PlotSettings,
    ) -> bool:
        assert type(drts) is list, drts
        assert type(data) is DataSet, data
        assert type(settings) is PlotSettings, settings
        drt_hash: str = ",".join([_.uuid for _ in drts])
        if drt_hash == self.drt_hash:
            return False
        self.clear()
        self.drt_hash = drt_hash
        dpg.set_item_label(self.header, data.get_label())
        drt: DRTResult
        for drt in drts:
            with dpg.table_row(
                filter_key=f"{data.get_label().lower()} {drt.get_label().lower()}",
                parent=self.table,
            ):
                dpg.add_checkbox(
                    default_value=drt.uuid in settings.series_order,
                    callback=lambda s, a, u: signals.emit(
                        Signal.TOGGLE_PLOT_SERIES, enabled=a, **u
                    ),
                    user_data={
                        "drts": [drt],
                        "settings": settings,
                    },
                )
                dpg.add_text(drt.get_label())
                attach_tooltip(drt.get_label())
        dpg.configure_item(
            self.table,
            height=TABLE_HEADER_HEIGHT + TABLE_ROW_HEIGHT * max(1, len(drts)),
        )
        dpg.show_item(self.header)
        return True

    def update(
        self,
        active_hash: str,
        drts: List[DRTResult],
        data: DataSet,
        settings: PlotSettings,
    ):
        assert type(active_hash) is str, active_hash
        assert type(drts) is list, drts
        assert type(data) is DataSet, data
        assert type(settings) is PlotSettings, settings
        if active_hash == self.active_hash:
            return
        self.active_hash = active_hash
        drt: DRTResult
        row: int
        for (drt, row) in zip(drts, dpg.get_item_children(self.table, slot=1)):
            cells: List[int] = dpg.get_item_children(row, slot=1)
            dpg.configure_item(
                cells[0],
                default_value=drt.uuid in settings.series_order,
                user_data={
                    "drts": [drt],
                    "settings": settings,
                },
            )

    def filter(self, string: str, collapse: bool) -> List[DRTResult]:
        assert type(string) is str, string
        stripped_string: str = string.strip()
        dpg.set_value(self.table, string)
        drts: List[DRTResult] = []
        row: int
        for row in dpg.get_item_children(self.table, slot=1):
            filter_key: str = dpg.get_item_filter_key(row)
            subset: List[DataSet] = dpg.get_item_user_data(
                dpg.get_item_children(row, slot=1)[0]
            ).get("drts", [])
            if is_filtered_item_visible(row, stripped_string):
                drts.extend(subset)
        dpg.configure_item(
            self.table, height=TABLE_HEADER_HEIGHT + TABLE_ROW_HEIGHT * len(drts)
        )
        if drts:
            dpg.show_item(self.header)
            if collapse:
                dpg.set_value(self.header, not string == "")
        else:
            if collapse:
                dpg.set_value(self.header, False)
            dpg.hide_item(self.header)
        dpg.get_item_user_data(self.select_all_button).update({"drts": drts})
        dpg.get_item_user_data(self.unselect_all_button).update({"drts": drts})
        return drts


class DRTsGroup:
    def __init__(self):
        self.groups: Dict[str, DRTResultGroup] = {}
        self.header: int = dpg.generate_uuid()
        with dpg.collapsing_header(
            label="DRT analyses",
            tag=self.header,
        ):
            self.button_group: int = dpg.generate_uuid()
            with dpg.group(horizontal=True, indent=8, tag=self.button_group):
                dpg.add_button(
                    label="Expand all",
                    callback=lambda s, a, u: self.expand_subheaders(True),
                )
                dpg.add_button(
                    label="Collapse all",
                    callback=lambda s, a, u: self.expand_subheaders(False),
                )
                self.select_all_button: int = dpg.generate_uuid()
                dpg.add_button(
                    label="Select all",
                    callback=lambda s, a, u: signals.emit(
                        Signal.TOGGLE_PLOT_SERIES, **u
                    ),
                    user_data={},
                    tag=self.select_all_button,
                )
                self.unselect_all_button: int = dpg.generate_uuid()
                dpg.add_button(
                    label="Unselect all",
                    callback=lambda s, a, u: signals.emit(
                        Signal.TOGGLE_PLOT_SERIES, **u
                    ),
                    user_data={},
                    tag=self.unselect_all_button,
                )
            dpg.add_spacer(height=8)
        self.data_hash: str = ""

    def expand_subheaders(self, state: bool):
        assert type(state) is bool
        subheader: int
        for subheader in dpg.get_item_children(self.header, slot=1):
            if "::mvCollapsingHeader" not in dpg.get_item_type(subheader):
                continue
            dpg.set_value(subheader, state)

    def clear(self):
        group: DRTResultGroup
        for group in self.groups.values():
            group.clear()
        dpg.hide_item(self.header)
        self.data_hash = ""

    def populate(
        self,
        drts: Dict[str, List[DRTResult]],
        data_sets: List[DataSet],
        settings: PlotSettings,
    ):
        assert type(drts) is dict, drts
        assert type(data_sets) is list, data_sets
        assert type(settings) is PlotSettings, settings
        if not data_sets:
            self.clear()
            dpg.configure_item(
                self.select_all_button,
                user_data={},
            )
            dpg.configure_item(
                self.unselect_all_button,
                user_data={},
            )
            return
        data_hash: str = ",".join([_.uuid for _ in data_sets])
        if data_hash != self.data_hash:
            self.clear()
            self.data_hash = data_hash
        active_hash: str = ",".join(sorted(settings.series_order)) + f",{settings.uuid}"
        all_drts: List[DRTResult] = []
        data: DataSet
        for data in data_sets:
            if not drts[data.uuid]:
                if data.uuid in self.groups:
                    self.groups[data.uuid].clear()
                continue
            if data.uuid not in self.groups:
                self.groups[data.uuid] = DRTResultGroup(self.header)
            group: DRTResultGroup = self.groups[data.uuid]
            if not group.populate(drts[data.uuid], data, settings):
                group.update(active_hash, drts[data.uuid], data, settings)
            dpg.get_item_user_data(group.select_all_button).update(
                {
                    "enabled": True,
                    "drts": drts,
                    "settings": settings,
                }
            )
            dpg.get_item_user_data(group.unselect_all_button).update(
                {
                    "enabled": False,
                    "drts": drts,
                    "settings": settings,
                }
            )
            all_drts.extend(drts[data.uuid])
        if all_drts:
            dpg.show_item(self.header)
        dpg.get_item_user_data(self.select_all_button).update(
            {
                "enabled": True,
                "drts": all_drts,
                "settings": settings,
            }
        )
        dpg.get_item_user_data(self.unselect_all_button).update(
            {
                "enabled": False,
                "drts": all_drts,
                "settings": settings,
            }
        )

    def filter(self, string: str, collapse: bool) -> List[DRTResult]:
        assert type(string) is str, string
        drts: List[DRTResult] = []
        group: DRTResultGroup
        for group in self.groups.values():
            drts.extend(group.filter(string, collapse))
        if drts:
            dpg.show_item(self.header)
            if collapse:
                dpg.set_value(self.header, not string == "")
        else:
            if collapse:
                dpg.set_value(self.header, False)
            dpg.hide_item(self.header)
        dpg.get_item_user_data(self.select_all_button).update({"drts": drts})
        dpg.get_item_user_data(self.unselect_all_button).update({"drts": drts})
        dpg.set_item_label(self.header, f"DRT analyses ({len(drts)})")
        return drts


class FitResultGroup:
    def __init__(self, parent: int):
        self.header: int = dpg.generate_uuid()
        with dpg.collapsing_header(
            label="PLACEHOLDER", show=False, tag=self.header, parent=parent, indent=8
        ):
            with dpg.group(horizontal=True, indent=8):
                self.select_all_button: int = dpg.generate_uuid()
                dpg.add_button(
                    label="Select all",
                    callback=lambda s, a, u: signals.emit(
                        Signal.TOGGLE_PLOT_SERIES, **u
                    ),
                    user_data={},
                    tag=self.select_all_button,
                )
                self.unselect_all_button: int = dpg.generate_uuid()
                dpg.add_button(
                    label="Unselect all",
                    callback=lambda s, a, u: signals.emit(
                        Signal.TOGGLE_PLOT_SERIES, **u
                    ),
                    user_data={},
                    tag=self.unselect_all_button,
                )
            with dpg.group(indent=8):
                self.table: int = dpg.generate_uuid()
                with dpg.table(
                    borders_outerV=True,
                    borders_outerH=True,
                    borders_innerV=True,
                    borders_innerH=True,
                    scrollY=True,
                    freeze_rows=1,
                    width=-1,
                    height=TABLE_HEADER_HEIGHT + TABLE_ROW_HEIGHT,
                    tag=self.table,
                ):
                    dpg.add_table_column(label="", width_fixed=True)
                    attach_tooltip(tooltips.plotting.fit_checkbox)
                    dpg.add_table_column(label="Label", width_fixed=True)
            dpg.add_spacer(height=8)
        self.fit_hash: str = ""
        self.active_hash: str = ""

    def clear(self):
        dpg.delete_item(self.table, children_only=True, slot=1)
        dpg.configure_item(self.table, height=TABLE_HEADER_HEIGHT + TABLE_ROW_HEIGHT)
        dpg.hide_item(self.header)
        self.fit_hash = ""
        self.active_hash = ""

    def populate(
        self,
        fits: List[FitResult],
        data: DataSet,
        settings: PlotSettings,
    ) -> bool:
        assert type(fits) is list, fits
        assert type(data) is DataSet, data
        assert type(settings) is PlotSettings, settings
        fit_hash: str = ",".join([_.uuid for _ in fits])
        if fit_hash == self.fit_hash:
            return False
        self.clear()
        self.fit_hash = fit_hash
        dpg.set_item_label(self.header, data.get_label())
        fit: FitResult
        for fit in fits:
            with dpg.table_row(
                filter_key=f"{data.get_label().lower()} {fit.get_label().lower()}",
                parent=self.table,
            ):
                dpg.add_checkbox(
                    default_value=fit.uuid in settings.series_order,
                    callback=lambda s, a, u: signals.emit(
                        Signal.TOGGLE_PLOT_SERIES, enabled=a, **u
                    ),
                    user_data={
                        "fits": [fit],
                        "settings": settings,
                    },
                )
                dpg.add_text(fit.get_label())
                attach_tooltip(fit.get_label())
        dpg.configure_item(
            self.table,
            height=TABLE_HEADER_HEIGHT + TABLE_ROW_HEIGHT * max(1, len(fits)),
        )
        dpg.show_item(self.header)
        return True

    def update(
        self,
        active_hash: str,
        fits: List[FitResult],
        data: DataSet,
        settings: PlotSettings,
    ):
        assert type(active_hash) is str, active_hash
        assert type(fits) is list, fits
        assert type(data) is DataSet, data
        assert type(settings) is PlotSettings, settings
        if active_hash == self.active_hash:
            return
        self.active_hash = active_hash
        fit: FitResult
        row: int
        for (fit, row) in zip(fits, dpg.get_item_children(self.table, slot=1)):
            cells: List[int] = dpg.get_item_children(row, slot=1)
            dpg.configure_item(
                cells[0],
                default_value=fit.uuid in settings.series_order,
                user_data={
                    "fits": [fit],
                    "settings": settings,
                },
            )

    def filter(self, string: str, collapse: bool) -> List[FitResult]:
        assert type(string) is str, string
        stripped_string: str = string.strip()
        dpg.set_value(self.table, string)
        fits: List[FitResult] = []
        row: int
        for row in dpg.get_item_children(self.table, slot=1):
            filter_key: str = dpg.get_item_filter_key(row)
            subset: List[DataSet] = dpg.get_item_user_data(
                dpg.get_item_children(row, slot=1)[0]
            ).get("fits", [])
            if is_filtered_item_visible(row, stripped_string):
                fits.extend(subset)
        dpg.configure_item(
            self.table,
            height=TABLE_HEADER_HEIGHT + TABLE_ROW_HEIGHT * max(1, len(fits)),
        )
        if fits:
            dpg.show_item(self.header)
            if collapse:
                dpg.set_value(self.header, not string == "")
        else:
            if collapse:
                dpg.set_value(self.header, False)
            dpg.hide_item(self.header)
        dpg.get_item_user_data(self.select_all_button).update({"fits": fits})
        dpg.get_item_user_data(self.unselect_all_button).update({"fits": fits})
        return fits


class FitsGroup:
    def __init__(self):
        self.groups: Dict[str, FitResultGroup] = {}
        self.header: int = dpg.generate_uuid()
        with dpg.collapsing_header(
            label="Fitted equivalent circuits",
            tag=self.header,
        ):
            self.button_group: int = dpg.generate_uuid()
            with dpg.group(horizontal=True, indent=8, tag=self.button_group):
                dpg.add_button(
                    label="Expand all",
                    callback=lambda s, a, u: self.expand_subheaders(True),
                )
                dpg.add_button(
                    label="Collapse all",
                    callback=lambda s, a, u: self.expand_subheaders(False),
                )
                self.select_all_button: int = dpg.generate_uuid()
                dpg.add_button(
                    label="Select all",
                    callback=lambda s, a, u: signals.emit(
                        Signal.TOGGLE_PLOT_SERIES, **u
                    ),
                    user_data={},
                    tag=self.select_all_button,
                )
                self.unselect_all_button: int = dpg.generate_uuid()
                dpg.add_button(
                    label="Unselect all",
                    callback=lambda s, a, u: signals.emit(
                        Signal.TOGGLE_PLOT_SERIES, **u
                    ),
                    user_data={},
                    tag=self.unselect_all_button,
                )
            dpg.add_spacer(height=8)
        self.data_hash: str = ""

    def expand_subheaders(self, state: bool):
        assert type(state) is bool
        subheader: int
        for subheader in dpg.get_item_children(self.header, slot=1):
            if "::mvCollapsingHeader" not in dpg.get_item_type(subheader):
                continue
            dpg.set_value(subheader, state)

    def clear(self):
        group: FitResultGroup
        for group in self.groups.values():
            group.clear()
        dpg.hide_item(self.header)
        self.data_hash = ""

    def populate(
        self,
        fits: Dict[str, List[FitResult]],
        data_sets: List[DataSet],
        settings: PlotSettings,
    ):
        assert type(fits) is dict, fits
        assert type(data_sets) is list, data_sets
        assert type(settings) is PlotSettings, settings
        if not data_sets:
            self.clear()
            dpg.configure_item(
                self.select_all_button,
                user_data={},
            )
            dpg.configure_item(
                self.unselect_all_button,
                user_data={},
            )
            return
        data_hash: str = ",".join([_.uuid for _ in data_sets])
        if data_hash != self.data_hash:
            self.clear()
            self.data_hash = data_hash
        active_hash: str = ",".join(sorted(settings.series_order)) + f",{settings.uuid}"
        all_fits: List[FitResult] = []
        data: DataSet
        for data in data_sets:
            if not fits[data.uuid]:
                if data.uuid in self.groups:
                    self.groups[data.uuid].clear()
                continue
            if data.uuid not in self.groups:
                self.groups[data.uuid] = FitResultGroup(self.header)
            group: FitResultGroup = self.groups[data.uuid]
            if not group.populate(fits[data.uuid], data, settings):
                group.update(active_hash, fits[data.uuid], data, settings)
            dpg.get_item_user_data(group.select_all_button).update(
                {
                    "enabled": True,
                    "fits": fits[data.uuid],
                    "settings": settings,
                }
            )
            dpg.get_item_user_data(group.unselect_all_button).update(
                {
                    "enabled": False,
                    "fits": fits[data.uuid],
                    "settings": settings,
                }
            )
            all_fits.extend(fits[data.uuid])
        if all_fits:
            dpg.show_item(self.header)
        dpg.get_item_user_data(self.select_all_button).update(
            {
                "enabled": True,
                "fits": all_fits,
                "settings": settings,
            }
        )
        dpg.get_item_user_data(self.unselect_all_button).update(
            {
                "enabled": False,
                "fits": all_fits,
                "settings": settings,
            }
        )

    def filter(self, string: str, collapse: bool) -> List[FitResult]:
        assert type(string) is str, string
        # TODO: Determine whether to filter
        fits: List[FitResult] = []
        group: FitResultGroup
        for group in self.groups.values():
            fits.extend(group.filter(string, collapse))
        if fits:
            dpg.show_item(self.header)
            if collapse:
                dpg.set_value(self.header, not string == "")
        else:
            if collapse:
                dpg.set_value(self.header, False)
            dpg.hide_item(self.header)
        dpg.get_item_user_data(self.select_all_button).update({"fits": fits})
        dpg.get_item_user_data(self.unselect_all_button).update({"fits": fits})
        dpg.set_item_label(self.header, f"Fitted equivalent circuits ({len(fits)})")
        return fits


class SimulationsGroup:
    def __init__(self):
        self.header: int = dpg.generate_uuid()
        with dpg.collapsing_header(
            label="Simulated spectra",
            tag=self.header,
        ):
            with dpg.group(horizontal=True, indent=8):
                self.select_all_button: int = dpg.generate_uuid()
                dpg.add_button(
                    label="Select all",
                    callback=lambda s, a, u: signals.emit(
                        Signal.TOGGLE_PLOT_SERIES, **u
                    ),
                    user_data={},
                    tag=self.select_all_button,
                )
                self.unselect_all_button: int = dpg.generate_uuid()
                dpg.add_button(
                    label="Unselect all",
                    callback=lambda s, a, u: signals.emit(
                        Signal.TOGGLE_PLOT_SERIES, **u
                    ),
                    user_data={},
                    tag=self.unselect_all_button,
                )
            with dpg.group(indent=8):
                self.table: int = dpg.generate_uuid()
                with dpg.table(
                    borders_outerV=True,
                    borders_outerH=True,
                    borders_innerV=True,
                    borders_innerH=True,
                    scrollY=True,
                    freeze_rows=1,
                    width=-1,
                    height=TABLE_HEADER_HEIGHT + TABLE_ROW_HEIGHT,
                    tag=self.table,
                ):
                    dpg.add_table_column(label="", width_fixed=True)
                    attach_tooltip(tooltips.plotting.simulation_checkbox)
                    dpg.add_table_column(label="Label", width_fixed=True)
            dpg.add_spacer(height=8)
        self.sim_hash: str = ""
        self.active_hash: str = ""

    def clear(self):
        dpg.delete_item(self.table, children_only=True, slot=1)
        dpg.configure_item(self.table, height=TABLE_HEADER_HEIGHT + TABLE_ROW_HEIGHT)
        dpg.hide_item(self.header)
        self.sim_hash = ""
        self.active_hash = ""

    def populate(
        self,
        simulations: List[SimulationResult],
        settings: PlotSettings,
    ) -> bool:
        assert type(simulations) is list, simulations
        assert type(settings) is PlotSettings, settings
        sim_hash: str = ",".join([_.uuid for _ in simulations])
        if sim_hash == self.sim_hash:
            return False
        self.clear()
        self.sim_hash = sim_hash
        if not simulations:
            dpg.configure_item(
                self.select_all_button,
                user_data={},
            )
            dpg.configure_item(
                self.unselect_all_button,
                user_data={},
            )
            return True
        sim: SimulationResult
        for sim in simulations:
            with dpg.table_row(filter_key=sim.get_label().lower(), parent=self.table):
                dpg.add_checkbox(
                    default_value=sim.uuid in settings.series_order,
                    callback=lambda s, a, u: signals.emit(
                        Signal.TOGGLE_PLOT_SERIES, enabled=a, **u
                    ),
                    user_data={
                        "simulations": [sim],
                        "settings": settings,
                    },
                )
                dpg.add_text(sim.get_label())
                attach_tooltip(sim.get_label())
        dpg.configure_item(
            self.table,
            height=TABLE_HEADER_HEIGHT + TABLE_ROW_HEIGHT * max(1, len(simulations)),
        )
        dpg.show_item(self.header)
        return True

    def update(
        self,
        active_hash: str,
        simulations: List[SimulationResult],
        settings: PlotSettings,
    ):
        assert type(active_hash) is str, active_hash
        assert type(simulations) is list, simulations
        assert type(settings) is PlotSettings, settings
        if active_hash == self.active_hash:
            return
        self.active_hash = active_hash
        sim: SimulationResult
        row: int
        for (sim, row) in zip(simulations, dpg.get_item_children(self.table, slot=1)):
            cells: List[int] = dpg.get_item_children(row, slot=1)
            dpg.configure_item(
                cells[0],
                default_value=sim.uuid in settings.series_order,
                user_data={
                    "simulations": [sim],
                    "settings": settings,
                },
            )

    def filter(self, string: str, collapse: bool) -> List[SimulationResult]:
        assert type(string) is str, string
        stripped_string: str = string.strip()
        dpg.set_value(self.table, string)
        simulations: List[SimulationResult] = []
        row: int
        for row in dpg.get_item_children(self.table, slot=1):
            filter_key: str = dpg.get_item_filter_key(row)
            subset: List[DataSet] = dpg.get_item_user_data(
                dpg.get_item_children(row, slot=1)[0]
            ).get("simulations", [])
            if is_filtered_item_visible(row, stripped_string):
                simulations.extend(subset)
        dpg.configure_item(
            self.table,
            height=TABLE_HEADER_HEIGHT + TABLE_ROW_HEIGHT * max(1, len(simulations)),
        )
        if simulations:
            dpg.show_item(self.header)
            if collapse:
                dpg.set_value(self.header, not string == "")
        else:
            if collapse:
                dpg.set_value(self.header, False)
            dpg.hide_item(self.header)
        dpg.get_item_user_data(self.select_all_button).update(
            {"simulations": simulations}
        )
        dpg.get_item_user_data(self.unselect_all_button).update(
            {"simulations": simulations}
        )
        dpg.set_item_label(self.header, f"Simulated spectra ({len(simulations)})")
        return simulations


class ActiveSeries:
    def __init__(self):
        self.table: int = dpg.generate_uuid()
        with dpg.table(
            borders_outerV=True,
            borders_outerH=True,
            borders_innerV=True,
            borders_innerH=True,
            scrollY=True,
            freeze_rows=1,
            width=-1,
            height=TABLE_HEADER_HEIGHT + TABLE_ROW_HEIGHT,
            tag=self.table,
        ):
            dpg.add_table_column(
                label="Type",
                width_fixed=True,
            )
            attach_tooltip(tooltips.plotting.item_type)
            dpg.add_table_column(label="Label")
            attach_tooltip(tooltips.plotting.label)
            dpg.add_table_column(label="Appearance", width_fixed=True)
            attach_tooltip(tooltips.plotting.appearance)
            dpg.add_table_column(label="Position", width_fixed=True)
            attach_tooltip(tooltips.plotting.position)

    def clear(self):
        dpg.delete_item(self.table, children_only=True, slot=1)
        dpg.configure_item(self.table, height=TABLE_HEADER_HEIGHT + TABLE_ROW_HEIGHT)

    def populate(
        self,
        data_sets: List[DataSet],
        tests: Dict[str, List[TestResult]],
        drts: Dict[str, List[DRTResult]],
        fits: Dict[str, List[FitResult]],
        simulations: List[SimulationResult],
        settings: PlotSettings,
    ):
        assert type(data_sets) is list, data_sets
        assert type(tests) is dict, tests
        assert type(drts) is dict, drts
        assert type(fits) is dict, fits
        assert type(simulations) is list, simulations
        assert type(settings) is PlotSettings, settings
        self.clear()
        series: List[
            Union[DataSet, TestResult, DRTResult, FitResult, SimulationResult]
        ] = []
        series.extend(filter(lambda _: _.uuid in settings.series_order, data_sets))
        series.extend(
            filter(
                lambda _: _.uuid in settings.series_order,
                list(chain(*list(tests.values()))),
            )
        )
        series.extend(
            filter(
                lambda _: _.uuid in settings.series_order,
                list(chain(*list(drts.values()))),
            )
        )
        series.extend(
            filter(
                lambda _: _.uuid in settings.series_order,
                list(chain(*list(fits.values()))),
            )
        )
        series.extend(filter(lambda _: _.uuid in settings.series_order, simulations))
        series.sort(key=lambda _: settings.series_order.index(_.uuid))
        ser: Union[DataSet, TestResult, DRTResult, FitResult, SimulationResult]
        types: dict = {
            DataSet: (
                "D",
                "Data set",
            ),
            TestResult: (
                "KK",
                "Kramers-Kronig test",
            ),
            DRTResult: (
                "DRT",
                "DRT analysis",
            ),
            FitResult: (
                "F",
                "Fit",
            ),
            SimulationResult: (
                "S",
                "Simulation",
            ),
        }
        marker_lookup: Dict[int, str] = {v: k for k, v in themes.PLOT_MARKERS.items()}
        for ser in series:
            type_label: str
            type_tooltip: str
            type_label, type_tooltip = types[type(ser)]
            with dpg.table_row(parent=self.table):
                dpg.add_text(type_label.ljust(4))
                attach_tooltip(type_tooltip)
                dpg.add_input_text(
                    hint=ser.get_label(),
                    default_value=settings.get_series_label(ser.uuid),
                    width=-1,
                    on_enter=True,
                    callback=lambda s, a, u: signals.emit(
                        Signal.RENAME_PLOT_SERIES,
                        label=a,
                        **u,
                    ),
                    user_data={
                        "settings": settings,
                        "uuid": ser.uuid,
                        "series": ser,
                    },
                )
                attach_tooltip(ser.get_label())
                dpg.add_button(
                    label="Edit",
                    width=-1,
                    callback=lambda s, a, u: signals.emit(
                        Signal.MODIFY_PLOT_SERIES_THEME,
                        settings=settings,
                        series=u,
                    ),
                    user_data=ser,
                )
                with dpg.tooltip(parent=dpg.last_item()):
                    with dpg.group(horizontal=True):
                        dpg.add_text(" Color:")
                        dpg.add_color_edit(
                            default_value=settings.get_series_color(ser.uuid),
                            enabled=False,
                            alpha_preview=dpg.mvColorEdit_AlphaPreviewHalf,
                            no_inputs=True,
                        )
                    dpg.add_text(
                        "Marker: "
                        + marker_lookup.get(
                            settings.get_series_marker(ser.uuid), "None"
                        )
                    )
                    dpg.add_text(
                        "  Line: "
                        + ("Yes" if settings.get_series_line(ser.uuid) else "No")
                    )
                with dpg.group(horizontal=True):
                    dpg.add_button(
                        label="U",
                        width=24,
                        callback=lambda s, a, u: signals.emit(
                            Signal.REORDER_PLOT_SERIES, settings=settings, **u
                        ),
                        user_data={
                            "uuid": ser.uuid,
                            "step": -1,
                        },
                    )
                    attach_tooltip("Move this series up by one position.")
                    dpg.add_button(
                        label="D",
                        width=24,
                        callback=lambda s, a, u: signals.emit(
                            Signal.REORDER_PLOT_SERIES, settings=settings, **u
                        ),
                        user_data={
                            "uuid": ser.uuid,
                            "step": 1,
                        },
                    )
                    attach_tooltip("Move this series down by one position.")
        dpg.configure_item(
            self.table,
            height=TABLE_HEADER_HEIGHT + TABLE_ROW_HEIGHT * max(1, len(series)),
        )

    def has_active_input(self) -> bool:
        row: int
        for row in dpg.get_item_children(self.table, slot=1):
            label_input: int = dpg.get_item_children(row, slot=1)[2]
            if dpg.is_item_active(label_input):
                return True
        return False


class PlottingTab:
    def __init__(self, state):
        self.state = state
        self.series_tags: Dict[str, int] = {}
        self.queued_update: Optional[Callable] = None
        self.plotted_uuid: str = ""
        self.plot_types: Dict[PlotType, Plot] = {}
        label_pad: int = 5
        sidebar_width: int = 400
        self.tab: int = dpg.generate_uuid()
        with dpg.tab(label="Plotting", tag=self.tab):
            with dpg.child_window(border=False):
                with dpg.group(horizontal=True):
                    self.sidebar_window: int = dpg.generate_uuid()
                    with dpg.child_window(
                        width=sidebar_width, border=False, tag=self.sidebar_window
                    ):
                        with dpg.child_window(height=82):
                            with dpg.group(horizontal=True):
                                dpg.add_text("Plot".rjust(label_pad))
                                self.plot_combo: int = dpg.generate_uuid()
                                dpg.add_combo(
                                    width=-64,
                                    callback=lambda s, a, u: signals.emit(
                                        Signal.SELECT_PLOT_SETTINGS,
                                        settings=u.get(a),
                                    ),
                                    user_data={},
                                    tag=self.plot_combo,
                                )
                                self.new_button: int = dpg.generate_uuid()
                                dpg.add_button(
                                    label="New",
                                    callback=lambda s, a, u: signals.emit(
                                        Signal.NEW_PLOT_SETTINGS,
                                    ),
                                    width=-1,
                                    tag=self.new_button,
                                )
                                attach_tooltip(tooltips.plotting.create)
                            with dpg.group(horizontal=True):
                                dpg.add_text("Label".rjust(label_pad))
                                self.label_input: int = dpg.generate_uuid()
                                dpg.add_input_text(
                                    width=-64,
                                    on_enter=True,
                                    callback=lambda s, a, u: signals.emit(
                                        Signal.RENAME_PLOT_SETTINGS,
                                        label=a,
                                        settings=dpg.get_item_user_data(
                                            self.delete_button
                                        ),
                                    ),
                                    tag=self.label_input,
                                )
                                self.delete_button: int = dpg.generate_uuid()
                                dpg.add_button(
                                    label="Delete",
                                    callback=lambda s, a, u: signals.emit(
                                        Signal.DELETE_PLOT_SETTINGS, settings=u
                                    ),
                                    user_data=None,
                                    width=-1,
                                    tag=self.delete_button,
                                )
                                attach_tooltip(tooltips.plotting.remove)
                            with dpg.group(horizontal=True):
                                dpg.add_text("Type".rjust(label_pad))
                                self.type_combo: int = dpg.generate_uuid()
                                dpg.add_combo(
                                    default_value=plot_type_to_label[PlotType.NYQUIST],
                                    items=list(
                                        map(
                                            lambda _: plot_type_to_label[_],
                                            [_ for _ in PlotType],
                                        )
                                    ),
                                    width=-64,
                                    tag=self.type_combo,
                                    callback=lambda s, a, u: signals.emit(
                                        Signal.SELECT_PLOT_TYPE,
                                        plot_type=label_to_plot_type.get(a),
                                        settings=dpg.get_item_user_data(
                                            self.delete_button
                                        ),
                                    ),
                                    user_data=PlotType.NYQUIST,
                                )
                        with dpg.child_window(width=sidebar_width, height=-40):
                            with dpg.tab_bar():
                                with dpg.tab(label="Available"):
                                    with dpg.group(horizontal=True):
                                        dpg.add_text("Filter")
                                        attach_tooltip(tooltips.plotting.filter)
                                        self.filter_input: int = dpg.generate_uuid()
                                        dpg.add_input_text(
                                            width=-1,
                                            callback=lambda s, a, u: self.filter_possible_series(
                                                a
                                            ),
                                            tag=self.filter_input,
                                        )
                                    with dpg.child_window(
                                        border=False, width=-1, height=-1
                                    ):
                                        self.possible_series_group: int = (
                                            dpg.generate_uuid()
                                        )
                                        with dpg.group(tag=self.possible_series_group):
                                            self.possible_data_sets: DataSetsGroup = (
                                                DataSetsGroup()
                                            )
                                            self.possible_tests: TestsGroup = (
                                                TestsGroup()
                                            )
                                            self.possible_drts: DRTsGroup = DRTsGroup()
                                            self.possible_fits: FitsGroup = FitsGroup()
                                            self.possible_simulations: SimulationsGroup = (
                                                SimulationsGroup()
                                            )
                                with dpg.tab(label="Active"):
                                    self.active_series: ActiveSeries = ActiveSeries()
                        with dpg.child_window(width=sidebar_width, height=-1):
                            with dpg.group(horizontal=True):
                                self.select_all_button: int = dpg.generate_uuid()
                                dpg.add_button(
                                    label="Select all",
                                    callback=lambda s, a, u: signals.emit(
                                        Signal.TOGGLE_PLOT_SERIES,
                                        enabled=True,
                                        **u,
                                    ),
                                    user_data={},
                                    tag=self.select_all_button,
                                )
                                attach_tooltip(tooltips.plotting.select_all)
                                self.unselect_all_button: int = dpg.generate_uuid()
                                dpg.add_button(
                                    label="Unselect all",
                                    callback=lambda s, a, u: signals.emit(
                                        Signal.TOGGLE_PLOT_SERIES,
                                        enabled=False,
                                        **u,
                                    ),
                                    user_data={},
                                    tag=self.unselect_all_button,
                                )
                                attach_tooltip(tooltips.plotting.unselect_all)
                                self.copy_appearances_button: int = dpg.generate_uuid()
                                dpg.add_button(
                                    label="Copy appearance",
                                    callback=lambda s, a, u: signals.emit(
                                        Signal.SELECT_PLOT_APPEARANCE_SETTINGS,
                                        settings=dpg.get_item_user_data(
                                            self.delete_button
                                        ),
                                    ),
                                    tag=self.copy_appearances_button,
                                )
                                attach_tooltip(tooltips.plotting.copy_appearance)
                                self.export_button: int = dpg.generate_uuid()
                                dpg.add_button(
                                    label="Export",
                                    callback=lambda s, a, u: signals.emit(
                                        Signal.EXPORT_PLOT, **u
                                    ),
                                    user_data={},
                                    tag=self.export_button,
                                )
                                attach_tooltip(tooltips.plotting.export_plot)
                    with dpg.child_window(border=False, width=-1, height=-1):
                        self.plots_group: int = dpg.generate_uuid()
                        self.plot_height: int = -24
                        with dpg.group(tag=self.plots_group):
                            self.plot_types[PlotType.NYQUIST] = Nyquist(
                                width=-1,
                                height=self.plot_height,
                                legend_horizontal=False,
                                legend_location=dpg.mvPlot_Location_NorthEast,
                                legend_outside=False,
                            )
                            self.plot_types[PlotType.BODE_MAGNITUDE] = BodeMagnitude(
                                width=-1,
                                height=self.plot_height,
                                legend_horizontal=False,
                                legend_location=dpg.mvPlot_Location_NorthEast,
                                legend_outside=False,
                            )
                            self.plot_types[PlotType.BODE_PHASE] = BodePhase(
                                width=-1,
                                height=self.plot_height,
                                legend_horizontal=False,
                                legend_location=dpg.mvPlot_Location_NorthEast,
                                legend_outside=False,
                            )
                            self.plot_types[PlotType.IMPEDANCE_REAL] = ImpedanceReal(
                                width=-1,
                                height=self.plot_height,
                                legend_horizontal=False,
                                legend_location=dpg.mvPlot_Location_NorthEast,
                                legend_outside=False,
                            )
                            self.plot_types[
                                PlotType.IMPEDANCE_IMAGINARY
                            ] = ImpedanceImaginary(
                                width=-1,
                                height=self.plot_height,
                                legend_horizontal=False,
                                legend_location=dpg.mvPlot_Location_NorthEast,
                                legend_outside=False,
                            )
                            self.plot_types[PlotType.DRT] = DRT(
                                width=-1,
                                height=self.plot_height,
                                legend_horizontal=False,
                                legend_location=dpg.mvPlot_Location_NorthEast,
                                legend_outside=False,
                            )
                            self.plot_types[PlotType.BODE_MAGNITUDE].hide()
                            self.plot_types[PlotType.BODE_PHASE].hide()
                            self.plot_types[PlotType.IMPEDANCE_REAL].hide()
                            self.plot_types[PlotType.IMPEDANCE_IMAGINARY].hide()
                            self.plot_types[PlotType.DRT].hide()
                        with dpg.child_window(border=False):
                            with dpg.group(horizontal=True):
                                self.expand_sidebar_button: int = dpg.generate_uuid()
                                dpg.add_button(
                                    label="Collapse",
                                    show=True,
                                    callback=self.collapse_expand_sidebar,
                                    tag=self.expand_sidebar_button,
                                )
                                attach_tooltip(
                                    tooltips.plotting.collapse_expand_sidebar
                                )
                                self.visibility_item: int = dpg.generate_uuid()
                                self.adjust_limits_checkbox: int = dpg.generate_uuid()
                                dpg.add_checkbox(
                                    default_value=True,
                                    tag=self.adjust_limits_checkbox,
                                )
                                attach_tooltip(tooltips.general.adjust_limits)
                                dpg.add_button(
                                    label="Copy as CSV",
                                    callback=lambda s, a, u: signals.emit(
                                        Signal.COPY_PLOT_DATA,
                                        context=Context.PLOTTING_TAB,
                                        plot=self.plot_types[
                                            dpg.get_item_user_data(self.type_combo)
                                        ],
                                    ),
                                    tag=self.visibility_item,
                                )
                                attach_tooltip(tooltips.general.copy_plot_data_as_csv)

    def resize(self, width: int, height: int):
        assert type(width) is int and width > 0
        assert type(height) is int and height > 0

    def is_visible(self) -> bool:
        return dpg.is_item_visible(self.visibility_item)

    def collapse_expand_sidebar(self):
        if self.is_sidebar_shown():
            dpg.set_item_label(self.expand_sidebar_button, "Expand")
            dpg.hide_item(self.sidebar_window)
        else:
            dpg.set_item_label(self.expand_sidebar_button, "Collapse")
            dpg.show_item(self.sidebar_window)

    def is_sidebar_shown(self) -> bool:
        return dpg.is_item_shown(self.sidebar_window)

    def populate_plots(self, plots: Dict[str, PlotSettings]):
        assert type(plots) is dict, plots
        labels: List[str] = list(plots.keys())
        label: str = dpg.get_value(self.plot_combo) or ""
        update_plot: bool = label not in labels
        if update_plot and labels:
            label = labels[0]
        dpg.configure_item(
            self.plot_combo,
            default_value=label,
            items=labels,
            user_data=plots,
        )
        if not plots:
            signals.emit(Signal.NEW_PLOT_SETTINGS)

    def plot_series(
        self,
        data_sets: List[DataSet],
        tests: Dict[str, List[TestResult]],
        drts: Dict[str, List[DRTResult]],
        fits: Dict[str, List[FitResult]],
        simulations: List[SimulationResult],
        settings: PlotSettings,
        adjust_limits: bool = True,
    ):
        assert type(data_sets) is list, data_sets
        assert type(tests) is dict, tests
        assert type(drts) is dict, drts
        assert type(fits) is dict, fits
        assert type(simulations) is list, simulations
        assert type(settings) is PlotSettings, settings
        assert type(adjust_limits) is bool, adjust_limits
        self.series_tags.clear()
        uuid: str
        label: Optional[str]
        is_simulation: bool
        is_fit: bool
        theme: Optional[int]
        from_empty: bool = False
        changed_plot_settings: bool = self.plotted_uuid != settings.uuid
        self.plotted_uuid = settings.uuid
        visible_plots: List[Plot] = []
        hidden_plots: List[Plot] = []
        plot: Plot
        for plot in self.plot_types.values():
            if plot.is_visible():
                visible_plots.append(plot)
            else:
                hidden_plots.append(plot)
        plot_type: PlotType = settings.get_type()
        plot = self.plot_types[plot_type]
        list(map(lambda _: _.clear(), visible_plots))
        list(map(lambda _: _.clear(), hidden_plots))
        if plot in hidden_plots:
            list(map(lambda _: _.hide(), visible_plots))
            plot.show()
            from_empty = True
        elif len(plot.get_series()) == 0:
            from_empty = True
        plot.clear()
        dpg.split_frame()
        plot.set_title(settings.get_label())
        for uuid in settings.series_order:
            series: Optional[
                Union[DataSet, TestResult, DRTResult, FitResult, SimulationResult]
            ]
            series = settings.find_series(
                uuid, data_sets, tests, drts, fits, simulations
            )
            if series is None:
                settings.series_order.remove(uuid)
                continue
            label = settings.get_series_label(uuid)
            show_label: bool = True
            if label == "":
                label = series.get_label()
            elif label.strip() == "":
                label = series.get_label()
                show_label = False
            is_simulation = type(series) is SimulationResult
            is_fit = (
                type(series) is FitResult
                or type(series) is TestResult
                or type(series) is DRTResult
            )
            theme = settings.get_series_theme(uuid)
            if theme < 0:
                theme = None
            real: ndarray
            imag: ndarray
            freq: ndarray
            mag: ndarray
            phase: ndarray
            tau: ndarray
            gamma: ndarray
            if plot_type == PlotType.NYQUIST:
                if settings.get_series_marker(uuid) >= 0:
                    real, imag = series.get_nyquist_data()
                    self.series_tags[series.uuid] = plot.plot(
                        real=real,
                        imaginary=imag,
                        label=label,
                        simulation=is_simulation,
                        fit=is_fit,
                        line=False,
                        theme=theme,
                        show_label=show_label,
                    )
                    if (is_simulation or is_fit) and "num_per_decade" in signature(
                        series.get_nyquist_data
                    ).parameters:
                        real, imag = series.get_nyquist_data(
                            num_per_decade=self.state.config.num_per_decade_in_simulated_lines
                        )
                    if settings.get_series_line(uuid):
                        plot.plot(
                            real=real,
                            imaginary=imag,
                            label=label,
                            simulation=is_simulation,
                            fit=is_fit,
                            line=True,
                            theme=theme,
                            show_label=False,
                        )
                elif settings.get_series_line(uuid):
                    if (is_simulation or is_fit) and "num_per_decade" in signature(
                        series.get_nyquist_data
                    ).parameters:
                        real, imag = series.get_nyquist_data(
                            num_per_decade=self.state.config.num_per_decade_in_simulated_lines
                        )
                    else:
                        real, imag = series.get_nyquist_data()
                    self.series_tags[series.uuid] = plot.plot(
                        real=real,
                        imaginary=imag,
                        label=label,
                        simulation=is_simulation,
                        fit=is_fit,
                        line=True,
                        theme=theme,
                        show_label=show_label,
                    )
            elif plot_type == PlotType.BODE_MAGNITUDE:
                if settings.get_series_marker(uuid) >= 0:
                    freq, mag, _ = series.get_bode_data()
                    self.series_tags[series.uuid] = plot.plot(
                        frequency=freq,
                        magnitude=mag,
                        label=label,
                        simulation=is_simulation,
                        fit=is_fit,
                        line=False,
                        theme=theme,
                        show_label=show_label,
                    )
                    if (is_simulation or is_fit) and "num_per_decade" in signature(
                        series.get_bode_data
                    ).parameters:
                        freq, mag, _ = series.get_bode_data(
                            num_per_decade=self.state.config.num_per_decade_in_simulated_lines
                        )
                    if settings.get_series_line(uuid):
                        plot.plot(
                            frequency=freq,
                            magnitude=mag,
                            label=label,
                            simulation=is_simulation,
                            fit=is_fit,
                            line=True,
                            theme=theme,
                            show_label=False,
                        )
                elif settings.get_series_line(uuid):
                    if (is_simulation or is_fit) and "num_per_decade" in signature(
                        series.get_bode_data
                    ).parameters:
                        freq, mag, _ = series.get_bode_data(
                            num_per_decade=self.state.config.num_per_decade_in_simulated_lines
                        )
                    else:
                        freq, mag, _ = series.get_bode_data()
                    self.series_tags[series.uuid] = plot.plot(
                        frequency=freq,
                        magnitude=mag,
                        label=label,
                        simulation=is_simulation,
                        fit=is_fit,
                        line=True,
                        theme=theme,
                        show_label=show_label,
                    )
            elif plot_type == PlotType.BODE_PHASE:
                if settings.get_series_marker(uuid) >= 0:
                    freq, _, phase = series.get_bode_data()
                    self.series_tags[series.uuid] = plot.plot(
                        frequency=freq,
                        phase=phase,
                        label=label,
                        simulation=is_simulation,
                        fit=is_fit,
                        line=False,
                        theme=theme,
                        show_label=show_label,
                    )
                    if (is_simulation or is_fit) and "num_per_decade" in signature(
                        series.get_bode_data
                    ).parameters:
                        freq, _, phase = series.get_bode_data(
                            num_per_decade=self.state.config.num_per_decade_in_simulated_lines
                        )
                    if settings.get_series_line(uuid):
                        plot.plot(
                            frequency=freq,
                            phase=phase,
                            label=label,
                            simulation=is_simulation,
                            fit=is_fit,
                            line=True,
                            theme=theme,
                            show_label=False,
                        )
                elif settings.get_series_line(uuid):
                    if (is_simulation or is_fit) and "num_per_decade" in signature(
                        series.get_bode_data
                    ).parameters:
                        freq, _, phase = series.get_bode_data(
                            num_per_decade=self.state.config.num_per_decade_in_simulated_lines
                        )
                    else:
                        freq, _, phase = series.get_bode_data()
                    self.series_tags[series.uuid] = plot.plot(
                        frequency=freq,
                        phase=phase,
                        label=label,
                        simulation=is_simulation,
                        fit=is_fit,
                        line=True,
                        theme=theme,
                        show_label=show_label,
                    )
            elif plot_type == PlotType.DRT:
                if type(series) is not DRTResult:
                    continue
                if series.settings.method == DRTMethod.BHT:
                    tau, gamma = series.get_drt_data()
                    self.series_tags[series.uuid] = plot.plot(
                        tau=tau,
                        gamma=gamma,
                        label=f"{label}, real" if label is not None else label,
                        line=True,
                        theme=theme,
                        show_label=show_label,
                    )
                    tau, gamma = series.get_drt_data(imaginary=True)
                    self.series_tags[f"{series.uuid}_imaginary"] = plot.plot(
                        tau=tau,
                        gamma=gamma,
                        label=f"{label}, imag." if label is not None else label,
                        line=True,
                        theme=theme,
                        show_label=show_label,
                    )
                elif (
                    series.settings.method == DRTMethod.TR_RBF
                    and series.settings.credible_intervals is True
                ):
                    tau, mean, lower, upper = series.get_drt_credible_intervals()
                    alt_color: List[float] = settings.get_series_color(uuid).copy()
                    alt_color[-1] = themes.get_plot_series_theme_color(
                        themes.drt.credible_intervals
                    )[-1]
                    self.series_tags[f"{series.uuid}_bounds"] = plot.plot(
                        tau=tau,
                        lower=lower,
                        upper=upper,
                        label=f"{label}, 3-sigma CI" if label is not None else label,
                        theme=themes.create_plot_series_theme(
                            alt_color,
                            dpg.mvPlotMarker_Circle,
                        ),
                        show_label=True,
                    )
                    self.series_tags[f"{series.uuid}_mean"] = plot.plot(
                        tau=tau,
                        gamma=mean,
                        label=f"{label}, mean" if label is not None else label,
                        line=True,
                        theme=theme,
                        show_label=show_label,
                    )
                    tau, gamma = series.get_drt_data()
                    self.series_tags[series.uuid] = plot.plot(
                        tau=tau,
                        gamma=gamma,
                        label=label,
                        line=True,
                        theme=theme,
                        show_label=show_label,
                    )
                else:
                    tau, gamma = series.get_drt_data()
                    self.series_tags[series.uuid] = plot.plot(
                        tau=tau,
                        gamma=gamma,
                        label=label,
                        line=True,
                        theme=theme,
                        show_label=show_label,
                    )
            elif plot_type == PlotType.IMPEDANCE_REAL:
                if settings.get_series_marker(uuid) >= 0:
                    freq = series.get_frequency()
                    real = series.get_impedance().real
                    self.series_tags[series.uuid] = plot.plot(
                        x=freq,
                        y=real,
                        label=label,
                        line=False,
                        theme=theme,
                        show_label=show_label,
                    )
                    if (
                        (is_simulation or is_fit)
                        and "num_per_decade"
                        in signature(series.get_frequency).parameters
                        and "num_per_decade"
                        in signature(series.get_impedance).parameters
                    ):
                        freq = series.get_frequency(
                            num_per_decade=self.state.config.num_per_decade_in_simulated_lines
                        )
                        real = series.get_impedance(
                            num_per_decade=self.state.config.num_per_decade_in_simulated_lines
                        ).real
                    if settings.get_series_line(uuid):
                        plot.plot(
                            x=freq,
                            y=real,
                            label=label,
                            line=True,
                            theme=theme,
                            show_label=False,
                        )
                elif settings.get_series_line(uuid):
                    if (
                        (is_simulation or is_fit)
                        and "num_per_decade"
                        in signature(series.get_frequency).parameters
                        and "num_per_decade"
                        in signature(series.get_impedance).parameters
                    ):
                        freq = series.get_frequency(
                            num_per_decade=self.state.config.num_per_decade_in_simulated_lines
                        )
                        real = series.get_impedance(
                            num_per_decade=self.state.config.num_per_decade_in_simulated_lines
                        ).real
                    else:
                        freq = series.get_frequency()
                        real = series.get_impedance().real
                    self.series_tags[series.uuid] = plot.plot(
                        x=freq,
                        y=real,
                        label=label,
                        line=True,
                        theme=theme,
                        show_label=False,
                    )
            elif plot_type == PlotType.IMPEDANCE_IMAGINARY:
                if settings.get_series_marker(uuid) >= 0:
                    freq = series.get_frequency()
                    imag = -series.get_impedance().imag
                    self.series_tags[series.uuid] = plot.plot(
                        x=freq,
                        y=imag,
                        label=label,
                        line=False,
                        theme=theme,
                        show_label=show_label,
                    )
                    if (
                        (is_simulation or is_fit)
                        and "num_per_decade"
                        in signature(series.get_frequency).parameters
                        and "num_per_decade"
                        in signature(series.get_impedance).parameters
                    ):
                        freq = series.get_frequency(
                            num_per_decade=self.state.config.num_per_decade_in_simulated_lines
                        )
                        imag = -series.get_impedance(
                            num_per_decade=self.state.config.num_per_decade_in_simulated_lines
                        ).imag
                    if settings.get_series_line(uuid):
                        plot.plot(
                            x=freq,
                            y=imag,
                            label=label,
                            line=True,
                            theme=theme,
                            show_label=False,
                        )
                elif settings.get_series_line(uuid):
                    if (
                        (is_simulation or is_fit)
                        and "num_per_decade"
                        in signature(series.get_frequency).parameters
                        and "num_per_decade"
                        in signature(series.get_impedance).parameters
                    ):
                        freq = series.get_frequency(
                            num_per_decade=self.state.config.num_per_decade_in_simulated_lines
                        )
                        imag = -series.get_impedance(
                            num_per_decade=self.state.config.num_per_decade_in_simulated_lines
                        ).imag
                    else:
                        freq = series.get_frequency()
                        imag = -series.get_impedance().imag
                    self.series_tags[series.uuid] = plot.plot(
                        x=freq,
                        y=imag,
                        label=label,
                        line=True,
                        theme=theme,
                        show_label=False,
                    )
        if not adjust_limits:
            return
        if dpg.get_value(self.adjust_limits_checkbox) and (
            from_empty or changed_plot_settings
        ):
            plot.queue_limits_adjustment()

    def set_series_label(self, uuid: str, label: Optional[str]):
        assert type(uuid) is str, uuid
        assert type(label) is str or label is None, label
        assert uuid in self.series_tags, self.series_tags
        for uuid in filter(lambda _: _.startswith(uuid), self.series_tags.keys()):
            if label == "":
                dpg.set_item_label(self.series_tags[uuid], "")
            elif f"{uuid}_imaginary" in self.series_tags:
                dpg.set_item_label(self.series_tags[uuid], f"{label}, real")
            elif uuid.endswith("_imaginary"):
                dpg.set_item_label(self.series_tags[uuid], f"{label}, imag.")
            elif uuid.endswith("_mean"):
                dpg.set_item_label(self.series_tags[uuid], f"{label}, mean")
            else:
                dpg.set_item_label(self.series_tags[uuid], label)

    def get_active_plot(self) -> Optional[PlotSettings]:
        return dpg.get_item_user_data(self.delete_button)

    def get_next_plot(self) -> Optional[PlotSettings]:
        settings: Optional[PlotSettings] = self.get_active_plot()
        lookup: Optional[Dict[str, PlotSettings]] = dpg.get_item_user_data(
            self.plot_combo
        )
        if settings is None or lookup is None:
            return None
        plots: List[PlotSettings] = list(lookup.values())
        if settings not in plots:
            return None
        index: int = plots.index(settings) + 1
        return plots[index % len(plots)]

    def get_previous_plot(self) -> Optional[PlotSettings]:
        settings: Optional[PlotSettings] = self.get_active_plot()
        lookup: Optional[Dict[str, PlotSettings]] = dpg.get_item_user_data(
            self.plot_combo
        )
        if settings is None or lookup is None:
            return None
        plots: List[PlotSettings] = list(lookup.values())
        if settings not in plots:
            return None
        index: int = plots.index(settings) - 1
        return plots[index % len(plots)]

    def get_next_plot_type(self) -> Optional[PlotType]:
        settings: Optional[PlotSettings] = self.get_active_plot()
        if settings is None:
            return None
        plot_types: List[PlotType] = [_ for _ in PlotType]
        index: int = plot_types.index(settings.get_type()) + 1
        return plot_types[index % len(plot_types)]

    def get_previous_plot_type(self) -> Optional[PlotType]:
        settings: Optional[PlotSettings] = self.get_active_plot()
        if settings is None:
            return None
        plot_types: List[PlotType] = [_ for _ in PlotType]
        index: int = plot_types.index(settings.get_type()) - 1
        return plot_types[index % len(plot_types)]

    def select_plot(
        self,
        settings: PlotSettings,
        data_sets: List[DataSet],
        tests: Dict[str, List[TestResult]],
        drts: Dict[str, List[DRTResult]],
        fits: Dict[str, List[FitResult]],
        simulations: List[SimulationResult],
        adjust_limits: bool,
        plot_only: bool,
    ):
        assert type(settings) is PlotSettings, settings
        assert type(data_sets) is list, data_sets
        assert type(tests) is dict, tests
        assert type(drts) is dict, drts
        assert type(fits) is dict, fits
        assert type(simulations) is list, simulations
        assert type(adjust_limits) is bool, adjust_limits
        assert type(plot_only) is bool, plot_only
        dpg.set_item_user_data(self.delete_button, settings)
        dpg.set_item_user_data(self.export_button, {"settings": settings})
        if not self.is_visible():
            self.queued_update = lambda: self.select_plot(
                settings,
                data_sets,
                tests,
                drts,
                fits,
                simulations,
                adjust_limits,
                plot_only,
            )
            return
        self.queued_update = None
        if not plot_only:
            dpg.set_value(self.plot_combo, settings.get_label())
            dpg.set_value(self.label_input, settings.get_label())
            self.populate_possible_series(
                data_sets,
                tests,
                drts,
                fits,
                simulations,
                settings,
            )
            self.active_series.populate(
                data_sets,
                tests,
                drts,
                fits,
                simulations,
                settings,
            )
        self.select_plot_type(settings.get_type())
        dpg.split_frame()
        self.plot_series(
            data_sets,
            tests,
            drts,
            fits,
            simulations,
            settings,
            adjust_limits,
        )

    def populate_possible_series(
        self,
        data_sets: List[DataSet],
        tests: Dict[str, List[TestResult]],
        drts: Dict[str, List[DRTResult]],
        fits: Dict[str, List[FitResult]],
        simulations: List[SimulationResult],
        settings: PlotSettings,
    ):
        assert type(data_sets) is list, data_sets
        assert type(tests) is dict, tests
        assert type(drts) is dict, drts
        assert type(fits) is dict, fits
        assert type(simulations) is list, simulations
        assert type(settings) is PlotSettings, settings
        self.populate_data_sets(data_sets, settings)
        self.populate_tests(tests, data_sets, settings)
        self.populate_drts(drts, data_sets, settings)
        self.populate_fits(fits, data_sets, settings)
        self.populate_simulations(simulations, settings)
        dpg.get_item_user_data(self.select_all_button).update({"settings": settings})
        dpg.get_item_user_data(self.unselect_all_button).update({"settings": settings})

    def get_filter_string(self) -> str:
        return dpg.get_value(self.filter_input).strip().lower()

    def populate_data_sets(self, data_sets: List[DataSet], settings: PlotSettings):
        assert type(data_sets) is list, data_sets
        assert type(settings) is PlotSettings, settings
        if not self.possible_data_sets.populate(data_sets, settings):
            self.possible_data_sets.update(
                ",".join(sorted(settings.series_order)) + f",{settings.uuid}",
                data_sets,
                settings,
            )
        dpg.get_item_user_data(self.possible_data_sets.select_all_button).update(
            {
                "enabled": True,
                "data_sets": data_sets,
                "settings": settings,
            }
        )
        dpg.get_item_user_data(self.possible_data_sets.unselect_all_button).update(
            {
                "enabled": False,
                "data_sets": data_sets,
                "settings": settings,
            }
        )
        data_sets = self.possible_data_sets.filter(self.get_filter_string(), False)
        dpg.get_item_user_data(self.select_all_button).update(
            {
                "data_sets": data_sets,
                "settings": settings,
            }
        )
        dpg.get_item_user_data(self.unselect_all_button).update(
            {
                "data_sets": data_sets,
                "settings": settings,
            }
        )

    def populate_tests(
        self,
        tests: Dict[str, List[TestResult]],
        data_sets: List[DataSet],
        settings: PlotSettings,
    ):
        assert type(tests) is dict, tests
        assert type(data_sets) is list, data_sets
        assert type(settings) is PlotSettings, settings
        self.possible_tests.populate(tests, data_sets, settings)
        user_data: List[TestResult] = self.possible_tests.filter(
            self.get_filter_string(), False
        )
        dpg.get_item_user_data(self.select_all_button).update(
            {
                "tests": user_data,
                "settings": settings,
            }
        )
        dpg.get_item_user_data(self.unselect_all_button).update(
            {
                "tests": user_data,
                "settings": settings,
            }
        )

    def populate_drts(
        self,
        drts: Dict[str, List[DRTResult]],
        data_sets: List[DataSet],
        settings: PlotSettings,
    ):
        assert type(drts) is dict, drts
        assert type(data_sets) is list, data_sets
        assert type(settings) is PlotSettings, settings
        self.possible_drts.populate(drts, data_sets, settings)
        user_data: List[DRTResult] = self.possible_drts.filter(
            self.get_filter_string(),
            False,
        )
        dpg.get_item_user_data(self.select_all_button).update(
            {
                "drts": user_data,
                "settings": settings,
            }
        )
        dpg.get_item_user_data(self.unselect_all_button).update(
            {
                "drts": user_data,
                "settings": settings,
            }
        )

    def populate_fits(
        self,
        fits: Dict[str, List[FitResult]],
        data_sets: List[DataSet],
        settings: PlotSettings,
    ):
        assert type(fits) is dict, fits
        assert type(data_sets) is list, data_sets
        assert type(settings) is PlotSettings, settings
        self.possible_fits.populate(fits, data_sets, settings)
        user_data: List[FitResult] = self.possible_fits.filter(
            self.get_filter_string(), False
        )
        dpg.get_item_user_data(self.select_all_button).update(
            {
                "fits": user_data,
                "settings": settings,
            }
        )
        dpg.get_item_user_data(self.unselect_all_button).update(
            {
                "fits": user_data,
                "settings": settings,
            }
        )

    def populate_simulations(
        self, simulations: List[SimulationResult], settings: PlotSettings
    ):
        assert type(simulations) is list, simulations
        assert type(settings) is PlotSettings, settings
        if not self.possible_simulations.populate(simulations, settings):
            self.possible_simulations.update(
                ",".join(sorted(settings.series_order)) + f",{settings.uuid}",
                simulations,
                settings,
            )
        dpg.get_item_user_data(self.possible_simulations.select_all_button).update(
            {
                "enabled": True,
                "simulations": simulations,
                "settings": settings,
            }
        )
        dpg.get_item_user_data(self.possible_simulations.unselect_all_button).update(
            {
                "enabled": False,
                "simulations": simulations,
                "settings": settings,
            }
        )
        simulations = self.possible_simulations.filter(self.get_filter_string(), False)
        dpg.get_item_user_data(self.select_all_button).update(
            {
                "simulations": simulations,
                "settings": settings,
            }
        )
        dpg.get_item_user_data(self.unselect_all_button).update(
            {
                "simulations": simulations,
                "settings": settings,
            }
        )

    def select_plot_type(self, plot_type: PlotType):
        assert type(plot_type) is PlotType, plot_type
        dpg.set_value(self.type_combo, plot_type_to_label.get(plot_type))
        dpg.set_item_user_data(self.type_combo, plot_type)
        for typ, plot in self.plot_types.items():
            if typ == plot_type:
                dpg.show_item(plot._plot)
            else:
                dpg.hide_item(plot._plot)

    def filter_possible_series(
        self, string: str
    ) -> Tuple[
        List[DataSet],
        List[TestResult],
        List[DRTResult],
        List[FitResult],
        List[SimulationResult],
    ]:
        string = string.lower()
        data_sets: List[DataSet] = self.possible_data_sets.filter(string, True)
        tests: List[TestResult] = self.possible_tests.filter(string, True)
        drts: List[DRTResult] = self.possible_drts.filter(string, True)
        fits: List[FitResult] = self.possible_fits.filter(string, True)
        simulations: List[SimulationResult] = self.possible_simulations.filter(
            string, True
        )
        dpg.get_item_user_data(self.select_all_button).update(
            {
                "data_sets": data_sets,
                "tests": tests,
                "drts": drts,
                "fits": fits,
                "simulations": simulations,
            }
        )
        dpg.get_item_user_data(self.unselect_all_button).update(
            {
                "data_sets": data_sets,
                "tests": tests,
                "drts": drts,
                "fits": fits,
                "simulations": simulations,
            }
        )
        return (
            data_sets,
            tests,
            drts,
            fits,
            simulations,
        )

    def has_active_input(self) -> bool:
        return (
            dpg.is_item_active(self.label_input)
            or dpg.is_item_active(self.filter_input)
            or self.active_series.has_active_input()
        )
