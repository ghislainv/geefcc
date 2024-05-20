"""Make minimal grid with buffer around polygons."""

import os

import numpy as np
from osgeo import ogr, osr


def create_buffer(input_file, output_file, buffer_dist):
    """Create buffer.

    Make buffers around features of a layer and saves them to a new
    layer.

    Source: https://pcjericks.github.io/py-gdalogr-cookbook/
    vector_layers.html#create-buffer

    :param input_file: Input filename.
    :param output_file: Output filename (`.gpkg`).
    :param buffer_dist: Buffer distance (in unit of CRS).

    """
    input_ds = ogr.Open(input_file)
    input_lyr = input_ds.GetLayer()

    driver = ogr.GetDriverByName("GPKG")
    if os.path.exists(output_file):
        driver.DeleteDataSource(output_file)
    ds = driver.CreateDataSource(output_file)
    lyr = ds.CreateLayer(
        "buffer",
        geom_type=ogr.wkbPolygon)
    feature_defn = lyr.GetLayerDefn()

    for feature in input_lyr:
        in_geom = feature.GetGeometryRef()
        geom_buffer = in_geom.Buffer(buffer_dist)

        out_feature = ogr.Feature(feature_defn)
        out_feature.SetGeometry(geom_buffer)
        lyr.CreateFeature(out_feature)
        out_feature = None


def gpkg_from_grid(grid, proj=4326, ofile="grid.gpkg"):
    """Make vector file from grid.

    Source: https://pcjericks.github.io/py-gdalogr-cookbook/
    vector_layers.html#create-fishnet-grid

    :param grid: List of extents for each grid cell.
    :param proj: Projection as EPSG code, default to 4326.
    :param ofile: Output file, default to `grid.gpkg`.

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

    # Return
    ds = None


def make_grid(extent, buff, tile_size, scale, proj=4326,
              ofile="grid.gpkg"):
    """Make overlapping grid from an extent and resolution.

    :param extent: Extent (xmin, ymin, xmax, ymax).
    :param buff: Buffer (same unit as extent).
    :param tile_size: Tile size (same unit as extent).
    :param scale: Resolution (same unit as extent).
    :param proj: Projection as EPSG code, default to 4326.
    :param ofile: Output file, default to `grid.gpkg`.

    :return: List of extents for each grid cell.

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
    return grid


def grid_intersection(grid, input_grid, output_grid, borders_gpkg):
    """Grid intersection.

    :param grid: List of extents for grid cells.
    :param input_grid: Input grid vector file.
    :param output_grid: Output grid vector file.
    :param borders_gpkg: Border vector file.

    :return: List of extents for intersecting grid cells.

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
    # Clean
    ds = None
    ds_b = None
    ds_g = None
    # Return
    return grid_i

# End Of File
