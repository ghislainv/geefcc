"""Make geotiff from tiles."""

import os
from glob import glob

from osgeo import gdal

opj = os.path.join
opd = os.path.dirname


def geotiff_from_tiles(output_file):
    """Make geotiff from tiles.

    :param output_file: Path to output GeoTIFF file.
    """

    # Dir for forest tiles
    out_dir = opd(output_file)
    out_dir_tiles = opj(out_dir, "forest_tiles")

    tif_forest_files = glob(opj(out_dir_tiles, "forest_*.tif"))
    if len(tif_forest_files) == 0:
        raise ValueError("No forest tiles found.")
    elif len(tif_forest_files) == 1:
        print("Only one tile found. Copying to output.")
        os.rename(tif_forest_files[0], output_file)
        return
    else:
        print(f"{len(tif_forest_files)} tiles found.")
        # Make vrt
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
        vrt_file = opj(out_dir, "forest.vrt")

        # VRT to GeoTIFF
        # Creation options
        copts = ["COMPRESS=DEFLATE", "BIGTIFF=YES"]
        gdal.Translate(output_file, vrt_file,
                       maskBand=None,
                       creationOptions=copts,
                       callback=cback)

# End
