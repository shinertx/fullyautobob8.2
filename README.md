# v26meme — Autonomous Crypto Trading Intelligence (Institutional Edition)

Note: The project files are under the folder `v26meme_institutional_extracted/`. Change into that directory before running commands, e.g., `cd v26meme_institutional_extracted`.

**Goal:** Build a self-improving trading intelligence that discovers edges, proves them fast, allocates to the best, and compounds — fully autonomously.  
Stretch target: $200 → $1,000,000 in 30 days (aspirational). Survival and risk-adjusted compounding first.

## Features
- 4-Lab Learning Stack: SimLab (CV+stress), FieldLab (penny live probes), CounterfactualLab (what-ifs), WorldLab (stress generators).
- Strategy DSL: StrategyCards and EdgeCards (Pydantic) define every edge with entry/exit, filters, risk, capacity, telemetry.
- Allocator: Contextual bandit + fractional-Kelly sizing with correlation/theme caps and capacity curves.
- Execution: Deterministic FSM per symbol with smart routing, slippage model, fills, and circuit breakers (paper by default).
- Risk Policy-as-Code: daily & portfolio DD brakes, Core/Turbo sleeves, %ADV caps, venue allowlist.
- Dashboard: Streamlit cockpit for PnL, drawdown, allocator weights, correlation matrix, slippage TCA, and live status.
- No stubs: Everything runs end-to-end today in paper mode with synthetic or live market data (via ccxt).

## Quick Start
```bash
# 0) Go to the extracted project root
cd v26meme_institutional_extracted

# 1) Setup
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# 2) (Optional) Edit .env to add data/dirs and any API keys (live is OFF by default).

# 3) Run discovery + backtest + paper loop on synthetic data
python -m v26meme.cli bootstrap --synthetic
python -m v26meme.cli loop --minutes 30

# 4) Launch the dashboard
streamlit run dashboard/app.py
```

## Safety Defaults
- Live trading is disabled by default. Paper engine uses fills with a calibrated slippage model.
- To enable live later, set exchange keys in `.env` and toggle `--live` (after stable paper performance).

## Project Layout
```
v26meme_institutional_extracted/
  v26meme/
    core/            # DSL, policy, utils, event store, regime labels
    research/        # generators (template, miner), triage
    labs/            # SimLab, FieldLab, CounterfactualLab, WorldLab
    allocation/      # allocator and Kelly sizing
    execution/       # FSM and router
    data/            # connectors (ccxt), synthetic generator
    cli.py           # CLI entrypoint
  dashboard/
    app.py           # Streamlit cockpit
  configs/
    config.yaml
  .env.example
  requirements.txt
  README.md
```

## .env Keys
- ENV=dev
- DATA_DIR, LOG_DIR, STATE_DIR
- Optional exchange keys for live trading:
  - Kraken: KRAKEN_API_KEY, KRAKEN_SECRET
  - Coinbase: COINBASE_API_KEY, COINBASE_SECRET (passphrase not required here)
- Optional: OPENAI_API_KEY (research only)

## Disclaimer
This repository is for research/educational purposes. Crypto trading is risky. Use paper mode first; enable live trading only if you fully understand and accept the risks.
