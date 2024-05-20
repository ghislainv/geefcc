"""Make geotiff from tiles."""

import os
from glob import glob
import math

from osgeo import gdal

opj = os.path.join
opd = os.path.dirname


def geotiff_from_tiles(extent_latlong, scale, out_dir):
    """Make geotiff from tiles.

    :param extent_latlong: Extent in lat/long.
    :param scale: Resolution.
    :param out_dir: Output directory.

    """

    # Dir for forest tiles
    out_dir_tiles = opj(out_dir, "forest_tiles")

    # Make vrt
    tif_forest_files = glob(opj(out_dir_tiles, "forest_*.tif"))
    # Callback
    verbose = False
    cback = gdal.TermProgress if verbose else 0
    forest_vrt = gdal.BuildVRT(
        opj(out_dir, "forest.vrt"),
        tif_forest_files,
        callback=cback)
    # Flush cache
    # https://gis.stackexchange.com/questions/306664/
    # gdal-buildvrt-not-creating-any-output
    # https://gis.stackexchange.com/questions/44003/
    # python-equivalent-of-gdalbuildvrt
    forest_vrt.FlushCache()
    forest_vrt = None

    # VRT to GeoTIFF
    # Creation options
    copts = ["COMPRESS=DEFLATE", "BIGTIFF=YES"]
    # Adjusted extent
    xmin = extent_latlong[0]
    xmax = extent_latlong[2]
    xmax_tap = xmin + math.ceil((xmax - xmin) / scale) * scale
    ymin = extent_latlong[1]
    ymax = extent_latlong[3]
    ymax_tap = ymin + math.ceil((ymax - ymin) / scale) * scale

    # Call to gdal_translate
    ifile = opj(out_dir, "forest.vrt")
    ofile = opj(out_dir, "fcc.tif")
    # projWin = [ulx, uly, lrx, lry]
    gdal.Translate(ofile, ifile,
                   maskBand=None,
                   projWin=[xmin, ymax_tap, xmax_tap, ymin],
                   creationOptions=copts,
                   callback=cback)

# End
