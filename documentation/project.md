---
layout: documentation
title: API - project
permalink: /api/project/
---

`Project` objects can be created via the API for, e.g., the purposes of batch processing multiple experimental data files rather than manually loading files via the GUI program.
`Project` objects can also be used to, e.g., perform statistical analysis on multiple equivalent circuit fitting result and then generate a Markdown/LaTeX table.

**Table of Contents**

- [Project](#deareisproject)
	- [add_data_set](#deareisprojectadd_data_set)
	- [add_fit](#deareisprojectadd_fit)
	- [add_plot](#deareisprojectadd_plot)
	- [add_simulation](#deareisprojectadd_simulation)
	- [add_test](#deareisprojectadd_test)
	- [delete_data_set](#deareisprojectdelete_data_set)
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
	- [get_all_fits](#deareisprojectget_all_fits)
	- [get_all_tests](#deareisprojectget_all_tests)
	- [get_data_sets](#deareisprojectget_data_sets)
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
def get_plot_series(self, plot: PlotSettings, num_per_decade: int = 100) -> List[PlotSeries]:
```


_Parameters_

- `plot`: The plot whose items/series to get.
- `num_per_decade`: The number of data points in fitted/simulated spectra.
Can be used to adjust how smooth an item/series looks.


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



