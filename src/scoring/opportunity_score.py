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

