# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
import datetime
import re  # Regular expression
sys.path.insert(0, os.path.abspath('..'))


# -- Project information -----------------------------------------------------

project = "geefcc"
_today = datetime.date.today()
year = _today.year
copyright = f"{year}, Cirad"

# The full version, including alpha/beta/rc tags
with open("../geefcc/__init__.py", encoding="utf-8") as init_file:
    init_text = init_file.read()
author = re.search('^__author__\\s*=\\s*"(.*)"', init_text, re.M).group(1)
version = re.search('^__version__\\s*=\\s*"(.*)"', init_text, re.M).group(1)
release = version

# -- Sphynx options ----------------------------------------------------------
add_module_names = False
add_function_parentheses = True

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ["sphinx.ext.autodoc", "sphinx.ext.viewcode",
              "sphinx.ext.mathjax"]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "alabaster"  # 'sphinx_rtd_theme'

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
html_theme_options = {
    'description': "Forest cover change from Google Earth Engine",
    'code_font_family': "'Roboto Mono', 'Consolas', 'Menlo', "
                        "'Deja Vu Sans Mono', "
                        "'Bitstream Vera Sans Mono', monospace",
    'font_family': "'Lato', Arial, sans-serif",
    'head_font_family': "'Lato', Arial, sans-serif",
    'body_text': '#000',
    'sidebar_header': '#4B4032',
    'sidebar_text': '#49443E',
    'github_banner': 'false',
    'github_user': 'ghislainv',
    'github_repo': 'geefcc',
    'github_button': 'true',
    'github_type': 'star',
    'travis_button': 'false',
    'codecov_button': 'false',
    'logo': 'logo-geefcc.svg',
    'logo_name': 'true',
    'page_width': '1300px',
    'body_max_width': 'auto',
    'fixed_sidebar': 'true'
}

html_favicon = "_static/favicon.ico"
html_title = "geefcc — Forest cover change from Google Earth Engine"
html_short_title = "geefcc"
html_base_url = "https://ecology.ghislainv.fr/geefcc/"


# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# End of file
