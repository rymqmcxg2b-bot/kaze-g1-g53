# Evidence Boundaries

## Claims Supported by This Archive

- kaZe used project labels G1–G53 during a long research and engineering process.
- Some small, tightly constrained live-trading experiments produced real orders, fills, reconciliation evidence, and incident records.
- The preserved G20 audit indicates concrete problems involving quote placement, cancel-first maintenance, and quote availability.
- In the observed G51 evaluation, estimated round-trip costs were roughly an order of magnitude larger than the measured short-horizon signal; the low-latency taker candidate was rejected.
- G52 built a strict after-cost evaluation contract, but its usable data could not answer the positive-expectancy question.
- G53 produced no-write shadow and strict-replay evidence. Integrity checks could pass while replay windows with complete causal follow-through and economic outcome labels remained insufficient.
- I did not maintain continuous evidence that account, order, and market state remained synchronized through one authoritative snapshot. That gap could contaminate strategy conclusions.

## Claims Not Supported by This Archive

- kaZe found or validated a positive-expectancy strategy.
- Any backtest, shadow result, or small live sample from any project iteration predicts future performance.
- Public market trades are kaZe fills.
- An active service means trading is healthy or even occurring.
- `open orders = 0` implies `position = 0`, or the reverse.
- Passing hash, schema, unit-test, benchmark, or deployment checks validates an economic hypothesis.
- G52 proved the strategy had negative expectancy. The correct conclusion was that evaluation was unavailable.
- G53 selected an RL or ML execution model suitable for live trading.

## How to Interpret the Reported Counts

### 86 fills / 34 cycles

This was an early sample from small, tightly constrained live-trading experiments, with a negative aggregate net result. It shows that some execution paths operated and provides clues about incidents and costs. It does not estimate long-run expectancy reliably.

### G52’s many market rows

They were ingestion events, not independent strategy observations. Without every decision, rejected alternative, attempt, no-fill/partial/full-fill outcome, associated fee, exit, and capital-time record, the event count cannot be treated as the sample size.

### G53’s 35 activations / 4 usable

Replay binding and integrity checks passed, but most activations were right-censored because they lacked complete causal follow-through. The usable population was too small and contained no linked actual execution outcomes, so it supported neither model selection nor a positive-expectancy conclusion. It also contained no positive hypothetical fill components.

## What Was Excluded from the Public Archive

This repository was rebuilt from a private workspace with an allowlist:

- It does not inherit the original Git history.
- It contains no account address, position detail, equity, entry price, fees, funding, or order-level identifiers.
- It contains no API token, private key, credential-bearing URL, cloud account/resource identifier, or host path.
- It contains no deployment receipt, owner authorization, service unit, or operable live endpoint.
- It retains only synthetic, non-trading code examples.

This archive is useful for learning and review, but it is not a complete forensic record. Academic-style reproduction would require a separately authorized, de-identified, and verifiable dataset.
