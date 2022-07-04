DearEIS is a Python package that includes both a program with a graphical user interface (GUI) and an application programming interface (API) for working with impedance spectra.
The target audience is researchers who use electrochemical impedance spectroscopy (EIS) though the program may also be useful in educational settings.
The program includes features such as:

- [projects that can contain multiple experimental data sets](assets/images/example-projects.gif)
- reading experimental data from several different data formats
- [validation of impedance spectra by checking if the data is Kramers-Kronig transformable](assets/images/example-kramers-kronig.gif)
- [construction of equivalent circuits either by parsing a circuit definition code or by using the included graphical editor](assets/images/example-circuit-editor.gif)
- [equivalent circuit fitting](assets/images/example-fitting.gif)
- simulation of impedance spectra
- [composition of complex plots](assets/images/example-plotting.gif)


## Recent news

<ul>
  {% for post in site.posts limit:5 %}
    <li>
      <a href="{{ site.baseurl }}{{ post.url }}">{{ post.title }} ({{ post.date | date: "%Y-%m-%d" }})</a>
    </li>
  {% endfor %}
</ul>


## How to install

### Requirements

- [Python (version 3.7 or later)](https://www.python.org/)

### Supported platforms

- Linux
- Windows

DearEIS **may** also work on other platforms such as e.g. MacOS.


### Step-by-step

- Make sure to first install a recent version of Python if you do not already have it installed.
- DearEIS can then be installed with [pip](https://pip.pypa.io/en/stable/), which is the package installer for Python and should be included with most distributions of the official Python runtime.
	- **NOTE!** [An installer](https://github.com/vyrjana/DearEIS/releases/download/1.0.0/DearEIS-installer.exe) is available for Windows.
		The installer takes care of installing DearEIS for you using pip so the next step can be ignored.
		Additionally, the installer also creates a few shortcuts in the start menu.
- Execute the following command in a terminal (e.g. PowerShell on Windows) once Python has been installed:

```
pip install deareis
```


### Updating

Updating DearEIS is as simple as adding the `--upgrade` (or `-U`) argument to the command shown above:

```
pip install --upgrade deareis
```

**NOTE!** If DearEIS was installed on Windows using the installer, then there should be a shortcut in the start menu that will run the command.
Alternatively, the installer can be executed again.


## How to run

### Linux

DearEIS can be run by executing the `deareis` command in a terminal.
The command may also be available in application launchers (e.g. in the `run` mode in [rofi](https://github.com/davatorium/rofi)).


### Windows

If installed using the installer, then a shortcut to DearEIS should exist in the start menu.
Alternatively, the program can also be executed on via the start menu by searching for the `deareis` command.
**Note that the full name needs to be typed in for the command to be found!**


## API documentation

Documentation about the API can be found on the [GitHub wiki](https://github.com/vyrjana/DearEIS/wiki).
Check [this Jupyter notebook](https://github.com/vyrjana/DearEIS/blob/main/examples/examples.ipynb) for examples of how to use the DearEIS API, which is based on [pyimpspec](https://github.com/vyrjana/pyimpspec).
Check [this other Jupyter notebook](https://github.com/vyrjana/pyimpspec/blob/main/examples/examples.ipynb) for examples of how to use the pyimpspec API.


## Support

Bug reports, feature requests, and requests for help can be posted on [GitHub](https://github.com/vyrjana/DearEIS/issues).

`deareis-debug` is an alternative command that can be executed and prints debugging messages to the terminal, which can be useful when troubleshooting issues.


## Contributing

If you wish to help make DearEIS even better, then please head on over to the [GitHub repository](https://github.com/vyrjana/DearEIS) for more information in the README.md file.


## License

DearEIS is licensed under the [GPLv3 or later](https://www.gnu.org/licenses/gpl-3.0.html).

The licenses of DearEIS' dependencies and/or sources of portions of code are included in the [LICENSES folder on GitHub](https://github.com/vyrjana/DearEIS/tree/main/LICENSES).
