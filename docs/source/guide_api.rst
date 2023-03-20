.. include:: ./substitutions.rst

Application programming interface
=================================

The GUI is the primary interface of DearEIS but an API is also included for some batch processing capabilities.
However, if an API is the desired interface for performing various tasks, then using pyimpspec_ directly may be preferable.


Creating/loading a project
--------------------------


.. doctest::

   >>> from deareis import Project
   >>>
   >>> # Create a new project
   >>> project: Project = Project()
   >>>
   >>> # Load an existing project
   >>> project = Project.from_file("./tests/example-project-v5.json")


Batch importing data sets
-------------------------

.. doctest::

   >>> from deareis import DataSet, Project, parse_data
   >>>
   >>> project: Project = Project()
   >>>
   >>> data: DataSet
   >>> for data in parse_data("./tests/data-1.idf"):
   ...   project.add_data_set(data)
   >>>
   >>> # Remember to save the project somewhere as well!
   >>> # project.save("./tests/batch-imported-data.json")


Batch plotting results
----------------------

In the following example we will load a project, iterate over data sets, various results, simulations, and plots.
A single example of each of these will be plotted.

.. doctest::

   >>> from deareis import (
   ...   DRTResult,
   ...   DataSet,
   ...   FitResult,
   ...   PlotSettings,
   ...   Project,
   ...   SimulationResult,
   ...   TestResult,
   ...   ZHITResult,
   ...   mpl,
   ... )
   >>> import matplotlib.pyplot as plt
   >>>
   >>> project: Project = Project.from_file("./tests/example-project-v5.json")
   >>>
   >>> data: DataSet
   >>> for data in project.get_data_sets():
   ...   figure, axes = mpl.plot_data(
   ...     data,
   ...     colored_axes=True,
   ...     legend=False,
   ...   )
   ...
   ...   # Iterate over Kramers-Kronig results
   ...   test: TestResult
   ...   for test in project.get_tests(data):
   ...     figure, axes = mpl.plot_fit(
   ...       test,
   ...       data=data,
   ...       colored_axes=True,
   ...       legend=False,
   ...     )
   ...     break
   ...
   ...   # Iterate over Z-HIT results
   ...   zhit: ZHITResult
   ...   for zhit in project.get_zhits(data):
   ...     figure, axes = mpl.plot_fit(
   ...       zhit,
   ...       data=data,
   ...       colored_axes=True,
   ...       legend=False,
   ...     )
   ...     break
   ...
   ...   # Iterate over DRT results
   ...   drt: DRTResult
   ...   for drt in project.get_drts(data):
   ...     figure, axes = mpl.plot_drt(
   ...       drt,
   ...       data=data,
   ...       colored_axes=True,
   ...       legend=False,
   ...     )
   ...     break
   ...
   ...   # Iterate over circuit fits
   ...   fit: FitResult
   ...   for fit in project.get_fits(data):
   ...     figure, axes = mpl.plot_fit(
   ...       fit,
   ...       data=data,
   ...       colored_axes=True,
   ...       legend=False,
   ...     )
   ...     break
   ...   break
   >>>
   >>> # Iterate over simulations
   >>> sim: SimulationResult
   >>> for sim in project.get_simulations():
   ...   figure, axes = mpl.plot_nyquist(
   ...     sim,
   ...     line=True,
   ...     colored_axes=True,
   ...     legend=False,
   ...   )
   ...   break
   >>>
   >>> # Iterate over plots
   >>> plot: PlotSettings
   >>> for plot in project.get_plots():
   ...   figure, axes = mpl.plot(plot, project)
   ...   break
   >>>
   >>> plt.close("all")

.. raw:: latex

   \clearpage


.. plot::

   from deareis import Project, mpl
   project = Project.from_file("../../tests/example-project-v5.json")
   for data in project.get_data_sets():
     figure, axes = mpl.plot_data(
       data,
       colored_axes=True,
       legend=False,
     )
     figure.tight_layout()
     break


.. plot::

   from deareis import Project, mpl
   project = Project.from_file("../../tests/example-project-v5.json")
   for data in project.get_data_sets():
     for test in project.get_tests(data):
       figure, axes = mpl.plot_fit(
         test,
         data=data,
         colored_axes=True,
         legend=False,
       )
       figure.tight_layout()
       break
     break


