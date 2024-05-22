"""Compute fcc on GEE using the TMF product."""

import ee


def ee_tmf(years):
    """Compute fcc on GEE using the TMF product.

    :param years: List of years defining time-periods for estimating
        forest cover change. Years for computing forest cover change
        can be in the interval 2001--2024 for GFC (GFC does not
        provide loss for the year 2000) and 2000--2023 for TMF.

    :return: An image collection for forest where each image
        correspond to a year.

    """

    # Get annual product
    annual_product = ee.ImageCollection(
        "projects/JRC/TMF/"
        "v1_2022/AnnualChanges")
    annual_product = annual_product.mosaic().toByte()

    # ap_all_year: forest if Y = 1 or 2.
    ap_forest = annual_product.where(annual_product.eq(2), 1)
    ap_all_year = ap_forest.where(ap_forest.neq(1), 0)

    # Forest list
    forest_list = []

    for year in years:
        # Get forest
        id_year = year - 1990 - 1
        ap = ap_all_year.select(list(range(id_year, 33)))
        forest_yr = ap.reduce(ee.Reducer.sum()).gte(1)
        # Set time
        forest_yr = forest_yr.set(
            "system:time_start",
            ee.Date.fromYMD(year, 1, 1).millis())
        # Rename band
        forest_yr = forest_yr.rename(["forest_cover"])
        # Append to list
        forest_list.append(forest_yr)

    forest_ic = ee.ImageCollection(forest_list)

    def get_date(image):
        """Get formatted date."""
        date = ee.Image(image).date().format("YYYY-MM-dd")
        return date

    def filter_and_mosaic(d):
        """Create mosaic for one date."""
        d = ee.Date(d)
        im = (forest_ic
              .filterDate(d, d.advance(1, "day"))
              .mosaic().toByte())
        im = im.set("system:time_start", d.millis(),
                    "system:id", d.format("YYYY-MM-dd"))
        return im

    def mosaic_by_date(img_list):
        """Mosaic by date."""
        unique_dates = img_list.map(get_date).distinct()
        mosaic_list = unique_dates.map(filter_and_mosaic)
        return ee.ImageCollection(mosaic_list)

    forest = mosaic_by_date(ee.List(forest_list))

    return forest


# End
