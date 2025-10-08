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

