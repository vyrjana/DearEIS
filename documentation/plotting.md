---
layout: documentation
title: API - plotting
permalink: /api/plotting/
---


**Table of Contents**

- [deareis.api.plotting](#deareisapiplotting)
	- [PlotSeries](#deareisapiplottingplotseries)
		- [get_bode_data](#deareisapiplottingplotseriesget_bode_data)
		- [get_color](#deareisapiplottingplotseriesget_color)
		- [get_drt_credible_intervals](#deareisapiplottingplotseriesget_drt_credible_intervals)
		- [get_drt_data](#deareisapiplottingplotseriesget_drt_data)
		- [get_frequency](#deareisapiplottingplotseriesget_frequency)
		- [get_gamma](#deareisapiplottingplotseriesget_gamma)
		- [get_impedance](#deareisapiplottingplotseriesget_impedance)
		- [get_label](#deareisapiplottingplotseriesget_label)
		- [get_marker](#deareisapiplottingplotseriesget_marker)
		- [get_nyquist_data](#deareisapiplottingplotseriesget_nyquist_data)
		- [get_tau](#deareisapiplottingplotseriesget_tau)
		- [has_legend](#deareisapiplottingplotserieshas_legend)
		- [has_line](#deareisapiplottingplotserieshas_line)
		- [has_markers](#deareisapiplottingplotserieshas_markers)
	- [PlotSettings](#deareisapiplottingplotsettings)
		- [add_series](#deareisapiplottingplotsettingsadd_series)
		- [find_series](#deareisapiplottingplotsettingsfind_series)
		- [from_dict](#deareisapiplottingplotsettingsfrom_dict)
		- [get_label](#deareisapiplottingplotsettingsget_label)
		- [get_series_color](#deareisapiplottingplotsettingsget_series_color)
		- [get_series_label](#deareisapiplottingplotsettingsget_series_label)
		- [get_series_line](#deareisapiplottingplotsettingsget_series_line)
		- [get_series_marker](#deareisapiplottingplotsettingsget_series_marker)
		- [get_series_theme](#deareisapiplottingplotsettingsget_series_theme)
		- [get_type](#deareisapiplottingplotsettingsget_type)
		- [recreate_themes](#deareisapiplottingplotsettingsrecreate_themes)
		- [remove_series](#deareisapiplottingplotsettingsremove_series)
		- [set_label](#deareisapiplottingplotsettingsset_label)
		- [set_series_color](#deareisapiplottingplotsettingsset_series_color)
		- [set_series_label](#deareisapiplottingplotsettingsset_series_label)
		- [set_series_line](#deareisapiplottingplotsettingsset_series_line)
		- [set_series_marker](#deareisapiplottingplotsettingsset_series_marker)
		- [set_type](#deareisapiplottingplotsettingsset_type)
		- [to_dict](#deareisapiplottingplotsettingsto_dict)
	- [PlotType](#deareisapiplottingplottype)



## **deareis.api.plotting**

### **deareis.api.plotting.PlotSeries**

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

#### **deareis.api.plotting.PlotSeries.get_bode_data**


```python
def get_bode_data(self, num_per_decade: int = -1) -> Tuple[ndarray, ndarray, ndarray]:
```


_Parameters_

- `num_per_decade`


_Returns_
```python
Tuple[ndarray, ndarray, ndarray]
```

#### **deareis.api.plotting.PlotSeries.get_color**


```python
def get_color(self) -> Tuple[float, float, float, float]:
```


_Returns_
```python
Tuple[float, float, float, float]
```

#### **deareis.api.plotting.PlotSeries.get_drt_credible_intervals**


```python
def get_drt_credible_intervals(self) -> Tuple[ndarray, ndarray, ndarray, ndarray]:
```


_Returns_
```python
Tuple[ndarray, ndarray, ndarray, ndarray]
```

#### **deareis.api.plotting.PlotSeries.get_drt_data**


```python
def get_drt_data(self, imaginary: bool = False) -> Tuple[ndarray, ndarray]:
```


_Parameters_

- `imaginary`


_Returns_
```python
Tuple[ndarray, ndarray]
```

#### **deareis.api.plotting.PlotSeries.get_frequency**


```python
def get_frequency(self, num_per_decade: int = -1) -> ndarray:
```


_Parameters_

- `num_per_decade`


_Returns_
```python
ndarray
```

#### **deareis.api.plotting.PlotSeries.get_gamma**


```python
def get_gamma(self, imaginary: bool = False) -> ndarray:
```


_Parameters_

- `imaginary`


_Returns_
```python
ndarray
```

#### **deareis.api.plotting.PlotSeries.get_impedance**


```python
def get_impedance(self, num_per_decade: int = -1) -> ndarray:
```


_Parameters_

- `num_per_decade`


_Returns_
```python
ndarray
```

#### **deareis.api.plotting.PlotSeries.get_label**


```python
def get_label(self) -> str:
```


_Returns_
```python
str
```

#### **deareis.api.plotting.PlotSeries.get_marker**


```python
def get_marker(self) -> int:
```


_Returns_
```python
int
```

#### **deareis.api.plotting.PlotSeries.get_nyquist_data**


```python
def get_nyquist_data(self, num_per_decade: int = -1) -> Tuple[ndarray, ndarray]:
```


_Parameters_

- `num_per_decade`


_Returns_
```python
Tuple[ndarray, ndarray]
```

#### **deareis.api.plotting.PlotSeries.get_tau**


```python
def get_tau(self) -> ndarray:
```


_Returns_
```python
ndarray
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

#### **deareis.api.plotting.PlotSettings.add_series**


```python
def add_series(self, series: Union[DataSet, TestResult, DRTResult, FitResult, SimulationResult]):
```


_Parameters_

- `series`

#### **deareis.api.plotting.PlotSettings.find_series**


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
- BODE_MAGNITUDE: \|Z\| vs f
- BODE_PHASE: phi vs f
- DRT: gamma vs tau
- IMPEDANCE_REAL: Zre vs f
- IMPEDANCE_IMAGINARY: Zim vs f

```python
class PlotType(IntEnum):
	args
	kwargs
```

_Constructor parameters_

- `args`
- `kwargs`



