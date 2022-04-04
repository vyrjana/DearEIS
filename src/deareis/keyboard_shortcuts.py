# Copyright 2022 DearEIS developers
# DearEIS is licensed under the GPLv3 or later (https://www.gnu.org/licenses/gpl-3.0.html).
# The licenses of DearEIS' dependencies and/or sources of portions of code are included in
# the LICENSES folder.

import dearpygui.dearpygui as dpg
from typing import List, Optional, Tuple
from traceback import format_exc
from pyimpspec import DataSet
from pyimpspec.circuit.parser import (
    ParsingError,
    ConnectionWithoutElements,
    DuplicateParameterDefinition,
    ExpectedNumericValue,
    ExpectedParameterIdentifier,
    InsufficientElementsInParallelConnection,
    InsufficientTokens,
    InvalidElementSymbol,
    InvalidParameterDefinition,
    InvalidParameterLowerLimit,
    InvalidParameterUpperLimit,
    TooManyParameterDefinitions,
    UnexpectedToken,
)
import pyimpspec
from deareis.data import (
    TestResult,
    TestSettings,
    FitResult,
    FitSettings,
    SimulationResult,
    SimulationSettings,
    PlotSettings,
    plot_type_to_label,
)
from deareis.plot import ResidualsPlot
from deareis.project.datasets import DataSetsTab
from deareis.project.fitting import FittingTab
from deareis.project.kramers_kronig import KramersKronigTab
from deareis.project.simulation import SimulationTab
from deareis.project.plotting import PlottingTab


def go_to_top_tab(
    program: "Program", index: Optional[int] = None, step: Optional[int] = None
):
    assert type(index) is int or index is None
    assert type(step) is int or step is None
    project: "Project"
    if index is not None:
        try:
            project = program.projects[index]
        except IndexError:
            return
        dpg.set_value(program.tab_bar, project.tab)
        project.resize()
    elif step is not None:
        tags: List[int] = [program.home_tab] + list(
            map(lambda _: _.tab, program.projects)
        )
        if len(tags) < 2:
            return
        index = (tags.index(dpg.get_value(program.tab_bar)) + step) % len(tags)
        dpg.set_value(program.tab_bar, tags[index])
        if index == 0:
            return
        program.projects[index - 1].resize()


def go_to_home_tab(program: "Program"):
    dpg.set_value(program.tab_bar, program.home_tab)


def go_to_project_tab(
    project: "Project", index: Optional[int] = None, step: Optional[int] = None
):
    assert type(index) is int or index is None
    assert type(step) is int or step is None
    tabs = [
        project.overview_tab,
        project.datasets_tab,
        project.kramers_kronig_tab,
        project.fitting_tab,
        project.simulation_tab,
        project.plotting_tab,
    ]
    tags = list(map(lambda _: _.tab, tabs))
    if step is not None:
        index = (tags.index(dpg.get_value(project.tab_bar)) + step) % len(tags)
    elif index is None:
        return
    try:
        dpg.set_value(project.tab_bar, tags[index])
    except IndexError:
        return
    if index == 0:
        return
    tabs[index].resize()


def go_to_dataset(
    project: "Project", index: Optional[int] = None, step: Optional[int] = None
):
    assert type(index) is int or index is None
    assert type(step) is int or step is None
    if project.overview_tab.is_visible():
        return
    labels: List[str] = list(map(lambda _: _.get_label(), project.datasets))
    if len(labels) == 0:
        return
    label: str = ""
    in_simulation: bool = project.simulation_tab.is_visible()
    if index is None:
        assert step is not None
        if in_simulation:
            label = dpg.get_value(project.simulation_tab.dataset_combo)
            if label == "None":
                if step >= 0:
                    label = labels[0]
                else:
                    label = labels[-1]
            else:
                index = labels.index(label) + step
                if index >= 0 and index < len(labels):
                    label = labels[index]
                else:
                    label = ""
        else:
            label = dpg.get_value(project.datasets_tab.dataset_combo)
            try:
                index = labels.index(label)
            except ValueError:
                return
            label = labels[(index + step) % len(labels)]
    else:
        try:
            label = labels[index]
        except IndexError:
            label = ""
    if in_simulation:
        project.select_simulation_dataset(label)
    else:
        project.select_dataset(label)


