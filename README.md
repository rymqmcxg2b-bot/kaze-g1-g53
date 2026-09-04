# kaZe: What I Learned from 53 Project Iterations of an Unproven Trading System

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

> **Status: PAUSED / RESEARCH ARCHIVE**
>
> kaZe did not establish positive after-cost expectancy. It is not a production trading system and should not be entrusted with capital. This public edition contains no credentials, account identifiers, cloud-resource identifiers, private trading data, or exchange-connected execution component.

> **Formal descriptive research title:** *kaZe G1–G53: An Exploratory Systems Study of Inventory-Aware Maker Quoting, Execution-State Reconciliation, and After-Cost Evaluation in a BTC Perpetual Limit-Order Book*

> **Public-example corrections:** The review of revision `7c6f248` found three bugs in the rewritten educational state example and one contradiction in its architecture documentation. [Errata and corrections](docs/ERRATA.md) records the affected lines, old behavior, corrected rules, and regression checks. These findings concern the public example; they do not establish that the private historical runtime had the same bugs.

kaZe began as a “vibe coding” project: an AI-assisted learning experiment in market microstructure, automated trading, data integrity, and live execution. Its project labels eventually ran from G1 to G53. What remains is not a successful equity curve, but a record of gradually learning to distinguish “the program runs,” “an order can be submitted,” and “the strategy has a defensible edge.”

[Errata and corrections](docs/ERRATA.md) · [Theoretical foundations](docs/THEORETICAL_FOUNDATIONS.md) · [The complete G1–G53 index](docs/JOURNEY_G1_G53.md) · [Architecture and data flow](docs/ARCHITECTURE.md) · [Failures and lessons](docs/FAILURES_AND_LESSONS.md) · [Evidence boundaries](docs/EVIDENCE_BOUNDARIES.md) · [Questions I still want to understand](docs/OPEN_QUESTIONS.md)

## Why I Am Publishing kaZe

The reason I started kaZe was simple: I was deeply curious about how markets work. I wanted to know whether an ordinary person, using today’s AI tools, could turn an idea about trading into a real system—one that reads the market, manages inventory, submits orders, and faces real outcomes.

AI-assisted coding let me attempt things I could not previously build. Subjects that once felt far beyond my reach—WebSockets, order books, replay, risk controls, cloud deployment, state machines, and model training—suddenly became approachable. I became absorbed in the project, and I genuinely enjoyed each moment when one solved problem revealed another layer underneath it. That is how kaZe went from G1 to G53.

The same journey also showed me how much I still do not know.

For a while, I confused more versions, passing tests, and growing engineering complexity with progress toward profitability. I slowly learned that the hardest part of a trading system is not merely writing the software. It is knowing what the data actually represents, how costs enter the result, whether a public market trade represented one of the system’s fills, whether positions and open orders were synchronized, and whether the strategy, risk controls, and execution system were even observing the same state.

kaZe did not establish positive after-cost expectancy. In the observed G51 evaluation, estimated round-trip costs were roughly an order of magnitude larger than the measured short-horizon taker signal. The maker path lacked sufficient evidence about fills, queue position, adverse selection, and complete rewards. Live engineering repeatedly exposed weaknesses in account-state reconciliation, startup behavior, permissions, packaging, and resource constraints. Some components passed rigorous tests while the system still could not answer its most important question with confidence: under real costs and real execution, did this exact strategy have a repeatable edge?

So I decided to pause the project.

I have not lost interest. I simply do not want to hide gaps in my foundations—market microstructure, statistical validation, experimental design, and distributed systems—under another layer of code. I need to learn those subjects more seriously before deciding whether kaZe deserves to continue.

I am publishing this project not to present a successful trading machine, and not to give anyone something to trade with. I want to share a learning process that was real, messy, enthusiastic, and often wrong. If this unfinished and unsuccessful experiment, one of its tests, an incident pattern, or a data contract helps someone avoid even one mistake, I will be very happy.

If you are willing to tell me where my reasoning went wrong, recommend foundations I should study, investigate a question together, or simply talk about a system you built that failed, I would love to hear from you. I also hope this archive helps me meet friends who enjoy careful inquiry and are comfortable admitting what they do not know.

Thank you for visiting kaZe. There is no promise of profit here—only the questions, evidence, and curiosity that survived throughout the G1–G53 record.

## What kaZe Tried to Explore

