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

from typing import (
    Dict,
    List,
    Optional,
    Tuple,
)
import dearpygui.dearpygui as dpg
from deareis.gui.plots import Plot
from deareis.gui.data_sets import DataSetsTab
from deareis.gui.drt import DRTTab
from deareis.gui.fitting import FittingTab
from deareis.gui.kramers_kronig import KramersKronigTab
from deareis.gui.overview import OverviewTab
from deareis.gui.plotting import PlottingTab
from deareis.gui.simulation import SimulationTab
from deareis.signals import Signal
import deareis.signals as signals
from deareis.enums import (
    PlotType,
    FitSimOutput,
)
from deareis.data import (
    DRTResult,
    DRTSettings,
    DataSet,
    FitResult,
    FitSettings,
    PlotSettings,
    Project,
    SimulationResult,
    SimulationSettings,
    TestResult,
    TestSettings,
)
import deareis.themes as themes
from deareis.keybindings import Context


class ProjectTab:
    def __init__(self, uuid: str, tab_bar: int, state):
        assert type(uuid) is str, uuid
        assert type(tab_bar) is int, tab_bar
        self.uuid: str = uuid
        self.tab: int = dpg.generate_uuid()
        with dpg.tab(
            label="Project",
            order_mode=dpg.mvTabOrder_Reorderable,
            user_data=uuid,
            tag=self.tab,
            parent=tab_bar,
        ):
            tab_lookup: dict = {}
            self.context_lookup: Dict[int, Context] = {}

            def select_tab(tab_id: int):
                tab = tab_lookup.get(tab_id)
                assert tab is not None
                tab.resize(
                    width=dpg.get_viewport_width(),
                    height=dpg.get_viewport_height(),
                )
                if hasattr(tab, "queued_update") and tab.queued_update is not None:
                    tab.queued_update()

            self.tab_bar: int = dpg.generate_uuid()
            with dpg.tab_bar(
                callback=lambda s, a, u: select_tab(a),
                tag=self.tab_bar,
            ):
                self.overview_tab: OverviewTab = OverviewTab()
                self.data_sets_tab: DataSetsTab = DataSetsTab()
                self.kramers_kronig_tab: KramersKronigTab = KramersKronigTab(state)
                self.drt_tab: DRTTab = DRTTab(state)
                self.fitting_tab: FittingTab = FittingTab(state)
                self.simulation_tab: SimulationTab = SimulationTab(state)
                self.plotting_tab: PlottingTab = PlottingTab(state)
            tab_lookup.update(
                {
                    self.overview_tab.tab: self.overview_tab,
                    self.data_sets_tab.tab: self.data_sets_tab,
                    self.kramers_kronig_tab.tab: self.kramers_kronig_tab,
                    self.drt_tab.tab: self.drt_tab,
                    self.fitting_tab.tab: self.fitting_tab,
                    self.simulation_tab.tab: self.simulation_tab,
                    self.plotting_tab.tab: self.plotting_tab,
                }
            )
            self.context_lookup.update(
                {
                    self.overview_tab.tab: Context.OVERVIEW_TAB,
                    self.data_sets_tab.tab: Context.DATA_SETS_TAB,
                    self.kramers_kronig_tab.tab: Context.KRAMERS_KRONIG_TAB,
                    self.drt_tab.tab: Context.DRT_TAB,
                    self.fitting_tab.tab: Context.FITTING_TAB,
                    self.simulation_tab.tab: Context.SIMULATION_TAB,
                    self.plotting_tab.tab: Context.PLOTTING_TAB,
                }
            )

            def visibility_handler(tab):
                if not dpg.does_item_exist(tab.tab):
                    return
                elif not tab.is_visible():
                    return
                elif hasattr(tab, "queued_update") and tab.queued_update is not None:
                    tab.queued_update()

            for tab in tab_lookup.values():
                if not (hasattr(tab, "is_visible") and hasattr(tab, "visibility_item")):
                    continue
                item_handler: int = dpg.generate_uuid()
                with dpg.item_handler_registry(tag=item_handler):
                    dpg.add_item_visible_handler(
                        callback=lambda s, a, u: visibility_handler(u),
                        user_data=tab,
                    )
                dpg.bind_item_handler_registry(tab.visibility_item, item_handler)

    def resize(self, width: int, height: int):
        assert type(width) is int and width > 0, width
        assert type(height) is int and height > 0, height
        self.data_sets_tab.resize(width, height)
        self.kramers_kronig_tab.resize(width, height)
        self.drt_tab.resize(width, height)
        self.fitting_tab.resize(width, height)
        self.simulation_tab.resize(width, height)
        self.plotting_tab.resize(width, height)

    def select_next_tab(self):
        current_tab: int = dpg.get_value(self.tab_bar)
        tabs: List[int] = dpg.get_item_children(self.tab_bar, slot=1)
        while tabs:
            tab: int = tabs.pop(0)
            if tab == current_tab:
                break
        if not tabs:
            tabs = dpg.get_item_children(self.tab_bar, slot=1)
        tab = tabs[0]
        dpg.set_value(self.tab_bar, tab)

    def select_previous_tab(self):
        current_tab: int = dpg.get_value(self.tab_bar)
        tabs: List[int] = dpg.get_item_children(self.tab_bar, slot=1)
        while tabs:
            tab: int = tabs.pop()
            if tab == current_tab:
                break
        if not tabs:
            tabs = dpg.get_item_children(self.tab_bar, slot=1)
        tab = tabs[-1]
        dpg.set_value(self.tab_bar, tab)

    def get_active_context(self) -> Context:
        return self.context_lookup[dpg.get_value(self.tab_bar)]

    def get_active_data_set(
        self, context: Optional[Context] = None
    ) -> Optional[DataSet]:
        assert type(context) is Context or context is None, context
        tag: Optional[int] = None
        if context is not None:
            tag = {
                Context.DATA_SETS_TAB: self.data_sets_tab.delete_button,
                Context.KRAMERS_KRONIG_TAB: self.kramers_kronig_tab.perform_test_button,
                Context.DRT_TAB: self.drt_tab.perform_drt_button,
                Context.FITTING_TAB: self.fitting_tab.perform_fit_button,
                Context.SIMULATION_TAB: self.simulation_tab.perform_sim_button,
            }.get(context)
        else:
            tag = {
                self.data_sets_tab.tab: self.data_sets_tab.delete_button,
                self.kramers_kronig_tab.tab: self.kramers_kronig_tab.perform_test_button,
                self.drt_tab.tab: self.drt_tab.perform_drt_button,
                self.fitting_tab.tab: self.fitting_tab.perform_fit_button,
                self.simulation_tab.tab: self.simulation_tab.perform_sim_button,
            }.get(dpg.get_value(self.tab_bar))
        if tag is None:
            return None
        return dpg.get_item_user_data(tag)

    def get_active_test(self) -> Optional[TestResult]:
        return dpg.get_item_user_data(self.kramers_kronig_tab.delete_button).get("test")

    def get_active_drt(self) -> Optional[DRTResult]:
        return dpg.get_item_user_data(self.drt_tab.delete_button).get("drt")

    def get_active_fit(self) -> Optional[FitResult]:
        return dpg.get_item_user_data(self.fitting_tab.delete_button).get("fit")

    def get_active_simulation(self) -> Optional[SimulationResult]:
        return dpg.get_item_user_data(self.simulation_tab.delete_button)

    def get_active_plot(self) -> Optional[PlotSettings]:
        return self.plotting_tab.get_active_plot()

    def select_overview_tab(self):
        dpg.set_value(self.tab_bar, self.overview_tab.tab)

    def select_data_sets_tab(self):
        dpg.set_value(self.tab_bar, self.data_sets_tab.tab)

    def select_kramers_kronig_tab(self):
        dpg.set_value(self.tab_bar, self.kramers_kronig_tab.tab)

    def select_drt_tab(self):
        dpg.set_value(self.tab_bar, self.drt_tab.tab)

    def select_fitting_tab(self):
        dpg.set_value(self.tab_bar, self.fitting_tab.tab)

    def select_simulation_tab(self):
        dpg.set_value(self.tab_bar, self.simulation_tab.tab)

    def select_plotting_tab(self):
        dpg.set_value(self.tab_bar, self.plotting_tab.tab)

    def set_label(self, label: str):
        assert type(label) is str and label != "", label
        dpg.set_item_label(self.tab, label)
        self.overview_tab.set_label(label)

    def get_notes(self) -> str:
        return self.overview_tab.get_notes()

    def set_notes(self, notes: str):
        assert type(notes) is str, notes
        self.overview_tab.set_notes(notes)

    def set_dirty(self, state: bool):
        dpg.bind_item_theme(self.tab, themes.tab.dirty if state else themes.tab.clean)

    def populate_data_sets(self, project: Project):
        assert type(project) is Project, project
        data_sets: List[DataSet] = project.get_data_sets()
        lookup: Dict[str, DataSet] = {_.get_label(): _ for _ in data_sets}
        labels: List[str] = list(lookup.keys())
        self.data_sets_tab.populate_data_sets(labels, lookup)
        self.kramers_kronig_tab.populate_data_sets(labels, lookup)
        self.drt_tab.populate_data_sets(labels, lookup)
        self.fitting_tab.populate_data_sets(labels, lookup)
        self.simulation_tab.populate_data_sets(labels, lookup)

    def populate_tests(self, project: Project, data: Optional[DataSet]):
        assert type(project) is Project, project
        assert type(data) is DataSet or data is None, data
        self.kramers_kronig_tab.populate_tests(
            {_.get_label(): _ for _ in project.get_tests(data)}
            if data is not None
            else {},
            data,
        )

    def populate_drts(self, project: Project, data: Optional[DataSet]):
        assert type(project) is Project, project
        assert type(data) is DataSet or data is None, data
        self.drt_tab.populate_drts(
            {_.get_label(): _ for _ in project.get_drts(data)}
            if data is not None
            else {},
            data,
        )

    def populate_fits(self, project: Project, data: Optional[DataSet]):
        assert type(project) is Project, project
        assert type(data) is DataSet or data is None, data
        self.fitting_tab.populate_fits(
            {_.get_label(): _ for _ in project.get_fits(data)}
            if data is not None
            else {},
            data,
        )

    def populate_simulations(self, project: Project):
        assert type(project) is Project, project
        self.simulation_tab.populate_simulations(
            {_.get_label(): _ for _ in project.get_simulations()}
        )

    def populate_plots(self, project: Project):
        assert type(project) is Project, project
        self.plotting_tab.populate_plots(
            {_.get_label(): _ for _ in project.get_plots()}
        )

    def select_data_set(self, data: Optional[DataSet]):
        assert type(data) is DataSet or data is None, data
        self.data_sets_tab.select_data_set(data)
        self.kramers_kronig_tab.select_test_result(None, data)
        self.drt_tab.select_drt_result(None, data)
        self.fitting_tab.select_fit_result(None, data)

    def get_next_data_set(self, context: Context) -> Optional[DataSet]:
        if context == Context.DATA_SETS_TAB:
            return self.data_sets_tab.get_next_data_set()
        elif context == Context.KRAMERS_KRONIG_TAB:
            return self.kramers_kronig_tab.get_next_data_set()
        elif context == Context.DRT_TAB:
            return self.drt_tab.get_next_data_set()
        elif context == Context.FITTING_TAB:
            return self.fitting_tab.get_next_data_set()
        return None

    def get_previous_data_set(self, context: Context) -> Optional[DataSet]:
        if context == Context.DATA_SETS_TAB:
            return self.data_sets_tab.get_previous_data_set()
        elif context == Context.KRAMERS_KRONIG_TAB:
            return self.kramers_kronig_tab.get_previous_data_set()
        elif context == Context.DRT_TAB:
            return self.drt_tab.get_previous_data_set()
        elif context == Context.FITTING_TAB:
            return self.fitting_tab.get_previous_data_set()
        return None

    def get_next_simulation_data_set(self) -> Optional[DataSet]:
        return self.simulation_tab.get_next_data_set()

    def get_previous_simulation_data_set(self) -> Optional[DataSet]:
        return self.simulation_tab.get_previous_data_set()

    def get_next_test_result(self) -> Optional[TestResult]:
        return self.kramers_kronig_tab.get_next_result()

    def get_previous_test_result(self) -> Optional[TestResult]:
        return self.kramers_kronig_tab.get_previous_result()

    def get_next_drt_result(self) -> Optional[DRTResult]:
        return self.drt_tab.get_next_result()

    def get_previous_drt_result(self) -> Optional[DRTResult]:
        return self.drt_tab.get_previous_result()

    def get_next_fit_result(self) -> Optional[FitResult]:
        return self.fitting_tab.get_next_result()

    def get_previous_fit_result(self) -> Optional[FitResult]:
        return self.fitting_tab.get_previous_result()

    def get_next_simulation_result(self) -> Optional[SimulationResult]:
        return self.simulation_tab.get_next_result()

    def get_previous_simulation_result(self) -> Optional[SimulationResult]:
        return self.simulation_tab.get_previous_result()

    def get_next_plot(self) -> Optional[PlotSettings]:
        return self.plotting_tab.get_next_plot()

    def get_previous_plot(self) -> Optional[PlotSettings]:
        return self.plotting_tab.get_previous_plot()

    def get_next_plot_type(self) -> Optional[PlotType]:
        return self.plotting_tab.get_next_plot_type()

    def get_previous_plot_type(self) -> Optional[PlotType]:
        return self.plotting_tab.get_previous_plot_type()

    def select_test_result(self, test: TestResult, data: DataSet):
        assert type(test) is TestResult, test
        assert type(data) is DataSet, data
        self.kramers_kronig_tab.select_test_result(test, data)

    def select_drt_result(self, drt: DRTResult, data: DataSet):
        assert type(drt) is DRTResult, drt
        assert type(data) is DataSet, data
        self.drt_tab.select_drt_result(drt, data)

    def select_fit_result(self, fit: FitResult, data: DataSet):
        assert type(fit) is FitResult, fit
        assert type(data) is DataSet, data
        self.fitting_tab.select_fit_result(fit, data)

    def select_simulation_result(
        self, simulation: Optional[SimulationResult], data: Optional[DataSet]
    ):
        assert type(simulation) is SimulationResult or simulation is None, simulation
        assert type(data) is DataSet or data is None, data
        self.simulation_tab.select_simulation_result(simulation, data)

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
        self.plotting_tab.select_plot(
            settings,
            data_sets,
            tests,
            drts,
            fits,
            simulations,
            adjust_limits,
            plot_only,
        )

    def select_plot_type(self, plot_type: PlotType):
        assert type(plot_type) is PlotType, plot_type
        self.plotting_tab.select_plot_type(plot_type)

    def set_series_label(self, uuid: str, label: Optional[str]):
        assert type(uuid) is str, uuid
        assert type(label) is str or label is None, label
        self.plotting_tab.set_series_label(uuid, label)

    def get_test_settings(self) -> TestSettings:
        return self.kramers_kronig_tab.get_settings()

    def set_test_settings(self, settings: TestSettings):
        assert type(settings) is TestSettings, settings
        self.kramers_kronig_tab.set_settings(settings)

    def get_fit_settings(self) -> FitSettings:
        return self.fitting_tab.get_settings()

    def set_fit_settings(self, settings: FitSettings):
        assert type(settings) is FitSettings, settings
        self.fitting_tab.set_settings(settings)

    def get_drt_settings(self) -> DRTSettings:
        return self.drt_tab.get_settings()

    def set_drt_settings(self, settings: DRTSettings):
        assert type(settings) is DRTSettings, settings
        self.drt_tab.set_settings(settings)

    def get_simulation_settings(self) -> SimulationSettings:
        return self.simulation_tab.get_settings()

    def set_simulation_settings(self, settings: SimulationSettings):
        assert type(settings) is SimulationSettings, settings
        self.simulation_tab.set_settings(settings)

    def show_enlarged_nyquist(self):
        {
            self.data_sets_tab.tab: self.data_sets_tab.show_enlarged_nyquist,
            self.kramers_kronig_tab.tab: self.kramers_kronig_tab.show_enlarged_nyquist,
            self.fitting_tab.tab: self.fitting_tab.show_enlarged_nyquist,
            self.simulation_tab.tab: self.simulation_tab.show_enlarged_nyquist,
        }.get(dpg.get_value(self.tab_bar))()

    def show_enlarged_bode(self):
        {
            self.data_sets_tab.tab: self.data_sets_tab.show_enlarged_bode,
            self.kramers_kronig_tab.tab: self.kramers_kronig_tab.show_enlarged_bode,
            self.fitting_tab.tab: self.fitting_tab.show_enlarged_bode,
            self.simulation_tab.tab: self.simulation_tab.show_enlarged_bode,
        }.get(dpg.get_value(self.tab_bar))()

    def show_enlarged_residuals(self):
        {
            self.kramers_kronig_tab.tab: self.kramers_kronig_tab.show_enlarged_residuals,
            self.drt_tab.tab: self.drt_tab.show_enlarged_residuals,
            self.fitting_tab.tab: self.fitting_tab.show_enlarged_residuals,
        }.get(dpg.get_value(self.tab_bar))()

    def show_enlarged_drt(self):
        {
            self.drt_tab.tab: self.drt_tab.show_enlarged_drt,
        }.get(dpg.get_value(self.tab_bar))()

    def show_enlarged_impedance(self):
        {
            self.drt_tab.tab: self.drt_tab.show_enlarged_impedance,
        }.get(dpg.get_value(self.tab_bar))()

    def update_plots(
        self,
        settings: PlotSettings,
        data_sets: List[DataSet],
        tests: Dict[str, List[TestResult]],
        drts: Dict[str, List[DRTResult]],
        fits: Dict[str, List[FitResult]],
        simulations: List[SimulationResult],
    ):
        assert type(settings) is PlotSettings, settings
        assert type(data_sets) is list, data_sets
        assert type(tests) is dict, tests
        assert type(drts) is dict, drts
        assert type(fits) is dict, fits
        assert type(simulations) is list, simulations
        self.plotting_tab.plot_series(
            data_sets,
            tests,
            drts,
            fits,
            simulations,
            settings,
            adjust_limits=False,
        )

    def get_drt_plot(self, context: Context) -> Optional[Plot]:
        if context == Context.DRT_TAB:
            return self.drt_tab.drt_plot
        return None

    def get_impedance_plot(self, context: Context) -> Optional[Plot]:
        if context == Context.DRT_TAB:
            return self.drt_tab.impedance_plot
        return None

    def get_nyquist_plot(self, context: Context) -> Optional[Plot]:
        if context == Context.KRAMERS_KRONIG_TAB:
            return self.kramers_kronig_tab.nyquist_plot
        elif context == Context.FITTING_TAB:
            return self.fitting_tab.nyquist_plot
        elif context == Context.SIMULATION_TAB:
            return self.simulation_tab.nyquist_plot
        return None

    def get_bode_plot(self, context: Context) -> Optional[Plot]:
        if context == Context.KRAMERS_KRONIG_TAB:
            return self.kramers_kronig_tab.bode_plot_horizontal
        elif context == Context.FITTING_TAB:
            return self.fitting_tab.bode_plot_horizontal
        elif context == Context.SIMULATION_TAB:
            return self.simulation_tab.bode_plot_horizontal
        return None

    def get_residuals_plot(self, context: Context) -> Optional[Plot]:
        if context == Context.KRAMERS_KRONIG_TAB:
            return self.kramers_kronig_tab.residuals_plot
        elif context == Context.DRT_TAB:
            return self.drt_tab.residuals_plot
        elif context == Context.FITTING_TAB:
            return self.fitting_tab.residuals_plot
        return None

    def get_active_output(self, context: Context) -> Optional[FitSimOutput]:
        if context == Context.FITTING_TAB:
            return self.fitting_tab.get_active_output()
        elif context == Context.SIMULATION_TAB:
            return self.simulation_tab.get_active_output()
        return None

    def get_filtered_plot_series(
        self,
    ) -> Tuple[
        List[DataSet],
        List[TestResult],
        List[DRTResult],
        List[FitResult],
        List[SimulationResult],
    ]:
        string: str = self.plotting_tab.get_filter_string()
        return (
            self.plotting_tab.possible_data_sets.filter(string, False),
            self.plotting_tab.possible_tests.filter(string, False),
            self.plotting_tab.possible_drts.filter(string, False),
            self.plotting_tab.possible_fits.filter(string, False),
            self.plotting_tab.possible_simulations.filter(string, False),
        )

    def has_active_input(self, context: Optional[Context] = None) -> bool:
        assert type(context) is Context or context is None, context
        if context is None:
            context = self.get_active_context()
        if context == Context.OVERVIEW_TAB:
            return self.overview_tab.has_active_input()
        elif context == Context.DATA_SETS_TAB:
            return self.data_sets_tab.has_active_input()
        elif context == Context.KRAMERS_KRONIG_TAB:
            return self.kramers_kronig_tab.has_active_input()
        elif context == Context.DRT_TAB:
            return self.drt_tab.has_active_input()
        elif context == Context.FITTING_TAB:
            return self.fitting_tab.has_active_input()
        elif context == Context.SIMULATION_TAB:
            return self.simulation_tab.has_active_input()
        elif context == Context.PLOTTING_TAB:
            return self.plotting_tab.has_active_input()
        return False
