-- Production PostGIS schema (proposed — not used by the local Parquet build).
-- Migration path: src/ingestion/* writes here instead of data/processed/*.parquet;
-- src/geospatial/features.py becomes ST_Distance / ST_DWithin SQL instead of GeoPandas joins.

CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE hotels (
    hotel_id        TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    brand           TEXT,
    is_portfolio    BOOLEAN NOT NULL DEFAULT FALSE,
    tier            TEXT,
    rooms           INTEGER,
    geom            GEOMETRY(Point, 4326) NOT NULL
);
CREATE INDEX hotels_geom_idx ON hotels USING GIST (geom);

CREATE TABLE poi (
    poi_id      SERIAL PRIMARY KEY,
    category    TEXT NOT NULL,  -- airport | university | hospital | attraction | convention_center | highway | business_district
    name        TEXT NOT NULL,
    tier        INTEGER,
    geom        GEOMETRY(Point, 4326) NOT NULL
);
CREATE INDEX poi_geom_idx ON poi USING GIST (geom);
CREATE INDEX poi_category_idx ON poi (category);

CREATE TABLE population (
    cell_id                     TEXT PRIMARY KEY,
    pop_density_per_sqmi        NUMERIC,
    median_income               NUMERIC,
    business_activity_index     NUMERIC,
    geom                        GEOMETRY(Point, 4326) NOT NULL
);
CREATE INDEX population_geom_idx ON population USING GIST (geom);

CREATE TABLE candidate_locations (
    candidate_id    TEXT PRIMARY KEY,
    label           TEXT,
    geom            GEOMETRY(Point, 4326) NOT NULL
);
CREATE INDEX candidate_geom_idx ON candidate_locations USING GIST (geom);

CREATE TABLE market_features (
    candidate_id                    TEXT PRIMARY KEY REFERENCES candidate_locations(candidate_id),
    dist_nearest_airport_mi         NUMERIC,
    dist_nearest_highway_mi         NUMERIC,
    dist_nearest_competitor_mi      NUMERIC,
    dist_nearest_portfolio_hotel_mi NUMERIC,
    hotels_within_3mi               INTEGER,
    competitors_within_3mi          INTEGER,
    portfolio_hotels_within_3mi     INTEGER,
    pop_density_per_sqmi            NUMERIC,
    median_income                   NUMERIC,
    computed_at                     TIMESTAMPTZ DEFAULT now()
);