.. plot::

   from deareis import Project, mpl
   project = Project.from_file("../../tests/example-project-v5.json")
   for data in project.get_data_sets():
     for zhit in project.get_zhits(data):
       figure, axes = mpl.plot_fit(
         zhit,
         data=data,
         colored_axes=True,
         legend=False,
       )
       figure.tight_layout()
       break
     break


.. plot::

   from deareis import Project, mpl
   project = Project.from_file("../../tests/example-project-v5.json")
   for data in project.get_data_sets():
     for drt in project.get_drts(data):
       figure, axes = mpl.plot_drt(
         drt,
         data=data,
         colored_axes=True,
         legend=False,
       )
       figure.tight_layout()
       break
     break


.. plot::

   from deareis import Project, mpl
   project = Project.from_file("../../tests/example-project-v5.json")
   for data in project.get_data_sets():
     for fit in project.get_fits(data):
       figure, axes = mpl.plot_fit(
         fit,
         data=data,
         colored_axes=True,
         legend=False,
       )
       figure.tight_layout()
       break
     break


.. plot::

   from deareis import Project, mpl
   project = Project.from_file("../../tests/example-project-v5.json")
   for sim in project.get_simulations():
     figure, axes = mpl.plot_nyquist(
       sim,
       line=True,
       colored_axes=True,
       legend=False,
     )
     figure.tight_layout()
     break


.. plot::

   from deareis import Project, mpl
   project = Project.from_file("../../tests/example-project-v5.json")
   for plot in project.get_plots():
     figure, axes = mpl.plot(plot, project)
     figure.tight_layout()
     break


.. raw:: latex

    \clearpage


Customized plots
----------------

The approach used in the previous example could be used as the basis for creating more complicated plots (i.e., select the data sets and results programmatically).
However, it may be more convenient to use DearEIS' GUI to select the data sets, results, etc. and assign colors, markers, etc.
The resulting |PlotSettings| and |PlotSeries| objects can then be used as the foundation for generating the final plot using either the plotting functions included with DearEIS or another plotting library.

.. doctest::

   >>> from deareis import (
   ...   PlotSeries,   # Wrapper class for DataSet, TestResult, etc.
   ...   PlotSettings, # The settings class for plots created via DearEIS' GUI
   ...   PlotType,     # Enum for different types of plots (e.g., Nyquist)
   ...   Project,
   ...   mpl,
   ... )
   >>> import matplotlib.pyplot as plt
   >>> from matplotlib.figure import Figure
   >>> from typing import (
   ...   Optional,
   ...   Tuple,
   ... )
   >>> 
   >>> # Prepare the figure that will be used to create a custom Nyquist plot.
   >>> figure, axis = plt.subplots()
   >>> axes = [axis]
   >>> 
   >>> # Load the project of interest.
   >>> project: Project = Project.from_file("./tests/example-project-v5.json")
   >>>
   >>> # Get the settings for the plot that contains the series (data sets,
   >>> # fit results, etc.) that we wish to plot.
   >>> plot: PlotSettings = [
   ...   plot for plot in project.get_plots()
   ...   if plot.get_label() == "Noisy"
   ... ][0]
   >>> 
   >>> # Each data set, fit result, etc. can be represented as a PlotSeries
   >>> # object that contains the required data and the style (color, marker, etc.).
   >>> series: PlotSeries
   >>> for series in project.get_plot_series(plot):
   ...   # Figure out if the series should be included in the figure legend.
   ...   label: Optional[str] = None
   ...   if series.has_legend():
   ...     label = series.get_label()
   ...       
   ...   # Figure out the color and marker.
   ...   color: Tuple[float, float, float, float] = series.get_color()
   ...   marker: Optional[str] = mpl.MPL_MARKERS.get(series.get_marker())
   ...   
   ...   # Determine whether or not the series should be plotted using markers,
   ...   # a line, or both.
   ...   # We will use the plotting functions provided by DearEIS in this example
   ...   # but you could use any plotting library that you wish. However, you
   ...   # would need to call, e.g., series.get_frequencies() and/or
   ...   # series.get_impedances() to get the relevant data.
   ...   if series.has_line():
   ...     _ = mpl.plot_nyquist(
   ...       series,
   ...       colors={"impedance": color},
   ...       markers={"impedance": marker},
   ...       line=True,
   ...       label=label if marker is None else "",
   ...       figure=figure,
   ...       axes=axes,
   ...       num_per_decade=50,
   ...     )
   ...     if marker is not None:
   ...       _ = mpl.plot_nyquist(
   ...         series,
   ...         colors={"impedance": color},
   ...         markers={"impedance": marker},
   ...         line=False,
   ...         label=label,
   ...         figure=figure,
   ...         axes=axes,
   ...         num_per_decade=-1,
   ...       )
   ...   elif marker is not None:
   ...     _ = mpl.plot_nyquist(
   ...       series,
   ...       colors={"impedance": color},
   ...       markers={"impedance": marker},
   ...       line=False,
   ...       label=label,
   ...       figure=figure,
   ...       axes=axes,
   ...       num_per_decade=-1,
   ...     )
   >>>     
   >>> # Add the figure title and legend.
   >>> _ = figure.suptitle(plot.get_label())
   >>> _ = axis.legend()


