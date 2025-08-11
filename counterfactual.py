
from __future__ import annotations
import pandas as pd
import numpy as np

def inverse_propensity_estimate(returns: pd.Series, propensity: pd.Series) -> float:
    p = propensity.clip(1e-3,1-1e-3)
    w = 1.0/p
    return float((returns * w).sum() / w.sum())

def doubly_robust(returns: pd.Series, propensity: pd.Series, q_model: pd.Series) -> float:
    p = propensity.clip(1e-3,1-1e-3)
    w = 1.0/p
    dr = q_model + w*(returns - q_model)
    return float(dr.mean())
