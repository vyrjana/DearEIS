#!/usr/bin/env python3
from os import getcwd, makedirs
from os.path import exists, join
from typing import IO
from api_documenter import (
    process,
    process_classes,
    process_functions,
)  # github.com/vyrjana/python-api-documenter
import deareis
import deareis.plot.mpl


def write_file(path: str, content: str):
    fp: IO
    with open(path, "w") as fp:
        fp.write(content)


def jekyll_header(title: str, link: str) -> str:
    return f"""---
layout: documentation
title: API - {title}
permalink: /api/{link}/
---
"""


if __name__ == "__main__":
    # PDF
    write_file(
        join(getcwd(), "API.md"),
        r"""---
header-includes:
    \usepackage{geometry}
    \geometry{a4paper, margin=2.5cm}
---
"""
        + process(
            title="DearEIS - API reference",
            description="""
_DearEIS_ is built on top of the `pyimpspec` package.
See the API reference for `pyimpspec` for information more information about classes and functions that are provided by that package and referenced below (e.g. the `Circuit` class).
            """.strip(),
            modules_to_document=[
                deareis,
                deareis.plot.mpl,
            ],
            minimal_classes=[
                deareis.Circuit,
            ],
            latex_pagebreak=True,
        ),
    )
    # Jekyll
    root_folder: str = join(getcwd(), "documentation")
    if not exists(root_folder):
        makedirs(root_folder)
    root_url: str = "https://vyrjana.github.io/DearEIS/api"
    # - index
    write_file(
        join(root_folder, "index.md"),
        f"""---
layout: documentation
title: API documentation
permalink: /api/
---

## API documentation

Check out [this Jupyter notebook](https://github.com/vyrjana/DearEIS/blob/main/examples/examples.ipynb) for examples of how to use the API.

- [Project]({root_url}/project)
- [Data set]({root_url}/data-set)
- [Kramers-Kronig testing]({root_url}/kramers-kronig)
- [Circuit]({root_url}/circuit)
- [Fitting]({root_url}/fitting)
- [Simulating]({root_url}/simulating)
- [Plotting]({root_url}/plotting)
  - [matplotlib]({root_url}/plot-mpl)

The DearEIS API is built upon the [pyimpspec](https://vyrjana.github.io/pyimpspec) package but the top-level module of the DearEIS API only exposes what is needed to, e.g., take an existing DearEIS project and plot various results (e.g., from equivalent circuit fitting).
Check out the API documentation for [pyimpspec](https://vyrjana.github.io/pyimpspec/api/) for information about, e.g., the various circuit element classes or how to perform Kramers-Kronig tests programmatically rather than via DearEIS' graphical user interface.
[This Jupyter notebook](https://github.com/vyrjana/pyimpspec/blob/main/examples/examples.ipynb) contains examples of how to use the pyimpspec API

""",
    )
    # Project
    write_file(
        join(root_folder, "project.md"),
        jekyll_header("project", "project")
        + """
`Project` objects can be created via the API for, e.g., the purposes of batch processing multiple experimental data files rather than manually loading files via the GUI program.
`Project` objects can also be used to, e.g., perform statistical analysis on multiple equivalent circuit fitting result and then generate a Markdown/LaTeX table.

"""
        + process_classes(
            classes_to_document=[
                deareis.Project,
            ],
            module_name="deareis",
        ),
    )
    # Data sets
    write_file(
        join(root_folder, "data-set.md"),
        jekyll_header("data set", "data-set")
        + """
The `DataSet` class in the DearEIS API differs slightly from the base class found in the pyimpspec API.
Check the [high-level functions of the pyimpspec API]() for information on how to read data files.

"""
        + process_classes(
            classes_to_document=[
                deareis.DataSet,
            ],
            module_name="deareis",
        ),
    )
    # Kramers-Kronig results
    write_file(
        join(root_folder, "kramers-kronig.md"),
        jekyll_header("Kramers-Kronig testing", "kramers-kronig")
        + process_classes(
            classes_to_document=[
                deareis.TestResult,
                deareis.TestSettings,
            ],
            module_name="deareis",
        ),
    )
    # Fit results
    write_file(
        join(root_folder, "fitting.md"),
        jekyll_header("fitting", "fitting")
        + process_classes(
            classes_to_document=[
                deareis.FitResult,
                deareis.FitSettings,
            ],
            module_name="deareis",
        ),
    )
    # Simulation results
    write_file(
        join(root_folder, "simulating.md"),
        jekyll_header("simulating", "simulating")
        + process_classes(
            classes_to_document=[
                deareis.SimulationResult,
                deareis.SimulationSettings,
            ],
            module_name="deareis",
        ),
    )
    # Plots
    write_file(
        join(root_folder, "plotting.md"),
        jekyll_header("plotting", "plotting")
        + process_classes(
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
        join(root_folder, "plot-mpl.md"),
        jekyll_header("plotting - matplotlib", "plot-mpl")
        + process(
            title="",
            modules_to_document=[
                deareis.plot.mpl,
            ],
            description="""
These functions are for basic visualization of various objects (e.g., `DataSet`, `TestResult`, and `FitResult`) using the [matplotlib](https://matplotlib.org/) package.
            """,
        ),
    )
