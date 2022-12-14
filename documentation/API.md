# DearEIS - API reference (3.4.3)

DearEIS is built on top of the pyimpspec package.
See the [API reference for pyimpspec](https://vyrjana.github.io/pyimpspec/api/) for information more information about classes and functions that are provided by that package and referenced below (e.g. the `Circuit` class).
The API of DearEIS can be used for automatic some tasks (e.g., batch importing data or batch exporting plots).
However, the pyimpspec API may be a bit easier to use if you just want to have an API to use in Python scripts or Jupyter notebooks.
Primarily because the DearEIS API uses settings objects (e.g., `DRTSettings` that can be (de)serialized easily) instead of keyword arguments in the function signatures.


**NOTE!** The API makes use of multiple processes where possible to perform tasks in parallel. Functions that implement this parallelization have a `num_procs` keyword argument that can be used to override the maximum number of processes allowed. Using this keyword argument should not be necessary for most users under most circumstances.

If NumPy is linked against a multithreaded linear algebra library like OpenBLAS or MKL, then this may in some circumstances result in unusually poor performance despite heavy CPU utilization. It may be possible to remedy the issue by specifying a lower number of processes via the `num_procs` keyword argument and/or limiting the number of threads that, e.g., OpenBLAS should use by setting the appropriate environment variable (e.g., `OPENBLAS_NUM_THREADS`). Again, this should not be necessary for most users and reporting this as an issue to the pyimpspec or DearEIS repository on GitHub would be preferred.

**Table of Contents**

- [deareis](#deareis)
	- [CNLSMethod](#deareiscnlsmethod)
	- [Capacitor](#deareiscapacitor)
	- [Circuit](#deareiscircuit)
		- [get_connections](#deareiscircuitget_connections)
		- [get_element](#deareiscircuitget_element)
		- [get_elements](#deareiscircuitget_elements)
		- [get_label](#deareiscircuitget_label)
		- [get_parameters](#deareiscircuitget_parameters)
		- [impedance](#deareiscircuitimpedance)
		- [impedances](#deareiscircuitimpedances)
		- [set_label](#deareiscircuitset_label)
		- [set_parameters](#deareiscircuitset_parameters)
		- [substitute_element](#deareiscircuitsubstitute_element)
		- [to_circuitikz](#deareiscircuitto_circuitikz)
		- [to_drawing](#deareiscircuitto_drawing)
		- [to_latex](#deareiscircuitto_latex)
		- [to_stack](#deareiscircuitto_stack)
		- [to_string](#deareiscircuitto_string)
		- [to_sympy](#deareiscircuitto_sympy)
	- [CircuitBuilder](#deareiscircuitbuilder)
		- [add](#deareiscircuitbuilderadd)
		- [parallel](#deareiscircuitbuilderparallel)
		- [series](#deareiscircuitbuilderseries)
		- [to_circuit](#deareiscircuitbuilderto_circuit)
		- [to_string](#deareiscircuitbuilderto_string)
	- [Connection](#deareisconnection)
		- [contains](#deareisconnectioncontains)
		- [get_connections](#deareisconnectionget_connections)
		- [get_element](#deareisconnectionget_element)
		- [get_elements](#deareisconnectionget_elements)
		- [get_label](#deareisconnectionget_label)
		- [get_parameters](#deareisconnectionget_parameters)
		- [impedance](#deareisconnectionimpedance)
		- [impedances](#deareisconnectionimpedances)
		- [set_parameters](#deareisconnectionset_parameters)
		- [substitute_element](#deareisconnectionsubstitute_element)
		- [to_latex](#deareisconnectionto_latex)
		- [to_stack](#deareisconnectionto_stack)
		- [to_string](#deareisconnectionto_string)
		- [to_sympy](#deareisconnectionto_sympy)
	- [ConstantPhaseElement](#deareisconstantphaseelement)
	- [DRTError](#deareisdrterror)
	- [DRTMethod](#deareisdrtmethod)
	- [DRTMode](#deareisdrtmode)
	- [DRTResult](#deareisdrtresult)
		- [from_dict](#deareisdrtresultfrom_dict)
		- [get_bode_data](#deareisdrtresultget_bode_data)
		- [get_drt_credible_intervals](#deareisdrtresultget_drt_credible_intervals)
		- [get_drt_data](#deareisdrtresultget_drt_data)
		- [get_frequency](#deareisdrtresultget_frequency)
		- [get_gamma](#deareisdrtresultget_gamma)
		- [get_impedance](#deareisdrtresultget_impedance)
		- [get_label](#deareisdrtresultget_label)
		- [get_nyquist_data](#deareisdrtresultget_nyquist_data)
		- [get_peaks](#deareisdrtresultget_peaks)
		- [get_residual_data](#deareisdrtresultget_residual_data)
		- [get_score_dataframe](#deareisdrtresultget_score_dataframe)
		- [get_scores](#deareisdrtresultget_scores)
		- [get_tau](#deareisdrtresultget_tau)
		- [to_dataframe](#deareisdrtresultto_dataframe)
		- [to_dict](#deareisdrtresultto_dict)
	- [DRTSettings](#deareisdrtsettings)
		- [from_dict](#deareisdrtsettingsfrom_dict)
		- [to_dict](#deareisdrtsettingsto_dict)
	- [DataSet](#deareisdataset)
		- [average](#deareisdatasetaverage)
		- [copy](#deareisdatasetcopy)
		- [from_dict](#deareisdatasetfrom_dict)
		- [get_bode_data](#deareisdatasetget_bode_data)
		- [get_frequency](#deareisdatasetget_frequency)
		- [get_imaginary](#deareisdatasetget_imaginary)
		- [get_impedance](#deareisdatasetget_impedance)
		- [get_label](#deareisdatasetget_label)
		- [get_magnitude](#deareisdatasetget_magnitude)
		- [get_mask](#deareisdatasetget_mask)
		- [get_num_points](#deareisdatasetget_num_points)
		- [get_nyquist_data](#deareisdatasetget_nyquist_data)
		- [get_path](#deareisdatasetget_path)
		- [get_phase](#deareisdatasetget_phase)
		- [get_real](#deareisdatasetget_real)
		- [set_label](#deareisdatasetset_label)
		- [set_mask](#deareisdatasetset_mask)
		- [set_path](#deareisdatasetset_path)
		- [subtract_impedance](#deareisdatasetsubtract_impedance)
		- [to_dataframe](#deareisdatasetto_dataframe)
		- [to_dict](#deareisdatasetto_dict)
	- [DeLevieFiniteLength](#deareisdeleviefinitelength)
	- [Element](#deareiselement)
		- [get_default_fixed](#deareiselementget_default_fixed)
		- [get_default_label](#deareiselementget_default_label)
		- [get_default_lower_limits](#deareiselementget_default_lower_limits)
		- [get_default_upper_limits](#deareiselementget_default_upper_limits)
		- [get_defaults](#deareiselementget_defaults)
		- [get_description](#deareiselementget_description)
		- [get_extended_description](#deareiselementget_extended_description)
		- [get_identifier](#deareiselementget_identifier)
		- [get_label](#deareiselementget_label)
		- [get_lower_limit](#deareiselementget_lower_limit)
		- [get_parameters](#deareiselementget_parameters)
		- [get_symbol](#deareiselementget_symbol)
		- [get_upper_limit](#deareiselementget_upper_limit)
		- [impedance](#deareiselementimpedance)
		- [impedances](#deareiselementimpedances)
		- [is_fixed](#deareiselementis_fixed)
		- [reset_parameters](#deareiselementreset_parameters)
		- [set_fixed](#deareiselementset_fixed)
		- [set_label](#deareiselementset_label)
		- [set_lower_limit](#deareiselementset_lower_limit)
		- [set_parameters](#deareiselementset_parameters)
		- [set_upper_limit](#deareiselementset_upper_limit)
		- [to_latex](#deareiselementto_latex)
		- [to_string](#deareiselementto_string)
		- [to_sympy](#deareiselementto_sympy)
	- [FitResult](#deareisfitresult)
		- [from_dict](#deareisfitresultfrom_dict)
		- [get_bode_data](#deareisfitresultget_bode_data)
		- [get_frequency](#deareisfitresultget_frequency)
		- [get_impedance](#deareisfitresultget_impedance)
		- [get_label](#deareisfitresultget_label)
		- [get_nyquist_data](#deareisfitresultget_nyquist_data)
		- [get_residual_data](#deareisfitresultget_residual_data)
		- [to_dataframe](#deareisfitresultto_dataframe)
		- [to_dict](#deareisfitresultto_dict)
	- [FitSettings](#deareisfitsettings)
		- [from_dict](#deareisfitsettingsfrom_dict)
		- [to_dict](#deareisfitsettingsto_dict)
	- [FittedParameter](#deareisfittedparameter)
		- [from_dict](#deareisfittedparameterfrom_dict)
		- [get_relative_error](#deareisfittedparameterget_relative_error)
		- [to_dict](#deareisfittedparameterto_dict)
	- [FittingError](#deareisfittingerror)
	- [Gerischer](#deareisgerischer)
	- [HavriliakNegami](#deareishavriliaknegami)
	- [HavriliakNegamiAlternative](#deareishavriliaknegamialternative)
	- [Inductor](#deareisinductor)
	- [ModifiedInductor](#deareismodifiedinductor)
	- [Parallel](#deareisparallel)
	- [ParsingError](#deareisparsingerror)
	- [PlotSeries](#deareisplotseries)
		- [get_bode_data](#deareisplotseriesget_bode_data)
		- [get_color](#deareisplotseriesget_color)
		- [get_drt_credible_intervals](#deareisplotseriesget_drt_credible_intervals)
		- [get_drt_data](#deareisplotseriesget_drt_data)
		- [get_frequency](#deareisplotseriesget_frequency)
		- [get_gamma](#deareisplotseriesget_gamma)
		- [get_impedance](#deareisplotseriesget_impedance)
		- [get_label](#deareisplotseriesget_label)
		- [get_marker](#deareisplotseriesget_marker)
		- [get_nyquist_data](#deareisplotseriesget_nyquist_data)
		- [get_tau](#deareisplotseriesget_tau)
		- [has_legend](#deareisplotserieshas_legend)
		- [has_line](#deareisplotserieshas_line)
		- [has_markers](#deareisplotserieshas_markers)
	- [PlotSettings](#deareisplotsettings)
		- [add_series](#deareisplotsettingsadd_series)
		- [find_series](#deareisplotsettingsfind_series)
		- [from_dict](#deareisplotsettingsfrom_dict)
		- [get_label](#deareisplotsettingsget_label)
		- [get_series_color](#deareisplotsettingsget_series_color)
		- [get_series_label](#deareisplotsettingsget_series_label)
		- [get_series_line](#deareisplotsettingsget_series_line)
		- [get_series_marker](#deareisplotsettingsget_series_marker)
		- [get_series_theme](#deareisplotsettingsget_series_theme)
		- [get_type](#deareisplotsettingsget_type)
		- [recreate_themes](#deareisplotsettingsrecreate_themes)
		- [remove_series](#deareisplotsettingsremove_series)
		- [set_label](#deareisplotsettingsset_label)
		- [set_series_color](#deareisplotsettingsset_series_color)
		- [set_series_label](#deareisplotsettingsset_series_label)
		- [set_series_line](#deareisplotsettingsset_series_line)
		- [set_series_marker](#deareisplotsettingsset_series_marker)
		- [set_type](#deareisplotsettingsset_type)
		- [to_dict](#deareisplotsettingsto_dict)
	- [PlotType](#deareisplottype)
	- [Project](#deareisproject)
		- [add_data_set](#deareisprojectadd_data_set)
		- [add_drt](#deareisprojectadd_drt)
		- [add_fit](#deareisprojectadd_fit)
		- [add_plot](#deareisprojectadd_plot)
		- [add_simulation](#deareisprojectadd_simulation)
		- [add_test](#deareisprojectadd_test)
		- [delete_data_set](#deareisprojectdelete_data_set)
		- [delete_drt](#deareisprojectdelete_drt)
		- [delete_fit](#deareisprojectdelete_fit)
		- [delete_plot](#deareisprojectdelete_plot)
		- [delete_simulation](#deareisprojectdelete_simulation)
		- [delete_test](#deareisprojectdelete_test)
		- [edit_data_set_label](#deareisprojectedit_data_set_label)
		- [edit_data_set_path](#deareisprojectedit_data_set_path)
		- [edit_plot_label](#deareisprojectedit_plot_label)
		- [from_dict](#deareisprojectfrom_dict)
		- [from_file](#deareisprojectfrom_file)
		- [from_json](#deareisprojectfrom_json)
		- [get_all_drts](#deareisprojectget_all_drts)
		- [get_all_fits](#deareisprojectget_all_fits)
		- [get_all_tests](#deareisprojectget_all_tests)
		- [get_data_sets](#deareisprojectget_data_sets)
		- [get_drts](#deareisprojectget_drts)
		- [get_fits](#deareisprojectget_fits)
		- [get_label](#deareisprojectget_label)
		- [get_notes](#deareisprojectget_notes)
		- [get_path](#deareisprojectget_path)
		- [get_plot_series](#deareisprojectget_plot_series)
		- [get_plots](#deareisprojectget_plots)
		- [get_simulations](#deareisprojectget_simulations)
		- [get_tests](#deareisprojectget_tests)
		- [merge](#deareisprojectmerge)
		- [replace_data_set](#deareisprojectreplace_data_set)
		- [save](#deareisprojectsave)
		- [set_label](#deareisprojectset_label)
		- [set_notes](#deareisprojectset_notes)
		- [set_path](#deareisprojectset_path)
		- [to_dict](#deareisprojectto_dict)
	- [RBFShape](#deareisrbfshape)
	- [RBFType](#deareisrbftype)
	- [Resistor](#deareisresistor)
	- [Series](#deareisseries)
	- [SimulationResult](#deareissimulationresult)
		- [from_dict](#deareissimulationresultfrom_dict)
		- [get_bode_data](#deareissimulationresultget_bode_data)
		- [get_frequency](#deareissimulationresultget_frequency)
		- [get_impedance](#deareissimulationresultget_impedance)
		- [get_label](#deareissimulationresultget_label)
		- [get_nyquist_data](#deareissimulationresultget_nyquist_data)
		- [to_dataframe](#deareissimulationresultto_dataframe)
		- [to_dict](#deareissimulationresultto_dict)
	- [SimulationSettings](#deareissimulationsettings)
		- [from_dict](#deareissimulationsettingsfrom_dict)
		- [to_dict](#deareissimulationsettingsto_dict)
	- [Test](#deareistest)
	- [TestMode](#deareistestmode)
	- [TestResult](#deareistestresult)
		- [calculate_score](#deareistestresultcalculate_score)
		- [from_dict](#deareistestresultfrom_dict)
		- [get_bode_data](#deareistestresultget_bode_data)
		- [get_frequency](#deareistestresultget_frequency)
		- [get_impedance](#deareistestresultget_impedance)
		- [get_label](#deareistestresultget_label)
		- [get_nyquist_data](#deareistestresultget_nyquist_data)
		- [get_residual_data](#deareistestresultget_residual_data)
		- [to_dict](#deareistestresultto_dict)
	- [TestSettings](#deareistestsettings)
		- [from_dict](#deareistestsettingsfrom_dict)
		- [to_dict](#deareistestsettingsto_dict)
	- [UnexpectedCharacter](#deareisunexpectedcharacter)
	- [UnsupportedFileFormat](#deareisunsupportedfileformat)
	- [Warburg](#deareiswarburg)
	- [WarburgOpen](#deareiswarburgopen)
	- [WarburgShort](#deareiswarburgshort)
	- [Weight](#deareisweight)
	- [calculate_drt](#deareiscalculate_drt)
	- [fit_circuit](#deareisfit_circuit)
	- [get_elements](#deareisget_elements)
	- [parse_cdc](#deareisparse_cdc)
	- [parse_data](#deareisparse_data)
	- [perform_exploratory_tests](#deareisperform_exploratory_tests)
	- [perform_test](#deareisperform_test)
	- [simulate_spectrum](#deareissimulate_spectrum)
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



## **deareis**

### **deareis.CNLSMethod**

Iterative methods used during complex non-linear least-squares fitting:

- AUTO: try each method
- AMPGO
- BASINHOPPING
- BFGS
- BRUTE
- CG
- COBYLA
- DIFFERENTIAL_EVOLUTION
- DOGLEG
- DUAL_ANNEALING
- EMCEE
- LBFGSB
- LEASTSQ
- LEAST_SQUARES
- NELDER
- NEWTON
- POWELL
- SHGO
- SLSQP
- TNC
- TRUST_CONSTR
- TRUST_EXACT
- TRUST_KRYLOV
- TRUST_NCG

```python
class CNLSMethod(IntEnum):
```



### **deareis.Capacitor**

Capacitor

    Symbol: C

    Z = 1/(j*2*pi*f*C)

    Variables
    ---------
    C: float = 1E-6 (F)

```python
class Capacitor(Element):
	kwargs
```

_Constructor parameters_

- `kwargs`




### **deareis.Circuit**

A class that represents an equivalent circuit.

```python
class Circuit(object):
	elements: Series
	label: str = ""
```

_Constructor parameters_

- `elements`: The elements of the circuit wrapped in a Series connection.
- `label`: The label assigned to the circuit.


_Functions and methods_

#### **deareis.Circuit.get_connections**

Get the connections in this circuit.

```python
def get_connections(self, flattened: bool = True) -> List[Connection]:
```


_Parameters_

- `flattened`: Whether or not the connections should be returned as a list of all connections or as a list connections that may also contain more connections.


_Returns_
```python
List[Connection]
```

#### **deareis.Circuit.get_element**

Get the circuit element with a given integer identifier.

```python
def get_element(self, ident: int) -> Optional[Element]:
```


_Parameters_

- `ident`: The integer identifier corresponding to an element in the circuit.


_Returns_
```python
Optional[Element]
```

#### **deareis.Circuit.get_elements**

Get the elements in this circuit.

```python
def get_elements(self, flattened: bool = True) -> List[Union[Element, Connection]]:
```


_Parameters_

- `flattened`: Whether or not the elements should be returned as a list of only elements or as a list of connections containing elements.


_Returns_
```python
List[Union[Element, Connection]]
```

#### **deareis.Circuit.get_label**

Get the label assigned to this circuit.

```python
def get_label(self) -> str:
```


_Returns_
```python
str
```

#### **deareis.Circuit.get_parameters**

Get a mapping of each circuit element's integer identifier to an OrderedDict representing that element's parameters.

```python
def get_parameters(self) -> Dict[int, OrderedDict[str, float]]:
```


_Returns_
```python
Dict[int, OrderedDict[str, float]]
```

#### **deareis.Circuit.impedance**

Calculate the impedance of this circuit at a single frequency.

```python
def impedance(self, f: float) -> complex:
```


_Parameters_

- `f`: The frequency in hertz.


_Returns_
```python
complex
```

#### **deareis.Circuit.impedances**

Calculate the impedance of this circuit at multiple frequencies.

```python
def impedances(self, f: Union[list, ndarray]) -> ndarray:
```


_Parameters_

- `f`


_Returns_
```python
ndarray
```

#### **deareis.Circuit.set_label**

Set the label assigned to this circuit.

```python
def set_label(self, label: str):
```


_Parameters_

- `label`: The new label.

#### **deareis.Circuit.set_parameters**

Assign new parameters to the circuit elements.

```python
def set_parameters(self, parameters: Dict[int, Dict[str, float]]):
```


_Parameters_

- `parameters`: A mapping of circuit element integer identifiers to an OrderedDict mapping the parameter symbol to the new value.

#### **deareis.Circuit.substitute_element**

Substitute the element with the given integer identifier in the circuit with another element.

```python
def substitute_element(self, ident: int, element: Element):
```


_Parameters_

- `ident`: The integer identifier corresponding to an element in the circuit.
- `element`: The new element that will substitute the old element.

#### **deareis.Circuit.to_circuitikz**

Get the LaTeX source needed to draw a circuit diagram for this circuit using the circuitikz package.

```python
def to_circuitikz(self, node_width: float = 3.0, node_height: float = 1.5, working_label: str = "WE", counter_label: str = "CE+RE", hide_labels: bool = False) -> str:
```


_Parameters_

- `node_width`: The width of each node.
- `node_height`: The height of each node.
- `working_label`: The label assigned to the terminal representing the working and working sense electrodes.
- `counter_label`: The label assigned to the terminal representing the counter and reference electrodes.
- `hide_labels`: Whether or not to hide element and terminal labels.


_Returns_
```python
str
```

#### **deareis.Circuit.to_drawing**

Get a schemdraw.Drawing object to draw a circuit diagram using the matplotlib backend.

```python
def to_drawing(self, node_height: float = 1.5, working_label: str = "WE", counter_label: str = "CE+RE", hide_labels: bool = False) -> Drawing:
```


_Parameters_

- `node_height`: The height of each node.
- `working_label`: The label assigned to the terminal representing the working and working sense electrodes.
- `counter_label`: The label assigned to the terminal representing the counter and reference electrodes.
- `hide_labels`: Whether or not to hide element and terminal labels.


_Returns_
```python
Drawing
```

#### **deareis.Circuit.to_latex**

Get the LaTeX math expression corresponding to this circuit's impedance.

```python
def to_latex(self) -> str:
```


_Returns_
```python
str
```

#### **deareis.Circuit.to_stack**


```python
def to_stack(self) -> List[Tuple[str, Union[Element, Connection]]]:
```


_Returns_
```python
List[Tuple[str, Union[Element, Connection]]]
```

#### **deareis.Circuit.to_string**

Generate the circuit description code (CDC) that represents this circuit.

```python
def to_string(self, decimals: int = -1) -> str:
```


_Parameters_

- `decimals`: The number of decimals to include for the current element parameter values and limits.
-1 means that the CDC is generated using the basic syntax, which omits element labels, parameter values, and parameter limits.


_Returns_
```python
str
```

#### **deareis.Circuit.to_sympy**

Get the SymPy expression corresponding to this circuit's impedance.

```python
def to_sympy(self, substitute: bool = False) -> Expr:
```


_Parameters_

- `substitute`: Whether or not the variables should be substituted with the current values.


_Returns_
```python
Expr
```




### **deareis.CircuitBuilder**

A class for building circuits using context managers

```python
class CircuitBuilder(object):
	parallel: bool = False
```

_Constructor parameters_

- `parallel`: Whether or not this context/connection is a parallel connection.


_Functions and methods_

#### **deareis.CircuitBuilder.add**

Add an element to the current context (i.e., connection).

```python
def add(self, element: Element):
```


_Parameters_

- `element`: The element to add to the current series or parallel connection.

#### **deareis.CircuitBuilder.parallel**

Create a parallel connection.

```python
def parallel(self) -> CircuitBuilder:
```


_Returns_
```python
CircuitBuilder
```

#### **deareis.CircuitBuilder.series**

Create a series connection.

```python
def series(self) -> CircuitBuilder:
```


_Returns_
```python
CircuitBuilder
```

#### **deareis.CircuitBuilder.to_circuit**

Generate a circuit.

```python
def to_circuit(self) -> Circuit:
```


_Returns_
```python
Circuit
```

#### **deareis.CircuitBuilder.to_string**

Generate a circuit description code.

```python
def to_string(self, decimals: int = -1) -> str:
```


_Parameters_

- `decimals`: The number of decimals to include for the current element parameter values and limits.
-1 means that the CDC is generated using the basic syntax, which omits element labels, parameter values, and parameter limits.


_Returns_
```python
str
```




### **deareis.Connection**

```python
class Connection(object):
	elements: List[Union[Element, Connection]]
```

_Constructor parameters_

- `elements`


_Functions and methods_

#### **deareis.Connection.contains**

Check if this connection contains a specific Element or Connection instance.

```python
def contains(self, element: Union[Element, Connection], top_level: bool = False) -> bool:
```


_Parameters_

- `element`: The Element or Connection instance to check for.
- `top_level`: Whether to only check in the current Connection instance instead of also checking in any nested Connection instances.


_Returns_
```python
bool
```

#### **deareis.Connection.get_connections**

Get the connections in this circuit.

```python
def get_connections(self, flattened: bool = True) -> List[Connection]:
```


_Parameters_

- `flattened`: Whether or not the connections should be returned as a list of all connections or as a list connections that may also contain more connections.


_Returns_
```python
List[Connection]
```

#### **deareis.Connection.get_element**

Get a specific element based on its unique identifier.

```python
def get_element(self, ident: int) -> Optional[Element]:
```


_Parameters_

- `ident`: The integer identifier that should be unique in the context of the circuit.


_Returns_
```python
Optional[Element]
```

#### **deareis.Connection.get_elements**

Get the elements in this circuit.

```python
def get_elements(self, flattened: bool = True) -> List[Union[Element, Connection]]:
```


_Parameters_

- `flattened`: Whether or not the elements should be returned as a list of only elements or as a list of connections containing elements.


_Returns_
```python
List[Union[Element, Connection]]
```

#### **deareis.Connection.get_label**


```python
def get_label(self) -> str:
```


_Returns_
```python
str
```

#### **deareis.Connection.get_parameters**

Get the current element parameters of all elements nested inside this connection.
The outer key is the unique identifier assigned to an element.
The inner key is the symbol corresponding to an element parameter.

```python
def get_parameters(self) -> Dict[int, OrderedDict[str, float]]:
```


_Returns_
```python
Dict[int, OrderedDict[str, float]]
```

#### **deareis.Connection.impedance**

Calculates the impedance of the connection at a single frequency.

```python
def impedance(self, f: float) -> complex:
```


_Parameters_

- `f`: Frequency in Hz


_Returns_
```python
complex
```

#### **deareis.Connection.impedances**

Calculates the impedance of the element at multiple frequencies.

```python
def impedances(self, freq: Union[list, ndarray]) -> ndarray:
```


_Parameters_

- `freq`: Frequencies in Hz


_Returns_
```python
ndarray
```

#### **deareis.Connection.set_parameters**

Set new element parameters to some/all elements nested inside this connection.

```python
def set_parameters(self, parameters: Dict[int, Dict[str, float]]):
```


_Parameters_

- `parameters`: The outer key is the unique identifier assigned to an element.
The inner key is the symbol corresponding to an element parameter.

#### **deareis.Connection.substitute_element**


```python
def substitute_element(self, ident: int, element: Element) -> bool:
```


_Parameters_

- `ident`
- `element`


_Returns_
```python
bool
```

#### **deareis.Connection.to_latex**


```python
def to_latex(self) -> str:
```


_Returns_
```python
str
```

#### **deareis.Connection.to_stack**


```python
def to_stack(self, stack: List[Tuple[str, Union[Element, Connection]]]):
```


_Parameters_

- `stack`

#### **deareis.Connection.to_string**


```python
def to_string(self, decimals: int = -1) -> str:
```


_Parameters_

- `decimals`


_Returns_
```python
str
```

#### **deareis.Connection.to_sympy**


```python
def to_sympy(self, substitute: bool = False) -> Expr:
```


_Parameters_

- `substitute`


_Returns_
```python
Expr
```




### **deareis.ConstantPhaseElement**

Constant phase element

    Symbol: Q

    Z = 1/(Y*(j*2*pi*f)^n)

    Variables
    ---------
    Y: float = 1E-6 (F*s^(n-1))
    n: float = 0.95

```python
class ConstantPhaseElement(Element):
	kwargs
```

_Constructor parameters_

- `kwargs`




### **deareis.DRTError**

```python
class DRTError(Exception):
```



### **deareis.DRTMethod**

The method to use for calculating the DRT:

- TR_NNLS
- TR_RBF
- BHT
- M_RQ_FIT

```python
class DRTMethod(IntEnum):
```



### **deareis.DRTMode**

The parts of the impedance data to use:

- COMPLEX
- REAL
- IMAGINARY

```python
class DRTMode(IntEnum):
```



### **deareis.DRTResult**

An object representing the results of calculating the distribution of relaxation times in a  data set.

```python
class DRTResult(object):
	uuid: str
	timestamp: float
	tau: ndarray
	gamma: ndarray
	frequency: ndarray
	impedance: ndarray
	real_residual: ndarray
	imaginary_residual: ndarray
	mean_gamma: ndarray
	lower_bound: ndarray
	upper_bound: ndarray
	imaginary_gamma: ndarray
	scores: Dict[str, complex]
	chisqr: float
	lambda_value: float
	mask: Dict[int, bool]
	settings: DRTSettings
```

_Constructor parameters_

- `uuid`: The universally unique identifier assigned to this result.
- `timestamp`: The Unix time (in seconds) for when the test was performed.
- `tau`: The time constants (in seconds).
- `gamma`: The corresponding gamma(tau) values (in ohms).
These are the gamma(tau) for the real part when the BHT method has been used.
- `frequency`: The frequencies of the analyzed data set.
- `impedance`: The modeled impedances.
- `real_residual`: The residuals for the real parts of the modeled and experimental impedances.
- `imaginary_residual`: The residuals for the imaginary parts of the modeled and experimental impedances.
- `mean_gamma`: The mean values for gamma(tau).
Only non-empty when the TR-RBF method has been used and the Bayesian credible intervals have been calculated.
- `lower_bound`: The lower bound for the gamma(tau) values.
Only non-empty when the TR-RBF method has been used and the Bayesian credible intervals have been calculated.
- `upper_bound`: The upper bound for the gamma(tau) values.
Only non-empty when the TR-RBF method has been used and the Bayesian credible intervals have been calculated.
- `imaginary_gamma`: These are the gamma(tau) for the imaginary part when the BHT method has been used.
Only non-empty when the BHT method has been used.
- `scores`: The scores calculated for the analyzed data set.
Only non-empty when the BHT method has been used.
- `chisqr`: The chi-square goodness of fit value for the modeled impedance.
- `lambda_value`: The regularization parameter used as part of the Tikhonov regularization.
Only valid (i.e., positive) when the TR-NNLS or TR-RBF methods have been used.
- `mask`: The mask that was applied to the analyzed data set.
- `settings`: The settings used to perform this analysis.


_Functions and methods_

#### **deareis.DRTResult.from_dict**

Create an instance from a dictionary.

```python
def from_dict(dictionary: dict) -> DRTResult:
```


_Parameters_

- `dictionary`


_Returns_
```python
DRTResult
```

#### **deareis.DRTResult.get_bode_data**

Get the data necessary to plot this DataSet as a Bode plot: the frequencies, the absolute magnitudes of the impedances, and the negative phase angles/shifts of the impedances in degrees.

```python
def get_bode_data(self) -> Tuple[ndarray, ndarray, ndarray]:
```


_Returns_
```python
Tuple[ndarray, ndarray, ndarray]
```

#### **deareis.DRTResult.get_drt_credible_intervals**

Get the data necessary to plot the Bayesian credible intervals for this DRTResult: the time constants, the mean gamma values, the lower bound gamma values, and the upper bound gamma values.

```python
def get_drt_credible_intervals(self) -> Tuple[ndarray, ndarray, ndarray, ndarray]:
```


_Returns_
```python
Tuple[ndarray, ndarray, ndarray, ndarray]
```

#### **deareis.DRTResult.get_drt_data**

Get the data necessary to plot this DRTResult as a DRT plot: the time constants and the corresponding gamma values.

```python
def get_drt_data(self, imaginary: bool = False) -> Tuple[ndarray, ndarray]:
```


_Parameters_

- `imaginary`: Get the imaginary gamma (non-empty only when using the BHT method).


_Returns_
```python
Tuple[ndarray, ndarray]
```

#### **deareis.DRTResult.get_frequency**

Get the frequencies (in hertz) of the data set.

```python
def get_frequency(self) -> ndarray:
```


_Returns_
```python
ndarray
```

#### **deareis.DRTResult.get_gamma**

Get the gamma values.

```python
def get_gamma(self, imaginary: bool = False) -> ndarray:
```


_Parameters_

- `imaginary`: Get the imaginary gamma (non-empty only when using the BHT method).


_Returns_
```python
ndarray
```

#### **deareis.DRTResult.get_impedance**

Get the complex impedance of the model.

```python
def get_impedance(self) -> ndarray:
```


_Returns_
```python
ndarray
```

#### **deareis.DRTResult.get_label**

Generate a label for the result.

```python
def get_label(self) -> str:
```


_Returns_
```python
str
```

#### **deareis.DRTResult.get_nyquist_data**

Get the data necessary to plot this DataSet as a Nyquist plot: the real and the negative imaginary parts of the impedances.

```python
def get_nyquist_data(self) -> Tuple[ndarray, ndarray]:
```


_Returns_
```python
Tuple[ndarray, ndarray]
```

#### **deareis.DRTResult.get_peaks**

Get the time constants (in seconds) and gamma (in ohms) of peaks with magnitudes greater than the threshold.
The threshold and the magnitudes are all relative to the magnitude of the highest peak.

```python
def get_peaks(self, threshold: float = 0.0, imaginary: bool = False) -> Tuple[ndarray, ndarray]:
```


_Parameters_

- `threshold`: The threshold for the relative magnitude (0.0 to 1.0).
- `imaginary`: Use the imaginary gamma (non-empty only when using the BHT method).


_Returns_
```python
Tuple[ndarray, ndarray]
```

#### **deareis.DRTResult.get_residual_data**

Get the data necessary to plot the relative residuals for this DRTResult: the frequencies, the relative residuals for the real parts of the impedances in percents, and the relative residuals for the imaginary parts of the impedances in percents.

```python
def get_residual_data(self) -> Tuple[ndarray, ndarray, ndarray]:
```


_Returns_
```python
Tuple[ndarray, ndarray, ndarray]
```

#### **deareis.DRTResult.get_score_dataframe**

Get the scores (BHT) method for the data set as a pandas.DataFrame object that can be used to generate, e.g., a Markdown table.

```python
def get_score_dataframe(self, latex_labels: bool = False) -> Optional[DataFrame]:
```


_Parameters_

- `latex_labels`: Whether or not to use LaTeX macros in the labels.


_Returns_
```python
Optional[DataFrame]
```

#### **deareis.DRTResult.get_scores**

Get the scores (BHT method) for the data set.
The scores are represented as complex values where the real and imaginary parts have magnitudes ranging from 0.0 to 1.0.
A consistent impedance spectrum should score high.

```python
def get_scores(self) -> Dict[str, complex]:
```


_Returns_
```python
Dict[str, complex]
```

#### **deareis.DRTResult.get_tau**

Get the time constants.

```python
def get_tau(self) -> ndarray:
```


_Returns_
```python
ndarray
```

#### **deareis.DRTResult.to_dataframe**

Get the peaks as a pandas.DataFrame object that can be used to generate, e.g., a Markdown table.

```python
def to_dataframe(self, threshold: float = 0.0, imaginary: bool = False, latex_labels: bool = False, include_frequency: bool = False) -> DataFrame:
```


_Parameters_

- `threshold`: The threshold for the peaks (0.0 to 1.0 relative to the highest peak).
- `imaginary`: Use the imaginary gamma (non-empty only when using the BHT method).
- `latex_labels`: Whether or not to use LaTeX macros in the labels.
- `include_frequency`: Whether or not to also include a column with the frequencies corresponding to the time constants.


_Returns_
```python
DataFrame
```

#### **deareis.DRTResult.to_dict**

Return a dictionary that can be used to recreate an instance.

```python
def to_dict(self) -> dict:
```


_Returns_
```python
dict
```




### **deareis.DRTSettings**

The settings to use when performing a DRT analysis.

```python
class DRTSettings(object):
	method: DRTMethod
	mode: DRTMode
	lambda_value: float
	rbf_type: RBFType
	derivative_order: int
	rbf_shape: RBFShape
	shape_coeff: float
	inductance: bool
	credible_intervals: bool
	num_samples: int
	num_attempts: int
	maximum_symmetry: float
	circuit: Optional[Circuit]
	W: float
	num_per_decade: int
```

_Constructor parameters_

- `method`: The method to use to perform the analysis.
- `mode`: The mode or type of data  (i.e., complex, real, or imaginary) to use.
TR-NNLS and TR-RBF methods only.
- `lambda_value`: The Tikhonov regularization parameter to use.
TR-NNLS and TR-RBF methods only.
- `rbf_type`: The radial basis function to use for discretization.
BHT and TR-RBF methods only.
- `derivative_order`: The derivative order to use when calculating the penalty in the Tikhonov regularization.
BHT and TR-RBF methods only.
- `rbf_shape`: The shape to use with the radial basis function discretization.
BHT and TR-RBF methods only.
- `shape_coeff`: The shape coefficient.
BHT and TR-RBF methods only.
- `inductance`: Whether or not to include an inductive term in the calculations.
TR-RBF methods only.
- `credible_intervals`: Whether or not to calculate Bayesian credible intervals.
TR-RBF methods only.
- `num_samples`: The number of samples to use when calculating:
    - the Bayesian credible intervals (TR-RBF method)
    - the Jensen-Shannon distance (BHT method)
- `num_attempts`: The number of attempts to make to find a solution.
BHT method only.
- `maximum_symmetry`: The maximum vertical peak-to-peak symmetry allowed.
Used to discard results with strong oscillations.
Smaller values provide stricter conditions.
BHT and TR-RBF methods only.
- `circuit`: A circuit that contains one or more "(RQ)" or "(RC)" elements connected in series.
An optional series resistance may also be included.
For example, a circuit with a CDC representation of "R(RQ)(RQ)(RC)" would be a valid circuit.
It is highly recommended that the provided circuit has already been fitted.
However, if all of the various parameters of the provided circuit are at their default values, then an attempt will be made to fit the circuit to the data.
m(RQ)fit method only.
- `W`: The width of the Gaussian curve that is used to approximate the DRT of an "(RC)" element.
m(RQ)fit method only.
- `num_per_decade`: The number of points per decade to use when calculating a DRT.
m(RQ)fit method only.


_Functions and methods_

#### **deareis.DRTSettings.from_dict**


```python
def from_dict(dictionary: dict) -> DRTSettings:
```


_Parameters_

- `dictionary`


_Returns_
```python
DRTSettings
```

#### **deareis.DRTSettings.to_dict**


```python
def to_dict(self) -> dict:
```


_Returns_
```python
dict
```




### **deareis.DataSet**

Extends `pyimpspec.DataSet` to implement data minimization when writing to disk and to recreate the data when loading from disk.
Equality checks between DataSet instances is also modified.

```python
class DataSet(DataSet):
	frequency: ndarray
	impedance: ndarray
	mask: Dict[int, bool] = {}
	path: str = ""
	label: str = ""
	uuid: str = ""
```

_Constructor parameters_

- `frequency`: A 1-dimensional array of frequencies in hertz.
- `impedance`: A 1-dimensional array of complex impedances in ohms.
- `mask`: A mapping of integer indices to boolean values where a value of True means that the data point is to be omitted.
- `path`: The path to the file that has been parsed to generate this DataSet instance.
- `label`: The label assigned to this DataSet instance.
- `uuid`: The universivally unique identifier assigned to this DataSet instance.
If empty, then one will be automatically assigned.


_Functions and methods_

#### **deareis.DataSet.average**

Create a DataSet by averaging the impedances of multiple DataSet instances.

```python
def average(data_sets: List[DataSet], label: str = "Average") -> DataSet:
```


_Parameters_

- `data_sets`: The DataSet instances to average.
- `label`: The label that the new DataSet should have.


_Returns_
```python
DataSet
```

#### **deareis.DataSet.copy**

Create a copy of an existing DataSet.

```python
def copy(data: DataSet, label: Optional[str] = None) -> DataSet:
```


_Parameters_

- `data`: The existing DataSet to make a copy of.
- `label`: The label that the copy should have.


_Returns_
```python
DataSet
```

#### **deareis.DataSet.from_dict**

Return a DataSet instance that has been created based off of a dictionary.

```python
def from_dict(dictionary: dict) -> DataSet:
```


_Parameters_

- `dictionary`: Create an instance from a dictionary.


_Returns_
```python
DataSet
```

#### **deareis.DataSet.get_bode_data**

Get the data necessary to plot this DataSet as a Bode plot: the frequencies, the absolute magnitudes of the impedances, and the negative phase angles/shifts of the impedances in degrees.

```python
def get_bode_data(self, masked: Optional[bool] = False) -> Tuple[ndarray, ndarray, ndarray]:
```


_Parameters_

- `masked`: None means that all impedances are returned.
True means that only impedances that are to be omitted are returned.
False means that only impedances that are to be included are returned.


_Returns_
```python
Tuple[ndarray, ndarray, ndarray]
```

#### **deareis.DataSet.get_frequency**

Get the frequencies in this DataSet.

```python
def get_frequency(self, masked: Optional[bool] = False) -> ndarray:
```


_Parameters_

- `masked`: None means that all frequencies are returned.
True means that only frequencies that are to be omitted are returned.
False means that only frequencies that are to be included are returned.


_Returns_
```python
ndarray
```

#### **deareis.DataSet.get_imaginary**

Get the imaginary parts of the impedances in this DataSet.

```python
def get_imaginary(self, masked: Optional[bool] = False) -> ndarray:
```


_Parameters_

- `masked`: None means that all impedances are returned.
True means that only impedances that are to be omitted are returned.
False means that only impedances that are to be included are returned.


_Returns_
```python
ndarray
```

#### **deareis.DataSet.get_impedance**

Get the complex impedances in this DataSet.

```python
def get_impedance(self, masked: Optional[bool] = False) -> ndarray:
```


_Parameters_

- `masked`: None means that all impedances are returned.
True means that only impedances that are to be omitted are returned.
False means that only impedances that are to be included are returned.


_Returns_
```python
ndarray
```

#### **deareis.DataSet.get_label**

Get the label assigned to this DataSet.

```python
def get_label(self) -> str:
```


_Returns_
```python
str
```

#### **deareis.DataSet.get_magnitude**

Get the absolute magnitudes of the impedances in this DataSet.

```python
def get_magnitude(self, masked: Optional[bool] = False) -> ndarray:
```


_Parameters_

- `masked`: None means that all impedances are returned.
True means that only impedances that are to be omitted are returned.
False means that only impedances that are to be included are returned.


_Returns_
```python
ndarray
```

#### **deareis.DataSet.get_mask**

Get the mask for this DataSet.
The keys are zero-based indices and the values are booleans.
True means that the data point is to be omitted and False means that the data point is to be included.

```python
def get_mask(self) -> Dict[int, bool]:
```


_Returns_
```python
Dict[int, bool]
```

#### **deareis.DataSet.get_num_points**

Get the number of data points in this DataSet

```python
def get_num_points(self, masked: Optional[bool] = False) -> int:
```


_Parameters_

- `masked`: None means that all impedances are returned.
True means that only impedances that are to be omitted are returned.
False means that only impedances that are to be included are returned.


_Returns_
```python
int
```

#### **deareis.DataSet.get_nyquist_data**

Get the data necessary to plot this DataSet as a Nyquist plot: the real and the negative imaginary parts of the impedances.

```python
def get_nyquist_data(self, masked: Optional[bool] = False) -> Tuple[ndarray, ndarray]:
```


_Parameters_

- `masked`: None means that all impedances are returned.
True means that only impedances that are to be omitted are returned.
False means that only impedances that are to be included are returned.


_Returns_
```python
Tuple[ndarray, ndarray]
```

#### **deareis.DataSet.get_path**

Get the path to the file that was parsed to generate this DataSet.

```python
def get_path(self) -> str:
```


_Returns_
```python
str
```

#### **deareis.DataSet.get_phase**

Get the phase angles/shifts of the impedances in this DataSet in degrees.

```python
def get_phase(self, masked: Optional[bool] = False) -> ndarray:
```


_Parameters_

- `masked`: None means that all impedances are returned.
True means that only impedances that are to be omitted are returned.
False means that only impedances that are to be included are returned.


_Returns_
```python
ndarray
```

#### **deareis.DataSet.get_real**

Get the real parts of the impedances in this DataSet.

```python
def get_real(self, masked: Optional[bool] = False) -> ndarray:
```


_Parameters_

- `masked`: None means that all impedances are returned.
True means that only impedances that are to be omitted are returned.
False means that only impedances that are to be included are returned.


_Returns_
```python
ndarray
```

#### **deareis.DataSet.set_label**

Set the label assigned to this DataSet.

```python
def set_label(self, label: str):
```


_Parameters_

- `label`: The new label.

#### **deareis.DataSet.set_mask**

Set the mask for this DataSet.

```python
def set_mask(self, mask: Dict[int, bool]):
```


_Parameters_

- `mask`: The new mask.
The keys must be zero-based indices and the values must be boolean values.
True means that the data point is to be omitted and False means that the data point is to be included.

#### **deareis.DataSet.set_path**

Set the path to the file that was parsed to generate this DataSet.

```python
def set_path(self, path: str):
```


_Parameters_

- `path`: The path.

#### **deareis.DataSet.subtract_impedance**

Subtract either the same complex value from all data points or a unique complex value for each data point in this DataSet.

```python
def subtract_impedance(self, Z: Union[complex, List[complex], ndarray]):
```


_Parameters_

- `Z`: The complex value(s) to subtract from this DataSet's impedances.

#### **deareis.DataSet.to_dataframe**

Create a pandas.DataFrame instance from this DataSet.

```python
def to_dataframe(self, masked: Optional[bool] = False, frequency_label: str = "f (Hz)", real_label: Optional[str] = "Zre (ohm)", imaginary_label: Optional[str] = "Zim (ohm)", magnitude_label: Optional[str] = "|Z| (ohm)", phase_label: Optional[str] = "phase angle (deg.)", negative_imaginary: bool = False, negative_phase: bool = False) -> DataFrame:
```


_Parameters_

- `masked`: None means that all impedances are returned.
True means that only impedances that are to be omitted are returned.
False means that only impedances that are to be included are returned.
- `frequency_label`: The label assigned to the frequency data.
- `real_label`: The label assigned to the real part of the impedance data.
- `imaginary_label`: The label assigned to the imaginary part of the impedance data.
- `magnitude_label`: The label assigned to the magnitude of the impedance data.
- `phase_label`: The label assigned to the phase of the imedance data.
- `negative_imaginary`: Whether or not the sign of the imaginary part of the impedance data should be inverted.
- `negative_phase`: Whether or not the sign of the phase of the impedance data should be inverted.


_Returns_
```python
DataFrame
```

#### **deareis.DataSet.to_dict**

Return a dictionary that can be used to recreate this data set.

```python
def to_dict(self, session: bool = True) -> dict:
```


_Parameters_

- `session`: If true, then no data minimization is performed.


_Returns_
```python
dict
```




### **deareis.DeLevieFiniteLength**

de Levie pore (finite length)

    Symbol: Ls

    Z = (Ri*Rr)^(1/2)*coth(d*(Ri/Rr)^(1/2)*(1+Y*(2*pi*f*j)^n)^(1/2))/(1+Y*(2*pi*f*j)^n)^(1/2)

    Variables
    ---------
    Ri: float = 10.0 (ohm/cm)
    Rr: float = 1.0 (ohm*cm)
    Y: float = 0.01 (F*s^(n-1)/cm)
    n: float = 0.8
    d: float = 0.2 (cm)

```python
class DeLevieFiniteLength(Element):
	kwargs
```

_Constructor parameters_

- `kwargs`




### **deareis.Element**

```python
class Element(object):
	keys: List[str]
```

_Constructor parameters_

- `keys`


_Functions and methods_

#### **deareis.Element.get_default_fixed**

Get whether or not the element's parameters are fixed by default.

```python
def get_default_fixed() -> Dict[str, bool]:
```


_Returns_
```python
Dict[str, bool]
```

#### **deareis.Element.get_default_label**

Get the default label for this element.

```python
def get_default_label(self) -> str:
```


_Returns_
```python
str
```

#### **deareis.Element.get_default_lower_limits**

Get the default lower limits for the element's parameters.

```python
def get_default_lower_limits() -> Dict[str, float]:
```


_Returns_
```python
Dict[str, float]
```

#### **deareis.Element.get_default_upper_limits**

Get the default upper limits for the element's parameters.

```python
def get_default_upper_limits() -> Dict[str, float]:
```


_Returns_
```python
Dict[str, float]
```

#### **deareis.Element.get_defaults**

Get the default values for the element's parameters.

```python
def get_defaults() -> Dict[str, float]:
```


_Returns_
```python
Dict[str, float]
```

#### **deareis.Element.get_description**

Get a brief description of the element and its symbol.

```python
def get_description() -> str:
```


_Returns_
```python
str
```

#### **deareis.Element.get_extended_description**


```python
def get_extended_description() -> str:
```


_Returns_
```python
str
```

#### **deareis.Element.get_identifier**

Get the internal identifier that is unique in the context of a circuit.
Used internally when generating unique names for parameters when fitting a circuit to a
data set.

```python
def get_identifier(self) -> int:
```


_Returns_
```python
int
```

#### **deareis.Element.get_label**

Get the label assigned to a specific instance of the element.

```python
def get_label(self) -> str:
```


_Returns_
```python
str
```

#### **deareis.Element.get_lower_limit**

Get the lower limit for the value of an element parameter when fitting a circuit to a data
set.
The absence of a limit is represented by -numpy.inf.

```python
def get_lower_limit(self, key: str) -> float:
```


_Parameters_

- `key`: A key corresponding to an element parameter.


_Returns_
```python
float
```

#### **deareis.Element.get_parameters**

Get the current parameters of the element.

```python
def get_parameters(self) -> OrderedDict[str, float]:
```


_Returns_
```python
OrderedDict[str, float]
```

#### **deareis.Element.get_symbol**

Get the symbol representing the element.

```python
def get_symbol() -> str:
```


_Returns_
```python
str
```

#### **deareis.Element.get_upper_limit**

Get the upper limit for the value of an element parameter when fitting a circuit to a data
set.
The absence of a limit is represented by numpy.inf.

```python
def get_upper_limit(self, key: str) -> float:
```


_Parameters_

- `key`: A key corresponding to an element parameter.


_Returns_
```python
float
```

#### **deareis.Element.impedance**

Calculates the complex impedance of the element at a specific frequency.

```python
def impedance(self, f: float) -> complex:
```


_Parameters_

- `f`: Frequency in hertz.


_Returns_
```python
complex
```

#### **deareis.Element.impedances**

Calculates the complex impedance of the element at specific frequencies.

```python
def impedances(self, freq: Union[list, ndarray]) -> ndarray:
```


_Parameters_

- `freq`: Frequencies in hertz.


_Returns_
```python
ndarray
```

#### **deareis.Element.is_fixed**

Check if an element parameter should have a fixed value when fitting a circuit to a data
set.
True if fixed and False if not fixed.

```python
def is_fixed(self, key: str) -> bool:
```


_Parameters_

- `key`: A key corresponding to an element parameter.


_Returns_
```python
bool
```

#### **deareis.Element.reset_parameters**

Resets the value, lower limit, upper limit, and fixed state of one or more parameters.

```python
def reset_parameters(self, keys: List[str]):
```


_Parameters_

- `keys`: Names of the parameters to reset.

#### **deareis.Element.set_fixed**

Set whether or not an element parameter should have a fixed value when fitting a circuit
to a data set.

```python
def set_fixed(self, key: str, value: bool) -> Element:
```


_Parameters_

- `key`: A key corresponding to an element parameter.
- `value`: True if the value should be fixed.


_Returns_
```python
Element
```

#### **deareis.Element.set_label**

Set the label assigned to a specific instance of the element.

```python
def set_label(self, label: str) -> Element:
```


_Parameters_

- `label`: The new label.


_Returns_
```python
Element
```

#### **deareis.Element.set_lower_limit**

Set the upper limit for the value of an element parameter when fitting a circuit to a data
set.

```python
def set_lower_limit(self, key: str, value: float) -> Element:
```


_Parameters_

- `key`: A key corresponding to an element parameter.
- `value`: The new limit for the element parameter. The limit can be removed by setting the limit
to be -numpy.inf.


_Returns_
```python
Element
```

#### **deareis.Element.set_parameters**

Set new values for the parameters of the element.

```python
def set_parameters(self, parameters: Dict[str, float]):
```


_Parameters_

- `parameters`

#### **deareis.Element.set_upper_limit**

Set the upper limit for the value of an element parameter when fitting a circuit to a data
set.

```python
def set_upper_limit(self, key: str, value: float) -> Element:
```


_Parameters_

- `key`: A key corresponding to an element parameter.
- `value`: The new limit for the element parameter. The limit can be removed by setting the limit
to be numpy.inf.


_Returns_
```python
Element
```

#### **deareis.Element.to_latex**


```python
def to_latex(self) -> str:
```


_Returns_
```python
str
```

#### **deareis.Element.to_string**

Generates a string representation of the element.

```python
def to_string(self, decimals: int = -1) -> str:
```


_Parameters_

- `decimals`: The number of decimals used when formatting the current value and the limits for the element's parameters.
-1 corresponds to no values being included in the output.


_Returns_
```python
str
```

#### **deareis.Element.to_sympy**


```python
def to_sympy(self, substitute: bool = False) -> Expr:
```


_Parameters_

- `substitute`


_Returns_
```python
Expr
```




### **deareis.FitResult**

A class containing the result of a circuit fit.

```python
class FitResult(object):
	uuid: str
	timestamp: float
	circuit: Circuit
	parameters: Dict[str, Dict[str, FittedParameter]]
	frequency: ndarray
	impedance: ndarray
	real_residual: ndarray
	imaginary_residual: ndarray
	mask: Dict[int, bool]
	chisqr: float
	red_chisqr: float
	aic: float
	bic: float
	ndata: int
	nfree: int
	nfev: int
	method: CNLSMethod
	weight: Weight
	settings: FitSettings
```

_Constructor parameters_

- `uuid`: The universally unique identifier assigned to this result.
- `timestamp`: The Unix time (in seconds) for when the test was performed.
- `circuit`: The final, fitted circuit.
- `parameters`: The mapping to the mappings of the final, fitted values of the element parameters.
- `frequency`: The frequencies used to perform the fit.
- `impedance`: The complex impedances of the fitted circuit at each of the frequencies.
- `real_residual`: The residuals of the real part of the complex impedances.
- `imaginary_residual`: The residuals of the imaginary part of the complex impedances.
- `mask`: The mask that was applied to the DataSet that the circuit was fitted to.
- `chisqr`: The chi-squared value calculated for the result.
- `red_chisqr`: The reduced chi-squared value calculated for the result.
- `aic`: The calculated Akaike information criterion.
- `bic`: The calculated Bayesian information criterion.
- `ndata`: The number of data points.
- `nfree`: The degrees of freedom.
- `nfev`: The number of function evaluations.
- `method`: The iterative method that produced the result.
- `weight`: The weight function that produced the result.
- `settings`: The settings that were used to perform the fit.


_Functions and methods_

#### **deareis.FitResult.from_dict**

Create an instance from a dictionary.

```python
def from_dict(dictionary: dict) -> FitResult:
```


_Parameters_

- `dictionary`


_Returns_
```python
FitResult
```

#### **deareis.FitResult.get_bode_data**

Get the data required to plot the results as a Bode plot (\|Z\| and phi vs f).

```python
def get_bode_data(self, num_per_decade: int = -1) -> Tuple[ndarray, ndarray, ndarray]:
```


_Parameters_

- `num_per_decade`: If the value is greater than zero, then logarithmically distributed frequencies will be generated within the range of frequencies in the data set and used to calculate the impedance produced by the fitted circuit.


_Returns_
```python
Tuple[ndarray, ndarray, ndarray]
```

#### **deareis.FitResult.get_frequency**

Get an array of frequencies within the range of frequencies in the data set.

```python
def get_frequency(self, num_per_decade: int = -1) -> ndarray:
```


_Parameters_

- `num_per_decade`: If the value is greater than zero, then logarithmically distributed frequencies will be generated within the range of fitted frequencies.


_Returns_
```python
ndarray
```

#### **deareis.FitResult.get_impedance**

Get the complex impedances produced by the fitted circuit within the range of frequencies in the data set.

```python
def get_impedance(self, num_per_decade: int = -1) -> ndarray:
```


_Parameters_

- `num_per_decade`: If the value is greater than zero, then logarithmically distributed frequencies will be generated within the range of fitted frequencies and used to calculate the impedance produced by the fitted circuit.


_Returns_
```python
ndarray
```

#### **deareis.FitResult.get_label**

Generate a label for the result.

```python
def get_label(self) -> str:
```


_Returns_
```python
str
```

#### **deareis.FitResult.get_nyquist_data**

Get the data required to plot the results as a Nyquist plot (-Z" vs Z').

```python
def get_nyquist_data(self, num_per_decade: int = -1) -> Tuple[ndarray, ndarray]:
```


_Parameters_

- `num_per_decade`: If the value is greater than zero, then logarithmically distributed frequencies will be generated within the range of frequencies in the data set and used to calculate the impedance produced by the fitted circuit.


_Returns_
```python
Tuple[ndarray, ndarray]
```

#### **deareis.FitResult.get_residual_data**

Get the data required to plot the residuals (real and imaginary vs f).

```python
def get_residual_data(self) -> Tuple[ndarray, ndarray, ndarray]:
```


_Returns_
```python
Tuple[ndarray, ndarray, ndarray]
```

#### **deareis.FitResult.to_dataframe**

Get a `pandas.DataFrame` instance containing a table of fitted element parameters.

```python
def to_dataframe(self) -> DataFrame:
```


_Returns_
```python
DataFrame
```

#### **deareis.FitResult.to_dict**

Return a dictionary that can be used to recreate an instance.

```python
def to_dict(self, session: bool) -> dict:
```


_Parameters_

- `session`


_Returns_
```python
dict
```




### **deareis.FitSettings**

A class to store the settings used to perform a circuit fit.

```python
class FitSettings(object):
	cdc: str
	method: CNLSMethod
	weight: Weight
	max_nfev: int
```

_Constructor parameters_

- `cdc`: The circuit description code (CDC) for the circuit to fit.
- `method`: The iterative method to use when performing the fit.
- `weight`: The weight function to use when performing the fit.
- `max_nfev`: The maximum number of function evaluations to use when performing the fit.


_Functions and methods_

#### **deareis.FitSettings.from_dict**

Create an instance from a dictionary.

```python
def from_dict(dictionary: dict) -> FitSettings:
```


_Parameters_

- `dictionary`


_Returns_
```python
FitSettings
```

#### **deareis.FitSettings.to_dict**

Return a dictionary that can be used to recreate an instance.

```python
def to_dict(self) -> dict:
```


_Returns_
```python
dict
```




### **deareis.FittedParameter**

An object representing a fitted parameter.

```python
class FittedParameter(object):
	value: float
	stderr: Optional[float] = None
	fixed: bool = False
```

_Constructor parameters_

- `value`: The fitted value.
- `stderr`: The estimated standard error of the fitted value.
- `fixed`: Whether or not this parameter had a fixed value during the circuit fitting.


_Functions and methods_

#### **deareis.FittedParameter.from_dict**


```python
def from_dict(dictionary: dict) -> FittedParameter:
```


_Parameters_

- `dictionary`


_Returns_
```python
FittedParameter
```

#### **deareis.FittedParameter.get_relative_error**


```python
def get_relative_error(self) -> float:
```


_Returns_
```python
float
```

#### **deareis.FittedParameter.to_dict**


```python
def to_dict(self) -> dict:
```


_Returns_
```python
dict
```




### **deareis.FittingError**

```python
class FittingError(Exception):
```



### **deareis.Gerischer**

Gerischer

    Symbol: G

    Z = 1/(Y*(k+j*2*pi*f)^n)

    Variables
    ---------
    Y: float = 1.0 (S*s^n)
    k: float = 1.0 (s^-1)
    n: float = 0.5

```python
class Gerischer(Element):
	kwargs
```

_Constructor parameters_

- `kwargs`




### **deareis.HavriliakNegami**

Havriliak-Negami relaxation

    Symbol: H

    Z = (((1+(j*2*pi*f*t)^a)^b)/(j*2*pi*f*dC))

    Variables
    ---------
    dC: float = 1E-6 (F)
    t: float = 1.0 (s)
    a: float = 0.9
    b: float = 0.9

```python
class HavriliakNegami(Element):
	kwargs
```

_Constructor parameters_

- `kwargs`




### **deareis.HavriliakNegamiAlternative**

Havriliak-Negami relaxation (alternative form)

    Symbol: Ha

    Z = R / ((1 + (I*2*pi*f*t)^b)^g)

    Variables
    ---------
    R: float = 1 (ohm)
    t: float = 1.0 (s)
    b: float = 0.7
    g: float = 0.8

```python
class HavriliakNegamiAlternative(Element):
	kwargs
```

_Constructor parameters_

- `kwargs`




### **deareis.Inductor**

Inductor

    Symbol: L

    Z = j*2*pi*f*L

    Variables
    ---------
    L: float = 1E-6 (H)

```python
class Inductor(Element):
	kwargs
```

_Constructor parameters_

- `kwargs`




### **deareis.ModifiedInductor**

Modified inductor

    Symbol: La

    Z = L*(j*2*pi*f)^n

    Variables
    ---------
    L: float = 1E-6 (H*s^(n-1))
    n: float = 0.95

```python
class ModifiedInductor(Element):
	kwargs
```

_Constructor parameters_

- `kwargs`




### **deareis.Parallel**

Elements connected in parallel.

```python
class Parallel(Connection):
	elements: List[Union[Element, Connection]]
```

_Constructor parameters_

- `elements`: List of elements (and connections) that are connected in parallel.




### **deareis.ParsingError**

```python
class ParsingError(Exception):
```



### **deareis.PlotSeries**

A class that represents the data used to plot an item/series.

```python
class PlotSeries(object):
	data: Union[DataSet, TestResult, DRTResult, FitResult, SimulationResult]
	label: str
	color: Tuple[float, float, float, float]
	marker: int
	line: bool
	legend: bool
```

_Constructor parameters_

- `data`
- `label`
- `color`
- `marker`
- `line`
- `legend`


_Functions and methods_

#### **deareis.PlotSeries.get_bode_data**


```python
def get_bode_data(self, num_per_decade: int = -1) -> Tuple[ndarray, ndarray, ndarray]:
```


_Parameters_

- `num_per_decade`


_Returns_
```python
Tuple[ndarray, ndarray, ndarray]
```

#### **deareis.PlotSeries.get_color**


```python
def get_color(self) -> Tuple[float, float, float, float]:
```


_Returns_
```python
Tuple[float, float, float, float]
```

#### **deareis.PlotSeries.get_drt_credible_intervals**


```python
def get_drt_credible_intervals(self) -> Tuple[ndarray, ndarray, ndarray, ndarray]:
```


_Returns_
```python
Tuple[ndarray, ndarray, ndarray, ndarray]
```

#### **deareis.PlotSeries.get_drt_data**


```python
def get_drt_data(self, imaginary: bool = False) -> Tuple[ndarray, ndarray]:
```


_Parameters_

- `imaginary`


_Returns_
```python
Tuple[ndarray, ndarray]
```

#### **deareis.PlotSeries.get_frequency**


```python
def get_frequency(self, num_per_decade: int = -1) -> ndarray:
```


_Parameters_

- `num_per_decade`


_Returns_
```python
ndarray
```

#### **deareis.PlotSeries.get_gamma**


```python
def get_gamma(self, imaginary: bool = False) -> ndarray:
```


_Parameters_

- `imaginary`


_Returns_
```python
ndarray
```

#### **deareis.PlotSeries.get_impedance**


```python
def get_impedance(self, num_per_decade: int = -1) -> ndarray:
```


_Parameters_

- `num_per_decade`


_Returns_
```python
ndarray
```

#### **deareis.PlotSeries.get_label**


```python
def get_label(self) -> str:
```


_Returns_
```python
str
```

#### **deareis.PlotSeries.get_marker**


```python
def get_marker(self) -> int:
```


_Returns_
```python
int
```

#### **deareis.PlotSeries.get_nyquist_data**


```python
def get_nyquist_data(self, num_per_decade: int = -1) -> Tuple[ndarray, ndarray]:
```


_Parameters_

- `num_per_decade`


_Returns_
```python
Tuple[ndarray, ndarray]
```

#### **deareis.PlotSeries.get_tau**


```python
def get_tau(self) -> ndarray:
```


_Returns_
```python
ndarray
```

#### **deareis.PlotSeries.has_legend**


```python
def has_legend(self) -> bool:
```


_Returns_
```python
bool
```

#### **deareis.PlotSeries.has_line**


```python
def has_line(self) -> bool:
```


_Returns_
```python
bool
```

#### **deareis.PlotSeries.has_markers**


```python
def has_markers(self) -> bool:
```


_Returns_
```python
bool
```




### **deareis.PlotSettings**

A class representing a complex plot that can contain one or more data sets, Kramers-Kronig test results, DRT analysis results, equivalent circuit fitting results, and simulation results.

```python
class PlotSettings(object):
	plot_label: str
	plot_type: PlotType
	series_order: List[str]
	labels: Dict[str, str]
	colors: Dict[str, List[float]]
	markers: Dict[str, int]
	show_lines: Dict[str, bool]
	themes: Dict[str, int]
	uuid: str
```

_Constructor parameters_

- `plot_label`
- `plot_type`
- `series_order`
- `labels`
- `colors`
- `markers`
- `show_lines`
- `themes`
- `uuid`


_Functions and methods_

#### **deareis.PlotSettings.add_series**


```python
def add_series(self, series: Union[DataSet, TestResult, DRTResult, FitResult, SimulationResult]):
```


_Parameters_

- `series`

#### **deareis.PlotSettings.find_series**


```python
def find_series(self, uuid: str, datasets: List[DataSet], tests: Dict[str, List[TestResult]], drts: Dict[str, List[DRTResult]], fits: Dict[str, List[FitResult]], simulations: List[SimulationResult]) -> Union[DataSet, TestResult, DRTResult, FitResult, SimulationResult, NoneType]:
```


_Parameters_

- `uuid`
- `datasets`
- `tests`
- `drts`
- `fits`
- `simulations`


_Returns_
```python
Union[DataSet, TestResult, DRTResult, FitResult, SimulationResult, NoneType]
```

#### **deareis.PlotSettings.from_dict**


```python
def from_dict(dictionary: dict) -> PlotSettings:
```


_Parameters_

- `dictionary`


_Returns_
```python
PlotSettings
```

#### **deareis.PlotSettings.get_label**


```python
def get_label(self) -> str:
```


_Returns_
```python
str
```

#### **deareis.PlotSettings.get_series_color**


```python
def get_series_color(self, uuid: str) -> List[float]:
```


_Parameters_

- `uuid`


_Returns_
```python
List[float]
```

#### **deareis.PlotSettings.get_series_label**


```python
def get_series_label(self, uuid: str) -> str:
```


_Parameters_

- `uuid`


_Returns_
```python
str
```

#### **deareis.PlotSettings.get_series_line**


```python
def get_series_line(self, uuid: str) -> bool:
```


_Parameters_

- `uuid`


_Returns_
```python
bool
```

#### **deareis.PlotSettings.get_series_marker**


```python
def get_series_marker(self, uuid: str) -> int:
```


_Parameters_

- `uuid`


_Returns_
```python
int
```

#### **deareis.PlotSettings.get_series_theme**


```python
def get_series_theme(self, uuid: str) -> int:
```


_Parameters_

- `uuid`


_Returns_
```python
int
```

#### **deareis.PlotSettings.get_type**


```python
def get_type(self) -> PlotType:
```


_Returns_
```python
PlotType
```

#### **deareis.PlotSettings.recreate_themes**


```python
def recreate_themes(self):
```

#### **deareis.PlotSettings.remove_series**


```python
def remove_series(self, uuid: str):
```


_Parameters_

- `uuid`

#### **deareis.PlotSettings.set_label**


```python
def set_label(self, label: str):
```


_Parameters_

- `label`

#### **deareis.PlotSettings.set_series_color**


```python
def set_series_color(self, uuid: str, color: List[float]):
```


_Parameters_

- `uuid`
- `color`

#### **deareis.PlotSettings.set_series_label**


```python
def set_series_label(self, uuid: str, label: str):
```


_Parameters_

- `uuid`
- `label`

#### **deareis.PlotSettings.set_series_line**


```python
def set_series_line(self, uuid: str, state: bool):
```


_Parameters_

- `uuid`
- `state`

#### **deareis.PlotSettings.set_series_marker**


```python
def set_series_marker(self, uuid: str, marker: int):
```


_Parameters_

- `uuid`
- `marker`

#### **deareis.PlotSettings.set_type**


```python
def set_type(self, plot_type: PlotType):
```


_Parameters_

- `plot_type`

#### **deareis.PlotSettings.to_dict**


```python
def to_dict(self, session: bool) -> dict:
```


_Parameters_

- `session`


_Returns_
```python
dict
```




### **deareis.PlotType**

Types of plots:

- NYQUIST: -Zim vs Zre
- BODE_MAGNITUDE: \|Z\| vs f
- BODE_PHASE: phi vs f
- DRT: gamma vs tau
- IMPEDANCE_REAL: Zre vs f
- IMPEDANCE_IMAGINARY: Zim vs f

```python
class PlotType(IntEnum):
```



### **deareis.Project**

A class representing a collection of notes, data sets, test results, fit results, simulation results, and complex plots.

```python
class Project(object):
	args
	kwargs
```

_Constructor parameters_

- `args`
- `kwargs`


_Functions and methods_

#### **deareis.Project.add_data_set**

Add a data set to the project.

```python
def add_data_set(self, data: DataSet):
```


_Parameters_

- `data`: The data set to add.

#### **deareis.Project.add_drt**

Add the provided DRT analysis result to the provided data set's list of DRT analysis results.

```python
def add_drt(self, data: DataSet, drt: DRTResult):
```


_Parameters_

- `data`: The data set that was analyzed.
- `drt`: The result of the analysis.

#### **deareis.Project.add_fit**

Add the provided fit result to the provided data set.

```python
def add_fit(self, data: DataSet, fit: FitResult):
```


_Parameters_

- `data`: The data set that a circuit was fit to.
- `fit`: The result of the circuit fit.

#### **deareis.Project.add_plot**

Add the provided plot to the list of plots.

```python
def add_plot(self, plot: PlotSettings):
```


_Parameters_

- `plot`: The settings for the plot.

#### **deareis.Project.add_simulation**

Add the provided simulation result to the list of simulation results.

```python
def add_simulation(self, simulation: SimulationResult):
```


_Parameters_

- `simulation`: The result of the simulation.

#### **deareis.Project.add_test**

Add the provided Kramers-Kronig test result to the provided data set's list of Kramers-Kronig test results.

```python
def add_test(self, data: DataSet, test: TestResult):
```


_Parameters_

- `data`: The data set that was tested.
- `test`: The result of the test.

#### **deareis.Project.delete_data_set**

Delete a data set (and its associated test and fit results) from the project.

```python
def delete_data_set(self, data: DataSet):
```


_Parameters_

- `data`: The data set to remove.

#### **deareis.Project.delete_drt**

Delete the provided DRT analysis result from the provided data set's list of DRT analysis results.

```python
def delete_drt(self, data: DataSet, drt: DRTResult):
```


_Parameters_

- `data`: The data set associated with the analysis result.
- `drt`: The analysis result to delete.

#### **deareis.Project.delete_fit**

Delete the provided fit result from the provided data set's list of fit results.

```python
def delete_fit(self, data: DataSet, fit: FitResult):
```


_Parameters_

- `data`: The data set associated with the fit result.
- `fit`: The fit result to delete.

#### **deareis.Project.delete_plot**

Delete the provided plot from the list of plots.

```python
def delete_plot(self, plot: PlotSettings):
```


_Parameters_

- `plot`: The plot settings to delete.

#### **deareis.Project.delete_simulation**

Remove the provided simulation result from the list of simulation results.

```python
def delete_simulation(self, simulation: SimulationResult):
```


_Parameters_

- `simulation`: The simulation result to delete.

#### **deareis.Project.delete_test**

Delete the provided Kramers-Kronig test result from the provided data set's list of Kramers-Kronig test results.

```python
def delete_test(self, data: DataSet, test: TestResult):
```


_Parameters_

- `data`: The data set associated with the test result.
- `test`: The test result to delete.

#### **deareis.Project.edit_data_set_label**

Edit the label of a data set in the project.
Ensures that each data set has a unique label.

```python
def edit_data_set_label(self, data: DataSet, label: str):
```


_Parameters_

- `data`: The data set to rename.
- `label`: The new label.

#### **deareis.Project.edit_data_set_path**

Edit the path of a data set in the project.

```python
def edit_data_set_path(self, data: DataSet, path: str):
```


_Parameters_

- `data`: The data set to edit.
- `path`: The new path.

#### **deareis.Project.edit_plot_label**

Edit the label of a plot in the project.
Ensures that each plot has a unique label.

```python
def edit_plot_label(self, plot: PlotSettings, label: str):
```


_Parameters_

- `plot`: The plot settings to edit.
- `label`: The new label.

#### **deareis.Project.from_dict**

Create an instance from a dictionary.

```python
def from_dict(state: dict) -> Project:
```


_Parameters_

- `state`: A dictionary-based representation of a project state.


_Returns_
```python
Project
```

#### **deareis.Project.from_file**

Create an instance by parsing a file containing a Project that has been serialized using JSON.

```python
def from_file(path: str) -> Project:
```


_Parameters_

- `path`: The path to a file containing a serialized project state.


_Returns_
```python
Project
```

#### **deareis.Project.from_json**

Create an instance by parsing a JSON string.

```python
def from_json(json: str) -> Project:
```


_Parameters_

- `json`: A JSON representation of a project state.


_Returns_
```python
Project
```

#### **deareis.Project.get_all_drts**

Get a mapping of data set UUIDs to the corresponding DRT analysis results of those data sets.

```python
def get_all_drts(self) -> Dict[str, List[DRTResult]]:
```


_Returns_
```python
Dict[str, List[DRTResult]]
```

#### **deareis.Project.get_all_fits**

Get a mapping of data set UUIDs to the corresponding list of fit results of those data sets.

```python
def get_all_fits(self) -> Dict[str, List[FitResult]]:
```


_Returns_
```python
Dict[str, List[FitResult]]
```

#### **deareis.Project.get_all_tests**

Get a mapping of data set UUIDs to the corresponding Kramers-Kronig test results of those data sets.

```python
def get_all_tests(self) -> Dict[str, List[TestResult]]:
```


_Returns_
```python
Dict[str, List[TestResult]]
```

#### **deareis.Project.get_data_sets**

Get the project's data sets.

```python
def get_data_sets(self) -> List[DataSet]:
```


_Returns_
```python
List[DataSet]
```

#### **deareis.Project.get_drts**

Get the DRT analysis results associated with a specific data set.

```python
def get_drts(self, data: DataSet) -> List[DRTResult]:
```


_Parameters_

- `data`: The data set whose analyses to get.


_Returns_
```python
List[DRTResult]
```

#### **deareis.Project.get_fits**

Get fit results associated with a specific data set.

```python
def get_fits(self, data: DataSet) -> List[FitResult]:
```


_Parameters_

- `data`: The data set whose fits to get.


_Returns_
```python
List[FitResult]
```

#### **deareis.Project.get_label**

Get the project's label.

```python
def get_label(self) -> str:
```


_Returns_
```python
str
```

#### **deareis.Project.get_notes**

Get the project's notes.

```python
def get_notes(self) -> str:
```


_Returns_
```python
str
```

#### **deareis.Project.get_path**

Get the project's currrent path.
An empty string signifies that no path has been set previously.

```python
def get_path(self) -> str:
```


_Returns_
```python
str
```

#### **deareis.Project.get_plot_series**

Get PlotSeries instances of each of the plotted items/series in a specific plot.

```python
def get_plot_series(self, plot: PlotSettings) -> List[PlotSeries]:
```


_Parameters_

- `plot`: The plot whose items/series to get.


_Returns_
```python
List[PlotSeries]
```

#### **deareis.Project.get_plots**

Get all of the plots.

```python
def get_plots(self) -> List[PlotSettings]:
```


_Returns_
```python
List[PlotSettings]
```

#### **deareis.Project.get_simulations**

Get all of the simulation results.

```python
def get_simulations(self) -> List[SimulationResult]:
```


_Returns_
```python
List[SimulationResult]
```

#### **deareis.Project.get_tests**

Get the Kramers-Kronig test results associated with a specific data set.

```python
def get_tests(self, data: DataSet) -> List[TestResult]:
```


_Parameters_

- `data`: The data set whose tests to get.


_Returns_
```python
List[TestResult]
```

#### **deareis.Project.merge**

Create an instance by merging multiple Project instances.
All UUIDs are replaced to avoid collisions.
The labels of some objects are also replaced to avoid collisions.

```python
def merge(projects: List[Project]) -> Project:
```


_Parameters_

- `projects`


_Returns_
```python
Project
```

#### **deareis.Project.replace_data_set**

Replace a data set in the project with another one.

```python
def replace_data_set(self, old: DataSet, new: DataSet):
```


_Parameters_

- `old`: The data set to be replaced.
- `new`: The replacement data set.

#### **deareis.Project.save**

Serialize the project as a file containing a JSON string.

```python
def save(self, path: Optional[str] = None):
```


_Parameters_

- `path`: The path to write the project state to.
If this is None, then the most recently defined path is used.

#### **deareis.Project.set_label**

Set the project's label.

```python
def set_label(self, label: str):
```


_Parameters_

- `label`: The new label.

#### **deareis.Project.set_notes**

Set the project's notes.

```python
def set_notes(self, notes: str):
```


_Parameters_

- `notes`: The project notes.

#### **deareis.Project.set_path**

Set the path to use when calling the `save` method without arguments.

```python
def set_path(self, path: str):
```


_Parameters_

- `path`: The path where the project's state should be saved.

#### **deareis.Project.to_dict**

Return a dictionary containing the project state.
The dictionary can be used to recreate a project or to restore a project state.

```python
def to_dict(self, session: bool) -> dict:
```


_Parameters_

- `session`: If true, then data minimization is not performed.


_Returns_
```python
dict
```




### **deareis.RBFShape**

The shape to use with the radial basis function discretization:

- FWHM
- FACTOR

```python
class RBFShape(IntEnum):
```



### **deareis.RBFType**

The radial basis function to use for discretization (or piecewise linear discretization):

- C0_MATERN
- C2_MATERN
- C4_MATERN
- C6_MATERN
- CAUCHY
- GAUSSIAN
- INVERSE_QUADRATIC
- INVERSE_QUADRIC
- PIECEWISE_LINEAR

```python
class RBFType(IntEnum):
```



### **deareis.Resistor**

Resistor

    Symbol: R

    Z = R

    Variables
    ---------
    R: float = 1E+3 (ohm)

```python
class Resistor(Element):
	kwargs
```

_Constructor parameters_

- `kwargs`




### **deareis.Series**

Elements connected in series.

```python
class Series(Connection):
	elements: List[Union[Element, Connection]]
```

_Constructor parameters_

- `elements`: List of elements (and connections) that are connected in series.




### **deareis.SimulationResult**

A class containing the result of a simulation.

```python
class SimulationResult(object):
	uuid: str
	timestamp: float
	circuit: Circuit
	settings: SimulationSettings
```

_Constructor parameters_

- `uuid`: The universally unique identifier assigned to this result.
- `timestamp`: The Unix time (in seconds) for when the simulation was performed.
- `circuit`: The simulated circuit.
- `settings`: The settings that were used to perform the simulation.


_Functions and methods_

#### **deareis.SimulationResult.from_dict**

Create an instance from a dictionary.

```python
def from_dict(dictionary: dict) -> SimulationResult:
```


_Parameters_

- `dictionary`


_Returns_
```python
SimulationResult
```

#### **deareis.SimulationResult.get_bode_data**

Get the data required to plot the results as a Bode plot (\|Z\| and phi vs f).

```python
def get_bode_data(self, num_per_decade: int = -1) -> Tuple[ndarray, ndarray, ndarray]:
```


_Parameters_

- `num_per_decade`: If the value is greater than zero, then logarithmically distributed frequencies will be generated within the range of frequencies and used to calculate the impedance produced by the fitted circuit.


_Returns_
```python
Tuple[ndarray, ndarray, ndarray]
```

#### **deareis.SimulationResult.get_frequency**

Get an array of frequencies within the range of simulated frequencies.

```python
def get_frequency(self, num_per_decade: int = -1) -> ndarray:
```


_Parameters_

- `num_per_decade`: If the value is greater than zero, then logarithmically distributed frequencies will be generated within the range of frequencies defined by the minimum and maximum frequencies used to generate the original simulation result.


_Returns_
```python
ndarray
```

#### **deareis.SimulationResult.get_impedance**

Get the complex impedances produced by the simulated circuit within the range of frequencies used to generate the original simulation result.

```python
def get_impedance(self, num_per_decade: int = -1) -> ndarray:
```


_Parameters_

- `num_per_decade`: If the value is greater than zero, then logarithmically distributed frequencies will be generated within the range of simulated frequencies and used to calculate the impedance produced by the simulated circuit.


_Returns_
```python
ndarray
```

#### **deareis.SimulationResult.get_label**

Generate a label for the result.

```python
def get_label(self) -> str:
```


_Returns_
```python
str
```

#### **deareis.SimulationResult.get_nyquist_data**

Get the data required to plot the results as a Nyquist plot (-Z" vs Z').

```python
def get_nyquist_data(self, num_per_decade: int = -1) -> Tuple[ndarray, ndarray]:
```


_Parameters_

- `num_per_decade`: If the value is greater than zero, then logarithmically distributed frequencies will be generated within the range of frequencies and used to calculate the impedance produced by the simulated circuit.


_Returns_
```python
Tuple[ndarray, ndarray]
```

#### **deareis.SimulationResult.to_dataframe**

Get a `pandas.DataFrame` instance containing a table of element parameters.

```python
def to_dataframe(self) -> DataFrame:
```


_Returns_
```python
DataFrame
```

#### **deareis.SimulationResult.to_dict**

Return a dictionary that can be used to recreate an instance.

```python
def to_dict(self) -> dict:
```


_Returns_
```python
dict
```




### **deareis.SimulationSettings**

A class to store the settings used to perform a simulation.

```python
class SimulationSettings(object):
	cdc: str
	min_frequency: float
	max_frequency: float
	num_per_decade: int
```

_Constructor parameters_

- `cdc`: The circuit description code (CDC) for the circuit to simulate.
- `min_frequency`: The minimum frequency (in hertz) to simulate.
- `max_frequency`: The maximum frequency (in hertz) to simulate.
- `num_per_decade`: The number of frequencies per decade to simulate.
The frequencies are distributed logarithmically within the inclusive boundaries defined by `min_frequency` and `max_frequency`.


_Functions and methods_

#### **deareis.SimulationSettings.from_dict**

Create an instance from a dictionary.

```python
def from_dict(dictionary: dict) -> SimulationSettings:
```


_Parameters_

- `dictionary`


_Returns_
```python
SimulationSettings
```

#### **deareis.SimulationSettings.to_dict**

Return a dictionary that can be used to recreate an instance.

```python
def to_dict(self) -> dict:
```


_Returns_
```python
dict
```




### **deareis.Test**

Types of Kramers-Kronig tests:

- CNLS: complex non-linear least-squares fit of circuit (fig. 1, Boukamp, 1995) with a distribution of fixed time constants
- COMPLEX: eqs. 11 and 12, Boukamp, 1995
- IMAGINARY: eqs. 4, 6, and 7, Boukamp, 1995
- REAL: eqs. 5, 8, 9, and 10, Boukamp, 1995

```python
class Test(IntEnum):
```



### **deareis.TestMode**

Types of modes that determine how the number of Voigt elements (capacitor connected in parallel with resistor) is chosen:

- AUTO: follow procedure described by Schönleber, Klotz, and Ivers-Tiffée (2014)
- EXPLORATORY: same procedure as AUTO but present intermediate results to user and apply additional weighting to the initial suggestion
- MANUAL: manually choose the number

```python
class TestMode(IntEnum):
```



### **deareis.TestResult**

A class containing the result of a Kramers-Kronig test.

```python
class TestResult(object):
	uuid: str
	timestamp: float
	circuit: Circuit
	num_RC: int
	mu: float
	pseudo_chisqr: float
	frequency: ndarray
	impedance: ndarray
	real_residual: ndarray
	imaginary_residual: ndarray
	mask: Dict[int, bool]
	settings: TestSettings
```

_Constructor parameters_

- `uuid`: The universally unique identifier assigned to this result.
- `timestamp`: The Unix time (in seconds) for when the test was performed.
- `circuit`: The final, fitted circuit.
- `num_RC`: The final number of parallel RC circuits connected in series.
- `mu`: The mu-value that was calculated for the result.
- `pseudo_chisqr`: The pseudo chi-squared value calculated according to eq. N in Boukamp (1995).
- `frequency`: The frequencies used to perform the test.
- `impedance`: The complex impedances of the fitted circuit at each of the frequencies.
- `real_residual`: The residuals of the real part of the complex impedances.
- `imaginary_residual`: The residuals of the imaginary part of the complex impedances.
- `mask`: The mask that was applied to the DataSet that was tested.
- `settings`: The settings that were used to perform the test.


_Functions and methods_

#### **deareis.TestResult.calculate_score**

Calculate a score based on the provided mu-criterion and the statistics of the result.
A result with a mu-value greater than or equal to the mu-criterion will get a score of -numpy.inf.

```python
def calculate_score(self, mu_criterion: float) -> float:
```


_Parameters_

- `mu_criterion`: The mu-criterion to apply.
See perform_test for details.


_Returns_
```python
float
```

#### **deareis.TestResult.from_dict**

Create an instance from a dictionary.

```python
def from_dict(dictionary: dict) -> TestResult:
```


_Parameters_

- `dictionary`


_Returns_
```python
TestResult
```

#### **deareis.TestResult.get_bode_data**

Get the data required to plot the results as a Bode plot (\|Z\| and phi vs f).

```python
def get_bode_data(self, num_per_decade: int = -1) -> Tuple[ndarray, ndarray, ndarray]:
```


_Parameters_

- `num_per_decade`: If the value is greater than zero, then logarithmically distributed frequencies will be generated within the range of tested frequencies and used to calculate the impedance produced by the fitted circuit.


_Returns_
```python
Tuple[ndarray, ndarray, ndarray]
```

#### **deareis.TestResult.get_frequency**

Get an array of frequencies within the range of tested frequencies.

```python
def get_frequency(self, num_per_decade: int = -1) -> ndarray:
```


_Parameters_

- `num_per_decade`: If the value is greater than zero, then logarithmically distributed frequencies will be generated within the range of tested frequencies.


_Returns_
```python
ndarray
```

#### **deareis.TestResult.get_impedance**

Get the complex impedances produced by the fitted circuit within the range of tested frequencies.

```python
def get_impedance(self, num_per_decade: int = -1) -> ndarray:
```


_Parameters_

- `num_per_decade`: If the value is greater than zero, then logarithmically distributed frequencies will be generated within the range of tested frequencies and used to calculate the impedance produced by the fitted circuit.


_Returns_
```python
ndarray
```

#### **deareis.TestResult.get_label**

Generate a label for the result.

```python
def get_label(self) -> str:
```


_Returns_
```python
str
```

#### **deareis.TestResult.get_nyquist_data**

Get the data required to plot the results as a Nyquist plot (-Z" vs Z').

```python
def get_nyquist_data(self, num_per_decade: int = -1) -> Tuple[ndarray, ndarray]:
```


_Parameters_

- `num_per_decade`: If the value is greater than zero, then logarithmically distributed frequencies will be generated within the range of tested frequencies and used to calculate the impedance produced by the fitted circuit.


_Returns_
```python
Tuple[ndarray, ndarray]
```

#### **deareis.TestResult.get_residual_data**

Get the data required to plot the residuals (real and imaginary vs f).

```python
def get_residual_data(self) -> Tuple[ndarray, ndarray, ndarray]:
```


_Returns_
```python
Tuple[ndarray, ndarray, ndarray]
```

#### **deareis.TestResult.to_dict**

Return a dictionary that can be used to recreate an instance.

```python
def to_dict(self, session: bool) -> dict:
```


_Parameters_

- `session`


_Returns_
```python
dict
```




### **deareis.TestSettings**

A class to store the settings used to perform a Kramers-Kronig test.

```python
class TestSettings(object):
	test: Test
	mode: TestMode
	num_RC: int
	mu_criterion: float
	add_capacitance: bool
	add_inductance: bool
	method: CNLSMethod
	max_nfev: int
```

_Constructor parameters_

- `test`: The type of test to perform: complex, real, imaginary, or CNLS.
See pyimpspec and its documentation for details about the different types of tests.
- `mode`: How to perform the test: automatic, exploratory, or manual.
The automatic mode uses the procedure described by Schönleber et al. (2014) to determine a suitable number of parallel RC circuits connected in series.
The exploratory mode is similar to the automatic mode except the user is allowed to choose which of the results to accept and the initial suggestion has additional weighting applied to it in an effort to reduce false negatives that would lead to the conclusion that the data is invalid.
The manual mode requires the user to pick the number of parallel RC circuits connected in series.
- `num_RC`: The (maximum) number of parallel RC circuits connected in series.
- `mu_criterion`: The threshold value used in the procedure described by Schönleber et al. (2014).
- `add_capacitance`: Add a capacitance in series to the Voigt circuit.
- `add_inductance`: Add an inductance in series to the Voigt circuit.
- `method`: The iterative method to use if the CNLS test is chosen.
- `max_nfev`: The maximum number of function evaluations to use if the CNLS test is chosen.


_Functions and methods_

#### **deareis.TestSettings.from_dict**

Create an instance from a dictionary.

```python
def from_dict(dictionary: dict) -> TestSettings:
```


_Parameters_

- `dictionary`


_Returns_
```python
TestSettings
```

#### **deareis.TestSettings.to_dict**

Return a dictionary that can be used to recreate an instance.

```python
def to_dict(self) -> dict:
```


_Returns_
```python
dict
```




### **deareis.UnexpectedCharacter**

```python
class UnexpectedCharacter(Exception):
```



### **deareis.UnsupportedFileFormat**

```python
class UnsupportedFileFormat(Exception):
```



### **deareis.Warburg**

Warburg (semi-infinite diffusion)

    Symbol: W

    Z = 1/(Y*(2*pi*f*j)^(1/2))

    Variables
    ---------
    Y: float = 1.0 (S*s^(1/2))

```python
class Warburg(Element):
	kwargs
```

_Constructor parameters_

- `kwargs`




### **deareis.WarburgOpen**

Warburg, finite space or open (finite length diffusion with reflective boundary)

    Symbol: Wo

    Z = coth((B*j*2*pi*f)^n)/((Y*j*2*pi*f)^n)

    Variables
    ---------
    Y: float = 1.0 (S)
    B: float = 1.0 (s^n)
    n: float = 0.5

```python
class WarburgOpen(Element):
	kwargs
```

_Constructor parameters_

- `kwargs`




### **deareis.WarburgShort**

Warburg, finite length or short (finite length diffusion with transmissive boundary)

    Symbol: Ws

    Z = tanh((B*j*2*pi*f)^n)/((Y*j*2*pi*f)^n)

    Variables
    ---------
    Y: float = 1.0 (S)
    B: float = 1.0 (s^n)
    n: float = 0.5

```python
class WarburgShort(Element):
	kwargs
```

_Constructor parameters_

- `kwargs`




### **deareis.Weight**

Types of weights to use during complex non-linear least squares fitting:

- AUTO: try each weight
- BOUKAMP: 1 / (Zre^2 + Zim^2) (eq. 13, Boukamp, 1995)
- MODULUS: 1 / \|Z\|
- PROPORTIONAL: 1 / Zre^2, 1 / Zim^2
- UNITY: 1

```python
class Weight(IntEnum):
```



### **deareis.calculate_drt**

Wrapper for the `pyimpspec.calculate_drt` function.

Calculates the distribution of relaxation times (DRT) for a given data set.

References:

- Kulikovsky, A., 2020, Phys. Chem. Chem. Phys., 22, 19131-19138 (https://doi.org/10.1039/D0CP02094J)
- Wan, T. H., Saccoccio, M., Chen, C., and Ciucci, F., 2015, Electrochim. Acta, 184, 483-499 (https://doi.org/10.1016/j.electacta.2015.09.097).
- Ciucci, F. and Chen, C., 2015, Electrochim. Acta, 167, 439-454 (https://doi.org/10.1016/j.electacta.2015.03.123)
- Effat, M. B. and Ciucci, F., 2017, Electrochim. Acta, 247, 1117-1129 (https://doi.org/10.1016/j.electacta.2017.07.050)
- Liu, J., Wan, T. H., and Ciucci, F., 2020, Electrochim. Acta, 357, 136864 (https://doi.org/10.1016/j.electacta.2020.136864)
- Boukamp, B.A., 2015, Electrochim. Acta, 154, 35-46, (https://doi.org/10.1016/j.electacta.2014.12.059)
- Boukamp, B.A. and Rolle, A, 2017, Solid State Ionics, 302, 12-18 (https://doi.org/10.1016/j.ssi.2016.10.009)

```python
def calculate_drt(data: DataSet, settings: DRTSettings, num_procs: int = -1) -> DRTResult:
```


_Parameters_

- `data`: The data set to use in the calculations.
- `settings`: The settings to use.
- `num_procs`: The maximum number of processes to use.
A value below one results in using the total number of CPU cores present.


_Returns_

```python
DRTResult
```
### **deareis.fit_circuit**

Wrapper for the `pyimpspec.fit_circuit` function.

Fit a circuit to a data set.

```python
def fit_circuit(data: DataSet, settings: FitSettings, num_procs: int = -1) -> FitResult:
```


_Parameters_

- `data`: The data set that the circuit will be fitted to.
- `settings`: The settings that determine the circuit and how the fit is performed.
- `num_procs`: The maximum number of parallel processes to use when method is `CNLSMethod.AUTO` and/or weight is `Weight.AUTO`.


_Returns_

```python
FitResult
```
### **deareis.get_elements**

Returns a mapping of element symbols to the element class.

```python
def get_elements() -> Dict[str, Type[Element]]:
```


_Returns_

```python
Dict[str, Type[Element]]
```
### **deareis.parse_cdc**

Generate a Circuit instance from a string that contains a circuit description code (CDC).

```python
def parse_cdc(cdc: str) -> Circuit:
```


_Parameters_

- `cdc`: A circuit description code (CDC) corresponding to an equivalent circuit.


_Returns_

```python
Circuit
```
### **deareis.parse_data**

Wrapper for `pyimpspec.parse_data`.


    Parse experimental data and return a list of DataSet instances.
    One or more specific sheets can be specified by name when parsing spreadsheets (e.g., .xlsx or .ods) to only return DataSet instances for those sheets.
    If no sheets are specified, then all sheets will be processed and the data from successfully parsed sheets will be returned as DataSet instances.

```python
def parse_data(path: str, file_format: Optional[str] = None, kwargs) -> List[DataSet]:
```


_Parameters_

- `path`: The path to a file containing experimental data that is to be parsed.
- `file_format`: The file format (or extension) that should be assumed when parsing the data.
If no file format is specified, then the file format will be determined based on the file extension.
If there is no file extension, then attempts will be made to parse the file as if it was one of the supported file formats.
- `kwargs`: Keyword arguments are passed to the parser.


_Returns_

```python
List[DataSet]
```
### **deareis.perform_exploratory_tests**

Wrapper for the `pyimpspec.perform_exploratory_tests` function.

Performs a batch of linear Kramers-Kronig tests, which are then scored and sorted from best to worst before they are returned.

```python
def perform_exploratory_tests(data: DataSet, settings: TestSettings, num_procs: int = -1) -> List[TestResult]:
```


_Parameters_

- `data`: The data set to be tested.
- `settings`: The settings that determine how the test is performed.
Note that only `Test.EXPLORATORY` is supported by this function.
- `num_procs`: See perform_test for details.


_Returns_

```python
List[TestResult]
```
### **deareis.perform_test**

Wrapper for the `pyimpspec.perform_test` function.

Performs a linear Kramers-Kronig test as described by Boukamp (1995).
The results can be used to check the validity of an impedance spectrum before performing equivalent circuit fitting.
If the number of (RC) circuits is less than two, then a suitable number of (RC) circuits is determined using the procedure described by Schönleber et al. (2014) based on a criterion for the calculated mu-value (zero to one).
A mu-value of one represents underfitting and a mu-value of zero represents overfitting.

References:

- B.A. Boukamp, 1995, J. Electrochem. Soc., 142, 1885-1894 (https://doi.org/10.1149/1.2044210)
- M. Schönleber, D. Klotz, and E. Ivers-Tiffée, 2014, Electrochim. Acta, 131, 20-27 (https://doi.org/10.1016/j.electacta.2014.01.034)

```python
def perform_test(data: DataSet, settings: TestSettings, num_procs: int = -1) -> TestResult:
```


_Parameters_

- `data`: The data to be tested.
- `settings`: The settings that determine how the test is performed.
Note that `Test.EXPLORATORY` is not supported by this function.
- `num_procs`: The maximum number of parallel processes to use when performing a test.
A value less than one results in using the number of cores returned by multiprocessing.cpu_count.
Applies only to the `TestMode.CNLS` test.


_Returns_

```python
TestResult
```
### **deareis.simulate_spectrum**

Wrapper for the `pyimpspec.simulate_spectrum` function.

Simulate the impedance spectrum generated by a circuit in a certain frequency range.

```python
def simulate_spectrum(settings: SimulationSettings) -> SimulationResult:
```


_Parameters_

- `settings`: The settings to use when performing the simulation.


_Returns_

```python
SimulationResult
```



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