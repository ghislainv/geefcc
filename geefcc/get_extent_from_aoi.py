"""Get extent from aoi."""

import os

from download_gadm import download_gadm
from make_grid import create_buffer
from get_vector_extent import get_vector_extent

opj = os.path.join
opd = os.path.dirname


def get_extent_from_aoi(aoi, buff, out_dir):
    """Get extent from aoi.

    :param aoi: Area of interest defined either by a country iso code
        (three letters), a vector file, or an extent in lat/long
        (tuple with (xmin, ymin, xmax, ymax)).

    :param buff: Buffer around the aoi. In decimal degrees
        (e.g. 0.08983152841195216 correspond to ~10 km at the
        equator).

    :out_dir: Output directory.

    :return: A dictionary including extent and border vector file.
    """

    # Set aoi_isfile
    aoi_isfile = True

    # aoi = country iso code
    if isinstance(aoi, str) and len(aoi) == 3:
        # Download borders
        iso = aoi
        borders_gpkg = opj(out_dir, f"gadm41_{iso}_0.gpkg")
        download_gadm(iso, output_file=borders_gpkg)
        # Buffer around borders
        if buff > 0:
            buff_file = opj(
                out_dir,
                f"gadm41_{iso}_buffer.gpkg")
            create_buffer(input_file=borders_gpkg,
                          output_file=buff_file,
                          buffer_dist=buff)
            borders_gpkg = buff_file
        # Extent
        extent_latlong = get_vector_extent(borders_gpkg)

    # aoi = extent
    elif isinstance(aoi, tuple) and len(aoi) == 4:
        aoi_isfile = False
        # nb: We could create a vector file here...
        borders_gpkg = None
        if buff > 0:
            extent_latlong = (aoi[0] - buff, aoi[1] - buff,
                              aoi[2] + buff, aoi[3] + buff)
        else:
            extent_latlong = aoi

    # aoi = gpkg file
    elif os.path.isfile(aoi) and aoi[-5:] == ".gpkg":
        # Buffer around borders
        if buff > 0:
            buff_file = opj(
                out_dir,
                "borders_buffer.gpkg")
            create_buffer(input_file=aoi,
                          output_file=buff_file,
                          buffer_dist=buff)
            borders_gpkg = buff_file
        else:
            borders_gpkg = aoi
        # Extent
        extent_latlong = get_vector_extent(borders_gpkg)

    # Else raise error
    else:
        raise ValueError("aoi must be either a country iso code, "
                         "an extent, or a gpkg file")

    return {"extent_latlong": extent_latlong,
            "borders_gpkg": borders_gpkg,
            "aoi_isfile": aoi_isfile}


# End
