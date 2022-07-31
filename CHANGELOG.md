# 2.0.0

- Added a window for exporting plots using matplotlib.
	- Testing showed that attempting to free the memory allocated to the plot previews caused DearEIS to always crash on one of the computers used for testing.
	  The cause is not known at the moment but it could a bug in the GPU drivers (NVIDIA 515.57 on Linux) and/or in the GUI framework (Dear PyGui 1.6.2).
	- Two workarounds have been implemented in the form of two settings that can be found in the **Settings - defaults** window:
		- Disabling the **Clear texture registry** setting prevents the crashes without taking away the ability to have plot previews.
		  However, doing so introduces a memory leak since the memory allocated to each plot preview is not freed until DearEIS is closed.
		- Alternatively, enabling the **Disable plot previews** setting prevents the crashes without introducing a memory leak by not generating plot previews at all.
- Added settings for the default values used when exporting plots (e.g., dimensions and extension).
- Added support for the new data formats supported by pyimpspec.
- Added tests for the API and the GUI.
- Updated the config file structure to support the new settings.
- Updated minimum Python and dependency versions.
- Updated the API and its documentation.
- Added new keybindings and updated some old ones for greater consistency.
- Changed how most of the plots are updated to prevent flickering of the legend.
- Fixed a bug that allowed an empty string to be used as the file name when saving using the file dialog window.
- Fixed a bug that caused an exception when deleting a simulation result after undoing/redoing an action.
- Fixed a bug that caused an exception when undoing impedance subtraction.
- Fixed a bug that caused an exception when undoing the creation of a simulation.
- Fixed a bug that caused an exception when undoing the loading of a data set.
- Fixed a bug that caused focus to switch to another input in the file dialog window when pressing just the F key.
- Fixed a bug that prevented the table of data points and plots from updating when undoing/redoing impedance subtraction.
- Fixed bugs that occurred when trying to copy a mask or subtract an impedance with fewer than two data sets present in a project.
- Fixed issues detected by mypy.
- Fixed the incorrect label on the x-axis of the mu/chi-squared vs num. RC plot.
- Optimized the plotting tab to reduce loading times (by approx. 25-30 % based on testing).
- Refactored code and removed deprecated code.


# 1.1.0

- Added support for `.dfr` data format.


# 1.0.2

- Updated classifiers in `setup.py`.
- Fixed a bug that caused an error when deleting any data set.


# 1.0.1

- Added an Inno Setup Script for producing an installer for Windows.
- Updated About window.
- Updated docstrings.
- Fixed a bug in the `utility.is_filtered_item_visible` implementation that would cause the wrong result to be returned.
- Fixed a bug that prevented plots and the table of data points from updating when undoing/redoing toggling of the masked state of data points.
- Refactored code.


# 1.0.0

- Rewrote large parts of the program.
- Added the ability to create a project by merging two or more existing projects.
- Added remappable keybindings.
- Added a command palette that can be used to search for and to execute actions. Accessible by default via the Ctrl+P keybinding.
- Added individual toggles for most plots to set whether or not the plot's limits should be adjusted automatically when modifying the contents of the plot.
- Added a button for clearing the list of recent projects.
- Added a button for randomizing an active plot item's color.
- Various bug fixes.


# 0.3.0

- Added a "Plotting" tab that can be used to plot multiple data sets, test results, fit results, and simulation results in a single figure. Currently supports Nyquist, Bode (magnitude), and Bode (phase) plot types.
- Added a setting for specifying the number of points per decade to use when drawing simulated responses as lines.
- Added an "Edit" menu to the menu bar with "Undo" and "Redo" actions.
- Added indicators for when the program is busy loading data files or loading/saving projects.
- Added support for messages and progress bars to the indicator that is shown when the program is busy.
- Added a check to make sure there are no UUID collisions when saving a project.
- Added more keybindings.
- Added more tooltips.
- Updated the project file and config file structures to support the new features.
- Updated keybinding documentation.
- Updated existing tooltips.
- Updated the labels of some buttons.
- Updated the implementation of the recent projects table to update when a project is saved.
- Updated how paths, which are passed as CLI arguments, to data files and projects, and project snapshots are processed when the program is started.
- Updated CDC inputs in the fitting and simulation tabs to not require the Enter/Return key to be pressed before a fit or simulation can be performed.
- Updated the confirmation window, which is shown when possibly saving over an existing project file, to automatically adjust its height to accommodate long paths.
- Removed the restriction imposed on moving the error message window.
- Fixed a bug that allowed duplicate entries in the list of recent projects.
- Fixed a bug that allowed multiple instances of a project to be loaded.
- Fixed a bug that triggered state snapshots twice when toggling the mask state of multiple points.
- Fixed a bug that allowed specifying an invalid number of RC circuits for the Kramers-Kronig test.


# 0.2.1

- Fixed the handling of unsupported file formats when loading data sets.
- Fixed erroneous extension on state file for storing recently opened projects.
- Fixed the effect of editing notes on whether or not a project is dirty.
- Fixed a bug that caused an exception just before the program terminates.

# 0.2.0

- Added a confirmation window when possibly overwriting a file while saving a project under a new name.
- Added file extension filters to the file dialog when loading data sets.
- Added support for the new circuit validation that occurs prior to fitting a circuit.
- Updated the implementation of the window that is used for displaying error messages.
- Fixed a bug that prevented saving a project that had previously been saved, then modified just prior to an abrupt termination of the program, and finally restored from the snapshot created before the program terminated.


# 0.1.3

- Fixed a packaging bug that prevented the `console_script` entry point from working on Windows.


# 0.1.2

- Fixed a packaging bug that prevented the `console_script` entry point from working on Windows.


# 0.1.1

- Fixed a packaging bug that prevented third-party licenses from being included in the generated wheel.


# 0.1.0

- Initial public beta release.
