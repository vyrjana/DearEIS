---
layout: documentation
title: API - Elements
permalink: /api/elements/
---


**Table of Contents**

- [deareis.api.circuit](#deareisapicircuit)
	- [Capacitor](#deareisapicircuitcapacitor)
	- [ConstantPhaseElement](#deareisapicircuitconstantphaseelement)
	- [DeLevieFiniteLength](#deareisapicircuitdeleviefinitelength)
	- [Element](#deareisapicircuitelement)
		- [get_default_fixed](#deareisapicircuitelementget_default_fixed)
		- [get_default_label](#deareisapicircuitelementget_default_label)
		- [get_default_lower_limits](#deareisapicircuitelementget_default_lower_limits)
		- [get_default_upper_limits](#deareisapicircuitelementget_default_upper_limits)
		- [get_defaults](#deareisapicircuitelementget_defaults)
		- [get_description](#deareisapicircuitelementget_description)
		- [get_extended_description](#deareisapicircuitelementget_extended_description)
		- [get_identifier](#deareisapicircuitelementget_identifier)
		- [get_label](#deareisapicircuitelementget_label)
		- [get_lower_limit](#deareisapicircuitelementget_lower_limit)
		- [get_parameters](#deareisapicircuitelementget_parameters)
		- [get_symbol](#deareisapicircuitelementget_symbol)
		- [get_upper_limit](#deareisapicircuitelementget_upper_limit)
		- [impedance](#deareisapicircuitelementimpedance)
		- [impedances](#deareisapicircuitelementimpedances)
		- [is_fixed](#deareisapicircuitelementis_fixed)
		- [reset_parameters](#deareisapicircuitelementreset_parameters)
		- [set_fixed](#deareisapicircuitelementset_fixed)
		- [set_label](#deareisapicircuitelementset_label)
		- [set_lower_limit](#deareisapicircuitelementset_lower_limit)
		- [set_parameters](#deareisapicircuitelementset_parameters)
		- [set_upper_limit](#deareisapicircuitelementset_upper_limit)
		- [to_latex](#deareisapicircuitelementto_latex)
		- [to_string](#deareisapicircuitelementto_string)
		- [to_sympy](#deareisapicircuitelementto_sympy)
	- [Gerischer](#deareisapicircuitgerischer)
	- [HavriliakNegami](#deareisapicircuithavriliaknegami)
	- [HavriliakNegamiAlternative](#deareisapicircuithavriliaknegamialternative)
	- [Inductor](#deareisapicircuitinductor)
	- [ModifiedInductor](#deareisapicircuitmodifiedinductor)
	- [Resistor](#deareisapicircuitresistor)
	- [Warburg](#deareisapicircuitwarburg)
	- [WarburgOpen](#deareisapicircuitwarburgopen)
	- [WarburgShort](#deareisapicircuitwarburgshort)
	- [get_elements](#deareisapicircuitget_elements)



## **deareis.api.circuit**

### **deareis.api.circuit.Capacitor**

Capacitor

    Symbol: C

    Z = 1/(j*2*pi*f*C)

    Variables
    ---------
    C: float = 1E-6 (F)

```python
class Capacitor(Element):
	kwargs
```

_Constructor parameters_

- `kwargs`




### **deareis.api.circuit.ConstantPhaseElement**

Constant phase element

    Symbol: Q

    Z = 1/(Y*(j*2*pi*f)^n)

    Variables
    ---------
    Y: float = 1E-6 (F*s^(n-1))
    n: float = 0.95

```python
class ConstantPhaseElement(Element):
	kwargs
```

_Constructor parameters_

- `kwargs`




### **deareis.api.circuit.DeLevieFiniteLength**

de Levie pore (finite length)

    Symbol: Ls

    Z = (Ri*Rr)^(1/2)*coth(d*(Ri/Rr)^(1/2)*(1+Y*(2*pi*f*j)^n)^(1/2))/(1+Y*(2*pi*f*j)^n)^(1/2)

    Variables
    ---------
    Ri: float = 10.0 (ohm/cm)
    Rr: float = 1.0 (ohm*cm)
    Y: float = 0.01 (F*s^(n-1)/cm)
    n: float = 0.8
    d: float = 0.2 (cm)

```python
class DeLevieFiniteLength(Element):
	kwargs
```

_Constructor parameters_

- `kwargs`




### **deareis.api.circuit.Element**

```python
class Element(object):
	keys: List[str]
```

_Constructor parameters_

- `keys`


_Functions and methods_

#### **deareis.api.circuit.Element.get_default_fixed**

Get whether or not the element's parameters are fixed by default.

```python
def get_default_fixed() -> Dict[str, bool]:
```


_Returns_
```python
Dict[str, bool]
```

#### **deareis.api.circuit.Element.get_default_label**

Get the default label for this element.

```python
def get_default_label(self) -> str:
```


_Returns_
```python
str
```

#### **deareis.api.circuit.Element.get_default_lower_limits**

Get the default lower limits for the element's parameters.

```python
def get_default_lower_limits() -> Dict[str, float]:
```


_Returns_
```python
Dict[str, float]
```

#### **deareis.api.circuit.Element.get_default_upper_limits**

Get the default upper limits for the element's parameters.

```python
def get_default_upper_limits() -> Dict[str, float]:
```


_Returns_
```python
Dict[str, float]
```

#### **deareis.api.circuit.Element.get_defaults**

Get the default values for the element's parameters.

```python
def get_defaults() -> Dict[str, float]:
```


_Returns_
```python
Dict[str, float]
```

#### **deareis.api.circuit.Element.get_description**

Get a brief description of the element and its symbol.

```python
def get_description() -> str:
```


_Returns_
```python
str
```

#### **deareis.api.circuit.Element.get_extended_description**


```python
def get_extended_description() -> str:
```


_Returns_
```python
str
```

#### **deareis.api.circuit.Element.get_identifier**

Get the internal identifier that is unique in the context of a circuit.
Used internally when generating unique names for parameters when fitting a circuit to a
data set.

```python
def get_identifier(self) -> int:
```


_Returns_
```python
int
```

#### **deareis.api.circuit.Element.get_label**

Get the label assigned to a specific instance of the element.

```python
def get_label(self) -> str:
```


_Returns_
```python
str
```

#### **deareis.api.circuit.Element.get_lower_limit**

Get the lower limit for the value of an element parameter when fitting a circuit to a data
set.
The absence of a limit is represented by -numpy.inf.

```python
def get_lower_limit(self, key: str) -> float:
```


_Parameters_

- `key`: A key corresponding to an element parameter.


_Returns_
```python
float
```

#### **deareis.api.circuit.Element.get_parameters**

Get the current parameters of the element.

```python
def get_parameters(self) -> OrderedDict[str, float]:
```


_Returns_
```python
OrderedDict[str, float]
```

#### **deareis.api.circuit.Element.get_symbol**

Get the symbol representing the element.

```python
def get_symbol() -> str:
```


_Returns_
```python
str
```

#### **deareis.api.circuit.Element.get_upper_limit**

Get the upper limit for the value of an element parameter when fitting a circuit to a data
set.
The absence of a limit is represented by numpy.inf.

```python
def get_upper_limit(self, key: str) -> float:
```


_Parameters_

- `key`: A key corresponding to an element parameter.


_Returns_
```python
float
```

#### **deareis.api.circuit.Element.impedance**

Calculates the complex impedance of the element at a specific frequency.

```python
def impedance(self, f: float) -> complex:
```


_Parameters_

- `f`: Frequency in hertz.


_Returns_
```python
complex
```

#### **deareis.api.circuit.Element.impedances**

Calculates the complex impedance of the element at specific frequencies.

```python
def impedances(self, freq: Union[list, ndarray]) -> ndarray:
```


_Parameters_

- `freq`: Frequencies in hertz.


_Returns_
```python
ndarray
```

#### **deareis.api.circuit.Element.is_fixed**

Check if an element parameter should have a fixed value when fitting a circuit to a data
set.
True if fixed and False if not fixed.

```python
def is_fixed(self, key: str) -> bool:
```


_Parameters_

- `key`: A key corresponding to an element parameter.


_Returns_
```python
bool
```

#### **deareis.api.circuit.Element.reset_parameters**

Resets the value, lower limit, upper limit, and fixed state of one or more parameters.

```python
def reset_parameters(self, keys: List[str]):
```


_Parameters_

- `keys`: Names of the parameters to reset.

#### **deareis.api.circuit.Element.set_fixed**

Set whether or not an element parameter should have a fixed value when fitting a circuit
to a data set.

```python
def set_fixed(self, key: str, value: bool) -> Element:
```


_Parameters_

- `key`: A key corresponding to an element parameter.
- `value`: True if the value should be fixed.


_Returns_
```python
Element
```

#### **deareis.api.circuit.Element.set_label**

Set the label assigned to a specific instance of the element.

```python
def set_label(self, label: str) -> Element:
```


_Parameters_

- `label`: The new label.


_Returns_
```python
Element
```

#### **deareis.api.circuit.Element.set_lower_limit**

Set the upper limit for the value of an element parameter when fitting a circuit to a data
set.

```python
def set_lower_limit(self, key: str, value: float) -> Element:
```


_Parameters_

- `key`: A key corresponding to an element parameter.
- `value`: The new limit for the element parameter. The limit can be removed by setting the limit
to be -numpy.inf.


_Returns_
```python
Element
```

#### **deareis.api.circuit.Element.set_parameters**

Set new values for the parameters of the element.

```python
def set_parameters(self, parameters: Dict[str, float]):
```


_Parameters_

- `parameters`

#### **deareis.api.circuit.Element.set_upper_limit**

Set the upper limit for the value of an element parameter when fitting a circuit to a data
set.

```python
def set_upper_limit(self, key: str, value: float) -> Element:
```


_Parameters_

- `key`: A key corresponding to an element parameter.
- `value`: The new limit for the element parameter. The limit can be removed by setting the limit
to be numpy.inf.


_Returns_
```python
Element
```

#### **deareis.api.circuit.Element.to_latex**


```python
def to_latex(self) -> str:
```


_Returns_
```python
str
```

#### **deareis.api.circuit.Element.to_string**

Generates a string representation of the element.

```python
def to_string(self, decimals: int = -1) -> str:
```


_Parameters_

- `decimals`: The number of decimals used when formatting the current value and the limits for the element's parameters.
-1 corresponds to no values being included in the output.


_Returns_
```python
str
```

#### **deareis.api.circuit.Element.to_sympy**


```python
def to_sympy(self, substitute: bool = False) -> Expr:
```


_Parameters_

- `substitute`


_Returns_
```python
Expr
```




### **deareis.api.circuit.Gerischer**

Gerischer

    Symbol: G

    Z = 1/(Y*(k+j*2*pi*f)^n)

    Variables
    ---------
    Y: float = 1.0 (S*s^n)
    k: float = 1.0 (s^-1)
    n: float = 0.5

```python
class Gerischer(Element):
	kwargs
```

_Constructor parameters_

- `kwargs`




### **deareis.api.circuit.HavriliakNegami**

Havriliak-Negami relaxation

    Symbol: H

    Z = (((1+(j*2*pi*f*t)^a)^b)/(j*2*pi*f*dC))

    Variables
    ---------
    dC: float = 1E-6 (F)
    t: float = 1.0 (s)
    a: float = 0.9
    b: float = 0.9

```python
class HavriliakNegami(Element):
	kwargs
```

_Constructor parameters_

- `kwargs`




### **deareis.api.circuit.HavriliakNegamiAlternative**

Havriliak-Negami relaxation (alternative form)

    Symbol: Ha

    Z = R / ((1 + (I*2*pi*f*t)^b)^g)

    Variables
    ---------
    R: float = 1 (ohm)
    t: float = 1.0 (s)
    b: float = 0.7
    g: float = 0.8

```python
class HavriliakNegamiAlternative(Element):
	kwargs
```

_Constructor parameters_

- `kwargs`




### **deareis.api.circuit.Inductor**

Inductor

    Symbol: L

    Z = j*2*pi*f*L

    Variables
    ---------
    L: float = 1E-6 (H)

```python
class Inductor(Element):
	kwargs
```

_Constructor parameters_

- `kwargs`




### **deareis.api.circuit.ModifiedInductor**

Modified inductor

    Symbol: La

    Z = L*(j*2*pi*f)^n

    Variables
    ---------
    L: float = 1E-6 (H*s^(n-1))
    n: float = 0.95

```python
class ModifiedInductor(Element):
	kwargs
```

_Constructor parameters_

- `kwargs`




### **deareis.api.circuit.Resistor**

Resistor

    Symbol: R

    Z = R

    Variables
    ---------
    R: float = 1E+3 (ohm)

```python
class Resistor(Element):
	kwargs
```

_Constructor parameters_

- `kwargs`




### **deareis.api.circuit.Warburg**

Warburg (semi-infinite diffusion)

    Symbol: W

    Z = 1/(Y*(2*pi*f*j)^(1/2))

    Variables
    ---------
    Y: float = 1.0 (S*s^(1/2))

```python
class Warburg(Element):
	kwargs
```

_Constructor parameters_

- `kwargs`




### **deareis.api.circuit.WarburgOpen**

Warburg, finite space or open (finite length diffusion with reflective boundary)

    Symbol: Wo

    Z = coth((B*j*2*pi*f)^n)/((Y*j*2*pi*f)^n)

    Variables
    ---------
    Y: float = 1.0 (S)
    B: float = 1.0 (s^n)
    n: float = 0.5

```python
class WarburgOpen(Element):
	kwargs
```

_Constructor parameters_

- `kwargs`




### **deareis.api.circuit.WarburgShort**

Warburg, finite length or short (finite length diffusion with transmissive boundary)

    Symbol: Ws

    Z = tanh((B*j*2*pi*f)^n)/((Y*j*2*pi*f)^n)

    Variables
    ---------
    Y: float = 1.0 (S)
    B: float = 1.0 (s^n)
    n: float = 0.5

```python
class WarburgShort(Element):
	kwargs
```

_Constructor parameters_

- `kwargs`




### **deareis.api.circuit.get_elements**

Returns a mapping of element symbols to the element class.

```python
def get_elements() -> Dict[str, Type[Element]]:
```


_Returns_

```python
Dict[str, Type[Element]]
```