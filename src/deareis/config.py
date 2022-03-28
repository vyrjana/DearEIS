# Copyright 2022 DearEIS developers
# DearEIS is licensed under the GPLv3 or later (https://www.gnu.org/licenses/gpl-3.0.html).
# The licenses of DearEIS' dependencies and/or sources of portions of code are included in
# the LICENSES folder.

import dearpygui.dearpygui as dpg
from json import dumps as dump_json, load as load_json
from os import makedirs
from os.path import exists, isdir, join
from typing import Callable, Dict, IO, List, Union
from xdg import (
    xdg_cache_home,  #  User-specific cache files
    xdg_config_home,  # User-specific configuration files
    xdg_data_home,  #   User-specific data files
)
from deareis.data.kramers_kronig import TestSettings, Test, Mode
from deareis.data.fitting import FitSettings
from deareis.data.simulation import SimulationSettings
from deareis.data.shared import Method, Weight


VERSION: int = 1


class Config:
    def __init__(self):
        self.config_dir_path: str = join(xdg_config_home(), "DearEIS")
        self.config_path: str = join(self.config_dir_path, "config.json")
        self.default_test_settings: TestSettings = TestSettings(
            Test.COMPLEX,
            Mode.EXPLORATORY,
            999,
            0.85,
            True,
            True,
            Method.LEASTSQ,
            1000,
        )
        self.default_fit_settings: FitSettings = FitSettings(
            "",
            Method.AUTO,
            Weight.AUTO,
            1000,
        )
        self.default_simulation_settings: SimulationSettings = SimulationSettings(
            "",
            1.0e-2,
            1.0e5,
            1,
        )
        self.colors: Dict[str, Union[List[int], List[float]]] = {
            "real_error": [
                238,
                51,
                119,
                190,
            ],
            "imag_error": [
                0,
                153,
                136,
                190,
            ],
            "nyquist_data": [
                51,
                187,
                238,
                190,
            ],
            "nyquist_sim": [
                238,
                51,
                119,
                190,
            ],
            "bode_magnitude_data": [
                51,
                187,
                238,
                190,
            ],
            "bode_magnitude_sim": [
                238,
                51,
                119,
                190,
            ],
            "bode_phase_data": [
                238,
                119,
                51,
                190,
            ],
            "bode_phase_sim": [
                0,
                153,
                136,
                190,
            ],
            "exploratory_mu_criterion": [
                255,
                255,
                255,
                128,
            ],
            "exploratory_mu": [
                238,
                51,
                119,
                190,
            ],
            "exploratory_mu_highlight": [
                51,
                187,
                238,
                190,
            ],
            "exploratory_xps": [
                0,
                153,
                136,
                190,
            ],
            "exploratory_xps_highlight": [
                238,
                119,
                51,
                190,
            ],
        }
        self.markers: Dict[str, int] = {
            "real_error": dpg.mvPlotMarker_Circle,
            "imag_error": dpg.mvPlotMarker_Square,
            "nyquist_data": dpg.mvPlotMarker_Circle,
            "nyquist_sim": dpg.mvPlotMarker_Cross,
            "bode_magnitude_data": dpg.mvPlotMarker_Circle,
            "bode_magnitude_sim": dpg.mvPlotMarker_Cross,
            "bode_phase_data": dpg.mvPlotMarker_Square,
            "bode_phase_sim": dpg.mvPlotMarker_Plus,
            "exploratory_mu": dpg.mvPlotMarker_Circle,
            "exploratory_xps": dpg.mvPlotMarker_Square,
        }
        if not exists(self.config_path):
            self.save()
        else:
            try:
                self.load()
            except AssertionError as e:
                print(e)
                print("\nEncountered malformed config! Using defaults...")
            except Exception as e:
                print(e)
                print("\nEncountered issue while parsing config! Using defaults...")

    def save(self):
        if not isdir(self.config_dir_path):
            makedirs(self.config_dir_path)
        old_config: str = ""
        fp: IO
        if exists(self.config_path):
            with open(self.config_path, "r") as fp:
                old_config = fp.read().strip()
        new_config: str = dump_json(
            {
                "version": VERSION,
                "default_test_settings": self.default_test_settings.to_dict(),
                "default_fit_settings": self.default_fit_settings.to_dict(),
                "default_simulation_settings": self.default_simulation_settings.to_dict(),
                "colors": self.colors,
                "markers": self.markers,
            },
            sort_keys=True,
            indent=2,
        ).strip()
        if new_config == old_config:
            return
        with open(self.config_path, "w") as fp:
            fp.write(new_config)

    def load(self):
        with open(self.config_path, "r") as fp:
            dictionary: dict = load_json(fp)
        assert "version" in dictionary
        version: int = dictionary["version"]
        assert version <= VERSION, f"{version=} > {VERSION=}"
        parsers: Dict[int, Callable] = {
            1: self._parse_v1,
        }
        assert version in parsers, f"{version=} not in {parsers.keys()=}"
        parsers[version](dictionary)

    def _parse_v1(self, dictionary: dict):
        assert type(dictionary) is dict
        if "default_test_settings" in dictionary:
            self.default_test_settings = TestSettings.from_dict(
                dictionary["default_test_settings"]
            )
        if "default_fit_settings" in dictionary:
            self.default_fit_settings = FitSettings.from_dict(
                dictionary["default_fit_settings"]
            )
        if "default_simulation_settings" in dictionary:
            self.default_simulation_settings = SimulationSettings.from_dict(
                dictionary["default_simulation_settings"]
            )
        if "colors" in dictionary:
            for k, v in dictionary["colors"].items():
                if k not in self.colors:
                    continue
                self.colors[k] = v
        if "markers" in dictionary:
            for k, v in dictionary["markers"].items():
                if k not in self.markers:
                    continue
                self.markers[k] = v


CONFIG: Config = Config()
