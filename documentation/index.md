---
layout: documentation
title: API documentation
permalink: /api/
---

## API documentation

Check out [this Jupyter notebook](https://github.com/vyrjana/DearEIS/blob/main/examples/examples.ipynb) for examples of how to use the API.
A single Markdown file of the API reference is available [here](https://raw.githubusercontent.com/vyrjana/DearEIS/gh-pages/documentation/API.md).
The [pyimpspec API](https://vyrjana.github.io/pyimpspec/api/) may be a bit easier to use if you just want to have an API to use in Python scripts or Jupyter notebooks.
Primarily because the DearEIS API uses settings objects (e.g., `DRTSettings` that can be (de)serialized easily) instead of keyword arguments in the function signatures.

- [Project](https://vyrjana.github.io/DearEIS/api/project)
- [Data set](https://vyrjana.github.io/DearEIS/api/data-set)
- [Kramers-Kronig testing](https://vyrjana.github.io/DearEIS/api/kramers-kronig)
- [Distribution of relaxation times](https://vyrjana.github.io/DearEIS/api/drt)
- [Circuit](https://vyrjana.github.io/DearEIS/api/circuit)
- [Elements](https://vyrjana.github.io/DearEIS/api/elements)
- [Fitting](https://vyrjana.github.io/DearEIS/api/fitting)
- [Simulating](https://vyrjana.github.io/DearEIS/api/simulating)
- [Plotting](https://vyrjana.github.io/DearEIS/api/plotting)
  - [matplotlib](https://vyrjana.github.io/DearEIS/api/plot-mpl)

The DearEIS API is built upon the [pyimpspec](https://vyrjana.github.io/pyimpspec) package.


**NOTE!** The API makes use of multiple processes where possible to perform tasks in parallel. Functions that implement this parallelization have a `num_procs` keyword argument that can be used to override the maximum number of processes allowed. Using this keyword argument should not be necessary for most users under most circumstances.

If NumPy is linked against a multithreaded linear algebra library like OpenBLAS or MKL, then this may in some circumstances result in unusually poor performance despite heavy CPU utilization. It may be possible to remedy the issue by specifying a lower number of processes via the `num_procs` keyword argument and/or limiting the number of threads that, e.g., OpenBLAS should use by setting the appropriate environment variable (e.g., `OPENBLAS_NUM_THREADS`). Again, this should not be necessary for most users and reporting this as an issue to the pyimpspec or DearEIS repository on GitHub would be preferred.


