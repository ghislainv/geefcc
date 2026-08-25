"""Make minimal grid with buffer around polygons."""

from pathlib import Path

import numpy as np
from osgeo import ogr, osr


def create_buffer(input_file, output_file, buffer_dist):
    """Create buffer around features of a layer and save to a new layer."""

    input_file = Path(input_file)
    output_file = Path(output_file)

    input_ds = ogr.Open(str(input_file))
    input_lyr = input_ds.GetLayer(0)

    driver = ogr.GetDriverByName("GPKG")
    if output_file.exists():
        driver.DeleteDataSource(str(output_file))
    output_ds = driver.CreateDataSource(str(output_file))
    lyr = output_ds.CreateLayer("buffer", geom_type=ogr.wkbMultiPolygon)
    feature_defn = lyr.GetLayerDefn()

    for feature in input_lyr:
        in_geom = feature.GetGeometryRef()
        geom_buffer = in_geom.Buffer(buffer_dist)
        out_feature = ogr.Feature(feature_defn)
        out_feature.SetGeometry(geom_buffer)
        lyr.CreateFeature(out_feature)
        out_feature = None

    input_ds = None
    output_ds = None


def gpkg_from_grid(grid, proj=4326, ofile="grid.gpkg"):
    """Make vector file from grid."""

    ofile = Path(ofile)
    driver = ogr.GetDriverByName("GPKG")
    if ofile.exists():
        ofile.unlink()
    ds = driver.CreateDataSource(str(ofile))
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(proj)
    layer = ds.CreateLayer("grid", srs, ogr.wkbPolygon)
    id_field = ogr.FieldDefn("id", ogr.OFTInteger)
    layer.CreateField(id_field)
    feature_def = layer.GetLayerDefn()

    for (i, coords) in enumerate(grid):
        xmin, ymin, xmax, ymax = coords
        ring = ogr.Geometry(ogr.wkbLinearRing)
        ring.AddPoint(xmin, ymax)
        ring.AddPoint(xmax, ymax)
        ring.AddPoint(xmax, ymin)
        ring.AddPoint(xmin, ymin)
        ring.AddPoint(xmin, ymax)
        poly = ogr.Geometry(ogr.wkbPolygon)
        poly.AddGeometry(ring)
        feature = ogr.Feature(feature_def)
        feature.SetGeometry(poly)
        feature.SetField("id", i)
        layer.CreateFeature(feature)
        feature = None

    ds = None


def make_grid(extent, buff, tile_size, scale, proj=4326, ofile="grid.gpkg"):
    """Make overlapping grid from an extent and resolution."""

    xmin = extent[0] - buff
    ymin = extent[1] - buff
    xmax = extent[2] + buff
    ymax = extent[3] + buff
    tile_size = int(np.round(tile_size / scale)) * scale
    xlist = list(np.arange(xmin, xmax + tile_size, tile_size))
    nx = len(xlist)
    ylist = list(np.arange(ymin, ymax + tile_size, tile_size))
    ny = len(ylist)
    grid = [(xlist[i], ylist[j], xlist[i + 1], ylist[j + 1])
            for i in range(nx - 1) for j in range(ny - 1)]
    gpkg_from_grid(grid, proj, ofile)
    return grid


def grid_intersection(grid, input_grid, output_grid, borders_gpkg):
    """Compute the intersection between a grid and a border vector file."""

    input_grid = Path(input_grid)
    output_grid = Path(output_grid)
    borders_gpkg = Path(borders_gpkg)

    dr_g = ogr.GetDriverByName("GPKG")
    ds_g = dr_g.Open(str(input_grid))
    lay_g = ds_g.GetLayer()
    dr_b = ogr.GetDriverByName("GPKG")
    ds_b = dr_b.Open(str(borders_gpkg))
    lay_b = ds_b.GetLayer()

    grid_i = []
    if output_grid.exists():
        output_grid.unlink()
    ds = dr_g.CreateDataSource(str(output_grid))
    wkt = lay_g.GetSpatialRef().ExportToWkt()
    srs = osr.SpatialReference()
    srs.ImportFromWkt(wkt)
    layer = ds.CreateLayer("grid_i", srs, ogr.wkbPolygon)
    defn = lay_g.GetLayerDefn()
    for i in range(defn.GetFieldCount()):
        layer.CreateField(defn.GetFieldDefn(i))

    for (ext, feat_g) in zip(grid, lay_g):
        geom_g = feat_g.GetGeometryRef()
        for feat_b in lay_b:
            geom_b = feat_b.GetGeometryRef()
            if geom_g.Intersects(geom_b):
                grid_i.append(ext)
                layer.CreateFeature(feat_g)
                lay_b.ResetReading()
                break

    ds = None
    ds_b = None
    ds_g = None

    return grid_i

# End
