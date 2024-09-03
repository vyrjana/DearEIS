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
from numpy import (
    array,
    inf,
    isinf,
)
from pyimpspec import (
    Circuit,
    Connection,
    Container,
    Element,
    Series,
)
import pyimpspec
import dearpygui.dearpygui as dpg
from deareis.signals import Signal
import deareis.signals as signals
from deareis.utility import (
    calculate_window_position_dimensions,
    process_cdc,
)
from deareis.gui.circuit_editor.parser import (
    Node,
    Parser,
)
import deareis.themes as themes
from deareis.tooltips import (
    attach_tooltip,
    update_tooltip,
)
import deareis.tooltips as tooltips
from deareis.keybindings import (
    is_alt_down,
    is_control_down,
)
from deareis.enums import Action
from deareis.keybindings import (
    Keybinding,
    TemporaryKeybindingHandler,
)

# TODO: Keybindings
# - Add dummy
# - Add element
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


class CircuitEditor:
    def __init__(
        self,
        window: int,
        callback: Callable,
        keybindings: List[Keybinding] = [],
    ):
        assert type(window) is int and dpg.does_item_exist(window), window
        self.window: int = window
        self.parameter_inputs: List[int] = []
        self.callback: Callable = callback
        self.current_node: Optional[Node] = None
        self.setup_window()
        self.register_keybindings(keybindings)
        self.keybinding_handler.block()

    def register_keybindings(self, keybindings: List[Keybinding]):
        def delete_callback():
            if not dpg.does_item_exist(self.window):
                return
            elif not dpg.is_item_shown(self.window):
                return
            elif not dpg.is_item_hovered(self.node_editor):
                return
            elif self.has_active_input():
                return
            tag: int
            link_tags: List[int] = dpg.get_selected_links(self.node_editor)
            if link_tags:
                for tag in link_tags:
                    self.delink(-1, tag)
            node_tags: List[int] = dpg.get_selected_nodes(self.node_editor)
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

        def accept_callback():
            if self.has_active_input():
                return
            self.callback(dpg.get_item_user_data(self.accept_button))

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
        callbacks[kb] = accept_callback
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
        # Previous circuit node
        for kb in keybindings:
            if kb.action is Action.PREVIOUS_SECONDARY_RESULT:
                break
        else:
            kb = Keybinding(
                key=dpg.mvKey_Prior,
                mod_alt=True,
                mod_ctrl=False,
                mod_shift=False,
                action=Action.PREVIOUS_SECONDARY_RESULT,
            )
        callbacks[kb] = lambda: self.cycle_elements(step=-1)
        # Next circuit node
        for kb in keybindings:
            if kb.action is Action.NEXT_SECONDARY_RESULT:
                break
        else:
            kb = Keybinding(
                key=dpg.mvKey_Next,
                mod_alt=True,
                mod_ctrl=False,
                mod_shift=False,
                action=Action.NEXT_SECONDARY_RESULT,
            )
        callbacks[kb] = lambda: self.cycle_elements(step=1)
        # Create the handler
        self.keybinding_handler: TemporaryKeybindingHandler = (
            TemporaryKeybindingHandler(callbacks=callbacks)
        )

    def setup_window(self):
        with dpg.group(horizontal=True, parent=self.window):
            self.parameter_window: int = dpg.generate_uuid()
            with dpg.child_window(width=250, tag=self.parameter_window):
                pass
            with dpg.group():
                with dpg.group(horizontal=True):
                    dpg.add_text("CDC input")
                    attach_tooltip(tooltips.circuit_editor.cdc_input)
                    self.cdc_input: int = dpg.generate_uuid()
                    dpg.add_input_text(
                        width=-147,
                        tag=self.cdc_input,
                        callback=lambda s, a, u: self.parse_cdc(a),
                        on_enter=True,
                    )
                    dpg.add_button(
                        label="Parse",
                        width=50,
                        callback=lambda s, a, u: self.parse_cdc(
                            dpg.get_value(self.cdc_input)
                        ),
                    )
                    attach_tooltip(tooltips.circuit_editor.parse_cdc)
                    dpg.add_button(
                        label="Clear",
                        width=80,
                        callback=lambda s, a, u: self.parse_cdc(""),
                    )
                    attach_tooltip(tooltips.circuit_editor.clear)
                with dpg.group(horizontal=True):
                    dpg.add_text("  Element")
                    attach_tooltip(tooltips.circuit_editor.element_combo)
                    elements: Dict[str, Type[Element]] = {
                        _.get_description(): _
                        for _ in pyimpspec.get_elements().values()
                    }
                    items: List[str] = list(elements.keys())
                    self.element_combo: int = dpg.generate_uuid()
                    dpg.add_combo(
                        width=-147,
                        items=items,
                        default_value=items[0],
                        tag=self.element_combo,
                    )
                    dpg.add_button(
                        label="Add",
                        width=50,
                        callback=lambda s, a, u: self.add_element_node(
                            u.get(dpg.get_value(self.element_combo))()
                        ),
                        user_data=elements,
                    )
                    attach_tooltip(tooltips.circuit_editor.add_element)
                    dpg.add_button(
                        label="Add dummy",
                        width=80,
                        callback=lambda s, a, u: self.add_dummy_node(),
                    )
                    attach_tooltip(tooltips.circuit_editor.dummy_node)
                self.node_editor: int = dpg.generate_uuid()
                dpg.add_node_editor(
                    width=-1,
                    height=-72,
                    tag=self.node_editor,
                    minimap=True,
                    minimap_location=dpg.mvNodeMiniMap_Location_BottomRight,
                )
                self.node_handler: int = dpg.generate_uuid()
                with dpg.item_handler_registry(tag=self.node_handler):
                    dpg.add_item_clicked_handler(callback=self.node_clicked)
                self.parser: Parser = Parser(self.node_editor, self.node_handler)
                dpg.configure_item(
                    self.node_editor,
                    callback=self.link,
                    delink_callback=self.delink,
                )
                with dpg.group():
                    with dpg.group(horizontal=True):
                        dpg.add_text("   Basic CDC")
                        attach_tooltip(tooltips.circuit_editor.basic_cdc)
                        self.basic_cdc_output_field: int = dpg.generate_uuid()
                        dpg.add_input_text(
                            tag=self.basic_cdc_output_field, width=-150, enabled=False
                        )
                        dpg.add_button(
                            label="Copy to clipboard",
                            width=-1,
                            callback=lambda: dpg.set_clipboard_text(
                                dpg.get_value(self.basic_cdc_output_field)
                            ),
                        )
                    with dpg.group(horizontal=True):
                        dpg.add_text("Extended CDC")
                        attach_tooltip(tooltips.circuit_editor.extended_cdc)
                        self.extended_cdc_output_field: int = dpg.generate_uuid()
                        dpg.add_input_text(
                            tag=self.extended_cdc_output_field,
                            width=-150,
                            enabled=False,
                        )
                        dpg.add_button(
                            label="Copy to clipboard",
                            width=-1,
                            callback=lambda: dpg.set_clipboard_text(
                                dpg.get_value(self.extended_cdc_output_field)
                            ),
                        )
                    with dpg.group(horizontal=True):
                        dpg.add_text("      Status")
                        attach_tooltip(tooltips.circuit_editor.status)
                        self.status_field: int = dpg.generate_uuid()
                        dpg.add_input_text(
                            tag=self.status_field, width=-150, enabled=False
                        )
                        self.accept_button: int = dpg.generate_uuid()
                        dpg.add_button(
                            label="Accept circuit",
                            width=-1,
                            callback=lambda s, a, u: self.callback(u),
                            tag=self.accept_button,
                            show=False,
                        )
                        self.cancel_button: int = dpg.generate_uuid()
                        dpg.add_button(
                            label="Cancel",
                            width=-1,
                            callback=lambda s, a, u: self.callback(None),
                            tag=self.cancel_button,
                        )

    def show(self, circuit: Optional[Circuit]):
        assert type(circuit) is Circuit or circuit is None, circuit
        self.clear_parameter_window(add_info=True)
        self.parser.circuit_to_nodes(circuit)
        self.update(circuit, update_input=True)
        self.update_outputs(circuit=circuit)
        self.update_status("OK" if circuit is not None else "", False)
        self.keybinding_handler.unblock()
        dpg.show_item(self.window)

    def hide(self):
        self.keybinding_handler.block()
        dpg.hide_item(self.window)

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
        dpg.set_item_user_data(self.accept_button, circuit)

    def parse_cdc(self, cdc: str):
        assert type(cdc) is str, cdc
        self.current_node = None
        self.clear_parameter_window(add_info=True)
        circuit: Optional[Circuit]
        msg: str
        try:
            circuit, msg = process_cdc(cdc)
        except Exception as err:
            circuit = None
            msg = str(err)
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

    def clear_parameter_window(self, add_info: bool = False):
        self.parameter_inputs.clear()
        dpg.delete_item(self.parameter_window, children_only=True)
        if add_info:
            dpg.add_text(
                """
Nodes can be connected by left-clicking on the input/output of one node, dragging to the output/input of another node, and releasing. Connections can be deleted by left-clicking a connection while holding down the Ctrl key.

The parameters of the element represented by a node can be altered by left-clicking on the label of the node. The parameters that can be modified will then show up in the sidebar to the left. An element's label can also be modified.

Nodes can be deleted by left-clicking on the label of a node and then left-clicking on the 'Delete' button that shows up in the sidebar to the left. Alternatively, you can select a node and use the keyboard shortcut for deleting a result (e.g., Alt+Delete). Note that the 'WE' and 'CE+RE' nodes, which represent the terminals of the circuit, cannot be deleted.

You can pan the node editor by holding down the middle mouse button and moving the cursor.
            """.strip(),
                wrap=220,
                parent=self.parameter_window,
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

    def node_clicked(self, sender: int, app_data: tuple):
        assert type(sender) is int
        self.clear_parameter_window()
        dpg.clear_selected_nodes(self.node_editor)
        dpg.clear_selected_links(self.node_editor)
        if self.current_node is not None and dpg.does_item_exist(self.current_node.tag):
            self.current_node.set_unselected()
        node: Node = self.parser.find_node(tag=app_data[1])
        self.current_node = node
        node.set_selected()
        tooltip_text: str
        if node.id == self.parser.we_node.id or node.id == self.parser.cere_node.id:
            with dpg.group(parent=self.parameter_window):
                dpg.add_text(
                    (
                        "Working electrode"
                        if node.id == self.parser.we_node.id
                        else "Counter and reference electrodes"
                    )
                    + "\n\nOne of the terminals in the circuit.",
                    wrap=220,
                )
            return
        elif node.id < 0:
            with dpg.group(parent=self.parameter_window):
                dpg.add_text(
                    "Dummy node\n\nCan be used as a junction to connect, e.g., two parallel connections together in series.",
                    wrap=220,
                )
            return
        else:
            dpg.add_button(
                label="Delete",
                width=-1,
                callback=lambda s, a, u: self.delete_node(node),
                parent=self.parameter_window,
            )
            element: Element = node.element
            with dpg.group(parent=self.parameter_window):
                with dpg.group(horizontal=True):
                    lines: List[str] = element.get_extended_description().split("\n")
                    prefix: str = ":math:`Z = "
                    replace_equation: bool = True
                    if replace_equation is True:
                        lines = self.replace_equation(lines, prefix)
                    else:
                        lines = self.move_equation(lines, prefix)
                    tooltip_text = "\n".join(lines).strip()
                    attach_tooltip(tooltip_text, parent=dpg.add_text("?"))
                    label = element.get_description()
                    if len(label) > 30:
                        label = label[:27] + "..."
                    dpg.add_text(label)
                with dpg.group(horizontal=True):
                    dpg.add_text("Label")
                    default_label: str = str(self.parser.element_identifiers[element])
                    hint: str = default_label

                    def update_label(sender: int, new_label: str):
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
                        if new_label == "" and not dpg.get_value(sender) == new_label:
                            dpg.set_value(sender, new_label)
                        element.set_label(new_label)
                        if new_label == "":
                            new_label = str(self.parser.element_identifiers[element])
                        node.set_label(f"{element.get_symbol()}_{new_label}")
                        self.validate_nodes()

                    current_label: str = element.get_label()
                    self.parameter_inputs.append(
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
                dpg.add_text("Parameters")
                key: str
                value: float
                for key, value in element.get_values().items():
                    self.node_parameter(element, key, value)
                if isinstance(element, Container):
                    con: Optional[Connection]
                    for key, con in element.get_subcircuits().items():
                        self.node_subcircuit(element, key, con)

    def delete_node(self, node: Node):
        assert type(node) is Node, node
        if node == self.current_node:
            self.current_node = None
        self.parser.delete_node(node)
        self.validate_nodes()
        self.clear_parameter_window()

    def add_element_node(self, element: Optional[Element]):
        assert element is None or isinstance(element, Element), element
        if element is None:
            return
        self.parser.add_element_node(element)
        self.validate_nodes()

    def add_dummy_node(self):
        self.parser.add_dummy_node()
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
        combo: int = dpg.generate_uuid()
        cdc_input: int = dpg.generate_uuid()
        cdc_tooltip: int = dpg.generate_uuid()
        edit_button: int = dpg.generate_uuid()
        value_group: int = dpg.generate_uuid()

        def choose_option(
            sender: int,
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
            sender: int,
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
            connection: Connection = circuit.get_connections(flattened=False)[0]
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
                subcircuit_editor.keybinding_handler.delete()
                dpg.split_frame(delay=33)
                dpg.delete_item(subcircuit_editor.window)
                dpg.show_item(self.window)
                self.keybinding_handler.unblock()
                signals.emit(
                    Signal.BLOCK_KEYBINDINGS,
                    window=self.window,
                    window_object=self,
                )
                if circuit is None:
                    return
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
            subcircuit_editor.show(circuit)

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

    def node_parameter(
        self,
        element: Element,
        key: str,
        initial_value: float,
    ):
        assert isinstance(element, Element)
        assert type(key) is str
        assert type(initial_value) is float
        fixed: bool = element.is_fixed(key)
        enabled: bool
        lower_limit: float = element.get_lower_limit(key)
        upper_limit: float = element.get_upper_limit(key)
        cv_input_field: int = dpg.generate_uuid()
        cv_checkbox: int = dpg.generate_uuid()
        ll_input_field: int = dpg.generate_uuid()
        ll_checkbox: int = dpg.generate_uuid()
        ul_input_field: int = dpg.generate_uuid()
        ul_checkbox: int = dpg.generate_uuid()
        label_pad: int = 14
        with dpg.collapsing_header(label=f" {key}", leaf=True):
            tooltip: str = ""
            description: str = element.get_value_description(key).strip()
            unit: str = element.get_unit(key).strip()
            if description != "" or unit != "":
                tooltip = (
                    description + (f"\n\nUnit: {unit}" if unit != "" else "")
                ).strip()
            with dpg.group(horizontal=True):
                dpg.add_text("Initial value".rjust(label_pad))
                if tooltip != "":
                    attach_tooltip(tooltip)
                dpg.add_input_float(
                    default_value=initial_value,
                    step=0,
                    format="%.4g",
                    width=-48,
                    tag=cv_input_field,
                    on_enter=True,
                )
                dpg.add_checkbox(
                    label="F",
                    default_value=fixed,
                    tag=cv_checkbox,
                )
                attach_tooltip("Fixed")
            with dpg.group(horizontal=True):
                dpg.add_text("Lower limit".rjust(label_pad))
                if tooltip != "":
                    attach_tooltip(tooltip)
                enabled = not isinf(lower_limit)
                dpg.add_input_float(
                    default_value=lower_limit,
                    step=0,
                    format="%.4g",
                    width=-48,
                    tag=ll_input_field,
                    on_enter=True,
                    readonly=not enabled,
                    enabled=enabled,
                )
                dpg.add_checkbox(
                    label="E",
                    default_value=enabled,
                    tag=ll_checkbox,
                )
                attach_tooltip("Enabled")
            with dpg.group(horizontal=True):
                dpg.add_text("Upper limit".rjust(label_pad))
                if tooltip != "":
                    attach_tooltip(tooltip)
                enabled = not isinf(upper_limit)
                dpg.add_input_float(
                    default_value=upper_limit,
                    step=0,
                    format="%.4g",
                    width=-48,
                    tag=ul_input_field,
                    on_enter=True,
                    readonly=not enabled,
                    enabled=enabled,
                )
                dpg.add_checkbox(
                    label="E",
                    default_value=enabled,
                    tag=ul_checkbox,
                )
                attach_tooltip("Enabled")

            def reset_parameter():
                element.reset_parameter(key)
                dpg.set_value(cv_input_field, element.get_value(key))
                dpg.set_value(cv_checkbox, element.is_fixed(key))
                value = element.get_lower_limit(key)
                dpg.configure_item(
                    ll_input_field,
                    default_value=value,
                    readonly=isinf(value) is True,
                    enabled=not isinf(value),
                )
                dpg.set_value(ll_checkbox, not isinf(value))
                value = element.get_upper_limit(key)
                dpg.configure_item(
                    ul_input_field,
                    default_value=value,
                    readonly=isinf(value) is True,
                    enabled=not isinf(value),
                )
                dpg.set_value(ul_checkbox, not isinf(value))

            dpg.add_button(label="Reset", callback=reset_parameter)
        dpg.add_spacer(height=8)
        self.parameter_inputs.extend(
            [
                cv_input_field,
                ll_input_field,
                ul_input_field,
            ]
        )

        def set_lower_limit(sender: int, new_value: float):
            assert type(sender) is int
            if not dpg.get_value(ll_checkbox):
                new_value = -inf
            current_value: float = dpg.get_value(cv_input_field)
            if new_value > current_value:
                new_value = current_value
                dpg.configure_item(ll_input_field, default_value=new_value)
            element.set_lower_limits(key, new_value)
            self.validate_nodes()

        def toggle_lower_limit(sender: int, state: bool):
            assert type(sender) is int
            assert type(state) is bool
            new_value: float
            if state:
                new_value = element.get_default_lower_limit(key)
                current_value: float = dpg.get_value(cv_input_field)
                if isinf(new_value) or new_value > current_value:
                    new_value = 0.9 * current_value
            else:
                new_value = -inf
            dpg.configure_item(
                ll_input_field,
                default_value=new_value,
                readonly=not state,
                enabled=state,
            )
            element.set_lower_limits(key, new_value)
            self.validate_nodes()

        def set_upper_limit(sender: int, new_value: float):
            assert type(sender) is int
            if not dpg.get_value(ul_checkbox):
                new_value = inf
            current_value: float = dpg.get_value(cv_input_field)
            if new_value < current_value:
                new_value = current_value
                dpg.configure_item(ul_input_field, default_value=new_value)
            element.set_upper_limits(key, new_value)
            self.validate_nodes()

        def toggle_upper_limit(sender: int, state: bool):
            assert type(sender) is int
            assert type(state) is bool
            new_value: float
            if state:
                new_value = element.get_default_upper_limit(key)
                current_value: float = dpg.get_value(cv_input_field)
                if isinf(new_value) or new_value < current_value:
                    new_value = 1.1 * current_value
            else:
                new_value = inf
            dpg.configure_item(
                ul_input_field,
                default_value=new_value,
                readonly=not state,
                enabled=state,
            )
            element.set_upper_limits(key, new_value)
            self.validate_nodes()

        def set_value(sender: int, new_value: float):
            assert type(sender) is int
            if dpg.get_value(ll_checkbox):
                lower_limit = dpg.get_value(ll_input_field)
                if lower_limit > new_value:
                    dpg.configure_item(ll_input_field, default_value=new_value)
                    element.set_lower_limits(key, new_value)
            if dpg.get_value(ul_checkbox):
                upper_limit = dpg.get_value(ul_input_field)
                if upper_limit < new_value:
                    dpg.configure_item(ul_input_field, default_value=new_value)
                    element.set_upper_limits(key, new_value)
            element.set_values(**{key: new_value})
            self.validate_nodes()

        def toggle_fixed(sender: int, state: bool):
            assert type(sender) is int
            assert type(state) is bool
            element.set_fixed(key, state)
            if dpg.get_value(ll_checkbox):
                dpg.set_value(ll_checkbox, False)
                toggle_lower_limit(ll_checkbox, False)
            if dpg.get_value(ul_checkbox):
                dpg.set_value(ul_checkbox, False)
                toggle_upper_limit(ul_checkbox, False)
            self.validate_nodes()

        dpg.set_item_callback(cv_input_field, set_value)
        dpg.set_item_callback(cv_checkbox, toggle_fixed)
        dpg.set_item_callback(ll_input_field, set_lower_limit)
        dpg.set_item_callback(ll_checkbox, toggle_lower_limit)
        dpg.set_item_callback(ul_input_field, set_upper_limit)
        dpg.set_item_callback(ul_checkbox, toggle_upper_limit)

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

    def link(self, sender: int, attributes: Tuple[int, int]):
        self.parser.link(sender, attributes)
        self.validate_nodes()

    def delink(self, sender: int, link: int):
        self.parser.delink(sender, link)
        self.validate_nodes()

    def cycle_elements(self, step: int):
        items: List[str] = dpg.get_item_configuration(self.element_combo)["items"]
        index: int = items.index(dpg.get_value(self.element_combo)) + step
        dpg.set_value(self.element_combo, items[index % len(items)])

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
            or any(map(lambda _: dpg.is_item_active(_), self.parameter_inputs))
        )
