#!/bin/bash
# DearEIS is licensed under the GPLv3 or later (https://www.gnu.org/licenses/gpl-3.0.html).
# Copyright 2025 DearEIS developers
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
# The licenses of DearEIS's dependencies and/or sources of portions of code are included in
# the LICENSES folder.

target_folder=".venv/DearEIS"
if [ -d "$target_folder" ]; then
	echo "The '$target_folder' folder already exists!"
	exit
fi

echo "Initializing virtual environment in '$target_folder'"
python3 -m venv "$target_folder"
if [ $? -ne 0 ]; then
	exit
fi

# Activating the virtual environment
source "$target_folder/bin/activate"
if [ $? -ne 0 ]; then
	exit
fi

echo "Installing package (editable mode) without dependencies"
# This will cause setup.py to refresh the dev-requirements.txt
# and requirements.txt files.
python3 -m pip install -e . --no-deps
if [ $? -ne 0 ]; then
	exit
fi

echo "Installing development dependencies"
python3 -m pip install -r "dev-requirements.txt"
if [ $? -ne 0 ]; then
	exit
fi

echo "Installing package dependencies"
python3 -m pip install -r "requirements.txt"
if [ $? -ne 0 ]; then
	exit
fi
