"""Get the extent of a vector file."""

from pathlib import Path

from osgeo import ogr


def get_vector_extent(input_file):
    """Compute the extent of a vector file.

    Parameters
    ----------
    input_file : str or Path
        Path to the input vector file.

    Returns
    -------
    tuple of float
        The extent as a tuple (xmin, ymin, xmax, ymax).

    Examples
    --------
    >>> extent = get_vector_extent("myfile.gpkg")
    >>> print(extent)
    (-180.0, -90.0, 180.0, 90.0)
    """

    in_data_source = ogr.Open(str(Path(input_file)))  # OGR requires str
    in_layer = in_data_source.GetLayer()
    extent = in_layer.GetExtent()
    in_data_source = None

    return (extent[0], extent[2], extent[1], extent[3])  # (xmin, ymin, xmax, ymax)

# End
