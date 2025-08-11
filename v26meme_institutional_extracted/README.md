Short, honest answer:

* You’ve got a **fully runnable, end‑to‑end system in paper mode** (discovery → SimLab → allocate → execute → dashboard). There are **no dead stubs**—every module you see is active.
* But “number‑one‑in‑the‑world institutional” is a higher bar than any single drop can meet. To hit that bar you’d add hardened ops (CI/CD, alerting, chaos tests), deeper market microstructure, richer data coverage, and live‑trading guards. I can map those out when you’re ready.

If you want an even clearer repo story, here’s an **upgraded README.md** you can paste over the existing one—more thorough, more “institutional,” with precise steps, guardrails, and common pitfalls.

# README.md (improved)

````markdown
# v26meme — Autonomous Crypto Trading Intelligence (Institutional-Style, Paper by Default)

**Mission**  
A self‑improving trading intelligence that **discovers**, **proves**, **allocates**, and **executes** edges with zero babysitting.  
Stretch target: **$200 → $1,000,000 in 30 days** (aspirational). First principles: **risk-adjusted compounding**, **safety**, **autonomy**.

---

## What this repo delivers today

- ✅ **End‑to‑end autonomy (paper mode):** idea generation → SimLab CV+stress → bandit+Kelly allocation → deterministic execution FSM → event log → **Streamlit dashboard**.
- ✅ **4‑Lab learning hooks:** SimLab (implemented), FieldLab slippage/fill **priors** (live‑style updates), Counterfactual estimators (IPS/DR), WorldLab stress (flash‑crash/low‑liq/spread blowout).
- ✅ **Policy‑as‑code risk:** daily & portfolio DD brakes, capacity/ADV caps, microstructure circuit breakers.
- ✅ **Strategy DSL:** StrategyCard/EdgeCard schemas (Pydantic) so edges are structured and auditable.
- ✅ **No stubs in the hot path:** everything you run is doing real work on synthetic candles; live connectors are included for future use.

⚠️ **Not yet:** colocated/HFT, real‑money execution, external alerting/on‑call, multi‑venue live OMS, or proprietary data feeds. Paper mode is the safe default.

---

## Quick start (VS Code or terminal)

```bash
# 1) Python env
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2) Environment
cp .env.example .env   # paper mode works with blanks
# (Optional) edit .env paths if you want custom data/log/state dirs

# 3) Bootstrap and run a paper loop
python -m v26meme.cli bootstrap --synthetic
python -m v26meme.cli loop --minutes 30

# 4) Dashboard (new terminal)
streamlit run dashboard/app.py
````

Open the dashboard and watch: SimLab stats → allocator weights → trade decisions.
All events stream to `logs/events.ndjson`.

---

## What the bot actually does

1. **Generates strategy candidates** (ontology templates: listings, round‑numbers, momentum, mean‑revert, correlation filters).
2. **Ranks** by an EV‑per‑cost triage score (keeps exploration smart).
3. **Cross‑validates** each top idea with fees/slippage/latency + stress; only **CI>0, Sortino>1, MDD<20%** survive.
4. **Allocates** with a bandit + fractional‑Kelly and theme/capacity caps.
5. **Executes** in paper via a **deterministic FSM** with a router fed by FieldLab slippage/fill **priors**.
6. **Logs everything** to an event store; the dashboard visualizes health and decisions.

---

## Config & environment

* **Main config:** `configs/config.yaml`

  * Paper fees/slippage/latency, starting equity, symbols, sleeves, DD limits, circuit breakers.
* **.env keys:** (paper needs none)

  * `ENV`, `DATA_DIR`, `LOG_DIR`, `STATE_DIR`
  * Optional exchange keys (for future live): `BINANCE_*`, `COINBASE_*`
  * Optional `OPENAI_API_KEY` (LLMs never in hot path)

---

## Project layout

```
v26meme/
  core/         # Strategy/Edge DSL, policy, event store, utils, regime tags
  research/     # generators + triage (EV-per-cost)
  labs/         # SimLab, FieldLab priors, Counterfactual (IPS/DR), WorldLab stress
  allocation/   # bandit allocator + fractional Kelly
  execution/    # FSM + router (slippage/fill model)
  data/         # synthetic candles, ccxt live fetch
  cli.py        # bootstrap + loop entrypoints
dashboard/
  app.py        # Streamlit cockpit (metrics/weights/trades)
configs/
  config.yaml
```

---

## Operating principles (baked in)

* **LLM-light, policy-heavy:** no LLMs in execution/risk; deterministic FSMs and rules run the book.
* **Learn reality fast:** FieldLab updates slippage/fill priors; SimLab pulls them each loop.
* **Never brute-force:** triage gates ideas; early-stop losers; champion‑challenger rotation is supported.
* **Risk is a throttle, not a cap:** fractional‑Kelly, Core/Turbo sleeves, DD brakes, circuit breakers.

---

## Common issues

* **Nothing shows on dashboard yet:** run the loop first; events stream to `logs/events.ndjson`.
* **No trades:** SimLab filters aggressively. Increase runtime (`--minutes`), or relax thresholds in `configs/config.yaml`.
* **Pip issues on macOS/Windows:** ensure Python 3.10+, then `pip install -r requirements.txt` inside the venv.
* **Live data:** `data/ccxt_conn.py` is ready, but this repo defaults to synthetic for safety.

---

## Roadmap to “institutional #1” (beyond this repo)

* CI/CD (pytest + smoke backtests + golden SimLab stats), pre‑commit hooks, typed API checks.
* External alerting (Slack/Discord/Webhooks), SLO monitors, chaos drills (API freezes/data gaps).
* Multi‑venue paper OMS with order book replay + queue‑position model; reconciliation & TCA store.
* Advanced discovery: matrix profile motif mining; causal/lead‑lag graphing at scale.
* Live trading toggles with hard brakes; reserve accounting; venue health scoring; richer knowledge graph.

---

#