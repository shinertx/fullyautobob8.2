
from __future__ import annotations
import random
from typing import List, Dict, Any
from v26meme.core.dsl import StrategyCard

THEMES = ["listings","round_number","momentum","mean_revert","correlation_filter"]

def _rand_sessions():
    sessions = [("00:00","04:00"),("12:00","16:00"),("20:00","23:59")]
    k = random.randint(1,2)
    return [f"{a}-{b}" for a,b in random.sample(sessions, k)]

def template_generator(symbols: List[str]) -> List[StrategyCard]:
    out = []
    for _ in range(random.randint(10,25)):
        theme = random.choice(THEMES)
        sym = random.sample(symbols, k=min(len(symbols), random.randint(1,3)))
        if theme == "round_number":
            entry = {"trigger":"round_number","level":1.0,"distance_bps":random.choice([10,15,20,25,30])}
            exit = {"tp_bps": random.choice([60,80,100]), "sl_bps": random.choice([30,40,50]), "timeout_min": random.choice([30,60,120])}
        elif theme == "listings":
            entry = {"trigger":"listing_window","minutes_after":[20,30,45,60]}
            exit = {"tp_bps": 120, "sl_bps": 60, "timeout_min": 180}
        elif theme == "momentum":
            entry = {"trigger":"momentum","lookback": random.choice([5,10,20]), "z": random.choice([0.5,1.0,1.5])}
            exit = {"tp_bps": 80, "sl_bps": 50, "timeout_min": 90}
        elif theme == "mean_revert":
            entry = {"trigger":"rsi_div","period":14,"z":-1.0}
            exit = {"tp_bps": 60, "sl_bps": 40, "timeout_min": 120}
        else:
            entry = {"trigger":"corr_filter","btc_dom_down":True,"eth_btc_up":True}
            exit = {"tp_bps": 70, "sl_bps": 45, "timeout_min": 120}
        card = StrategyCard(
            name=f"{theme}_{random.randint(1000,9999)}",
            theme=theme,
            assets=sym,
            sessions_utc=_rand_sessions(),
            entry=entry,
            exit=exit,
            filters={"btc_dom_down": random.choice([True, False]), "eth_btc_up": random.choice([True, False])},
            latency_budget_ms=random.choice([250,500,750,1000]),
            capacity_adv=0.02,
            risk_bps=random.choice([25,50,75,100]),
            kill_rules={"max_consec_losses":3, "slippage_bps":35},
            telemetry=["hit_rate","expectancy","sortino","mdd","slippage","fill_rate"]
        )
        out.append(card)
    return out
