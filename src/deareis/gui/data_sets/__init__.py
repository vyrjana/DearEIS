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

from typing import (
    Callable,
    Dict,
    List,
    Optional,
)
from numpy import (
    angle,
    array,
    ndarray,
)
import dearpygui.dearpygui as dpg
from deareis.signals import Signal
import deareis.signals as signals
from deareis.gui.plots import Bode, Nyquist
from deareis.utility import (
    align_numbers,
    format_number,
)
from deareis.tooltips import (
    attach_tooltip,
    update_tooltip,
)
import deareis.tooltips as tooltips
import deareis.themes as themes
from deareis.data import DataSet


class DataTable:
    def __init__(self):
        self._table: int = dpg.generate_uuid()
        with dpg.table(
            borders_outerV=True,
            borders_outerH=True,
            borders_innerV=True,
            borders_innerH=True,
            scrollY=True,
            freeze_rows=1,
            tag=self._table,
        ):
            dpg.add_table_column(
                label="Mask",
                width_fixed=True,
            )
            attach_tooltip(tooltips.data_sets.mask)
            dpg.add_table_column(
                label="Index",
                width_fixed=True,
            )
            dpg.add_table_column(
                label="f (Hz)",
            )
            attach_tooltip(tooltips.data_sets.frequency)
            dpg.add_table_column(
                label="Z' (ohm)",
            )
            attach_tooltip(tooltips.data_sets.real)
            dpg.add_table_column(
                label='-Z" (ohm)',
            )
            attach_tooltip(tooltips.data_sets.imaginary)
            dpg.add_table_column(
                label="|Z| (ohm)",
            )
            attach_tooltip(tooltips.data_sets.magnitude)
            dpg.add_table_column(
                label="-phi (°)",
            )
            attach_tooltip(tooltips.data_sets.phase)

    def clear(self):
        dpg.delete_item(self._table, children_only=True, slot=1)

    def populate(self, data: DataSet):
        assert type(data) is DataSet, data
        num_rows: int = data.get_num_points(masked=None)
        if num_rows == 0:
            self.clear()
            return
        rows: List[int] = dpg.get_item_children(self._table, slot=1)
        if len(rows) > num_rows:
            while len(rows) > num_rows:
                dpg.delete_item(rows.pop())
            return
        i: int
        for i in range(0, num_rows - len(rows)):
            with dpg.table_row(parent=self._table):
                dpg.add_checkbox(
                    default_value=False,
                    callback=lambda s, a, u: signals.emit(
                        Signal.TOGGLE_DATA_POINT,
                        state=a,
                        index=u[0],
                        data=u[1],
                    ),
                    user_data=(
                        i,
                        data,
                    ),
                )
                dpg.add_text("")
                dpg.add_text("")
                attach_tooltip("")
                dpg.add_text("")
                attach_tooltip("")
                dpg.add_text("")
                attach_tooltip("")
                dpg.add_text("")
                attach_tooltip("")
                dpg.add_text("")
                attach_tooltip("")

    def update(self, data: DataSet):
        assert type(data) is DataSet, data
        rows: List[int] = dpg.get_item_children(self._table, slot=1)
        assert len(rows) == data.get_num_points(masked=None)
        mask: Dict[int, bool] = data.get_mask()
        indices: List[str] = list(
            map(lambda _: str(_ + 1), range(0, data.get_num_points(masked=None)))
        )
        frequencies: ndarray = data.get_frequency(masked=None)
        freqs: List[str] = list(
            map(
                lambda _: format_number(_, significants=4),
                frequencies,
            )
        )
        Z: ndarray = data.get_impedance(masked=None)
        reals: List[str] = list(
            map(
                lambda _: format_number(
                    _.real,
                    significants=4,
                ),
                Z,
            )
        )
        imags: List[str] = list(
            map(lambda _: format_number(-_.imag, significants=4), Z)
        )
        mags: List[str] = list(
            map(
                lambda _: format_number(
                    abs(_),
                    significants=4,
                ),
                Z,
            )
        )
        phis: List[str] = list(
            map(
                lambda _: format_number(
                    -angle(_, deg=True),  # type: ignore
                    significants=4,
                    exponent=False,
                ),
                Z,
            )
        )
        indices = align_numbers(indices)
        freqs = align_numbers(freqs)
        reals = align_numbers(reals)
        imags = align_numbers(imags)
        mags = align_numbers(mags)
        phis = align_numbers(phis)
        fmt: str = "{:.6E}"
        i: int
        row: int
        for i, row in enumerate(rows):
            cells: List[int] = dpg.get_item_children(row, slot=1)
            # Mask
            dpg.configure_item(
                cells[0],
                default_value=mask.get(i, False),
                user_data=(
                    i,
                    data,
                ),
            )
            # Index
            dpg.configure_item(
                cells[1],
                default_value=indices[i],
            )
            # Frequency
            dpg.configure_item(
                cells[2],
                default_value=freqs[i],
            )
            update_tooltip(dpg.get_item_user_data(cells[3]), fmt.format(frequencies[i]))
            # Z, real
            dpg.configure_item(
                cells[4],
                default_value=reals[i],
            )
            update_tooltip(dpg.get_item_user_data(cells[5]), fmt.format(Z[i].real))
            # -Z, imaginary
            dpg.configure_item(
                cells[6],
                default_value=imags[i],
            )
            update_tooltip(dpg.get_item_user_data(cells[7]), fmt.format(-Z[i].imag))
            # Z, magnitude
            dpg.configure_item(
                cells[8],
                default_value=mags[i],
            )
            update_tooltip(dpg.get_item_user_data(cells[9]), fmt.format(abs(Z[i])))
            # Phase shift
            dpg.configure_item(
                cells[10],
                default_value=phis[i],
            )
            update_tooltip(
                dpg.get_item_user_data(cells[11]), fmt.format(-angle(Z[i], deg=True))
            )


