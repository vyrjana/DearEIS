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
    Any,
    Callable,
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


class ResultPalette(BasePalette):
    def __init__(self):
        super().__init__(
            title="Result palette",
            tooltip="Select a result to show.\n\n",
        )
        self.histories: Dict[Project, Dict[Context, Dict[DataSet, List[Option]]]] = {}

    def show(
        self,
        project: Optional[Project],
        tab: Optional[ProjectTab],
    ):
        active_result_lookup: Dict[Context, Callable] = {
            Context.KRAMERS_KRONIG_TAB: tab.get_active_test,
            Context.ZHIT_TAB: tab.get_active_zhit,
            Context.DRT_TAB: tab.get_active_drt,
            Context.FITTING_TAB: tab.get_active_fit,
            Context.SIMULATION_TAB: tab.get_active_simulation,
            Context.PLOTTING_TAB: tab.get_active_plot,
        }
        context: Context = tab.get_active_context()
        if context not in active_result_lookup:
            return
        self.active_data_set: Optional[DataSet] = tab.get_active_data_set()
        self.context = context
        self.project: Optional[Project] = project
        self.tab: Optional[ProjectTab] = tab
        if project not in self.histories:
            self.histories[project] = {}
        if context not in self.histories[project]:
            self.histories[project][context] = {}
        if self.active_data_set not in self.histories[project][context]:
            self.histories[project][context][self.active_data_set] = []
        self.options_history = self.histories[project][context][self.active_data_set]
        self.options = []
        active_result: Optional[Any] = active_result_lookup[context]()
        i: int
        result: Any
        for i, result in enumerate(self.generate_options()):
            if result == active_result:
                continue
            self.options.append(
                Option(
                    description=self.format_result_label(result.get_label()),
                    rank=i,
                    data=result,
                )
            )
        super().show()

    def format_result_label(self, label: str) -> str:
        i: int = label.rfind(" (")
        if i < 0:
            return label
        timestamp: str
        label, timestamp = (label[:i], label[i + 1 :])
        max_length: int = 96 - len(timestamp)
        if max_length < 5:
            max_length = 5
        label = label.ljust(max_length)
        if len(label.strip()) > max_length:
            label = label[: max_length - 3] + "..."
        return f"{label} {timestamp}"

    def generate_options(self) -> List[Any]:
        if self.active_data_set is None and self.context not in (
            Context.SIMULATION_TAB,
            Context.PLOTTING_TAB,
        ):
            return []
        return {
            Context.KRAMERS_KRONIG_TAB: self.project.get_tests,
            Context.ZHIT_TAB: self.project.get_zhits,
            Context.DRT_TAB: self.project.get_drts,
            Context.FITTING_TAB: self.project.get_fits,
            Context.SIMULATION_TAB: lambda _: self.project.get_simulations(),
            Context.PLOTTING_TAB: lambda _: self.project.get_plots(),
        }.get(self.context, lambda _: [])(self.active_data_set)

    def select_option(self, option: Optional[Option] = None, click: bool = False):
        if option is None:
            return
        self.hide()
        if option in self.options_history:
            self.options_history.remove(option)
        self.options_history.insert(0, option)
        signal: Signal = {
            Context.KRAMERS_KRONIG_TAB: Signal.SELECT_TEST_RESULT,
            Context.ZHIT_TAB: Signal.SELECT_ZHIT_RESULT,
            Context.DRT_TAB: Signal.SELECT_DRT_RESULT,
            Context.FITTING_TAB: Signal.SELECT_FIT_RESULT,
            Context.SIMULATION_TAB: Signal.SELECT_SIMULATION_RESULT,
            Context.PLOTTING_TAB: Signal.SELECT_PLOT_SETTINGS,
        }[self.context]
        kwargs: dict
        if self.context == Context.PLOTTING_TAB:
            kwargs = {
                "settings": option.data,
            }
        else:
            key: str = {
                Context.KRAMERS_KRONIG_TAB: "test",
                Context.ZHIT_TAB: "zhit",
                Context.DRT_TAB: "drt",
                Context.FITTING_TAB: "fit",
                Context.SIMULATION_TAB: "simulation",
            }[self.context]
            kwargs = {
                key: option.data,
                "data": self.active_data_set,
            }
        signals.emit(
            signal,
            **kwargs,
        )
