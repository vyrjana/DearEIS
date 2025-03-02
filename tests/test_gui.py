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

from json import dumps
from math import isclose
from os import (
    getcwd,
    remove,
    walk,
)
from os.path import (
    abspath,
    basename,
    dirname,
    exists,
    join,
    splitext,
)
from tempfile import gettempdir
from threading import Timer
from time import time
from traceback import format_exc
from typing import (
    Callable,
    Dict,
    List,
    Optional,
)
from pyimpspec.analysis.zhit.weights import (
    _WINDOW_FUNCTIONS,
    _initialize_window_functions,
)
from pyimpspec import (
    get_elements,
    parse_cdc,
)
import dearpygui.dearpygui as dpg
from deareis.utility import calculate_window_position_dimensions
import deareis.signals as signals
from deareis.signals import Signal
from deareis.state import STATE
from deareis.enums import (
    Action,
    CNLSMethod,
    Context,
    CrossValidationMethod,
    DRTMethod,
    DRTMode,
    PlotType,
    RBFShape,
    RBFType,
    TRNNLSLambdaMethod,
    KramersKronigTest,
    KramersKronigMode,
    KramersKronigRepresentation,
    Weight,
    ZHITInterpolation,
    ZHITRepresentation,
    ZHITSmoothing,
    ZHITWindow,
    label_to_drt_output,
    label_to_fit_sim_output,
    value_to_zhit_window,
)
from deareis.gui.settings import refresh_user_defined_elements
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
    KramersKronigResult,
    KramersKronigSettings,
    KramersKronigSuggestionSettings,
    ZHITSettings,
)
from deareis.data.project import VERSION as LATEST_PROJECT_VERSION
from deareis.gui import ProjectTab


PARENT_FOLDER: str = dirname(__file__)
TMP_FOLDER: str = gettempdir()
TMP_PROJECT: str = join(TMP_FOLDER, "deareis_temporary_test_project.json")


START_TIME: float = 0.0


def sleep(delay):
    dpg.split_frame(delay=round(delay * 1000))


def selection_window():
    window = dpg.generate_uuid()

    def start_tests(function):
        signals.emit(Signal.UNBLOCK_KEYBINDINGS)
        sleep(0.2)
        dpg.delete_item(window)
        sleep(0.2)
        global START_TIME
        START_TIME = time()
        Timer(1.0, function).start()
        # function()

    options = {
        "Overlay": test_overlay,
        "Ancillary windows": test_ancillary_windows,
        "User-defined elements": test_user_defined_elements,
        "Project versions": test_project_versions,
        "Project": test_project,
    }
    x, y, w, h = calculate_window_position_dimensions(
        400, len(options) * 24 + 2 * 8 + len(options) * 2
    )
    with dpg.window(
        label="Automated tests",
        modal=True,
        pos=(x, y),
        width=w,
        height=h,
        no_resize=True,
        tag=window,
    ):
        for label, function in options.items():
            dpg.add_button(
                label=label,
                callback=lambda s, a, u: start_tests(u),
                user_data=function,
                width=-1,
            )
    signals.emit(
        Signal.BLOCK_KEYBINDINGS,
        window=window,
        window_object=None,
    )


def finish_tests():
    project: Optional[Project] = STATE.get_active_project()
    if project is not None and project.get_label() == "Test project":
        path: str = project.get_path()
        assert path == TMP_PROJECT, (path, TMP_PROJECT)
        signals.emit(Signal.CLOSE_PROJECT, force=True)
    else:
        signals.emit(Signal.CLOSE_PROJECT, force=True)
    print(f"\nFinished in {time() - START_TIME:.2f} s")
    sleep(1.0)
    selection_window()


def next_step(next_func: Callable = finish_tests, delay: float = 1.0) -> Callable:
    def outer_wrapper(func: Callable) -> Callable:
        def inner_wrapper():
            func()
            if delay > 0.0:
                Timer(delay, next_func).start()
            else:
                next_func()

        return inner_wrapper

    return outer_wrapper


def test_undo_redo():
    def count_results(project) -> int:
        counter: int = 0
        for data in project.get_data_sets():
            counter += len(project.get_tests(data))
            counter += len(project.get_zhits(data))
            counter += len(project.get_drts(data))
            counter += len(project.get_fits(data))
        counter += len(project.get_simulations())
        counter += len(project.get_plots())
        return counter

    project: Optional[Project] = STATE.get_active_project()
    project_tab: Optional[ProjectTab] = STATE.get_active_project_tab()
    num_undo_steps: int = 0
    num_results: int = count_results(STATE.get_active_project())
    expected_final_state: str = dumps(STATE.get_active_project().to_dict(session=False))

    @next_step()
    def validate_redo():
        project = STATE.get_active_project()
        assert num_results == count_results(project)
        num_data_sets = len(project.get_data_sets())
        assert num_data_sets > 0
        assert len(project.get_all_tests()) == num_data_sets
        assert len(project.get_all_zhits()) == num_data_sets
        assert len(project.get_all_drts()) == num_data_sets
        assert len(project.get_all_fits()) == num_data_sets
        assert len(project.get_simulations()) > 0
        assert len(project.get_plots()) > 1
        final_state: str = dumps(project.to_dict(session=False))
        assert final_state == expected_final_state

    @next_step(validate_redo)
    def redo():
        nonlocal num_undo_steps
        while num_undo_steps > 0:
            signals.emit(Signal.REDO_PROJECT_ACTION)
            sleep(1.0)
            num_undo_steps -= 1
            print(f"  - Redo ({num_undo_steps})")

    @next_step(redo)
    def validate_undo():
        num_data_sets = len(project.get_data_sets())
        assert num_data_sets == 0
        assert len(project.get_all_tests()) == num_data_sets
        assert len(project.get_all_zhits()) == num_data_sets
        assert len(project.get_all_drts()) == num_data_sets
        assert len(project.get_all_fits()) == num_data_sets
        assert len(project.get_simulations()) == 0
        assert len(project.get_plots()) == 1

    @next_step(validate_undo)
    def undo():
        nonlocal num_undo_steps
        while STATE.get_active_project().get_label() == "Test project":
            signals.emit(Signal.UNDO_PROJECT_ACTION)
            sleep(1.0)
            num_undo_steps += 1
            print(f"  - Undo ({num_undo_steps})")

    @next_step(undo)
    def switch_tab():
        STATE.keybinding_handler.perform_action(
            action=Action.SELECT_OVERVIEW_TAB,
            context=Context.PROJECT,
            project=project,
            project_tab=project_tab,
        )

    print("\n- Undo/redo")
    switch_tab()


def test_plotting_tab():
    project: Optional[Project] = STATE.get_active_project()
    project_tab: Optional[ProjectTab] = STATE.get_active_project_tab()
    perform_action = lambda action: STATE.keybinding_handler.perform_action(
        action=action,
        context=Context.PLOTTING_TAB,
        project=project,
        project_tab=project_tab,
    )

    @next_step(test_undo_redo)
    def result_palette():
        print("  - Result palette")
        signals.emit(Signal.SHOW_RESULT_PALETTE)
        sleep(0.5)
        STATE.active_modal_window_object.hide()

    @next_step(result_palette)
    def validate_delete_plot():
        assert STATE.is_project_dirty(project) is True
        assert len(project.get_plots()) == 2
        settings = project_tab.get_active_plot()
        assert settings.get_num_series() > 0
        signals.emit(Signal.SAVE_PROJECT)

    @next_step(validate_delete_plot)
    def delete_plot():
        print("  - Delete plot")
        perform_action(action=Action.DELETE_RESULT)

    @next_step(delete_plot)
    def validate_copy_plot_appearance():
        assert STATE.is_project_dirty(project) is True
        assert STATE.active_modal_window_object is not None
        STATE.active_modal_window_object.accept()

    @next_step(validate_copy_plot_appearance)
    def copy_plot_appearance():
        print("  - Copy plot appearance")
        assert STATE.is_project_dirty(project) is False
        perform_action(action=Action.SELECT_ALL_PLOT_SERIES)
        sleep(0.5)
        perform_action(action=Action.COPY_PLOT_APPEARANCE)

    @next_step(copy_plot_appearance)
    def validate_new_plot():
        assert STATE.is_project_dirty(project) is True
        assert len(project.get_plots()) == 3
        settings = project_tab.get_active_plot()
        assert settings.get_num_series() == 0
        signals.emit(Signal.SAVE_PROJECT)

    @next_step(validate_new_plot)
    def new_plot():
        print("  - New plot")
        perform_action(action=Action.PERFORM_ACTION)

    @next_step(new_plot)
    def cycle_plot_types():
        print("  - Cycle plot types, preview export, and copy as CSV")
        settings = project_tab.get_active_plot()
        seen_types = []
        while True:
            perform_action(action=Action.EXPORT_PLOT)
            sleep(0.5)
            assert STATE.active_modal_window_object is not None
            STATE.active_modal_window_object.close()
            sleep(0.5)
            perform_action(action=Action.COPY_PLOT_DATA)
            sleep(0.5)
            text = dpg.get_clipboard_text().strip()
            assert text != ""
            perform_action(action=Action.NEXT_PLOT_TAB)
            sleep(0.5)
            seen_types.append(settings.get_type())
            if len(set(seen_types)) < len(seen_types):
                break
        assert len(set(seen_types)) == len(PlotType), (set(seen_types), PlotType)

    @next_step(cycle_plot_types)
    def cycle_plots():
        print("  - Cycle plots")
        perform_action(action=Action.NEXT_PRIMARY_RESULT)
        sleep(0.5)
        perform_action(action=Action.NEXT_PRIMARY_RESULT)
        sleep(0.5)
        perform_action(action=Action.PREVIOUS_PRIMARY_RESULT)

    @next_step(cycle_plots)
    def validate_unselect_all():
        assert STATE.is_project_dirty(project) is True
        assert len(project.get_plots()) == 2
        settings = project_tab.get_active_plot()
        assert settings.get_num_series() == 0
        signals.emit(Signal.SAVE_PROJECT)

    @next_step(validate_unselect_all)
    def unselect_all():
        print("  - Unselect all")
        assert STATE.is_project_dirty(project) is False
        perform_action(action=Action.UNSELECT_ALL_PLOT_SERIES)

    @next_step(unselect_all)
    def validate_duplicate_plot():
        assert STATE.is_project_dirty(project) is True
        assert len(project.get_plots()) == 2
        signals.emit(Signal.SAVE_PROJECT)

    @next_step(validate_duplicate_plot)
    def duplicate_plot():
        print("  - Duplicate plot")
        assert STATE.is_project_dirty(project) is False
        perform_action(action=Action.DUPLICATE_PLOT)

    @next_step(duplicate_plot)
    def validate_select_all():
        assert STATE.is_project_dirty(project) is True
        assert len(project.get_plots()) == 1
        settings = project_tab.get_active_plot()
        assert settings.get_num_series() > 0
        signals.emit(Signal.SAVE_PROJECT)

    @next_step(validate_select_all)
    def select_all():
        print("  - Select all")
        assert STATE.is_project_dirty(project) is False
        perform_action(action=Action.SELECT_ALL_PLOT_SERIES)

    @next_step(select_all)
    def expand_collapse_sidebar():
        print("  - Expand/collapse sidebar")
        assert STATE.is_project_dirty(project) is False
        perform_action(action=Action.EXPAND_COLLAPSE_SIDEBAR)
        sleep(0.5)
        perform_action(action=Action.EXPAND_COLLAPSE_SIDEBAR)

    @next_step(expand_collapse_sidebar)
    def switch_tab():
        STATE.keybinding_handler.perform_action(
            action=Action.SELECT_PLOTTING_TAB,
            context=Context.PROJECT,
            project=project,
            project_tab=project_tab,
        )

    print("\n- Plotting tab")
    switch_tab()
    sleep(0.5)
    context: Context = project_tab.get_active_context()
    assert context == Context.PLOTTING_TAB, context


