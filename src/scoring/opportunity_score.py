"""
Site Opportunity Score: a transparent, configurable weighted scoring system.

Opportunity Score = Demand + Accessibility + Market Gap - Competition - Cannibalization

Each component is normalized to 0-100 using percentile rank within the
current candidate set (robust to outliers, unlike min-max scaling). Weights
are configurable and every component contribution is retained on the output
so the score is explainable (see explain_score()).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

DEFAULT_WEIGHTS = {
    "demand": 0.35,
    "accessibility": 0.20,
    "market_gap": 0.20,
    "competition": 0.15,
    "cannibalization": 0.10,
}


def _pct_rank(s: pd.Series) -> pd.Series:
    return s.rank(pct=True) * 100


def compute_component_scores(feat: pd.DataFrame) -> pd.DataFrame:
    out = feat.copy()

    # Demand: population density + income + business activity + attraction/hospital/university proximity
    demand_raw = (
        _pct_rank(out["pop_density_per_sqmi"]) * 0.35
        + _pct_rank(out["median_income"]) * 0.15
        + _pct_rank(out["business_activity_index"]) * 0.25
        + _pct_rank(out["attractions_within_3mi"]) * 0.15
        + _pct_rank(-out["dist_nearest_hospital_mi"]) * 0.05
        + _pct_rank(-out["dist_nearest_university_mi"]) * 0.05
    )
    out["demand_score"] = demand_raw.clip(0, 100)

    # Accessibility: closer to airport/highway/convention center = better (inverse distance)
    access_raw = (
        _pct_rank(-out["dist_nearest_airport_mi"]) * 0.35
        + _pct_rank(-out["dist_nearest_highway_mi"]) * 0.40
        + _pct_rank(-out["dist_nearest_convention_center_mi"]) * 0.25
    )
    out["accessibility_score"] = access_raw.clip(0, 100)

    # Market gap: high demand relative to existing hotel supply nearby = under-served market
    supply_pressure = _pct_rank(out["hotels_within_3mi"])
    out["market_gap_score"] = (out["demand_score"] - 0.6 * supply_pressure).clip(0, 100)

    # Competition penalty: competitor density + proximity to nearest competitor
    comp_raw = (
        _pct_rank(out["competitors_within_3mi"]) * 0.6
        + _pct_rank(-out["dist_nearest_competitor_mi"]) * 0.4
    )
    out["competition_penalty"] = comp_raw.clip(0, 100)

    # Cannibalization: overlap with the company's OWN existing portfolio nearby
    cannib_raw = (
        _pct_rank(out["portfolio_hotels_within_3mi"]) * 0.5
        + _pct_rank(out["portfolio_hotels_within_5mi"]) * 0.3
        + _pct_rank(-out["dist_nearest_portfolio_hotel_mi"]) * 0.2
    )
    out["cannibalization_score"] = cannib_raw.clip(0, 100)
    out["cannibalization_risk_level"] = pd.cut(
        out["cannibalization_score"], bins=[-1, 25, 50, 75, 100],
        labels=["Low", "Moderate", "High", "Very High"]
    )
    return out


