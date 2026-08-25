"""Initialize GEE."""

import os
import json

import ee


def ee_initialize(token_name, project, **kwargs):
    """Initialize Google Earth Engine (GEE).

    Parameters
    ----------
    token_name : str
        The name of the environment variable containing the Earth Engine
        authentication token.
    project : str
        Name of the Google Cloud project to use with Earth Engine.
    **kwargs : dict, optional
        Additional keyword arguments passed to ``ee.Initialize()``.

    Returns
    -------
    None
    """

    ee_token = os.environ.get(token_name)
    credential_file_path = os.path.expanduser(
        "~/.config/earthengine/credentials")

    if not os.path.exists(credential_file_path):
        os.makedirs(os.path.dirname(credential_file_path), exist_ok=True)
        if ee_token.startswith("{") and ee_token.endswith("}"):
            token_dict = json.loads(ee_token)
            with open(credential_file_path, "w", encoding="utf-8") as f:
                f.write(json.dumps(token_dict))
        else:
            credential = '{"refresh_token":"%s"}' % ee_token
            with open(credential_file_path, "w", encoding="utf-8") as f:
                f.write(credential)

    ee.Initialize(project=project, **kwargs)

# End
