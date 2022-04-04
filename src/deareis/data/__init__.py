# Copyright 2022 DearEIS developers
# DearEIS is licensed under the GPLv3 or later (https://www.gnu.org/licenses/gpl-3.0.html).
# The licenses of DearEIS' dependencies and/or sources of portions of code are included in
# the LICENSES folder.

from .kramers_kronig import TestResult, TestSettings
from .fitting import FitResult, FitSettings
from .simulation import SimulationResult, SimulationSettings
from .plotting import (
    PlotSettings,
    # PlotSeries,
    PlotType,
    plot_type_to_label,
)
