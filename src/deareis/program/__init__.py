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

import dearpygui.dearpygui as dpg

dpg.create_context()

import matplotlib

matplotlib.use("Agg")

from json import (
    dumps as dump_json,
    load as load_json,
)
from multiprocessing import (
    Process,
    Queue,
    set_start_method,
)
from queue import Empty
from os import remove
from traceback import format_exc
from typing import (
    Dict,
    IO,
    List,
    Optional,
    Union,
)
from numpy import (
    array,
    ndarray,
)
from pyimpspec import (
    Circuit,
)
import pyimpspec
from pandas import DataFrame
from sympy import (
    Expr,
    latex,
    simplify,
)
from .project import (
    close_project,
    create_project_snapshot,
    load_project_files,
    new_project,
    restore_project_state,
    save_project,
    save_project_as,
    select_project_files,
)
from .overview import (
    rename_project,
    modify_project_notes,
)
from .data_sets import (
    apply_data_set_mask,
    delete_data_set,
    load_data_set_files,
    modify_data_set_path,
    rename_data_set,
    select_data_points_to_toggle,
    select_data_set,
    select_data_set_files,
    select_data_set_mask_to_copy,
    select_data_sets_to_average,
    select_impedance_to_subtract,
    toggle_data_point,
)
from .kramers_kronig import (
    apply_test_settings,
    delete_test_result,
    perform_test,
    select_test_result,
)
from .drt import (
    apply_drt_settings,
    delete_drt_result,
    perform_drt,
    select_drt_result,
)
from .fitting import (
    apply_fit_settings,
    delete_fit_result,
    perform_fit,
    select_fit_result,
)
from .simulation import (
    apply_simulation_settings,
    delete_simulation_result,
    perform_simulation,
    select_simulation_result,
)
from .plotting import (
    copy_plot_appearance_settings,
    delete_plot_settings,
    export_plot,
    modify_plot_series_theme,
    new_plot_settings,
    rename_plot_series,
    rename_plot_settings,
    reorder_plot_series,
    save_plot,
    select_plot_appearance_settings,
    select_plot_settings,
    select_plot_type,
    toggle_plot_series,
)
from .check_updates import perform_update_check
from deareis.gui.plots import show_modal_plot_window
from deareis.gui.changelog import show_changelog
from deareis.enums import (
    Context,
    DRTOutput,
    FitSimOutput,
    drt_output_to_label,
    label_to_drt_output,
    fit_sim_output_to_label,
)
from deareis.data import (
    DRTResult,
    DataSet,
    FitResult,
    Project,
    SimulationResult,
)
from deareis.arguments import (
    Namespace,
    parse as parse_arguments,
)
from deareis.gui import (
    ProjectTab,
)
from deareis.signals import Signal
import deareis.signals as signals
from deareis.state import STATE
from deareis.utility import (
    calculate_window_position_dimensions,
    pad_dataframe_dictionary,
)
from deareis.gui.plots import (
    Bode,
    BodeMagnitude,
    BodePhase,
    DRT,
    Impedance,
    ImpedanceReal,
    ImpedanceImaginary,
    Nyquist,
    Residuals,
)
from deareis.gui.plots.base import Plot
from deareis.gui.licenses import show_license_window
from deareis.gui.settings import (
    AppearanceSettings,
    KeybindingRemapping,
    show_defaults_settings_window,
)
import deareis.themes as themes
from deareis.version import PACKAGE_VERSION


# Hook into the progress callbacks implemented in pyimpspec
pyimpspec.progress.register(
    lambda *a, **k: signals.emit(Signal.SHOW_BUSY_MESSAGE, *a, **k)
)


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


