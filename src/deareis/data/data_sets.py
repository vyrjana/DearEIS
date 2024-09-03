# DearEIS is licensed under the GPLv3 or later (https://www.gnu.org/licenses/gpl-3.0.html).
# Copyright 2024 DearEIS developers
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

from numpy import allclose
import pyimpspec


class DataSet(pyimpspec.DataSet):
    """
    Extends `pyimpspec.DataSet` to implement data minimization when writing to disk and to recreate the data when loading from disk.
    Equality checks between DataSet instances is also modified.

    Parameters
    ----------
    frequencies: Frequencies
        A 1-dimensional array of frequencies in hertz.

    impedances: ComplexImpedances
        A 1-dimensional array of complex impedances in ohms.

    mask: Dict[int, bool], optional
        A mapping of integer indices to boolean values where a value of True means that the data point is to be omitted.

    path: str, optional
        The path to the file that has been parsed to generate this DataSet instance.

    label: str, optional
        The label assigned to this DataSet instance.

    uuid: str, optional
        The universivally unique identifier assigned to this DataSet instance.
        If empty, then one will be automatically assigned.
    """

    def __hash__(self) -> int:
        return int(self.uuid, 16)

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
                self.get_frequencies(masked=None),
                other.get_frequencies(masked=None),
            )
            assert allclose(
                self.get_impedances(masked=None),
                other.get_impedances(masked=None),
            )
        except AssertionError:
            return False
        
        return True

    def to_dict(self, session: bool = True) -> dict:
        """
        Return a dictionary that can be used to recreate an instance.

        Parameters
        ----------
        session: bool, optional
            If False, then a minimal dictionary is generated to reduce file size.

        Returns
        -------
        dict
        """
        assert type(session) is bool, session

        dictionary: dict = super().to_dict()

        if not session:
            # This helps to reduce the file sizes of projects.
            dictionary["mask"] = {
                k: v for k, v in dictionary["mask"].items() if v is True
            }
        
        return dictionary

    @classmethod
    def from_dict(Class, dictionary: dict) -> "DataSet":
        """
        Return a DataSet instance that has been created based off of a dictionary.

        Parameters
        ----------
        dictionary: dict
            Create an instance from a dictionary.
        """
        # This is implemented to deal with the effects of the modified to_dict method.
        if any(map(lambda _: type(_) is str, dictionary["mask"].keys())):
            dictionary["mask"] = {int(k): v for k, v in dictionary["mask"].items()}

        return Class(**Class._parse(dictionary))
