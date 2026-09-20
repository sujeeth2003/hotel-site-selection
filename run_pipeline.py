"""Runs the full local pipeline: ingest -> features -> score -> model -> save artifacts."""
import json
import time

import pandas as pd

from src.ingestion.generate_hotel_inventory import generate_hotels
from src.ingestion.generate_demand_surface import generate_grid
from src.ingestion.reference_pois import (
    AIRPORTS, UNIVERSITIES, HOSPITALS, ATTRACTIONS, HIGHWAYS, CONVENTION_CENTERS,
)
from src.features.candidates import generate_candidates
from src.geospatial.features import build_site_features
from src.scoring.opportunity_score import compute_opportunity_score, DEFAULT_WEIGHTS
from src.modeling.train import build_proxy_target, compare_models, feature_importance, segment_markets, name_clusters, FEATURE_COLS


def main():
    t0 = time.time()
    print("1/6 Ingesting hotel inventory + demand surface...")
    hotels = generate_hotels()
    demand_grid = generate_grid()
    candidates = generate_candidates()
    hotels.to_parquet("data/processed/hotels.parquet", index=False)
    demand_grid.to_parquet("data/processed/demand_grid.parquet", index=False)
    candidates.to_parquet("data/processed/candidates.parquet", index=False)

    print("2/6 Building geospatial features for", len(candidates), "candidates...")
    feat = build_site_features(
        candidates, hotels, demand_grid,
        AIRPORTS, UNIVERSITIES, HOSPITALS, ATTRACTIONS, HIGHWAYS, CONVENTION_CENTERS,
    )

