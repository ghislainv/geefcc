Changelog
*********

geefcc 0.2.3
============

* Bug corrections.
* Changes: https://github.com/ghislainv/geefcc/compare/v0.2.2...v0.2.3
  
geefcc 0.2.2
============

* Adding functions for plots and statistics.
* Functions were grouped in subdirectories (eg. `plot`, `stat`, `_download`).
* Changes: https://github.com/ghislainv/geefcc/compare/v0.2.1...v0.2.2

geefcc 0.2.1
============

* This version includes **forest gain** in addition to **forest loss**
  when deriving the forest cover change map.
* Function ``get_fcc`` is deprecated and has been replaced by ``get_fcc_loss``.
* Function ``get_fcc_loss_gain`` has been added.
* Use Numpy style for docstrings when documenting functions.
* Code refactoring:

  * **Common pipeline** extracted into ``_run_fcc.py``.
  * **Bug fix**: ``if`` → ``elif/else`` in ``get_fcc_loss``.
  * **Atomic download** implemented in ``download_gadm``.
  * **AOI coordinate validation** added in ``get_extent_from_aoi``.
  * **Retry logic** using ``tenacity`` in ``geeic2geotiff``.
  * **Explicit OGR resource closing** in ``get_vector_extent``.
  * **Mutable default argument fix**: ``years=None`` in ``get_fcc_loss``.
  * **Modernisation**: ``pathlib.Path`` used throughout, with ``str()``
    conversion for GDAL/OGR calls.
  * **Tests**:

    * ``test_validation.py``: tests without GEE (AOI validation, argument
      checking).
    * ``test_get_fcc_loss_gain.py``: tests with GEE on Singapore.

* Changes: https://github.com/ghislainv/geefcc/compare/v0.1.7...v0.2.1
  
geefcc 0.1.7
============

* Using version v1_2025 of TMF.
* Using version 2025_v1_13 of GFC.
* Migrating code to use Xee v0.1.0.
* Use of rioxarray to convert Xarray dataset to GeoTIFF. This makes several internal functions deprecated.
* Changes: https://github.com/ghislainv/geefcc/compare/v0.1.6...v0.1.7

geefcc 0.1.6
============

* Using ``xarray.load_dataset()`` to automatically load and close dataset.
* Adding pyproject.toml.
* Dereference gdal datasets properly.
* Changes: https://github.com/ghislainv/geefcc/compare/v0.1.5...v0.1.6

geefcc 0.1.5
============

* Using version v1_2023 of TMF.
* Adding example with New Caledonia.
* Changes: https://github.com/ghislainv/geefcc/compare/v0.1.4...v0.1.5

geefcc 0.1.4
============

* Replace ``gdal.TermProgress`` with ``gdal.TermProgress_nocb``.
* Changes: https://github.com/ghislainv/geefcc/compare/v0.1.3...v0.1.4

geefcc 0.1.3
============

* Add an option to compute the tiles sequentially
* Change multiprocessing to multiprocess
* Adding ``crop_to_aoi`` argument to function ``get_fcc()``
* Changes: https://github.com/ghislainv/geefcc/compare/v0.1.2...v0.1.3

geefcc 0.1.2
============

* Changing import statements.
* Changes: https://github.com/ghislainv/geefcc/compare/v0.1.1...v0.1.2

geefcc 0.1.1
============

* Adding function sum_raster_band().
* New tutorial for large countries.

geefcc 0.1
==========

* First release of the package.
  
