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

from enum import (
    IntEnum,
    auto,
)
from typing import (
    Callable,
    Dict,
    List,
    Optional,
    Tuple,
    Type,
)
from numpy import array
from pyimpspec import (
    Circuit,
    Connection,
    Container,
    Element,
    Series,
    get_elements,
    parse_cdc,
)
import dearpygui.dearpygui as dpg
from deareis.signals import Signal
import deareis.signals as signals
from deareis.utility import (
    calculate_window_position_dimensions,
    pad_tab_labels,
    process_cdc,
)
from deareis.gui.circuit_editor.parser import (
    Node,
    Parser,
)
from deareis.gui.circuit_editor.parameters import ParameterAdjustment
import deareis.themes as themes
from deareis.tooltips import (
    attach_tooltip,
    update_tooltip,
)
import deareis.tooltips as tooltips
from deareis.enums import Action
from deareis.keybindings import (
    Keybinding,
    TemporaryKeybindingHandler,
)
from deareis.data.data_sets import DataSet
from deareis.typing.helpers import Tag


FIRST_TIME_OPENING: bool = True

# TODO: Keybindings
# - Add dummy
# - Parse CDC
# - Clear


class ContainerOption(IntEnum):
    DEFAULT = auto()
    CUSTOM = auto()
    SHORT = auto()
    OPEN = auto()


CONTAINER_OPTIONS_TO_LABELS: Dict[ContainerOption, str] = {
    ContainerOption.DEFAULT: "Default",
    ContainerOption.CUSTOM: "Custom",
    ContainerOption.SHORT: "Short",
    ContainerOption.OPEN: "Open",
}
LABELS_TO_CONTAINER_OPTIONS: Dict[str, ContainerOption] = {
    v: k for k, v in CONTAINER_OPTIONS_TO_LABELS.items()
}


