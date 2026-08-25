"""
geefcc: Forest cover change from Google Earth Engine.
https://ecology.ghislainv.fr/geefcc/
"""

# Standard library imports
import logging
import warnings
from typing import TYPE_CHECKING

# Module-level dunder names
# https://peps.python.org/pep-0008/#module-level-dunder-names
__author__ = "Ghislain Vieilledent and Thomas Arsouze"
__email__ = "ghislain.vieilledent@cirad.fr, thomas.arsouze@cirad.fr"
__version__ = "0.2.2"
__license__ = "GPL-3.0"
__all__ = [
    "ee_initialize",
    "get_fcc_loss_gain",
    "get_fcc_loss",
    "get_fcc",
    "plot_fcc_loss_gain",
    "plot_fcc_loss",
    "stat_fcc_loss_gain",
    "stat_fcc_loss",
    "sum_raster_bands",
    "make_dir",
]

# Third-party imports
from osgeo import gdal

# Local imports
from ._download.ee_initialize import ee_initialize
from .get_fcc_loss_gain import get_fcc_loss_gain
from .get_fcc_loss import get_fcc_loss
from .plot import plot_fcc_loss_gain, plot_fcc_loss
from .stat import stat_fcc_loss_gain, stat_fcc_loss
from .sum_raster_bands import sum_raster_bands
from .misc import make_dir

# ------------------------------------
# GDAL configuration
# ------------------------------------
gdal.PushErrorHandler("CPLQuietErrorHandler")
gdal.UseExceptions()

# ------------------------------------
# Logging configuration
# ------------------------------------
logging.getLogger(__name__).addHandler(logging.NullHandler())

# ------------------------------------
# Alias
# ------------------------------------

if TYPE_CHECKING:
    get_fcc = get_fcc_loss

else:
    def get_fcc(*args, **kwargs):
        """
        .. deprecated:: 0.1.8
           Use :func:`get_fcc_loss` instead. This alias will be removed
        in a future release.
        """
        warnings.warn(
            "The alias 'get_fcc' is deprecated and will "
            "be removed in a future version. "
            "Please use 'get_fcc_loss' instead.",
            category=DeprecationWarning,
            stacklevel=2
        )
        return get_fcc_loss(*args, **kwargs)

    get_fcc.__name__ = "get_fcc"
    get_fcc.__doc__ = (
        ".. deprecated:: 0.1.8\n"
        "\n"
        "   Use :func:`get_fcc_loss` instead."
    )
    get_fcc.__wrapped__ = get_fcc_loss

# End
