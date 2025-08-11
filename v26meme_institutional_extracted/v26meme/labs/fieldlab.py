
from __future__ import annotations
import os, json, random
from typing import Dict, Any, List
import pandas as pd
import numpy as np

class FieldLab:
    """Learn real-world costs by placing tiny paper 'probes'. Updates slippage priors."""
    def __init__(self, state_dir: str):
        self.state_dir = state_dir
        os.makedirs(self.state_dir, exist_ok=True)
        self.priors_path = os.path.join(self.state_dir, "slippage_priors.json")
        if not os.path.exists(self.priors_path):
            with open(self.priors_path,"w") as f: json.dump({"slippage_bps": 15.0, "fill_rate": 0.7}, f)

    def get_priors(self) -> Dict[str,Any]:
        with open(self.priors_path,"r") as f:
            return json.load(f)

    def update(self, observed_slippage_bps: float, observed_fill_rate: float):
        pri = self.get_priors()
        # EWMA update
        pri["slippage_bps"] = 0.8*pri["slippage_bps"] + 0.2*observed_slippage_bps
        pri["fill_rate"] = 0.8*pri["fill_rate"] + 0.2*observed_fill_rate
        with open(self.priors_path,"w") as f: json.dump(pri,f)
        return pri
