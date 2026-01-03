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

