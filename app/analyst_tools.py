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


def rank_markets(df: pd.DataFrame, n: int = 5, ascending: bool = False) -> pd.DataFrame:
    return df.nlargest(n, "opportunity_score") if not ascending else df.nsmallest(n, "opportunity_score")


def low_cannibalization_top(df: pd.DataFrame, n: int = 5) -> pd.DataFrame:
    return df[df["cannibalization_risk_level"].isin(["Low", "Moderate"])].nlargest(n, "opportunity_score")


def high_demand_low_competition(df: pd.DataFrame, n: int = 5) -> pd.DataFrame:
    sub = df[(df["demand_label"] == "High") & (df["competition_label"].isin(["Low", "Moderate"]))]
    return sub.nlargest(n, "opportunity_score")


def compare_markets(df: pd.DataFrame, label_a: str, label_b: str) -> tuple[pd.Series, pd.Series]:
    a = df[df["label"].str.contains(label_a, case=False, na=False)].iloc[0]
    b = df[df["label"].str.contains(label_b, case=False, na=False)].iloc[0]
    return a, b


# ---------------- Fallback deterministic router (no external LLM needed) ----------------

def _fmt_row(r) -> str:
    return (f"**{r['label']}** — Opportunity {r['opportunity_score']:.0f}, demand {r['demand_label'].lower()}, "
            f"competition {r['competition_label'].lower()}, cannibalization {r['cannibalization_risk_level'].lower()}")


def answer_question(question: str, df: pd.DataFrame) -> str:
    if os.environ.get("ANTHROPIC_API_KEY"):
        try:
            return route_with_claude(question, df)
        except Exception:
            pass  # fall through to deterministic router

    q = question.lower()

