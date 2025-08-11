
from __future__ import annotations
import os, json, time
from typing import Dict, Any, Optional

class EventStore:
    def __init__(self, log_dir: str):
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        self.events_path = os.path.join(self.log_dir, "events.ndjson")

    def emit(self, type_: str, payload: Dict[str, Any], ts: Optional[float]=None):
        evt = {"ts": ts or time.time(), "type": type_, "payload": payload}
        with open(self.events_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(evt) + "\n")
        return evt

    def read_all(self):
        if not os.path.exists(self.events_path): return []
        with open(self.events_path, "r", encoding="utf-8") as f:
            return [json.loads(x) for x in f if x.strip()]
