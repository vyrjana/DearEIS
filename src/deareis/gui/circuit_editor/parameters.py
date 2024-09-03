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

from dataclasses import dataclass
from traceback import format_exc
from typing import (
    Callable,
    Dict,
    List,
    Optional,
    Tuple,
    Union,
)
import dearpygui.dearpygui as dpg
from numpy import (
    array,
    complex128,
    floor,
    inf,
    isinf,
    isposinf,
    isneginf,
    isnan,
    log10 as log,
    ndarray,
)
from pyimpspec import (
    Circuit,
    Container,
    Connection,
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
from deareis.utility import pad_tab_labels
from deareis.tooltips import (
    attach_tooltip,
    update_tooltip,
)
import deareis.tooltips as tooltips
from deareis.typing.helpers import Tag


SI_PREFIXES: Dict[str, float] = {
    "Q (10^30)": 1e30,
    "R (10^27)": 1e27,
    "Y (10^24)": 1e24,
    "Z (10^21)": 1e21,
    "E (10^18)": 1e18,
    "P (10^15)": 1e15,
    "T (10^12)": 1e12,
    "G (10^9)": 1e9,
    "M (10^6)": 1e6,
    "k (10^3)": 1e3,
    "": 1e0,
    "m (10^-3)": 1e-3,
    "µ (10^-6)": 1e-6,
    "n (10^-9)": 1e-9,
    "p (10^-12)": 1e-12,
    "f (10^-15)": 1e-15,
    "a (10^-18)": 1e-18,
    "z (10^-21)": 1e-21,
    "y (10^-24)": 1e-24,
    "r (10^-27)": 1e-27,
    "q (10^-30)": 1e-30,
}


@dataclass
class ParameterSettings:
    element: Element
    key: str
    header: Tag
    tooltip: Tag
    value_input: Tag
    fixed_checkbox: Tag
    value_slider: Tag
    si_prefix_combo: Tag
    lower_limit_input: Tag
    lower_limit_checkbox: Tag
    upper_limit_input: Tag
    upper_limit_checkbox: Tag
    callback: Callable

    def reset(self):
        self.element.reset_parameter(self.key)
        
        self.set_value(
            sender=-1,
            value=self.get_value(),
        )

        self.set_lower_limit(
            sender=-1,
            value=self.get_lower_limit(default=True),
        )

        self.set_upper_limit(
            sender=-1,
            value=self.get_upper_limit(default=True),
        )

    def get_value(self, default: bool = False) -> float:
        if default:
            return self.element.get_default_value(self.key)

        return self.element.get_value(self.key)

    def set_label(self, label: str):
        dpg.set_item_label(self.header, label)

    def set_tooltip(self, tooltip: str):
        update_tooltip(tag=self.tooltip, msg=tooltip)

    def to_value_slider(self, value: float) -> Tuple[float, str]:
        if value == 0.0:
            return (0.0, min(SI_PREFIXES.keys(), key=lambda k: len(k)))

        exponent: float = floor(log(abs(value)))

        for prefix, factor in SI_PREFIXES.items():
            if exponent >= log(factor):
                break
        else:
            prefix, factor = list(SI_PREFIXES.items())[10]

        return (log(abs(value) / factor), prefix)

    def update_value_slider(self, value: float, prefix: str):
        dpg.set_value(self.value_slider, value)
        dpg.set_value(self.si_prefix_combo, prefix)

    def from_value_slider(self, value: float) -> float:
        value = (10**value) * SI_PREFIXES[dpg.get_value(self.si_prefix_combo)]
        if dpg.get_value(self.value_input) < 0.0:
            value *= -1

        return value

    def update_value_input(self, value: float):
        dpg.set_value(self.value_input, value)

    def set_value(
        self,
        sender: Tag,
        value: float,
    ):
        lower_limit: float = self.get_lower_limit()
        upper_limit: float = self.get_upper_limit()

        if sender == self.value_slider:
            value = self.from_value_slider(value)
            if lower_limit <= value <= upper_limit:
                self.update_value_input(value)
            else:
                self.set_value(
                    sender=-1,
                    value=value,
                )
                return

        elif sender == self.value_input:
            if value < lower_limit:
                if upper_limit > 0.0 and lower_limit == 0.0:
                    if isinf(upper_limit):
                        value = 1
                    else:
                        value = min((1, upper_limit / 2))
                else:
                    value = lower_limit

                dpg.set_value(self.value_input, value)

            elif value > upper_limit:
                if lower_limit < 0.0 and upper_limit == 0.0:
                    if isinf(lower_limit):
                        value = -1
                    else:
                        value = max((-1, lower_limit / 2))
                else:
                    value = upper_limit

                dpg.set_value(self.value_input, value)

            self.update_value_slider(*self.to_value_slider(value))

        else:
            if value < lower_limit:
                value = lower_limit
            elif value > upper_limit:
                value = upper_limit

            self.update_value_input(value)
            self.update_value_slider(*self.to_value_slider(value))

        self.element.set_values(self.key, value)
        self.callback()

    def set_si_prefix(
        self,
        sender: Tag,
        prefix: str,
    ):
        self.set_value(
            sender=self.value_slider,
            value=dpg.get_value(self.value_slider),
        )

    def is_fixed(self, default: bool = False) -> bool:
        if default:
            return self.element.is_fixed_by_default(self.key)

        return self.element.is_fixed(self.key)

    def set_fixed(self, sender: Tag, value: bool):
        if sender != self.fixed_checkbox:
            dpg.set_value(self.fixed_checkbox, value)

        self.element.set_fixed(self.key, value)

    def get_lower_limit(self, default: bool = False) -> float:
        if default:
            return self.element.get_default_lower_limit(self.key)

        return self.element.get_lower_limit(self.key)

    def set_lower_limit(
        self,
        sender: Tag,
        value: float,
    ):
        # Invalid value -> simply reset the value in the input widget
        if isposinf(value) or value >= self.get_upper_limit():
            dpg.set_value(self.lower_limit_input, self.get_lower_limit())
            return

        self.element.set_lower_limits(self.key, value)

        # New lower limit was set programmatically (initialization or reset)
        if sender != self.lower_limit_input:
            self.toggle_lower_limit(sender=sender, value=not isneginf(value))

        # New lower limit is higher than the current initial value
        # -> Set initial value to equal the new lower limit
        if value > dpg.get_value(self.value_input):
            self.set_value(sender=-1, value=value)


    def toggle_lower_limit(
        self,
        sender: Tag,
        value: bool,
    ):
        if sender != self.lower_limit_checkbox:
            dpg.set_value(self.lower_limit_checkbox, value)

        if sender == self.lower_limit_input:
            return

        lower_limit: float = -inf
        if value is True:
            if sender != self.lower_limit_checkbox:
                lower_limit = self.get_lower_limit(default=False)
            else:
                lower_limit = self.get_lower_limit(default=True)

        if sender == self.lower_limit_checkbox:
            self.element.set_lower_limits(self.key, lower_limit)

        dpg.configure_item(
            self.lower_limit_input,
            default_value=lower_limit,
            enabled=value,
            readonly=not value,
        )

    def get_upper_limit(self, default: bool = False) -> float:
        if default:
            return self.element.get_default_upper_limit(self.key)

        return self.element.get_upper_limit(self.key)

    def set_upper_limit(
        self,
        sender: Tag,
        value: float,
    ):
        # Invalid value -> simply reset the value in the input widget
        if isneginf(value) or value <= self.get_lower_limit():
            dpg.set_value(self.upper_limit_input, self.get_upper_limit())
            return

        self.element.set_upper_limits(self.key, value)

        # New upper limit was set programmatically (initialization or reset)
        if sender != self.upper_limit_input:
            self.toggle_upper_limit(sender=sender, value=not isposinf(value))

        # New upper limit is lower than the current initial value
        # -> Set initial value to equal the new upper limit
        if value < dpg.get_value(self.value_input):
            self.set_value(sender=-1, value=value)


    def toggle_upper_limit(
        self,
        sender: Tag,
        value: bool,
    ):
        if sender != self.upper_limit_checkbox:
            dpg.set_value(self.upper_limit_checkbox, value)
        
        if sender == self.upper_limit_input:
            return

        upper_limit: float = inf
        if value is True:
            if sender != self.upper_limit_checkbox:
                upper_limit = self.get_upper_limit(default=False)
            else:
                upper_limit = self.get_upper_limit(default=True)

        if sender == self.upper_limit_checkbox:
            self.element.set_upper_limits(self.key, upper_limit)

        dpg.configure_item(
            self.upper_limit_input,
            default_value=upper_limit,
            enabled=value,
            readonly=not value,
        )


class ParameterAdjustment:
    def __init__(
        self,
        window: Tag,
        callback: Callable,
    ):
        assert isinstance(window, int), window
        assert callable(callback), callback

        self.callback: Callable = callback

        self.circuit: Optional[Circuit] = None

        self.data: DataSet = None  # typing: ignore
        self.marker_frequencies: Frequencies = array([])
        self.line_frequencies: Frequencies = array([])

        self.input_widgets: List[int] = []
        self.create_window(window)

    def set_circuit(self, circuit: Optional[Circuit]):
        if circuit is self.circuit:
            return

        self.circuit = circuit
        if circuit is None:
            return

        folded: Dict[Element, Dict[str, bool]] = {}

        settings: ParameterSettings
        for settings in map(
            dpg.get_item_user_data,
            dpg.get_item_children(self.sidebar_window, slot=1),
        ):
            if settings.element not in folded:
                folded[settings.element] = {}

            folded[settings.element][settings.key] = dpg.get_value(settings.header)

        self.clear_widgets()

        identifiers: Dict[Element, int] = circuit.generate_element_identifiers(
            running=False
        )

        elements_to_add: List[Element] = circuit.get_elements(recursive=True)
        parent_containers: Dict[Element, Element] = {}
        nested_elements: Dict[Element, Dict[str, List[Element]]] = {}
        widgets: Dict[Element, List[ParameterSettings]] = {}

        while elements_to_add:
            element: Union[Element, Connection] = elements_to_add.pop(0)
            if isinstance(element, Container):
                if element not in nested_elements:
                    nested_elements[element] = {}

                subcircuit_elements: Dict[str, List[Element]] = nested_elements[element]

                widgets[element] = self.add_element(element)
                container: Container = element

                subcircuit_name: str
                subcircuit: Optional[Connection]
                for subcircuit_name, subcircuit in container.get_subcircuits().items():
                    if subcircuit is None:
                        continue

                    subcircuit_elements[subcircuit_name] = subcircuit.get_elements(
                        recursive=True
                    )

                    for element in reversed(subcircuit_elements[subcircuit_name]):
                        parent_containers[element] = container
                        elements_to_add.insert(0, element)

            elif isinstance(element, Element):
                widgets[element] = self.add_element(element)
            else:
                raise ValueError(f"Expected an Element: {type(element)}")

        element_names: Dict[Element, str] = {}
        elements_to_process: List[Element] = list(widgets.keys())
        while elements_to_process:
            element = elements_to_process.pop(0)
            if element not in element_names:
                element_names[element] = self.circuit.get_element_name(
                    element,
                    identifiers,
                )

            is_nested_element: bool = element in parent_containers
            if is_nested_element and parent_containers[element] not in element_names:
                elements_to_process.append(element)
                continue

            parent_name: Optional[str] = None
            subcircuit_name: Optional[str] = None
            if is_nested_element:
                container = parent_containers[element]
                parent_name = element_names[container]
                for subcircuit_name, elements in nested_elements[container].items():
                    if element in elements:
                        break
                else:
                    raise ValueError(
                        f"Could not find the subcircuit that should contain the nested element: {element}"
                    )

            for settings in widgets[element]:
                label: str = f"{element_names[element]} - {settings.key}"
                tooltip: str = (
                    f"Description: {element.get_value_description(settings.key)}\n\n"
                    + f"Unit: {element.get_unit(settings.key)}"
                )
                if is_nested_element:
                    label += (
                        f" (nested inside {parent_name}'s {subcircuit_name} subcircuit)"
                    )
                    tooltip = f"*Nested inside {parent_name}'s {subcircuit_name} subcircuit\n\n{tooltip}"

                i: int = label.rfind(")")
                if len(label) > 48 and (i < 0 or i > 49):
                    label = label[:45] + "..."

                settings.set_label(label)
                settings.set_tooltip(tooltip)
                if settings.element in folded:
                    dpg.set_value(
                        settings.header,
                        folded[settings.element].get(settings.key, True),
                    )

        self.update()
        dpg.split_frame(delay=67)

        self.nyquist_plot.queue_limits_adjustment()
        self.bode_plot.queue_limits_adjustment()
        self.impedance_plot.queue_limits_adjustment()
        dpg.split_frame(delay=67)

    def set_data(self, data: DataSet, num_per_decade: int):
        self.data = data
        self.marker_frequencies = data.get_frequencies()
        self.line_frequencies = _interpolate(
            self.marker_frequencies,
            num_per_decade=num_per_decade,
        )
        if len(self.marker_frequencies) >= len(self.line_frequencies):
            self.line_frequencies = self.marker_frequencies

        Z_markers: ndarray = self.data.get_impedances()
        if not isinf(Z_markers).all():
            self.nyquist_plot.update(
                index=0,
                impedances=Z_markers,
            )
            self.bode_plot.update(
                index=0,
                frequencies=self.marker_frequencies,
                impedances=Z_markers,
            )
            self.impedance_plot.update(
                index=0,
                frequencies=self.marker_frequencies,
                impedances=Z_markers,
            )
        else:
            self.nyquist_plot.hide_series(index=0)
            self.bode_plot.hide_series(index=0)
            self.impedance_plot.hide_series(index=0)

    def fold_all(self):
        for header in dpg.get_item_children(self.sidebar_window, slot=1):
            dpg.set_value(header, False)

    def unfold_all(self):
        for header in dpg.get_item_children(self.sidebar_window, slot=1):
            dpg.set_value(header, True)

    def create_window(self, window: int):
        with dpg.group(horizontal=True, parent=window):
            with dpg.group():
                self.sidebar_window: Tag = dpg.generate_uuid()
                with dpg.child_window(width=400, height=-24, tag=self.sidebar_window):
                    pass

                with dpg.group(horizontal=True):
                    dpg.add_button(
                        label="Fold all",
                        width=196,
                        callback=self.fold_all,
                    )
                    dpg.add_button(
                        label="Unfold all",
                        width=196,
                        callback=self.unfold_all,
                    )

            with dpg.group():
                with dpg.child_window(border=False, width=-1, height=-24):
                    self.create_plots()

                with dpg.group(horizontal=True):
                    self.admittance_checkbox: Tag = dpg.generate_uuid()
                    dpg.add_checkbox(
                        label="Y",
                        default_value=False,
                        callback=lambda s, a, u: self.toggle_plot_admittance(a),
                        tag=self.admittance_checkbox,
                    )
                    attach_tooltip(tooltips.general.plot_admittance)

                    dpg.add_child_window(width=-150, height=1, border=False)
                    dpg.add_button(
                        label="Accept circuit",
                        width=-1,
                        callback=self.callback,
                    )

    def create_plots(self):
        self.plot_tab_bar: Tag = dpg.generate_uuid()
        with dpg.tab_bar(tag=self.plot_tab_bar):
            self.create_nyquist_plot()
            self.create_bode_plot()
            self.create_impedance_plot()

        pad_tab_labels(self.plot_tab_bar)

    def toggle_plot_admittance(self, admittance: bool):
        dpg.set_value(self.admittance_checkbox, admittance)
        self.nyquist_plot.set_admittance(admittance)
        self.bode_plot.set_admittance(admittance)
        self.impedance_plot.set_admittance(admittance)

    def create_nyquist_plot(self):
        with dpg.tab(label="Nyquist"):
            self.nyquist_plot: Nyquist = Nyquist(width=-1, height=-1)
            Z: ndarray = (
                self.data.get_impedances() if self.data is not None else array([])
            )
            self.nyquist_plot.plot(
                impedances=Z,
                label="Data",
                theme=themes.nyquist.data,
            )

            self.nyquist_plot.plot(
                impedances=array([], dtype=complex128),
                label="Sim.",
                show_label=False,
                line=False,
                simulation=True,
                theme=themes.nyquist.simulation,
            )
            self.nyquist_plot.plot(
                impedances=array([], dtype=complex128),
                label="Sim.",
                line=True,
                simulation=True,
                theme=themes.nyquist.simulation,
            )

    def create_bode_plot(self):
        with dpg.tab(label="Bode"):
            self.bode_plot: Bode = Bode(width=-1, height=-1)
            freq: ndarray = (
                self.data.get_frequencies() if self.data is not None else array([])
            )
            Z: ndarray = (
                self.data.get_impedances() if self.data is not None else array([])
            )
            self.bode_plot.plot(
                frequencies=freq,
                impedances=Z,
                labels=(
                    "Mod(data)",
                    "Phase(data)",
                ),
                line=False,
                themes=(
                    themes.bode.magnitude_data,
                    themes.bode.phase_data,
                ),
            )

            self.bode_plot.plot(
                frequencies=array([]),
                impedances=array([], dtype=complex128),
                labels=(
                    "Mod(sim.)",
                    "Phase(sim.)",
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
                frequencies=array([]),
                impedances=array([], dtype=complex128),
                labels=(
                    "Mod(sim.)",
                    "Phase(sim.)",
                ),
                line=True,
                fit=True,
                themes=(
                    themes.bode.magnitude_simulation,
                    themes.bode.phase_simulation,
                ),
            )

    def create_impedance_plot(self):
        with dpg.tab(label="Real & imag."):
            self.impedance_plot: Impedance = Impedance(width=-1, height=-1)
            freq: ndarray = (
                self.data.get_frequencies() if self.data is not None else array([])
            )
            Z: ndarray = (
                self.data.get_impedances() if self.data is not None else array([])
            )
            self.impedance_plot.plot(
                frequencies=freq,
                impedances=Z,
                labels=(
                    "Re(data)",
                    "Im(data)",
                ),
                line=False,
                themes=(
                    themes.impedance.real_data,
                    themes.impedance.imaginary_data,
                ),
            )

            self.impedance_plot.plot(
                frequencies=array([]),
                impedances=array([], dtype=complex128),
                labels=(
                    "Re(sim.)",
                    "Im(sim.)",
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
                frequencies=array([]),
                impedances=array([], dtype=complex128),
                labels=(
                    "Re(sim.)",
                    "Im(sim.)",
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
        slider_width: int,
        label_pad: int,
    ) -> ParameterSettings:
        settings: ParameterSettings = ParameterSettings(
            element=element,
            key=key,
            header=dpg.generate_uuid(),
            tooltip=dpg.generate_uuid(),
            value_input=dpg.generate_uuid(),
            fixed_checkbox=dpg.generate_uuid(),
            value_slider=dpg.generate_uuid(),
            si_prefix_combo=dpg.generate_uuid(),
            lower_limit_input=dpg.generate_uuid(),
            lower_limit_checkbox=dpg.generate_uuid(),
            upper_limit_input=dpg.generate_uuid(),
            upper_limit_checkbox=dpg.generate_uuid(),
            callback=self.update,
        )

        with dpg.collapsing_header(
            label=f"{element.get_symbol()}_x - {key}",
            default_open=True,
            user_data=settings,
            tag=settings.header,
            parent=self.sidebar_window,
        ):
            self.parameter_value_input(
                settings=settings,
                slider_width=slider_width,
                label_pad=label_pad,
            )
            self.parameter_limit_inputs(
                settings=settings,
                slider_width=slider_width,
                label_pad=label_pad,
            )
            with dpg.group(horizontal=True):
                dpg.add_button(label="Reset", callback=settings.reset)
                dpg.add_text("?")
                attach_tooltip("PLACEHOLDER", tag=settings.tooltip)

            dpg.add_spacer(height=8)

        self.input_widgets.extend(
            [
                _
                for _ in (
                    settings.value_input,
                    settings.lower_limit_input,
                    settings.upper_limit_input,
                )
                if _ > 0
            ]
        )
        return settings

    def parameter_value_input(
        self,
        settings: ParameterSettings,
        slider_width: int,
        label_pad: int,
    ):
        with dpg.group(horizontal=True):
            dpg.add_text("Value".rjust(label_pad))
            dpg.add_input_float(
                default_value=0.0,
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
                default_value=0.0,
                format="",
                no_input=True,
                min_value=0.0,
                max_value=3.0,
                callback=settings.set_value,
                width=slider_width,
                tag=settings.value_slider,
            )
            dpg.add_combo(
                default_value="",
                items=list(SI_PREFIXES.keys()),
                callback=settings.set_si_prefix,
                width=-1,
                tag=settings.si_prefix_combo,
            )

    def parameter_limit_inputs(
        self,
        settings: ParameterSettings,
        slider_width: int,
        label_pad: int,
    ):
        with dpg.group(horizontal=True):
            dpg.add_text("Lower limit".rjust(label_pad))
            dpg.add_input_float(
                default_value=-inf,
                step=0,
                format="%.4g",
                width=slider_width,
                tag=settings.lower_limit_input,
                on_enter=True,
                readonly=True,
                enabled=False,
                callback=settings.set_lower_limit,
            )
            dpg.add_checkbox(
                label="E",
                default_value=False,
                tag=settings.lower_limit_checkbox,
                callback=settings.toggle_lower_limit,
            )
            attach_tooltip("Enabled")

        with dpg.group(horizontal=True):
            dpg.add_text("Upper limit".rjust(label_pad))
            dpg.add_input_float(
                default_value=inf,
                step=0,
                format="%.4g",
                width=slider_width,
                tag=settings.upper_limit_input,
                on_enter=True,
                readonly=True,
                enabled=False,
                callback=settings.set_upper_limit,
            )
            dpg.add_checkbox(
                label="E",
                default_value=False,
                tag=settings.upper_limit_checkbox,
                callback=settings.toggle_upper_limit,
            )
            attach_tooltip("Enabled")

    def add_element(self, element: Element) -> List[ParameterSettings]:
        all_settings: List[ParameterSettings] = []

        key: str
        for key in element.get_values().keys():
            settings: ParameterSettings = self.parameter_heading(
                element=element,
                key=key,
                slider_width=230,
                label_pad=12,
            )
            all_settings.append(settings)

            settings.set_value(
                sender=-1,
                value=settings.get_value(),
            )

            settings.set_lower_limit(
                sender=-1,
                value=settings.get_lower_limit(),
            )

            settings.set_upper_limit(
                sender=-1,
                value=settings.get_upper_limit(),
            )

        return all_settings

    def clear_widgets(self):
        dpg.delete_item(self.sidebar_window, children_only=True)
        self.input_widgets.clear()

    def update(self):
        try:
            Z_markers: ndarray = self.circuit.get_impedances(self.marker_frequencies)
            if isinf(Z_markers).any():
                raise InfiniteImpedance()
            elif isnan(Z_markers).any():
                raise NotANumberImpedance()

            Z_line: ndarray = self.circuit.get_impedances(self.line_frequencies)
            if isinf(Z_line).any():
                raise InfiniteImpedance()
            elif isnan(Z_line).any():
                raise NotANumberImpedance()

        except (InfiniteImpedance, NotANumberImpedance):
            Z_markers = array([], dtype=complex128)
            Z_line = array([], dtype=complex128)
        except Exception:
            dpg.split_frame(delay=60)
            self.callback(None)
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
            index=1,
            impedances=Z_markers,
        )
        self.nyquist_plot.update(
            index=2,
            impedances=Z_line,
        )
        self.bode_plot.update(
            index=1,
            frequencies=self.marker_frequencies,
            impedances=Z_markers,
        )
        self.bode_plot.update(
            index=2,
            frequencies=self.line_frequencies,
            impedances=Z_line,
        )
        self.impedance_plot.update(
            index=1,
            frequencies=self.marker_frequencies,
            impedances=Z_markers,
        )
        self.impedance_plot.update(
            index=2,
            frequencies=self.line_frequencies,
            impedances=Z_line,
        )

    def has_active_input(self) -> bool:
        widget: int
        for widget in self.input_widgets:
            if dpg.does_item_exist(widget) and dpg.is_item_active(widget):
                return True

        return False

    def cycle_plot_tab(self, step: int):
        tabs: List[Tag] = dpg.get_item_children(self.plot_tab_bar, slot=1)
        index: int = tabs.index(dpg.get_value(self.plot_tab_bar)) + step
        dpg.set_value(self.plot_tab_bar, tabs[index % len(tabs)])
