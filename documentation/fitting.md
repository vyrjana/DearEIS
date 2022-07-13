---
layout: documentation
title: API - fitting
permalink: /api/fitting/
---
**Table of Contents**

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
	method: Method
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

Get the data required to plot the results as a Bode plot (log |Z| and phi vs log f).

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

Get the data required to plot the residuals (real and imaginary vs log f).

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
	method: Method
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



