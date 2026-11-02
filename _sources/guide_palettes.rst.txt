.. include:: ./substitutions.rst

Palettes
========

Command palette
---------------

DearEIS supports the use of keybindings to perform many but not all of the actions available in the various windows and tabs (e.g., switch to a specific tab, switch to a certain plot type, a Kramers-Kronig test, or perform a Kramers-Kronig test).
These keybindings are in many cases similar from window to window and tab to tab, and the keybindings can be reassigned via the corresponding settings window.
However, in some cases the keybindings are unique to the window (e.g., the file dialog).

When a modal/popup window isn't open, then it is possible to perform actions via the **Command palette** (:numref:`command_palette`) that can be opened by default via ``Ctrl+P``.
The contents of the list of actions depends upon the context (e.g., which tab is currently open).
The list of actions can be navigated using, e.g., the arrow keys.
Alternatively, the input field at the top can be used to search of a specific action.
If the input field is empty, then the order of the options depends upon how recently an option was chosen.
This should help with finding actions that are used frequently.

.. _command_palette:
.. figure:: https://raw.githubusercontent.com/wiki/vyrjana/DearEIS/images/command-palette.png
   :alt: The Command palette window

   Various actions can be performed via the **Command palette**, which only requires memorization of a single keybinding (``Ctrl+P`` by default).
   Actions can be navigated with the ``Up/Down`` arrow keys, ``Page Up/Down`` keys, and ``Home/End`` keys.
   The window also supports fuzzy matching for finding a specific action (e.g., ``saw`` should bring the ``Show the 'About' window`` action to the top).


Data set and result palettes
----------------------------

The **Data set palette** and **Result palette** are similar to the **Command palette** but they instead facilitate switching between data sets or various results depending on the current tab (Kramers-Kronig test results, fit results, plots, etc.).
The **Data set palette** and **Result palette** can be opened by default via ``Ctrl+Shift+P`` and ``Ctrl+Shift+Alt+P``, respectively.


.. raw:: latex

    \clearpage
