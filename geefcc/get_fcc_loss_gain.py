"""Get forest cover change data with loss and gain."""

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

    Produce a forest cover change raster file with loss and gain.

    Recodes forest/tree cover change products into 6 transition
    classes between two reference years, distinguishing old regrowth
    (continuously classified as regrowth for at least `min_years`)
    from young regrowth / non-forest.

    Transition classes:

    - 1 = F to F -- stable forest (undisturbed or degraded at both dates)
    - 2 = F to D -- deforestation (includes young regrowth at year2)
    - 3 = D to oR -- non-forest / young regrowth becoming old regrowth
    - 4 = F to oR (via D) -- forest cleared then regrown to old regrowth
      within the window
    - 5 = oR to oR -- stable old regrowth
    - 6 = oR to D -- old regrowth deforested, or fallen back below `min_years`
      of continuous regrowth

    Parameters
    ----------
    aoi : str or tuple
        Area of interest defined either by a country iso code
        (three letters), a vector file path, or an extent in lat/long
        as a tuple with ``(xmin, ymin, xmax, ymax)``.
    buff : float, optional
        Buffer around the aoi in decimal degrees. For example,
        ``0.08983152841195216`` corresponds to approximately 10 km at
        the equator. Default is ``0``.
    year1 : int, optional
        Start year. State is assessed on the 1st of January of this
        year. Default is ``2005``.
    year2 : int, optional
        End year. State is assessed on the 1st of January of this
        year. Must be greater than `year1`. Default is ``2025``.
    min_years : int, optional
        Minimum number of consecutive years classified as regrowth to
        be considered "old regrowth" (oR). Default is ``10``.
    tile_size : int or float, optional
        Tile size used for parallel computing, in degrees. Default is
        ``1``.
    crop_to_aoi : bool, optional
        If ``True``, crop the output raster GeoTIFF to the aoi with
        buffer. If ``False``, the output file will match the grid
        covering the aoi with buffer. Default is ``False``.
    parallel : bool, optional
        If ``True``, use parallel computing. If ``False``, use
        sequential computing. Default is ``False``.
    ncpu : int or None, optional
        Number of CPUs to use for parallel computing. If ``None``, it
        will be set to the number of cores on the computer minus one.
        Default is ``None``.
    output_file : str, optional
        Path to the output GeoTIFF file. If directories in the path do
        not exist, they will be created. Default is ``"fcc.tif"``.

    Returns
    -------
    None
        The function writes a single-band GeoTIFF raster to
        `output_file` containing forest cover change (loss and gain)
        between `year1` and `year2`. Pixel values correspond to the
        six transition classes described above.

    Raises
    ------
    ValueError
        If `year2` is not greater than `year1`.
    FileNotFoundError
        If `aoi` is specified as a file path and the file does not
        exist.

    Notes
    -----
    This function returns a one-band raster with forest cover change
    (loss and gain) between two dates. Both old-growth forest and old
    regrowth (following deforestation) are considered as forest at one
    point in time and can be deforested during the period of time. The
    user can differentiate the results between the different states and
    changes and make appropriate choices to estimate deforestation and
    regrowth rates.

    This function can only be used with the Tropical Moist Forest
    product. The Global Forest Change product does not provide annual
    forest gain.

    The output raster uses the ``EPSG:4326`` coordinate reference
    system and a pixel resolution of approximately 30 m
    (``0.000269494585235856472`` decimal degrees).

    Examples
    --------
    >>> get_fcc_loss_gain(
    ...     aoi="MDG",
    ...     buff=0,
    ...     year1=2010,
    ...     year2=2020,
    ...     min_years=10,
    ...     tile_size=1,
    ...     crop_to_aoi=True,
    ...     parallel=False,
    ...     ncpu=None,
    ...     output_file="output/fcc_madagascar.tif"
    ... )

    >>> get_fcc_loss_gain(
    ...     aoi=(44.0, -25.5, 50.5, -12.0),
    ...     year1=2000,
    ...     year2=2015,
    ...     parallel=True,
    ...     ncpu=4,
    ...     output_file="output/fcc_custom_extent.tif"
    ... )
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
