"""Get forest cover change data."""

import os
import multiprocess as mp

from .get_extent_from_aoi import get_extent_from_aoi
from .misc import make_dir
from .make_grid import make_grid, grid_intersection
from .geeic2geotiff import geeic2geotiff
from .geotiff_from_tiles import geotiff_from_tiles
from .ee_tmf_loss_gain import ee_tmf_loss_gain

opj = os.path.join
opd = os.path.dirname


def get_fcc_loss_gain(
        aoi,
        buff=0,
        year1=2005,
        year2=2025,
        min_years=10,
        tile_size=1,
        crop_to_aoi=False,
        parallel=False,
        ncpu=None,
        output_file="fcc.tif"):
    """Get forest cover change data.

    Produce a forest cover change raster file.

    Recodes forest/tree cover change products into 6 transition
    classes between two reference years, distinguishing old regrowth
    (continuously classified as regrowth for at least `min_years`)
    from young regrowth / non-forest.

    Transition classes:
        1. F to F -- stable forest (undisturbed or degraded at both dates)
        2. F to D -- deforestation (includes young regrowth at year2)
        3. D to oR -- non-forest / young regrowth becoming old regrowth
        4. F to oR (via D) -- forest cleared then regrown to old regrowth
           within the window
        5. oR to oR -- stable old regrowth
        6. oR to D -- old regrowth deforested, or fallen back below
           `min_years` of continuous regrowth

    .. note::
       :func:`get_fcc_loss_gain` returns a one-band raster with
       forest cover change (loss and gain) between two dates. In this
       case, both old-growth forest and old regrowth (following
       deforestation) are considered as forest at one point in time
       and can be deforested during the period of time. The user can
       differentiate the results between the different states and
       changes and make appropriate choices to estimate deforestation
       and regrowth rates.

       :func:`get_fcc_loss_gain` can only be used with the Tropical
       Moist Forest product. The Global Forest Change product does not
       provide annual forest gain.

    :param aoi: Area of interest defined either by a country iso code
        (three letters), a vector file, or an extent in lat/long
        (tuple with (xmin, ymin, xmax, ymax)).

    :param buff: Buffer around the aoi. In decimal degrees
        (e.g. 0.08983152841195216 correspond to ~10 km at the
        equator).

    :param year1: Start year (state assessed on 1st of January).

    :param year2: End year (state assessed on 1st of January).
        Must be greater than year1.

    :param min_years: Minimum number of consecutive years classified as
        regrowth to be considered "old regrowth" (oR). Default 10.

    :param tile_size: Tile size for parallel computing.

    :param crop_to_aoi: Crop the raster GeoTIFF file to **aoi with
        buffer**. If ``False``, the output file will match the
        **grid** covering the aoi with buffer.

    :param parallel: Logical. Parallel (if ``True``) or sequential (if
        ``False``) computing. Default to ``False``.

    :param ncpu: Number of CPU to use for parallel computing. If None,
        it will be set to the number of cores on the computer minus
        one.

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
    extent = get_extent_from_aoi(aoi, buff, out_dir)
    aoi_isfile = extent["aoi_isfile"]
    borders_gpkg = extent["borders_gpkg"]
    extent_latlong = extent["extent_latlong"]

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

    # Forest image collection
    forest = ee_tmf_loss_gain(year1, year2, min_years).fcc

    # Create dir for forest tiles
    out_dir_tiles = opj(out_dir, "forest_tiles")
    make_dir(out_dir_tiles)

    # Message
    print(f"get_fcc running, {ntiles} tiles .", end="", flush=True)

    # Sequential computing
    if parallel is False:
        # Loop on tiles
        for (i, ext) in enumerate(grid):
            geeic2geotiff(i, ext, ntiles, forest, proj, scale, out_dir_tiles)

    # Parallel computing
    if parallel is True:
        # Write tiles in parallel
        # https://superfastpython.com/multiprocessing-pool-starmap_async/
        # create and configure the process pool
        if ncpu is None:
            ncpu = os.cpu_count() - 1
        with mp.Pool(processes=ncpu) as pool:
            # prepare arguments
            args = [(i, ext, ntiles, forest, proj, scale, out_dir_tiles)
                    for (i, ext) in enumerate(grid)]
            # issue many tasks asynchronously to the process pool
            _ = pool.starmap_async(geeic2geotiff, args)
            # close the pool
            pool.close()
            # wait for all issued tasks to complete
            pool.join()

    # Geotiff from tiles
    geotiff_from_tiles(crop_to_aoi, extent, output_file)

# End
