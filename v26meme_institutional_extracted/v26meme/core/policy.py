
from __future__ import annotations
from typing import Dict, Any

class Policy:
    def __init__(self, cfg: Dict[str, Any]):
        self.cfg = cfg

    def can_place_order(self, ctx: Dict[str, Any]) -> (bool, str):
        # Daily/portfolio DD checks
        dd = ctx.get("portfolio_drawdown", 0.0)
        if dd >= self.cfg["risk"]["portfolio_dd_limit"]:
            return False, "Portfolio drawdown limit breached"
        daily_dd = ctx.get("daily_drawdown", 0.0)
        if daily_dd >= self.cfg["risk"]["daily_dd_limit"]:
            return False, "Daily drawdown limit breached"
        # Capacity caps
        if ctx.get("order_adv_frac", 0.0) > ctx["execution"]["adv_cap_fraction"]:
            return False, "Exceeds ADV capacity cap"
        # Circuit breakers
        slip_bps = ctx.get("est_slippage_bps", 0.0)
        if slip_bps > ctx["execution"]["circuit_slippage_bps"]:
            return False, "Slippage circuit breaker"
        fillrate = ctx.get("est_fill_rate", 1.0)
        if fillrate < ctx["execution"]["circuit_fillrate"]:
            return False, "Fill-rate circuit breaker"
        var = ctx.get("returns_variance", 0.0)
        if var > ctx["execution"]["circuit_var_ceiling"]:
            return False, "Variance circuit breaker"
        return True, "OK"
