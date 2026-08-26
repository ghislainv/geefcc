"""Compute statistics per class for a TMF or GFC loss forest cover change raster."""

from pathlib import Path

import dask.array as da_
import pandas as pd
import rioxarray
from osgeo import gdal


def stat_fcc_loss(
        input_file,
        years,
        epsg,
        output_file="fcc_statistics.csv"):
    """Compute statistics per class for a TMF or GFC loss forest cover change raster.

    Reprojects the input raster to a metric CRS, then uses
    :func:`dask.array.bincount` to count pixels per class and converts
    counts to hectares. The input raster must be a single-band raster
    produced by :func:`sum_raster_bands` applied to the output of
    :func:`get_fcc_loss`.

    Pixel values encode the following classes:

    - 0 = non-forest at ``years[0]``
    - 1 = deforestation during period 1 (``years[0]``--``years[1]``)
    - 2 = deforestation during period 2 (``years[1]``--``years[2]``)
    - ... (one class per intermediate period)
    - n = forest at ``years[-1]``

    Parameters
    ----------
    input_file : str or Path
        Path to the single-band GeoTIFF raster file (in ``EPSG:4326``)
        produced by :func:`sum_raster_bands`.
    years : list of int
        List of years, e.g. ``[2000, 2010, 2020]``.
    epsg : int
        EPSG code of a metric CRS (e.g. ``32740`` for UTM zone 40S).
    output_file : str or Path, optional
        Path to the output CSV file. Default is ``"fcc_statistics.csv"``.

    Returns
    -------
    pandas.DataFrame
        DataFrame with columns ``category``, ``label``, ``count``,
        ``area_ha``. Also written to ``output_file``.

    Examples
    --------
    >>> import geefcc
    >>> res_df = geefcc.stat_fcc_loss(
    ...     input_file="out_tmf/fcc_tmf.tif",
    ...     years=[2000, 2010, 2020],
    ...     epsg=32740,
    ...     output_file="fcc_statistics.csv",
    ... )
    """

    input_file = Path(input_file)
    output_file = Path(output_file)

    # Build labels from years
    n_periods = len(years) - 1
    n_classes = len(years) + 1
    labels = {0: f"non-forest in {years[0]}"}
    for i in range(n_periods):
        labels[i + 1] = f"deforestation {years[i]}-{years[i + 1]}"
    labels[n_periods + 1] = f"forest in {years[-1]}"

    # Reproject to metric CRS at 30 m resolution
    proj_file = input_file.with_stem(input_file.stem + f"_epsg{epsg}")
    if not proj_file.is_file():
        ds = gdal.Warp(
            str(proj_file), str(input_file),
            xRes=30, yRes=30,
            dstSRS=f"EPSG:{epsg}",
            resampleAlg="near",
            targetAlignedPixels=True,
            creationOptions=["COMPRESS=DEFLATE"],
        )
        ds = None

    # Count pixels per class with dask bincount
    fcc = rioxarray.open_rasterio(str(proj_file),
                                  chunks={"x": 512, "y": 512})
    x_res, y_res = fcc.rio.resolution()
    pixel_area_m2 = abs(x_res) * abs(y_res)
    fcc_flat = fcc.data.ravel()
    counts = da_.bincount(fcc_flat, minlength=n_classes).compute()
    counts = counts[:n_classes]

    # Build DataFrame
    categories = list(range(n_classes))
    res_df = pd.DataFrame({
        "category": categories,
        "label": [labels[i] for i in categories],
        "count": counts,
        "area_ha": (
            (counts * pixel_area_m2 / 10_000).round().astype(int)
        ),
    })

    res_df.to_csv(str(output_file), index=False)
    return res_df

# End
