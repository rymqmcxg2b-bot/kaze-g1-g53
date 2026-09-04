# kaZe G1–G53: A Reconstructed Project-Iteration Timeline

This public timeline was reconstructed from surviving design reviews, incident records, test results, release names, and research reports. It is not a verbatim copy of the original operational log.

## How to Read This Table

- **Direct:** Surviving material names the generation and records a design, release, incident, or evaluation.
- **Partial:** Neighboring generations or later material establish the general direction, but not the complete delta.
- **Not preserved:** Publicly safe evidence is insufficient. Missing detail is not invented to make the story appear complete.
- Each row describes a research or engineering focus. It does not imply success, profitability, or formal deployment.

## G1–G15: Early Exploration

| Generation | What can be responsibly reconstructed | Evidence confidence |
|---:|---|---|
| G1 | The individual change was not preserved; it belonged to the early data and strategy exploration. | Not preserved |
| G2 | The individual change was not preserved; it belonged to the early data and strategy exploration. | Not preserved |
| G3 | The individual change was not preserved; it belonged to the early data and strategy exploration. | Not preserved |
| G4 | The individual change was not preserved; it belonged to the early data and strategy exploration. | Not preserved |
| G5 | The individual change was not preserved; it belonged to the early data and strategy exploration. | Not preserved |
| G6 | The individual change was not preserved; it belonged to the early data and strategy exploration. | Not preserved |
| G7 | The individual change was not preserved; it belonged to the early data and strategy exploration. | Not preserved |
| G8 | The individual change was not preserved; it belonged to the early data and strategy exploration. | Not preserved |
| G9 | The individual change was not preserved; it belonged to the early data and strategy exploration. | Not preserved |
| G10 | The individual change was not preserved; it belonged to the early data and strategy exploration. | Not preserved |
| G11 | The individual change was not preserved; it belonged to the early data and strategy exploration. | Not preserved |
| G12 | The individual change was not preserved; it belonged to the early data and strategy exploration. | Not preserved |
| G13 | The individual change was not preserved; it belonged to the early data and strategy exploration. | Not preserved |
| G14 | The individual change was not preserved; it belonged to the early data and strategy exploration. | Not preserved |
| G15 | Later material shows that an initial controlled-live baseline existed, but the generation-specific design is incomplete. | Partial |

The later repository confirms that this period gradually produced the P0–P6 engineering foundation: read-only source handling, data lineage, replay bundles, a shadow runtime, a fail-closed risk gate, audit JSONL, paper execution, and separation between phase state and execution capability. The evidence does not reliably assign each component to a particular generation from G1 through G15.

## G16–G22: Teaching the Runtime to Agree on “Now”

| Generation | What happened | Result or lesson | Confidence |
|---:|---|---|---|
| G16 | Corrected BBO/L2 freshness handling and initial-inventory baselines in fill attribution. | Market heartbeat and position conservation have to be established separately. | Direct |
| G17 | Used a durable fill ledger for continuous protective attribution and recovery after the previous latch. | A short current query window cannot reconstruct complete position history. | Direct |
| G18 | Bounded reconciliation work and checked position and open orders again immediately before dispatch. | A remote query can be healthy while a local data path still blocks the system. | Direct |
| G19 | Repaired execution-layer state around recovery and protective exits. | A protective attempt needs a terminal outcome and must not silently retry after restart. | Direct |
| G20 | Re-armed a new generation after a successful flatten and performed a mathematical fill-rate audit. | The strategy usually produced quotes, but cancel-first maintenance, distant placement, and short quote age jointly suppressed fills. | Direct |
| G21 | Ran a one-parameter experiment on the minimum half-spread floor while holding other strategy settings and limits fixed. | Parameter effects need to be separated from execution-availability effects. | Direct |
| G22 | Repaired the service-stop contract so a normal stop could complete graceful cancellation. | The operating system’s process-termination behavior is part of the trading state machine. | Direct |

## G23–G30: From “A Decision Exists” to “The Order Actually Remains in the Market”

| Generation | What happened | Result or lesson | Confidence |
|---:|---|---|---|
| G23 | Brought the market-data path into the hot-path review and examined L2/BBO update and decision latency. | Message frequency, deduplication, and freshness definitions directly change quoting behavior. | Direct |
| G24 | Built a capital-utilization candidate and scenario tests. | Higher capital use cannot be separated from fill probability, exit cost, and inventory dwell time. | Direct |
| G25 | Added request-budget recovery and audited strategy theory against execution. | API budgets, retries, and quote replacement create hidden strategy constraints. | Direct |
| G26 | Pursued cycle throughput, corrected protective scope, and encountered a quote-availability incident. | A faster loop without coherent state only creates gaps more quickly. | Direct |
| G27 | Redesigned quote availability. | Time-weighted resting availability on each side matters more than decision count alone. | Direct |
| G28 | Explored atomic order modification, dust recovery, post-fill ALO rejection, and a missing reduction cost basis. | Cancel/reinsert is not atomic; minimum size, cost basis, and protective exits can all break theoretical assumptions. | Direct |
| G29 | Recovered from the G27/G28 incident chain and re-armed under a new project-iteration label. | A new iteration label documents operational recovery, not new alpha. | Partial |
| G30 | Completed a combined deployment and stability observation for the G28 atomic-modify series. | Engineering recovery must not be described as strategy progress. | Partial |

