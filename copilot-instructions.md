
# Copilot Instructions — v26meme

You are assisting on an **autonomous trading intelligence**. Follow these rules:

## When asked to add a strategy
- Use the **StrategyCard DSL** (`v26meme/core/dsl.py`) with required fields.
- Ensure **entry/exit**, **stops**, **filters**, **risk bps**, **capacity caps**, **latency budget** are present.
- Add tests in **SimLab** (CV+embargo) and **stress**; require Expectancy CI>0, Sortino>1, MDD<20% before promotion.

## When changing allocation or risk
- Modify `v26meme/allocation/allocator.py` and `v26meme/core/policy.py` **together**.
- Keep **Core/Turbo sleeves**, **fractional-Kelly**, **theme caps**, **capacity curves**.

## When touching execution
- Use the state machine in `v26meme/execution/fsm.py` and router in `v26meme/execution/router.py`.
- No LLM in hot path. All actions must pass **policy checks** in `policy.py`.

## When expanding discovery
- Use **TemplateGenerator** and **PatternMiner** in `v26meme/research/`.
- Rank new ideas with **EV-per-Cost** score in `triage.py`.
- Only top-ranked ideas go to SimLab; losers are killed early.

## Do
- Add helpful comments and docstrings.
- Keep outputs structured (JSON-like dicts).  
- Log to event store with `emit_event`.

## Don’t
- Don’t bypass policy checks.
- Don’t enable live trading in commits.
