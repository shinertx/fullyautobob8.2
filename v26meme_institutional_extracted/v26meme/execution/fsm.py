
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class OrderState:
    state: str = "idle"   # idle|enter|manage|exit|settle
    entry_px: Optional[float] = None
    qty: float = 0.0
    ts_open: Optional[int] = None

class ExecutionFSM:
    def __init__(self, policy, router):
        self.policy = policy
        self.router = router

    def step(self, ctx: Dict[str,Any]) -> Dict[str,Any]:
        # ctx includes: price, signal, equity, policy context, etc.
        can, reason = self.policy.can_place_order(ctx)
        if not can:
            return {"action":"hold","reason":reason}
        signal = ctx.get("signal",0)
        state = ctx.setdefault("order_state", OrderState())
        price = ctx["price"]
        if state.state == "idle" and signal == 1:
            # Enter
            px, fill_prob, slip_bps = self.router.quote(price, side="buy")
            if fill_prob < ctx["execution"]["min_fill_prob"]:
                return {"action":"hold","reason":"fill_prob_low"}
            state.state = "enter"; state.entry_px = px; state.qty = ctx.get("qty",0.0)
            return {"action":"enter","price":px,"qty":state.qty}
        elif state.state in ("enter","manage"):
            # Check exits
            tp_bps = ctx["card"]["exit"].get("tp_bps",80)/10000.0
            sl_bps = ctx["card"]["exit"].get("sl_bps",40)/10000.0
            ret = (price - (state.entry_px or price))/(state.entry_px or price)
            if ret >= tp_bps or ret <= -sl_bps:
                px, fill_prob, slip_bps = self.router.quote(price, side="sell")
                state.state = "exit"
                return {"action":"exit","price":px,"qty":state.qty}
            else:
                state.state = "manage"
                return {"action":"manage"}
        elif state.state == "exit":
            state.state = "settle"
            return {"action":"settle"}
        else:
            return {"action":"hold"}
