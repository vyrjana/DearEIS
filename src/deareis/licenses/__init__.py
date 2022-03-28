# Copyright 2022 DearEIS developers
# DearEIS is licensed under the GPLv3 or later (https://www.gnu.org/licenses/gpl-3.0.html).
# The licenses of DearEIS' dependencies and/or sources of portions of code are included in
# the LICENSES folder.

import dearpygui.dearpygui as dpg
from deareis.utility import window_pos_dims
from os import walk
from os.path import abspath, exists, dirname, join
from typing import Dict, IO, List


def _read_file(path: str) -> str:
    assert type(path) is str
    assert exists(path), path
    fp: IO
    with open(path, "r") as fp:
        return fp.read()


def _get_licenses(root: str) -> Dict[str, str]:
    assert type(root) is str
    assert exists(root), root
    files: List[str] = []
    for _, _, files in walk(root):
        files.remove("__init__.py")
        break
    assert len(files) > 0
    prefix: str = "LICENSE-"
    extension: str = ".txt"
    assert all(map(lambda _: _.startswith(prefix) and _.endswith(extension), files))
    files.sort()
    licenses: Dict[str, str] = {}
    file: str
    for file in files:
        key: str = file[len(prefix) : file.rfind(extension)]
        licenses[key] = _read_file(join(root, file))
    return licenses


def show_license_window():
    licenses: Dict[str, str] = _get_licenses(dirname(abspath(__file__)))
    x: int
    y: int
    w: int
    h: int
    x, y, w, h = window_pos_dims(640)
    window: int = dpg.generate_uuid()
    key_handler: int = dpg.generate_uuid()

    def close_window():
        if dpg.does_item_exist(window):
            dpg.delete_item(window)
        if dpg.does_item_exist(key_handler):
            dpg.delete_item(key_handler)

    with dpg.handler_registry(tag=key_handler):
        dpg.add_key_release_handler(
            key=dpg.mvKey_Escape,
            callback=close_window,
        )

    with dpg.window(
        label="Licenses",
        modal=True,
        pos=(
            x,
            y,
        ),
        width=w,
        height=h,
        no_move=True,
        no_resize=True,
        on_close=close_window,
        tag=window,
    ):
        with dpg.tab_bar():
            with dpg.tab(label="DearEIS"):
                with dpg.child_window(border=False):
                    dpg.add_text(licenses["DearEIS"], wrap=w)
                del licenses["DearEIS"]
            with dpg.tab(label="Dependencies"):
                text_widget: int = dpg.generate_uuid()

                def show_dependency_license(sender: int, label: str):
                    dpg.set_value(text_widget, licenses[label])

                items: List[str] = list(sorted(licenses.keys()))
                dpg.add_combo(
                    items=items,
                    default_value=items[0],
                    width=-1,
                    callback=show_dependency_license,
                )
                with dpg.child_window(border=False):
                    dpg.add_text(licenses[items[0]], wrap=w, tag=text_widget)
