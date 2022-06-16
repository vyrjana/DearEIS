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

from argparse import (
    ArgumentParser,
    Namespace,
    RawTextHelpFormatter,
)
from os.path import abspath
from deareis.version import PACKAGE_VERSION


def parse() -> Namespace:
    parser: ArgumentParser = ArgumentParser(
        allow_abbrev=False,
        formatter_class=RawTextHelpFormatter,
        description=f"""
DearEIS ({PACKAGE_VERSION})
A GUI program for analyzing, simulating, and visualizing impedance spectra.

Copyright (C) 2022 DearEIS developers

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

THERE IS NO WARRANTY FOR THE PROGRAM, TO THE EXTENT PERMITTED BY
APPLICABLE LAW.  EXCEPT WHEN OTHERWISE STATED IN WRITING THE COPYRIGHT
HOLDERS AND/OR OTHER PARTIES PROVIDE THE PROGRAM "AS IS" WITHOUT WARRANTY
OF ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING, BUT NOT LIMITED TO,
THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
PURPOSE.  THE ENTIRE RISK AS TO THE QUALITY AND PERFORMANCE OF THE PROGRAM
IS WITH YOU.  SHOULD THE PROGRAM PROVE DEFECTIVE, YOU ASSUME THE COST OF
ALL NECESSARY SERVICING, REPAIR OR CORRECTION.
""".strip(),
    )
    parser.add_argument(
        "-d",
        "--data-files",
        metavar="path",
        dest="data_files",
        nargs="*",
        default=[],
        help="Create a new project and load the specified data files as data sets in that project.",
    )
    parser.add_argument(
        "project_files",
        nargs="*",
        metavar="project",
        default=[],
        help="Load the specified project files.",
    )
    args: Namespace = parser.parse_args()
    if len(args.data_files) > 0:
        args.data_files = list(map(abspath, args.data_files))
    if len(args.project_files) > 0:
        args.project_files = list(map(abspath, args.project_files))
    return args
