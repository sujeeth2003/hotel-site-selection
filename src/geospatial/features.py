"""
Geospatial feature engineering for candidate hotel sites.

Uses geopandas with a projected CRS (EPSG:6487, Maryland State Plane-derived
NAD83 / meters, which covers the DC-MD-VA region with low distortion) for all
distance and buffer calculations. Lat/lon (EPSG:4326) is never used directly
for distance math — that's a common and misleading mistake in geospatial code
that this project deliberately avoids.
"""
from __future__ import annotations

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import Point

# NAD83 / Maryland (meters) — reasonable low-distortion projection for the DC metro region
PROJECTED_CRS = "EPSG:6487"
GEOGRAPHIC_CRS = "EPSG:4326"

MILE_TO_M = 1609.344
KM_TO_M = 1000.0


