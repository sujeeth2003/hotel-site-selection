"""
Generates a population/income/business-activity grid for the region.

LIMITATION: Census API is unreachable from this sandbox. Real deployment
pulls ACS block-group population + median income via the Census API
(see docs/data_sources.md). This module builds a plausible demand surface by
combining distance-decay from real business districts (higher density/income
near urban cores, decaying outward) with regional noise, calibrated to
roughly match known DC-metro population density magnitudes (order of
magnitude ~5,000-11,000/sq mi in the urban core, ~1,000-3,000 suburban).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