class DataSetsTab:
    def __init__(self):
        self.queued_update: Optional[Callable] = None
        self.tab: int = dpg.generate_uuid()
        with dpg.tab(label="Data sets", tag=self.tab):
            with dpg.child_window(border=False, width=-1, height=-1):
                with dpg.group(horizontal=True):
                    self.table_window: int = dpg.generate_uuid()
                    self.table_width: int = 600
                    with dpg.child_window(
                        border=False,
                        width=self.table_width,
                        tag=self.table_window,
                        show=True,
                    ):
                        label_pad: int = 8
                        with dpg.child_window(border=True, height=82, width=-2):
                            with dpg.group(horizontal=True):
                                with dpg.child_window(border=False, width=-72):
                                    # TODO: Split into combo class?
                                    self.data_sets_combo: int = dpg.generate_uuid()
                                    with dpg.group(horizontal=True):
                                        self.visibility_item: int = dpg.generate_uuid()
                                        dpg.add_text(
                                            "Data set".rjust(label_pad),
                                            tag=self.visibility_item,
                                        )
                                        dpg.add_combo(
                                            callback=lambda s, a, u: signals.emit(
                                                Signal.SELECT_DATA_SET,
                                                data=u.get(a),
                                            ),
                                            user_data={},
                                            width=-1,
                                            tag=self.data_sets_combo,
                                        )
                                    self.label_input: int = dpg.generate_uuid()
                                    with dpg.group(horizontal=True):
                                        dpg.add_text("Label".rjust(label_pad))
                                        dpg.add_input_text(
                                            on_enter=True,
                                            callback=lambda s, a, u: signals.emit(
                                                Signal.RENAME_DATA_SET,
                                                label=a,
                                                data=u,
                                            ),
                                            width=-1,
                                            tag=self.label_input,
                                        )
                                    self.path_input: int = dpg.generate_uuid()
                                    with dpg.group(horizontal=True):
                                        dpg.add_text("Path".rjust(label_pad))
                                        dpg.add_input_text(
                                            on_enter=True,
                                            callback=lambda s, a, u: signals.emit(
                                                Signal.MODIFY_DATA_SET_PATH,
                                                path=a,
                                                data=u,
                                            ),
                                            width=-1,
                                            tag=self.path_input,
                                        )
                                with dpg.child_window(border=False, width=-1):
                                    self.load_button: int = dpg.generate_uuid()
                                    dpg.add_button(
                                        label="Load",
                                        callback=lambda s, a, u: signals.emit(
                                            Signal.SELECT_DATA_SET_FILES,
                                        ),
                                        width=-1,
                                        tag=self.load_button,
                                    )
                                    attach_tooltip(tooltips.data_sets.load)
                                    self.delete_button: int = dpg.generate_uuid()
                                    dpg.add_button(
                                        label="Delete",
                                        callback=lambda s, a, u: signals.emit(
                                            Signal.DELETE_DATA_SET,
                                            data=u,
                                        ),
                                        width=-1,
                                        tag=self.delete_button,
                                    )
                                    attach_tooltip(tooltips.data_sets.delete)
                                    self.average_button: int = dpg.generate_uuid()
                                    dpg.add_button(
                                        label="Average",
                                        callback=lambda s, a, u: signals.emit(
                                            Signal.SELECT_DATA_SETS_TO_AVERAGE,
                                        ),
                                        width=-1,
                                        tag=self.average_button,
                                    )
                                    attach_tooltip(tooltips.data_sets.average)
                        with dpg.child_window(
                            border=False, width=-2, height=-40, show=True
                        ):
                            self.data_table = DataTable()
                        with dpg.child_window(border=True, width=-2):
                            with dpg.group(horizontal=True):
                                self.toggle_points_button: int = dpg.generate_uuid()
                                dpg.add_button(
                                    label="Toggle points",
                                    tag=self.toggle_points_button,
                                    callback=lambda s, a, u: signals.emit(
                                        Signal.SELECT_DATA_POINTS_TO_TOGGLE,
                                        data=u,
                                    ),
                                )
                                attach_tooltip(tooltips.data_sets.toggle)
                                self.copy_mask_button: int = dpg.generate_uuid()
                                dpg.add_button(
                                    label="Copy mask",
                                    tag=self.copy_mask_button,
                                    callback=lambda s, a, u: signals.emit(
                                        Signal.SELECT_DATA_SET_MASK_TO_COPY,
                                        data=u,
                                    ),
                                )
                                attach_tooltip(tooltips.data_sets.copy)
                                self.subtract_impedance_button: int = (
                                    dpg.generate_uuid()
                                )
                                dpg.add_button(
                                    label="Subtract",
                                    tag=self.subtract_impedance_button,
                                    callback=lambda s, a, u: signals.emit(
                                        Signal.SELECT_IMPEDANCE_TO_SUBTRACT,
                                        data=u,
                                    ),
                                )
                                attach_tooltip(tooltips.data_sets.subtract)
                                self.enlarge_nyquist_button: int = dpg.generate_uuid()
                                self.adjust_nyquist_limits_checkbox: int = (
                                    dpg.generate_uuid()
                                )
                                dpg.add_button(
                                    label="Enlarge Nyquist",
                                    callback=self.show_enlarged_nyquist,
                                    tag=self.enlarge_nyquist_button,
                                )
                                dpg.add_checkbox(
                                    default_value=True,
                                    tag=self.adjust_nyquist_limits_checkbox,
                                )
                                attach_tooltip(tooltips.general.adjust_nyquist_limits)
                                self.enlarge_bode_button: int = dpg.generate_uuid()
                                self.adjust_bode_limits_checkbox: int = (
                                    dpg.generate_uuid()
                                )
                                dpg.add_button(
                                    label="Enlarge Bode",
                                    callback=self.show_enlarged_bode,
                                    tag=self.enlarge_bode_button,
                                )
                                dpg.add_checkbox(
                                    default_value=True,
                                    tag=self.adjust_bode_limits_checkbox,
                                )
                                attach_tooltip(tooltips.general.adjust_bode_limits)
                    self.plot_window: int = dpg.generate_uuid()
                    self.plot_width: int = 400
                    with dpg.child_window(
                        border=False,
                        width=-1,
                        no_scrollbar=True,
                        tag=self.plot_window,
                        show=True,
                    ):
                        self.nyquist_plot: Nyquist = Nyquist()
                        self.nyquist_plot.plot(
                            real=array([]),
                            imaginary=array([]),
                            label="Data",
                            line=False,
                            theme=themes.nyquist.data,
                        )
                        self.nyquist_plot.plot(
                            real=array([]),
                            imaginary=array([]),
                            label="Data",
                            line=True,
                            theme=themes.nyquist.data,
                            show_label=False,
                        )
                        self.bode_plot: Bode = Bode()
                        self.bode_plot.plot(
                            frequency=array([]),
                            magnitude=array([]),
                            phase=array([]),
                            labels=(
                                "|Z|",
                                "phi",
                            ),
                            line=False,
                            themes=(
                                themes.bode.magnitude_data,
                                themes.bode.phase_data,
                            ),
                        )
                        self.bode_plot.plot(
                            frequency=array([]),
                            magnitude=array([]),
                            phase=array([]),
                            labels=(
                                "|Z|",
                                "phi",
                            ),
                            line=True,
                            themes=(
                                themes.bode.magnitude_data,
                                themes.bode.phase_data,
                            ),
                            show_labels=False,
                        )

    def is_visible(self) -> bool:
        return dpg.is_item_visible(self.visibility_item)

    def resize(self, width: int, height: int):
        assert type(width) is int and width > 0, width
        assert type(height) is int and height > 0, height
        if not self.is_visible():
            return
        if width < (self.table_width + self.plot_width):
            if dpg.is_item_shown(self.plot_window):
                dpg.hide_item(self.plot_window)
                dpg.set_item_width(self.table_window, -1)
                dpg.set_item_label(self.enlarge_nyquist_button, "Show Nyquist")
                dpg.set_item_label(self.enlarge_bode_button, "Show Bode")
        else:
            if not dpg.is_item_shown(self.plot_window):
                dpg.show_item(self.plot_window)
                dpg.set_item_width(self.table_window, self.table_width)
                dpg.split_frame()
                dpg.set_item_label(self.enlarge_nyquist_button, "Enlarge Nyquist")
                dpg.set_item_label(self.enlarge_bode_button, "Enlarge Bode")
        if not dpg.is_item_shown(self.plot_window):
            return
        width, height = dpg.get_item_rect_size(self.plot_window)
        item: int
        for item in dpg.get_item_children(self.plot_window, slot=1):
            dpg.set_item_height(item, height / 2)

    def clear(self):
        dpg.set_value(self.data_sets_combo, "")
        dpg.set_value(self.label_input, "")
        dpg.set_value(self.path_input, "")
        dpg.set_item_user_data(self.delete_button, None)
        dpg.set_item_user_data(self.toggle_points_button, None)
        dpg.set_item_user_data(self.copy_mask_button, None)
        dpg.set_item_user_data(self.subtract_impedance_button, None)
        self.data_table.clear()
        self.nyquist_plot.clear(delete=False)
        self.bode_plot.clear(delete=False)

    def populate_data_sets(self, labels: List[str], lookup: Dict[str, DataSet]):
        assert type(labels) is list, labels
        assert type(lookup) is dict, lookup
        label: str = dpg.get_value(self.data_sets_combo) or ""
        if labels and label not in labels:
            label = labels[0]
        dpg.configure_item(
            self.data_sets_combo,
            items=labels,
            default_value=label,
            user_data=lookup,
        )

    def get_next_data_set(self) -> Optional[DataSet]:
        lookup: Dict[str, DataSet] = dpg.get_item_user_data(self.data_sets_combo)
        if not lookup:
            return None
        labels: List[str] = list(lookup.keys())
        index: int = labels.index(dpg.get_value(self.data_sets_combo)) + 1
        return lookup[labels[index % len(labels)]]

    def get_previous_data_set(self) -> Optional[DataSet]:
        lookup: Dict[str, DataSet] = dpg.get_item_user_data(self.data_sets_combo)
        if not lookup:
            return None
        labels: List[str] = list(lookup.keys())
        index: int = labels.index(dpg.get_value(self.data_sets_combo)) - 1
        return lookup[labels[index % len(labels)]]

    def select_data_set(self, data: Optional[DataSet]):
        assert type(data) is DataSet or data is None, data
        if not self.is_visible():
            self.queued_update = lambda: self.select_data_set(data)
            return
        self.queued_update = None
        if data is None:
            self.clear()
            return
        self.data_table.populate(data)
        self.data_table.update(data)
        dpg.set_value(self.data_sets_combo, data.get_label())
        dpg.configure_item(
            self.label_input,
            default_value=data.get_label(),
            user_data=data,
        )
        dpg.configure_item(
            self.path_input,
            default_value=data.get_path(),
            user_data=data,
        )
        # TODO: Could this be simplified so that data is stored in one place?
        dpg.set_item_user_data(self.delete_button, data)
        dpg.set_item_user_data(self.toggle_points_button, data)
        dpg.set_item_user_data(self.copy_mask_button, data)
        dpg.set_item_user_data(self.subtract_impedance_button, data)
        real: ndarray
        imag: ndarray
        real, imag = data.get_nyquist_data()
        self.nyquist_plot.update(
            index=0,
            real=real,
            imaginary=imag,
        )
        self.nyquist_plot.update(
            index=1,
            real=real,
            imaginary=imag,
        )
        freq: ndarray
        mag: ndarray
        phase: ndarray
        freq, mag, phase = data.get_bode_data()
        self.bode_plot.update(
            index=0,
            frequency=freq,
            magnitude=mag,
            phase=phase,
        )
        self.bode_plot.update(
            index=1,
            frequency=freq,
            magnitude=mag,
            phase=phase,
        )
        if dpg.get_value(self.adjust_nyquist_limits_checkbox):
            self.nyquist_plot.queue_limits_adjustment()
        if dpg.get_value(self.adjust_bode_limits_checkbox):
            self.bode_plot.queue_limits_adjustment()

    def show_enlarged_nyquist(self):
        signals.emit(
            Signal.SHOW_ENLARGED_PLOT,
            plot=self.nyquist_plot,
            adjust_limits=dpg.get_value(self.adjust_nyquist_limits_checkbox),
        )

    def show_enlarged_bode(self):
        signals.emit(
            Signal.SHOW_ENLARGED_PLOT,
            plot=self.bode_plot,
            adjust_limits=dpg.get_value(self.adjust_bode_limits_checkbox),
        )

    def has_active_input(self) -> bool:
        return dpg.is_item_active(self.label_input) or dpg.is_item_active(
            self.path_input
        )
