# DearEIS is licensed under the GPLv3 or later (https://www.gnu.org/licenses/gpl-3.0.html).
# Copyright 2023 DearEIS developers
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

from typing import (
    Callable,
    Dict,
    List,
    Optional,
)
import dearpygui.dearpygui as dpg
from numpy import (
    array,
    float64,
    log10 as log,
)
from numpy.typing import NDArray
from pyimpspec.analysis.zhit.weights import (
    _generate_weights,
    _initialize_window_functions,
)
from deareis.data import (
    DataSet,
    ZHITSettings,
)
from deareis.enums import (
    ZHITWindow,
    zhit_window_to_label,
    zhit_window_to_value,
)
from deareis.gui.plots.zhit_weights import ZHITWeights
from deareis.utility import calculate_window_position_dimensions
from deareis.signals import Signal
import deareis.signals as signals
import deareis.themes as themes
import deareis.tooltips as tooltips
from deareis.tooltips import attach_tooltip
from deareis.state import STATE
from deareis.enums import Action
from deareis.keybindings import (
    Keybinding,
    TemporaryKeybindingHandler,
)

_initialize_window_functions()


class WeightsPreview:
    def __init__(self, data: DataSet, settings: ZHITSettings):
        assert isinstance(data, DataSet)
        assert isinstance(settings, ZHITSettings)
        self.data: DataSet = data
        self.settings: ZHITSettings = settings
        self.weights: Dict[ZHITWindow, NDArray[float64]] = {}
        self.checkboxes: Dict[ZHITWindow, int] = {}
        self.previous_choice: Optional[ZHITWindow] = None
        log_f: NDArray[float64] = log(data.get_frequencies())
        enum: ZHITWindow
        value: str
        for enum, value in zhit_window_to_value.items():
            if enum == ZHITWindow.AUTO:
                continue
            self.weights[enum] = _generate_weights(
                log_f=log_f,
                window=value,
                center=settings.window_center,
                width=settings.window_width,
            )
        self.create_window()
        self.register_keybindings()
        self.update_preview(
            settings.window if settings.window != ZHITWindow.AUTO else ZHITWindow.BOXCAR
        )

    def register_keybindings(self):
        callbacks: Dict[Keybinding, Callable] = {}
        # Cancel
        kb: Keybinding = Keybinding(
            key=dpg.mvKey_Escape,
            mod_alt=False,
            mod_ctrl=False,
            mod_shift=False,
            action=Action.CANCEL,
        )
        callbacks[kb] = self.close
        # Previous function
        for kb in STATE.config.keybindings:
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
        callbacks[kb] = lambda: self.cycle(step=-1)
        # Next function
        for kb in STATE.config.keybindings:
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
        callbacks[kb] = lambda: self.cycle(step=1)
        # Create the handler
        self.keybinding_handler: TemporaryKeybindingHandler = (
            TemporaryKeybindingHandler(callbacks=callbacks)
        )

    def create_window(self):
        x: int
        y: int
        w: int
        h: int
        x, y, w, h = calculate_window_position_dimensions()
        self.window: int = dpg.generate_uuid()
        with dpg.window(
            label="Preview weights",
            modal=True,
            pos=(x, y),
            width=w,
            height=h,
            tag=self.window,
            on_close=self.close,
        ):
            with dpg.group(horizontal=True):
                self.create_table()
                self.create_plot()

    def create_table(self):
        self.table: int = dpg.generate_uuid()
        with dpg.table(
            borders_outerV=True,
            borders_outerH=True,
            borders_innerV=True,
            borders_innerH=True,
            scrollY=True,
            freeze_rows=1,
            width=200,
            tag=self.table,
        ):
            dpg.add_table_column(
                label="?",
                width_fixed=True,
            )
            attach_tooltip(tooltips.zhit.select_window_function)
            dpg.add_table_column(
                label="Name",
            )
        for enum in self.weights:
            with dpg.table_row(parent=self.table):
                self.checkboxes[enum] = dpg.add_checkbox(
                    default_value=(
                        enum == self.settings.window
                        or (
                            self.settings.window == ZHITWindow.AUTO
                            and enum == ZHITWindow.BOXCAR
                        )
                    ),
                    callback=lambda s, a, u: self.update_preview(
                        window=u,
                        flag=a,
                    ),
                    user_data=enum,
                )
                dpg.add_text(zhit_window_to_label[enum])
                attach_tooltip(zhit_window_to_label[enum])

    def create_plot(self):
        self.plot: ZHITWeights = ZHITWeights(width=-1, height=-1)
        f, mag, _ = self.data.get_bode_data()
        self.plot.plot(
            frequency=f,
            magnitude=mag,
            weight=array([]),
            labels=("Mod(Z)", ""),
            themes=(themes.zhit.magnitude, themes.zhit.weight),
            show_labels=True,
        )
        self.plot.plot(
            frequency=array([]),
            magnitude=array([]),
            weight=array([]),
            labels=("", "Weight"),
            themes=(themes.zhit.magnitude, themes.zhit.weight),
            show_labels=True,
        )
        self.plot.plot_window(
            center=self.settings.window_center,
            width=self.settings.window_width,
            label="Window",
            theme=themes.zhit.window,
        )

    def cycle(self, index: Optional[int] = None, step: Optional[int] = None):
        i: int
        checkbox: int
        if index is not None:
            i = index
        elif step is not None:
            for i, checkbox in enumerate(self.checkboxes.values()):
                if dpg.get_value(checkbox) is True:
                    break
            else:
                return
            i += step
        else:
            return
        enums: List[ZHITWindow] = list(self.checkboxes.keys())
        enum: ZHITWindow = enums[i % len(enums)]
        dpg.set_value(self.checkboxes[enum], True)
        self.update_preview(enum, flag=True)

    def update_preview(self, window: ZHITWindow, flag: bool = True):
        enum: ZHITWindow
        checkbox: int
        if self.previous_choice is None:
            self.previous_choice = window
        elif flag is True:
            for enum, checkbox in self.checkboxes.items():
                if enum != window and dpg.get_value(checkbox) is True:
                    self.previous_choice = enum
                    dpg.set_value(checkbox, window == enum)
        elif flag is False:
            window = self.previous_choice
            dpg.set_value(self.checkboxes[window], True)
        self.plot.update(
            1,
            frequency=self.data.get_frequencies(),
            magnitude=array([]),
            weight=self.weights[window],
        )
        self.plot.queue_limits_adjustment()

    def close(self):
        dpg.hide_item(self.window)
        dpg.delete_item(self.window)
        self.keybinding_handler.delete()
        signals.emit(Signal.UNBLOCK_KEYBINDINGS)
