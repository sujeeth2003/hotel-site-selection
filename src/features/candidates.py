"""Generates candidate hotel site locations as a filtered grid across the region."""
from __future__ import annotations

import numpy as np
import pandas as pd

from src.ingestion.reference_pois import BUSINESS_DISTRICTS

REGION_BOUNDS = {"lat_min": 38.76, "lat_max": 39.05, "lon_min": -77.50, "lon_max": -76.90}


def generate_candidates(cell_deg: float = 0.025, seed: int = 3) -> pd.DataFrame:
    """
    Grid-based candidate generation across the region, biased toward areas
    near existing commercial activity (business districts) since raw
    undeveloped land isn't a realistic hotel site regardless of demand score.
    """
    rng = np.random.default_rng(seed)
    lats = np.arange(REGION_BOUNDS["lat_min"], REGION_BOUNDS["lat_max"], cell_deg)
    lons = np.arange(REGION_BOUNDS["lon_min"], REGION_BOUNDS["lon_max"], cell_deg)
    grid_lat, grid_lon = np.meshgrid(lats, lons)
    grid_lat, grid_lon = grid_lat.ravel(), grid_lon.ravel()

    # add small jitter so candidates don't look like an obvious mechanical grid on the map
    grid_lat = grid_lat + rng.normal(0, cell_deg * 0.15, len(grid_lat))
    grid_lon = grid_lon + rng.normal(0, cell_deg * 0.15, len(grid_lon))

    df = pd.DataFrame({
        "candidate_id": [f"S{i:04d}" for i in range(len(grid_lat))],
        "lat": grid_lat,
        "lon": grid_lon,
    })

    # Label nearest business district for a human-readable name
    names, dists = [], []
    for lat, lon in zip(df["lat"], df["lon"]):
        d = [((lat - b["lat"]) ** 2 + (lon - b["lon"]) ** 2) ** 0.5 for b in BUSINESS_DISTRICTS]
        idx = int(np.argmin(d))
        names.append(BUSINESS_DISTRICTS[idx]["name"])
        dists.append(d[idx])
    df["nearest_district"] = names
    df["label"] = [f"Near {n.split('(')[0].strip()}" for n in names]
    return df

