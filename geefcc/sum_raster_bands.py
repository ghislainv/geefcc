"""Summing raster bands.
See: https://github.com/mstrimas/gdal-summarize/blob/master/gdal-summarize.py
"""

import os

import numpy as np
from osgeo import gdal

from .misc import progress_bar, makeblock


def sum_raster_bands(input_file, output_file="sum.tif",
                     blk_rows=128, verbose=True):
    """Summing the raster bands.

    :param input file: Input file with several bands.

    :param output_file: Output file with one band corresponding to the
        sum of the input bands.

    :param blk_rows: Number of rows for block. This is used to break
        lage raster files in several blocks of data that can be hold
        in memory.

    :param verbose: Logical. Whether to print messages or not.

    """

    # Load input raster info
    ds = gdal.Open(input_file)
    gt = ds.GetGeoTransform()
    proj = ds.GetProjection()
    ncol = ds.RasterXSize
    nrow = ds.RasterYSize
    nband = ds.RasterCount

    # Create output raster file
    driver = gdal.GetDriverByName("GTiff")
    if os.path.isfile(output_file):
        os.remove(output_file)
    ds_out = driver.Create(
        output_file,
        ncol, nrow, 1,
        gdal.GDT_Byte,
        ["COMPRESS=DEFLATE", "BIGTIFF=YES"],
    )
    ds_out.SetGeoTransform(gt)
    ds_out.SetProjection(proj)
    band_out = ds_out.GetRasterBand(1)
    band_out.SetNoDataValue(255)
    band_out.SetDescription("fcc")  # band name

    # Make blocks
    blockinfo = makeblock(input_file, blk_rows=blk_rows)
    nblock = blockinfo[0]
    nblock_x = blockinfo[1]
    x = blockinfo[3]
    y = blockinfo[4]
    nx = blockinfo[5]
    ny = blockinfo[6]

    # Loop on blocks of data
    for b in range(nblock):
        # Progress bar
        if verbose:
            progress_bar(nblock, b + 1)
        # Position in 1D-arrays
        px = b % nblock_x
        py = b // nblock_x
        # Make stack to store data
        stack = np.empty(shape=(nband, ny[py], nx[px]),
                         dtype="b")
        # Data for one block
        for i in range(nband):
            stack[i] = (ds.GetRasterBand(i + 1)
                        .ReadAsArray(x[px], y[py], nx[px], ny[py]))
        # Compute sum
        result = np.sum(stack, axis=0)
        # Write data
        band_out.WriteArray(result, x[px], y[py])

    print("Compute statistics")
    band_out.FlushCache()  # Write cache data to disk
    band_out.ComputeStatistics(False)

    # Dereference driver
    band_out = None
    del ds_out


# End
