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

from typing import Callable, Dict, List, Optional, Tuple, Type
from numpy import inf
from pyimpspec import Circuit, Element, ParsingError
import pyimpspec
import dearpygui.dearpygui as dpg
from deareis.gui.circuit_editor.parser import Parser, Node
import deareis.themes as themes
from deareis.tooltips import attach_tooltip, update_tooltip
import deareis.tooltips as tooltips
from deareis.keybindings import is_alt_down, is_control_down


class CircuitEditor:
    def __init__(self, window: int, callback: Callable):
        assert type(window) is int and dpg.does_item_exist(window), window
        self.parameter_inputs: List[int] = []
        self.callback: Callable = callback
        self.window: int = window
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
                    dpg.add_button(
                        label="Clear",
                        width=80,
                        callback=lambda s, a, u: self.parse_cdc(""),
                    )
                with dpg.group(horizontal=True):
                    dpg.add_text("  Element")
                    attach_tooltip(tooltips.circuit_editor.element_combo)
                    elements: Dict[str, Type[Element]] = {
                        _.get_description(): _
                        for _ in pyimpspec.get_elements().values()
                    }
                    items: List[str] = list(elements.keys())
                    element_combo: int = dpg.add_combo(
                        width=-147, items=items, default_value=items[0]
                    )
                    dpg.add_button(
                        label="Add",
                        width=50,
                        callback=lambda s, a, u: self.add_element_node(
                            u.get(dpg.get_value(element_combo))()
                        ),
                        user_data=elements,
                    )
                    dpg.add_button(
                        label="Add dummy",
                        width=80,
                        callback=lambda s, a, u: self.add_dummy_node(),
                    )
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
        self.setup_keybindings()
        dpg.show_item(self.window)

    def hide(self):
        if hasattr(self, "key_handler") and dpg.does_item_exist(self.key_handler):
            dpg.delete_item(self.key_handler)
        dpg.hide_item(self.window)

    def setup_keybindings(self):
        def delete_callback():
            if not dpg.does_item_exist(self.window):
                return
            elif not dpg.is_item_shown(self.window):
                return
            elif not dpg.is_item_hovered(self.node_editor):
                return
            elif (
                dpg.is_item_active(self.cdc_input)
                or dpg.is_item_active(self.basic_cdc_output_field)
                or dpg.is_item_active(self.extended_cdc_output_field)
                or dpg.is_item_active(self.status_field)
                or any(map(lambda _: dpg.is_item_active(_), self.parameter_inputs))
            ):
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

        def accept_callback():
            if not (is_alt_down() or is_control_down()):
                return
            self.callback(dpg.get_item_user_data(self.accept_button))

        self.key_handler: int = dpg.generate_uuid()
        with dpg.handler_registry(tag=self.key_handler):
            dpg.add_key_release_handler(key=dpg.mvKey_Delete, callback=delete_callback)
            dpg.add_key_release_handler(
                key=dpg.mvKey_Escape, callback=lambda: self.callback(None)
            )
            dpg.add_key_release_handler(
                key=dpg.mvKey_Return,
                callback=accept_callback,
            )

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
        if cdc == "":
            self.clear_parameter_window()
        circuit: Optional[Circuit] = None
        try:
            circuit = pyimpspec.parse_cdc(cdc)
            dpg.bind_item_theme(self.cdc_input, themes.cdc.valid)
            self.update_outputs(circuit=circuit)
            self.update_status("OK", False)
        except ParsingError as err:
            dpg.bind_item_theme(self.cdc_input, themes.cdc.invalid)
            self.update_outputs(stack=[])
            self.update_status(str(err), True)
        if circuit is not None:
            self.parser.circuit_to_nodes(circuit)
        else:
            self.parser.clear_nodes()
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

Nodes can be deleted by left-clicking on the label of a node and then left-clicking on the 'Delete' button that shows up in the sidebar to the left. Alternatively, you can select a node and press the Delete key. Note that the 'WE' and 'CE+RE' nodes, which represent the terminals of the circuit, cannot be deleted.

You can pan the node editor by holding down the middle mouse button and moving the cursor.
            """.strip(),
                wrap=235,
                parent=self.parameter_window,
            )

    def node_clicked(self, sender: int, app_data):
        assert type(sender) is int
        self.clear_parameter_window()
        node: Node = self.parser.find_node(tag=app_data[1])
        tooltip_text: str
        if node.id == self.parser.we_node.id or node.id == self.parser.cere_node.id:
            with dpg.group(parent=self.parameter_window):
                dpg.add_text("Electrode(s)")
                with dpg.group(horizontal=True):
                    attach_tooltip(
                        """
The working electrode.
                        """.strip()
                        if node.id == self.parser.we_node.id
                        else """
The counter and reference electrodes.
                        """.strip(),
                        parent=dpg.add_text("?"),
                    )
                    dpg.add_text(
                        "WE" if node.id == self.parser.we_node.id else "CE+RE"
                    )
            return
        elif node.id < 0:
            with dpg.group(parent=self.parameter_window):
                with dpg.group(horizontal=True):
                    attach_tooltip(
                        """
