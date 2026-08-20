"""Saves an xarray dataset to a Cloud Optimized GeoTIFF (COG).

Adapted from:
https://gist.github.com/GerardoLopez/35123d4a15aa31f3ea4b01efb5b26d4d
"""

import os
import sys
from tenacity import retry, stop_after_attempt, wait_exponential

from osgeo import gdal, osr, gdal_array
import shapely
import rioxarray
import xarray as xr
from xee import helpers


# Dummy variable
_ = rioxarray


def progress_bar_sequence(index, ntiles):
    """Display a sequential progress bar in the terminal.

    Parameters
    ----------
    index : int
        Current iteration index (zero-based).
    ntiles : int
        Total number of tiles or iterations.

    Returns
    -------
    None
        Writes progress bar output directly to stdout.

    Examples
    --------
    >>> for i in range(10):
    ...     progress_bar_sequence(i, 10)
    """
    j = (index + 1) / ntiles
    sys.stdout.write("\r")
    sys.stdout.write("[%-20s] %d%%" % ('='*int(20 * j), 100 * j))
    sys.stdout.flush()


def progress_bar_async(index, ntiles):
    """Display an asynchronous progress indicator in the terminal.

    Prints a dot for each completed iteration without blocking.

    Parameters
    ----------
    index : int
        Current iteration index (zero-based). Not used internally
        but kept for API consistency with ``progress_bar_sequence``.
    ntiles : int
        Total number of tiles or iterations. Not used internally
        but kept for API consistency with ``progress_bar_sequence``.

    Returns
    -------
    None
        Writes a dot character directly to stdout.

    Examples
    --------
    >>> for i in range(5):
    ...     progress_bar_async(i, 5)
    .....
    """
    (_, _) = (index, ntiles)
    print(".", end="", flush=True)


