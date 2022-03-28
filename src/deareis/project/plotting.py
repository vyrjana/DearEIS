# Copyright 2022 DearEIS developers
# DearEIS is licensed under the GPLv3 or later (https://www.gnu.org/licenses/gpl-3.0.html).
# The licenses of DearEIS' dependencies and/or sources of portions of code are included in
# the LICENSES folder.

import dearpygui.dearpygui as dpg
from deareis.utility import attach_tooltip


"""
This tab is mainly intended for plotting e.g. multiple data sets together for easy comparison.

TODO:
- Implement different plot types
    - Bode
    - Nyquist
- Different sources
    - Data sets
    - Kramers-Kronig tests
    - Circuit fits
    - Simulations
"""


class PlottingTab:
    def __init__(self):
        self.tab: int = dpg.generate_uuid()
        self.resize_group: int = dpg.generate_uuid()
        #
        self.plot_combo: int = dpg.generate_uuid()
        #
        self._assemble()

    def to_dict(self) -> dict:
        # TODO: Implement
        return {}

    def restore_state(self, state):
        # TODO: Implement
        pass

    def _assemble(self):
        label_pad: int = 5
        with dpg.tab(label="Plotting", show=False, tag=self.tab):
            with dpg.group(horizontal=True, tag=self.resize_group):
                with dpg.child_window(width=500, height=-1):
                    with dpg.group(horizontal=True):
                        dpg.add_text("Plot".rjust(label_pad))
                        dpg.add_combo(width=-96, tag=self.plot_combo)
                        dpg.add_button(label="New")
                        dpg.add_button(label="Delete")
                    with dpg.group(horizontal=True):
                        dpg.add_text("Type".rjust(label_pad))
                        dpg.add_combo(width=-96)
                    with dpg.group(horizontal=True):
                        dpg.add_text("Label".rjust(label_pad))
                        dpg.add_input_text(width=-96)
                    dpg.add_spacer(height=8)
                    with dpg.table(
                        borders_outerV=True,
                        borders_outerH=True,
                        borders_innerV=True,
                        borders_innerH=True,
                        scrollY=True,
                        freeze_rows=1,
                        width=-1,
                        height=41,
                    ):
                        dpg.add_table_column(label="Type", width_fixed=True)
                        dpg.add_table_column(label="Label", width_fixed=True)
                        dpg.add_table_column(label="Appearance", width_fixed=True)
                        dpg.add_table_column(label="Position", width=30)
                        with dpg.table_row():
                            dpg.add_text("D   ")
                            attach_tooltip("Data set")
                            dpg.add_input_text(hint="Default", width=240)
                            attach_tooltip("Default label")
                            dpg.add_button(label="Edit", width=-1)
                            with dpg.group(horizontal=True):
                                dpg.add_button(label="Up", width=50)
                                dpg.add_button(label="Down", width=50)
                    dpg.add_spacer(height=8)
                    with dpg.collapsing_header(label="Data sets"):
                        with dpg.table(
                            borders_outerV=True,
                            borders_outerH=True,
                            borders_innerV=True,
                            borders_innerH=True,
                            scrollY=True,
                            freeze_rows=1,
                            width=-1,
                            height=41,
                        ):
                            dpg.add_table_column(label="", width_fixed=True)
                            dpg.add_table_column(label="Label", width_fixed=True)
                            with dpg.table_row():
                                dpg.add_checkbox()
                                dpg.add_text("Default")
                    with dpg.collapsing_header(label="Kramers-Kronig tests"):
                        with dpg.table(
                            borders_outerV=True,
                            borders_outerH=True,
                            borders_innerV=True,
                            borders_innerH=True,
                            scrollY=True,
                            freeze_rows=1,
                            width=-1,
                            height=41,
                        ):
                            dpg.add_table_column(label="", width_fixed=True)
                            dpg.add_table_column(label="Label", width_fixed=True)
                            with dpg.table_row():
                                dpg.add_checkbox()
                                dpg.add_text("Default")
                    with dpg.collapsing_header(label="Fitted equivalent circuits"):
                        with dpg.table(
                            borders_outerV=True,
                            borders_outerH=True,
                            borders_innerV=True,
                            borders_innerH=True,
                            scrollY=True,
                            freeze_rows=1,
                            width=-1,
                            height=41,
                        ):
                            dpg.add_table_column(label="", width_fixed=True)
                            dpg.add_table_column(label="Label", width_fixed=True)
                            with dpg.table_row():
                                dpg.add_checkbox()
                                dpg.add_text("Default")
                    with dpg.collapsing_header(label="Simulations"):
                        with dpg.table(
                            borders_outerV=True,
                            borders_outerH=True,
                            borders_innerV=True,
                            borders_innerH=True,
                            scrollY=True,
                            freeze_rows=1,
                            width=-1,
                            height=41,
                        ):
                            dpg.add_table_column(label="", width_fixed=True)
                            dpg.add_table_column(label="Label", width_fixed=True)
                            with dpg.table_row():
                                dpg.add_checkbox()
                                dpg.add_text("Default")
                with dpg.group():
                    pass

    def is_visible(self) -> bool:
        return dpg.is_item_visible(self.plot_combo)

    def resize(self):
        dpg.split_frame(delay=100)


if __name__ == "__main__":
    dpg.create_context()
    dpg.create_viewport(title="Plotting tab")
    dpg.setup_dearpygui()
    dpg.show_viewport()
    window: int
    with dpg.window() as window:
        with dpg.tab_bar():
            PlottingTab()
    dpg.set_primary_window(window, True)
    dpg.start_dearpygui()
    dpg.destroy_context()