def test_simulation_tab():
    project: Optional[Project] = STATE.get_active_project()
    project_tab: Optional[ProjectTab] = STATE.get_active_project_tab()
    perform_action = lambda action: STATE.keybinding_handler.perform_action(
        action=action,
        context=Context.SIMULATION_TAB,
        project=project,
        project_tab=project_tab,
    )
    outputs: List[str] = list(
        [_ for _ in label_to_fit_sim_output.keys() if "statistics" not in _]
    )

    @next_step(test_plotting_tab)
    def result_palette():
        print("  - Result palette")
        signals.emit(Signal.SHOW_RESULT_PALETTE)
        sleep(0.5)
        STATE.active_modal_window_object.hide()

    @next_step(result_palette)
    def data_set_palette():
        print("  - Data set palette")
        signals.emit(Signal.SHOW_DATA_SET_PALETTE)
        sleep(0.5)
        STATE.active_modal_window_object.hide()

    @next_step(data_set_palette)
    def validate_copy_sympy_expression_with_values():
        assert STATE.is_project_dirty(project) is False
        text = dpg.get_clipboard_text().strip()
        assert text.startswith(
            """expr = sympify("R_0 + 1/(2*I*pi*C_2*f + 1/R_1)")
C_2, R_0, R_1, f = sorted(expr.free_symbols, key=str)
parameters = {"""
        ), text
        assert len(outputs) == 0, outputs

    @next_step(validate_copy_sympy_expression_with_values)
    def copy_sympy_expression_with_values():
        output = outputs.pop(0)
        print(f"  - Copy: {output}")
        project_tab.simulation_tab.output_combo.set_label(output)
        perform_action(action=Action.COPY_OUTPUT)

    @next_step(copy_sympy_expression_with_values)
    def validate_copy_sympy_expression():
        assert STATE.is_project_dirty(project) is False
        text = dpg.get_clipboard_text().strip()
        assert text == "R_0 + 1/(2*I*pi*C_2*f + 1/R_1)", text

    @next_step(validate_copy_sympy_expression)
    def copy_sympy_expression():
        output = outputs.pop(0)
        print(f"  - Copy: {output}")
        project_tab.simulation_tab.output_combo.set_label(output)
        perform_action(action=Action.COPY_OUTPUT)

    @next_step(copy_sympy_expression)
    def validate_copy_svg_circuit_without_labels():
        assert STATE.is_project_dirty(project) is False
        text = dpg.get_clipboard_text().strip()
        assert "<svg xmlns:xlink" in text and r"$R_{\rm 1}$" not in text, text

    @next_step(validate_copy_svg_circuit_without_labels)
    def copy_svg_circuit_without_labels():
        output = outputs.pop(0)
        print(f"  - Copy: {output}")
        project_tab.simulation_tab.output_combo.set_label(output)
        perform_action(action=Action.COPY_OUTPUT)

    @next_step(copy_svg_circuit_without_labels)
    def validate_copy_svg_circuit():
        assert STATE.is_project_dirty(project) is False
        text = dpg.get_clipboard_text().strip()
        assert "<svg xmlns:xlink" in text, text

    @next_step(validate_copy_svg_circuit)
    def copy_svg_circuit():
        output = outputs.pop(0)
        print(f"  - Copy: {output}")
        project_tab.simulation_tab.output_combo.set_label(output)
        perform_action(action=Action.COPY_OUTPUT)

    @next_step(copy_svg_circuit)
    def validate_copy_markdown_parameters():
        assert STATE.is_project_dirty(project) is False
        text = dpg.get_clipboard_text().strip()
        assert text.startswith(
            """| Element   | Parameter   |   Value | Unit   |
|:----------|:------------|--------:|:-------|"""
        ), text

    @next_step(validate_copy_markdown_parameters)
    def copy_markdown_parameters():
        output = outputs.pop(0)
        print(f"  - Copy: {output}")
        project_tab.simulation_tab.output_combo.set_label(output)
        perform_action(action=Action.COPY_OUTPUT)

    @next_step(copy_markdown_parameters)
    def validate_copy_latex_parameters():
        assert STATE.is_project_dirty(project) is False
        text = dpg.get_clipboard_text().strip()
        assert text.startswith(
            r"""\begin{tabular}{llrl}
\toprule
Element & Parameter & Value & Unit \\
\midrule"""
        )
        assert text.endswith(
            r"""\bottomrule
\end{tabular}"""
        ), text

    @next_step(validate_copy_latex_parameters)
    def copy_latex_parameters():
        output = outputs.pop(0)
        print(f"  - Copy: {output}")
        project_tab.simulation_tab.output_combo.set_label(output)
        perform_action(action=Action.COPY_OUTPUT)

    @next_step(copy_latex_parameters)
    def validate_copy_latex_expression():
        assert STATE.is_project_dirty(project) is False
        text = dpg.get_clipboard_text().strip()
        assert text == r"R_{0} + \frac{1}{2 i \pi C_{2} f + \frac{1}{R_{1}}}", text

    @next_step(validate_copy_latex_expression)
    def copy_latex_expression():
        output = outputs.pop(0)
        print(f"  - Copy: {output}")
        project_tab.simulation_tab.output_combo.set_label(output)
        perform_action(action=Action.COPY_OUTPUT)

    @next_step(copy_latex_expression)
    def validate_copy_latex_circuit():
        assert STATE.is_project_dirty(project) is False
        text = dpg.get_clipboard_text().strip()
        assert text.startswith(r"\begin{circuitikz}") and text.endswith(
            r"\end{circuitikz}"
        ), text

    @next_step(validate_copy_latex_circuit)
    def copy_latex_circuit():
        output = outputs.pop(0)
        print(f"  - Copy: {output}")
        project_tab.simulation_tab.output_combo.set_label(output)
        perform_action(action=Action.COPY_OUTPUT)

    @next_step(copy_latex_circuit)
    def validate_copy_json_parameters():
        assert STATE.is_project_dirty(project) is False
        text = dpg.get_clipboard_text().strip()
        assert text.startswith('{"Element":{"0":"') and text.endswith('"}}'), text

    @next_step(validate_copy_json_parameters)
    def copy_json_parameters():
        output = outputs.pop(0)
        print(f"  - Copy: {output}")
        project_tab.simulation_tab.output_combo.set_label(output)
        perform_action(action=Action.COPY_OUTPUT)

    @next_step(copy_json_parameters)
    def validate_copy_csv_parameters():
        assert STATE.is_project_dirty(project) is False
        text = dpg.get_clipboard_text().strip()
        assert text.startswith("Element,Parameter,Value,Unit"), text

    @next_step(validate_copy_csv_parameters)
    def copy_csv_parameters():
        output = outputs.pop(0)
        print(f"  - Copy: {output}")
        project_tab.simulation_tab.output_combo.set_label(output)
        perform_action(action=Action.COPY_OUTPUT)

    @next_step(copy_csv_parameters)
    def validate_copy_csv_impedance():
        assert STATE.is_project_dirty(project) is False
        text = dpg.get_clipboard_text().strip()
        assert text.startswith("f (Hz),Re(Z) (ohm) - Sim.,Im(Z) (ohm) - Sim."), text

    @next_step(validate_copy_csv_impedance)
    def copy_csv_impedance():
        output = outputs.pop(0)
        print(f"  - Copy: {output}")
        project_tab.simulation_tab.output_combo.set_label(output)
        perform_action(action=Action.COPY_OUTPUT)

    @next_step(copy_csv_impedance)
    def validate_copy_extended_cdc():
        assert STATE.is_project_dirty(project) is False
        text = dpg.get_clipboard_text().strip()
        assert text.startswith("[R{R=") and text.endswith("})]"), text

    @next_step(validate_copy_extended_cdc)
    def copy_extended_cdc():
        output = outputs.pop(0)
        print(f"  - Copy: {output}")
        project_tab.simulation_tab.output_combo.set_label(output)
        perform_action(action=Action.COPY_OUTPUT)

    @next_step(copy_extended_cdc)
    def validate_copy_basic_cdc():
        assert STATE.is_project_dirty(project) is False
        text = dpg.get_clipboard_text().strip()
        assert text == "[R(RC)]", text

    @next_step(validate_copy_basic_cdc)
    def copy_basic_cdc():
        output = outputs.pop(0)
        print(f"  - Copy: {output}")
        project_tab.simulation_tab.output_combo.set_label(output)
        perform_action(action=Action.COPY_OUTPUT)

    @next_step(copy_basic_cdc)
    def validate_copy_bode():
        assert STATE.is_project_dirty(project) is False
        text = dpg.get_clipboard_text().strip()
        headers = text.split("\n")[0].strip()
        assert (
            headers
            == "f (Hz) - Data (scatter),Mod(Z) (ohm) - Data (scatter),-Phase(Z) (°) - Data (scatter),f (Hz) - Sim. (scatter),Mod(Z) (ohm) - Sim. (scatter),-Phase(Z) (°) - Sim. (scatter),f (Hz) - Sim. (line),Mod(Z) (ohm) - Sim. (line),-Phase(Z) (°) - Sim. (line)"
        ), headers

    @next_step(validate_copy_bode)
    def copy_bode():
        print("  - Copy Bode")
        assert STATE.is_project_dirty(project) is False
        perform_action(action=Action.COPY_BODE_DATA)

    @next_step(copy_bode)
    def validate_copy_nyquist():
        assert STATE.is_project_dirty(project) is False
        text = dpg.get_clipboard_text().strip()
        headers = text.split("\n")[0].strip()
        assert (
            headers
            == "Re(Z) (ohm) - Data (scatter),-Im(Z) (ohm) - Data (scatter),Re(Z) (ohm) - Sim. (scatter),-Im(Z) (ohm) - Sim. (scatter),Re(Z) (ohm) - Sim. (line),-Im(Z) (ohm) - Sim. (line)"
        ), headers

    @next_step(validate_copy_nyquist)
    def copy_nyquist():
        print("  - Copy Nyquist")
        assert STATE.is_project_dirty(project) is False
        perform_action(action=Action.COPY_NYQUIST_DATA)

    @next_step(copy_nyquist)
    def validate_enlarge_impedance():
        assert STATE.is_project_dirty(project) is False
        assert STATE.active_modal_window_object is not None
        STATE.active_modal_window_object.close()

    @next_step(validate_enlarge_impedance)
    def enlarge_impedance():
        print("  - Enlarge Real & Imag.")
        assert STATE.is_project_dirty(project) is False
        perform_action(action=Action.SHOW_ENLARGED_IMPEDANCE)

    @next_step(enlarge_impedance)
    def validate_enlarge_bode():
        assert STATE.is_project_dirty(project) is False
        assert STATE.active_modal_window_object is not None
        STATE.active_modal_window_object.close()

    @next_step(validate_enlarge_bode)
    def enlarge_bode():
        print("  - Enlarge Bode")
        assert STATE.is_project_dirty(project) is False
        perform_action(action=Action.SHOW_ENLARGED_BODE)

    @next_step(enlarge_bode)
    def validate_enlarge_nyquist():
        assert STATE.is_project_dirty(project) is False
        assert STATE.active_modal_window_object is not None
        STATE.active_modal_window_object.close()

    @next_step(validate_enlarge_nyquist)
    def enlarge_nyquist():
        print("  - Enlarge Nyquist")
        assert STATE.is_project_dirty(project) is False
        perform_action(action=Action.SHOW_ENLARGED_NYQUIST)

    @next_step(enlarge_nyquist)
    def validate_load_as_data_set():
        assert STATE.is_project_dirty(project) is True
        STATE.keybinding_handler.perform_action(
            action=Action.SELECT_DATA_SETS_TAB,
            context=Context.PROJECT,
            project=project,
            project_tab=project_tab,
        )
        sleep(1.0)
        assert len(project.get_data_sets()) == 3
        data = project_tab.get_active_data_set(context=Context.DATA_SETS_TAB)
        # If the following assertion fails, then it may be because the state
        # has not finished updating (e.g., the table in the GUI might be in
        # the process of being updated). Try increasing the amount of time
        # spent sleeping after switching tabs.
        assert data.get_label().startswith("R(RC)"), data.get_label()
        signals.emit(
            Signal.DELETE_DATA_SET,
            data=project_tab.get_active_data_set(),
        )
        signals.emit(Signal.SAVE_PROJECT)
        assert len(project.get_data_sets()) == 2
        STATE.keybinding_handler.perform_action(
            action=Action.SELECT_SIMULATION_TAB,
            context=Context.PROJECT,
            project=project,
            project_tab=project_tab,
        )

    @next_step(validate_load_as_data_set)
    def load_as_data_set():
        print("  - Load as data set")
        project_tab.start_loading_simulation_as_data_set()
        sleep(0.5)
        modal_window = STATE.active_modal_window_object
        modal_window.accept()
        sleep(0.5)

    @next_step(load_as_data_set)
    def validate_apply_settings():
        assert STATE.is_project_dirty(project) is False
        settings = project_tab.get_simulation_settings()
        assert parse_cdc(settings.cdc).to_string() == "[R(RC)]"
        assert isclose(settings.min_frequency, 1e-3, abs_tol=1e-6)
        assert isclose(settings.max_frequency, 1e3, abs_tol=1e-6)
        assert settings.num_per_decade == 20

    @next_step(validate_apply_settings)
    def apply_settings():
        print("  - Apply setting")
        assert STATE.is_project_dirty(project) is False
        signals.emit(
            Signal.APPLY_SIMULATION_SETTINGS,
            settings=project_tab.get_active_simulation().settings,
        )

    @next_step(apply_settings)
    def validate_delete_result():
        assert STATE.is_project_dirty(project) is True
        data = project_tab.get_active_data_set()
        assert len(project.get_simulations()) == 1
        signals.emit(Signal.SAVE_PROJECT)

    @next_step(validate_delete_result)
    def delete_result():
        print("  - Delete result")
        perform_action(action=Action.DELETE_RESULT)

    @next_step(delete_result)
    def cycle_results():
        print("  - Cycle results")
        perform_action(action=Action.NEXT_SECONDARY_RESULT)
        sleep(0.5)
        perform_action(action=Action.NEXT_SECONDARY_RESULT)
        sleep(0.5)
        perform_action(action=Action.NEXT_SECONDARY_RESULT)
        sleep(0.5)
        perform_action(action=Action.PREVIOUS_SECONDARY_RESULT)
        sleep(0.5)

    @next_step(cycle_results)
    def validate_perform_simulation():
        assert STATE.is_project_dirty(project) is True
        data = project_tab.get_active_data_set()
        assert len(project.get_simulations()) == 2
        signals.emit(Signal.SAVE_PROJECT)

    @next_step(validate_perform_simulation)
    def perform_simulation():
        print("  - Perform simulation")
        assert STATE.is_project_dirty(project) is False
        perform_action(action=Action.PERFORM_ACTION)
        sleep(0.5)
        signals.emit(
            Signal.APPLY_SIMULATION_SETTINGS,
            settings=SimulationSettings(
                cdc=parse_cdc("R(RL)").to_string(),
                min_frequency=1e-2,
                max_frequency=1e4,
                num_per_decade=15,
            ),
        )
        perform_action(action=Action.PERFORM_ACTION)

    @next_step(perform_simulation)
    def validate_circuit_editor():
        assert STATE.is_project_dirty(project) is False
        settings = project_tab.get_simulation_settings()
        assert parse_cdc(settings.cdc).to_string() == "[R(RC)]"

    @next_step(validate_circuit_editor)
    def circuit_editor():
        print("  - Circuit editor")
        assert STATE.is_project_dirty(project) is False
        signals.emit(
            Signal.APPLY_SIMULATION_SETTINGS,
            settings=SimulationSettings(
                cdc=parse_cdc("R(RC)").to_string(),
                min_frequency=1e-3,
                max_frequency=1e3,
                num_per_decade=20,
            ),
        )
        sleep(0.5)
        perform_action(action=Action.SHOW_CIRCUIT_EDITOR)
        sleep(0.5)
        editor = STATE.active_modal_window_object
        editor.node_clicked(editor.node_handler, (0, editor.parser.nodes[0].tag))
        sleep(0.5)
        editor.callback(dpg.get_item_user_data(editor.accept_button))

    @next_step(circuit_editor)
    def cycle_data_sets():
        print("  - Cycle data sets")
        perform_action(action=Action.NEXT_PRIMARY_RESULT)
        sleep(0.5)
        perform_action(action=Action.NEXT_PRIMARY_RESULT)
        sleep(0.5)
        perform_action(action=Action.NEXT_PRIMARY_RESULT)
        sleep(0.5)
        perform_action(action=Action.NEXT_PRIMARY_RESULT)
        sleep(0.5)
        perform_action(action=Action.PREVIOUS_PRIMARY_RESULT)

    @next_step(cycle_data_sets)
    def switch_tab():
        STATE.keybinding_handler.perform_action(
            action=Action.SELECT_SIMULATION_TAB,
            context=Context.PROJECT,
            project=project,
            project_tab=project_tab,
        )

    print("\n- Simulation tab")
    switch_tab()
    sleep(0.5)
    context: Context = project_tab.get_active_context()
    assert context == Context.SIMULATION_TAB, context


