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

