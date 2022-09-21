from setuptools import (
    setup,
    find_packages,
)
from os import walk
from os.path import (
    basename,
    exists,
    join,
)


entry_points = {
    "gui_scripts": [
        "deareis = deareis.program:main",
    ],
    "console_scripts": [
        "deareis-debug = deareis.program:debug",  # For the convenience of users on Windows
    ],
}

dependencies = [
    "dearpygui==1.6.2",  # Used to implement the GUI.
    "pyimpspec>=3.1.2",  # Used for parsing, fitting, and analyzing impedance spectra.
    "requests>=2.28.1",  # Used to check package status on PyPI.
    "xdg>=5.1.1",  # Used to figure out where to place config, state, etc. files.
]

optional_dependencies = {
    "cvxpy": "cvxpy>=1.2.1",  # Used in the DRT calculations (TR-RBF method)
}

with open("requirements.txt", "w") as fp:
    fp.write("\n".join(dependencies))

# The version number defined below is propagated to /src/deareis/version.py
# when running this script.
version = "3.1.3"

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


def update_file(src: str, dst: str):
    if not exists(src):
        return
    src_contents = ""
    with open(src, "r") as fp:
        src_contents = fp.read()
    if exists(dst):
        with open(dst, "r") as fp:
            if fp.read() == src_contents:
                return
    with open(dst, "w") as fp:
        fp.write(src_contents)


copyright_notice = ""
with open("COPYRIGHT") as fp:
    copyright_notice = fp.read().strip()

with open(join("src", "deareis", "version.py"), "w") as fp:
    fp.write(f'{copyright_notice}\n\nPACKAGE_VERSION: str = "{version}"')

# The changelog bundled with the package will also be updated when running this script.
update_file(
    join("CHANGELOG.md"),
    join("src", "deareis", "gui", "changelog", "CHANGELOG.md"),
)

# The licenses bundled with the package will also be updated when running this script.
update_file(
    join("LICENSE"),
    join("src", "deareis", "gui", "licenses", "LICENSE-DearEIS.txt"),
)
list(
    map(
        lambda _: update_file(
            _,
            join("src", "deareis", "gui", "licenses", basename(_)),
        ),
        licenses,
    )
)

data_files = [
    "COPYRIGHT",
    "CONTRIBUTORS",
    "LICENSES/README.md",
    "src/deareis/gui/changelog/CHANGELOG.md",
] + licenses

setup(
    name="deareis",
    version=version,
    author="DearEIS developers",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    data_files=data_files,
    url="https://vyrjana.github.io/DearEIS",
    project_urls={
        "Documentation": "https://vyrjana.github.io/DearEIS/api/",
        "Source Code": "https://github.com/vyrjana/DearEIS",
        "Bug Tracker": "https://github.com/vyrjana/DearEIS/issues",
    },
    license="GPLv3",
    description="A GUI program for analyzing, simulating, and visualizing impedance spectra.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    entry_points=entry_points,
    install_requires=dependencies,
    extras_require=optional_dependencies,
    python_requires=">=3.8",
    classifiers=[
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Scientific/Engineering :: Chemistry",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Scientific/Engineering",
    ],
)
