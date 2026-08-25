"""TMF forest transition (loss/gain) analysis."""

from dataclasses import dataclass
import warnings

import ee


CLASS_NAMES = {
    1: "F to F",
    2: "F to D",
    3: "D to oR",
    4: "F to oR (via D)",
    5: "oR to oR",
    6: "oR to D",
}

PALETTE = [
    "#228B22",
    "#E31A1C",
    "#1E64C8",
    "#64A0E6",
    "#96BE8C",
    "#FF8C00",
]

TMF_ANNUAL_CHANGES_ASSET = "projects/JRC/TMF/v1_2025/AnnualChanges"
TMF_COLLECTION_START_YEAR = 1990


@dataclass
class TmfLossGainResult:
    """Result of ee_tmf_loss_gain."""
    fcc: ee.Image
    state1: ee.Image
    state2: ee.Image
    palette: list
    class_names: dict


def _get_old_regrowth_mask(annual_changes, year, min_years):
    years = list(range(year - min_years + 1, year + 1))
    band_names = [f"Dec{y}" for y in years]
    recent_bands = annual_changes.select(band_names)
    years_as_regrowth = recent_bands.eq(4).reduce(ee.Reducer.sum())
    return years_as_regrowth.eq(min_years)


def _recode_state(ac, old_regrowth_mask):
    forest = ac.eq(1).Or(ac.eq(2))
    old_regrowth = ac.eq(4).And(old_regrowth_mask)
    state = ee.Image(3).rename("state")
    state = state.where(forest, 1)
    state = state.where(old_regrowth, 4)
    return state


def ee_tmf_loss_gain(year1, year2, min_years=10):
    """Compute TMF forest transition classes between two years."""

    if year2 <= year1:
        raise ValueError("year2 must be greater than year1")
    if min_years < 1:
        raise ValueError("min_years must be >= 1")
    if (year1 - 1) - min_years + 1 < TMF_COLLECTION_START_YEAR:
        warnings.warn(
            f"min_years extends before {TMF_COLLECTION_START_YEAR} for "
            f"year1={year1}. Old-regrowth detection will be incomplete.",
            stacklevel=2,
        )

    annual_changes = ee.ImageCollection(TMF_ANNUAL_CHANGES_ASSET).mosaic()

    band1 = f"Dec{year1 - 1}"
    band2 = f"Dec{year2 - 1}"
    ac1 = annual_changes.select(band1)
    ac2 = annual_changes.select(band2)

    old_mask1 = _get_old_regrowth_mask(annual_changes, year1 - 1, min_years)
    old_mask2 = _get_old_regrowth_mask(annual_changes, year2 - 1, min_years)

    state1 = _recode_state(ac1, old_mask1)
    state2 = _recode_state(ac2, old_mask2)

    fcc = ee.Image(0).rename("fcc")
    fcc = fcc.where(state1.eq(1).And(state2.eq(1)), 1)
    fcc = fcc.where(state1.eq(1).And(state2.eq(3)), 2)
    fcc = fcc.where(state1.eq(3).And(state2.eq(4)), 3)
    fcc = fcc.where(state1.eq(1).And(state2.eq(4)), 4)
    fcc = fcc.where(state1.eq(4).And(state2.eq(4)), 5)
    fcc = fcc.where(state1.eq(4).And(state2.eq(3)), 6)

    fcc = fcc.set(
        "system:time_start", ee.Date.fromYMD(year1, 1, 1).millis(),
        "system:time_end", ee.Date.fromYMD(year2, 1, 1).millis(),
    )

    return TmfLossGainResult(
        fcc=fcc,
        state1=state1,
        state2=state2,
        palette=PALETTE,
        class_names=CLASS_NAMES,
    )

# End