# TODO: Update tests
# - Automatic lambda (TR-NNLS and TR-RBF)
def test_drt_tab():
    project: Optional[Project] = STATE.get_active_project()
    project_tab: Optional[ProjectTab] = STATE.get_active_project_tab()
    perform_action = lambda action: STATE.keybinding_handler.perform_action(
        action=action,
        context=Context.DRT_TAB,
        project=project,
        project_tab=project_tab,
    )
    outputs: List[str] = list(label_to_drt_output.keys())

    @next_step(test_simulation_tab)
    def result_palette():
        print("  - Result palette")
        signals.emit(Signal.SHOW_RESULT_PALETTE)
        sleep(0.5)
        STATE.active_modal_window_object.hide()

    @next_step(result_palette)
    def data_set_palette():
        print("  - Data set palette")
        signals.emit(Signal.SHOW_DATA_SET_PALETTE)
        sleep(0.5)
        STATE.active_modal_window_object.hide()

    @next_step(data_set_palette)
    def validate_copy_markdown_scores():
        assert STATE.is_project_dirty(project) is False
        text = dpg.get_clipboard_text().strip()
        assert text.startswith(
            """| Score                   |   Real (%) |   Imag. (%) |
|:------------------------|-----------:|------------:|"""
        ), text
        assert len(outputs) == 0, outputs

    @next_step(validate_copy_markdown_scores)
    def copy_markdown_scores():
        output = outputs.pop(0)
        print(f"  - Copy: {output}")
        project_tab.drt_tab.output_combo.set_label(output)
        perform_action(action=Action.COPY_OUTPUT)

    @next_step(copy_markdown_scores)
    def validate_copy_latex_scores():
        assert STATE.is_project_dirty(project) is False
        text = dpg.get_clipboard_text().strip()
        assert text.startswith(
            r"""\begin{tabular}{lrr}
\toprule
Score & Real (\%) & Imag. (\%) \\"""
        ), text
        assert text.endswith(
            r"""\bottomrule
\end{tabular}"""
        ), text

    @next_step(validate_copy_latex_scores)
    def copy_latex_scores():
        output = outputs.pop(0)
        print(f"  - Copy: {output}")
        project_tab.drt_tab.output_combo.set_label(output)
        perform_action(action=Action.COPY_OUTPUT)

    @next_step(copy_latex_scores)
    def validate_copy_json_scores():
        assert STATE.is_project_dirty(project) is False
        text = dpg.get_clipboard_text().strip()
        assert text.startswith('{"Score":{"0":"'), text

    @next_step(validate_copy_json_scores)
    def copy_json_scores():
        output = outputs.pop(0)
        print(f"  - Copy: {output}")
        project_tab.drt_tab.output_combo.set_label(output)
        perform_action(action=Action.COPY_OUTPUT)

    @next_step(copy_json_scores)
    def validate_copy_csv_scores():
        assert STATE.is_project_dirty(project) is False
        text = dpg.get_clipboard_text().strip()
        assert text.startswith("Score,Real (%),Imag. (%)"), text

    @next_step(validate_copy_csv_scores)
    def copy_csv_scores():
        perform_action(action=Action.PREVIOUS_SECONDARY_RESULT)
        sleep(0.5)
        output = outputs.pop(0)
        print(f"  - Copy: {output}")
        project_tab.drt_tab.output_combo.set_label(output)
        perform_action(action=Action.COPY_OUTPUT)

    @next_step(copy_csv_scores)
    def validate_copy_complex():
        assert STATE.is_project_dirty(project) is False
        text = dpg.get_clipboard_text().strip()
        headers = text.split("\n")[0].strip()
        assert (
            headers
            == "f (Hz) - Data,Re(Z) (ohm) - Data,-Im(Z) (ohm) - Data,f (Hz) - Fit,Re(Z) (ohm) - Fit,-Im(Z) (ohm) - Fit"
        ), headers

    @next_step(validate_copy_complex)
    def copy_complex():
        print("  - Copy complex impedance")
        assert STATE.is_project_dirty(project) is False
        perform_action(action=Action.COPY_IMPEDANCE_DATA)

    @next_step(copy_complex)
    def validate_copy_drt():
        assert STATE.is_project_dirty(project) is False
        text = dpg.get_clipboard_text().strip()
        headers = text.split("\n")[0].strip()
        assert headers == "tau (s),gamma (ohm)", headers

    @next_step(validate_copy_drt)
    def copy_drt():
        print("  - Copy DRT")
        assert STATE.is_project_dirty(project) is False
        perform_action(action=Action.COPY_DRT_DATA)

    @next_step(copy_drt)
    def validate_copy_residuals():
        assert STATE.is_project_dirty(project) is False
        text = dpg.get_clipboard_text().strip()
        headers = text.split("\n")[0].strip()
        assert headers == "f (Hz),real_error (%),imag_error (%)", headers

    @next_step(validate_copy_residuals)
    def copy_residuals():
        print("  - Copy residuals")
        assert STATE.is_project_dirty(project) is False
        perform_action(action=Action.COPY_RESIDUALS_DATA)

    @next_step(copy_residuals)
    def validate_enlarge_impedance():
        assert STATE.is_project_dirty(project) is False
        assert STATE.active_modal_window_object is not None
        STATE.active_modal_window_object.close()

    @next_step(validate_enlarge_impedance)
    def enlarge_impedance():
        print("  - Enlarge Real & Imag.")
        assert STATE.is_project_dirty(project) is False
        perform_action(action=Action.SHOW_ENLARGED_IMPEDANCE)

    @next_step(enlarge_impedance)
    def validate_enlarge_bode():
        assert STATE.is_project_dirty(project) is False
        assert STATE.active_modal_window_object is not None
        STATE.active_modal_window_object.close()

    @next_step(validate_enlarge_bode)
    def enlarge_bode():
        print("  - Enlarge Bode")
        assert STATE.is_project_dirty(project) is False
        perform_action(action=Action.SHOW_ENLARGED_BODE)

    @next_step(enlarge_bode)
    def validate_enlarge_nyquist():
        assert STATE.is_project_dirty(project) is False
        assert STATE.active_modal_window_object is not None
        STATE.active_modal_window_object.close()

    @next_step(validate_enlarge_nyquist)
    def enlarge_nyquist():
        print("  - Enlarge Nyquist")
        assert STATE.is_project_dirty(project) is False
        perform_action(action=Action.SHOW_ENLARGED_NYQUIST)

    @next_step(enlarge_nyquist)
    def validate_enlarge_drt():
        assert STATE.is_project_dirty(project) is False
        assert STATE.active_modal_window_object is not None
        STATE.active_modal_window_object.close()

    @next_step(validate_enlarge_drt)
    def enlarge_drt():
        print("  - Enlarge DRT")
        assert STATE.is_project_dirty(project) is False
        perform_action(action=Action.SHOW_ENLARGED_DRT)

    @next_step(enlarge_drt)
    def validate_enlarge_residuals():
        assert STATE.is_project_dirty(project) is False
        assert STATE.active_modal_window_object is not None
        STATE.active_modal_window_object.close()

    @next_step(validate_enlarge_residuals)
    def enlarge_residuals():
        print("  - Enlarge residuals")
        assert STATE.is_project_dirty(project) is False
        perform_action(action=Action.SHOW_ENLARGED_RESIDUALS)

    @next_step(enlarge_residuals)
    def validate_apply_mask():
        assert STATE.is_project_dirty(project) is True
        data = project_tab.get_active_data_set()
        assert list(data.get_mask().values()).count(True) == 2
        signals.emit(Signal.SAVE_PROJECT)

    @next_step(validate_apply_mask)
    def apply_mask():
        print("  - Apply mask")
        assert STATE.is_project_dirty(project) is False
        data = project_tab.get_active_data_set()
        signals.emit(
            Signal.APPLY_DATA_SET_MASK,
            data=data,
            mask={},
        )
        sleep(0.5)
        signals.emit(
            Signal.APPLY_DATA_SET_MASK,
            data=data,
            mask=project_tab.get_active_drt().mask,
        )

    @next_step(apply_mask)
    def validate_apply_settings():
        assert STATE.is_project_dirty(project) is False
        settings = project_tab.get_drt_settings()
        assert settings.method == DRTMethod.TR_NNLS
        assert settings.mode == DRTMode.REAL
        assert isclose(settings.lambda_value, -1.0, abs_tol=1e-6)
        assert settings.rbf_type == RBFType.CAUCHY
        assert settings.derivative_order == 1
        assert settings.rbf_shape == RBFShape.FWHM
        assert isclose(settings.shape_coeff, 0.5, abs_tol=1e-6)
        assert settings.inductance is False
        assert settings.credible_intervals is False
        assert settings.timeout == 1
        assert settings.num_samples == 2000
        assert settings.num_attempts == 1
        assert isclose(settings.maximum_symmetry, 0.5, abs_tol=1e-6)
        assert isclose(settings.gaussian_width, 0.15, abs_tol=1e-6)
        assert settings.num_per_decade == 30

    @next_step(validate_apply_settings)
    def apply_settings():
        print("  - Apply setting")
        assert STATE.is_project_dirty(project) is False
        signals.emit(
            Signal.APPLY_DRT_SETTINGS,
            settings=project_tab.get_active_drt().settings,
        )

    @next_step(apply_settings)
    def validate_delete_result():
        assert STATE.is_project_dirty(project) is True
        data = project_tab.get_active_data_set()
        assert len(project.get_drts(data)) == 3
        signals.emit(Signal.SAVE_PROJECT)

    @next_step(validate_delete_result)
    def delete_result():
        print("  - Delete result")
        perform_action(action=Action.DELETE_RESULT)

    @next_step(delete_result)
    def cycle_results():
        print("  - Cycle results")
        perform_action(action=Action.NEXT_SECONDARY_RESULT)
        sleep(0.5)
        perform_action(action=Action.NEXT_SECONDARY_RESULT)
        sleep(0.5)
        perform_action(action=Action.NEXT_SECONDARY_RESULT)
        sleep(0.5)
        perform_action(action=Action.NEXT_SECONDARY_RESULT)
        sleep(0.5)
        perform_action(action=Action.NEXT_SECONDARY_RESULT)
        sleep(0.5)
        perform_action(action=Action.PREVIOUS_SECONDARY_RESULT)

    @next_step(cycle_results)
    def validate_perform_tr_rbf():
        assert STATE.is_project_dirty(project) is True
        data = project_tab.get_active_data_set()
        assert len(project.get_drts(data)) == 4
        signals.emit(Signal.SAVE_PROJECT)

    @next_step(validate_perform_tr_rbf)
    def perform_tr_rbf():
        print("  - Perform TR-RBF DRT analysis")
        assert STATE.is_project_dirty(project) is False
        signals.emit(
            Signal.APPLY_DRT_SETTINGS,
            settings=DRTSettings(
                method=DRTMethod.TR_RBF,
                mode=DRTMode.COMPLEX,
                lambda_value=-1.0,
                rbf_type=RBFType.GAUSSIAN,
                derivative_order=1,
                rbf_shape=RBFShape.FWHM,
                shape_coeff=0.5,
                inductance=False,
                credible_intervals=False,
                timeout=1,
                num_samples=2000,
                num_attempts=1,
                maximum_symmetry=0.5,
                fit=project_tab.get_active_fit(),
                gaussian_width=0.15,
                num_per_decade=20,
                cross_validation_method=CrossValidationMethod.MGCV,
                tr_nnls_lambda_method=TRNNLSLambdaMethod.NONE,
            ),
        )
        sleep(0.5)
        perform_action(action=Action.PERFORM_ACTION)

    @next_step(perform_tr_rbf)
    def validate_perform_tr_nnls():
        assert STATE.is_project_dirty(project) is True
        data = project_tab.get_active_data_set()
        assert len(project.get_drts(data)) == 3
        signals.emit(Signal.SAVE_PROJECT)

    @next_step(validate_perform_tr_nnls)
    def perform_tr_nnls():
        print("  - Perform TR-NNLS DRT analysis")
        assert STATE.is_project_dirty(project) is False
        signals.emit(
            Signal.APPLY_DRT_SETTINGS,
            settings=DRTSettings(
                method=DRTMethod.TR_NNLS,
                mode=DRTMode.REAL,
                lambda_value=-1.0,
                rbf_type=RBFType.CAUCHY,
                derivative_order=1,
                rbf_shape=RBFShape.FWHM,
                shape_coeff=0.5,
                inductance=False,
                credible_intervals=False,
                timeout=1,
                num_samples=2000,
                num_attempts=1,
                maximum_symmetry=0.5,
                fit=project_tab.get_active_fit(),
                gaussian_width=0.15,
                num_per_decade=30,
                cross_validation_method=CrossValidationMethod.NONE,
                tr_nnls_lambda_method=TRNNLSLambdaMethod.CUSTOM,
            ),
        )
        sleep(0.5)
        perform_action(action=Action.BATCH_PERFORM_ACTION)
        sleep(0.5)
        assert STATE.active_modal_window_object is not None
        STATE.active_modal_window_object.toggle(index=0)
        STATE.active_modal_window_object.accept()

    @next_step(perform_tr_nnls)
    def validate_perform_mRQfit():
        assert STATE.is_project_dirty(project) is True
        data = project_tab.get_active_data_set()
        assert len(project.get_drts(data)) == 2
        signals.emit(Signal.SAVE_PROJECT)

    @next_step(validate_perform_mRQfit)
    def perform_mRQfit():
        print("  - Perform m(RQ)fit DRT analysis")
        assert STATE.is_project_dirty(project) is False
        signals.emit(
            Signal.APPLY_DRT_SETTINGS,
            settings=DRTSettings(
                method=DRTMethod.MRQ_FIT,
                mode=DRTMode.COMPLEX,
                lambda_value=-1.0,
                rbf_type=RBFType.CAUCHY,
                derivative_order=1,
                rbf_shape=RBFShape.FWHM,
                shape_coeff=0.5,
                inductance=False,
                credible_intervals=False,
                timeout=1,
                num_samples=2000,
                num_attempts=1,
                maximum_symmetry=0.5,
                fit=project_tab.get_active_fit(),
                gaussian_width=0.15,
                num_per_decade=20,
                cross_validation_method=CrossValidationMethod.NONE,
                tr_nnls_lambda_method=TRNNLSLambdaMethod.NONE,
            ),
        )
        sleep(0.5)
        perform_action(action=Action.PERFORM_ACTION)

    @next_step(perform_mRQfit)
    def validate_perform_bht():
        assert STATE.is_project_dirty(project) is True
        data = project_tab.get_active_data_set()
        assert len(project.get_drts(data)) == 1
        signals.emit(Signal.SAVE_PROJECT)

    @next_step(validate_perform_bht)
    def perform_bht():
        print("  - Perform BHT DRT analysis")
        assert STATE.is_project_dirty(project) is False
        signals.emit(
            Signal.APPLY_DRT_SETTINGS,
            settings=DRTSettings(
                method=DRTMethod.BHT,
                mode=DRTMode.COMPLEX,
                lambda_value=-1.0,
                rbf_type=RBFType.CAUCHY,
                derivative_order=1,
                rbf_shape=RBFShape.FWHM,
                shape_coeff=0.5,
                inductance=False,
                credible_intervals=False,
                timeout=1,
                num_samples=2000,
                num_attempts=1,
                maximum_symmetry=0.5,
                fit=None,
                gaussian_width=0.15,
                num_per_decade=1,
                cross_validation_method=CrossValidationMethod.NONE,
                tr_nnls_lambda_method=TRNNLSLambdaMethod.NONE,
            ),
        )
        sleep(0.5)
        perform_action(action=Action.PERFORM_ACTION)

    @next_step(perform_bht)
    def cycle_data_sets():
        print("  - Cycle data sets")
        perform_action(action=Action.NEXT_PRIMARY_RESULT)
        sleep(0.5)
        perform_action(action=Action.NEXT_PRIMARY_RESULT)
        sleep(0.5)
        perform_action(action=Action.NEXT_PRIMARY_RESULT)
        sleep(0.5)
        perform_action(action=Action.PREVIOUS_PRIMARY_RESULT)

    @next_step(cycle_data_sets)
    def switch_tab():
        STATE.keybinding_handler.perform_action(
            action=Action.SELECT_DRT_TAB,
            context=Context.PROJECT,
            project=project,
            project_tab=project_tab,
        )

    print("\n- DRT tab")
    switch_tab()
    sleep(0.5)
    context: Context = project_tab.get_active_context()
    assert context == Context.DRT_TAB, context


