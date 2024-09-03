# DearEIS

A GUI program for analyzing, simulating, and visualizing impedance spectra.

[![tests](https://github.com/vyrjana/DearEIS/actions/workflows/test-package.yml/badge.svg)](https://github.com/vyrjana/DearEIS/actions/workflows/test-package.yml)
[![build](https://github.com/vyrjana/DearEIS/actions/workflows/test-wheel.yml/badge.svg)](https://github.com/vyrjana/DearEIS/actions/workflows/test-wheel.yml)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/DearEIS)
[![GitHub](https://img.shields.io/github/license/vyrjana/DearEIS)](https://www.gnu.org/licenses/gpl-3.0.html)
[![PyPI](https://img.shields.io/pypi/v/DearEIS)](https://pypi.org/project/deareis/)
[![DOI](https://joss.theoj.org/papers/10.21105/joss.04808/status.svg)](https://doi.org/10.21105/joss.04808)


## Table of contents

- [About](#about)
- [Changelog](#changelog)
- [Contributing](#contributing)
- [License](#license)


## About

DearEIS is a Python package that includes a program with a graphical user interface (GUI) for working with impedance spectra.
An application programming interface (API) is also included that is primarily for batch processing.
The target audience is researchers who use electrochemical impedance spectroscopy (EIS) though the program may also be useful in educational settings.

The GUI program implements features such as:

- projects that can contain multiple experimental data sets and analysis results
- reading certain data formats and parsing the experimental data contained within
- validation of impedance spectra using linear Kramers-Kronig tests or the Z-HIT algorithm
- estimation of the distribution of relaxation times (DRT)
- construction of circuits, e.g., by parsing circuit description codes (CDC) or by using the included graphical editor
- support for user-defined circuit elements
- complex non-linear least squares fitting of equivalent circuits
- simulation of the impedance spectra of circuits
- visualization of impedance spectra and/or various analysis results

See the [official documentation](https://vyrjana.github.io/DearEIS/) for instructions on how to  install DearEIS, screenshots and guides, and the API reference.

Those who would prefer to only use an API (or a command-line interface (CLI)) for everything may wish to use [pyimpspec](https://github.com/vyrjana/pyimpspec) instead.


## Changelog

See [CHANGELOG.md](CHANGELOG.md) for details.


## Contributing

If you wish to contribute to the further development of DearEIS, then there are several options available to you depending on your ability and the amount of time that you can spare.

If you find bugs, wish some feature was added, or find the documentation to be lacking, then please open an issue on [GitHub](https://github.com/vyrjana/DearEIS/issues).

If you wish to contribute code, then start by cloning the repository:

`git clone https://github.com/vyrjana/DearEIS.git`

The development dependencies can be installed from within the repository directory:

`pip install -r ./dev-requirements.txt`

Create a new branch based on either the `main` branch or the most recent development branch (e.g., `dev-*`), and submit your changes as a pull request.

Note that some of the core functionality of DearEIS is based on [pyimpspec](https://github.com/vyrjana/pyimpspec) and thus certain changes (e.g., parsers for data formats) should be contributed to that project instead.

Code contributions should, if it is applicable, also include unit tests, which should be implemented in files placed in the `tests` folder found in the root of the repository along with any assets required by the tests.
It should be possible to run the tests by executing the `run_tests.sh` script, which uses the test discovery built into the `unittest` module that is included with Python.

See [CONTRIBUTORS](CONTRIBUTORS) for a list of people who have contributed to the DearEIS project.


## License

Copyright 2024 DearEIS developers

DearEIS is licensed under the [GPLv3 or later](https://www.gnu.org/licenses/gpl-3.0.html).

The licenses of DearEIS' dependencies and/or sources of portions of code are included in the LICENSES folder.
