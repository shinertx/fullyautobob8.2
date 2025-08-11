
from __future__ import annotations
import pandas as pd
import numpy as np

def label_regime(df: pd.DataFrame) -> pd.Series:
    # Simple regime labels: trend/chop/vol
    r = df['close'].pct_change().fillna(0)
    vol = r.rolling(30).std().fillna(r.std())
    trend = df['close'].rolling(30).apply(lambda s: np.polyfit(range(len(s)), s.values, 1)[0], raw=False)
    trend = trend.fillna(0)
    label = []
    for t,v in zip(trend, vol):
        if v > vol.quantile(0.8):
            label.append("high_vol")
        elif t > 0:
            label.append("trend_up")
        elif t < 0:
            label.append("trend_down")
        else:
            label.append("chop")
    return pd.Series(label, index=df.index, name="regime")