def test_fitting_tab():
    project: Optional[Project] = STATE.get_active_project()
    project_tab: Optional[ProjectTab] = STATE.get_active_project_tab()
    perform_action = lambda action: STATE.keybinding_handler.perform_action(
        action=action,
        context=Context.FITTING_TAB,
        project=project,
        project_tab=project_tab,
    )
    outputs: List[str] = list(label_to_fit_sim_output.keys())

    @next_step(test_drt_tab)
    def result_palette():
        print("  - Result palette")
        signals.emit(Signal.SHOW_RESULT_PALETTE)
        sleep(0.5)
        STATE.active_modal_window_object.hide()

    @next_step(result_palette)
    def data_set_palette():
        print("  - Data set palette")
        signals.emit(Signal.SHOW_DATA_SET_PALETTE)
        sleep(0.5)
        STATE.active_modal_window_object.hide()

    @next_step(data_set_palette)
    def validate_copy_sympy_expression_with_values():
        assert STATE.is_project_dirty(project) is False
        text = dpg.get_clipboard_text().strip()
        assert text.startswith(
            """expr = sympify("R_0 + 1/(2*I*pi*C_2*f + 1/R_1) + 1/(Y_4*(2*I*pi*f)**n_4 + 1/R_3)")
C_2, R_0, R_1, R_3, Y_4, f, n_4 = sorted(expr.free_symbols, key=str)
parameters = {"""
        ), text
        assert len(outputs) == 0, outputs

    @next_step(validate_copy_sympy_expression_with_values)
    def copy_sympy_expression_with_values():
        output = outputs.pop(0)
        print(f"  - Copy: {output}")
        project_tab.fitting_tab.output_combo.set_label(output)
        perform_action(action=Action.COPY_OUTPUT)

    @next_step(copy_sympy_expression_with_values)
    def validate_copy_sympy_expression():
        assert STATE.is_project_dirty(project) is False
        text = dpg.get_clipboard_text().strip()
        assert (
            text == "R_0 + 1/(2*I*pi*C_2*f + 1/R_1) + 1/(Y_4*(2*I*pi*f)**n_4 + 1/R_3)"
        ), text

    @next_step(validate_copy_sympy_expression)
    def copy_sympy_expression():
        output = outputs.pop(0)
        print(f"  - Copy: {output}")
        project_tab.fitting_tab.output_combo.set_label(output)
        perform_action(action=Action.COPY_OUTPUT)

    @next_step(copy_sympy_expression)
    def validate_copy_svg_circuit_without_labels():
        assert STATE.is_project_dirty(project) is False
        text = dpg.get_clipboard_text().strip()
        assert "<svg xmlns:xlink" in text and r"$R_{\rm 1}$" not in text, text

    @next_step(validate_copy_svg_circuit_without_labels)
    def copy_svg_circuit_without_labels():
        output = outputs.pop(0)
        print(f"  - Copy: {output}")
        project_tab.fitting_tab.output_combo.set_label(output)
        perform_action(action=Action.COPY_OUTPUT)

    @next_step(copy_svg_circuit_without_labels)
    def validate_copy_svg_circuit():
        assert STATE.is_project_dirty(project) is False
        text = dpg.get_clipboard_text().strip()
        assert "<svg xmlns:xlink" in text, text

    @next_step(validate_copy_svg_circuit)
    def copy_svg_circuit():
        output = outputs.pop(0)
        print(f"  - Copy: {output}")
        project_tab.fitting_tab.output_combo.set_label(output)
        perform_action(action=Action.COPY_OUTPUT)

    @next_step(copy_svg_circuit)
    def validate_copy_markdown_statistics():
        assert STATE.is_project_dirty(project) is False
        text = dpg.get_clipboard_text().strip()
        headers = text.split("\n")[0]
        assert headers.count("|") == 3, text
        assert 0 < headers.find("Label") < headers.find("Value"), text

    @next_step(validate_copy_markdown_statistics)
    def copy_markdown_statistics():
        output = outputs.pop(0)
        print(f"  - Copy: {output}")
        project_tab.fitting_tab.output_combo.set_label(output)
        perform_action(action=Action.COPY_OUTPUT)

    @next_step(copy_markdown_statistics)
    def validate_copy_markdown_parameters():
        assert STATE.is_project_dirty(project) is False
        text = dpg.get_clipboard_text().strip()
        assert text.startswith(
            """| Element   | Parameter   |      Value |   Std. err. (%) | Unit   | Fixed   |
|:----------|:------------|-----------:|----------------:|:-------|:--------|"""
        ), text

    @next_step(validate_copy_markdown_parameters)
    def copy_markdown_parameters():
        output = outputs.pop(0)
        print(f"  - Copy: {output}")
        project_tab.fitting_tab.output_combo.set_label(output)
        perform_action(action=Action.COPY_OUTPUT)

    @next_step(copy_markdown_parameters)
    def validate_copy_latex_statistics():
        assert STATE.is_project_dirty(project) is False
        text = dpg.get_clipboard_text().strip()
        assert text.startswith(
            r"""\begin{tabular}{ll}
\toprule
Label & Value \\
\midrule"""
        )
        assert text.endswith(
            r"""\bottomrule
\end{tabular}"""
        ), text

    @next_step(validate_copy_latex_statistics)
    def copy_latex_statistics():
        output = outputs.pop(0)
        print(f"  - Copy: {output}")
        project_tab.fitting_tab.output_combo.set_label(output)
        perform_action(action=Action.COPY_OUTPUT)

    @next_step(copy_latex_statistics)
    def validate_copy_latex_parameters():
        assert STATE.is_project_dirty(project) is False
        text = dpg.get_clipboard_text().strip()
        assert text.startswith(
            r"""\begin{tabular}{llrrll}
\toprule
Element & Parameter & Value & Std. err. (\%) & Unit & Fixed \\
\midrule"""
        )
        assert text.endswith(
            r"""\bottomrule
\end{tabular}"""
        ), text

    @next_step(validate_copy_latex_parameters)
    def copy_latex_parameters():
        output = outputs.pop(0)
        print(f"  - Copy: {output}")
        project_tab.fitting_tab.output_combo.set_label(output)
        perform_action(action=Action.COPY_OUTPUT)

    @next_step(copy_latex_parameters)
    def validate_copy_latex_expression():
        assert STATE.is_project_dirty(project) is False
        text = dpg.get_clipboard_text().strip()
        assert (
            text
            == r"R_{0} + \frac{1}{2 i \pi C_{2} f + \frac{1}{R_{1}}} + \frac{1}{Y_{4} \left(2 i \pi f\right)^{n_{4}} + \frac{1}{R_{3}}}"
        ), text

    @next_step(validate_copy_latex_expression)
    def copy_latex_expression():
        output = outputs.pop(0)
        print(f"  - Copy: {output}")
        project_tab.fitting_tab.output_combo.set_label(output)
        perform_action(action=Action.COPY_OUTPUT)

    @next_step(copy_latex_expression)
    def validate_copy_latex_circuit():
        assert STATE.is_project_dirty(project) is False
        text = dpg.get_clipboard_text().strip()
        assert text.startswith(r"\begin{circuitikz}") and text.endswith(
            r"\end{circuitikz}"
        ), text

    @next_step(validate_copy_latex_circuit)
    def copy_latex_circuit():
        output = outputs.pop(0)
        print(f"  - Copy: {output}")
        project_tab.fitting_tab.output_combo.set_label(output)
        perform_action(action=Action.COPY_OUTPUT)

    @next_step(copy_latex_circuit)
    def validate_copy_json_statistics():
        assert STATE.is_project_dirty(project) is False
        text = dpg.get_clipboard_text().strip()
        assert text.startswith('{"Label":{"0":"') and text.endswith('"}}'), text

    @next_step(validate_copy_json_statistics)
    def copy_json_statistics():
        output = outputs.pop(0)
        print(f"  - Copy: {output}")
        project_tab.fitting_tab.output_combo.set_label(output)
        perform_action(action=Action.COPY_OUTPUT)

    @next_step(copy_json_statistics)
    def validate_copy_json_parameters():
        assert STATE.is_project_dirty(project) is False
        text = dpg.get_clipboard_text().strip()
        assert text.startswith('{"Element":{"0":"') and text.endswith('"}}'), text

    @next_step(validate_copy_json_parameters)
    def copy_json_parameters():
        output = outputs.pop(0)
        print(f"  - Copy: {output}")
        project_tab.fitting_tab.output_combo.set_label(output)
        perform_action(action=Action.COPY_OUTPUT)

    @next_step(copy_json_parameters)
    def validate_copy_csv_statistics():
        assert STATE.is_project_dirty(project) is False
        text = dpg.get_clipboard_text().strip()
        assert text.startswith("Label,Value"), text

    @next_step(validate_copy_csv_statistics)
    def copy_csv_statistics():
        output = outputs.pop(0)
        print(f"  - Copy: {output}")
        project_tab.fitting_tab.output_combo.set_label(output)
        perform_action(action=Action.COPY_OUTPUT)

    @next_step(copy_csv_statistics)
    def validate_copy_csv_parameters():
        assert STATE.is_project_dirty(project) is False
        text = dpg.get_clipboard_text().strip()
        assert text.startswith("Element,Parameter,Value,Std. err. (%),Unit,Fixed"), text

    @next_step(validate_copy_csv_parameters)
    def copy_csv_parameters():
        output = outputs.pop(0)
        print(f"  - Copy: {output}")
        project_tab.fitting_tab.output_combo.set_label(output)
        perform_action(action=Action.COPY_OUTPUT)

    @next_step(copy_csv_parameters)
    def validate_copy_csv_impedance():
        assert STATE.is_project_dirty(project) is False
        text = dpg.get_clipboard_text().strip()
        assert text.startswith(
            "f (Hz),Re(Z) (ohm) - Data,Im(Z) (ohm) - Data,Re(Z) (ohm) - Fit,Im(Z) (ohm) - Fit"
        ), text

    @next_step(validate_copy_csv_impedance)
    def copy_csv_impedance():
        output = outputs.pop(0)
        print(f"  - Copy: {output}")
        project_tab.fitting_tab.output_combo.set_label(output)
        perform_action(action=Action.COPY_OUTPUT)

    @next_step(copy_csv_impedance)
    def validate_copy_extended_cdc():
        assert STATE.is_project_dirty(project) is False
        text = dpg.get_clipboard_text().strip()
        assert text.startswith("[R{R=") and text.endswith("})]"), text

    @next_step(validate_copy_extended_cdc)
    def copy_extended_cdc():
        output = outputs.pop(0)
        print(f"  - Copy: {output}")
        project_tab.fitting_tab.output_combo.set_label(output)
        perform_action(action=Action.COPY_OUTPUT)

    @next_step(copy_extended_cdc)
    def validate_copy_basic_cdc():
        assert STATE.is_project_dirty(project) is False
        text = dpg.get_clipboard_text().strip()
        assert text == "[R(RC)(RQ)]", text

    @next_step(validate_copy_basic_cdc)
    def copy_basic_cdc():
        output = outputs.pop(0)
        print(f"  - Copy: {output}")
        project_tab.fitting_tab.output_combo.set_label(output)
        perform_action(action=Action.COPY_OUTPUT)

    @next_step(copy_basic_cdc)
    def validate_copy_bode():
        assert STATE.is_project_dirty(project) is False
        text = dpg.get_clipboard_text().strip()
        headers = text.split("\n")[0].strip()
        assert (
            headers
            == "f (Hz) - Data (scatter),Mod(Z) (ohm) - Data (scatter),-Phase(Z) (°) - Data (scatter),f (Hz) - Fit (scatter),Mod(Z) (ohm) - Fit (scatter),-Phase(Z) (°) - Fit (scatter),f (Hz) - Fit (line),Mod(Z) (ohm) - Fit (line),-Phase(Z) (°) - Fit (line)"
        ), headers

    @next_step(validate_copy_bode)
    def copy_bode():
        print("  - Copy Bode")
        assert STATE.is_project_dirty(project) is False
        perform_action(action=Action.COPY_BODE_DATA)

    @next_step(copy_bode)
    def validate_copy_nyquist():
        assert STATE.is_project_dirty(project) is False
        text = dpg.get_clipboard_text().strip()
        headers = text.split("\n")[0].strip()
        assert (
            headers
            == "Re(Z) (ohm) - Data (scatter),-Im(Z) (ohm) - Data (scatter),Re(Z) (ohm) - Fit (scatter),-Im(Z) (ohm) - Fit (scatter),Re(Z) (ohm) - Fit (line),-Im(Z) (ohm) - Fit (line)"
        ), headers

    @next_step(validate_copy_nyquist)
    def copy_nyquist():
        print("  - Copy Nyquist")
        assert STATE.is_project_dirty(project) is False
        perform_action(action=Action.COPY_NYQUIST_DATA)

    @next_step(copy_nyquist)
    def validate_copy_residuals():
        assert STATE.is_project_dirty(project) is False
        text = dpg.get_clipboard_text().strip()
        headers = text.split("\n")[0].strip()
        assert headers == "f (Hz),real_error (%),imag_error (%)", headers

    @next_step(validate_copy_residuals)
    def copy_residuals():
        print("  - Copy residuals")
        assert STATE.is_project_dirty(project) is False
        perform_action(action=Action.COPY_RESIDUALS_DATA)

    @next_step(copy_residuals)
    def validate_enlarge_impedance():
        assert STATE.is_project_dirty(project) is False
        assert STATE.active_modal_window_object is not None
        STATE.active_modal_window_object.close()

    @next_step(validate_enlarge_impedance)
    def enlarge_impedance():
        print("  - Enlarge Real & Imag.")
        assert STATE.is_project_dirty(project) is False
        perform_action(action=Action.SHOW_ENLARGED_IMPEDANCE)

    @next_step(enlarge_impedance)
    def validate_enlarge_bode():
        assert STATE.is_project_dirty(project) is False
        assert STATE.active_modal_window_object is not None
        STATE.active_modal_window_object.close()

    @next_step(validate_enlarge_bode)
    def enlarge_bode():
        print("  - Enlarge Bode")
        assert STATE.is_project_dirty(project) is False
        perform_action(action=Action.SHOW_ENLARGED_BODE)

    @next_step(enlarge_bode)
    def validate_enlarge_nyquist():
        assert STATE.is_project_dirty(project) is False
        assert STATE.active_modal_window_object is not None
        STATE.active_modal_window_object.close()

    @next_step(validate_enlarge_nyquist)
    def enlarge_nyquist():
        print("  - Enlarge Nyquist")
        assert STATE.is_project_dirty(project) is False
        perform_action(action=Action.SHOW_ENLARGED_NYQUIST)

    @next_step(enlarge_nyquist)
    def validate_enlarge_residuals():
        assert STATE.is_project_dirty(project) is False
        assert STATE.active_modal_window_object is not None
        STATE.active_modal_window_object.close()

    @next_step(validate_enlarge_residuals)
    def enlarge_residuals():
        print("  - Enlarge residuals")
        assert STATE.is_project_dirty(project) is False
        perform_action(action=Action.SHOW_ENLARGED_RESIDUALS)

    @next_step(enlarge_residuals)
    def validate_apply_mask():
        assert STATE.is_project_dirty(project) is True
        data = project_tab.get_active_data_set()
        assert list(data.get_mask().values()).count(True) == 2
        signals.emit(Signal.SAVE_PROJECT)

    @next_step(validate_apply_mask)
    def apply_mask():
        print("  - Apply mask")
        assert STATE.is_project_dirty(project) is False
        data = project_tab.get_active_data_set()
        signals.emit(
            Signal.APPLY_DATA_SET_MASK,
            data=data,
            mask={},
        )
        sleep(0.5)
        signals.emit(
            Signal.APPLY_DATA_SET_MASK,
            data=data,
            mask=project_tab.get_active_fit().mask,
        )

    @next_step(apply_mask)
    def validate_apply_settings():
        assert STATE.is_project_dirty(project) is False
        settings = project_tab.get_fit_settings()
        assert parse_cdc(settings.cdc).to_string() == "[R(RC)(RQ)]"
        assert settings.method == CNLSMethod.POWELL
        assert settings.weight == Weight.PROPORTIONAL
        assert settings.max_nfev == 1000

    @next_step(validate_apply_settings)
    def apply_settings():
        print("  - Apply setting")
        assert STATE.is_project_dirty(project) is False
        signals.emit(
            Signal.APPLY_FIT_SETTINGS,
            settings=project_tab.get_active_fit().settings,
        )

    @next_step(apply_settings)
    def validate_delete_result():
        assert STATE.is_project_dirty(project) is True
        data = project_tab.get_active_data_set()
        assert len(project.get_fits(data)) == 1
        signals.emit(Signal.SAVE_PROJECT)

    @next_step(validate_delete_result)
    def delete_result():
        print("  - Delete result")
        perform_action(action=Action.DELETE_RESULT)

    @next_step(delete_result)
    def cycle_results():
        print("  - Cycle results")
        perform_action(action=Action.NEXT_SECONDARY_RESULT)
        sleep(0.5)
        perform_action(action=Action.NEXT_SECONDARY_RESULT)
        sleep(0.5)
        perform_action(action=Action.NEXT_SECONDARY_RESULT)
        sleep(0.5)
        perform_action(action=Action.PREVIOUS_SECONDARY_RESULT)

    @next_step(cycle_results)
    def validate_perform_fit():
        assert STATE.is_project_dirty(project) is True
        data = project_tab.get_active_data_set()
        assert len(project.get_fits(data)) == 2
        signals.emit(Signal.SAVE_PROJECT)

    @next_step(validate_perform_fit)
    def perform_fit():
        print("  - Perform fit")
        assert STATE.is_project_dirty(project) is False
        perform_action(action=Action.PERFORM_ACTION)
        sleep(0.5)
        signals.emit(
            Signal.APPLY_FIT_SETTINGS,
            settings=FitSettings(
                cdc=parse_cdc("R(RC)(RW)").to_string(),
                method=CNLSMethod.LEASTSQ,
                weight=Weight.BOUKAMP,
                max_nfev=1000,
                timeout=60,
            ),
        )
        perform_action(action=Action.BATCH_PERFORM_ACTION)
        sleep(0.5)
        assert STATE.active_modal_window_object is not None
        STATE.active_modal_window_object.toggle(index=0)
        STATE.active_modal_window_object.accept()

    @next_step(perform_fit)
    def validate_circuit_editor():
        assert STATE.is_project_dirty(project) is False
        settings = project_tab.get_fit_settings()
        assert parse_cdc(settings.cdc).to_string() == "[R(RC)(RQ)]"

    @next_step(validate_circuit_editor)
    def circuit_editor():
        print("  - Circuit editor")
        assert STATE.is_project_dirty(project) is False
        signals.emit(
            Signal.APPLY_FIT_SETTINGS,
            settings=FitSettings(
                cdc=parse_cdc("R(RC)(RQ)").to_string(),
                method=CNLSMethod.POWELL,
                weight=Weight.PROPORTIONAL,
                max_nfev=1000,
                timeout=60,
            ),
        )
        sleep(0.5)
        perform_action(action=Action.SHOW_CIRCUIT_EDITOR)
        sleep(0.5)
        editor = STATE.active_modal_window_object
        editor.node_clicked(editor.node_handler, (0, editor.parser.nodes[0].tag))
        sleep(0.5)
        editor.callback(dpg.get_item_user_data(editor.accept_button))

    @next_step(circuit_editor)
    def cycle_data_sets():
        print("  - Cycle data sets")
        perform_action(action=Action.NEXT_PRIMARY_RESULT)
        sleep(0.5)
        perform_action(action=Action.NEXT_PRIMARY_RESULT)
        sleep(0.5)
        perform_action(action=Action.NEXT_PRIMARY_RESULT)
        sleep(0.5)
        perform_action(action=Action.PREVIOUS_PRIMARY_RESULT)

    @next_step(cycle_data_sets)
    def switch_tab():
        STATE.keybinding_handler.perform_action(
            action=Action.SELECT_FITTING_TAB,
            context=Context.PROJECT,
            project=project,
            project_tab=project_tab,
        )

    print("\n- Fitting tab")
    switch_tab()
    sleep(0.5)
    context: Context = project_tab.get_active_context()
    assert context == Context.FITTING_TAB, context


