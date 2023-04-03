# DearEIS is licensed under the GPLv3 or later (https://www.gnu.org/licenses/gpl-3.0.html).
# Copyright 2023 DearEIS developers
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

from dataclasses import dataclass
from datetime import date
from os import (
    makedirs,
    remove,
    walk,
)
from os.path import (
    exists,
    isdir,
    join,
    splitext,
)
from re import search
from shutil import (
    copy,
    copytree,
    rmtree,
)
from typing import (
    IO,
    List,
    Match,
    Optional,
    Union,
)


def copy_html(src: str, dst: str):
    if exists(dst):
        rmtree(dst)
    files: List[str] = []
    for _, _, files in walk(src):
        break
    assert len(files) > 0
    files = [
        _
        for _ in files
        if not _.startswith(".")
        and splitext(_)[1]
        in (
            ".html",
            ".js",
            ".png",
            ".py",
            ".svg",
        )
    ]
    dirs: List[str] = ["_images", "_static", "_sources"]
    if not isdir(dst):
        makedirs(dst)
    name: str
    for name in files:
        copy(join(src, name), join(dst, name))
    for name in dirs:
        copytree(join(src, name), join(dst, name))


def copy_pdf(src: str, dst: str, name: str, version_path: str):
    version: str = ""
    fp: IO
    with open(version_path, "r") as fp:
        version = fp.read().strip().replace(".", "-")
    assert version != ""
    ext: str = splitext(src)[1]
    dst = join(dst, f"{name}-{version}{ext}")
    if exists(dst):
        remove(dst)
    copy(src, dst)


@dataclass(frozen=True)
class Version:
    major: int
    minor: int
    patch: int
    year: int
    month: int
    day: int


def validate_changelog(path: str):
    def parse_version(match: Match) -> Version:
        return Version(
            major=int(match.group("major")),
            minor=int(match.group("minor")),
            patch=int(match.group("patch")),
            year=int(match.group("year")),
            month=int(match.group("month")),
            day=int(match.group("day")),
        )

    def validate_date(
        version: Version, comparison: Union[Version, date] = date.today()
    ):
        assert version.year <= comparison.year, (version, comparison)
        assert 1 <= version.month <= 12, version
        assert 1 <= version.day <= 31, version
        if version.year == comparison.year:
            assert version.month <= comparison.month, (version, comparison)
            if version.month == comparison.month:
                assert version.day <= comparison.day, (version, comparison)

    def validate_version(earlier: Version, current: Version):
        assert earlier.major <= current.major, (earlier, current)
        if earlier.major < current.major:
            return
        assert earlier.minor <= current.minor, (earlier, current)
        if earlier.minor < current.minor:
            return
        assert earlier.patch < current.patch, (earlier, current)

    assert exists(path), path
    fp: IO
    with open(path, "r") as fp:
        lines: List[str] = fp.readlines()
    pattern: str = (
        r"# (?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)"
        r" \((?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})\)"
    )
    try:
        match: Optional[Match] = search(pattern, lines.pop(0))
        assert match is not None, pattern
        versions: List[Version] = list(
            map(
                parse_version,
                [match]
                + [
                    match
                    for match in map(lambda _: search(pattern, _), lines)
                    if match is not None
                ],
            )
        )
        list(map(validate_date, versions))
        while len(versions) > 1:
            current: Version = versions.pop(0)
            earlier = versions[0]
            validate_date(earlier, current)
            validate_version(earlier, current)
    except AssertionError:
        raise Exception("The changelog needs to be updated!")


if __name__ == "__main__":
    copy_html(
        src="./docs/build/html",
        dst="./dist/html",
    )
    copy_pdf(
        src="./docs/build/latex/latex/deareis.pdf",
        dst="./dist",
        name="DearEIS",
        version_path="./version.txt",
    )
    validate_changelog("./CHANGELOG.md")
