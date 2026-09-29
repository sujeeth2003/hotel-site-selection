import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
import pytest

from src.geospatial.features import to_projected_gdf, nearest_distance_m, count_within_radius, MILE_TO_M
from src.scoring.opportunity_score import compute_opportunity_score, DEFAULT_WEIGHTS


def test_projected_distance_matches_known_value():
    # Two points ~1 mile apart along a meridian (roughly 0.0145 deg lat)
    a = pd.DataFrame({"lat": [38.90], "lon": [-77.03]})
    b = pd.DataFrame({"lat": [38.9145], "lon": [-77.03]})
    a_gdf, b_gdf = to_projected_gdf(a), to_projected_gdf(b)
    dist = nearest_distance_m(a_gdf, b_gdf)[0]
    assert 1400 < dist < 1750  # ~1 mile in meters, generous tolerance


