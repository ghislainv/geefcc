#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ==============================================================================
# author          :Ghislain Vieilledent
# email           :ghislain.vieilledent@cirad.fr, ghislainv@gmail.com
# web             :https://ecology.ghislainv.fr
# python_version  :>=2.7
# license         :GPLv3
# ==============================================================================

# Import
from __future__ import division, print_function  # Python 3 compatibility
import os

import json
import numpy as np
from osgeo import ogr
import requests

from .get_token import get_token

# get_wdpa()


def get_wdpa(iso3, output_dir="."):
    """This function downloads protected areas for one country using the
    WDPA API. Protected areas defined by a point are not
    considered. The shapefile is written on the hard drive (in the
    current directory).

    :param iso3: The ISO-3 code of the country.

    :param output_dir: Directory used for download.

    """

    os.environ["SHAPE_ENCODING"] = "utf-8"
    base_url = "https://api.protectedplanet.net/"
    category = "v3/countries/"
    wdpa_token = get_token()
    request = base_url + category + iso3 + "?token=" + wdpa_token
    response = requests.get(request)

    if response.status_code == 404:
        return "Invalid ISO-3 code"

    response = json.loads(response.text)  # Equivalent to response.json()

    pas_count = response["country"]["pas_count"]
    pages = list(range(int(np.ceil(pas_count / 50.0))))

    if pas_count is not None:

        # Create the output shapefile
        output_file = os.path.join(output_dir, "pa_" + iso3 + ".shp")
        driver = ogr.GetDriverByName("ESRI Shapefile")
        if os.path.exists(output_file):
            driver.DeleteDataSource(output_file)
        ds = driver.CreateDataSource(output_file)
        # Create the spatial reference, WGS84
        srs = ogr.osr.SpatialReference()
        srs.ImportFromEPSG(4326)
        layer = ds.CreateLayer("wdpa", srs, ogr.wkbMultiPolygon)
        # Add attributes
        layer.CreateField(ogr.FieldDefn("wdpa_id", ogr.OFTInteger))
        layer.CreateField(ogr.FieldDefn("pa_name", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("orig_name", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("ctry_iso3", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("owner_type", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("is_marine", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("type", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("iucn_cat", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("status", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("date", ogr.OFTString))

        # API
        category = "v3/protected_areas/search/"

        # Loop on pages
        for p in pages:
            request = "".join(
                [base_url, category, "?token=", wdpa_token,
                 "&with_geometry=", "true", "&country=",
                 iso3, "&per_page=", str(50), "&page=", str(p+1)]
            )

            response = requests.get(request)
            response = response.json()
            response = response["protected_areas"]

            # Number of protected areas
            npa = len(response)

            # Loop on protected areas
            for i in range(npa):

                # Get pa geometry from json
                pa = response[i]
                g = ogr.CreateGeometryFromJson(
                    json.dumps(pa["geojson"]["geometry"])
                )

                # # If point, convert to polygon with a buffer
                # if (g.GetGeometryName() is "POINT" and pa["reported_area"] is not "0.0"):
                #     area = np.float(pa["reported_area"])
                #     buffer_size = int(round(np.sqrt(area/np.pi)*1000))
                #     g = g.Buffer(buffer_size)

                # If polygon, add feature
                if g.GetGeometryName() in ["POLYGON", "MULTIPOLYGON"]:
                    # Create feature with geometry and attributes
                    featureDefn = layer.GetLayerDefn()
                    feature = ogr.Feature(featureDefn)
                    feature.SetGeometry(g)
                    feature.SetField("wdpa_id", pa["wdpa_id"])
                    feature.SetField("pa_name", pa["name"])
                    feature.SetField(
                        "orig_name", pa["original_name"])
                    feature.SetField("ctry_iso3", iso3)
                    feature.SetField("owner_type", pa["owner_type"])
                    feature.SetField("is_marine", str(pa["marine"]))
                    feature.SetField(
                        "type", pa["designation"]["name"])
                    feature.SetField("iucn_cat", pa["iucn_category"]["name"])
                    feature.SetField("status", pa["legal_status"]["name"])
                    feature.SetField("date", pa["legal_status_updated_at"])
                    # Add feature to layer
                    layer.CreateFeature(feature)
                    # Dereference the feature
                    feature = None

        # Save and close the data source
        ds = None

    else:
        return "The WDPA does not contain any protected areas for " + iso3

# End
