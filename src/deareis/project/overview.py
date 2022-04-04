# Copyright 2022 DearEIS developers
# DearEIS is licensed under the GPLv3 or later (https://www.gnu.org/licenses/gpl-3.0.html).
# The licenses of DearEIS' dependencies and/or sources of portions of code are included in
# the LICENSES folder.

import dearpygui.dearpygui as dpg

# TODO: Argument type assertions


class OverviewTab:
    def __init__(self):
        self.tab: int = dpg.generate_uuid()
        #
        self.label_input: int = dpg.generate_uuid()
        self.notes_input: int = dpg.generate_uuid()
        #
        self._assemble()

    def to_dict(self) -> dict:
        return {
            "label": dpg.get_value(self.label_input),
            "notes": dpg.get_value(self.notes_input),
        }

    def restore_state(self, state: dict):
        dpg.set_value(self.label_input, state["label"])
        dpg.set_value(self.notes_input, state["notes"])

    def get_label(self) -> str:
        return dpg.get_value(self.label_input) or "Project"

    def set_label(self, label: str):
        assert type(label) is str
        dpg.set_value(self.label_input, label)

    def get_notes(self) -> str:
        return dpg.get_value(self.notes_input) or ""

    def set_notes(self, notes: str):
        assert type(notes) is str
        dpg.set_value(self.notes_input, notes)

    def _assemble(self):
        with dpg.tab(label="Overview", tag=self.tab):
            with dpg.group(horizontal=True):
                dpg.add_text("Label")
                dpg.add_input_text(
                    tag=self.label_input,
                    on_enter=True,
                    width=-1,
                )
            dpg.add_text("Notes")
            dpg.add_input_text(
                tag=self.notes_input,
                multiline=True,
                tab_input=True,
                width=-1,
                height=-1,
            )

    def is_visible(self) -> bool:
        return dpg.is_item_visible(self.label_input)


if __name__ == "__main__":
    dpg.create_context()
    dpg.create_viewport(title="Overview tab")
    dpg.setup_dearpygui()
    dpg.show_viewport()
    window: int
    with dpg.window() as window:
        with dpg.tab_bar():
            OverviewTab()
    dpg.set_primary_window(window, True)
    dpg.start_dearpygui()
    dpg.destroy_context()
