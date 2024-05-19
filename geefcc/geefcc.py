#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ==============================================================================
# author          :Ghislain Vieilledent
# email           :ghislain.vieilledent@cirad.fr, ghislainv@gmail.com
# web             :https://ecology.ghislainv.fr
# python_version  :>=2.7
# license         :GPLv3
# ==============================================================================

import geefcc


def main():
    """geefcc.geefcc: provides entry point main().

    Running ``geefcc`` in the terminal prints ``geefcc``
    description and version. Can be used to check that the
    ``geefcc`` Python package has been correctly imported.

    """

    print(geefcc.__doc__)
    print(f"version {geefcc.__version__}.")


# End
