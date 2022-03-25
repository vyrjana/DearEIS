# Copyright 2022 DearEIS developers
# DearEIS is licensed under the GPLv3 or later (https://www.gnu.org/licenses/gpl-3.0.html).
# The licenses of DearEIS' dependencies and/or sources of portions of code are included in
# the LICENSES folder.

import dearpygui.dearpygui as dpg
from typing import Callable, Dict, List, Optional, Set, Tuple, Union
from pyimpspec import (
    string_to_circuit,
    get_elements,
    Circuit,
    Series,
    Parallel,
    Element,
    Connection,
    ParsingError,
)
from deareis.utility import attach_tooltip, is_alt_down
import deareis.themes as themes
import deareis.tooltips as tooltips
from numpy import inf


# TODO:
# - Add tooltip to nodes (not possible at the moment) so that long labels can be supported
# TODO FIXME: Bugs
# - Nodes may sometimes spawn with inactive attributes and thus cannot be linked to anything.


class Node:
    def __init__(
        self,
        parent: int,
        node_id: int,
        label: str,
        pos: Tuple[int, int],
        element: Optional[Element] = None,
        input_attribute: bool = True,
        output_attribute: bool = True,
    ):
        assert type(parent) is int
        assert type(node_id) is int
        assert type(label) is str
        assert (
            type(pos) is tuple
            and len(pos) == 2
            and all(map(lambda _: type(_) is int, pos))
        )
        assert isinstance(element, Element) or element is None
        assert type(input_attribute) is bool
        assert type(output_attribute) is bool
        self.tag: int = dpg.generate_uuid()
        self.id: int = node_id
        self.label: str = ""
        self.element: Optional[Element] = element
        self.input_attribute: int = dpg.generate_uuid() if input_attribute else -1
        self.output_attribute: int = dpg.generate_uuid() if output_attribute else -1
        self.input_links: Dict[int, int] = {}
        self.output_links: Dict[int, int] = {}
        with dpg.node(label=label, pos=pos, tag=self.tag, parent=parent):
            if input_attribute:
                dpg.add_node_attribute(
                    attribute_type=dpg.mvNode_Attr_Input, tag=self.input_attribute
                )
            if output_attribute:
                dpg.add_node_attribute(
                    attribute_type=dpg.mvNode_Attr_Output, tag=self.output_attribute
                )
        self.set_label(label)

    def __repr__(self) -> str:
        return self.label.strip()

    def set_label(self, label: str):
        assert type(label) is str
        width: int = 5
        label = label.ljust(width, " ")
        self.label = label
        dpg.configure_item(self.tag, label=label[:width])

    def has_attribute(self, attribute: int) -> bool:
        assert type(attribute) is int
        if self.input_attribute >= 0 and self.input_attribute == attribute:
            return True
        elif self.output_attribute >= 0 and self.output_attribute == attribute:
            return True
        return False

    def get_num_input_links(self) -> int:
        return len(self.input_links)

    def get_num_output_links(self) -> int:
        return len(self.output_links)

    def has_link_to(self, link: int) -> bool:
        assert type(link) is int
        return link in self.output_links.values()

    def has_link_from(self, link: int) -> bool:
        assert type(link) is int
        return link in self.input_links.values()

    def add_link_to(self, node: "Node", link: int):
        assert type(link) is int
        self.output_links[node.id] = link

    def delete_link_to(self, node: "Node") -> int:
        link: int = self.output_links[node.id]
        del self.output_links[node.id]
        return link

    def add_link_from(self, node: "Node", link: int):
        assert type(link) is int
        self.input_links[node.id] = link

    def delete_link_from(self, node: "Node") -> int:
        link: int = self.input_links[node.id]
        del self.input_links[node.id]
        return link

    def set_valid(self):
        dpg.bind_item_theme(self.tag, themes.valid_node)

    def set_invalid(self, msg: str) -> str:
        dpg.bind_item_theme(self.tag, themes.invalid_node)
        return msg


class CircuitPreview:
    def __init__(self, node_editor: int):
        assert type(node_editor) is int
        self.node_editor: int = node_editor

    def clear(self):
        dpg.delete_item(self.node_editor, children_only=True)

    def update(self, definitions: dict):
        assert type(definitions) is dict
        self.clear()
        x_offset: int = 10
        y_offset: int = 10
        x_step: int = 90
        y_step: int = 70
        input_attributes: Dict[int, int] = {}
        output_attributes: Dict[int, int] = {}
        # Create nodes
        node: dict
        for node in definitions["nodes"]:
            width: int = 5
            label: str = node["label"].ljust(width, " ")[:width]
            pos: Tuple[int, int] = (
                x_offset + x_step * node["x"],
                y_offset + y_step * node["y"],
            )
            with dpg.node(label=label, pos=pos, parent=self.node_editor):
                tag: int
                if len(node["inputs"]) > 0:
                    tag = dpg.add_node_attribute(attribute_type=dpg.mvNode_Attr_Input)
                    input_attributes[node["id"]] = tag
                if len(node["outputs"]) > 0:
                    tag = dpg.add_node_attribute(attribute_type=dpg.mvNode_Attr_Output)
                    output_attributes[node["id"]] = tag
        # Connect nodes
        for node in definitions["nodes"]:
            this: int = node["id"]
            other: int
            src: int
            dst: int
            # Input links
            if this in input_attributes:
                dst = input_attributes[this]
                for other in node["inputs"]:
                    src = output_attributes[other]
                    dpg.add_node_link(src, dst, parent=self.node_editor)
            # Output links
            if this in output_attributes:
                src = output_attributes[this]
                for other in node["outputs"]:
                    dst = input_attributes[other]
                    dpg.add_node_link(src, dst, parent=self.node_editor)


