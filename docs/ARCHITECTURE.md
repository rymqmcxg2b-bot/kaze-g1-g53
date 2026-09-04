# Architecture and Data Flow: The Core Problem I Understood Late

The most important architectural lesson from kaZe was not a spread parameter. It was this: **strategy, risk controls, and execution must operate on one coherent live-state snapshot with explicit freshness and provenance.**

> **Correction record:** [DOC-001 and ERR-001–ERR-003](ERRATA.md) identify the earlier evidence-source contradiction and the three bugs in the public educational example. The architecture below describes intended contracts; the example implements only a small, in-memory subset.

## Intended Data Flow

```text
Market stream ───────┐
                     │
Account stream ──────┼──> Authoritative Live State ──> Strategy
                     │           │                        │
Order/fill events ───┘           │                        v
                                 │                   Quote intent
REST reconciliation ─────────────┤                        │
                                 │                        v
                                 │                    Execution
                                 │                        │
                                 └<── ACK / fill / reject┘
```

Every decision should bind to an unambiguous snapshot:

```text
S(t) = {
  market: bid, ask, depth, trades, volatility, event_time, receive_time,
  account: equity, available_balance, position, margin, unrealized_pnl,
  orders: exchange_open_orders, pending_new, pending_cancel, last_ack,
  execution: last_fill, last_cancel, last_reject,
  provenance: source, sequence, freshness, reconciliation_version
}
```

The strategy produces only an intent:

```text
A(t) = policy(S(t))
```

`A(t)` is not a fill and must not directly mutate the recorded position.

## A Possible Failure Mechanism in Loosely Coupled State

```text
Market WebSocket ──> fast strategy loop

Account REST ──────> slower cache ──> risk module

Local order table ─> execution assumptions
```

If those paths represent different moments, a loop like this can emerge:

1. The strategy sees position = 0 and decides to place a bid.
2. The risk module later sees position != 0 and immediately cancels.
3. The next strategy tick reads the stale cache and quotes again.
4. The system enters `QUOTE → CANCEL → QUOTE → CANCEL`.

This is a possible mechanism for quote/cancel oscillation when modules act on different versions of the world. It is an illustrative sequence, not a proven diagnosis of a particular historical incident. Establishing that cause would require decision-linked snapshots and order/risk events from the same interval.

## Source of Truth by State Type

| State | Low-latency primary source | Reconciliation source | Unacceptable shortcut |
|---|---|---|---|
| Intent / submission / cancel request | Local strategy and transport records | Local action journal, correlated with later exchange results | Treating a local request as proof that the exchange accepted or completed it |
| BBO / L2 / trades | Market stream, subject to sequence, gap, and freshness checks | Bounded public snapshot | Allowing ping traffic or another channel to hide a stale book |
| Position / balance | Account stream, subject to the same checks | Periodic authenticated REST snapshot | Running `position += qty` when a buy intent is merely submitted |
| Open orders | Order/account stream | Exchange REST snapshot | Trusting a local `submitted` row by itself |
| Exchange order status | Exchange ACK/fill/cancel/reject events | Explicit reconciliation result | Treating `sent` as `resting` |
| PnL / costs | Decision-linked fills, fees, funding, and exits | Independently reconstructed ledger | Substituting a public trade or an equity delta for strategy attribution |

## Order State Is Not Boolean

```text
Local action:       INTENT → SUBMITTED
                                │
Exchange result:                ├──> REJECTED
                                ├──> ACKNOWLEDGED → RESTING
                                │                       │
                                │                       ├──> PARTIAL_FILL → FILLED
                                │                       └──> CANCEL_PENDING
                                │                                  ├──> CANCELED
                                │                                  └──> PARTIAL_FILL / FILLED
Unresolved result:              └──> UNKNOWN → RECONCILE
```

