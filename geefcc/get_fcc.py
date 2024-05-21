"""Get forest cover change data."""

import os
import multiprocessing as mp

from .get_extent_from_aoi import get_extent_from_aoi
from .make_dir import make_dir
from .make_grid import make_grid, grid_intersection
from .geeic2geotiff import geeic2geotiff
from .ee_tmf import ee_tmf
from .geotiff_from_tiles import geotiff_from_tiles

opj = os.path.join
opd = os.path.dirname


def get_fcc(aoi,
            buff=0,
            years=[2000, 2010, 2020],
            source="tmf",
            perc=75,
            tile_size=1,
            output_file="fcc.tiff"):
    """Get forest cover change data.

    :param aoi: Area of interest defined either by a country iso code
        (three letters), a vector file, or an extent in lat/long
        (tuple with (xmin, ymin, xmax, ymax)).

    :param buff: Buffer around the aoi. In decimal degrees
        (e.g. 0.08983152841195216 correspond to ~10 km at the
        equator).

    :param years: List of years defining time-periods for estimating
        forest cover change. Years for computing forest cover change
        can be in the interval 2001--2024 for GFC (GFC does not
        provide loss for the year 2000) and 2000--2023 for TMF.

    :param source: Either "gfc" for Global Forest Change or "tmf" for
        Tropical Moist Forest. If "gfc", the tree cover threshold
        defining the forest must be specified with parameter `perc`.

    :param perc: Tree cover threshold defining the forest.

    :param tile_size: Tile size for parallel computing.

    :output_file: Path to output GeoTIFF file. One band for each
        year. Value 1 for forest and 0 for non-forest.

    """

    # Output dir
    out_dir = opd(output_file)

    # Variables
    proj = "EPSG:4326"
    epsg_code = 4326
    scale = 0.000269494585235856472  # in dd, ~30 m

    # Get aoi
    ext = get_extent_from_aoi(aoi, buff, out_dir)
    aoi_isfile = ext["aoi_isfile"]
    borders_gpkg = ext["borders_gpkg"]
    extent_latlong = ext["extent_latlong"]

    # Make minimal grid
    grid_gpkg = opj(out_dir, "grid.gpkg")
    grid = make_grid(extent_latlong, buff=0, tile_size=tile_size,
                     scale=scale, proj=epsg_code, ofile=grid_gpkg)
    if aoi_isfile:
        min_grid = opj(out_dir, "min_grid.gpkg")
        grid_i = grid_intersection(grid, grid_gpkg, min_grid,
                                   borders_gpkg)
        # Update grid and file
        grid = grid_i
        grid_gpkg = min_grid

    # Forest image collection
    if source == "tmf":
        forest = ee_tmf(years)

    # Create dir for forest tiles
    out_dir_tiles = opj(out_dir, "forest_tiles")
    make_dir(out_dir_tiles)

    # Write tiles in parallel
    ncpu = os.cpu_count() - 1
    pool = mp.Pool(processes=ncpu)
    args = [(i, ext, forest, proj, scale, out_dir_tiles)
            for (i, ext) in enumerate(grid)]
    pool.starmap_async(geeic2geotiff, args).get()
    pool.close()
    pool.join()

    # Geotiff from tiles
    geotiff_from_tiles(extent_latlong, scale, out_dir)


# End
