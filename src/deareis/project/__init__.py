# Copyright 2022 DearEIS developers
# DearEIS is licensed under the GPLv3 or later (https://www.gnu.org/licenses/gpl-3.0.html).
# The licenses of DearEIS' dependencies and/or sources of portions of code are included in
# the LICENSES folder.

from os import getcwd, rename, remove
from os.path import basename, dirname, exists, isdir, splitext
from pathlib import Path
from multiprocessing import cpu_count, Process, Queue
from queue import Empty
from uuid import uuid4
from time import time
from traceback import format_exc
from json import dumps as dump_json, loads as load_json
from typing import (
    Any,
    Callable,
    Dict,
    IO,
    List,
    Optional,
    Set,
    Tuple,
    Union,
)
from deareis.plot import ResidualsPlot, Plot
from pandas import DataFrame
from numpy import array, ndarray, pad
from sympy import Expr, latex, simplify
from collections import OrderedDict
import dearpygui.dearpygui as dpg
from pyimpspec import (
    Circuit,
    string_to_circuit,
    DataSet,
    FittingError,
    FittingResult,
    KramersKronigResult,
    ParsingError,
)
from pyimpspec.data.formats import UnsupportedFileFormat
import pyimpspec
from deareis.config import CONFIG
from deareis.file_dialog import file_dialog
from deareis.project.average_data import AverageData
from deareis.project.copy_mask import CopyMask
from deareis.project.circuit_editor import CircuitEditor
from deareis.project.datasets import DataSetsTab
from deareis.project.exploratory_results import ExploratoryResults
from deareis.project.fitting import (
    FittingTab,
    Output,
)
from deareis.project.kramers_kronig import KramersKronigTab
from deareis.project.overview import OverviewTab
from deareis.project.plotting import PlottingTab
from deareis.project.simulation import SimulationTab
from deareis.project.subtract_impedance import SubtractImpedance
from deareis.project.toggle_points import TogglePoints
from deareis.utility import (
    attach_tooltip,
    get_item_pos,
    is_alt_down,
    is_control_down,
    is_shift_down,
    window_pos_dims,
)
import deareis.themes as themes
from deareis.data.kramers_kronig import (
    Method,
    Mode,
    Test,
    TestResult,
    TestSettings,
    label_to_test,
    label_to_mode,
    method_to_label,
    method_to_value,
    mode_to_label,
    test_to_label,
    test_to_value,
)
from deareis.data.fitting import (
    FitResult,
    FitSettings,
    Weight,
    value_to_method,
    value_to_weight,
    weight_to_label,
    weight_to_value,
)
from deareis.data.simulation import (
    SimulationResult,
    SimulationSettings,
)
from deareis.data.plotting import PlotSettings, PlotType, label_to_plot_type
from deareis.data.project import _parse_old_state, VERSION
import deareis.keyboard_shortcuts as keyboard_shortcuts


def serialize_state(project: "Project", to_disk: bool = False) -> str:
    assert type(to_disk) is bool
    data: Optional[DataSet] = project.datasets_tab.get_dataset()
    test: Optional[TestResult] = project.kramers_kronig_tab.get_result()
    fit: Optional[FitResult] = project.fitting_tab.get_result()
    simulation: Optional[SimulationResult] = project.simulation_tab.get_result()
    simulation_data: Optional[DataSet] = project.simulation_tab.get_dataset()
    plot: Optional[PlotSettings] = project.plotting_tab.get_plot()
    state: dict = {
        "uuid": project.uuid,
        "datasets": list(map(lambda _: _.to_dict(), project.datasets)),
        "tests": {
            k: list(map(lambda _: _.to_dict(), v)) for k, v in project.tests.items()
        },
        "latest_fit_circuit": (
            project.latest_fit_circuit.to_string(12)
            if project.latest_fit_circuit is not None
            else None
        ),
        "fits": {
            k: list(map(lambda _: _.to_dict(), v)) for k, v in project.fits.items()
        },
        "latest_simulation_circuit": (
            project.latest_simulation_circuit.to_string(12)
            if project.latest_simulation_circuit is not None
            else None
        ),
        "simulations": list(map(lambda _: _.to_dict(), project.simulations)),
        "plots": list(map(lambda _: _.to_dict(), project.plots)),
        "label": project.label,
        "notes": project.overview_tab.get_notes(),
        # Extra stuff
        "active_data_uuid": data.uuid if data is not None else "",
        "active_test_uuid": test.uuid if test is not None else "",
        "active_fit_uuid": fit.uuid if fit is not None else "",
        "active_simulation_uuid": simulation.uuid if simulation is not None else "",
        "active_simulation_data_uuid": (
            simulation_data.uuid if simulation_data is not None else ""
        ),
        "active_plot_uuid": plot.uuid if plot is not None else "",
    }
    if to_disk:
        plot_dict: dict
        for plot_dict in state["plots"]:
            for uuid in plot_dict["themes"]:
                plot_dict["themes"][uuid] = -1
        state["version"] = VERSION
        return dump_json(state, sort_keys=True, indent=2)
    state["overview_tab"] = project.overview_tab.to_dict()
    state["datasets_tab"] = project.datasets_tab.to_dict()
    state["kramers_kronig_tab"] = project.kramers_kronig_tab.to_dict()
    state["fitting_tab"] = project.fitting_tab.to_dict()
    state["simulation_tab"] = project.simulation_tab.to_dict()
    return dump_json(state, sort_keys=True, indent=2)


def find_object_by_uuid(values: Any, uuid: str) -> Optional[Any]:
    assert type(uuid) is str, uuid
    for value in values:
        if value.uuid == uuid:
            return value
    return None


def restore_state(json: str, project: "Project", is_dirty: bool = False):
    assert type(json) is str
    state: dict = load_json(json)
    from_disk: bool = False
    if "version" in state:
        from_disk = True
        # This state was serialized in a previous session, possibly in an old format.
        assert type(state["version"]) is int
        if state["version"] != VERSION:
            state = _parse_old_state(state)
        else:
            del state["version"]
    # Restore the state of the Project instance
    project.uuid = state["uuid"]
    project.datasets = list(map(DataSet.from_dict, state["datasets"]))
    project.tests = {
        k: list(map(TestResult.from_dict, v)) for k, v in state["tests"].items()
    }
    if not from_disk:
        project.latest_fit_circuit = (
            string_to_circuit(state["latest_fit_circuit"])
            if state["latest_fit_circuit"] is not None
            else None
        )
    project.fits = {
        k: list(map(FitResult.from_dict, v)) for k, v in state["fits"].items()
    }
    if not from_disk:
        project.latest_simulation_circuit = (
            string_to_circuit(state["latest_simulation_circuit"])
            if state["latest_simulation_circuit"] is not None
            else None
        )
    project.simulations = list(map(SimulationResult.from_dict, state["simulations"]))
    project.plots = list(map(PlotSettings.from_dict, state["plots"]))
    if from_disk:
        list(map(lambda _: _.recreate_themes(), project.plots))
    project.set_label(state["label"])
    project.set_notes(state["notes"])
    # Use the restored Project state to restore the GUI
    data: Optional[DataSet] = find_object_by_uuid(
        project.datasets, state["active_data_uuid"]
    )
    project.update_dataset_combos(data, True)
    if data is not None:
        project.select_test_result(
            result=find_object_by_uuid(
                project.tests[data.uuid],
                state["active_test_uuid"],
            ),
            data=data,
        )
        project.select_fit_result(
            result=find_object_by_uuid(
                project.fits[data.uuid],
                state["active_fit_uuid"],
            ),
            data=data,
        )
    simulation: Optional[SimulationResult] = find_object_by_uuid(
        project.simulations,
        state["active_simulation_uuid"],
    )
    project.simulation_tab.populate_result_combo(
        list(map(lambda _: _.get_label(), project.simulations)),
        simulation.get_label() if simulation is not None else "",
    )
    project.select_simulation_dataset(
        data=find_object_by_uuid(
            project.datasets,
            state["active_simulation_data_uuid"],
        ),
    )
    project.select_simulation_result(result=simulation)
    plot: Optional[PlotSettings] = find_object_by_uuid(
        project.plots,
        state["active_plot_uuid"],
    )
    project.update_possible_plot_series()
    if plot is None:
        project.create_plot()
    else:
        project.plotting_tab.populate_plot_combo(project.plots)
        project.select_plot(plot.get_label(), fit_to_data=from_disk)
    if from_disk:
        # The initial state should not be an empty project when loaded from disk
        project.state_history_index = -1
        project.update_state_history()
        # This condition is here to prevent the restored state from being flagged as not dirty.
        # This is relevant for dirty projects that were not saved before the program was abruptly
        # terminated by the user without the chance to save those projects.
        if not is_dirty:
            project.set_dirty(False)
    else:
        # Restore the GUI state as well when not loading from disk.
        try:
            project.overview_tab.restore_state(state["overview_tab"])
            project.datasets_tab.restore_state(state["datasets_tab"])
            project.kramers_kronig_tab.restore_state(state["kramers_kronig_tab"])
            project.fitting_tab.restore_state(state["fitting_tab"])
            project.simulation_tab.restore_state(state["simulation_tab"])
        except KeyError:
            pass


def sympy_wrapper(expr: Expr, queue: Queue):
    queue.put(simplify(expr))


def get_sympy_expr(circuit: Circuit) -> Expr:
    assert type(circuit) is Circuit
    expr: Expr = circuit.to_sympy()
    # Try to simplify the expression, but don't wait for an indefinite period of time
    queue: Queue = Queue()
    proc: Process = Process(
        target=sympy_wrapper,
        args=(
            expr,
            queue,
        ),
    )
    proc.start()
    try:
        expr = queue.get(True, 2)
    except Empty:
        pass
    if proc.is_alive:
        proc.kill()
    return expr


