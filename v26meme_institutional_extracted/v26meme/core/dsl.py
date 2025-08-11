
from __future__ import annotations
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any

class StrategyCard(BaseModel):
    name: str
    theme: str                 # listings|round_number|momentum|mean_revert|correlation_filter|other
    assets: List[str]
    sessions_utc: List[str]    # e.g., ["00:00-04:00","20:00-23:59"]
    entry: Dict[str, Any]      # e.g., {"trigger":"round_number","level":1.00,"distance_bps":15}
    exit: Dict[str, Any]       # e.g., {"tp_bps":80,"sl_bps":40,"timeout_min":120}
    filters: Dict[str, Any]    # e.g., {"btc_dom_down":true, "eth_btc_up":true}
    latency_budget_ms: int
    capacity_adv: float        # max fraction of ADV
    risk_bps: int              # basis points of equity per trade
    kill_rules: Dict[str, Any] # e.g., {"max_consec_losses":3,"slippage_bps":35}
    telemetry: List[str]       # metrics to track

    @field_validator("capacity_adv")
    @classmethod
    def _cap(cls, v):
        assert 0 < v <= 0.1, "capacity_adv must be (0,0.1]"
        return v

class EdgeCard(BaseModel):
    strategy: StrategyCard
    params: Dict[str, Any]
    performance: Dict[str, Any] = Field(default_factory=dict)
    regimes: Dict[str, Any] = Field(default_factory=dict)
    capacity_curve: Dict[str, Any] = Field(default_factory=dict)
    decay_triggers: Dict[str, Any] = Field(default_factory=dict)
    lineage: List[Dict[str, Any]] = Field(default_factory=list)
