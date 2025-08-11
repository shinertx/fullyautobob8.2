
from __future__ import annotations
import random

class Router:
    def __init__(self, field_priors: dict):
        self.priors = field_priors

    def quote(self, mid_price: float, side: str="buy"):
        # Simple model: slippage_bps around priors and fill probability from priors
        slip_bps = max(1.0, random.gauss(self.priors.get("slippage_bps",15.0), 2.0))
        fill_prob = max(0.1, min(0.95, random.gauss(self.priors.get("fill_rate",0.7), 0.05)))
        px = mid_price * (1 + (slip_bps/10000.0 if side=="buy" else -slip_bps/10000.0))
        return px, fill_prob, slip_bps