- Maker and inventory-aware market making for BTC perpetual contracts.
- Using order flow, imbalance, volatility, and adverse selection to decide whether to quote.
- Letting inventory skew influence both quote prices and sizes.
- Keeping replay, shadow, and live execution on as much of the same decision path as possible.
- Managing real state with reconciliation, append-only evidence, and fail-closed gates.
- Keeping a 24/7 runtime observable, recoverable, and reproducible on constrained hardware.

These were goals the project explored incrementally. They were not all achieved.

## Formal Research Framing

**Strategy family:** Inventory-aware, signal-conditioned limit-order-book market making with event-driven feedback control.

kaZe explored four connected bodies of theory and engineering:

- **Inventory-based market making.** Quote prices and sizes responded to inventory, placing the design in the broad lineage of the Ho–Stoll dealer models, the Avellaneda–Stoikov stochastic-control formulation, and later inventory-constrained market-making work.
- **Limit-order-book microstructure.** Quote decisions explored microprice, depth imbalance, trade-flow imbalance, spread, short-horizon volatility, maker fill uncertainty, and adverse selection.
- **Event-driven feedback control and distributed state.** Decisions were intended to operate on a coherent snapshot of market, account, order, and execution state, followed by evidence-backed ACK, fill, cancel, reject, and reconciliation transitions.
- **After-cost empirical evaluation.** A credible result would require decision-linked attempts, fills and no-fills, fees, slippage, funding, exits, inventory dwell time, and censored outcomes—not merely public trades or service activity.

This classification describes kaZe’s intellectual lineage, not a claim that it implemented a canonical optimal-market-making model. Its quote engine was a rule-based engineering heuristic: it did not solve a Hamilton–Jacobi–Bellman equation, calibrate the canonical order-arrival model, or establish an optimality result. Partial observability is a useful lens for its stale, missing, and conflicting state, but kaZe did not formulate or solve a POMDP.

ML and reinforcement learning remained possible future directions for a bounded execution layer. G53 did not select, train, or validate an RL or ML policy for live trading. G51 was a separate short-horizon taker experiment rather than the theoretical core of the maker system.

See [Theoretical Foundations and Research Classification](docs/THEORETICAL_FOUNDATIONS.md) for the full mapping and the correctly qualified historical quote equations.

## The G1–G53 Project Map

| Stage | What happened |
|---|---|
| G1–G15 | Early exploration and the P0–P6 foundation: read-only sources, lineage, replay bundles, a shadow runtime, a risk gate, and an execution state machine. The surviving evidence cannot reliably separate every generation, so this archive does not invent the missing details. |
| G16–G22 | Confronted BBO/L2 freshness, fill attribution, reconciliation, a latency latch, a spread-floor experiment, and the service-stop contract. This was the first clear lesson that “market data exists” does not mean every module sees the same present. |
| G23–G30 | Pursued the hot path, capital utilization, request budgets, cycle throughput, quote availability, and atomic order modification. Also encountered cancel-to-reinsert gaps, dust recovery, and a missing reduction cost basis. |
| G31–G37 | Put after-cost EV into the decision path, then repeatedly ran into Decimal representation, SQLite and memory pressure, startup recovery, permissions, and resting-intent reconciliation. |
| G38–G44 | Made startup, health checks, known fills, protective flattening, operator stops, and zero-position rows state-aware. The central question became: what does the system know, and when does it know it? |
| G45–G50 | Returned to maker quote availability, inventory acquisition, loss-aware accumulation, adverse-selection guards, bounded startup, and continuous resume. Engineering became stricter; profitability still did not follow. |
| G51 | Tried a low-latency taker design. Engineering benchmarks passed, but held-out forward evidence showed that measured trading costs were much larger than the observed signal, so the candidate was rejected. |
| G52 | Built a stricter positive-expectancy test contract, a five-channel data path, sealed-cohort foundations, and action shadow. The data and decision-to-outcome population were incomplete, so the expectancy question remained unanswerable. |
| G53 | Returned to maker execution and built public shadow, activation-L2 capture, strict replay, historical-data analysis, and model candidates. Replay windows with complete causal follow-through were too scarce, with no positive hypothetical fill components, no complete rewards, and no sufficiently complete outcome dataset for defensible model training. Later live continuations also exposed packaging, permission, SQLite identity, startup-wait, and account/order-reconciliation failures. |

