#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ==============================================================================
# author          :Ghislain Vieilledent
# email           :ghislain.vieilledent@cirad.fr, ghislainv@gmail.com
# web             :https://ecology.ghislainv.fr
# python_version  :>=2.7
# license         :GPLv3
# ==============================================================================

import sys

from .get_wdpa import get_wdpa

__version__ = "0.1.5"


def main():
    """
    pywdpa.pywdpa: provides entry point main().
    """
    isocode = sys.argv[1]
    print("Executing pywdpa version {}.".format(__version__))
    print("For country with isocode: {}.".format(isocode))
    get_wdpa(isocode)
    return None

# End