# TODO: Update tests
# - Representation
def test_zhit_tab():
    project: Optional[Project] = STATE.get_active_project()
    project_tab: Optional[ProjectTab] = STATE.get_active_project_tab()
    perform_action = lambda action: STATE.keybinding_handler.perform_action(
        action=action,
        context=Context.ZHIT_TAB,
        project=project,
        project_tab=project_tab,
    )

    @next_step(test_fitting_tab)
    def result_palette():
        print("  - Result palette")
        signals.emit(Signal.SHOW_RESULT_PALETTE)
        sleep(0.5)
        STATE.active_modal_window_object.hide()

    @next_step(result_palette)
    def data_set_palette():
        print("  - Data set palette")
        signals.emit(Signal.SHOW_DATA_SET_PALETTE)
        sleep(0.5)
        STATE.active_modal_window_object.hide()

    @next_step(data_set_palette)
    def validate_copy_bode():
        assert STATE.is_project_dirty(project) is False
        text = dpg.get_clipboard_text().strip()
        headers = text.split("\n")[0].strip()
        assert (
            headers
            == "f (Hz) - Data (scatter),Mod(Z) (ohm) - Data (scatter),-Phase(Z) (°) - Data (scatter),f (Hz) - Fit (scatter),Mod(Z) (ohm) - Fit (scatter),-Phase(Z) (°) - Fit (scatter),f (Hz) - Fit (line),Mod(Z) (ohm) - Fit (line),-Phase(Z) (°) - Fit (line)"
        ), headers

    @next_step(validate_copy_bode)
    def copy_bode():
        print("  - Copy Bode")
        assert STATE.is_project_dirty(project) is False
        perform_action(action=Action.COPY_BODE_DATA)

    @next_step(copy_bode)
    def validate_copy_residuals():
        assert STATE.is_project_dirty(project) is False
        text = dpg.get_clipboard_text().strip()
        headers = text.split("\n")[0].strip()
        assert headers == "f (Hz),real_error (%),imag_error (%)", headers

    @next_step(validate_copy_residuals)
    def copy_residuals():
        print("  - Copy residuals")
        assert STATE.is_project_dirty(project) is False
        perform_action(action=Action.COPY_RESIDUALS_DATA)

    @next_step(copy_residuals)
    def validate_enlarge_impedance():
        assert STATE.is_project_dirty(project) is False
        assert STATE.active_modal_window_object is not None
        STATE.active_modal_window_object.close()

    @next_step(validate_enlarge_impedance)
    def enlarge_impedance():
        print("  - Enlarge Real & Imag.")
        assert STATE.is_project_dirty(project) is False
        perform_action(action=Action.SHOW_ENLARGED_IMPEDANCE)

    @next_step(enlarge_impedance)
    def validate_enlarge_bode():
        assert STATE.is_project_dirty(project) is False
        assert STATE.active_modal_window_object is not None
        STATE.active_modal_window_object.close()

    @next_step(validate_enlarge_bode)
    def enlarge_bode():
        print("  - Enlarge Bode")
        assert STATE.is_project_dirty(project) is False
        perform_action(action=Action.SHOW_ENLARGED_BODE)

    @next_step(enlarge_bode)
    def validate_enlarge_nyquist():
        assert STATE.is_project_dirty(project) is False
        assert STATE.active_modal_window_object is not None
        STATE.active_modal_window_object.close()

    @next_step(validate_enlarge_nyquist)
    def enlarge_nyquist():
        print("  - Enlarge Nyquist")
        assert STATE.is_project_dirty(project) is False
        perform_action(action=Action.SHOW_ENLARGED_NYQUIST)

    @next_step(enlarge_nyquist)
    def validate_enlarge_residuals():
        assert STATE.is_project_dirty(project) is False
        assert STATE.active_modal_window_object is not None
        STATE.active_modal_window_object.close()

    @next_step(validate_enlarge_residuals)
    def enlarge_residuals():
        print("  - Enlarge residuals")
        assert STATE.is_project_dirty(project) is False
        perform_action(action=Action.SHOW_ENLARGED_RESIDUALS)

    @next_step(enlarge_residuals)
    def validate_load_as_data_set():
        assert STATE.is_project_dirty(project) is True
        assert len(project.get_data_sets()) == 3
        signals.emit(
            Signal.DELETE_DATA_SET,
            data=project_tab.get_active_data_set(),
        )
        signals.emit(Signal.SAVE_PROJECT)
        assert len(project.get_data_sets()) == 2

    @next_step(validate_load_as_data_set)
    def load_as_data_set():
        print("  - Load as data set")
        perform_action(action=Action.LOAD_ZHIT_AS_DATA_SET)

    @next_step(load_as_data_set)
    def validate_apply_mask():
        assert STATE.is_project_dirty(project) is True
        data = project_tab.get_active_data_set()
        assert list(data.get_mask().values()).count(True) == 2
        signals.emit(Signal.SAVE_PROJECT)

    @next_step(validate_apply_mask)
    def apply_mask():
        print("  - Apply mask")
        assert STATE.is_project_dirty(project) is False
        data = project_tab.get_active_data_set()
        signals.emit(
            Signal.APPLY_DATA_SET_MASK,
            data=data,
            mask={},
        )
        sleep(0.5)
        signals.emit(
            Signal.APPLY_DATA_SET_MASK,
            data=data,
            mask=project_tab.get_active_zhit().mask,
        )

    @next_step(apply_mask)
    def validate_apply_settings():
        assert STATE.is_project_dirty(project) is False
        settings = project_tab.get_zhit_settings()
        assert settings.smoothing == ZHITSmoothing.LOWESS
        assert settings.num_points == 3, settings.num_points
        assert settings.polynomial_order == 1, settings.polynomial_order
        assert settings.num_iterations == 3, settings.num_iterations
        assert settings.interpolation == ZHITInterpolation.AKIMA
        assert settings.window == ZHITWindow.HAMMING
        assert isclose(
            settings.window_center, 1.6, abs_tol=1e-6
        ), settings.window_center
        assert isclose(settings.window_width, 2.0, abs_tol=1e-6), settings.window_width

    @next_step(validate_apply_settings)
    def apply_settings():
        print("  - Apply setting")
        assert STATE.is_project_dirty(project) is False
        signals.emit(
            Signal.APPLY_ZHIT_SETTINGS,
            settings=project_tab.get_active_zhit().settings,
        )

    @next_step(apply_settings)
    def validate_delete_result():
        assert STATE.is_project_dirty(project) is True
        data = project_tab.get_active_data_set()
        assert len(project.get_zhits(data)) == 1
        signals.emit(Signal.SAVE_PROJECT)

    @next_step(validate_delete_result)
    def delete_result():
        print("  - Delete result")
        assert STATE.is_project_dirty(project) is False
        perform_action(action=Action.DELETE_RESULT)

    @next_step(delete_result)
    def cycle_results():
        print("  - Cycle results")
        perform_action(action=Action.NEXT_SECONDARY_RESULT)
        sleep(0.5)
        perform_action(action=Action.NEXT_SECONDARY_RESULT)
        sleep(0.5)
        perform_action(action=Action.NEXT_SECONDARY_RESULT)
        sleep(0.5)
        perform_action(action=Action.PREVIOUS_SECONDARY_RESULT)
        sleep(0.5)

    @next_step(cycle_results)
    def validate_perform_nonsmoothed_analysis():
        assert STATE.is_project_dirty(project) is True
        data = project_tab.get_active_data_set()
        assert len(project.get_zhits(data)) == 2
        signals.emit(Signal.SAVE_PROJECT)

    @next_step(validate_perform_nonsmoothed_analysis)
    def perform_nonsmoothed_analysis():
        print("  - Perform nonsmoothed analysis")
        assert STATE.is_project_dirty(project) is False
        signals.emit(
            Signal.APPLY_ZHIT_SETTINGS,
            settings=ZHITSettings(
                smoothing=ZHITSmoothing.NONE,
                num_points=5,
                polynomial_order=2,
                num_iterations=3,
                interpolation=ZHITInterpolation.CUBIC,
                window=ZHITWindow.BOXCAR,
                window_center=1.5,
                window_width=2.0,
                representation=ZHITRepresentation.IMPEDANCE,
            ),
        )
        sleep(0.5)
        perform_action(action=Action.BATCH_PERFORM_ACTION)
        sleep(0.5)
        assert STATE.active_modal_window_object is not None
        STATE.active_modal_window_object.toggle(index=0)
        STATE.active_modal_window_object.accept()

    @next_step(perform_nonsmoothed_analysis)
    def validate_perform_smoothed_analysis():
        assert STATE.is_project_dirty(project) is True
        data = project_tab.get_active_data_set()
        assert len(project.get_zhits(data)) == 1
        signals.emit(Signal.SAVE_PROJECT)

    @next_step(validate_perform_smoothed_analysis)
    def perform_smoothed_analysis():
        print("  - Perform smoothed analysis")
        assert STATE.is_project_dirty(project) is False
        signals.emit(
            Signal.APPLY_ZHIT_SETTINGS,
            settings=ZHITSettings(
                smoothing=ZHITSmoothing.LOWESS,
                num_points=3,
                polynomial_order=1,
                num_iterations=3,
                interpolation=ZHITInterpolation.AKIMA,
                window=ZHITWindow.HAMMING,
                window_center=1.6,
                window_width=2.0,
                representation=ZHITRepresentation.IMPEDANCE,
            ),
        )
        sleep(0.5)
        perform_action(action=Action.PERFORM_ACTION)

    @next_step(perform_smoothed_analysis)
    def preview_weights():
        print("  - Preview weights")
        assert STATE.is_project_dirty(project) is False
        perform_action(action=Action.PREVIEW_ZHIT_WEIGHTS)
        sleep(0.5)
        STATE.active_modal_window_object.cycle(index=0)
        sleep(0.5)
        STATE.active_modal_window_object.cycle(step=-1)
        sleep(0.5)
        STATE.active_modal_window_object.close()

    @next_step(preview_weights)
    def cycle_data_sets():
        print("  - Cycle data sets")
        assert STATE.is_project_dirty(project) is False
        perform_action(action=Action.NEXT_PRIMARY_RESULT)
        sleep(0.5)
        perform_action(action=Action.NEXT_PRIMARY_RESULT)
        sleep(0.5)
        perform_action(action=Action.NEXT_PRIMARY_RESULT)
        sleep(0.5)
        perform_action(action=Action.PREVIOUS_PRIMARY_RESULT)

    @next_step(cycle_data_sets)
    def switch_tab():
        STATE.keybinding_handler.perform_action(
            action=Action.SELECT_ZHIT_TAB,
            context=Context.PROJECT,
            project=project,
            project_tab=project_tab,
        )

    print("\n- Z-HIT tab")
    switch_tab()
    sleep(0.5)
    context: Context = project_tab.get_active_context()
    assert context == Context.ZHIT_TAB, context


