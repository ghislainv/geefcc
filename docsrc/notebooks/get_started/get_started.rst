===========
Get started
===========




.. _get-forest-cover-change-from-tmf:

Get forest cover change from TMF
--------------------------------

The function ``.get_fcc()`` can be used to download forest cover change
from the Tropical Moist Forest product. We will use the Reunion Island
(isocode “REU”) as a case study.

.. code:: python

    import os

    import ee
    import geefcc
    import rioxarray

.. code:: python

    # Initialize GEE
    ee.Initialize(project="forestatrisk", opt_url="https://earthengine-highvolume.googleapis.com")

.. code:: python

    # Download data from GEE
    if not os.path.isfile("out_tmf/forest_tmf.tif"):
        geefcc.get_fcc(
            aoi="REU",
            years=[2000, 2010, 2020],
            source="tmf",
            parallel=False,
            crop_to_aoi=True,
            tile_size=0.5,
            output_file="out_tmf/forest_tmf.tif",
        )

::

    get_fcc running, 3 tiles ....


.. code:: python

    # Load data
    forest_tmf = rioxarray.open_rasterio("out_tmf/forest_tmf.tif")
    forest_tmf

::

    <xarray.DataArray (band: 3, y: 1923, x: 2305)> Size: 13MB
    [13297545 values with dtype=int8]
    Coordinates:
      * band         (band) int64 24B 1 2 3
      * x            (x) float64 18kB 55.22 55.22 55.22 55.22 ... 55.84 55.84 55.84
      * y            (y) float64 15kB -20.87 -20.87 -20.87 ... -21.39 -21.39 -21.39
        spatial_ref  int64 8B 0
    Attributes:
        AREA_OR_POINT:  Area
        scale_factor:   1.0
        add_offset:     0.0


.. code:: python

    # Plot
    geefcc.plots.plot_fcc("out_tmf/forest_tmf.tif", output_file="tmf.png")

.. image:: tmf.png
    :width: 800
    :align: center

.. _compare-with-forest-cover-change-from-gfc:

Compare with forest cover change from GFC
-----------------------------------------

.. code:: python

    # Get data from GEE
    if not os.path.isfile("out_gfc_50/forest_gfc_50.tif"):
        geefcc.get_fcc(
            aoi="REU",
            years=[2001, 2010, 2020],  # Here, first year must be 2001 (1st Jan)
            source="gfc",
            perc=50,
            parallel=False,
            crop_to_aoi=True,
            tile_size=0.5,
            output_file="out_gfc_50/forest_gfc_50.tif",
        )

::

    get_fcc running, 3 tiles ....


.. code:: python

    # Plot
    geefcc.plots.plot_fcc("out_tmf/forest_gfc.tif", output_file="gfc.png", source="gfc")

.. image:: gfc.png
    :width: 800
    :align: center

.. _comparing-forest-cover-in-2020-between-tmf-and-gfc:

Comparing forest cover in 2020 between TMF and GFC
--------------------------------------------------

.. code:: python

    # Plot
    geefcc.plots.plot_fc_tmf_vs_gfc(input_tmf_raster = "out_tmf/forest_tmf.tif",
                                    input_gfc_raster = "out_gfc/forest_gfc.tif",
                                    output_file="comp.png")

.. image:: comp.png
    :width: 800
    :align: center

Differences are quite important between the two data-sets. This might
change depending on the tree cover threshold (here = 75%) we select for
defining forest with the GFC dataset.

.. _download-data-from-an-extent:

Download data from an extent
----------------------------

We will use the following extent which corresponds to a region around
the Analamazaotra special reserve in Madagascar.

.. code:: python

    if not os.path.isfile("out_tmf_extent/forest_tmf_extent.tif"):
        geefcc.get_fcc(
            aoi=(48.4, -19.0, 48.6, -18.8),
            years=[2000, 2010, 2020],
            source="tmf",
            tile_size=0.2,
            output_file="out_tmf_extent/forest_tmf_extent.tif",
        )

.. code:: python

    # Plot
    geefcc.plots.plot_fcc("out_tmf_extent/forest_tmf_extent.tif", output_file="extent.png")

.. image:: extent.png
    :width: 700
    :align: center
