# Documentation

## API documentation

### How to generate

This folder contains a script (`generate-api-reference.py`) for generating Markdown files containing the API reference that is hosted as part of the project's GitHub pages site.
The script can be run independently but it is also executed by `build.sh`, which can be found in the repository root directory.
The generated Markdown files should be copied to the `documentation` folder found in the `gh-pages` branch.
The recommended setup is to:

- Clone the project repository as a separate local repository dedicated to just working with the `gh-pages` branch.
- Symlink the `documentation` directory that exists in the repository dedicated to the `gh-pages` branch to this directory.

The generated Markdown files will then automatically be placed in the repository dedicated to the `gh-pages` branch where they can then be committed and pushed to GitHub.

### Dependencies

The script shares code with the [pyimpspec](https://github.com/vyrjana/pyimpspec) project, which also has a script for generating API documentation in the same way.
The shared code is contained in [this repository](https://github.com/vyrjana/python-api-documenter), which has been added to this repository as a submodule.
The submodule can be updated with the following command when new commits are pushed to the shared repository:

`git submodule update --remote --merge`
