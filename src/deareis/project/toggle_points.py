# Copyright 2022 DearEIS developers
# DearEIS is licensed under the GPLv3 or later (https://www.gnu.org/licenses/gpl-3.0.html).
# The licenses of DearEIS' dependencies and/or sources of portions of code are included in
# the LICENSES folder.

from pyimpspec import DataSet
from typing import Callable, Dict, List
import dearpygui.dearpygui as dpg
from deareis.plot import NyquistPlot
import deareis.themes as themes
from deareis.utility import window_pos_dims, number_formatter

# TODO: Argument type assertions

# TODO: Add resize handler to check when the viewport is resized


class TogglePoints:
    def __init__(self, data: DataSet, callback: Callable):
        assert type(data) is DataSet
        assert callback is not None
        self.data: DataSet = data
        self.callback: Callable = callback
        self.preview_data: DataSet = DataSet.from_dict(data.to_dict())
        self.original_mask: Dict[int, bool] = data.get_mask()
        self.final_mask: Dict[int, bool] = {
            i: state for i, state in self.original_mask.items()
        }
        self.labels: List[str] = []
        i: int
        f: float
        Z: complex
        for i, (f, Z) in enumerate(
            zip(data.get_frequency(masked=None), data.get_impedance(masked=None))
        ):
            self.labels.append(
                f"{i + 1:02}: "
                + f"f = {number_formatter(f, 1, 9).strip()}, "
                + f"Z'= {number_formatter(Z.real, 1, 10).strip()}, "
                + f'-Z" = {number_formatter(-Z.imag, 1, 10).strip()}'
            )
        self.window: int = dpg.generate_uuid()
        self.from_combo: int = dpg.generate_uuid()
        self.to_combo: int = dpg.generate_uuid()
        self.preview_plot: int = dpg.generate_uuid()
        self.preview_nyquist: NyquistPlot = None
        self.key_handler: int = dpg.generate_uuid()
        self._assemble()
        self._setup_keybindings()
        self.update_items(self.from_combo, self.labels[0])
        self.update_items(self.to_combo, self.labels[-1])
        self.update_preview()

    def _setup_keybindings(self):
        with dpg.handler_registry(tag=self.key_handler):
            dpg.add_key_release_handler(
                key=dpg.mvKey_Escape,
                callback=self.close,
            )
            dpg.add_key_release_handler(
                key=dpg.mvKey_Return,
                callback=self.accept,
            )

    def _assemble(self):
        x: int
        y: int
        w: int
        h: int
        x, y, w, h = window_pos_dims()
        with dpg.window(
            label="Toggle points",
            modal=True,
            pos=(
                x,
                y,
            ),
            width=w,
            height=h,
            tag=self.window,
            on_close=self.close,
        ):
            with dpg.group(horizontal=True):
                dpg.add_text("From")
                dpg.add_combo(
                    default_value=self.labels[0],
                    width=-1,
                    callback=self.update_items,
                    tag=self.from_combo,
                )
            with dpg.group(horizontal=True):
                dpg.add_text("  To")
                dpg.add_combo(
                    default_value=self.labels[-1],
                    width=-1,
                    callback=self.update_items,
                    tag=self.to_combo,
                )
            with dpg.group(horizontal=True):
                dpg.add_text("    ")
                dpg.add_button(
                    label="Exclude all",
                    callback=self.exclude,
                )
                dpg.add_button(
                    label="Include all",
                    callback=self.include,
                )
            self.preview_nyquist = NyquistPlot(
                dpg.add_plot(
                    equal_aspects=True,
                    width=-1,
                    height=-24,
                    query=True,
                    anti_aliased=True,
                    tag=self.preview_plot,
                )
            )
            dpg.add_button(
                label="Accept",
                callback=self.accept,
            )

    def update_preview(self):
        self.preview_nyquist.clear_plot()
        self.preview_nyquist._plot(
            *self.preview_data.get_nyquist_data(masked=True),
            "Excluded",
            False,
            True,
            themes.nyquist_data,
            -1,
            self.preview_nyquist.x_axis,
            self.preview_nyquist.y_axis,
        )
        self.preview_nyquist._plot(
            *self.preview_data.get_nyquist_data(masked=False),
            "Included",
            False,
            True,
            themes.bode_phase_data,
            -1,
            self.preview_nyquist.x_axis,
            self.preview_nyquist.y_axis,
        )
        self.preview_nyquist.adjust_limits()

    def close(self):
        dpg.hide_item(self.window)
        dpg.delete_item(self.window)
        dpg.delete_item(self.key_handler)

    def accept(self):
        if dpg.is_plot_queried(self.preview_plot):
            sx, ex, sy, ey = dpg.get_plot_query_area(self.preview_plot)
            for i, Z in enumerate(self.data.get_impedance(masked=None)):
                if Z.real >= sx and Z.real <= ex and -Z.imag >= sy and -Z.imag <= ey:
                    self.final_mask[i] = not self.final_mask[i]
        self.callback(self.final_mask)
        self.close()

    def exclude(self):
        self.final_mask = {i: True for i in self.original_mask}
        self.preview_data.set_mask(self.final_mask)
        self.update_preview()

    def include(self):
        self.final_mask = {i: False for i in self.original_mask}
        self.preview_data.set_mask(self.final_mask)
        self.update_preview()

    def update_items(self, sender: int, label: str):
        index: int = self.labels.index(label)
        receiver: int
        items: List[str]
        if sender == self.from_combo:
            receiver = self.to_combo
            items = self.labels[index + 1 :]
        elif sender == self.to_combo:
            receiver = self.from_combo
            items = self.labels[:index]
        dpg.configure_item(receiver, items=items)
        start: int = self.labels.index(dpg.get_value(self.from_combo))
        end: int = self.labels.index(dpg.get_value(self.to_combo))
        assert end > start
        self.final_mask = {}
        for i, state in self.original_mask.items():
            if i >= start and i <= end:
                self.final_mask[i] = not state
            else:
                self.final_mask[i] = state
        self.preview_data.set_mask(self.final_mask)
        self.update_preview()