def copy_output(*args, **kwargs):
    project: Optional[Project] = STATE.get_active_project()
    project_tab: Optional[ProjectTab] = STATE.get_active_project_tab()
    if project is None or project_tab is None:
        return
    output: Optional[Union[FitSimOutput, DRTOutput]] = kwargs.get("output")
    if output is None:
        return
    clipboard_content: str = ""
    if type(output) is FitSimOutput:
        fit_or_sim: Optional[Union[FitResult, SimulationResult]] = kwargs.get(
            "fit_or_sim"
        )
        data: Optional[DataSet] = kwargs.get("data")
        if fit_or_sim is None:
            return
        assert output in fit_sim_output_to_label, "Unsupported output!"
        signals.emit(Signal.SHOW_BUSY_MESSAGE, message="Generating output")
        if output == FitSimOutput.CDC_BASIC:
            clipboard_content = fit_or_sim.circuit.to_string()
        elif output == FitSimOutput.CDC_EXTENDED:
            clipboard_content = fit_or_sim.circuit.to_string(6)
        elif output == FitSimOutput.CSV_DATA_TABLE:
            Z_fit_or_sim: ndarray = fit_or_sim.get_impedance()
            dictionary: dict = {}
            if type(fit_or_sim) is FitResult:
                Z_exp: ndarray = data.get_impedance(masked=None)
                indices: ndarray = array(
                    [
                        _
                        for _ in range(0, data.get_num_points(masked=None))
                        if fit_or_sim.mask.get(_, False) is False
                    ]
                )
                dictionary = {
                    "f (Hz)": fit_or_sim.get_frequency(),
                    "Zre_exp (ohm)": Z_exp[indices].real,
                    "Zim_exp (ohm)": Z_exp[indices].imag,
                    "Zre_fit (ohm)": Z_fit_or_sim.real,
                    "Zim_fit (ohm)": Z_fit_or_sim.imag,
                }
            else:
                dictionary = {
                    "f (Hz)": fit_or_sim.get_frequency(),
                    "Zre_sim (ohm)": Z_fit_or_sim.real,
                    "Zim_sim (ohm)": Z_fit_or_sim.imag,
                }
            if dictionary:
                dataframe = DataFrame.from_dict(dictionary)
                clipboard_content = dataframe.to_csv(index=False)
        elif (
            output == FitSimOutput.CSV_PARAMETERS_TABLE
            or output == FitSimOutput.JSON_PARAMETERS_TABLE
            or output == FitSimOutput.LATEX_PARAMETERS_TABLE
            or output == FitSimOutput.MARKDOWN_PARAMETERS_TABLE
        ):
            dataframe = fit_or_sim.to_dataframe()
            if output == FitSimOutput.CSV_PARAMETERS_TABLE:
                clipboard_content = dataframe.to_csv(index=False)
            elif output == FitSimOutput.JSON_PARAMETERS_TABLE:
                clipboard_content = dataframe.to_json()
            elif output == FitSimOutput.LATEX_PARAMETERS_TABLE:
                clipboard_content = dataframe.to_latex(
                    index=False,
                    float_format="%.3g",
                )
            elif output == FitSimOutput.MARKDOWN_PARAMETERS_TABLE:
                clipboard_content = dataframe.to_markdown(
                    index=False,
                    floatfmt=".3g",
                )
        elif output == FitSimOutput.LATEX_DIAGRAM:
            clipboard_content = fit_or_sim.circuit.to_circuitikz()
        elif output == FitSimOutput.SVG_DIAGRAM:
            clipboard_content = (
                fit_or_sim.circuit.to_drawing().get_imagedata(fmt="svg").decode()
            )
        elif output == FitSimOutput.LATEX_EXPR:
            clipboard_content = latex(get_sympy_expr(fit_or_sim.circuit))
        elif (
            output == FitSimOutput.SYMPY_EXPR
            or output == FitSimOutput.SYMPY_EXPR_VALUES
        ):
            expr = get_sympy_expr(fit_or_sim.circuit)
            if output == FitSimOutput.SYMPY_EXPR:
                clipboard_content = str(expr)
            else:
                lines: List[str] = []
                lines.append(f'expr = sympify("{str(expr)}")')
                symbols: List[str] = list(sorted(map(str, expr.free_symbols)))
                if len(symbols) == 0:
                    clipboard_content = str(expr)
                else:
                    parameters = fit_or_sim.circuit.get_parameters()
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
                            for element in fit_or_sim.circuit.get_elements():
                                if not element.get_label().endswith(f"_{ident}"):
                                    continue
                                value = element.get_parameters().get(label)
                        assert value is not None
                        lines.append(f"\t{sym}: {value:.6E},")
                    lines.append("}")
                    clipboard_content = "\n".join(lines)
        else:
            raise Exception(f"Unsupported FitSimOutput: {output=}")
    elif type(output) is DRTOutput:
        assert output in drt_output_to_label, "Unsupported output!"
        drt: Optional[DRTResult] = kwargs.get("drt")
        if drt is None:
            return
        signals.emit(Signal.SHOW_BUSY_MESSAGE, message="Generating output")
        if (
            output == DRTOutput.CSV_SCORES
            or output == DRTOutput.JSON_SCORES
            or output == DRTOutput.LATEX_SCORES
            or output == DRTOutput.MARKDOWN_SCORES
        ):
            score_dataframe: Optional[DataFrame] = drt.get_score_dataframe(
                latex_labels=output == DRTOutput.LATEX_SCORES
            )
            if score_dataframe is not None:
                if output == DRTOutput.CSV_SCORES:
                    clipboard_content = score_dataframe.to_csv(index=False)
                elif output == DRTOutput.JSON_SCORES:
                    clipboard_content = score_dataframe.to_json()
                elif output == DRTOutput.LATEX_SCORES:
                    clipboard_content = score_dataframe.to_latex(
                        index=False,
                        escape=False,
                        float_format="%.3g",
                    )
                elif output == DRTOutput.MARKDOWN_SCORES:
                    clipboard_content = score_dataframe.to_markdown(
                        index=False,
                        floatfmt=".3g",
                    )
    else:
        raise Exception(f"Unsupported output type: {type(output)}")
    if clipboard_content != "":
        dpg.set_clipboard_text(clipboard_content)
    signals.emit(Signal.HIDE_BUSY_MESSAGE)


