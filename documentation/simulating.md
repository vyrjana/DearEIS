---
layout: documentation
title: API - simulating
permalink: /api/simulating/
---


**Table of Contents**

- [deareis.api.simulation](#deareis-api-simulation)
	- [SimulationResult](#deareis-api-simulationsimulationresult)
		- [from_dict](#deareis-api-simulationsimulationresultfrom_dict)
		- [get_bode_data](#deareis-api-simulationsimulationresultget_bode_data)
		- [get_frequency](#deareis-api-simulationsimulationresultget_frequency)
		- [get_impedance](#deareis-api-simulationsimulationresultget_impedance)
		- [get_label](#deareis-api-simulationsimulationresultget_label)
		- [get_nyquist_data](#deareis-api-simulationsimulationresultget_nyquist_data)
		- [to_dataframe](#deareis-api-simulationsimulationresultto_dataframe)
		- [to_dict](#deareis-api-simulationsimulationresultto_dict)
	- [SimulationSettings](#deareis-api-simulationsimulationsettings)
		- [from_dict](#deareis-api-simulationsimulationsettingsfrom_dict)
		- [to_dict](#deareis-api-simulationsimulationsettingsto_dict)
	- [simulate_spectrum](#deareis-api-simulationsimulate_spectrum)



## **deareis.api.simulation**

### **deareis.api.simulation.SimulationResult**

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

#### **deareis.api.simulation.SimulationResult.from_dict**

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

#### **deareis.api.simulation.SimulationResult.get_bode_data**

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

#### **deareis.api.simulation.SimulationResult.get_frequency**

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

#### **deareis.api.simulation.SimulationResult.get_impedance**

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

#### **deareis.api.simulation.SimulationResult.get_label**

Generate a label for the result.

```python
def get_label(self) -> str:
```


_Returns_
```python
str
```

#### **deareis.api.simulation.SimulationResult.get_nyquist_data**

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

#### **deareis.api.simulation.SimulationResult.to_dataframe**

Get a `pandas.DataFrame` instance containing a table of element parameters.

```python
def to_dataframe(self) -> DataFrame:
```


_Returns_
```python
DataFrame
```

#### **deareis.api.simulation.SimulationResult.to_dict**

Return a dictionary that can be used to recreate an instance.

```python
def to_dict(self) -> dict:
```


_Returns_
```python
dict
```




### **deareis.api.simulation.SimulationSettings**

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

#### **deareis.api.simulation.SimulationSettings.from_dict**

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

#### **deareis.api.simulation.SimulationSettings.to_dict**

Return a dictionary that can be used to recreate an instance.

```python
def to_dict(self) -> dict:
```


_Returns_
```python
dict
```




### **deareis.api.simulation.simulate_spectrum**

Wrapper for `pyimpspec.simulate_spectrum` function.

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