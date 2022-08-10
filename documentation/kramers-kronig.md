---
layout: documentation
title: API - Kramers-Kronig testing
permalink: /api/kramers-kronig/
---


**Table of Contents**

- [deareis.api.kramers_kronig](#deareisapikramers_kronig)
	- [Method](#deareisapikramers_kronigmethod)
	- [Mode](#deareisapikramers_kronigmode)
	- [Test](#deareisapikramers_kronigtest)
	- [TestResult](#deareisapikramers_kronigtestresult)
		- [from_dict](#deareisapikramers_kronigtestresultfrom_dict)
		- [get_bode_data](#deareisapikramers_kronigtestresultget_bode_data)
		- [get_frequency](#deareisapikramers_kronigtestresultget_frequency)
		- [get_impedance](#deareisapikramers_kronigtestresultget_impedance)
		- [get_label](#deareisapikramers_kronigtestresultget_label)
		- [get_nyquist_data](#deareisapikramers_kronigtestresultget_nyquist_data)
		- [get_residual_data](#deareisapikramers_kronigtestresultget_residual_data)
		- [to_dict](#deareisapikramers_kronigtestresultto_dict)
	- [TestSettings](#deareisapikramers_kronigtestsettings)
		- [from_dict](#deareisapikramers_kronigtestsettingsfrom_dict)
		- [to_dict](#deareisapikramers_kronigtestsettingsto_dict)
	- [perform_test](#deareisapikramers_kronigperform_test)



## **deareis.api.kramers_kronig**

### **deareis.api.kramers_kronig.Method**

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
class Method(IntEnum):
	args
	kwargs
```

_Constructor parameters_

- `args`
- `kwargs`




### **deareis.api.kramers_kronig.Mode**

Types of modes that determine how the number of Voigt elements (capacitor connected in parallel with resistor) is chosen:

- AUTO: follow procedure described by Schönleber, Klotz, and Ivers-Tiffée (2014)
- EXPLORATORY: same procedure as AUTO but present intermediate results to user and apply additional weighting to the initial suggestion
- MANUAL: manually choose the number

```python
class Mode(IntEnum):
	args
	kwargs
```

_Constructor parameters_

- `args`
- `kwargs`




### **deareis.api.kramers_kronig.Test**

Types of tests:

- CNLS: complex non-linear least-squares fit of circuit (fig. 1, Boukamp, 1995) with a distribution of fixed time constants
- COMPLEX: eqs. 11 and 12, Boukamp, 1995
- IMAGINARY: eqs. 4, 6, and 7, Boukamp, 1995
- REAL: eqs. 5, 8, 9, and 10, Boukamp, 1995

```python
class Test(IntEnum):
	args
	kwargs
```

_Constructor parameters_

- `args`
- `kwargs`




### **deareis.api.kramers_kronig.TestResult**

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

#### **deareis.api.kramers_kronig.TestResult.from_dict**

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

#### **deareis.api.kramers_kronig.TestResult.get_bode_data**

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

#### **deareis.api.kramers_kronig.TestResult.get_frequency**

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

#### **deareis.api.kramers_kronig.TestResult.get_impedance**

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

#### **deareis.api.kramers_kronig.TestResult.get_label**

Generate a label for the result.

```python
def get_label(self) -> str:
```


_Returns_
```python
str
```

#### **deareis.api.kramers_kronig.TestResult.get_nyquist_data**

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

#### **deareis.api.kramers_kronig.TestResult.get_residual_data**

Get the data required to plot the residuals (real and imaginary vs log f).

```python
def get_residual_data(self) -> Tuple[ndarray, ndarray, ndarray]:
```


_Returns_
```python
Tuple[ndarray, ndarray, ndarray]
```

#### **deareis.api.kramers_kronig.TestResult.to_dict**

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




### **deareis.api.kramers_kronig.TestSettings**

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

#### **deareis.api.kramers_kronig.TestSettings.from_dict**

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

#### **deareis.api.kramers_kronig.TestSettings.to_dict**

Return a dictionary that can be used to recreate an instance.

```python
def to_dict(self) -> dict:
```


_Returns_
```python
dict
```




### **deareis.api.kramers_kronig.perform_test**

Wrapper for `pyimpspec.perform_test` function.

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
Applies only to the `Mode.CNLS` test.


_Returns_

```python
TestResult
```