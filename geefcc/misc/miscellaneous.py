"""Miscellaneous functions."""

# Standard library imports
from pathlib import Path

# Third party imports
import numpy as np
from osgeo import gdal


# Function to make a directory
def make_dir(newdir):
    """Make new directory.

    Handles three cases:

    * Already exists, silently complete
    * Regular file in the way, raise an exception
    * Parent directory(ies) does not exist, make them as well

    Parameters
    ----------
    newdir : str or Path
        Directory path to create.

    Raises
    ------
    OSError
        If a file with the same name as the desired directory already exists.

    Examples
    --------
    >>> make_dir("/tmp/new_directory")
    >>> make_dir("/tmp/parent/child/grandchild")
    """
    newdir = Path(newdir)
    if newdir.is_dir():
        pass
    elif newdir.is_file():
        raise OSError(
            f"a file with the same name as the desired "
            f"dir, '{newdir}', already exists."
        )
    else:
        newdir.mkdir(parents=True, exist_ok=True)


# Makeblock
def makeblock(rasterfile, blk_rows=128):
    """Compute block information.

    This function computes block information from the caracteristics
    of a raster file and an indication on the number of rows to
    consider.

    Parameters
    ----------
    rasterfile : str or Path
        Path to a raster file.
    blk_rows : int, optional
        If > 0, number of rows for block. If <= 0, the block size will
        be 256 x 256. Default is 128.

    Returns
    -------
    nblock : int
        Total number of blocks.
    nblock_x : int
        Number of blocks on the x axis.
    nblock_y : int
        Number of blocks on the y axis.
    x : list of int
        Block offsets on the x axis (upper-left x coordinates of each block).
    y : list of int
        Block offsets on the y axis (upper-left y coordinates of each block).
    nx : list of int
        Block sizes (number of columns) on the x axis.
    ny : list of int
        Block sizes (number of rows) on the y axis.

    Notes
    -----
    The returned tuple has length 7 and contains block count information
    alongside the offsets and sizes needed to iterate over all blocks
    in a raster file.

    Examples
    --------
    >>> nblock, nblock_x, nblock_y, x, y, nx, ny = makeblock("raster.tif")
    >>> nblock, nblock_x, nblock_y, x, y, nx, ny = makeblock(
    ...     "raster.tif", blk_rows=256
    ... )
    """

    r = gdal.Open(str(rasterfile))  # GDAL requires str
    # Landscape variables
    ncol = r.RasterXSize
    nrow = r.RasterYSize
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
    del r
    return (nblock, nblock_x, nblock_y, x, y, nx, ny)


def progress_bar(niter, i):
    """Draw progress bar.

    Prints a simple text-based progress bar to standard output.
    See results of ``[(100 * i / niter) // 10 * 10 for i in
    range(niter + 1)]`` to understand how it works.

    Parameters
    ----------
    niter : int
        Total number of iterations.
    i : int
        Current number of iteration (starts at 1).

    Notes
    -----
    When ``niter >= 40``, the progress bar prints percentage markers
    at every 10% and dot markers at every 2.5%. When ``niter < 40``,
    only 10% markers are printed. Output is flushed immediately to
    support real-time display in terminals and notebooks.

    Examples
    --------
    >>> niter = 100
    >>> for i in range(1, niter + 1):
    ...     progress_bar(niter, i)
    geefcc: 0....10....20....30....40....50....60....70....80....90....100 - done
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
