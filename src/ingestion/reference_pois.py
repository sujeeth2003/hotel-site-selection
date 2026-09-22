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

UNIVERSITIES = [
    {"name": "Georgetown University", "lat": 38.9076, "lon": -77.0723},
    {"name": "George Washington University", "lat": 38.8998, "lon": -77.0472},
    {"name": "American University", "lat": 38.9377, "lon": -77.0891},
    {"name": "Howard University", "lat": 38.9219, "lon": -77.0192},
    {"name": "University of Maryland, College Park", "lat": 38.9869, "lon": -76.9426},
    {"name": "George Mason University", "lat": 38.8318, "lon": -77.3074},
    {"name": "Georgetown Law Center", "lat": 38.8975, "lon": -77.0027},
    {"name": "Catholic University of America", "lat": 38.9339, "lon": -76.9989},
]

HOSPITALS = [
    {"name": "MedStar Georgetown University Hospital", "lat": 38.9127, "lon": -77.0761},
    {"name": "MedStar Washington Hospital Center", "lat": 38.9339, "lon": -77.0136},
    {"name": "George Washington University Hospital", "lat": 38.9012, "lon": -77.0480},
    {"name": "Inova Fairfax Hospital", "lat": 38.8462, "lon": -77.2260},
    {"name": "Suburban Hospital (Bethesda)", "lat": 38.9847, "lon": -77.0947},
    {"name": "Holy Cross Hospital (Silver Spring)", "lat": 39.0231, "lon": -77.0197},
    {"name": "Virginia Hospital Center (Arlington)", "lat": 38.8783, "lon": -77.1103},
    {"name": "Johns Hopkins Hospital (Baltimore)", "lat": 39.2969, "lon": -76.5928},
]