# TODO: Update tests
# - Representation
# - Log Fext widgets
def test_kramers_kronig_tab():
    project: Optional[Project] = STATE.get_active_project()
    project_tab: Optional[ProjectTab] = STATE.get_active_project_tab()
    perform_action = lambda action: STATE.keybinding_handler.perform_action(
        action=action,
        context=Context.KRAMERS_KRONIG_TAB,
        project=project,
        project_tab=project_tab,
    )

    @next_step(test_zhit_tab)
    def result_palette():
        print("  - Result palette")
        signals.emit(Signal.SHOW_RESULT_PALETTE)
        sleep(0.5)
        STATE.active_modal_window_object.hide()

    @next_step(result_palette)
    def data_set_palette():
        print("  - Data set palette")
        signals.emit(Signal.SHOW_DATA_SET_PALETTE)
        sleep(0.5)
        STATE.active_modal_window_object.hide()

    @next_step(data_set_palette)
    def validate_copy_bode():
        assert STATE.is_project_dirty(project) is False
        text = dpg.get_clipboard_text().strip()
        headers = text.split("\n")[0].strip()
        assert (
            headers
            == "f (Hz) - Data (scatter),Mod(Z) (ohm) - Data (scatter),-Phase(Z) (°) - Data (scatter),f (Hz) - Fit (scatter),Mod(Z) (ohm) - Fit (scatter),-Phase(Z) (°) - Fit (scatter),f (Hz) - Fit (line),Mod(Z) (ohm) - Fit (line),-Phase(Z) (°) - Fit (line)"
        ), headers

    @next_step(validate_copy_bode)
    def copy_bode():
        print("  - Copy Bode")
        assert STATE.is_project_dirty(project) is False
        perform_action(action=Action.COPY_BODE_DATA)

    @next_step(copy_bode)
    def validate_copy_nyquist():
        assert STATE.is_project_dirty(project) is False
        text = dpg.get_clipboard_text().strip()
        headers = text.split("\n")[0].strip()
        assert (
            headers
            == "Re(Z) (ohm) - Data (scatter),-Im(Z) (ohm) - Data (scatter),Re(Z) (ohm) - Fit (scatter),-Im(Z) (ohm) - Fit (scatter),Re(Z) (ohm) - Fit (line),-Im(Z) (ohm) - Fit (line)"
        ), headers

    @next_step(validate_copy_nyquist)
    def copy_nyquist():
        print("  - Copy Nyquist")
        assert STATE.is_project_dirty(project) is False
        perform_action(action=Action.COPY_NYQUIST_DATA)

    @next_step(copy_nyquist)
    def validate_copy_residuals():
        assert STATE.is_project_dirty(project) is False
        text = dpg.get_clipboard_text().strip()
        headers = text.split("\n")[0].strip()
        assert headers == "f (Hz),real_error (%),imag_error (%)", headers

    @next_step(validate_copy_residuals)
    def copy_residuals():
        print("  - Copy residuals")
        assert STATE.is_project_dirty(project) is False
        perform_action(action=Action.COPY_RESIDUALS_DATA)

    @next_step(copy_residuals)
    def validate_enlarge_impedance():
        assert STATE.is_project_dirty(project) is False
        assert STATE.active_modal_window_object is not None
        STATE.active_modal_window_object.close()

    @next_step(validate_enlarge_impedance)
    def enlarge_impedance():
        print("  - Enlarge Real & Imag.")
        assert STATE.is_project_dirty(project) is False
        perform_action(action=Action.SHOW_ENLARGED_IMPEDANCE)

    @next_step(enlarge_impedance)
    def validate_enlarge_bode():
        assert STATE.is_project_dirty(project) is False
        assert STATE.active_modal_window_object is not None
        STATE.active_modal_window_object.close()

    @next_step(validate_enlarge_bode)
    def enlarge_bode():
        print("  - Enlarge Bode")
        assert STATE.is_project_dirty(project) is False
        perform_action(action=Action.SHOW_ENLARGED_BODE)

    @next_step(enlarge_bode)
    def validate_enlarge_nyquist():
        assert STATE.is_project_dirty(project) is False
        assert STATE.active_modal_window_object is not None
        STATE.active_modal_window_object.close()

    @next_step(validate_enlarge_nyquist)
    def enlarge_nyquist():
        print("  - Enlarge Nyquist")
        assert STATE.is_project_dirty(project) is False
        perform_action(action=Action.SHOW_ENLARGED_NYQUIST)

    @next_step(enlarge_nyquist)
    def validate_enlarge_residuals():
        assert STATE.is_project_dirty(project) is False
        assert STATE.active_modal_window_object is not None
        STATE.active_modal_window_object.close()

    @next_step(validate_enlarge_residuals)
    def enlarge_residuals():
        print("  - Enlarge residuals")
        assert STATE.is_project_dirty(project) is False
        perform_action(action=Action.SHOW_ENLARGED_RESIDUALS)

    @next_step(enlarge_residuals)
    def validate_apply_mask():
        assert STATE.is_project_dirty(project) is True
        data = project_tab.get_active_data_set()
        assert list(data.get_mask().values()).count(True) == 2
        signals.emit(Signal.SAVE_PROJECT)

    @next_step(validate_apply_mask)
    def apply_mask():
        print("  - Apply mask")
        assert STATE.is_project_dirty(project) is False
        data = project_tab.get_active_data_set()
        signals.emit(
            Signal.APPLY_DATA_SET_MASK,
            data=data,
            mask={},
        )
        sleep(0.5)
        signals.emit(
            Signal.APPLY_DATA_SET_MASK,
            data=data,
            mask=project_tab.get_active_test().mask,
        )

    @next_step(apply_mask)
    def validate_apply_settings():
        assert STATE.is_project_dirty(project) is False
        settings = project_tab.get_test_settings()
        assert settings.test == KramersKronigTest.REAL
        assert settings.mode == KramersKronigMode.AUTO

    @next_step(validate_apply_settings)
    def apply_settings():
        print("  - Apply setting")
        assert STATE.is_project_dirty(project) is False
        signals.emit(
            Signal.APPLY_TEST_SETTINGS,
            settings=project_tab.get_active_test().settings,
        )

    @next_step(apply_settings)
    def validate_delete_result():
        assert STATE.is_project_dirty(project) is True
        data = project_tab.get_active_data_set()
        assert len(project.get_tests(data)) == 2
        signals.emit(Signal.SAVE_PROJECT)

    @next_step(validate_delete_result)
    def delete_result():
        print("  - Delete result")
        assert STATE.is_project_dirty(project) is False
        perform_action(action=Action.DELETE_RESULT)

    @next_step(delete_result)
    def cycle_results():
        print("  - Cycle results")
        perform_action(action=Action.NEXT_SECONDARY_RESULT)
        sleep(0.5)
        perform_action(action=Action.NEXT_SECONDARY_RESULT)
        sleep(0.5)
        perform_action(action=Action.NEXT_SECONDARY_RESULT)
        sleep(0.5)
        perform_action(action=Action.NEXT_SECONDARY_RESULT)
        sleep(0.5)
        perform_action(action=Action.PREVIOUS_SECONDARY_RESULT)
        sleep(0.5)

    @next_step(cycle_results)
    def validate_perform_exploratory_complex():
        assert STATE.is_project_dirty(project) is True
        data = project_tab.get_active_data_set()
        assert len(project.get_tests(data)) == 3
        signals.emit(Signal.SAVE_PROJECT)

    @next_step(validate_perform_exploratory_complex)
    def perform_exploratory_complex():
        print("  - Perform exploratory complex test")
        assert STATE.is_project_dirty(project) is False
        signals.emit(
            Signal.APPLY_TEST_SETTINGS,
            settings=KramersKronigSettings(
                test=KramersKronigTest.COMPLEX,
                mode=KramersKronigMode.EXPLORATORY,
                representation=KramersKronigRepresentation.AUTO,
                num_RC=25,
                add_capacitance=True,
                add_inductance=True,
                min_log_F_ext=-1.0,
                max_log_F_ext=1.0,
                log_F_ext=0.0,
                num_F_ext_evaluations=20,
                rapid_F_ext_evaluations=True,
                timeout=10,
                cnls_method=CNLSMethod.LEASTSQ,
                max_nfev=1,
                suggestion_settings=KramersKronigSuggestionSettings(
                    methods=[],
                    use_mean=False,
                    use_ranking=False,
                    use_sum=False,
                    lower_limit=0,
                    upper_limit=0,
                    limit_delta=0,
                    m1_mu_criterion=0.7,
                    m1_beta=0.75,
                ),
            ),
        )
        sleep(0.5)
        perform_action(action=Action.PERFORM_ACTION)
        sleep(0.5)
        STATE.active_modal_window_object.accept(
            result=dpg.get_item_user_data(
                STATE.active_modal_window_object.accept_button
            )
        )

    @next_step(perform_exploratory_complex)
    def validate_perform_automatic_real():
        assert STATE.is_project_dirty(project) is True
        data = project_tab.get_active_data_set()
        assert len(project.get_tests(data)) == 2
        signals.emit(Signal.SAVE_PROJECT)

    @next_step(validate_perform_automatic_real)
    def perform_automatic_real():
        print("  - Perform automatic real test")
        assert STATE.is_project_dirty(project) is False
        signals.emit(
            Signal.APPLY_TEST_SETTINGS,
            settings=KramersKronigSettings(
                test=KramersKronigTest.REAL,
                mode=KramersKronigMode.AUTO,
                representation=KramersKronigRepresentation.AUTO,
                num_RC=16,
                add_capacitance=True,
                add_inductance=True,
                min_log_F_ext=-1.0,
                max_log_F_ext=1.0,
                log_F_ext=0.0,
                num_F_ext_evaluations=20,
                rapid_F_ext_evaluations=True,
                timeout=10,
                cnls_method=CNLSMethod.LEASTSQ,
                max_nfev=1,
                suggestion_settings=KramersKronigSuggestionSettings(
                    methods=[],
                    use_mean=False,
                    use_ranking=False,
                    use_sum=False,
                    lower_limit=0,
                    upper_limit=0,
                    limit_delta=0,
                    m1_mu_criterion=0.7,
                    m1_beta=0.75,
                ),
            ),
        )
        sleep(0.5)
        perform_action(action=Action.BATCH_PERFORM_ACTION)
        sleep(0.5)
        assert STATE.active_modal_window_object is not None
        STATE.active_modal_window_object.toggle(index=0)
        STATE.active_modal_window_object.accept()

    @next_step(perform_automatic_real)
    def validate_perform_manual_cnls():
        assert STATE.is_project_dirty(project) is True
        data = project_tab.get_active_data_set()
        assert len(project.get_tests(data)) == 1
        signals.emit(Signal.SAVE_PROJECT)

    @next_step(validate_perform_manual_cnls)
    def perform_manual_cnls():
        print("  - Perform manual CNLS test")
        assert STATE.is_project_dirty(project) is False
        signals.emit(
            Signal.APPLY_TEST_SETTINGS,
            settings=KramersKronigSettings(
                test=KramersKronigTest.CNLS,
                mode=KramersKronigMode.MANUAL,
                representation=KramersKronigRepresentation.AUTO,
                num_RC=7,
                add_capacitance=True,
                add_inductance=True,
                min_log_F_ext=-1.0,
                max_log_F_ext=1.0,
                log_F_ext=0.0,
                num_F_ext_evaluations=20,
                rapid_F_ext_evaluations=True,
                timeout=10,
                cnls_method=CNLSMethod.LEASTSQ,
                max_nfev=100,
                suggestion_settings=KramersKronigSuggestionSettings(
                    methods=[],
                    use_mean=False,
                    use_ranking=False,
                    use_sum=False,
                    lower_limit=0,
                    upper_limit=0,
                    limit_delta=0,
                    m1_mu_criterion=0.7,
                    m1_beta=0.75,
                ),
            ),
        )
        sleep(0.5)
        perform_action(action=Action.PERFORM_ACTION)

    @next_step(perform_manual_cnls)
    def cycle_data_sets():
        print("  - Cycle data sets")
        perform_action(action=Action.NEXT_PRIMARY_RESULT)
        sleep(0.5)
        perform_action(action=Action.NEXT_PRIMARY_RESULT)
        sleep(0.5)
        perform_action(action=Action.NEXT_PRIMARY_RESULT)
        sleep(0.5)
        perform_action(action=Action.PREVIOUS_PRIMARY_RESULT)

    @next_step(cycle_data_sets)
    def switch_tab():
        STATE.keybinding_handler.perform_action(
            action=Action.SELECT_KRAMERS_KRONIG_TAB,
            context=Context.PROJECT,
            project=project,
            project_tab=project_tab,
        )

    print("\n- Kramers-Kronig tab")
    switch_tab()
    sleep(0.5)
    context: Context = project_tab.get_active_context()
    assert context == Context.KRAMERS_KRONIG_TAB, context


