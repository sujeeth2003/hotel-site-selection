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

st.set_page_config(page_title="Hotel Market Opportunity Engine", layout="wide", initial_sidebar_state="expanded")


# ---------- styling: strip default Streamlit chrome, restrained typography ----------
st.markdown(f"""
<style>
    #MainMenu, footer, header {{visibility: hidden;}}
    .block-container {{ padding-top: 1.6rem; padding-bottom: 2rem; max-width: 1400px; }}
    html, body, [class*="css"] {{ font-family: -apple-system, "Segoe UI", Helvetica, Arial, sans-serif; }}
    h1 {{ font-size: 1.4rem; font-weight: 600; color: {NEUTRAL_DARK}; margin-bottom: 0.1rem; letter-spacing: -0.01em;}}
    h2 {{ font-size: 1.05rem; font-weight: 600; color: {NEUTRAL_DARK}; margin-top: 1.2rem; }}
    h3 {{ font-size: 0.92rem; font-weight: 600; color: {NEUTRAL_MED}; text-transform: uppercase; letter-spacing: 0.04em; }}
    .subtitle {{ color: {NEUTRAL_MED}; font-size: 0.92rem; margin-bottom: 1.1rem; }}
    div[data-testid="stMetric"] {{ background: white; border: 1px solid #E4E6E9; border-radius: 6px; padding: 0.7rem 0.9rem; }}
    div[data-testid="stMetricValue"] {{ font-size: 1.4rem; color: {NEUTRAL_DARK}; }}
    div[data-testid="stMetricLabel"] {{ color: {NEUTRAL_MED}; font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.03em; }}
    .stTabs [data-baseweb="tab"] {{ font-size: 0.88rem; }}
    div[data-testid="stDataFrame"] {{ border: 1px solid #E4E6E9; border-radius: 6px; }}
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    scored = pd.read_parquet(DATA_DIR / "scored_candidates.parquet")
    hotels = pd.read_parquet(DATA_DIR / "hotels.parquet")
    model_results = pd.read_csv(DATA_DIR / "model_comparison.csv")
    importances = pd.read_csv(DATA_DIR / "feature_importance.csv")
    with open(DATA_DIR / "model_meta.json") as f:
        meta = json.load(f)
    return scored, hotels, model_results, importances, meta


def recompute_weights(feat_raw_cols, weights):
    from src.geospatial.features import build_site_features  # noqa
    return compute_opportunity_score(st.session_state["_base_features"], weights)


try:
    scored_default, hotels, model_results, importances, meta = load_data()
except FileNotFoundError:
    st.error("No pipeline output found. Run `python run_pipeline.py` first to generate data/processed/*.parquet.")
    st.stop()

if "_base_features" not in st.session_state:
    # keep the pre-score feature table around so weight sliders can recompute without re-running geospatial joins
    from src.scoring.opportunity_score import compute_component_scores
    st.session_state["_base_features"] = scored_default.drop(
        columns=[c for c in scored_default.columns if c.endswith(("_score", "_penalty", "_label", "_level")) or c in
                 ["opportunity_score", "cluster_id", "cluster_name"]], errors="ignore"
    )

# ---------------- Sidebar: navigation + score weight controls ----------------
st.sidebar.markdown("### Hotel Market Opportunity Engine")
st.sidebar.caption("DC · Maryland · Northern Virginia demo region")
page = st.sidebar.radio("", ["Overview", "Market Explorer", "Site Analysis", "Compare Markets", "Model Insights", "AI Analyst"],
                         label_visibility="collapsed")

st.sidebar.markdown("---")
st.sidebar.markdown("**Score weights**")
w_demand = st.sidebar.slider("Demand", 0.0, 0.6, DEFAULT_WEIGHTS["demand"], 0.05)
w_access = st.sidebar.slider("Accessibility", 0.0, 0.6, DEFAULT_WEIGHTS["accessibility"], 0.05)
w_gap = st.sidebar.slider("Market gap", 0.0, 0.6, DEFAULT_WEIGHTS["market_gap"], 0.05)
w_comp = st.sidebar.slider("Competition penalty", 0.0, 0.6, DEFAULT_WEIGHTS["competition"], 0.05)
w_cannib = st.sidebar.slider("Cannibalization penalty", 0.0, 0.6, DEFAULT_WEIGHTS["cannibalization"], 0.05)
weights = {"demand": w_demand, "accessibility": w_access, "market_gap": w_gap,
           "competition": w_comp, "cannibalization": w_cannib}

scored = compute_opportunity_score(st.session_state["_base_features"], weights)
st.sidebar.caption("Adjust and every score/rank on this page recalculates.")

# ---------------- Overview ----------------
if page == "Overview":
    st.markdown("# Hotel Market Opportunity & Site Selection Engine")
    st.markdown('<div class="subtitle">Where should we consider opening the next hotel? Demand, competition, '
                'accessibility, and portfolio cannibalization for every candidate site in the region.</div>',
                unsafe_allow_html=True)

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Candidate sites analyzed", len(scored))
    c2.metric("Existing hotels tracked", len(hotels))
    c3.metric("Top opportunity score", f"{scored['opportunity_score'].max():.0f}")
    c4.metric("Median opportunity score", f"{scored['opportunity_score'].median():.0f}")
    high_risk = (scored["cannibalization_risk_level"].isin(["High", "Very High"])).sum()
    c5.metric("High cannibalization-risk sites", high_risk)

