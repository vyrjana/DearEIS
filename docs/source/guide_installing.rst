.. include:: ./substitutions.rst

Installing
==========

Supported platforms
-------------------

- Linux
- Windows
- MacOS

The package **may** also work on other platforms depending on whether or not those platforms are supported by DearEIS' dependencies.


Requirements
------------

- `Python <https://www.python.org>`_ (3.8, 3.9, or 3.10)
- The following Python packages

  - `dearpygui <https://github.com/hoffstadt/DearPyGui>`_
  - pyimpspec_
  - `requests <https://github.com/psf/requests>`_

These Python packages (and their dependencies) are installed automatically when DearEIS is installed using `pip <https://pip.pypa.io/en/stable/>`_.

The following Python packages can be installed as optional dependencies for additional functionality:

- DRT calculations using the `TR-RBF method <https://doi.org/10.1016/j.electacta.2015.09.097>`_ (at least one of the following is required):
	- `cvxopt <https://github.com/cvxopt/cvxopt>`_
	- `kvxopt <https://github.com/sanurielf/kvxopt>`_ (this fork of cvxopt may support additional platforms)
	- `cvxpy <https://github.com/cvxpy/cvxpy>`_


.. note::

   Windows and MacOS users who wish to install CVXPY **must** follow the steps described in the `CVXPY documentation <https://www.cvxpy.org/install/index.html>`_!


Installing
----------

Make sure that Python and pip are installed first (see previous section for supported Python versions).
For example, open a terminal and run the command:

.. code:: bash

   pip --version

.. note::

   If you only intend to use DearEIS via the GUI or are familiar with `virtual environments <https://docs.python.org/3/tutorial/venv.html>`_, then you should consider using `pipx <https://pypa.github.io/pipx/>`_ instead of pip to install DearEIS.
   Pipx will install DearEIS inside of a virtual environment, which can help with preventing potential version conflicts that may arise if DearEIS requires an older or a newer version of a dependency than another package.
   Pipx also manages these virtual environments and makes it easy to run applications/packages.


If there are no errors, then run the following command to install pyimpspec and its dependencies:

.. code:: bash

   pip install deareis

DearEIS should now be available as a command in the terminal and possibly also some application launchers.

If you wish to install the optional dependencies, then they must be specified explicitly when installing DearEIS:

.. code:: bash

   pip install deareis[cvxpy]

Newer versions of DearEIS can be installed at a later date by adding the ``--upgrade`` option to the command:

.. code:: bash
   
   pip install --upgrade deareis


Running the GUI program
-----------------------

You should now be able to run DearEIS via, e.g., a terminal or the Windows start menu by typing in the command ``deareis``.
There is also a ``deareis-debug`` command that can be used for troubleshooting purposes and prints a lot of potentially useful information to a terminal window.
DearEIS can also be launched as a Python module:

.. code:: bash

   python -m deareis


Using the API
-------------

The ``deareis`` package should now be accessible in Python:

.. doctest::

   >>> import deareis


.. raw:: latex

    \clearpage
