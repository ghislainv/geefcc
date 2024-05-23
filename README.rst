..
   # ==============================================================================
   # author          :Ghislain Vieilledent
   # email           :ghislain.vieilledent@cirad.fr
   # web             :https://ecology.ghislainv.fr
   # license         :GPLv3
   # ==============================================================================

.. image:: https://ecology.ghislainv.fr/geefcc/_static/logo-geefcc.svg
   :align: right
   :target: https://ecology.ghislainv.fr/geefcc
   :alt: Logo geefcc
   :width: 140px
	   
``geefcc`` Python package
*************************


|Python version| |PyPI version| |GitHub Actions| |License| |Zenodo|


Overview
========

The ``geefcc`` Python package can be used to make forest cover change (fcc) maps from Google Earth Engine (GEE) and download them locally. Forest cover change maps are obtained from two global tree/forest cover change products: `Global Forest Change <https://glad.earthengine.app/view/global-forest-change>`_ or `Tropical Moist Forests <https://forobs.jrc.ec.europa.eu/TMF>`_. These two products are derived from the Landsat satellite image archive and provide tree/forest cover data at 30 m resolution.

.. image:: https://ecology.ghislainv.fr/geefcc/_static/banner_geefcc.png
   :align: center
   :target: https://ecology.ghislainv.fr/geefcc
   :alt: banner_geefcc

The ``geefcc`` package depends on the `xee <https://github.com/google/Xee>`_ Python package, which allows opening GEE datasets locally without exporting data to GEE assets or Google Drive. The user only has to specify an area of interest (aoi), either with an extent, a polygon vector file, or a country iso code (e.g. PER for Peru), and the years defining the time periods considered for the forest cover change (e.g. 2000, 2010, 2020). For the Global Forest Change product, the users also has to specify a tree cover threshold to define the forest (e.g. 75%).

.. note::
   The current version of the package uses GFC data up to year 2023 (`GFC v1.11 2023 <https://developers.google.com/earth-engine/datasets/catalog/UMD_hansen_global_forest_change_2023_v1_11>`_) and TMF data up to year 2022 (`TMF v1 2022 <https://forobs.jrc.ec.europa.eu/TMF/data>`_) so that years for computing forest cover change can be in the interval 2001--2024 for GFC (GFC does not provide loss for the year 2000) and 2000--2023 for TMF. Forest cover is given on the 1\ :sup:`st` of January for each year. The current version of the package only considers **deforestation as change** and **not forest gain or regrowth**.

Prerequisites
=============

Access to Google Earth Engine
-----------------------------

To use the ``geefcc`` Python package, you need a Google account and an `access to Earth Engine <https://developers.google.com/earth-engine/guides/access#a-role-in-a-cloud-project>`_ either via a Google Cloud project that's registered to use Earth Engine or via an individually signed-up account. Please follow this link `to register for Earth Engine <https://code.earthengine.google.com/register>`_.

You must always initialize GEE before using ``geefcc`` functions specifying a Google Cloud project name and `Earth Engine high-volume endpoint <https://developers.google.com/earth-engine/cloud/highvolume>`_:

.. code-block:: python

    ee.Initialize(
      credentials=credentials,
      project=project,
      opt_url="https://earthengine-highvolume.googleapis.com"
    )

GDAL
----

GDAL must be installed on your system.

To install GDAL on Windows, use the `OSGeo4W <https://trac.osgeo.org/osgeo4w/>`_ network installer. OSGeo4W is a binary distribution of a broad set of open source geospatial software for Windows environments (Windows 11 down to 7). Select *Express Install* and install GDAL. Several Gb of space will be needed on disk to install this programs. This will also install *OSGeo4W Shell* to execute command lines.

To install GDAL on other systems, use your package manager, for example ``apt`` for Debian/Ubuntu Linux distributions.

.. code:: shell

    sudo apt update
    sudo apt install gdal-bin libgdal-dev

After installing GDAL, you can test the installation by running ``gdalinfo --version`` in the command prompt or terminal, which should display the installed GDAL version.

GADM website
------------
    
The ``geefcc`` package downloads country administrative borders from the `GADM <https://gadm.org/data.html>`_ website. From time to time, their server is not responding. In case of problem with downloading country borders, check directly on the GADM website that data can be downloaded manually to be sure that the problem is coming from ``geefcc``.

Installation
============

The easiest way to install the ``geefcc`` Python package is via `pip <https://pip.pypa.io/en/stable/>`_ in the *OSGeo4W Shell* for Windows or in a virtual environment for Linux.

For Linux, create and activate a virtual environment before install ``geefcc`` with ``pip``:

.. code-block:: shell

   cd ~
   # Create a directory for virtual environments
   mkdir venvs
   # Create the virtual environment with venv
   python3 -m venv ~/venvs/venv-geefcc
   # Activate (start) the virtual environment
   source ~/venvs/venv-geefcc/bin/activate

Install Python dependencies and ``geefcc`` in the *OSGeo4W Shell* or in the newly created virtual environment:
   
.. code-block:: shell
   
   # Upgrade pip, setuptools, and wheel
   python3 -m pip install --upgrade pip setuptools wheel
   # Install numpy
   python3 -m numpy
   # Install gdal Python bindings (the correct version)
   python3 -m pip install gdal==$(gdal-config --version)
   # Install geefcc. This will install all other dependencies
   python3 -m pip install geefcc

If you want to install the development version of ``geefcc``, replace the last line with:

.. code-block:: shell

   python3 -m pip install https://github.com/ghislainv/geefcc/archive/master.zip

To deactivate and delete the virtual environment:

.. code-block:: shell
		
   deactivate
   rm -R ~/venvs/venv-geefcc # Just remove the repository

In case of problem while installing GDAL Python bindings, try the following command:

.. code-block:: shell
		
   python3 -m pip install  --no-cache-dir --force-reinstall gdal==$(gdal-config --version)
   
Contributing
============

The ``geefcc`` Python package is Open Source and released under
the `GNU GPL version 3 license
<https://ecology.ghislainv.fr/geefcc/license.html>`__. Anybody
who is interested can contribute to the package development following
our `Community guidelines
<https://ecology.ghislainv.fr/geefcc/contributing.html>`__. Every
contributor must agree to follow the project's `Code of conduct
<https://ecology.ghislainv.fr/geefcc/code_of_conduct.html>`__.
   
.. |Python version| image:: https://img.shields.io/pypi/pyversions/geefcc?logo=python&logoColor=ffd43b&color=306998
   :target: https://pypi.org/project/geefcc
   :alt: Python version

.. |PyPI version| image:: https://img.shields.io/pypi/v/geefcc
   :target: https://pypi.org/project/geefcc
   :alt: PyPI version

.. |GitHub Actions| image:: https://github.com/ghislainv/geefcc/workflows/PyPkg/badge.svg
   :target: https://github.com/ghislainv/geefcc/actions
   :alt: GitHub Actions
	 
.. |License| image:: https://img.shields.io/badge/licence-GPLv3-8f10cb.svg
   :target: https://www.gnu.org/licenses/gpl-3.0.html
   :alt: License GPLv3

.. |Zenodo| image:: https://zenodo.org/badge/DOI/10.5281/zenodo.11258039.svg
   :target: https://doi.org/10.5281/zenodo.11258039
   :alt: Zenodo

