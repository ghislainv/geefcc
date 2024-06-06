"""Get forest cover change data."""

import os
import multiprocessing as mp

from .get_extent_from_aoi import get_extent_from_aoi
from .misc import make_dir
from .make_grid import make_grid, grid_intersection
from .geeic2geotiff import xarray2geotiff
from .geotiff_from_tiles import geotiff_from_tiles
from .get_forest import get_forest
from tqdm.autonotebook import tqdm

opj = os.path.join
opd = os.path.dirname


def get_forest_to_geotiff(i, years, ext, source, proj, scale, perc, out_dir_tiles):
    """Get forest cover change from GEE and write to geotiff."""
    forest = get_forest(years, ext, source, proj, scale, perc)
    xarray2geotiff(i, forest, years, proj, out_dir_tiles)


def get_fcc(aoi,
            buff=0,
            years=[2000, 2010, 2020],
            source="tmf",
            perc=75,
            tile_size=1,
            # crop_to_aoi=False,
            parallel=False,
            ncpu=None,
            output_file="fcc.tif"):
    """Get forest cover change data.

     Produce a forest cover change raster file. One band for each
     year. Value 1 for forest and 0 for non-forest.

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
        defining the forest must be specified with parameter ``perc``.

    :param perc: Tree cover threshold defining the forest for GFC
        product.

    :param tile_size: Tile size for parallel computing.

    :param parallel: Logical. Parallel (if ``True``) or sequential (if
        ``False``) computing. Default to ``False``.

    :param ncpu: Number of CPU to use for parallel computing. If None,
        it will be set to the number of cores on the computer minus
        one.

    :param crop_to_aoi: Crop the raster GeoTIFF file to aoi. If False,
        the output file will match the grid covering the aoi with
        buffer.

    :param output_file: Path to output GeoTIFF file. If directories in
        path do not exist they will be created.

    """

    # Output dir
    out_dir = opd(output_file)
    make_dir(out_dir)

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

    # Number of tiles
    ntiles = len(grid)

    # Create dir for forest tiles
    out_dir_tiles = opj(out_dir, "forest_tiles")
    make_dir(out_dir_tiles)

    # Message
    print(f"get_fcc running, {ntiles} tiles .", end="", flush=True)

    # Sequential computing
    if parallel is False:
        # Loop on tiles
        for (i, ext) in enumerate(tqdm(grid)):
            get_forest_to_geotiff(i, years, ext, source, proj, scale, perc, out_dir_tiles)

    # Parallel computing
    if parallel is True:
        # Write tiles in parallel
        # https://superfastpython.com/multiprocessing-pool-starmap_async/
        # create and configure the process pool
        if ncpu is None:
            ncpu = os.cpu_count() - 1
        with mp.Pool(processes=ncpu) as pool:
            # prepare arguments
            args = [(i, years, ext, source, proj, scale, perc, out_dir_tiles)
                    for (i, ext) in enumerate(grid)]
            # issue many tasks asynchronously to the process pool
            _ = pool.starmap_async(get_forest_to_geotiff, args)
            # close the pool
            pool.close()
            # wait for all issued tasks to complete
            pool.join()

    # Geotiff from tiles
    geotiff_from_tiles(output_file)

# End
