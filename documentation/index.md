---
layout: default
title: API reference
permalink: /api/
---

# API reference

Testing out how this would look.

- [FitResult](#fitresult)
	- [from_dict](#fitresult-from-dict)

## FitResult

A class containing the result of a circuit fit.

### Signature

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

### Parameters

- `uuid`: The universally unique identifier assigned to this result.


### Properties


### Methods

#### FitResult.from_dict

Create an instance from a dictionary.

##### Signature

```python
def from_dict(dictionary: dict) -> FitResult:
```

##### Parameters

- `dictionary`: A dictionary.

##### Returns

```python
FitResult
```

