import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
import pytest

from src.geospatial.features import to_projected_gdf, nearest_distance_m, count_within_radius, MILE_TO_M
from src.scoring.opportunity_score import compute_opportunity_score, DEFAULT_WEIGHTS


