---
layout: documentation
title: API - drt
permalink: /api/drt/
---


**Table of Contents**

- [deareis.api.drt](#deareisapidrt)
	- [DRTError](#deareisapidrtdrterror)
	- [DRTMethod](#deareisapidrtdrtmethod)
	- [DRTMode](#deareisapidrtdrtmode)
	- [DRTResult](#deareisapidrtdrtresult)
		- [from_dict](#deareisapidrtdrtresultfrom_dict)
		- [get_bode_data](#deareisapidrtdrtresultget_bode_data)
		- [get_drt_credible_intervals](#deareisapidrtdrtresultget_drt_credible_intervals)
		- [get_drt_data](#deareisapidrtdrtresultget_drt_data)
		- [get_frequency](#deareisapidrtdrtresultget_frequency)
		- [get_gamma](#deareisapidrtdrtresultget_gamma)
		- [get_impedance](#deareisapidrtdrtresultget_impedance)
		- [get_label](#deareisapidrtdrtresultget_label)
		- [get_nyquist_data](#deareisapidrtdrtresultget_nyquist_data)
		- [get_peaks](#deareisapidrtdrtresultget_peaks)
		- [get_residual_data](#deareisapidrtdrtresultget_residual_data)
		- [get_score_dataframe](#deareisapidrtdrtresultget_score_dataframe)
		- [get_scores](#deareisapidrtdrtresultget_scores)
		- [get_tau](#deareisapidrtdrtresultget_tau)
		- [to_dataframe](#deareisapidrtdrtresultto_dataframe)
		- [to_dict](#deareisapidrtdrtresultto_dict)
	- [DRTSettings](#deareisapidrtdrtsettings)
		- [from_dict](#deareisapidrtdrtsettingsfrom_dict)
		- [to_dict](#deareisapidrtdrtsettingsto_dict)
	- [RBFShape](#deareisapidrtrbfshape)
	- [RBFType](#deareisapidrtrbftype)
	- [calculate_drt](#deareisapidrtcalculate_drt)



## **deareis.api.drt**

### **deareis.api.drt.DRTError**

```python
class DRTError(Exception):
```



### **deareis.api.drt.DRTMethod**

The method to use for calculating the DRT:

- TR_NNLS
- TR_RBF
- BHT

```python
class DRTMethod(IntEnum):
```



### **deareis.api.drt.DRTMode**

The parts of the impedance data to use:

- COMPLEX
- REAL
- IMAGINARY

```python
class DRTMode(IntEnum):
```



### **deareis.api.drt.DRTResult**

An object representing the results of calculating the distribution of relaxation times in a  data set.

```python
class DRTResult(object):
	uuid: str
	timestamp: float
	tau: ndarray
	gamma: ndarray
	frequency: ndarray
	impedance: ndarray
	real_residual: ndarray
	imaginary_residual: ndarray
	mean_gamma: ndarray
	lower_bound: ndarray
	upper_bound: ndarray
	imaginary_gamma: ndarray
	scores: Dict[str, complex]
	chisqr: float
	lambda_value: float
	mask: Dict[int, bool]
	settings: DRTSettings
```

_Constructor parameters_

- `uuid`: The universally unique identifier assigned to this result.
- `timestamp`: The Unix time (in seconds) for when the test was performed.
- `tau`: The time constants (in seconds).
- `gamma`: The corresponding gamma(tau) values (in ohms).
These are the gamma(tau) for the real part when the BHT method has been used.
- `frequency`: The frequencies of the analyzed data set.
- `impedance`: The modeled impedances.
- `real_residual`: The residuals for the real parts of the modeled and experimental impedances.
- `imaginary_residual`: The residuals for the imaginary parts of the modeled and experimental impedances.
- `mean_gamma`: The mean values for gamma(tau).
Only non-empty when the TR-RBF method has been used and the Bayesian credible intervals have been calculated.
- `lower_bound`: The lower bound for the gamma(tau) values.
Only non-empty when the TR-RBF method has been used and the Bayesian credible intervals have been calculated.
- `upper_bound`: The upper bound for the gamma(tau) values.
Only non-empty when the TR-RBF method has been used and the Bayesian credible intervals have been calculated.
- `imaginary_gamma`: These are the gamma(tau) for the imaginary part when the BHT method has been used.
Only non-empty when the BHT method has been used.
- `scores`: The scores calculated for the analyzed data set.
Only non-empty when the BHT method has been used.
- `chisqr`: The chi-square goodness of fit value for the modeled impedance.
- `lambda_value`: The regularization parameter used as part of the Tikhonov regularization.
Only valid (i.e., positive) when the TR-NNLS or TR-RBF methods have been used.
- `mask`: The mask that was applied to the analyzed data set.
- `settings`: The settings used to perform this analysis.


_Functions and methods_

#### **deareis.api.drt.DRTResult.from_dict**

Create an instance from a dictionary.

```python
def from_dict(dictionary: dict) -> DRTResult:
```


_Parameters_

- `dictionary`


_Returns_
```python
DRTResult
```

#### **deareis.api.drt.DRTResult.get_bode_data**

Get the data necessary to plot this DataSet as a Bode plot: the frequencies, the absolute magnitudes of the impedances, and the negative phase angles/shifts of the impedances in degrees.

```python
def get_bode_data(self) -> Tuple[ndarray, ndarray, ndarray]:
```


_Returns_
```python
Tuple[ndarray, ndarray, ndarray]
```

#### **deareis.api.drt.DRTResult.get_drt_credible_intervals**

Get the data necessary to plot the Bayesian credible intervals for this DRTResult: the time constants, the mean gamma values, the lower bound gamma values, and the upper bound gamma values.

```python
def get_drt_credible_intervals(self) -> Tuple[ndarray, ndarray, ndarray, ndarray]:
```


_Returns_
```python
Tuple[ndarray, ndarray, ndarray, ndarray]
```

#### **deareis.api.drt.DRTResult.get_drt_data**

Get the data necessary to plot this DRTResult as a DRT plot: the time constants and the corresponding gamma values.

```python
def get_drt_data(self, imaginary: bool = False) -> Tuple[ndarray, ndarray]:
```


_Parameters_

- `imaginary`: Get the imaginary gamma (non-empty only when using the BHT method).


_Returns_
```python
Tuple[ndarray, ndarray]
```

#### **deareis.api.drt.DRTResult.get_frequency**

Get the frequencies (in hertz) of the data set.

```python
def get_frequency(self) -> ndarray:
```


_Returns_
```python
ndarray
```

#### **deareis.api.drt.DRTResult.get_gamma**

Get the gamma values.

```python
def get_gamma(self, imaginary: bool = False) -> ndarray:
```


_Parameters_

- `imaginary`: Get the imaginary gamma (non-empty only when using the BHT method).


_Returns_
```python
ndarray
```

#### **deareis.api.drt.DRTResult.get_impedance**

Get the complex impedance of the model.

```python
def get_impedance(self) -> ndarray:
```


_Returns_
```python
ndarray
```

#### **deareis.api.drt.DRTResult.get_label**

Generate a label for the result.

```python
def get_label(self) -> str:
```


_Returns_
```python
str
```

#### **deareis.api.drt.DRTResult.get_nyquist_data**

Get the data necessary to plot this DataSet as a Nyquist plot: the real and the negative imaginary parts of the impedances.

```python
def get_nyquist_data(self) -> Tuple[ndarray, ndarray]:
```


_Returns_
```python
Tuple[ndarray, ndarray]
```

#### **deareis.api.drt.DRTResult.get_peaks**

Get the time constants (in seconds) and gamma (in ohms) of peaks with magnitudes greater than the threshold.
The threshold and the magnitudes are all relative to the magnitude of the highest peak.

```python
def get_peaks(self, threshold: float = 0.0, imaginary: bool = False) -> Tuple[ndarray, ndarray]:
```


_Parameters_

- `threshold`: The threshold for the relative magnitude (0.0 to 1.0).
- `imaginary`: Use the imaginary gamma (non-empty only when using the BHT method).


_Returns_
```python
Tuple[ndarray, ndarray]
```

#### **deareis.api.drt.DRTResult.get_residual_data**

Get the data necessary to plot the relative residuals for this DRTResult: the frequencies, the relative residuals for the real parts of the impedances in percents, and the relative residuals for the imaginary parts of the impedances in percents.

```python
def get_residual_data(self) -> Tuple[ndarray, ndarray, ndarray]:
```


_Returns_
```python
Tuple[ndarray, ndarray, ndarray]
```

#### **deareis.api.drt.DRTResult.get_score_dataframe**

Get the scores (BHT) method for the data set as a pandas.DataFrame object that can be used to generate, e.g., a Markdown table.

```python
def get_score_dataframe(self, latex_labels: bool = False) -> Optional[DataFrame]:
```


_Parameters_

- `latex_labels`: Whether or not to use LaTeX macros in the labels.


_Returns_
```python
Optional[DataFrame]
```

#### **deareis.api.drt.DRTResult.get_scores**

Get the scores (BHT method) for the data set.
The scores are represented as complex values where the real and imaginary parts have magnitudes ranging from 0.0 to 1.0.
A consistent impedance spectrum should score high.

```python
def get_scores(self) -> Dict[str, complex]:
```


_Returns_
```python
Dict[str, complex]
```

#### **deareis.api.drt.DRTResult.get_tau**

Get the time constants.

```python
def get_tau(self) -> ndarray:
```


_Returns_
```python
ndarray
```

#### **deareis.api.drt.DRTResult.to_dataframe**

Get the peaks as a pandas.DataFrame object that can be used to generate, e.g., a Markdown table.

```python
def to_dataframe(self, threshold: float = 0.0, imaginary: bool = False, latex_labels: bool = False, include_frequency: bool = False) -> DataFrame:
```


_Parameters_

- `threshold`: The threshold for the peaks (0.0 to 1.0 relative to the highest peak).
- `imaginary`: Use the imaginary gamma (non-empty only when using the BHT method).
- `latex_labels`: Whether or not to use LaTeX macros in the labels.
- `include_frequency`: Whether or not to also include a column with the frequencies corresponding to the time constants.


_Returns_
```python
DataFrame
```

#### **deareis.api.drt.DRTResult.to_dict**

Return a dictionary that can be used to recreate an instance.

```python
def to_dict(self) -> dict:
```


_Returns_
```python
dict
```




### **deareis.api.drt.DRTSettings**

The settings to use when performing a DRT analysis.

```python
class DRTSettings(object):
	method: DRTMethod
	mode: DRTMode
	lambda_value: float
	rbf_type: RBFType
	derivative_order: int
	rbf_shape: RBFShape
	shape_coeff: float
	inductance: bool
	credible_intervals: bool
	num_samples: int
	num_attempts: int
	maximum_symmetry: float
```

_Constructor parameters_

- `method`: The method to use to perform the analysis.
- `mode`: The mode or type of data  (i.e., complex, real, or imaginary) to use.
TR-NNLS and TR-RBF methods only.
- `lambda_value`: The Tikhonov regularization parameter to use.
TR-NNLS and TR-RBF methods only.
- `rbf_type`: The radial basis function to use for discretization.
BHT and TR-RBF methods only.
- `derivative_order`: The derivative order to use when calculating the penalty in the Tikhonov regularization.
BHT and TR-RBF methods only.
- `rbf_shape`: The shape to use with the radial basis function discretization.
BHT and TR-RBF methods only.
- `shape_coeff`: The shape coefficient.
BHT and TR-RBF methods only.
- `inductance`: Whether or not to include an inductive term in the calculations.
TR-RBF methods only.
- `credible_intervals`: Whether or not to calculate Bayesian credible intervals.
TR-RBF methods only.
- `num_samples`: The number of samples to use when calculating:
    - the Bayesian credible intervals (TR-RBF method)
    - the Jensen-Shannon distance (BHT method)
- `num_attempts`: The number of attempts to make to find a solution.
BHT method only.
- `maximum_symmetry`: The maximum vertical peak-to-peak symmetry allowed.
Used to discard results with strong oscillations.
Smaller values provide stricter conditions.
BHT and TR-RBF methods only.


_Functions and methods_

#### **deareis.api.drt.DRTSettings.from_dict**


```python
def from_dict(dictionary: dict) -> DRTSettings:
```


_Parameters_

- `dictionary`


_Returns_
```python
DRTSettings
```

#### **deareis.api.drt.DRTSettings.to_dict**


```python
def to_dict(self) -> dict:
```


_Returns_
```python
dict
```




### **deareis.api.drt.RBFShape**

The shape to use with the radial basis function discretization:

- FWHM
- FACTOR

```python
class RBFShape(IntEnum):
```



### **deareis.api.drt.RBFType**

The radial basis function to use for discretization (or piecewise linear discretization):

- C0_MATERN
- C2_MATERN
- C4_MATERN
- C6_MATERN
- CAUCHY
- GAUSSIAN
- INVERSE_QUADRATIC
- INVERSE_QUADRIC
- PIECEWISE_LINEAR

```python
class RBFType(IntEnum):
```



### **deareis.api.drt.calculate_drt**

Wrapper for the `pyimpspec.calculate_drt` function.

Calculates the distribution of relaxation times (DRT) for a given data set.

```python
def calculate_drt(data: DataSet, settings: DRTSettings, num_procs: int = -1) -> DRTResult:
```


_Parameters_

- `data`: The data set to use in the calculations.
- `settings`: The settings to use.
- `num_procs`: The maximum number of processes to use.
A value below one results in using the total number of CPU cores present.


_Returns_

```python
DRTResult
```