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


def build_proxy_target(feat: pd.DataFrame, seed: int = 11) -> pd.Series:
    """
    Market Performance Index (0-100), a documented PROXY for real occupancy/
    revenue potential. Independent weighting from the scoring engine;
    includes noise so it isn't trivially learnable (deliberately caps
    achievable R^2, which we report honestly rather than hide).
    """
    rng = np.random.default_rng(seed)
    z = lambda s: (s - s.mean()) / (s.std() + 1e-9)
    raw = (
        0.30 * z(feat["pop_density_per_sqmi"])
        + 0.20 * z(feat["business_activity_index"])
        + 0.15 * z(feat["attractions_within_3mi"])
        + 0.15 * z(-feat["dist_nearest_airport_mi"])
        + 0.10 * z(-feat["dist_nearest_convention_center_mi"])
        - 0.10 * z(feat["competitors_within_3mi"])
    )
    noise = rng.normal(0, 0.6, len(feat))  # substantial noise -> realistic, imperfect model
    raw = raw + noise
    pct = pd.Series(raw).rank(pct=True) * 100
    return pct.round(1)


def compare_models(X: pd.DataFrame, y: pd.Series) -> tuple[pd.DataFrame, object, str, StandardScaler]:
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)
    scaler = StandardScaler().fit(X_train)
    X_train_s, X_test_s = scaler.transform(X_train), scaler.transform(X_test)

    candidates = {
        "Linear Regression": LinearRegression(),
        "Random Forest": RandomForestRegressor(n_estimators=300, max_depth=8, random_state=42),
        "Gradient Boosting": GradientBoostingRegressor(n_estimators=300, max_depth=3, learning_rate=0.05, random_state=42),
    }

    rows, fitted = [], {}
    for name, model in candidates.items():
        model.fit(X_train_s, y_train)
        pred = model.predict(X_test_s)
        rows.append({
            "model": name,
            "MAE": round(mean_absolute_error(y_test, pred), 2),
            "RMSE": round(mean_squared_error(y_test, pred) ** 0.5, 2),
            "R2": round(r2_score(y_test, pred), 3),
        })
        fitted[name] = model

    results = pd.DataFrame(rows).sort_values("R2", ascending=False).reset_index(drop=True)
    best_name = results.iloc[0]["model"]
    return results, fitted[best_name], best_name, scaler


def feature_importance(model, feature_names: list[str]) -> pd.DataFrame:
    if hasattr(model, "feature_importances_"):
        imp = model.feature_importances_
    elif hasattr(model, "coef_"):
        imp = np.abs(model.coef_)
    else:
        imp = np.zeros(len(feature_names))
    df = pd.DataFrame({"feature": feature_names, "importance": imp})
    return df.sort_values("importance", ascending=False).reset_index(drop=True)


def segment_markets(feat: pd.DataFrame, k: int | None = None) -> tuple[pd.Series, int, float]:
    from sklearn.metrics import silhouette_score

    X = StandardScaler().fit_transform(feat[CLUSTER_COLS].fillna(0))

    if k is None:
        best_k, best_sil = 3, -1
        for candidate_k in range(3, 7):
            labels = KMeans(n_clusters=candidate_k, n_init=10, random_state=42).fit_predict(X)
            sil = silhouette_score(X, labels)
            if sil > best_sil:
                best_k, best_sil = candidate_k, sil
        k = best_k
    else:
        best_sil = silhouette_score(X, KMeans(n_clusters=k, n_init=10, random_state=42).fit_predict(X))