class Project:
    def __init__(self, parent: int = -1):
        assert type(parent) is int
        self.uuid: str = uuid4().hex
        self.tab: int = dpg.generate_uuid()
        self.key_handler: int = dpg.generate_uuid()
        self.is_initialized: bool = False
        # Project-level tabs
        self.tab_bar: int = dpg.generate_uuid()
        self.overview_tab: OverviewTab = None  # type: ignore
        self.datasets_tab: DataSetsTab = None  # type: ignore
        self.kramers_kronig_tab: KramersKronigTab = None  # type: ignore
        self.fitting_tab: FittingTab = None  # type: ignore
        self.simulation_tab: SimulationTab = None  # type: ignore
        self.plotting_tab: PlottingTab = None  # type: ignore
        # State
        self.error_message: Optional["ErrorMessage"] = None
        self.working_indicator: Optional["WorkingIndicator"] = None
        self.close_callback: Optional[Callable] = None
        self.save_callback: Optional[Callable] = None
        self.is_dirty: bool = True
        self.label: str = "Project"
        self.notes: str = ""
        self.recent_directory: str = getcwd()
        self.path: str = ""
        self.modal_window: int = -1
        # - undo-redo
        self.state_history: List[str] = []
        self.state_history_index: int = 0
        self.state_saved_index: int = -1
        # - Data sets
        self.datasets: List[DataSet] = []
        # - Kramers-Kronig results
        self.tests: Dict[str, List[TestResult]] = {}
        # - Fitting
        self.latest_fit_circuit: Optional[Circuit] = None
        self.fits: Dict[str, List[FitResult]] = {}
        # - Simulation
        self.latest_simulation_circuit: Optional[Circuit] = None
        self.simulations: List[SimulationResult] = []
        # - Plotting
        self.plots: List[PlotSettings] = []
        #
        self._assemble(parent if parent >= 0 else dpg.last_item())
        self._assign_handlers()
        self.set_dirty(True)
        self.is_initialized = True
        self.update_state_history()

    def _assemble(self, parent: int):
        assert type(parent) is int
        with dpg.tab(label=self.label, tag=self.tab, parent=parent):
            with dpg.tab_bar(tag=self.tab_bar):
                self._attach_overview()
                self._attach_datasets()
                self._attach_kramers_kronig()
                self._attach_fitting()
                self._attach_simulation()
                self._attach_plotting()

    def _attach_overview(self):
        tab: OverviewTab = OverviewTab()
        self.overview_tab = tab
        dpg.set_item_callback(tab.label_input, lambda s, a, u: self.rename_project(a))
        dpg.set_item_callback(tab.notes_input, lambda s, a, u: self.notes_modified(a))
        dpg.set_value(tab.label_input, self.label)

    def _attach_datasets(self):
        tab: DataSetsTab = DataSetsTab()
        self.datasets_tab = tab
        tab.dataset_mask_modified_callback = self.dataset_mask_modified
        dpg.set_item_callback(tab.dataset_combo, lambda s, a, u: self.select_dataset(a))
        dpg.set_item_callback(tab.label_input, lambda s, a, u: self.rename_dataset(a))
        dpg.set_item_callback(
            tab.path_input, lambda s, a, u: self.modify_dataset_path(a)
        )
        dpg.set_item_callback(tab.load_button, self.select_dataset_files)
        dpg.set_item_callback(tab.remove_button, lambda s, a, u: self.remove_dataset())
        dpg.set_item_callback(tab.subtract_impedance_button, self.subtract_impedance)
        dpg.set_item_callback(tab.toggle_points_button, self.toggle_points)
        dpg.set_item_callback(tab.copy_mask_button, self.copy_mask)
        dpg.set_item_callback(tab.average_button, self.average_datasets)
        dpg.set_item_callback(tab.enlarge_nyquist_button, self.show_plot_modal_window)
        dpg.set_item_callback(tab.enlarge_bode_button, self.show_plot_modal_window)

    def _attach_kramers_kronig(self):
        tab: KramersKronigTab = KramersKronigTab()
        self.kramers_kronig_tab = tab
        dpg.set_item_callback(tab.test_combo, self.test_setting_modified)
        dpg.set_item_callback(tab.mode_combo, self.test_setting_modified)
        dpg.set_item_callback(tab.dataset_combo, lambda s, a, u: self.select_dataset(a))
        dpg.set_item_callback(
            tab.result_combo, lambda s, a, u: self.select_test_result(a)
        )
        dpg.set_item_callback(tab.perform_test_button, self.perform_test)
        dpg.set_item_callback(
            tab.delete_result_button, lambda s, a, u: self.remove_test(u)
        )
        dpg.set_item_callback(
            tab.apply_settings_button,
            lambda s, a, u: self.apply_test_settings(u),
        )
        dpg.set_item_callback(tab.enlarge_residuals_button, self.show_plot_modal_window)
        dpg.set_item_callback(tab.enlarge_nyquist_button, self.show_plot_modal_window)
        dpg.set_item_callback(
            tab.enlarge_bode_horizontal_button, self.show_plot_modal_window
        )
        dpg.set_item_callback(
            tab.enlarge_bode_vertical_button, self.show_plot_modal_window
        )
        self.apply_test_settings(settings=CONFIG.default_test_settings)

    def _attach_fitting(self):
        tab: FittingTab = FittingTab()
        self.fitting_tab = tab
        dpg.set_item_callback(tab.dataset_combo, lambda s, a, u: self.select_dataset(a))
        dpg.set_item_callback(
            tab.result_combo, lambda s, a, u: self.select_fit_result(a)
        )
        dpg.set_item_callback(tab.perform_fit_button, self.perform_fit)
        dpg.set_item_callback(
            tab.delete_result_button, lambda s, a, u: self.remove_fit(u)
        )
        dpg.set_item_callback(
            tab.apply_settings_button,
            lambda s, a, u: self.apply_fit_settings(u),
        )
        dpg.set_item_callback(tab.cdc_input, self.validate_fit_circuit)
        dpg.set_item_callback(tab.editor_button, self.show_fit_circuit_editor)
        dpg.set_item_callback(
            tab.copy_output_button, lambda s, a, u: self.copy_fit_output(u)
        )
        dpg.set_item_callback(tab.enlarge_residuals_button, self.show_plot_modal_window)
        dpg.set_item_callback(tab.enlarge_nyquist_button, self.show_plot_modal_window)
        dpg.set_item_callback(
            tab.enlarge_bode_horizontal_button, self.show_plot_modal_window
        )
        dpg.set_item_callback(
            tab.enlarge_bode_vertical_button, self.show_plot_modal_window
        )
        tab.select_dataset(None, [], True)
        tab.select_result(None, None)
        self.apply_fit_settings(settings=CONFIG.default_fit_settings)

    def _attach_simulation(self):
        tab: SimulationTab = SimulationTab()
        self.simulation_tab = tab
        dpg.set_item_callback(
            tab.result_combo, lambda s, a, u: self.select_simulation_result(a)
        )
        dpg.set_item_callback(
            tab.dataset_combo, lambda s, a, u: self.select_simulation_dataset(a)
        )
        dpg.set_item_callback(tab.perform_sim_button, self.perform_simulation)
        dpg.set_item_callback(
            tab.delete_result_button, lambda s, a, u: self.remove_simulation(u)
        )
        dpg.set_item_callback(
            tab.apply_settings_button,
            lambda s, a, u: self.apply_simulation_settings(u),
        )
        dpg.set_item_callback(tab.cdc_input, self.validate_simulation_circuit)
        dpg.set_item_callback(tab.editor_button, self.show_simulation_circuit_editor)
        dpg.set_item_callback(
            tab.copy_output_button, lambda s, a, u: self.copy_simulation_output(u)
        )
        dpg.set_item_callback(tab.enlarge_nyquist_button, self.show_plot_modal_window)
        dpg.set_item_callback(
            tab.enlarge_bode_horizontal_button, self.show_plot_modal_window
        )
        dpg.set_item_callback(
            tab.enlarge_bode_vertical_button, self.show_plot_modal_window
        )
        self.select_simulation_result("")
        self.apply_simulation_settings(settings=CONFIG.default_simulation_settings)

    def _attach_plotting(self):
        tab: PlottingTab = PlottingTab()
        self.plotting_tab = tab
        dpg.set_item_callback(tab.plot_combo, lambda s, a, u: self.select_plot(a))
        dpg.set_item_callback(
            tab.label_input, lambda s, a, u: self.update_plot_label(a)
        )
        dpg.set_item_callback(tab.type_combo, lambda s, a, u: self.select_plot_type(a))
        dpg.set_item_callback(tab.new_button, self.create_plot)
        dpg.set_item_callback(tab.remove_button, self.remove_plot)
        dpg.set_item_callback(
            tab.select_all_button, lambda s, a, u: self.select_all_plot_series(u)
        )
        dpg.set_item_callback(
            tab.unselect_all_button, lambda s, a, u: self.select_all_plot_series(u)
        )
        dpg.set_item_callback(
            tab.copy_appearances_button, self.copy_plot_appearance_settings
        )
        dpg.set_item_callback(tab.copy_csv_button, self.copy_plot_csv)
        self.create_plot()

    def _assign_handlers(self):
        keys: List[int] = [
            dpg.mvKey_0,
            dpg.mvKey_1,
            dpg.mvKey_2,
            dpg.mvKey_3,
            dpg.mvKey_4,
            dpg.mvKey_5,
            dpg.mvKey_6,
            dpg.mvKey_7,
            dpg.mvKey_8,
            dpg.mvKey_9,
            dpg.mvKey_A,
            dpg.mvKey_B,
            dpg.mvKey_C,
            dpg.mvKey_D,
            dpg.mvKey_Delete,
            dpg.mvKey_Down,
            dpg.mvKey_E,
            dpg.mvKey_F,
            dpg.mvKey_K,
            dpg.mvKey_L,
            dpg.mvKey_Left,
            dpg.mvKey_N,
            dpg.mvKey_Next,
            dpg.mvKey_O,
            dpg.mvKey_Prior,
            dpg.mvKey_R,
            dpg.mvKey_Return,
            dpg.mvKey_Right,
            dpg.mvKey_S,
            dpg.mvKey_Spacebar,
            dpg.mvKey_T,
            dpg.mvKey_W,
            dpg.mvKey_Up,
            dpg.mvKey_Y,
            dpg.mvKey_Z,
        ]
        with dpg.handler_registry(tag=self.key_handler):
            key: int
            for key in keys:
                dpg.add_key_release_handler(
                    key=key,
                    callback=self.keybinding_handler,
                )

    def keybinding_handler(self, sender: int, key: int):
        assert type(sender) is int
        assert type(key) is int
        if not self.is_visible():
            return
        elif self.modal_window >= 0:
            modal_window_exists: bool = dpg.does_item_exist(self.modal_window)
            if modal_window_exists and dpg.is_item_shown(self.modal_window):
                return
            elif (
                modal_window_exists
                and self.modal_window != self.error_message.window  # type: ignore
                and self.modal_window != self.working_indicator.window  # type: ignore
            ):
                dpg.delete_item(self.modal_window)
            self.modal_window = -1
        if is_control_down() and is_shift_down():
            if key == dpg.mvKey_S:  # Save project as
                keyboard_shortcuts.save(self, True)
            elif key == dpg.mvKey_Z:  # Redo (Unix-style)
                keyboard_shortcuts.redo(self)
        elif is_control_down() and is_alt_down():
            pass
        elif is_alt_down() and is_shift_down():
            if key == dpg.mvKey_B:
                if self.datasets_tab.is_visible():
                    keyboard_shortcuts.copy_plot_data(self.datasets_tab.bode_plot)
                elif self.kramers_kronig_tab.is_visible():
                    keyboard_shortcuts.copy_plot_data(
                        self.kramers_kronig_tab.bode_plot_horizontal
                    )
                elif self.fitting_tab.is_visible():
                    keyboard_shortcuts.copy_plot_data(
                        self.fitting_tab.bode_plot_horizontal
                    )
                elif self.simulation_tab.is_visible():
                    keyboard_shortcuts.copy_plot_data(
                        self.simulation_tab.bode_plot_horizontal
                    )
            elif key == dpg.mvKey_C:
                if self.plotting_tab.is_visible():
                    self.copy_plot_csv()
            elif key == dpg.mvKey_N:
                if self.datasets_tab.is_visible():
                    keyboard_shortcuts.copy_plot_data(self.datasets_tab.nyquist_plot)
                elif self.kramers_kronig_tab.is_visible():
                    keyboard_shortcuts.copy_plot_data(
                        self.kramers_kronig_tab.nyquist_plot
                    )
                elif self.fitting_tab.is_visible():
                    keyboard_shortcuts.copy_plot_data(self.fitting_tab.nyquist_plot)
                elif self.simulation_tab.is_visible():
                    keyboard_shortcuts.copy_plot_data(self.simulation_tab.nyquist_plot)
            elif key == dpg.mvKey_R:
                if self.kramers_kronig_tab.is_visible():
                    keyboard_shortcuts.copy_plot_data(
                        self.kramers_kronig_tab.residuals_plot
                    )
                elif self.fitting_tab.is_visible():
                    keyboard_shortcuts.copy_plot_data(self.fitting_tab.residuals_plot)
            elif key == dpg.mvKey_S:
                if self.plotting_tab.is_visible():
                    self.select_all_plot_series(False)
            elif key == dpg.mvKey_Down:
                keyboard_shortcuts.go_to_project_tab(self, step=1)
            elif key == dpg.mvKey_Up:
                keyboard_shortcuts.go_to_project_tab(self, step=-1)
            elif (
                key == dpg.mvKey_1
                or key == dpg.mvKey_2
                or key == dpg.mvKey_3
                or key == dpg.mvKey_4
                or key == dpg.mvKey_5
                or key == dpg.mvKey_6
                or key == dpg.mvKey_7
                or key == dpg.mvKey_8
            ):
                keyboard_shortcuts.go_to_project_tab(
                    self,
                    index=[
                        dpg.mvKey_1,
                        dpg.mvKey_2,
                        dpg.mvKey_3,
                        dpg.mvKey_4,
                        dpg.mvKey_5,
                        dpg.mvKey_6,
                        dpg.mvKey_7,
                        dpg.mvKey_8,
                    ].index(key),
                )
            elif key == dpg.mvKey_9:
                keyboard_shortcuts.go_to_project_tab(self, index=-1)
            elif key == dpg.mvKey_0:
                keyboard_shortcuts.go_to_project_tab(self, index=0)
        elif is_control_down():
            if key == dpg.mvKey_Return:
                if self.datasets_tab.is_visible():
                    keyboard_shortcuts.perform_action(self.datasets_tab)
                elif self.kramers_kronig_tab.is_visible():
                    keyboard_shortcuts.perform_action(self.kramers_kronig_tab)
                elif self.fitting_tab.is_visible():
                    keyboard_shortcuts.perform_action(self.fitting_tab)
                elif self.simulation_tab.is_visible():
                    keyboard_shortcuts.perform_action(self.simulation_tab)
                elif self.plotting_tab.is_visible():
                    keyboard_shortcuts.perform_action(self.plotting_tab)
            elif key == dpg.mvKey_S:  # Save project
                keyboard_shortcuts.save(self)
            elif key == dpg.mvKey_Spacebar:
                if self.fitting_tab.is_visible():
                    if self.fitting_tab.is_input_active():
                        pos = get_item_pos(
                            self.fitting_tab.cdc_input,
                            relative=self.fitting_tab.resize_group,
                        )
                        pos = (
                            pos[0] - 8,
                            pos[1] + 12,
                        )
                        keyboard_shortcuts.cdc_hints(self.fitting_tab.cdc_input, pos)
                elif self.simulation_tab.is_visible():
                    if self.simulation_tab.is_input_active():
                        pos = get_item_pos(
                            self.simulation_tab.cdc_input,
                            relative=self.simulation_tab.resize_group,
                        )
                        pos = (
                            pos[0] - 8,
                            pos[1] + 12,
                        )
                        keyboard_shortcuts.cdc_hints(self.simulation_tab.cdc_input, pos)
            elif key == dpg.mvKey_W:  # Close project
                keyboard_shortcuts.close(self)
            elif key == dpg.mvKey_Y:  # Redo (Windows-style)
                keyboard_shortcuts.redo(self)
            elif key == dpg.mvKey_Z:  # Undo
                keyboard_shortcuts.undo(self)
        elif is_alt_down():
            if key == dpg.mvKey_A:
                if self.datasets_tab.is_visible():
                    keyboard_shortcuts.average_datasets(self)
                elif self.kramers_kronig_tab.is_visible():
                    keyboard_shortcuts.apply_settings(self, TestSettings)
                elif self.fitting_tab.is_visible():
                    keyboard_shortcuts.apply_settings(self, FitSettings)
                elif self.simulation_tab.is_visible():
                    keyboard_shortcuts.apply_settings(self, SimulationSettings)
            elif key == dpg.mvKey_B:
                if self.datasets_tab.is_visible():
                    keyboard_shortcuts.show_plot(self.datasets_tab.bode_plot, self)
                elif self.kramers_kronig_tab.is_visible():
                    keyboard_shortcuts.show_plot(
                        self.kramers_kronig_tab.bode_plot_horizontal,
                        self,
                    )
                elif self.fitting_tab.is_visible():
                    keyboard_shortcuts.show_plot(
                        self.fitting_tab.bode_plot_horizontal, self
                    )
                elif self.simulation_tab.is_visible():
                    keyboard_shortcuts.show_plot(
                        self.simulation_tab.bode_plot_horizontal,
                        self,
                    )
            elif key == dpg.mvKey_C:
                if self.datasets_tab.is_visible():
                    keyboard_shortcuts.copy_mask(self)
                elif self.fitting_tab.is_visible():
                    keyboard_shortcuts.copy_output(self.fitting_tab)
                elif self.simulation_tab.is_visible():
                    keyboard_shortcuts.copy_output(self.simulation_tab)
                elif self.plotting_tab.is_visible():
                    self.copy_plot_appearance_settings()
            elif key == dpg.mvKey_E:
                if self.fitting_tab.is_visible():
                    keyboard_shortcuts.show_circuit_editor(self.fitting_tab)
                elif self.simulation_tab.is_visible():
                    keyboard_shortcuts.show_circuit_editor(self.simulation_tab)
            elif key == dpg.mvKey_L:
                if self.datasets_tab.is_visible():
                    self.select_dataset_files()
            elif key == dpg.mvKey_N:
                if self.datasets_tab.is_visible():
                    keyboard_shortcuts.show_plot(self.datasets_tab.nyquist_plot, self)
                elif self.kramers_kronig_tab.is_visible():
                    keyboard_shortcuts.show_plot(
                        self.kramers_kronig_tab.nyquist_plot, self
                    )
                elif self.fitting_tab.is_visible():
                    keyboard_shortcuts.show_plot(self.fitting_tab.nyquist_plot, self)
                elif self.simulation_tab.is_visible():
                    keyboard_shortcuts.show_plot(self.simulation_tab.nyquist_plot, self)
            elif key == dpg.mvKey_R:
                if self.kramers_kronig_tab.is_visible():
                    keyboard_shortcuts.show_plot(
                        self.kramers_kronig_tab.residuals_plot, self
                    )
                elif self.fitting_tab.is_visible():
                    keyboard_shortcuts.show_plot(self.fitting_tab.residuals_plot, self)
            elif key == dpg.mvKey_S:
                if self.datasets_tab.is_visible():
                    keyboard_shortcuts.subtract_impedance(self)
                elif self.plotting_tab.is_visible():
                    self.select_all_plot_series(True)
            elif key == dpg.mvKey_T:
                if self.datasets_tab.is_visible():
                    keyboard_shortcuts.toggle_points(self)
            elif key == dpg.mvKey_Delete:
                if self.datasets_tab.is_visible():
                    keyboard_shortcuts.remove(self, DataSet)
                elif self.kramers_kronig_tab.is_visible():
                    keyboard_shortcuts.remove(self, TestResult)
                elif self.fitting_tab.is_visible():
                    keyboard_shortcuts.remove(self, FitResult)
                elif self.simulation_tab.is_visible():
                    keyboard_shortcuts.remove(self, SimulationResult)
                elif self.plotting_tab.is_visible():
                    keyboard_shortcuts.remove(self, PlotSettings)
            elif key == dpg.mvKey_Return:
                if self.datasets_tab.is_visible():
                    keyboard_shortcuts.perform_action(self.datasets_tab)
                elif self.kramers_kronig_tab.is_visible():
                    keyboard_shortcuts.perform_action(self.kramers_kronig_tab)
                elif self.fitting_tab.is_visible():
                    keyboard_shortcuts.perform_action(self.fitting_tab)
                elif self.simulation_tab.is_visible():
                    keyboard_shortcuts.perform_action(self.simulation_tab)
                elif self.plotting_tab.is_visible():
                    keyboard_shortcuts.perform_action(self.plotting_tab)
            elif key == dpg.mvKey_Next:
                if self.overview_tab.is_visible():
                    pass
                elif self.datasets_tab.is_visible():
                    pass
                elif self.plotting_tab.is_visible():
                    keyboard_shortcuts.go_to_plot_type(self, step=1)
                else:
                    keyboard_shortcuts.go_to_result(self, step=1)
            elif key == dpg.mvKey_Prior:
                if self.overview_tab.is_visible():
                    pass
                elif self.datasets_tab.is_visible():
                    pass
                elif self.plotting_tab.is_visible():
                    keyboard_shortcuts.go_to_plot_type(self, step=-1)
                else:
                    keyboard_shortcuts.go_to_result(self, step=-1)
        elif is_shift_down():
            pass
        else:
            if self.overview_tab.is_visible():
                pass
            elif self.plotting_tab.is_visible():
                if key == dpg.mvKey_Next:
                    keyboard_shortcuts.go_to_plot(self, step=1)
                elif key == dpg.mvKey_Prior:
                    keyboard_shortcuts.go_to_plot(self, step=-1)
            else:
                if key == dpg.mvKey_Next:
                    keyboard_shortcuts.go_to_dataset(self, step=1)
                elif key == dpg.mvKey_Prior:
                    keyboard_shortcuts.go_to_dataset(self, step=-1)

    def is_visible(self) -> bool:
        return (
            self.overview_tab.is_visible()
            or self.datasets_tab.is_visible()
            or self.kramers_kronig_tab.is_visible()
            or self.fitting_tab.is_visible()
            or self.simulation_tab.is_visible()
            or self.plotting_tab.is_visible()
        )

    def resize(self):
        for tab in [
            self.datasets_tab,
            self.kramers_kronig_tab,
            self.fitting_tab,
            self.simulation_tab,
        ]:
            if tab.is_visible():
                tab.resize()
                return

    def show_error(self, msg: str):
        assert type(msg) is str
        if self.error_message is not None:
            dpg.split_frame(delay=250)
            self.error_message.show(msg)
        print(msg)
        self.modal_window = self.error_message.show(msg)

    def show_working_indicator(self, *args, **kwargs):
        if self.working_indicator is None:
            return
        self.modal_window = self.working_indicator.show(*args, **kwargs)

    def hide_working_indicator(self):
        if self.working_indicator is None:
            return
        self.working_indicator.hide()

    def show_plot_modal_window(self, sender: int, app_data: None, plot: Plot):
        assert type(sender) is int
        assert app_data is None
        if type(plot) is ResidualsPlot:
            self.modal_window = plot.show_modal_window()
        else:
            self.modal_window = plot.show_modal_window(  # type: ignore
                not (
                    plot == self.datasets_tab.nyquist_plot
                    or plot == self.datasets_tab.bode_plot
                )
            )

    def set_dirty(self, state: bool):
        assert type(state) is bool
        self.is_dirty = state
        if state is False:
            self.state_saved_index = self.state_history_index
        dpg.set_item_label(self.tab, self.label + ("*" if self.is_dirty else ""))

    def update_state_history(self):
        if not self.is_initialized:
            return
        while len(self.state_history) - 1 > self.state_history_index:
            self.state_history.pop()
        if self.state_history_index < self.state_saved_index:
            self.state_saved_index = -1
        self.state_history.append(serialize_state(self))
        self.state_history_index = len(self.state_history) - 1
        self.set_dirty(True)

    def undo(self):
        if len(self.state_history) < 1 or self.state_history_index < 1:
            # There is no previous state to restore (at all or we're already at the initial state).
            return
        if self.state_history_index >= len(self.state_history) - 1:
            self.state_history[-1] = serialize_state(self)
        self.state_history_index -= 1
        restore_state(self.state_history[self.state_history_index], self)
        self.set_dirty(self.state_history_index != self.state_saved_index)

    def redo(self):
        if (
            len(self.state_history) == 0
            or self.state_history_index >= len(self.state_history) - 1
        ):
            # There is no next state to restore.
            return
        self.state_history_index += 1
        restore_state(self.state_history[self.state_history_index], self)
        self.set_dirty(self.state_history_index != self.state_saved_index)

    def save_as(self, app_data: dict):
        assert type(app_data) is dict
        try:
            path: str = app_data["file_path_name"]
            filename: str
            extension: str
            filename, extension = splitext(basename(path))
            assert filename != ""
            assert extension == ".json"
        except (KeyError, AssertionError):
            self.show_error(
                format_exc()
                + """

Encountered error while trying to save project to a new path!"""
            )
            return
        if exists(path) and path != self.path:
            dpg.split_frame(delay=100)
            window: int = dpg.generate_uuid()

            def confirm_overwrite():
                dpg.delete_item(window)
                self.path = path
                self.save()

            def try_again():
                dpg.delete_item(window)
                dpg.split_frame(delay=100)
                self.save(save_as=True)

            x: int
            y: int
            w: int
            h: int
            x, y, w, h = window_pos_dims(300, 50)
            wrap_width: int = 280
            message: str = f"Path already exists:\n{path}"
            _, h = dpg.get_text_size(message, wrap_width=wrap_width)
            h += 8 + 24 * 3
            with dpg.window(
                label="Confirm overwrite",
                modal=True,
                pos=(
                    x,
                    y,
                ),
                width=w,
                height=h,
                no_resize=True,
                no_move=True,
                no_close=True,
                tag=window,
            ):
                dpg.add_text(message, wrap=wrap_width)
                dpg.add_spacer(height=8)
                with dpg.group(horizontal=True):
                    dpg.add_button(
                        label="Overwrite",
                        callback=confirm_overwrite,
                    )
                    dpg.add_button(
                        label="Cancel",
                        callback=try_again,
                    )
            self.modal_window = window
            return
        self.path = path
        self.save()

    def save(self, save_as: bool = False):
        assert type(save_as) is bool
        if self.path == "" or not isdir(dirname(self.path)) or save_as:
            self.modal_window = file_dialog(
                self.recent_directory,
                "Select path to save to",
                lambda s, a, u: self.save_as(a),
                [".json"],
            )
            return
        self.show_working_indicator("Saving project")
        try:
            path: str = str(Path(self.path).resolve())
            tmp_path: Optional[str] = None
            if exists(path):
                tmp_path = path
                i: int = 0
                while exists(tmp_path):
                    i += 1
                    tmp_path = f"{path}.bak{i}"
                rename(path, tmp_path)
            state: str = serialize_state(self, True)
            fp: IO
            with open(path, "w") as fp:
                fp.write(state)
            self.path = path
            if tmp_path is not None and exists(tmp_path):
                if exists(path):
                    remove(tmp_path)
            self.state_history[-1] = serialize_state(self)
            self.notes = self.overview_tab.get_notes()
            self.set_dirty(False)
            self.save_callback(self)
        except Exception:
            self.hide_working_indicator()
            self.show_error(
                format_exc()
                + """

Encountered error while trying to save project!"""
            )
            return
        self.hide_working_indicator()
        # Check for UUID collisions
        all_uuids: List[str] = []
        data: DataSet
        for data in self.datasets:
            all_uuids.append(data.uuid)
            all_uuids.extend(map(lambda _: _.uuid, self.tests.get(data.uuid, [])))
            all_uuids.extend(map(lambda _: _.uuid, self.fits.get(data.uuid, [])))
        all_uuids.extend(map(lambda _: _.uuid, self.simulations))
        all_uuids.extend(map(lambda _: _.uuid, self.plots))
        try:
            assert all(
                map(lambda _: type(_) is str, all_uuids)
            ), "Detected an invalid UUID!"
        except AssertionError:
            self.show_error(format_exc())
            return
        try:
            assert len(set(all_uuids)) == len(all_uuids), "Detected a UUID collision!"
        except AssertionError:
            self.show_error(format_exc())
            # TODO: Add reassignment of UUIDs if any collisions are detected?
            return

    def close(self, force: bool = False):
        if self.is_dirty and not force:
            x: int
            y: int
            w: int
            h: int
            x, y, w, h = window_pos_dims(231, 50)
            window: int = dpg.generate_uuid()

            def confirm_save():
                dpg.delete_item(window)
                if exists(self.path):
                    self.save()
                    self.close()
                else:
                    self.save()

            def confirm_discard():
                dpg.delete_item(window)
                self.set_dirty(False)
                self.close()

            with dpg.window(
                label="Unsaved changes detected!",
                pos=(
                    x,
                    y,
                ),
                width=w,
                height=h,
                modal=True,
                no_resize=True,
                no_close=True,
                tag=window,
            ):
                with dpg.group(horizontal=True):
                    dpg.add_button(label="Save", callback=confirm_save)
                    dpg.add_button(label="Discard changes", callback=confirm_discard)
                    dpg.add_button(
                        label="Cancel", callback=lambda: dpg.delete_item(window)
                    )
            self.modal_window = window
            return
        dpg.delete_item(self.key_handler)
        dpg.delete_item(self.tab)
        self.close_callback(self)  # type: ignore

    def set_label(self, label: str):
        assert type(label) is str
        self.label = label
        dpg.set_item_label(self.tab, self.label)
        self.overview_tab.set_label(label)

    def rename_project(self, label: str):
        assert type(label) is str
        label = label.strip()
        if label == "":
            return
        self.set_label(label)
        self.update_state_history()

    def set_notes(self, notes: str):
        assert type(notes) is str
        self.notes = notes
        self.overview_tab.set_notes(notes)

    def notes_modified(self, notes: str):
        assert type(notes) is str
        self.set_dirty(True)

    def select_dataset_files(self):
        self.modal_window = file_dialog(
            self.recent_directory,
            "Select data file(s)",
            lambda s, a, u: self.parse_dataset_files(
                list(a.get("selections", {}).values()),
                s,
            ),
            [
                ".*",
                ".csv",
                ".dta",
                ".idf",
                ".ids",
                ".ods",
                ".xlsx",
                ".xls",
            ],
        )

    def parse_dataset_files(self, paths: List[str], sender: int = -1):
        assert type(paths) is list and all(map(lambda _: type(_) is str, paths))
        assert type(sender) is int
        if sender >= 0:
            dpg.delete_item(sender)
        self.recent_directory = dirname(paths[-1])
        existing_labels: List[str] = list(map(lambda _: _.get_label(), self.datasets))
        loaded_data: bool = False
        num_paths: int = len(paths)
        n: int
        path: str
        for n, path in enumerate(paths):
            self.show_working_indicator(
                f"Loading data: {n + 1}/{num_paths}", n / num_paths
            )
            try:
                spectra: List[DataSet] = pyimpspec.parse_data(path)
            except UnsupportedFileFormat:
                continue
            except Exception:
                self.hide_working_indicator()
                self.show_error(
                    format_exc()
                    + f"""

Encountered error while parsing data file:
{path}

The file might not contain any impedance data (e.g. due to an incomplete measurement), it could be in an unsupported format, or the file may even be corrupted."""
                )
                return
            spectrum: DataSet
            for spectrum in spectra:
                label: str = spectrum.get_label().strip()
                if label == "":
                    label = "Data set"
                i: int = 0
                while label in existing_labels:
                    i += 1
                    label = f"{spectrum.get_label()} ({i})"
                existing_labels.append(label)
                spectrum.set_label(label)
                self.tests[spectrum.uuid] = []
                self.fits[spectrum.uuid] = []
            self.datasets.extend(spectra)
            loaded_data = True
        self.hide_working_indicator()
        if not loaded_data:
            return
        assert all(map(lambda _: type(_) is DataSet, self.datasets))
        self.update_dataset_combos(spectrum, True)
        self.update_possible_plot_series()
        self.update_state_history()

    def find_dataset(self, label: str) -> Optional[DataSet]:
        assert type(label) is str
        data: DataSet
        for data in self.datasets:
            if label == data.get_label():
                return data
        return None

    def find_simulation(self, label: str) -> Optional[SimulationResult]:
        assert type(label) is str
        result: SimulationResult
        for result in self.simulations:
            if label == result.get_label():
                return result
        return None

    def update_dataset_combos(self, data: Optional[DataSet], update_table_plots: bool):
        assert type(data) is DataSet or data is None
        assert type(update_table_plots) is bool
        self.datasets.sort(key=lambda _: _.get_label())
        labels: List[str] = list(map(lambda _: _.get_label(), self.datasets))
        label: str = data.get_label() if data is not None else ""
        self.datasets_tab.populate_combo(labels, label)
        self.kramers_kronig_tab.populate_combo(labels, label)
        self.fitting_tab.populate_combo(labels, label)
        self.simulation_tab.populate_dataset_combo(labels)
        update_sim_data: bool = (
            self.simulation_tab.get_dataset_label() == label or label not in labels
        )
        if data is not None:
            self.datasets_tab.select_dataset(
                data, update_table_plots, update_table_plots
            )
            self.kramers_kronig_tab.select_dataset(
                data,
                self.tests[data.uuid],
                update_table_plots,
            )
            self.fitting_tab.select_dataset(
                data,
                self.fits[data.uuid],
                update_table_plots,
            )
            if update_sim_data:
                self.select_simulation_dataset(label)
        elif len(self.datasets) > 0:
            self.datasets_tab.select_dataset(
                self.datasets[0], update_table_plots, update_table_plots
            )
            self.kramers_kronig_tab.select_dataset(
                self.datasets[0],
                self.tests[self.datasets[0].uuid],
                update_table_plots,
            )
            self.fitting_tab.select_dataset(
                self.datasets[0],
                self.fits[self.datasets[0].uuid],
                update_table_plots,
            )
            if update_sim_data:
                self.select_simulation_dataset(self.datasets[0].get_label())
        else:
            self.datasets_tab.select_dataset(
                None, update_table_plots, update_table_plots
            )
            self.kramers_kronig_tab.select_dataset(
                None,
                [],
                update_table_plots,
            )
            self.fitting_tab.select_dataset(
                None,
                [],
                update_table_plots,
            )
            self.select_simulation_dataset("None")

    def get_dataset(self) -> Optional[DataSet]:
        if len(self.datasets) == 0:
            return None
        return self.datasets_tab.get_dataset()

    def remove_dataset(self, force: bool = False):
        assert type(force) is bool
        data: Optional[DataSet] = self.get_dataset()
        if data is None:
            return
        window: int = dpg.generate_uuid()
        handler: int = dpg.generate_uuid()

        def close():
            if dpg.does_item_exist(window):
                dpg.hide_item(window)
                dpg.delete_item(window)
            if dpg.does_item_exist(handler):
                dpg.delete_item(handler)

        def confirm():
            close()
            self.datasets.remove(data)
            del self.tests[data.uuid]
            del self.fits[data.uuid]
            self.update_dataset_combos(None, True)
            self.update_plotting_tab()
            self.update_state_history()

        if force:
            confirm()
            return

        x: int
        y: int
        w: int
        h: int
        x, y, w, h = window_pos_dims(132, 100)
        x, y = dpg.get_mouse_pos()
        y += 100
        with dpg.window(
            label="Delete data set",
            modal=True,
            pos=(
                x,
                y,
            ),
            width=w,
            height=h,
            tag=window,
            on_close=close,
            no_resize=True,
        ):
            with dpg.group(horizontal=True):
                dpg.add_button(label="Confirm", callback=confirm)
                dpg.add_button(label="Cancel", callback=close)
        with dpg.handler_registry(tag=handler):
            dpg.add_key_release_handler(
                key=dpg.mvKey_Escape,
                callback=close,
            )
            dpg.add_key_release_handler(
                key=dpg.mvKey_Return,
                callback=confirm,
            )
        self.modal_window = window

    def modify_dataset_path(self, path: str):
        assert type(path) is str
        path = path.strip()
        data: Optional[DataSet] = self.get_dataset()
        if data is None:
            return
        elif path == data.get_path():
            return
        data.set_path(path)
        self.select_dataset(data.get_label())
        self.update_state_history()

    def rename_dataset(self, label: str):
        assert type(label) is str
        label = label.strip()
        data: Optional[DataSet] = self.get_dataset()
        if label == "" or data is None:
            return
        existing_labels: List[str] = list(map(lambda _: _.get_label(), self.datasets))
        existing_labels.pop(self.datasets.index(data))
        i: int = 0
        while label in existing_labels:
            i += 1
            label = f"{label} ({i})"
        existing_labels.append(label)
        existing_labels.sort()
        data.set_label(label)
        self.update_dataset_combos(data, False)
        self.update_plotting_tab()
        self.update_state_history()

    def subtract_impedance(self):
        data: DataSet = self.get_dataset()
        if data is None:
            return
        self.modal_window = SubtractImpedance(
            data, self.datasets, self.replace_data
        ).window

    def replace_data(self, old: DataSet, new: DataSet):
        assert type(old) is DataSet
        assert type(new) is DataSet
        assert old.uuid != new.uuid
        self.datasets.append(new)
        self.tests[new.uuid] = []
        self.fits[new.uuid] = []
        self.remove_dataset(force=True)
        label: str = new.get_label()
        self.select_dataset(label)
        if self.simulation_tab.get_dataset_label() == label:
            self.select_simulation_dataset(label)
        self.update_plotting_tab()
        self.update_state_history()

    def toggle_points(self):
        data: DataSet = self.get_dataset()
        if data is None:
            return
        self.modal_window = TogglePoints(data, self.accept_new_mask).window

    def accept_new_mask(self, mask: Dict[int, bool]):
        assert (
            type(mask) is dict
            and all(map(lambda _: type(_) is int, mask.keys()))
            and all(map(lambda _: type(_) is bool, mask.values()))
        )
        self.datasets_tab.update_mask(mask)
        self.dataset_mask_modified()

    def copy_mask(self):
        if len(self.datasets) < 2:
            return
        data: DataSet = self.get_dataset()
        if data is None:
            return
        self.modal_window = CopyMask(data, self.datasets, self.accept_new_mask).window

    def accept_average_dataset(self, data: DataSet):
        assert type(data) is DataSet
        existing_labels: List[str] = list(map(lambda _: _.get_label(), self.datasets))
        label: str = data.get_label()
        i: int = 0
        while label in existing_labels:
            i += 1
            label = f"{data.get_label()} ({i})"
        data.set_label(label)
        self.datasets.append(data)
        self.tests[data.uuid] = []
        self.fits[data.uuid] = []
        self.update_dataset_combos(data, True)
        self.update_possible_plot_series()
        self.update_state_history()

    def average_datasets(self):
        if len(self.datasets) < 2:
            return
        self.modal_window = AverageData(
            self.datasets, self.accept_average_dataset
        ).window

    def select_dataset(self, label: str):
        assert type(label) is str
        data: DataSet
        for data in self.datasets:
            if data.get_label() == label:
                self.datasets_tab.select_dataset(data, True, True)
                self.kramers_kronig_tab.select_dataset(
                    data, self.tests[data.uuid], True
                )
                self.fitting_tab.select_dataset(data, self.fits[data.uuid], True)
                return
        self.datasets_tab.select_dataset(None, False, False)
        self.kramers_kronig_tab.select_dataset(None, [], False)
        self.fitting_tab.select_dataset(None, [], False)

    def select_simulation_dataset(
        self, label: str = "", data: Optional[DataSet] = None
    ):
        assert type(label) is str
        assert type(data) is DataSet or data is None
        if data is None:
            data = self.find_dataset(label)
        result: Optional[SimulationResult]
        result = self.find_simulation(dpg.get_value(self.simulation_tab.result_combo))
        self.simulation_tab.select_dataset(data, result)

    def dataset_mask_modified(self):
        data: Optional[DataSet] = self.get_dataset()
        if data is None:
            return
        data.set_mask(self.datasets_tab.get_mask())
        self.datasets_tab.select_dataset(data, False, True)
        self.kramers_kronig_tab.select_dataset(data, self.tests[data.uuid], True)
        self.fitting_tab.select_dataset(data, self.fits[data.uuid], True)
        label: str = data.get_label()
        if self.simulation_tab.get_dataset_label() == label:
            self.select_simulation_dataset(label)
        self.update_plotting_tab()
        self.update_state_history()

    def get_test(self, data: DataSet, label: str = "") -> Optional[TestResult]:
        assert type(data) is DataSet
        assert type(label) is str
        assert data.uuid in self.tests
        labels: List[str] = list(
            map(lambda _: _.get_label(), self.tests[data.uuid]),
        )
        if label == "":
            if data == self.datasets_tab.get_dataset():
                return self.kramers_kronig_tab.get_result()
            label = dpg.get_value(self.kramers_kronig_tab.result_combo)
        if label not in labels:
            return None
        return self.tests[data.uuid][labels.index(label)]

    def remove_test(self, result: Optional[TestResult]):
        assert type(result) is TestResult or result is None
        data: Optional[DataSet] = self.get_dataset()
        if data is None:
            return
        assert data.uuid in self.tests
        results: List[TestResult] = self.tests[data.uuid]
        if result not in results:
            return
        results.remove(result)
        self.kramers_kronig_tab.select_dataset(data, results, True)
        self.update_plotting_tab()
        self.update_state_history()

    def apply_test_settings(
        self,
        result: Optional[TestResult] = None,
        settings: Optional[TestSettings] = None,
    ):
        assert type(result) is TestResult or result is None, result
        assert type(settings) is TestSettings or settings is None, settings
        if result is not None:
            assert settings is None
            settings = result.settings
        if result is None and settings is None:
            return
        assert settings is not None
        tab: KramersKronigTab = self.kramers_kronig_tab
        label: Optional[str] = test_to_label.get(settings.test)
        assert label is not None
        dpg.set_value(tab.test_combo, label)
        self.test_setting_modified(tab.test_combo, label)
        label = mode_to_label.get(settings.mode)
        dpg.set_value(tab.mode_combo, label)
        assert label is not None
        self.test_setting_modified(tab.mode_combo, label)
        dpg.set_value(tab.num_RC_slider, settings.num_RC)
        dpg.set_value(tab.add_cap_checkbox, settings.add_capacitance)
        dpg.set_value(tab.add_ind_checkbox, settings.add_inductance)
        dpg.set_value(tab.mu_crit_slider, settings.mu_criterion)
        label = method_to_label.get(settings.method)
        dpg.set_value(tab.method_combo, label)
        dpg.set_value(tab.max_nfev_input, settings.max_nfev)
        self.update_state_history()

    def test_setting_modified(self, sender: int, value: str):
        assert type(sender) is int
        assert type(value) is str
        tab: KramersKronigTab = self.kramers_kronig_tab
        if sender == tab.test_combo:
            test: Optional[Test] = label_to_test.get(value)
            assert test is not None
            if test == Test.CNLS:
                dpg.enable_item(tab.method_combo)
                dpg.enable_item(tab.max_nfev_input)
                dpg.enable_item(tab.add_ind_checkbox)
            else:
                dpg.disable_item(tab.method_combo)
                dpg.disable_item(tab.max_nfev_input)
                dpg.set_value(tab.add_ind_checkbox, True)
                dpg.disable_item(tab.add_ind_checkbox)
        elif sender == tab.mode_combo:
            mode: Optional[Mode] = label_to_mode.get(value)
            assert mode is not None
            if mode == Mode.MANUAL:
                dpg.disable_item(tab.mu_crit_slider)
            else:
                dpg.enable_item(tab.mu_crit_slider)
        else:
            raise Exception("Unsupported test setting!")

    def perform_test(self):
        data: Optional[DataSet] = self.get_dataset()
        if data is None:
            return
        tab: KramersKronigTab = self.kramers_kronig_tab
        test: Test = label_to_test.get(dpg.get_value(tab.test_combo), Test.COMPLEX)
        mode: Mode = label_to_mode.get(dpg.get_value(tab.mode_combo), Mode.EXPLORATORY)
        num_RC: int = tab.get_num_RC()
        add_cap: bool = tab.get_add_capacitor()
        add_ind: bool = tab.get_add_inductor()
        mu_crit: float = tab.get_mu_criterion()
        method: Method = tab.get_method()
        max_nfev: int = tab.get_max_nfev()
        settings: TestSettings = TestSettings(
            test,
            mode,
            num_RC,
            mu_crit,
            add_cap,
            add_ind,
            method,
            max_nfev,
        )
        num_procs: int = max(2, cpu_count() - 1)
        if mode == Mode.AUTO or mode == Mode.MANUAL:
            if mode == Mode.AUTO:
                num_RC *= -1
            self.show_working_indicator("Performing test(s)")
            try:
                raw_result: KramersKronigResult = pyimpspec.perform_test(
                    data,
                    test=test_to_value[test],
                    num_RC=num_RC,
                    mu_criterion=mu_crit,
                    add_capacitance=add_cap,
                    add_inductance=add_ind,
                    method=method_to_value[method],
                    max_nfev=max_nfev,
                    num_procs=num_procs,
                )
            except FittingError:
                self.hide_working_indicator()
                self.show_error(
                    format_exc()
                    + """

Encountered error while performing a test!"""
                )
                return
            self.hide_working_indicator()
            result = TestResult(
                uuid4().hex,
                time(),
                raw_result.circuit,
                raw_result.num_RC,
                raw_result.mu,
                raw_result.pseudo_chisqr,
                raw_result.frequency,
                raw_result.impedance,
                raw_result.real_residual,
                raw_result.imaginary_residual,
                data.get_mask().copy(),
                settings,
            )
            self.tests[data.uuid].insert(0, result)
            self.kramers_kronig_tab.select_dataset(data, self.tests[data.uuid], True)
            self.update_plotting_tab()
            self.update_state_history()
        elif mode == Mode.EXPLORATORY:
            num_RCs: List[int] = list(range(1, num_RC + 1))
            if len(num_RCs) == 0:
                return
            self.show_working_indicator("Performing test(s)")
            try:
                raw_results: List[
                    KramersKronigResult
                ] = pyimpspec.perform_exploratory_tests(
                    data,
                    test=test_to_value[test],
                    num_RCs=num_RCs,
                    mu_criterion=mu_crit,
                    add_capacitance=add_cap,
                    add_inductance=add_ind,
                    method=method_to_value[method],
                    max_nfev=max_nfev,
                    num_procs=num_procs,
                )
            except FittingError:
                self.hide_working_indicator()
                self.show_error(
                    format_exc()
                    + """

Encountered error while performing a test!"""
                )
                return
            self.hide_working_indicator()
            self.show_exploratory_results(data, raw_results, settings, array(num_RCs))
        else:
            raise Exception("Unsupported mode!")

    def accept_exploratory_result(
        self, data: DataSet, result: KramersKronigResult, settings: TestSettings
    ):
        assert type(data) is DataSet
        assert type(result) is KramersKronigResult
        assert type(settings) is TestSettings
        self.tests[data.uuid].insert(
            0,
            TestResult(
                uuid4().hex,
                time(),
                result.circuit,
                result.num_RC,
                result.mu,
                result.pseudo_chisqr,
                result.frequency,
                result.impedance,
                result.real_residual,
                result.imaginary_residual,
                data.get_mask().copy(),
                settings,
            ),
        )
        self.kramers_kronig_tab.select_dataset(data, self.tests[data.uuid], True)
        self.update_plotting_tab()
        self.update_state_history()

    def show_exploratory_results(
        self,
        data: DataSet,
        results: List[KramersKronigResult],
        settings: TestSettings,
        num_RCs: ndarray,
    ):
        assert type(data) is DataSet
        assert type(results) is list and all(
            map(lambda _: type(_) is KramersKronigResult, results)
        )
        assert type(settings) is TestSettings
        assert type(num_RCs) is ndarray
        exploratory_results: ExploratoryResults = ExploratoryResults(
            data, results, settings, num_RCs, self.accept_exploratory_result
        )
        self.modal_window = exploratory_results.window

    def select_test_result(
        self,
        label: str = "",
        result: Optional[TestResult] = None,
        data: Optional[DataSet] = None,
    ):
        assert type(label) is str
        assert type(result) is TestResult or result is None
        assert type(data) is DataSet or data is None
        if data is None:
            data = self.get_dataset()
        if data is None:
            self.kramers_kronig_tab.select_result(None, None)
            return
        if result is not None:
            self.kramers_kronig_tab.select_result(data, result)
        else:
            self.kramers_kronig_tab.select_result(data, self.get_test(data, label))

    def show_fit_circuit_editor(self):
        x: int
        y: int
        w: int
        h: int
        x, y, w, h = window_pos_dims()
        self.modal_window = dpg.add_window(
            label="Circuit editor",
            modal=True,
            pos=(
                x,
                y,
            ),
            width=w,
            height=h,
        )
        editor: CircuitEditor = CircuitEditor(
            self.modal_window,
            self.accept_fit_circuit,
        )
        dpg.configure_item(self.modal_window, on_close=editor.hide_window)
        if self.latest_fit_circuit is not None:
            editor.parse_cdc(self.latest_fit_circuit.to_string(4), True)

    def accept_fit_circuit(self, circuit: Optional[Circuit]):
        assert type(circuit) is Circuit or circuit is None
        if circuit is None:
            return
        self.fitting_tab.update_cdc_input(circuit.to_string(), themes.valid_cdc)
        self.latest_fit_circuit = circuit
        self.update_state_history()

    def copy_fit_output(self, result: Optional[FitResult]):
        assert type(result) is FitResult or result is None
        if result is None:
            dpg.set_clipboard_text("")
            return
        data: Optional[DataSet] = self.datasets_tab.get_dataset()
        if data is None:
            return
        output: Output = self.fitting_tab.get_output_type()
        dataframe: DataFrame
        expr: Expr
        self.show_working_indicator("Generating output")
        if output == Output.CDC_BASIC:
            dpg.set_clipboard_text(result.circuit.to_string())
        elif output == Output.CDC_EXTENDED:
            dpg.set_clipboard_text(result.circuit.to_string(6))
        elif output == Output.CSV_DATA_TABLE:
            Z_exp: ndarray = data.get_impedance(masked=None)
            Z_fit: ndarray = result.impedance
            indices: ndarray = array([k for k, v in result.mask.items() if v is False])
            dataframe = DataFrame.from_dict(
                {
                    "f (Hz)": result.frequency,
                    "Zre_exp (ohm)": Z_exp[indices].real,
                    "Zim_exp (ohm)": Z_exp[indices].imag,
                    "Zre_fit (ohm)": Z_fit.real,
                    "Zim_fit (ohm)": Z_fit.imag,
                }
            )
            dpg.set_clipboard_text(dataframe.to_csv(index=False))
        elif (
            output == Output.CSV_PARAMETERS_TABLE
            or output == Output.JSON_PARAMETERS_TABLE
            or output == Output.LATEX_PARAMETERS_TABLE
            or output == Output.MARKDOWN_PARAMETERS_TABLE
        ):
            dataframe = result.to_dataframe()
            if output == Output.CSV_PARAMETERS_TABLE:
                dpg.set_clipboard_text(dataframe.to_csv(index=False))
            elif output == Output.JSON_PARAMETERS_TABLE:
                dpg.set_clipboard_text(dataframe.to_json())
            elif output == Output.LATEX_PARAMETERS_TABLE:
                dpg.set_clipboard_text(dataframe.to_latex(index=False))
            elif output == Output.MARKDOWN_PARAMETERS_TABLE:
                dpg.set_clipboard_text(
                    dataframe.to_markdown(index=False, floatfmt=".3g")
                )
        elif output == Output.LATEX_EXPR:
            dpg.set_clipboard_text(latex(get_sympy_expr(result.circuit)))
        elif output == Output.LATEX_DIAGRAM:
            dpg.set_clipboard_text(result.circuit.to_circuitikz())
        elif output == Output.SYMPY_EXPR or output == Output.SYMPY_EXPR_VALUES:
            expr = get_sympy_expr(result.circuit)
            if output == Output.SYMPY_EXPR:
                dpg.set_clipboard_text(str(expr))
            else:
                lines: List[str] = []
                lines.append(f'expr = sympify("{str(expr)}")')
                symbols: List[str] = list(sorted(map(str, expr.free_symbols)))
                if len(symbols) == 0:
                    dpg.set_clipboard_text(str(expr))
                else:
                    parameters = result.circuit.get_parameters()
                    lines.append(
                        ", ".join(symbols) + " = sorted(expr.free_symbols, key=str)"
                    )
                    lines.append("parameters = {")
                    if "f" in symbols:
                        symbols.remove("f")
                    sym: str
                    for sym in symbols:
                        assert "_" in sym
                        ident: Union[int, str]
                        label, ident = sym.split("_")
                        value: Optional[float] = None
                        try:
                            ident = int(label)
                            assert ident in parameters
                            value = parameters[ident][label]
                        except ValueError:
                            for element in result.circuit.get_elements():
                                if not element.get_label().endswith(f"_{ident}"):
                                    continue
                                value = element.get_parameters().get(label)
                        assert value is not None
                        lines.append(f"\t{sym}: {value:.6E},")
                    lines.append("}")
                    dpg.set_clipboard_text("\n".join(lines))
        else:
            self.hide_working_indicator()
            raise Exception(f"Unsupported output: {label} -> {output}")
        self.hide_working_indicator()

    def validate_fit_circuit(self, sender: int, cdc: str):
        assert type(sender) is int
        assert type(cdc) is str
        cdc = cdc.strip()
        if cdc == "" or cdc == "[]":
            return
        try:
            circuit: Circuit = pyimpspec.string_to_circuit(cdc)
        except ParsingError:
            self.fitting_tab.update_cdc_input(cdc, themes.invalid_cdc)
            self.latest_fit_circuit = None
            return
        if sender != self.fitting_tab.cdc_input:
            cdc = circuit.to_string()
        if cdc == "[]":
            cdc = ""
        self.fitting_tab.update_cdc_input(cdc, themes.valid_cdc)
        self.latest_fit_circuit = circuit

    def perform_fit(self):
        data: Optional[DataSet] = self.get_dataset()
        current_cdc: str = self.fitting_tab.get_cdc_input()
        if data is None:
            return
        elif (
            self.latest_fit_circuit is None
            or current_cdc != self.latest_fit_circuit.to_string()
        ):
            self.validate_fit_circuit(
                self.fitting_tab.cdc_input,
                current_cdc,
            )
            if self.latest_fit_circuit is None:
                return
        elif current_cdc in ["", "[]"]:
            return
        tab: FittingTab = self.fitting_tab
        cdc: str = self.latest_fit_circuit.to_string(12)
        method: Method = tab.get_method()
        weight: Weight = tab.get_weight()
        max_nfev: int = tab.get_max_nfev()
        settings: FitSettings = FitSettings(
            cdc,
            method,
            weight,
            max_nfev,
        )
        num_procs: int = max(2, cpu_count() - 1)
        try:
            pyimpspec.analysis.fitting.validate_circuit(self.latest_fit_circuit)
        except AssertionError:
            self.show_error(
                format_exc()
                + """

Encountered error while performing a fit!"""
            )
            return
        self.show_working_indicator("Performing fit(s)")
        try:
            raw_result: FittingResult = pyimpspec.fit_circuit_to_data(
                self.latest_fit_circuit,
                data,
                method=method_to_value.get(method),
                weight=weight_to_value.get(weight),
                max_nfev=max_nfev,
                num_procs=num_procs,
            )
        except FittingError:
            self.hide_working_indicator()
            self.show_error(
                format_exc()
                + """

Encountered error while performing a fit!"""
            )
            return
        self.hide_working_indicator()
        result: FitResult = FitResult(
            uuid4().hex,
            time(),
            raw_result.circuit,
            raw_result.parameters,
            raw_result.frequency,
            raw_result.impedance,
            data.get_mask(),
            raw_result.real_residual,
            raw_result.imaginary_residual,
            raw_result.minimizer_result.chisqr,
            raw_result.minimizer_result.redchi,
            raw_result.minimizer_result.aic,
            raw_result.minimizer_result.bic,
            raw_result.minimizer_result.ndata,
            raw_result.minimizer_result.nfree,
            raw_result.minimizer_result.nfev,
            value_to_method.get(raw_result.method),
            value_to_weight.get(raw_result.weight),
            settings,
        )
        self.fits[data.uuid].insert(0, result)
        self.fitting_tab.select_dataset(data, self.fits[data.uuid], True)
        self.update_plotting_tab()
        self.update_state_history()

    def get_fit(self, data: DataSet, label: str = "") -> Optional[FitResult]:
        assert type(data) is DataSet
        assert type(label) is str
        assert data.uuid in self.fits
        labels: List[str] = list(
            map(lambda _: _.get_label(), self.fits[data.uuid]),
        )
        if label == "":
            if self.datasets_tab.get_dataset() == data:
                return self.fitting_tab.get_result()
            label = dpg.get_value(self.fitting_tab.result_combo)
        if label not in labels:
            return None
        return self.fits[data.uuid][labels.index(label)]

    def select_fit_result(
        self,
        label: str = "",
        result: Optional[FitResult] = None,
        data: Optional[DataSet] = None,
    ):
        assert type(label) is str
        assert type(result) is FitResult or result is None
        assert type(data) is DataSet or data is None
        if data is None:
            data = self.get_dataset()
        if data is None:
            self.fitting_tab.select_result(None, None)
            return
        if result is not None:
            self.fitting_tab.select_result(data, result)
        else:
            self.fitting_tab.select_result(data, self.get_fit(data, label))

    def apply_fit_settings(
        self, result: Optional[FitResult] = None, settings: Optional[FitSettings] = None
    ):
        assert type(result) is FitResult or result is None, result
        assert type(settings) is FitSettings or settings is None, settings
        if result is not None:
            assert settings is None
            settings = result.settings
        if result is None and settings is None:
            return
        assert settings is not None
        tab: FittingTab = self.fitting_tab
        self.validate_fit_circuit(-1, settings.cdc)
        dpg.set_value(tab.method_combo, method_to_label.get(settings.method))
        dpg.set_value(tab.weight_combo, weight_to_label.get(settings.weight))
        dpg.set_value(tab.max_nfev_input, settings.max_nfev)
        self.update_state_history()

    def remove_fit(self, result: Optional[FitResult]):
        assert type(result) is FitResult or result is None
        data: Optional[DataSet] = self.get_dataset()
        if data is None:
            return
        assert data.uuid in self.fits
        results: List[FitResult] = self.fits[data.uuid]
        if result not in results:
            return
        results.remove(result)
        self.fitting_tab.select_dataset(data, results, True)
        self.update_plotting_tab()
        self.update_state_history()

    def perform_simulation(self):
        current_cdc: str = self.simulation_tab.get_cdc_input()
        if (
            self.latest_simulation_circuit is None
            or current_cdc != self.latest_simulation_circuit.to_string()
        ):
            self.validate_simulation_circuit(
                self.simulation_tab.cdc_input,
                current_cdc,
            )
            if self.latest_simulation_circuit is None:
                return
        elif self.simulation_tab.get_cdc_input() in ["", "[]"]:
            return
        tab: SimulationTab = self.simulation_tab
        cdc: str = self.latest_simulation_circuit.to_string(12)
        freqs: Tuple[float, float] = (
            tab.get_max_freq(),
            tab.get_min_freq(),
        )
        max_f: float = max(freqs)
        min_f: float = min(freqs)
        if freqs[0] != max_f:
            tab.set_freq_range(min_f, max_f)
        num_freq_per_dec: int = tab.get_num_per_decade()
        settings: SimulationSettings = SimulationSettings(
            cdc,
            min_f,
            max_f,
            num_freq_per_dec,
        )
        result: SimulationResult = SimulationResult(
            uuid4().hex,
            time(),
            pyimpspec.string_to_circuit(cdc),
            settings,
        )
        self.simulations.insert(0, result)
        label: str = result.get_label()
        self.simulation_tab.populate_result_combo(
            list(map(lambda _: _.get_label(), self.simulations)),
            label,
        )
        self.select_simulation_result(label)
        self.update_plotting_tab()
        self.update_state_history()

    def select_simulation_result(
        self, label: str = "", result: Optional[SimulationResult] = None
    ):
        assert type(label) is str
        assert type(result) is SimulationResult or result is None
        data: Optional[DataSet]
        data = self.simulation_tab.get_dataset()
        if result is None:
            result = self.find_simulation(label)
        self.simulation_tab.select_result(data, result)

    def remove_simulation(self, result: Optional[SimulationResult]):
        assert type(result) is SimulationResult or result is None
        if result is None:
            return
        assert result in self.simulations
        self.simulations.remove(result)
        label: str = (
            self.simulations[0].get_label() if len(self.simulations) > 0 else ""
        )
        self.select_simulation_result(label)
        self.update_plotting_tab()
        self.update_state_history()

    def apply_simulation_settings(
        self,
        result: Optional[SimulationResult] = None,
        settings: Optional[SimulationSettings] = None,
    ):
        assert type(result) is SimulationResult or result is None, result
        assert type(settings) is SimulationSettings or settings is None, settings
        if result is not None:
            assert settings is None
            settings = result.settings
        if result is None and settings is None:
            return
        assert settings is not None
        tab: SimulationTab = self.simulation_tab
        self.validate_simulation_circuit(-1, settings.cdc)
        dpg.set_value(tab.max_freq_input, settings.max_frequency)
        dpg.set_value(tab.min_freq_input, settings.min_frequency)
        dpg.set_value(tab.per_decade_input, settings.num_freq_per_dec)
        self.update_state_history()

    def validate_simulation_circuit(self, sender: int, cdc: str):
        assert type(sender) is int
        assert type(cdc) is str
        cdc = cdc.strip()
        if cdc == "" or cdc == "[]":
            return
        try:
            circuit: Circuit = pyimpspec.string_to_circuit(cdc)
        except ParsingError:
            self.simulation_tab.update_cdc_input(cdc, themes.invalid_cdc)
            self.latest_simulation_circuit = None
            return
        if sender != self.simulation_tab.cdc_input:
            cdc = circuit.to_string()
        if cdc == "[]":
            cdc = ""
        self.simulation_tab.update_cdc_input(cdc, themes.valid_cdc)
        self.latest_simulation_circuit = circuit

    def show_simulation_circuit_editor(self):
        x: int
        y: int
        w: int
        h: int
        x, y, w, h = window_pos_dims()
        self.modal_window = dpg.add_window(
            label="Circuit editor",
            modal=True,
            pos=(
                x,
                y,
            ),
            width=w,
            height=h,
        )
        editor: CircuitEditor = CircuitEditor(
            self.modal_window,
            self.accept_simulation_circuit,
        )
        dpg.configure_item(self.modal_window, on_close=editor.hide_window)
        if self.latest_simulation_circuit is not None:
            editor.parse_cdc(self.latest_simulation_circuit.to_string(4), True)

    def accept_simulation_circuit(self, circuit: Optional[Circuit]):
        assert type(circuit) is Circuit or circuit is None
        if circuit is None:
            return
        self.simulation_tab.update_cdc_input(circuit.to_string(), themes.valid_cdc)
        self.latest_simulation_circuit = circuit
        self.update_state_history()

    def copy_simulation_output(self, result: Optional[SimulationResult]):
        assert type(result) is SimulationResult or result is None
        if result is None:
            dpg.set_clipboard_text("")
            return
        output: Output = self.simulation_tab.get_output_type()
        expr: Expr
        dataframe: DataFrame
        value: Optional[float]
        self.show_working_indicator("Generating output")
        if output == Output.CDC_BASIC:
            dpg.set_clipboard_text(result.circuit.to_string())
        elif output == Output.CDC_EXTENDED:
            dpg.set_clipboard_text(result.circuit.to_string(6))
        elif output == Output.CSV_DATA_TABLE:
            Z_sim: ndarray = result.get_impedance()
            dataframe = DataFrame.from_dict(
                {
                    "f (Hz)": result.get_frequency(),
                    "Zre_sim (ohm)": Z_sim.real,
                    "Zim_sim (ohm)": Z_sim.imag,
                }
            )
            dpg.set_clipboard_text(dataframe.to_csv(index=False))
        elif (
            output == Output.CSV_PARAMETERS_TABLE
            or output == Output.JSON_PARAMETERS_TABLE
            or output == Output.LATEX_PARAMETERS_TABLE
            or output == Output.MARKDOWN_PARAMETERS_TABLE
        ):
            dataframe = result.to_dataframe()
            if output == Output.CSV_PARAMETERS_TABLE:
                dpg.set_clipboard_text(dataframe.to_csv(index=False))
            elif output == Output.JSON_PARAMETERS_TABLE:
                dpg.set_clipboard_text(dataframe.to_json())
            elif output == Output.LATEX_PARAMETERS_TABLE:
                dpg.set_clipboard_text(dataframe.to_latex(index=False))
            elif output == Output.MARKDOWN_PARAMETERS_TABLE:
                dpg.set_clipboard_text(
                    dataframe.to_markdown(index=False, floatfmt=".3g")
                )
        elif output == Output.LATEX_EXPR:
            dpg.set_clipboard_text(latex(get_sympy_expr(result.circuit)))
        elif output == Output.LATEX_DIAGRAM:
            dpg.set_clipboard_text(result.circuit.to_circuitikz())
        elif output == Output.SYMPY_EXPR or output == Output.SYMPY_EXPR_VALUES:
            expr = get_sympy_expr(result.circuit)
            if output == Output.SYMPY_EXPR:
                dpg.set_clipboard_text(str(expr))
            else:
                lines: List[str] = []
                lines.append(f'expr = sympify("{str(expr)}")')
                symbols: List[str] = list(sorted(map(str, expr.free_symbols)))
                if len(symbols) == 0:
                    dpg.set_clipboard_text(str(expr))
                else:
                    parameters: Dict[int, OrderedDict[str, float]]
                    parameters = result.circuit.get_parameters()
                    lines.append(
                        ", ".join(symbols) + " = sorted(expr.free_symbols, key=str)"
                    )
                    lines.append("parameters = {")
                    if "f" in symbols:
                        symbols.remove("f")
                    sym: str
                    for sym in symbols:
                        assert "_" in sym
                        ident: Union[int, str]
                        label, ident = sym.split("_")
                        value = None
                        try:
                            ident = int(label)
                            assert ident in parameters
                            value = parameters[ident][label]
                        except ValueError:
                            for element in result.circuit.get_elements():
                                if not element.get_label().endswith(f"_{ident}"):
                                    continue
                                value = element.get_parameters().get(label)
                        assert value is not None
                        lines.append(f"\t{sym}: {value:.6E},")
                    lines.append("}")
                    dpg.set_clipboard_text("\n".join(lines))
        else:
            self.hide_working_indicator()
            raise Exception(f"Unsupported output: {label} -> {output}")
        self.hide_working_indicator()

    def update_plotting_tab(self):
        self.update_possible_plot_series()
        self.update_active_plot_series()
        self.update_plots()

    def update_possible_plot_series(self):
        plot: Optional[Plot] = self.plotting_tab.get_plot()
        if plot is None:
            return
        self.plotting_tab.populate_possible_series(
            plot,
            self.datasets,
            self.tests,
            self.fits,
            self.simulations,
            self.toggle_plot_series,
            self.select_plot_series,
        )

    def update_active_plot_series(self):
        plot: Optional[Plot] = self.plotting_tab.get_plot()
        if plot is None:
            return
        self.plotting_tab.populate_active_series(
            plot,
            self.datasets,
            self.tests,
            self.fits,
            self.simulations,
            self.update_plot_series_label,
            self.edit_plot_series_theme,
            self.change_plot_series_order,
        )

    def update_plots(self, fit_to_data: Optional[bool] = None):
        assert type(fit_to_data) is bool or fit_to_data is None
        plot: Optional[PlotSettings] = self.plotting_tab.get_plot()
        if plot is None:
            return
        self.plotting_tab.update_plots(
            plot,
            self.datasets,
            self.tests,
            self.fits,
            self.simulations,
            fit_to_data,
        )

    def create_plot(self):
        existing_labels: List[str] = list(map(lambda _: _.get_label(), self.plots))
        label: str = "Plot"
        i: int = 1
        while label in existing_labels:
            i += 1
            label = f"Plot ({i})"
        plot: PlotSettings = PlotSettings(
            label,
            PlotType.NYQUIST,
            [],  # Series order
            {},  # Labels
            {},  # Colors
            {},  # Markers
            {},  # Show lines
            {},  # Themes
            uuid4().hex,
        )
        self.plots.append(plot)
        self.plots.sort(key=lambda _: _.get_label())
        self.plotting_tab.populate_plot_combo(self.plots)
        self.select_plot(plot.get_label())
        self.update_state_history()

    def select_plot(self, label: str, fit_to_data: Optional[bool] = None):
        if len(self.plots) == 0:
            return
        plot: PlotSettings
        for plot in self.plots:
            if plot.get_label() == label:
                break
        self.plotting_tab.select_plot(plot)
        self.update_active_plot_series()
        self.update_plots(fit_to_data=fit_to_data)

    def update_plot_label(self, label: str):
        plot: Optional[PlotSettings] = self.plotting_tab.get_plot()
        if plot is None:
            return
        plot.set_label(label)
        self.plots.sort(key=lambda _: _.get_label())
        self.plotting_tab.populate_plot_combo(self.plots)
        self.select_plot(plot.get_label())
        self.update_state_history()

    def select_plot_type(self, label: str):
        plot: Optional[PlotSettings] = self.plotting_tab.get_plot()
        if plot is None:
            return
        plot_type: PlotType = label_to_plot_type[label]
        plot.plot_type = plot_type
        self.plotting_tab.select_plot_type(plot_type)
        self.update_state_history()

    def remove_plot(self):
        plot: Optional[PlotSettings] = self.plotting_tab.get_plot()
        if plot is None:
            return
        self.plots.remove(plot)
        if len(self.plots) == 0:
            self.create_plot()
        else:
            plot = self.plots[0]
            self.plotting_tab.populate_plot_combo(self.plots)
            self.select_plot(plot.get_label())
        self.update_state_history()

    def copy_plot_appearance_settings(self):
        plot: Optional[PlotSettings] = self.plotting_tab.get_plot()
        if plot is None:
            return
        elif len(self.plots) < 2:
            return
        affected_series: List[DataSet, TestResult, FitResult, SimulationResult] = []
        uuid: str
        for uuid in plot.themes:
            series: Union[DataSet, TestResult, FitResult, SimulationResult]
            series = plot.find_series(
                uuid,
                self.datasets,
                self.tests,
                self.fits,
                self.simulations,
            )
            if series is None:
                continue
            affected_series.append(series)
        types: list = [
            DataSet,
            TestResult,
            FitResult,
            SimulationResult,
        ]
        affected_series.sort(
            key=lambda _: (
                types.index(type(_)),
                _.get_label(),
            )
        )
        affected_checkboxes: Dict[str, bool] = {_.uuid: True for _ in affected_series}
        window: int = dpg.generate_uuid()
        handler: int = dpg.generate_uuid()
        source_combo: int = dpg.generate_uuid()
        preview_table: int = dpg.generate_uuid()
        labels_checkbox: int = dpg.generate_uuid()
        colors_checkbox: int = dpg.generate_uuid()
        markers_checkbox: int = dpg.generate_uuid()
        lines_checkbox: int = dpg.generate_uuid()
        plot_lookup: Dict[str, PlotSettings] = {_.get_label(): _ for _ in self.plots}
        del plot_lookup[plot.get_label()]
        marker_lookup: Dict[int, str] = {v: k for k, v in themes.PLOT_MARKERS.items()}
        label: str

        def close():
            dpg.hide_item(window)
            dpg.delete_item(window)
            dpg.delete_item(handler)

        def accept_settings():
            row: int
            for row in dpg.get_item_children(preview_table, slot=1):
                uuid = dpg.get_item_user_data(row)
                i: int
                item: int
                for i, item in enumerate(dpg.get_item_children(row, slot=1)):
                    item_type: str = dpg.get_item_type(item)
                    if i == 0:
                        assert "::mvText" in item_type, item_type
                        plot.set_series_label(uuid, dpg.get_item_user_data(item))
                    elif i == 1:
                        assert "::mvTooltip" in item_type, item_type
                    elif i == 2:
                        assert "::mvColorEdit" in item_type, item_type
                        plot.set_series_color(uuid, dpg.get_item_user_data(item))
                        themes.update_plot_theme_color(
                            plot.themes[uuid], plot.get_series_color(uuid)
                        )
                    elif i == 3:
                        assert "::mvText" in item_type, item_type
                        plot.set_series_marker(uuid, dpg.get_item_user_data(item))
                        themes.update_plot_theme_marker(
                            plot.themes[uuid], plot.get_series_marker(uuid)
                        )
                    elif i == 4:
                        assert "::mvCheckbox" in item_type, item_type
                        plot.set_series_line(uuid, dpg.get_item_user_data(item))
            close()
            self.update_plotting_tab()
            self.update_state_history()

        def change_source(label=""):
            if label == "":
                label = dpg.get_value(source_combo)
            other_plot: PlotSettings = plot_lookup[label]
            assert other_plot is not None
            dpg.delete_item(preview_table, children_only=True)
            dpg.add_table_column(label="Label", parent=preview_table)
            dpg.add_table_column(label="Color", width_fixed=True, parent=preview_table)
            dpg.add_table_column(label="Marker", width_fixed=True, parent=preview_table)
            dpg.add_table_column(label="Line", width_fixed=True, parent=preview_table)
            copy_labels: bool = dpg.get_value(labels_checkbox)
            copy_colors: bool = dpg.get_value(colors_checkbox)
            copy_markers: bool = dpg.get_value(markers_checkbox)
            copy_lines: bool = dpg.get_value(lines_checkbox)
            for series in affected_series:
                uuid = series.uuid
                source: PlotSettings = (
                    other_plot
                    if uuid in other_plot.themes and affected_checkboxes[uuid] is True
                    else plot
                )
                with dpg.table_row(parent=preview_table, user_data=uuid):
                    label = (
                        source.get_series_label(uuid)
                        if copy_labels
                        else plot.get_series_label(uuid)
                    )
                    dpg.add_text(
                        label or series.get_label(),
                        user_data=label,
                    )
                    attach_tooltip(
                        label
                        or series.get_label()
                        + (
                            ""
                            if (label or series.get_label()) == series.get_label()
                            else f"\n{series.get_label()}"
                        )
                    )
                    color: List[float] = (
                        source.get_series_color(uuid)
                        if copy_colors
                        else plot.get_series_color(uuid)
                    )
                    dpg.add_color_edit(
                        default_value=color,
                        enabled=False,
                        no_picker=True,
                        alpha_preview=dpg.mvColorEdit_AlphaPreviewHalf,
                        no_inputs=True,
                        user_data=color,
                    )
                    marker: int = (
                        source.get_series_marker(uuid)
                        if copy_markers
                        else plot.get_series_marker(uuid)
                    )
                    dpg.add_text(
                        marker_lookup.get(marker, "None"),
                        user_data=marker,
                    )
                    show_line: bool = (
                        source.get_series_line(uuid)
                        if copy_lines
                        else plot.get_series_line(uuid)
                    )
                    dpg.add_checkbox(
                        default_value=show_line,
                        enabled=False,
                        user_data=show_line,
                    )

        def toggle_affected_series(state: bool, uuid: str):
            nonlocal affected_checkboxes
            affected_checkboxes[uuid] = state
            change_source()

        x: int
        y: int
        w: int
        h: int
        x, y, w, h = window_pos_dims(720, 540)
        with dpg.window(
            label="Copy appearance settings",
            modal=True,
            no_resize=True,
            pos=(
                x,
                y,
            ),
            width=w,
            height=h,
            on_close=close,
            tag=window,
        ):
            with dpg.group(horizontal=True):
                dpg.add_text("Source")
                dpg.add_combo(
                    items=list(plot_lookup.keys()),
                    default_value=list(plot_lookup.keys())[0],
                    width=-1,
                    callback=lambda s, a, u: change_source(a),
                    tag=source_combo,
                )
            with dpg.group(horizontal=True):
                with dpg.group():
                    dpg.add_text("Before")
                    with dpg.child_window(width=348, height=-24):
                        with dpg.table(
                            borders_outerV=True,
                            borders_outerH=True,
                            borders_innerV=True,
                            borders_innerH=True,
                            scrollY=True,
                            freeze_rows=1,
                            width=-1,
                            height=18 + 23 * len(plot.series_order),
                            # tag=self.active_series_table,
                        ):
                            dpg.add_table_column(label="", width_fixed=True)
                            dpg.add_table_column(label="Label")
                            dpg.add_table_column(label="Color", width_fixed=True)
                            dpg.add_table_column(label="Marker", width_fixed=True)
                            dpg.add_table_column(label="Line", width_fixed=True)
                            for series in affected_series:
                                uuid = series.uuid
                                with dpg.table_row():
                                    dpg.add_checkbox(
                                        default_value=True,
                                        callback=lambda s, a, u: toggle_affected_series(
                                            a, u
                                        ),
                                        user_data=uuid,
                                    )
                                    attach_tooltip(
                                        "Toggle this to set whether or not this series should copy settings from the chosen source."
                                    )
                                    label = (
                                        plot.get_series_label(uuid)
                                        or series.get_label()
                                    )
                                    dpg.add_text(label)
                                    attach_tooltip(
                                        label
                                        + (
                                            ""
                                            if label == series.get_label()
                                            else f"\n{series.get_label()}"
                                        )
                                    )
                                    dpg.add_color_edit(
                                        default_value=plot.get_series_color(uuid),
                                        enabled=False,
                                        no_picker=True,
                                        alpha_preview=dpg.mvColorEdit_AlphaPreviewHalf,
                                        no_inputs=True,
                                    )
                                    dpg.add_text(
                                        marker_lookup.get(
                                            plot.get_series_marker(uuid), "None"
                                        )
                                    )
                                    dpg.add_checkbox(
                                        default_value=plot.get_series_line(uuid),
                                        enabled=False,
                                    )
                with dpg.group():
                    dpg.add_text("After")
                    with dpg.child_window(width=348, height=-24):
                        dpg.add_table(
                            borders_outerV=True,
                            borders_outerH=True,
                            borders_innerV=True,
                            borders_innerH=True,
                            scrollY=True,
                            freeze_rows=1,
                            width=-1,
                            height=18 + 23 * len(plot.series_order),
                            tag=preview_table,
                        )
            with dpg.group(horizontal=True):
                dpg.add_button(
                    label="Accept",
                    callback=accept_settings,
                )
                dpg.add_spacer(width=354)
                dpg.add_checkbox(
                    label="Labels",
                    default_value=True,
                    tag=labels_checkbox,
                    callback=lambda s, a, u: change_source(),
                )
                dpg.add_checkbox(
                    label="Colors",
                    default_value=True,
                    tag=colors_checkbox,
                    callback=lambda s, a, u: change_source(),
                )
                dpg.add_checkbox(
                    label="Markers",
                    default_value=True,
                    tag=markers_checkbox,
                    callback=lambda s, a, u: change_source(),
                )
                dpg.add_checkbox(
                    label="Lines",
                    default_value=True,
                    tag=lines_checkbox,
                    callback=lambda s, a, u: change_source(),
                )

        change_source()
        with dpg.handler_registry(tag=handler):
            dpg.add_key_release_handler(
                key=dpg.mvKey_Escape,
                callback=close,
            )
            dpg.add_key_release_handler(
                key=dpg.mvKey_Return,
                callback=accept_settings,
            )
        self.modal_window = window

    def select_all_plot_series(
        self,
        select: bool,
    ):
        assert type(select) is bool
        plot: Optional[PlotSettings] = self.plotting_tab.get_plot()
        if plot is None:
            return
        series: Union[DataSet, TestResult, FitResult, SimulationResult]
        for series in self.datasets:
            if select:
                plot.add_series(series)
            else:
                plot.remove_series(series.uuid)
        tests: List[TestResult]
        for tests in self.tests.values():
            for series in tests:
                if select:
                    plot.add_series(series)
                else:
                    plot.remove_series(series.uuid)
        fits: List[FitResult]
        for fits in self.fits.values():
            for series in fits:
                if select:
                    plot.add_series(series)
                else:
                    plot.remove_series(series.uuid)
        for series in self.simulations:
            if select:
                plot.add_series(series)
            else:
                plot.remove_series(series.uuid)
        self.update_possible_plot_series()
        self.update_active_plot_series()
        self.update_plots()
        self.update_state_history()

    def select_plot_series(
        self,
        user_data: Tuple[
            bool, List[Union[DataSet, TestResult, FitResult, SimulationResult]]
        ],
    ):
        assert (
            type(user_data) is tuple
            and len(user_data) == 2
            and type(user_data[0]) is bool
            and type(user_data[1]) is list
        )
        plot: Optional[PlotSettings] = self.plotting_tab.get_plot()
        if plot is None:
            return
        select: bool
        affected_series: List[Union[DataSet, TestResult, FitResult, SimulationResult]]
        select, affected_series = user_data
        series: Union[DataSet, TestResult, FitResult, SimulationResult]
        for series in affected_series:
            if select:
                plot.add_series(series)
            else:
                plot.remove_series(series.uuid)
        self.update_possible_plot_series()
        self.update_active_plot_series()
        self.update_plots()
        self.update_state_history()

    def toggle_plot_series(
        self,
        sender: int,
        state: bool,
        series: Union[DataSet, TestResult, FitResult, SimulationResult],
    ):
        assert type(sender) is int
        assert type(state) is bool
        assert (
            type(series) is DataSet
            or type(series) is TestResult
            or type(series) is FitResult
            or type(series) is SimulationResult
        )
        plot: Optional[PlotSettings] = self.plotting_tab.get_plot()
        if plot is None:
            return
        if state:
            plot.add_series(series)
        else:
            plot.remove_series(series.uuid)
        self.update_active_plot_series()
        self.update_plots()
        self.update_state_history()

    def edit_plot_series_theme(
        self,
        sender: int,
        app_data: None,
        series: Union[DataSet, TestResult, FitResult, SimulationResult],
    ):
        assert (
            type(series) is DataSet
            or type(series) is TestResult
            or type(series) is FitResult
            or type(series) is SimulationResult
        )
        plot: Optional[PlotSettings] = self.plotting_tab.get_plot()
        if plot is None:
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
            self.update_active_plot_series()
            self.update_state_history()

        uuid: str = series.uuid
        marker_lookup: Dict[int, str] = {v: k for k, v in themes.PLOT_MARKERS.items()}
        color: List[float] = plot.get_series_color(uuid)
        marker: int = plot.get_series_marker(uuid)
        show_line: bool = plot.get_series_line(uuid)

        def hash_state() -> str:
            return f"{','.join(map(str, color))};{str(marker)};{str(show_line)}"

        states.extend([hash_state(), hash_state()])

        def update_color(sender: int, new_color: List[float]):
            nonlocal states
            nonlocal color
            new_color = list(map(lambda _: _ * 255, new_color))
            color = new_color[:]
            plot.set_series_color(uuid, new_color)  # type: ignore
            states[1] = hash_state()

        def update_marker(sender: int, label: str):
            nonlocal states
            nonlocal marker
            marker = themes.PLOT_MARKERS.get(label, -1)
            plot.set_series_marker(uuid, marker)  # type: ignore
            self.update_plots()
            states[1] = hash_state()

        def update_line(sender: int, state: bool):
            nonlocal states
            nonlocal show_line
            show_line = state
            plot.set_series_line(uuid, state)  # type: ignore
            self.update_plots()
            states[1] = hash_state()

        x: int
        y: int
        w: int
        h: int
        x, y, w, h = window_pos_dims(200, 100)
        x, y = dpg.get_mouse_pos()
        y += 190
        with dpg.window(
            label="Edit appearance",
            modal=True,
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
                    callback=update_color,
                )
            with dpg.group(horizontal=True):
                dpg.add_text("Marker")
                dpg.add_combo(
                    items=["None"] + list(themes.PLOT_MARKERS.keys()),
                    default_value=marker_lookup.get(marker, "None"),
                    width=-1,
                    callback=update_marker,
                )
            with dpg.group(horizontal=True):
                dpg.add_text("  Line")
                dpg.add_checkbox(
                    default_value=plot.get_series_line(uuid),
                    callback=update_line,
                )

        with dpg.handler_registry(tag=handler):
            dpg.add_key_release_handler(
                key=dpg.mvKey_Escape,
                callback=accept_plot_series_theme,
            )
        self.modal_window = window

    def update_plot_series_label(self, sender: int, label: str, uuid: str):
        plot: Optional[PlotSettings] = self.plotting_tab.get_plot()
        if plot is None:
            return
        plot.set_series_label(uuid, label)
        self.update_plots()
        self.update_state_history()

    def change_plot_series_order(
        self, sender: int, app_data: None, user_data: Tuple[str, int]
    ):
        uuid: str
        step: int
        uuid, step = user_data
        plot: Optional[PlotSettings] = self.plotting_tab.get_plot()
        if plot is None:
            return
        elif uuid not in plot.series_order:
            return
        index: int = plot.series_order.index(uuid)
        if index <= 0 and step < 0:
            return
        elif index >= len(plot.series_order) - 1 and step > 0:
            return
        plot.series_order.pop(index)
        index += step
        plot.series_order.insert(index, uuid)
        self.update_active_plot_series()
        self.update_plots()
        self.update_state_history()

    def copy_plot_csv(self):
        data: dict = self.plotting_tab.get_data()
        if len(data) == 0:
            dpg.set_clipboard_text("")
            return
        lengths: Set[int] = set(map(len, data.values()))
        max_len: int = max(lengths)
        if max_len == 0:
            dpg.set_clipboard_text("")
            return
        elif len(lengths) > 1:
            label: str
            for label in data.keys():
                data[label] = pad(
                    data[label],
                    (
                        0,
                        max_len - len(data[label]),
                    ),
                    constant_values=None,
                )
        dpg.set_clipboard_text(DataFrame.from_dict(data).to_csv(index=False))


if __name__ == "__main__":
    dpg.create_context()
    dpg.create_viewport(title="Project")
    dpg.setup_dearpygui()
    dpg.show_viewport()
    window: int
    with dpg.window() as window:
        with dpg.tab_bar():
            Project()
    dpg.set_primary_window(window, True)
    dpg.start_dearpygui()
    dpg.destroy_context()
