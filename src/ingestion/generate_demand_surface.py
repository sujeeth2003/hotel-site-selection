"""
Generates a population/income/business-activity grid for the region.

LIMITATION: Census API is unreachable from this sandbox. Real deployment
pulls ACS block-group population + median income via the Census API
(see docs/data_sources.md). This module builds a plausible demand surface by
combining distance-decay from real business districts (higher density/income
near urban cores, decaying outward) with regional noise, calibrated to
roughly match known DC-metro population density magnitudes (order of
magnitude ~5,000-11,000/sq mi in the urban core, ~1,000-3,000 suburban).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from src.ingestion.reference_pois import BUSINESS_DISTRICTS

RNG = np.random.default_rng(7)

REGION_BOUNDS = {"lat_min": 38.75, "lat_max": 39.10, "lon_min": -77.55, "lon_max": -76.85}


def _haversine_km(lat1, lon1, lat2, lon2):
    r = 6371.0
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlmb = np.radians(lon2 - lon1)
    a = np.sin(dphi / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dlmb / 2) ** 2
    return 2 * r * np.arcsin(np.sqrt(a))


def generate_grid(cell_deg: float = 0.01) -> pd.DataFrame:
    lats = np.arange(REGION_BOUNDS["lat_min"], REGION_BOUNDS["lat_max"], cell_deg)
    lons = np.arange(REGION_BOUNDS["lon_min"], REGION_BOUNDS["lon_max"], cell_deg)
    grid_lat, grid_lon = np.meshgrid(lats, lons)
    grid_lat, grid_lon = grid_lat.ravel(), grid_lon.ravel()

    n = len(grid_lat)
    min_dist = np.full(n, np.inf)
    for d in BUSINESS_DISTRICTS:
        dist = _haversine_km(grid_lat, grid_lon, d["lat"], d["lon"])
        min_dist = np.minimum(min_dist, dist)

    # Distance-decay density model, roughly calibrated to DC-metro magnitudes
    density = 11000 * np.exp(-min_dist / 4.5) + 900 + RNG.normal(0, 250, n)
    density = np.clip(density, 150, None)

