---
layout: documentation
title: API - Kramers-Kronig testing
permalink: /api/kramers-kronig/
---
**Table of Contents**

- [TestResult](#deareistestresult)
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

Get the data required to plot the results as a Bode plot (log |Z| and phi vs log f).

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

Get the data required to plot the residuals (real and imaginary vs log f).

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
	mode: Mode
	num_RC: int
	mu_criterion: float
	add_capacitance: bool
	add_inductance: bool
	method: Method
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