class CircuitEditor:
    def __init__(self, window: int, accept_callback: Optional[Callable] = None):
        assert type(window) is int
        self.window: int = window
        self.accept_callback: Optional[Callable] = accept_callback
        self.latest_circuit: Optional[Circuit] = None
        self.accept_button: int = dpg.generate_uuid()
        self.node_editor: int = dpg.generate_uuid()
        self.node_handler: int = dpg.generate_uuid()
        self.key_handler: int = -1
        self.parameter_window: int = dpg.generate_uuid()
        self.cdc_input_field: int = dpg.generate_uuid()
        self.simple_cdc_output_field: int = dpg.generate_uuid()
        self.detailed_cdc_output_field: int = dpg.generate_uuid()
        self.status_field: int = dpg.generate_uuid()
        self.wes_node: Node = None  # type: ignore
        self.cere_node: Node = None  # type: ignore
        self.nodes: List[Node] = []
        self.element_counter: int = -1
        self.dummy_counter: int = -1
        self.x_offset: int = 20
        self.y_offset: int = 20
        self.x_step: int = 100
        self.y_step: int = 100
        self.elements: Dict[str, Element] = {
            _.get_description(): _ for _ in get_elements().values()
        }
        self._assemble()
        self._initialize_key_bindings()

    def nodes_to_dict(self, cdc: str = "") -> dict:
        assert type(cdc) is str
        circuit: Optional[Circuit] = self.validate_nodes()
        tmp_cdc: str = circuit.to_string(12) if circuit is not None else ""
        do_reset: bool = cdc != ""
        if cdc != "":
            circuit = self.parse_cdc(cdc)
        assert circuit is not None
        result: dict = {"nodes": []}

        def process_node(node: Node):
            assert type(node) is Node
            x: int
            y: int
            x, y = dpg.get_item_pos(node.tag)
            result["nodes"].append(
                {
                    "id": node.id,
                    "x": (x - self.x_offset) / self.x_step,
                    "y": (y - self.y_offset) / self.y_step,
                    "label": node.label.strip(),
                    "inputs": list(node.input_links.keys()),
                    "outputs": list(node.output_links.keys()),
                }
            )

        process_node(self.wes_node)
        for node in self.nodes:
            process_node(node)
        process_node(self.cere_node)

        if do_reset:
            self.parse_cdc(tmp_cdc)
        return result

    def _assemble(self):
        with dpg.group(horizontal=True, parent=self.window):
            with dpg.child_window(width=250, tag=self.parameter_window):
                pass
            with dpg.group():
                with dpg.group(horizontal=True):
                    dpg.add_text("CDC input")
                    attach_tooltip(tooltips.circuit_editor_cdc_input)

                    def cdc_callback(sender: int, cdc: Optional[str]):
                        assert type(sender) is int
                        assert type(cdc) is str or cdc is None
                        if cdc is None:  # Necessary when the "Parse" button is clicked
                            cdc = dpg.get_value(self.cdc_input_field)
                        if self.parse_cdc(cdc, update_input_field=True) is not None:
                            dpg.bind_item_theme(self.cdc_input_field, themes.valid_cdc)
                        else:
                            dpg.bind_item_theme(
                                self.cdc_input_field, themes.invalid_cdc
                            )

                    dpg.add_input_text(
                        width=-147,
                        tag=self.cdc_input_field,
                        callback=cdc_callback,
                        on_enter=True,
                    )
                    dpg.add_button(label="Parse", width=50, callback=cdc_callback)

                    def clear_callback():
                        self.parse_cdc("", update_input_field=True)

                    dpg.add_button(label="Clear", width=80, callback=clear_callback)
                with dpg.group(horizontal=True):
                    dpg.add_text("  Element")
                    attach_tooltip(tooltips.circuit_editor_element_combo)
                    items: List[str] = list(self.elements.keys())
                    element_combo: int = dpg.add_combo(
                        width=-147, items=items, default_value=items[0]
                    )

                    def element_callback():
                        element: Optional[Element]
                        element = self.elements.get(dpg.get_value(element_combo))
                        if element is None:
                            return
                        self.add_element_node(element())
                        self.validate_nodes()

                    dpg.add_button(label="Add", width=50, callback=element_callback)

                    def dummy_callback():
                        self.add_dummy_node()
                        self.validate_nodes()

                    dpg.add_button(label="Add dummy", width=80, callback=dummy_callback)
                with dpg.node_editor(
                    width=-1,
                    height=-72,
                    tag=self.node_editor,
                    callback=self.link,
                    delink_callback=self.delink,
                    user_data=True,
                ):
                    pass
                with dpg.group():
                    with dpg.group(horizontal=True):
                        dpg.add_text("  Simple CDC")
                        attach_tooltip(tooltips.circuit_editor_simple_cdc)
                        dpg.add_input_text(
                            tag=self.simple_cdc_output_field, width=-150, enabled=False
                        )
                        dpg.add_button(
                            label="Copy to clipboard",
                            width=-1,
                            callback=lambda: dpg.set_clipboard_text(
                                dpg.get_value(self.simple_cdc_output_field)
                            ),
                        )
                    with dpg.group(horizontal=True):
                        dpg.add_text("Detailed CDC")
                        attach_tooltip(tooltips.circuit_editor_detailed_cdc)
                        dpg.add_input_text(
                            tag=self.detailed_cdc_output_field,
                            width=-150,
                            enabled=False,
                        )
                        dpg.add_button(
                            label="Copy to clipboard",
                            width=-1,
                            callback=lambda: dpg.set_clipboard_text(
                                dpg.get_value(self.detailed_cdc_output_field)
                            ),
                        )
                    with dpg.group(horizontal=True):
                        dpg.add_text("      Status")
                        attach_tooltip(tooltips.circuit_editor_status)
                        dpg.add_input_text(
                            tag=self.status_field, width=-150, enabled=False
                        )

                        dpg.add_button(
                            label="Close",
                            width=-1,
                            callback=self.accept_circuit,
                            tag=self.accept_button,
                        )
        with dpg.item_handler_registry(tag=self.node_handler):
            dpg.add_item_clicked_handler(callback=self.node_clicked)
        self.parse_cdc("")

    def _initialize_key_bindings(self):
        def delete_callback():
            if not dpg.does_item_exist(self.window):
                return
            elif not dpg.is_item_shown(self.window):
                return
            elif not dpg.is_item_hovered(self.node_editor):
                return
            tag: int
            link_tags: List[int] = dpg.get_selected_links(self.node_editor)
            if link_tags:
                for tag in link_tags:
                    self.delink(-1, tag)
            node_tags: List[int] = dpg.get_selected_nodes(self.node_editor)
            if node_tags:
                for tag in node_tags:
                    node: Node = self.find_node(tag=tag)
                    if node == self.wes_node or node == self.cere_node:
                        continue
                    self.delete_node(node)

        self.key_handler = dpg.generate_uuid()
        with dpg.handler_registry(tag=self.key_handler):
            dpg.add_key_release_handler(key=dpg.mvKey_Delete, callback=delete_callback)
            dpg.add_key_release_handler(key=dpg.mvKey_Escape, callback=self.hide_window)
            dpg.add_key_release_handler(
                key=dpg.mvKey_Return, callback=self.accept_circuit_keybinding
            )

    def is_visible(self) -> bool:
        return dpg.is_item_visible(self.cdc_input_field)

    def hide_window(self):
        if self.latest_circuit is None and self.nodes:
            self.clear_nodes()
        dpg.hide_item(self.window)
        dpg.delete_item(self.key_handler)

    def accept_circuit(self):
        if self.accept_callback is None:
            return
        self.accept_callback(self.latest_circuit)
        self.hide_window()

    def accept_circuit_keybinding(self):
        if not is_alt_down():
            return
        self.accept_circuit()

    def show_window(self, x: int = -1, y: int = -1, width: int = -1, height: int = -1):
        assert type(x) is int
        assert type(y) is int
        assert type(width) is int
        assert type(height) is int
        if x >= 0 and y >= 0:
            dpg.configure_item(
                self.window,
                pos=(
                    x,
                    y,
                ),
            )
        if width > 0 and height > 0:
            dpg.configure_item(self.window, width=width, height=height)
        if self.latest_circuit is not None:
            # Reorganize the nodes
            self.parse_cdc(self.latest_circuit.to_string(12))
        self._initialize_key_bindings()
        dpg.show_item(self.window)

    def clear_parameter_window(self, add_info: bool = False):
        assert type(add_info) is bool
        dpg.delete_item(self.parameter_window, children_only=True)
        if add_info:
            dpg.add_text(
                """
Nodes can be connected by left-clicking on the input/output of one node, dragging to the output/input of another node, and releasing. Connections can be deleted by left-clicking a connection while holding down the Ctrl key.

The parameters of the element represented by a node can be altered by left-clicking on the label of the node. The parameters that can be modified will then show up in the sidebar to the left. An element's label can also be modified.

Nodes can be deleted by left-clicking on the label of a node and then left-clicking on the 'Delete' button that shows up in the sidebar to the left. Alternatively, you can select a node and press the Delete key. Note that the 'WE+WS' and 'CE+RE' nodes, which represent the terminals of the circuit, cannot be deleted.

You can pan the node editor by holding down the middle mouse button and moving the cursor.
            """.strip(),
                wrap=235,
                parent=self.parameter_window,
            )

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
                    format="%.4E",
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
                    format="%.4E",
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
                    format="%.4E",
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

    def node_clicked(self, sender, app_data):
        assert type(sender) is int
        self.clear_parameter_window()
        parent: int = self.parameter_window
        node: Node = self.find_node(tag=app_data[1])
        tooltip_text: str
        if node.id == self.wes_node.id:
            with dpg.group(parent=parent):
                dpg.add_text("Electrodes")
                with dpg.group(horizontal=True):
                    attach_tooltip(
                        """
The working and sense electrodes.
                    """.strip(),
                        parent=dpg.add_text("?"),
                    )
                    dpg.add_text("WE+WS")
            return
        elif node.id == self.cere_node.id:
            with dpg.group(parent=parent):
                dpg.add_text("Electrodes")
                with dpg.group(horizontal=True):
                    attach_tooltip(
                        """
The counter and reference electrodes.
                    """.strip(),
                        parent=dpg.add_text("?"),
                    )
                    dpg.add_text("CE+RE")
            return
        dpg.add_button(
            label="Delete",
            width=-1,
            callback=lambda: self.delete_node(node),
            parent=parent,
        )
        if node.id < 0:
            with dpg.group(parent=parent):
                with dpg.group(horizontal=True):
                    attach_tooltip(
                        """
A dummy node that can be used as a junction when required to construct a circuit.
                    """.strip(),
                        parent=dpg.add_text("?"),
                    )
                    dpg.add_text("Dummy node")
            return
        element: Element = node.element
        with dpg.group(parent=parent):
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
                dpg.add_input_text(
                    hint=hint,
                    default_value=current_label if current_label != hint else "",
                    width=-1,
                    callback=update_label,
                    on_enter=True,
                )
            dpg.add_spacer(height=8)
            dpg.add_text("Parameters")
            key: str
            value: float
            for key, value in element.get_parameters().items():
                self.node_parameter(element, key, value, 34)

    def find_node(
        self,
        tag: int = -1,
        node_id: int = -1,
        attribute: int = -1,
        link_to: int = -1,
        link_from: int = -1,
    ) -> Node:
        assert type(tag) is int, tag
        assert type(node_id) is int, node_id
        assert type(attribute) is int, attribute
        assert type(link_to) is int, link_to
        assert type(link_from) is int, link_from
        func: Callable
        if tag >= 0:
            func = lambda _: _.tag == tag
        elif node_id != -1:
            func = lambda _: _.id == node_id
        elif attribute >= 0:
            func = lambda _: _.has_attribute(attribute)
        elif link_to >= 0:
            func = lambda _: _.has_link_to(link_to)
        elif link_from >= 0:
            func = lambda _: _.has_link_from(link_from)
        else:
            raise Exception("Nothing has been provided to use to find a node!")
        node: Node
        for node in self.nodes:
            if func(node):
                return node
        if func(self.wes_node):
            return self.wes_node
        elif func(self.cere_node):
            return self.cere_node
        raise Exception("Node does not exist!")

    def link(self, sender: int, attributes: Tuple[int, int], validate: bool = True):
        assert type(sender) is int
        assert (
            type(attributes) is tuple
            and len(attributes) == 2
            and all(map(lambda _: type(_) is int, attributes))
        )
        assert type(validate) is bool
        link: int = dpg.add_node_link(*attributes, parent=sender)
        src: Node = self.find_node(attribute=attributes[0])
        dst: Node = self.find_node(attribute=attributes[1])
        # print(f"Link: {src.label=}, {dst.label=}, {link=}, {validate=}")
        src.add_link_to(dst, link)
        dst.add_link_from(src, link)
        if validate:
            self.validate_nodes()

    def delink(self, sender: int, link: int):
        assert type(sender) is int
        assert type(link) is int
        src: Node = self.find_node(link_to=link)
        dst: Node = self.find_node(link_from=link)
        # print(f"Delink: {src.label=}, {dst.label=}, {link=}")
        src.delete_link_to(dst)
        dst.delete_link_from(src)
        dpg.delete_item(link)
        self.validate_nodes()

    def link_nodes(self, src: Node, dst: Node):
        assert type(src) is Node
        assert type(dst) is Node
        src_attr = dpg.get_item_children(src.tag, slot=1)[
            1 if src != self.wes_node else 0
        ]
        dst_attr = dpg.get_item_children(dst.tag, slot=1)[0]
        self.link(self.node_editor, (src_attr, dst_attr), False)

    def add_node(self, **kwargs) -> Node:
        element: Optional[Element] = kwargs.get("element", None)
        pos: Tuple[int, int] = kwargs.get(
            "pos",
            (
                0,
                1,
            ),
        )
        pos = (
            self.x_offset + self.x_step * pos[0],
            self.y_offset + self.y_step * pos[1],
        )
        self.nodes.append(
            Node(
                parent=self.node_editor,
                node_id=kwargs.get("node_id", len(self.nodes)),
                label=kwargs.get("label", "?"),
                pos=pos,
                element=element,
            )
        )
        dpg.bind_item_handler_registry(self.nodes[-1].tag, self.node_handler)
        return self.nodes[-1]

    def add_element_node(self, element: Element, **kwargs) -> Node:
        assert isinstance(element, Element)
        kwargs["element"] = element
        if "label" not in kwargs:
            kwargs["label"] = element.get_label()
        node_id: int = kwargs.get("node_id", -1)
        if node_id < 0:
            node_id = self.next_element()
            kwargs["node_id"] = node_id
        element._assign_identifier(node_id)
        node: Node = self.add_node(**kwargs)
        node.set_label(element.get_label())
        return node

    def add_dummy_node(self, **kwargs) -> Node:
        kwargs["label"] = "Dummy"
        node_id: int = kwargs.get("node_id", -1)
        if node_id >= -1:
            kwargs["node_id"] = self.next_dummy()
        return self.add_node(**kwargs)

    def delete_node(self, node: Node):
        assert type(node) is Node
        other: Node
        other_id: int
        link: int
        for other_id, link in node.output_links.copy().items():
            other = self.find_node(node_id=other_id)
            node.delete_link_to(other)
            other.delete_link_from(node)
            dpg.delete_item(link)
        for other_id, link in node.input_links.copy().items():
            other = self.find_node(node_id=other_id)
            node.delete_link_from(other)
            other.delete_link_to(node)
            dpg.delete_item(link)
        if node in self.nodes:
            self.nodes.remove(node)
        dpg.delete_item(node.tag)
        self.clear_parameter_window(True)
        self.validate_nodes()

    def clear_nodes(self):
        self.reset_element_counter()
        self.reset_dummy_counter()
        dpg.delete_item(self.node_editor, children_only=True)
        self.wes_node = Node(
            self.node_editor,
            -999999,
            "WE+WS",
            (
                self.x_offset,
                self.y_offset,
            ),
            input_attribute=False,
        )
        dpg.bind_item_handler_registry(self.wes_node.tag, self.node_handler)
        self.cere_node = Node(
            self.node_editor,
            999999,
            "CE+RE",
            (
                self.x_offset + self.x_step * 2,
                self.y_offset,
            ),
            output_attribute=False,
        )
        dpg.bind_item_handler_registry(self.cere_node.tag, self.node_handler)
        self.nodes = []
        self.clear_parameter_window(True)

    def reset_element_counter(self):
        self.element_counter = -1

    def next_element(self) -> int:
        self.element_counter += 1
        assert self.element_counter < self.cere_node.id
        return self.element_counter

    def reset_dummy_counter(self):
        self.dummy_counter = -1

    def next_dummy(self) -> int:
        self.dummy_counter -= 1
        assert self.dummy_counter > self.wes_node.id
        return self.dummy_counter

    def set_status(self, msg: str):
        assert type(msg) is str
        dpg.configure_item(self.status_field, default_value=msg)

    def set_accept_button(self, label: str):
        assert type(label) is str
        dpg.configure_item(self.accept_button, label=label)

    def update_cdc_output(self, circuit: Optional[Circuit], stack: List[str] = []):
        assert type(circuit) is Circuit or circuit is None
        assert type(stack) is list and all(map(lambda _: type(_) is str, stack))
        simple_cdc: str = ""
        detailed_cdc: str = ""
        theme: int = themes.valid_cdc
        if circuit is not None:
            simple_cdc = circuit.to_string()
            detailed_cdc = circuit.to_string(4)
        else:
            simple_cdc = "".join(
                map(lambda _: _[: _.find("{")] if "{" in _ else _, stack)
            )
            detailed_cdc = "".join(stack)
            theme = themes.invalid_cdc
        dpg.configure_item(self.simple_cdc_output_field, default_value=simple_cdc)
        dpg.configure_item(self.detailed_cdc_output_field, default_value=detailed_cdc)
        dpg.bind_item_theme(self.simple_cdc_output_field, theme)
        dpg.bind_item_theme(self.detailed_cdc_output_field, theme)

    def walk_nodes(
        self,
        node: Node,
        stack: List[str],
        visited_nodes: Set[int],
        pending_nodes: Set[int],
    ):
        assert type(node) is Node
        assert type(stack) is list and all(map(lambda _: type(_) is str, stack))
        assert type(visited_nodes) is set
        assert type(pending_nodes) is set
        if node.id in visited_nodes:
            return
        num_links_out: int = len(node.output_links)
        num_links_in: int
        stack_len: int
        if node == self.wes_node:  # WE+WS node (i.e. the starting point)
            assert num_links_out > 0, self.wes_node.set_invalid(
                "WE+WS is not connected to anything!"
            )
            assert (
                self.cere_node.id not in node.output_links
            ), self.wes_node.set_invalid(
                self.cere_node.set_invalid("WE+WS is shorted to CE+RE!")
            )
            stack.append("[")
            if num_links_out > 1:  # Start of parallel connection
                stack.append("(")
                tmp_pending_nodes = set(pending_nodes)
                for ident, link in node.output_links.items():
                    stack.append("[")
                    stack_len = len(stack)
                    self.walk_nodes(
                        self.find_node(node_id=ident),
                        stack,
                        visited_nodes,
                        pending_nodes,
                    )
                    if len(stack) > stack_len + 1:  # More than one element was added
                        stack.append("]")
                    else:  # Only one element was added
                        stack.pop(-2)
                for ident in list(pending_nodes):
                    if ident in tmp_pending_nodes:
                        continue
                    pending_nodes.remove(ident)
                    self.walk_nodes(
                        self.find_node(node_id=ident),
                        stack,
                        visited_nodes,
                        pending_nodes,
                    )
            else:
                for ident, link in node.output_links.items():
                    self.walk_nodes(
                        self.find_node(node_id=ident),
                        stack,
                        visited_nodes,
                        pending_nodes,
                    )
            for node in filter(lambda _: _.id >= 0, self.nodes):  # Element nodes
                assert node.get_num_input_links() > 0, node.set_invalid(
                    f"{node.label.strip()} has insufficient input connections!"
                )
                assert node.get_num_output_links() > 0, node.set_invalid(
                    f"{node.label.strip()} has insufficient output connections!"
                )
                assert node.id in visited_nodes, node.set_invalid(
                    f"{node.label.strip()} was not visited!"
                )
            for node in filter(lambda _: _.id < -1, self.nodes):  # Dummy nodes
                num_links_in = node.get_num_input_links()
                num_links_out = node.get_num_output_links()
                assert (num_links_in > 0 and num_links_out > 1) or (
                    num_links_in > 1 and num_links_out > 0
                ), node.set_invalid("A dummy node has insufficient connections!")
                assert node.id in visited_nodes, node.set_invalid(
                    "A dummy node was not visited!"
                )
            assert len(pending_nodes) == 0, "The queue for nodes to visit is not empty!"
            # Make sure all other nodes have been visited
            required_nodes: Set[int] = set(map(lambda _: _.id, self.nodes))
            required_nodes.add(self.cere_node.id)
            assert required_nodes == visited_nodes, "Disconnected node(s) detected!"
            return
        num_links_in = len(node.input_links)
        if node == self.cere_node:  # CE+RE node (i.e. the end point)
            if num_links_in > 1:  # End of a parallel connection
                # Make sure all nodes in the parallel connection have been visited first
                if not set(node.input_links.keys()).issubset(visited_nodes):
                    pending_nodes.add(node.id)
                    return
                elif node.id in pending_nodes:
                    return
                if stack[-1] == "(":
                    stack.pop()
                elif stack[-1] != ")":
                    stack.append(")")
            visited_nodes.add(node.id)
            stack.append("]")
        else:  # Element and dummy nodes
            element: Optional[Element] = node.element
            if num_links_in > 1:  # End of a parallel connection
                # Make sure all nodes in the parallel connection have been visited first
                if not set(node.input_links.keys()).issubset(visited_nodes):
                    pending_nodes.add(node.id)
                    return
                elif node.id in pending_nodes:
                    return
                if stack[-1] != ")":
                    stack.append(")")
            visited_nodes.add(node.id)
            if element is not None:
                assert num_links_out > 0, node.set_invalid(
                    f"{element.get_label()} is missing a connection!"
                )
                stack.append(node.element.to_string(12))  # type: ignore
                # stack.append(node.element.to_string())  # DEBUGGING
            else:
                assert (num_links_in > 0 and num_links_out > 1) or (
                    num_links_in > 1 and num_links_out > 0
                ), node.set_invalid(
                    "Dummy nodes must connect to at least one element on one side "
                    "and at least two elements on the other side!"
                )
            if num_links_out > 1:
                stack.append("(")
                tmp_pending_nodes = set(pending_nodes)
                for ident, link in node.output_links.items():
                    stack.append("[")
                    stack_len = len(stack)
                    self.walk_nodes(
                        self.find_node(node_id=ident),
                        stack,
                        visited_nodes,
                        pending_nodes,
                    )
                    if len(stack) > stack_len + 1:  # More than one element was added
                        stack.append("]")
                    else:  # Only one element was added
                        stack.pop(-2)
                stack.append(")")
                for ident in list(pending_nodes):
                    if ident in tmp_pending_nodes:
                        continue
                    pending_nodes.remove(ident)
                    self.walk_nodes(
                        self.find_node(node_id=ident),
                        stack,
                        visited_nodes,
                        pending_nodes,
                    )
            else:
                for ident, link in node.output_links.items():
                    self.walk_nodes(
                        self.find_node(node_id=ident),
                        stack,
                        visited_nodes,
                        pending_nodes,
                    )

    def generate_circuit(self) -> Tuple[Optional[Circuit], str, List[str]]:
        circuit: Optional[Circuit] = None
        msg: str = "OK"
        stack: List[str] = []
        visited_nodes: Set[int] = set({})
        pending_nodes: Set[int] = set({})
        if self.wes_node is not None:
            self.wes_node.set_valid()
        if self.cere_node is not None:
            self.cere_node.set_valid()
        list(map(lambda _: _.set_valid(), self.nodes))
        try:
            self.walk_nodes(self.wes_node, stack, visited_nodes, pending_nodes)
            circuit = string_to_circuit("".join(stack))
        except AssertionError as e:
            msg = str(e)
        except ParsingError as e:
            msg = str(e)
        return (
            circuit,
            msg,
            stack,
        )

    def validate_nodes(self) -> Optional[Circuit]:
        circuit: Optional[Circuit]
        msg: str
        stack: List[str]
        circuit, msg, stack = self.generate_circuit()
        self.update_cdc_output(circuit, stack)
        self.set_status(msg)
        if circuit is not None:
            self.set_accept_button("Accept circuit")
        else:
            if not self.nodes:
                self.set_accept_button("Close window")
            else:
                self.set_accept_button("Cancel")
        self.latest_circuit = circuit
        return circuit

    def generate_nodes(self, input_stack):
        element_stack: List[Union[Connection, Element]] = []
        symbol_stack: List[str] = []
        node_stack: List[Union[Node, List[Node]]] = [self.wes_node]

        symbol: str
        element: Union[Connection, Element]
        node: Node
        other: Node
        others: List[Node]
        width: int
        height: int
        w: int
        h: int

        def is_dummy_node(item) -> bool:
            if type(item) is Node:
                return item.id < -1 and item.id > self.wes_node.id
            return False

        def pop_input() -> Tuple[str, Union[Element, Series, Parallel]]:
            symbol, element = input_stack.pop(0)
            symbol_stack.append(symbol)
            element_stack.append(element)
            return (
                symbol,
                element,
            )

        def process_series_element(this: Element, x: int, y: int) -> Tuple[int, int]:
            assert isinstance(this, Element), type(element)
            assert type(x) is int
            assert type(y) is int
            nonlocal symbol_stack
            node = self.add_element_node(
                this,
                pos=(
                    x,
                    y,
                ),
            )
            if type(node_stack[-1]) is list:
                if len(element_stack) > 2 and type(element_stack[-3]) is Parallel:
                    if symbol_stack[-2] == ")":
                        for other in node_stack.pop():  # type: ignore
                            self.link_nodes(other, node)
                    else:
                        assert type(node_stack[-2]) is Node
                        if (
                            node_stack[-2] == self.wes_node
                            or is_dummy_node(node_stack[-2])
                        ) or (
                            type(node_stack[-2]) is Node
                            and type(node_stack[-1]) is list
                        ):
                            other = node_stack[-2]
                        else:
                            other = node_stack.pop(-2)
                        self.link_nodes(other, node)  # type: ignore
                else:
                    others = node_stack.pop()
                    for other in others:  # type: ignore
                        self.link_nodes(other, node)
            else:
                if node_stack[-1] == self.wes_node:
                    other = node_stack[-1]
                else:
                    other = node_stack.pop()
                self.link_nodes(other, node)  # type: ignore
            node_stack.append(node)
            element_stack.pop()
            return (
                1,
                0,
            )

        def process_series_dummy(x: int, y: int) -> Tuple[int, int]:
            assert type(x) is int
            assert type(y) is int
            if (
                element_stack
                and type(element_stack[-1]) is Parallel
                and type(node_stack[-1]) is list
                and symbol_stack[-2] == ")"
                and symbol_stack[-1] == "]"
            ):
                node = self.add_dummy_node(
                    pos=(
                        x,
                        y,
                    )
                )
                for other in node_stack.pop():  # type: ignore
                    self.link_nodes(other, node)
                node_stack.append(node)
                return (
                    1,
                    0,
                )
            return (
                0,
                0,
            )

        def process_series(this: Series, x: int, y: int) -> Tuple[int, int]:
            assert type(this) is Series
            assert type(x) is int
            assert type(y) is int
            nonlocal symbol_stack
            width = 0
            height = 0
            # Main processing of the series connection
            symbol, element = pop_input()
            while element is not this:
                if type(element) is Series:
                    w, h = process_series(element, x + width, y)
                    width += w
                    if h > height:
                        height = h
                elif type(element) is Parallel:
                    w, h = process_parallel(element, x + width, y)
                    width += w
                    if h > height:
                        height = h
                else:
                    w, h = process_series_element(element, x + width, y)
                    width += w
                symbol, element = pop_input()
            assert element_stack.pop() is this
            assert element_stack.pop() is this
            # Add a dummy node, if necessary
            w, h = process_series_dummy(x + width, y)
            width += w
            # Clean up
            if len(node_stack) > 1 and type(node_stack[-2]) is list:
                assert type(node_stack[-1]) is Node
                node_stack[-2].append(node_stack.pop())  # type: ignore
            return (
                max(1, width),
                max(1, height),
            )

        def process_parallel_element(this: Element, x: int, y: int) -> Tuple[int, int]:
            assert isinstance(this, Element), type(element)
            assert type(x) is int
            assert type(y) is int
            nonlocal symbol_stack
            node = self.add_element_node(
                this,
                pos=(
                    x,
                    y,
                ),
            )
            assert type(node_stack[-2]) is Node
            self.link_nodes(node_stack[-2], node)  # type: ignore
            assert type(node_stack[-1]) is list
            node_stack[-1].append(node)  # type: ignore
            element_stack.pop()
            return (
                1,
                1,
            )

        def process_parallel_dummy(x: int, y: int) -> Tuple[int, int]:
            assert type(x) is int
            assert type(y) is int
            if type(node_stack[-1]) is list:
                if len(element_stack) > 2 and type(element_stack[-2]) is Series:
                    node = self.add_dummy_node(
                        pos=(
                            x,
                            y,
                        )
                    )
                    if type(node_stack[-1]) is list:
                        if symbol_stack[-2] == "[" and symbol_stack[-1] == "(":
                            assert type(node_stack[-2]) is Node
                            self.link_nodes(node_stack[-2], node)  # type: ignore
                        else:
                            for other in node_stack.pop():  # type: ignore
                                self.link_nodes(other, node)  # type: ignore
                    else:
                        assert type(node_stack[-2]) is Node
                        self.link_nodes(node_stack[-2], node)  # type: ignore
                    node_stack.append(node)
                elif symbol_stack[-1] == "(" and (
                    symbol_stack[-2] == ")"
                    or (symbol_stack[-2] == "]" and symbol_stack[-3] == ")")
                ):
                    node = self.add_dummy_node(
                        pos=(
                            x,
                            y,
                        )
                    )
                    for other in node_stack.pop():  # type: ignore
                        self.link_nodes(other, node)
                    node_stack.append(node)
                else:
                    return (
                        0,
                        0,
                    )
                return (
                    1,
                    0,
                )
            return (
                0,
                0,
            )

        def process_parallel(this: Parallel, x: int, y: int) -> Tuple[int, int]:
            assert type(this) is Parallel
            assert type(x) is int
            assert type(y) is int
            nonlocal symbol_stack
            width = 0
            height = 0
            # Add a dummy node, if necessary
            dummy_width: int
            dummy_width, _ = process_parallel_dummy(x, y)
            # Main processing of the parallel connection
            node_stack.append([])
            symbol, element = pop_input()
            while element is not this:
                if type(element) is Series:
                    w, h = process_series(element, x + dummy_width, y + height)
                    if w > width:
                        width = w
                    height += h
                elif type(element) is Parallel:
                    w, h = process_parallel(element, x + dummy_width, y + height)
                    if w > width:
                        width = w
                    height += h
                else:
                    w, h = process_parallel_element(
                        element, x + dummy_width, y + height
                    )
                    if w > width:
                        width = w
                    height += h
                symbol, element = pop_input()
            assert element_stack.pop() is this
            assert element_stack.pop() is this
            # Clean up
            if (
                len(node_stack) > 1
                and type(node_stack[-2]) is Node
                and node_stack[-2] != self.wes_node
            ):
                node_stack.pop(-2)
            return (
                max(1, width + dummy_width),
                max(1, height),
            )

        input_length: int = len(input_stack)
        symbol, element = pop_input()
        assert symbol == "[" and type(element) is Series
        width, height = process_series(element, 1, 0)
        assert len(element_stack) == 0, element_stack
        assert len(symbol_stack) == input_length
        assert node_stack.pop(0) == self.wes_node
        assert len(node_stack) == 1
        if type(node_stack[-1]) is list:
            for node in node_stack[-1]:
                self.link_nodes(node, self.cere_node)
        else:
            self.link_nodes(node_stack[-1], self.cere_node)
        dpg.configure_item(
            self.cere_node.tag,
            pos=(
                self.x_offset + self.x_step * (width + 1),
                self.y_offset,
            ),
        )

    def parse_cdc(
        self, cdc: str = "", update_input_field: bool = False
    ) -> Optional[Circuit]:
        assert type(cdc) is str
        assert type(update_input_field) is bool
        if not (cdc.startswith("[") and cdc.endswith("]")) and not (
            ("[" + cdc).startswith("[[") or (cdc + "]").endswith("]]")
        ):
            cdc = f"[{cdc}]"
        if update_input_field:
            dpg.set_value(self.cdc_input_field, cdc)
        self.clear_nodes()
        try:
            circuit: Circuit = string_to_circuit(cdc)
        except (AssertionError, ParsingError) as e:
            self.update_cdc_output(None)
            self.set_status(str(e))
            return None
        cdc = circuit.to_string()
        if cdc == "[]":
            return self.validate_nodes()
        if update_input_field:
            dpg.set_value(self.cdc_input_field, cdc)
        input_stack = circuit.to_stack()
        assert cdc == "".join(map(lambda _: _[0], input_stack))
        self.generate_nodes(input_stack)
        return self.validate_nodes()


