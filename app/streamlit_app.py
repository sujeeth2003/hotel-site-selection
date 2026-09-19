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

    st.markdown("## Top candidate markets")
    top20 = scored.nlargest(20, "opportunity_score")
    fig = px.bar(
        top20.sort_values("opportunity_score"), x="opportunity_score", y="label",
        orientation="h", color="cannibalization_risk_level",
        color_discrete_map=RISK_COLORS,
        labels={"opportunity_score": "Opportunity score", "label": "", "cannibalization_risk_level": "Cannibalization risk"},
        height=560,
    )
    fig.update_layout(plot_bgcolor="white", paper_bgcolor="white", margin=dict(l=0, r=10, t=10, b=10),
                       legend=dict(orientation="h", y=1.05))
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("## Demand vs. competition")
        fig2 = px.scatter(
            scored, x="competition_penalty", y="demand_score", color="opportunity_score",
            size="pop_density_per_sqmi", hover_name="label",
            color_continuous_scale=["#D8DEE4", ACCENT_LIGHT, ACCENT],
            labels={"competition_penalty": "Competition", "demand_score": "Demand", "opportunity_score": "Opportunity"},
            height=420,
        )
        fig2.update_layout(plot_bgcolor="white", paper_bgcolor="white", margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig2, use_container_width=True)
    with col2:
        st.markdown("## Opportunity vs. cannibalization risk")
        fig3 = px.scatter(
            scored, x="cannibalization_score", y="opportunity_score", color="cannibalization_risk_level",
            color_discrete_map=RISK_COLORS, hover_name="label",
            labels={"cannibalization_score": "Cannibalization risk score", "opportunity_score": "Opportunity score"},
            height=420,
        )
        fig3.update_layout(plot_bgcolor="white", paper_bgcolor="white", margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig3, use_container_width=True)

# ---------------- Market Explorer ----------------
elif page == "Market Explorer":
    st.markdown("# Market Explorer")
    st.markdown('<div class="subtitle">Every candidate site and existing hotel on the map. Color = opportunity score, size = population density.</div>', unsafe_allow_html=True)

    show_competitors = st.checkbox("Show competitor hotels", True)
    show_portfolio = st.checkbox("Show our portfolio hotels", True)
    show_candidates = st.checkbox("Show candidate sites", True)

    fig = go.Figure()
    if show_candidates:
        fig.add_trace(go.Scattermapbox(
            lat=scored["lat"], lon=scored["lon"], mode="markers",
            marker=dict(size=8, color=scored["opportunity_score"], colorscale=[[0, "#D8DEE4"], [1, ACCENT]],
                        showscale=True, colorbar=dict(title="Opportunity")),
            text=scored["label"] + "<br>Score: " + scored["opportunity_score"].astype(str),
            hoverinfo="text", name="Candidate sites",
        ))
    if show_competitors:
        comp = hotels[~hotels["is_portfolio"]]
        fig.add_trace(go.Scattermapbox(
            lat=comp["lat"], lon=comp["lon"], mode="markers",
            marker=dict(size=5, color="#B25A3E"), text=comp["name"] + " (" + comp["tier"] + ")",
            hoverinfo="text", name="Competitor hotels",
        ))
    if show_portfolio:
        port = hotels[hotels["is_portfolio"]]
        fig.add_trace(go.Scattermapbox(
            lat=port["lat"], lon=port["lon"], mode="markers",
            marker=dict(size=7, color="#4A8A6F", symbol="star"), text=port["name"],
            hoverinfo="text", name="Our portfolio",
        ))
    fig.update_layout(
        mapbox=dict(style="carto-positron", center=dict(lat=38.92, lon=-77.15), zoom=9),
        height=680, margin=dict(l=0, r=0, t=0, b=0),
        legend=dict(orientation="h", y=1.02),
    )
    st.plotly_chart(fig, use_container_width=True)

