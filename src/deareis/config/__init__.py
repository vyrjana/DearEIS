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

from json import dumps as dump_json, load as load_json, loads as parse_json
from os import makedirs
from os.path import exists, isdir, join
from traceback import format_exc
from typing import Any, Callable, Dict, IO, List, Optional, Set
from xdg import (
    xdg_cache_home,  #  User-specific cache files
    xdg_config_home,  # User-specific configuration files
    xdg_data_home,  #   User-specific data files
)
import dearpygui.dearpygui as dpg
from deareis.keybindings import Keybinding
from deareis.data import (
    FitSettings,
    SimulationSettings,
    TestSettings,
)
from deareis.enums import (
    Action,
    Context,
    Method,
    Mode,
    Test,
    Weight,
    action_contexts,
)
import deareis.themes as themes
from deareis.signals import Signal
import deareis.signals as signals


DEFAULT_KEYBINDINGS: List[Keybinding] = [
    Keybinding(
        dpg.mvKey_N,
        False,
        True,
        False,
        Action.NEW_PROJECT,
    ),
    Keybinding(
        dpg.mvKey_O,
        False,
        True,
        False,
        Action.LOAD_PROJECT,
    ),
    Keybinding(
        dpg.mvKey_Q,
        False,
        True,
        False,
        Action.EXIT,
    ),
    Keybinding(
        dpg.mvKey_Next,
        False,
        False,
        True,
        Action.NEXT_PROGRAM_TAB,
    ),
    Keybinding(
        dpg.mvKey_Prior,
        False,
        False,
        True,
        Action.PREVIOUS_PROGRAM_TAB,
    ),
    Keybinding(
        dpg.mvKey_F1,
        False,
        False,
        False,
        Action.SHOW_SETTINGS_APPEARANCE,
    ),
    Keybinding(
        dpg.mvKey_F2,
        False,
        False,
        False,
        Action.SHOW_SETTINGS_DEFAULTS,
    ),
    Keybinding(
        dpg.mvKey_F3,
        False,
        False,
        False,
        Action.SHOW_SETTINGS_KEYBINDINGS,
    ),
    Keybinding(
        dpg.mvKey_F11,
        False,
        False,
        False,
        Action.SHOW_HELP_LICENSES,
    ),
    Keybinding(
        dpg.mvKey_F12,
        False,
        False,
        False,
        Action.SHOW_HELP_ABOUT,
    ),
    Keybinding(
        dpg.mvKey_P,
        False,
        True,
        False,
        Action.SHOW_COMMAND_PALETTE,
    ),
    Keybinding(
        dpg.mvKey_S,
        False,
        True,
        False,
        Action.SAVE_PROJECT,
    ),
    Keybinding(
        dpg.mvKey_S,
        False,
        True,
        True,
        Action.SAVE_PROJECT_AS,
    ),
    Keybinding(
        dpg.mvKey_W,
        False,
        True,
        False,
        Action.CLOSE_PROJECT,
    ),
    Keybinding(
        dpg.mvKey_Z,
        False,
        True,
        False,
        Action.UNDO,
    ),
    Keybinding(
        dpg.mvKey_Y if dpg.get_platform() == dpg.mvPlatform_Windows else dpg.mvKey_Z,
        False,
        True,
        False if dpg.get_platform() == dpg.mvPlatform_Windows else True,
        Action.REDO,
    ),
    Keybinding(
        dpg.mvKey_Next,
        False,
        True,
        False,
        Action.NEXT_PROJECT_TAB,
    ),
    Keybinding(
        dpg.mvKey_Prior,
        False,
        True,
        False,
        Action.PREVIOUS_PROJECT_TAB,
    ),
    Keybinding(
        dpg.mvKey_D,
        True,
        True,
        False,
        Action.SELECT_DATA_SETS_TAB,
    ),
    Keybinding(
        dpg.mvKey_F,
        True,
        True,
        False,
        Action.SELECT_FITTING_TAB,
    ),
    Keybinding(
        dpg.mvKey_K,
        True,
        True,
        False,
        Action.SELECT_KRAMERS_KRONIG_TAB,
    ),
    Keybinding(
        dpg.mvKey_O,
        True,
        True,
        False,
        Action.SELECT_OVERVIEW_TAB,
    ),
    Keybinding(
        dpg.mvKey_P,
        True,
        True,
        False,
        Action.SELECT_PLOTTING_TAB,
    ),
    Keybinding(
        dpg.mvKey_S,
        True,
        True,
        False,
        Action.SELECT_SIMULATION_TAB,
    ),
    Keybinding(
        dpg.mvKey_Return,
        False if dpg.get_platform() == dpg.mvPlatform_Windows else True,
        True if dpg.get_platform() == dpg.mvPlatform_Windows else False,
        False,
        Action.PERFORM_ACTION,
    ),
    Keybinding(
        dpg.mvKey_Delete,
        True,
        False,
        False,
        Action.DELETE_RESULT,
    ),
    Keybinding(
        dpg.mvKey_Next,
        False,
        False,
        False,
        Action.NEXT_PRIMARY_RESULT,
    ),
    Keybinding(
        dpg.mvKey_Prior,
        False,
        False,
        False,
        Action.PREVIOUS_PRIMARY_RESULT,
    ),
    Keybinding(
        dpg.mvKey_Next,
        True,
        False,
        False,
        Action.NEXT_SECONDARY_RESULT,
    ),
    Keybinding(
        dpg.mvKey_Prior,
        True,
        False,
        False,
        Action.PREVIOUS_SECONDARY_RESULT,
    ),
    Keybinding(
        dpg.mvKey_A,
        True,
        False,
        False,
        Action.APPLY_SETTINGS,
    ),
    Keybinding(
        dpg.mvKey_M,
        True,
        False,
        False,
        Action.APPLY_MASK,
    ),
    Keybinding(
        dpg.mvKey_N,
        True,
        False,
        False,
        Action.SHOW_ENLARGED_NYQUIST,
    ),
    Keybinding(
        dpg.mvKey_B,
        True,
        False,
        False,
        Action.SHOW_ENLARGED_BODE,
    ),
    Keybinding(
        dpg.mvKey_R,
        True,
        False,
        False,
        Action.SHOW_ENLARGED_RESIDUALS,
    ),
    Keybinding(
        dpg.mvKey_E,
        True,
        False,
        False,
        Action.SHOW_CIRCUIT_EDITOR,
    ),
    Keybinding(
        dpg.mvKey_N,
        True,
        False,
        True,
        Action.COPY_NYQUIST_DATA,
    ),
    Keybinding(
        dpg.mvKey_B,
        True,
        False,
        True,
        Action.COPY_BODE_DATA,
    ),
    Keybinding(
        dpg.mvKey_R,
        True,
        False,
        True,
        Action.COPY_RESIDUALS_DATA,
    ),
    Keybinding(
        dpg.mvKey_C,
        True,
        False,
        False,
        Action.COPY_OUTPUT,
    ),
    Keybinding(
        dpg.mvKey_A,
        True,
        False,
        False,
        Action.AVERAGE_DATA_SETS,
    ),
    Keybinding(
        dpg.mvKey_T,
        True,
        False,
        False,
        Action.TOGGLE_DATA_POINTS,
    ),
    Keybinding(
        dpg.mvKey_C,
        True,
        False,
        False,
        Action.COPY_DATA_SET_MASK,
    ),
    Keybinding(
        dpg.mvKey_S,
        True,
        False,
        False,
        Action.SUBTRACT_IMPEDANCE,
    ),
    Keybinding(
        dpg.mvKey_A,
        True,
        False,
        False,
        Action.SELECT_ALL_PLOT_SERIES,
    ),
    Keybinding(
        dpg.mvKey_A,
        True,
        False,
        True,
        Action.UNSELECT_ALL_PLOT_SERIES,
    ),
    Keybinding(
        dpg.mvKey_C,
        True,
        False,
        False,
        Action.COPY_PLOT_APPEARANCE,
    ),
    Keybinding(
        dpg.mvKey_C,
        True,
        False,
        True,
        Action.COPY_PLOT_DATA,
    ),
    Keybinding(
        dpg.mvKey_E,
        True,
        False,
        False,
        Action.EXPAND_COLLAPSE_SIDEBAR,
    ),
]


