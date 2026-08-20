"""Test for get_fcc_loss()."""

from pathlib import Path

import geefcc as gf

# "EARTHENGINE_TOKEN" for GitHub actions
# https://github.com/gee-community/geemap/discussions/1341
# Find the Earth Engine credentials file on your computer.
# Open the credentials file and copy its content.
# On the GitHub Actions page, create a new secret
# with the name EARTHENGINE_TOKEN.

# Initialize GEE
gf.ee_initialize(
    token_name="EARTHENGINE_TOKEN",
    project="deforisk",
    opt_url="https://earthengine-highvolume.googleapis.com")

# Directory of this test file
TEST_DIR = Path(__file__).parent


def test_get_fcc_extent_tmf():
    """
    Test get_fcc_loss() using the Tropical Moist Forest (TMF) source.

    Parameters
    ----------
    None

    Returns
    -------
    None

    Raises
    ------
    AssertionError
        If the output file ``out_tmf/fcc_tmf.tif`` does not exist after
        calling ``get_fcc_loss()``.

    Notes
    -----
    Uses a bounding box corresponding to Reunion Island as the area of
    interest. The TMF (Tropical Moist Forest) dataset is used as the
    forest cover change source. The output raster is written to
    ``out_tmf/fcc_tmf.tif``.

    Examples
    --------
    >>> test_get_fcc_extent_tmf()
    """
    gf.get_fcc_loss(
        # Extent for Reunion Island
        aoi=(55.21625137, -21.38986015, 55.83736038, -20.87180519),
        buff=0.08983152841195216,
        years=[2000, 2010, 2020],
        source="tmf",
        tile_size=0.5,
        output_file=TEST_DIR / "out_tmf/fcc_tmf.tif",
    )
    assert (TEST_DIR / "out_tmf/fcc_tmf.tif").is_file()


def test_get_fcc_extent_gfc():
    """
    Test get_fcc_loss() using the Global Forest Change (GFC) source.

    Parameters
    ----------
    None

    Returns
    -------
    None

    Raises
    ------
    AssertionError
        If the output file ``out_gfc_50/fcc_gfc_50.tif`` does not exist
        after calling ``get_fcc_loss()``.

    Notes
    -----
    Uses a bounding box corresponding to Reunion Island as the area of
    interest. The GFC (Global Forest Change) dataset is used as the
    forest cover change source, with a canopy cover threshold of 50
    percent (``perc=50``). The output raster is written to
    ``out_gfc_50/fcc_gfc_50.tif``.

    Examples
    --------
    >>> test_get_fcc_extent_gfc()
    """
    gf.get_fcc_loss(
        # Extent for Reunion Island
        aoi=(55.21625137, -21.38986015, 55.83736038, -20.87180519),
        buff=0.08983152841195216,
        years=[2001, 2010, 2020],
        source="gfc",
        perc=50,
        tile_size=0.5,
        output_file=TEST_DIR / "out_gfc_50/fcc_gfc_50.tif",
    )
    assert (TEST_DIR / "out_gfc_50/fcc_gfc_50.tif").is_file()

# End