def go_to_plot(project: "Project", step: int):
    assert type(step) is int and step != 0
    if len(project.plots) < 2:
        return
    index: int = project.plots.index(project.plotting_tab.get_plot())
    project.select_plot(project.plots[(index + step) % len(project.plots)].get_label())


def go_to_plot_type(project: "Project", step: int):
    assert type(step) is int and step != 0
    if len(project.plots) == 0:
        return
    index: int = list(plot_type_to_label.keys()).index(
        project.plotting_tab.get_plot_type()
    )
    labels: List[str] = list(plot_type_to_label.values())
    project.select_plot_type(labels[(index + step) % len(labels)])


def go_to_result(
    project: "Project", index: Optional[int] = None, step: Optional[int] = None
):
    assert type(index) is int or index is None
    assert type(step) is int or step is None
    if project.overview_tab.is_visible() or project.datasets_tab.is_visible():
        return
    data: Optional[DataSet]
    in_simulation: bool = project.simulation_tab.is_visible()
    if in_simulation:
        data = project.find_dataset(dpg.get_value(project.simulation_tab.dataset_combo))
        if len(project.simulations) < 2:
            return
        simulation: Optional[SimulationResult]
        simulation = project.find_simulation(
            dpg.get_value(project.simulation_tab.result_combo)
        )
        if simulation is None:
            return
        elif simulation not in project.simulations:
            return
        index = (project.simulations.index(simulation) + step) % len(
            project.simulations
        )
        project.simulation_tab.select_result(data, project.simulations[index])
        return
    else:
        data = project.get_dataset()
        if data is None:
            return
        if project.kramers_kronig_tab.is_visible():
            tests: List[TestResult] = project.tests[data.uuid]
            if len(tests) < 2:
                return
            test: Optional[TestResult] = project.get_test(data, "")
            if test is None:
                return
            elif test not in tests:
                return
            assert step is not None
            index = (tests.index(test) + step) % len(tests)
            project.select_test_result(result=tests[index])
            return
        elif project.fitting_tab.is_visible():
            fits: List[FitResult] = project.fits[data.uuid]
            if len(fits) < 2:
                return
            fit: Optional[FitResult] = project.get_fit(data, "")
            if fit is None:
                return
            elif fit not in fits:
                return
            assert step is not None
            index = (fits.index(fit) + step) % len(fits)
            project.select_fit_result(result=fits[index])
            return
        else:
            return


def _is_input_active(parent: int) -> bool:
    assert type(parent) is int
    for slot, children in dpg.get_item_children(parent).items():
        for item in children:
            if dpg.is_item_container(item):
                if _is_input_active(item):
                    return True
            elif "::mvInput" in dpg.get_item_type(item):
                if dpg.is_item_active(item):
                    return True
    return False


def undo(project: "Project"):
    if (
        _is_input_active(project.overview_tab.tab)
        or _is_input_active(project.datasets_tab.tab)
        or _is_input_active(project.kramers_kronig_tab.tab)
        or _is_input_active(project.fitting_tab.tab)
        or _is_input_active(project.simulation_tab.tab)
    ):
        return
    project.undo()


def redo(project: "Project"):
    if (
        _is_input_active(project.overview_tab.tab)
        or _is_input_active(project.datasets_tab.tab)
        or _is_input_active(project.kramers_kronig_tab.tab)
        or _is_input_active(project.fitting_tab.tab)
        or _is_input_active(project.simulation_tab.tab)
    ):
        return
    project.redo()


def save(project: "Project", save_as: bool = False):
    assert type(save_as) is bool
    project.save(save_as)


def close(project: "Project"):
    project.close()


def show_plot(plot: "Plot", project: "Project"):
    if type(plot) is ResidualsPlot:
        plot.show_modal_window()
        return
    plot.show_modal_window(
        not (
            plot == project.datasets_tab.nyquist_plot
            or plot == project.datasets_tab.bode_plot
        )
    )


def copy_plot_data(plot: "Plot"):
    plot.copy_data()


