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

    print("3/6 Computing opportunity scores...")
    scored = compute_opportunity_score(feat, DEFAULT_WEIGHTS)

    print("4/6 Training models on proxy Market Performance Index...")
    y = build_proxy_target(scored)
    X = scored[FEATURE_COLS].fillna(0)
    results, best_model, best_name, scaler = compare_models(X, y)
    importances = feature_importance(best_model, FEATURE_COLS)
    print(results)
    print("Best model:", best_name)

    print("5/6 Market segmentation (KMeans)...")
    labels, k, sil = segment_markets(scored)
    cluster_names = name_clusters(scored, labels)
    scored["cluster_id"] = labels
    scored["cluster_name"] = scored["cluster_id"].map(cluster_names)
    print(f"k={k}, silhouette={sil}")
    print(scored["cluster_name"].value_counts())

    print("6/6 Saving artifacts...")
    scored.to_parquet("data/processed/scored_candidates.parquet", index=False)
    results.to_csv("data/processed/model_comparison.csv", index=False)
    importances.to_csv("data/processed/feature_importance.csv", index=False)
    with open("data/processed/model_meta.json", "w") as f:
        json.dump({
            "best_model": best_name,
            "silhouette": sil,
            "n_clusters": int(k),
            "cluster_names": {str(k_): v for k_, v in cluster_names.items()},
        }, f, indent=2)

    print(f"Done in {time.time()-t0:.1f}s. {len(scored)} scored candidates, {len(hotels)} hotels.")


if __name__ == "__main__":
    main()