# TODO: Replace string keys with int keys (e.g. themes.nyquist.data) and use strings only in the
# config file
DEFAULT_MARKERS: Dict[str, int] = {
    "residuals_real": dpg.mvPlotMarker_Circle,
    "residuals_imaginary": dpg.mvPlotMarker_Square,
    "nyquist_data": dpg.mvPlotMarker_Circle,
    "nyquist_simulation": dpg.mvPlotMarker_Cross,
    "bode_magnitude_data": dpg.mvPlotMarker_Circle,
    "bode_magnitude_simulation": dpg.mvPlotMarker_Cross,
    "bode_phase_data": dpg.mvPlotMarker_Square,
    "bode_phase_simulation": dpg.mvPlotMarker_Plus,
    "mu_Xps_mu": dpg.mvPlotMarker_Circle,
    "mu_Xps_Xps": dpg.mvPlotMarker_Square,
}


DEFAULT_COLORS: Dict[str, List[float]] = {
    "residuals_real": [
        238.0,
        51.0,
        119.0,
        190.0,
    ],
    "residuals_imaginary": [
        0.0,
        153.0,
        136.0,
        190.0,
    ],
    "nyquist_data": [
        51.0,
        187.0,
        238.0,
        190.0,
    ],
    "nyquist_simulation": [
        238.0,
        51.0,
        119.0,
        190.0,
    ],
    "bode_magnitude_data": [
        51.0,
        187.0,
        238.0,
        190.0,
    ],
    "bode_magnitude_simulation": [
        238.0,
        51.0,
        119.0,
        190.0,
    ],
    "bode_phase_data": [
        238.0,
        119.0,
        51.0,
        190.0,
    ],
    "bode_phase_simulation": [
        0.0,
        153.0,
        136.0,
        190.0,
    ],
    "mu_Xps_mu_criterion": [
        255.0,
        255.0,
        255.0,
        128.0,
    ],
    "mu_Xps_mu": [
        238.0,
        51.0,
        119.0,
        190.0,
    ],
    "mu_Xps_mu_highlight": [
        51.0,
        187.0,
        238.0,
        190.0,
    ],
    "mu_Xps_Xps": [
        0.0,
        153.0,
        136.0,
        190.0,
    ],
    "mu_Xps_Xps_highlight": [
        238.0,
        119.0,
        51.0,
        190.0,
    ],
}

