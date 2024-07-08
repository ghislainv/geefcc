"""Make geotiff from tiles."""

import os
from glob import glob

from osgeo import gdal

opj = os.path.join
opd = os.path.dirname


def geotiff_from_tiles(crop_to_aoi, extent, output_file):
    """Make geotiff from tiles.

    :param crop_to_aoi: Crop the raster using aoi extent.

    :param extent: Result of ``get_extent_from_aoi()`` function (a
        dictionary).

    :param output_file: Output file.

    """

    # Dir for forest tiles
    out_dir = opd(output_file)
    out_dir_tiles = opj(out_dir, "forest_tiles")

    # Make vrt
    tif_forest_files = glob(opj(out_dir_tiles, "forest_*.tif"))
    # Callback
    verbose = False
    cback = gdal.TermProgress_nocb if verbose else 0
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
    aoi_isfile = extent["aoi_isfile"]
    borders_gpkg = extent["borders_gpkg"]
    extent_latlong = extent["extent_latlong"]
    if crop_to_aoi:
        if aoi_isfile:
            gdal.Warp(output_file, vrt_file,
                      cropToCutline=True,
                      warpOptions=["CUTLINE_ALL_TOUCHED=TRUE"],
                      cutlineDSName=borders_gpkg,
                      creationOptions=copts,
                      callback=cback)
        else:
            xmin, ymin, xmax, ymax = extent_latlong
            ulx_uly_lrx_lry = [xmin, ymax, xmax, ymin]
            gdal.Translate(output_file, vrt_file,
                           projWin=ulx_uly_lrx_lry,
                           maskBand=None,
                           creationOptions=copts,
                           callback=cback)
    else:
        gdal.Translate(output_file, vrt_file,
                       maskBand=None,
                       creationOptions=copts,
                       callback=cback)

# End
