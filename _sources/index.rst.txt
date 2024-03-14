.. DearEIS documentation master file, created by
   sphinx-quickstart on Wed Jan 11 19:11:26 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. include:: ./substitutions.rst

Welcome to DearEIS' documentation!
==================================

.. only:: html

   .. image:: https://github.com/vyrjana/DearEIS/actions/workflows/test-package.yml/badge.svg
      :alt: tests
      :target: https://github.com/vyrjana/DearEIS/actions/workflows/test-package.yml
   
   .. image:: https://github.com/vyrjana/DearEIS/actions/workflows/test-wheel.yml/badge.svg
      :alt: build
      :target: https://github.com/vyrjana/DearEIS/actions/workflows/test-wheel.yml
   
   .. image:: https://img.shields.io/pypi/pyversions/DearEIS
      :alt: Supported Python versions

   .. image:: https://img.shields.io/github/license/vyrjana/DearEIS
      :alt: GitHub
      :target: https://www.gnu.org/licenses/gpl-3.0.html

   .. image:: https://img.shields.io/pypi/v/DearEIS
      :alt: PyPI
      :target: https://pypi.org/project/deareis/
   
   .. image:: https://joss.theoj.org/papers/10.21105/joss.04808/status.svg
      :alt: DOI
      :target: https://doi.org/10.21105/joss.04808

DearEIS is a Python package for processing, analyzing, and visualizing impedance spectra.
The primary interface for using DearEIS is a graphical user interface (GUI).

.. figure:: https://raw.githubusercontent.com/wiki/vyrjana/DearEIS/images/fitting-tab.png
   :alt: The graphical user interface of DearEIS


.. only:: html

   .. note::

      PDF copies of the documentation are available in the `releases section <https://github.com/vyrjana/DearEIS/releases>`_.


The GUI can be started via the following command:

.. code:: bash

   deareis


The GUI can also be started by running DearEIS as a Python module:

.. code:: bash

   python -m deareis


An application programming interface (API) is also included and it can be used to, e.g., batch process results into tables and plots.

.. doctest::

   >>> import deareis


.. note::

   If you would prefer to primarily use an API or are looking for a command-line interface (CLI), then check out `pyimpspec <https://vyrjana.github.io/pyimpspec>`_.

The source code for DearEIS can be found `here <https://github.com/vyrjana/DearEIS>`_.
The changelog can be found `here <https://github.com/vyrjana/DearEIS/blob/main/CHANGELOG.md>`_.
If you encounter bugs or wish to request a feature, then please open an `issue on GitHub <https://github.com/vyrjana/DearEIS/issues>`_.
If you wish to contribute to the project, then please read the `readme <https://github.com/vyrjana/DearEIS/blob/main/README.md>`_ before submitting a `pull request via GitHub <https://github.com/vyrjana/DearEIS/pulls>`_.

DearEIS is licensed under GPLv3_ or later.


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   guide
   apidocs