DEFAULT_TEST_SETTINGS: TestSettings = TestSettings(
    Test.COMPLEX,
    Mode.EXPLORATORY,
    999,
    0.85,
    True,
    True,
    Method.LEASTSQ,
    1000,
)

DEFAULT_FIT_SETTINGS: FitSettings = FitSettings(
    "R([RW]C)",
    Method.AUTO,
    Weight.AUTO,
    1000,
)

DEFAULT_SIMULATION_SETTINGS: SimulationSettings = SimulationSettings(
    "R([RW]C)",
    1.0e-2,
    1.0e5,
    1,
)


VERSION: int = 2


def _parse_v2(dictionary: dict) -> dict:
    # TODO: Update when VERSION is incremented to 3
    return dictionary


def _parse_v1(dictionary: dict) -> dict:
    assert type(dictionary) is dict
    new_color_marker_keys: Dict[str, str] = {
        "real_error": "residuals_real",
        "imag_error": "residuals_imaginary",
        "nyquist_sim": "nyquist_simulation",
        "bode_magnitude_sim": "bode_magnitude_simulation",
        "bode_phase_sim": "bode_phase_simulation",
        "exploratory_mu_criterion": "mu_Xps_mu_criterion",
        "exploratory_mu": "mu_Xps_mu",
        "exploratory_mu_highlight": "mu_Xps_mu_highlight",
        "exploratory_xps": "mu_Xps_Xps",
        "exploratory_xps_highlight": "mu_Xps_Xps_highlight",
    }
    old: str
    new: str
    colors: dict = dictionary.get("colors", {})
    markers: dict = dictionary.get("markers", {})
    for old, new in new_color_marker_keys.items():
        if old in colors:
            colors[new] = colors[old]
            del colors[old]
        if old in markers:
            markers[new] = markers[old]
            del markers[old]
    return _parse_v2(
        {
            "version": 2,
            "auto_backup_interval": dictionary.get("auto_backup_interval", 10),
            "num_per_decade_in_simulated_lines": dictionary[
                "num_per_decade_in_simulated_lines"
            ],
            "markers": dictionary["markers"],
            "colors": dictionary["colors"],
            "default_test_settings": dictionary["default_test_settings"],
            "default_fit_settings": dictionary["default_fit_settings"],
            "default_simulation_settings": dictionary["default_simulation_settings"],
        }
    )


