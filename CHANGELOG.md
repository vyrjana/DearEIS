# 5.1.0 (2024/11/03)

- Added support for plotting DRT as a function of frequency in the `Plotting` tab.
- Added the ability to load Kramers-Kronig results as data sets.
- Added the ability to copy the circuit description code (CDC) of the fitted circuit from a Kramers-Kronig result.
- Added support for using the modified Akima spline as part of the Z-HIT analysis and set it as the new default.
- Updated support for migrating old user configuration file versions and testing of the process.
- Updated tooltips.
- Fixed a bug that caused parts of some modal windows to not be fully visible on some operating systems and/or desktop environments.
- Fixed a bug where plotting DRT as a function of frequency used the angular frequency on the x-axis but was labeled as frequency.
- Fixed a bug that caused an exception to be raised if a `DataSet` instance was included in a `PlotSettings` instance that was made to plot distributions of relaxation times.


# 5.0.1 (2024/09/10)

- Fixed a bug where merging the user and default configurations would raise an exception because key-value pairs could have differing value types (e.g., an enum in the user configuration and an integer in another default configuration).


# 5.0.0 (2024/09/03)

## Kramers-Kronig

- Added support for complex, real, and imaginary linear Kramers-Kronig tests implemented using least squares fitting.
  - The previous implementations based on matrix inversion are still available.
- Added a `Representation` setting that can be used to choose which immittance representation to perform the linear Kramers-Kronig tests on: admittance or impedance. There is also an option to perform the tests with both representations and then automatically suggest the one that seems to be the most appropriate.
- Added settings (`Log Fext`, `Minimum log Fext`, `Maximum log Fext`, `Number of Fext eval.`, and `Rapid Fext eval.`) related to the range of time constants used during the linear Kramers-Kronig tests. Fext is used to either extend (Fext > 1) or contract (Fext < 1) the limits of the range of time constants. See DOI:10.1149/1.2044210 (e.g., eq. 18) for more information `Fext`.
- Added a `Timeout` setting for the CNLS variant of the linear Kramers-Kronig test.
- Updated the `Exploratory test results` window:
  - If more than one immittance representation was tested, then one can switch between their results.
  - If more than one Fext was evaluated, then one can switch between their results.
  - Added a tab for plots that present the statistic that was minimized when optimizing Fext and the pseudo chi-squared values as a function of the number of RC elements for the chosen Fext value.
  - Added support for the additional methods for suggesting the optimal number of RC elements added in the latest version of pyimpspec.
    - The three new methods described by Plank et al. (2022, DOI:10.1109/IWIS57888.2022.9975131) with some modifications proposed by Yrjänä and Bobacka (2024, DOI:10.1016/j.electacta.2024.144951).
    - Two new methods described by Yrjänä and Bobacka (2024, DOI:10.1016/j.electacta.2024.144951).
  - Added support for combining multiple methods for suggesting the optimal number of RC elements.
  - Added support for using the automatically suggested lower and upper limits for the number of RC elements. These limits can also be set manually.
  - Added a static 3D plot (generated using matplotlib) of log pseudo chi-squared as a function of the number of RC elements and log Fext. Only available if the `Clear registry` setting is enabled and `Disable preview` setting is disabled (see the `Export plot` section in the default settings).
- Added additional entries to the table of statistics for a Kramers-Kronig test result. These include, e.g., the mean and standard deviation of the residuals, and p-values for some statistical tests performed on the residuals.
- Updated the default settings. The default settings should work for most scenarios and require nothing more than for the user to click the button to perform the test.
- Updated tooltips.



## Z-HIT analysis

- Added support for additional smoothing methods introduced in the latest version of pyimpspec.
- Added a setting for performing Z-HIT analyses on the admittance representation instead of the impedance representation.


## DRT analysis

- Added support for choosing the cross-validation method to use in conjunction with the TR-RBF method. The cross-validation method is used to pick a suitable lambda value.
- See the changelog for the latest version of pyimpspec for other changes related to DRT methods.
- Added the ability to toggle between plotting DRT spectra as a function of the time constant (in seconds) and the frequency (in hertz).
- Updated tooltips.


## Fitting

