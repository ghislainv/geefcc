"""Compute fcc on GEE using the TMF product."""

import ee


def ee_tmf(years):
    """Compute fcc on GEE using the TMF product."""

    year_version = 2025
    tmf_version = f"v1_{year_version}"
    annual_product = ee.ImageCollection(
        "projects/JRC/TMF/"
        f"{tmf_version}/AnnualChanges")
    annual_product = annual_product.mosaic().toByte()

    ap_forest = annual_product.where(annual_product.eq(2), 1)
    ap_all_year = ap_forest.where(ap_forest.neq(1), 0)

    forest_list = []

    for year in years:
        year_start = 1990
        id_year = year - year_start - 1
        ap = ap_all_year.select(
            list(range(id_year, year_version - year_start))
        )
        forest_yr = ap.reduce(ee.Reducer.sum()).gte(1)
        forest_yr = forest_yr.set(
            "system:time_start",
            ee.Date.fromYMD(year, 1, 1).millis())
        forest_yr = forest_yr.rename(["forest_cover"])
        forest_list.append(forest_yr)

    forest_ic = ee.ImageCollection(forest_list)

    def get_date(image):
        return ee.Image(image).date().format("YYYY-MM-dd")

    def filter_and_mosaic(d):
        d = ee.Date(d)
        im = (forest_ic
              .filterDate(d, d.advance(1, "day"))
              .mosaic().toByte())
        im = im.set("system:time_start", d.millis(),
                    "system:id", d.format("YYYY-MM-dd"))
        return im

    def mosaic_by_date(img_list):
        unique_dates = img_list.map(get_date).distinct()
        mosaic_list = unique_dates.map(filter_and_mosaic)
        return ee.ImageCollection(mosaic_list)

    forest = mosaic_by_date(ee.List(forest_list))

    return forest

# End
