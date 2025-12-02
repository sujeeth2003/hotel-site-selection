"""
Modeling module.

IMPORTANT / HONESTY NOTE (see docs/methodology.md and README limitations):
No public dataset of actual hotel occupancy/ADR/revenue by exact coordinate
exists for free ingestion in this environment. Rather than fabricate that or
skip modeling entirely, we construct a documented, clearly-labeled proxy
target — a "Market Performance Index" (MPI) built from a DIFFERENT weighting
formula over raw observed variables than the Opportunity Score uses, plus
injected noise, to avoid circularity (the model must actually learn
generalizable relationships, not just re-derive the scoring formula). This is
explicitly a proxy, not real performance data, and is labeled as such
everywhere it's displayed.

FEATURE_COLS below are the true model inputs (raw geospatial/demand
variables only — never engineered score components), so the model is
learning from primary features, same as the scoring engine, but is
evaluated independently.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

FEATURE_COLS = [
    "pop_density_per_sqmi", "median_income", "business_activity_index",
    "dist_nearest_airport_mi", "dist_nearest_highway_mi", "dist_nearest_attraction_mi",
    "dist_nearest_university_mi", "dist_nearest_hospital_mi", "dist_nearest_convention_center_mi",
    "hotels_within_1mi", "hotels_within_3mi", "hotels_within_5mi",
    "competitors_within_3mi", "attractions_within_3mi", "hospitals_within_5mi",
    "universities_within_5mi", "airports_within_25mi", "hotel_density_per_sqmi",
]

CLUSTER_COLS = [
    "pop_density_per_sqmi", "median_income", "hotels_within_3mi", "competitors_within_3mi",
    "attractions_within_3mi", "business_activity_index", "dist_nearest_airport_mi",
]

