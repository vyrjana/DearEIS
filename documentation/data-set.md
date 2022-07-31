---
layout: documentation
title: API - data set
permalink: /api/data-set/
---

The `DataSet` class in the DearEIS API differs slightly from the base class found in the pyimpspec API.
The `parse_data` function is a wrapper for the corresponding function in pyimpspec's API with the only difference being that the returned `DataSet` instances are the variant used by DearEIS.
            

**Table of Contents**

- [deareis.api.data](#deareis-api-data)
	- [DataSet](#deareis-api-datadataset)
		- [average](#deareis-api-datadatasetaverage)
		- [copy](#deareis-api-datadatasetcopy)
		- [from_dict](#deareis-api-datadatasetfrom_dict)
		- [get_bode_data](#deareis-api-datadatasetget_bode_data)
		- [get_frequency](#deareis-api-datadatasetget_frequency)
		- [get_imaginary](#deareis-api-datadatasetget_imaginary)
		- [get_impedance](#deareis-api-datadatasetget_impedance)
		- [get_label](#deareis-api-datadatasetget_label)
		- [get_magnitude](#deareis-api-datadatasetget_magnitude)
		- [get_mask](#deareis-api-datadatasetget_mask)
		- [get_num_points](#deareis-api-datadatasetget_num_points)
		- [get_nyquist_data](#deareis-api-datadatasetget_nyquist_data)
		- [get_path](#deareis-api-datadatasetget_path)
		- [get_phase](#deareis-api-datadatasetget_phase)
		- [get_real](#deareis-api-datadatasetget_real)
		- [set_label](#deareis-api-datadatasetset_label)
		- [set_mask](#deareis-api-datadatasetset_mask)
		- [set_path](#deareis-api-datadatasetset_path)
		- [subtract_impedance](#deareis-api-datadatasetsubtract_impedance)
		- [to_dataframe](#deareis-api-datadatasetto_dataframe)
		- [to_dict](#deareis-api-datadatasetto_dict)
	- [UnsupportedFileFormat](#deareis-api-dataunsupportedfileformat)
	- [parse_data](#deareis-api-dataparse_data)



## **deareis.api.data**

### **deareis.api.data.DataSet**

Extends `pyimpspec.DataSet` to implement data minimization when writing to disk and to recreate the data when loading from disk.
Equality checks between DataSet instances is also modified.

```python
class DataSet(DataSet):
	frequency: ndarray
	impedance: ndarray
	mask: Dict[int, bool] = {}
	path: str = ""
	label: str = ""
	uuid: str = ""
```

_Constructor parameters_

- `frequency`: A 1-dimensional array of frequencies in hertz.
- `impedance`: A 1-dimensional array of complex impedances in ohms.
- `mask`: A mapping of integer indices to boolean values where a value of True means that the data point is to be omitted.
- `path`: The path to the file that has been parsed to generate this DataSet instance.
- `label`: The label assigned to this DataSet instance.
- `uuid`: The universivally unique identifier assigned to this DataSet instance.
If empty, then one will be automatically assigned.


_Functions and methods_

#### **deareis.api.data.DataSet.average**

Create a DataSet by averaging the impedances of multiple DataSet instances.

```python
def average(data_sets: List[DataSet], label: str = "Average") -> DataSet:
```


_Parameters_

- `data_sets`: The DataSet instances to average.
- `label`: The label that the new DataSet should have.


_Returns_
```python
DataSet
```

#### **deareis.api.data.DataSet.copy**

Create a copy of an existing DataSet.

```python
def copy(data: DataSet, label: Optional[str] = None) -> DataSet:
```


_Parameters_

- `data`: The existing DataSet to make a copy of.
- `label`: The label that the copy should have.


_Returns_
```python
DataSet
```

#### **deareis.api.data.DataSet.from_dict**

Return a DataSet instance that has been created based off of a dictionary.

```python
def from_dict(dictionary: dict) -> DataSet:
```


_Parameters_

- `dictionary`: Create an instance from a dictionary.


_Returns_
```python
DataSet
```

#### **deareis.api.data.DataSet.get_bode_data**

Get the data necessary to plot this DataSet as a Bode plot: the base-10 logarithms of the frequencies, the base-10 logarithms of the absolute magnitudes of the impedances, and the negative phase angles/shifts of the impedances in degrees.

```python
def get_bode_data(self, masked: Optional[bool] = False) -> Tuple[ndarray, ndarray, ndarray]:
```


_Parameters_

- `masked`: None means that all impedances are returned.
True means that only impedances that are to be omitted are returned.
False means that only impedances that are to be included are returned.


_Returns_
```python
Tuple[ndarray, ndarray, ndarray]
```

#### **deareis.api.data.DataSet.get_frequency**

Get the frequencies in this DataSet.

```python
def get_frequency(self, masked: Optional[bool] = False) -> ndarray:
```


_Parameters_

- `masked`: None means that all frequencies are returned.
True means that only frequencies that are to be omitted are returned.
False means that only frequencies that are to be included are returned.


_Returns_
```python
ndarray
```

#### **deareis.api.data.DataSet.get_imaginary**

Get the imaginary parts of the impedances in this DataSet.

```python
def get_imaginary(self, masked: Optional[bool] = False) -> ndarray:
```


_Parameters_

- `masked`: None means that all impedances are returned.
True means that only impedances that are to be omitted are returned.
False means that only impedances that are to be included are returned.


_Returns_
```python
ndarray
```

#### **deareis.api.data.DataSet.get_impedance**

Get the complex impedances in this DataSet.

```python
def get_impedance(self, masked: Optional[bool] = False) -> ndarray:
```


_Parameters_

- `masked`: None means that all impedances are returned.
True means that only impedances that are to be omitted are returned.
False means that only impedances that are to be included are returned.


_Returns_
```python
ndarray
```

#### **deareis.api.data.DataSet.get_label**

Get the label assigned to this DataSet.

```python
def get_label(self) -> str:
```


_Returns_
```python
str
```

#### **deareis.api.data.DataSet.get_magnitude**

Get the absolute magnitudes of the impedances in this DataSet.

```python
def get_magnitude(self, masked: Optional[bool] = False) -> ndarray:
```


_Parameters_

- `masked`: None means that all impedances are returned.
True means that only impedances that are to be omitted are returned.
False means that only impedances that are to be included are returned.


_Returns_
```python
ndarray
```

#### **deareis.api.data.DataSet.get_mask**

Get the mask for this DataSet.
The keys are zero-based indices and the values are booleans.
True means that the data point is to be omitted and False means that the data point is to be included.

```python
def get_mask(self) -> Dict[int, bool]:
```


_Returns_
```python
Dict[int, bool]
```

#### **deareis.api.data.DataSet.get_num_points**

Get the number of data points in this DataSet

```python
def get_num_points(self, masked: Optional[bool] = False) -> int:
```


_Parameters_

- `masked`: None means that all impedances are returned.
True means that only impedances that are to be omitted are returned.
False means that only impedances that are to be included are returned.


_Returns_
```python
int
```

#### **deareis.api.data.DataSet.get_nyquist_data**

Get the data necessary to plot this DataSet as a Nyquist plot: the real and the negative imaginary parts of the impedances.

```python
def get_nyquist_data(self, masked: Optional[bool] = False) -> Tuple[ndarray, ndarray]:
```


_Parameters_

- `masked`: None means that all impedances are returned.
True means that only impedances that are to be omitted are returned.
False means that only impedances that are to be included are returned.


_Returns_
```python
Tuple[ndarray, ndarray]
```

#### **deareis.api.data.DataSet.get_path**

Get the path to the file that was parsed to generate this DataSet.

```python
def get_path(self) -> str:
```


_Returns_
```python
str
```

#### **deareis.api.data.DataSet.get_phase**

Get the phase angles/shifts of the impedances in this DataSet in degrees.

```python
def get_phase(self, masked: Optional[bool] = False) -> ndarray:
```


_Parameters_

- `masked`: None means that all impedances are returned.
True means that only impedances that are to be omitted are returned.
False means that only impedances that are to be included are returned.


_Returns_
```python
ndarray
```

#### **deareis.api.data.DataSet.get_real**

Get the real parts of the impedances in this DataSet.

```python
def get_real(self, masked: Optional[bool] = False) -> ndarray:
```


_Parameters_

- `masked`: None means that all impedances are returned.
True means that only impedances that are to be omitted are returned.
False means that only impedances that are to be included are returned.


_Returns_
```python
ndarray
```

#### **deareis.api.data.DataSet.set_label**

Set the label assigned to this DataSet.

```python
def set_label(self, label: str):
```


_Parameters_

- `label`: The new label.

#### **deareis.api.data.DataSet.set_mask**

Set the mask for this DataSet.

```python
def set_mask(self, mask: Dict[int, bool]):
```


_Parameters_

- `mask`: The new mask.
The keys must be zero-based indices and the values must be boolean values.
True means that the data point is to be omitted and False means that the data point is to be included.

#### **deareis.api.data.DataSet.set_path**

Set the path to the file that was parsed to generate this DataSet.

```python
def set_path(self, path: str):
```


_Parameters_

- `path`: The path.

#### **deareis.api.data.DataSet.subtract_impedance**

Subtract either the same complex value from all data points or a unique complex value for each data point in this DataSet.

```python
def subtract_impedance(self, Z: Union[complex, List[complex], ndarray]):
```


_Parameters_

- `Z`: The complex value(s) to subtract from this DataSet's impedances.

#### **deareis.api.data.DataSet.to_dataframe**

Create a pandas.DataFrame instance from this DataSet.

```python
def to_dataframe(self, masked: Optional[bool] = False, frequency_label: str = "f (Hz)", real_label: Optional[str] = "Zre (ohm)", imaginary_label: Optional[str] = "Zim (ohm)", magnitude_label: Optional[str] = "|Z| (ohm)", phase_label: Optional[str] = "phase angle (deg.)", negative_imaginary: bool = False, negative_phase: bool = False) -> DataFrame:
```


_Parameters_

- `masked`: None means that all impedances are returned.
True means that only impedances that are to be omitted are returned.
False means that only impedances that are to be included are returned.
- `frequency_label`: The label assigned to the frequency data.
- `real_label`: The label assigned to the real part of the impedance data.
- `imaginary_label`: The label assigned to the imaginary part of the impedance data.
- `magnitude_label`: The label assigned to the magnitude of the impedance data.
- `phase_label`: The label assigned to the phase of the imedance data.
- `negative_imaginary`: Whether or not the sign of the imaginary part of the impedance data should be inverted.
- `negative_phase`: Whether or not the sign of the phase of the impedance data should be inverted.


_Returns_
```python
DataFrame
```

#### **deareis.api.data.DataSet.to_dict**

Return a dictionary that can be used to recreate this data set.

```python
def to_dict(self, session: bool = True) -> dict:
```


_Parameters_

- `session`: If true, then no data minimization is performed.


_Returns_
```python
dict
```




### **deareis.api.data.UnsupportedFileFormat**

```python
class UnsupportedFileFormat(Exception):
	args
	kwargs
```

_Constructor parameters_

- `args`
- `kwargs`




### **deareis.api.data.parse_data**

Wrapper for `pyimpspec.parse_data`.


    Parse experimental data and return a list of DataSet instances.
    One or more specific sheets can be specified by name when parsing spreadsheets (e.g., .xlsx or .ods) to only return DataSet instances for those sheets.
    If no sheets are specified, then all sheets will be processed and the data from successfully parsed sheets will be returned as DataSet instances.

```python
def parse_data(path: str, file_format: Optional[str] = None, kwargs) -> List[DataSet]:
```


_Parameters_

- `path`: The path to a file containing experimental data that is to be parsed.
- `file_format`: The file format (or extension) that should be assumed when parsing the data.
If no file format is specified, then the file format will be determined based on the file extension.
If there is no file extension, then attempts will be made to parse the file as if it was one of the supported file formats.
- `kwargs`: Keyword arguments are passed to the parser.


_Returns_

```python
List[DataSet]
```