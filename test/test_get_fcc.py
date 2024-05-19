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
import os.path
from geefcc import get_fcc


# test_get_fcc
def test_get_fcc():
    # get_fcc(source="tmf",
    #     iso="REU",
    #     years=[2000, 2010, 2020],
    #     ee_project="forestatrisk")
    tmp = get_fcc()
    # assert os.path.isfile("fcc_tmf_REU_2000_2010_2020.shp")
    assert tmp == "get_fcc"

# End
