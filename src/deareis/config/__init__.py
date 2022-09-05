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

from json import (
    dumps as dump_json,
    load as load_json,
    loads as parse_json,
)
from os import makedirs
from os.path import (
    exists,
    isdir,
    join,
)
from traceback import format_exc
from typing import (
    Any,
    Callable,
    Dict,
    IO,
    List,
    Optional,
    Set,
)
from xdg import (
    xdg_cache_home,  #  User-specific cache files
    xdg_config_home,  # User-specific configuration files
    xdg_data_home,  #   User-specific data files
)
from deareis.keybindings import Keybinding
from deareis.data.plotting import PlotExportSettings
from deareis.data import (
    DRTSettings,
    FitSettings,
    SimulationSettings,
    TestSettings,
)
from deareis.enums import (
    Action,
    Context,
    action_contexts,
)
import deareis.themes as themes
from deareis.signals import Signal
import deareis.signals as signals
from .defaults import (
    DEFAULT_KEYBINDINGS,
    DEFAULT_MARKERS,
    DEFAULT_COLORS,
    DEFAULT_TEST_SETTINGS,
    DEFAULT_FIT_SETTINGS,
    DEFAULT_SIMULATION_SETTINGS,
    DEFAULT_DRT_SETTINGS,
    DEFAULT_PLOT_EXPORT_SETTINGS,
)


VERSION: int = 4


def _parse_v4(dictionary: dict) -> dict:
    # TODO: Update when VERSION is incremented to 4
    return dictionary


def _parse_v3(dictionary: dict) -> dict:
    dictionary.update(
        {
            "version": 4,
            "default_drt_settings": dictionary.get(
                "default_drt_settings",
                DEFAULT_DRT_SETTINGS.to_dict(),
            ),
            "default_plot_export_settings": dictionary.get(
                "default_plot_export_settings",
                DEFAULT_PLOT_EXPORT_SETTINGS.to_dict(),
            ),
        }
    )
    del dictionary["export_units"]
    del dictionary["export_width"]
    del dictionary["export_height"]
    del dictionary["export_dpi"]
    del dictionary["export_preview"]
    del dictionary["export_title"]
    del dictionary["export_legend"]
    del dictionary["export_legend_location"]
    del dictionary["export_grid"]
    del dictionary["export_tight"]
    del dictionary["export_num_per_decade"]
    del dictionary["export_extension"]
    del dictionary["export_experimental_clear_registry"]
    del dictionary["export_experimental_disable_previews"]
    return _parse_v4(dictionary)


def _parse_v2(dictionary: dict) -> dict:
    return _parse_v3(
        {
            "version": 3,
            "auto_backup_interval": dictionary["auto_backup_interval"],
            "num_per_decade_in_simulated_lines": dictionary[
                "num_per_decade_in_simulated_lines"
            ],
            "markers": dictionary["markers"],
            "colors": dictionary["colors"],
            "default_test_settings": dictionary["default_test_settings"],
            "default_fit_settings": dictionary["default_fit_settings"],
            "default_drt_settings": dictionary.get(
                "default_drt_settings",
                DEFAULT_DRT_SETTINGS.to_dict(),
            ),
            "default_simulation_settings": dictionary["default_simulation_settings"],
            "export_units": dictionary.get("export_units", 1),
            "export_width": dictionary.get("export_width", 10.0),
            "export_height": dictionary.get("export_height", 6.0),
            "export_dpi": dictionary.get("export_dpi", 100),
            "export_preview": dictionary.get("export_preview", 4),
            "export_title": dictionary.get("export_title", True),
            "export_legend": dictionary.get("export_legend", True),
            "export_legend_location": dictionary.get("export_legend_location", 0),
            "export_grid": dictionary.get("export_grid", False),
            "export_tight": dictionary.get("export_tight", False),
            "export_num_per_decade": dictionary.get("export_num_per_decade", 100),
            "export_extension": dictionary.get("export_extension", 4),
            "export_experimental_clear_registry": dictionary.get(
                "export_experimental_clear_registry",
                True,
            ),
            "export_experimental_disable_previews": dictionary.get(
                "export_experimental_disable_previews",
                False,
            ),
        }
    )


