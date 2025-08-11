
from __future__ import annotations
import os, json, time, math, random
from typing import Dict, Any, Tuple
import numpy as np
import pandas as pd

def ensure_dirs(*paths):
    for p in paths:
        os.makedirs(p, exist_ok=True)

def ts():
    return time.time()

def rolling_max_drawdown(equity_curve: pd.Series) -> float:
    roll_max = equity_curve.cummax()
    dd = (equity_curve - roll_max) / roll_max
    return dd.min() if len(dd) else 0.0

def sortino_ratio(returns: pd.Series, rf: float=0.0) -> float:
    if returns.empty: return 0.0
    downside = returns[returns < rf]
    dd = downside.std(ddof=1)
    if dd == 0: return 0.0
    return (returns.mean() - rf) / dd

def bootstrap_expectancy_ci(returns: pd.Series, n_boot: int=1000, alpha: float=0.05) -> Tuple[float,float,float]:
    if returns.empty:
        return 0.0, 0.0, 0.0
    means = []
    for _ in range(n_boot):
        s = returns.sample(frac=1.0, replace=True)
        means.append(s.mean())
    lo = np.percentile(means, 100*alpha/2)
    hi = np.percentile(means, 100*(1-alpha/2))
    return returns.mean(), lo, hi
