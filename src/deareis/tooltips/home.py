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

from types import SimpleNamespace


home = SimpleNamespace(
    **{
        "load": """
Load this project.
    """.strip(),
        "new_project": """
Create a new project.
    """.strip(),
        "load_projects": """
Select project(s) to load. If one or more recent projects are marked, then those will be loaded instead.
    """.strip(),
        "merge_projects": """
Select project(s) to merge into a new project. If one or more recent projects are marked, then those will be merged instead.

If a project file has been copied and renamed, then this function can be used to reassign all of the universally uniqued identifiers (UUIDs) in the copy. This will then prevent DearEIS from mistaking the copy for the original if there is an attempt to load the copy when the original is already open (or vice versa).
    """.strip(),
        "clear_recent_projects": """
Clear the list of recent projects. If one or more recent projects are marked, then only those will be cleared from the list.
    """.strip(),
    }
)