def undo(*args, **kwargs):
    project: Optional[Project] = STATE.get_active_project()
    project_tab: Optional[ProjectTab] = STATE.get_active_project_tab()
    if project is None or project_tab is None:
        return
    signals.emit(Signal.SHOW_BUSY_MESSAGE, message="Undoing")
    signals.emit(
        Signal.RESTORE_PROJECT_STATE,
        project=project,
        project_tab=project_tab,
        state_snapshot=STATE.get_previous_project_state_snapshot(project),
    )
    signals.emit(Signal.HIDE_BUSY_MESSAGE)


def redo(*args, **kwargs):
    project: Optional[Project] = STATE.get_active_project()
    project_tab: Optional[ProjectTab] = STATE.get_active_project_tab()
    if project is None or project_tab is None:
        return
    signals.emit(Signal.SHOW_BUSY_MESSAGE, message="Redoing")
    signals.emit(
        Signal.RESTORE_PROJECT_STATE,
        project=project,
        project_tab=project_tab,
        state_snapshot=STATE.get_next_project_state_snapshot(project),
    )
    signals.emit(Signal.HIDE_BUSY_MESSAGE)


def select_home_tab(*args, **kwargs):
    STATE.set_active_project(None)


def select_project_tab(*args, **kwargs):
    uuid: Optional[str] = kwargs.get("uuid")
    assert type(uuid) is str or uuid is None
    STATE.set_active_project(uuid)
    signals.emit(
        Signal.VIEWPORT_RESIZED,
        width=dpg.get_viewport_width(),
        height=dpg.get_viewport_height(),
    )


