Changelog
*********

geefcc 0.1.8 (dev)
==================

* This version includes forest gain in addition to forest loss when
  deriving the forest cover change map.
* Function `get_fcc` is deprecated and has been replaced by `get_fcc_loss`.
* Function `get_fcc_loss_gain` has been added.
* Changes: https://github.com/ghislainv/geefcc/compare/v0.1.7...v0.1.8

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
  
