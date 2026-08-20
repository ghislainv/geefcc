"""Make minimal grid with buffer around polygons."""

import os

import numpy as np
from osgeo import ogr, osr


def create_buffer(input_file, output_file, buffer_dist):
    """Create buffer around features of a layer and save to a new layer.

    Make buffers around features of a layer and saves them to a new
    layer.

    Source: https://pcjericks.github.io/py-gdalogr-cookbook/
    vector_layers.html#create-buffer

    Parameters
    ----------
    input_file : str
        Input filename.
    output_file : str
        Output filename (`.gpkg`).
    buffer_dist : float
        Buffer distance (in unit of CRS).

    Returns
    -------
    None
        The buffered features are written directly to ``output_file``.

    Notes
    -----
    The output layer is created as a ``MultiPolygon`` geometry type.
    If ``output_file`` already exists, it will be deleted before
    creating a new one.

    Examples
    --------
    >>> create_buffer("input.gpkg", "output_buffer.gpkg", buffer_dist=100)
    """
    input_ds = ogr.Open(input_file)
    # Get first layer
    input_lyr = input_ds.GetLayer(0)

    driver = ogr.GetDriverByName("GPKG")
    if os.path.exists(output_file):
        driver.DeleteDataSource(output_file)
    output_ds = driver.CreateDataSource(output_file)
    # Must be MultiPolygon here
    lyr = output_ds.CreateLayer(
        "buffer",
        geom_type=ogr.wkbMultiPolygon)
    feature_defn = lyr.GetLayerDefn()

    for feature in input_lyr:
        in_geom = feature.GetGeometryRef()
        geom_buffer = in_geom.Buffer(buffer_dist)

        out_feature = ogr.Feature(feature_defn)
        out_feature.SetGeometry(geom_buffer)
        lyr.CreateFeature(out_feature)
        out_feature = None

    # Dereference
    input_ds = None
    output_ds = None


def gpkg_from_grid(grid, proj=4326, ofile="grid.gpkg"):
    """Make vector file from grid.

    Source: https://pcjericks.github.io/py-gdalogr-cookbook/
    vector_layers.html#create-fishnet-grid

    Parameters
    ----------
    grid : list of tuple of float
        List of extents ``(xmin, ymin, xmax, ymax)`` for each grid cell.
    proj : int, optional
        Projection as EPSG code, by default ``4326``.
    ofile : str, optional
        Output file path, by default ``"grid.gpkg"``.

    Returns
    -------
    None
        The grid is written directly to ``ofile``.

    Notes
    -----
    If ``ofile`` already exists, it will be removed before creating a
    new file. Each grid cell is stored as a ``Polygon`` feature with an
    integer ``id`` field.

    Examples
    --------
    >>> grid = [(0.0, 0.0, 1.0, 1.0), (1.0, 0.0, 2.0, 1.0)]
    >>> gpkg_from_grid(grid, proj=4326, ofile="grid.gpkg")
    """

    # Set up the shapefile driver
    driver = ogr.GetDriverByName("GPKG")

    # Create the data source
    if os.path.exists(ofile):
        os.remove(ofile)
    ds = driver.CreateDataSource(ofile)

    # Create the spatial reference system, WGS84
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(proj)

    # Create one layer
    layer = ds.CreateLayer("grid", srs, ogr.wkbPolygon)

    # Add an ID field
    id_field = ogr.FieldDefn("id", ogr.OFTInteger)
    layer.CreateField(id_field)

    # Feature definition
    feature_def = layer.GetLayerDefn()

    # Create grid cells
    for (i, coords) in enumerate(grid):
        # Get coordinates
        xmin = coords[0]
        ymin = coords[1]
        xmax = coords[2]
        ymax = coords[3]
        # Create geometry
        ring = ogr.Geometry(ogr.wkbLinearRing)
        ring.AddPoint(xmin, ymax)
        ring.AddPoint(xmax, ymax)
        ring.AddPoint(xmax, ymin)
        ring.AddPoint(xmin, ymin)
        ring.AddPoint(xmin, ymax)
        poly = ogr.Geometry(ogr.wkbPolygon)
        poly.AddGeometry(ring)
        # Add geometry to layer
        feature = ogr.Feature(feature_def)
        feature.SetGeometry(poly)
        feature.SetField("id", i)
        layer.CreateFeature(feature)
        feature = None

    # Dereference
    ds = None


