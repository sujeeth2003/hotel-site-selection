"""
Reference point-of-interest data for the DC + Maryland + Northern Virginia demo region.

These are real, publicly known landmark coordinates (airports, universities,
hospitals, convention centers) entered directly rather than scraped, since
this environment's network access does not reach OSM Overpass / Census API.
In a full deployment (see docs/data_sources.md) these are replaced by live
pulls from OpenStreetMap, Census TIGER/Line, and HIFLD open data.
"""
from __future__ import annotations

AIRPORTS = [
    {"name": "Ronald Reagan Washington National Airport", "lat": 38.8512, "lon": -77.0402, "type": "major"},
    {"name": "Washington Dulles International Airport", "lat": 38.9531, "lon": -77.4565, "type": "major"},
    {"name": "Baltimore/Washington International Airport", "lat": 39.1774, "lon": -76.6684, "type": "major"},
]

