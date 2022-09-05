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

from traceback import format_exc
from enum import (
    IntEnum,
    auto,
)
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Tuple,
)


DEBUG: bool = False


class Signal(IntEnum):
    APPLY_DATA_SET_MASK = auto()
    APPLY_DRT_SETTINGS = auto()
    APPLY_FIT_SETTINGS = auto()
    APPLY_SIMULATION_SETTINGS = auto()
    APPLY_TEST_SETTINGS = auto()
    AVERAGE_DATA_SETS = auto()
    BLOCK_KEYBINDINGS = auto()
    CHECK_UPDATES = auto()
    CLEAR_RECENT_PROJECTS = auto()
    CLOSE_PROJECT = auto()
    COPY_OUTPUT = auto()
    COPY_PLOT_APPEARANCE_SETTINGS = auto()
    COPY_PLOT_DATA = auto()
    CREATE_PROJECT_SNAPSHOT = auto()
    DELETE_DATA_SET = auto()
    DELETE_DRT_RESULT = auto()
    DELETE_FIT_RESULT = auto()
    DELETE_PLOT_SETTINGS = auto()
    DELETE_SIMULATION_RESULT = auto()
    DELETE_TEST_RESULT = auto()
    EXPORT_PLOT = auto()
    HIDE_BUSY_MESSAGE = auto()
    LOAD_DATA_SET_FILES = auto()
    LOAD_PROJECT_FILES = auto()
    MODIFY_DATA_SET_PATH = auto()
    MODIFY_PLOT_SERIES_THEME = auto()
    MODIFY_PROJECT_NOTES = auto()
    NEW_PLOT_SETTINGS = auto()
    NEW_PROJECT = auto()
    PERFORM_DRT = auto()
    PERFORM_FIT = auto()
    PERFORM_SIMULATION = auto()
    PERFORM_TEST = auto()
    REDO_PROJECT_ACTION = auto()
    RENAME_DATA_SET = auto()
    RENAME_PLOT_SERIES = auto()
    RENAME_PLOT_SETTINGS = auto()
    RENAME_PROJECT = auto()
    REORDER_PLOT_SERIES = auto()
    RESTORE_PROJECT_STATE = auto()
    SAVE_PLOT = auto()
    SAVE_PROJECT = auto()
    SAVE_PROJECT_AS = auto()
    SELECT_DATA_POINTS_TO_TOGGLE = auto()
    SELECT_DATA_SET = auto()
    SELECT_DATA_SETS_TO_AVERAGE = auto()
    SELECT_DATA_SET_FILES = auto()
    SELECT_DATA_SET_MASK_TO_COPY = auto()
    SELECT_DRT_RESULT = auto()
    SELECT_FIT_RESULT = auto()
    SELECT_HOME_TAB = auto()
    SELECT_IMPEDANCE_TO_SUBTRACT = auto()
    SELECT_PLOT_APPEARANCE_SETTINGS = auto()
    SELECT_PLOT_SETTINGS = auto()
    SELECT_PLOT_TYPE = auto()
    SELECT_PROJECT_FILES = auto()
    SELECT_PROJECT_TAB = auto()
    SELECT_SIMULATION_RESULT = auto()
    SELECT_TEST_RESULT = auto()
    SHOW_BUSY_MESSAGE = auto()
    SHOW_CHANGELOG = auto()
    SHOW_COMMAND_PALETTE = auto()
    SHOW_ENLARGED_PLOT = auto()
    SHOW_ERROR_MESSAGE = auto()
    SHOW_HELP_ABOUT = auto()
    SHOW_HELP_LICENSES = auto()
    SHOW_SETTINGS_APPEARANCE = auto()
    SHOW_SETTINGS_DEFAULTS = auto()
    SHOW_SETTINGS_KEYBINDINGS = auto()
    TOGGLE_DATA_POINT = auto()
    TOGGLE_PLOT_SERIES = auto()
    UNBLOCK_KEYBINDINGS = auto()
    UNDO_PROJECT_ACTION = auto()
    VIEWPORT_RESIZED = auto()


_UUID_COUNTER: int = 0
_REGISTERED_CALLBACKS: Dict[Signal, List[Tuple[Callable, int]]] = {}
_QUEUE: Optional[Dict[Signal, List[Tuple[tuple, dict]]]] = {}


