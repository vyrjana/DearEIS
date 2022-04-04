# Copyright 2022 DearEIS developers
# DearEIS is licensed under the GPLv3 or later (https://www.gnu.org/licenses/gpl-3.0.html).
# The licenses of DearEIS' dependencies and/or sources of portions of code are included in
# the LICENSES folder.

from pyimpspec import DataSet, string_to_circuit, simulate_spectrum
from numpy import angle
from typing import Callable, Dict, List, Optional
import dearpygui.dearpygui as dpg
from deareis.utility import (
    attach_tooltip,
    generate_test_data,
    number_formatter,
    align_numbers,
)
from deareis.plot import NyquistPlot, BodePlot
import deareis.tooltips as tooltips
import deareis.themes as themes

# TODO: Argument type assertions


class DataSetsTab:
    def __init__(self):
        self.tab: int = dpg.generate_uuid()
        self.resize_group: int = dpg.generate_uuid()
        # Left-hand side window
        self.left_window: int = dpg.generate_uuid()
        # - Data set selection
        self.dataset_combo: int = dpg.generate_uuid()
        self.load_button: int = dpg.generate_uuid()
        self.remove_button: int = dpg.generate_uuid()
        self.label_input: int = dpg.generate_uuid()
        self.path_input: int = dpg.generate_uuid()
        self.subtract_impedance_button: int = dpg.generate_uuid()
        # - Data points table
        self.dataset_table: int = dpg.generate_uuid()
        self.table_width: int = 600
        self.plot_width: int = 400
        # - Button window
        self.toggle_points_button: int = dpg.generate_uuid()
        self.copy_mask_button: int = dpg.generate_uuid()
        self.average_button: int = dpg.generate_uuid()
        self.enlarge_nyquist_button: int = dpg.generate_uuid()
        self.enlarge_bode_button: int = dpg.generate_uuid()
        # Right-hand side window
        self.right_window: int = dpg.generate_uuid()
        # - Plot window
        self.nyquist_plot: int = dpg.generate_uuid()
        self.bode_plot: int = dpg.generate_uuid()
        # State
        self.dataset_mask_modified_callback: Optional[Callable] = None
        #
        self._assemble()
        self._assign_handlers()
        self.populate_combo([])
        self.populate_table(None)

    def to_dict(self) -> dict:
        return {
            "label": dpg.get_value(self.label_input),
        }

    def restore_state(self, state: dict):
        dpg.set_value(self.label_input, state["label"])

    def _assemble(self):
        settings_height: int = 82
        sidebar_width: int = -1

        def selection_window():
            label_pad: int = 8
            with dpg.child_window(border=True, height=settings_height, width=-2):
                with dpg.group(horizontal=True):
                    with dpg.child_window(border=False, width=-72):
                        with dpg.group(horizontal=True):
                            dpg.add_text("Data set".rjust(label_pad))
                            dpg.add_combo(
                                tag=self.dataset_combo,
                                width=-1,
                            )
                        with dpg.group(horizontal=True):
                            dpg.add_text("Label".rjust(label_pad))
                            dpg.add_input_text(
                                width=-1,
                                on_enter=True,
                                tag=self.label_input,
                            )
                        with dpg.group(horizontal=True):
                            dpg.add_text("Path".rjust(label_pad))
                            dpg.add_input_text(
                                width=-1,
                                on_enter=True,
                                tag=self.path_input,
                            )
                    with dpg.child_window(border=False, width=-1):
                        dpg.add_button(
                            label="Load",
                            width=-1,
                            tag=self.load_button,
                        )
                        attach_tooltip(tooltips.datasets_load)
                        dpg.add_button(
                            label="Delete",
                            width=-1,
                            tag=self.remove_button,
                        )
                        attach_tooltip(tooltips.datasets_remove)
                        dpg.add_button(
                            label="Average",
                            tag=self.average_button,
                            width=-1,
                        )
                        attach_tooltip(tooltips.datasets_average)

        def dataset_table():
            with dpg.child_window(border=False, width=-2, height=-40, show=True):
                dpg.add_table(
                    borders_outerV=True,
                    borders_outerH=True,
                    borders_innerV=True,
                    borders_innerH=True,
                    scrollY=True,
                    freeze_rows=1,
                    tag=self.dataset_table,
                )

        def buttons_window():
            with dpg.child_window(border=True, width=-2):
                with dpg.group(horizontal=True):
                    dpg.add_button(
                        label="Toggle points",
                        tag=self.toggle_points_button,
                    )
                    attach_tooltip(tooltips.datasets_toggle)
                    dpg.add_button(
                        label="Copy mask",
                        tag=self.copy_mask_button,
                    )
                    attach_tooltip(tooltips.datasets_copy)
                    dpg.add_button(
                        label="Subtract",
                        tag=self.subtract_impedance_button,
                    )
                    attach_tooltip(tooltips.datasets_subtract)
                    dpg.add_button(
                        label="Enlarge Nyquist",
                        tag=self.enlarge_nyquist_button,
                    )
                    dpg.add_button(
                        label="Enlarge Bode",
                        tag=self.enlarge_bode_button,
                    )

        def plots_window():
            with dpg.child_window(
                border=False,
                width=-1,
                no_scrollbar=True,
                tag=self.right_window,
                show=True,
            ):
                self.nyquist_plot = NyquistPlot(
                    dpg.add_plot(
                        equal_aspects=True,
                        width=-1,
                        anti_aliased=True,
                    )
                )
                dpg.set_item_user_data(
                    self.enlarge_nyquist_button,
                    self.nyquist_plot,
                )
                self.bode_plot = BodePlot(
                    dpg.add_plot(
                        width=-1,
                        anti_aliased=True,
                    )
                )
                dpg.set_item_user_data(
                    self.enlarge_bode_button,
                    self.bode_plot,
                )

        with dpg.tab(label="Data sets", tag=self.tab):
            with dpg.child_window(border=False, width=-1, height=-1):
                with dpg.group(horizontal=True, tag=self.resize_group):
                    with dpg.child_window(
                        border=False,
                        width=self.table_width,
                        tag=self.left_window,
                        show=True,
                    ):
                        selection_window()
                        dataset_table()
                        buttons_window()
                    plots_window()

    def _assign_handlers(self):
        group_handler: int
        with dpg.item_handler_registry() as group_handler:
            dpg.add_item_resize_handler(callback=self.resize)
        dpg.bind_item_handler_registry(self.resize_group, group_handler)

        tab_handler: int
        with dpg.item_handler_registry() as tab_handler:
            dpg.add_item_clicked_handler(callback=self.resize)
        dpg.bind_item_handler_registry(self.tab, tab_handler)

    def is_visible(self) -> bool:
        return dpg.is_item_visible(self.dataset_combo)

    def resize(self):
        dpg.split_frame(delay=100)
        total_width: int
        total_height: int
        total_width, total_height = dpg.get_item_rect_size(self.resize_group)
        if total_width >= self.table_width + self.plot_width:
            plot_height: int = (
                round(total_height / 2)
                if total_height >= self.plot_width
                else total_height
            )
            no_scrollbar: bool = total_height >= self.plot_width
            self.nyquist_plot.resize(-1, plot_height)
            self.bode_plot.resize(-1, plot_height)
            dpg.configure_item(self.right_window, no_scrollbar=no_scrollbar)
            dpg.configure_item(self.left_window, width=self.table_width)
            if not dpg.is_item_shown(self.right_window):
                dpg.configure_item(self.enlarge_nyquist_button, label="Enlarge Nyquist")
                dpg.configure_item(self.enlarge_bode_button, label="Enlarge Bode")
                dpg.show_item(self.right_window)
        elif total_width < self.table_width + self.plot_width:
            dpg.configure_item(self.left_window, width=-2)
            if dpg.is_item_shown(self.right_window):
                dpg.configure_item(self.enlarge_nyquist_button, label="Show Nyquist")
                dpg.configure_item(self.enlarge_bode_button, label="Show Bode")
                dpg.hide_item(self.right_window)
        self.nyquist_plot.adjust_limits()
        self.bode_plot.adjust_limits()

    def populate_combo(self, labels: List[str], default: str = ""):
        assert type(labels) is list and all(list(map(lambda _: type(_) is str, labels)))
        assert type(default) is str
        if default == "" and len(labels) > 0:
            default = labels[0]
        dpg.configure_item(self.dataset_combo, items=labels, default_value=default)

    def populate_table(self, data: Optional[DataSet]):
        assert type(data) is DataSet or data is None
        dpg.delete_item(self.dataset_table, children_only=True)
        dpg.add_table_column(parent=self.dataset_table, label="Mask", width_fixed=True)
        attach_tooltip(tooltips.datasets_mask)
        dpg.add_table_column(parent=self.dataset_table, label="Index", width_fixed=True)
        dpg.add_table_column(parent=self.dataset_table, label="f (Hz)")
        attach_tooltip(tooltips.datasets_frequency)
        dpg.add_table_column(parent=self.dataset_table, label="Z' (ohm)")
        attach_tooltip(tooltips.datasets_real)
        dpg.add_table_column(parent=self.dataset_table, label='-Z" (ohm)')
        attach_tooltip(tooltips.datasets_imaginary)
        dpg.add_table_column(parent=self.dataset_table, label="|Z| (ohm)")
        attach_tooltip(tooltips.datasets_modulus)
        dpg.add_table_column(parent=self.dataset_table, label="-phi (deg.)")
        attach_tooltip(tooltips.datasets_phase)
        if data is None:
            return
        mask: Dict[int, bool] = data.get_mask()
        indices: List[str] = list(
            map(lambda _: str(_ + 1), range(0, data.get_num_points(masked=None)))
        )
        frequencies: ndarray = data.get_frequency(masked=None)
        freq: List[str] = list(
            map(
                lambda _: number_formatter(_, significants=4),
                frequencies,
            )
        )
        Z: ndarray = data.get_impedance(masked=None)
        reals: List[str] = list(
            map(lambda _: number_formatter(_.real, significants=4), Z)
        )
        imags: List[str] = list(
            map(lambda _: number_formatter(-_.imag, significants=4), Z)
        )
        mags: List[str] = list(
            map(lambda _: number_formatter(abs(_), significants=4), Z)
        )
        phis: List[str] = list(
            map(
                lambda _: number_formatter(
                    -angle(_, deg=True), significants=4, exponent=False
                ),
                Z,
            )
        )
        fmt: str = "{:.6E}"
        for i, (idx, f, re, im, mag, phi) in enumerate(
            zip(
                align_numbers(indices),
                align_numbers(freq),
                align_numbers(reals),
                align_numbers(imags),
                align_numbers(mags),
                align_numbers(phis),
            )
        ):
            with dpg.table_row(parent=self.dataset_table):
                dpg.add_checkbox(
                    default_value=mask.get(i, False),
                    callback=(
                        self.dataset_mask_modified_callback
                        if self.dataset_mask_modified_callback is not None
                        else None
                    ),
                )
                dpg.add_text(idx)
                dpg.add_text(f)
                attach_tooltip(fmt.format(frequencies[i]))
                dpg.add_text(re)
                attach_tooltip(fmt.format(Z[i].real))
                dpg.add_text(im)
                attach_tooltip(fmt.format(-Z[i].imag))
                dpg.add_text(mag)
                attach_tooltip(fmt.format(abs(Z[i])))
                dpg.add_text(phi)
                attach_tooltip(fmt.format(-angle(Z[i], deg=True)))

    def plot(self, data: Optional[DataSet]):
        assert type(data) is DataSet or data is None
        self.nyquist_plot.clear_plot()
        self.bode_plot.clear_plot()
        if data is None:
            return
        self.nyquist_plot.plot_data(*data.get_nyquist_data(), -1)
        self.nyquist_plot.adjust_limits()
        self.bode_plot.plot_data(
            *data.get_bode_data(),
            (
                -1,
                -1,
            )
        )
        self.bode_plot.adjust_limits()

    def get_dataset(self) -> Optional[DataSet]:
        if not dpg.does_item_exist(self.dataset_combo):
            return None
        return dpg.get_item_user_data(self.dataset_combo)

    def select_dataset(
        self, data: Optional[DataSet], update_table: bool, update_plots: bool
    ):
        assert type(data) is DataSet or data is None
        assert type(update_table) is bool
        assert type(update_plots) is bool
        dpg.set_item_user_data(self.dataset_combo, data)
        label: str = data.get_label() if data is not None else ""
        dpg.set_value(self.dataset_combo, label)
        dpg.set_value(self.label_input, label)
        path: str = data.get_path() if data is not None else ""
        dpg.set_value(self.path_input, path)
        if update_table:
            self.populate_table(data)
        elif data is None:
            self.populate_table(None)
        if update_plots:
            self.plot(data)
        elif data is None:
            self.plot(None)

    def get_mask(self) -> Dict[int, bool]:
        mask: Dict[int, bool] = {}
        i: int
        row: int
        for i, row in enumerate(dpg.get_item_children(self.dataset_table, slot=1)):
            column: int
            for column in dpg.get_item_children(row, slot=1):
                assert dpg.get_item_type(column).endswith("mvCheckbox")
                mask[i] = dpg.get_value(column)
                break
        return mask

    def update_mask(self, mask: Dict[int, bool]):
        i: int
        row: int
        for i, row in enumerate(dpg.get_item_children(self.dataset_table, slot=1)):
            column: int
            for column in dpg.get_item_children(row, slot=1):
                assert dpg.get_item_type(column).endswith("mvCheckbox")
                dpg.set_value(column, mask[i])
                break


if __name__ == "__main__":
    dpg.create_context()
    dpg.create_viewport(title="Data sets tab")
    dpg.setup_dearpygui()
    dpg.show_viewport()
    themes.initialize()
    data: DataSet = generate_test_data()
    window: int
    with dpg.window() as window:
        with dpg.tab_bar():
            dst: DataSetsTab = DataSetsTab()
            dst.populate_combo([data.get_label()])
            dst.select_dataset(data, True)
    dpg.set_primary_window(window, True)
    dpg.start_dearpygui()
    dpg.destroy_context()