def viewport_resized(width: int, height: int):
    STATE.program_window.busy_message.resize(width, height)
    STATE.program_window.error_message.resize(width, height)
    project_tab: Optional[ProjectTab] = STATE.get_active_project_tab()
    if project_tab is not None:
        project_tab.resize(width, height)
    modal_window: Optional[int] = STATE.get_active_modal_window()
    if modal_window is None or not dpg.does_item_exist(modal_window):
        return
    elif modal_window in [
        STATE.program_window.busy_message.window,
        STATE.program_window.error_message.window,
    ]:
        return
    item_configuration: dict = dpg.get_item_configuration(modal_window)
    if item_configuration.get("no_move", False):
        return
    x: int
    y: int
    w: int
    h: int
    if item_configuration.get("no_resize", False):
        x, y, w, h = calculate_window_position_dimensions(
            dpg.get_item_width(modal_window), dpg.get_item_height(modal_window)
        )
    else:
        x, y, w, h = calculate_window_position_dimensions()
    if "mvFileDialog" in dpg.get_item_type(modal_window):
        dpg.configure_item(
            modal_window,
            width=w,
            height=h,
        )
    else:
        dpg.configure_item(
            modal_window,
            pos=(
                x,
                y,
            ),
            width=w,
            height=h,
        )


def show_enlarged_plot(*args, **kwargs):
    plot: Optional[Plot] = kwargs.get("plot")
    adjust_limits: bool = kwargs.get("adjust_limits", True)
    if plot is None or plot.is_blank():
        return
    show_modal_plot_window(plot, adjust_limits=adjust_limits)


