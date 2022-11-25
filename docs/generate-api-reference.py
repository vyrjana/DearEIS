#!/usr/bin/env python3
from os import makedirs
from os.path import (
    dirname,
    exists,
    join,
)
from typing import IO
import deareis

# Import github.com/vyrjana/python-api-documenter, which has been added as a submodule
import sys

submodule_path: str = join(dirname(__file__), "api_documenter", "src")
assert exists(submodule_path), submodule_path
sys.path.append(submodule_path)
from api_documenter import (
    process,
    process_classes,
    process_functions,
)


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
    version: str = ""
    with open(join(dirname(dirname(__file__)), "version.txt"), "r") as fp:
        version = fp.read().strip()
    assert version.strip() != ""
    output_dir: str = dirname(__file__)
    root_folder: str = join(output_dir, "documentation")
    if not exists(root_folder):
        makedirs(root_folder)
    multiprocessing_disclaimer: str = """
**NOTE!** The API makes use of multiple processes where possible to perform tasks in parallel. Functions that implement this parallelization have a `num_procs` keyword argument that can be used to override the maximum number of processes allowed. Using this keyword argument should not be necessary for most users under most circumstances.

If NumPy is linked against a multithreaded linear algebra library like OpenBLAS or MKL, then this may in some circumstances result in unusually poor performance despite heavy CPU utilization. It may be possible to remedy the issue by specifying a lower number of processes via the `num_procs` keyword argument and/or limiting the number of threads that, e.g., OpenBLAS should use by setting the appropriate environment variable (e.g., `OPENBLAS_NUM_THREADS`). Again, this should not be necessary for most users and reporting this as an issue to the pyimpspec or DearEIS repository on GitHub would be preferred.
"""
    # Markdown
    write_file(
        join(root_folder, "API.md"),
        process(
            title=f"DearEIS - API reference ({version})",
            description=f"""
_DearEIS_ is built on top of the `pyimpspec` package.
See the [API reference for `pyimpspec`](https://vyrjana.github.io/pyimpspec/api/) for information more information about classes and functions that are provided by that package and referenced below (e.g. the `Circuit` class).
The API of DearEIS can be used for automatic some tasks (e.g., batch importing data or batch exporting plots).
However, the `pyimpspec` API may be a bit easier to use if you just want to have an API to use in Python scripts or Jupyter notebooks.
Primarily because the DearEIS API uses settings objects (e.g., `DRTSettings` that can be (de)serialized easily) instead of keyword arguments in the function signatures.

{multiprocessing_disclaimer}
            """.strip(),
            modules_to_document=[
                deareis,
                deareis.mpl,
            ],
            minimal_classes=[
                # Connections
                deareis.Parallel,
                deareis.Series,
                # Elements
                deareis.Capacitor,
                deareis.ConstantPhaseElement,
                deareis.Gerischer,
                deareis.HavriliakNegami,
                deareis.HavriliakNegamiAlternative,
                deareis.Inductor,
                deareis.ModifiedInductor,
                deareis.Resistor,
                deareis.Warburg,
                deareis.WarburgOpen,
                deareis.WarburgShort,
                deareis.DeLevieFiniteLength,
                # Exceptions
                deareis.DRTError,
                deareis.FittingError,
                deareis.ParsingError,
                deareis.UnexpectedCharacter,
            ],
            objects_to_ignore=[
                deareis.Project.parse,
                deareis.Project.update,
            ],
            latex_pagebreak=False,
        ),
    )
    # Jekyll
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
A single Markdown file of the API reference is available [here](https://raw.githubusercontent.com/vyrjana/DearEIS/gh-pages/documentation/API.md).
The [`pyimpspec` API](https://vyrjana.github.io/pyimpspec/api/) may be a bit easier to use if you just want to have an API to use in Python scripts or Jupyter notebooks.
Primarily because the DearEIS API uses settings objects (e.g., `DRTSettings` that can be (de)serialized easily) instead of keyword arguments in the function signatures.

- [Project]({root_url}/project)
- [Data set]({root_url}/data-set)
- [Kramers-Kronig testing]({root_url}/kramers-kronig)
- [Distribution of relaxation times]({root_url}/drt)
- [Circuit]({root_url}/circuit)
- [Elements]({root_url}/elements)
- [Fitting]({root_url}/fitting)
- [Simulating]({root_url}/simulating)
- [Plotting]({root_url}/plotting)
  - [matplotlib]({root_url}/plot-mpl)

The DearEIS API is built upon the [pyimpspec](https://vyrjana.github.io/pyimpspec) package.

{multiprocessing_disclaimer}

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
            objects_to_ignore=[
                deareis.Project.parse,
                deareis.Project.update,
            ],
            module_name="deareis",
        ),
    )
    # Data sets
    write_file(
        join(root_folder, "data-set.md"),
        jekyll_header("data set", "data-set")
        + process(
            title="",
            modules_to_document=[
                deareis.api.data,
            ],
            minimal_classes=[
                deareis.UnsupportedFileFormat,
            ],
            description="""
The `DataSet` class in the DearEIS API differs slightly from the base class found in the pyimpspec API.
The `parse_data` function is a wrapper for the corresponding function in pyimpspec's API with the only difference being that the returned `DataSet` instances are the variant used by DearEIS.
            """,
        ),
    )
    # Kramers-Kronig results
    write_file(
        join(root_folder, "kramers-kronig.md"),
        jekyll_header("Kramers-Kronig testing", "kramers-kronig")
        + process(
            title="",
            modules_to_document=[
                deareis.api.kramers_kronig,
            ],
            objects_to_ignore=[
                deareis.DataSet,
            ],
            description="",
        ),
    )
    # Circuit
    write_file(
        join(root_folder, "circuit.md"),
        jekyll_header("Circuit", "circuit")
        + process(
            title="",
            modules_to_document=[
                deareis.api.circuit,
            ],
            minimal_classes=[
                deareis.Parallel,
                deareis.Series,
                deareis.ParsingError,
                deareis.UnexpectedCharacter,
            ],
            objects_to_ignore=[
                deareis.get_elements,
                deareis.Element,
            ]
            + list(deareis.get_elements().values()),
            description="""
Circuits can be generated in one of two ways:
- by parsing a circuit description code (CDC)
- by using the `CircuitBuilder` class

The basic syntax for CDCs is fairly straighforward:

```python
# A resistor connected in series with a resistor and a capacitor connected in parallel
circuit: deareis.Circuit = deareis.parse_cdc("[R(RC)]")
```

An extended syntax, which allows for defining initial values, lower/upper limits, and labels, is also supported:

```python
circuit: deareis.Circuit = deareis.parse_cdc("[R{R=50:sol}(R{R=250f:ct}C{C=1.5e-6/1e-6/2e-6:dl})]")
```

Alternatively, the `CircuitBuilder` class can be used:

```python
with deareis.CircuitBuilder() as builder:
    builder += (
        deareis.Resistor(R=50)
        .set_label("sol")
    )
    with builder.parallel() as parallel:
        parallel += (
            deareis.Resistor(R=250)
            .set_fixed("R", True)
        )
        parallel += (
            deareis.Capacitor(C=1.5e-6)
            .set_label("dl")
            .set_lower_limit("C", 1e-6)
            .set_upper_limit("C", 2e-6)
        )
circuit: deareis.Circuit = builder.to_circuit()
```

"""
            + f"Information about the supported circuit elements can be found [here]({root_url}/elements).\n\n",
        ),
    )
    # Elements
    write_file(
        join(root_folder, "elements.md"),
        jekyll_header("Elements", "elements")
        + process(
            title="",
            modules_to_document=[
                deareis.api.circuit,
            ],
            minimal_classes=list(deareis.get_elements().values()),
            objects_to_ignore=[
                deareis.Circuit,
                deareis.CircuitBuilder,
                deareis.Connection,
                deareis.Parallel,
                deareis.Series,
                deareis.ParsingError,
                deareis.UnexpectedCharacter,
                deareis.parse_cdc,
            ],
            description="",
        ),
    )
    # Fitting
    write_file(
        join(root_folder, "fitting.md"),
        jekyll_header("fitting", "fitting")
        + process(
            title="",
            modules_to_document=[
                deareis.api.fitting,
            ],
            objects_to_ignore=[
                deareis.Circuit,
                deareis.DataSet,
            ],
            minimal_classes=[
                deareis.FittingError,
            ],
            description="",
        ),
    )
    # Simulating
    write_file(
        join(root_folder, "simulating.md"),
        jekyll_header("simulating", "simulating")
        + process(
            title="",
            modules_to_document=[
                deareis.api.simulation,
            ],
            description="",
        ),
    )
    # Plots
    write_file(
        join(root_folder, "plotting.md"),
        jekyll_header("plotting", "plotting")
        + process(
            title="",
            modules_to_document=[
                deareis.api.plotting,
            ],
            minimal_classes=[
                deareis.PlotType,
            ],
            description="",
        ),
    )
    # DRT results
    write_file(
        join(root_folder, "drt.md"),
        jekyll_header("drt", "drt")
        + process(
            title="",
            modules_to_document=[
                deareis.api.drt,
            ],
            objects_to_ignore=[
                deareis.DataSet,
            ],
            minimal_classes=[
                deareis.DRTError,
            ],
            description="",
        ),
    )
    # Plotting - matplotlib
    write_file(
        join(root_folder, "plot-mpl.md"),
        jekyll_header("plotting - matplotlib", "plot-mpl")
        + process(
            title="",
            modules_to_document=[
                deareis.mpl,
            ],
            description="""
These functions are for basic visualization of various objects (e.g., `DataSet`, `TestResult`, and `FitResult`) using the [matplotlib](https://matplotlib.org/) package.
            """,
        ),
    )
