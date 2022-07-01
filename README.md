# DearEIS

A GUI program for analyzing, simulating, and visualizing impedance spectra.


## Table of contents

- [About](#about)
- [Getting started](#getting-started)
	- [Installing](#installing)
	- [Running](#running)
	- [Settings and keybindings](#settings-and-keybindings)
- [Features](#features)
	- [Projects](#projects)
	- [Data sets](#data-sets)
	- [Data validation](#data-validation)
	- [Circuit fitting and simulation](#circuit-fitting-and-simulation)
	- [Visualization](#visualization)
	- [Scripting](#scripting)
- [Changelog](#changelog)
- [Contributing](#contributing)
- [License](#license)


## About

_DearEIS_ is a Python package that includes both a program with a graphical user interface (GUI) and an application programming interface (API) for working with impedance spectra.
The target audience is researchers who use electrochemical impedance spectroscopy (EIS) though the program may also be useful in educational settings.
The program implements:

- projects that can contain multiple experimental data sets
- reading experimental data from several different data formats
- validation of impedance spectra by checking if the data is Kramers-Kronig transformable
- construction of equivalent circuits either by parsing a circuit definition code or by using the included graphical editor
- equivalent circuit fitting
- simulation of impedance spectra
- composition of complex plots

Check out the [wiki](https://github.com/vyrjana/DearEIS/wiki/Screenshots) for screenshots of the GUI.
See the [Features](#features) section and [_pyimpspec_](https://github.com/vyrjana/pyimpspec) for more details about e.g. supported data formats and implementation details.

The API is an extension of the API provided by [_pyimpspec_](https://github.com/vyrjana/pyimpspec) and can be used to e.g. perform batch processing.
Documentation about the API can be found on the [wiki](https://github.com/vyrjana/DearEIS/wiki).
[This Jupyter notebook](examples/examples.ipynb) contains some examples of how to use the API though the focus is on the additions available in the _DearEIS_ API.
See the [pyimpspec](https://github.com/vyrjana/pyimpspec) repository for examples and documentation regarding its API.

If you encounter issues, then please open an issue on [GitHub](https://github.com/vyrjana/DearEIS/issues).


## Getting started

### Installing

The latest version of _DearEIS_ requires **Python 3.7 or newer (64-bit)** and the most straightforward way to install _DearEIS_ is by using [_pip_](https://pip.pypa.io/en/stable/).
Make sure that _pip_ is installed first and then type the following command into a terminal of your choice (e.g. _PowerShell_ in Windows).

```
pip install deareis
```

Newer versions of _DearEIS_ can be installed at a later date by appending the `-U` option to the command:

```
pip install deareis -U
```

Supported platforms:
- Linux
	- Primary development and testing platform.
- Windows
	- Tested on Windows 10 (x86-64).

The package **may** also work on other platforms (e.g. MacOS) depending on whether or not those platforms are supported by _DearEIS_' [dependencies](setup.py).


### Running

Once installed, _DearEIS_ can be started e.g. from a terminal or the Windows start menu by searching for the command `deareis`.

There is also a `deareis-debug` command that prints additional information to the terminal and can be useful when troubleshooting issues.


### Settings and keybindings

_DearEIS_ has several user-configurable settings.
It is possible to configure the default values of the settings on the Kramers-Kronig, fitting, and simulation tabs as well as some aspects of the plots (e.g. colors and markers).
Several keybindings, which are user-configurable, are supported for more keyboard-based navigation although a mouse or trackpad is required in some circumstances.


## Features

Below is a brief overview of the main features of _DearEIS_.
See the included tooltips and instructions in the program for more information.


### Projects

_DearEIS_ has a project-based workflow and multiple projects can be open at the same time.
Each project has a user-definable label and a section for keeping notes.
Multiple projects can also be merged to form a single project.


### Data sets

The experimentally obtained impedance spectra are referred to as "data sets".
Each project can contain multiple data sets.
Multiple noisy data sets can be averaged to produce a single data set.
Individual data points can be masked to exclude outliers or to focus on a part of the spectrum.
Corrections can be made by subtracting either a constant complex value, the impedance of an equivalent circuit, or another spectrum.


### Data validation

Data sets can be validated by checking if they are Kramers-Kronig transformable.
See [_pyimpspec_](https://github.com/vyrjana/pyimpspec/) for more details regarding the implementation of the tests.


### Circuit fitting and simulation

Equivalent circuits can be constructed either by means of inputting a circuit description code (CDC) or by using the graphical, node-based circuit editor.
More information about the CDC syntax can be found in the program.
The circuits can be fitted to the experimental data to obtain values for the element parameters.
Initial values as well as upper and lower limits can be defined for each element parameter.
Element parameters can also be fixed at a constant value.
The impedance spectra produced by the circuits can also be simulated in a wide frequency range.
Various aspects of the circuits and the fitting results can be copied to the clipboard in different formats.
For example, a table of fitted element parameters can be obtained in the form of a Markdown or LaTeX table.
The mathematical expression for a circuit's impedance as a function of the applied frequency can also be obtained as e.g. a _SymPy_ expression.


### Visualization

Data sets and their corresponding results (Kramers-Kronig test or equivalent circuit fit) are visualized using simple Nyquist plots, Bode plots, and residual plots.
More complex plots containing multiple data sets, Kramers-Kronig test results, equivalent circuit fitting results, and/or simulation results can also be created.
These complex plots can be used to overlay and compare results more easily.
However, they can also be used to create plots that can be turned into publication-ready figures with the help of a Python script (see the [Scripting](#scripting) section for more details).


### Scripting

_DearEIS_ projects can also be used in Python scripts for the purposes of batch processing results.
This capability could be used to:
- generate project files from large numbers of measurements in an automated fashion
- export the processed data to another format
- generate tables that can be included in a document written in e.g. LaTeX or Markdown
- plot publication-ready figures using e.g. _matplotlib_

See [the Jupyter notebook](examples/examples.ipynb) for some examples.
Documentation about the API can be found on the [wiki](https://github.com/vyrjana/DearEIS/wiki).


## Changelog

See [CHANGELOG.md](CHANGELOG.md) for details.


## Contributing

If you wish to contribute to the further development of _pyimpspec_, then there are several options available to you depending on your ability and the amount of time that you can spare.
If you find bugs, wish some feature was added, or find the documentation to be lacking, then please open an issue on [GitHub](https://github.com/vyrjana/DearEIS/issues).
If you wish to contribute code, then clone the repository, create a new branch based on either the main branch or the most recent development branch, and submit your changes as a pull request.
Note that some of the core functionality of _DearEIS_ is based on [_pyimpspec_](https://github.com/vyrjana/pyimpspec) and thus certain changes (e.g. parsers for data formats) should be contributed to that project instead.
Code contributions should, if it is applicable, also include unit tests, which should be implemented in files placed in the `tests` folder found in the root of the repository along with any assets required by the tests.
It should be possible to run the tests by executing the `run_tests.sh` script, which uses the test discovery built into the `unittest` module that is included with Python.

See [CONTRIBUTORS](CONTRIBUTORS) for a list of people who have contributed to the _DearEIS_ project.


## License

Copyright 2022 DearEIS developers

_DearEIS_ is licensed under the [GPLv3 or later](https://www.gnu.org/licenses/gpl-3.0.html).

The licenses of _DearEIS_' dependencies and/or sources of portions of code are included in the LICENSES folder.