def get_dst_dataset(dst_img, cols, rows, layers, dtype, proj, gt):
    """Create a GDAL dataset in Cloud Optimized GeoTIFF (COG) format.

    Parameters
    ----------
    dst_img : str
        Output filename full path.
    cols : int
        Number of columns (pixels in the x direction).
    rows : int
        Number of rows (pixels in the y direction).
    layers : int
        Number of layers (bands).
    dtype : int
        GDAL type code representing the pixel data type.
    proj : str
        Projection information in WKT (Well Known Text) format.
    gt : tuple of float
        GeoTransform tuple with six elements:
        ``(top_left_x, x_pixel_size, rotation_x,
        top_left_y, rotation_y, y_pixel_size)``.

    Returns
    -------
    dst_ds : gdal.Dataset
        GDAL destination dataset object configured with COG settings.

    Raises
    ------
    RuntimeError
        If GDAL encounters an error at or above the warning level
        during dataset creation. The exception carries
        ``(err_level, err_no, err_msg)`` as arguments.

    Notes
    -----
    The dataset is created with the following default driver options:

    - ``COMPRESS=DEFLATE``
    - ``PREDICTOR=1``
    - ``BIGTIFF=YES``
    - ``TILED=YES``
    - ``COPY_SRC_OVERVIEWS=YES``

    If a file already exists at ``dst_img``, it is removed before
    creating the new dataset.

    Examples
    --------
    >>> dst_ds = get_dst_dataset(
    ...     dst_img="/tmp/output.tif",
    ...     cols=512,
    ...     rows=512,
    ...     layers=1,
    ...     dtype=gdal.GDT_Byte,
    ...     proj='GEOGCS["WGS 84", ...]',
    ...     gt=(-180.0, 0.25, 0.0, 90.0, 0.0, -0.25)
    ... )
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
    """Compute the pixel resolution from an xarray Dataset or DataArray.

    Parameters
    ----------
    xarray : xarray.Dataset or xarray.DataArray
        An xarray object containing ``latitude`` and ``longitude``
        coordinate variables with at least two elements each.

    Returns
    -------
    tuple of float
        A two-element tuple ``(x_res, y_res)`` where:

        - ``x_res`` is the resolution in the x (longitude) direction.
        - ``y_res`` is the resolution in the y (latitude) direction.

    Notes
    -----
    The resolution is computed as the difference between the first two
    consecutive coordinate values, so the coordinates are assumed to be
    uniformly spaced.

    Examples
    --------
    >>> import xarray as xr
    >>> import numpy as np
    >>> ds = xr.Dataset(
    ...     coords={
    ...         "longitude": np.arange(0, 1, 0.25),
    ...         "latitude": np.arange(0, 1, 0.25),
    ...     }
    ... )
    >>> get_resolution_from_xarray(ds)
    (0.25, 0.25)
    """

    x_res = xarray.longitude.values[1] - xarray.longitude.values[0]
    y_res = xarray.latitude.values[1] - xarray.latitude.values[0]

    return (x_res, y_res)


def xarray2geotiff(xarray, data_var, out_dir, index):
    """Save an xarray Dataset to a Cloud Optimized GeoTIFF (COG).

    Parameters
    ----------
    xarray : xarray.Dataset
        Dataset containing the data variable to export. Must have
        ``latitude``, ``longitude``, and optionally ``time`` dimensions.
        A CRS must be accessible via ``xarray.rio.crs``.
    data_var : str
        Name of the data variable within ``xarray`` to export.
    out_dir : str
        Path to the output directory where the GeoTIFF file will be saved.
    index : int
        Tile index used to construct the output filename
        (e.g., ``forest_0.tif``).

    Returns
    -------
    None
        The function writes the GeoTIFF file to disk and returns nothing.

    Notes
    -----
    The output filename follows the pattern ``forest_{index}.tif`` and is
    written to ``out_dir``.

    The GeoTransform is derived from the ``latitude`` and ``longitude``
    coordinates of the selected data variable and assumes a "north up"
    image without rotation or shearing:

    - ``GeoTransform[0]``: top left x
    - ``GeoTransform[1]``: west-east pixel resolution
    - ``GeoTransform[2]``: 0 (no rotation)
    - ``GeoTransform[3]``: top left y
    - ``GeoTransform[4]``: 0 (no rotation)
    - ``GeoTransform[5]``: north-south pixel resolution (negative value)

    Boolean arrays are written as ``GDT_Byte``; other dtypes are mapped
    using ``gdal_array.NumericTypeCodeToGDALTypeCode``.

    Band metadata items ``time`` (if a ``time`` dimension exists) and
    ``data_var`` are set on each raster band.

    Examples
    --------
    >>> xarray2geotiff(ds, "tree_cover", "/tmp/output", index=3)
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


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1))
def geeic2geotiff(index, extent, ntiles, forest,
                  proj, scale, out_dir, verbose=True):
    """Write a Google Earth Engine image collection tile to a GeoTIFF file.

    Parameters
    ----------
    index : int
        Tile index used to construct the output filename
        (e.g., ``forest_0.tif``).
    extent : array-like of float
        Bounding box of the tile as ``[min_x, min_y, max_x, max_y]``
        in the coordinate system defined by ``proj``.
    ntiles : int
        Total number of tiles. Used for progress bar display.
    forest : ee.ImageCollection
        Forest image collection from Google Earth Engine.
    proj : str or dict
        Projection (CRS) used to define the output grid, compatible
        with ``xee.helpers.fit_geometry``.
    scale : float
        Pixel scale in the units of ``proj`` (e.g., metres or degrees).
    out_dir : str
        Path to the output directory where the GeoTIFF file will be saved.
    verbose : bool, optional
        If ``True`` (default), prints a dot to stdout after each tile
        is successfully written.

    Returns
    -------
    None
        The function writes a GeoTIFF file to disk and returns nothing.

    Notes
    -----
    The output filename follows the pattern ``forest_{index}.tif`` and is
    saved to ``out_dir``. If the file already exists and is non-empty, the
    function skips processing for that tile.

    The dataset is loaded using the ``"ee"`` engine via ``xarray``, cast
    to bytes (``"b"``), and written as a ``uint8`` GeoTIFF with the
    following GDAL creation options:

    - ``COMPRESS=DEFLATE``
    - ``PREDICTOR=1``
    - ``BIGTIFF=YES``
    - ``TILED=YES``
    - ``COPY_SRC_OVERVIEWS=YES``

    Dimension names ``"x"`` and ``"y"`` are renamed to ``"longitude"``
    and ``"latitude"`` respectively before export.

    Examples
    --------
    >>> geeic2geotiff(
    ...     index=0,
    ...     extent=[-10.0, -10.0, 10.0, 10.0],
    ...     ntiles=4,
    ...     forest=ee_image_collection,
    ...     proj="EPSG:4326",
    ...     scale=30,
    ...     out_dir="/tmp/output",
    ...     verbose=True,
    ... )
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

        # Var name
        var_name = list(ds.data_vars)[0]

        # Load and write data to geotiff
        # xarray2geotiff(ds, var_name, out_dir, index)
        # Simplified with rioxarray
        da = ds[var_name]
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
