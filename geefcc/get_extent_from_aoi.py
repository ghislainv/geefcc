"""Get extent from aoi."""

import os

from .download_gadm import download_gadm
from .make_grid import create_buffer
from .get_vector_extent import get_vector_extent

opj = os.path.join
opd = os.path.dirname


def get_extent_from_aoi(aoi, buff, out_dir):
    """Get extent from aoi.

    Parameters
    ----------
    aoi : str or tuple
        Area of interest defined either by a country ISO code (three
        letters), a path to a vector file in GeoPackage format
        (``.gpkg``), or an extent in lat/long coordinates as a tuple
        with ``(xmin, ymin, xmax, ymax)``.
    buff : float
        Buffer around the aoi in decimal degrees. For example,
        ``0.08983152841195216`` corresponds to approximately 10 km at
        the equator. Use ``0`` to apply no buffer.
    out_dir : str
        Path to the output directory where intermediate and result files
        will be saved.

    Returns
    -------
    dict
        A dictionary with the following keys:

        - ``"extent_latlong"`` : tuple of float
            The bounding box of the aoi (with buffer if applicable) as
            ``(xmin, ymin, xmax, ymax)`` in decimal degrees.
        - ``"borders_gpkg"`` : str or None
            Path to the borders GeoPackage file (with buffer if
            applicable). ``None`` when ``aoi`` is provided as a tuple
            extent.
        - ``"aoi_isfile"`` : bool
            ``True`` if the aoi was defined by a country ISO code or a
            vector file, ``False`` if it was defined as a tuple extent.

    Raises
    ------
    ValueError
        If ``aoi`` is not a valid country ISO code (three-letter
        string), a tuple of four coordinates, or a path to an existing
        ``.gpkg`` file.

    Notes
    -----
    - When ``aoi`` is a three-letter country ISO code, the GADM borders
      are downloaded automatically using :func:`download_gadm` and
      saved to ``out_dir``.
    - When ``aoi`` is a tuple, no vector border file is created; the
      buffer is applied directly to the coordinate values.
    - When ``aoi`` is a ``.gpkg`` file and ``buff > 0``, a buffered
      copy is saved as ``borders_buffer.gpkg`` inside ``out_dir``.

    Examples
    --------
    Using a country ISO code:

    >>> result = get_extent_from_aoi("BRA", buff=0.1, out_dir="/tmp")
    >>> result["extent_latlong"]
    (-73.9904, -33.7517, -28.6481, 5.2717)

    Using a tuple extent with no buffer:

    >>> result = get_extent_from_aoi(
    ...     (-10.0, -5.0, 10.0, 5.0), buff=0, out_dir="/tmp"
    ... )
    >>> result["borders_gpkg"] is None
    True

    Using a GeoPackage file:

    >>> result = get_extent_from_aoi(
    ...     "/data/my_area.gpkg", buff=0.05, out_dir="/tmp"
    ... )
    >>> result["aoi_isfile"]
    True
    """

    # Set aoi_isfile
    aoi_isfile = True

    # aoi = country iso code
    if isinstance(aoi, str) and len(aoi) == 3:
        # Download borders
        iso = aoi
        borders_gpkg = opj(out_dir, f"gadm41_{iso}_0.gpkg")
        download_gadm(iso, output_file=borders_gpkg)
        # Buffer around borders
        if buff > 0:
            buff_file = opj(
                out_dir,
                f"gadm41_{iso}_buffer.gpkg")
            create_buffer(input_file=borders_gpkg,
                          output_file=buff_file,
                          buffer_dist=buff)
            borders_gpkg = buff_file
        # Extent
        extent_latlong = get_vector_extent(borders_gpkg)

    # aoi = extent
    elif isinstance(aoi, tuple) and len(aoi) == 4:
        xmin, ymin, xmax, ymax = aoi
        if xmin >= xmax or ymin >= ymax:
            raise ValueError("Invalid extent: xmin >= xmax or ymin >= ymax")
        if not (-180 <= xmin <= 180 and -90 <= ymin <= 90):
            raise ValueError("Coordinates out of lat/long bounds")
        aoi_isfile = False
        # nb: We could create a vector file here...
        borders_gpkg = None
        if buff > 0:
            extent_latlong = (aoi[0] - buff, aoi[1] - buff,
                              aoi[2] + buff, aoi[3] + buff)
        else:
            extent_latlong = aoi

    # aoi = gpkg file
    elif os.path.isfile(aoi) and aoi[-5:] == ".gpkg":
        # Buffer around borders
        if buff > 0:
            buff_file = opj(
                out_dir,
                "borders_buffer.gpkg")
            create_buffer(input_file=aoi,
                          output_file=buff_file,
                          buffer_dist=buff)
            borders_gpkg = buff_file
        else:
            borders_gpkg = aoi
        # Extent
        extent_latlong = get_vector_extent(borders_gpkg)

    # Else raise error
    else:
        raise ValueError("aoi must be either a country iso code, "
                         "an extent, or a gpkg file")

    return {"extent_latlong": extent_latlong,
            "borders_gpkg": borders_gpkg,
            "aoi_isfile": aoi_isfile}


# End
