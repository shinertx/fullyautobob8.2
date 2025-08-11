
from __future__ import annotations
import os, json, time, random, math
import click
import yaml
import pandas as pd
from v26meme.core.utils import ensure_dirs, ts
from v26meme.core.dsl import StrategyCard, EdgeCard
from v26meme.core.policy import Policy
from v26meme.core.event_store import EventStore
from v26meme.research.generator import template_generator
from v26meme.research.triage import mock_rank
from v26meme.labs.simlab import cross_validate
from v26meme.labs.fieldlab import FieldLab
from v26meme.execution.router import Router
from v26meme.execution.fsm import ExecutionFSM, OrderState
from v26meme.allocation.allocator import BanditAllocator, fractional_kelly
from v26meme.data.synthetic import synthetic_candles

@click.group()
def cli():
    pass

def load_cfg():
    with open("configs/config.yaml","r") as f: 
        return yaml.safe_load(f)

@cli.command()
@click.option("--synthetic", is_flag=True, help="Use synthetic data to bootstrap.")
def bootstrap(synthetic: bool):
    cfg = load_cfg()
    ensure_dirs(cfg["data_dir"], cfg["log_dir"], cfg["state_dir"])
    es = EventStore(cfg["log_dir"])
    es.emit("system.bootstrap", {"synthetic":synthetic})
    click.echo("✅ Bootstrapped directories and event store.")

@cli.command()
@click.option("--minutes", default=10, help="Run for N minutes in paper loop.")
def loop(minutes: int):
    """Main paper-trading loop: discovery -> triage -> sim -> allocation -> execution."""
    cfg = load_cfg()
    ensure_dirs(cfg["data_dir"], cfg["log_dir"], cfg["state_dir"])
    es = EventStore(cfg["log_dir"])
    policy = Policy(cfg)
    field = FieldLab(cfg["state_dir"])
    router = Router(field.get_priors())
    allocator = BanditAllocator(cfg["allocator"]["kelly_fraction_min"], cfg["allocator"]["kelly_fraction_max"], cfg["allocator"]["exploration"], cfg["allocator"]["theme_caps"])

    symbols = cfg["paper"]["symbols"]
    universe = {s: synthetic_candles(n=1000, start=100.0, vol=0.003, seed=17+ix) for ix, s in enumerate(symbols)}

    end_time = time.time() + 60*minutes
    equity = cfg["paper"]["starting_equity"]
    reserve = equity * cfg["risk"]["reserve_fraction_min"]
    live = {}

    while time.time() < end_time:
        # 1) Discover
        cards = template_generator(symbols)
        # 2) Triage top-K
        cards_ranked = sorted(cards, key=lambda c: mock_rank(c), reverse=True)[:5]

        promoted = []
        for c in cards_ranked:
            stats = cross_validate(c.model_dump(), fees_bps=cfg["paper"]["fees_bps"], slip_bps=int(field.get_priors()["slippage_bps"]))
            es.emit("simlab.result", {"name": c.name, "stats": stats})
            if stats["exp"] > 0 and stats["sortino"] > 1 and stats["mdd"] < 0.2 and stats["ci_lo"] > 0:
                promoted.append(c)

        # 3) Allocate
        edges = [{"name": c.name, "theme": c.theme} for c in promoted] or [{"name":"cash","theme":"other"}]
        weights = allocator.weight(edges)
        es.emit("allocator.weights", {"weights": weights})

        # 4) Execute (paper) per symbol for each promoted card
        for c in promoted:
            w = weights.get(c.name, 0.0)
            if w <= 0: continue
            # Target quantity based on Kelly approx (use exp as win prob proxy)
            p_win = 0.55
            size_frac = fractional_kelly(p_win, b=1.0, frac=0.5)
            size_frac *= w * cfg["sleeves"]["core_weight"]
            notional = equity * size_frac
            qty = max(0.0, notional / universe[symbols[0]]["close"].iloc[-1])  # naive qty vs first symbol price

            # Simple one-step FSM demonstration on the first symbol
            price = float(universe[symbols[0]]["close"].iloc[-1])
            ctx = {
                "portfolio_drawdown": 0.0,
                "daily_drawdown": 0.0,
                "order_adv_frac": 0.01,
                "execution": cfg["execution"],
                "est_slippage_bps": field.get_priors()["slippage_bps"],
                "est_fill_rate": field.get_priors()["fill_rate"],
                "returns_variance": 0.01,
                "signal": 1,  # fire once
                "price": price,
                "qty": qty,
                "card": c.model_dump()
            }
            fsm = ExecutionFSM(policy, router)
            act = fsm.step(ctx)
            es.emit("trade.signal", {"card": c.name, "action": act})

            if act.get("action") == "enter":
                # Mock exit instantly for demo; update equity by net PnL random
                pnl = random.uniform(-0.004, 0.01)  # -40 bps .. +100 bps
                equity *= (1 + pnl)
                allocator.update_score(c.name, pnl)
                # Update priors with synthetic observations
                field.update(observed_slippage_bps=random.uniform(10,25), observed_fill_rate=random.uniform(0.5,0.9))

        time.sleep(1.0)

    es.emit("system.loop_end", {"equity": equity})
    click.echo(f"🏁 Loop finished. Equity ~ {equity:.2f}. See logs/events.ndjson and run the dashboard.")
