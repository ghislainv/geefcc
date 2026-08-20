"""Summing raster bands.

See: https://github.com/mstrimas/gdal-summarize/blob/master/gdal-summarize.py
"""

import os

import numpy as np
from osgeo import gdal

from .misc import progress_bar, makeblock


def sum_raster_bands(input_file, output_file="sum.tif",
                     blk_rows=128, verbose=True):
    """Sum the raster bands of a multi-band input file into a single
    output band.

    Reads the input raster file band by band in configurable block sizes to
    manage memory usage, computes the pixel-wise sum across all bands, and
    writes the result to a single-band GeoTIFF output file.

    Parameters
    ----------
    input_file : str
        Path to the input raster file containing several bands to be summed.
    output_file : str, optional
        Path to the output GeoTIFF file with one band corresponding to the
        sum of the input bands. Defaults to ``"sum.tif"``.
    blk_rows : int, optional
        Number of rows per processing block. Used to break large raster files
        into several blocks of data that can be held in memory at one time.
        Defaults to ``128``.
    verbose : bool, optional
        Whether to print progress messages during processing. Defaults to
        ``True``.

    Returns
    -------
    None
        The function writes results directly to ``output_file`` and does not
        return a value.

    Raises
    ------
    RuntimeError
        If ``input_file`` cannot be opened by GDAL or if the output raster
        cannot be created.

    Notes
    -----
    - The output raster is created with ``gdal.GDT_Byte`` data type, DEFLATE
      compression, and BIGTIFF support enabled.
    - A NoData value of ``255`` is assigned to the output band.
    - If ``output_file`` already exists, it will be removed before the new
      file is created.
    - Band statistics are computed and flushed to disk after all blocks have
      been processed.

    Examples
    --------
    >>> sum_raster_bands(
    ...     input_file="input_multiband.tif",
    ...     output_file="sum.tif",
    ...     blk_rows=256,
    ...     verbose=True,
    ... )

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
