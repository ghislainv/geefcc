"""Compute fcc on GEE using the TMF product."""

import ee
import xarray as xr
import pandas as pd

def chunk_lon_lat(ds: xr.Dataset, chunk_size: int) -> xr.Dataset:
    """Chunk dimensions lon and lat of `ds` dataset."""
    return ds.chunk({"lon": chunk_size, "lat": chunk_size})

def get_forest_tmf(years: list[int], proj: str, scale: float,
                   region: ee.Geometry) -> xr.Dataset:
    """Get forest cover change from GEE using the TMF product.
    """

    date_list = range(years[0]-1, years[-1] + 1)
    IC = ee.ImageCollection(
        "projects/JRC/TMF/"
        "v1_2022/AnnualChanges")\
            .select([f"Dec{year}" for year in date_list])
    ds = xr.open_dataset(IC,engine="ee",crs=proj,scale=scale,
                         geometry=region,).\
                        isel(time=0).drop_vars('time').squeeze()
    ds = chunk_lon_lat(ds, 1500)

    AP = xr.concat([ds[f"Dec{i}"] for i in date_list],
                   dim = pd.Index(date_list, name="years")
                   ).rename("Annuals Products")

    def forest_masking(AP):
        return (AP==1) + (AP==2)

    def determine_forest(AP_forest, year, ref_year):
        return AP_forest.sel(years=slice(year-1, ref_year+1)).\
                sum("years").\
                rename("forest"+str(year)) >= 1

    AP_forest = AP.map_blocks(forest_masking)
    AP_forest = AP_forest.chunk({"years": AP_forest.sizes['years']})
    return xr.merge([AP_forest.map_blocks(
            determine_forest,
            kwargs={"year":year, "ref_year":years[-1]})
            for year in years])


def get_forest_gfc(years: list[int], proj: str, scale: float,
                   region: ee.Geometry, perc: int) -> xr.Dataset:
    """Get forest cover change from GEE using the GFC product.
    """

    IC = ee.ImageCollection(ee.Image("UMD/hansen/global_forest_change_2023_v1_11"))

    ds = xr.open_dataset(IC,
                        engine='ee',
                        crs=proj,
                        scale=scale,
                        geometry=region,
                        ).drop_vars('time').squeeze()
    ds = chunk_lon_lat(ds, 1500)

    def forest_perc(treecover, perc):
        return treecover>=perc

    # Forest in 2000
    forest2000 = ds["treecover2000"].\
        map_blocks(forest_perc, kwargs={"perc":perc})

    # Deforestation
    def determine_loss(lossyear, year):
        return (lossyear>=1) & (lossyear<=year-2000-1)

    fyears = years[1:] if 2000 in years else years
    forest = xr.merge(
        [forest2000.where(
            ds.lossyear.map_blocks(determine_loss,kwargs={"year":year})).\
        astype(bool).rename("forest"+str(year)) for year in fyears])
    if 2000 in years:
        forest['forest2000'] = forest2000

    return forest

def get_forest(
    years: list[int],
    extent: tuple[float, float, float, float],
    source: str,
    proj: str,
    scale: float,
    perc: int,
) -> xr.Dataset:
    """Get forest cover change from GEE.

    :param years: List of years defining time-periods for estimating
        forest cover change. Years for computing forest cover change
        can be in the interval 2001--2024 for GFC (GFC does not
        provide loss for the year 2000) and 2000--2023 for TMF.
    :param extent: Extent of the region, expressed as a tuple of (min_lon,
        min_lat, max_lon, max_lat).
    :param source: Either "gfc" for Global Forest Change or "tmf" for
        Tropical Moist Forest. If "gfc", the tree cover threshold
        defining the forest must be specified with parameter `perc`.
    :param proj: Projection.
    :param scale: Scale convertion factor from degrees to meters.
    :param perc: Tree cover threshold defining the forest for GFC product.

    :return: Forest cover for each year of `years`,
        as an xarray dataset.
    """
    region = ee.Geometry.Rectangle(extent, proj=proj, geodesic=False)
    if source == "gfc":
        return get_forest_gfc(years, proj, scale, region, perc)
    return get_forest_tmf(years, proj, scale, region)


# End