- Added a button that copies the fitted circuit of the currently active result and uses the fitted values as the initial values in preparation for a new fit.
- Added the ability to drag-and-drop elements from the list of elements into the node editor part of the `Circuit editor` window.
- Moved the parameter adjustment into a tab in the `Circuit editor` window. The tab is only visible when the equivalent circuit model is valid (i.e., there are no missing or invalid connections).
- Updated the widgets for adjusting a circuit element's parameter. If the value is represented as `m*10^n`, then there is now a slider that represents `log m` and a drop-down list representing `n`. The slider represents values in the range from 0 to 3 and the the items in the drop-down list represent the SI prefixes in the range 10^-30 to 10^30. There is still an input field for typing in a value directly and using that will update both the slider and drop-down list (and vice versa). If the value needs to be zero, then it has to be typed into the input field. Negative values can be adjusted with the slider after typing a negative value into the input field first. The slider will then adjust the magnitude as it would for positive values (i.e., low to high absolute values from left to right) and then multiply the value by -1.


## Simulation

- Added a modal window, which allows specifying the amount of noise to add to the impedance spectrum, when loading a simulation result as a data set.


## Plotting

- Updated the preview in the `Export plot` window to always use 100 DPI.
- Deprecated the preview limits setting.


## Miscellaneous

- Added support for changing the default values of parameters for circuit elements (e.g., the default resistance of a resistor). These values can be changed in `Settings > Defaults`.
- Added a checkbox to the `Data sets` tab for toggling the visibility of a tooltip that shows the frequency of the data point closest to the mouse cursor in the Nyquist plot.
- Added checkboxes to various tabs for toggling between plotting the impedance or the admittance representation of the immittance data.
- Updated migration of project files to automatically save a backup of the pre-migrated project with `.backupN` extensions where `N` is some integer that is incremented so as to avoid overwriting previous backups.
- Updated how project snapshots are handled at initialization and when closing a project while discarding changes.
- Updated automatic adjustment of limits for y-axes in plots of real and imaginary impedances.
- Updated minimum versions of dependencies.
- Updated tooltips.
- Updated the error message window.
- Fixed a bug that prevented modification of the regularization parameter in the `DRT analysis` tab after switching to a method that does not make use of the regularization parameter input.
- Refactored code.


# 4.2.1 (2024/03/14)

- Maintenance release that updates the version requirements for dependencies.
- Support for Python 3.8 has been dropped due to minimum requirements set by one or more dependencies.
- Support for Python 3.11 and 3.12 has been added.


# 4.2.0 (2023/04/03)

- Added support for choosing between multiple approaches to suggesting the regularization parameter (lambda) in DRT methods utilizing Tikhonov regularization.
- Added a `Data set palette` for searching and selecting data sets via a window similar to the `Command palette`.
- Added a `Result palette` for searching and selecting various results (depending on the context) via a window similar to the `Command palette`.
- Added an `Add parallel impedance` window, which is accessible via the `Process` button in the `Data sets` tab. This is useful for, e.g., Kramers-Kronig testing impedance data that include negative differential resistances.
- Updated the table of fitted parameters in the `Fitting` tab to highlight parameters with large estimated errors.
- Updated the table of statistics in the `Fitting` tab to highlight values that may be indicative of issues.
- Updated tooltips.
- Refactored code.
- Fixed a bug that caused two click of the `Accept` button in the `Subtract impedance` window after opening and closing the circuit editor.
- Fixed a bug that caused an exception when opening and closing the circuit editor in the `Subtract impedance` window two or more times in a row.
- Fixed a bug where loading a simulation result as a data set would also cause the `Simulation` tab to switch to the latest simulation result.
- Fixed a mistake in the docstring of the DRTResult class.
- Possibly fixed a bug where resizing signals could sometimes cause an exception to occur while launching the program.


# 4.1.0 (2023/03/22)

- Added a `Copy` button next to the fit results in the `Subtract impedance` window. This button can be used to copy a fitted circuit to the `Circuit` option above.
- Updated appearance of nodes and links of fitted/simulated circuits in the `Fitting`/`Simulation` tab.
- Updated how plots are resized in various tabs.
- Refactored some parts of the `Subtract impedance` window.
- Fixed a bug where selecting a data set in the `Simulation` tab by using the mouse caused the current simulation result to become deselected.


# 4.0.1 (2023/03/21)

- Fixed a bug that caused the mask that was applied to the original data to also be applied to the new data set when subtracting impedances.
- Fixed bugs related to keybindings in the file dialog window.
- Fixed bugs causing plots in the `Fitting` and `Simulation` tabs to have incorrect heights on Windows.


# 4.0.0 (2023/03/20)

