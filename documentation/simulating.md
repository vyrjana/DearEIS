---
layout: documentation
title: API - simulating
permalink: /api/simulating/
---
**Table of Contents**

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

Get the data required to plot the results as a Bode plot (log |Z| and phi vs log f).

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
	num_freq_per_dec: int
```

_Constructor parameters_

- `cdc`: The circuit description code (CDC) for the circuit to simulate.
- `min_frequency`: The minimum frequency (in hertz) to simulate.
- `max_frequency`: The maximum frequency (in hertz) to simulate.
- `num_freq_per_dec`: The number of frequencies per decade to simulate.
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



