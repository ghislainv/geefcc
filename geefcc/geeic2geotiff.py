"""Saves an xarray dataset to a Cloud Optimized GeoTIFF (COG).

Adapted from:
https://gist.github.com/GerardoLopez/35123d4a15aa31f3ea4b01efb5b26d4d
"""

import os
import sys

from osgeo import gdal, osr, gdal_array
import shapely
import rioxarray
import xarray as xr
from xee import helpers


# Dummy variable
_ = rioxarray


def progress_bar_sequence(index, ntiles):
    """Progress bar."""
    j = (index + 1) / ntiles
    sys.stdout.write("\r")
    sys.stdout.write("[%-20s] %d%%" % ('='*int(20 * j), 100 * j))
    sys.stdout.flush()


def progress_bar_async(index, ntiles):
    """Progress bar."""
    (_, _) = (index, ntiles)
    print(".", end="", flush=True)


def get_dst_dataset(dst_img, cols, rows, layers, dtype, proj, gt):
    """Create a GDAL data set in Cloud Optimized GeoTIFF (COG) format.

    :param dst_img: Output filename full path
    :param cols: Number of columns
    :param rows: Number of rows
    :param layers: Number of layers
    :param dtype: GDAL type code
    :param proj: Projection information in WKT format
    :param gt: GeoTransform tupple

    :return: GDAL destination dataset object

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

        # Create dataset
        if os.path.isfile(dst_img):
            os.remove(dst_img)
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


def get_resolution_from_xarray(xarray):
    """Method to create a tuple (x resolution, y resolution) in x and y
    dimensions.

    :param xarray: xarray with latitude and longitude variables.

    :return: tuple with x and y resolutions
    """

    x_res = xarray.longitude.values[1] - xarray.longitude.values[0]
    y_res = xarray.latitude.values[1] - xarray.latitude.values[0]

    return (x_res, y_res)


def xarray2geotiff(xarray, data_var, out_dir, index):
    """Saves an xarray dataset to a Cloud Optimized GeoTIFF (COG).

    :param xarray: xarray Dataset.
    :param data_var: Data variable in the xarray dataset.
    :param out_dir: Output directory.
    :param index: Tile index.

    """

    # Create GeoTransform - perhaps the user requested a
    # spatial subset, therefore it is mandatory to update it

    # GeoTransform -- case of a "north up" image without
    #                 any rotation or shearing
    #  GeoTransform[0] top left x
    #  GeoTransform[1] w-e pixel resolution
    #  GeoTransform[2] 0
    #  GeoTransform[3] top left y
    #  GeoTransform[4] 0
    #  GeoTransform[5] n-s pixel resolution (negative value)

    # Reorganize the data (not necessary with version xee >= v0.1.0
    # xarray = xarray.transpose("time", "latitude", "longitude")

    # Create tmp xarray DataArray
    _xarray = getattr(xarray, data_var)

    x_res, y_res = get_resolution_from_xarray(_xarray)

    gt = (_xarray.longitude.data[0] - (x_res / 2.),
          x_res, 0.0,
          _xarray.latitude.data[0] - (y_res / 2.),
          0.0, y_res)

    # Coordinate Reference System (CRS) in a PROJ4 string to a
    # Spatial Reference System Well Known Text (WKT)
    crs = xarray.rio.crs.to_epsg()
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(crs)
    proj = srs.ExportToWkt()

    # Get GDAL datatype from NumPy datatype
    if _xarray.dtype == 'bool':
        dtype = gdal.GDT_Byte
    else:
        dtype = gdal_array.NumericTypeCodeToGDALTypeCode(_xarray.dtype)

    # File name with index
    fname = os.path.join(out_dir, f"forest_{index}.tif")

    # Dimensions
    layers, rows, cols = _xarray.shape

    # Create destination dataset
    dst_ds = get_dst_dataset(
        dst_img=fname, cols=cols, rows=rows,
        layers=layers, dtype=dtype, proj=proj, gt=gt)

    for layer in range(layers):
        dst_band = dst_ds.GetRasterBand(layer + 1)

        # Date
        if 'time' in _xarray.dims:
            dst_band.SetMetadataItem(
                'time',
                _xarray.time.data[layer].astype(str))

        # Data variable name
        dst_band.SetMetadataItem('data_var', data_var)

        # Data
        data_npa = _xarray[layer].data
        # index = list(reversed(range(rows)))
        # data_npa = data_npa[index]
        dst_band.WriteArray(data_npa)

        # Dereference band
        dst_band = None

    # Dereference dataset
    del dst_ds


def geeic2geotiff(index, extent, ntiles, forest,
                  proj, scale, out_dir, verbose=True):
    """Write a GEE image collection to a geotiff.

    :param index: Tile index.
    :param extent: Tile extent.
    :param ntiles: Total number of tiles.
    :param forest: Forest image collection from GEE.
    :param proj: Projection.
    :param scale: Scale.
    :param output_dir: Output directory.
    :param verbose: If True, shows a progress bar.

    """

    ofile = os.path.join(out_dir, f"forest_{index}.tif")
    if (not os.path.isfile(ofile)) or (os.path.getsize(ofile) == 0):
        # Open dataset
        shapely_geom = shapely.geometry.box(
            extent[0], extent[1], extent[2], extent[3])
        grid_params = helpers.fit_geometry(
            geometry=shapely_geom,
            grid_crs=proj,
            grid_scale=(scale, -scale)
        )
        ds = (xr.load_dataset(
            forest,
            engine="ee",
            chunks=None,
            **grid_params)
              .astype("b")
              .rename({"x": "longitude", "y": "latitude"})
              )

        # Load and write data to geotiff
        # xarray2geotiff(ds, "forest_cover", out_dir, index)
        # Simplified with rioxarray
        da = ds["forest_cover"]
        gdal_args = {
            "COMPRESS": "DEFLATE", "PREDICTOR": "1",
            "BIGTIFF": "YES", "TILED": "YES",
            "COPY_SRC_OVERVIEWS": "YES"
        }
        da.rio.to_raster(ofile, driver="GTiff", dtype="uint8", **gdal_args)

        # Progress bar
        if verbose:
            progress_bar_async(index, ntiles)

# End Of File
