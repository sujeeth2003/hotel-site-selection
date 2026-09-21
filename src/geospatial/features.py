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


def to_projected_gdf(df: pd.DataFrame, lat_col: str = "lat", lon_col: str = "lon") -> gpd.GeoDataFrame:
    geometry = [Point(xy) for xy in zip(df[lon_col], df[lat_col])]
    gdf = gpd.GeoDataFrame(df.copy(), geometry=geometry, crs=GEOGRAPHIC_CRS)
    return gdf.to_crs(PROJECTED_CRS)


def nearest_distance_m(candidates_gdf: gpd.GeoDataFrame, targets_gdf: gpd.GeoDataFrame) -> np.ndarray:
    """Distance in meters from each candidate to the nearest target geometry."""
    if len(targets_gdf) == 0:
        return np.full(len(candidates_gdf), np.nan)
    joined = gpd.sjoin_nearest(candidates_gdf, targets_gdf, distance_col="_dist_m", how="left")
    # sjoin_nearest can duplicate rows on ties — keep the closest per candidate
    joined = joined.groupby(joined.index)["_dist_m"].min()
    return joined.reindex(candidates_gdf.index).values