class Config:
    def __init__(self):
        self.config_dir_path: str = join(xdg_config_home(), "DearEIS")
        self.config_path: str = join(self.config_dir_path, "config.json")
        self.auto_backup_interval: int = None  # type: ignore
        self.num_per_decade_in_simulated_lines: int = None  # type: ignore
        self.default_test_settings: TestSettings = None  # type: ignore
        self.default_fit_settings: FitSettings = None  # type: ignore
        self.default_simulation_settings: SimulationSettings = None  # type: ignore
        self.markers: Dict[str, int] = None  # type: ignore
        self.colors: Dict[str, List[float]] = None  # type: ignore
        self.keybindings: List[Keybinding] = None  # type: ignore
        self.from_dict(self.default_settings())
        if not exists(self.config_path):
            self.save()
        else:
            try:
                self.load()
            except AssertionError:
                signals.emit(
                    Signal.SHOW_ERROR_MESSAGE,
                    traceback=format_exc(),
                    message="Encountered malformed config! Using defaults...",
                )
            except Exception as e:
                signals.emit(
                    Signal.SHOW_ERROR_MESSAGE,
                    traceback=format_exc(),
                    message="Encountered issue while parsing config! Using defaults...",
                )

    def default_settings(self) -> dict:
        return {
            "version": VERSION,
            "auto_backup_interval": 10,
            "num_per_decade_in_simulated_lines": 100,
            "default_test_settings": DEFAULT_TEST_SETTINGS.to_dict(),
            "default_fit_settings": DEFAULT_FIT_SETTINGS.to_dict(),
            "default_simulation_settings": DEFAULT_SIMULATION_SETTINGS.to_dict(),
            "colors": DEFAULT_COLORS,
            "markers": DEFAULT_MARKERS,
            "keybindings": list(map(lambda _: _.to_dict(), DEFAULT_KEYBINDINGS)),
        }

    def to_dict(self) -> dict:
        return parse_json(
            dump_json(
                {
                    "version": VERSION,
                    "auto_backup_interval": self.auto_backup_interval,
                    "num_per_decade_in_simulated_lines": self.num_per_decade_in_simulated_lines,
                    "default_test_settings": self.default_test_settings.to_dict(),
                    "default_fit_settings": self.default_fit_settings.to_dict(),
                    "default_simulation_settings": self.default_simulation_settings.to_dict(),
                    "colors": self.colors,
                    "markers": self.markers,
                    "keybindings": list(map(lambda _: _.to_dict(), self.keybindings)),
                }
            )
        )

    def save(self):
        if not isdir(self.config_dir_path):
            makedirs(self.config_dir_path)
        old_config: str = ""
        fp: IO
        if exists(self.config_path):
            with open(self.config_path, "r") as fp:
                old_config = fp.read().strip()
        new_config: str = dump_json(
            self.to_dict(),
            sort_keys=True,
            indent=2,
        ).strip()
        if new_config == old_config:
            return
        with open(self.config_path, "w") as fp:
            fp.write(new_config)

    def from_dict(self, settings: dict):
        self.auto_backup_interval = settings["auto_backup_interval"]
        self.num_per_decade_in_simulated_lines = settings[
            "num_per_decade_in_simulated_lines"
        ]
        self.default_test_settings = TestSettings.from_dict(
            settings["default_test_settings"]
        )
        self.default_fit_settings = FitSettings.from_dict(
            settings["default_fit_settings"]
        )
        self.default_simulation_settings = SimulationSettings.from_dict(
            settings["default_simulation_settings"]
        )
        self.markers = settings["markers"]
        marker_themes: Dict[str, int] = {
            "residuals_real": themes.residuals.real,
            "residuals_imaginary": themes.residuals.imaginary,
            "nyquist_data": themes.nyquist.data,
            "nyquist_simulation": themes.nyquist.simulation,
            "bode_magnitude_data": themes.bode.magnitude_data,
            "bode_magnitude_simulation": themes.bode.magnitude_simulation,
            "bode_phase_data": themes.bode.phase_data,
            "bode_phase_simulation": themes.bode.phase_simulation,
            "mu_Xps_mu": themes.mu_Xps.mu,
            "mu_Xps_Xps": themes.mu_Xps.Xps,
        }
        key: str
        theme: int
        for key, theme in marker_themes.items():
            themes.update_plot_series_theme_marker(theme, self.markers[key])
        self.colors = settings["colors"]
        color_themes: Dict[str, int] = {
            "residuals_real": themes.residuals.real,
            "residuals_imaginary": themes.residuals.imaginary,
            "nyquist_data": themes.nyquist.data,
            "nyquist_simulation": themes.nyquist.simulation,
            "bode_magnitude_data": themes.bode.magnitude_data,
            "bode_magnitude_simulation": themes.bode.magnitude_simulation,
            "bode_phase_data": themes.bode.phase_data,
            "bode_phase_simulation": themes.bode.phase_simulation,
            "mu_Xps_mu_criterion": themes.mu_Xps.mu_criterion,
            "mu_Xps_mu": themes.mu_Xps.mu,
            "mu_Xps_mu_highlight": themes.mu_Xps.mu_highlight,
            "mu_Xps_Xps": themes.mu_Xps.Xps,
            "mu_Xps_Xps_highlight": themes.mu_Xps.Xps_highlight,
        }
        for key, theme in color_themes.items():
            themes.update_plot_series_theme_color(theme, self.colors[key])
        self.keybindings = list(map(Keybinding.from_dict, settings["keybindings"]))
        self.validate_keybindings(self.keybindings)

    def check_type(self, user: Any, default: Any, key: str):
        assert type(user) == type(default), (user, default, key)
        if type(default) is list:
            user_types: set = set(list(map(type, user)))
            default_types: set = set(list(map(type, default)))
            assert user_types == default_types, (user_types, default_types, key)
        elif type(default) is dict:
            for key in default:
                if key in user:
                    self.check_type(user[key], default[key], key)

    def merge_dicts(self, user: dict, default: dict) -> dict:
        result: dict = {}
        key: str
        for key in default.keys():
            value: Optional[Any] = user.get(key)
            if value is None:
                result[key] = default[key]
                continue
            self.check_type(value, default[key], key)
            if type(value) is dict:
                result[key] = self.merge_dicts(value, default[key])
            else:
                result[key] = value
        return result

    def load(self):
        with open(self.config_path, "r") as fp:
            dictionary: dict = load_json(fp)
        assert "version" in dictionary
        version: int = dictionary["version"]
        assert version <= VERSION, f"{version=} > {VERSION=}"
        parsers: Dict[int, Callable] = {
            1: _parse_v1,
            2: _parse_v2,
        }
        assert version in parsers, f"{version=} not in {parsers.keys()=}"
        self.from_dict(self.merge_dicts(parsers[version](dictionary), self.to_dict()))

    def validate_keybindings(self, keybindings: List[Keybinding]):
        stringified: List[str] = list(map(str, keybindings))
        string: str
        for string in set(stringified):
            count: int = stringified.count(string)
            if count == 1:
                continue
            contexts: List[Set[Context]] = list(
                map(
                    lambda _: set(action_contexts[_.action]),
                    filter(lambda _: str(_) == string, keybindings),
                )
            )
            while contexts:
                a = contexts.pop(0)
                for b in contexts:
                    assert (
                        not a.issuperset(b)
                        and not a.issubset(b)
                        and Context.PROGRAM not in a
                        and Context.PROGRAM not in b
                    ), (
                        "The same keybinding has been applied to multiple actions in the same context or in overlapping contexts:\n- "
                        + "\n- ".join(
                            map(repr, filter(lambda _: str(_) == string, keybindings))
                        )
                    )
        actions: List[Action] = list(map(lambda _: _.action, keybindings))
        action: Action
        for action in set(actions):
            assert actions.count(action) == 1, (
                "Multiple keybindings have been applied to the same action:\n- "
                + "\n- ".join(
                    map(repr, filter(lambda _: _.action == action, keybindings))
                )
            )
