"""
Site Opportunity Score: a transparent, configurable weighted scoring system.

Opportunity Score = Demand + Accessibility + Market Gap - Competition - Cannibalization

Each component is normalized to 0-100 using percentile rank within the
current candidate set (robust to outliers, unlike min-max scaling). Weights
are configurable and every component contribution is retained on the output
so the score is explainable (see explain_score()).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

