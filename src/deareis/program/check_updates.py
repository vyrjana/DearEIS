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

from time import sleep
from typing import Tuple
from requests import get
from requests.models import Response
from deareis.signals import Signal
import deareis.signals as signals
from deareis.version import PACKAGE_VERSION


def download_json() -> dict:
    url: str = "https://pypi.org/pypi/DearEIS/json"
    res: Response = get(url)
    res.raise_for_status()  # Check if there were any issues
    return res.json()


def parse_version(string: str) -> Tuple[int, int, int]:
    assert string.count(".") == 2, string
    return tuple(map(int, string.split(".")))  # type: ignore


def is_up_to_date(installed: str, pypi: str) -> bool:
    installed_major: int
    installed_minor: int
    installed_patch: int
    installed_major, installed_minor, installed_patch = parse_version(installed)
    pypi_major: int
    pypi_minor: int
    pypi_patch: int
    pypi_major, pypi_minor, pypi_patch = parse_version(pypi)
    if installed_major > pypi_major:
        return True
    elif installed_major < pypi_major:
        return False
    if installed_minor > pypi_minor:
        return True
    elif installed_minor < pypi_minor:
        return False
    if installed_patch > pypi_patch:
        return True
    elif installed_patch < pypi_patch:
        return False
    return True


def perform_update_check():
    signals.emit(
        Signal.SHOW_BUSY_MESSAGE,
        message="Checking PyPI",
    )
    json: dict = download_json()
    assert (
        "info" in json and "version" in json["info"]
    ), "Failed to extract version number from the response from PyPI!"
    pypi_version: str = json["info"]["version"]
    message: str = f"""
Already up-to-date!

     PyPI: {pypi_version}
Installed: {PACKAGE_VERSION}
    """.strip()
    if not is_up_to_date(PACKAGE_VERSION, pypi_version):
        message = f"""
Update available!

     PyPI: {pypi_version}
Installed: {PACKAGE_VERSION}
        """.strip()
    signals.emit(
        Signal.SHOW_BUSY_MESSAGE,
        message=message,
    )
    sleep(5)
    signals.emit(Signal.HIDE_BUSY_MESSAGE)
