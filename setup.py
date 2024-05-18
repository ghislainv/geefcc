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
def find_version():
    """Finding package version."""
    with open("pyfcc/__init__.py", encoding="utf-8") as init_file:
        init_text = init_file.read()
    far_version = (re.search('^__version__\\s*=\\s*"(.*)"',
                             init_text, re.M)
                   .group(1))
    return far_version


version = find_version()

# reStructuredText README file
with io.open("README.rst", encoding="utf-8") as f:
    long_description = f.read()

# Project URLs
project_urls = {
    "Documentation": "https://ecology.ghislainv.fr/pyfcc",
    "Source": "https://github.com/ghislainv/pyfcc/",
    "Traker": "https://github.com/ghislainv/pyfcc/issues",
}

# Setup
setup(name="pyfcc",
      version=version,
      author="Ghislain Vieilledent",
      author_email="ghislain.vieilledent@cirad.fr",
      url="https://ecology.ghislainv.fr/pyfcc",
      project_urls=project_urls,
      license="GPLv3",
      description="Easy access to world's protected areas",
      long_description=long_description,
      long_description_content_type="text/x-rst",
      classifiers=["Development Status :: 4 - Beta",
                   "License :: OSI Approved :: GNU General Public License v3 "
                   "(GPLv3)",
                   "Programming Language :: Python :: 3",
                   "Operating System :: OS Independent",
                   "Topic :: Scientific/Engineering :: Bio-Informatics"],
      keywords="deforestation tropical forests forest cover change",
      python_requires=">=3.6",
      packages=["pyfcc"],
      package_dir={"pyfcc": "pyfcc"},
      entry_points={"console_scripts": ["pyfcc = pyfcc.pyfcc:main"]},
      install_requires=["numpy", "gdal", "xarray", "xee"],
      extras_require={
          "interactive": ["jupyter", "geopandas",
                          "descartes", "folium"]},
      zip_safe=False)

# End
