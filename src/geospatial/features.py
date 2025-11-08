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


def count_within_radius(candidates_gdf: gpd.GeoDataFrame, targets_gdf: gpd.GeoDataFrame, radius_m: float) -> np.ndarray:
    """Count of target points within radius_m of each candidate (proper buffer + spatial join)."""
    if len(targets_gdf) == 0:
        return np.zeros(len(candidates_gdf), dtype=int)
    buffers = candidates_gdf.copy()
    buffers["geometry"] = buffers.geometry.buffer(radius_m)
    joined = gpd.sjoin(buffers, targets_gdf, predicate="contains", how="left")
    counts = joined.groupby(joined.index).size()
    # sjoin drops candidates with zero matches from the groupby result — reindex to fill 0
    return counts.reindex(candidates_gdf.index, fill_value=0).values


def build_site_features(
    candidates: pd.DataFrame,
    hotels: pd.DataFrame,
    demand_grid: pd.DataFrame,
    airports: list[dict],
    universities: list[dict],
    hospitals: list[dict],
    attractions: list[dict],
    highways: list[dict],
    convention_centers: list[dict],
) -> pd.DataFrame:
    """
    Computes the full geospatial feature set for each candidate location:
    distance features, radius counts, density features, and demand-surface
    lookups. All distance/radius math happens in a projected CRS (meters).
    """
    cand_gdf = to_projected_gdf(candidates)
    all_hotels_gdf = to_projected_gdf(hotels)
    competitor_gdf = to_projected_gdf(hotels[~hotels["is_portfolio"]])
    portfolio_gdf = to_projected_gdf(hotels[hotels["is_portfolio"]])

    airports_gdf = to_projected_gdf(pd.DataFrame(airports))
    universities_gdf = to_projected_gdf(pd.DataFrame(universities))
    hospitals_gdf = to_projected_gdf(pd.DataFrame(hospitals))
    attractions_gdf = to_projected_gdf(pd.DataFrame(attractions))
    highways_gdf = to_projected_gdf(pd.DataFrame(highways))
    conventions_gdf = to_projected_gdf(pd.DataFrame(convention_centers))

    feat = candidates.copy()

    # --- Distance features (meters -> miles for readability) ---
    feat["dist_nearest_airport_mi"] = nearest_distance_m(cand_gdf, airports_gdf) / MILE_TO_M
    feat["dist_nearest_highway_mi"] = nearest_distance_m(cand_gdf, highways_gdf) / MILE_TO_M
    feat["dist_nearest_competitor_mi"] = nearest_distance_m(cand_gdf, competitor_gdf) / MILE_TO_M
    feat["dist_nearest_portfolio_hotel_mi"] = nearest_distance_m(cand_gdf, portfolio_gdf) / MILE_TO_M
    feat["dist_nearest_attraction_mi"] = nearest_distance_m(cand_gdf, attractions_gdf) / MILE_TO_M
    feat["dist_nearest_university_mi"] = nearest_distance_m(cand_gdf, universities_gdf) / MILE_TO_M
    feat["dist_nearest_hospital_mi"] = nearest_distance_m(cand_gdf, hospitals_gdf) / MILE_TO_M
    feat["dist_nearest_convention_center_mi"] = nearest_distance_m(cand_gdf, conventions_gdf) / MILE_TO_M