def make_grid(extent, buff, tile_size, scale, proj=4326,
              ofile="grid.gpkg"):
    """Make overlapping grid from an extent and resolution.

    Parameters
    ----------
    extent : tuple of float
        Extent of the area of interest as ``(xmin, ymin, xmax, ymax)``.
    buff : float
        Buffer to add around the extent (same unit as ``extent``).
    tile_size : float
        Tile size for each grid cell (same unit as ``extent``).
    scale : float
        Resolution used to snap ``tile_size`` to a multiple of ``scale``
        (same unit as ``extent``).
    proj : int, optional
        Projection as EPSG code, by default ``4326``.
    ofile : str, optional
        Output file path, by default ``"grid.gpkg"``.

    Returns
    -------
    list of tuple of float
        List of extents ``(xmin, ymin, xmax, ymax)`` for each grid cell.

    Notes
    -----
    The ``tile_size`` is first rounded to the nearest multiple of
    ``scale`` before generating the grid coordinates. The resulting
    grid is also saved as a GeoPackage vector file via
    :func:`gpkg_from_grid`.

    Examples
    --------
    >>> extent = (0.0, 0.0, 10.0, 10.0)
    >>> grid = make_grid(extent, buff=1.0, tile_size=5.0,
    ...                  scale=1.0, proj=4326, ofile="grid.gpkg")
    >>> len(grid)
    4
    """

    # Buffer around extent
    xmin = extent[0] - buff
    ymin = extent[1] - buff
    xmax = extent[2] + buff
    ymax = extent[3] + buff
    # Adapt tile_size to scale
    tile_size = int(np.round(tile_size / scale)) * scale
    # List of x coordinates
    xlist = list(np.arange(xmin, xmax + tile_size, tile_size))
    nx = len(xlist)
    # List of y coordinates
    ylist = list(np.arange(ymin, ymax + tile_size, tile_size))
    ny = len(ylist)
    # Grid: list of extents
    grid = [(xlist[i], ylist[j], xlist[i + 1], ylist[j + 1])
            for i in range(nx - 1) for j in range(ny - 1)]
    # Create vector file from grid
    gpkg_from_grid(grid, proj, ofile)
    # Return
    return grid


def grid_intersection(grid, input_grid, output_grid, borders_gpkg):
    """Compute the intersection between a grid and a border vector file.

    Parameters
    ----------
    grid : list of tuple of float
        List of extents ``(xmin, ymin, xmax, ymax)`` for each grid cell,
        corresponding to the features in ``input_grid``.
    input_grid : str
        Path to the input grid vector file (GeoPackage format).
    output_grid : str
        Path to the output grid vector file for intersecting cells
        (GeoPackage format).
    borders_gpkg : str
        Path to the border vector file (GeoPackage format) used for
        intersection testing.

    Returns
    -------
    list of tuple of float
        List of extents ``(xmin, ymin, xmax, ymax)`` for grid cells that
        intersect with at least one feature in ``borders_gpkg``.

    Raises
    ------
    RuntimeError
        If ``input_grid`` or ``borders_gpkg`` cannot be opened by the
        GPKG driver.

    Notes
    -----
    A grid cell is included in the result if its geometry intersects
    with at least one feature geometry from ``borders_gpkg``. The
    spatial reference system of the output layer is derived from
    ``input_grid``. If ``output_grid`` already exists, it will be
    removed before creating a new file.

    Examples
    --------
    >>> grid = [(0.0, 0.0, 1.0, 1.0), (1.0, 0.0, 2.0, 1.0)]
    >>> intersecting = grid_intersection(
    ...     grid,
    ...     input_grid="grid.gpkg",
    ...     output_grid="grid_intersect.gpkg",
    ...     borders_gpkg="borders.gpkg"
    ... )
    >>> len(intersecting)
    1
    """
    # Grid
    dr_g = ogr.GetDriverByName("GPKG")
    ds_g = dr_g.Open(input_grid)
    lay_g = ds_g.GetLayer()
    # Borders
    dr_b = ogr.GetDriverByName("GPKG")
    ds_b = dr_b.Open(borders_gpkg)
    lay_b = ds_b.GetLayer()
    # New grid
    grid_i = []
    if os.path.exists(output_grid):
        os.remove(output_grid)
    ds = dr_g.CreateDataSource(output_grid)
    wkt = lay_g.GetSpatialRef().ExportToWkt()
    srs = osr.SpatialReference()
    srs.ImportFromWkt(wkt)
    layer = ds.CreateLayer("grid_i", srs, ogr.wkbPolygon)
    defn = lay_g.GetLayerDefn()
    for i in range(defn.GetFieldCount()):
        layer.CreateField(defn.GetFieldDefn(i))
    # Loop on features
    for (ext, feat_g) in zip(grid, lay_g):
        geom_g = feat_g.GetGeometryRef()
        for feat_b in lay_b:
            geom_b = feat_b.GetGeometryRef()
            if geom_g.Intersects(geom_b):
                grid_i.append(ext)
                layer.CreateFeature(feat_g)
                # Reset reading so that features of lay_b
                # are accessible again
                lay_b.ResetReading()
                break

    # Dereference
    ds = None
    ds_b = None
    ds_g = None

    # Return
    return grid_i

# End Of File
