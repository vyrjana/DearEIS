from setuptools import setup, find_packages
from os import walk
from os.path import dirname, join


licenses = []
for _, _, files in walk("LICENSES"):
    licenses.extend(
        list(
            map(
                lambda _: join("LICENSES", _),
                filter(lambda _: _.startswith("LICENSE-"), files),
            )
        )
    )

entry_points = {
    "gui_scripts": [
        "deareis = deareis.program:main",
    ],
    "console_scripts": [
        "deareis-debug = deareis.program:debug",  # For the convenience of users on Windows
    ],
}

copyright_notice = ""
with open(join(dirname(__file__), "COPYRIGHT")) as fp:
    copyright_notice = fp.read().strip()
version = "1.1.0"
with open(join(dirname(__file__), "src", "deareis", "version.py"), "w") as fp:
    fp.write(f'{copyright_notice}\n\nPACKAGE_VERSION: str = "{version}"')

setup(
    name="deareis",
    version=version,
    author="DearEIS developers",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    data_files=[
        "COPYRIGHT",
        "CONTRIBUTORS",
        "LICENSES/README.md",
    ]
    + licenses,
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
        "dearpygui>=1.6.2",  # Used to implement the GUI.
        "pyimpspec>=1.1.0",  # Used for parsing, fitting, and analyzing impedance spectra.
        "tabulate>=0.8.9",  # Required by pandas to generate Markdown tables.
        "xdg>=5.1.1",  # Used to figure out where to place config, state, etc. files.
    ],
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Chemistry",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Scientific/Engineering",
    ],
)
