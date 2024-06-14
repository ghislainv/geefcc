#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Installation setup."""

# ================================================================
# author          :Ghislain Vieilledent
# email           :ghislain.vieilledent@cirad.fr
# web             :https://ecology.ghislainv.fr
# python_version  :>=3.6
# license         :GPLv3
# ================================================================

# Import
import io
import re  # Regular expression
from setuptools import setup


# find_version
def find_version(pkg_name):
    """Finding package version."""
    with open(f"{pkg_name}/__init__.py", encoding="utf-8") as init_file:
        init_text = init_file.read()
    _version = (re.search('^__version__\\s*=\\s*"(.*)"',
                          init_text, re.M)
                .group(1))
    return _version


version = find_version("geefcc")

# reStructuredText README file
with io.open("README.rst", encoding="utf-8") as f:
    long_description = f.read()

# Project URLs
project_urls = {
    "Documentation": "https://ecology.ghislainv.fr/geefcc",
    "Source": "https://github.com/ghislainv/geefcc/",
    "Traker": "https://github.com/ghislainv/geefcc/issues",
}

# Setup
setup(name="geefcc",
      version=version,
      author="Ghislain Vieilledent",
      author_email="ghislain.vieilledent@cirad.fr",
      url="https://ecology.ghislainv.fr/geefcc",
      project_urls=project_urls,
      license="GPLv3",
      description="Forest cover change from Google Earth Engine",
      long_description=long_description,
      long_description_content_type="text/x-rst",
      classifiers=["Development Status :: 4 - Beta",
                   "License :: OSI Approved :: GNU General Public License v3 "
                   "(GPLv3)",
                   "Programming Language :: Python :: 3",
                   "Operating System :: OS Independent",
                   "Topic :: Scientific/Engineering :: Bio-Informatics"],
      keywords=("deforestation tropical forests forest "
                "cover change map google earth engine"),
      python_requires=">=3.6",
      packages=["geefcc", "geefcc/misc"],
      package_dir={"geefcc": "geefcc", "misc": "geefcc/misc"},
      entry_points={"console_scripts": ["geefcc = geefcc.geefcc:main"]},
      install_requires=["numpy", "gdal", "xarray", "xee", "multiprocess"],
      extras_require={
          "interactive": ["cartopy", "rioxarray",
                          "matplotlib", "geopandas"]},
      zip_safe=False)

# End
