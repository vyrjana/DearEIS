#!/bin/bash
# Upload to PyPI
python3 -m twine upload dist/*.tar.gz dist/*.whl
