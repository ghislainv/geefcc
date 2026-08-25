"""Plot forest cover change map from TMF or GFC loss product."""

from pathlib import Path
import math

import geopandas
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import rioxarray
from osgeo import gdal


def plot_fcc_loss(
        input_file,
        years,
        output_file="fcc_loss.png",
        title="Forest cover change",
        dpi=100,
        max_pixels=10_000_000,
        borders=None,
        buffer=None,
        grid=None,
        xlim=None,
        ylim=None):
    """Plot a forest cover change map from the TMF or GFC loss product.

    Produces a PNG map from a single-band raster file obtained by
    summing the bands of a multiband raster produced by
    :func:`get_fcc_loss` (e.g. with :func:`sum_raster_bands`). Pixel
    values encode forest cover change classes:

    - 0 = non-forest at ``years[0]``
    - 1 = deforestation during period 1 (``years[0]``--``years[1]``)
    - 2 = deforestation during period 2 (``years[1]``--``years[2]``)
    - ... (one class per intermediate period)
    - n = forest at ``years[-1]``

    Colors are fixed: transparent for class 0 (non-forest), then orange,
    red, and forest green for the last class (remaining forest).

    If the raster exceeds ``max_pixels`` pixels, it is automatically
    resampled to a coarser resolution before plotting, using nearest
    neighbour resampling. The resampled raster is saved alongside the
    input file (suffix ``_coarsen.tif``) and reused on subsequent calls.

    Parameters
    ----------
    input_file : str or Path
        Path to the single-band GeoTIFF raster file. Pixel values must
        be integers in the range 0--n where n = len(years) - 1.
    years : list of int
        List of years used for the forest cover change computation,
        e.g. ``[2000, 2010, 2020]``. Used to build legend labels.
    output_file : str or Path, optional
        Path to the output PNG file. Default is ``"fcc_loss.png"``.
    title : str, optional
        Title displayed above the map. Default is
        ``"Forest cover change"``.
    dpi : int, optional
        Resolution of the output figure in dots per inch. Default is
        ``100``.
    max_pixels : int, optional
        Maximum number of pixels (rows x columns) allowed before
        automatic resampling is triggered. Default is ``10_000_000``.
    borders : str, Path, geopandas.GeoDataFrame, or None, optional
        Country or administrative borders to overlay as a black line.
        Accepts a file path or an already-loaded
        :class:`geopandas.GeoDataFrame`. Default is ``None``.
    buffer : str, Path, geopandas.GeoDataFrame, or None, optional
        Buffer polygon to overlay as a black dashed line. Accepts a
        file path or an already-loaded
        :class:`geopandas.GeoDataFrame`. Default is ``None``.
    grid : str, Path, geopandas.GeoDataFrame, or None, optional
        Download tile grid to overlay as a grey line. Accepts a file
        path or an already-loaded :class:`geopandas.GeoDataFrame`.
        Default is ``None``.
    xlim : tuple of float or None, optional
        Longitude limits of the map as ``(xmin, xmax)``. Default is
        ``None`` (derived from the raster).
    ylim : tuple of float or None, optional
        Latitude limits of the map as ``(ymin, ymax)``. Default is
        ``None`` (derived from the raster).

    Returns
    -------
    None
        The function writes the figure directly to ``output_file``.

    Examples
    --------
    Simple plot:

    >>> plot_fcc_loss(
    ...     input_file="out_tmf/fcc_tmf.tif",
    ...     years=[2000, 2010, 2020],
    ...     output_file="fcc_loss.png",
    ...     title="Forest cover change 2000-2010-2020, TMF",
    ...     dpi=100,
    ... )

    Plot with borders, buffer and grid:

    >>> plot_fcc_loss(
    ...     input_file="out_tmf/fcc_tmf.tif",
    ...     years=[2000, 2010, 2020],
    ...     output_file="fcc_loss.png",
    ...     title="Forest cover change 2000-2010-2020, TMF",
    ...     dpi=200,
    ...     borders="out_tmf/gadm41_PER_0.gpkg",
    ...     buffer="out_tmf/gadm41_PER_buffer.gpkg",
    ...     grid="out_tmf/min_grid.gpkg",
    ... )
    """

    input_file = Path(input_file)
    output_file = Path(output_file)

    # Load vector layers
    if isinstance(borders, (str, Path)):
        borders = geopandas.read_file(str(borders))
    if isinstance(buffer, (str, Path)):
        buffer = geopandas.read_file(str(buffer))
    if isinstance(grid, (str, Path)):
        grid = geopandas.read_file(str(grid))

    # Resample if raster exceeds max_pixels
    ds_info = gdal.Open(str(input_file))
    nrow = ds_info.RasterYSize
    ncol = ds_info.RasterXSize
    scale = ds_info.GetGeoTransform()[1]
    ds_info = None

    plot_file = input_file
    if nrow * ncol > max_pixels:
        factor = math.ceil(math.sqrt(nrow * ncol / max_pixels))
        xres = factor * scale
        yres = factor * scale
        coarsen_file = input_file.with_stem(input_file.stem + "_coarsen")
        if not coarsen_file.is_file():
            ds = gdal.Warp(
                str(coarsen_file), str(input_file),
                xRes=xres, yRes=yres, resampleAlg="near",
            )
            ds = None
        plot_file = coarsen_file

    # Colors
    n_periods = len(years) - 1
    orange_shades = [
        (255, 165, 0, 255),
        (227, 26, 28, 255),
        (180, 50, 50, 255),
        (140, 30, 30, 255),
    ]
    cmax = 255.0
    colors = [(1, 1, 1, 0)]
    for i in range(n_periods):
        col = orange_shades[i % len(orange_shades)]
        colors.append(tuple(c / cmax for c in col))
    colors.append((34 / cmax, 139 / cmax, 34 / cmax, 1))
    color_map = ListedColormap(colors)

    # Labels
    labels = {0: f"non-forest in {years[0]}"}
    for i in range(n_periods):
        labels[i + 1] = f"deforestation {years[i]}\u2013{years[i + 1]}"
    labels[n_periods + 1] = f"forest in {years[-1]}"
    patches = [
        mpatches.Patch(facecolor=col, edgecolor="black", label=labels[i])
        for i, col in enumerate(colors)
    ]

    # Load raster and compute geographic extent
    ds = rioxarray.open_rasterio(str(plot_file)).squeeze()
    nrow, ncol = ds.shape
    xmin = float(ds.x.min())
    xmax = float(ds.x.max())
    ymin = float(ds.y.min())
    ymax = float(ds.y.max())
    xres = (xmax - xmin) / (ncol - 1)
    yres = (ymax - ymin) / (nrow - 1)
    extent = [xmin - xres / 2, xmax + xres / 2,
              ymin - yres / 2, ymax + yres / 2]

    # Plot
    fig = plt.figure()
    ax = plt.subplot(111)
    ax.imshow(ds.values, cmap=color_map, extent=extent, resample=False)
    ax.set_aspect("equal")
    if grid is not None:
        grid.boundary.plot(ax=ax, color="grey", linewidth=0.5)
    if borders is not None:
        borders.boundary.plot(ax=ax, color="black", linewidth=0.5)
    if buffer is not None:
        buffer.boundary.plot(ax=ax, color="black", linewidth=0.5,
                             linestyle="dashed")
    if xlim is not None:
        ax.set_xlim(xlim)
    if ylim is not None:
        ax.set_ylim(ylim)
    plt.title(title)
    plt.legend(handles=patches, bbox_to_anchor=(1.05, 1),
               loc=2, borderaxespad=0.)
    fig.savefig(str(output_file), bbox_inches="tight", dpi=dpi)
    plt.close(fig)

# End
