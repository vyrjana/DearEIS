---
layout: documentation
title: API - plotting
permalink: /api/plotting/
---
**Table of Contents**

- [PlotSeries](#deareisplotseries)
	- [get_color](#deareisplotseriesget_color)
	- [get_label](#deareisplotseriesget_label)
	- [get_line_data](#deareisplotseriesget_line_data)
	- [get_marker](#deareisplotseriesget_marker)
	- [get_scatter_data](#deareisplotseriesget_scatter_data)
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


### **deareis.PlotSeries**

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

#### **deareis.PlotSeries.get_color**


```python
def get_color(self) -> List[float]:
```


_Returns_
```python
List[float]
```

#### **deareis.PlotSeries.get_label**


```python
def get_label(self) -> str:
```


_Returns_
```python
str
```

#### **deareis.PlotSeries.get_line_data**


```python
def get_line_data(self) -> List[ndarray]:
```


_Returns_
```python
List[ndarray]
```

#### **deareis.PlotSeries.get_marker**


```python
def get_marker(self) -> int:
```


_Returns_
```python
int
```

#### **deareis.PlotSeries.get_scatter_data**


```python
def get_scatter_data(self) -> List[ndarray]:
```


_Returns_
```python
List[ndarray]
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

#### **deareis.PlotSettings.add_series**


```python
def add_series(self, series: Union[DataSet, TestResult, FitResult, SimulationResult]):
```


_Parameters_

- `series`

#### **deareis.PlotSettings.find_series**


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

- NYQUIST
- BODE_MAGNITUDE
- BODE_PHASE

```python
class PlotType(IntEnum):
	args
	kwargs
```

_Constructor parameters_

- `args`
- `kwargs`



