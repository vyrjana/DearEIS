.. include:: ./substitutions.rst

.. _settings_page:

Settings
========

The configuration for DearEIS is stored as `JavaScript Object Notation (JSON) <https://en.wikipedia.org/wiki/JSON>`_ that is stored in ``XDG_CONFIG_HOME`` paths specified by the `XDG Base Directory Specification <https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html>`_:

.. list-table:: Default location of the configuration file on different operating systems.
   :widths: 33 67
   :header-rows: 1

   * - Operating system
     - Location
   * - Linux
     - ``~/.config/DearEIS``
   * - MacOS
     - ``~/Library/Application Support/DearEIS``
   * - Windows
     - ``%LOCALAPPDATA%\DearEIS``


Appearance
----------

Some aspects of the appearances of various plots can be defined (:numref:`appearance`).
Some of these settings are also mixed and matched in some plots when there are more items to plot than shown in the plots in this window (e.g., see the plots in the window for interpolating data points in the **Data sets** tab).

.. _appearance:
.. figure:: https://raw.githubusercontent.com/wiki/vyrjana/DearEIS/images/settings-appearance.png
   :alt: The Appearance settings window

   Most changes made to plot appearances should take effect immediately.
   Changing the number of points in simulated lines requires switching back and forth between data sets or results to update the plots.


Defaults
--------

The default settings that are used in, e.g., the tabs for performing analyses can be defined here (:numref:`defaults`).

.. _defaults:
.. figure:: https://raw.githubusercontent.com/wiki/vyrjana/DearEIS/images/settings-defaults.png
   :alt: The Default settings window

   Changes made to defaults should take effect immediately.

.. raw:: latex

    \clearpage


Keybindings
-----------

Many actions can be performed via keybindings.
If an update to DearEIS changes or adds keybindings for actions, then those keybindings may not change or be assigned.
In such cases it may be necessary to manually assign keybindings to those actions or to simply reset the keybindings.

.. _keybindings:
.. figure:: https://raw.githubusercontent.com/wiki/vyrjana/DearEIS/images/settings-keybindings.png
   :alt: The Keybinding settings window

   The keybindings defined in this window apply to a great extent also to modal/popup windows with similar functionality (e.g., for cycling results or plot types).

.. raw:: latex

    \clearpage


User-defined elements
---------------------

Both pyimpspec and DearEIS include support for user-defined elements since version 4.0.0.
The support has been implemented in DearEIS by providing a setting where the user can specify a Python script that defines one or more new elements.
See `the source code (e.g., for the constant phase element) <https://github.com/vyrjana/pyimpspec/blob/main/src/pyimpspec/circuit/constant_phase_element.py>`_ and `the documentation <https://vyrjana.github.io/pyimpspec/guide_circuit.html#user-defined-elements>`_ for pyimpspec for examples.
The relevant functions and classes are available via the APIs of both DearEIS (:doc:`/apidocs_circuit`) and pyimpspec.

.. warning::

   User-defined elements are not stored in project files.
   If a project is dependent on a user-defined element, then that project cannot be opened unless the user-defined element has been loaded.
   A project is dependent on a user-defined element if it is used in, e.g., a circuit fit or a simulation.

   The circuits used in these types of results are stored in a project file in the form of a circuit description code (CDC), which DearEIS needs to parse when a project is loaded.
   User-defined elements are thus required at the moment of parsing and DearEIS/pyimpspec will expect to find elements that match the symbols encountered while parsing the CDC.
   Changing the symbol of a user-defined element while it is in use can thus cause issues and symbols can conflict with, e.g., new elements that have been added to pyimpspec.
   Changing the parameters/subcircuits of a user-defined element is also likely to cause issues if an older version is being used by a project.

   So keep track of your script(s) that define user-defined elements and consider creating new elements when changes have to be made.

.. _user_defined_elements:
.. figure:: https://raw.githubusercontent.com/wiki/vyrjana/DearEIS/images/settings-user-defined-elements.png
   :alt: The User-defined elements window

   Specify the path to a Python script and then click the **Refresh** button.
   The new circuit elements should show up in the table.
   Hovering over a row in the table should show the automatically generated extended description for a circuit element.
   If the path is left empty and then the **Refresh** button is clicked, then the user-defined elements are cleared.


.. raw:: latex

    \clearpage