def copy_plot_data(*args, **kwargs):
    plot: Optional[Plot] = kwargs.get("plot")
    context: Optional[Context] = kwargs.get("context")
    if plot is None or plot.is_blank() or context is None:
        return
    dictionary: dict = {}
    series: dict
    label: str
    key: str
    if type(plot) is Bode:
        for series in plot.get_series():
            label = "Data"
            if series.get("simulation", False):
                label = "Sim."
            elif series.get("fit", False):
                label = "Fit"
            if series.get("line", False):
                label += " (line)"
            else:
                label += " (scatter)"
            key = f"f (Hz) - {label}"
            while key in dictionary:
                label += " "
                key = f"f (Hz) - {label}"
            dictionary[key] = series["frequency"]
            dictionary[f"|Z| (ohm) - {label}"] = series["magnitude"]
            dictionary[f"-phi (°) - {label}"] = series["phase"]
    elif type(plot) is Nyquist:
        for series in plot.get_series():
            label = "Data"
            if context != Context.PLOTTING_TAB:
                if series.get("simulation", False):
                    label = "Sim."
                elif series.get("fit", False):
                    label = "Fit"
            else:
                label = series.get("label") or ""
            if series.get("line", False):
                label += " (line)"
            else:
                label += " (scatter)"
            key = f"Zre (ohm) - {label}"
            while key in dictionary:
                label += " "
                key = f"Zre (ohm) - {label}"
            dictionary[key] = series["real"]
            dictionary[f"-Zim (ohm) - {label}"] = series["imaginary"]
    elif type(plot) is BodeMagnitude:
        for series in plot.get_series():
            label = "Data"
            if context != Context.PLOTTING_TAB:
                if series.get("simulation", False):
                    label = "Sim."
                elif series.get("fit", False):
                    label = "Fit"
            else:
                label = series.get("label") or ""
            if series.get("line", False):
                label += " (line)"
            else:
                label += " (scatter)"
            key = f"f (Hz) - {label}"
            while key in dictionary:
                label += " "
                key = f"f (Hz) - {label}"
            dictionary[key] = series["frequency"]
            dictionary[f"|Z| (ohm) - {label}"] = series["magnitude"]
    elif type(plot) is BodePhase:
        for series in plot.get_series():
            label = "Data"
            if context != Context.PLOTTING_TAB:
                if series.get("simulation", False):
                    label = "Sim."
                elif series.get("fit", False):
                    label = "Fit"
            else:
                label = series.get("label") or ""
            if series.get("line", False):
                label += " (line)"
            else:
                label += " (scatter)"
            key = f"f (Hz) - {label}"
            while key in dictionary:
                label += " "
                key = f"f (Hz) - {label}"
            dictionary[key] = series["frequency"]
            dictionary[f"-phi (°) - {label}"] = series["phase"]
    elif type(plot) is Residuals:
        for series in plot.get_series():
            dictionary["f (Hz)"] = series["frequency"]
            dictionary["real error (%)"] = series["real"]
            dictionary["imaginary error (%)"] = series["imaginary"]
    elif type(plot) is DRT:
        for series in plot.get_series():
            label = "Data"
            if context != Context.PLOTTING_TAB:
                if series.get("simulation", False):
                    label = "Sim."
                elif series.get("fit", False):
                    label = "Fit"
            else:
                label = series.get("label") or ""
            key = f"tau (s) - {label}"
            while key in dictionary:
                label += " "
                key = f"tau (s) - {label}"
            dictionary[key] = series["tau"]
            if "gamma" in series:
                dictionary[f"gamma (ohm) - {label}"] = series["gamma"]
            elif "imaginary" in series:
                if f"gamma (ohm) - {label}" in dictionary:
                    dictionary[f"gamma, real (ohm) - {label}"] = dictionary[
                        "gamma (ohm) - {label}"
                    ]
                    del dictionary[f"gamma (ohm) - {label}"]
                dictionary[f"gamma, imag. (ohm) - {label}"] = series["imaginary"]
            elif "mean" in series:
                dictionary[f"gamma, mean (ohm) - {label}"] = series["mean"]
            elif "lower" in series and "upper" in series:
                dictionary[f"gamma, lower bound (ohm) - {label}"] = series["lower"]
                dictionary[f"gamma, upper bound (ohm) - {label}"] = series["lower"]
    elif type(plot) is Impedance:
        for series in plot.get_series():
            label = "Data"
            if context != Context.PLOTTING_TAB:
                if series.get("simulation", False):
                    label = "Sim."
                elif series.get("fit", False):
                    label = "Fit"
            else:
                label = series.get("label") or ""
            key = f"f (Hz) - {label}"
            while key in dictionary:
                label += " "
                key = f"f (Hz) - {label}"
            dictionary[key] = series["frequency"]
            dictionary["Zre (ohm)"] = series["real"]
            dictionary["-Zim (ohm)"] = series["imaginary"]
    elif type(plot) is ImpedanceReal or type(plot) is ImpedanceImaginary:
        for series in plot.get_series():
            label = "Data"
            if context != Context.PLOTTING_TAB:
                if series.get("simulation", False):
                    label = "Sim."
                elif series.get("fit", False):
                    label = "Fit"
            else:
                label = series.get("label") or ""
            key = f"f (Hz) - {label}"
            while key in dictionary:
                label += " "
                key = f"f (Hz) - {label}"
            dictionary[key] = series["x"]
            if type(plot) is ImpedanceReal:
                dictionary[f"Zre (ohm) - {label}"] = series["y"]
            else:
                dictionary[f"-Zim (ohm) - {label}"] = series["y"]
    padded_dictionary: Optional[dict] = pad_dataframe_dictionary(dictionary)
    if padded_dictionary is None:
        dpg.set_clipboard_text("")
    else:
        dpg.set_clipboard_text(
            DataFrame.from_dict(padded_dictionary).to_csv(index=False)
        )


def show_help_about(*args, **kwargs):
    x: int
    y: int
    w: int
    h: int
    x, y, w, h = calculate_window_position_dimensions(270, 100)
    window: int = dpg.generate_uuid()
    key_handler: int = dpg.generate_uuid()

    def close_window():
        if dpg.does_item_exist(window):
            dpg.delete_item(window)
        if dpg.does_item_exist(key_handler):
            dpg.delete_item(key_handler)
        signals.emit(Signal.UNBLOCK_KEYBINDINGS)

    with dpg.handler_registry(tag=key_handler):
        dpg.add_key_release_handler(
            key=dpg.mvKey_Escape,
            callback=close_window,
        )

    with dpg.window(
        label="About",
        modal=True,
        pos=(
            x,
            y,
        ),
        width=w,
        height=h,
        no_resize=True,
        on_close=close_window,
        tag=window,
    ):
        dpg.add_text(f"DearEIS ({PACKAGE_VERSION})")
        dpg.bind_item_theme(
            dpg.add_input_text(
                default_value="https://vyrjana.github.io/DearEIS",
                enabled=False,
                width=-1,
            ),
            themes.url_theme,
        )
        dpg.bind_item_theme(
            dpg.add_input_text(
                default_value="https://github.com/vyrjana/DearEIS",
                enabled=False,
                width=-1,
            ),
            themes.url_theme,
        )
    signals.emit(Signal.BLOCK_KEYBINDINGS, window=window, window_object=None)


