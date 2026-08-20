"""Make geotiff from tiles."""

import os
from glob import glob

from osgeo import gdal

opj = os.path.join
opd = os.path.dirname


def add_color_table(output_file):
    """Add color table to GeoTIFF.

    Parameters
    ----------
    output_file : str
        Path to the output GeoTIFF file to add the color table to.
        The file must exist and will be opened in update mode. The
        color table is only applied if the raster has a single band.

    Returns
    -------
    None
        The function modifies the file in place and returns nothing.

    Raises
    ------
    RuntimeError
        If the file cannot be opened by GDAL in update mode.

    Notes
    -----
    The color table is applied only for single-band rasters. The
    following pixel values and their corresponding RGBA colors are
    defined:

    - 0: (255, 255, 255, 0)   -- stable non-forest
    - 1: (34, 139, 34, 255)   -- stable forest
    - 2: (227, 26, 28, 255)   -- forest to deforested
    - 3: (30, 100, 200, 255)  -- non-forest to old regrowth
    - 4: (100, 160, 230, 255) -- forest to old-regrowth (via deforestation)
    - 5: (150, 190, 140, 255) -- stable old-regrowth
    - 6: (255, 140, 0, 255)   -- old regrowth to deforested

    Pixel value 0 is also set as the NoData value.

    Examples
    --------
    >>> add_color_table("output/forest_map.tif")
    """

    # Open file in update mode
    ds = gdal.Open(output_file, gdal.GA_Update)
    n_bands = ds.RasterCount

    # Apply color table only for single band raster
    if n_bands == 1:
        # Define color table
        # Format: {pixel_value: (R, G, B, A)}
        colors = {
            0: (255, 255, 255, 0),    # stable non-forest
            1: (34, 139, 34, 255),    # stable forest
            2: (227, 26, 28, 255),    # forest --> deforested
            3: (30, 100, 200, 255),   # non-forest --> old regrowth
            4: (100, 160, 230, 255),  # forest --> old-regrowth (via defor)
            5: (150, 190, 140, 255),  # stable old-regrowth
            6: (255, 140, 0, 255),    # old regrowth --> deforested
        }
        band = ds.GetRasterBand(1)
        ct = gdal.ColorTable()
        for pixel_value, rgba in colors.items():
            ct.SetColorEntry(pixel_value, rgba)
        band.SetRasterColorTable(ct)
        band.SetRasterColorInterpretation(gdal.GCI_PaletteIndex)
        band.SetNoDataValue(0)
        band.FlushCache()

    # Close dataset
    ds = None


def geotiff_from_tiles(crop_to_aoi, extent, output_file):
    """Make geotiff from tiles.

    Assembles individual forest tile GeoTIFFs into a single VRT and
    then converts the VRT to a compressed GeoTIFF, optionally cropping
    to the area of interest. A color table is added to the output file
    upon completion.

    Parameters
    ----------
    crop_to_aoi : bool
        If True, crop the output raster to the extent of the area of
        interest (AOI). If the AOI is provided as a file, the raster
        is cropped using a cutline. If the AOI is defined by a bounding
        box, the raster is cropped using ``gdal.Translate``.
    extent : dict
        A dictionary returned by the ``get_extent_from_aoi()`` function.
        Expected keys are:

        - ``"aoi_isfile"`` (*bool*): Whether the AOI is provided as a
          file.
        - ``"borders_gpkg"`` (*str*): Path to the GeoPackage file
          containing the AOI borders, used as a cutline when
          ``aoi_isfile`` is True.
        - ``"extent_latlong"`` (*tuple*): A tuple of
          ``(xmin, ymin, xmax, ymax)`` in latitude/longitude
          coordinates, used when ``aoi_isfile`` is False.

    output_file : str
        Path to the output GeoTIFF file to be created. The parent
        directory must already exist and will also be used to store
        intermediate files (``forest.vrt`` and the ``forest_tiles``
        subdirectory).

    Returns
    -------
    None
        The function writes the output GeoTIFF to disk and returns
        nothing.

    Raises
    ------
    RuntimeError
        If GDAL encounters an error during VRT construction, warping,
        or translation.

    Notes
    -----
    Intermediate files created during processing:

    - ``<output_dir>/forest.vrt``: A virtual raster dataset built from
      all tile files found in ``<output_dir>/forest_tiles/``.

    The output GeoTIFF is created with the following creation options:

    - ``COMPRESS=DEFLATE``
    - ``BIGTIFF=YES``

    NoData value is set to 0 for both source and destination. After the
    GeoTIFF is created, ``add_color_table()`` is called to assign a
    color palette to the output file.

    Examples
    --------
    >>> extent = {
    ...     "aoi_isfile": False,
    ...     "borders_gpkg": None,
    ...     "extent_latlong": (-180.0, -90.0, 180.0, 90.0),
    ... }
    >>> geotiff_from_tiles(
    ...     crop_to_aoi=True,
    ...     extent=extent,
    ...     output_file="output/forest_map.tif",
    ... )
    """

    # Dir for forest tiles
    out_dir = opd(output_file)
    out_dir_tiles = opj(out_dir, "forest_tiles")

    # Make vrt
    tif_forest_files = glob(opj(out_dir_tiles, "forest_*.tif"))
    # Callback
    verbose = False
    cback = gdal.TermProgress_nocb if verbose else 0
    forest_vrt = gdal.BuildVRT(
        opj(out_dir, "forest.vrt"),
        tif_forest_files,
        srcNodata=0,
        VRTNodata=0,
        callback=cback)
    forest_vrt.FlushCache()
    forest_vrt = None
    vrt_file = opj(out_dir, "forest.vrt")

    # VRT to GeoTIFF
    copts = ["COMPRESS=DEFLATE", "BIGTIFF=YES"]
    aoi_isfile = extent["aoi_isfile"]
    borders_gpkg = extent["borders_gpkg"]
    extent_latlong = extent["extent_latlong"]
    if crop_to_aoi:
        if aoi_isfile:
            gdal.Warp(output_file, vrt_file,
                      cropToCutline=True,
                      warpOptions=["CUTLINE_ALL_TOUCHED=TRUE"],
                      cutlineDSName=borders_gpkg,
                      creationOptions=copts,
                      srcNodata=0,
                      dstNodata=0,
                      callback=cback)
        else:
            xmin, ymin, xmax, ymax = extent_latlong
            ulx_uly_lrx_lry = [xmin, ymax, xmax, ymin]
            gdal.Translate(output_file, vrt_file,
                           projWin=ulx_uly_lrx_lry,
                           noData=0,
                           maskBand=None,
                           creationOptions=copts,
                           callback=cback)
    else:
        gdal.Translate(output_file, vrt_file,
                       noData=0,
                       maskBand=None,
                       creationOptions=copts,
                       callback=cback)

    # Add color table to output file
    add_color_table(output_file)

# End