.. plot::

   from deareis import (
     PlotSeries,
     PlotSettings,
     PlotType,
     Project,
     mpl,
   )
   import matplotlib.pyplot as plt
   from matplotlib.figure import Figure
   from typing import (
     Optional,
     Tuple,
   )
   figure, axis = plt.subplots()
   axes = [axis]
   project: Project = Project.from_file("../../tests/example-project-v5.json")
   plot: PlotSettings = [plot for plot in project.get_plots() if plot.get_label() == "Noisy"][0]
   assert plot.get_type() == PlotType.NYQUIST
   series: PlotSeries
   for series in project.get_plot_series(plot):
     label: Optional[str] = None
     if series.has_legend():
       label = series.get_label()
     color: Tuple[float, float, float, float] = series.get_color()
     marker: Optional[str] = mpl.MPL_MARKERS.get(series.get_marker())
     if series.has_line():
       _ = mpl.plot_nyquist(
         series,
         colors={"impedance": color},
         markers={"impedance": marker},
         line=True,
         label=label if marker is None else "",
         figure=figure,
         axes=axes,
         num_per_decade=50,
       )
       if marker is not None:
         _ = mpl.plot_nyquist(
           series,
           colors={"impedance": color},
           markers={"impedance": marker},
           line=False,
           label=label,
           figure=figure,
           axes=axes,
           num_per_decade=-1,
         )
     elif marker is not None:
       _ = mpl.plot_nyquist(
         series,
         colors={"impedance": color},
         markers={"impedance": marker},
         line=False,
         label=label,
         figure=figure,
         axes=axes,
         num_per_decade=-1,
       )
   _ = figure.suptitle(plot.get_label())
   _ = axis.legend()

.. raw:: latex

    \clearpage


Generating tables
-----------------

Several of the various ``*Result`` classes have ``to_*_dataframe`` methods that return tables as ``pandas.DataFrame`` objects, which can be used to output, e.g., Markdown or LaTeX tables.

.. doctest::

   >>> from deareis import DataSet, FitResult, Project
   >>> project: Project = Project.from_file("./tests/example-project-v5.json")
   >>> data: DataSet = project.get_data_sets()[0]
   >>> fit: FitResult = project.get_fits(data)[0]
   >>> print(fit.to_parameters_dataframe().to_markdown(index=False))
   | Element   | Parameter   |         Value |   Std. err. (%) | Unit      | Fixed   |
   |:----------|:------------|--------------:|----------------:|:----------|:--------|
   | R_1       | R           |  99.9527      |      0.0270272  | ohm       | No      |
   | R_2       | R           | 200.295       |      0.0161674  | ohm       | No      |
   | C_1       | C           |   7.98618e-07 |      0.00251014 | F         | No      |
   | R_3       | R           | 499.93        |      0.0228817  | ohm       | No      |
   | W_1       | Y           |   0.000400664 |      0.0303242  | S*s^(1/2) | No      |
   >>> print(fit.to_parameters_dataframe(running=True).to_markdown(index=False))
   | Element   | Parameter   |         Value |   Std. err. (%) | Unit      | Fixed   |
   |:----------|:------------|--------------:|----------------:|:----------|:--------|
   | R_0       | R           |  99.9527      |      0.0270272  | ohm       | No      |
   | R_1       | R           | 200.295       |      0.0161674  | ohm       | No      |
   | C_2       | C           |   7.98618e-07 |      0.00251014 | F         | No      |
   | R_3       | R           | 499.93        |      0.0228817  | ohm       | No      |
   | W_4       | Y           |   0.000400664 |      0.0303242  | S*s^(1/2) | No      |