def _parse_v1(dictionary: dict) -> dict:
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
            "default_drt_settings": DEFAULT_DRT_SETTINGS.to_dict(),
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
        self.default_drt_settings: DRTSettings = None  # type: ignore
        self.default_simulation_settings: SimulationSettings = None  # type: ignore
        self.default_plot_export_settings: PlotExportSettings = None  # type: ignore
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
            except Exception:
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
            "default_drt_settings": DEFAULT_DRT_SETTINGS.to_dict(),
            "default_plot_export_settings": DEFAULT_PLOT_EXPORT_SETTINGS.to_dict(),
            "default_simulation_settings": DEFAULT_SIMULATION_SETTINGS.to_dict(),
            "colors": DEFAULT_COLORS,
            "markers": DEFAULT_MARKERS,
            "keybindings": list(map(lambda _: _.to_dict(), DEFAULT_KEYBINDINGS)),
        }

    def to_dict(self) -> dict:
        return parse_json(
            dump_json(  # This is done to get new instances in memory
                {
                    "version": VERSION,
                    "auto_backup_interval": self.auto_backup_interval,
                    "num_per_decade_in_simulated_lines": self.num_per_decade_in_simulated_lines,
                    "default_test_settings": self.default_test_settings.to_dict(),
                    "default_fit_settings": self.default_fit_settings.to_dict(),
                    "default_drt_settings": self.default_drt_settings.to_dict(),
                    "default_simulation_settings": self.default_simulation_settings.to_dict(),
                    "default_plot_export_settings": self.default_plot_export_settings.to_dict(),
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
            settings.get(
                "default_test_settings",
                DEFAULT_TEST_SETTINGS.to_dict(),
            )
        )
        self.default_fit_settings = FitSettings.from_dict(
            settings.get(
                "default_fit_settings",
                DEFAULT_FIT_SETTINGS.to_dict(),
            )
        )
        self.default_drt_settings = DRTSettings.from_dict(
            settings.get(
                "default_drt_settings",
                DEFAULT_DRT_SETTINGS.to_dict(),
            )
        )
        self.default_simulation_settings = SimulationSettings.from_dict(
            settings.get(
                "default_simulation_settings",
                DEFAULT_SIMULATION_SETTINGS.to_dict(),
            )
        )
        self.default_plot_export_settings = PlotExportSettings.from_dict(
            settings.get(
                "default_plot_export_settings",
                DEFAULT_PLOT_EXPORT_SETTINGS.to_dict(),
            )
        )
        self.markers = settings["markers"]
        marker_themes: Dict[str, int] = {
            "bode_magnitude_data": themes.bode.magnitude_data,
            "bode_magnitude_simulation": themes.bode.magnitude_simulation,
            "bode_phase_data": themes.bode.phase_data,
            "bode_phase_simulation": themes.bode.phase_simulation,
            "impedance_imaginary_data": themes.impedance.imaginary_data,
            "impedance_imaginary_simulation": themes.impedance.imaginary_simulation,
            "impedance_real_data": themes.impedance.real_data,
            "impedance_real_simulation": themes.impedance.real_simulation,
            "mu_Xps_Xps": themes.mu_Xps.Xps,
            "mu_Xps_mu": themes.mu_Xps.mu,
            "nyquist_data": themes.nyquist.data,
            "nyquist_simulation": themes.nyquist.simulation,
            "residuals_imaginary": themes.residuals.imaginary,
            "residuals_real": themes.residuals.real,
        }
        key: str
        theme: int
        for key, theme in marker_themes.items():
            themes.update_plot_series_theme_marker(theme, self.markers[key])
        self.colors = settings["colors"]
        color_themes: Dict[str, int] = {
            "bode_magnitude_data": themes.bode.magnitude_data,
            "bode_magnitude_simulation": themes.bode.magnitude_simulation,
            "bode_phase_data": themes.bode.phase_data,
            "bode_phase_simulation": themes.bode.phase_simulation,
            "drt_credible_intervals": themes.drt.credible_intervals,
            "drt_imaginary_gamma": themes.drt.imaginary_gamma,
            "drt_mean_gamma": themes.drt.mean_gamma,
            "drt_real_gamma": themes.drt.real_gamma,
            "impedance_imaginary_data": themes.impedance.imaginary_data,
            "impedance_imaginary_simulation": themes.impedance.imaginary_simulation,
            "impedance_real_data": themes.impedance.real_data,
            "impedance_real_simulation": themes.impedance.real_simulation,
            "mu_Xps_Xps": themes.mu_Xps.Xps,
            "mu_Xps_Xps_highlight": themes.mu_Xps.Xps_highlight,
            "mu_Xps_mu": themes.mu_Xps.mu,
            "mu_Xps_mu_criterion": themes.mu_Xps.mu_criterion,
            "mu_Xps_mu_highlight": themes.mu_Xps.mu_highlight,
            "nyquist_data": themes.nyquist.data,
            "nyquist_simulation": themes.nyquist.simulation,
            "residuals_imaginary": themes.residuals.imaginary,
            "residuals_real": themes.residuals.real,
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
            3: _parse_v3,
            4: _parse_v4,
        }
        assert version in parsers, f"{version=} not in {parsers.keys()=}"
        dictionary = self.merge_dicts(parsers[version](dictionary), self.to_dict())
        self.from_dict(dictionary)

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
