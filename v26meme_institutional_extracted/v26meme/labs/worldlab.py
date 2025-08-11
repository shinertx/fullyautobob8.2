
from __future__ import annotations
import numpy as np, pandas as pd

def stress_pack(df: pd.DataFrame, kind: str="flash_crash", severity: float=0.1) -> pd.DataFrame:
    out = df.copy()
    n = len(out)
    if kind == "flash_crash":
        idx = int(n*0.7)
        out.loc[out.index[idx:idx+5], "close"] *= (1-severity)
    elif kind == "spread_blowout":
        # emulate by widening high-low range
        out["high"] *= (1+severity*0.5); out["low"] *= (1-severity*0.5)
    elif kind == "low_liquidity":
        out["volume"] *= (1-severity)
    return out