def test_data_sets_tab():
    project: Optional[Project] = STATE.get_active_project()
    project_tab: Optional[ProjectTab] = STATE.get_active_project_tab()
    perform_action = lambda action: STATE.keybinding_handler.perform_action(
        action=action,
        context=Context.DATA_SETS_TAB,
        project=project,
        project_tab=project_tab,
    )

    @next_step(test_kramers_kronig_tab)
    def data_set_palette():
        print("  - Data set palette")
        signals.emit(Signal.SHOW_DATA_SET_PALETTE)
        sleep(0.5)
        STATE.active_modal_window_object.hide()

    @next_step(data_set_palette)
    def validate_mask_points():
        assert STATE.is_project_dirty(project) is True
        data = project_tab.get_active_data_set()
        assert data.get_num_points() == data.get_num_points(masked=None) - 2
        signals.emit(Signal.SAVE_PROJECT)

    @next_step(validate_mask_points)
    def mask_points():
        print("  - Mask points")
        assert STATE.is_project_dirty(project) is False
        data = project_tab.get_active_data_set()
        signals.emit(Signal.TOGGLE_DATA_POINT, state=True, index=1, data=data)
        sleep(0.5)
        signals.emit(Signal.TOGGLE_DATA_POINT, state=True, index=7, data=data)
        sleep(0.5)
        signals.emit(Signal.TOGGLE_DATA_POINT, state=True, index=8, data=data)
        sleep(0.5)
        signals.emit(Signal.TOGGLE_DATA_POINT, state=False, index=8, data=data)

    @next_step(mask_points)
    def validate_delete_data_sets():
        assert STATE.is_project_dirty(project) is True
        assert len(project.get_data_sets()) == 2
        signals.emit(Signal.SAVE_PROJECT)

    @next_step(validate_delete_data_sets)
    def delete_data_sets():
        print("  - Delete data sets")
        assert STATE.is_project_dirty(project) is False
        data_sets = [
            _ for _ in project.get_data_sets() if _.get_label() not in ("Foo", "Baz")
        ]
        for data in data_sets:
            signals.emit(Signal.DELETE_DATA_SET, data=data)
            sleep(0.5)

    @next_step(delete_data_sets)
    def validate_enlarge_impedance():
        assert STATE.is_project_dirty(project) is False
        assert STATE.active_modal_window_object is not None
        STATE.active_modal_window_object.close()

    @next_step(validate_enlarge_impedance)
    def enlarge_impedance():
        print("  - Enlarge Real & Imag.")
        assert STATE.is_project_dirty(project) is False
        perform_action(action=Action.SHOW_ENLARGED_IMPEDANCE)

    @next_step(enlarge_impedance)
    def validate_enlarge_bode():
        assert STATE.is_project_dirty(project) is False
        assert STATE.active_modal_window_object is not None
        STATE.active_modal_window_object.close()

    @next_step(validate_enlarge_bode)
    def enlarge_bode():
        print("  - Enlarge Bode")
        assert STATE.is_project_dirty(project) is False
        perform_action(action=Action.SHOW_ENLARGED_BODE)

    @next_step(enlarge_bode)
    def validate_enlarge_nyquist():
        assert STATE.is_project_dirty(project) is False
        assert STATE.active_modal_window_object is not None
        STATE.active_modal_window_object.close()

    @next_step(validate_enlarge_nyquist)
    def enlarge_nyquist():
        print("  - Enlarge Nyquist")
        assert STATE.is_project_dirty(project) is False
        perform_action(action=Action.SHOW_ENLARGED_NYQUIST)

    @next_step(enlarge_nyquist)
    def validate_copy_mask():
        assert STATE.is_project_dirty(project) is True
        data = project_tab.get_active_data_set()
        assert data.get_num_points() == data.get_num_points(masked=None)
        signals.emit(Signal.SAVE_PROJECT)

    @next_step(validate_copy_mask)
    def copy_mask():
        print("  - Copy mask")
        assert STATE.is_project_dirty(project) is False
        perform_action(action=Action.COPY_DATA_SET_MASK)
        sleep(0.5)
        STATE.active_modal_window_object.accept()

    @next_step(copy_mask)
    def validate_toggle_points():
        assert STATE.is_project_dirty(project) is True
        data = project_tab.get_active_data_set()
        assert data.get_num_points() == 0
        signals.emit(Signal.SAVE_PROJECT)

    @next_step(validate_toggle_points)
    def toggle_points():
        print("  - Toggle points")
        assert STATE.is_project_dirty(project) is False
        perform_action(action=Action.TOGGLE_DATA_POINTS)
        sleep(0.5)
        STATE.active_modal_window_object.accept()

    @next_step(toggle_points)
    def validate_subtract_impedances():
        assert STATE.is_project_dirty(project) is True
        assert len(project.get_data_sets()) == 6
        data = project_tab.get_active_data_set()
        assert data.get_label() == "Average - interpolated - added parallel impedance - subtracted"
        signals.emit(Signal.SAVE_PROJECT)

    @next_step(validate_subtract_impedances)
    def subtract_impedances():
        print("  - Subtract")
        assert STATE.is_project_dirty(project) is False
        perform_action(action=Action.SUBTRACT_IMPEDANCE)
        sleep(0.5)
        dpg.set_value(STATE.active_modal_window_object.constant_real, 150)
        STATE.active_modal_window_object.update_preview()
        sleep(0.5)
        STATE.active_modal_window_object.accept()

    @next_step(subtract_impedances)
    def validate_parallel_impedances():
        assert STATE.is_project_dirty(project) is True
        assert len(project.get_data_sets()) == 5
        data = project_tab.get_active_data_set()
        assert data.get_label() == "Average - interpolated - added parallel impedance"
        signals.emit(Signal.SAVE_PROJECT)

    @next_step(validate_parallel_impedances)
    def parallel_impedances():
        print("  - Add parallel impedance")
        assert STATE.is_project_dirty(project) is False
        perform_action(action=Action.PARALLEL_IMPEDANCE)
        sleep(0.5)
        dpg.set_value(STATE.active_modal_window_object.constant_real, 500)
        STATE.active_modal_window_object.update_preview()
        sleep(0.5)
        STATE.active_modal_window_object.accept()

    @next_step(parallel_impedances)
    def validate_interpolate_data_points():
        assert STATE.is_project_dirty(project) is True
        assert len(project.get_data_sets()) == 4
        data = project_tab.get_active_data_set()
        assert data.get_label() == "Average - interpolated"
        signals.emit(Signal.SAVE_PROJECT)

    @next_step(validate_interpolate_data_points)
    def interpolate_data_points():
        print("  - Interpolate")
        assert STATE.is_project_dirty(project) is False
        data = project_tab.get_active_data_set()
        perform_action(action=Action.INTERPOLATE_POINTS)
        sleep(0.5)
        for i in range(0, data.get_num_points(masked=None)):
            if i % 2 == 0:
                continue
            row = STATE.active_modal_window_object.get_rows()[i]
            checkbox = STATE.active_modal_window_object.get_checkbox(row)
            dpg.set_value(checkbox, True)
            STATE.active_modal_window_object.toggle_point(index=i, state=True)
            sleep(0.5)
        STATE.active_modal_window_object.accept()

    @next_step(interpolate_data_points)
    def validate_average_data_sets():
        assert STATE.is_project_dirty(project) is True
        assert len(project.get_data_sets()) == 3
        data = project_tab.get_active_data_set()
        assert data.get_label() == "Average"
        signals.emit(Signal.SAVE_PROJECT)

    @next_step(validate_average_data_sets)
    def average_data_sets():
        print("  - Average")
        assert STATE.is_project_dirty(project) is False
        perform_action(action=Action.AVERAGE_DATA_SETS)
        sleep(0.5)
        assert STATE.active_modal_window_object is not None
        row: int
        for row in dpg.get_item_children(
            STATE.active_modal_window_object.data_set_table,
            slot=1,
        ):
            dpg.set_value(dpg.get_item_children(row, slot=1)[0], True)
        STATE.active_modal_window_object.update_preview([])
        sleep(0.5)
        STATE.active_modal_window_object.accept()

    @next_step(average_data_sets)
    def validate_cycle_rename_data_sets():
        assert STATE.is_project_dirty(project) is True
        data = project_tab.get_active_data_set()
        assert data is project.get_data_sets()[1]
        assert data.get_label() == "Foo"
        assert data.get_path() == "Bar"
        data = project.get_data_sets()[0]
        assert data.get_label() == "Baz"
        assert data.get_path() == "Foo"
        signals.emit(Signal.SAVE_PROJECT)

    @next_step(validate_cycle_rename_data_sets)
    def cycle_rename_data_sets():
        print("  - Cycle, rename, and modify path")
        assert STATE.is_project_dirty(project) is False
        data = project_tab.get_active_data_set()
        signals.emit(Signal.RENAME_DATA_SET, data=data, label="Foo")
        sleep(0.5)
        signals.emit(Signal.MODIFY_DATA_SET_PATH, data=data, path="Bar")
        sleep(0.5)
        perform_action(Action.NEXT_PRIMARY_RESULT)
        sleep(0.5)
        data = project_tab.get_active_data_set()
        signals.emit(Signal.RENAME_DATA_SET, data=data, label="Baz")
        sleep(0.5)
        signals.emit(Signal.MODIFY_DATA_SET_PATH, data=data, path="Foo")
        sleep(0.5)
        perform_action(Action.PREVIOUS_PRIMARY_RESULT)
        sleep(0.5)
        perform_action(Action.PREVIOUS_PRIMARY_RESULT)
        sleep(0.5)
        perform_action(Action.NEXT_PRIMARY_RESULT)

    @next_step(cycle_rename_data_sets)
    def validate_load_data():
        assert STATE.is_project_dirty(project) is True
        assert len(project.get_data_sets()) == 2
        signals.emit(Signal.SAVE_PROJECT)

    @next_step(validate_load_data)
    def load_data():
        print("  - Load")
        assert STATE.is_project_dirty(project) is False
        path: str = join(PARENT_FOLDER, "data-2.csv")
        signals.emit(Signal.LOAD_DATA_SET_FILES, paths=[path])
        signals.emit(Signal.LOAD_DATA_SET_FILES, paths=[path])

    @next_step(load_data)
    def switch_tab():
        STATE.keybinding_handler.perform_action(
            action=Action.SELECT_DATA_SETS_TAB,
            context=Context.PROJECT,
            project=project,
            project_tab=project_tab,
        )

    print("\n- Data sets tab")
    switch_tab()
    sleep(0.5)
    context: Context = project_tab.get_active_context()
    assert context == Context.DATA_SETS_TAB, context


