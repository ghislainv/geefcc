"""Compute statistics per class for a TMF loss and gain forest cover change raster."""

from pathlib import Path

import dask.array as da_
import pandas as pd
import rioxarray
from osgeo import gdal


# Class labels for the TMF loss and gain product
FCC_LABELS = {
    0: "stable non-forest",
    1: "stable forest",
    2: "forest --> deforested",
    3: "non-forest --> old regrowth",
    4: "forest --> old regrowth (via deforestation)",
    5: "stable old-regrowth",
    6: "old regrowth --> deforested",
}


def stat_fcc_loss_gain(
        input_file,
        epsg,
        output_file="fcc_statistics.csv"):
    """Compute statistics per class for a TMF loss and gain forest cover change raster.

    Reprojects the input raster to a metric CRS, then uses
    :func:`dask.array.bincount` to count pixels per class and converts
    counts to hectares.

    The seven transition classes produced by :func:`get_fcc_loss_gain`
    are:

    - 0 = stable non-forest
    - 1 = stable forest
    - 2 = forest to deforested
    - 3 = non-forest to old regrowth
    - 4 = forest to old regrowth (via deforestation)
    - 5 = stable old regrowth
    - 6 = old regrowth to deforested

    Parameters
    ----------
    input_file : str or Path
        Path to the input GeoTIFF raster file (in ``EPSG:4326``) produced
        by :func:`get_fcc_loss_gain`.
    epsg : int
        EPSG code of a metric CRS (e.g. ``32740`` for UTM zone 40S).
    output_file : str or Path, optional
        Path to the output CSV file. Default is ``"fcc_statistics.csv"``.

    Returns
    -------
    pandas.DataFrame
        DataFrame with columns ``category``, ``label``, ``count``,
        ``area_ha``. All seven classes included. Also written to
        ``output_file``.

    Notes
    -----
    The reprojected raster is saved alongside the input file (suffix
    ``_epsg<EPSG>.tif``) and reused on subsequent calls.

    Examples
    --------
    >>> import geefcc
    >>> res_df = geefcc.stat_fcc_loss_gain(
    ...     input_file="out_tmf_5yr/fcc_tmf.tif",
    ...     epsg=32740,
    ...     output_file="fcc_statistics.csv",
    ... )
    """

    input_file = Path(input_file)
    output_file = Path(output_file)

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
    counts = da_.bincount(fcc_flat, minlength=7).compute()

    # Build DataFrame
    res_df = pd.DataFrame({
        "category": list(FCC_LABELS.keys()),
        "label": list(FCC_LABELS.values()),
        "count": counts,
        "area_ha": (
            (counts * pixel_area_m2 / 10_000).round().astype(int)
        ),
    })

    res_df.to_csv(str(output_file), index=False)
    return res_df

# End
