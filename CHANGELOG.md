# 3.1.3

- Fixed bugs that caused the toggling of a plottable series (e.g., a data set or a Kramers-Kronig test result) in the `Plotting` tab to apply the change to the wrong plot under certain circumstances.
- Fixed bugs that caused a failure to properly adjust the axis limits in cases where the difference between the maximum and minimum values being plotted was zero or all values were zero.


# 3.1.2

- Added the 3-sigma CI series to the legends of DRT plots.
- Updated the order that the mean and 3-sigma CI series are plotted in DRT plots.
- Updated labels of plotted series in the DRT plots.
- Updated the 3-sigma CI series to use the same alpha value in the `Plotting` tab as in the `DRT analysis` tab.
  A manual refresh of the plot is required for changes to take effect.
- Updated labels in the `DRT plots` section of the appearance settings window.


# 3.1.1

- Updated API documentation.


# 3.1.0

- Added the ability to copy circuit diagrams to the clipboard as SVG from the `Fitting` and `Simulation` tabs.
- Updated to use version 3.1.0 of `pyimpspec`, which resulted in the following changes:
	- Added `Circuit.to_drawing` method for drawing circuit diagrams using the `schemdraw` package.
	- Added support for using the `cvxpy` package as an optional solver in DRT calculations (TR-RBF method only).
	- Added `cvxpy` as an optional dependency.
	- Added `CircuitBuilder.__iadd__` method so that the `+=` operator can be used instead of the `CircuitBuilder.add` method.
	- Updated `Element.set_label`, `Element.set_fixed`, `Element.set_lower_limit`, and `Element.set_upper_limit` methods to return the element so that the calls can be chained (e.g., `Resistor(R=50).set_label("ct").set_fixed("R", True)`).
	- Updated the default terminal labels used in circuit diagrams.
- Updated the label of a terminal node in the circuit editor.
- Fixed a bug that prevented the lambda value input field from being disabled under certain circumstances when switching to the BHT method.
- Fixed a bug that prevented the "Copy output..." action in the command palette from working in the `DRT analysis` tab.
- Updated the minimum version for a dependency.
- Pinned Dear PyGui at version 1.6.2 until the automatic adjustment of axis limits in plots can be made to work properly with version 1.7.0.


# 3.0.0

**Breaking changes in the API!**

- `DataSet`, `TestResult`, `FitResult`, and `SimulationResult` methods such as `get_bode_data` that previously returned base-10 logarithms of, e.g., frequencies now instead return the non-logarithmic values.
- The `perform_exploratory_tests` function now returns a list of `deareis.TestResult` instead of a list of `pyimpspec.KramersKronigResult` and the results have already been sorted from best to worst.
- The `score_test_results` function has been removed.
- The `string_to_circuit` function has been renamed to `parse_cdc`.
- The `fit_circuit_to_data` function has been renamed to `fit_circuit`.
- The `PlotSeries` class now has methods such as `get_nyquist_data`, `get_bode_data`, etc.
  Thus, such objects can be either passed directly to the plotting functions available through the API of DearEIS or they can be used with unsupported plotting libraries.
  The underlying source of the data is stored in a `data` property but accessing the data needed for plotting purposes is best accessed via the methods.
	If the data is not available because the source does not contain it (e.g., `TestResult` objects do not have the data required to plot a distribution of relaxation times), then empty `numpy.ndarray` objects are returned.
- Some enums have been renamed (e.g., `Method` is now `CNLSMethod`).

# 

- Added a `DRT analysis` tab with support for calculating the distribution of relaxation times using a few different methods.
- Added appearance settings for the new plot types used in the `DRT analysis` tab.
- Added new keybindings for use in the `DRT analysis` tab.
- Added new plot types to the `Plotting` tab.
- Added support for rendering math using matplotlib.
- Added new plotting functions to the API.
- Added `perform_exploratory_tests` function to the API.
- Added overlay messages when switching to, e.g., another data set.
- Added `CircuitBuilder` class to the API.
- Updated tooltips (e.g., to make use of the new math rendering capability).
- Updated formatting of axis limits in the popup window for exporting plots created in the `Plotting` tab.
- Updated the appearances of plots (e.g., removal of grid lines and changing over to using logarithmic scales).
- Updated config file structure as a result of changes to plot exporting settings and the addition of DRT analysis settings.
- Updated the `Project` class and its corresponding file structure to support DRT analysis results.
- Updated how labels are generated for `TestResult`, `FitResult`, and `SimulationResult` objects.
- Updated buttons in the home tab to have dynamic labels according to whether or not recent projects have been selected.
- Updated overlay messages to use pyimpspec's API for more detailed progress information when performing, e.g., Kramers-Kronig tests.
- Updated number formatting.
- Refactored how the tabs are updated when switching to, e.g., another data set.
- Refactored the `deareis.mpl.plot` function to make better use of `pyimpspec`'s API.
- Refactored settings for exporting plots.
- Refactored the settings menus in the `Kramers-Kronig`, `Fitting`, and `Simulation` tabs.
- Refactored the window for defining default settings.
- Fixed bugs that caused (un)selecting groups of items in the `Plotting` tab to not work properly.


# 2.2.0

- Added `num_per_decade` argument to the `deareis.mpl.plot_fit` function.
- Added sorting of elements to the `to_dataframe` methods in the `FitResult` and `SimulationResult` classes.
- Updated the required minimum version for `pyimpspec`.
- Fixed a bug where an exception would occur in the GUI program because a `Project` instance created outside of the GUI program would not have a `PlotSettings` instance.
- Fixed bugs that prevented the entries for Kramers-Kronig test results and circuit fit results in the `Plotting` tab from updating properly when deleting those results or when undoing/redoing changes affecting those results.
- Removed `tabulate` as explicit dependency since it was added as an explicit dependency to `pyimpspec`.


# 2.1.0

- Added a setting for the interval for saving automatic backups to the `Settings - defaults` window.
- Added a changelog window that is shown automatically when DearEIS has been updated.
- Added the ability to check if a new version of DearEIS is available on PyPI.
	- The `requests` package has been added as a dependency.
- Updated minimum versions for dependencies.
- Updated the `About` window (e.g., so that the URLs can be highlighted and copied).
- Fixed a bug that caused the table of keybindings to not apply filters when updating.
- Refactored code.


# 2.0.1

- Added GitHub Actions workflow for testing the package (API only) on Linux (Ubuntu), MacOS, and Windows.
- Fixed issues that prevented tests from passing.


# 2.0.0

- Added a window for exporting plots using matplotlib.
	- Testing showed that attempting to free the memory allocated to the plot previews caused DearEIS to always crash on one of the computers used for testing.
	  The cause is not known at the moment but it could a bug in the GPU drivers (NVIDIA 515.57 on Linux) and/or in the GUI framework (Dear PyGui 1.6.2).
	- Two workarounds have been implemented in the form of two settings that can be found in the `Settings - defaults` window:
		- Disabling the `Clear texture registry` setting prevents the crashes without taking away the ability to have plot previews.
		  However, doing so introduces a memory leak since the memory allocated to each plot preview is not freed until DearEIS is closed.
		- Alternatively, enabling the `Disable plot previews` setting prevents the crashes without introducing a memory leak by not generating plot previews at all.
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
- Optimized the `Plotting` tab to reduce loading times (by approx. 25-30 % based on testing).
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

- Added a `Plotting` tab that can be used to plot multiple data sets, test results, fit results, and simulation results in a single figure. Currently supports Nyquist, Bode (magnitude), and Bode (phase) plot types.
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