def restore_unsaved_project_snapshots():
    parsing_errors: Dict[str, str] = {}
    unsaved_project_snapshots: List[str] = STATE.get_unsaved_project_snapshots()
    path: str
    for path in unsaved_project_snapshots:
        try:
            fp: IO
            with open(path, "r") as fp:
                project: Project = Project.from_dict(load_json(fp))
        except Exception:
            parsing_errors[path] = format_exc()
            continue
        project_tab, _ = STATE.add_project(project)
        STATE.program_window.select_tab(project_tab)
        signals.emit(Signal.SELECT_PROJECT_TAB, uuid=project.uuid)
        STATE.snapshot_project_state(project)
        signals.emit(
            Signal.RESTORE_PROJECT_STATE,
            project=project,
            project_tab=project_tab,
            state_snapshot=dump_json(project.to_dict(session=True)),
        )
    for path in unsaved_project_snapshots:
        if path not in parsing_errors:
            remove(path)
    if parsing_errors:
        total_traceback: str = ""
        traceback: str
        for path, traceback in parsing_errors.items():
            total_traceback += f"{traceback}\nThe exception above was encountered while parsing '{path}'.\n\n"
        signals.emit(
            Signal.SHOW_ERROR_MESSAGE,
            traceback=total_traceback.strip(),
            message="""
Encountered error(s) while parsing project file(s). The file(s) might be malformed, corrupted, or simply a newer version than is supported by this version of DearEIS.
            """.strip(),
        )