**DOC-001 correction:** Evidence must match the fact being recorded. Creating `INTENT`, recording a local submission, and requesting a cancel are local facts. Acceptance, resting status, fills, confirmed cancellation, and exchange rejection require exchange evidence or an authoritative reconciliation result. A source label in an educational fixture is not itself proof of authenticity.

The diagram is conceptual rather than an exhaustive transition table. A submission can be rejected before it rests, and an order can fill before a separate resting notification arrives. A cancel request can race with a fill; rejecting the cancel does not mean the original order was rejected. Its remaining state must be established from the exchange. Local validation failure is also distinct from an exchange rejection.

`UNKNOWN` describes an unresolved result, including after a submission or cancellation timeout. It is not proof that an order is open, closed, or rejected. Reconciliation must resolve the uncertainty before the system assumes an outcome; a timeout does not authorize a blind retry of a signed write.

The corrected educational example keeps local intent and unresolved work distinct from confirmed open orders:

| Snapshot view | Included statuses | Meaning |
|---|---|---|
| `orders` | All retained records | Local and exchange records remain distinguishable by their status and linkage. |
| `pending_new` | `INTENT`, `SUBMITTED`, `ACKNOWLEDGED` | The example has not yet established that the order is resting. An ACK alone does not supply that fact. |
| `open_orders` | `RESTING`, `PARTIAL_FILL`, `CANCEL_PENDING` | Confirmed open state, including a cancellation still awaiting an outcome. |
| `unknown_orders` | `UNKNOWN` | The outcome needs reconciliation. |

An exchange event may carry `intent_id` to link its exchange `order_id` to a local intent. Valid linked evidence retires the pending local record; rebinding that intent to a different exchange order is rejected. Reconciliation compares only confirmed-open IDs and separately reports `PENDING_ORDER_CONFIRMATION` for submitted or acknowledged work and `ORDER_STATE_UNKNOWN` for unknown outcomes. An unsent intent alone is not an exchange-open mismatch.

The example validates a restricted normalized lifecycle, fixes side and quantity for a given order ID, and prevents terminal-state changes and cumulative-fill regressions. Identical repeated order events are no-ops; older events, conflicting timestamp ties, and invalid transitions raise `ValueError` without changing state. These limited invariants are not a complete exchange lifecycle implementation; late reports, correction/bust events, cancel races, and amendments require explicit venue-specific semantics.

Freshness also has two bounds: `0 <= snapshot_time - update_time <= max_age`, with a nonnegative maximum age. A timestamp ahead of the snapshot is not fresh. The example assumes comparable clock values and uses market receipt time for its market freshness check; this does not independently prove that the underlying exchange event is current.

## Roles of WebSocket and REST

- WebSocket and account streams are low-latency primary event feeds, subject to sequence, gap, and freshness checks.
- REST supplies startup, periodic, and exception-driven reconciliation.
- Strategy reads one coherent snapshot instead of independently querying multiple clients.
- Execution submits an intent, waits for ACK, fill, cancel, or rejection evidence, and feeds those events back into live state.

REST should not block every decision tick, but a WebSocket must not be assumed to be permanently complete. Both paths require explicit freshness, sequence/gap, and conflict policies.

## What Was Still Missing When the Project Paused

kaZe built many local reconciliation mechanisms and fail-closed gates, but it did not continuously establish all four of these properties at once:

1. Account, order, fill, and market states share one snapshot identity.
2. Every decision can be traced to the complete action set—including no-action, filtered, and censored alternatives—and a terminal or explicitly censored outcome.
3. Live, shadow, and replay use the same verified transition path.
4. Every strategy conclusion can be recomputed from a complete, immutable population with after-cost and capital-time accounting.

The file `src/kaze_archive/live_state.py` is a minimal, non-trading illustration of this lesson. It assumes a single-threaded caller and copies the currently stored values into a snapshot. That copy does not make independently received feeds simultaneous or transactionally coherent, authenticate their sources, or establish continuous synchronization.
