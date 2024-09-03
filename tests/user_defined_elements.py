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

from numpy import inf
from pyimpspec import (
    Element,
    ElementDefinition,
    ParameterDefinition,
    register_element,
)


class Test(Element):
    def _impedance(self, f, A, B):
        return A * f + B * 1j


register_element(
    ElementDefinition(
        Class=Test,
        symbol="Userdefined",
        name="foo",
        description="bar",
        equation="A*f+B*I",
        parameters=[
            ParameterDefinition(
                symbol="A",
                unit="foo",
                description="bar",
                value=1.5,
                lower_limit=0.0,
                upper_limit=3.0,
                fixed=False,
            ),
            ParameterDefinition(
                symbol="B",
                unit="foo",
                description="baz",
                value=25e-6,
                lower_limit=-inf,
                upper_limit=inf,
                fixed=False,
            ),
        ],
    )
)
