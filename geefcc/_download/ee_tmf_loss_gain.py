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
    7: "oA to oA",
    8: "oA to D",
    9: "D to oA",
}

PALETTE = [
    "#228B22",  # 1: F to F
    "#E31A1C",  # 2: F to D
    "#1E64C8",  # 3: D to oR
    "#64A0E6",  # 4: F to oR (via D)
    "#96BE8C",  # 5: oR to oR
    "#FF8C00",  # 6: oR to D
    "#9B59B6",  # 7: oA to oA
    "#FFD700",  # 8: oA to D
    "#BDC3E6",  # 9: D to oA
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
    """Return a mask of pixels continuously classified as regrowth for min_years.

    Checks that the pixel holds TMF value 4 (regrowth) in every one of
    the ``min_years`` bands ending at ``year`` (i.e. the window
    ``[year - min_years + 1, year]``). This is used to identify
    regrowth old enough to qualify as old regrowth (oR) or old
    afforestation (oA).

    Parameters
    ----------
    annual_changes : ee.Image
        Mosaicked TMF AnnualChanges image containing one band per year
        named ``DecYYYY``.
    year : int
        Last year of the consecutive window to check (inclusive).
    min_years : int
        Number of consecutive years the pixel must be classified as
        regrowth (TMF value 4).

    Returns
    -------
    ee.Image
        Binary mask (1 = at least ``min_years`` consecutive years of
        regrowth ending at ``year``, 0 otherwise).
    """
    years = list(range(year - min_years + 1, year + 1))
    band_names = [f"Dec{y}" for y in years]
    recent_bands = annual_changes.select(band_names)
    years_as_regrowth = recent_bands.eq(4).reduce(ee.Reducer.sum())
    return years_as_regrowth.eq(min_years)


def _get_ever_forest_mask(annual_changes, year):
    """Return a mask of pixels that had TMF value 1 at least once before year.

    Searches the full TMF history from TMF_COLLECTION_START_YEAR up to
    and including (year - 1), i.e. all years strictly before the
    reference year.

    Parameters
    ----------
    annual_changes : ee.Image
        Mosaicked TMF AnnualChanges image containing one band per year
        named ``DecYYYY``.
    year : int
        Reference year (exclusive upper bound). Bands up to
        ``Dec{year - 1}`` are included in the search.

    Returns
    -------
    ee.Image
        Binary mask (1 = pixel was forest at least once, 0 = never
        forest).
    """
    years = list(range(TMF_COLLECTION_START_YEAR, year))
    band_names = [f"Dec{y}" for y in years]
    history_bands = annual_changes.select(band_names)
    ever_forest = history_bands.eq(1).reduce(ee.Reducer.sum())
    return ever_forest.gt(0)


def _recode_state(ac, old_regrowth_mask, ever_forest_mask):
    """Recode a TMF annual changes band into internal states.

    States:
    - 1 : forest (TMF values 1 or 2)
    - 3 : non-forest / deforested
    - 4 : old regrowth (oR) — consecutive regrowth >= min_years AND pixel
          was forest at some point in the TMF history
    - 5 : old afforestation (oA) — consecutive regrowth >= min_years AND
          pixel was NEVER forest in the TMF history
    """
    forest = ac.eq(1).Or(ac.eq(2))
    old_regrowth_candidate = ac.eq(4).And(old_regrowth_mask)
    old_regrowth = old_regrowth_candidate.And(ever_forest_mask)
    old_afforestation = old_regrowth_candidate.And(ever_forest_mask.Not())

    state = ee.Image(3).rename("state")
    state = state.where(forest, 1)
    state = state.where(old_regrowth, 4)
    state = state.where(old_afforestation, 5)
    return state


def ee_tmf_loss_gain(year1, year2, min_years=10):
    """Compute TMF forest transition classes between two years.

    Differentiates old regrowth (oR) from old afforestation (oA) based
    on whether the pixel was ever classified as forest (TMF value 1) in
    the full TMF history prior to ``year1``.

    Transition classes:

    - 0 = stable non-forest (background / no transition)
    - 1 = F to F   : stable forest
    - 2 = F to D   : forest to deforested
    - 3 = D to oR  : non-forest to old regrowth (reforestation)
    - 4 = F to oR  : forest to old regrowth via deforestation
    - 5 = oR to oR : stable old regrowth
    - 6 = oR to D  : old regrowth to deforested
    - 7 = oA to oA : stable old afforestation
    - 8 = oA to D  : old afforestation to deforested
    - 9 = D to oA  : non-forest to old afforestation

    Parameters
    ----------
    year1 : int
        Start year.
    year2 : int
        End year. Must be greater than ``year1``.
    min_years : int, optional
        Minimum number of consecutive years classified as regrowth (TMF
        value 4) to be considered "old" regrowth or afforestation.
        Default is ``10``.

    Returns
    -------
    TmfLossGainResult
        Dataclass with fields ``fcc``, ``state1``, ``state2``,
        ``palette``, ``class_names``.
    """

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

    # ever_forest_mask is the same for both dates: it looks at the full
    # TMF history strictly before year1, independent of year2.
    ever_forest_mask = _get_ever_forest_mask(annual_changes, year1)

    state1 = _recode_state(ac1, old_mask1, ever_forest_mask)
    state2 = _recode_state(ac2, old_mask2, ever_forest_mask)

    fcc = ee.Image(0).rename("fcc")
    fcc = fcc.where(state1.eq(1).And(state2.eq(1)), 1)  # F to F
    fcc = fcc.where(state1.eq(1).And(state2.eq(3)), 2)  # F to D
    # Reforestation-related transitions (oR, state 4)
    fcc = fcc.where(state1.eq(3).And(state2.eq(4)), 3)  # D to oR
    fcc = fcc.where(state1.eq(1).And(state2.eq(4)), 4)  # F to oR (via D)
    fcc = fcc.where(state1.eq(4).And(state2.eq(4)), 5)  # oR to oR
    fcc = fcc.where(state1.eq(4).And(state2.eq(3)), 6)  # oR to D
    # Afforestation-related transitions (oA, state 5)
    fcc = fcc.where(state1.eq(5).And(state2.eq(5)), 7)  # oA to oA
    fcc = fcc.where(state1.eq(5).And(state2.eq(3)), 8)  # oA to D
    fcc = fcc.where(state1.eq(3).And(state2.eq(5)), 9)  # D to oA

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
