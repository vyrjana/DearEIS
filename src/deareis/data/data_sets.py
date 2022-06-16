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

from typing import Dict
from numpy import allclose
import pyimpspec


class DataSet(pyimpspec.DataSet):
    """
Extends `pyimpspec.DataSet` to reduce the amount of data written do disk and to recreate the data when loading from disk.
    """

    def __eq__(self, other) -> bool:
        # This is implemented because gui/data_sets.py checks if the newly selected DataSet is the
        # same as the current DataSet (if there even is one) and then decides whether to clear the
        # table of data points or if it just needs to be updated. Clearing the table causes the
        # scroll position to reset, which results in a bad UX when the user is modifying the
        # DataSet's mask.
        try:
            assert isinstance(other, pyimpspec.DataSet), other
            assert self.uuid == other.uuid, (
                self.uuid,
                other.uuid,
            )
            assert self.get_label() == other.get_label(), (
                self.get_label(),
                other.get_label(),
            )
            assert self.get_path() == other.get_path(), (
                self.get_path(),
                other.get_path(),
            )
            assert self.get_num_points(masked=None) == other.get_num_points(
                masked=None
            ), (
                self.get_num_points(masked=None),
                other.get_num_points(masked=None),
            )
            assert allclose(
                self.get_frequency(masked=None), other.get_frequency(masked=None)
            )
            assert allclose(
                self.get_impedance(masked=None), other.get_impedance(masked=None)
            )
        except AssertionError:
            return False
        return True

    def to_dict(self, session: bool = True) -> dict:
        # This is implemented to reduce the file sizes of projects.
        dictionary: dict = super().to_dict()
        if not session:
            dictionary["mask"] = {
                k: v for k, v in dictionary["mask"].items() if v is True
            }
        return dictionary

    @classmethod
    def from_dict(Class, dictionary: dict) -> "DataSet":
        # This is implemented to deal with the effects of the modified to_dict method.
        mask: Dict[str, bool] = dictionary.get("mask")
        if type(mask) is dict and len(mask) < len(dictionary["frequency"]):
            i: int
            for i in range(0, len(dictionary["frequency"])):
                if mask.get(str(i)) is not True:
                    mask[str(i)] = False
        return Class(**Class._parse(dictionary))
