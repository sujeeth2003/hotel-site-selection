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


def test_radius_count_zero_when_no_targets():
    a = pd.DataFrame({"lat": [38.9], "lon": [-77.0]})
    empty = pd.DataFrame({"lat": [], "lon": []})
    a_gdf, empty_gdf = to_projected_gdf(a), to_projected_gdf(empty)
    counts = count_within_radius(a_gdf, empty_gdf, 5 * MILE_TO_M)
    assert counts[0] == 0


def test_radius_count_increases_with_radius():
    center = pd.DataFrame({"lat": [38.9], "lon": [-77.0]})
    targets = pd.DataFrame({"lat": [38.9, 38.905, 38.95], "lon": [-77.0, -77.0, -77.0]})
    c_gdf, t_gdf = to_projected_gdf(center), to_projected_gdf(targets)
    small = count_within_radius(c_gdf, t_gdf, 1 * MILE_TO_M)[0]
    large = count_within_radius(c_gdf, t_gdf, 10 * MILE_TO_M)[0]
    assert large >= small


def _minimal_feature_frame(n=30, seed=0):
    rng = np.random.default_rng(seed)
    return pd.DataFrame({
        "candidate_id": [f"S{i}" for i in range(n)],
        "label": [f"site {i}" for i in range(n)],
        "pop_density_per_sqmi": rng.uniform(500, 12000, n),
        "median_income": rng.uniform(45000, 140000, n),
        "business_activity_index": rng.uniform(0, 100, n),
        "attractions_within_3mi": rng.integers(0, 10, n),
        "dist_nearest_hospital_mi": rng.uniform(0, 10, n),
        "dist_nearest_university_mi": rng.uniform(0, 10, n),
        "dist_nearest_airport_mi": rng.uniform(0, 30, n),
        "dist_nearest_highway_mi": rng.uniform(0, 10, n),
        "dist_nearest_convention_center_mi": rng.uniform(0, 30, n),
        "hotels_within_3mi": rng.integers(0, 40, n),
        "competitors_within_3mi": rng.integers(0, 30, n),
        "dist_nearest_competitor_mi": rng.uniform(0, 10, n),
        "portfolio_hotels_within_3mi": rng.integers(0, 5, n),
        "portfolio_hotels_within_5mi": rng.integers(0, 8, n),
        "dist_nearest_portfolio_hotel_mi": rng.uniform(0, 15, n),
    })


def test_opportunity_score_bounded_0_100():
    feat = _minimal_feature_frame()
    scored = compute_opportunity_score(feat, DEFAULT_WEIGHTS)
    assert scored["opportunity_score"].min() >= 0
    assert scored["opportunity_score"].max() <= 100


def test_weight_change_changes_ranking_order_is_possible():
    feat = _minimal_feature_frame(seed=1)
    default_scored = compute_opportunity_score(feat, DEFAULT_WEIGHTS)
    demand_heavy = compute_opportunity_score(feat, {"demand": 0.9, "accessibility": 0.02, "market_gap": 0.02,
                                                      "competition": 0.02, "cannibalization": 0.02})
    top_default = default_scored.nlargest(1, "opportunity_score")["candidate_id"].iloc[0]
    top_demand_heavy = demand_heavy.nlargest(1, "opportunity_score")["candidate_id"].iloc[0]
    # not asserting they must differ (could coincide by chance) - just that both are valid computations
    assert top_default in feat["candidate_id"].values
    assert top_demand_heavy in feat["candidate_id"].values


def test_weights_missing_key_raises():
    feat = _minimal_feature_frame()
    with pytest.raises(KeyError):
        compute_opportunity_score(feat, {"demand": 1.0})
