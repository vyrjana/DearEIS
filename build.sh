#!/bin/bash
# Stop when a non-zero exit code is encountered
set -e

# Check for uncommitted changes and untracked files
if [ "$(git status --porcelain=v1 | wc -l)" -ne 0 ]; then
	echo "Detected uncommitted changes and/or untracked files!"
	exit
fi

# Check for major issues
flake8 . --select=E9,F63,F7,F82 --show-source --statistics
echo "flake8 didn't find any issues..."
echo

# Build wheel
python3 -m build

# Validate the source and wheel distributions
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
python -c "from sys import argv; from os.path import basename; dist = list(map(basename, argv[1].split('\n'))); dist.remove('LICENSE-DearEIS.txt'); repo = list(map(basename, argv[2].split('\n'))); assert dist == repo; list(map(print, dist))" "$dist" "$repo"

# Validate the source and wheel distributions
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
python -c "from sys import argv; from os.path import basename; dist = list(map(basename, argv[1].split('\n'))); dist.remove('LICENSE-DearEIS.txt'); repo = list(map(basename, argv[2].split('\n'))); assert dist == repo; list(map(print, dist))" "$dist" "$repo"

# Update documentation
echo
echo "Generating API documentation..."
# The package at https://github.com/vyrjana/python-api-documenter is required for
# generating the API documentation.
# The "documentation" folder should be copied to the gh-pages branch in the end.
python3 ./docs/generate-api-reference.py

# Everything should be okay
echo
echo "Finished!!!"
