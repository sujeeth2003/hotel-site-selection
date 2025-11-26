"""
Modeling module.

IMPORTANT / HONESTY NOTE (see docs/methodology.md and README limitations):
No public dataset of actual hotel occupancy/ADR/revenue by exact coordinate
exists for free ingestion in this environment. Rather than fabricate that or
skip modeling entirely, we construct a documented, clearly-labeled proxy
target — a "Market Performance Index" (MPI) built from a DIFFERENT weighting
formula over raw observed variables than the Opportunity Score uses, plus
injected noise, to avoid circularity (the model must actually learn
generalizable relationships, not just re-derive the scoring formula). This is
explicitly a proxy, not real performance data, and is labeled as such
everywhere it's displayed.

