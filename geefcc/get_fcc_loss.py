"""Get forest cover change data."""

from ._download.ee_tmf import ee_tmf
from ._download.ee_gfc import ee_gfc
from ._download._run_fcc import _run_fcc_pipeline


def get_fcc_loss(
        aoi,
        buff=0,
        years=None,
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
        Buffer around the aoi in decimal degrees. Default is 0.
    years : list of int, optional
        List of years defining time-periods for estimating forest cover
        change. Default is [2000, 2010, 2020].
    source : {"tmf", "gfc"}, optional
        Source of forest cover data. Default is ``"tmf"``.
    perc : int, optional
        Tree cover threshold (percentage) for the GFC product. Default
        is 75.
    tile_size : int or float, optional
        Tile size in degrees for parallel computing. Default is 1.
    crop_to_aoi : bool, optional
        Crop the raster to the aoi with buffer. Default is ``False``.
    parallel : bool, optional
        Use parallel computing. Default is ``False``.
    ncpu : int or None, optional
        Number of CPUs for parallel computing. Default is ``None``.
    output_file : str or Path, optional
        Path to output GeoTIFF file. Default is ``"fcc.tif"``.

    Returns
    -------
    None

    Examples
    --------
    >>> get_fcc_loss(
    ...     aoi="BRA",
    ...     years=[2000, 2010, 2020],
    ...     source="tmf",
    ...     output_file="output/fcc_brazil.tif"
    ... )
    """

    if years is None:
        years = [2000, 2010, 2020]

    if source == "tmf":
        forest = ee_tmf(years)
    elif source == "gfc":
        forest = ee_gfc(years, perc)
    else:
        raise ValueError(f"source must be 'tmf' or 'gfc', got '{source}'")

    _run_fcc_pipeline(aoi, buff, tile_size, forest,
                      crop_to_aoi, parallel, ncpu, output_file)

# End