def apply_settings(project: "Project", Class):
    if Class is TestSettings:
        project.apply_test_settings(
            dpg.get_item_user_data(project.kramers_kronig_tab.apply_settings_button)
        )
    elif Class is FitSettings:
        project.apply_fit_settings(
            dpg.get_item_user_data(project.fitting_tab.apply_settings_button)
        )
    elif Class is SimulationSettings:
        project.apply_simulation_settings(
            dpg.get_item_user_data(project.simulation_tab.apply_settings_button)
        )
    else:
        raise Exception(f"Unsupported class: {Class}")


def copy_output(tab):
    if not (type(tab) is FittingTab or type(tab) is SimulationTab):
        raise Exception(f"Unsupported class: {type(tab)}")
    dpg.get_item_callback(tab.copy_output_button)(
        tab.copy_output_button,
        None,
        dpg.get_item_user_data(tab.copy_output_button),
    )


def show_circuit_editor(tab):
    if type(tab) is FittingTab:
        dpg.get_item_callback(tab.editor_button)()
    elif type(tab) is SimulationTab:
        dpg.get_item_callback(tab.editor_button)()
    else:
        raise Exception(f"Unsupported class: {type(tab)}")


def subtract_impedance(project: "Project"):
    dpg.get_item_callback(project.datasets_tab.subtract_impedance_button)()


def toggle_points(project: "Project"):
    dpg.get_item_callback(project.datasets_tab.toggle_points_button)()


def copy_mask(project: "Project"):
    dpg.get_item_callback(project.datasets_tab.copy_mask_button)()


def average_datasets(project: "Project"):
    dpg.get_item_callback(project.datasets_tab.average_button)()


def remove(project: "Project", Class):
    if Class is DataSet:
        project.remove_dataset()
    elif Class is TestResult:
        project.remove_test(
            dpg.get_item_user_data(project.kramers_kronig_tab.delete_result_button)
        )
    elif Class is FitResult:
        project.remove_fit(
            dpg.get_item_user_data(project.fitting_tab.delete_result_button)
        )
    elif Class is SimulationResult:
        project.remove_simulation(
            dpg.get_item_user_data(project.simulation_tab.delete_result_button)
        )
    elif Class is PlotSettings:
        project.remove_plot()
    else:
        raise Exception(f"Unsupported class: {Class}")


def perform_action(tab):
    if type(tab) is DataSetsTab:
        dpg.get_item_callback(tab.load_button)()
    elif type(tab) is KramersKronigTab:
        dpg.get_item_callback(tab.perform_test_button)()
    elif type(tab) is FittingTab:
        dpg.get_item_callback(tab.perform_fit_button)()
    elif type(tab) is SimulationTab:
        dpg.get_item_callback(tab.perform_sim_button)()
    elif type(tab) is PlottingTab:
        dpg.get_item_callback(tab.new_button)()
    else:
        raise Exception(f"Unsupported class: {type(tab)}")


def cdc_hints(item: int, pos: Tuple[int, int]):
    assert type(item) is int
    assert (
        type(pos) is tuple and len(pos) == 2 and all(map(lambda _: type(_) is int, pos))
    )
    cdc: str = dpg.get_value(item)
    suggestions: List[str] = []
    suggestions.extend(
        map(lambda _: _.get_description(), pyimpspec.get_elements().values())
    )
    suggestions.extend(
        [
            "[]: Series connection",
            "(): Parallel connection",
        ]
    )
    try:
        pyimpspec.string_to_circuit(cdc)
    except (ExpectedParameterIdentifier, InvalidParameterDefinition) as e:
        suggestions = [
            f"ERROR: {str(e)}",
            e.element.get_extended_description(),
        ]
    except (
        DuplicateParameterDefinition,
        ExpectedNumericValue,
        # InsufficientTokens,
        UnexpectedToken,
        InvalidParameterLowerLimit,
        InvalidParameterUpperLimit,
    ) as e:
        suggestions = [f"ERROR: {str(e)}"]
    except ParsingError as e:
        # print(type(e))
        suggestions.insert(0, f"ERROR: {str(e)}")
        suggestions.insert(1, "")
    except Exception:
        print(format_exc())
    with dpg.window(popup=True, pos=pos, no_move=True):
        for string in suggestions:
            dpg.add_text(string, wrap=500)
