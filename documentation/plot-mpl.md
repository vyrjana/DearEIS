---
layout: documentation
title: API - plotting - matplotlib
permalink: /api/plot-mpl/
---

These functions are for basic visualization of various objects (e.g., `DataSet`, `TestResult`, and `FitResult`) using the [matplotlib](https://matplotlib.org/) package.
            

**Table of Contents**

- [deareis.api.plot.mpl](#deareisapiplotmpl)
	- [plot](#deareisapiplotmplplot)
	- [plot_bode](#deareisapiplotmplplot_bode)
	- [plot_circuit](#deareisapiplotmplplot_circuit)
	- [plot_complex_impedance](#deareisapiplotmplplot_complex_impedance)
	- [plot_data](#deareisapiplotmplplot_data)
	- [plot_drt](#deareisapiplotmplplot_drt)
	- [plot_exploratory_tests](#deareisapiplotmplplot_exploratory_tests)
	- [plot_fit](#deareisapiplotmplplot_fit)
	- [plot_gamma](#deareisapiplotmplplot_gamma)
	- [plot_imaginary_impedance](#deareisapiplotmplplot_imaginary_impedance)
	- [plot_impedance_magnitude](#deareisapiplotmplplot_impedance_magnitude)
	- [plot_impedance_phase](#deareisapiplotmplplot_impedance_phase)
	- [plot_mu_xps](#deareisapiplotmplplot_mu_xps)
	- [plot_nyquist](#deareisapiplotmplplot_nyquist)
	- [plot_real_impedance](#deareisapiplotmplplot_real_impedance)
	- [plot_residual](#deareisapiplotmplplot_residual)



## **deareis.api.plot.mpl**

### **deareis.api.plot.mpl.plot**

Plot a complex plot containing one or more items from a project based on the provided settings.

```python
def plot(settings: PlotSettings, project: Project, x_limits: Optional[Tuple[Optional[float], Optional[float]]] = None, y_limits: Optional[Tuple[Optional[float], Optional[float]]] = None, show_title: bool = True, show_legend: Optional[bool] = None, legend_loc: Union[int, str] = 0, show_grid: bool = False, tight_layout: bool = False, fig: Optional[Figure] = None, axis: Optional[Axes] = None, num_per_decade: int = 100) -> Tuple[Figure, Axes]:
```


_Parameters_

- `settings`: The settings for the plot.
- `project`: The project that the plot is a part of.
- `x_limits`: The lower and upper limits of the x-axis.
- `y_limits`: The lower and upper limits of the y-axis.
- `show_title`: Whether or not to include the title in the figure.
- `show_legend`: Whether or not to include a legend in the figure.
- `legend_loc`: The position of the legend in the figure. See matplotlib's documentation for valid values.
- `show_grid`: Whether or not to include a grid in the figure.
- `tight_layout`: Whether or not to apply a tight layout that the sizes of the reduces margins.
- `fig`: The matplotlib.figure.Figure instance to use when plotting the data.
- `axis`: The matplotlib.axes.Axes instance to use when plotting the data.
- `num_per_decade`: If any circuit fits, circuit simulations, or Kramers-Kronig test results are included in the plot, then this parameter can be used to change how many points are used to draw the line (i.e. how smooth or angular the line looks).


_Returns_

```python
Tuple[Figure, Axes]
```
### **deareis.api.plot.mpl.plot_bode**

Plot some data as a Bode plot (\|Z\| and phi vs f).

```python
def plot_bode(data: Union[DataSet, TestResult, FitResult, DRTResult], color_magnitude: str = "black", color_phase: str = "black", marker_magnitude: str = "o", marker_phase: str = "s", line: bool = False, label: Optional[str] = None, legend: bool = True, fig: Optional[Figure] = None, axes: List[Axes] = [], num_per_decade: int = 100, adjust_axes: bool = True) -> Tuple[Figure, List[Axes]]:
```


_Parameters_

- `data`: The data to plot.
DataSet instances are plotted using markers (optionally as a line) while all other types of data are plotted as lines.
- `color_magnitude`: The color of the marker or line for the absolute magnitude of the impedance.
- `color_phase`: The color of the marker or line) for the phase shift of the impedance.
- `marker_magnitude`: The marker for the absolute magnitude of the impedance.
- `marker_phase`: The marker for the phase shift of the impedance.
- `line`: Whether or not a DataSet instance should be plotted as a line instead.
- `label`: The optional label to use in the legend.
- `legend`: Whether or not to add a legend.
- `fig`: The matplotlib.figure.Figure instance to use when plotting the data.
- `axes`: A list of matplotlib.axes.Axes instances to use when plotting the data.
- `num_per_decade`: If the data being plotted is not a DataSet instance (e.g. a TestResult instance), then this parameter can be used to change how many points are used to draw the line (i.e. how smooth or angular the line looks).
- `adjust_axes`: Whether or not to adjust the axes (label, scale, limits, etc.).


_Returns_

```python
Tuple[Figure, List[Axes]]
```
### **deareis.api.plot.mpl.plot_circuit**

Plot the simulated impedance response of a circuit as both a Nyquist and a Bode plot.

```python
def plot_circuit(circuit: Circuit, f: Union[List[float], ndarray] = [], min_f: float = 0.1, max_f: float = 100000.0, color_nyquist: str = "#CC3311", color_bode_magnitude: str = "#CC3311", color_bode_phase: str = "#009988", data: Optional[DataSet] = None, visible_data: bool = False, title: Optional[str] = None, label: Optional[str] = None, legend: bool = True, fig: Optional[Figure] = None, axes: List[Axes] = []) -> Tuple[Figure, List[Axes]]:
```


_Parameters_

- `circuit`: The circuit to use when simulating the impedance response.
- `f`: The frequencies (in hertz) to use when simulating the impedance response.
If no frequencies are provided, then the range defined by the min_f and max_f parameters will be used instead.
Alternatively, a DataSet instance can be provided via the data parameter.
- `min_f`: The lower limit of the frequency range to use if a list of frequencies is not provided.
- `max_f`: The upper limit of the frequency range to use if a list of frequencies is not provided.
- `color_nyquist`: The color to use in the Nyquist plot.
- `color_bode_magnitude`: The color to use for the magnitude in the Bode plot.
- `color_bode_phase`: The color to use for the phase shift in the Bode plot.
- `data`: An optional DataSet instance.
If provided, then the frequencies of this instance will be used when simulating the impedance spectrum of the circuit.
- `visible_data`: Whether or not the optional DataSet instance should also be plotted alongside the simulated impedance spectrum of the circuit.
- `title`: The title of the figure.
If not title is provided, then the circuit description code of the circuit is used instead.
- `label`: The optional label to use in the legend.
- `legend`: Whether or not to add a legend.
- `fig`: The matplotlib.figure.Figure instance to use when plotting the data.
- `axes`: A list of matplotlib.axes.Axes instances to use when plotting the data.


_Returns_

```python
Tuple[Figure, List[Axes]]
```
### **deareis.api.plot.mpl.plot_complex_impedance**

Plot the real and imaginary parts of the impedance of some data.

```python
def plot_complex_impedance(data: Union[DataSet, TestResult, FitResult, DRTResult], color_real: str = "black", color_imaginary: str = "black", marker_real: str = "o", marker_imaginary: str = "s", line: bool = False, label: Optional[str] = None, legend: bool = True, fig: Optional[Figure] = None, axes: List[Axes] = [], num_per_decade: int = 100, adjust_axes: bool = True) -> Tuple[Figure, List[Axes]]:
```


_Parameters_

- `data`: The data to plot.
DataSet instances are plotted using markers (optionally as a line) while all other types of data are plotted as lines.
- `color_real`: The color of the marker or line for the real part of the impedance.
- `color_imaginary`: The color of the marker or line for the imaginary part of the impedance.
- `marker_real`: The marker for the real part of the impedance.
- `marker_imaginary`: The marker for the imaginary part of the impedance.
- `line`: Whether or not a DataSet instance should be plotted as a line instead.
- `label`: The optional label to use in the legend.
- `legend`: Whether or not to add a legend.
- `fig`: The matplotlib.figure.Figure instance to use when plotting the data.
- `axes`: A list of matplotlib.axes.Axes instances to use when plotting the data.
- `num_per_decade`: If the data being plotted is not a DataSet instance (e.g. a TestResult instance), then this parameter can be used to change how many points are used to draw the line (i.e. how smooth or angular the line looks).
- `adjust_axes`: Whether or not to adjust the axes (label, scale, limits, etc.).


_Returns_

```python
Tuple[Figure, List[Axes]]
```
### **deareis.api.plot.mpl.plot_data**

Plot a DataSet instance as both a Nyquist and a Bode plot.

```python
def plot_data(data: DataSet, title: Optional[str] = None, label: Optional[str] = None, legend: bool = True, fig: Optional[Figure] = None, axes: List[Axes] = []) -> Tuple[Figure, List[Axes]]:
```


_Parameters_

- `data`: The DataSet instance to plot.
- `title`: The title of the figure.
If not title is provided, then the label of the DataSet is used instead.
- `label`: The optional label to use in the legend.
- `legend`: Whether or not to add a legend.
- `fig`: The matplotlib.figure.Figure instance to use when plotting the data.
- `axes`: A list of matplotlib.axes.Axes instances to use when plotting the data.


_Returns_

```python
Tuple[Figure, List[Axes]]
```
### **deareis.api.plot.mpl.plot_drt**

Plot the result of calculating the distribution of relaxation times (DRT) as a Bode plot, a DRT plot, and a plot of the residuals.

```python
def plot_drt(drt: DRTResult, data: Optional[DataSet] = None, peak_threshold: float = -1.0, title: Optional[str] = None, label: Optional[str] = None, legend: bool = True, fig: Optional[Figure] = None, axes: List[Axes] = []) -> Tuple[Figure, List[Tuple[Axes]]]:
```


_Parameters_

- `drt`: The result to plot.
- `data`: The DataSet instance that was used in the DRT calculations.
- `peak_threshold`: The threshold to use for identifying and marking peaks (0.0 to 1.0, relative to the highest peak).
Negative values disable marking peaks.
- `title`: The title of the figure.
If no title is provided, then the circuit description code (and label of the DataSet) is used instead.
- `label`: The optional label to use in the legend.
- `legend`: Whether or not to add a legend.
- `fig`: The matplotlib.figure.Figure instance to use when plotting the data.
- `axes`: A list of matplotlib.axes.Axes instances to use when plotting the data.


_Returns_

```python
Tuple[Figure, List[Tuple[Axes]]]
```
### **deareis.api.plot.mpl.plot_exploratory_tests**

Plot the results of an exploratory Kramers-Kronig test as a Nyquist plot, a Bode plot, a plot of the residuals, and a plot of the mu- and pseudo chi-squared values.

```python
def plot_exploratory_tests(tests: List[TestResult], mu_criterion: float, data: DataSet, title: Optional[str] = None, legend: bool = True, fig: Optional[Figure] = None, axes: List[Axes] = []) -> Tuple[Figure, List[Axes]]:
```


_Parameters_

- `tests`: The results to plot.
- `mu_criterion`: The mu-criterion to apply.
- `data`: The DataSet instance that was tested.
- `title`: The title of the figure.
If no title is provided, then the label of the DataSet is used instead.
- `legend`: Whether or not to add a legend.
- `fig`: The matplotlib.figure.Figure instance to use when plotting the data.
- `axes`: A list of matplotlib.axes.Axes instances to use when plotting the data.


_Returns_

```python
Tuple[Figure, List[Axes]]
```
### **deareis.api.plot.mpl.plot_fit**

Plot the result of a fit as a Nyquist plot, a Bode plot, and a plot of the residuals.

```python
def plot_fit(fit: Union[TestResult, FitResult, DRTResult], data: Optional[DataSet] = None, title: Optional[str] = None, label: Optional[str] = None, legend: bool = True, fig: Optional[Figure] = None, axes: List[Axes] = [], num_per_decade: int = 100) -> Tuple[Figure, List[Tuple[Axes]]]:
```


_Parameters_

- `fit`: The circuit fit or test result.
- `data`: The DataSet instance that a circuit was fitted to.
- `title`: The title of the figure.
If no title is provided, then the circuit description code (and label of the DataSet) is used instead.
- `label`: The optional label to use in the legend.
- `legend`: Whether or not to add a legend.
- `fig`: The matplotlib.figure.Figure instance to use when plotting the data.
- `axes`: A list of matplotlib.axes.Axes instances to use when plotting the data.
- `num_per_decade`: If the data being plotted is not a DataSet instance (e.g. a TestResult instance), then this parameter can be used to change how many points are used to draw the line (i.e. how smooth or angular the line looks).


_Returns_

```python
Tuple[Figure, List[Tuple[Axes]]]
```
### **deareis.api.plot.mpl.plot_gamma**

Plot the distribution of relaxation times (gamma vs tau).

```python
def plot_gamma(drt: DRTResult, peak_threshold: float = -1.0, color: Any = "black", bounds_alpha: float = 0.3, label: Optional[str] = None, legend: bool = True, fig: Optional[Figure] = None, axis: Optional[Axes] = None, adjust_axes: bool = True) -> Tuple[Figure, Axes]:
```


_Parameters_

- `drt`: The result to plot.
- `peak_threshold`: The threshold to use for identifying and marking peaks (0.0 to 1.0, relative to the highest peak).
Negative values disable marking peaks.
- `color`: The color to use to plot the data.
- `bounds_alpha`: The alpha to use when plotting the bounds of the Bayesian credible intervals (if they are included in the data).
- `label`: The optional label to use in the legend.
- `legend`: Whether or not to add a legend.
- `fig`: The matplotlib.figure.Figure instance to use when plotting the data.
- `axis`: The matplotlib.axes.Axes instance to use when plotting the data.
- `adjust_axes`: Whether or not to adjust the axes (label, scale, limits, etc.).


_Returns_

```python
Tuple[Figure, Axes]
```
### **deareis.api.plot.mpl.plot_imaginary_impedance**

Plot the imaginary impedance of some data (-Zim vs f).

```python
def plot_imaginary_impedance(data: Union[DataSet, TestResult, FitResult, DRTResult], color: Any = "black", marker: str = "s", line: bool = False, label: Optional[str] = None, legend: bool = True, fig: Optional[Figure] = None, axis: Optional[Axes] = None, num_per_decade: int = 100, adjust_axes: bool = True) -> Tuple[Figure, Axes]:
```


_Parameters_

- `data`: The data to plot.
DataSet instances are plotted using markers (optionally as a line) while all other types of data are plotted as lines.
- `color`: The color of the marker or line.
- `marker`: The marker.
- `line`: Whether or not a DataSet instance should be plotted as a line instead.
- `label`: The optional label to use in the legend.
- `legend`: Whether or not to add a legend.
- `fig`: The matplotlib.figure.Figure instance to use when plotting the data.
- `axis`: The matplotlib.axes.Axes instance to use when plotting the data.
- `num_per_decade`: If the data being plotted is not a DataSet instance (e.g. a TestResult instance), then this parameter can be used to change how many points are used to draw the line (i.e. how smooth or angular the line looks).
- `adjust_axes`: Whether or not to adjust the axes (label, scale, limits, etc.).


_Returns_

```python
Tuple[Figure, Axes]
```
### **deareis.api.plot.mpl.plot_impedance_magnitude**

Plot the absolute magnitude of the impedance of some data (\|Z\| vs f).

```python
def plot_impedance_magnitude(data: Union[DataSet, TestResult, FitResult, DRTResult], color: Any = "black", marker: str = "o", line: bool = False, label: Optional[str] = None, legend: bool = True, fig: Optional[Figure] = None, axis: Optional[Axes] = None, num_per_decade: int = 100, adjust_axes: bool = True) -> Tuple[Figure, Axes]:
```


_Parameters_

- `data`: The data to plot.
DataSet instances are plotted using markers (optionally as a line) while all other types of data are plotted as lines.
- `color`: The color of the marker or line.
- `marker`: The marker.
- `line`: Whether or not a DataSet instance should be plotted as a line instead.
- `label`: The optional label to use in the legend.
- `legend`: Whether or not to add a legend.
- `fig`: The matplotlib.figure.Figure instance to use when plotting the data.
- `axis`: The matplotlib.axes.Axes instance to use when plotting the data.
- `num_per_decade`: If the data being plotted is not a DataSet instance (e.g. a TestResult instance), then this parameter can be used to change how many points are used to draw the line (i.e. how smooth or angular the line looks).
- `adjust_axes`: Whether or not to adjust the axes (label, scale, limits, etc.).


_Returns_

```python
Tuple[Figure, Axes]
```
### **deareis.api.plot.mpl.plot_impedance_phase**

Plot the phase shift of the impedance of some data (phi vs f).

```python
def plot_impedance_phase(data: Union[DataSet, TestResult, FitResult, DRTResult], color: Any = "black", marker: str = "o", line: bool = False, label: Optional[str] = None, legend: bool = True, fig: Optional[Figure] = None, axis: Optional[Axes] = None, num_per_decade: int = 100, adjust_axes: bool = True) -> Tuple[Figure, Axes]:
```


_Parameters_

- `data`: The data to plot.
DataSet instances are plotted using markers (optionally as a line) while all other types of data are plotted as lines.
- `color`: The color of the marker or line.
- `marker`: The marker.
- `line`: Whether or not a DataSet instance should be plotted as a line instead.
- `label`: The optional label to use in the legend.
- `legend`: Whether or not to add a legend.
- `fig`: The matplotlib.figure.Figure instance to use when plotting the data.
- `axis`: The matplotlib.axes.Axes instance to use when plotting the data.
- `num_per_decade`: If the data being plotted is not a DataSet instance (e.g. a TestResult instance), then this parameter can be used to change how many points are used to draw the line (i.e. how smooth or angular the line looks).
- `adjust_axes`: Whether or not to adjust the axes (label, scale, limits, etc.).


_Returns_

```python
Tuple[Figure, Axes]
```
### **deareis.api.plot.mpl.plot_mu_xps**

Plot the mu-values and pseudo chi-squared values of Kramers-Kronig test results.

```python
def plot_mu_xps(tests: List[TestResult], mu_criterion: float, color_mu: str = "black", color_xps: str = "black", color_criterion: str = "black", legend: bool = True, fig: Optional[Figure] = None, axes: List[Axes] = [], adjust_axes: bool = True) -> Tuple[Figure, List[Axes]]:
```


_Parameters_

- `tests`: The results to plot.
- `mu_criterion`: The mu-criterion to apply.
- `color_mu`: The color of the markers and line for the mu-values.
- `color_xps`: The color of the markers and line for the pseudo chi-squared values.
- `color_criterion`: The color of the line for the mu-criterion.
- `legend`: Whether or not to add a legend.
- `fig`: The matplotlib.figure.Figure instance to use when plotting the data.
- `axes`: A list of matplotlib.axes.Axes instances to use when plotting the data.
- `adjust_axes`: Whether or not to adjust the axes (label, scale, limits, etc.).


_Returns_

```python
Tuple[Figure, List[Axes]]
```
### **deareis.api.plot.mpl.plot_nyquist**

Plot some data as a Nyquist plot (-Z" vs Z').

```python
def plot_nyquist(data: Union[DataSet, TestResult, FitResult, DRTResult], color: Any = "black", marker: str = "o", line: bool = False, label: Optional[str] = None, legend: bool = True, fig: Optional[Figure] = None, axis: Optional[Axes] = None, num_per_decade: int = 100, adjust_axes: bool = True) -> Tuple[Figure, Axes]:
```


_Parameters_

- `data`: The data to plot.
DataSet instances are plotted using markers (optionally as a line) while all other types of data are plotted as lines.
- `color`: The color of the marker or line.
- `marker`: The marker.
- `line`: Whether or not a DataSet instance should be plotted as a line instead.
- `label`: The optional label to use in the legend.
- `legend`: Whether or not to add a legend.
- `fig`: The matplotlib.figure.Figure instance to use when plotting the data.
- `axis`: The matplotlib.axes.Axes instance to use when plotting the data.
- `num_per_decade`: If the data being plotted is not a DataSet instance (e.g. a TestResult instance), then this parameter can be used to change how many points are used to draw the line (i.e. how smooth or angular the line looks).
- `adjust_axes`: Whether or not to adjust the axes (label, scale, limits, etc.).


_Returns_

```python
Tuple[Figure, Axes]
```
### **deareis.api.plot.mpl.plot_real_impedance**

Plot the real impedance of some data (Zre vs f).

```python
def plot_real_impedance(data: Union[DataSet, TestResult, FitResult, DRTResult], color: Any = "black", marker: str = "o", line: bool = False, label: Optional[str] = None, legend: bool = True, fig: Optional[Figure] = None, axis: Optional[Axes] = None, num_per_decade: int = 100, adjust_axes: bool = True) -> Tuple[Figure, Axes]:
```


_Parameters_

- `data`: The data to plot.
DataSet instances are plotted using markers (optionally as a line) while all other types of data are plotted as lines.
- `color`: The color of the marker or line.
- `marker`: The marker.
- `line`: Whether or not a DataSet instance should be plotted as a line instead.
- `label`: The optional label to use in the legend.
- `legend`: Whether or not to add a legend.
- `fig`: The matplotlib.figure.Figure instance to use when plotting the data.
- `axis`: The matplotlib.axes.Axes instance to use when plotting the data.
- `num_per_decade`: If the data being plotted is not a DataSet instance (e.g. a TestResult instance), then this parameter can be used to change how many points are used to draw the line (i.e. how smooth or angular the line looks).
- `adjust_axes`: Whether or not to adjust the axes (label, scale, limits, etc.).


_Returns_

```python
Tuple[Figure, Axes]
```
### **deareis.api.plot.mpl.plot_residual**

Plot the residuals of a result.

```python
def plot_residual(result: Union[TestResult, FitResult, DRTResult], color_real: str = "black", color_imaginary: str = "black", legend: bool = True, fig: Optional[Figure] = None, axes: List[Axes] = [], adjust_axes: bool = True) -> Tuple[Figure, List[Axes]]:
```


_Parameters_

- `result`: The result to plot.
- `color_real`: The color of the markers and line for the residuals of the real parts of the impedances.
- `color_imaginary`: The color of the markers and line for the residuals of the imaginary parts of the impedances.
- `legend`: Whether or not to add a legend.
- `fig`: The matplotlib.figure.Figure instance to use when plotting the data.
- `axes`: A list of matplotlib.axes.Axes instances to use when plotting the data.
- `adjust_axes`: Whether or not to adjust the axes (label, scale, limits, etc.).


_Returns_

```python
Tuple[Figure, List[Axes]]
```