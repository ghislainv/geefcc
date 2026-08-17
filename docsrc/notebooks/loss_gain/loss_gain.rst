=============
Loss and gain
=============



Get forest cover change from TMF
--------------------------------

The function ``.get_fcc_loss_gain()`` can be used to download forest cover change
from the Tropical Moist Forest product.

This function, contrary to ``get_fcc_loss()`` which accounts only for loss in the forest cover change, considers both forest loss and gain (or regrowth) to derive the forest cover change map.

We will use the Reunion Island (isocode “REU”) as a case study.

.. code:: python

    import os

    import ee
    import geefcc
    import matplotlib.pyplot as plt
    from matplotlib.colors import ListedColormap
    import matplotlib.patches as mpatches
    import cartopy.crs as ccrs
    import rioxarray

.. code:: python

    # Initialize GEE
    ee.Initialize(project="deforisk", opt_url="https://earthengine-highvolume.googleapis.com")

.. code:: python

    # Download data from GEE
    ofile = os.path.join("out_tmf", "fcc_tmf.tif") 
    if not os.path.isfile(ofile):
        geefcc.get_fcc_loss_gain(
            aoi="REU",
            year1=2015,
            year2=2025,
            min_years=5,
            source="tmf",
            tile_size=0.5,
            crop_to_aoi=True,
            parallel=True,
            output_file=ofile,
        )

.. code:: python

    # Load data
    fcc_tmf = rioxarray.open_rasterio("out_tmf/fcc_tmf.tif")
    fcc_tmf

::

    <xarray.DataArray (band: 1, y: 1924, x: 2305)> Size: 4MB
    [4434820 values with dtype=uint8]
    Coordinates:
      * band         (band) int64 8B 1
      * y            (y) float64 15kB -20.87 -20.87 -20.87 ... -21.39 -21.39 -21.39
      * x            (x) float64 18kB 55.22 55.22 55.22 55.22 ... 55.84 55.84 55.84
        spatial_ref  int64 8B 0
    Attributes:
        AREA_OR_POINT:  Area
        scale_factor:   1.0
        add_offset:     0.0
        long_name:      fcc

Plot the forest cover change map
--------------------------------

.. code:: python

    # Colors
    cols=[(34, 139, 34, 255), (227, 26, 28, 255), (30, 100, 200, 255),
          (100, 160, 230, 255), (150, 190, 140, 255), (255, 140, 0, 255)]
    colors = [(1, 1, 1, 0)]  # transparent white for 0
    cmax = 255.0  # float for division
    for col in cols:
        col_class = tuple([i / cmax for i in col])
        colors.append(col_class)
    color_map = ListedColormap(colors)

    # Labels
    labels = {0: "stable non-forest", 1: "stable forest", 2: "forest --> deforested",
              3: "non-forest --> old regrowth", 4: "forest --> old regrowth (via deforestation)",
              5: "stable old-regrowth", 6: "old regrowth --> deforested"}
    patches = [mpatches.Patch(facecolor=col, edgecolor="black",
                              label=labels[i]) for (i, col) in enumerate(colors)]

.. code:: python

    # Plot
    fig = plt.figure()
    ax = fig.add_axes([0, 0, 1, 1], projection=ccrs.PlateCarree())
    raster_image = fcc_tmf.plot(ax=ax, cmap=color_map, add_colorbar=False)
    plt.title("Forest cover change 2015-2025, TMF")
    plt.legend(handles=patches, bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    fig.savefig("tmf.png", bbox_inches="tight", dpi=100)
    plt.close(fig)

.. image:: tmf.png
    :width: 800
    :align: center
