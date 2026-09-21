"""Generates candidate hotel site locations as a filtered grid across the region."""
from __future__ import annotations

import numpy as np
import pandas as pd

from src.ingestion.reference_pois import BUSINESS_DISTRICTS

REGION_BOUNDS = {"lat_min": 38.76, "lat_max": 39.05, "lon_min": -77.50, "lon_max": -76.90}


