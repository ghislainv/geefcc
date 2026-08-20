"""Get the extent of a shapefile."""

from osgeo import ogr


def get_vector_extent(input_file):
    """Compute the extent of a vector file.

    This function computes the extent (xmin, ymin, xmax, ymax) of a
    shapefile.

    Parameters
    ----------
    input_file : str
        Path to the input vector file.

    Returns
    -------
    tuple of float
        The extent as a tuple (xmin, ymin, xmax, ymax).

    Raises
    ------
    AttributeError
        If the input file cannot be opened or the layer cannot be retrieved.

    Notes
    -----
    The function uses the OGR library to open the vector file and retrieve
    the extent of its first layer. The extent is returned in the order
    (xmin, ymin, xmax, ymax), which differs from the OGR convention of
    (xmin, xmax, ymin, ymax).

    Examples
    --------
    >>> from forestatrisk import get_vector_extent
    >>> extent = get_vector_extent("myfile.shp")
    >>> print(extent)
    (-180.0, -90.0, 180.0, 90.0)

    """

    in_data_source = ogr.Open(input_file)
    in_layer = in_data_source.GetLayer()
    extent = in_layer.GetExtent()
    extent = (extent[0], extent[2], extent[1], extent[3])
    in_data_source = None  # Close OGR object

    return extent  # (xmin, ymin, xmax, ymax)

# End
