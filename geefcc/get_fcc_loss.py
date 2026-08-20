"""Get forest cover change data."""

from .ee_tmf import ee_tmf
from .ee_gfc import ee_gfc
from ._run_fcc import _run_fcc_pipeline


def get_fcc_loss(
        aoi,
        buff=0,
        years=[2000, 2010, 2020],
        source="tmf",
        perc=75,
        tile_size=1,
        crop_to_aoi=False,
        parallel=False,
        ncpu=None,
        output_file="fcc.tif"):
    """Get forest cover change data.

    Produce a forest cover change raster file. One band for each
    year. Value 1 for forest and 0 for non-forest.

    Parameters
    ----------
    aoi : str or tuple
        Area of interest defined either by a country iso code
        (three letters), a vector file path, or an extent in lat/long
        as a tuple with (xmin, ymin, xmax, ymax).
    buff : float, optional
        Buffer around the aoi in decimal degrees. For example,
        0.08983152841195216 corresponds to approximately 10 km at the
        equator. Default is 0.
    years : list of int, optional
        List of years defining time-periods for estimating forest cover
        change. Years for computing forest cover change can be in the
        interval 2001--2024 for GFC (GFC does not provide loss for the
        year 2000) and 2000--2024 for TMF. Default is [2000, 2010, 2020].
    source : {"tmf", "gfc"}, optional
        Source of forest cover data. Either ``"gfc"`` for Global Forest
        Change or ``"tmf"`` for Tropical Moist Forest. If ``"gfc"``,
        the tree cover threshold defining the forest must be specified
        with parameter ``perc``. Default is ``"tmf"``.
    perc : int, optional
        Tree cover threshold (percentage) defining the forest for the
        GFC product. Default is 75.
    tile_size : int or float, optional
        Tile size in degrees for parallel computing. Default is 1.
    crop_to_aoi : bool, optional
        Crop the raster GeoTIFF file to the aoi with buffer. If
        ``False``, the output file will match the grid covering the aoi
        with buffer. Default is ``False``.
    parallel : bool, optional
        If ``True``, use parallel computing. If ``False``, use
        sequential computing. Default is ``False``.
    ncpu : int or None, optional
        Number of CPUs to use for parallel computing. If ``None``, it
        will be set to the number of cores on the computer minus one.
        Default is ``None``.
    output_file : str, optional
        Path to output GeoTIFF file. If directories in the path do not
        exist, they will be created. Default is ``"fcc.tif"``.

    Returns
    -------
    None
        The function writes the forest cover change raster directly to
        ``output_file`` on disk. No Python object is returned.

    Raises
    ------
    ValueError
        If ``source`` is not one of ``"tmf"`` or ``"gfc"``, or if the
        specified ``years`` are outside the valid range for the chosen
        source.
    OSError
        If the output directory cannot be created or the output file
        cannot be written.

    Notes
    -----
    ``get_fcc_loss`` returns a multiband raster and can be used to
    produce deforestation maps between several dates. In this case,
    only old-growth forest (which was forest at the beginning of the
    satellite image archive) is considered.

    ``get_fcc_loss`` can be used with either the Tropical Moist Forest
    (TMF) or the Global Forest Change (GFC) product.

    The output raster uses the ``EPSG:4326`` projection at approximately
    30 m resolution (~0.000269 decimal degrees per pixel).

    Examples
    --------
    Get forest cover change using the TMF product for a country defined
    by its ISO3 code:

    >>> get_fcc_loss(
    ...     aoi="BRA",
    ...     buff=0,
    ...     years=[2000, 2010, 2020],
    ...     source="tmf",
    ...     output_file="output/fcc_brazil.tif"
    ... )

    Get forest cover change using the GFC product with a custom tree
    cover threshold:

    >>> get_fcc_loss(
    ...     aoi="COD",
    ...     years=[2001, 2015, 2024],
    ...     source="gfc",
    ...     perc=50,
    ...     output_file="output/fcc_cod.tif"
    ... )

    Get forest cover change using a bounding box extent and parallel
    computing:

    >>> get_fcc_loss(
    ...     aoi=(-55.0, -15.0, -45.0, -5.0),
    ...     years=[2000, 2020],
    ...     source="tmf",
    ...     parallel=True,
    ...     ncpu=4,
    ...     output_file="output/fcc_extent.tif"
    ... )
    """

    # Forest image collection
    if source == "tmf":
        forest = ee_tmf(years)
    elif source == "gfc":
        forest = ee_gfc(years, perc)
    else:
        raise ValueError(f"source must be 'tmf' or 'gfc', got '{source}'")

    # Run common pipeline
    _run_fcc_pipeline(aoi, buff, tile_size, forest,
                      crop_to_aoi, parallel, ncpu, output_file)

# End
