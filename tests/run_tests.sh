#!/bin/bash
# DearEIS is licensed under the GPLv3 or later (https://www.gnu.org/licenses/gpl-3.0.html).
# Copyright 2023 DearEIS developers
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

if [ "$#" -ne 1 ]; then
	echo "Incorrect number of arguments provided! One of the following arguments is allowed at a time:"
	echo "- all: Run all (non-headless) tests."
	echo "- api: Run API-related tests."
	echo "- gui: Run GUI-related tests."
	echo "- headless: Run headless GUI-related tests."
	exit
fi
if [ "$1" == "headless" ]; then
	python3 -c "from deareis.program import main; from test_gui import setup_headless_tests; setup_headless_tests(); main()"
	exit
fi
if ! [ "$1" == "gui" ]; then
	python3 -m unittest discover . -v -f
fi
if [ "$?" -eq "0" ] && ! [ "$1" == "api" ]; then
	python3 -c "from deareis.program import main; from test_gui import setup_tests; setup_tests(); main()"
fi
