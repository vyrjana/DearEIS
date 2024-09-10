.. include:: ./substitutions.rst

Processing data
===============

The **Data sets** tab
---------------------

Multiple impedance spectra (or *data sets*) can be loaded and processed in the **Data sets** tab (:numref:`data_tab`) that contains the following:

- **Data set** combo for switching between data sets that have been loaded via the **Load** button.
- **Label** input for modifying the label assigned to the current data set.
- **Path** input for modifying the file path assigned to the current data set.
- **Process** button for opening a popup window with buttons for accessing features that enable further processing of the current data set.
- A table of data points with the ability to mask (i.e., hide/exclude) individual points (e.g., outliers).
- **Toggle points** button for (un)masking multiple points at once.
- **Copy mask** button for copying a mask from another data set and applying it to the current data set.
- **Enlarge/show plot** button for viewing a larger version of the current plot type.
- **Adjust limits** checkbox for enabling/disabling automatic adjustment of plot limits when switching between data sets.
- Plot type combo for switching between plot types. This is primarily for use when the program window is so narrow that the plots are hidden in order to keep the table of data points from becoming to narrow.


.. _data_tab:
.. figure:: https://raw.githubusercontent.com/wiki/vyrjana/DearEIS/images/data-sets-tab.png
   :alt: The Data sets tab of a project

   The data point around 50 Hz has been omitted from this rather noisy data set as an outlier.

.. raw:: latex

    \clearpage


Supported file formats
----------------------

Several different file formats are supported:

- BioLogic: ``.mpt``
- Eco Chemie: ``.dfr``
- Gamry: ``.dta``
- Ivium: ``.idf`` and ``.ids``
- PalmSens: ``.pssession``
- ZView: ``.z``
- Spreadsheets: ``.xlsx`` and ``.ods``
- Plain-text character-separated values (CSV): ``.csv`` and ``.txt``

Additional file formats may be supported in the future.

Not all CSV files and spreadsheets are necessarily supported as-is but the parsing of those types of files should be quite flexible in terms of, e.g., the characters that are used as separators.
The parsers expect to find at least a column with frequencies (Hz) and columns for either the real and imaginary parts of the impedance (|ohm|), or the absolute magnitude (|ohm|) and the phase angle/shift (degrees).
The supported column headers are:

- frequency: ``frequency``, ``freq``, or ``f``
- real: ``z'``, ``z re``, ``z_re``, ``zre``, ``real``, or ``re``
- imaginary: ``z"``, ``z''``, ``z im``, ``z_im``, ``zim``, ``imaginary``, ``imag``, or ``im``
- magnitude: ``|z|``, ``z``, ``magnitude``, ``modulus``, ``mag``, or ``mod``
- phase: ``phase``, ``phz``, or ``phi``

The identification of column headers is case insensitive (i.e., ``Zre`` and ``zre`` are considered to be the same).
The sign of the imaginary part of the impedance and/or the phase angle/shift may be negative, but then that has to be indicated in the column header with a ``-`` prefix (e.g., ``-Zim`` or ``-phase``).

.. raw:: latex

    \clearpage


Masking data points
-------------------

Masks can be applied to hide data points in several ways and masked data points are excluded from plots and analyses.
This feature can be used to get rid of outliers or to analyze a fragment of a data set.
Individual data points can be masked via the checkboxes along the left-hand side of the table of data points (:numref:`data_tab`).
Ranges of data points can be toggled via the window that is accessible via the **Toggle points** button below the table of data points.
This can be used to, e.g., quickly mask multiple points or to remove the mask from all points (:numref:`toggle_figure`).
Middle-mouse clicking and dragging a region in a plot in that window can also be used to choose the points to toggle.


.. _toggle_figure:
.. figure:: https://raw.githubusercontent.com/wiki/vyrjana/DearEIS/images/data-sets-tab-toggle.png
   :alt: Masking multiple points

   The **Toggle points** can be used to (un)mask multiple data points in several ways.
   A preview of what the current data set would look like with the new mask is also included.
   Here a region has been highlighted in one of the plots by holding down the middle-mouse button and dragging.
   All of the points are included, which means that the points within the highlighted region will be toggled (i.e., excluded) when the **Accept** button is clicked.

.. raw:: latex

    \clearpage

If multiple data sets will need to have the same (or very similar) masks, then the **Copy mask** window can be used to copy the applied mask from another data set to the current data set (:numref:`mask_figure`).


.. _mask_figure:
.. figure:: https://raw.githubusercontent.com/wiki/vyrjana/DearEIS/images/data-sets-tab-copy.png
   :alt: Copying a mask from another data set

   The **Copy mask** includes a preview of what the current data set would look like with the mask that was applied to another data set in :numref:`toggle_figure`.

.. raw:: latex

    \clearpage


Processing data sets
--------------------

