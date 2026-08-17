"""TMF forest transition (loss/gain) analysis using the JRC Tropical Moist
Forest Annual Change Collection.
"""

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
    "#228B22",  # 1. F to F, green
    "#E31A1C",  # 2. F to D, red
    "#1E64C8",  # 3. D to oR, medium-strong blue
    "#64A0E6",  # 4. F to oR (via D), medium blue
    "#96BE8C",  # 5. oR to oR, muted light green
    "#FF8C00",  # 6. oR to D, orange
]

TMF_ANNUAL_CHANGES_ASSET = "projects/JRC/TMF/v1_2025/AnnualChanges"
TMF_COLLECTION_START_YEAR = 1990


@dataclass
class TmfLossGainResult:
    """Result of :func:`ee_tmf_lossgain`.

    Attributes:
        fcc: ee.Image, values 1-6 (0 = not in any class).
        state1: ee.Image, recoded state (F/D/oR) at year1.
        state2: ee.Image, recoded state (F/D/oR) at year2.
        palette: list of hex color strings for classes 1-6.
        class_names: dict mapping class value (int) to class label (str).
    """

    fcc: ee.Image
    state1: ee.Image
    state2: ee.Image
    palette: list
    class_names: dict


def _get_old_regrowth_mask(
    annual_changes: ee.Image, year: int, min_years: int
) -> ee.Image:
    """Mask of pixels classified as regrowth (val 4) continuously for
    `min_years` years ending at `year` (inclusive)."""
    years = list(range(year - min_years + 1, year + 1))
    band_names = [f"Dec{y}" for y in years]
    recent_bands = annual_changes.select(band_names)
    years_as_regrowth = recent_bands.eq(4).reduce(ee.Reducer.sum())
    return years_as_regrowth.eq(min_years)


def _recode_state(ac: ee.Image, old_regrowth_mask: ee.Image) -> ee.Image:
    """Recode an AnnualChanges band into 3 states: 1=F, 3=D (incl. young
    regrowth), 4=oR."""
    forest = ac.eq(1).Or(ac.eq(2))
    old_regrowth = ac.eq(4).And(old_regrowth_mask)
    state = ee.Image(3).rename("state")
    state = state.where(forest, 1)
    state = state.where(old_regrowth, 4)
    return state


def ee_tmf_loss_gain(
    year1: int,
    year2: int,
    min_years: int = 10,
) -> TmfLossGainResult:
    """Compute TMF forest transition classes (loss/gain) between two dates.

    Recodes the JRC Tropical Moist Forest (TMF) Annual Change Collection into
    6 transition classes between two reference years, distinguishing old
    regrowth (continuously classified as regrowth for at least `min_years`)
    from young regrowth / non-forest.

    Transition classes:
        1. F to F -- stable forest (undisturbed or degraded at both dates)
        2. F to D -- deforestation (includes young regrowth at year2)
        3. D to oR -- non-forest / young regrowth becoming old regrowth
        4. F to oR (via D) -- forest cleared then regrown to old regrowth
           within the window
        5. oR to oR -- stable old regrowth
        6. oR to D -- old regrowth deforested, or fallen back below
           `min_years` of continuous regrowth

    Pixels that remain "D" (non-forest, including young regrowth) at both
    dates are left unmasked (value 0), since young regrowth is treated as
    non-forest by design.

    JRC TMF annual change values used internally: 1 = undisturbed forest,
    2 = degraded forest, 3 = deforested land, 4 = regrowth, 5 = water,
    6 = other land cover.

    Args:
        year1: Start year (state assessed at Dec 31 of year1 - 1).
        year2: End year (state assessed at Dec 31 of year2 - 1). Must be
            greater than year1.
        min_years: Minimum number of consecutive years classified as
            regrowth (TMF annual value 4) to be considered "old regrowth"
            (oR). Default 10.

    Returns:
        TmfLossGainResult dataclass instance.

    Raises:
        ValueError: if year2 <= year1 or min_years < 1.

    Example:
        >>> import ee
        >>> ee.Initialize()
        >>> aoi = (
        ...     ee.FeatureCollection("FAO/GAUL/2015/level0")
        ...     .filter(ee.Filter.eq("ADM0_NAME", "New Caledonia"))
        ...     .geometry()
        ... )
        >>> res = ee_tmf_lossgain(aoi, year1=2015, year2=2025, min_years=10)
        >>> res.fcc
    """
    if year2 <= year1:
        raise ValueError("year2 must be greater than year1")
    if min_years < 1:
        raise ValueError("min_years must be >= 1")
    if (year1 - 1) - min_years + 1 < TMF_COLLECTION_START_YEAR:
        warnings.warn(
            f"min_years extends before {TMF_COLLECTION_START_YEAR} (start "
            f"of the TMF Annual Change Collection) for year1={year1}. "
            "Old-regrowth detection near the start of the record will be "
            "incomplete.",
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
    fcc = fcc.where(state1.eq(1).And(state2.eq(1)), 1)  # F -> F
    fcc = fcc.where(state1.eq(1).And(state2.eq(3)), 2)  # F -> D
    fcc = fcc.where(state1.eq(3).And(state2.eq(4)), 3)  # D -> oR
    fcc = fcc.where(state1.eq(1).And(state2.eq(4)), 4)  # F -> oR (via D)
    fcc = fcc.where(state1.eq(4).And(state2.eq(4)), 5)  # oR -> oR
    fcc = fcc.where(state1.eq(4).And(state2.eq(3)), 6)  # oR -> D

    # Temporal metadata
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
