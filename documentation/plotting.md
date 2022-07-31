---
layout: documentation
title: API - plotting
permalink: /api/plotting/
---


**Table of Contents**

- [deareis.api.plotting](#deareis-api-plotting)
	- [PlotSeries](#deareis-api-plottingplotseries)
		- [get_color](#deareis-api-plottingplotseriesget_color)
		- [get_label](#deareis-api-plottingplotseriesget_label)
		- [get_line_data](#deareis-api-plottingplotseriesget_line_data)
		- [get_marker](#deareis-api-plottingplotseriesget_marker)
		- [get_scatter_data](#deareis-api-plottingplotseriesget_scatter_data)
		- [has_legend](#deareis-api-plottingplotserieshas_legend)
		- [has_line](#deareis-api-plottingplotserieshas_line)
		- [has_markers](#deareis-api-plottingplotserieshas_markers)
	- [PlotSettings](#deareis-api-plottingplotsettings)
		- [add_series](#deareis-api-plottingplotsettingsadd_series)
		- [find_series](#deareis-api-plottingplotsettingsfind_series)
		- [from_dict](#deareis-api-plottingplotsettingsfrom_dict)
		- [get_label](#deareis-api-plottingplotsettingsget_label)
		- [get_series_color](#deareis-api-plottingplotsettingsget_series_color)
		- [get_series_label](#deareis-api-plottingplotsettingsget_series_label)
		- [get_series_line](#deareis-api-plottingplotsettingsget_series_line)
		- [get_series_marker](#deareis-api-plottingplotsettingsget_series_marker)
		- [get_series_theme](#deareis-api-plottingplotsettingsget_series_theme)
		- [get_type](#deareis-api-plottingplotsettingsget_type)
		- [recreate_themes](#deareis-api-plottingplotsettingsrecreate_themes)
		- [remove_series](#deareis-api-plottingplotsettingsremove_series)
		- [set_label](#deareis-api-plottingplotsettingsset_label)
		- [set_series_color](#deareis-api-plottingplotsettingsset_series_color)
		- [set_series_label](#deareis-api-plottingplotsettingsset_series_label)
		- [set_series_line](#deareis-api-plottingplotsettingsset_series_line)
		- [set_series_marker](#deareis-api-plottingplotsettingsset_series_marker)
		- [set_type](#deareis-api-plottingplotsettingsset_type)
		- [to_dict](#deareis-api-plottingplotsettingsto_dict)
	- [PlotType](#deareis-api-plottingplottype)



## **deareis.api.plotting**

### **deareis.api.plotting.PlotSeries**

A class that represents the data used to plot an item/series.

```python
class PlotSeries(object):
	label: str
	scatter_data: List[ndarray]
	line_data: List[ndarray]
	color: List[float]
	marker: int
	line: bool
	legend: bool
```

_Constructor parameters_

- `label`
- `scatter_data`
- `line_data`
- `color`
- `marker`
- `line`
- `legend`


_Functions and methods_

#### **deareis.api.plotting.PlotSeries.get_color**


```python
def get_color(self) -> List[float]:
```


_Returns_
```python
List[float]
```

#### **deareis.api.plotting.PlotSeries.get_label**


```python
def get_label(self) -> str:
```


_Returns_
```python
str
```

#### **deareis.api.plotting.PlotSeries.get_line_data**


```python
def get_line_data(self) -> List[ndarray]:
```


_Returns_
```python
List[ndarray]
```

#### **deareis.api.plotting.PlotSeries.get_marker**


```python
def get_marker(self) -> int:
```


_Returns_
```python
int
```

#### **deareis.api.plotting.PlotSeries.get_scatter_data**


```python
def get_scatter_data(self) -> List[ndarray]:
```


_Returns_
```python
List[ndarray]
```

#### **deareis.api.plotting.PlotSeries.has_legend**


```python
def has_legend(self) -> bool:
```


_Returns_
```python
bool
```

#### **deareis.api.plotting.PlotSeries.has_line**


```python
def has_line(self) -> bool:
```


_Returns_
```python
bool
```

#### **deareis.api.plotting.PlotSeries.has_markers**


```python
def has_markers(self) -> bool:
```


_Returns_
```python
bool
```




### **deareis.api.plotting.PlotSettings**

A class representing a complex plot that can contain one or more data sets, Kramers-Kronig test results, equivalent circuit fitting results, and simulation results.

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

#### **deareis.api.plotting.PlotSettings.add_series**


```python
def add_series(self, series: Union[DataSet, TestResult, FitResult, SimulationResult]):
```


_Parameters_

- `series`

#### **deareis.api.plotting.PlotSettings.find_series**


```python
def find_series(self, uuid: str, datasets: List[DataSet], tests: Dict[str, List[TestResult]], fits: Dict[str, List[FitResult]], simulations: List[SimulationResult]) -> Union[DataSet, TestResult, FitResult, SimulationResult, NoneType]:
```


_Parameters_

- `uuid`
- `datasets`
- `tests`
- `fits`
- `simulations`


_Returns_
```python
Union[DataSet, TestResult, FitResult, SimulationResult, NoneType]
```

#### **deareis.api.plotting.PlotSettings.from_dict**


```python
def from_dict(dictionary: dict) -> PlotSettings:
```


_Parameters_

- `dictionary`


_Returns_
```python
PlotSettings
```

#### **deareis.api.plotting.PlotSettings.get_label**


```python
def get_label(self) -> str:
```


_Returns_
```python
str
```

#### **deareis.api.plotting.PlotSettings.get_series_color**


```python
def get_series_color(self, uuid: str) -> List[float]:
```


_Parameters_

- `uuid`


_Returns_
```python
List[float]
```

#### **deareis.api.plotting.PlotSettings.get_series_label**


```python
def get_series_label(self, uuid: str) -> str:
```


_Parameters_

- `uuid`


_Returns_
```python
str
```

#### **deareis.api.plotting.PlotSettings.get_series_line**


```python
def get_series_line(self, uuid: str) -> bool:
```


_Parameters_

- `uuid`


_Returns_
```python
bool
```

#### **deareis.api.plotting.PlotSettings.get_series_marker**


```python
def get_series_marker(self, uuid: str) -> int:
```


_Parameters_

- `uuid`


_Returns_
```python
int
```

#### **deareis.api.plotting.PlotSettings.get_series_theme**


```python
def get_series_theme(self, uuid: str) -> int:
```


_Parameters_

- `uuid`


_Returns_
```python
int
```

#### **deareis.api.plotting.PlotSettings.get_type**


```python
def get_type(self) -> PlotType:
```


_Returns_
```python
PlotType
```

#### **deareis.api.plotting.PlotSettings.recreate_themes**


```python
def recreate_themes(self):
```

#### **deareis.api.plotting.PlotSettings.remove_series**


```python
def remove_series(self, uuid: str):
```


_Parameters_

- `uuid`

#### **deareis.api.plotting.PlotSettings.set_label**


```python
def set_label(self, label: str):
```


_Parameters_

- `label`

#### **deareis.api.plotting.PlotSettings.set_series_color**


```python
def set_series_color(self, uuid: str, color: List[float]):
```


_Parameters_

- `uuid`
- `color`

#### **deareis.api.plotting.PlotSettings.set_series_label**


```python
def set_series_label(self, uuid: str, label: str):
```


_Parameters_

- `uuid`
- `label`

#### **deareis.api.plotting.PlotSettings.set_series_line**


```python
def set_series_line(self, uuid: str, state: bool):
```


_Parameters_

- `uuid`
- `state`

#### **deareis.api.plotting.PlotSettings.set_series_marker**


```python
def set_series_marker(self, uuid: str, marker: int):
```


_Parameters_

- `uuid`
- `marker`

#### **deareis.api.plotting.PlotSettings.set_type**


```python
def set_type(self, plot_type: PlotType):
```


_Parameters_

- `plot_type`

#### **deareis.api.plotting.PlotSettings.to_dict**


```python
def to_dict(self, session: bool) -> dict:
```


_Parameters_

- `session`


_Returns_
```python
dict
```




### **deareis.api.plotting.PlotType**

Types of plots:

- NYQUIST: -Zim vs Zre
- BODE_MAGNITUDE: |Z| vs log f
- BODE_PHASE: phi vs log f

```python
class PlotType(IntEnum):
	args
	kwargs
```

_Constructor parameters_

- `args`
- `kwargs`



