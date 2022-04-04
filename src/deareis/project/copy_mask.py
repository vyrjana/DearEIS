# Copyright 2022 DearEIS developers
# DearEIS is licensed under the GPLv3 or later (https://www.gnu.org/licenses/gpl-3.0.html).
# The licenses of DearEIS' dependencies and/or sources of portions of code are included in
# the LICENSES folder.

from pyimpspec import DataSet
from typing import Callable, List
import dearpygui.dearpygui as dpg
from deareis.plot import NyquistPlot
import deareis.themes as themes
from deareis.utility import window_pos_dims


# TODO: Add resize handler to check when the viewport is resized


class CopyMask:
    def __init__(self, data: DataSet, datasets: List[DataSet], callback: Callable):
        assert type(data) is DataSet
        assert type(datasets) is list and all(
            map(lambda _: type(_) is DataSet, datasets)
        )
        assert callback is not None
        self.data: DataSet = data
        self.preview_data: DataSet = DataSet.from_dict(data.to_dict())
        self.datasets: List[DataSet] = [
            _ for _ in sorted(datasets, key=lambda _: _.get_label()) if _ != data
        ]
        self.labels: List[str] = list(map(lambda _: _.get_label(), self.datasets))
        self.callback: Callable = callback
        self.window: int = dpg.generate_uuid()
        self.combo: int = dpg.generate_uuid()
        self.nyquist_plot: NyquistPlot = None  # type: ignore
        self.key_handler: int = dpg.generate_uuid()
        self._assemble()
        self._setup_keybindings()
        self.select_source(self.labels[0])

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
            label="Copy mask",
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
                dpg.add_text("Source")
                dpg.add_combo(
                    items=self.labels,
                    default_value=self.labels[0],
                    width=-1,
                    tag=self.combo,
                    callback=lambda s, a, u: self.select_source(a),
                )
            self.nyquist_plot = NyquistPlot(
                dpg.add_plot(
                    equal_aspects=True,
                    width=-1,
                    height=-24,
                    anti_aliased=True,
                )
            )
            dpg.add_button(label="Accept", callback=self.accept)

    def select_source(self, label: str):
        assert type(label) is str
        self.preview_data.set_mask(self.data.get_mask())
        self.preview_data.set_mask(self.datasets[self.labels.index(label)].get_mask())
        self.update_preview()

    def update_preview(self):
        self.nyquist_plot.clear_plot()
        self.nyquist_plot._plot(
            *self.preview_data.get_nyquist_data(masked=True),
            "Excluded",
            False,
            True,
            themes.nyquist_data,
            -1,
            self.nyquist_plot.x_axis,
            self.nyquist_plot.y_axis,
        )
        self.nyquist_plot._plot(
            *self.preview_data.get_nyquist_data(masked=False),
            "Included",
            False,
            True,
            themes.bode_phase_data,
            -1,
            self.nyquist_plot.x_axis,
            self.nyquist_plot.y_axis,
        )
        self.nyquist_plot.adjust_limits()

    def close(self):
        dpg.hide_item(self.window)
        dpg.delete_item(self.window)
        dpg.delete_item(self.key_handler)

    def accept(self):
        self.callback(
            self.datasets[self.labels.index(dpg.get_value(self.combo))].get_mask(),
        )
        self.close()
