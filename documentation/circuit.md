---
layout: documentation
title: API - Circuit
permalink: /api/circuit/
---


**Table of Contents**

- [deareis.api.circuit](#deareisapicircuit)
	- [Circuit](#deareisapicircuitcircuit)
		- [get_element](#deareisapicircuitcircuitget_element)
		- [get_elements](#deareisapicircuitcircuitget_elements)
		- [get_label](#deareisapicircuitcircuitget_label)
		- [get_parameters](#deareisapicircuitcircuitget_parameters)
		- [impedance](#deareisapicircuitcircuitimpedance)
		- [impedances](#deareisapicircuitcircuitimpedances)
		- [set_label](#deareisapicircuitcircuitset_label)
		- [set_parameters](#deareisapicircuitcircuitset_parameters)
		- [to_circuitikz](#deareisapicircuitcircuitto_circuitikz)
		- [to_latex](#deareisapicircuitcircuitto_latex)
		- [to_stack](#deareisapicircuitcircuitto_stack)
		- [to_string](#deareisapicircuitcircuitto_string)
		- [to_sympy](#deareisapicircuitcircuitto_sympy)
	- [Connection](#deareisapicircuitconnection)
		- [contains](#deareisapicircuitconnectioncontains)
		- [get_element](#deareisapicircuitconnectionget_element)
		- [get_elements](#deareisapicircuitconnectionget_elements)
		- [get_label](#deareisapicircuitconnectionget_label)
		- [get_parameters](#deareisapicircuitconnectionget_parameters)
		- [impedance](#deareisapicircuitconnectionimpedance)
		- [impedances](#deareisapicircuitconnectionimpedances)
		- [set_parameters](#deareisapicircuitconnectionset_parameters)
		- [to_latex](#deareisapicircuitconnectionto_latex)
		- [to_stack](#deareisapicircuitconnectionto_stack)
		- [to_string](#deareisapicircuitconnectionto_string)
		- [to_sympy](#deareisapicircuitconnectionto_sympy)
	- [Parallel](#deareisapicircuitparallel)
	- [ParsingError](#deareisapicircuitparsingerror)
	- [Series](#deareisapicircuitseries)
	- [UnexpectedCharacter](#deareisapicircuitunexpectedcharacter)
	- [string_to_circuit](#deareisapicircuitstring_to_circuit)



## **deareis.api.circuit**

### **deareis.api.circuit.Circuit**

A class that represents an equivalent circuit.

```python
class Circuit(object):
	elements: Series
	label: str = ""
```

_Constructor parameters_

- `elements`: The elements of the circuit wrapped in a Series connection.
- `label`: The label assigned to the circuit.


_Functions and methods_

#### **deareis.api.circuit.Circuit.get_element**

Get the circuit element with a given integer identifier.

```python
def get_element(self, ident: int) -> Optional[Element]:
```


_Parameters_

- `ident`: The integer identifier corresponding to an element in the circuit.


_Returns_
```python
Optional[Element]
```

#### **deareis.api.circuit.Circuit.get_elements**

Get the elements in this circuit.

```python
def get_elements(self, flattened: bool = True) -> List[Union[Element, Connection]]:
```


_Parameters_

- `flattened`: Whether or not the elements should be returned as a list of only elements or as a list of elements and connections.


_Returns_
```python
List[Union[Element, Connection]]
```

#### **deareis.api.circuit.Circuit.get_label**

Get the label assigned to this circuit.

```python
def get_label(self) -> str:
```


_Returns_
```python
str
```

#### **deareis.api.circuit.Circuit.get_parameters**

Get a mapping of each circuit element's integer identifier to an OrderedDict representing that element's parameters.

```python
def get_parameters(self) -> Dict[int, OrderedDict[str, float]]:
```


_Returns_
```python
Dict[int, OrderedDict[str, float]]
```

#### **deareis.api.circuit.Circuit.impedance**

Calculate the impedance of this circuit at a single frequency.

```python
def impedance(self, f: float) -> complex:
```


_Parameters_

- `f`: The frequency in hertz.


_Returns_
```python
complex
```

#### **deareis.api.circuit.Circuit.impedances**

Calculate the impedance of this circuit at multiple frequencies.

```python
def impedances(self, f: Union[list, ndarray]) -> ndarray:
```


_Parameters_

- `f`


_Returns_
```python
ndarray
```

#### **deareis.api.circuit.Circuit.set_label**

Set the label assigned to this circuit.

```python
def set_label(self, label: str):
```


_Parameters_

- `label`: The new label.

#### **deareis.api.circuit.Circuit.set_parameters**

Assign new parameters to the circuit elements.

```python
def set_parameters(self, parameters: Dict[int, Dict[str, float]]):
```


_Parameters_

- `parameters`: A mapping of circuit element integer identifiers to an OrderedDict mapping the parameter symbol to the new value.

#### **deareis.api.circuit.Circuit.to_circuitikz**

Get the LaTeX source needed to draw a circuit diagram for this circuit using the circuitikz package.

```python
def to_circuitikz(self, node_width: float = 3.0, node_height: float = 1.5, working_label: str = "WE+WS", counter_label: str = "CE+RE", hide_labels: bool = False) -> str:
```


_Parameters_

- `node_width`: The width of each node.
- `node_height`: The height of each node.
- `working_label`: The label assigned to the terminal representing the working and working sense electrodes.
- `counter_label`: The label assigned to the terminal representing the counter and reference electrodes.
- `hide_labels`: Whether or not to hide element and terminal labels.


_Returns_
```python
str
```

#### **deareis.api.circuit.Circuit.to_latex**

Get the LaTeX math expression corresponding to this circuit's impedance.

```python
def to_latex(self) -> str:
```


_Returns_
```python
str
```

#### **deareis.api.circuit.Circuit.to_stack**


```python
def to_stack(self) -> List[Tuple[str, Union[Element, Connection]]]:
```


_Returns_
```python
List[Tuple[str, Union[Element, Connection]]]
```

#### **deareis.api.circuit.Circuit.to_string**

Generate the circuit description code (CDC) that represents this circuit.

```python
def to_string(self, decimals: int = -1) -> str:
```


_Parameters_

- `decimals`: The number of decimals to include for the current element parameter values and limits.
-1 means that the CDC is generated using the basic syntax, which omits element labels, parameter values, and parameter limits.


_Returns_
```python
str
```

#### **deareis.api.circuit.Circuit.to_sympy**

Get the SymPy expression corresponding to this circuit's impedance.

```python
def to_sympy(self, substitute: bool = False) -> Expr:
```


_Parameters_

- `substitute`: Whether or not the variables should be substituted with the current values.


_Returns_
```python
Expr
```




### **deareis.api.circuit.Connection**

```python
class Connection(object):
	elements: List[Union[Element, Connection]]
```

_Constructor parameters_

- `elements`


_Functions and methods_

#### **deareis.api.circuit.Connection.contains**

Check if this connection contains a specific Element or Connection instance.

```python
def contains(self, element: Union[Element, Connection], top_level: bool = False) -> bool:
```


_Parameters_

- `element`: The Element or Connection instance to check for.
- `top_level`: Whether to only check in the current Connection instance instead of also checking in any nested Connection instances.


_Returns_
```python
bool
```

#### **deareis.api.circuit.Connection.get_element**

Get a specific element based on its unique identifier.

```python
def get_element(self, ident: int) -> Optional[Element]:
```


_Parameters_

- `ident`: The integer identifier that should be unique in the context of the circuit.


_Returns_
```python
Optional[Element]
```

#### **deareis.api.circuit.Connection.get_elements**

Get a list of elements and connections nested inside this connection.

```python
def get_elements(self, flattened: bool = True) -> List[Union[Element, Connection]]:
```


_Parameters_

- `flattened`: Whether the returned list should only contain elements or a combination of elements and connections.


_Returns_
```python
List[Union[Element, Connection]]
```

#### **deareis.api.circuit.Connection.get_label**


```python
def get_label(self) -> str:
```


_Returns_
```python
str
```

#### **deareis.api.circuit.Connection.get_parameters**

Get the current element parameters of all elements nested inside this connection.
The outer key is the unique identifier assigned to an element.
The inner key is the symbol corresponding to an element parameter.

```python
def get_parameters(self) -> Dict[int, OrderedDict[str, float]]:
```


_Returns_
```python
Dict[int, OrderedDict[str, float]]
```

#### **deareis.api.circuit.Connection.impedance**

Calculates the impedance of the connection at a single frequency.

```python
def impedance(self, f: float) -> complex:
```


_Parameters_

- `f`: Frequency in Hz


_Returns_
```python
complex
```

#### **deareis.api.circuit.Connection.impedances**

Calculates the impedance of the element at multiple frequencies.

```python
def impedances(self, freq: Union[list, ndarray]) -> ndarray:
```


_Parameters_

- `freq`: Frequencies in Hz


_Returns_
```python
ndarray
```

#### **deareis.api.circuit.Connection.set_parameters**

Set new element parameters to some/all elements nested inside this connection.

```python
def set_parameters(self, parameters: Dict[int, Dict[str, float]]):
```


_Parameters_

- `parameters`: The outer key is the unique identifier assigned to an element.
The inner key is the symbol corresponding to an element parameter.

#### **deareis.api.circuit.Connection.to_latex**


```python
def to_latex(self) -> str:
```


_Returns_
```python
str
```

#### **deareis.api.circuit.Connection.to_stack**


```python
def to_stack(self, stack: List[Tuple[str, Union[Element, Connection]]]):
```


_Parameters_

- `stack`

#### **deareis.api.circuit.Connection.to_string**


```python
def to_string(self, decimals: int = -1) -> str:
```


_Parameters_

- `decimals`


_Returns_
```python
str
```

#### **deareis.api.circuit.Connection.to_sympy**


```python
def to_sympy(self, substitute: bool = False) -> Expr:
```


_Parameters_

- `substitute`


_Returns_
```python
Expr
```




### **deareis.api.circuit.Parallel**

Elements connected in parallel.

```python
class Parallel(Connection):
	elements: List[Union[Element, Connection]]
```

_Constructor parameters_

- `elements`: List of elements (and connections) that are connected in parallel.




### **deareis.api.circuit.ParsingError**

```python
class ParsingError(Exception):
	msg: str
```

_Constructor parameters_

- `msg`




### **deareis.api.circuit.Series**

Elements connected in series.

```python
class Series(Connection):
	elements: List[Union[Element, Connection]]
```

_Constructor parameters_

- `elements`: List of elements (and connections) that are connected in series.




### **deareis.api.circuit.UnexpectedCharacter**

```python
class UnexpectedCharacter(Exception):
	args
	kwargs
```

_Constructor parameters_

- `args`
- `kwargs`




### **deareis.api.circuit.string_to_circuit**

Generate a Circuit instance from a string that contains a circuit description code (CDC).

```python
def string_to_circuit(cdc: str) -> Circuit:
```


_Parameters_

- `cdc`: A circuit description code (CDC) corresponding to an equivalent circuit.


_Returns_

```python
Circuit
```