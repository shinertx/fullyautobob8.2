
from __future__ import annotations
import numpy as np, pandas as pd, math, random
from typing import Dict, Any, List, Tuple
from v26meme.core.utils import sortino_ratio, bootstrap_expectancy_ci

def generate_synthetic_ohlc(n: int=1440, start: float=1.0, vol: float=0.01, seed: int=42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rets = rng.normal(0, vol, n)
    price = [start]
    for r in rets:
        price.append(max(0.0001, price[-1]*(1+r)))
    price = price[1:]
    df = pd.DataFrame({"close": price})
    df["open"] = df["close"].shift(1).fillna(df["close"].iloc[0])
    df["high"] = df[["open","close"]].max(axis=1)*(1+rng.uniform(0,0.002,n))
    df["low"] = df[["open","close"]].min(axis=1)*(1-rng.uniform(0,0.002,n))
    df["volume"] = rng.uniform(1000,5000,n)
    df.index = pd.date_range("2024-01-01", periods=n, freq="T")
    return df[["open","high","low","close","volume"]]

def apply_strategy_on_df(df: pd.DataFrame, card: Dict[str,Any], fees_bps: float=10, slip_bps: float=15) -> pd.DataFrame:
    # Very light implementations for triggers
    out = df.copy()
    out["signal"] = 0
    trig = card["entry"]["trigger"]
    if trig == "round_number":
        level = card["entry"].get("level",1.0)
        dist = card["entry"].get("distance_bps", 20)/10000.0
        rn = (out["close"] % level)/level
        out.loc[(rn < dist) | (rn > 1-dist), "signal"] = 1
    elif trig == "momentum":
        lb = card["entry"].get("lookback",10)
        z = card["entry"].get("z",1.0)
        ret = out["close"].pct_change(lb)
        out.loc[ret > (ret.rolling(200).std().fillna(ret.std())*z), "signal"] = 1
    elif trig == "rsi_div":
        # Simplified mean-revert: buy when return < -z*std over lookback
        z = abs(card["entry"].get("z",-1.0))
        lb = 14
        ret = out["close"].pct_change(lb)
        out.loc[ret < -(ret.rolling(200).std().fillna(ret.std())*z), "signal"] = 1
    else:
        out["signal"] = 0

    # Trade simulation
    tp = card["exit"].get("tp_bps",80)/10000.0
    sl = card["exit"].get("sl_bps",40)/10000.0
    timeout = int(card["exit"].get("timeout_min",120))
    fees = fees_bps/10000.0
    slip = slip_bps/10000.0

    pnl = []
    holding = 0
    entry_px = None
    entry_t = None

    for i in range(len(out)):
        if holding == 0 and out["signal"].iloc[i] == 1:
            holding = 1
            entry_px = out["close"].iloc[i]*(1+slip)  # pay slippage
            entry_t = i
            continue
        if holding == 1:
            px = out["close"].iloc[i]
            ret = (px - entry_px)/entry_px
            # check TP/SL/timeout
            if ret >= tp or ret <= -sl or (i-entry_t) >= timeout:
                gross = ret
                net = gross - (2*fees) - slip  # entry slippage counted; assume some exit slippage in fees
                pnl.append(net)
                holding = 0
                entry_px = None
                entry_t = None
    pnl_s = pd.Series(pnl) if pnl else pd.Series(dtype=float)
    stats = {
        "n_trades": int((out["signal"]==1).sum()),
        "mean": float(pnl_s.mean() if len(pnl_s) else 0.0),
        "sortino": float(sortino_ratio(pnl_s.fillna(0)) if len(pnl_s) else 0.0),
        "mdd": float(abs(min((pnl_s.cumsum()+1).cummax() - (pnl_s.cumsum()+1)).min()) if len(pnl_s) else 0.0),
    }
    mean, lo, hi = bootstrap_expectancy_ci(pnl_s.fillna(0)) if len(pnl_s) else (0.0,0.0,0.0)
    stats.update({"exp": float(mean), "ci_lo": float(lo), "ci_hi": float(hi)})
    out.attrs["stats"] = stats
    return out

def cross_validate(card: Dict[str,Any], n_splits: int=3, fees_bps: float=10, slip_bps: float=15, seed: int=42) -> Dict[str,Any]:
    # Purged/embargoed split approximation
    rng = np.random.default_rng(seed)
    all_stats = []
    for k in range(n_splits):
        df = generate_synthetic_ohlc(n=1440, start=1.0, vol=0.01*(1+0.1*k), seed=seed+k)
        res = apply_strategy_on_df(df, card, fees_bps=fees_bps, slip_bps=slip_bps)
        all_stats.append(res.attrs["stats"])
    # Aggregate
    exp = np.mean([s["exp"] for s in all_stats])
    sortino = np.mean([s["sortino"] for s in all_stats])
    mdd = np.max([s["mdd"] for s in all_stats])
    ci_lo = np.mean([s["ci_lo"] for s in all_stats])
    ci_hi = np.mean([s["ci_hi"] for s in all_stats])
    return {"exp":float(exp),"sortino":float(sortino),"mdd":float(mdd),"ci_lo":float(ci_lo),"ci_hi":float(ci_hi),"folds":all_stats}
