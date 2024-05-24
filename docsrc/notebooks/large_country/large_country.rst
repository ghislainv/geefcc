===============
Large countries
===============


We can use ``geefcc`` to download forest cover change for large countries,
for example Perou (iso code “PER”). The country will be divided into
several tiles which are processed in parallel. If your computer has 8
cores, 7 cores will be used in parallel.

.. code:: python

    import os
    import time

    import ee
    from geefcc import get_fcc

.. code:: python

    # Initialize GEE
    ee.Initialize(project="forestatrisk", opt_url="https://earthengine-highvolume.googleapis.com")

.. code:: python

    start_time = time.time()
    get_fcc(
        aoi="MTQ",
        buff=0.08983152841195216,
        years=[2000, 2010, 2020],
        source="tmf",
        tile_size=1,
        output_file="out_tmf/fcc_tmf.tif",
    )
    end_time = time.time()


.. code:: python

    # Computation time
    elapsed_time = (end_time - start_time) / 60
    print('Execution time:', elapsed_time, 'minutes')
