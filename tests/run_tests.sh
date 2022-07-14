#!/bin/bash
# Copyright 2022 DearEIS developers
# DearEIS is licensed under the GPLv3 or later (https://www.gnu.org/licenses/gpl-3.0.html).
# The licenses of DearEIS' dependencies and/or sources of portions of code are included in
# the LICENSES folder.

python -m unittest discover .
if [ "$?" -eq "0" ]; then
	python -c "from deareis.program import main; from test_gui import setup_tests; setup_tests(); main()"
fi