def _main_testing_window() -> int:
    main_window: int
    with dpg.window() as main_window:
        pass
    CDCs: List[str] = [
        "R",
        "RL",
        "(RL)",
        "([RL]C)",
        "(R[LC])",
        "(R[LC]W)",
        "(W[(RL)C])Q",
        "RLC",
        "RLCQ",
        "RLCQW",
        "(RLC)",
        "(RLCQ)",
        "(RLCQW)",
        "R(LCQW)",
        "RL(CQW)",
        "RLC(QW)",
        "(RLCQ)W",
        "(RLC)QW",
        "(RL)CQW",
        "R(LCQ)W",
        "R(LC)QW",
        "RL(CQ)W",
        "(R[WQ])",
        "(R[WQ]C)",
        "(R[W(LC)Q])",
        "([LC][RRQ])",
        "(R[WQ])([LC][RRQ])",
        "([RL][CW])",
        "R(RW)",
        "R(RW)C",
        "R(RWL)C",
        "R(RWL)(LQ)C",
        "R(RWL)C(LQ)",
        "R(LQ)C(RWL)",
        "R([RW]Q)C",
        "R(RW)(CQ)",
        "R([RW]Q[LRC])(CQ)",
        "R([RW][L(RQ)C]Q[LRC])(CQ)",
        "R([RW][L(WC)(RQ)C]Q[LRC])(CQ)",
        "(R[LCQW])",
        "(RL[CQW])",
        "(RLC[QW])",
        "(R[LCQ]W)",
        "(R[LC]QW)",
        "(RL[CQ]W)",
        "R(LC)(QW)",
        "(RL)C(QW)",
        "(RL)(CQ)W",
        "(RL)(CQW)",
        "(RLC)(QW)",
        "(R[LC])QW",
        "([RL]C)QW",
        "([RL]CQ)W",
        "([RL]CQW)",
        "([RLC]QW)",
        "([RLCQ]W)",
        "(R[(LC)QW])",
        "(R[L(CQ)W])",
        "(R[LC(QW)])",
        "(R[L(CQW)])",
        "(R[(LCQ)W])",
        "(R[(LC)Q]W)",
        "(R[L(CQ)]W)",
        "(RQ)RWL",
        "RWL(RQ)",
        "(R[QR])(LC)RW",
        "RW(LC)(RQ)",
        "RL(QW)L(RR)(RR)L(RR)C",
        "RL(QW)(L[(RR)(RR)L(RR)C])",
        "RL(QW)(L[(RR)(RR)L(RR)])",
    ]
    CDCs = list(map(lambda _: f"[{_}]", CDCs))
    # if True:
    if False:
        for cdc in set(CDCs):
            CDCs.remove(cdc)
        print(CDCs)
        assert None
    assert len(CDCs) == len(set(CDCs)), (
        len(CDCs),
        len(set(CDCs)),
    )
    cdc_counter: int = 0
    circuit_editor: Optional[CircuitEditor] = None

    def next_cdc(accepted_circuit: Optional[Circuit]):
        assert accepted_circuit is not None
        cdc: str = CDCs.pop(0)
        assert cdc == accepted_circuit.to_string(), (cdc, accepted_circuit.to_string())
        nonlocal cdc_counter
        cdc_counter += 1
        print(f"CDC #{cdc_counter} passed!")
        print(
            "################################################################################\n"
        )
        if not CDCs:
            print("Every CDC was successfully processed!")
            assert circuit_editor is not None
            circuit_editor.parse_cdc("", update_input_field=True)
            return
        cdc = CDCs[0]
        print(f"Testing: '{cdc}'")
        string_to_circuit(cdc)
        assert circuit_editor is not None
        circuit_editor.parse_cdc(cdc, update_input_field=True)
        circuit_editor.show_window()

    for cdc in CDCs:
        print(f"Validating '{cdc}'")
        string_to_circuit(cdc)
    circuit_editor = CircuitEditor(main_window, accept_callback=next_cdc)
    circuit_editor.parse_cdc(CDCs[0], update_input_field=True)
    # print(circuit_editor.nodes_to_dict("R{:Rsol}([R{:Rct}W{:Wdiff}]C{:Cdl})"))
    return main_window


def _main():
    dpg.create_context()
    themes.initialize()
    program_name: str = "Circuit editor"
    dpg.create_viewport(title=program_name)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.set_primary_window(_main_testing_window(), True)
    dpg.start_dearpygui()
    dpg.destroy_context()


if __name__ == "__main__":
    _main()
