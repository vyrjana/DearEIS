from setuptools import setup, find_packages
from os.path import exists, join

entry_points = {
    "gui_scripts": [
        "deareis = deareis.program:main",
    ],
    "console_scripts": [
        "deareis-debug = deareis.program:debug",  # For the convenience of users on Windows
    ],
}

dependencies = [
    "dearpygui~=1.11",  # Used to implement the GUI.
    "pyimpspec>=4.1.1, == 4.*",  # Used for parsing, fitting, and analyzing impedance spectra.
    "requests~=2.31",  # Used to check package status on PyPI.
]

dev_dependencies = [
    "build~=1.1",
    "flake8~=6.0",
    "setuptools~=69.2",
    "sphinx~=7.2",
    "sphinx-rtd-theme~=2.0",
]

optional_dependencies = {
    "cvxopt": "cvxopt~=1.3",  # Used in the DRT calculations (TR-RBF method)
    "kvxopt": "kvxopt~=1.3",  # Fork of cvxopt that may provide wheels for additional platforms
    "cvxpy": "cvxpy~=1.4",  # Used in the DRT calculations (TR-RBF method)
    "dev": dev_dependencies,
}

# The version number defined below is propagated to /src/deareis/version.py
# when running this script.
version = "4.2.1"

if __name__ == "__main__":
    with open("requirements.txt", "w") as fp:
        fp.write("\n".join(dependencies))
    with open("dev-requirements.txt", "w") as fp:
        fp.write("\n".join(dev_dependencies))
    with open("version.txt", "w") as fp:
        fp.write(version)
    assert version.strip != ""
    copyright_notice = ""
    if exists("COPYRIGHT"):
        with open("COPYRIGHT") as fp:
            copyright_notice = fp.read().strip()
        assert copyright_notice.strip() != ""
    with open(join("src", "deareis", "version.py"), "w") as fp:
        fp.write(f'{copyright_notice}\n\nPACKAGE_VERSION: str = "{version}"')
    setup(
        name="deareis",
        version=version,
        author="DearEIS developers",
        packages=find_packages(where="src"),
        package_dir={"": "src"},
        include_package_data=True,
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
        python_requires=">=3.9",
        classifiers=[
            "Intended Audience :: Science/Research",
            "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
            "Operating System :: MacOS",
            "Operating System :: Microsoft :: Windows",
            "Operating System :: POSIX :: Linux",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
            "Programming Language :: Python :: 3.11",
            "Programming Language :: Python :: 3.12",
            "Programming Language :: Python :: 3 :: Only",
            "Topic :: Scientific/Engineering :: Chemistry",
            "Topic :: Scientific/Engineering :: Physics",
            "Topic :: Scientific/Engineering",
        ],
    )