def initialize_program(args: Namespace):
    assert type(args) is Namespace
    signals.register(Signal.VIEWPORT_RESIZED, viewport_resized)
    dpg.set_primary_window(STATE.program_window.window, True)
    dpg.set_viewport_resize_callback(
        lambda: signals.emit(
            Signal.VIEWPORT_RESIZED,
            width=dpg.get_viewport_width(),
            height=dpg.get_viewport_height(),
        )
    )
    signals.register(
        Signal.BLOCK_KEYBINDINGS,
        lambda *a, **k: STATE.keybinding_handler.block(),
    )
    signals.register(Signal.BLOCK_KEYBINDINGS, STATE.set_active_modal_window)
    signals.register(Signal.UNBLOCK_KEYBINDINGS, STATE.keybinding_handler.unblock)
    # Signals that should cause program/project keybindings to be ignored
    # (e.g. when modal windows are shown).
    signals.register(
        Signal.SHOW_BUSY_MESSAGE,
        lambda *a, **k: signals.emit(
            Signal.BLOCK_KEYBINDINGS,
            window=STATE.program_window.busy_message.window,
            window_object=None,
        ),
    )
    signals.register(
        Signal.HIDE_BUSY_MESSAGE,
        lambda: signals.emit(Signal.UNBLOCK_KEYBINDINGS),
    )
    signals.register(
        Signal.SHOW_ERROR_MESSAGE,
        lambda *a, **k: signals.emit(
            Signal.BLOCK_KEYBINDINGS,
            window=STATE.program_window.error_message.window,
            window_object=None,
        ),
    )
    # Signals for showing/hiding the modal windows for error messages and for indicating when the
    # program is busy e.g. performing a fit.
    signals.register(Signal.SHOW_BUSY_MESSAGE, STATE.program_window.busy_message.show)
    signals.register(Signal.HIDE_BUSY_MESSAGE, STATE.program_window.busy_message.hide)
    signals.register(
        Signal.SHOW_ERROR_MESSAGE,
        lambda *a, **k: STATE.program_window.busy_message.hide(),
    )
    signals.register(Signal.SHOW_ERROR_MESSAGE, STATE.program_window.error_message.show)
    signals.register(Signal.SHOW_COMMAND_PALETTE, STATE.show_command_palette)
    # Settings and help windows
    signals.register(Signal.SHOW_HELP_ABOUT, show_help_about)
    signals.register(Signal.SHOW_HELP_LICENSES, show_license_window)
    signals.register(Signal.SHOW_SETTINGS_APPEARANCE, lambda: AppearanceSettings())
    signals.register(
        Signal.SHOW_SETTINGS_DEFAULTS, lambda: show_defaults_settings_window(STATE)
    )
    signals.register(
        Signal.SHOW_SETTINGS_KEYBINDINGS, lambda: KeybindingRemapping(STATE)
    )
    # Home tab state
    signals.register(Signal.SELECT_HOME_TAB, select_home_tab)
    STATE.set_recent_projects(paths=STATE.get_recent_projects())
    # Plots
    signals.register(Signal.SHOW_ENLARGED_PLOT, show_enlarged_plot)
    signals.register(Signal.COPY_PLOT_DATA, copy_plot_data)
    # Signals for dealing with projects and project files.
    signals.register(Signal.NEW_PROJECT, new_project)
    signals.register(Signal.SELECT_PROJECT_FILES, select_project_files)
    signals.register(Signal.LOAD_PROJECT_FILES, load_project_files)
    signals.register(Signal.RESTORE_PROJECT_STATE, restore_project_state)
    signals.register(Signal.RENAME_PROJECT, rename_project)
    signals.register(Signal.CLOSE_PROJECT, close_project)
    signals.register(Signal.SAVE_PROJECT, save_project)
    signals.register(Signal.SAVE_PROJECT_AS, save_project_as)
    signals.register(Signal.SELECT_PROJECT_TAB, select_project_tab)
    signals.register(Signal.CREATE_PROJECT_SNAPSHOT, create_project_snapshot)
    signals.register(Signal.UNDO_PROJECT_ACTION, undo)
    signals.register(Signal.REDO_PROJECT_ACTION, redo)
    signals.register(Signal.MODIFY_PROJECT_NOTES, modify_project_notes)
    signals.register(Signal.CLEAR_RECENT_PROJECTS, STATE.clear_recent_projects)
    # Signals for the data sets tab
    signals.register(Signal.LOAD_DATA_SET_FILES, load_data_set_files)
    signals.register(Signal.SELECT_DATA_SET, select_data_set)
    signals.register(Signal.SELECT_DATA_SET_FILES, select_data_set_files)
    signals.register(Signal.RENAME_DATA_SET, rename_data_set)
    signals.register(Signal.MODIFY_DATA_SET_PATH, modify_data_set_path)
    signals.register(Signal.DELETE_DATA_SET, delete_data_set)
    signals.register(Signal.SELECT_DATA_SETS_TO_AVERAGE, select_data_sets_to_average)
    signals.register(Signal.SELECT_DATA_POINTS_TO_TOGGLE, select_data_points_to_toggle)
    signals.register(Signal.SELECT_DATA_SET_MASK_TO_COPY, select_data_set_mask_to_copy)
    signals.register(Signal.SELECT_IMPEDANCE_TO_SUBTRACT, select_impedance_to_subtract)
    signals.register(Signal.TOGGLE_DATA_POINT, toggle_data_point)
    signals.register(Signal.APPLY_DATA_SET_MASK, apply_data_set_mask)
    # Signals for the Kramers-Kronig tab
    signals.register(Signal.PERFORM_TEST, perform_test)
    signals.register(Signal.SELECT_TEST_RESULT, select_test_result)
    signals.register(Signal.DELETE_TEST_RESULT, delete_test_result)
    signals.register(Signal.APPLY_TEST_SETTINGS, apply_test_settings)
    # Signals for the DRT tab
    signals.register(Signal.PERFORM_DRT, perform_drt)
    signals.register(Signal.SELECT_DRT_RESULT, select_drt_result)
    signals.register(Signal.DELETE_DRT_RESULT, delete_drt_result)
    signals.register(Signal.APPLY_DRT_SETTINGS, apply_drt_settings)
    # Signals for the fitting tab
    signals.register(Signal.PERFORM_FIT, perform_fit)
    signals.register(Signal.SELECT_FIT_RESULT, select_fit_result)
    signals.register(Signal.COPY_OUTPUT, copy_output)
    signals.register(Signal.DELETE_FIT_RESULT, delete_fit_result)
    signals.register(Signal.APPLY_FIT_SETTINGS, apply_fit_settings)
    # Signals for the simulation tab
    signals.register(Signal.PERFORM_SIMULATION, perform_simulation)
    signals.register(Signal.SELECT_SIMULATION_RESULT, select_simulation_result)
    signals.register(Signal.DELETE_SIMULATION_RESULT, delete_simulation_result)
    signals.register(Signal.APPLY_SIMULATION_SETTINGS, apply_simulation_settings)
    # Signals for the plotting tab
    signals.register(Signal.NEW_PLOT_SETTINGS, new_plot_settings)
    signals.register(Signal.SELECT_PLOT_SETTINGS, select_plot_settings)
    signals.register(Signal.SELECT_PLOT_TYPE, select_plot_type)
    signals.register(Signal.DELETE_PLOT_SETTINGS, delete_plot_settings)
    signals.register(Signal.TOGGLE_PLOT_SERIES, toggle_plot_series)
    signals.register(Signal.RENAME_PLOT_SETTINGS, rename_plot_settings)
    signals.register(Signal.RENAME_PLOT_SERIES, rename_plot_series)
    signals.register(Signal.REORDER_PLOT_SERIES, reorder_plot_series)
    signals.register(Signal.MODIFY_PLOT_SERIES_THEME, modify_plot_series_theme)
    signals.register(
        Signal.SELECT_PLOT_APPEARANCE_SETTINGS, select_plot_appearance_settings
    )
    signals.register(
        Signal.COPY_PLOT_APPEARANCE_SETTINGS, copy_plot_appearance_settings
    )
    signals.register(Signal.EXPORT_PLOT, export_plot)
    signals.register(Signal.SAVE_PLOT, save_plot)
    signals.register(Signal.CHECK_UPDATES, perform_update_check)
    signals.register(Signal.SHOW_CHANGELOG, show_changelog)
    # signals.register(Signal., )
    if args.data_files:
        signals.emit(Signal.NEW_PROJECT, data=args.data_files)
    if args.project_files:
        signals.emit(Signal.LOAD_PROJECT_FILES, paths=args.project_files)
    restore_unsaved_project_snapshots()
    signals.emit_backlog()
    STATE.check_version()


