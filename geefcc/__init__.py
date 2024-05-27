"""
geefcc: Forest cover change from Google Earth Engine.
https://ecology.ghislainv.fr/geefcc/
"""

# Define double undescore variables
# https://peps.python.org/pep-0008/#module-level-dunder-names
__author__ = "Ghislain Vieilledent and Thomas Arsouze"
__email__ = "ghislain.vieilledent@cirad.fr, thomas.arsouze@cirad.fr"
__version__ = "0.1"

# GDAL exceptions
from osgeo import gdal

from .ee_initialize import ee_initialize
from .get_fcc import get_fcc
from .sum_raster_bands import sum_raster_bands

# GDAL exceptions
gdal.UseExceptions()

# End
