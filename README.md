# DearEIS

A GUI program for analyzing, simulating, and visualizing impedance spectra.


## Table of contents

- [Installing](#installing)
- [Features](#features)
	- [Projects and data sets](#projects-and-data-sets)
	- [Validation, analysis, and simulation](#validation-analysis-and-simulation)
	- [Scripting](#scripting)
- [Settings and keybindings](#settings-and-keybindings)
- [Contributors](#contributors)
- [License](#license)


## Installing

_DearEIS_ can be installed with _pip_.

```
pip install deareis
```


## Features

### Projects and data sets

_DearEIS_ has a project-based workflow and multiple projects can be open at the same time.
Each project has a section for notes and projects can contain multiple data sets (i.e. spectra).
Multiple noisy data sets can be averaged to produce a single data set.
Individual data points and ranges of data points can be masked so that e.g. outliers are not included in any analyses or only analyze a section of the data set at a time.
Impedances (a constant value, a circuit, or another data set) can also be subtracted from a data set to make corrections.


### Validation, analysis, and simulation

Data sets can be validated by checking if they are Kramers-Kronig transformable.
Equivalent circuits can be created and fitted to a data set in order to extract information.
Circuits can be created by typing in a circuit description code (CDC) or by manually connecting nodes, which represent elements, in the graphical circuit editor.
The initial values, which can also be set as fixed values, and the limits of the parameters of each element can be configured.
The impedance spectra of arbitrary circuits can also be simulated over a wide range of frequencies.
The simulated spectra can also be plotted together with a data set.
Various aspects of the fitting and simulation results can be copied to the clipboard.
For example, the mathematical expression for the impedance of a circuit can be copied for use in LaTeX.


### Scripting

_DearEIS_ projects can also be used in Python scripts for batch processing of the results.
This could be used to export the data to another format, to create complex plots that combine multiple results, or to programmatically generate LaTeX tables.
See [the Jupyter notebook](https://github.com/vyrjana/DearEIS/blob/main/examples/examples.ipynb) for some examples.


## Settings and keybindings

_DearEIS_ has some user-configurable settings.
It is currently possible to configure the default values of the settings on the Kramers-Kronig, fitting, and simulation tabs as well as some aspects of the plots (e.g. colors and markers).

Several keybindings, which are not currently user-configurable, are supported for keyboard-based navigation although a mouse or trackpad is required in some circumstances.
The help section in the program's menu bar contains information about the keybindings.


## Contributors

See [CONTRIBUTORS](https://github.com/vyrjana/DearEIS/blob/main/CONTRIBUTORS) for a list of people who have contributed to the _DearEIS_ project.


## License

Copyright 2022 DearEIS developers

_DearEIS_ is licensed under the [GPLv3 or later](https://www.gnu.org/licenses/gpl-3.0.html).

The licenses of _DearEIS_' dependencies and/or sources of portions of code are included in the LICENSES folder.