See [the complete G1–G53 index](docs/JOURNEY_G1_G53.md) for every project iteration and its documentation confidence.

## The Most Honest Result

kaZe **did not establish positive after-cost expectancy**.

- One early sample from small, tightly constrained live-trading experiments contained 86 fills and 34 completed cycles, with a negative aggregate net result. The sample was too small to extrapolate.
- In the observed G51 evaluation, estimated round-trip costs were roughly an order of magnitude larger than the measured short-horizon taker signal, so the candidate was rejected.
- G52 collected many public-market events but lacked a complete population of strategy decisions, attempts, fills/no-fills, and after-cost outcomes. Positive expectancy could not be evaluated.
- In G53 strict replay, only 4 of 35 activations were usable. There were no positive hypothetical fill components, complete rewards, or sufficiently complete outcomes for defensible model training.
- Some live paths did successfully submit, maintain, and reconcile orders, but I did not maintain continuous evidence that account, order, and market state remained synchronized through one authoritative snapshot.

Having code, tests, data, and live-trading records is not the same as having credible strategy performance.

## What I Actually Learned

1. **Costs can be an order of magnitude larger than short-horizon alpha.** Fees, spread, slippage, adverse selection, funding, and exit costs must enter the definition before the experiment begins.
2. **A public-market trade is not your fill.** Without a complete decision → order → ACK/fill → position → PnL chain, performance analysis is not trustworthy.
3. **An order being sent does not mean it was accepted.** Accepted, resting, partially filled, filled, cancel pending, and canceled are different states.
4. **Account state needs one authoritative representation.** Position, balance, and open-order snapshots with different freshness can cause strategy and risk controls to act against each other.
5. **Execution mechanics are part of the strategy.** Cancel policy, queue position, request budgets, rate limits, cold starts, and recovery all alter the economics.
6. **More versions do not create better experimental design.** If the policy changes every time a result is observed, there is no untouched evidence.
7. **Fail-closed behavior has a cost.** It can prevent trading in an unknown state, but it can also remove inventory-managing maker orders while inventory remains. Risk boundaries and strategy semantics have to be designed together.
8. **Vibe coding is an amplifier.** It amplified my curiosity and my ability to build—and also the gaps in my knowledge that I did not yet know how to see.

## What Is in This Repository

This is not a dump of the original production repository. It is a **de-identified public research archive rebuilt from an explicit allowlist**:

- `docs/JOURNEY_G1_G53.md`: the focus, outcome, and documentation confidence of every project iteration.
- `docs/ERRATA.md`: the public-example bugs and documentation contradiction, with baseline evidence, corrected behavior, and regression checks.
- `docs/THEORETICAL_FOUNDATIONS.md`: the formal research name, theoretical lineage, historical quote equations, and limits of the classification.
- `docs/ARCHITECTURE.md`: the authoritative live-state data flow I eventually understood was necessary.
- `docs/FAILURES_AND_LESSONS.md`: recurring failure modes, causal relationships, and how I would approach them now.
- `docs/EVIDENCE_BOUNDARIES.md`: what the evidence supports and what it does not.
- `docs/OPEN_QUESTIONS.md`: possible starting points if you would like to teach me or investigate something together.
- `src/kaze_archive/`: a no-network, no-order educational state-machine example.
- `tests/`: invariants such as “recording an intent must not predictively change position.”

The original runtime, deployment receipts, account data, wallet/order/fill identifiers, cloud topology, secrets, and old Git history are deliberately excluded. The example code was rewritten from the lessons; it is not a production executor.

## Run the Educational Example Locally

Python 3.11+ is required. There are no third-party runtime dependencies, and the examples make no network requests:

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONPATH=src python -m kaze_archive.demo
python scripts/public_safety_scan.py
```

## Would You Like to Learn or Research Together?

Issues and Discussions are open. I would especially value help with:

- market microstructure and maker queue mechanics;
- after-cost statistical validation, selection bias, and leakage review;
- execution state machines and exchange reconciliation;
- data lineage, causal replay, and reproducible experiments;
- reliable runtime engineering on small cloud instances;
- books, papers, courses, and exercises that could strengthen my foundations.

Please see [CONTRIBUTING.md](CONTRIBUTING.md). Kind but direct criticism is very welcome.

## License

The entire repository, including its documentation, is released under the [Apache License 2.0](LICENSE).
