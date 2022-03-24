# Copyright 2022 DearEIS developers
# DearEIS is licensed under the GPLv3 or later (https://www.gnu.org/licenses/gpl-3.0.html).
# The licenses of DearEIS' dependencies and/or sources of portions of code are included in
# the LICENSES folder.

from os import makedirs
from os.path import exists, isdir, join
from typing import IO, List
from xdg import (
    xdg_cache_home,  #  User-specific cache files
    xdg_data_home,  #   User-specific data files
    xdg_state_home,  #  User-specific state data files
)


class State:
    def __init__(self):
        self.state_directory_path: str = join(xdg_state_home(), "DearEIS")
        self.recent_projects_path: str = join(
            self.state_directory_path, "recent_projects.json"
        )

    def get_data_directory(self) -> str:
        return str(xdg_data_home())

    def get_recent_projects(self) -> List[str]:
        if not exists(self.recent_projects_path):
            return []
        fp: IO
        with open(self.recent_projects_path, "r") as fp:
            return list(
                filter(lambda _: _ != "" and exists(_), map(str.strip, fp.readlines()))
            )

    def update_recent_projects(self, paths: List[str]):
        assert type(paths) is list and all(map(lambda _: type(_) is str, paths))
        if not exists(self.recent_projects_path):
            if not isdir(self.state_directory_path):
                makedirs(self.state_directory_path)
        if len(paths) == 0:
            return
        fp: IO
        with open(self.recent_projects_path, "w") as fp:
            fp.write("\n".join(paths))


STATE: State = State()
