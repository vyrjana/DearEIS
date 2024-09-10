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

from pathlib import Path
from shutil import rmtree
from typing import (
    List,
    IO,
)


PARENT_DIRECTORY: Path = Path(__file__).parent


def update_file(src: Path, dst: Path):
    if not src.is_file():
        return

    src_contents: str = ""

    fp: IO
    with open(src, "r") as fp:
        src_contents = fp.read()

    if dst.is_file():
        with open(dst, "r") as fp:
            if fp.read() == src_contents:
                return

    with open(dst, "w") as fp:
        fp.write(src_contents)


def copy_additional_files(files: List[Path]):
    src_dir: Path = PARENT_DIRECTORY
    dst_dir: Path = src_dir.joinpath("src", "deareis")
    licenses_dir: Path = dst_dir.joinpath("LICENSES")
    if licenses_dir.is_dir():
        rmtree(licenses_dir)

    licenses_dir.mkdir(parents=True)

    path: Path
    for path in files:
        update_file(src_dir.joinpath(path), dst_dir.joinpath(path))


if __name__ == "__main__":
    data_files: List[Path] = list(map(Path, (
        "CHANGELOG.md",
        "CONTRIBUTORS",
        "COPYRIGHT",
        "LICENSE",
        "README.md",
    )))

    path: Path
    for path in PARENT_DIRECTORY.joinpath("LICENSES").glob("*"):
        data_files.append(path.relative_to(PARENT_DIRECTORY))

    assert all(map(lambda path: path.is_file(), data_files))

    copy_additional_files(data_files)

    # The changelog bundled with the package will also be updated when running this script.
    update_file(
        src=PARENT_DIRECTORY.joinpath("CHANGELOG.md"),
        dst=PARENT_DIRECTORY.joinpath("src", "deareis", "gui", "changelog", "CHANGELOG.md"),
    )

    # The licenses bundled with the package will also be updated when running this script.
    update_file(
        src=PARENT_DIRECTORY.joinpath("LICENSE"),
        dst=PARENT_DIRECTORY.joinpath("src", "deareis", "gui", "licenses", "LICENSE-DearEIS.txt"),
    )

    list(
        map(
            lambda path: update_file(
                src=path,
                dst=PARENT_DIRECTORY.joinpath("src", "deareis", "gui", "licenses", path.name),
            ),
            filter(lambda path: path.name.startswith("LICENSE-"), data_files),
        )
    )

    # Remove old dist files
    dist_output: Path = PARENT_DIRECTORY.joinpath("dist")
    if dist_output.is_dir():
        rmtree(dist_output)

    # Remove old documentation files to force a rebuild
    docs_output: Path = PARENT_DIRECTORY.joinpath("docs", "build")
    if docs_output.is_dir():
        rmtree(docs_output)
