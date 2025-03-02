.. include:: ./substitutions.rst

Projects
========

The workflow of DearEIS is based upon projects, which are stored as `JavaScript Object Notation (JSON) <https://en.wikipedia.org/wiki/JSON>`_.
These projects can contain multiple impedance spectra (or data sets) as well as multiple analysis results.

Projects can be created from the **Home** tab (:numref:`home_tab`) or the **File** menu (top of the window).
Recent projects are listed in this tab for quick access.
The entire list can be cleared and individual entries can be also be removed.
Two or more projects can also be merged to form a new project.

.. _home_tab:
.. figure:: https://raw.githubusercontent.com/wiki/vyrjana/DearEIS/images/home-tab.png
   :alt: The Home tab of the program

   Recent projects are easily accessible from the **Home** tab.


DearEIS maintain a snapshot of a project while that project is open.
The snapshot is updated every *N* actions (configurable in the settings) and this snapshot is recoverable in case DearEIS crashes or is closed while a project has unsaved changes.
Any such snapshots are loaded automatically the next time that DearEIS is started.
The snapshots are stored in ``XDG_STATE_HOME`` paths specified by the `XDG Base Directory Specification <https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html>`_:


.. list-table:: Default location of project snapshots files on different operating systems.
   :widths: 33 67
   :header-rows: 1

   * - Operating system
     - Location
   * - Linux
     - ``~/.local/state/DearEIS``
   * - MacOS
     - ``~/Library/Application Support/DearEIS``
   * - Windows
     - ``%LOCALAPPDATA%\DearEIS``

.. raw:: latex

    \clearpage


Multiple projects can be open at the same time as separate tabs and each project is split into multiple tabs:

- The **Overview** tab is where the project's label can be specified and notes can be kept.

- The **Data sets** tab is for importing and processing experimental data before it is analyzed.

- The **Kramers-Kronig** and **Z-HIT analysis** tabs provide the primary means of validating impedance spectra.

- The **DRT analysis** and **Fitting** tabs are for extracting quantitative information.

- The **Simulation** tab can be used to familiarize oneself with or to demonstrate the impedance spectra of different circuits and how parameter values affect the resulting spectra.

- The **Plotting** tab is for composing figures where multiple results can be overlaid on top of each other.

.. _overview_tab:
.. figure:: https://raw.githubusercontent.com/wiki/vyrjana/DearEIS/images/overview-tab.png
   :alt: The Overview tab of a project

   Notes about a project can be kept in the **Overview** tab.


.. raw:: latex

    \clearpage
