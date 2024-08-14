from osgeo import gdal
import os

import cartopy.crs as ccrs
from cartopy.feature import BORDERS, OCEAN
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
from matplotlib.colors import ListedColormap
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import rioxarray

def _set_plot(raster, color_map, patches, figsize, dpi, grid, borders, **kwargs):
    """Set plot for raster.

    Sets the plot for raster, defining the extent, color map, and patches for legend.

    :param raster: Raster.
    :param color_map: Color map.
    :param patches: List of patches for legend.
    :param figsize: Figure size in inches.
    :param dpi: Resolution for output image.
    :param grid: Plot lat/lon grid.
    :param borders: Plot borders.
    :param \\**kwargs: Additional arguments to the plot.

    :return: A Matplotlib figure.
    """

    # Figure
    fig = plt.figure(figsize=figsize, dpi=dpi)
    ax = plt.axes(projection=ccrs.PlateCarree())

    # Extent
    xmin, xmax, ymin, ymax = raster.x.min(), raster.x.max(), raster.y.min(), raster.y.max()
    xbuffer = (xmax - xmin) * 0.025
    ybuffer = (ymax - ymin) * 0.025
    extent = [xmin-xbuffer, xmax+xbuffer, ymin-ybuffer, ymax+ybuffer]
    ax.set_extent(extent, ccrs.PlateCarree())

    # Plot raster
    raster.plot(ax=ax, cmap=color_map, add_colorbar=False, transform=ccrs.PlateCarree(), **kwargs)

    # Plot lat/lon grid
    if grid:
        gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                      linewidth=0.1, color='k', alpha=1,
                      linestyle='--')
        gl.top_labels = False
        gl.right_labels = False
        gl.xformatter = LONGITUDE_FORMATTER
        gl.yformatter = LATITUDE_FORMATTER
        gl.xlabel_style = {'size': 8}
        gl.ylabel_style = {'size': 8}

    # Add borders
    if borders:
        ax.add_feature(BORDERS)

    ax.add_feature(OCEAN, zorder=0)
    ax.coastlines(linewidth=1)

    plt.legend(handles=patches, bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)

    return fig



def _set_color_map_and_legend(colors: list[tuple], labels: dict):
    """Set color map for raster plot as well as patches for legend.

    This function sets the color map and patches that are used for plot.

    :param colors: List of colors.
    :param labels: Dictionary of labels associated with the colormap

    :return: Color map.
    :return: List of patches for legend.

    """

    # Colors
    list_colors = [(1, 1, 1, 0)]  # transparent white for 0
    cmax = 255.0  # float for division
    for col in colors:
        col_class = tuple([i / cmax for i in col])
        list_colors.append(col_class)
    color_map = ListedColormap(list_colors)
    patches = [mpatches.Patch(facecolor=col, edgecolor="black",
                              label=labels[i]) for (i, col) in enumerate(list_colors)]
    return color_map, patches


def plot_fcc(input_fcc_raster : str,
    output_file : str = "fcc.png",
    source : str = "tmf",
    years  : list = [2000, 2010, 2020],
    borders : bool = True,
    zoom : tuple | None = None,
    grid : bool = True,
    colors : list[tuple] = [(255, 165, 0, 255), (227, 26, 28, 255), (34, 139, 34, 255)],
    figsize : tuple = (11.69, 8.27),
    dpi : int = 300,
    **kwargs
):
    """Plot forest-cover change (fcc) map.

    This function plots the forest-cover change map with 2
    deforestation time-periods (2000 -> 2010 -> 2020 for example) plus
    the remaining forest (3 classes).


    :param input_fcc_raster: Path to fcc raster.
    :param output_file: Name of the plot file.
    :param source: Source of the forest cover data (tmf or gfc).
    :param maxpixels: Maximum number of pixels to plot.
    :param years: List of years for the fcc in the raster.
    :param borders: Vector file to be plotted.
    :param zoom: Zoom to region (xmin, xmax, ymin, ymax).
    :param colors: List of rgba colors for classes 123.
    :param figsize: Figure size in inches.
    :param dpi: Resolution for output image.
    :param \\**kwargs: see below.

    :Keyword Arguments: Additional arguments to plot borders.

    :return: A Matplotlib figure of the forest map.

    """

    # Open raster and sum bands
    fcc = rioxarray.open_rasterio(input_fcc_raster).sum(dim="band")
    if zoom:
        fcc = fcc.rio.clip_box(zoom[0], zoom[2], zoom[1], zoom[3])


    # Colors & Labels
    labels = {0:f"non-forest in {years[0]}", 1:f"deforestation {years[0]}-{years[1]-1}",
              2:f"deforestation {years[1]}-{years[2]-1}", 3:f"forest in {years[2]}"}
    color_map, patches = _set_color_map_and_legend(colors, labels)

    # Plot
    fig = _set_plot(fcc, color_map, patches, figsize, dpi, grid, borders, **kwargs)

    ## Add title & legend
    plt.title(f"Forest cover change {years[0]}-{years[1]}-{years[2]}, {source.upper()}")

    # Save and return figure
    fig.savefig(output_file, bbox_inches="tight")


def plot_fc_tmf_vs_gfc(
    input_tmf_raster: str,
    input_gfc_raster: str,
    output_file: str = "fc_tmf_vs_gfc.png",
    year: int = 2020,
    borders: bool = True,
    zoom: tuple | None = None,
    grid: bool = True,
    colors: list[tuple] = [(10, 10, 150, 255), (34, 139, 34, 255), (200, 200, 0, 255)],
    figsize: tuple = (11.69, 8.27),
    dpi: int = 300,
    **kwargs
):
    """Plot forest-cover (fc) differences according to TMF and GFC products.

    This function plots the forest-cover  differences from TMF and GFC products at a given year.

    :param input_tmf_raster: Path to TMF fcc raster.
    :param input_gfc_raster: Path to GFC fcc raster.
    :param output_file: Name of the plot file.
    :param year: Years for forest-cover comparison.
    :param borders: Vector file to be plotted.
    :param zoom: Zoom to region (xmin, xmax, ymin, ymax).
    :param colors: List of rgba colors for classes 123.
    :param figsize: Figure size in inches.
    :param dpi: Resolution for output image.
    """

    # Open raster and sum bands
    forest_tmf = rioxarray.open_rasterio(input_tmf_raster).sel(band=3) # wrong: hard coded but should be determined from year from data
    forest_gfc = rioxarray.open_rasterio(input_gfc_raster).sel(band=3) # wrong: hard coded but should be determined from year from data
    if zoom:
        forest_tmf = forest_tmf.rio.clip_box(zoom[0], zoom[2], zoom[1], zoom[3])
        forest_gfc = forest_gfc.rio.clip_box(zoom[0], zoom[2], zoom[1], zoom[3])
    forest_diff = forest_tmf - forest_gfc
    forest_sum = forest_tmf + forest_gfc
    forest_diff = forest_diff.where(forest_sum != 0, -2)

    # Colors & Labels
    labels = {0: "non-forest tmf, non-forest gfc", 1:"non-forest tmf / forest gfc",
              2:"forest tmf / forest gfc", 3:"forest tmf, non-forest gfc"}
    color_map, patches = _set_color_map_and_legend(colors, labels)

    # Plot
    fig = _set_plot(forest_diff, color_map, patches,figsize, dpi, grid, borders, **kwargs)

    ## Add title & legend
    plt.title(f"Difference between TMF and GFC for forest cover in {year}")

    # Save and return figure
    fig.savefig(output_file, bbox_inches="tight")

