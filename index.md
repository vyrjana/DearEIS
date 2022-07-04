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
      <a href="{{ site.baseurl }}{{ post.url }}">{{ post.title }}</a>
    </li>
  {% endfor %}
</ul>


## How to install

DearEIS has been tested on Linux and Windows but may also work on MacOS.

The easiest way to install DearEIS is to do it with [pip](https://pip.pypa.io/en/stable/), which is the package installer for [Python](https://www.python.org/) and should be included with most distributions of the official Python runtime.

Make sure that you have installed a recent version of Python and then execute the following command in a terminal (e.g. PowerShell on Windows):

```
pip install deareis
```

Updating DearEIS is then as simple as adding the `--upgrade` (or `-U`) argument:

```
pip install --upgrade deareis
```


## How to run

DearEIS can be run by executing `deareis` in a terminal.
Alternatively, on Windows the program can also be executed by searching for `deareis` in the start menu.
**Note that the full name needs to be typed in for this to work!**
On Linux `deareis` should similarly be available in application launchers (e.g. in the `run` mode in [rofi](https://github.com/davatorium/rofi)).


## API documentation

Documentation about the API can be found on the [GitHub wiki](https://github.com/vyrjana/DearEIS/wiki).


## Support

Bug reports, feature requests, and requests for help can be posted on [GitHub](https://github.com/vyrjana/DearEIS/issues).

`deareis-debug` is an alternative command that can be executed and prints debugging messages to the terminal, which can be useful when troubleshooting issues.


## Contributing

If you wish to help make DearEIS better, then please see the [GitHub repository](https://github.com/vyrjana/DearEIS) for more information.


## License

DearEIS is licensed under the [GPLv3 or later](https://www.gnu.org/licenses/gpl-3.0.html).

The licenses of DearEIS' dependencies and/or sources of portions of code are included in the [LICENSES folder on GitHub](https://github.com/vyrjana/DearEIS/tree/main/LICENSES).
