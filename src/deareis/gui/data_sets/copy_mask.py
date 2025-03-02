# DearEIS is licensed under the GPLv3 or later (https://www.gnu.org/licenses/gpl-3.0.html).
# Copyright 2025 DearEIS developers
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
    Tuple,
)
from numpy import (
    array,
    complex128,
    ndarray,
)
import dearpygui.dearpygui as dpg
from deareis.gui.plots import (
    BodeMagnitude,
    BodePhase,
    Nyquist,
)
import deareis.themes as themes
from deareis.utility import (
    calculate_window_position_dimensions,
    pad_tab_labels,
)
from deareis.signals import Signal
import deareis.signals as signals
from deareis.data import DataSet
from deareis.tooltips import attach_tooltip
import deareis.tooltips as tooltips
from deareis.state import STATE
from deareis.enums import Action
from deareis.keybindings import (
    Keybinding,
    TemporaryKeybindingHandler,
)
from deareis.typing.helpers import Tag


class CopyMask:
    def __init__(
        self,
        data: DataSet,
        data_sets: List[DataSet],
        callback: Callable,
        admittance: bool,
    ):
        assert type(data) is DataSet, data
        assert type(data_sets) is list and all(
            map(lambda _: type(_) is DataSet, data_sets)
        ), data_sets
        self.data: DataSet = data
        self.preview_data: DataSet = DataSet.from_dict(data.to_dict())
        self.data_sets: List[DataSet] = [
            _ for _ in sorted(data_sets, key=lambda _: _.get_label()) if _ != data
        ]
        self.labels: List[str] = list(map(lambda _: _.get_label(), self.data_sets))
        self.callback: Callable = callback
        self.create_window(admittance=admittance)
        self.register_keybindings()
        self.select_source(self.labels[0])
        self.nyquist_plot.queue_limits_adjustment()
        self.magnitude_plot.queue_limits_adjustment()
        self.phase_plot.queue_limits_adjustment()
        self.toggle_plot_admittance(admittance)

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

        # Accept
        for kb in STATE.config.keybindings:
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
        callbacks[kb] = self.accept

        # Previous source
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
        callbacks[kb] = lambda: self.cycle_source(-1)

        # Next source
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
        callbacks[kb] = lambda: self.cycle_source(1)

        # Previous plot tab
        for kb in STATE.config.keybindings:
            if kb.action is Action.PREVIOUS_PLOT_TAB:
                break
        else:
            kb = Keybinding(
                key=dpg.mvKey_Prior,
                mod_alt=True,
                mod_ctrl=False,
                mod_shift=True,
                action=Action.PREVIOUS_PLOT_TAB,
            )
        callbacks[kb] = lambda: self.cycle_plot_tab(step=-1)

        # Next plot tab
        for kb in STATE.config.keybindings:
            if kb.action is Action.NEXT_PLOT_TAB:
                break
        else:
            kb = Keybinding(
                key=dpg.mvKey_Next,
                mod_alt=True,
                mod_ctrl=False,
                mod_shift=True,
                action=Action.NEXT_PLOT_TAB,
            )
        callbacks[kb] = lambda: self.cycle_plot_tab(step=1)

        # Create the handler
        self.keybinding_handler: TemporaryKeybindingHandler = (
            TemporaryKeybindingHandler(callbacks=callbacks)
        )

    def create_window(self, admittance: bool):
        x: int
        y: int
        w: int
        h: int
        x, y, w, h = calculate_window_position_dimensions()

        self.window: Tag = dpg.generate_uuid()
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
                attach_tooltip(tooltips.data_sets.copy_mask_source)

                self.combo: Tag = dpg.generate_uuid()
                dpg.add_combo(
                    items=self.labels,
                    default_value=self.labels[0],
                    width=-1,
                    tag=self.combo,
                    callback=lambda s, a, u: self.select_source(a),
                )

            self.create_plots()
            
            with dpg.group(horizontal=True):
                dpg.add_button(
                    label="Accept".ljust(12),
                    callback=self.accept,
                )

                self.admittance_checkbox: Tag = dpg.generate_uuid()
                dpg.add_checkbox(
                    label="Y",
                    default_value=admittance,
                    callback=lambda s, a, u: self.toggle_plot_admittance(a),
                    tag=self.admittance_checkbox,
                )
                attach_tooltip(tooltips.general.plot_admittance)

    def toggle_plot_admittance(self, admittance: bool):
        self.nyquist_plot.set_admittance(admittance)
        self.magnitude_plot.set_admittance(admittance)
        self.phase_plot.set_admittance(admittance)

    def create_plots(self):
        settings: List[dict] = [
            {
                "label": "Excluded",
                "theme": themes.nyquist.data,
            },
            {
                "label": "Included",
                "theme": themes.bode.phase_data,
                "show_label": False,
            },
            {
                "label": "Included",
                "line": True,
                "theme": themes.bode.phase_data,
            },
        ]
        with dpg.child_window(height=-24, border=False):
            self.plot_tab_bar: Tag = dpg.generate_uuid()
            with dpg.tab_bar(tag=self.plot_tab_bar):
                self.create_nyquist_plot(settings)
                self.create_magnitude_plot(settings)
                self.create_phase_plot(settings)

            pad_tab_labels(self.plot_tab_bar)

    def create_nyquist_plot(self, settings: List[dict]):
        with dpg.tab(label="Nyquist"):
            self.nyquist_plot: Nyquist = Nyquist(width=-1, height=-1)
            for kwargs in settings:
                self.nyquist_plot.plot(
                    impedances=array([], dtype=complex128),
                    **kwargs,
                )

    def create_magnitude_plot(self, settings: List[dict]):
        with dpg.tab(label="Bode - magnitude"):
            self.magnitude_plot: BodeMagnitude = BodeMagnitude(width=-1, height=-1)
            for kwargs in settings:
                self.magnitude_plot.plot(
                    frequencies=array([]),
                    impedances=array([], dtype=complex128),
                    **kwargs,
                )

    def create_phase_plot(self, settings: List[dict]):
        with dpg.tab(label="Bode - phase"):
            self.phase_plot: BodePhase = BodePhase(width=-1, height=-1)
            for kwargs in settings:
                self.phase_plot.plot(
                    frequencies=array([]),
                    impedances=array([], dtype=complex128),
                    **kwargs,
                )

    def cycle_source(self, step: int):
        assert type(step) is int, step
        index: int = self.labels.index(dpg.get_value(self.combo)) + step
        label: str = self.labels[index % len(self.labels)]
        dpg.set_value(self.combo, label)
        self.select_source(label)

    def select_source(self, label: str):
        assert type(label) is str, label
        self.preview_data.set_mask(self.data.get_mask())
        self.preview_data.set_mask(self.data_sets[self.labels.index(label)].get_mask())
        self.update_previews()

    def update_previews(self):
        self.update_nyquist_plot(self.preview_data)
        self.update_magnitude_plot(self.preview_data)
        self.update_phase_plot(self.preview_data)

    def update_nyquist_plot(self, data: DataSet):
        data: List[ndarray] = [
            data.get_impedances(masked=True),
            data.get_impedances(masked=False),
            data.get_impedances(masked=False),
        ]

        i: int
        Z: ndarray
        for i, Z in enumerate(data):
            self.nyquist_plot.update(
                index=i,
                impedances=Z,
            )

    def update_magnitude_plot(self, data: DataSet):
        data: List[Tuple[ndarray, ndarray]] = [
            (
                data.get_frequencies(masked=True),
                data.get_impedances(masked=True),
            ),
            (
                data.get_frequencies(masked=False),
                data.get_impedances(masked=False),
            ),
            (
                data.get_frequencies(masked=False),
                data.get_impedances(masked=False),
            ),
        ]

        i: int
        freq: ndarray
        Z: ndarray
        for i, (freq, Z) in enumerate(data):
            self.magnitude_plot.update(
                index=i,
                frequencies=freq,
                impedances=Z,
            )

    def update_phase_plot(self, data: DataSet):
        data: List[Tuple[ndarray, ndarray]] = [
            (
                data.get_frequencies(masked=True),
                data.get_impedances(masked=True),
            ),
            (
                data.get_frequencies(masked=False),
                data.get_impedances(masked=False),
            ),
            (
                data.get_frequencies(masked=False),
                data.get_impedances(masked=False),
            ),
        ]

        i: int
        freq: ndarray
        Z: ndarray
        for i, (freq, Z) in enumerate(data):
            self.phase_plot.update(
                index=i,
                frequencies=freq,
                impedances=Z,
            )

    def close(self):
        dpg.hide_item(self.window)
        dpg.delete_item(self.window)
        self.keybinding_handler.delete()
        signals.emit(Signal.UNBLOCK_KEYBINDINGS)

    def accept(self):
        self.callback(
            self.data_sets[self.labels.index(dpg.get_value(self.combo))].get_mask(),
        )
        self.close()

    def cycle_plot_tab(self, step: int):
        tabs: List[Tag] = dpg.get_item_children(self.plot_tab_bar, slot=1)
        index: int = tabs.index(dpg.get_value(self.plot_tab_bar)) + step
        dpg.set_value(self.plot_tab_bar, tabs[index % len(tabs)])
