# Data Sources

## Currently used (this build)

| Dataset | Source | What it contains | License | Coverage | Used for |
|---|---|---|---|---|---|
| Reference POIs | Hand-entered, publicly known coordinates | Airports, universities, hospitals, convention centers, attractions, business districts, highway interchanges | Public fact, no license restriction | DC/MD/VA | Distance/radius features |
| Hotel inventory | Generated (`src/ingestion/generate_hotel_inventory.py`) | Synthetic hotel records clustered around real business districts, with brand-tier/room-count distributions calibrated to plausible market composition | N/A — synthetic | DC/MD/VA | Competition + cannibalization features |
| Demand surface | Generated (`src/ingestion/generate_demand_surface.py`) | Population density / median income / business activity grid, distance-decay model calibrated to real DC-metro magnitudes | N/A — synthetic | DC/MD/VA | Demand features |

## Intended for production (not reachable from this build environment)

| Dataset | Source | License | Notes |
|---|---|---|---|
| Population, income | US Census ACS 5-Year via Census API | Public domain | Block-group level; replaces `generate_demand_surface.py` |
| Roads, hotels, POIs, hospitals, universities | OpenStreetMap via Overpass API / OSMnx | ODbL | Replaces `reference_pois.py` and `generate_hotel_inventory.py` |
| Airports | FAA / OurAirports | Public domain | Cross-check against reference POIs |
| Administrative boundaries | US Census TIGER/Line | Public domain | For region-scope expansion beyond DC/MD/VA |

## Why generated data was used here

This execution environment's network egress is restricted to package
registries (pip/npm/GitHub) — it cannot reach the Census API or OSM Overpass.
Rather than fabricate an ingestion module that pretends to hit those APIs, or
skip the geospatial layer entirely, this build generates data anchored to
real landmark coordinates and calibrated to realistic regional magnitudes,
and documents this limitation everywhere it's relevant (README, in-app
warning on the Model Insights page, this file). Swapping in live sources is a
rewrite of `src/ingestion/` only — every downstream module (features, scoring,
modeling) consumes the same schema regardless of where the rows came from.
