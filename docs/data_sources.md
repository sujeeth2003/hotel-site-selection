# Data Sources

## Currently used (this build)

| Dataset | Source | What it contains | License | Coverage | Used for |
|---|---|---|---|---|---|
| Reference POIs | Hand-entered, publicly known coordinates | Airports, universities, hospitals, convention centers, attractions, business districts, highway interchanges | Public fact, no license restriction | DC/MD/VA | Distance/radius features |
| Hotel inventory | Generated (`src/ingestion/generate_hotel_inventory.py`) | Synthetic hotel records clustered around real business districts, with brand-tier/room-count distributions calibrated to plausible market composition | N/A — synthetic | DC/MD/VA | Competition + cannibalization features |
| Demand surface | Generated (`src/ingestion/generate_demand_surface.py`) | Population density / median income / business activity grid, distance-decay model calibrated to real DC-metro magnitudes | N/A — synthetic | DC/MD/VA | Demand features |

