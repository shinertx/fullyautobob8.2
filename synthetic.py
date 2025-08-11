
from __future__ import annotations
import numpy as np, pandas as pd

def synthetic_candles(n: int=1440, start: float=1.0, vol: float=0.01, seed: int=17):
    rng = np.random.default_rng(seed)
    rets = rng.normal(0, vol, n)
    price = [start]
    for r in rets:
        price.append(max(0.0001, price[-1]*(1+r)))
    price = price[1:]
    df = pd.DataFrame({"close": price})
    df["open"] = df["close"].shift(1).fillna(df["close"].iloc[0])
    df["high"] = df[["open","close"]].max(axis=1)*(1+rng.uniform(0,0.003,n))
    df["low"] = df[["open","close"]].min(axis=1)*(1-rng.uniform(0,0.003,n))
    df["volume"] = rng.uniform(1000,5000,n)
    df.index = pd.date_range("2024-01-01", periods=n, freq="T")
    return df[["open","high","low","close","volume"]]
