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

- `Python <https://www.python.org>`_ (3.10, 3.11, or 3.12)
- The following Python packages

  - `dearpygui <https://github.com/hoffstadt/DearPyGui>`_
  - `requests <https://github.com/psf/requests>`_
  - pyimpspec_

These Python packages (and their dependencies) are installed automatically when DearEIS is installed using `pip <https://pip.pypa.io/en/stable/>`_.

The following Python packages can be installed as optional dependencies for additional functionality:

- DRT calculations using the `TR-RBF method <https://doi.org/10.1016/j.electacta.2015.09.097>`_ (at least one of the following is required):
	- `cvxopt <https://github.com/cvxopt/cvxopt>`_
	- `kvxopt <https://github.com/sanurielf/kvxopt>`_ (this fork of cvxopt may support additional platforms)


Installing
----------

Make sure that Python and pip are installed first (see previous section for supported Python versions).
For example, open a terminal and run the command:

.. code:: bash

   pip --version


.. note::

   Using a Python `virtual environment <https://docs.python.org/3/tutorial/venv.html>`_ is highly recommended in order to avoid possible issues related to conflicting versions of dependencies installed on a system.
   Such a virtual environment needs to be activated before running a script that imports a package installed inside the virtual environment.
   The system-wide Python environment may also be `externally managed <https://peps.python.org/pep-0668/>`_ in order to prevent the user from accidentally breaking that environment since the operating system depends upon the packages in that environment.

   A third-party tool called `pipx <https://pypa.github.io/pipx/>`_ can automatically manage such virtual environments, but it is primarily for installing programs that provide, e.g., a command-line interface (CLI) or a graphical user interface (GUI).
   These programs can then be run without having to manually activate the virtual environment since pipx handles that.
   The virtual environment would still need to be activated before running a script that imports DearEIS and makes use of DearEIS's application programming interface (API).

If using pipx, then run the following command to make sure that pipx is available.
If pipx is not available, then follow the `instructions to install pipx <https://pypa.github.io/pipx/installation/>`_.

.. code:: bash

   pipx --version


If there are no errors, then run the following command to install DearEIS and its dependencies:

.. code:: bash

   # If manually managing the virtual environment,
   # follow the relevant pip documentation for creating
   # and activating a virtual environment before running
   # the following command.
   pip install deareis

   # If pipx is used to automatically manage the virtual environment.
   pipx install deareis


DearEIS should now be available as a command in the terminal and possibly also some application launchers.

If you wish to install the optional dependencies, then they can be specified explicitly when installing DearEIS via pip:

.. code:: bash

   pip install deareis[cvxopt]


Optional dependencies can also be install after the fact if pipx was used:

.. code:: bash

   pipx inject deareis cvxopt


Newer versions of DearEIS can be installed in the following ways:

.. code:: bash
   
   pip install deareis --upgrade

   pipx upgrade deareis --include-injected


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