def program_closing():
    dirty_projects: List[Project] = list(
        filter(
            lambda _: STATE.is_project_dirty(_)
            and STATE.get_project_tab(_) is not None,
            STATE.projects,
        )
    )
    STATE.serialize_project_snapshots(dirty_projects)
    clean_projects: List[Project] = list(
        filter(
            lambda _: not STATE.is_project_dirty(_)
            and STATE.get_project_tab(_) is not None,
            STATE.projects,
        )
    )
    STATE.clear_project_backups(clean_projects)
    STATE.save_recent_projects()
    STATE.config.save()


def main():
    set_start_method("spawn")
    args: Namespace = parse_arguments()
    dpg.create_viewport(title="DearEIS")
    dpg.set_viewport_min_width(800)
    dpg.set_viewport_min_height(600)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    # dpg.show_style_editor()
    # dpg.show_item_registry()
    try:
        dpg.set_frame_callback(1, lambda: initialize_program(args))
        dpg.set_exit_callback(program_closing)
        dpg.start_dearpygui()
    except Exception:
        print(format_exc())
    finally:
        dpg.destroy_context()


def debug():
    # This function is called by one of the entry points defined in setup.py.
    print("Enabling debugging features...")
    signals.DEBUG = True
    main()


if __name__ == "__main__":
    main()
