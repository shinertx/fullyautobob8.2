
from __future__ import annotations
from typing import Dict, Any
import math, random

def ev_per_cost_score(prior: float, net_edge: float, capacity: float, orthogonality: float, data_ready: float, risk: float, compute_cost: float) -> float:
    # All inputs in [0,1] roughly; guard against zeros
    risk = max(risk, 1e-6)
    compute_cost = max(compute_cost, 1e-6)
    return (prior * net_edge * capacity * orthogonality * data_ready) / (risk * compute_cost)

def mock_rank(card) -> float:
    # Heuristic mock ranking until real priors exist
    # Listing/round-number momentum edges slightly favored; punish long latency budget and high risk_bps
    theme_bias = {"listings": 1.2, "round_number": 1.15, "momentum": 1.05, "mean_revert": 1.0, "correlation_filter": 1.0}
    prior = theme_bias.get(card.theme,1.0)
    net_edge = 0.6
    capacity = min(1.0, 50*card.capacity_adv)
    orth = 0.7
    data_ready = 0.8
    risk = min(1.0, card.risk_bps/100.0 + 0.2)
    compute_cost = 0.5 + (card.latency_budget_ms/2000.0)
    return ev_per_cost_score(prior, net_edge, capacity, orth, data_ready, risk, compute_cost)
