"""Compute fcc on GEE using the GFC product."""

import ee


def ee_gfc(years, perc):
    """Compute fcc on GEE using the GFC product.

    :param years: List of years defining time-periods for estimating
        forest cover change. Years for computing forest cover change
        can be in the interval 2001--2024 for GFC (GFC does not
        provide loss for the year 2000) and 2000--2023 for TMF.

    :param perc: Tree cover threshold defining the forest for GFC
        product.

    :return: An image collection for forest where each image
        correspond to a year.

    """

    # Hansen map
    gfc = ee.Image("UMD/hansen/global_forest_change_2023_v1_11")

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