# TODO: Update e.g. circuit.get_elements(recursive=X)
class CircuitEditor:
    def __init__(
        self,
        window: int,
        callback: Callable,
        keybindings: List[Keybinding] = [],
    ):
        assert type(window) is int and dpg.does_item_exist(window), window
        self.window: int = window
        self.node_inputs: List[int] = []
        self.callback: Callable = callback
        self.current_node: Optional[Node] = None
        self.setup_window()

        self.register_global_keybindings(keybindings)
        self.register_diagram_keybindings(keybindings)
        self.register_parameter_adjustment_keybindings(keybindings)

        self.global_keybinding_handler.block()
        self.diagram_keybinding_handler.block()
        self.parameter_adjustment_keybinding_handler.block()

    def accept(self, keybinding: bool = False):
        if keybinding and (
            self.has_active_input() or self.parameter_adjustment.has_active_input()
        ):
            return

        self.callback(dpg.get_item_user_data(self.accept_button))

    def register_global_keybindings(self, keybindings: List[Keybinding]):
        callbacks: Dict[Keybinding, Callable] = {}

        # Cancel
        kb: Keybinding = Keybinding(
            key=dpg.mvKey_Escape,
            mod_alt=False,
            mod_ctrl=False,
            mod_shift=False,
            action=Action.CANCEL,
        )
        callbacks[kb] = lambda: self.callback(None)

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

        # Previous tab in the tab bar at the top
        for kb in keybindings:
            if kb.action is Action.PREVIOUS_PROGRAM_TAB:
                break
        else:
            kb = Keybinding(
                key=dpg.mvKey_Prior,
                mod_alt=False,
                mod_ctrl=False,
                mod_shift=True,
                action=Action.PREVIOUS_PROGRAM_TAB,
            )
        callbacks[kb] = lambda: self.cycle_top_tab(step=-1)

        # Next tab in the tab bar at the top
        for kb in keybindings:
            if kb.action is Action.NEXT_PROGRAM_TAB:
                break
        else:
            kb = Keybinding(
                key=dpg.mvKey_Next,
                mod_alt=False,
                mod_ctrl=False,
                mod_shift=True,
                action=Action.NEXT_PROGRAM_TAB,
            )
        callbacks[kb] = lambda: self.cycle_top_tab(step=1)

        # Create the handler
        self.global_keybinding_handler: TemporaryKeybindingHandler = (
            TemporaryKeybindingHandler(callbacks=callbacks)
        )

    def register_diagram_keybindings(self, keybindings: List[Keybinding]):
        def delete_callback():
            if not dpg.does_item_exist(self.window):
                return
            elif not dpg.is_item_shown(self.window):
                return
            elif not dpg.is_item_hovered(self.node_editor):
                return
            elif self.has_active_input():
                return

            tag: Tag
            link_tags: List[Tag] = dpg.get_selected_links(self.node_editor)
            if link_tags:
                for tag in link_tags:
                    self.delink(-1, tag)

            node_tags: List[Tag] = dpg.get_selected_nodes(self.node_editor)
            if node_tags:
                for tag in node_tags:
                    node: Node = self.parser.find_node(tag=tag)
                    if node == self.parser.we_node or node == self.parser.cere_node:
                        continue

                    self.delete_node(node)

            elif self.current_node is not None:
                if not (
                    self.current_node == self.parser.we_node
                    or self.current_node == self.parser.cere_node
                ):
                    self.delete_node(self.current_node)

        callbacks: Dict[Keybinding, Callable] = {}

        # Delete node
        for kb in keybindings:
            if kb.action is Action.DELETE_RESULT:
                break
        else:
            kb = Keybinding(
                key=dpg.mvKey_Delete,
                mod_alt=True,
                mod_ctrl=False,
                mod_shift=False,
                action=Action.DELETE_RESULT,
            )
        callbacks[kb] = delete_callback

        # Previous tab in the tab bar in the sidebar
        for kb in keybindings:
            if kb.action is Action.PREVIOUS_PROJECT_TAB:
                break
        else:
            kb = Keybinding(
                key=dpg.mvKey_Prior,
                mod_alt=False,
                mod_ctrl=True,
                mod_shift=False,
                action=Action.PREVIOUS_PROJECT_TAB,
            )
        callbacks[kb] = lambda: self.cycle_sidebar_tab(step=-1)

        # Next tab in the tab bar in the sidebar
        for kb in keybindings:
            if kb.action is Action.NEXT_PROJECT_TAB:
                break
        else:
            kb = Keybinding(
                key=dpg.mvKey_Next,
                mod_alt=False,
                mod_ctrl=True,
                mod_shift=False,
                action=Action.NEXT_PROJECT_TAB,
            )
        callbacks[kb] = lambda: self.cycle_sidebar_tab(step=1)

        # Previous circuit element
        for kb in keybindings:
            if kb.action is Action.PREVIOUS_PRIMARY_RESULT:
                break
        else:
            kb = Keybinding(
                key=dpg.mvKey_Prior,
                mod_alt=False,
                mod_ctrl=False,
                mod_shift=False,
                action=Action.PREVIOUS_PRIMARY_RESULT,
            )
        callbacks[kb] = lambda: self.cycle_nodes(step=-1)

        # Next circuit element
        for kb in keybindings:
            if kb.action is Action.NEXT_PRIMARY_RESULT:
                break
        else:
            kb = Keybinding(
                key=dpg.mvKey_Next,
                mod_alt=False,
                mod_ctrl=False,
                mod_shift=False,
                action=Action.NEXT_PRIMARY_RESULT,
            )
        callbacks[kb] = lambda: self.cycle_nodes(step=1)

        # Create the handler
        self.diagram_keybinding_handler: TemporaryKeybindingHandler = (
            TemporaryKeybindingHandler(callbacks=callbacks)
        )

    def register_parameter_adjustment_keybindings(self, keybindings: List[Keybinding]):
        callbacks: Dict[Keybinding, Callable] = {}

        # TODO
        # - Fold all?
        # - Unfold all?
        # - Admittance?

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
        callbacks[kb] = lambda: self.parameter_adjustment.cycle_plot_tab(step=-1)

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
        callbacks[kb] = lambda: self.parameter_adjustment.cycle_plot_tab(step=1)

        # Create the handler
        self.parameter_adjustment_keybinding_handler: TemporaryKeybindingHandler = (
            TemporaryKeybindingHandler(callbacks=callbacks)
        )

    def setup_window(self):
        with dpg.group(parent=self.window):
            self.top_tab_bar: Tag = dpg.generate_uuid()
            with dpg.tab_bar(
                tag=self.top_tab_bar,
                callback=lambda s, a, u: self.top_tab_clicked(a),
            ):
                self.top_diagram_tab: Tag = dpg.generate_uuid()
                with dpg.tab(label="Diagram", tag=self.top_diagram_tab):
                    self.setup_diagram_tab()

                self.top_parameters_tab: Tag = dpg.generate_uuid()
                with dpg.tab(label="Parameters", tag=self.top_parameters_tab):
                    self.parameter_adjustment: ParameterAdjustment = (
                        ParameterAdjustment(
                            window=dpg.add_child_window(
                                border=False,
                                width=-1,
                                height=-1,
                            ),
                            callback=self.accept,
                        )
                    )

            pad_tab_labels(self.top_tab_bar)

    def setup_diagram_tab(self):
        with dpg.child_window(border=False, height=-1):
            with dpg.group(horizontal=True):
                with dpg.child_window(
                    border=False,
                    width=300,
                    height=-72,
                ):
                    self.sidebar_tab_bar: Tag = dpg.generate_uuid()
                    with dpg.tab_bar(tag=self.sidebar_tab_bar):
                        self.sidebar_elements_tab: Tag = dpg.generate_uuid()
                        with dpg.tab(
                            label="Elements".ljust(16),
                            tag=self.sidebar_elements_tab,
                        ):
                            self.elements_window: Tag = dpg.generate_uuid()
                            with dpg.child_window(
                                width=-1,
                                height=-1,
                                tag=self.elements_window,
                            ):
                                button_label_pad: int = 36

                                with dpg.child_window(
                                    border=False,
                                    width=-1,
                                    height=-52,
                                ):
                                    for element in get_elements().values():
                                        label: str = element.get_description()
                                        if len(label) > button_label_pad:
                                            label = (
                                                label[: button_label_pad - 3] + "..."
                                            )

                                        label = label.ljust(button_label_pad)

                                        element_button: Tag = dpg.generate_uuid()
                                        dpg.add_button(
                                            label=label,
                                            width=-1,
                                            callback=lambda s, a, u: self.add_element_node(
                                                u()
                                            ),
                                            user_data=element,
                                            tag=element_button,
                                        )
                                        attach_tooltip(
                                            self.generate_element_tooltip(element)
                                        )
                                        with dpg.drag_payload(
                                            parent=element_button,
                                            drag_data=element,
                                        ):
                                            dpg.add_text(label.strip())

                                dpg.add_separator()

                                dummy_node_button: Tag = dpg.generate_uuid()
                                dpg.add_button(
                                    label="Add dummy/junction".ljust(button_label_pad),
                                    callback=lambda s, a, u: self.add_dummy_node(),
                                    width=-1,
                                    tag=dummy_node_button,
                                )
                                attach_tooltip(tooltips.circuit_editor.dummy_node)
                                with dpg.drag_payload(
                                    parent=dummy_node_button,
                                    drag_data=None,
                                ):
                                    dpg.add_text("Dummy/junction node")

                                dpg.add_button(
                                    label="Rearrange nodes".ljust(button_label_pad),
                                    width=-1,
                                    callback=self.reorganize_nodes,
                                )

                        self.sidebar_node_tab: Tag = dpg.generate_uuid()
                        with dpg.tab(
                            label="Node".ljust(16),
                            tag=self.sidebar_node_tab,
                        ):
                            self.node_window: Tag = dpg.generate_uuid()
                            with dpg.child_window(
                                width=-1,
                                height=-1,
                                tag=self.node_window,
                            ):
                                pass

                with dpg.group():
                    with dpg.group(horizontal=True):
                        dpg.add_text("CDC input")
                        attach_tooltip(tooltips.circuit_editor.cdc_input)

                        self.cdc_input: Tag = dpg.generate_uuid()
                        dpg.add_input_text(
                            width=-147,
                            tag=self.cdc_input,
                            callback=lambda s, a, u: self.parse_cdc(a),
                            on_enter=True,
                        )

                        dpg.add_button(
                            label="Parse",
                            width=65,
                            callback=lambda s, a, u: self.parse_cdc(
                                dpg.get_value(self.cdc_input)
                            ),
                        )
                        attach_tooltip(tooltips.circuit_editor.parse_cdc)

                        dpg.add_button(
                            label="Clear",
                            width=65,
                            callback=lambda s, a, u: self.parse_cdc(""),
                        )
                        attach_tooltip(tooltips.circuit_editor.clear)

                    with dpg.group(drop_callback=lambda s, a, u: self.on_drop_element(a)):
                        self.node_editor: Tag = dpg.generate_uuid()
                        dpg.add_node_editor(
                            width=-1,
                            height=-72,
                            tag=self.node_editor,
                            minimap=True,
                            minimap_location=dpg.mvNodeMiniMap_Location_BottomRight,
                        )

                    self.node_handler: Tag = dpg.generate_uuid()
                    with dpg.item_handler_registry(tag=self.node_handler):
                        dpg.add_item_clicked_handler(callback=self.node_clicked)

                    self.parser: Parser = Parser(
                        self.node_editor,
                        self.node_handler,
                    )
                    dpg.configure_item(
                        self.node_editor,
                        callback=self.link,
                        delink_callback=self.delink,
                    )

            with dpg.group():
                with dpg.group(horizontal=True):
                    self.basic_cdc_output_field: Tag = dpg.generate_uuid()
                    dpg.add_input_text(
                        tag=self.basic_cdc_output_field,
                        width=-150,
                        enabled=False,
                    )
                    attach_tooltip(tooltips.circuit_editor.basic_cdc)

                    dpg.add_button(
                        label="Copy to clipboard",
                        width=-1,
                        callback=lambda: dpg.set_clipboard_text(
                            dpg.get_value(self.basic_cdc_output_field)
                        ),
                    )
                with dpg.group(horizontal=True):
                    self.extended_cdc_output_field: Tag = dpg.generate_uuid()
                    dpg.add_input_text(
                        tag=self.extended_cdc_output_field,
                        width=-150,
                        enabled=False,
                    )
                    attach_tooltip(tooltips.circuit_editor.extended_cdc)

                    dpg.add_button(
                        label="Copy to clipboard",
                        width=-1,
                        callback=lambda: dpg.set_clipboard_text(
                            dpg.get_value(self.extended_cdc_output_field)
                        ),
                    )

                with dpg.group(horizontal=True):
                    self.status_field: Tag = dpg.generate_uuid()
                    dpg.add_input_text(
                        tag=self.status_field,
                        width=-150,
                        enabled=False,
                    )
                    attach_tooltip(tooltips.circuit_editor.status)

                    self.accept_button: Tag = dpg.generate_uuid()
                    dpg.add_button(
                        label="Accept circuit",
                        width=-1,
                        callback=lambda s, a, u: self.callback(u),
                        tag=self.accept_button,
                        show=False,
                    )

                    self.cancel_button: Tag = dpg.generate_uuid()
                    dpg.add_button(
                        label="Cancel",
                        width=-1,
                        callback=lambda s, a, u: self.callback(None),
                        tag=self.cancel_button,
                    )

    def show(
        self,
        circuit: Optional[Circuit],
        data: DataSet,
        num_per_decade: int = 20,
        admittance: bool = False,
    ):
        global FIRST_TIME_OPENING
        assert isinstance(circuit, Circuit) or circuit is None, circuit
        assert isinstance(data, DataSet), data
        assert num_per_decade >= 1, num_per_decade
        assert isinstance(admittance, bool), admittance

        if circuit is not None:
            circuit = parse_cdc(circuit.serialize())

        self.clear_node_window(add_info=True)
        self.parser.circuit_to_nodes(circuit)
        self.update(circuit, update_input=True)
        self.update_outputs(circuit=circuit)
        self.update_status("OK" if circuit is not None else "", False)

        self.parameter_adjustment.set_data(data, num_per_decade)
        self.parameter_adjustment.set_circuit(circuit)
        self.parameter_adjustment.toggle_plot_admittance(admittance)

        self.global_keybinding_handler.unblock()
        active_tab: Tag = dpg.get_value(self.top_tab_bar)
        if active_tab == self.top_parameters_tab:
            self.diagram_keybinding_handler.block()
            self.parameter_adjustment_keybinding_handler.unblock()
        else:
            self.parameter_adjustment_keybinding_handler.block()
            self.diagram_keybinding_handler.unblock()

        dpg.show_item(self.window)

        if FIRST_TIME_OPENING:
            FIRST_TIME_OPENING = False
            dpg.split_frame(delay=67)
            dpg.set_value(self.sidebar_tab_bar, self.sidebar_node_tab)

    def hide(self):
        self.global_keybinding_handler.block()
        self.diagram_keybinding_handler.block()
        self.parameter_adjustment_keybinding_handler.block()
        dpg.hide_item(self.window)

    def delete(self):
        self.hide()
        self.global_keybinding_handler.delete()
        self.diagram_keybinding_handler.delete()
        self.parameter_adjustment_keybinding_handler.delete()
        dpg.delete_item(self.window)

    def is_shown(self):
        return dpg.is_item_shown(self.window)

    def update(self, circuit: Optional[Circuit], update_input: bool = False):
        dpg.hide_item(self.accept_button)
        dpg.show_item(self.cancel_button)

        if update_input:
            dpg.set_value(
                self.cdc_input, circuit.to_string() if circuit is not None else ""
            )

        if circuit is not None and circuit.to_string() not in ["[]", "()"]:
            dpg.hide_item(self.cancel_button)
            dpg.show_item(self.accept_button)
            dpg.show_item(self.top_parameters_tab)
        else:
            dpg.hide_item(self.top_parameters_tab)

        dpg.set_item_user_data(self.accept_button, circuit)

    def parse_cdc(self, cdc: str):
        assert type(cdc) is str, cdc
        self.current_node = None
        self.clear_node_window(add_info=True)

        circuit: Optional[Circuit]
        msg: str
        try:
            circuit, msg = process_cdc(cdc)
        except Exception as err:
            circuit = None
            msg = str(err)
        else:
            msg = msg or "OK"

        if circuit is not None:
            dpg.bind_item_theme(self.cdc_input, themes.cdc.valid)
            self.update_outputs(circuit=circuit)
            self.parser.circuit_to_nodes(circuit)
        else:
            dpg.bind_item_theme(self.cdc_input, themes.cdc.invalid)
            self.update_outputs(stack=[])
            self.parser.clear_nodes()

        self.update_status(msg, circuit is None)
        self.update(circuit, update_input=cdc == "")
        if cdc == "":
            dpg.set_value(self.sidebar_tab_bar, self.sidebar_elements_tab)

    def update_status(self, msg: str, invalid: bool):
        dpg.set_value(self.status_field, msg)
        if invalid:
            dpg.bind_item_theme(self.status_field, themes.cdc.invalid)
        else:
            dpg.bind_item_theme(self.status_field, themes.cdc.valid)

    def update_outputs(self, circuit: Optional[Circuit] = None, stack: List[str] = []):
        assert type(circuit) is Circuit or (circuit is None and type(stack) is list), (
            circuit,
            stack,
        )

        theme: int = themes.cdc.valid
        basic_output: str = ""
        extended_output: str = ""

        if circuit is not None:
            basic_output = circuit.to_string()
            extended_output = circuit.to_string(4)
        else:
            theme = themes.cdc.invalid
            basic_output = "".join(
                map(lambda _: _[: _.find("{")] if "{" in _ else _, stack)
            )
            extended_output = "".join(stack)

        dpg.set_value(self.basic_cdc_output_field, basic_output)
        dpg.set_value(self.extended_cdc_output_field, extended_output)
        dpg.bind_item_theme(self.basic_cdc_output_field, theme)
        dpg.bind_item_theme(self.extended_cdc_output_field, theme)

    def clear_node_window(self, add_info: bool = False):
        self.node_inputs.clear()
        dpg.delete_item(self.node_window, children_only=True)
        if add_info:
            dpg.add_text(
                tooltips.circuit_editor.node_help,
                wrap=270,
                parent=self.node_window,
            )

    def replace_equation(self, lines: List[str], prefix: str) -> List[str]:
        i: int
        line: str
        for i, line in enumerate(map(str.strip, lines)):
            if line.startswith(prefix):
                lines[i] = "See documentation for equation(s)."
                break
        else:
            return lines

        i += 1
        if lines[i].strip() == "":
            i += 1

        line = lines.pop(i)
        while not (line == "Parameters" or line == "Subcircuits"):
            if not lines:
                break
            line = lines.pop(i)

        return lines

    def move_equation(self, lines: List[str], prefix: str) -> List[str]:
        j: int = -1
        k: int = -1

        i: int
        line: str
        for i, line in enumerate(map(str.strip, lines)):
            if line.startswith(prefix):
                # lines[i] = f"Z = {element._equation}"
                j = i
            elif line == "Parameters" or line == "Subcircuits":
                k = i
                break

        if j < 0:
            return lines

        equation_lines: List[str] = [
            "Equation",
            "--------",
        ]

        if k == -1:
            k = j + 1

        while k > j:
            equation_lines.append(lines.pop(j))
            k -= 1

        if lines[j].strip() == "":
            lines.pop(j)

        for i, line in enumerate(map(str.strip, lines[j:])):
            if line == "Parameters" or line == "Subcircuits":
                break

        for i in range(j, i):
            equation_lines.append(lines.pop(j))

        lines.extend(equation_lines)
        return lines

    def generate_element_tooltip(self, element: Type[Element]) -> str:
        lines: List[str] = element.get_extended_description().split("\n")
        prefix: str = ":math:`Z = "

        replace_equation: bool = True
        if replace_equation is True:
            lines = self.replace_equation(lines, prefix)
        else:
            lines = self.move_equation(lines, prefix)

        return "\n".join(lines).strip()

    def node_clicked(self, sender: Tag, app_data: tuple):
        self.clear_node_window()
        dpg.clear_selected_nodes(self.node_editor)
        dpg.clear_selected_links(self.node_editor)
        if self.current_node is not None and dpg.does_item_exist(self.current_node.tag):
            self.current_node.set_unselected()

        node: Node = self.parser.find_node(tag=app_data[1])
        self.current_node = node
        node.set_selected()

        dpg.set_value(self.sidebar_tab_bar, self.sidebar_node_tab)

        with dpg.child_window(
            border=False,
            width=-1,
            height=-24,
            parent=self.node_window,
        ):
            if node.id == self.parser.we_node.id or node.id == self.parser.cere_node.id:
                with dpg.group():
                    dpg.add_text(
                        (
                            "Working electrode"
                            if node.id == self.parser.we_node.id
                            else "Counter and reference electrodes"
                        )
                        + "\n\nOne of the terminals in the circuit.",
                        wrap=220,
                    )

            elif node.id < 0:
                with dpg.group():
                    dpg.add_text(
                        "Dummy node\n\n" + tooltips.circuit_editor.dummy_node,
                        wrap=220,
                    )
                    dpg.add_separator()
                    dpg.add_button(
                        label="Delete",
                        width=-1,
                        callback=lambda s, a, u: self.delete_node(node),
                    )

            else:
                element: Element = node.element
                with dpg.group():
                    with dpg.group(horizontal=True):
                        attach_tooltip(
                            self.generate_element_tooltip(element),
                            parent=dpg.add_text("?"),
                        )

                        label = element.get_description()
                        if len(label) > 30:
                            label = label[:27] + "..."

                        dpg.add_text(label)

                    with dpg.group(horizontal=True):
                        dpg.add_text("Label")
                        default_label: str = str(
                            self.parser.element_identifiers[element]
                        )
                        hint: str = default_label

                        def update_label(sender: Tag, new_label: str):
                            assert type(sender) is int
                            assert type(new_label) is str

                            new_label = new_label.strip()
                            try:
                                int(new_label)
                                new_label = ""
                                dpg.set_value(sender, "")
                                return
                            except ValueError:
                                pass

                            if new_label == default_label:
                                new_label = ""

                            if (
                                new_label == ""
                                and not dpg.get_value(sender) == new_label
                            ):
                                dpg.set_value(sender, new_label)

                            element.set_label(new_label)
                            if new_label == "":
                                new_label = str(
                                    self.parser.element_identifiers[element]
                                )

                            node.set_label(f"{element.get_symbol()}_{new_label}")
                            self.validate_nodes()

                        current_label: str = element.get_label()
                        self.node_inputs.append(
                            dpg.add_input_text(
                                hint=hint,
                                default_value=current_label
                                if current_label != hint
                                else "",
                                width=-1,
                                callback=update_label,
                                on_enter=True,
                            )
                        )
                    dpg.add_spacer(height=8)

                    if isinstance(element, Container):
                        con: Optional[Connection]
                        for key, con in element.get_subcircuits().items():
                            self.node_subcircuit(element, key, con)

                    dpg.add_separator()
                    dpg.add_button(
                        label="Delete",
                        width=-1,
                        callback=lambda s, a, u: self.delete_node(node),
                    )

        dpg.add_text("? How to use nodes", parent=self.node_window)
        attach_tooltip(tooltips.circuit_editor.node_help)

    def delete_node(self, node: Node):
        assert type(node) is Node, node
        if node == self.current_node:
            self.current_node = None

        self.parser.delete_node(node)
        self.validate_nodes()
        self.clear_node_window(add_info=True)
        dpg.set_value(self.sidebar_tab_bar, self.sidebar_elements_tab)

    def add_element_node(self, element: Optional[Element], **kwargs):
        assert element is None or isinstance(element, Element), element
        if element is None:
            return

        self.parser.add_element_node(element, **kwargs)
        self.validate_nodes()

    def add_dummy_node(self, **kwargs):
        self.parser.add_dummy_node(**kwargs)
        self.validate_nodes()

    def node_subcircuit(
        self,
        element: Container,
        key: str,
        initial_value: Optional[Connection],
    ):
        assert isinstance(element, Container)
        assert type(key) is str
        assert isinstance(initial_value, Connection) or initial_value is None
        items: List[str] = list(CONTAINER_OPTIONS_TO_LABELS.values())
        default_value: Optional[Connection] = element.get_default_subcircuit(key)
        combo: Tag = dpg.generate_uuid()
        cdc_input: Tag = dpg.generate_uuid()
        cdc_tooltip: Tag = dpg.generate_uuid()
        edit_button: Tag = dpg.generate_uuid()
        value_group: Tag = dpg.generate_uuid()

        def choose_option(
            sender: Tag,
            new_value: str,
        ):
            dpg.hide_item(dpg.get_item_parent(cdc_tooltip))
            dpg.bind_item_theme(cdc_input, themes.cdc.normal)
            enum: ContainerOption = LABELS_TO_CONTAINER_OPTIONS[new_value]
            dpg.set_value(sender, new_value)

            if enum == ContainerOption.CUSTOM:  # Custom
                dpg.show_item(value_group)
                dpg.set_value(
                    cdc_input,
                    initial_value.to_string() if initial_value is not None else "",
                )
                dpg.enable_item(cdc_input)
                dpg.enable_item(edit_button)
                element.set_subcircuits(key, initial_value)
            else:
                if enum == ContainerOption.DEFAULT:
                    if default_value is None:
                        enum = ContainerOption.OPEN
                    elif len(default_value) == 0:
                        enum = ContainerOption.SHORT
                    else:
                        dpg.set_value(cdc_input, default_value.to_string())
                        dpg.show_item(value_group)
                        dpg.disable_item(cdc_input)
                        dpg.disable_item(edit_button)
                        element.set_subcircuits(key, default_value)

                if enum != ContainerOption.DEFAULT:
                    dpg.hide_item(value_group)
                    if enum == ContainerOption.SHORT:
                        element.set_subcircuits(key, Series([]))
                    elif enum == ContainerOption.OPEN:
                        element.set_subcircuits(key, None)
                    dpg.set_value(sender, CONTAINER_OPTIONS_TO_LABELS[enum])

            self.validate_nodes()

        def parse_cdc(
            sender: Tag,
            cdc: str,
            tooltip: int,
            update: bool = False,
        ):
            circuit: Optional[Circuit]
            msg: str
            try:
                circuit, msg = process_cdc(cdc)
            except Exception as err:
                circuit = None
                msg = str(err)

            if circuit is None:
                dpg.bind_item_theme(sender, themes.cdc.invalid)
                update_tooltip(tooltip, msg)
                dpg.show_item(dpg.get_item_parent(tooltip))
                dpg.set_item_user_data(edit_button, default_value)
                element.set_subcircuits(key, default_value)
                self.validate_nodes()
                return

            dpg.bind_item_theme(cdc_input, themes.cdc.normal)
            dpg.hide_item(dpg.get_item_parent(tooltip))

            connection: Connection = circuit.get_connections(recursive=False)[0]
            dpg.set_item_user_data(edit_button, connection)
            element.set_subcircuits(key, connection)
            if update is True:
                dpg.set_value(sender, connection.to_string())

            self.validate_nodes()

        def show_subcircuit_editor():
            circuit: Optional[Circuit] = None
            con: Optional[Connection] = dpg.get_item_user_data(edit_button)
            if con is not None:
                circuit, _ = process_cdc(con.serialize())

            self.hide()

            dpg.split_frame(delay=33)

            subcircuit_editor: "CircuitEditor"
            subcircuit_editor = None  # type: ignore

            def callback(circuit: Optional[Circuit]):
                subcircuit_editor.hide()
                dpg.split_frame(delay=33)
                dpg.delete_item(subcircuit_editor.window)

                dpg.show_item(self.window)
                self.global_keybinding_handler.unblock()
                self.diagram_keybinding_handler.unblock()
                signals.emit(
                    Signal.BLOCK_KEYBINDINGS,
                    window=self.window,
                    window_object=self,
                )
                if circuit is not None:
                    parse_cdc(
                        cdc_input,
                        circuit.serialize(),
                        cdc_tooltip,
                        update=True,
                    )

            subcircuit_editor = CircuitEditor(
                window=dpg.add_window(
                    label=f"Subcircuit editor - {key}",
                    show=False,
                    modal=True,
                    on_close=lambda s, a, u: callback(None),
                ),
                callback=callback,
            )

            x: int
            y: int
            w: int
            h: int
            x, y, w, h = calculate_window_position_dimensions()
            dpg.configure_item(
                subcircuit_editor.window,
                pos=(
                    x,
                    y,
                ),
                width=w,
                height=h,
            )

            signals.emit(
                Signal.BLOCK_KEYBINDINGS,
                window=subcircuit_editor.window,
                window_object=subcircuit_editor,
            )
            subcircuit_editor.show(
                circuit,
                data=self.parameter_adjustment.data,
                admittance=dpg.get_value(self.parameter_adjustment.admittance_checkbox),
            )

        label_pad: int = 8
        with dpg.collapsing_header(label=f" {key}", leaf=True):
            tooltip: str = ""
            description: str = element.get_subcircuit_description(key).strip()
            unit: str = element.get_unit(key).strip()
            if description != "" or unit != "":
                tooltip = (
                    description + (f"\n[{key}] = {unit}" if unit != "" else "")
                ).strip()

            with dpg.group(horizontal=True):
                dpg.add_text("Options".rjust(label_pad))
                if tooltip != "":
                    attach_tooltip(tooltip)

                dpg.add_combo(
                    default_value="",
                    items=items,
                    callback=choose_option,
                    width=-1,
                    tag=combo,
                )

            with dpg.group(horizontal=True, tag=value_group):
                dpg.add_text("Circuit".rjust(label_pad))
                if tooltip != "":
                    attach_tooltip(tooltip)

                dpg.add_input_text(
                    width=-46,
                    on_enter=True,
                    callback=parse_cdc,
                    user_data=cdc_tooltip,
                    tag=cdc_input,
                )
                attach_tooltip("", tag=cdc_tooltip, parent=cdc_input)

                dpg.add_button(
                    label="Edit",
                    callback=show_subcircuit_editor,
                    tag=edit_button,
                    user_data=initial_value,
                )

        dpg.add_spacer(height=8)

        enum = ContainerOption.DEFAULT
        if initial_value is None:
            enum = ContainerOption.OPEN
        elif len(initial_value) == 0:
            enum = ContainerOption.SHORT
        elif (
            default_value is None
            or initial_value.serialize() != default_value.serialize()
        ):
            enum = ContainerOption.CUSTOM

        choose_option(combo, CONTAINER_OPTIONS_TO_LABELS[enum])

    def reorganize_nodes(self):
        circuit: Optional[Circuit] = dpg.get_item_user_data(self.accept_button)
        if circuit is not None:
            self.parse_cdc(circuit.serialize())

    def validate_nodes(self):
        circuit: Optional[Circuit]
        msg: str
        stack: List[str]
        circuit, msg, stack = self.parser.generate_circuit()
        if circuit is not None:
            try:
                circuit.get_impedances(array([1e-3, 1e0, 1e3]))
            except Exception as err:
                circuit = None
                msg = str(err)

        if circuit is None:
            self.update_outputs(stack=stack)
            self.update_status(msg, True)
        else:
            self.update_outputs(circuit=circuit)
            self.update_status("OK", False)

        self.update(circuit)

    def link(self, sender: Tag, attributes: Tuple[Tag, Tag]):
        self.parser.link(sender, attributes)
        self.validate_nodes()

    def delink(self, sender: Tag, link: Tag):
        self.parser.delink(sender, link)
        self.validate_nodes()

    def cycle_nodes(self, step: int):
        nodes: List[Node] = self.parser.nodes
        if len(nodes) < 2:
            return

        index: int
        if self.current_node is not None and self.current_node in nodes:
            index = nodes.index(self.current_node) + step
        elif step >= 0:
            index = 0
        elif step < 0:
            index = -1

        node: Node = nodes[index % len(nodes)]
        self.node_clicked(self.node_handler, (dpg.mvMouseButton_Left, node.tag))

    def has_active_input(self) -> bool:
        return (
            dpg.is_item_active(self.cdc_input)
            or dpg.is_item_active(self.basic_cdc_output_field)
            or dpg.is_item_active(self.extended_cdc_output_field)
            or dpg.is_item_active(self.status_field)
            or any(map(lambda _: dpg.is_item_active(_), self.node_inputs))
        )

    def cycle_sidebar_tab(self, step: int):
        tabs: List[Tag] = dpg.get_item_children(self.sidebar_tab_bar, slot=1)
        index: int = tabs.index(dpg.get_value(self.sidebar_tab_bar)) + step
        dpg.set_value(self.sidebar_tab_bar, tabs[index % len(tabs)])

    def cycle_top_tab(self, step: int):
        tabs: List[Tag] = dpg.get_item_children(self.top_tab_bar, slot=1)
        if len(list(filter(dpg.is_item_visible, tabs))) < 2:
            return

        index: int = tabs.index(dpg.get_value(self.top_tab_bar)) + step
        tab: Tag = tabs[index % len(tabs)]
        dpg.set_value(self.top_tab_bar, tab)
        self.top_tab_clicked(tab)

    def top_tab_clicked(self, tab: Tag):
        circuit: Optional[Circuit] = dpg.get_item_user_data(self.accept_button)
        if tab == self.top_diagram_tab:
            self.parameter_adjustment_keybinding_handler.block()
            self.update_outputs(circuit=circuit)
            self.diagram_keybinding_handler.unblock()
        elif tab == self.top_parameters_tab:
            self.diagram_keybinding_handler.block()
            self.parameter_adjustment.set_circuit(circuit=circuit)
            self.parameter_adjustment_keybinding_handler.unblock()

    def on_drop_element(self, element: Optional[Type[Element]]):
        # WE node as the reference point
        # - Grid coordinates
        rgx, rgy = dpg.get_item_pos(self.parser.we_node.tag)
        # - Screen coordinates
        rsx, rsy = dpg.get_item_rect_min(self.parser.we_node.tag)

        # New node
        # - Screen coordinates
        sx, sy = dpg.get_mouse_pos(local=False)
        # - Grid coordinates
        gx = sx - rsx + rgx
        gy = sy - rsy + rgy

        if element is None:
            self.add_dummy_node(x=gx, y=gy)
        else:
            self.add_element_node(element(), x=gx, y=gy)
