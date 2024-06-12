"""Saves an xarray dataset to a Cloud Optimized GeoTIFF (COG).

Adapted from:
https://gist.github.com/GerardoLopez/35123d4a15aa31f3ea4b01efb5b26d4d
"""

import os
import sys

from osgeo import gdal, osr, gdal_array
import xarray as xr
import pandas as pd
from typing import Union

def get_dst_dataset(dst_img, cols, rows, layers, dtype, proj, gt):
    """Create a GDAL data set in Cloud Optimized GeoTIFF (COG) format.

    :param dst_img: Output filenane full path
    :param cols: Number of columns
    :param rows: Number of rows
    :param layers: Number of layers
    :param dtype: GDAL type code
    :param proj: Projection information in WKT format
    :param gt: GeoTransform tupple

    :return dst_ds: GDAL destination dataset object

    """

    gdal.UseExceptions()
    try:
        # Default driver options to create a COG
        driver = gdal.GetDriverByName('GTiff')
        driver_options = ['COMPRESS=DEFLATE',
                          'PREDICTOR=1',
                          'BIGTIFF=YES',
                          'TILED=YES',
                          'COPY_SRC_OVERVIEWS=YES']

        # Create driver
        dst_ds = driver.Create(dst_img, cols, rows, layers,
                               dtype, driver_options)

        # Set cartographic projection
        dst_ds.SetProjection(proj)
        dst_ds.SetGeoTransform(gt)

    except Exception as err:
        if err.err_level >= gdal.CE_Warning:
            # print('Cannot write dataset: %s' % self.input.value)
            # Stop using GDAL exceptions
            gdal.DontUseExceptions()
            raise RuntimeError(err.err_level, err.err_no, err.err_msg)

    gdal.DontUseExceptions()
    return dst_ds


def get_resolution_from_xarray(dsa: Union[xr.DataArray, xr.Dataset]) -> tuple[float, float]:
    """Method to create a tuple (x resolution, y resolution) in x and y
    dimensions.

    :param ds: dataset or dataarray with `latitude` and `longitude` coordinates.

    :return: tuple with x and y resolutions
    """

    x_res = dsa.longitude.values[1] - dsa.longitude.values[0]
    y_res = dsa.latitude.values[0] - dsa.latitude.values[1]

    return (x_res, y_res)


def xarray2geotiff_rioxarray(
                    index: int,
                    forest: xr.Dataset,
                    years: list[int],
                    proj: str,
                    out_dir: str) -> None:
    """Saves an xarray (forest cover at multiple dates) dataset to a
    Cloud Optimized GeoTIFF (COG).

    :param index: Tile index.
    :param forest: xarray forest Dataset.
    :param years: List of years.
    :param proj: Projection.
    :param out_dir: Output directory.
    """

    forest_date_list = list(forest.keys())
    forest_date_list.sort() # Sort the dates, for year 2000 with gfc
    xr.concat([forest[i] for i in forest_date_list],
                       dim=pd.Index(years, name="band")).\
            astype('b').\
            rio.write_crs(proj).\
            rename({"lon": "x", "lat": "y"}).\
            rio.write_coordinate_system().\
            transpose("band", "y", "x").\
            rename("forest_cover").\
            rio.to_raster(os.path.join(out_dir, f"forest_{index}.tif"),
                          tiled = True,
                          BIGTIFF = True,
                          PREDICTOR = 1,
                          COPY_SRC_OVERVIEWS = True,
                          driver = "GTiff",
                          compress = "Deflate")




def xarray2geotiff(index: int,
                   forest: xr.Dataset,
                   years: list[int],
                   proj: str,
                   out_dir: str) -> None:
    """Saves an xarray (forest cover at multiple dates) dataset to a
    Cloud Optimized GeoTIFF (COG).

    :param index: Tile index.
    :param forest: xarray forest Dataset.
    :param years: List of years.
    :param proj: Projection.
    :param out_dir: Output directory.
    """

    # Create GeoTransform - perhaps the user requested a
    # spatial subset, therefore is compulsory to update it

    # GeoTransform -- case of a "north up" image without
    #                 any rotation or shearing
    #  GeoTransform[0] top left x
    #  GeoTransform[1] w-e pixel resolution
    #  GeoTransform[2] 0
    #  GeoTransform[3] top left y
    #  GeoTransform[4] 0
    #  GeoTransform[5] n-s pixel resolution (negative value)

    # Reorganize the data
    forest_date_list = list(forest.keys())
    forest_date_list.sort() # Sort the dates, for year 2000 with gfc
    forest = xr.concat([forest[i] for i in forest_date_list],
                       dim=pd.Index(years, name="time"))
    forest = forest.rename({"lon": "longitude", "lat": "latitude"}).\
                    transpose("time", "latitude", "longitude")

    x_res, y_res = get_resolution_from_xarray(forest)

    gt = (forest.longitude.data[0] - (x_res / 2.),
          x_res, 0.0,
          forest.latitude.data[-1] - (y_res / 2.),
          0.0, y_res)

    # Coordinate Reference System (CRS) in a PROJ4 string to a
    # Spatial Reference System Well Known Text (WKT)
    crs = int(proj[5:9])
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(crs)
    proj = srs.ExportToWkt()

    # Get GDAL datatype from NumPy datatype
    if forest.dtype == 'bool':
        dtype = gdal.GDT_Byte
    else:
        dtype = gdal_array.NumericTypeCodeToGDALTypeCode(forest.dtype)

    # File name with index
    fname = os.path.join(out_dir, f"forest_{index}.tif")

    # Dimensions
    layers, rows, cols = forest.shape

    # Create destination dataset
    dst_ds = get_dst_dataset(
        dst_img=fname, cols=cols, rows=rows,
        layers=layers, dtype=dtype, proj=proj, gt=gt)

    for layer in range(layers):
        dst_band = dst_ds.GetRasterBand(layer + 1)

        # Date
        if 'time' in forest.dims:
            dst_band.SetMetadataItem(
                'time',
                forest.time.data[layer].astype(str))

        # Data variable name
        dst_band.SetMetadataItem('data_var', "forest_cover")

        # Data
        data_npa = forest[layer].compute().data
        indexes = list(reversed(range(rows)))
        data_npa = data_npa[indexes]
        dst_band.WriteArray(data_npa)

    dst_band = None
    del dst_ds

# End Of File
