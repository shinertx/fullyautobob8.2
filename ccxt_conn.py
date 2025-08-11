
from __future__ import annotations
import ccxt
import pandas as pd
from typing import List

def fetch_ohlcv(symbol: str, timeframe: str="1m", limit: int=500, exchange_id: str="binance"):
    ex = getattr(ccxt, exchange_id)()
    ohlcv = ex.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(ohlcv, columns=["ts","open","high","low","close","volume"])
    df["ts"] = pd.to_datetime(df["ts"], unit="ms", utc=True)
    df = df.set_index("ts")
    return df
