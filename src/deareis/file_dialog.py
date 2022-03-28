# Copyright 2022 DearEIS developers
# DearEIS is licensed under the GPLv3 or later (https://www.gnu.org/licenses/gpl-3.0.html).
# The licenses of DearEIS' dependencies and/or sources of portions of code are included in
# the LICENSES folder.

import dearpygui.dearpygui as dpg
from typing import Callable, List
from deareis.utility import window_pos_dims

# TODO: Implement a custom file dialog?
# The one included in DPG has a few bug and quirks ranging from severe (crashes)
# to mildly annoying.
# 
# Features that would be good to have:
# - Ability to create folders (at least when picking where to save a project).
# - Ability to directly edit the path.
# - Visualize the path in an interactive way (e.g. buttons for each part in the path).
# - Ability to sort entries by name, type, date, and size?
# - Ability to filter by file extension.
# - Ability to search by name.
# - Ability to switch between partitions.
# - Support for following symbolic links.
# - Keybindings:
#   - Close window
#   - Go up one level
#
# Things to consider:
# - Cross-platform support
#   - No access to a machine with macOS for testing
# - Implement as a separate package that can be used by others?

def file_dialog(
    cwd: str, label: str, callback: Callable, extensions: List[str] = [".*"]
) -> int:
    assert type(cwd) is str
    assert type(label) is str
    assert type(extensions) is list and all(map(lambda _: type(_) is str, extensions))
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
