# Architecture and Data Flow: The Core Problem I Understood Late

The most important architectural lesson from kaZe was not a spread parameter. It was this: **strategy, risk controls, and execution must operate on one coherent live-state snapshot with explicit freshness and provenance.**

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

## The Loosely Coupled Pattern That Caused Trouble

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

The symptom looks like an overly sensitive cancel threshold. The underlying problem is that different modules are acting on different versions of the world.

## Source of Truth by State Type

| State | Low-latency primary source | Reconciliation source | Unacceptable shortcut |
|---|---|---|---|
| BBO / L2 / trades | Market stream, subject to sequence, gap, and freshness checks | Bounded public snapshot | Allowing ping traffic or another channel to hide a stale book |
| Position / balance | Account stream, subject to the same checks | Periodic authenticated REST snapshot | Running `position += qty` when a buy intent is merely submitted |
| Open orders | Order/account stream | Exchange REST snapshot | Trusting a local `submitted` row by itself |
| Order lifecycle | Exchange ACK/fill/cancel/reject events | Explicit reconciliation result | Treating `sent` as `resting` |
| PnL / costs | Decision-linked fills, fees, funding, and exits | Independently reconstructed ledger | Substituting a public trade or an equity delta for strategy attribution |

## Order State Is Not Boolean

```text
INTENT
  ↓
SUBMITTED
  ↓
ACKNOWLEDGED
  ↓
RESTING ───────> CANCEL_PENDING ───────> CANCELED
  │
  ├──> PARTIAL_FILL
  │         │
  │         └──> FILLED
  └──> REJECTED / UNKNOWN → RECONCILE
```

Every transition requires exchange evidence. A timeout makes the result unknown; it does not prove failure and does not authorize a blind retry of a signed write.

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

The file `src/kaze_archive/live_state.py` is a minimal, non-trading illustration of this lesson.
