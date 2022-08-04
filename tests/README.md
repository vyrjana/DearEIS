# Running the tests

Make sure that DearEIS is installed with the `--editable` tag from the root of the repository:

```
pip install --editable .
```

Execute the `run_tests.sh` script from within the `tests` folder.

The Jupyter notebook found in the `examples` folder in the root of the repository can also be used to verify that the API works as expected.

There is a GitHub Actions workflow (`test-package.yml`) that runs some of the tests.
The GUI tests are currently not included in those tests since the failure of a test would keep the workflow running until timed out.
So the GUI tests should only be run locally for now.
