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

CONVENTION_CENTERS = [
    {"name": "Walter E. Washington Convention Center", "lat": 38.9046, "lon": -77.0237},
    {"name": "Gaylord National Convention Center (Oxon Hill)", "lat": 38.7802, "lon": -77.0166},
    {"name": "Dulles Expo Center (Chantilly)", "lat": 38.8965, "lon": -77.4436},
]

ATTRACTIONS = [
    {"name": "National Mall", "lat": 38.8895, "lon": -77.0353, "tier": 1},
    {"name": "Smithsonian National Air & Space Museum", "lat": 38.8882, "lon": -77.0199, "tier": 1},
    {"name": "United States Capitol", "lat": 38.8899, "lon": -77.0091, "tier": 1},
    {"name": "The White House", "lat": 38.8977, "lon": -77.0365, "tier": 1},
    {"name": "Georgetown Waterfront", "lat": 38.9034, "lon": -77.0611, "tier": 2},
    {"name": "Union Market", "lat": 38.9088, "lon": -76.9993, "tier": 2},
    {"name": "Old Town Alexandria", "lat": 38.8048, "lon": -77.0469, "tier": 2},
    {"name": "National Harbor", "lat": 38.7823, "lon": -77.0161, "tier": 2},
    {"name": "Nationals Park", "lat": 38.8730, "lon": -77.0074, "tier": 2},
    {"name": "Capital One Arena", "lat": 38.8981, "lon": -77.0209, "tier": 1},
    {"name": "Wolf Trap National Park", "lat": 38.9385, "lon": -77.2653, "tier": 3},
    {"name": "Great Falls Park", "lat": 38.9977, "lon": -77.2551, "tier": 3},
]

BUSINESS_DISTRICTS = [
    {"name": "Downtown DC / K Street", "lat": 38.9027, "lon": -77.0341},
    {"name": "Rosslyn-Ballston Corridor (Arlington)", "lat": 38.8951, "lon": -77.0714},
    {"name": "Tysons Corner", "lat": 38.9187, "lon": -77.2311},
    {"name": "Bethesda Central Business District", "lat": 38.9847, "lon": -77.0947},
    {"name": "Silver Spring Downtown", "lat": 38.9959, "lon": -77.0261},
    {"name": "Reston Town Center", "lat": 38.9586, "lon": -77.3570},
    {"name": "Crystal City / National Landing", "lat": 38.8563, "lon": -77.0497},
    {"name": "Alexandria Old Town / Carlyle", "lat": 38.8048, "lon": -77.0469},
]

HIGHWAYS = [
    {"name": "I-495 Capital Beltway @ Bethesda", "lat": 38.9847, "lon": -77.1147},
    {"name": "I-495 Capital Beltway @ Tysons", "lat": 38.9260, "lon": -77.2280},
    {"name": "I-395 @ Pentagon", "lat": 38.8719, "lon": -77.0563},
    {"name": "I-95 @ Springfield Interchange", "lat": 38.7893, "lon": -77.1866},
    {"name": "I-270 @ Rockville", "lat": 39.0840, "lon": -77.1528},
    {"name": "US-50 @ New Carrollton", "lat": 38.9490, "lon": -76.8716},
    {"name": "I-66 @ Fair Oaks", "lat": 38.8698, "lon": -77.3564},
]