## G31–G37: After-Cost EV Meets the Real Runtime

| Generation | What happened | Result or lesson | Confidence |
|---:|---|---|---|
| G31 | Built a capital-aware EV candidate, then handled Decimal representation, reconciliation, and a startup timeout. | Putting costs into an equation is only the beginning; numeric representation and startup state also affect decisions. | Direct |
| G32 | Changed validation of a large SQLite ledger to a streaming design. | An integrity check that loads the entire ledger can itself become an availability failure on a small host. | Direct |
| G33 | Adjusted the resource envelope and encountered bounded-restore startup and stop-protection failures. | A larger instance can relieve symptoms but cannot replace a bounded algorithm. | Direct |
| G34 | Built a bounded-restore gate and release. | Recovery needs a clear work bound and cannot become indefinitely slower as history grows. | Direct |
| G35 | Added reverse scanning and an empty-history gate, then found a delayed-health race. | Empty history is not corruption; health checks and startup need compatible semantics. | Direct |
| G36 | Added quiescent acceptance, stopped-state persistence, and unresolved-intent checks. | “No action now” may be a valid state or an unknown state; the two must be distinguishable. | Direct |
| G37 | Added resting-intent acceptance and single-intent reconciliation and encountered a permission incident. | A local intent becomes real state only after it is reconciled with an exchange order. | Direct |

## G38–G44: Making Startup and Recovery State-Aware

| Generation | What happened | Result or lesson | Confidence |
|---:|---|---|---|
| G38 | Worked on an episode fill window, rate-budgeted startup, ledger/test gates, and delayed health. | Startup queries also consume request budget; diagnostics and execution must not compete without limits. | Direct |
| G39 | Introduced state-aware startup and acceptance. | Acceptance must depend on actual exchange state rather than demanding that every case look like a flat cold start. | Direct |
| G40 | Reached the first coherent startup path and added known-inventory resume. | Known inventory should be a startup input, not ignored or treated as an automatic error. | Direct |
| G41 | Added known-fill reconciliation on resume. | A known fill must close consistently against the local lifecycle, position, and order history. | Direct |
| G42 | Re-armed after a protective flatten. | Flattening is an execution episode with an evidence chain, not an assignment of zero to an in-memory position. | Direct |
| G43 | Added resume from an operator-stopped live state. | An operator stop is a first-class state; recovery must distinguish it from a crash or risk latch. | Direct |
| G44 | Added state-aware live resume and reconciliation of explicit zero-position rows. | `position = 0` is authoritative state and must not disappear merely because its value is zero. | Direct |

## G45–G50: Returning to Maker Availability and Economics

| Generation | What happened | Result or lesson | Confidence |
|---:|---|---|---|
| G45 | Worked on position-aware quote availability, inventory acquisition, and wide-stop design. | Suppressing all quotes while inventory exists may remove skew and exit capacity, but quote presence still does not imply positive EV. | Direct |
| G46 | Combined bounded initialization with a local profit-throughput candidate. | Startup cost, useful quote time, and per-order after-cost economics all need explicit bounds. | Direct |
| G47 | Added loss-averse inventory accumulation and handled state-aware resume, unresolved intent, release-unit binding, packaging, and permission incidents. | Strategy semantics and packaging/permissions are separate chains that can each distort live results. | Direct |
| G48 | Designed adverse-selection-guarded profit capture. | Avoiding toxic fills also lowers fill rate; both effects need the same after-cost objective. | Direct |
| G49 | Tightened bounded startup. | Recovery time, queries, and historical scanning were bounded again. | Direct |
| G50 | Pursued continuous operation and recovery across episodes. | Reliable continuous recovery is an engineering result, not profitability evidence. | Direct |

## G51–G53: From “Build More” to “What Can the Evidence Actually Answer?”

| Generation | What happened | Result or lesson | Confidence |
|---:|---|---|---|
| G51 | Built a low-latency pure-taker path, streaming pre-trade features, a continuously running no-write shadow process, and forward calibration. | The hot-path benchmark passed, but complete round-trip cost was roughly an order of magnitude larger than the short-horizon signal; the candidate was rejected. | Direct |
| G52 | Built a five-channel public collector, sealed-storage foundations, typed attestation, a lifecycle ledger, an untouched after-cost policy, and action-shadow preregistration. | Many market rows are not strategy observations. The complete decision/attempt/outcome population was missing, so expectancy remained unavailable. | Direct |
| G53 | Returned to maker execution and built public no-write shadow, activation-L2 capture, strict replay, Colab model comparison, historical-data research, and multiple live-continuation/reconciliation attempts. | Only 4 of 35 strict-replay activations were usable. The dataset contained no positive hypothetical fill components, no markout rows, no complete rewards, and no linked actual execution outcomes. Live continuation also exposed multiple state and packaging failures. The project was paused. | Direct |

## What This Timeline Deliberately Does Not Do

- It does not describe the existence of a file, a packaged release, or an active service as successful trading.
- It does not treat public trades as kaZe fills.
- It does not treat hypothetical replay as live performance.
- It does not treat passing engineering tests as evidence of positive expectancy.
- It does not publish private account data, individual account trades, order identifiers, cloud topology, or authorization receipts.
- It does not invent a technical story for the missing generation-specific details of G1–G15.