A dummy node that can be used as a junction when required to construct a circuit.
                    """.strip(),
                        parent=dpg.add_text("?"),
                    )
                    dpg.add_text("Dummy node")
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
                    tooltip_text = element.get_extended_description()
                    attach_tooltip(tooltip_text, parent=dpg.add_text("?"))
                    label = element.get_description()
                    if len(label) > 30:
                        label = label[:27] + "..."
                    dpg.add_text(label)
                with dpg.group(horizontal=True):
                    dpg.add_text("Label")
                    default_label: str = element.get_default_label()
                    hint: str = default_label[default_label.find("_") + 1 :]

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
                        node.set_label(element.get_label())
                        self.validate_nodes()

                    current_label: str = element.get_label()
                    current_label = current_label[current_label.find("_") + 1 :]
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
                for key, value in element.get_parameters().items():
                    self.node_parameter(element, key, value, 34)

    def delete_node(self, node: Node):
        assert type(node) is Node, node
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

    def node_parameter(
        self, element: Element, key: str, initial_value: float, max_padding: int
    ):
        assert isinstance(element, Element)
        assert type(key) is str
        assert type(initial_value) is float
        assert type(max_padding) is int
        fixed: bool = element.is_fixed(key)
        enabled: bool
        lower_limit: float = element.get_lower_limit(key)
        upper_limit: float = element.get_upper_limit(key)
        current_value: float
        cv_input_field: int = dpg.generate_uuid()
        cv_checkbox: int = dpg.generate_uuid()
        ll_input_field: int = dpg.generate_uuid()
        ll_checkbox: int = dpg.generate_uuid()
        ul_input_field: int = dpg.generate_uuid()
        ul_checkbox: int = dpg.generate_uuid()
        label_pad: int = 14
        with dpg.collapsing_header(label=f" {key}", leaf=True):
            with dpg.group(horizontal=True):
                dpg.add_text("Initial value".rjust(label_pad))
                dpg.add_input_float(
                    default_value=initial_value,
                    step=0,
                    format="%.4g",
                    width=-48,
                    tag=cv_input_field,
                    on_enter=True,
                )
                dpg.add_checkbox(
                    default_value=fixed,
                    tag=cv_checkbox,
                )
                dpg.add_text("F")
                attach_tooltip("Fixed")
            with dpg.group(horizontal=True):
                dpg.add_text("Lower limit".rjust(label_pad))
                enabled = lower_limit != -inf
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
                    default_value=enabled,
                    tag=ll_checkbox,
                )
                dpg.add_text("E")
                attach_tooltip("Enabled")
            with dpg.group(horizontal=True):
                dpg.add_text("Upper limit".rjust(label_pad))
                enabled = upper_limit != inf
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
                    default_value=enabled,
                    tag=ul_checkbox,
                )
                dpg.add_text("E")
                attach_tooltip("Enabled")

            def reset_parameter():
                element.reset_parameters([key])
                dpg.set_value(cv_input_field, element.get_parameters()[key])
                dpg.set_value(cv_checkbox, element.is_fixed(key))
                value = element.get_lower_limit(key)
                dpg.configure_item(
                    ll_input_field,
                    default_value=value,
                    readonly=value == -inf,
                    enabled=value != -inf,
                )
                dpg.set_value(ll_checkbox, value != -inf)
                value = element.get_upper_limit(key)
                dpg.configure_item(
                    ul_input_field,
                    default_value=value,
                    readonly=value == inf,
                    enabled=value != inf,
                )
                dpg.set_value(ul_checkbox, value != inf)

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
            current_value = dpg.get_value(cv_input_field)
            if new_value > current_value:
                new_value = current_value
                dpg.configure_item(ll_input_field, default_value=new_value)
            element.set_lower_limit(key, new_value)
            self.validate_nodes()

        def toggle_lower_limit(sender: int, state: bool):
            assert type(sender) is int
            assert type(state) is bool
            new_value: Optional[float]
            if state:
                new_value = element.get_default_lower_limits().get(key)
                current_value: float = dpg.get_value(cv_input_field)
                if new_value is None or new_value == -inf or new_value > current_value:
                    new_value = 0.9 * current_value
            else:
                new_value = -inf
            dpg.configure_item(
                ll_input_field,
                default_value=new_value,
                readonly=not state,
                enabled=state,
            )
            element.set_lower_limit(key, new_value)
            self.validate_nodes()

        def set_upper_limit(sender: int, new_value: float):
            assert type(sender) is int
            if not dpg.get_value(ul_checkbox):
                new_value = inf
            current_value = dpg.get_value(cv_input_field)
            if new_value < current_value:
                new_value = current_value
                dpg.configure_item(ul_input_field, default_value=new_value)
            element.set_upper_limit(key, new_value)
            self.validate_nodes()

        def toggle_upper_limit(sender: int, state: bool):
            assert type(sender) is int
            assert type(state) is bool
            new_value: Optional[float]
            if state:
                new_value = element.get_default_upper_limits().get(key)
                current_value: float = dpg.get_value(cv_input_field)
                if new_value is None or new_value == inf or new_value < current_value:
                    new_value = 1.1 * current_value
            else:
                new_value = inf
            dpg.configure_item(
                ul_input_field,
                default_value=new_value,
                readonly=not state,
                enabled=state,
            )
            element.set_upper_limit(key, new_value)
            self.validate_nodes()

        def set_value(sender: int, new_value: float):
            assert type(sender) is int
            if dpg.get_value(ll_checkbox):
                lower_limit = dpg.get_value(ll_input_field)
                if lower_limit > new_value:
                    dpg.configure_item(ll_input_field, default_value=new_value)
                    element.set_lower_limit(key, new_value)
            if dpg.get_value(ul_checkbox):
                upper_limit = dpg.get_value(ul_input_field)
                if upper_limit < new_value:
                    dpg.configure_item(ul_input_field, default_value=new_value)
                    element.set_upper_limit(key, new_value)
            element.set_parameters({key: new_value})
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
