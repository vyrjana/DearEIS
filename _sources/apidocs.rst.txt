.. include:: ./substitutions.rst

API Documentation
=================

DearEIS includes an API that is primarily intended for batch processing (e.g., importing data into a project or exporting results/plots/tables).

.. doctest::

   >>> import deareis          # The main functions, classes, etc.
   >>> from deareis import mpl # Plotting functions based on matplotlib.


.. warning::

   DearEIS provides wrapper functions for some of pyimpspec's functions since DearEIS uses classes that store the relevant arguments/settings in a way that can be serialized and deserialized as part of project files.
   Consequently, the API might feel somewhat cumbersome to use for some tasks where these settings classes must be instantiated and using pyimpspec directly might be more convenient.
   
   DearEIS also implements subclasses or entirely new classes to contain some of the information that pyimpspec's various result classes would contain.
   This has been done so that various results can be serialized and deserialized as part of project files.

   However, DearEIS' classes can in several cases be used directly with functions from pyimpspec (e.g., the various plotting functions) since pyimpspec checks for the presence of attributes and/or methods with specific names rather than whether or not an object is an instance of some class.

.. note::

   The API makes use of multiple processes where possible to perform tasks in parallel.
   Functions that implement this parallelization have a ``num_procs`` keyword argument that can be used to override the maximum number of processes allowed.
   Using this keyword argument should not be necessary for most users under most circumstances.
   Call the |get_default_num_procs| function to get the automatically determined value for your system.
   There is also a |set_default_num_procs| function that can be used to set a global override rather than using the ``num_procs`` keyword argument when calling various functions.

   If NumPy is linked against a multithreaded linear algebra library like OpenBLAS or MKL, then this may in some circumstances result in unusually poor performance despite heavy CPU utilization.
   It may be possible to remedy the issue by specifying a lower number of processes via the ``num_procs`` keyword argument and/or limiting the number of threads that, e.g., OpenBLAS should use by setting the appropriate environment variable (e.g., ``OPENBLAS_NUM_THREADS``).
   Again, this should not be necessary for most users and reporting this as an issue to the DearEIS or pyimpspec repository on GitHub would be preferred.


.. automodule:: deareis
   :members: get_default_num_procs, set_default_num_procs


.. raw:: latex

    \clearpage

.. toctree::
   :maxdepth: 1
   :caption: Contents:

   apidocs_data
   apidocs_project
   apidocs_kramers_kronig
   apidocs_zhit
   apidocs_drt
   apidocs_circuit
   apidocs_fitting
   apidocs_plot_mpl
   apidocs_typing
   apidocs_exceptions
