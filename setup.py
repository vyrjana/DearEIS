from setuptools import setup, find_packages
from os.path import dirname, join

entry_points = {
    "gui_scripts": [
        "deareis = deareis.program:main",
    ],
    "console_scripts": [
        "deareis-debug = deareis.program:main",  # For the convenience of users on Windows
    ],
}

version = "0.1.3"
with open(join(dirname(__file__), "src", "deareis", "version.py"), "w") as fp:
    fp.write(f"PACKAGE_VERSION: str = \"{version}\"")

setup(
    name="deareis",
    version=version,
    author="DearEIS developers",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    url="https://github.com/vyrjana/DearEIS",
    project_urls={
        "Bug Tracker": "https://github.com/vyrjana/DearEIS/issues",
    },
    license="GPLv3",
    description="A GUI program for analyzing, simulating, and visualizing impedance spectra.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    entry_points=entry_points,
    install_requires=[
        "dearpygui>=1.4.0",  # Used to implement the GUI.
        "pyimpspec>=0.1.0",  # Used for parsing, fitting, and analyzing impedance spectra.
        "tabulate>=0.8.9",  # Required by pandas to generate Markdown tables.
        "xdg>=5.1.1",  # Used to figure out where to place config, state, etc. files.
    ],
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Chemistry",
        "Topic :: Scientific/Engineering :: Physics",
        "Intended Audience :: Science/Research",
    ],
)
