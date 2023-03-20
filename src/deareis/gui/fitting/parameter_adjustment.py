# DearEIS is licensed under the GPLv3 or later (https://www.gnu.org/licenses/gpl-3.0.html).
# Copyright 2023 DearEIS developers
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

from dataclasses import dataclass
from traceback import format_exc
from typing import (
    Callable,
    Dict,
    List,
)
import dearpygui.dearpygui as dpg
from numpy import (
    angle,
    array,
    inf,
    isinf,
    isnan,
    ndarray,
)
from pyimpspec import (
    Circuit,
    ComplexImpedances,
    Element,
    Frequencies,
)
from pyimpspec.exceptions import (
    InfiniteImpedance,
    NotANumberImpedance,
)
from pyimpspec.analysis.utility import _interpolate
from deareis.data import DataSet
from deareis.gui.plots import (
    Bode,
    Nyquist,
    Impedance,
)
import deareis.themes as themes
from deareis.signals import Signal
import deareis.signals as signals
from deareis.utility import (
    calculate_window_position_dimensions,
    pad_tab_labels,
)
from deareis.tooltips import attach_tooltip
from deareis.enums import Action
from deareis.keybindings import (
    Keybinding,
    TemporaryKeybindingHandler,
)


@dataclass
class ParameterSettings:
    element: Element
    key: str
    tooltip: str
    value_input: int
    fixed_checkbox: int
    value_slider: int
    min_value_input: int
    max_value_input: int
    lower_limit_input: int
    lower_limit_checkbox: int
    upper_limit_input: int
    upper_limit_checkbox: int
    callback: Callable

    def reset(self):
        self.element.reset_parameter(self.key)
        if self.upper_limit_input > 0:
            upper: float = self.get_upper_limit()
            upper_enabled: bool = not isinf(upper)
            dpg.set_value(self.upper_limit_checkbox, upper_enabled)
            dpg.configure_item(
                self.upper_limit_input,
                default_value=upper,
                enabled=upper_enabled,
                readonly=not upper_enabled,
            )
        if self.lower_limit_input > 0:
            lower: float = self.get_lower_limit()
            lower_enabled: bool = not isinf(lower)
            dpg.set_value(self.lower_limit_checkbox, lower_enabled)
            dpg.configure_item(
                self.lower_limit_input,
                default_value=lower,
                enabled=lower_enabled,
                readonly=not lower_enabled,
            )
        maximum: float = self.get_max_value()
        dpg.set_value(self.max_value_input, maximum)
        minimum: float = self.get_min_value()
        dpg.set_value(self.min_value_input, minimum)
        value: float = self.get_value()
        dpg.configure_item(
            self.value_slider,
            default_value=value,
            min_value=minimum,
            max_value=maximum,
        )
        dpg.set_value(self.value_input, value)
        self.callback()

    def get_value(self, default: bool = False) -> float:
        if default:
            return self.element.get_default_value(self.key)
        return self.element.get_value(self.key)

    def set_value(self, sender: int, value: float):
        minimum: float = dpg.get_value(self.min_value_input)
        maximum: float = dpg.get_value(self.max_value_input)
        if value < minimum:
            value = minimum
        elif value > maximum:
            value = maximum
        dpg.set_value(self.value_input, value)
        dpg.set_value(self.value_slider, value)
        self.element.set_values(self.key, value)
        self.callback()

    def get_min_value(self, default: bool = False) -> float:
        value: float = self.get_value(default=default)
        minimum: float = value / 10
        lower: float = self.get_lower_limit(default=default)
        if self.lower_limit_input > 0 and minimum < lower:
            minimum = lower
        return minimum

    def set_min_value(self, sender: int, value: float):
        lower: float = self.get_lower_limit()
        maximum: float = dpg.get_value(self.max_value_input)
        if value < lower:
            value = lower
            dpg.set_value(self.min_value_input, value)
        elif value >= maximum:
            value = self.get_min_value()
            dpg.set_value(self.min_value_input, value)
        elif sender != self.min_value_input:
            dpg.set_value(self.min_value_input, value)
        if self.get_value() < value:
            self.set_value(-1, value)
        dpg.configure_item(self.value_slider, min_value=value)

    def get_max_value(self, default: bool = False) -> float:
        value: float = self.get_value(default=default)
        maximum: float = value * 2
        upper: float = self.get_upper_limit(default=default)
        if self.upper_limit_input > 0 and maximum > upper:
            maximum = upper
        return maximum

    def set_max_value(self, sender: int, value: float):
        upper: float = self.get_upper_limit()
        minimum: float = dpg.get_value(self.min_value_input)
        if value > upper:
            value = upper
            dpg.set_value(self.max_value_input, value)
        elif value <= minimum:
            value = self.get_max_value()
            dpg.set_value(self.max_value_input, value)
        elif sender != self.max_value_input:
            dpg.set_value(self.max_value_input, value)
        if self.get_value() > value:
            self.set_value(-1, value)
        dpg.configure_item(self.value_slider, max_value=value)

    def is_fixed(self, default: bool = False) -> bool:
        if default:
            return self.element.is_fixed_by_default(self.key)
        return self.element.is_fixed(self.key)

    def set_fixed(self, sender: int, value: bool):
        if sender != self.fixed_checkbox:
            dpg.set_value(self.fixed_checkbox, value)
        self.element.set_fixed(self.key, value)

    def get_lower_limit(self, default: bool = False) -> float:
        if default:
            return self.element.get_default_lower_limit(self.key)
        return self.element.get_lower_limit(self.key)

    def set_lower_limit(self, sender: int, value: float):
        maximum: float = dpg.get_value(self.max_value_input)
        if value >= maximum:
            value = dpg.get_value(self.min_value_input)
            dpg.set_value(self.lower_limit_input, value)
        elif sender != self.lower_limit_input:
            dpg.set_value(self.lower_limit_input, value)
        dpg.set_value(self.lower_limit_checkbox, not isinf(value))
        if not isinf(value):
            minimum: float = dpg.get_value(self.min_value_input)
            if minimum < value:
                self.set_min_value(-1, value)
        self.element.set_lower_limits(self.key, value)

    def toggle_lower_limit(self, sender: int, value: bool):
        if sender != self.lower_limit_checkbox:
            dpg.set_value(self.lower_limit_checkbox, value)
        limit: float = -inf if not value else self.get_lower_limit(default=True)
        if value is True and isinf(limit):
            limit = dpg.get_value(self.min_value_input)
        dpg.configure_item(
            self.lower_limit_input,
            default_value=limit,
            enabled=value,
            readonly=not value,
        )
        if not isinf(limit):
            minimum: float = dpg.get_value(self.min_value_input)
            if minimum < limit:
                self.set_min_value(-1, limit)
        self.element.set_lower_limits(self.key, limit)

    def get_upper_limit(self, default: bool = False) -> float:
        if default:
            return self.element.get_default_upper_limit(self.key)
        return self.element.get_upper_limit(self.key)

    def set_upper_limit(self, sender: int, value: float):
        minimum: float = dpg.get_value(self.min_value_input)
        if value <= minimum:
            value = dpg.get_value(self.max_value_input)
            dpg.set_value(self.upper_limit_input, value)
        elif sender != self.upper_limit_input:
            dpg.set_value(self.upper_limit_input, value)
        dpg.set_value(self.upper_limit_checkbox, not isinf(value))
        if not isinf(value):
            maximum: float = dpg.get_value(self.max_value_input)
            if maximum > value:
                self.set_max_value(-1, value)
        self.element.set_upper_limits(self.key, value)

    def toggle_upper_limit(self, sender: int, value: bool):
        if sender != self.upper_limit_checkbox:
            dpg.set_value(self.upper_limit_checkbox, value)
        limit: float = inf if value is False else self.get_upper_limit(default=True)
        if value is True and isinf(limit):
            limit = dpg.get_value(self.max_value_input)
        dpg.configure_item(
            self.upper_limit_input,
            default_value=limit,
            enabled=value,
            readonly=not value,
        )
        if not isinf(limit):
            maximum: float = dpg.get_value(self.max_value_input)
            if maximum > limit:
                self.set_max_value(-1, limit)
        self.element.set_upper_limits(self.key, limit)


