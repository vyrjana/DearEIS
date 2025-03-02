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
# The licenses of DearEIS' dependencies and/or sources of portions of code are included in
# the LICENSES folder.

# Stop when a non-zero exit code is encountered
set -e

docs_html(){
	sphinx-build "./docs/source" "./docs/build/html"
}

docs_test(){
	sphinx-build -b doctest "./docs/source" "./docs/build/html"
}

docs_latex(){
	sphinx-build -M latexpdf "./docs/source" "./docs/build/latex"
}

validate_tar(){
	echo
	echo "Listing changelogs and licenses that were bundled in *.tar.gz:"
	# Check if the changelog was bundled properly
	tar --list -f ./dist/*.tar.gz | grep "deareis/gui/changelog/CHANGELOG\.md"
	# Check if the package license was included
	tar --list -f ./dist/*.tar.gz | grep "LICENSE$"
	# Check if the other licenses were bundled properly
	tar --list -f ./dist/*.tar.gz | grep "deareis/gui/licenses/LICENSE-DearEIS.txt"
	dist="$(tar --list -f ./dist/*.tar.gz | grep "deareis/gui/licenses/LICENSE-.*\.txt" | sort)"
	repo="$(ls LICENSES | grep "LICENSE-.*.txt" | sort)"
	python3 -c "from sys import argv; from os.path import basename; dist = set(list(map(basename, argv[1].split('\n')))); dist.remove('LICENSE-DearEIS.txt'); repo = set(list(map(basename, argv[2].split('\n')))); assert dist == repo, 'Incorrect set of bundled licenses! An extra .txt file has probably been left in the \'/src/deareis/gui/licenses\' folder.'; list(map(print, sorted(dist)))" "$dist" "$repo"
}

validate_wheel(){
	echo
	echo "Listing changelogs and licenses that were bundled in *.whl:"
	# Check if the changelog was bundled properly
	unzip -Z1 ./dist/*.whl | grep "deareis/gui/changelog/CHANGELOG\.md"
	# Check if the package license was included
	unzip -Z1 ./dist/*.whl | grep "LICENSE$"
	# Check if the other licenses were bundled properly
	unzip -Z1 ./dist/*.whl | grep "deareis/gui/licenses/LICENSE-DearEIS.txt"
	dist="$(unzip -Z1 ./dist/*.whl | grep "deareis/gui/licenses/LICENSE-.*\.txt" | sort)"
	repo="$(ls LICENSES | grep "LICENSE-.*.txt" | sort)"
	python3 -c "from sys import argv; from os.path import basename; dist = set(list(map(basename, argv[1].split('\n')))); dist.remove('LICENSE-DearEIS.txt'); repo = set(list(map(basename, argv[2].split('\n')))); assert dist == repo, 'Incorrect set of bundled licenses! An extra .txt file has probably been left in the \'/src/deareis/gui/licenses\' folder.'; list(map(print, sorted(dist)))" "$dist" "$repo"
}

if [ "$1" == "docs" ]; then
	docs_html
	docs_test
	docs_latex
	exit
fi
if [ "$1" == "docs-html" ]; then
	docs_html
	exit
fi
if [ "$1" == "docs-test" ]; then
	docs_test
	exit
fi
if [ "$1" == "docs-latex" ]; then
	docs_latex
	exit
fi


# Check for uncommitted changes and untracked files
if [ "$(git status --porcelain=v1 | wc -l)" -ne 0 ]; then
	echo "Detected uncommitted changes and/or untracked files!"
	if ! [ "$1" == "override" ]; then
		echo "Continue with the build process anyway by providing 'override' as an argument to this script."
		exit
	fi
fi

# Check for major issues
flake8 ./src/deareis --select=E9,F63,F7,F82 --show-source --statistics
echo "flake8 didn't find any issues..."
echo

# Update non-source code files that should be included
python3 ./pre-build.py

# Build wheel
python3 -m build

# Validate the source and wheel distributions
validate_tar
validate_wheel
if [ "$1" == "distros" ]; then
	exit
fi

# Update documentation
# - The contents of ./dist/html should be committed to the gh-pages branch
#   - Run the reset.sh script found in gh-pages
#   - Copy the files from ./dist/html
#   - Commit
#   - Force push
# - ./dist/DearEIS-X-Y-Z.pdf should be uploaded as an attachment to a release
echo
echo "Generating documentation..."
# Generate HTML, run tests, and finally generate PDF
docs_html
docs_test
docs_latex

# Copy documentation assets
python3 ./post-build.py

# Everything should be okay
echo
echo "Finished!!!"
