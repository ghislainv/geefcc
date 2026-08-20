"""Download GADM data."""

import tempfile
import shutil
from pathlib import Path
from urllib.request import urlretrieve


def download_gadm(iso3, output_file):
    """Download GADM data for a country.

    Download GADM (Global Administrative Areas) for a specific
    country. See `<https://gadm.org>`_\\ .

    Parameters
    ----------
    iso3 : str
        Country ISO 3166-1 alpha-3 code.
    output_file : str or Path
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

    To avoid corrupt files from interrupted downloads, the file is
    first downloaded to a temporary location and then moved to
    ``output_file`` only upon success.

    Data are retrieved from the GADM version 4.1 repository hosted at
    the University of California, Davis:
    ``https://geodata.ucdavis.edu/gadm/gadm4.1/gpkg/``.

    Examples
    --------
    >>> download_gadm("BEN", "gadm41_BEN.gpkg")
    >>> download_gadm("MDG", "/tmp/gadm41_MDG.gpkg")

    """

    output_file = Path(output_file)

    if not output_file.is_file():
        url = ("https://geodata.ucdavis.edu/gadm/gadm4.1/"
               f"gpkg/gadm41_{iso3}.gpkg")
        # Download to a temp file first to avoid partial downloads
        with tempfile.NamedTemporaryFile(delete=False,
                                        suffix=".gpkg") as tmp:
            tmp_path = Path(tmp.name)
        try:
            urlretrieve(url, tmp_path)
            shutil.move(tmp_path, output_file)
        except Exception:
            tmp_path.unlink(missing_ok=True)
            raise

# End
