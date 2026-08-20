"""Test for get_fcc_loss_gain()."""

import os

import geefcc as gf

# Initialize GEE
# "EARTHENGINE_TOKEN" for GitHub actions
# https://github.com/gee-community/geemap/discussions/1341
gf.ee_initialize(
    token_name="EARTHENGINE_TOKEN",
    project="deforisk",
    opt_url="https://earthengine-highvolume.googleapis.com")


def test_get_fcc_loss_gain_extent_tmf():
    """
    Test get_fcc_loss_gain() using a bounding box as aoi.

    Parameters
    ----------
    None

    Returns
    -------
    None

    Raises
    ------
    AssertionError
        If the output file ``out_tmf_loss_gain/fcc_tmf.tif`` does not
        exist after calling ``get_fcc_loss_gain()``.

    Notes
    -----
    Uses a bounding box corresponding to Singapore as the area of
    interest. Singapore is small (fast to download) and surrounded
    by the dense forests of Malaysia and Indonesia (Borneo), making
    it a meaningful test case for forest cover change detection.
    The output raster is written to ``out_tmf_loss_gain/fcc_tmf.tif``.

    Examples
    --------
    >>> test_get_fcc_loss_gain_extent_tmf()
    """
    gf.get_fcc_loss_gain(
        # Extent for Singapore
        aoi=(103.6, 1.15, 104.1, 1.48),
        buff=0,
        year1=2010,
        year2=2020,
        min_years=10,
        tile_size=0.5,
        output_file="out_tmf_loss_gain/fcc_tmf.tif",
    )
    assert os.path.isfile("out_tmf_loss_gain/fcc_tmf.tif")


def test_get_fcc_loss_gain_gpkg_crop_to_aoi():
    """
    Test get_fcc_loss_gain() with a GeoPackage aoi and crop_to_aoi=True.

    Parameters
    ----------
    None

    Returns
    -------
    None

    Raises
    ------
    AssertionError
        If the output file ``out_tmf_loss_gain_crop/fcc_tmf.tif`` does
        not exist after calling ``get_fcc_loss_gain()``.

    Notes
    -----
    Uses a local Singapore GeoPackage border file (``data/gadm41_SGP_0.gpkg``)
    as the area of interest, with the output cropped to the exact AOI
    contour. This is the meaningful use case for crop_to_aoi=True, as it
    clips the raster to the actual polygon boundary rather than a bounding
    box, excluding the surrounding Malaysian and Indonesian forests.

    The border file is stored locally in ``test/data/`` to avoid
    dependency on the GADM download server, which can be unreliable.

    Examples
    --------
    >>> test_get_fcc_loss_gain_gpkg_crop_to_aoi()
    """
    gf.get_fcc_loss_gain(
        aoi="data/gadm41_SGP_0.gpkg",
        buff=0,
        year1=2010,
        year2=2020,
        min_years=10,
        tile_size=0.5,
        crop_to_aoi=True,
        output_file="out_tmf_loss_gain_crop/fcc_tmf.tif",
    )
    assert os.path.isfile("out_tmf_loss_gain_crop/fcc_tmf.tif")

# End
