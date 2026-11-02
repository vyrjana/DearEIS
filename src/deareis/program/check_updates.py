# DearEIS is licensed under the GPLv3 or later (https://www.gnu.org/licenses/gpl-3.0.html).
# Copyright 2026 DearEIS developers
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
from typing import (
    Any,
    Tuple,
)
from http.client import HTTPResponse
from urllib.error import HTTPError
from urllib.request import urlopen
from json import (
    JSONDecodeError,
    loads,
)
from deareis.signals import Signal
import deareis.signals as signals
from deareis.version import PACKAGE_VERSION


def parse_version(string: str) -> Tuple[int, int, int]:
    if string.count(".") != 2:
        raise ValueError(f"Expected {string=} to contain two periods (i.e., 'major.minor.patch')!")

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


def download_json() -> Tuple[dict, str]:
    url: str = "https://pypi.org/pypi/DearEIS/json"

    try:
        res: HTTPResponse = urlopen(url)
    except HTTPError as err:
        return (
            {},
            f"""
{str(err)}
when checking {url}
            """.strip(),
        )

    try:
        json: dict = loads(res.read())
    except JSONDecodeError:
        return (
            {},
            f"""
Failed to parse JSON from {url}
            """.strip(),
        )

    return (
        json,
        "",
    )


def extract_pypi_version(json: dict) -> Tuple[str, str]:
    info: Any = json.get("info", {})
    if isinstance(info, dict):
        version: Any = info.get("version", "")
        if isinstance(version, str):
            return (
                version,
                "",
            )

    return (
        "",
        "Failed to extract version number from the response from PyPI!"
    )


def perform_update_check():
    signals.emit(
        Signal.SHOW_BUSY_MESSAGE,
        message="Checking PyPI",
    )

    json: dict
    message: str
    json, message = download_json()
    if json:
        pypi_version: str
        pypi_version, message = extract_pypi_version(json=json)
        if pypi_version:
            if not is_up_to_date(PACKAGE_VERSION, pypi_version):
                message = f"""
Update available!

 PyPI: {pypi_version}
Installed: {PACKAGE_VERSION}
                """.strip()
            else:
                message = f"""
Already up-to-date!

Available: {pypi_version}
Installed: {PACKAGE_VERSION}
                """.strip()

    signals.emit(
        Signal.SHOW_BUSY_MESSAGE,
        message=message,
    )
    sleep(5)
    signals.emit(Signal.HIDE_BUSY_MESSAGE)
