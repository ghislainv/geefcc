"""Make geotiff from tiles."""

import os
from glob import glob

from osgeo import gdal

opj = os.path.join
opd = os.path.dirname


def add_color_table(output_file):
    """Add color table to GeoTIFF.

    :param output_file: Output file to add color table to.
    """

    # Open file in update mode
    ds = gdal.Open(output_file, gdal.GA_Update)
    n_bands = ds.RasterCount

    # Apply color table only for single band raster
    if n_bands == 1:
        # Define color table
        # Format: {pixel_value: (R, G, B, A)}
        colors = {
            0: (255, 255, 255, 0),    # stable non-forest
            1: (34, 139, 34, 255),    # stable forest
            2: (227, 26, 28, 255),    # forest --> deforested
            3: (30, 100, 200, 255),   # non-forest --> old regrowth
            4: (100, 160, 230, 255),  # forest --> old-regrowth (via defor)
            5: (150, 190, 140, 255),  # stable old-regrowth
            6: (255, 140, 0, 255),    # old regrowth --> deforested
        }
        band = ds.GetRasterBand(1)
        ct = gdal.ColorTable()
        for pixel_value, rgba in colors.items():
            ct.SetColorEntry(pixel_value, rgba)
        band.SetRasterColorTable(ct)
        band.SetRasterColorInterpretation(gdal.GCI_PaletteIndex)
        band.SetNoDataValue(0)
        band.FlushCache()

    # Close dataset
    ds = None


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
        srcNodata=0,
        VRTNodata=0,
        callback=cback)
    forest_vrt.FlushCache()
    forest_vrt = None
    vrt_file = opj(out_dir, "forest.vrt")

    # VRT to GeoTIFF
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
                      srcNodata=0,
                      dstNodata=0,
                      callback=cback)
        else:
            xmin, ymin, xmax, ymax = extent_latlong
            ulx_uly_lrx_lry = [xmin, ymax, xmax, ymin]
            gdal.Translate(output_file, vrt_file,
                           projWin=ulx_uly_lrx_lry,
                           noData=0,
                           maskBand=None,
                           creationOptions=copts,
                           callback=cback)
    else:
        gdal.Translate(output_file, vrt_file,
                       noData=0,
                       maskBand=None,
                       creationOptions=copts,
                       callback=cback)

    # Add color table to output file
    add_color_table(output_file)

# End
