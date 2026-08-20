"""Compute fcc on GEE using the GFC product."""

import ee


def ee_gfc(years, perc):
    """Compute fcc on GEE using the GFC product.

    GFC product documentation is available here:
    `https://developers.google.com/earth-engine/datasets/catalog/\
    UMD_hansen_global_forest_change_2025_v1_13`_.

    Parameters
    ----------
    years : list of int
        List of years defining time-periods for estimating forest cover
        change. Years for computing forest cover change can be in the
        interval 2001--2025 for GFC (GFC does not provide loss for the
        year 2000).
    perc : int or float
        Tree cover threshold defining the forest for GFC product.

    Returns
    -------
    ee.ImageCollection
        An image collection for forest where each image corresponds to
        a year. Each image contains a single band named ``forest_cover``
        and has the ``system:time_start`` and ``system:id`` properties
        set to the first of January of the corresponding year.

    Notes
    -----
    The function uses the Hansen Global Forest Change product version
    2025 v1.13. Forest cover at the end of year 2000 is derived from
    the ``treecover2000`` band by applying the ``perc`` threshold.
    Subsequent yearly forest maps are obtained by masking out pixels
    where tree cover loss occurred up to (but not including) the given
    year, using the ``lossyear`` band.

    Examples
    --------
    >>> import ee
    >>> ee.Initialize()
    >>> years = [2001, 2005, 2010]
    >>> perc = 75
    >>> forest_collection = ee_gfc(years, perc)
    >>> forest_collection.size().getInfo()
    3

    """

    # Hansen map
    year_version = 2025
    gfc_version = f"{year_version}_v1_13"
    gfc = ee.Image(f"UMD/hansen/global_forest_change_{gfc_version}")

    # Tree cover, loss, and gain
    treecover = gfc.select(["treecover2000"])
    lossyear = gfc.select(["lossyear"])

    # Forest at end of year 2000
    forest2000 = treecover.gte(perc)
    forest2000 = forest2000.toByte()

    # Forest list
    forest_list = []

    # Loop on years
    for year in years:
        # Get forest
        if year == 2001:
            # On 1st of January
            forest_yr = forest2000
        elif year == 2002:
            loss_yr = lossyear.eq(1)
            forest_yr = forest2000.where(loss_yr.eq(1), 0)
        else:
            # Deforestation
            index = year - 2001
            loss_yr = lossyear.gte(1).And(lossyear.lte(index))
            # Forest
            forest_yr = forest2000.where(loss_yr.eq(1), 0)
        # Set time
        d = ee.Date.fromYMD(year, 1, 1)
        forest_yr = forest_yr.set(
            "system:time_start", d.millis(),
            "system:id", d.format("YYYY-MM-dd"))
        # Rename band
        forest_yr = forest_yr.rename(["forest_cover"])
        # Append to list
        forest_list.append(forest_yr)

    forest = ee.ImageCollection(forest_list)

    return forest

# End
