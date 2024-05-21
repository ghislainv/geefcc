#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ==============================================================================
# author          :Ghislain Vieilledent
# email           :ghislain.vieilledent@cirad.fr, ghislainv@gmail.com
# web             :https://ecology.ghislainv.fr
# python_version  :>=2.7
# license         :GPLv3
# ==============================================================================

# Import
import os

from geefcc import get_fcc, ee_initialize

# "EARTHENGINE_TOKEN"
# https://github.com/gee-community/geemap/discussions/1341
# Find the Earth Engine credentials file on your computer.
# Open the credentials file and copy its content.
# On the GitHub Actions page, create a new secret
# with the name EARTHENGINE_TOKEN.

# Initialize GEE
ee_initialize(
    token_name="EARTHENGINE_TOKEN",
    project="forestatrisk",
    opt_url="https://earthengine-highvolume.googleapis.com")


def test_get_fcc():
    """Testing get_fcc()."""
    get_fcc(
        # Extent for Reunion Island
        aoi=(55.21625137, -21.38986015, 55.83736038, -20.87180519),
        buff=0.08983152841195216,
        years=[2000, 2010, 2020],
        source="tmf",
        perc=75,
        tile_size=0.5,
        output_file="fcc.tiff",
    )
    assert os.path.isfile("fcc.tiff")

# End