- Added `Getting started` window when running DearEIS for the first time.
- Added ability to replace outliers with interpolated points.
- Added `Process` button to the `Data sets` tab in the spot where the `Average` button used to be and clicking the button opens a popup with `Average`, `Interpolate`, and `Subtract` buttons.
- Added multiple plot types to most tabs and several modal windows as sub-tabs for each plot type.
- Added ability to perform batch analyses via the GUI.
- Added `Series resistance/capacitance/inductance` rows to the statistics table in the `Kramers-Kronig` tab.
- Added `Z-HIT analysis` tab for reconstructing modulus data from phase data.
- Added `Timeout` setting for the TR-RBF method in the `DRT analysis` tab.
- Added a row for the log pseudo chi-squared to the statistics table in the `Fitting` tab.
- Added highlighting of fitted parameters with values that were restricted by the lower or upper limit in the `Fitting` tab.
- Added an `Adjust parameters` button, which brings up a window for adjusting initial values with a real-time preview, to the `Fitting` and `Simulation` tabs.
- Added `Duplicate` button to the `Plotting` tab.
- Added a window for defining a path to a Python script/package that defines one or more user-defined elements using pyimpspec's API.
- Added setting for specifying how many parallel processes to use when, e.g., fitting circuits.
- Updated to use version 4.0.0 of pyimpspec.
- Updated project file and configuration file structures.
- Updated DRTSettings implementation regarding the settings for the m(RQ)fit method.
- Updated how "save as" works for projects (a new project tab is created alongside the original project tab after saving).
- Updated how result labels are displayed in their respective drop-down lists.
- Updated labels on plot axes, table headers, etc.
- Updated the layout of the window for averaging data sets.
- Updated tooltips.
- Updated the `Subtract impedances` function to result in the creation of a new data set instead of replacing the existing data set.
- Updated the keybindings in most of the modal windows to be based on similar keybindings that are available in other contexts (i.e., these keybindings are also affected by changes made by the user).
- Switched to Sphinx for documentation.


# 3.4.3 (2022/12/14)

- Updated dependency versions.
- Fixed a bug that caused `utility.format_number` to produce results with two exponents when given certain inputs.


# 3.4.2 (2022/11/28)

- Updated documentation.


# 3.4.1 (2022/11/26)

- Updated minimum version for pyimpspec.


# 3.4.0 (2022/11/26)

- Added labels above the circuit previes in the `Fitting` and `Simulation` tabs to clarify that those correspond to the circuits used in the chosen result rather than what is specified in the settings on the left-hand side.
- Added button that opens URL to tutorials.
- Updated how/when certain assets are rendered during startup.
- Updated how the y-axis limits of DRT plots are automatically adjusted.
- Updated tooltips.
- Fixed a bug that caused data sets to be incorrectly prevented from being selected in the `Average of multiple data sets` and `Subtract impedance` windows.
- Fixed a bug that caused DRT results to not always load properly.


# 3.3.0 (2022/11/22)

- Added clickable hyperlinks to the `About` window.
- Added the ability to subtract the impedance of a fitted circuit in the `Subtract impedance` window by choosing an existing fit result.
- Updated the `Spectrum` combo in the `Subtract impedance` window to only show other data sets with the same number of points and matching frequencies as the active data set.
- Updated the `Average of multiple data sets` window to only show data sets with the same number of points and matching frequencies as the first data set that is chosen.
- Updated how LaTeX tables are generated when copying, e.g., fitted parameter tables.
- Fixed the BHT method (DRT analysis) so that it works properly when `num_procs` is set to greater than one and NumPy is using OpenBLAS.


# 3.2.0 (2022/11/01)

- Added support for calculating the distribution of relaxation times using the `m(RQ)fit` method.
- Added support (including a keybinding) for loading a simulated spectrum as a data set.
- Added alternative forms of outputting circuit diagrams as SVG without terminal labels or any labels at all.
- Updated DearPyGui version requirement to 1.7.3.
- Updated `DRT analysis` tab to only show settings relevant to the currently chosen method.
- Updated how the `utility.format_number` function handles the `numpy.nan` value.
- Updated how the y-axis limits of DRT plots are automatically adjusted.
- Updated tooltips.
- Fixed a bug that prevented choosing to use anything but the complex data when performing a DRT analysis using the TR-RBF method.
- Fixed a bug that was triggered by having too few unmasked data points when performing Kramers-Kronig tests.


# 3.1.3 (2022/09/21)

- Fixed bugs that caused the toggling of a plottable series (e.g., a data set or a Kramers-Kronig test result) in the `Plotting` tab to apply the change to the wrong plot under certain circumstances.
- Fixed bugs that caused a failure to properly adjust the axis limits in cases where the difference between the maximum and minimum values being plotted was zero or all values were zero.


