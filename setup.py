from pathlib import Path
from tomllib import load
from setuptools import setup

with open("pyproject.toml", "rb") as fp:
    toml = load(fp)

version = toml["project"]["version"]
with open("version.txt", "w") as fp:
    fp.write(version)

with open("COPYRIGHT") as fp:
    copyright_notice = fp.read().strip()

with open(Path(__file__).parent.joinpath("src", "deareis", "version.py"), "w") as fp:
    fp.write(f'{copyright_notice}\n\nPACKAGE_VERSION: str = "{version}"')

setup()

