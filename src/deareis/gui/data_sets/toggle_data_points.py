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
    Tuple,
)
from numpy import (
    angle,
    array,
    ndarray,
)
import dearpygui.dearpygui as dpg
from deareis.gui.plots import (
    BodeMagnitude,
    BodePhase,
    Nyquist,
    Plot,
)
import deareis.themes as themes
from deareis.data import DataSet
from deareis.utility import (
    align_numbers,
    calculate_window_position_dimensions,
    format_number,
    pad_tab_labels,
)
from deareis.signals import Signal
import deareis.signals as signals
from deareis.tooltips import attach_tooltip
from deareis.state import STATE
from deareis.enums import Action
from deareis.keybindings import (
    Keybinding,
    TemporaryKeybindingHandler,
)


class ToggleDataPoints:
    def __init__(self, data: DataSet, callback: Callable):
        assert type(data) is DataSet
        self.data: DataSet = data
        self.callback: Callable = callback
        self.preview_data: DataSet = DataSet.from_dict(data.to_dict())
        self.original_mask: Dict[int, bool] = data.get_mask()
        self.final_mask: Dict[int, bool] = {
            i: state for i, state in self.original_mask.items()
        }
        self.plot_tabs: Dict[int, Plot] = {}
        self.labels: List[str] = []
        self.create_labels(data)
        self.create_window()
        self.register_keybindings()
        self.update_items(self.from_combo, self.labels[0])
        self.update_items(self.to_combo, self.labels[-1])
        self.update_previews()

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
        # Previous 'from'
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
        callbacks[kb] = lambda: self.cycle_from_item(step=-1)
        # Next 'from'
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
        callbacks[kb] = lambda: self.cycle_from_item(step=1)
        # Previous 'to'
        for kb in STATE.config.keybindings:
            if kb.action is Action.PREVIOUS_SECONDARY_RESULT:
                break
        else:
            kb = Keybinding(
                key=dpg.mvKey_Prior,
                mod_alt=True,
                mod_ctrl=False,
                mod_shift=False,
                action=Action.PREVIOUS_SECONDARY_RESULT,
            )
        callbacks[kb] = lambda: self.cycle_to_item(step=-1)
        # Next 'to'
        for kb in STATE.config.keybindings:
            if kb.action is Action.NEXT_SECONDARY_RESULT:
                break
        else:
            kb = Keybinding(
                key=dpg.mvKey_Next,
                mod_alt=True,
                mod_ctrl=False,
                mod_shift=False,
                action=Action.NEXT_SECONDARY_RESULT,
            )
        callbacks[kb] = lambda: self.cycle_to_item(step=1)
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
        # Select all
        for kb in STATE.config.keybindings:
            if kb.action is Action.SELECT_ALL_PLOT_SERIES:
                break
        else:
            kb = Keybinding(
                key=dpg.mvKey_A,
                mod_alt=True,
                mod_ctrl=False,
                mod_shift=False,
                action=Action.SELECT_ALL_PLOT_SERIES,
            )
        callbacks[kb] = self.include
        # Select all
        for kb in STATE.config.keybindings:
            if kb.action is Action.UNSELECT_ALL_PLOT_SERIES:
                break
        else:
            kb = Keybinding(
                key=dpg.mvKey_A,
                mod_alt=True,
                mod_ctrl=False,
                mod_shift=True,
                action=Action.UNSELECT_ALL_PLOT_SERIES,
            )
        callbacks[kb] = self.exclude
        # Create the handler
        self.keybinding_handler: TemporaryKeybindingHandler = (
            TemporaryKeybindingHandler(callbacks=callbacks)
        )

    def create_labels(self, data: DataSet):
        indices: List[str] = align_numbers(
            list(map(str, range(1, data.get_num_points(masked=None) + 1)))
        )
        freq: List[str] = list(
            map(
                lambda _: _.ljust(9),
                align_numbers(
                    list(
                        map(
                            lambda _: format_number(_, 1, 9),
                            data.get_frequencies(masked=None),
                        )
                    )
                ),
            )
        )
        Z: ndarray = data.get_impedances(masked=None)
        real: List[str] = list(
            map(
                lambda _: _.ljust(10),
                align_numbers(list(map(lambda _: format_number(_, 1, 10), Z.real))),
            )
        )
        imag: List[str] = list(
            map(
                lambda _: _.ljust(10),
                align_numbers(list(map(lambda _: format_number(_, 1, 10), -Z.imag))),
            )
        )
        i: str
        f: str
        re: str
        im: str
        for (i, f, re, im) in zip(
            indices,
            freq,
            real,
            imag,
        ):
            self.labels.append(
                f"{i}: " + f"f = {f} | " + f"Re(Z) = {re} | " + f"-Im(Z) = {im}"
            )

    def create_window(self):
        x: int
        y: int
        w: int
        h: int
        x, y, w, h = calculate_window_position_dimensions()
        self.window: int = dpg.generate_uuid()
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
                self.from_combo: int = dpg.generate_uuid()
                dpg.add_combo(
                    default_value=self.labels[0],
                    width=-1,
                    callback=self.update_items,
                    tag=self.from_combo,
                )
            with dpg.group(horizontal=True):
                dpg.add_text("  To")
                self.to_combo: int = dpg.generate_uuid()
                dpg.add_combo(
                    default_value=self.labels[-1],
                    width=-1,
                    callback=self.update_items,
                    tag=self.to_combo,
                )
            with dpg.group(horizontal=True):
                dpg.add_text("  ?")
                attach_tooltip(
                    """Points can also be chosen by drawing a rectangle on a plot while holding down the middle-mouse button.""".strip()
                )
                dpg.add_button(
                    label="Exclude all",
                    callback=self.exclude,
                )
                dpg.add_button(
                    label="Include all",
                    callback=self.include,
                )
            self.create_plots()
            dpg.add_button(
                label="Accept".ljust(12),
                callback=self.accept,
            )

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
        self.plot_tab_bar: int = dpg.generate_uuid()
        with dpg.tab_bar(tag=self.plot_tab_bar):
            self.create_nyquist_plot(settings)
            self.create_magnitude_plot(settings)
            self.create_phase_plot(settings)
        pad_tab_labels(self.plot_tab_bar)

    def create_nyquist_plot(self, settings: List[dict]):
        tab: int
        with dpg.tab(label="Nyquist") as tab:
            self.nyquist_plot: Nyquist = Nyquist(width=-1, height=-24)
            self.plot_tabs[tab] = self.nyquist_plot
            for kwargs in settings:
                self.nyquist_plot.plot(
                    real=array([]),
                    imaginary=array([]),
                    **kwargs,
                )
            dpg.configure_item(self.nyquist_plot._plot, query=True)

    def create_magnitude_plot(self, settings: List[dict]):
        tab: int
        with dpg.tab(label="Bode - magnitude") as tab:
            self.magnitude_plot: BodeMagnitude = BodeMagnitude(width=-1, height=-24)
            self.plot_tabs[tab] = self.magnitude_plot
            for kwargs in settings:
                self.magnitude_plot.plot(
                    frequency=array([]),
                    magnitude=array([]),
                    **kwargs,
                )
            dpg.configure_item(self.magnitude_plot._plot, query=True)

    def create_phase_plot(self, settings: List[dict]):
        tab: int
        with dpg.tab(label="Bode - phase") as tab:
            self.phase_plot: BodePhase = BodePhase(width=-1, height=-24)
            self.plot_tabs[tab] = self.phase_plot
            for kwargs in settings:
                self.phase_plot.plot(
                    frequency=array([]),
                    phase=array([]),
                    **kwargs,
                )
            dpg.configure_item(self.phase_plot._plot, query=True)

    def update_previews(self):
        self.update_nyquist_plot(self.preview_data)
        self.update_magnitude_plot(self.preview_data)
        self.update_phase_plot(self.preview_data)

    def update_nyquist_plot(self, data: DataSet):
        data: List[Tuple[ndarray, ndarray]] = [
            data.get_nyquist_data(masked=True),
            data.get_nyquist_data(masked=False),
            data.get_nyquist_data(masked=False),
        ]
        for i, (real, imag) in enumerate(data):
            self.nyquist_plot.update(
                index=i,
                real=real,
                imaginary=imag,
            )
        self.nyquist_plot.queue_limits_adjustment()

    def update_magnitude_plot(self, data: DataSet):
        data: List[Tuple[ndarray, ndarray, ndarray]] = [
            data.get_bode_data(masked=True),
            data.get_bode_data(masked=False),
            data.get_bode_data(masked=False),
        ]
        i: int
        freq: ndarray
        mag: ndarray
        for i, (freq, mag, _) in enumerate(data):
            self.magnitude_plot.update(
                index=i,
                frequency=freq,
                magnitude=mag,
            )
        self.magnitude_plot.queue_limits_adjustment()

    def update_phase_plot(self, data: DataSet):
        data: List[Tuple[ndarray, ndarray, ndarray]] = [
            data.get_bode_data(masked=True),
            data.get_bode_data(masked=False),
            data.get_bode_data(masked=False),
        ]
        i: int
        freq: ndarray
        phase: ndarray
        for i, (freq, _, phase) in enumerate(data):
            self.phase_plot.update(
                index=i,
                frequency=freq,
                phase=phase,
            )
        self.phase_plot.queue_limits_adjustment()

    def close(self):
        dpg.hide_item(self.window)
        dpg.delete_item(self.window)
        self.keybinding_handler.delete()
        signals.emit(Signal.UNBLOCK_KEYBINDINGS)

    def accept(self):
        plot: Plot = self.plot_tabs[dpg.get_value(self.plot_tab_bar)]
        if dpg.is_plot_queried(plot._plot):
            sx, ex, sy, ey = dpg.get_plot_query_area(plot._plot)
            if plot == self.nyquist_plot:
                for i, Z in enumerate(self.data.get_impedances(masked=None)):
                    if (
                        Z.real >= sx
                        and Z.real <= ex
                        and -Z.imag >= sy
                        and -Z.imag <= ey
                    ):
                        self.final_mask[i] = not self.final_mask[i]
            elif plot == self.magnitude_plot:
                for i, (f, Z) in enumerate(
                    zip(
                        self.data.get_frequencies(masked=None),
                        self.data.get_impedances(masked=None),
                    )
                ):
                    if f >= sx and f <= ex and abs(Z) >= sy and abs(Z) <= ey:
                        self.final_mask[i] = not self.final_mask[i]
            elif plot == self.phase_plot:
                for i, (f, Z) in enumerate(
                    zip(
                        self.data.get_frequencies(masked=None),
                        self.data.get_impedances(masked=None),
                    )
                ):
                    if (
                        f >= sx
                        and f <= ex
                        and -angle(Z, deg=True) >= sy
                        and -angle(Z, deg=True) <= ey
                    ):
                        self.final_mask[i] = not self.final_mask[i]
        self.callback(self.final_mask)
        self.close()

    def exclude(self):
        self.final_mask = {i: True for i in self.original_mask}
        self.preview_data.set_mask(self.final_mask)
        self.update_previews()

    def include(self):
        self.final_mask = {i: False for i in self.original_mask}
        self.preview_data.set_mask(self.final_mask)
        self.update_previews()

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
        self.update_previews()

    def cycle_from_item(self, step: int):
        items: List[str] = dpg.get_item_configuration(self.from_combo)["items"]
        index: int = items.index(dpg.get_value(self.from_combo)) + step
        dpg.set_value(self.from_combo, items[index % len(items)])
        self.update_items(self.from_combo, items[index % len(items)])

    def cycle_to_item(self, step: int):
        items: List[str] = dpg.get_item_configuration(self.to_combo)["items"]
        index: int = items.index(dpg.get_value(self.to_combo)) + step
        dpg.set_value(self.to_combo, items[index % len(items)])
        self.update_items(self.to_combo, items[index % len(items)])

    def cycle_plot_tab(self, step: int):
        tabs: List[int] = dpg.get_item_children(self.plot_tab_bar, slot=1)
        index: int = tabs.index(dpg.get_value(self.plot_tab_bar)) + step
        dpg.set_value(self.plot_tab_bar, tabs[index % len(tabs)])
