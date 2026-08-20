"""Shared pipeline for get_fcc_loss and get_fcc_loss_gain."""

import os
import multiprocess as mp

from .misc import make_dir
from .make_grid import make_grid, grid_intersection
from .geeic2geotiff import geeic2geotiff
from .geotiff_from_tiles import geotiff_from_tiles
from .get_extent_from_aoi import get_extent_from_aoi

opj = os.path.join
opd = os.path.dirname

PROJ = "EPSG:4326"
EPSG_CODE = 4326
SCALE = 0.000269494585235856472  # in dd, ~30 m


def _run_fcc_pipeline(aoi, buff, tile_size, forest,
                      crop_to_aoi, parallel, ncpu, output_file):
    """Run the common FCC download and assembly pipeline.

    Parameters
    ----------
    aoi : str or tuple
        Area of interest (ISO3 country code, tuple extent, or .gpkg path).
    buff : float
        Buffer around the aoi in decimal degrees.
    tile_size : float
        Tile size in degrees.
    forest : ee.Image or ee.ImageCollection
        The GEE forest image or image collection to download.
    crop_to_aoi : bool
        Whether to crop the output raster to the AOI.
    parallel : bool
        Whether to use parallel computing.
    ncpu : int or None
        Number of CPUs for parallel computing. If None, uses
        os.cpu_count() - 1.
    output_file : str
        Path to the output GeoTIFF file.

    Returns
    -------
    None
        The function writes the output GeoTIFF to disk and returns nothing.
    """

    # Output dir
    out_dir = opd(output_file)
    make_dir(out_dir)

    # Get aoi
    extent = get_extent_from_aoi(aoi, buff, out_dir)
    aoi_isfile = extent["aoi_isfile"]
    borders_gpkg = extent["borders_gpkg"]
    extent_latlong = extent["extent_latlong"]

    # Make minimal grid
    grid_gpkg = opj(out_dir, "grid.gpkg")
    grid = make_grid(extent_latlong, buff=0, tile_size=tile_size,
                     scale=SCALE, proj=EPSG_CODE, ofile=grid_gpkg)
    if aoi_isfile:
        min_grid = opj(out_dir, "min_grid.gpkg")
        grid = grid_intersection(grid, grid_gpkg, min_grid, borders_gpkg)

    # Number of tiles
    ntiles = len(grid)

    # Create dir for forest tiles
    out_dir_tiles = opj(out_dir, "forest_tiles")
    make_dir(out_dir_tiles)

    # Message
    print(f"get_fcc running, {ntiles} tiles .", end="", flush=True)

    # Sequential computing
    if not parallel:
        for (i, ext) in enumerate(grid):
            geeic2geotiff(i, ext, ntiles, forest, PROJ, SCALE, out_dir_tiles)

    # Parallel computing
    else:
        if ncpu is None:
            ncpu = os.cpu_count() - 1
        with mp.Pool(processes=ncpu) as pool:
            args = [(i, ext, ntiles, forest, PROJ, SCALE, out_dir_tiles)
                    for (i, ext) in enumerate(grid)]
            _ = pool.starmap_async(geeic2geotiff, args)
            pool.close()
            pool.join()

    # Geotiff from tiles
    geotiff_from_tiles(crop_to_aoi, extent, output_file)

# End
