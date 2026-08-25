"""Get extent from aoi."""

from pathlib import Path

from .download_gadm import download_gadm
from .make_grid import create_buffer
from .get_vector_extent import get_vector_extent


def get_extent_from_aoi(aoi, buff, out_dir):
    """Get extent from aoi."""

    out_dir = Path(out_dir)
    aoi_isfile = True

    # aoi = country iso code
    if isinstance(aoi, str) and len(aoi) == 3:
        iso = aoi
        borders_gpkg = out_dir / f"gadm41_{iso}_0.gpkg"
        download_gadm(iso, output_file=borders_gpkg)
        if buff > 0:
            buff_file = out_dir / f"gadm41_{iso}_buffer.gpkg"
            create_buffer(input_file=borders_gpkg,
                          output_file=buff_file,
                          buffer_dist=buff)
            borders_gpkg = buff_file
        extent_latlong = get_vector_extent(borders_gpkg)

    # aoi = extent tuple
    elif isinstance(aoi, tuple) and len(aoi) == 4:
        aoi_isfile = False
        borders_gpkg = None
        xmin, ymin, xmax, ymax = aoi
        if xmin >= xmax:
            raise ValueError(
                f"Invalid extent: xmin ({xmin}) must be less than xmax ({xmax}).")
        if ymin >= ymax:
            raise ValueError(
                f"Invalid extent: ymin ({ymin}) must be less than ymax ({ymax}).")
        if not (-180 <= xmin <= 180 and -180 <= xmax <= 180):
            raise ValueError(
                f"Invalid extent: xmin ({xmin}) and xmax ({xmax}) "
                "must be in the range [-180, 180].")
        if not (-90 <= ymin <= 90 and -90 <= ymax <= 90):
            raise ValueError(
                f"Invalid extent: ymin ({ymin}) and ymax ({ymax}) "
                "must be in the range [-90, 90].")
        if buff > 0:
            extent_latlong = (xmin - buff, ymin - buff,
                              xmax + buff, ymax + buff)
        else:
            extent_latlong = aoi

    # aoi = gpkg file
    elif isinstance(aoi, (str, Path)) and Path(aoi).is_file() \
            and Path(aoi).suffix == ".gpkg":
        aoi = Path(aoi)
        if buff > 0:
            buff_file = out_dir / "borders_buffer.gpkg"
            create_buffer(input_file=aoi,
                          output_file=buff_file,
                          buffer_dist=buff)
            borders_gpkg = buff_file
        else:
            borders_gpkg = aoi
        extent_latlong = get_vector_extent(borders_gpkg)

    else:
        raise ValueError("aoi must be either a country iso code, "
                         "an extent, or a gpkg file")

    return {"extent_latlong": extent_latlong,
            "borders_gpkg": borders_gpkg,
            "aoi_isfile": aoi_isfile}

# End
