
from __future__ import annotations
import math, random
from typing import Dict, Any, List

class BanditAllocator:
    def __init__(self, kelly_min: float, kelly_max: float, exploration: float, theme_caps: Dict[str,float]):
        self.kelly_min = kelly_min
        self.kelly_max = kelly_max
        self.exploration = exploration
        self.theme_caps = theme_caps
        self.score = {}   # edge_name -> running score
        self.theme_usage = {}  # theme -> usage fraction

    def update_score(self, edge_name: str, reward: float):
        self.score[edge_name] = 0.9*self.score.get(edge_name,0.0) + 0.1*reward

    def weight(self, edges: List[Dict[str,Any]], corr_penalty: float=0.2) -> Dict[str,float]:
        # Simple proportional weights by score with exploration
        names = [e["name"] for e in edges]
        raw = [max(1e-6, self.score.get(n, 0.01)) for n in names]
        total = sum(raw)
        w = [r/total for r in raw]
        # Apply theme caps (normalize within cap)
        themed = {}
        for e, wi in zip(edges, w):
            cap = self.theme_caps.get(e.get("theme","other"), 1.0)
            themed[e["name"]] = min(wi, cap)
        s = sum(themed.values())
        return {k: v/s for k,v in themed.items()} if s>0 else {n:1/len(names) for n in names}

def fractional_kelly(p: float, b: float=1.0, frac: float=0.5) -> float:
    # Kelly: f* = (bp - (1-p))/b ; clamp to [0,1]
    fk = ((b*p) - (1-p))/max(b,1e-6)
    return max(0.0, min(1.0, fk*frac))
