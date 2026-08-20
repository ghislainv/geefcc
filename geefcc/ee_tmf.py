"""Compute fcc on GEE using the TMF product."""

import ee


def ee_tmf(years):
    """Compute fcc on GEE using the TMF product.

    TMF product documentation is available here:
    `https://forobs.jrc.ec.europa.eu/TMF`_.

    Parameters
    ----------
    years : list of int
        List of years defining time-periods for estimating forest cover
        change. Years for computing forest cover change can be in the
        interval 2000--2026 for TMF.

    Returns
    -------
    ee.ImageCollection
        An image collection for forest where each image corresponds to a
        year. Each image contains a single band named ``"forest_cover"``
        with byte values (1 = forest, 0 = non-forest) and has
        ``system:time_start`` set to January 1st of the corresponding
        year.

    Raises
    ------
    ee.EEException
        If the Earth Engine session is not authenticated or if the TMF
        asset cannot be accessed.

    Notes
    -----
    The Tropical Moist Forest (TMF) annual change product assigns class
    values to each pixel for every year since 1990. Classes 1 and 2
    correspond to undisturbed and degraded tropical moist forest,
    respectively. This function remaps both classes to 1 (forest) and
    all other classes to 0 (non-forest).

    For a given target ``year``, a pixel is considered forested if it
    was classified as forest (class 1 or 2) in **at least one** of the
    annual layers spanning from ``year - 1`` up to the TMF product
    version year (2025). This cumulative logic is applied via
    ``ee.Reducer.sum().gte(1)``.

    The function uses the TMF version ``v1_2025``. The earliest
    supported target year is 2001 (i.e., ``year_start + 1 = 1991``
    offset applied internally).

    Examples
    --------
    Compute forest cover for the years 2000, 2010, and 2020:

    >>> import ee
    >>> ee.Initialize()
    >>> years = [2000, 2010, 2020]
    >>> forest_ic = ee_tmf(years)
    >>> print(forest_ic.size().getInfo())
    3

    Retrieve band names of the first image in the collection:

    >>> first = ee.Image(forest_ic.first())
    >>> print(first.bandNames().getInfo())
    ['forest_cover']
    """

    # Get annual product
    year_version = 2025
    tmf_version = f"v1_{year_version}"
    annual_product = ee.ImageCollection(
        "projects/JRC/TMF/"
        f"{tmf_version}/AnnualChanges")
    annual_product = annual_product.mosaic().toByte()

    # ap_all_year: forest if Y = 1 or 2.
    ap_forest = annual_product.where(annual_product.eq(2), 1)
    ap_all_year = ap_forest.where(ap_forest.neq(1), 0)

    # Forest list
    forest_list = []

    for year in years:
        # Get forest
        year_start = 1990
        id_year = year - year_start - 1
        ap = ap_all_year.select(
            list(range(id_year, year_version - year_start))
        )
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
        """Get formatted date.

        Parameters
        ----------
        image : ee.Image
            An Earth Engine image with a valid ``system:time_start``
            property.

        Returns
        -------
        ee.String
            The image acquisition date formatted as ``"YYYY-MM-dd"``.
        """
        date = ee.Image(image).date().format("YYYY-MM-dd")
        return date

    def filter_and_mosaic(d):
        """Create mosaic for one date.

        Parameters
        ----------
        d : ee.Date or str
            The date for which to filter the image collection and
            create a mosaic. Only images whose ``system:time_start``
            falls within the single day starting at ``d`` are included.

        Returns
        -------
        ee.Image
            A mosaicked byte image for the given date with
            ``system:time_start`` and ``system:id`` properties set.
        """
        d = ee.Date(d)
        im = (forest_ic
              .filterDate(d, d.advance(1, "day"))
              .mosaic().toByte())
        im = im.set("system:time_start", d.millis(),
                    "system:id", d.format("YYYY-MM-dd"))
        return im

    def mosaic_by_date(img_list):
        """Mosaic by date.

        Parameters
        ----------
        img_list : ee.List
            A list of ``ee.Image`` objects, potentially containing
            multiple images for the same date.

        Returns
        -------
        ee.ImageCollection
            An image collection in which each image is a mosaic of all
            input images sharing the same acquisition date.
        """
        unique_dates = img_list.map(get_date).distinct()
        mosaic_list = unique_dates.map(filter_and_mosaic)
        return ee.ImageCollection(mosaic_list)

    forest = mosaic_by_date(ee.List(forest_list))

    return forest

# End
