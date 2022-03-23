# Copyright 2022 DearEIS developers
# DearEIS is licensed under the GPLv3 or later (https://www.gnu.org/licenses/gpl-3.0.html).
# The licenses of DearEIS' dependencies and/or sources of portions of code are included in
# the LICENSES folder.

from argparse import ArgumentParser, Namespace
from os.path import abspath


def parse() -> Namespace:
    parser: ArgumentParser = ArgumentParser(allow_abbrev=False)
    parser.add_argument(
        "-d",
        "--data-files",
        metavar="path",
        dest="data_files",
        nargs="*",
        default=[],
        help="",
    )
    parser.add_argument(
        "project_files", nargs="*", metavar="project", default=[], help=""
    )
    args: Namespace = parser.parse_args()
    if len(args.data_files) > 0:
        args.data_files = list(map(abspath, args.data_files))
    if len(args.project_files) > 0:
        args.project_files = list(map(abspath, args.project_files))
    return args
