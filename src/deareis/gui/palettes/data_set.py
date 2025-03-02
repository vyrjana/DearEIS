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
    Dict,
    List,
    Optional,
)
from deareis.enums import Context
from deareis.data import DataSet
from deareis.signals import Signal
import deareis.signals as signals
from deareis.data.project import Project
from deareis.gui.project import ProjectTab
from .base import (
    BasePalette,
    Option,
)


class DataSetPalette(BasePalette):
    def __init__(self):
        super().__init__(
            title="Data set palette",
            tooltip="Select a data set to show.\n\n",
        )
        self.histories: Dict[Project, List[Option]] = {}

    def show(
        self,
        project: Optional[Project],
        tab: Optional[ProjectTab],
    ):
        context: Context = tab.get_active_context()
        if context not in (
            Context.DATA_SETS_TAB,
            Context.KRAMERS_KRONIG_TAB,
            Context.ZHIT_TAB,
            Context.DRT_TAB,
            Context.FITTING_TAB,
            Context.SIMULATION_TAB,
        ):
            return
        self.context: Context = tab.get_active_context()
        self.project: Optional[Project] = project
        self.tab: Optional[ProjectTab] = tab
        if project not in self.histories:
            self.histories[project] = []
        self.options_history = self.histories[project]
        self.options = []
        active_data_set: Optional[DataSet] = tab.get_active_data_set()
        i: int = 0
        data: DataSet
        for i, data in enumerate(project.get_data_sets()):
            if data == active_data_set:
                continue
            self.options.append(
                Option(
                    description=data.get_label(),
                    rank=i,
                    data=data,
                )
            )
        if self.context == Context.SIMULATION_TAB:
            self.options.append(
                Option(
                    description="None",
                    rank=i+1,
                    data=None,
                )
            )
        super().show()

    def select_option(self, option: Optional[Option] = None, click: bool = False):
        if option is None:
            return
        self.hide()
        if option in self.options_history:
            self.options_history.remove(option)
        self.options_history.insert(0, option)
        if self.context == Context.SIMULATION_TAB:
            signals.emit(
                Signal.SELECT_SIMULATION_RESULT,
                simulation=self.tab.get_active_simulation(),
                data=option.data,
            )
        else:
            signals.emit(Signal.SELECT_DATA_SET, data=option.data)
