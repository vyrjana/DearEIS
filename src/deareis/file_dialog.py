# Copyright 2022 DearEIS developers
# DearEIS is licensed under the GPLv3 or later (https://www.gnu.org/licenses/gpl-3.0.html).
# The licenses of DearEIS' dependencies and/or sources of portions of code are included in
# the LICENSES folder.

import dearpygui.dearpygui as dpg
from typing import Callable, List
from deareis.utility import window_pos_dims


def file_dialog(
    cwd: str, label: str, callback: Callable, extensions: List[str] = [".*"]
) -> int:
    assert type(cwd) is str
    assert type(label) is str
    assert type(extensions) is list and all(map(lambda _: type(_) is str, extensions))
    # TODO: Keybinding(s)
    window: int
    with dpg.file_dialog(
        label=label,
        default_path=cwd,
        default_filename="",
        modal=True,
        callback=callback,
    ) as window:
        for ext in extensions:
            dpg.add_file_extension(ext)
    w: int
    h: int
    _, _, w, h = window_pos_dims(0.5, 0.5)
    dpg.configure_item(
        window,
        width=w,
        height=h,
    )
    return window
