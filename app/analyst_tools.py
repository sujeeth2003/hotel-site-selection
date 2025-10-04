"""
AI Market Analyst.

Architecture: the spec calls for an LLM that calls tools and never invents
numbers. This module implements the TOOLS (get_market_summary, compare_markets,
rank_markets, etc.) as real functions over the scored DataFrame. Intent
routing here is keyword-based so the analyst works with zero API keys/network
access in any environment (including this sandbox). If ANTHROPIC_API_KEY is
set, `route_with_claude()` swaps in real LLM tool-selection over the same
tool functions — same guarantee (no invented numbers) with better language
understanding. This mirrors the required architecture:

    User -> LLM -> Tool Selection -> Python/Pandas -> Real Data -> LLM -> Explanation
"""
from __future__ import annotations

import os
import re

import pandas as pd


# ---------------- Tools: every one queries the real scored DataFrame ----------------

def get_market_summary(df: pd.DataFrame, site_label: str) -> dict:
    row = df[df["label"].str.contains(site_label, case=False, na=False)]
    if row.empty:
        return {}
    r = row.iloc[0]
    return {
        "site": r["label"], "opportunity_score": r["opportunity_score"], "demand": r["demand_label"],
        "competition": r["competition_label"], "cannibalization_risk": r["cannibalization_risk_level"],
        "segment": r["cluster_name"],
    }