def emit(signal: Signal, *args, **kwargs):
    global _REGISTERED_CALLBACKS
    global _QUEUE
    assert type(signal) is Signal, signal
    if _QUEUE is not None and signal not in _REGISTERED_CALLBACKS:
        if signal not in _QUEUE:
            _QUEUE[signal] = []
        _QUEUE[signal].append(
            (
                args,
                kwargs,
            )
        )
        return
    assert signal in _REGISTERED_CALLBACKS, signal
    try:
        if DEBUG:
            print(f"\nsignals.emit: {str(signal)}")
            if args:
                print("- args:")
                arg: Any
                for arg in args:
                    if len(repr(arg)) > 80:
                        print(f" - {repr(arg)[:80]}...")
                    else:
                        print(f" - {repr(arg)}")
            if kwargs:
                print("- kwargs:")
                key: str
                value: Any
                for key, value in kwargs.items():
                    if len(repr(value)) > 80:
                        print(f" - {key}: {repr(value)[:80]}...")
                    else:
                        print(f" - {key}: {repr(value)}")
            print("- entries:")
        entry: Tuple[Callable, int]
        func: Callable
        uuid: int
        for (func, uuid) in _REGISTERED_CALLBACKS[signal]:
            if DEBUG:
                print(f" - {uuid}: {repr(func)}")
            func(*args, **kwargs)
    except Exception:
        if signal == Signal.SHOW_ERROR_MESSAGE:
            print(format_exc())
        else:
            emit(Signal.SHOW_ERROR_MESSAGE, format_exc())


def register(signal: Signal, callback: Callable) -> int:
    global _UUID_COUNTER
    global _REGISTERED_CALLBACKS
    assert type(signal) is Signal, signal
    try:
        if signal not in _REGISTERED_CALLBACKS:
            _REGISTERED_CALLBACKS[signal] = []
        _UUID_COUNTER += 1
        _REGISTERED_CALLBACKS[signal].append(
            (
                callback,
                _UUID_COUNTER,
            )
        )
        if DEBUG:
            print(f"\nsignals.register: {str(signal)}")
            print(f"- callback: {callback} ({_UUID_COUNTER})")
        return _UUID_COUNTER
    except Exception:
        if signal == Signal.SHOW_ERROR_MESSAGE:
            print(format_exc())
        else:
            emit(Signal.SHOW_ERROR_MESSAGE, format_exc())
        return -1


def unregister(
    signal: Signal, callback: Optional[Callable] = None, uuid: Optional[int] = None
):
    if DEBUG:
        print(f"\nsignals.unregister: {str(signal)}")
        print(f"- callback: {callback}")
        print(f"- uuid: {uuid}")
    global _REGISTERED_CALLBACKS
    assert type(signal) is Signal, signal
    assert callback is not None or type(uuid) is int and uuid > 0, (
        callback,
        uuid,
    )
    assert signal in _REGISTERED_CALLBACKS, signal
    try:
        chosen_entry: Optional[Tuple[Callable, int]] = None
        entry: Tuple[Callable, int]
        for entry in _REGISTERED_CALLBACKS[signal]:
            if entry[0] == callback or entry[1] == uuid:
                chosen_entry = entry
                break
        assert chosen_entry is not None
        _REGISTERED_CALLBACKS[signal].remove(chosen_entry)
    except Exception:
        if signal == Signal.SHOW_ERROR_MESSAGE:
            print(format_exc())
        else:
            emit(Signal.SHOW_ERROR_MESSAGE, format_exc())


def clear(signal: Signal):
    if DEBUG:
        print(f"\nsignals.clear: {str(signal)}")
    global _REGISTERED_CALLBACKS
    assert type(signal) is Signal, signal
    assert signal in _REGISTERED_CALLBACKS, signal
    try:
        del _REGISTERED_CALLBACKS[signal]
    except Exception:
        if signal == Signal.SHOW_ERROR_MESSAGE:
            print(format_exc())
        else:
            emit(Signal.SHOW_ERROR_MESSAGE, format_exc())


def emit_backlog():
    global _QUEUE
    signal: Signal
    queue: List[Tuple[list, dict]]
    for signal, queue in _QUEUE.items():
        for (args, kwargs) in queue:
            emit(signal, *args, **kwargs)
    _QUEUE = None
