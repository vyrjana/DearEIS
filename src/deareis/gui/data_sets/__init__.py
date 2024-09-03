# DearEIS is licensed under the GPLv3 or later (https://www.gnu.org/licenses/gpl-3.0.html).
# Copyright 2024 DearEIS developers
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
    Tuple,
)
from numpy import (
    angle,
    array,
    ndarray,
)
import dearpygui.dearpygui as dpg
from deareis.signals import Signal
import deareis.signals as signals
from deareis.gui.plots import (
    Bode,
    Impedance,
    Nyquist,
    Plot,
)
from deareis.utility import (
    align_numbers,
    format_number,
    pad_tab_labels,
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
                label="Re(Z) (ohm)",
            )
            attach_tooltip(tooltips.data_sets.real)
            dpg.add_table_column(
                label="-Im(Z) (ohm)",
            )
            attach_tooltip(tooltips.data_sets.imaginary)
            dpg.add_table_column(
                label="Mod(Z) (ohm)",
            )
            attach_tooltip(tooltips.data_sets.magnitude)
            dpg.add_table_column(
                label="-Phase(Z) (°)",
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
        frequencies: ndarray = data.get_frequencies(masked=None)
        freqs: List[str] = list(
            map(
                lambda _: format_number(_, significants=4),
                frequencies,
            )
        )
        Z: ndarray = data.get_impedances(masked=None)
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
        self.create_tab()

    def create_tab(self):
        self.tab: int = dpg.generate_uuid()
        with dpg.tab(label="Data sets", tag=self.tab):
            with dpg.child_window(border=False, width=-1, height=-1):
                with dpg.group(horizontal=True):
                    self.create_sidebar()
                    self.create_plots()

    def create_sidebar(self):
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
                        self.create_process_menu()
            self.create_table()
            self.create_bottom_bar()

    def create_process_menu(self):
        self.process_button: int = dpg.generate_uuid()
        dpg.add_button(
            label="Process",
            width=-1,
            tag=self.process_button,
        )
        attach_tooltip(tooltips.data_sets.process)
        process_popup_dimensions: Tuple[int, int] = (
            110,
            104,
        )
        process_popup: int
        with dpg.popup(
            parent=self.process_button,
            mousebutton=dpg.mvMouseButton_Left,
            min_size=process_popup_dimensions,
            max_size=process_popup_dimensions,
        ) as process_popup:
            self.average_button: int = dpg.generate_uuid()
            dpg.add_button(
                label="Average",
                callback=lambda s, a, u: signals.emit(
                    Signal.SELECT_DATA_SETS_TO_AVERAGE,
                    popup=process_popup,
                ),
                width=-1,
                tag=self.average_button,
            )
            attach_tooltip(tooltips.data_sets.average)
            #
            self.interpolation_button: int = dpg.generate_uuid()
            dpg.add_button(
                label="Interpolate",
                callback=lambda s, a, u: signals.emit(
                    Signal.SELECT_POINTS_TO_INTERPOLATE,
                    data=u,
                    popup=process_popup,
                ),
                width=-1,
                tag=self.interpolation_button,
            )
            attach_tooltip(tooltips.data_sets.interpolate)
            #
            self.parallel_impedance_button: int = dpg.generate_uuid()
            dpg.add_button(
                label="Parallel",
                callback=lambda s, a, u: signals.emit(
                    Signal.SELECT_PARALLEL_IMPEDANCE,
                    data=u,
                    popup=process_popup,
                ),
                width=-1,
                tag=self.parallel_impedance_button,
            )
            attach_tooltip(tooltips.data_sets.parallel)
            #
            self.subtract_impedance_button: int = dpg.generate_uuid()
            dpg.add_button(
                label="Subtract",
                callback=lambda s, a, u: signals.emit(
                    Signal.SELECT_IMPEDANCE_TO_SUBTRACT,
                    data=u,
                    popup=process_popup,
                ),
                width=-1,
                tag=self.subtract_impedance_button,
            )
            attach_tooltip(tooltips.data_sets.subtract)

    def create_table(self):
        with dpg.child_window(
            border=False,
            width=-2,
            height=-40,
            show=True,
        ):
            self.data_table = DataTable()

    def create_bottom_bar(self):
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
                self.enlarge_plot_button: int = dpg.generate_uuid()
                self.adjust_plot_limits_checkbox: int = dpg.generate_uuid()
                dpg.add_button(
                    label="Enlarge plot",
                    callback=self.show_enlarged_plot,
                    tag=self.enlarge_plot_button,
                )
                dpg.add_checkbox(
                    label="Adjust limits",
                    default_value=True,
                    callback=lambda s, a, u: self.toggle_plot_limits_adjustment(a),
                    tag=self.adjust_plot_limits_checkbox,
                )
                self.adjust_plot_limits_tooltip = attach_tooltip(
                    tooltips.general.adjust_plot_limits,
                )
                self.plot_combo: int = dpg.generate_uuid()
                dpg.add_combo(
                    default_value="?",
                    items=[],
                    width=-1,
                    callback=lambda s, a, u: self.select_plot(
                        sender=s,
                        label=a,
                    ),
                    tag=self.plot_combo,
                )

    def create_plots(self):
        self.plot_window: int = dpg.generate_uuid()
        self.plot_width: int = 400
        with dpg.child_window(
            border=False,
            width=-1,
            no_scrollbar=True,
            tag=self.plot_window,
            show=True,
        ):
            self.plot_tab_bar: int = dpg.generate_uuid()
            with dpg.tab_bar(
                callback=lambda s, a, u: self.select_plot(
                    sender=s,
                    tab=a,
                ),
                tag=self.plot_tab_bar,
            ):
                self.create_nyquist_plot()
                self.create_bode_plot()
                self.create_impedance_plot()
            pad_tab_labels(self.plot_tab_bar)
        plots: List[Plot] = [
            self.nyquist_plot,
            self.bode_plot,
            self.impedance_plot,
        ]
        plot_lookup: Dict[int, Plot] = {}
        label_lookup: Dict[int, str] = {}
        tab: int
        for tab in dpg.get_item_children(self.plot_tab_bar, slot=1):
            label_lookup[tab] = dpg.get_item_label(tab)
            plot_lookup[tab] = plots.pop(0)
        # Tab bar
        dpg.set_item_user_data(self.plot_tab_bar, label_lookup)
        # Combo
        tab_lookup: Dict[str, int] = {v: k for k, v in label_lookup.items()}
        labels: List[str] = list(tab_lookup.keys())
        dpg.configure_item(
            self.plot_combo,
            default_value=labels[0],
            items=labels,
            user_data=tab_lookup,
        )
        # Limits checkbox
        dpg.set_item_user_data(
            self.adjust_plot_limits_checkbox, {_: True for _ in labels}
        )
        # Enlarge button
        dpg.set_item_user_data(self.enlarge_plot_button, plot_lookup)

    def create_nyquist_plot(self):
        with dpg.tab(label="Nyquist"):
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

    def create_bode_plot(self):
        with dpg.tab(label="Bode"):
            self.bode_plot: Bode = Bode()
            self.bode_plot.plot(
                frequency=array([]),
                magnitude=array([]),
                phase=array([]),
                labels=(
                    "Mod(Z)",
                    "Phase(Z)",
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
                    "Mod(Z)",
                    "Phase(Z)",
                ),
                line=True,
                themes=(
                    themes.bode.magnitude_data,
                    themes.bode.phase_data,
                ),
                show_labels=False,
            )

    def create_impedance_plot(self):
        with dpg.tab(label="Real & Imag."):
            self.impedance_plot: Impedance = Impedance()
            self.impedance_plot.plot(
                frequency=array([]),
                real=array([]),
                imaginary=array([]),
                labels=(
                    "Re(Z)",
                    "Im(Z)",
                ),
                line=False,
                themes=(
                    themes.impedance.real_data,
                    themes.impedance.imaginary_data,
                ),
            )
            self.impedance_plot.plot(
                frequency=array([]),
                real=array([]),
                imaginary=array([]),
                labels=(
                    "Re(Z)",
                    "Im(Z)",
                ),
                line=True,
                themes=(
                    themes.impedance.real_data,
                    themes.impedance.imaginary_data,
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
                dpg.set_item_label(self.enlarge_plot_button, "Show plot")
        else:
            if not dpg.is_item_shown(self.plot_window):
                dpg.show_item(self.plot_window)
                dpg.set_item_width(self.table_window, self.table_width)
                dpg.split_frame()
                dpg.set_item_label(self.enlarge_plot_button, "Enlarge plot")
        if not dpg.is_item_shown(self.plot_window):
            return

    def toggle_plot_limits_adjustment(self, flag: bool):
        label: str = dpg.get_value(self.plot_combo)
        dpg.get_item_user_data(self.adjust_plot_limits_checkbox)[label] = flag

    def select_plot(
        self,
        sender: int,
        tab: int = -1,
        label: str = "",
    ):
        label_lookup: Optional[Dict[int, str]] = dpg.get_item_user_data(
            self.plot_tab_bar
        )
        tab_lookup: Optional[Dict[str, int]] = dpg.get_item_user_data(self.plot_combo)
        limits_lookup: Optional[Dict[str, bool]] = dpg.get_item_user_data(
            self.adjust_plot_limits_checkbox
        )
        assert label_lookup is not None
        assert tab_lookup is not None
        assert limits_lookup is not None
        # Store the value of the checkbox of the previous plot
        old_label: str
        if tab > 0:
            old_label = dpg.get_value(self.plot_combo)
        else:
            old_label = label_lookup[dpg.get_value(self.plot_tab_bar)]
        limits_lookup[old_label] = dpg.get_value(self.adjust_plot_limits_checkbox)
        # Adjust tab bar or combo to show the current plot
        if tab > 0:
            label = label_lookup[tab]
            dpg.set_value(self.plot_combo, label)
            if sender <= 0:
                dpg.set_value(self.plot_tab_bar, tab)
        elif label != "":
            tab = tab_lookup[label]
            dpg.set_value(self.plot_tab_bar, tab)
            if sender <= 0:
                dpg.set_value(self.plot_combo, label)
        else:
            raise NotImplementedError("Unknown means of selecting plot!")
        # Update the value of the checkbox to match the current plot
        dpg.set_value(self.adjust_plot_limits_checkbox, limits_lookup[label])

    def clear(self):
        dpg.set_value(self.data_sets_combo, "")
        dpg.set_value(self.label_input, "")
        dpg.set_value(self.path_input, "")
        dpg.set_item_user_data(self.delete_button, None)
        dpg.set_item_user_data(self.toggle_points_button, None)
        dpg.set_item_user_data(self.copy_mask_button, None)
        dpg.set_item_user_data(self.parallel_impedance_button, None)
        dpg.set_item_user_data(self.subtract_impedance_button, None)
        dpg.set_item_user_data(self.interpolation_button, None)
        self.data_table.clear()
        self.nyquist_plot.clear(delete=False)
        self.bode_plot.clear(delete=False)
        self.impedance_plot.clear(delete=False)

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
        dpg.set_item_user_data(self.parallel_impedance_button, data)
        dpg.set_item_user_data(self.subtract_impedance_button, data)
        dpg.set_item_user_data(self.interpolation_button, data)
        real: ndarray
        imag: ndarray
        real, imag = data.get_nyquist_data()
        i: int
        for i in range(0, 2):
            self.nyquist_plot.update(
                index=i,
                real=real,
                imaginary=imag,
            )
        freq: ndarray
        mag: ndarray
        phase: ndarray
        freq, mag, phase = data.get_bode_data()
        for i in range(0, 2):
            self.bode_plot.update(
                index=i,
                frequency=freq,
                magnitude=mag,
                phase=phase,
            )
        for i in range(0, 2):
            self.impedance_plot.update(
                index=i,
                frequency=freq,
                real=real,
                imaginary=imag,
            )
        limits_lookup: Optional[Dict[str, bool]] = dpg.get_item_user_data(
            self.adjust_plot_limits_checkbox
        )
        label: str
        flag: bool
        for label, flag in limits_lookup.items():
            if flag is True:
                self.get_plot(label=label).queue_limits_adjustment()

    def get_plot(self, tab: int = -1, label: str = "") -> Plot:
        if tab > 0:
            pass
        elif label != "":
            tab = dpg.get_item_user_data(self.plot_combo)[label]
        else:
            if dpg.is_item_shown(self.plot_window):
                tab = dpg.get_value(self.plot_tab_bar)
            else:
                label = dpg.get_value(self.plot_combo)
                tab = dpg.get_item_user_data(self.plot_combo)[label]
        return dpg.get_item_user_data(self.enlarge_plot_button)[tab]

    def should_adjust_limit(
        self,
        tab: int = -1,
        label: str = "",
        plot: Optional[Plot] = None,
    ) -> bool:
        if tab > 0:
            label = dpg.get_item_user_data(self.plot_tab_bar)[tab]
        elif label != "":
            pass
        elif plot is not None:
            label = dpg.get_item_user_data(self.plot_tab_bar)[
                {
                    v: k
                    for k, v in dpg.get_item_user_data(self.enlarge_plot_button).items()
                }[plot]
            ]
        else:
            tab = dpg.get_value(self.plot_tab_bar)
            label = dpg.get_item_user_data(self.plot_tab_bar)[tab]
        return dpg.get_item_user_data(self.adjust_plot_limits_checkbox)[label]

    def next_plot_tab(self):
        index: int
        if dpg.is_item_shown(self.plot_window):
            tabs: List[int] = dpg.get_item_children(self.plot_tab_bar, slot=1)
            index = tabs.index(dpg.get_value(self.plot_tab_bar)) + 1
            self.select_plot(sender=-1, tab=tabs[index % len(tabs)])
        else:
            tab_lookup: Dict[Plot, int] = {
                v: k
                for k, v in dpg.get_item_user_data(self.enlarge_plot_button).items()
            }
            label_lookup: Dict[int, str] = dpg.get_item_user_data(self.plot_tab_bar)
            labels: List[str] = list(label_lookup.values())
            index = labels.index(label_lookup[tab_lookup[self.get_plot()]]) + 1
            self.select_plot(sender=-1, label=labels[index % len(labels)])

    def previous_plot_tab(self):
        index: int
        if dpg.is_item_shown(self.plot_window):
            tabs: List[int] = dpg.get_item_children(self.plot_tab_bar, slot=1)
            index = tabs.index(dpg.get_value(self.plot_tab_bar)) - 1
            self.select_plot(sender=-1, tab=tabs[index % len(tabs)])
        else:
            tab_lookup: Dict[Plot, int] = {
                v: k
                for k, v in dpg.get_item_user_data(self.enlarge_plot_button).items()
            }
            label_lookup: Dict[int, str] = dpg.get_item_user_data(self.plot_tab_bar)
            labels: List[str] = list(label_lookup.values())
            index = labels.index(label_lookup[tab_lookup[self.get_plot()]]) - 1
            self.select_plot(sender=-1, label=labels[index % len(labels)])

    def show_enlarged_plot(self):
        signals.emit(
            Signal.SHOW_ENLARGED_PLOT,
            plot=self.get_plot(),
            adjust_limits=dpg.get_value(self.adjust_plot_limits_checkbox),
        )

    def show_enlarged_nyquist(self):
        signals.emit(
            Signal.SHOW_ENLARGED_PLOT,
            plot=self.nyquist_plot,
            adjust_limits=self.should_adjust_limit(plot=self.nyquist_plot),
        )

    def show_enlarged_bode(self):
        signals.emit(
            Signal.SHOW_ENLARGED_PLOT,
            plot=self.bode_plot,
            adjust_limits=self.should_adjust_limit(plot=self.bode_plot),
        )

    def show_enlarged_impedance(self):
        signals.emit(
            Signal.SHOW_ENLARGED_PLOT,
            plot=self.impedance_plot,
            adjust_limits=self.should_adjust_limit(plot=self.impedance_plot),
        )

    def has_active_input(self) -> bool:
        return dpg.is_item_active(self.label_input) or dpg.is_item_active(
            self.path_input
        )
