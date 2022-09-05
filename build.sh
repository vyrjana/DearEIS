#!/bin/bash
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
if [ "$?" -ne 0 ]; then
	echo "Found issues that will cause the automated tests to fail!"
	exit
fi
# Build wheel
python3 -m build
