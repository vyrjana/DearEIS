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

import dearpygui.dearpygui as _dpg

_dpg.create_context()

from deareis.data import Project
from deareis.api.data import (
    DataSet,
    # - exceptions
    UnsupportedFileFormat,
    # - functions
    parse_data,
)
from deareis.api.circuit import (
    Circuit,
    CircuitBuilder,
    # - connections
    Connection,
    Parallel,
    Series,
    # - elements
    Element,
    Capacitor,
    ConstantPhaseElement,
    DeLevieFiniteLength,
    Gerischer,
    HavriliakNegami,
    Inductor,
    Resistor,
    Warburg,
    WarburgOpen,
    WarburgShort,
    # - exceptions
    ParsingError,
    UnexpectedCharacter,
    # - functions
    get_elements,
    parse_cdc,
)
from deareis.api.kramers_kronig import (
    TestResult,
    TestSettings,
    # - enums
    TestMode,
    Test,
    # - functions
    perform_test,
    perform_exploratory_tests,
)
from deareis.api.fitting import (
    FitResult,
    FitSettings,
    FittedParameter,
    # - enums
    CNLSMethod,
    Weight,
    # - exceptions
    FittingError,
    # - functions
    fit_circuit,
)
from deareis.api.simulation import (
    SimulationResult,
    SimulationSettings,
    # - functions
    simulate_spectrum,
)
from deareis.api.plotting import (
    PlotSeries,
    PlotSettings,
    # - enums
    PlotType,
)
from deareis.api.drt import (
    DRTResult,
    DRTSettings,
    # - enums
    DRTMethod,
    DRTMode,
    RBFShape,
    RBFType,
    # - exceptions
    DRTError,
    # - functions
    calculate_drt,
)
from deareis.api.plot import mpl  # matplotlib-based plotting
