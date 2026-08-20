"""Provide entry point main() for geefcc."""

import geefcc


def main():
    """Provide entry point main() for geefcc.

    Running ``geefcc`` in the terminal prints ``geefcc``
    description and version. Can be used to check that the
    ``geefcc`` Python package has been correctly imported.

    Parameters
    ----------
    None

    Returns
    -------
    None
        This function prints to standard output and returns nothing.

    Raises
    ------
    ImportError
        If the ``geefcc`` package has not been correctly installed
        or cannot be imported.

    Notes
    -----
    This function is intended to be used as a command-line entry point.
    It prints the module-level docstring of ``geefcc`` followed by its
    version string. It does not perform any computation or file I/O.

    Examples
    --------
    To run from the terminal after installing the package:

    .. code-block:: bash

        $ geefcc

    To call programmatically from Python:

    >>> from geefcc.geefcc import main
    >>> main()  # doctest: +SKIP
    """

    print(geefcc.__doc__)
    print(f"version {geefcc.__version__}.")

# End