def test_overview_tab():
    project: Optional[Project] = STATE.get_active_project()
    project_tab: Optional[ProjectTab] = STATE.get_active_project_tab()

    @next_step(test_data_sets_tab)
    def validate_modify_notes():
        assert STATE.is_project_dirty(project) is True
        assert project.get_notes() == "FOO BAR BAZ"
        assert project_tab.get_notes() == "FOO BAR BAZ"
        signals.emit(Signal.SAVE_PROJECT)

    @next_step(validate_modify_notes)
    def modify_notes():
        print("  - Modify notes")
        assert STATE.is_project_dirty(project) is False
        project_tab.set_notes("FOO BAR BAZ")
        signals.emit(Signal.MODIFY_PROJECT_NOTES, timers=[])

    @next_step(modify_notes)
    def validate_rename_project():
        assert project.get_label() == "Test project"
        assert dpg.get_item_label(project_tab.tab) == "Test project"
        assert STATE.is_project_dirty(project) is True
        signals.emit(Signal.SAVE_PROJECT)

    @next_step(validate_rename_project)
    def rename_project():
        print("  - Rename project")
        assert STATE.is_project_dirty(project) is False
        signals.emit(Signal.RENAME_PROJECT, label="Test project")

    print("\n- Overview tab")
    sleep(0.5)
    context: Context = project_tab.get_active_context()
    assert context == Context.OVERVIEW_TAB, context
    rename_project()


def test_project():
    project: Optional[Project] = None
    path = TMP_PROJECT
    if exists(path):
        remove(path)

    @next_step(test_overview_tab)
    def validate_load_project():
        nonlocal project
        assert len(STATE.projects) == 1
        project = STATE.get_active_project()
        assert STATE.is_project_dirty(project) is False

    @next_step(validate_load_project)
    def load_project():
        print("  - Load")
        signals.emit(Signal.CLOSE_PROJECT, force=True)
        sleep(0.5)
        signals.emit(Signal.LOAD_PROJECT_FILES, paths=[path])

    @next_step(load_project)
    def validate_saved_project():
        assert exists(path)
        assert STATE.is_project_dirty(project) is False

    @next_step(validate_saved_project)
    def save_project():
        print("  - Save")
        signals.emit(Signal.SAVE_PROJECT, path=path)

    @next_step(save_project)
    def validate_blank_project():
        nonlocal project
        assert len(STATE.projects) == 1
        project = STATE.get_active_project()
        assert project.get_label() == "Project"
        assert STATE.is_project_dirty(project) is True

    @next_step(validate_blank_project)
    def create_project():
        print("  - Create")
        signals.emit(Signal.NEW_PROJECT)

    print("\n- Project")
    create_project()


def test_project_versions():
    project_paths: List[str] = []
    for _, _, files in walk(PARENT_FOLDER):
        break
    
    project_paths = [
        join(PARENT_FOLDER, _)
        for _ in files
        if _.startswith("example-project-v") and _.endswith(".json")
    ]
    assert len(project_paths) > 0
    
    project_versions: Dict[str, int] = {}

    path: str
    for path in project_paths:
        name = splitext(basename(path))[0]
        i: int = -1
        
        while name[i:].isnumeric():
            i -= 1
        
        project_versions[path] = int(name[min((i+1, -1)):])
    
    project_paths.sort(key=lambda s: project_versions[s])

    actions = [
        Action.SELECT_DATA_SETS_TAB,
        Action.SELECT_KRAMERS_KRONIG_TAB,
        Action.SELECT_ZHIT_TAB,
        Action.SELECT_DRT_TAB,
        Action.SELECT_FITTING_TAB,
        Action.SELECT_SIMULATION_TAB,
        Action.SELECT_PLOTTING_TAB,
        Action.SELECT_OVERVIEW_TAB,
    ]

    @next_step()
    def close():
        while len(STATE.projects) > 0:
            signals.emit(Signal.CLOSE_PROJECT, force=True)
            sleep(0.5)

    @next_step(close)
    def load():
        num_projects: int = len(project_paths)
        backup_paths_to_remove: List[str] = []

        while project_paths:
            path = project_paths.pop(0)
            print(f"  - {basename(path)}")
            signals.emit(Signal.LOAD_PROJECT_FILES, paths=[path])
            sleep(1.0)
            backup_path: str = path.replace(".json", ".backup0")
            version: int = project_versions[path]
            assert exists(backup_path) or version == LATEST_PROJECT_VERSION, (backup_path, version)
            if exists(backup_path):
                backup_paths_to_remove.append(backup_path)

            project: Optional[Project] = STATE.get_active_project()
            project_tab: Optional[ProjectTab] = STATE.get_active_project_tab()
            for action in actions:
                STATE.keybinding_handler.perform_action(
                    action=action,
                    context=Context.PROJECT,
                    project=project,
                    project_tab=project_tab,
                )
                sleep(0.5)

        assert len(STATE.projects) == num_projects, num_projects

        for backup_path in backup_paths_to_remove:
            remove(backup_path)

    print("\n- Project versions")
    load()


def test_ancillary_windows():
    @next_step()
    def error_message():
        print("  - Error message")
        signals.emit(Signal.SHOW_ERROR_MESSAGE, traceback="FOO", message="BAR")
        sleep(0.5)
        STATE.active_modal_window_object.hide()

    @next_step(error_message)
    def command_palette():
        print("  - Command palette")
        signals.emit(Signal.SHOW_COMMAND_PALETTE)
        sleep(0.5)
        STATE.active_modal_window_object.hide()

    @next_step(command_palette)
    def help_about():
        print("  - About")
        signals.emit(Signal.SHOW_HELP_ABOUT)
        sleep(0.5)
        STATE.active_modal_window_object.close()

    @next_step(help_about)
    def help_changelog():
        print("  - Changelog")
        signals.emit(Signal.SHOW_CHANGELOG)
        sleep(0.5)
        STATE.active_modal_window_object.close()

    @next_step(help_changelog)
    def help_licenses():
        print("  - Licenses")
        signals.emit(Signal.SHOW_HELP_LICENSES)
        sleep(0.5)
        STATE.active_modal_window_object.close()

    @next_step(help_licenses)
    def settings_user_defined_elements():
        print("  - User-defined elements")
        signals.emit(Signal.SHOW_SETTINGS_USER_DEFINED_ELEMENTS)
        sleep(0.5)
        STATE.active_modal_window_object.close()

    @next_step(settings_user_defined_elements)
    def settings_keybindings():
        print("  - Keybindings")
        signals.emit(Signal.SHOW_SETTINGS_KEYBINDINGS)
        sleep(0.5)
        STATE.active_modal_window_object.close()

    @next_step(settings_keybindings)
    def settings_defaults():
        print("  - Defaults")
        signals.emit(Signal.SHOW_SETTINGS_DEFAULTS)
        sleep(0.5)
        STATE.active_modal_window_object.close()

    @next_step(settings_defaults)
    def settings_appearances():
        print("  - Appearances")
        signals.emit(Signal.SHOW_SETTINGS_APPEARANCE)
        sleep(0.5)
        STATE.active_modal_window_object.close()

    @next_step(settings_appearances)
    def select_project():
        print("  - Select project")
        signals.emit(Signal.SELECT_PROJECT_FILES)
        sleep(0.5)
        STATE.active_modal_window_object.close()

    print("\n- Ancillary windows")
    select_project()


def test_user_defined_elements():
    @next_step()
    def validate_load():
        assert "Userdefined" in get_elements().keys()

    @next_step(validate_load)
    def load():
        print("  - Load")
        refresh_user_defined_elements(
            path=abspath(
                join(
                    PARENT_FOLDER,
                    "user_defined_elements.py",
                )
            )
        )

    print("\n- User-defined elements")
    load()


def test_overlay():
    @next_step()
    def progress_bar():
        print("  - Progress bar")
        i: int
        num: int = 5
        for i in range(0, num):
            signals.emit(
                Signal.SHOW_BUSY_MESSAGE,
                message=f"Progress {i + 1}/{num}",
                progress=i / num,
            )
            sleep(0.2)
        signals.emit(Signal.HIDE_BUSY_MESSAGE)

    @next_step(progress_bar)
    def message():
        print("  - Message only")
        signals.emit(Signal.SHOW_BUSY_MESSAGE, message="Just a message")

    print("\n- Overlay")
    message()


def run_tests():
    message: str
    try:
        assert len(STATE.projects) == 0
    except AssertionError:
        message = "Detected open projects! Try running the tests again once all open projects have been closed."
        signals.emit(
            Signal.SHOW_ERROR_MESSAGE,
            traceback=format_exc(),
            message=message,
        )
        print(message)
        return
    _initialize_window_functions()
    try:
        window: str
        for window in _WINDOW_FUNCTIONS:
            assert window in value_to_zhit_window, window
    except AssertionError:
        message = "Detected unsupported window function(s)!"
        signals.emit(
            Signal.SHOW_ERROR_MESSAGE,
            traceback=format_exc(),
            message=message,
        )
        print(message)
        return
    project: Optional[Project] = STATE.get_active_project()
    assert project is None
    global START_TIME
    START_TIME = time()
    selection_window()


def setup_tests():
    dpg.set_frame_callback(60, run_tests)
