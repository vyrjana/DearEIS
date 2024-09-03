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

from cmath import rect
from typing import (
    Callable,
    Dict,
    List,
    Optional,
    Tuple,
)
import dearpygui.dearpygui as dpg
from numpy import (
    angle,
    array,
    empty,
    flip,
    float64,
    isclose,
    log10 as log,
    ndarray,
)
from numpy.typing import NDArray
from scipy.interpolate import Akima1DInterpolator
from statsmodels.nonparametric.smoothers_lowess import lowess
from pyimpspec import (
    ComplexImpedance,
    ComplexImpedances,
    Frequencies,
    Impedances,
)
from deareis.data import DataSet
from deareis.gui.plots import (
    BodeMagnitude,
    BodePhase,
    Nyquist,
)
from deareis.signals import Signal
from deareis.utility import (
    align_numbers,
    calculate_window_position_dimensions,
    format_number,
    pad_tab_labels,
)
import deareis.signals as signals
import deareis.themes as themes
from deareis.tooltips import (
    attach_tooltip,
    update_tooltip,
)
import deareis.tooltips as tooltips
from deareis.state import STATE
from deareis.enums import Action
from deareis.keybindings import (
    Keybinding,
    TemporaryKeybindingHandler,
)


class InterpolatePoints:
    def __init__(
        self,
        data: DataSet,
        callback: Callable,
    ):
        assert isinstance(data, DataSet), data
        assert callable(callback), callback
        self.original_data: DataSet = DataSet.from_dict(data.to_dict())
        self.smoothed_data: DataSet = DataSet.from_dict(data.to_dict())
        self.smoothed_data.set_mask({})
        self.preview_data: DataSet = DataSet.from_dict(data.to_dict())
        self.preview_data.set_mask({})
        self.callback: Callable = callback
        self.create_window()
        self.register_keybindings()
        self.update_smoothing()
        self.nyquist_plot.queue_limits_adjustment()
        self.magnitude_plot.queue_limits_adjustment()
        self.phase_plot.queue_limits_adjustment()

    def register_keybindings(self):
        callbacks: Dict[Keybinding, Callable] = {}
        # Cancel
        kb: Keybinding = Keybinding(
            key=dpg.mvKey_Escape,
            mod_alt=False,
            mod_ctrl=False,
            mod_shift=False,
            action=Action.CANCEL,
        )
        callbacks[kb] = self.close
        # Accept
        for kb in STATE.config.keybindings:
            if kb.action is Action.PERFORM_ACTION:
                break
        else:
            kb = Keybinding(
                key=dpg.mvKey_Return,
                mod_alt=True,
                mod_ctrl=False,
                mod_shift=False,
                action=Action.PERFORM_ACTION,
            )
        callbacks[kb] = self.accept
        # Previous plot tab
        for kb in STATE.config.keybindings:
            if kb.action is Action.PREVIOUS_PLOT_TAB:
                break
        else:
            kb = Keybinding(
                key=dpg.mvKey_Prior,
                mod_alt=True,
                mod_ctrl=False,
                mod_shift=True,
                action=Action.PREVIOUS_PLOT_TAB,
            )
        callbacks[kb] = lambda: self.cycle_plot_tab(step=-1)
        # Next plot tab
        for kb in STATE.config.keybindings:
            if kb.action is Action.NEXT_PLOT_TAB:
                break
        else:
            kb = Keybinding(
                key=dpg.mvKey_Next,
                mod_alt=True,
                mod_ctrl=False,
                mod_shift=True,
                action=Action.NEXT_PLOT_TAB,
            )
        callbacks[kb] = lambda: self.cycle_plot_tab(step=1)
        # Create the handler
        self.keybinding_handler: TemporaryKeybindingHandler = (
            TemporaryKeybindingHandler(callbacks=callbacks)
        )

    def create_window(self):
        x: int
        y: int
        w: int
        h: int
        x, y, w, h = calculate_window_position_dimensions()
        self.window: int = dpg.generate_uuid()
        with dpg.window(
            label="Interpolate points",
            modal=True,
            pos=(
                x,
                y,
            ),
            width=w,
            height=h,
            tag=self.window,
            on_close=self.close,
        ):
            with dpg.group(horizontal=True):
                self.table_window: int = dpg.generate_uuid()
                with dpg.child_window(
                    border=False,
                    width=500,
                    tag=self.table_window,
                ):
                    self.create_table()
                    dpg.add_button(
                        label="Accept".ljust(12),
                        callback=self.accept,
                    )
                self.create_plots()

    def create_table(self):
        with dpg.group(horizontal=True):
            dpg.add_text("Num. points")
            attach_tooltip(tooltips.zhit.num_points)
            self.num_points_input: int = dpg.generate_uuid()
            dpg.add_input_int(
                default_value=5,
                min_value=2,
                min_clamped=True,
                max_value=self.original_data.get_num_points(),
                max_clamped=True,
                step=0,
                callback=self.update_smoothing,
                on_enter=True,
                width=100,
                tag=self.num_points_input,
            )
            dpg.add_text("Num. iterations")
            attach_tooltip(tooltips.zhit.num_iterations)
            self.num_iterations_input: int = dpg.generate_uuid()
            dpg.add_input_int(
                default_value=3,
                min_value=1,
                min_clamped=True,
                max_value=100,
                max_clamped=True,
                step=0,
                callback=self.update_smoothing,
                on_enter=True,
                width=100,
                tag=self.num_iterations_input,
            )
            self.smooth_polar_checkbox: int = dpg.generate_uuid()
            dpg.add_checkbox(
                label="Polar",
                default_value=True,
                callback=self.update_smoothing,
                tag=self.smooth_polar_checkbox,
            )
            attach_tooltip(tooltips.data_sets.interpolation_smooth_polar)
        self.table = dpg.generate_uuid()
        with dpg.table(
            borders_outerV=True,
            borders_outerH=True,
            borders_innerV=True,
            borders_innerH=True,
            scrollY=True,
            freeze_rows=1,
            height=-24,
            tag=self.table,
        ):
            dpg.add_table_column(
                label="?",
                width_fixed=True,
            )
            attach_tooltip(tooltips.data_sets.interpolation_toggle)
            dpg.add_table_column(
                label="Index",
                width_fixed=True,
            )
            dpg.add_table_column(
                label="f (Hz)",
            )
            attach_tooltip(tooltips.data_sets.frequency)
            dpg.add_table_column(
                label="Re(Z) (ohm)",
            )
            attach_tooltip(tooltips.data_sets.real)
            dpg.add_table_column(
                label="-Im(Z) (ohm)",
            )
            attach_tooltip(tooltips.data_sets.imaginary)
            dpg.add_table_column(
                label="Mod(Z) (ohm)",
            )
            attach_tooltip(tooltips.data_sets.magnitude)
            dpg.add_table_column(
                label="-Phase(Z) (°)",
            )
            attach_tooltip(tooltips.data_sets.phase)
        num_points: int = self.original_data.get_num_points(masked=None)
        i: int
        for i in range(0, num_points):
            with dpg.table_row(parent=self.table):
                dpg.add_checkbox(
                    default_value=False,
                    callback=lambda s, a, u: self.toggle_point(u, a),
                    user_data=i,
                )
                dpg.add_text("")  # Index
                dpg.set_item_user_data(
                    dpg.add_text(""),
                    attach_tooltip(""),
                )  # f
                dpg.set_item_user_data(
                    dpg.add_input_text(
                        hint="?",
                        scientific=True,
                        width=-1,
                        callback=lambda s, a, u: self.modify_override(u, a),
                        on_enter=True,
                    ),
                    attach_tooltip(""),
                )  # Re(Z)
                dpg.set_item_user_data(
                    dpg.add_input_text(
                        hint="?",
                        scientific=True,
                        width=-1,
                        callback=lambda s, a, u: self.modify_override(u, a),
                        on_enter=True,
                    ),
                    attach_tooltip(""),
                )  # -Im(Z)
                dpg.set_item_user_data(
                    dpg.add_text(""),
                    attach_tooltip(""),
                )  # Mod(Z)
                dpg.set_item_user_data(
                    dpg.add_text(""),
                    attach_tooltip(""),
                )  # Phase(Z)

    def create_plots(self):
        settings: List[dict] = [
            {
                "label": "Before",
                "theme": themes.nyquist.data,
                "show_label": False,
            },
            {
                "label": "Before",
                "line": True,
                "theme": themes.nyquist.data,
            },
            {
                "label": "Masked",
                "theme": themes.residuals.imaginary,
            },
            {
                "label": "Smoothed",
                "line": True,
                "theme": themes.residuals.real,
            },
            {
                "label": "After",
                "theme": themes.bode.phase_data,
                "show_label": False,
            },
            {
                "label": "After",
                "line": True,
                "theme": themes.bode.phase_data,
            },
        ]
        self.preview_window: int = dpg.generate_uuid()
        with dpg.child_window(border=False, tag=self.preview_window):
            self.plot_tab_bar: int = dpg.generate_uuid()
            with dpg.tab_bar(tag=self.plot_tab_bar):
                self.create_nyquist_plot(settings)
                self.create_magnitude_plot(settings)
                self.create_phase_plot(settings)
            pad_tab_labels(self.plot_tab_bar)

    def create_nyquist_plot(self, settings: List[dict]):
        with dpg.tab(label="Nyquist"):
            self.nyquist_plot: Nyquist = Nyquist(width=-1, height=-1)
            for kwargs in settings:
                self.nyquist_plot.plot(
                    real=array([]),
                    imaginary=array([]),
                    **kwargs,
                )

    def create_magnitude_plot(self, settings: List[dict]):
        with dpg.tab(label="Bode - magnitude"):
            self.magnitude_plot: BodeMagnitude = BodeMagnitude(width=-1, height=-1)
            for kwargs in settings:
                self.magnitude_plot.plot(
                    frequency=array([]),
                    magnitude=array([]),
                    **kwargs,
                )

    def create_phase_plot(self, settings: List[dict]):
        with dpg.tab(label="Bode - phase"):
            self.phase_plot: BodePhase = BodePhase(width=-1, height=-1)
            for kwargs in settings:
                self.phase_plot.plot(
                    frequency=array([]),
                    phase=array([]),
                    **kwargs,
                )

    def close(self):
        dpg.hide_item(self.window)
        dpg.delete_item(self.window)
        self.keybinding_handler.delete()
        signals.emit(Signal.UNBLOCK_KEYBINDINGS)

    def accept(self):
        mask: Dict[int, bool] = self.get_mask()
        mask.update({_: True for _ in self.get_overrides().keys()})
        for modified in mask.values():
            if modified is True:
                break
        else:
            self.close()
            return
        dictionary: dict = self.preview_data.to_dict()
        del dictionary["uuid"]
        data: DataSet = DataSet.from_dict(dictionary)
        data.set_label(f"{self.preview_data.get_label()} - interpolated")
        self.callback(data)
        self.close()

    def toggle_point(self, index: int, state: bool):
        rows: List[int] = dpg.get_item_children(self.table, slot=1)
        inputs: Tuple[int, int] = self.get_inputs(rows[index])
        if state is True:
            dpg.disable_item(inputs[0])
            dpg.disable_item(inputs[1])
        else:
            dpg.set_value(inputs[0], "")
            dpg.set_value(inputs[1], "")
            dpg.enable_item(inputs[0])
            dpg.enable_item(inputs[1])
        self.update_table(index=index, state=state)
        self.update_plots()

    def modify_override(self, index: int, value: str):
        self.update_table()
        self.update_plots()

    def get_checkbox(self, row: int) -> int:
        return dpg.get_item_children(row, slot=1)[0]

    def get_inputs(self, row: int) -> Tuple[int, int]:
        cells: List[int] = dpg.get_item_children(row, slot=1)
        return (
            cells[4],
            cells[6],
        )

    def get_mask(self) -> Dict[int, bool]:
        mask: Dict[int, bool] = {}
        rows: List[int] = dpg.get_item_children(self.table, slot=1)
        i: int
        row: int
        for i, row in enumerate(rows):
            mask[i] = dpg.get_value(self.get_checkbox(rows[i]))
        return mask

    def get_real_input(self, row: int) -> int:
        return dpg.get_item_children(row, slot=1)[4]

    def get_imaginary_input(self, row: int) -> int:
        return dpg.get_item_children(row, slot=1)[6]

    def get_rows(self) -> List[int]:
        return dpg.get_item_children(self.table, slot=1)

    def get_overrides(self) -> Dict[int, ComplexImpedance]:
        overrides: Dict[int, ComplexImpedance] = {}
        rows: List[int] = self.get_rows()
        i: int
        row: int
        Z: ComplexImpedance
        for i, (row, Z) in enumerate(
            zip(rows, self.original_data.get_impedances(masked=None))
        ):
            re: str = dpg.get_value(self.get_real_input(row))
            im: str = dpg.get_value(self.get_imaginary_input(row))
            if re != "" or im != "":
                real: float = float(re) if re != "" else Z.real
                imag: float = -float(im) if im != "" else Z.imag
                overrides[i] = ComplexImpedance(real + imag * 1j)
        return overrides

    def get_impedances(self, mask: Dict[int, bool] = {}) -> ComplexImpedances:
        if not mask:
            mask = self.get_mask()
        overrides: Dict[int, ComplexImpedance] = self.get_overrides()
        Z: ComplexImpedances = self.original_data.get_impedances(masked=None)
        smooth_Z: ComplexImpedances = self.smoothed_data.get_impedances(masked=None)
        results: ComplexImpedances = empty(
            Z.shape,
            dtype=Z.dtype,
        )
        i: int
        state: bool
        for i, state in mask.items():
            if state is True:
                results[i] = smooth_Z[i]
            elif i in overrides:
                results[i] = overrides[i]
            else:
                results[i] = Z[i]
        return results

    def update_table(self, index: int = -1, state: Optional[bool] = None):
        if index >= 0:
            assert isinstance(state, bool), state
        else:
            assert state is None, state
        original_f: Frequencies = self.original_data.get_frequencies(masked=None)
        original_Z: ComplexImpedances = self.original_data.get_impedances(masked=None)
        mask: Dict[int, bool] = self.get_mask()
        Z: ComplexImpedances = self.get_impedances(mask)
        f: List[str] = list(
            map(
                lambda _: format_number(_, significants=4),
                self.original_data.get_frequencies(masked=None),
            )
        )
        re_Z: List[str] = list(
            map(
                lambda _: format_number(
                    _.real,
                    significants=4,
                ),
                Z,
            )
        )
        im_Z: List[str] = list(map(lambda _: format_number(-_.imag, significants=4), Z))
        mod_Z: List[str] = list(
            map(
                lambda _: format_number(
                    abs(_),
                    significants=4,
                ),
                Z,
            )
        )
        phase_Z: List[str] = list(
            map(
                lambda _: format_number(
                    -angle(_, deg=True),  # type: ignore
                    significants=4,
                    exponent=False,
                ),
                Z,
            )
        )
        indices: List[str] = list(map(lambda _: str(_ + 1), range(0, len(Z))))
        indices = align_numbers(indices)
        f = align_numbers(f)
        re_Z = align_numbers(re_Z)
        im_Z = align_numbers(im_Z)
        mod_Z = align_numbers(mod_Z)
        phase_Z = align_numbers(phase_Z)
        fmt: str = "{:.6E}"

        def get_cell_and_tooltip(cells: List[int], index: int) -> Tuple[int, int]:
            assert 0 <= index < 7
            if index < 2:
                return (
                    cells[index],
                    -1,
                )
            index = (index - 2) * 2 + 2
            return (
                cells[index],
                dpg.get_item_user_data(cells[index]),
            )

        rows: List[int] = dpg.get_item_children(self.table, slot=1)
        i: int
        row: int
        for i, row in enumerate(rows):
            if index >= 0 and i != index:
                continue
            cells: List[int] = dpg.get_item_children(row, slot=1)
            cell: int
            tooltip: int
            dpg.set_value(cells[0], mask[i])
            dpg.set_value(cells[1], indices[i])
            cell, tooltip = get_cell_and_tooltip(cells, 2)
            dpg.set_value(cell, f[i])
            update_tooltip(tooltip, fmt.format(original_f[i]))
            cell, tooltip = get_cell_and_tooltip(cells, 3)
            dpg.configure_item(cell, hint=re_Z[i])
            if mask[i] is True:
                dpg.set_value(cell, format_number(Z[i].real))
            update_tooltip(
                tooltip,
                fmt.format(original_Z[i].real)
                + (
                    (
                        " -> " + fmt.format(Z[i].real)
                        if not isclose(original_Z[i], Z[i])
                        else ""
                    )
                ),
            )
            cell, tooltip = get_cell_and_tooltip(cells, 4)
            dpg.configure_item(cell, hint=im_Z[i])
            if mask[i] is True:
                dpg.set_value(cell, format_number(-Z[i].imag))
            update_tooltip(
                tooltip,
                fmt.format(-original_Z[i].imag)
                + (
                    (
                        " -> " + fmt.format(-Z[i].imag)
                        if not isclose(original_Z[i], Z[i])
                        else ""
                    )
                ),
            )
            cell, tooltip = get_cell_and_tooltip(cells, 5)
            dpg.set_value(cell, mod_Z[i])
            update_tooltip(
                tooltip,
                fmt.format(abs(original_Z[i]))
                + (
                    (
                        " -> " + fmt.format(abs(Z[i]))
                        if not isclose(original_Z[i], Z[i])
                        else ""
                    )
                ),
            )
            cell, tooltip = get_cell_and_tooltip(cells, 6)
            dpg.set_value(cell, phase_Z[i])
            update_tooltip(
                tooltip,
                fmt.format(-angle(original_Z[i], deg=True))
                + (
                    (
                        " -> " + fmt.format(-angle(Z[i], deg=True))
                        if not isclose(original_Z[i], Z[i])
                        else ""
                    )
                ),
            )
        dictionary: dict = self.original_data.to_dict()
        dictionary.update(
            {
                "mask": {},
                "real_impedances": list(Z.real),
                "imaginary_impedances": list(Z.imag),
            }
        )
        self.preview_data = DataSet.from_dict(dictionary)

    def update_smoothing(self):
        log_f: NDArray[float64] = log(self.original_data.get_frequencies())
        Z: ComplexImpedances = self.original_data.get_impedances()
        fraction: float = dpg.get_value(self.num_points_input) / Z.size
        num_iterations: int = dpg.get_value(self.num_iterations_input)
        smooth_polar_data = dpg.get_value(self.smooth_polar_checkbox)
        if smooth_polar_data is True:
            smoothed_mod: Impedances = lowess(
                abs(Z),
                log_f,
                frac=fraction,
                it=num_iterations,
                return_sorted=False,
            )
            smoothed_phase = lowess(
                angle(Z),
                log_f,
                frac=fraction,
                it=num_iterations,
                return_sorted=False,
            )
            log_f = flip(log_f)
            mod_interpolator = Akima1DInterpolator(log_f, flip(smoothed_mod))
            phase_interpolator = Akima1DInterpolator(log_f, flip(smoothed_phase))
        else:
            smoothed_real: Impedances = lowess(
                Z.real,
                log_f,
                frac=fraction,
                it=num_iterations,
                return_sorted=False,
            )
            smoothed_imag: Impedances = lowess(
                Z.imag,
                log_f,
                frac=fraction,
                it=num_iterations,
                return_sorted=False,
            )
            log_f = flip(log_f)
            real_interpolator = Akima1DInterpolator(log_f, flip(smoothed_real))
            imag_interpolator = Akima1DInterpolator(log_f, flip(smoothed_imag))
        log_f = log(self.original_data.get_frequencies(masked=None))
        dictionary: dict = self.smoothed_data.to_dict()
        if smooth_polar_data is True:
            Z = array(
                list(
                    map(
                        lambda _: rect(*_),
                        zip(mod_interpolator(log_f), phase_interpolator(log_f)),
                    )
                )
            )
            dictionary.update(
                {
                    "real_impedances": Z.real,
                    "imaginary_impedances": Z.imag,
                }
            )
        else:
            dictionary.update(
                {
                    "real_impedances": list(map(real_interpolator, log_f)),
                    "imaginary_impedances": list(map(imag_interpolator, log_f)),
                }
            )
        self.smoothed_data = DataSet.from_dict(dictionary)
        self.update_table()
        self.update_plots()

    def update_plots(self):
        self.update_nyquist(self.original_data, self.smoothed_data, self.preview_data)
        self.update_magnitude(self.original_data, self.smoothed_data, self.preview_data)
        self.update_phase(self.original_data, self.smoothed_data, self.preview_data)

    def update_nyquist(self, original: DataSet, smoothed: DataSet, preview: DataSet):
        data: List[Tuple[ndarray, ndarray]] = [
            original.get_nyquist_data(masked=False),
            original.get_nyquist_data(masked=False),
            original.get_nyquist_data(masked=True),
            smoothed.get_nyquist_data(masked=None),
            preview.get_nyquist_data(masked=None),
            preview.get_nyquist_data(masked=None),
        ]
        i: int
        real: ndarray
        imag: ndarray
        for i, (real, imag) in enumerate(data):
            self.nyquist_plot.update(
                index=i,
                real=real,
                imaginary=imag,
            )

    def update_magnitude(self, original: DataSet, smoothed: DataSet, preview: DataSet):
        data: List[Tuple[ndarray, ndarray, ndarray]] = [
            original.get_bode_data(masked=False),
            original.get_bode_data(masked=False),
            original.get_bode_data(masked=True),
            smoothed.get_bode_data(masked=None),
            preview.get_bode_data(masked=None),
            preview.get_bode_data(masked=None),
        ]
        i: int
        freq: ndarray
        mag: ndarray
        for i, (freq, mag, _) in enumerate(data):
            self.magnitude_plot.update(
                index=i,
                frequency=freq,
                magnitude=mag,
            )

    def update_phase(self, original: DataSet, smoothed: DataSet, preview: DataSet):
        data: List[Tuple[ndarray, ndarray, ndarray]] = [
            original.get_bode_data(masked=False),
            original.get_bode_data(masked=False),
            original.get_bode_data(masked=True),
            smoothed.get_bode_data(masked=None),
            preview.get_bode_data(masked=None),
            preview.get_bode_data(masked=None),
        ]
        i: int
        freq: ndarray
        phase: ndarray
        for i, (freq, _, phase) in enumerate(data):
            self.phase_plot.update(
                index=i,
                frequency=freq,
                phase=phase,
            )

    def cycle_plot_tab(self, step: int):
        tabs: List[int] = dpg.get_item_children(self.plot_tab_bar, slot=1)
        index: int = tabs.index(dpg.get_value(self.plot_tab_bar)) + step
        dpg.set_value(self.plot_tab_bar, tabs[index % len(tabs)])
