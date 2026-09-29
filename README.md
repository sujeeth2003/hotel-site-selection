# Hotel Market Opportunity & Site Selection Engine

An independent portfolio project modeling a real hotel-industry decision:
**where should a hotel company consider opening its next hotel?**

> This project is an independent portfolio implementation inspired by real-world
> hotel market analysis and site-selection workflows. It uses generated/public
> reference data and does not use any proprietary company data.

## What it does

Given a candidate site, the engine scores it on demand, accessibility, competition,
and cannibalization of the company's own existing portfolio, using real geospatial
calculations (projected-CRS distances, radius counts, density surfaces) — not
hardcoded numbers. It generates and ranks candidate sites across the region,
segments markets with unsupervised clustering, and includes an AI analyst that
answers natural-language questions by calling tools over the real dataset.

## Quickstart

```bash
pip install -r requirements.txt
python run_pipeline.py          # ingest -> features -> score -> model -> save
streamlit run app/streamlit_app.py
```

Open `http://localhost:8501`. Everything (map, scores, model results, AI analyst)
is computed by the pipeline you just ran — nothing in the UI is hardcoded.

## Architecture

```
Reference POIs + generated hotel/demand data (src/ingestion/)
        |
Candidate grid generation (src/features/candidates.py)
        |
Geospatial feature engineering — projected CRS, real distance/radius math
(src/geospatial/features.py)
        |
Opportunity scoring — transparent, weighted, configurable
(src/scoring/opportunity_score.py)
        |
ML: proxy-target regression + market segmentation (src/modeling/train.py)
        |
Streamlit dashboard (app/streamlit_app.py) + AI Analyst tool layer (app/analyst_tools.py)
```

## Tech stack

```
Python, GeoPandas, Shapely, PyProj, scikit-learn, Streamlit, Plotly, pytest
(Anthropic API — optional, for LLM-routed AI Analyst)
```

## Methodology summary

- **Geospatial features** are computed in EPSG:6487 (a projected, meter-based CRS
  for the DC-metro region) — never in raw lat/lon — via `geopandas.sjoin_nearest`
  and true buffer polygons for radius counts.
- **Opportunity Score** = weighted combination of percentile-ranked demand,
  accessibility, and market-gap scores, minus competition and cannibalization
  penalties. Weights are user-configurable in the sidebar; the score is fully
  explainable per-site via a waterfall breakdown.
- **Cannibalization Score** is a separate signal from competition — it only
  measures proximity to the *company's own* portfolio hotels, since a new hotel
  near a competitor is a market-share fight, but near your own hotel it's
  self-cannibalization.
- **Market segmentation** uses KMeans with k chosen by silhouette score, and
  cluster labels are derived from each cluster's actual characteristics after
  fitting (never hardcoded).
- **ML model** predicts a documented proxy target (see Limitations) using
  Linear Regression, Random Forest, and Gradient Boosting; the best model by
  R² is kept and its feature importances are shown.

Full detail in `docs/methodology.md` and `docs/data_sources.md`.

## Limitations (read this)

- **No real hotel performance data.** No free, programmatically-accessible
  dataset of hotel occupancy/ADR/revenue by coordinate exists for this build.
  The ML target is a documented synthetic *Market Performance Index* — an
  independently-weighted proxy with injected noise, never presented as real
  revenue. Model R² is reported honestly (moderate, ~0.26-0.28) rather than
  inflated.
- **Hotel inventory and population/income surfaces are generated, not scraped
  live.** This sandbox's network access does not reach OSM Overpass or the
  Census API. Generation is anchored to *real* landmark coordinates
  (`src/ingestion/reference_pois.py` — actual airports, universities,
  hospitals, business districts) with a distance-decay model calibrated to
  realistic DC-metro density/income magnitudes, so market *shape* is
  plausible even though individual hotel records are synthetic. Swapping in
  live OSM/Census pulls only requires rewriting `src/ingestion/*` — the
  geospatial/scoring/modeling layers already consume the same schema.
- **Region scope** is DC + Maryland + Northern Virginia, as specified.
- **No PostgreSQL/PostGIS or FastAPI layer yet** — this build uses Parquet +
  GeoPandas locally, which is correct and sufficient at this data volume, and
  is a straightforward migration (schema sketched in `sql/schema.sql`).

## Production architecture (proposed, not deployed)

```
Public Data Sources (Census, OSM) → S3 → Glue/Lambda → Athena → PostgreSQL/PostGIS
→ SageMaker (model training) → FastAPI → Streamlit → Bedrock (LLM analyst)
```

**Implemented locally:** everything above the line. **Proposed only:** AWS deployment.