class ParameterAdjustment:
    def __init__(
        self,
        data: DataSet,
        circuit: Circuit,
        callback: Callable,
        hide_data: bool = False,
        keybindings: List[Keybinding] = [],
    ):
        assert isinstance(data, DataSet)
        assert isinstance(circuit, Circuit)
        assert callable(callback)
        assert isinstance(hide_data, bool)
        assert isinstance(keybindings, list)
        self.hide_data: bool = hide_data
        self.data: DataSet = data
        self.marker_frequencies: Frequencies = data.get_frequencies()
        self.line_frequencies: Frequencies = _interpolate(
            self.marker_frequencies,
            num_per_decade=20,
        )
        self.circuit: Circuit = circuit
        self.identifiers: Dict[Element, int] = circuit.generate_element_identifiers(
            running=False
        )
        self.callback: Callable = callback
        self.input_widgets: List[int] = []
        self.create_window()
        self.register_keybindings(keybindings)
        self.nyquist_plot.queue_limits_adjustment()
        self.bode_plot.queue_limits_adjustment()
        self.impedance_plot.queue_limits_adjustment()
        dpg.split_frame(delay=67)
        self.update()

    def register_keybindings(self, keybindings: List[Keybinding]):
        callbacks: Dict[Keybinding, Callable] = {}
        # Cancel
        kb: Keybinding = Keybinding(
            key=dpg.mvKey_Escape,
            mod_alt=False,
            mod_ctrl=False,
            mod_shift=False,
            action=Action.CANCEL,
        )
        callbacks[kb] = lambda: self.close(keybinding=True)
        # Accept
        for kb in keybindings:
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
        callbacks[kb] = lambda: self.accept(keybinding=True)
        # Previous plot tab
        for kb in keybindings:
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
        for kb in keybindings:
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
            label="Adjust parameters",
            modal=True,
            pos=(x, y),
            width=w,
            height=h,
            tag=self.window,
            on_close=self.close,
        ):
            with dpg.group(horizontal=True):
                with dpg.group():
                    self.create_parameter_widgets()
                    dpg.add_button(
                        label="Accept".ljust(12),
                        callback=self.accept,
                    )
                self.create_plots()

    def create_plots(self):
        self.plot_tab_bar: int = dpg.generate_uuid()
        with dpg.tab_bar(tag=self.plot_tab_bar):
            self.create_nyquist_plot()
            self.create_bode_plot()
            self.create_impedance_plot()
        pad_tab_labels(self.plot_tab_bar)

    def create_nyquist_plot(self):
        with dpg.tab(label="Nyquist"):
            self.nyquist_plot: Nyquist = Nyquist(width=-1, height=-1)
            if self.hide_data is False:
                real: ndarray
                imag: ndarray
                real, imag = self.data.get_nyquist_data()
                self.nyquist_plot.plot(
                    real=real,
                    imaginary=imag,
                    label="Data",
                    theme=themes.nyquist.data,
                )
            self.nyquist_plot.plot(
                real=array([]),
                imaginary=array([]),
                label="Sim.",
                show_label=False,
                line=False,
                simulation=True,
                theme=themes.nyquist.simulation,
            )
            self.nyquist_plot.plot(
                real=array([]),
                imaginary=array([]),
                label="Sim.",
                line=True,
                simulation=True,
                theme=themes.nyquist.simulation,
            )

    def create_bode_plot(self):
        with dpg.tab(label="Bode"):
            self.bode_plot: Bode = Bode(width=-1, height=-1)
            if self.hide_data is False:
                freq: ndarray
                mag: ndarray
                phase: ndarray
                freq, mag, phase = self.data.get_bode_data()
                self.bode_plot.plot(
                    frequency=freq,
                    magnitude=mag,
                    phase=phase,
                    labels=(
                        "Mod(Z), d.",
                        "Phase(Z), d.",
                    ),
                    line=False,
                    themes=(
                        themes.bode.magnitude_data,
                        themes.bode.phase_data,
                    ),
                )
            self.bode_plot.plot(
                frequency=array([]),
                magnitude=array([]),
                phase=array([]),
                labels=(
                    "Mod(Z), s.",
                    "Phase(Z), s.",
                ),
                line=False,
                fit=True,
                themes=(
                    themes.bode.magnitude_simulation,
                    themes.bode.phase_simulation,
                ),
                show_labels=False,
            )
            self.bode_plot.plot(
                frequency=array([]),
                magnitude=array([]),
                phase=array([]),
                labels=(
                    "Mod(Z), s.",
                    "Phase(Z), s.",
                ),
                line=True,
                fit=True,
                themes=(
                    themes.bode.magnitude_simulation,
                    themes.bode.phase_simulation,
                ),
            )

    def create_impedance_plot(self):
        with dpg.tab(label="Real & Imag."):
            self.impedance_plot: Impedance = Impedance(width=-1, height=-1)
            if self.hide_data is False:
                f: ndarray = self.data.get_frequencies()
                Z: ndarray = self.data.get_impedances()
                self.impedance_plot.plot(
                    frequency=f,
                    real=Z.real,
                    imaginary=-Z.imag,
                    labels=(
                        "Re(Z), d.",
                        "Im(Z), d.",
                    ),
                    line=False,
                    themes=(
                        themes.impedance.real_data,
                        themes.impedance.imaginary_data,
                    ),
                )
            self.impedance_plot.plot(
                frequency=array([]),
                real=array([]),
                imaginary=array([]),
                labels=(
                    "Re(Z), s.",
                    "Im(Z), s.",
                ),
                line=False,
                fit=True,
                themes=(
                    themes.impedance.real_simulation,
                    themes.impedance.imaginary_simulation,
                ),
                show_labels=False,
            )
            self.impedance_plot.plot(
                frequency=array([]),
                real=array([]),
                imaginary=array([]),
                labels=(
                    "Re(Z), s.",
                    "Im(Z), s.",
                ),
                line=True,
                fit=True,
                themes=(
                    themes.impedance.real_simulation,
                    themes.impedance.imaginary_simulation,
                ),
            )

    def parameter_heading(
        self,
        element: Element,
        key: str,
        window_width: int,
        slider_width: int,
        label_pad: int,
    ):
        settings: ParameterSettings = ParameterSettings(
            element=element,
            key=key,
            tooltip=f"Description: {element.get_value_description(key)}\n\nUnit: {element.get_unit(key)}",
            value_input=dpg.generate_uuid(),
            fixed_checkbox=dpg.generate_uuid(),
            value_slider=dpg.generate_uuid(),
            min_value_input=dpg.generate_uuid(),
            max_value_input=dpg.generate_uuid(),
            lower_limit_input=dpg.generate_uuid(),
            lower_limit_checkbox=dpg.generate_uuid(),
            upper_limit_input=dpg.generate_uuid(),
            upper_limit_checkbox=dpg.generate_uuid(),
            callback=self.update,
        )
        name: str = self.circuit.get_element_name(element, self.identifiers)
        with dpg.collapsing_header(label=f"{name} - {key}", open_on_arrow=False):
            self.parameter_value_input(
                settings=settings,
                slider_width=slider_width,
                label_pad=label_pad,
            )
            self.parameter_min_max_value_inputs(
                settings=settings,
                window_width=window_width,
                label_pad=label_pad,
            )
            self.parameter_limit_inputs(
                settings=settings,
                slider_width=slider_width,
                label_pad=label_pad,
            )
            dpg.add_button(label="Reset", callback=settings.reset)
            dpg.add_spacer(height=8)
        self.input_widgets.extend(
            [
                _
                for _ in (
                    settings.value_input,
                    settings.min_value_input,
                    settings.max_value_input,
                    settings.lower_limit_input,
                    settings.upper_limit_input,
                )
                if _ > 0
            ]
        )

    def parameter_value_input(
        self,
        settings: ParameterSettings,
        slider_width: int,
        label_pad: int,
    ):
        value: float = settings.get_value()
        with dpg.group(horizontal=True):
            dpg.add_text("Value".rjust(label_pad))
            attach_tooltip(settings.tooltip)
            dpg.add_input_float(
                default_value=value,
                step=0,
                format="%.4g",
                on_enter=True,
                callback=settings.set_value,
                width=slider_width,
                tag=settings.value_input,
            )
            dpg.add_checkbox(
                label="F",
                default_value=settings.is_fixed(),
                callback=settings.set_fixed,
                tag=settings.fixed_checkbox,
            )
            attach_tooltip("Whether or not the value is fixed during fitting")
        with dpg.group(horizontal=True):
            dpg.add_text("".rjust(label_pad))
            dpg.add_slider_float(
                default_value=value,
                format="%.4g",
                no_input=True,
                min_value=settings.get_min_value(),
                max_value=settings.get_max_value(),
                callback=settings.set_value,
                width=slider_width,
                tag=settings.value_slider,
            )

    def parameter_min_max_value_inputs(
        self,
        settings: ParameterSettings,
        window_width: int,
        label_pad: int,
    ):
        min_max_width: int = (window_width - 162) / 2 - 8
        with dpg.group(horizontal=True):
            dpg.add_text("Min.".rjust(label_pad))
            min_tooltip: str = "The minimum value of the value slider."
            attach_tooltip(min_tooltip)
            dpg.add_input_float(
                default_value=settings.get_min_value(),
                format="%.4g",
                callback=settings.set_min_value,
                on_enter=True,
                step=0,
                width=min_max_width,
                tag=settings.min_value_input,
            )
            attach_tooltip(min_tooltip)
            dpg.add_input_float(
                label="Max.",
                default_value=settings.get_max_value(),
                format="%.4g",
                callback=settings.set_max_value,
                on_enter=True,
                step=0,
                width=min_max_width,
                tag=settings.max_value_input,
            )
            attach_tooltip("The maximum value of the value slider.")

    def parameter_limit_inputs(
        self,
        settings: ParameterSettings,
        slider_width: int,
        label_pad: int,
    ):
        lower: float = settings.get_lower_limit()
        upper: float = settings.get_upper_limit()
        lower_enabled: bool = not isinf(lower)
        upper_enabled: bool = not isinf(upper)
        with dpg.group(horizontal=True):
            dpg.add_text("Lower limit".rjust(label_pad))
            attach_tooltip(settings.tooltip)
            dpg.add_input_float(
                default_value=lower,
                step=0,
                format="%.4g",
                width=slider_width,
                tag=settings.lower_limit_input,
                on_enter=True,
                readonly=not lower_enabled,
                enabled=lower_enabled,
                callback=settings.set_lower_limit,
            )
            dpg.add_checkbox(
                label="E",
                default_value=lower_enabled,
                tag=settings.lower_limit_checkbox,
                callback=settings.toggle_lower_limit,
            )
            attach_tooltip("Enabled")
        with dpg.group(horizontal=True):
            dpg.add_text("Upper limit".rjust(label_pad))
            attach_tooltip(settings.tooltip)
            dpg.add_input_float(
                default_value=upper,
                step=0,
                format="%.4g",
                width=slider_width,
                tag=settings.upper_limit_input,
                on_enter=True,
                readonly=not upper_enabled,
                enabled=upper_enabled,
                callback=settings.set_upper_limit,
            )
            dpg.add_checkbox(
                label="E",
                default_value=upper_enabled,
                tag=settings.upper_limit_checkbox,
                callback=settings.toggle_upper_limit,
            )
            attach_tooltip("Enabled")

    def create_parameter_widgets(self):
        label_pad: int = 12
        slider_width: int = 230
        window_width: int = 400
        with dpg.child_window(width=window_width, height=-24):
            element: Element
            for element in self.identifiers:
                key: str
                for key in element.get_values().keys():
                    self.parameter_heading(
                        element=element,
                        key=key,
                        window_width=window_width,
                        slider_width=slider_width,
                        label_pad=label_pad,
                    )

    def update(self):
        marker_real: ndarray
        marker_imag: ndarray
        marker_mag: ndarray
        marker_phase: ndarray
        line_real: ndarray
        line_imag: ndarray
        line_mag: ndarray
        line_phase: ndarray
        try:
            Z: ComplexImpedances = self.circuit.get_impedances(self.marker_frequencies)
            if isinf(Z).any():
                raise InfiniteImpedance()
            elif isnan(Z).any():
                raise NotANumberImpedance()
            marker_real = Z.real
            marker_imag = -Z.imag
            marker_mag = abs(Z)
            marker_phase = -angle(Z, deg=True)
            Z = self.circuit.get_impedances(self.line_frequencies)
            if isinf(Z).any():
                raise InfiniteImpedance()
            elif isnan(Z).any():
                raise NotANumberImpedance()
            line_real = Z.real
            line_imag = -Z.imag
            line_mag = abs(Z)
            line_phase = -angle(Z, deg=True)
        except (InfiniteImpedance, NotANumberImpedance):
            marker_real = array([])
            marker_imag = array([])
            line_real = array([])
            line_imag = array([])
        except Exception:
            dpg.split_frame(delay=60)
            self.close()
            dpg.split_frame(delay=60)
            signals.emit(
                Signal.SHOW_ERROR_MESSAGE,
                traceback=format_exc(),
                message="""
Encountered exception while calculating impedances.
                """.strip(),
            )
            return
        self.nyquist_plot.update(
            index=0 if self.hide_data is True else 1,
            real=marker_real,
            imaginary=marker_imag,
        )
        self.nyquist_plot.update(
            index=1 if self.hide_data is True else 2,
            real=line_real,
            imaginary=line_imag,
        )
        self.bode_plot.update(
            index=0 if self.hide_data is True else 1,
            frequency=self.marker_frequencies,
            magnitude=marker_mag,
            phase=marker_phase,
        )
        self.bode_plot.update(
            index=1 if self.hide_data is True else 2,
            frequency=self.line_frequencies,
            magnitude=line_mag,
            phase=line_phase,
        )
        self.impedance_plot.update(
            index=0 if self.hide_data is True else 1,
            frequency=self.marker_frequencies,
            real=marker_real,
            imaginary=marker_imag,
        )
        self.impedance_plot.update(
            index=1 if self.hide_data is True else 2,
            frequency=self.line_frequencies,
            real=line_real,
            imaginary=line_imag,
        )

    def close(self, keybinding: bool = False):
        if keybinding is True and self.has_active_input():
            return
        dpg.hide_item(self.window)
        dpg.delete_item(self.window)
        self.keybinding_handler.delete()
        signals.emit(Signal.UNBLOCK_KEYBINDINGS)

    def accept(self, keybinding: bool = False):
        if keybinding is True and self.has_active_input():
            return
        self.callback(self.circuit)
        self.close()

    def has_active_input(self) -> bool:
        widget: int
        for widget in self.input_widgets:
            if dpg.is_item_active(widget):
                return True
        return False

    def cycle_plot_tab(self, step: int):
        tabs: List[int] = dpg.get_item_children(self.plot_tab_bar, slot=1)
        index: int = tabs.index(dpg.get_value(self.plot_tab_bar)) + step
        dpg.set_value(self.plot_tab_bar, tabs[index % len(tabs)])
