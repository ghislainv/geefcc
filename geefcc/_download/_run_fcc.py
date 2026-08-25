"""Shared pipeline for get_fcc_loss and get_fcc_loss_gain."""

import os
from pathlib import Path
import multiprocess as mp

from ..misc import make_dir
from .make_grid import make_grid, grid_intersection
from .geeic2geotiff import geeic2geotiff
from .geotiff_from_tiles import geotiff_from_tiles
from .get_extent_from_aoi import get_extent_from_aoi

PROJ = "EPSG:4326"
EPSG_CODE = 4326
SCALE = 0.000269494585235856472  # in dd, ~30 m


def _run_fcc_pipeline(aoi, buff, tile_size, forest,
                      crop_to_aoi, parallel, ncpu, output_file):
    """Run the common FCC download and assembly pipeline."""

    output_file = Path(output_file)
    out_dir = output_file.parent
    make_dir(out_dir)

    extent = get_extent_from_aoi(aoi, buff, out_dir)
    aoi_isfile = extent["aoi_isfile"]
    borders_gpkg = extent["borders_gpkg"]
    extent_latlong = extent["extent_latlong"]

    grid_gpkg = out_dir / "grid.gpkg"
    grid = make_grid(extent_latlong, buff=0, tile_size=tile_size,
                     scale=SCALE, proj=EPSG_CODE, ofile=grid_gpkg)
    if aoi_isfile:
        min_grid = out_dir / "min_grid.gpkg"
        grid = grid_intersection(grid, grid_gpkg, min_grid, borders_gpkg)

    ntiles = len(grid)
    out_dir_tiles = out_dir / "forest_tiles"
    make_dir(out_dir_tiles)

    print(f"get_fcc running, {ntiles} tiles .", end="", flush=True)

    if not parallel:
        for (i, ext) in enumerate(grid):
            geeic2geotiff(i, ext, ntiles, forest, PROJ, SCALE, out_dir_tiles)
    else:
        if ncpu is None:
            ncpu = os.cpu_count() - 1
        with mp.Pool(processes=ncpu) as pool:
            args = [(i, ext, ntiles, forest, PROJ, SCALE, str(out_dir_tiles))
                    for (i, ext) in enumerate(grid)]
            _ = pool.starmap_async(geeic2geotiff, args)
            pool.close()
            pool.join()

    geotiff_from_tiles(crop_to_aoi, extent, output_file)

# End
