#!/usr/bin/env python3
from os import getcwd
from os.path import join
from typing import IO
from api_documenter import process, process_classes, process_functions  # github.com/vyrjana/python-api-documenter
import deareis
import deareis.plot.mpl


def write_file(path: str, content: str):
    fp: IO
    with open(path, "w") as fp:
        fp.write(content)


if __name__ == "__main__":
    # Project
    write_file(
        join(getcwd(), "API-project.md"),
        process_classes(
            classes_to_document=[
                deareis.Project,
            ],
            module_name="deareis",
        ),
    )
    # Data sets
    write_file(
        join(getcwd(), "API-data-sets.md"),
        process_classes(
            classes_to_document=[
                deareis.DataSet,
            ],
            module_name="deareis",
        ),
    )
    # Kramers-Kronig results
    write_file(
        join(getcwd(), "API-test-results.md"),
        process_classes(
            classes_to_document=[
                deareis.TestResult,
                deareis.TestSettings,
            ],
            module_name="deareis",
        ),
    )
    # Fit results
    write_file(
        join(getcwd(), "API-fit-results.md"),
        process_classes(
            classes_to_document=[
                deareis.FitResult,
                deareis.FitSettings,
            ],
            module_name="deareis",
        ),
    )
    # Simulation results
    write_file(
        join(getcwd(), "API-simulation-results.md"),
        process_classes(
            classes_to_document=[
                deareis.SimulationResult,
                deareis.SimulationSettings,
            ],
            module_name="deareis",
        ),
    )
    # Plots
    write_file(
        join(getcwd(), "API-plots.md"),
        process_classes(
            classes_to_document=[
                deareis.PlotSettings,
                deareis.PlotSeries,
                deareis.PlotType,
            ],
            module_name="deareis",
        ),
    )
    # Plotting - matplotlib
    write_file(
        join(getcwd(), "API-plot.mpl.md"),
        process(
            title="API - deareis.plot.mpl",
            modules_to_document=[
                deareis.plot.mpl,
            ],
        ),
    )
