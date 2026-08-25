"""Make geotiff from tiles."""

from pathlib import Path

from osgeo import gdal


def add_color_table(output_file):
    """Add color table to GeoTIFF."""

    ds = gdal.Open(str(Path(output_file)), gdal.GA_Update)
    n_bands = ds.RasterCount

    if n_bands == 1:
        colors = {
            0: (255, 255, 255, 0),
            1: (34, 139, 34, 255),
            2: (227, 26, 28, 255),
            3: (30, 100, 200, 255),
            4: (100, 160, 230, 255),
            5: (150, 190, 140, 255),
            6: (255, 140, 0, 255),
        }
        band = ds.GetRasterBand(1)
        ct = gdal.ColorTable()
        for pixel_value, rgba in colors.items():
            ct.SetColorEntry(pixel_value, rgba)
        band.SetRasterColorTable(ct)
        band.SetRasterColorInterpretation(gdal.GCI_PaletteIndex)
        band.SetNoDataValue(0)
        band.FlushCache()

    ds = None


def geotiff_from_tiles(crop_to_aoi, extent, output_file):
    """Make geotiff from tiles."""

    output_file = Path(output_file)
    out_dir = output_file.parent
    out_dir_tiles = out_dir / "forest_tiles"

    tif_forest_files = [str(p) for p in out_dir_tiles.glob("forest_*.tif")]
    verbose = False
    cback = gdal.TermProgress_nocb if verbose else 0
    vrt_file = out_dir / "forest.vrt"
    forest_vrt = gdal.BuildVRT(
        str(vrt_file),
        tif_forest_files,
        srcNodata=0,
        VRTNodata=0,
        callback=cback)
    forest_vrt.FlushCache()
    forest_vrt = None

    copts = ["COMPRESS=DEFLATE", "BIGTIFF=YES"]
    aoi_isfile = extent["aoi_isfile"]
    borders_gpkg = extent["borders_gpkg"]
    extent_latlong = extent["extent_latlong"]

    if crop_to_aoi:
        if aoi_isfile:
            gdal.Warp(str(output_file), str(vrt_file),
                      cropToCutline=True,
                      warpOptions=["CUTLINE_ALL_TOUCHED=TRUE"],
                      cutlineDSName=str(borders_gpkg),
                      creationOptions=copts,
                      srcNodata=0,
                      dstNodata=0,
                      callback=cback)
        else:
            xmin, ymin, xmax, ymax = extent_latlong
            ulx_uly_lrx_lry = [xmin, ymax, xmax, ymin]
            gdal.Translate(str(output_file), str(vrt_file),
                           projWin=ulx_uly_lrx_lry,
                           noData=0,
                           maskBand=None,
                           creationOptions=copts,
                           callback=cback)
    else:
        gdal.Translate(str(output_file), str(vrt_file),
                       noData=0,
                       maskBand=None,
                       creationOptions=copts,
                       callback=cback)

    add_color_table(output_file)

# End
