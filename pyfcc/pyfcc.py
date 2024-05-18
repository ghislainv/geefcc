#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ==============================================================================
# author          :Ghislain Vieilledent
# email           :ghislain.vieilledent@cirad.fr, ghislainv@gmail.com
# web             :https://ecology.ghislainv.fr
# python_version  :>=2.7
# license         :GPLv3
# ==============================================================================

import pyfcc


def main():
    """pyfcc.pyfcc: provides entry point main().

    Running ``pyfcc`` in the terminal prints ``pyfcc``
    description and version. Can be used to check that the
    ``pyfcc`` Python package has been correctly imported.

    """

    print(pyfcc.__doc__)
    print(f"version {pyfcc.__version__}.")


# End
