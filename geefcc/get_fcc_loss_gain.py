"""Get forest cover change data with loss and gain."""

from ._download.ee_tmf_loss_gain import ee_tmf_loss_gain
from ._download._run_fcc import _run_fcc_pipeline


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
    """Get forest cover change data with loss and gain.

    Produce a forest cover change raster file with loss and gain.

    Parameters
    ----------
    aoi : str or tuple
        Area of interest defined either by a country iso code
        (three letters), a vector file path, or an extent in lat/long
        as a tuple with ``(xmin, ymin, xmax, ymax)``.
    buff : float, optional
        Buffer around the aoi in decimal degrees. Default is ``0``.
    year1 : int, optional
        Start year. Default is ``2005``.
    year2 : int, optional
        End year. Must be greater than `year1`. Default is ``2025``.
    min_years : int, optional
        Minimum consecutive years classified as regrowth to be
        considered "old regrowth". Default is ``10``.
    tile_size : int or float, optional
        Tile size in degrees. Default is ``1``.
    crop_to_aoi : bool, optional
        Crop output raster to the aoi. Default is ``False``.
    parallel : bool, optional
        Use parallel computing. Default is ``False``.
    ncpu : int or None, optional
        Number of CPUs for parallel computing. Default is ``None``.
    output_file : str, optional
        Path to the output GeoTIFF file. Default is ``"fcc.tif"``.

    Returns
    -------
    None

    Examples
    --------
    >>> get_fcc_loss_gain(
    ...     aoi="MDG",
    ...     year1=2010,
    ...     year2=2020,
    ...     min_years=10,
    ...     crop_to_aoi=True,
    ...     output_file="output/fcc_madagascar.tif"
    ... )
    """

    forest = ee_tmf_loss_gain(year1, year2, min_years).fcc
    _run_fcc_pipeline(aoi, buff, tile_size, forest,
                      crop_to_aoi, parallel, ncpu, output_file)

# End
