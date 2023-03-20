# Running the tests

Make sure that DearEIS is installed with the `--editable` tag from the root of the repository:

```
pip install --editable .
```

Execute the `run_tests.sh` script from within the `tests` folder with `all`, `api` or `gui` as an argument.
The `run_tests.bat` script can only run the API tests at the moment (the GUI becomes unresponsive at some point while running the GUI tests on Windows).

The GUI tests will open up an instance of DearEIS but it will abort if there are open projects (e.g., because a project snapshot was opened upon startup).
A modal window should appear with buttons for running different tests.
The `Project` test takes quite a while to complete since it tries to cover a lot of aspects of using the GUI (creates a project, loads data, masks points, performs analyses, etc.).

There is a GitHub Actions workflow (`test-package.yml`) but that can only run the API tests.
