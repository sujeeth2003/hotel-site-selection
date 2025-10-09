"""
Hotel Market Opportunity & Site Selection Engine — Streamlit application.

Design approach: internal analytics tool for a strategy/DS team. Restrained
palette (one accent color + neutrals), compact information density, the map
and comparison table carry the weight — not cards/gradients/decoration.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import json

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.scoring.opportunity_score import compute_opportunity_score, explain_score, DEFAULT_WEIGHTS

DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "processed"

ACCENT = "#2C5F8A"       # single restrained accent (deep steel blue)
ACCENT_LIGHT = "#7FA8C9"
NEUTRAL_DARK = "#1F2328"
NEUTRAL_MED = "#5B6470"
NEUTRAL_BG = "#F5F6F7"
RISK_COLORS = {"Low": "#4A8A6F", "Moderate": "#C7973A", "High": "#B25A3E", "Very High": "#8C3B34"}

