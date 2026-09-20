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