# ---------------- Site Analysis ----------------
elif page == "Site Analysis":
    st.markdown("# Site Analysis")
    site_options = scored.sort_values("opportunity_score", ascending=False)
    choice = st.selectbox("Select a candidate site", site_options["candidate_id"] + " — " + site_options["label"] +
                           " (score " + site_options["opportunity_score"].astype(str) + ")")
    cid = choice.split(" — ")[0]
    row = scored[scored["candidate_id"] == cid].iloc[0]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Opportunity score", f"{row['opportunity_score']:.0f} / 100")
    c2.metric("Demand", row["demand_label"])
    c3.metric("Competition", row["competition_label"])
    c4.metric("Cannibalization risk", row["cannibalization_risk_level"])

    col1, col2 = st.columns([1.1, 1])
    with col1:
        st.markdown("## Score breakdown")
        exp = explain_score(row, weights)
        wf = go.Figure(go.Waterfall(
            orientation="v",
            measure=["relative", "relative", "relative", "relative", "relative", "total"],
            x=["Demand", "Accessibility", "Market gap", "Competition", "Cannibalization", "Final score"],
            y=[exp["demand_contribution"], exp["accessibility_contribution"], exp["market_gap_contribution"],
               exp["competition_contribution"], exp["cannibalization_contribution"], exp["final_score"]],
            connector=dict(line=dict(color=NEUTRAL_MED)),
            decreasing=dict(marker=dict(color="#B25A3E")),
            increasing=dict(marker=dict(color=ACCENT)),
            totals=dict(marker=dict(color=NEUTRAL_DARK)),
        ))
        wf.update_layout(height=380, plot_bgcolor="white", paper_bgcolor="white", margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(wf, use_container_width=True)

    with col2:
        st.markdown("## Nearby context")
        st.write(f"**{int(row['hotels_within_3mi'])}** hotels within 3 mi · **{int(row['competitors_within_3mi'])}** competitors within 3 mi")
        st.write(f"**{row['dist_nearest_airport_mi']:.1f} mi** to nearest airport")
        st.write(f"**{row['dist_nearest_highway_mi']:.1f} mi** to nearest highway")
        st.write(f"**{row['dist_nearest_attraction_mi']:.1f} mi** to nearest attraction")
        st.write(f"**{int(row['attractions_within_3mi'])}** attractions within 3 mi")
        st.write(f"**{row['dist_nearest_portfolio_hotel_mi']:.1f} mi** to nearest of our own hotels")
        st.write(f"Population density: **{row['pop_density_per_sqmi']:,.0f}/sq mi** · Median income: **${row['median_income']:,.0f}**")
        st.write(f"Market segment: **{row['cluster_name']}**")

    st.markdown("## Recommendation")
    demand_word = row["demand_label"].lower()
    comp_word = row["competition_label"].lower()
    cannib_word = row["cannibalization_risk_level"].lower()
    st.info(
        f"{'Strong' if row['opportunity_score'] >= 70 else 'Moderate' if row['opportunity_score'] >= 45 else 'Weak'} "
        f"candidate market. Demand indicators are {demand_word} while nearby competition is {comp_word}. "
        f"Estimated cannibalization of our existing portfolio is {cannib_word}."
    )

# ---------------- Compare Markets ----------------
elif page == "Compare Markets":
    st.markdown("# Compare Markets")
    options = scored["candidate_id"] + " — " + scored["label"]
    picks = st.multiselect("Select 2-4 candidate sites to compare", options, default=list(options.head(3)))
    if len(picks) >= 2:
        ids = [p.split(" — ")[0] for p in picks]
        rows = scored[scored["candidate_id"].isin(ids)]
        display_cols = {
            "label": "Site", "opportunity_score": "Opportunity", "demand_score": "Demand",
            "accessibility_score": "Accessibility", "competition_penalty": "Competition",
            "cannibalization_score": "Cannibalization", "hotels_within_3mi": "Hotels (3mi)",
            "dist_nearest_airport_mi": "Airport dist (mi)", "cluster_name": "Segment",
        }
        table = rows[list(display_cols.keys())].rename(columns=display_cols).set_index("Site").T
        st.dataframe(table, use_container_width=True)

        fig = go.Figure()
        for _, r in rows.iterrows():
            fig.add_trace(go.Scatterpolar(
                r=[r["demand_score"], r["accessibility_score"], r["market_gap_score"],
                   100 - r["competition_penalty"], 100 - r["cannibalization_score"]],
                theta=["Demand", "Accessibility", "Market gap", "Low competition", "Low cannibalization"],
                fill="toself", name=r["label"],
            ))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), height=480,
                           margin=dict(l=40, r=40, t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.caption("Select at least two sites.")

# ---------------- Model Insights ----------------
elif page == "Model Insights":
    st.markdown("# Model Insights")
    st.markdown('<div class="subtitle">Predicting a proxy "Market Performance Index" — see limitation note below.</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1.2])
    with col1:
        st.markdown("## Model comparison")
        st.dataframe(model_results, use_container_width=True, hide_index=True)
        st.caption(f"Best model: **{meta['best_model']}**. Market segmentation: k={meta['n_clusters']} "
                   f"clusters, silhouette score {meta['silhouette']}.")
    with col2:
        st.markdown("## Feature importance")
        fig = px.bar(importances.head(10).sort_values("importance"), x="importance", y="feature", orientation="h",
                     color_discrete_sequence=[ACCENT], height=380)
        fig.update_layout(plot_bgcolor="white", paper_bgcolor="white", margin=dict(l=0, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("## Market segments")
    seg_summary = scored.groupby("cluster_name").agg(
        sites=("candidate_id", "count"), avg_opportunity=("opportunity_score", "mean"),
        avg_pop_density=("pop_density_per_sqmi", "mean"), avg_competitors=("competitors_within_3mi", "mean"),
    ).round(1).reset_index()
    st.dataframe(seg_summary, use_container_width=True, hide_index=True)

    st.warning(
        "**Limitation:** No public hotel occupancy/ADR/revenue-by-location dataset was available for this "
        "environment. The model target (Market Performance Index) is a documented synthetic proxy built from "
        "raw demand/accessibility/competition variables with injected noise — not real performance data. "
        "R² is intentionally moderate because the proxy includes noise the model cannot learn. Treat model "
        "outputs directionally, not as revenue forecasts."
    )

# ---------------- AI Analyst ----------------
elif page == "AI Analyst":
    st.markdown("# AI Market Analyst")
    st.markdown('<div class="subtitle">Ask about the candidate markets. Answers are generated by querying the '
                'underlying data with tools — never invented.</div>', unsafe_allow_html=True)
    from app.analyst_tools import answer_question

    if "chat" not in st.session_state:
        st.session_state.chat = []

    examples = ["Which market should we prioritize?", "Which markets have high demand but low competition?",
                "Top 5 markets with low cannibalization risk", "Compare the two highest-scoring markets"]
    cols = st.columns(len(examples))
    for i, ex in enumerate(examples):
        if cols[i].button(ex, use_container_width=True):
            st.session_state.chat.append(("user", ex))
            st.session_state.chat.append(("assistant", answer_question(ex, scored)))

    q = st.chat_input("Ask a question about the candidate markets...")
    if q:
        st.session_state.chat.append(("user", q))
        st.session_state.chat.append(("assistant", answer_question(q, scored)))

    for role, msg in st.session_state.chat:
        with st.chat_message(role):
            st.markdown(msg)
