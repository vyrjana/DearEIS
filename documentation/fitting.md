---
layout: documentation
title: API - fitting
permalink: /api/fitting/
---


**Table of Contents**

- [deareis.api.fitting](#deareisapifitting)
	- [CNLSMethod](#deareisapifittingcnlsmethod)
	- [FitResult](#deareisapifittingfitresult)
		- [from_dict](#deareisapifittingfitresultfrom_dict)
		- [get_bode_data](#deareisapifittingfitresultget_bode_data)
		- [get_frequency](#deareisapifittingfitresultget_frequency)
		- [get_impedance](#deareisapifittingfitresultget_impedance)
		- [get_label](#deareisapifittingfitresultget_label)
		- [get_nyquist_data](#deareisapifittingfitresultget_nyquist_data)
		- [get_residual_data](#deareisapifittingfitresultget_residual_data)
		- [to_dataframe](#deareisapifittingfitresultto_dataframe)
		- [to_dict](#deareisapifittingfitresultto_dict)
	- [FitSettings](#deareisapifittingfitsettings)
		- [from_dict](#deareisapifittingfitsettingsfrom_dict)
		- [to_dict](#deareisapifittingfitsettingsto_dict)
	- [FittedParameter](#deareisapifittingfittedparameter)
		- [from_dict](#deareisapifittingfittedparameterfrom_dict)
		- [get_relative_error](#deareisapifittingfittedparameterget_relative_error)
		- [to_dict](#deareisapifittingfittedparameterto_dict)
	- [FittingError](#deareisapifittingfittingerror)
	- [Weight](#deareisapifittingweight)
	- [fit_circuit](#deareisapifittingfit_circuit)



## **deareis.api.fitting**

### **deareis.api.fitting.CNLSMethod**

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
	args
	kwargs
```

_Constructor parameters_

- `args`
- `kwargs`




### **deareis.api.fitting.FitResult**

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

#### **deareis.api.fitting.FitResult.from_dict**

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

#### **deareis.api.fitting.FitResult.get_bode_data**

Get the data required to plot the results as a Bode plot (|Z| and phi vs f).

```python
def get_bode_data(self, num_per_decade: int = -1) -> Tuple[ndarray, ndarray, ndarray]:
```


_Parameters_

- `num_per_decade`: If the value is greater than zero, then logarithmically distributed frequencies will be generated within the range of frequencies in the data set and used to calculate the impedance produced by the fitted circuit.


_Returns_
```python
Tuple[ndarray, ndarray, ndarray]
```

#### **deareis.api.fitting.FitResult.get_frequency**

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

#### **deareis.api.fitting.FitResult.get_impedance**

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

#### **deareis.api.fitting.FitResult.get_label**

Generate a label for the result.

```python
def get_label(self) -> str:
```


_Returns_
```python
str
```

#### **deareis.api.fitting.FitResult.get_nyquist_data**

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

#### **deareis.api.fitting.FitResult.get_residual_data**

Get the data required to plot the residuals (real and imaginary vs f).

```python
def get_residual_data(self) -> Tuple[ndarray, ndarray, ndarray]:
```


_Returns_
```python
Tuple[ndarray, ndarray, ndarray]
```

#### **deareis.api.fitting.FitResult.to_dataframe**

Get a `pandas.DataFrame` instance containing a table of fitted element parameters.

```python
def to_dataframe(self) -> DataFrame:
```


_Returns_
```python
DataFrame
```

#### **deareis.api.fitting.FitResult.to_dict**

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




### **deareis.api.fitting.FitSettings**

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

#### **deareis.api.fitting.FitSettings.from_dict**

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

#### **deareis.api.fitting.FitSettings.to_dict**

Return a dictionary that can be used to recreate an instance.

```python
def to_dict(self) -> dict:
```


_Returns_
```python
dict
```




### **deareis.api.fitting.FittedParameter**

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

#### **deareis.api.fitting.FittedParameter.from_dict**


```python
def from_dict(dictionary: dict) -> FittedParameter:
```


_Parameters_

- `dictionary`


_Returns_
```python
FittedParameter
```

#### **deareis.api.fitting.FittedParameter.get_relative_error**


```python
def get_relative_error(self) -> float:
```


_Returns_
```python
float
```

#### **deareis.api.fitting.FittedParameter.to_dict**


```python
def to_dict(self) -> dict:
```


_Returns_
```python
dict
```




### **deareis.api.fitting.FittingError**

```python
class FittingError(Exception):
	args
	kwargs
```

_Constructor parameters_

- `args`
- `kwargs`




### **deareis.api.fitting.Weight**

Types of weights:

- AUTO: try each weight
- BOUKAMP: 1 / (Zre^2 + Zim^2) (eq. 13, Boukamp, 1995)
- MODULUS: 1 / |Z|
- PROPORTIONAL: 1 / Zre^2, 1 / Zim^2
- UNITY: 1

```python
class Weight(IntEnum):
	args
	kwargs
```

_Constructor parameters_

- `args`
- `kwargs`




### **deareis.api.fitting.fit_circuit**

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