DearEIS includes a few functions for processing data sets: averaging, interpolation, addition of parallel impedances, and subtraction of impedances.
All of these functions are available via the **Process** button that can be found above the table of data points (:numref:`data_tab`).
The results of these functions are added to the project as a new data set (i.e., without getting rid of the original data set).


Averaging
~~~~~~~~~

The averaging feature can be used to obtain a less noisy spectrum by averaging multiple measurements (:numref:`averaging_figure`).
This can be useful in cases where the noise cannot be reduced by adjusting some aspect of the experimental setup (e.g., by improving the shielding).
Only data sets with the same frequencies can be averaged.

.. note::

   Make sure that the measurements differ due to random noise rather than, e.g., drift before using this feature.

.. _averaging_figure:
.. figure:: https://raw.githubusercontent.com/wiki/vyrjana/DearEIS/images/data-sets-tab-averaging.png
   :alt: Averaging of multiple data sets

   Two data sets have been chosen (markers) and an average data set has been generated (line).
   The other data sets do not have the same frequencies as the two chosen data sets and thus cannot be selected while at least one of those two data sets is selected.

.. raw:: latex

    \clearpage


Interpolation
~~~~~~~~~~~~~

The interpolation feature can be used to replace an outlier rather than simply omitting it (:numref:`interpolation_figure`).
Some specific methods of analysis may be sensitive to the spacing of data points, which is why interpolation may be preferred over omission.
The data set is smoothed using `LOWESS <https://en.wikipedia.org/wiki/Local_regression>`_ and interpolated using an `Akima spline <https://en.wikipedia.org/wiki/Akima_spline>`_ while ignoring any masked points.
Individual data points can then be replaced with a point on this spline by ticking the checkbox next to that data point.
Alternatively, if the smoothing and interpolation cannot provide a reasonable result, then values for the real and/or imaginary part of the data point can be inputted directly.


.. _interpolation_figure:
.. figure:: https://raw.githubusercontent.com/wiki/vyrjana/DearEIS/images/data-sets-tab-interpolation.png
   :alt: Interpolation of data points

   The outlier (red marker), which was masked in :numref:`data_tab`, has been replaced with a value (orange marker) along the interpolated spline (green line).

.. raw:: latex

    \clearpage

.. _parallel impedances:

Adding parallel impedances
~~~~~~~~~~~~~~~~~~~~~~~~~~

Impedance data that include negative differential resistances may present some challenges.
For example, such spectra cannot be validated directly using linear Kramers-Kronig tests if only the impedance representation is tested.
However, they can be validated if the admittance representation is tested.
Alternatively, one can add a suitable parallel resistance to the impedance data.
The addition of a parallel resistance does not affect the Kramers-Kronig compliance of the data.

.. plot::
   :alt: A circuit where the a parallel resistance, R, has been added to the original impedance data, Z.

   from pyimpspec import parse_cdc
   # A Warburg impedance is used here just to have two different symbols
   circuit = parse_cdc("(WR)")
   elements = circuit.get_elements()
   custom_labels = {
       elements[0]: r"$Z_{\rm data}$",
       elements[1]: r"$R_{\rm par}$",
   }
   circuit.to_drawing(custom_labels=custom_labels).draw()


The magnitude of the parallel resistance to add depends on the original impedance data.
In the example below (:numref:`parallel_figure`), a resistance of 50 |ohm| was chosen.


.. note::

   Equivalent circuits can be fitted to the original impedance data that include negative differential resistances provided that negative resistances are allowed (i.e., the lower limits of resistances are disabled or modified prior to fitting).

.. _parallel_figure:
.. figure:: https://raw.githubusercontent.com/wiki/vyrjana/DearEIS/images/data-sets-tab-parallel.png
   :alt: Addition of parallel impedance to impedance data

   An impedance spectrum that includes a negative differential resistance was generated for this example (marked here as **Before**).
   Performing Kramers-Kronig tests on the impedance representation would fail despite the original data being compliant.
   Adding a parallel resistance of 50 |ohm| produces impedance data (marked here as **After**) that can be validated.
   The added parallel resistance is always Kramers-Kronig compliant, which means that the compliance of the resulting circuit and its impedance data depends on the compliance of the original data.


.. raw:: latex

    \clearpage


Subtracting impedances
~~~~~~~~~~~~~~~~~~~~~~

The recorded impedances can also be corrected by subtracting one of the following (:numref:`subtraction_figure`):

- a fixed impedance
- a circuit
- a fitted circuit
- another data set

This feature can be used to, e.g., correct for some aspect of a measurement setup that is independent of the sample itself.

.. _subtraction_figure:
.. figure:: https://raw.githubusercontent.com/wiki/vyrjana/DearEIS/images/data-sets-tab-subtraction.png
   :alt: Subtraction of impedances from a recorded spectrum

   A resistance of 50 |ohm| is subtracted from a data set.


.. raw:: latex

    \clearpage
