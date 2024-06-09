"""Miscellaneous functions."""

# Standard library imports
import os

# Third party imports
import numpy as np
from osgeo import gdal


# Function to make a directory
def make_dir(newdir):
    """Make new directory

        * Already exists, silently complete
        * Regular file in the way, raise an exception
        * Parent directory(ies) does not exist, make them as well

    :param newdir: Directory path to create.

    """
    if os.path.isdir(newdir):
        pass
    elif os.path.isfile(newdir):
        raise OSError(
            "a file with the same name as the desired \
                      dir, '{}', already exists.".format(
                newdir
            )
        )
    else:
        head, tail = os.path.split(newdir)
        if head and not os.path.isdir(head):
            make_dir(head)
        # print "_mkdir %s" % repr(newdir)
        if tail:
            os.mkdir(newdir)


# Makeblock
def makeblock(rasterfile, blk_rows=128):
    """Compute block information.

    This function computes block information from the caracteristics
    of a raster file and an indication on the number of rows to
    consider.

    :param rasterfile: Path to a raster file.
    :param blk_rows: If > 0, number of rows for block. If <=0, the
        block size will be 256 x 256.

    :return: A tuple of length 6 including block number, block number
        on x axis, block number on y axis, block offsets on x axis,
        block offsets on y axis, block sizes on x axis, block sizes on
        y axis.

    """

    r = gdal.Open(rasterfile)
    # b = r.GetRasterBand(1)
    # Landscape variables
    ncol = r.RasterXSize
    nrow = r.RasterYSize
    # Block size
    # block_xsize, block_ysize = b.GetBlockSize()
    # Adapt number of blocks
    if blk_rows > 0:
        block_xsize = ncol
        block_ysize = blk_rows
    else:
        block_xsize = 256
        block_ysize = 256
    # Number of blocks
    nblock_x = int(np.ceil(ncol / block_xsize))
    nblock_y = int(np.ceil(nrow / block_ysize))
    nblock = nblock_x * nblock_y
    # Upper-left coordinates of each block
    x = np.arange(0, ncol, block_xsize, dtype=int).tolist()
    y = np.arange(0, nrow, block_ysize, dtype=int).tolist()
    # Size (number of col and row) of each block
    nx = [block_xsize] * nblock_x
    ny = [block_ysize] * nblock_y
    # Modify last values of nx and ny
    if (ncol % block_xsize) > 0:
        nx[-1] = ncol % block_xsize
    if (nrow % block_ysize) > 0:
        ny[-1] = nrow % block_ysize
    # b = None
    del r
    return (nblock, nblock_x, nblock_y, x, y, nx, ny)


def progress_bar(niter, i):
    """Draw progress_bar

     See results of ``[(100 * i / niter) // 10 * 10 for i in
     range(niter + 1)]`` to understand how it works.

    :param niter: Total number of iterations.
    :param i: Current number of iteration (starts at 1).

    """

    pkg_name = "geefcc"

    if niter >= 40:
        perc_10 = 100 * i / niter // 10 * 10
        perc_previous_10 = 100 * (i - 1) / niter // 10 * 10
        perc_2_5 = 100 * i / niter // 2.5 * 2.5
        perc_previous_2_5 = 100 * (i - 1) / niter // 2.5 * 2.5
        if i == 1:
            print(f"{pkg_name}: 0", end="", flush=True)
        elif perc_10 != perc_previous_10:
            if i == niter:
                print("100 - done", end="\n", flush=True)
            else:
                print(f"{int(perc_10)}", end="", flush=True)
        elif perc_2_5 != perc_previous_2_5:
            print(".", end="", flush=True)
    else:
        perc_10 = 100 * i / niter // 10 * 10
        perc_previous_10 = 100 * (i - 1) / niter // 10 * 10
        if i == 0:
            print(f"{pkg_name}: 0...", end="", flush=True)
        elif perc_10 != perc_previous_10:
            if i == niter:
                print("100 - done", end="\n", flush=True)
            else:
                print(f"{int(perc_10)}...", end="", flush=True)


# End
