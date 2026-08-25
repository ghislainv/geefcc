"""Compute fcc on GEE using the GFC product."""

import ee


def ee_gfc(years, perc):
    """Compute fcc on GEE using the GFC product."""

    year_version = 2025
    gfc_version = f"{year_version}_v1_13"
    gfc = ee.Image(f"UMD/hansen/global_forest_change_{gfc_version}")

    treecover = gfc.select(["treecover2000"])
    lossyear = gfc.select(["lossyear"])

    forest2000 = treecover.gte(perc).toByte()

    forest_list = []

    for year in years:
        if year == 2001:
            forest_yr = forest2000
        elif year == 2002:
            loss_yr = lossyear.eq(1)
            forest_yr = forest2000.where(loss_yr.eq(1), 0)
        else:
            index = year - 2001
            loss_yr = lossyear.gte(1).And(lossyear.lte(index))
            forest_yr = forest2000.where(loss_yr.eq(1), 0)
        d = ee.Date.fromYMD(year, 1, 1)
        forest_yr = forest_yr.set(
            "system:time_start", d.millis(),
            "system:id", d.format("YYYY-MM-dd"))
        forest_yr = forest_yr.rename(["forest_cover"])
        forest_list.append(forest_yr)

    forest = ee.ImageCollection(forest_list)

    return forest

# End
