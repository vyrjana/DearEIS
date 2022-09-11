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

from typing import Callable, Dict, List, Optional, Set, Tuple, Union
import dearpygui.dearpygui as dpg
from pyimpspec import Circuit, Connection, Element, Parallel, Series, ParsingError
import pyimpspec
import deareis.themes as themes


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
        dpg.bind_item_theme(self.tag, themes.circuit_editor.valid_node)

    def set_invalid(self, msg: str) -> str:
        dpg.bind_item_theme(self.tag, themes.circuit_editor.invalid_node)
        return msg


class Parser:
    def __init__(self, node_editor: int, node_handler: int = -1):
        assert type(node_editor) is int, node_editor
        assert dpg.does_item_exist(node_editor) and "mvNodeEditor" in dpg.get_item_type(
            node_editor
        )
        assert type(node_handler) is int, node_handler
        assert node_handler < 0 or dpg.does_item_exist(node_handler), node_handler
        self.node_editor: int = node_editor
        dpg.configure_item(
            self.node_editor,
            callback=self.link,
            delink_callback=self.delink,
        )
        self.node_handler: int = node_handler
        self.we_node: Node = None  # type: ignore
        self.cere_node: Node = None  # type: ignore
        self.nodes: List[Node] = []
        self.element_counter: int = -1
        self.dummy_counter: int = -1
        self.x_offset: int = 10
        self.y_offset: int = 10
        self.x_step: int = 90
        self.y_step: int = 70
        self.elements: Dict[str, Element] = {
            _.get_description(): _ for _ in pyimpspec.get_elements().values()
        }

    def circuit_to_nodes(self, circuit: Circuit):
        assert type(circuit) is Circuit, circuit
        input_stack: List[Tuple[str, Union[Element, Connection]]] = circuit.to_stack()
        assert circuit.to_string() == "".join(map(lambda _: _[0], input_stack))
        self.clear_nodes()
        if circuit.to_string() not in ["[]", "()"]:
            self.generate_nodes(input_stack)

    def nodes_to_circuit(self, node_editor: int) -> Circuit:
        assert type(node_editor) is int, node_editor
        circuit: Optional[Circuit]
        msg: str
        stack: List[str]
        circuit, msg, stack = self.generate_circuit()
        assert type(circuit) is Circuit, circuit
        return circuit

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
        if func(self.we_node):
            return self.we_node
        elif func(self.cere_node):
            return self.cere_node
        raise Exception("Node does not exist!")

    def link(self, sender: int, attributes: Tuple[int, int]):
        assert type(sender) is int
        assert (
            type(attributes) is tuple
            and len(attributes) == 2
            and all(map(lambda _: type(_) is int, attributes))
        )
        link: int = dpg.add_node_link(*attributes, parent=sender)
        src: Node = self.find_node(attribute=attributes[0])
        dst: Node = self.find_node(attribute=attributes[1])
        # print(f"Link: {src.label=}, {dst.label=}, {link=}, {validate=}")
        src.add_link_to(dst, link)
        dst.add_link_from(src, link)

    def delink(self, sender: int, link: int):
        assert type(sender) is int
        assert type(link) is int
        src: Node = self.find_node(link_to=link)
        dst: Node = self.find_node(link_from=link)
        # print(f"Delink: {src.label=}, {dst.label=}, {link=}")
        src.delete_link_to(dst)
        dst.delete_link_from(src)
        dpg.delete_item(link)

    def link_nodes(self, src: Node, dst: Node):
        assert type(src) is Node
        assert type(dst) is Node
        src_attr = dpg.get_item_children(src.tag, slot=1)[
            1 if src != self.we_node else 0
        ]
        dst_attr = dpg.get_item_children(dst.tag, slot=1)[0]
        self.link(self.node_editor, (src_attr, dst_attr))

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
        if self.node_handler > 0:
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

    def clear_nodes(self):
        self.reset_element_counter()
        self.reset_dummy_counter()
        dpg.delete_item(self.node_editor, children_only=True)
        self.we_node = Node(
            self.node_editor,
            -999999,
            "WE",
            (
                self.x_offset,
                self.y_offset,
            ),
            input_attribute=False,
        )
        if self.node_handler > 0:
            dpg.bind_item_handler_registry(self.we_node.tag, self.node_handler)
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
        if self.node_handler > 0:
            dpg.bind_item_handler_registry(self.cere_node.tag, self.node_handler)
        self.nodes = []

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
        assert self.dummy_counter > self.we_node.id
        return self.dummy_counter

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
        if node == self.we_node:  # WE node (i.e. the starting point)
            assert num_links_out > 0, self.we_node.set_invalid(
                "WE is not connected to anything!"
            )
            assert (
                self.cere_node.id not in node.output_links
            ), self.we_node.set_invalid(
                self.cere_node.set_invalid("WE is shorted to CE+RE!")
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
        if self.we_node is not None:
            self.we_node.set_valid()
        if self.cere_node is not None:
            self.cere_node.set_valid()
        list(map(lambda _: _.set_valid(), self.nodes))
        try:
            self.walk_nodes(self.we_node, stack, visited_nodes, pending_nodes)
            circuit = pyimpspec.parse_cdc("".join(stack))
        except AssertionError as e:
            msg = str(e)
        except ParsingError as e:
            msg = str(e)
        return (
            circuit,
            msg,
            stack,
        )

    def generate_nodes(self, input_stack):
        element_stack: List[Union[Connection, Element]] = []
        symbol_stack: List[str] = []
        node_stack: List[Union[Node, List[Node]]] = [self.we_node]

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
                return item.id < -1 and item.id > self.we_node.id
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
                            node_stack[-2] == self.we_node
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
                if node_stack[-1] == self.we_node:
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
                and node_stack[-2] != self.we_node
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
        assert node_stack.pop(0) == self.we_node
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