# 3.1.2 (2022/09/15)

- Added the 3-sigma CI series to the legends of DRT plots.
- Updated the order that the mean and 3-sigma CI series are plotted in DRT plots.
- Updated labels of plotted series in the DRT plots.
- Updated the 3-sigma CI series to use the same alpha value in the `Plotting` tab as in the `DRT analysis` tab.
  A manual refresh of the plot is required for changes to take effect.
- Updated labels in the `DRT plots` section of the appearance settings window.


# 3.1.1 (2022/09/13)

- Updated API documentation.


# 3.1.0 (2022/09/11)

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


# 3.0.0 (2022/09/05)

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


# 2.2.0 (2022/08/10)

- Added `num_per_decade` argument to the `deareis.mpl.plot_fit` function.
- Added sorting of elements to the `to_dataframe` methods in the `FitResult` and `SimulationResult` classes.
- Updated the required minimum version for `pyimpspec`.
- Fixed a bug where an exception would occur in the GUI program because a `Project` instance created outside of the GUI program would not have a `PlotSettings` instance.
- Fixed bugs that prevented the entries for Kramers-Kronig test results and circuit fit results in the `Plotting` tab from updating properly when deleting those results or when undoing/redoing changes affecting those results.
- Removed `tabulate` as explicit dependency since it was added as an explicit dependency to `pyimpspec`.


# 2.1.0 (2022/08/04)

- Added a setting for the interval for saving automatic backups to the `Settings - defaults` window.
- Added a changelog window that is shown automatically when DearEIS has been updated.
- Added the ability to check if a new version of DearEIS is available on PyPI.
	- The `requests` package has been added as a dependency.
- Updated minimum versions for dependencies.
- Updated the `About` window (e.g., so that the URLs can be highlighted and copied).
- Fixed a bug that caused the table of keybindings to not apply filters when updating.
- Refactored code.


# 2.0.1 (2022/08/01)

- Added GitHub Actions workflow for testing the package (API only) on Linux (Ubuntu), MacOS, and Windows.
- Fixed issues that prevented tests from passing.


# 2.0.0 (2022/07/31)

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


# 1.1.0 (2022/07/13)

- Added support for `.dfr` data format.


# 1.0.2 (2022/07/09)

- Updated classifiers in `setup.py`.
- Fixed a bug that caused an error when deleting any data set.


# 1.0.1 (2022/07/05)

- Added an Inno Setup Script for producing an installer for Windows.
- Updated About window.
- Updated docstrings.
- Fixed a bug in the `utility.is_filtered_item_visible` implementation that would cause the wrong result to be returned.
- Fixed a bug that prevented plots and the table of data points from updating when undoing/redoing toggling of the masked state of data points.
- Refactored code.


# 1.0.0 (2022/06/16)

- Rewrote large parts of the program.
- Added the ability to create a project by merging two or more existing projects.
- Added remappable keybindings.
- Added a command palette that can be used to search for and to execute actions. Accessible by default via the Ctrl+P keybinding.
- Added individual toggles for most plots to set whether or not the plot's limits should be adjusted automatically when modifying the contents of the plot.
- Added a button for clearing the list of recent projects.
- Added a button for randomizing an active plot item's color.
- Various bug fixes.


# 0.3.0 (2022/04/04)

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


# 0.2.1 (2022/03/28)

- Fixed the handling of unsupported file formats when loading data sets.
- Fixed erroneous extension on state file for storing recently opened projects.
- Fixed the effect of editing notes on whether or not a project is dirty.
- Fixed a bug that caused an exception just before the program terminates.

# 0.2.0 (2022/03/28)

- Added a confirmation window when possibly overwriting a file while saving a project under a new name.
- Added file extension filters to the file dialog when loading data sets.
- Added support for the new circuit validation that occurs prior to fitting a circuit.
- Updated the implementation of the window that is used for displaying error messages.
- Fixed a bug that prevented saving a project that had previously been saved, then modified just prior to an abrupt termination of the program, and finally restored from the snapshot created before the program terminated.


# 0.1.3 (2022/03/28)

- Fixed a packaging bug that prevented the `console_script` entry point from working on Windows.


# 0.1.2 (2022/03/28)

- Fixed a packaging bug that prevented the `console_script` entry point from working on Windows.


# 0.1.1 (2022/03/28)

- Fixed a packaging bug that prevented third-party licenses from being included in the generated wheel.


# 0.1.0 (2022/03/28)

- Initial public beta release.