.. raw:: latex

    \clearpage


Generating circuit diagrams
---------------------------

``Circuit`` objects can be used to draw circuit diagrams.

.. doctest::

   >>> from deareis import DataSet, FitResult, Project
   >>> project: Project = Project.from_file("./tests/example-project-v5.json")
   >>> data: DataSet = project.get_data_sets()[0]
   >>> fit: FitResult = project.get_fits(data)[0]
   >>> print(fit.circuit.to_circuitikz())
   \begin{circuitikz}
     \draw (0,0) to[short, o-] (1,0);
     \draw (1.0,0.0) to[R=$R_{\rm 1}$] (3.0,0.0);
     \draw (3.0,-0.0) to[R=$R_{\rm 2}$] (5.0,-0.0);
     \draw (3.0,-1.5) to[capacitor=$C_{\rm 1}$] (5.0,-1.5);
     \draw (3.0,-0.0) to[short] (3.0,-1.5);
     \draw (5.0,-0.0) to[short] (5.0,-1.5);
     \draw (5.0,-0.0) to[R=$R_{\rm 3}$] (7.0,-0.0);
     \draw (5.0,-1.5) to[generic=$W_{\rm 1}$] (7.0,-1.5);
     \draw (5.0,-0.0) to[short] (5.0,-1.5);
     \draw (7.0,-0.0) to[short] (7.0,-1.5);
     \draw (7.0,0) to[short, -o] (8.0,0);
   \end{circuitikz}
   >>> print(fit.circuit.to_circuitikz(running=True))
   \begin{circuitikz}
     \draw (0,0) to[short, o-] (1,0);
     \draw (1.0,0.0) to[R=$R_{\rm 0}$] (3.0,0.0);
     \draw (3.0,-0.0) to[R=$R_{\rm 1}$] (5.0,-0.0);
     \draw (3.0,-1.5) to[capacitor=$C_{\rm 2}$] (5.0,-1.5);
     \draw (3.0,-0.0) to[short] (3.0,-1.5);
     \draw (5.0,-0.0) to[short] (5.0,-1.5);
     \draw (5.0,-0.0) to[R=$R_{\rm 3}$] (7.0,-0.0);
     \draw (5.0,-1.5) to[generic=$W_{\rm 4}$] (7.0,-1.5);
     \draw (5.0,-0.0) to[short] (5.0,-1.5);
     \draw (7.0,-0.0) to[short] (7.0,-1.5);
     \draw (7.0,0) to[short, -o] (8.0,0);
   \end{circuitikz}
   >>> figure = fit.circuit.to_drawing().draw()
   >>> figure = fit.circuit.to_drawing(running=True).draw()

.. plot::

   from deareis import Project
   project = Project.from_file("../../tests/example-project-v5.json")
   data = project.get_data_sets()[0]
   fit = project.get_fits(data)[0]
   fit.circuit.to_drawing().draw()
   fit.circuit.to_drawing(running=True).draw()

.. raw:: latex

    \clearpage

.. _generating_equations:

Generating equations
--------------------

Equations for the impedances of elements and circuits can be obtained in the form of SymPy_ expressions or LaTeX strings.

.. note::

   Equations **always** make use of a running count of the elements as the lower index in variables to avoid conflicting/duplicate variable names from different elements.
   Circuit diagrams and tables can also make use of running counts as lower indices if explicitly told to (e.g., ``circuit.to_drawing(running=True)``, ``circuit.to_circuitikz(running=True)``, or ``fit.to_parameters_dataframe(running=True)``).

.. doctest::

   >>> from deareis import DataSet, FitResult, Project
   >>> project: Project = Project.from_file("./tests/example-project-v5.json")
   >>> data: DataSet = project.get_data_sets()[0]
   >>> fit: FitResult = project.get_fits(data)[0]
   >>> print(fit.circuit.to_sympy())
   R_0 + 1/(2*I*pi*C_2*f + 1/R_1) + 1/(sqrt(2)*sqrt(pi)*Y_4*sqrt(I*f) + 1/R_3)
   >>> print(fit.circuit.to_latex())
   Z = R_{0} + \frac{1}{2 i \pi C_{2} f + \frac{1}{R_{1}}} + \frac{1}{\sqrt{2} \sqrt{\pi} Y_{4} \sqrt{i f} + \frac{1}{R_{3}}}

.. raw:: latex

    \clearpage
