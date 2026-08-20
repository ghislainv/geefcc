"""Download GADM data."""

import os
from urllib.request import urlretrieve
import tempfile, shutil

def download_gadm(iso3, output_file):
    """Download GADM data for a country.

    Download GADM (Global Administrative Areas) for a specific
    country. See `<https://gadm.org>`_\\ .

    Parameters
    ----------
    iso3 : str
        Country ISO 3166-1 alpha-3 code.
    output_file : str
        Path to output GPKG file.

    Returns
    -------
    None
        The function downloads the file to ``output_file`` and does
        not return any value.

    Raises
    ------
    urllib.error.URLError
        If the download URL is unreachable or the request fails.
    urllib.error.HTTPError
        If the server returns an HTTP error code (e.g., 404 if the
        country code is not found on the GADM server).
    OSError
        If the output file cannot be written to the specified path.

    Notes
    -----
    The function checks whether ``output_file`` already exists before
    attempting to download. If the file is present, the download is
    skipped entirely.

    Data are retrieved from the GADM version 4.1 repository hosted at
    the University of California, Davis:
    ``https://geodata.ucdavis.edu/gadm/gadm4.1/gpkg/``.

    Examples
    --------
    >>> download_gadm("BEN", "gadm41_BEN.gpkg")
    >>> download_gadm("MDG", "/tmp/gadm41_MDG.gpkg")

    """

    if not os.path.isfile(output_file):
        url = ("https://geodata.ucdavis.edu/gadm/gadm4.1/"
               f"gpkg/gadm41_{iso3}.gpkg")
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            try:
                urlretrieve(url, tmp.name)
                shutil.move(tmp.name, output_file)
            except Exception:
                os.unlink(tmp.name)
                raise

# End
