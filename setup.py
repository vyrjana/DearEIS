from setuptools import setup, find_packages


setup(
    name="DearEIS",
    version="0.1.0",
    author="DearEIS developers",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    url="https://github.com/vyrjana/DearEIS",
    license="GPLv3",
    description="A GUI program for analyzing, simulating, and visualizing impedance spectra.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    scripts=["bin/deareis"],
    install_requires=[
        "dearpygui>=1.4.0",  # Used to implement the GUI.
        "pyimpspec",  # Used for parsing, fitting, and analyzing impedance spectra.
        "tabulate>=0.8.9",  # Required by pandas to generate Markdown tables.
        "xdg>=5.1.1",  # Used to figure out where to place config, state, etc. files.
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
)
