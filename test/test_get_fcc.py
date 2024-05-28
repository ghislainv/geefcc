"""Test for gee_fcc()."""

# Import
import os

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
    project="forestatrisk",
    opt_url="https://earthengine-highvolume.googleapis.com")


def test_get_fcc_extent_tmf():
    """Testing get_fcc()."""
    gf.get_fcc(
        # Extent for Reunion Island
        aoi=(55.21625137, -21.38986015, 55.83736038, -20.87180519),
        buff=0.08983152841195216,
        years=[2000, 2010, 2020],
        source="tmf",
        tile_size=0.5,
        output_file="out_tmf/fcc_tmf.tif",
    )
    assert os.path.isfile("out_tmf/fcc_tmf.tif")


def test_get_fcc_extent_gfc():
    """Testing get_fcc()."""
    gf.get_fcc(
        # Extent for Reunion Island
        aoi=(55.21625137, -21.38986015, 55.83736038, -20.87180519),
        buff=0.08983152841195216,
        years=[2001, 2010, 2020],
        source="gfc",
        perc=50,
        tile_size=0.5,
        output_file="out_gfc_50/fcc_gfc_50.tif",
    )
    assert os.path.isfile("out_gfc_50/fcc_gfc_50.tif")

# End
