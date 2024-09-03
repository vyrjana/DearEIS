from os.path import abspath, dirname, exists, join
from inspect import getmodule

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "DearEIS"
copyright = "2024, DearEIS developers"
author = "DearEIS developers"
release = "X.Y.Z"
version_path = join(dirname(dirname(dirname(abspath(__file__)))), "version.txt")
if exists(version_path):
    with open(version_path, "r") as fp:
        release = fp.read().strip()

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.doctest",
    "sphinx.ext.napoleon",
    "sphinx.ext.autodoc",
    "sphinx.ext.mathjax",
    "matplotlib.sphinxext.plot_directive",
]

numfig = True
templates_path = ["_templates"]
exclude_patterns = []

autodoc_typehints = "description"
autodoc_typehints_format = "short"

plot_formats = ["svg", "pdf"]
plot_html_show_formats = False
plot_rcparams = {"savefig.transparent": True}


def autodoc_skip_member_handler(app, what, name, obj, skip, options):
    module_string = str(getmodule(obj))
    conditions = [
        skip,
        name.startswith("_"),
        "deareis" not in module_string and "pyimpspec" not in module_string,
    ]
    to_skip = any(conditions)
    # print(to_skip, name, module_string, skip)
    return to_skip


def autodoc_process_docstring(app, what, name, obj, options, lines):
    replacements = {
        "|DataFrame|": "`pandas.DataFrame <https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html#pandas.DataFrame>`_",
        "|Drawing|": "`schemdraw.Drawing <https://schemdraw.readthedocs.io/en/latest/classes/drawing.html#schemdraw.Drawing>`_",
        "|Expr|": "`sympy.Expr <https://docs.sympy.org/latest/modules/core.html#sympy.core.expr.Expr>`_",
        "|MinimizerResult|": "`lmfit.MinimizerResult <https://lmfit.github.io/lmfit-py/fitting.html#lmfit.minimizer.MinimizerResult>`_",
        "|Figure|": "`matplotlib.Figure <https://matplotlib.org/stable/api/figure_api.html#matplotlib.figure.Figure>`_",
        "|Axes|": "`matplotlib.Axes <https://matplotlib.org/stable/api/axes_api.html#the-axes-class>`_",
    }
    for i, line in enumerate(lines):
        for key, value in replacements.items():
            if key in line:
                line = line.replace(key, value)
        lines[i] = line


def setup(app):
    app.connect("autodoc-skip-member", autodoc_skip_member_handler)
    app.connect("autodoc-process-docstring", autodoc_process_docstring)


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
