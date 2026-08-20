"""Get extent from aoi."""

from pathlib import Path

from .download_gadm import download_gadm
from .make_grid import create_buffer
from .get_vector_extent import get_vector_extent


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
    out_dir : str or Path
        Path to the output directory where intermediate and result files
        will be saved.

    Returns
    -------
    dict
        A dictionary with the following keys:

        - ``"extent_latlong"`` : tuple of float
            The bounding box of the aoi (with buffer if applicable) as
            ``(xmin, ymin, xmax, ymax)`` in decimal degrees.
        - ``"borders_gpkg"`` : Path or None
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
        ``.gpkg`` file. Also raised if the tuple extent has invalid
        coordinates (e.g. xmin >= xmax, or values out of lat/long
        bounds).

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

    out_dir = Path(out_dir)

    # Set aoi_isfile
    aoi_isfile = True

    # aoi = country iso code
    if isinstance(aoi, str) and len(aoi) == 3:
        iso = aoi
        borders_gpkg = out_dir / f"gadm41_{iso}_0.gpkg"
        download_gadm(iso, output_file=borders_gpkg)
        # Buffer around borders
        if buff > 0:
            buff_file = out_dir / f"gadm41_{iso}_buffer.gpkg"
            create_buffer(input_file=borders_gpkg,
                          output_file=buff_file,
                          buffer_dist=buff)
            borders_gpkg = buff_file
        # Extent
        extent_latlong = get_vector_extent(borders_gpkg)

    # aoi = extent
    elif isinstance(aoi, tuple) and len(aoi) == 4:
        aoi_isfile = False
        borders_gpkg = None
        xmin, ymin, xmax, ymax = aoi
        # Validate coordinates
        if xmin >= xmax:
            raise ValueError(
                f"Invalid extent: xmin ({xmin}) must be less than xmax ({xmax}).")
        if ymin >= ymax:
            raise ValueError(
                f"Invalid extent: ymin ({ymin}) must be less than ymax ({ymax}).")
        if not (-180 <= xmin <= 180 and -180 <= xmax <= 180):
            raise ValueError(
                f"Invalid extent: xmin ({xmin}) and xmax ({xmax}) "
                "must be in the range [-180, 180].")
        if not (-90 <= ymin <= 90 and -90 <= ymax <= 90):
            raise ValueError(
                f"Invalid extent: ymin ({ymin}) and ymax ({ymax}) "
                "must be in the range [-90, 90].")
        # Apply buffer
        if buff > 0:
            extent_latlong = (xmin - buff, ymin - buff,
                              xmax + buff, ymax + buff)
        else:
            extent_latlong = aoi

    # aoi = gpkg file (only check Path compatibility for str/Path types)
    elif isinstance(aoi, (str, Path)) and Path(aoi).is_file() \
            and Path(aoi).suffix == ".gpkg":
        aoi = Path(aoi)
        if buff > 0:
            buff_file = out_dir / "borders_buffer.gpkg"
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
