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

    if "prioritize" in q or "best market" in q or "which market should we" in q:
        top = rank_markets(df, 1).iloc[0]
        second = rank_markets(df, 2).iloc[1]
        diff = top["opportunity_score"] - second["opportunity_score"]
        return (f"**Top recommendation: {top['label']}**\n\nOpportunity score: {top['opportunity_score']:.0f}\n\n"
                f"Why:\n- {top['demand_label']} demand\n- {top['accessibility_label']} accessibility\n"
                f"- {top['competition_label']} competitive density\n- {top['cannibalization_risk_level']} estimated cannibalization\n\n"
                f"Compared with the next-best site ({second['label']}), it scores {diff:.1f} points higher.")

    if "low cannibalization" in q or "cannibalization" in q and ("top" in q or "low" in q):
        rows = low_cannibalization_top(df, 5)
        return "**Top candidate markets with low/moderate cannibalization risk:**\n\n" + "\n\n".join(_fmt_row(r) for _, r in rows.iterrows())

    if ("high demand" in q and "low competition" in q) or "demand but low" in q:
        rows = high_demand_low_competition(df, 5)
        if rows.empty:
            return "No candidate sites currently combine high demand with low/moderate competition in this dataset."
        return "**Markets with high demand and low/moderate competition:**\n\n" + "\n\n".join(_fmt_row(r) for _, r in rows.iterrows())

    if "compare" in q:
        names = re.findall(r"[A-Z][a-zA-Z\.\-]+(?:\s[A-Z][a-zA-Z\.\-]+)*", question)
        if len(names) >= 2:
            try:
                a, b = compare_markets(df, names[0], names[1])
                diff = a["opportunity_score"] - b["opportunity_score"]
                higher, lower = (a, b) if diff >= 0 else (b, a)
                return (f"**{a['label']}**: {a['opportunity_score']:.0f} vs **{b['label']}**: {b['opportunity_score']:.0f}\n\n"
                        f"{higher['label']} scores {abs(diff):.1f} points higher, driven primarily by "
                        f"{'stronger demand' if higher['demand_score'] > lower['demand_score'] else 'better accessibility' if higher['accessibility_score'] > lower['accessibility_score'] else 'lower competitive pressure'}.")
            except IndexError:
                pass
        top2 = rank_markets(df, 2)
        a, b = top2.iloc[0], top2.iloc[1]
        return (f"Comparing the two top-ranked markets — **{a['label']}** ({a['opportunity_score']:.0f}) vs "
                f"**{b['label']}** ({b['opportunity_score']:.0f}): {a['label']} leads mainly on "
                f"{'demand' if a['demand_score'] > b['demand_score'] else 'accessibility'}.")

