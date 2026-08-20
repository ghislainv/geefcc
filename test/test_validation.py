"""Tests for input validation and utility functions."""

import pytest

import geefcc as gf
from geefcc.get_extent_from_aoi import get_extent_from_aoi


# ============================================================
# Tests for get_extent_from_aoi validation (tuple aoi)
# ============================================================

def test_aoi_tuple_invalid_xmin_xmax():
    """Raise ValueError when xmin >= xmax."""
    with pytest.raises(ValueError, match="xmin"):
        get_extent_from_aoi((10.0, -5.0, 5.0, 5.0), buff=0, out_dir="/tmp")


def test_aoi_tuple_invalid_ymin_ymax():
    """Raise ValueError when ymin >= ymax."""
    with pytest.raises(ValueError, match="ymin"):
        get_extent_from_aoi((-10.0, 5.0, 10.0, -5.0), buff=0, out_dir="/tmp")


def test_aoi_tuple_x_out_of_bounds():
    """Raise ValueError when x coordinates are out of [-180, 180]."""
    with pytest.raises(ValueError, match="xmin"):
        get_extent_from_aoi((-200.0, -5.0, 10.0, 5.0), buff=0, out_dir="/tmp")


def test_aoi_tuple_y_out_of_bounds():
    """Raise ValueError when y coordinates are out of [-90, 90]."""
    with pytest.raises(ValueError, match="ymin"):
        get_extent_from_aoi((-10.0, -100.0, 10.0, 5.0), buff=0, out_dir="/tmp")


def test_aoi_tuple_valid():
    """Valid tuple extent returns correct dict structure."""
    result = get_extent_from_aoi((-10.0, -5.0, 10.0, 5.0), buff=0,
                                 out_dir="/tmp")
    assert result["aoi_isfile"] is False
    assert result["borders_gpkg"] is None
    assert result["extent_latlong"] == (-10.0, -5.0, 10.0, 5.0)


def test_aoi_tuple_valid_with_buffer():
    """Valid tuple extent with buffer is correctly applied."""
    result = get_extent_from_aoi((-10.0, -5.0, 10.0, 5.0), buff=1.0,
                                 out_dir="/tmp")
    assert result["extent_latlong"] == (-11.0, -6.0, 11.0, 6.0)


def test_aoi_invalid_type():
    """Raise ValueError for unsupported aoi type."""
    with pytest.raises(ValueError, match="aoi must be"):
        get_extent_from_aoi(12345, buff=0, out_dir="/tmp")


# ============================================================
# Tests for get_fcc_loss default arguments
# ============================================================

def test_get_fcc_loss_default_years_not_shared():
    """Ensure default years list is not shared between calls."""
    import inspect
    sig = inspect.signature(gf.get_fcc_loss)
    assert sig.parameters["years"].default is None


# ============================================================
# Tests for get_fcc_loss source validation
# ============================================================

def test_get_fcc_loss_invalid_source():
    """Raise ValueError for unknown source."""
    with pytest.raises(ValueError, match="source must be"):
        gf.get_fcc_loss(
            aoi=(-10.0, -5.0, 10.0, 5.0),
            source="invalid_source",
            output_file="/tmp/test_fcc.tif"
        )

# End
