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

from typing import Optional
import dearpygui.dearpygui as dpg
from pyimpspec import Circuit
from deareis.gui.circuit_editor.parser import Parser


class CircuitPreview:
    def __init__(self, width: int = -1, height: int = -1):
        self.node_editor: int = dpg.generate_uuid()
        dpg.add_node_editor(
            width=width,
            height=height,
            tag=self.node_editor,
            minimap=True,
            minimap_location=dpg.mvNodeMiniMap_Location_BottomRight,
        )
        self.parser: Parser = Parser(self.node_editor)

    def clear(self):
        dpg.delete_item(self.node_editor, children_only=True)

    def update(self, circuit: Optional[Circuit]):
        self.clear()
        if circuit is None:
            return
        self.parser.circuit_to_nodes(circuit)
