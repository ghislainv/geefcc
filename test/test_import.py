#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ==============================================================================
# author          :Ghislain Vieilledent
# email           :ghislain.vieilledent@cirad.fr, ghislainv@gmail.com
# web             :https://ecology.ghislainv.fr
# python_version  :>=2.7
# license         :GPLv3
# ==============================================================================


# test_import
def test_import():
    """
    Test that the geefcc package can be successfully imported.

    Parameters
    ----------
    None

    Returns
    -------
    None
        This function does not return a value. It uses an assertion
        to verify that the import was successful.

    Raises
    ------
    AssertionError
        If the geefcc package cannot be imported, the assertion
        ``imp is True`` will fail, raising an AssertionError.

    Notes
    -----
    This function attempts to import the ``geefcc`` package and sets
    a boolean flag ``imp`` to ``True`` if the import succeeds, or
    ``False`` if an ``ImportError`` is raised. The test passes only
    when ``geefcc`` is installed and importable in the current
    Python environment.

    Examples
    --------
    >>> test_import()
    # Passes silently if geefcc is installed, raises AssertionError otherwise.
    """
    imp = True
    try:
        import geefcc
    except ImportError:
        imp = False
    assert imp is True

# End
