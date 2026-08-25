"""Saves an xarray dataset to a Cloud Optimized GeoTIFF (COG)."""

import sys
from pathlib import Path

from osgeo import gdal, osr, gdal_array
import shapely
import rioxarray
import xarray as xr
from xee import helpers
from tenacity import (retry, stop_after_attempt,
                      wait_exponential, retry_if_exception_type)

# Dummy variable
_ = rioxarray


def progress_bar_async(index, ntiles):
    """Print a dot for each completed tile."""
    (_, _) = (index, ntiles)
    print(".", end="", flush=True)


def get_resolution_from_xarray(xarray):
    """Compute pixel resolution from an xarray Dataset."""
    x_res = xarray.longitude.values[1] - xarray.longitude.values[0]
    y_res = xarray.latitude.values[1] - xarray.latitude.values[0]
    return (x_res, y_res)


def get_dst_dataset(dst_img, cols, rows, layers, dtype, proj, gt):
    """Create a GDAL dataset in COG format."""

    dst_img = Path(dst_img)
    gdal.UseExceptions()
    try:
        driver = gdal.GetDriverByName("GTiff")
        driver_options = ["COMPRESS=DEFLATE", "PREDICTOR=1",
                          "BIGTIFF=YES", "TILED=YES",
                          "COPY_SRC_OVERVIEWS=YES"]
        if dst_img.is_file():
            dst_img.unlink()
        dst_ds = driver.Create(str(dst_img), cols, rows, layers,
                               dtype, driver_options)
        dst_ds.SetProjection(proj)
        dst_ds.SetGeoTransform(gt)
    except Exception as err:
        if err.err_level >= gdal.CE_Warning:
            gdal.DontUseExceptions()
            raise RuntimeError(err.err_level, err.err_no, err.err_msg)
    gdal.DontUseExceptions()
    return dst_ds


@retry(
    retry=retry_if_exception_type(Exception),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    reraise=True,
)
def _download_tile(forest, shapely_geom, proj, scale):
    """Download a single GEE tile with retry on failure."""
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
    return ds


def geeic2geotiff(index, extent, ntiles, forest,
                  proj, scale, out_dir, verbose=True):
    """Write a GEE image collection tile to a GeoTIFF file."""

    out_dir = Path(out_dir)
    ofile = out_dir / f"forest_{index}.tif"

    if (not ofile.is_file()) or (ofile.stat().st_size == 0):
        shapely_geom = shapely.geometry.box(
            extent[0], extent[1], extent[2], extent[3])
        ds = _download_tile(forest, shapely_geom, proj, scale)
        var_name = list(ds.data_vars)[0]
        da = ds[var_name]
        gdal_args = {
            "COMPRESS": "DEFLATE", "PREDICTOR": "1",
            "BIGTIFF": "YES", "TILED": "YES",
            "COPY_SRC_OVERVIEWS": "YES"
        }
        da.rio.to_raster(str(ofile), driver="GTiff",
                         dtype="uint8", **gdal_args)
        if verbose:
            progress_bar_async(index, ntiles)

# End
