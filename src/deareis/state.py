# Copyright 2022 DearEIS developers
# DearEIS is licensed under the GPLv3 or later (https://www.gnu.org/licenses/gpl-3.0.html).
# The licenses of DearEIS' dependencies and/or sources of portions of code are included in
# the LICENSES folder.

from os import makedirs, remove, walk
from os.path import exists, isdir, join
from typing import IO, List, Tuple
from xdg import (
    xdg_cache_home,  #  User-specific cache files
    xdg_data_home,  #   User-specific data files
    xdg_state_home,  #  User-specific state data files
)
from deareis.project import Project, serialize_state


class State:
    def __init__(self):
        self.state_directory_path: str = join(xdg_state_home(), "DearEIS")
        self.recent_projects_path: str = join(
            self.state_directory_path, "recent_projects.json"
        )
        self.projects_directory_path: str = join(self.state_directory_path, "projects")

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

    def serialize_projects(self, projects: List[Project]):
        if not isdir(self.projects_directory_path):
            makedirs(self.projects_directory_path)
        project: Project
        for project in projects:
            path: str = join(self.projects_directory_path, f"{project.uuid}")
            fp: IO
            with open(path, "w") as fp:
                fp.write(f"{project.path}\n{serialize_state(project, True)}")

    def get_serialized_projects(self) -> List[Tuple[str, str]]:
        files: List[str] = []
        for _, _, files in walk(self.projects_directory_path):
            break
        projects: List[Tuple[str, str]] = []
        path: str
        for path in map(lambda _: join(self.projects_directory_path, _), files):
            fp: IO
            with open(path, "r") as fp:
                lines: List[str] = fp.readlines()
                project_path: str = lines.pop(0)
                projects.append((project_path, "".join(lines),))
            remove(path)
        return projects


STATE: State = State()
